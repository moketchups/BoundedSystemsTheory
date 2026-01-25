#!/usr/bin/env python3
# Demerzel: single-file, provable loop
# Wake -> quick ack -> command window -> (optional confirm) -> speak response -> follow-up window -> back to idle

import os
import re
import json
import time
import queue
import signal
import threading
import datetime
import subprocess
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Tuple

import pyaudio
from vosk import Model, KaldiRecognizer

try:
    from rapidfuzz import fuzz
except Exception:
    fuzz = None

# -------------------------
# Config (tune here if needed)
# -------------------------
MODEL_DIR = os.getenv("VOSK_MODEL_DIR", "vosk-model-small-en-us-0.15")

WAKE_NAME = "DEMERZEL"
WAKE_ALIASES = [
    "demerzel", "demersel", "demers", "dammers", "damers", "dam ezell", "dam ezel", "damazell", "demer zell"
]
WAKE_THRESHOLD = 78  # 0-100 fuzzy match; raise = fewer false wakes

COMMAND_WINDOW_SEC = 5.0
FOLLOWUP_WINDOW_SEC = 7.0
CONFIRM_WINDOW_SEC = 8.0

SAMPLE_RATE = 16000
CHANNELS = 1
FRAMES_PER_BUFFER = 8000  # chunk size; larger reduces CPU
SILENCE_END_SEC = 0.85    # how long without new words before we end capture

MEMORY_PATH = "brain_memory.json"  # simple local persistence

# -------------------------
# Utilities
# -------------------------
def now_iso() -> str:
    return datetime.datetime.now().isoformat(timespec="seconds")

def speak(text: str) -> None:
    """macOS TTS (say). Safe fallback to print if say fails."""
    text = (text or "").strip()
    if not text:
        return
    try:
        subprocess.run(["say", text], check=False)
    except Exception:
        pass
    print(f"[SAY] {text}", flush=True)

def beep() -> None:
    # Terminal bell; not perfect but gives a quick acknowledgement without extra deps.
    print("\a", end="", flush=True)

def safe_load_json(path: str, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def safe_write_json(path: str, data) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)

