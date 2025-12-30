#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Demerzel - Step 11
Goal: Keep the same architecture, but make intent recognition robust to phrasing.
- Wake -> quick ACK -> command listening window
- Interprets common intents: time, remember_task (+confirm/cancel), list_tasks, complete_task
- Adds strong normalization + paraphrase mapping so "what am I tasks" doesn't become unknown
- Uses macOS 'say' for voice output if available (fallback to print)

Dependencies (same as earlier steps):
- vosk
- sounddevice
"""

import os
import sys
import json
import time
import re
import queue
import shutil
import subprocess
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any, List, Tuple

import sounddevice as sd
from vosk import Model, KaldiRecognizer


# =========================
# CONFIG (safe to leave)
# =========================

WAKE_NAME = "DEMERZEL"

# Wake aliases help when ASR hears "dammers", "dam ezell", etc.
WAKE_ALIASES = [
    "demerzel",
    "damerzel",
    "dammers",
    "damers",
    "dam ezell",
    "dam ezel",
    "dam ezzell",
    "dammers l",
    "dammers ill",
    "damm ezell",
    "dammers",
]

WAKE_THRESHOLD = 0.72  # fuzzy threshold
SAMPLE_RATE = 16000
BLOCKSIZE = 8000

# Timing windows (seconds)
COMMAND_LISTEN_WINDOW = 6.0         # after wake, how long to listen for the command
FOLLOWUP_LISTEN_WINDOW = 7.0        # after responding, listen for a follow-up without requiring wake word
CONFIRM_LISTEN_WINDOW = 8.0         # confirmation window after "remember ..."
START_GRACE = 3.0                   # ignore any speech immediately after wake (you breathing / overlap)
END_SILENCE = 0.9                   # how long of silence indicates user finished speaking

# Where memory is stored
MEMORY_PATH = os.path.join(os.path.dirname(__file__), "memory.json")

# Vosk model path
DEFAULT_MODEL_DIR = os.path.join(os.path.dirname(__file__), "models", "vosk-model-small-en-us-0.15")


# =========================
# SMALL UTILITIES
# =========================

def now_ts() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())

def term_beep():
    # Terminal bell (not always audible depending on settings, but harmless)
    print("\a", end="", flush=True)

def macos_say(text: str) -> bool:
    """Return True if spoken successfully via macOS 'say'."""
    if shutil.which("say") is None:
        return False
    try:
        subprocess.run(["say", text], check=False)
        return True
    except Exception:
        return False

def SAY(text: str):
    print(f"[SAY] {text}")
    term_beep()
    if not macos_say(text):
        # fallback is just printed text
        pass

def load_memory() -> Dict[str, Any]:
    if not os.path.exists(MEMORY_PATH):
        return {"tasks": [], "facts": []}
    try:
        with open(MEMORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"tasks": [], "facts": []}

def save_memory(mem: Dict[str, Any]):
    tmp = MEMORY_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(mem, f, indent=2)
    os.replace(tmp, MEMORY_PATH)

def next_task_id(mem: Dict[str, Any]) -> int:
    ids = [t.get("id", 0) for t in mem.get("tasks", [])]
    return (max(ids) + 1) if ids else 1


# =========================
# NORMALIZATION LAYER
# =========================

def basic_clean(text: str) -> str:
    t = text.lower().strip()
    t = re.sub(r"[^a-z0-9\s']", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t

def drop_fillers(text: str) -> str:
    # Remove noise that often appears in ASR
    fillers = [
        "uh", "um", "like", "you know", "okay", "ok", "alright", "right",
        "hey", "yo", "so", "well", "please"
    ]
    t = text
    for f in fillers:
        t = re.sub(rf"\b{re.escape(f)}\b", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t

def strip_leading_wake(text: str) -> str:
    """
    Remove leading wake-like words if ASR includes them inside the command
    ex: 'awake listening what time is it' -> 'what time is it'
    """
    t = text
    t = re.sub(r"^(awake\s+listening\s+)", "", t)
    t = re.sub(r"^(awake\s+)", "", t)
    t = re.sub(r"^(listening\s+)", "", t)
    # also remove explicit wake name if ASR includes it
    for a in WAKE_ALIASES + ["demerzel"]:
        t = re.sub(rf"^{re.escape(a)}\s+", "", t)
    return t.strip()

def paraphrase_map(text: str) -> str:
    """
    This is Step 11’s main improvement:
    Map common “wrong but close” phrases into the canonical form expected by intents.
    """
    t = text

    # TASK LIST variations -> "what are my tasks"
    task_list_patterns = [
        r"what am i tasks",
        r"what am i task",
        r"what are my task",
        r"what is my tasks",
        r"what's my tasks",
        r"what do i have to do",
        r"do i have tasks",
        r"any tasks",
        r"show my tasks",
        r"list my tasks",
        r"tasks please",
        r"what are my to dos",
        r"what are my todos",
        r"what are my to do",
    ]
    for p in task_list_patterns:
        if re.fullmatch(p, t):
            return "what are my tasks"

    # TIME variations -> "what time is it"
    time_patterns = [
        r"what time is it",
        r"tell me the time",
        r"time",
        r"current time",
        r"what's the time",
        r"what time",
    ]
    for p in time_patterns:
        if re.fullmatch(p, t):
            return "what time is it"

    # COMPLETE variations -> canonical "complete task <n>"
    m = re.fullmatch(r"(complete|finish|done|mark done)\s+(task\s+)?(\d+)", t)
    if m:
        n = m.group(3)
        return f"complete task {n}"

    # CONFIRM/CANCEL variations -> canonical
    if t in ["confirm", "confirmed", "yes", "yep", "yeah", "save", "do it", "ok confirm"]:
        return "confirm"
    if t in ["cancel", "never mind", "nevermind", "no", "nope", "stop", "don't", "dont"]:
        return "cancel"

    return t

def normalize_text(raw: str) -> str:
    t = basic_clean(raw)
    t = drop_fillers(t)
    t = strip_leading_wake(t)
    t = paraphrase_map(t)
    return t


# =========================
# WAKE MATCH (fuzzy)
# =========================

def token_set(text: str) -> set:
    return set(text.split())

def jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 0.0
    return len(a & b) / max(1, len(a | b))

def best_wake_match(text: str) -> Tuple[str, float]:
    """
    Returns (best_alias, score) where score is token Jaccard similarity.
    Works better than exact match when ASR outputs weird spacing.
    """
    t = basic_clean(text)
    ts = token_set(t)
    best = ("", 0.0)
    for alias in WAKE_ALIASES:
        a = token_set(basic_clean(alias))
        s = jaccard(ts, a)
        if s > best[1]:
            best = (alias, s)
    return best


# =========================
# INTENTS
# =========================

@dataclass
class Intent:
    intent_type: str
    payload: Dict[str, Any]

def interpret_intent(normalized: str) -> Intent:
    """
    Very small, deterministic interpreter.
    Step 12 is where the LLM/planning layer comes in later.
    """
    if normalized == "what time is it":
        return Intent("time", {})

    if normalized == "what are my tasks":
        return Intent("list_tasks", {})

    m = re.fullmatch(r"complete task (\d+)", normalized)
    if m:
        return Intent("complete_task", {"id": int(m.group(1))})

    # remember task (we keep it strict and clean)
    m = re.fullmatch(r"(remember|remind me|add task)\s+(.+)", normalized)
    if m:
        text = m.group(2).strip()
        # Defensive: avoid capturing "remember" alone
        if len(text) >= 2:
            return Intent("remember_task", {"text": text})

    if normalized in ["confirm", "cancel"]:
        return Intent(normalized, {})

    return Intent("unknown", {"raw": normalized})


# =========================
# AUDIO / ASR
# =========================

class ASR:
    def __init__(self, model_dir: str):
        if not os.path.isdir(model_dir):
            raise FileNotFoundError(
                f"Vosk model folder not found:\n{model_dir}\n\n"
                f"Expected something like:\nmodels/vosk-model-small-en-us-0.15"
            )
        self.model = Model(model_dir)
        self.rec = KaldiRecognizer(self.model, SAMPLE_RATE)
        self.q = queue.Queue()

    def callback(self, indata, frames, time_info, status):
        if status:
            print(status, file=sys.stderr)
        self.q.put(bytes(indata))

    def listen_stream(self):
        return sd.RawInputStream(
            samplerate=SAMPLE_RATE,
            blocksize=BLOCKSIZE,
            dtype="int16",
            channels=1,
            callback=self.callback,
        )

    def read_partial_final(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Returns (partial, final). final only appears when Vosk finalizes an utterance.
        """
        data = self.q.get()
        if self.rec.AcceptWaveform(data):
            res = json.loads(self.rec.Result())
            text = (res.get("text") or "").strip()
            return None, text if text else None
        else:
            res = json.loads(self.rec.PartialResult())
            p = (res.get("partial") or "").strip()
            return p if p else None, None