def normalize_text(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9\s']", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def fuzzy_score(a: str, b: str) -> int:
    a = normalize_text(a)
    b = normalize_text(b)
    if not a or not b:
        return 0
    if fuzz is None:
        # Very rough fallback if rapidfuzz not installed
        return 100 if a == b else (80 if a in b or b in a else 0)
    return int(fuzz.ratio(a, b))

def best_wake_match(text: str) -> Tuple[str, int]:
    """
    Check wake on sliding n-grams of the recognized text so we can match
    "dam ezell" / "dammers" etc inside longer phrases.
    """
    t = normalize_text(text)
    if not t:
        return ("", 0)

    words = t.split()
    candidates = []
    # 1-3 word n-grams near the end are most relevant
    for n in (1, 2, 3):
        for i in range(max(0, len(words) - 6), len(words)):
            gram = " ".join(words[i:i+n]).strip()
            if gram:
                candidates.append(gram)

    best_alias = ""
    best_score = 0
    for c in candidates:
        for alias in WAKE_ALIASES:
            sc = fuzzy_score(c, alias)
            if sc > best_score:
                best_score = sc
                best_alias = alias
    return (best_alias, best_score)

# -------------------------
# Memory
# -------------------------
@dataclass
class Task:
    id: int
    text: str
    done: bool = False
    ts: str = field(default_factory=now_iso)

@dataclass
class BrainMemory:
    tasks: List[Task] = field(default_factory=list)
    turn_index: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tasks": [task.__dict__ for task in self.tasks],
            "turn_index": self.turn_index,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "BrainMemory":
        bm = BrainMemory()
        bm.turn_index = int(d.get("turn_index", 0))
        tasks = d.get("tasks", []) or []
        for t in tasks:
            bm.tasks.append(Task(
                id=int(t.get("id", 0)),
                text=str(t.get("text", "")),
                done=bool(t.get("done", False)),
                ts=str(t.get("ts", now_iso()))
            ))
        return bm

    def next_task_id(self) -> int:
        return (max([t.id for t in self.tasks], default=0) + 1)

    def add_task(self, text: str) -> Task:
        task = Task(id=self.next_task_id(), text=text.strip(), done=False)
        self.tasks.append(task)
        return task

    def list_open(self) -> List[Task]:
        return [t for t in self.tasks if not t.done]

    def complete_task(self, task_id: int) -> Optional[Task]:
        for t in self.tasks:
            if t.id == task_id:
                t.done = True
                return t
        return None

    def complete_latest(self) -> Optional[Task]:
        open_tasks = self.list_open()
        if not open_tasks:
            return None
        # latest open = highest id (simple)
        t = sorted(open_tasks, key=lambda x: x.id)[-1]
        t.done = True
        return t

# -------------------------
# Intent parsing (simple + deterministic)
# -------------------------
def interpret_command(text: str) -> Dict[str, Any]:
    raw = (text or "").strip()
    t = normalize_text(raw)

    # time
    if re.search(r"\b(what\s+time|time\s+is\s+it|current\s+time)\b", t):
        return {"intent": "time", "confidence": 0.9, "raw": raw, "payload": {}}

    # list tasks
    if re.search(r"\b(what\s+are\s+my\s+tasks|list\s+tasks|my\s+tasks|open\s+tasks|tasks)\b", t):
        return {"intent": "list_tasks", "confidence": 0.9, "raw": raw, "payload": {}}

    # remember task
    m = re.search(r"\b(remember|add)\b\s+(.*)$", t)
    if m and m.group(2).strip():
        return {"intent": "remember_task", "confidence": 0.9, "raw": raw, "payload": {"text": m.group(2).strip()}}

    # complete task <id>
    m2 = re.search(r"\b(complete|done|finish)\b\s+(task\s+)?(\d+)\b", t)
    if m2:
        return {"intent": "complete_task", "confidence": 0.9, "raw": raw, "payload": {"id": int(m2.group(3))}}

    # complete latest
    if re.search(r"\b(complete|done|finish)\b\s+(latest|last)\b", t):
        return {"intent": "complete_latest", "confidence": 0.9, "raw": raw, "payload": {}}

    # confirm/cancel (for confirm window)
    if t == "confirm" or t == "confirmed":
        return {"intent": "confirm", "confidence": 1.0, "raw": raw, "payload": {}}
    if t == "cancel" or t == "cancelled":
        return {"intent": "cancel", "confidence": 1.0, "raw": raw, "payload": {}}

    return {"intent": "unknown", "confidence": 0.3, "raw": raw, "payload": {}}

# -------------------------
# Audio + Vosk
# -------------------------
class VoskMic:
    def __init__(self, model_dir: str):
        if not os.path.isdir(model_dir):
            raise FileNotFoundError(
                f"Vosk model folder not found: {model_dir}\n"
                f"Set VOSK_MODEL_DIR or download/unzip a model into that path."
            )
        self.model = Model(model_dir)
        self.p = pyaudio.PyAudio()
        self.stream = None

    def start(self):
        if self.stream:
            return
        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=CHANNELS,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=FRAMES_PER_BUFFER,
        )
        self.stream.start_stream()

    def stop(self):
        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except Exception:
                pass
            self.stream = None
        try:
            self.p.terminate()
        except Exception:
            pass

    def listen_stream(self):
        """Generator of raw audio bytes."""
        self.start()
        while True:
            data = self.stream.read(FRAMES_PER_BUFFER, exception_on_overflow=False)
            yield data

def capture_utterance(mic: VoskMic, seconds: float) -> str:
    """
    Capture an utterance for up to `seconds`, ending early if we stop getting new final text
    for SILENCE_END_SEC.
    """
    rec = KaldiRecognizer(mic.model, SAMPLE_RATE)
    rec.SetWords(False)

    t_end = time.time() + seconds
    last_text_time = time.time()
    final_text = ""

    for chunk in mic.listen_stream():
        now = time.time()
        if now > t_end:
            break

        if rec.AcceptWaveform(chunk):
            result = json.loads(rec.Result() or "{}")
            txt = (result.get("text") or "").strip()
            if txt:
                final_text = txt
                last_text_time = now
                print(f"[FINAL] {txt}", flush=True)
        else:
            pres = json.loads(rec.PartialResult() or "{}")
            ptxt = (pres.get("partial") or "").strip()
            if ptxt:
                print(f"[partial] {ptxt}", flush=True)

        if final_text and (now - last_text_time) >= SILENCE_END_SEC:
            break

    # flush
    try:
        result = json.loads(rec.FinalResult() or "{}")
        txt = (result.get("text") or "").strip()
        if txt:
            final_text = txt
            print(f"[FINAL] {txt}", flush=True)
    except Exception:
        pass

    return final_text.strip()

def listen_for_wake(mic: VoskMic) -> Tuple[str, str, int]:
    """
    Idle loop: keep listening and fire when we detect wake.
    Returns: (heard_text, best_alias, score)
    """
    rec = KaldiRecognizer(mic.model, SAMPLE_RATE)
    rec.SetWords(False)

    for chunk in mic.listen_stream():
        if rec.AcceptWaveform(chunk):
            result = json.loads(rec.Result() or "{}")
            txt = (result.get("text") or "").strip()
            if not txt:
                continue
            alias, sc = best_wake_match(txt)
            print(f"[HEARD] {txt}", flush=True)
            if sc >= WAKE_THRESHOLD:
                return (txt, alias, sc)
        else:
            pres = json.loads(rec.PartialResult() or "{}")
            ptxt = (pres.get("partial") or "").strip()
            if ptxt:
                # keep partials quiet-ish
                pass

    return ("", "", 0)

# -------------------------
# Demerzel Brain Loop
# -------------------------
class Demerzel:
    def __init__(self):
        self.mic = VoskMic(MODEL_DIR)
        self.mem = BrainMemory.from_dict(safe_load_json(MEMORY_PATH, {}))
        self.pending_confirmation: Optional[Dict[str, Any]] = None
        self.running = True

    def save(self):
        safe_write_json(MEMORY_PATH, self.mem.to_dict())

    def respond(self, text: str):
        speak(text)

    def deliberate(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Return action dict: {speak: str, actions: [..], needs_confirm: bool, confirm_prompt: str, apply: {...}}"""
        name = intent.get("intent")
        payload = intent.get("payload", {}) or {}

        if name == "time":
            now = datetime.datetime.now()
            return {"speak": f"It is {now.strftime('%-I:%M %p')}.", "actions": [], "needs_confirm": False}

        if name == "list_tasks":
            open_tasks = self.mem.list_open()
            if not open_tasks:
                return {"speak": "You have no open tasks.", "actions": [], "needs_confirm": False}
            if len(open_tasks) == 1:
                t = open_tasks[0]
                return {"speak": f"You have 1 open task. Task {t.id}: {t.text}.", "actions": [], "needs_confirm": False}
            items = ", ".join([f"{t.id}: {t.text}" for t in open_tasks[:5]])
            more = "" if len(open_tasks) <= 5 else f" And {len(open_tasks)-5} more."
            return {"speak": f"You have {len(open_tasks)} open tasks. {items}.{more}", "actions": [], "needs_confirm": False}

        if name == "remember_task":
            text = (payload.get("text") or "").strip()
            if not text:
                return {"speak": "Tell me what to remember.", "actions": [], "needs_confirm": False}
            # Confirmation step
            return {
                "speak": f"You want me to remember: {text}. Say confirm to save, or cancel.",
                "actions": [],
                "needs_confirm": True,
                "confirm_prompt": "Say exactly one word: confirm or cancel.",
                "apply": {"type": "add_task", "text": text}
            }

        if name == "complete_task":
            tid = payload.get("id")
            if not tid:
                return {"speak": "Which task number?", "actions": [], "needs_confirm": False}
            return {
                "speak": f"Complete task {tid}? Say confirm or cancel.",
                "actions": [],
                "needs_confirm": True,
                "confirm_prompt": "Say exactly one word: confirm or cancel.",
                "apply": {"type": "complete_task", "id": int(tid)}
            }

        if name == "complete_latest":
            return {
                "speak": "Complete your latest open task? Say confirm or cancel.",
                "actions": [],
                "needs_confirm": True,
                "confirm_prompt": "Say exactly one word: confirm or cancel.",
                "apply": {"type": "complete_latest"}
            }

        return {"speak": "I heard you, but I don't have an action for that yet.", "actions": [], "needs_confirm": False}

    def apply_confirmed(self, apply: Dict[str, Any]) -> str:
        t = apply.get("type")
        if t == "add_task":
            task = self.mem.add_task(apply.get("text", ""))
            self.save()
            return f"Saved. Task {task.id}: {task.text}."
        if t == "complete_task":
            task = self.mem.complete_task(int(apply.get("id", 0)))
            self.save()
            if task:
                return f"Completed task {task.id}: {task.text}."
            return "I couldn't find that task."
        if t == "complete_latest":
            task = self.mem.complete_latest()
            self.save()
            if task:
                return f"Completed task {task.id}: {task.text}."
            return "You have no open tasks."
        return "Nothing to apply."

    def confirm_window(self) -> bool:
        """
        Listen ONLY for 'confirm' or 'cancel' for CONFIRM_WINDOW_SEC.
        Returns True if confirmed, False otherwise.
        """
        print(f"\n[CONFIRM] Say EXACTLY one word: 'confirm' or 'cancel' ({int(CONFIRM_WINDOW_SEC)}s)\n", flush=True)
        heard = capture_utterance(self.mic, CONFIRM_WINDOW_SEC)
        it = interpret_command(heard)
        if it["intent"] == "confirm":
            print("\n=== DECISION ===\nCONFIRM ✅\n", flush=True)
            return True
        print("\n=== DECISION ===\nCANCEL ❌\n", flush=True)
        return False

    def command_turn(self, window_sec: float) -> bool:
        """
        One command attempt during a command/followup window.
        Returns True if we handled something that should keep followup alive, else False.
        """
        heard = capture_utterance(self.mic, window_sec)
        if not heard:
            self.respond("No command heard.")
            return False

        intent = interpret_command(heard)
        self.mem.turn_index += 1

        # Print structured intent for debugging
        event = {
            "ts": now_iso(),
            "source": "voice",
            "wake": {"name": WAKE_NAME},
            "raw_text": heard,
            "normalized": normalize_text(heard),
            "intent_type": intent["intent"],
            "payload": intent.get("payload", {}),
        }
        print("\n[INTENT]", json.dumps(event, indent=2), "\n", flush=True)

        plan = self.deliberate(intent)
        self.respond(plan.get("speak", ""))

        if plan.get("needs_confirm"):
            confirmed = self.confirm_window()
            if confirmed:
                msg = self.apply_confirmed(plan.get("apply", {}))
                self.respond(msg)
            else:
                self.respond("Cancelled.")
            return True

        # Non-confirming intents still count as handled
        return True

    def run(self):
        print(f"[RUN] Demerzel running. Say '{WAKE_NAME}' to wake. Ctrl+C to stop.")
        print(f"[WAKE] threshold={WAKE_THRESHOLD} aliases={len(WAKE_ALIASES)}")
        print(f"[CMD] command_window={COMMAND_WINDOW_SEC}s followup_window={FOLLOWUP_WINDOW_SEC}s confirm_window={CONFIRM_WINDOW_SEC}s\n")

        while self.running:
            # IDLE: wait for wake
            heard, alias, sc = listen_for_wake(self.mic)
            if not self.running:
                break

            print(f"\n=== WAKE === name={WAKE_NAME} heard='{heard}' best_alias='{alias}' score={sc}\n", flush=True)
            beep()
            speak("Awake.")
            speak("Listening.")

            # COMMAND WINDOW (first command requires wake)
            handled = self.command_turn(COMMAND_WINDOW_SEC)

            # FOLLOWUP WINDOW (lets you say next thing without wake word)
            # If you keep talking, we keep giving you a short follow-up window.
            follow_deadline = time.time() + FOLLOWUP_WINDOW_SEC
            while time.time() < follow_deadline:
                print(f"\n[STATE] FOLLOWUP ({int(follow_deadline - time.time())}s left)\n", flush=True)
                ok = self.command_turn(FOLLOWUP_WINDOW_SEC)
                if not ok:
                    break
                # If we successfully handled something, refresh the followup deadline once.
                follow_deadline = time.time() + FOLLOWUP_WINDOW_SEC

            print("\n[IDLE] Back to wake listening.\n", flush=True)

def main():
    d = Demerzel()

    def handle_sigint(sig, frame):
        d.running = False
        print("\n[STOP] Ctrl+C received. Exiting cleanly.\n", flush=True)
        try:
            d.mic.stop()
        except Exception:
            pass
        raise SystemExit(0)

    signal.signal(signal.SIGINT, handle_sigint)

    try:
        d.run()
    finally:
        try:
            d.mic.stop()
        except Exception:
            pass

if __name__ == "__main__":
    main()