def capture_utterance(asr: ASR, max_seconds: float, start_grace: float = 0.0) -> Tuple[str, str]:
    """
    Capture one utterance up to max_seconds.
    Returns (raw_final_text, normalized_text). If nothing, returns ("", "").
    """
    start = time.time()
    heard_anything = False
    final_text = ""

    # We end if we get a final result OR time runs out.
    while time.time() - start < max_seconds:
        partial, final = asr.read_partial_final()
        if partial:
            # ignore partial spam during grace period
            if time.time() - start < start_grace:
                continue
            heard_anything = True
            print(f"partial: {partial}")
        if final:
            if time.time() - start < start_grace:
                # ignore a finalized chunk inside grace window
                continue
            print(f"FINAL: {final}")
            final_text = final
            break

    raw = final_text.strip()
    norm = normalize_text(raw) if raw else ""
    return raw, norm


# =========================
# BRAIN / STATE MACHINE
# =========================

@dataclass
class BrainState:
    name: str = "Demerzel"
    attention_state: str = "IDLE"
    last_input: str = ""
    last_intent: str = ""
    last_action_said: str = ""
    pending_confirmation: Optional[Dict[str, Any]] = None  # {"type": "remember_task", "payload": {...}}
    turn_index: int = 0

def log_phase(phase: str, data: Dict[str, Any]):
    event = {"ts": now_ts(), "phase": phase, "data": data}
    print(json.dumps(event, indent=2))

def handle_intent(brain: BrainState, intent: Intent, mem: Dict[str, Any]) -> str:
    """
    Returns spoken response text.
    """
    brain.last_intent = intent.intent_type

    if intent.intent_type == "time":
        t = time.strftime("%I:%M %p").lstrip("0")
        return f"It is {t}."

    if intent.intent_type == "list_tasks":
        tasks = [t for t in mem.get("tasks", []) if not t.get("done")]
        if not tasks:
            return "You have no open tasks."
        if len(tasks) == 1:
            return f"You have 1 open task. Task 1: {tasks[0].get('text','')}"
        # keep it short
        return f"You have {len(tasks)} open tasks. The latest is: {tasks[-1].get('text','')}"

    if intent.intent_type == "complete_task":
        tid = intent.payload.get("id")
        for t in mem.get("tasks", []):
            if t.get("id") == tid and not t.get("done"):
                t["done"] = True
                t["done_ts"] = now_ts()
                save_memory(mem)
                return f"Completed task {tid}: {t.get('text','')}."
        return f"I could not find an open task {tid}."

    if intent.intent_type == "remember_task":
        # Start confirmation flow
        brain.pending_confirmation = {"type": "remember_task", "payload": intent.payload}
        text = intent.payload.get("text", "")
        return f"You want me to remember: {text}. Say confirm to save, or cancel."

    if intent.intent_type == "confirm":
        if brain.pending_confirmation and brain.pending_confirmation.get("type") == "remember_task":
            text = brain.pending_confirmation["payload"].get("text", "").strip()
            if text:
                tid = next_task_id(mem)
                mem.setdefault("tasks", []).append({"id": tid, "text": text, "done": False, "ts": now_ts()})
                save_memory(mem)
                brain.pending_confirmation = None
                return f"Saved. Task {tid}: {text}"
        return "Nothing to confirm."

    if intent.intent_type == "cancel":
        if brain.pending_confirmation:
            brain.pending_confirmation = None
            return "Canceled."
        return "Nothing to cancel."

    return "I heard you, but I don't have an action for that yet."


def main():
    model_dir = os.environ.get("VOSK_MODEL_DIR", DEFAULT_MODEL_DIR)
    asr = ASR(model_dir)
    mem = load_memory()
    brain = BrainState()

    print(f"[RUN] Demerzel Step 11 running. Say '{WAKE_NAME}' to wake. Ctrl+C to stop.")
    print(f"[WAKE] threshold={WAKE_THRESHOLD} aliases={len(WAKE_ALIASES)}")
    print(f"[CMD] command_window={COMMAND_LISTEN_WINDOW}s followup_window={FOLLOWUP_LISTEN_WINDOW}s confirm_window={CONFIRM_LISTEN_WINDOW}s")
    print(f"[MEM] {MEMORY_PATH}")

    try:
        with asr.listen_stream():
            while True:
                # ======================
                # IDLE: waiting for wake
                # ======================
                brain.attention_state = "IDLE"
                # Keep listening until we hear something that matches wake aliases
                partial, final = asr.read_partial_final()
                if partial:
                    print(f"partial: {partial}")
                if not final:
                    continue

                print(f"FINAL: {final}")
                alias, score = best_wake_match(final)
                if score < WAKE_THRESHOLD:
                    continue

                print(f"=== WAKE === name={WAKE_NAME} heard='{final}' best_alias='{alias}' score={score:.3f}")
                brain.attention_state = "WAKING"
                log_phase("STATE", {"attention_state": brain.attention_state})
                SAY("Awake.")
                SAY("Listening.")

                # ======================
                # COMMAND window
                # ======================
                brain.attention_state = "LISTENING"
                log_phase("STATE", {"attention_state": brain.attention_state, "mode": "COMMAND", "window": COMMAND_LISTEN_WINDOW})

                raw, norm = capture_utterance(asr, max_seconds=COMMAND_LISTEN_WINDOW, start_grace=START_GRACE)
                if not norm:
                    SAY("No command heard.")
                    continue

                brain.turn_index += 1
                brain.last_input = norm

                intent = interpret_intent(norm)
                log_phase("INTERPRET", {"raw_text": raw, "normalized": norm, "intent": intent.intent_type, "payload": intent.payload})

                brain.attention_state = "THINKING"
                log_phase("STATE", {"attention_state": brain.attention_state})

                speak = handle_intent(brain, intent, mem)

                brain.attention_state = "RESPONDING"
                log_phase("DELIBERATE", {"speak": speak, "actions": []})
                SAY(speak)

                # ======================
                # CONFIRMATION window (only if pending)
                # ======================
                if brain.pending_confirmation:
                    brain.attention_state = "CONFIRMING"
                    log_phase("STATE", {"attention_state": brain.attention_state, "window": CONFIRM_LISTEN_WINDOW})
                    raw2, norm2 = capture_utterance(asr, max_seconds=CONFIRM_LISTEN_WINDOW, start_grace=0.2)
                    norm2 = normalize_text(norm2) if norm2 else ""

                    if norm2 in ["confirm", "cancel"]:
                        intent2 = interpret_intent(norm2)
                        log_phase("INTERPRET", {"raw_text": raw2, "normalized": norm2, "intent": intent2.intent_type, "payload": intent2.payload})
                        speak2 = handle_intent(brain, intent2, mem)
                        log_phase("DELIBERATE", {"speak": speak2, "actions": []})
                        SAY(speak2)
                    else:
                        # If user didn't confirm/cancel, we keep it simple and exit.
                        SAY("No confirmation heard. Returning to wake listening.")
                        brain.pending_confirmation = None

                # ======================
                # FOLLOW-UP window
                # ======================
                brain.attention_state = "LISTENING"
                log_phase("STATE", {"attention_state": brain.attention_state, "mode": "FOLLOWUP", "window": FOLLOWUP_LISTEN_WINDOW})

                raw3, norm3 = capture_utterance(asr, max_seconds=FOLLOWUP_LISTEN_WINDOW, start_grace=0.2)
                if norm3:
                    brain.turn_index += 1
                    intent3 = interpret_intent(norm3)
                    log_phase("INTERPRET", {"raw_text": raw3, "normalized": norm3, "intent": intent3.intent_type, "payload": intent3.payload})
                    speak3 = handle_intent(brain, intent3, mem)
                    log_phase("DELIBERATE", {"speak": speak3, "actions": []})
                    SAY(speak3)

                # Back to idle (wake listening)
                brain.attention_state = "IDLE"
                log_phase("STATE", {"attention_state": brain.attention_state})

    except KeyboardInterrupt:
        print("\n[STOP] Ctrl+C received. Exiting cleanly.")
        return


if __name__ == "__main__":
    main()

