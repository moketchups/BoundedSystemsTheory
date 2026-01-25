#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Demerzel — Step 12
Goal:
- Keep wake + command loop working
- Add echo suppression so Demerzel does NOT react to its own voice (TTS)
- Keep a follow-up window after speaking, but ignore self-echo during/after TTS

How it works:
- Uses Vosk + PyAudio for ASR (offline)
- Uses macOS `say` for TTS (reliable) with a fallback to pyttsx3 if present
- While speaking (and for a short guard window after), it ignores mic input
- Also drops recognized text that is too similar to the last phrase Demerzel spoke
"""

import os
import re
import sys
import json
import time
import queue
import difflib
import sqlite3
import threading
import subprocess
from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Tuple

import pyaudio
from vosk import Model, KaldiRecognizer

# -----------------------------
# Config (tune later if needed)
# -----------------------------
MODEL_DIR = "vosk-model-small-en-us-0.15"   # folder in your project
SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK = 4000

WAKE_NAME = "demerzel"
WAKE_ALIASES = [
    "demerzel", "demers", "dammers", "damers", "dammerz", "dam ezell", "dam ezel", "dam brazil"
]

WAKE_SCORE_THRESHOLD = 0.78   # similarity threshold for wake phrase
COMMAND_WINDOW_SEC = 5.0      # after wake, time to start speaking command
FOLLOWUP_WINDOW_SEC = 7.0     # after responding, time to accept a follow-up command
CONFIRM_WINDOW_SEC = 8.0      # confirm/cancel window for memory saving

# Echo suppression / guard
TTS_GUARD_SEC = 1.20          # ignore mic for this long AFTER TTS finishes
MIN_SPEAK_SEC = 0.35          # minimum assumed speak duration (safety)
CHAR_SIMILARITY_DROP = 0.78   # drop if recognized text is too similar to last spoken text

# Storage
DB_PATH = "demerzel_memory.db"

# -----------------------------
# Helpers
# -----------------------------

def now() -> float:
    return time.time()

def clean_text(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9\s']", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def similarity(a: str, b: str) -> float:
    a = clean_text(a)
    b = clean_text(b)
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(None, a, b).ratio()

def contains_wake(text: str) -> Tuple[bool, float, str]:
    """
    Returns: (is_wake, best_score, best_alias)
    Uses fuzzy similarity against known aliases.
    """
    t = clean_text(text)
    best = (False, 0.0, "")
    for alias in WAKE_ALIASES:
        sc = similarity(t, alias)
        if sc > best[1]:
            best = (sc >= WAKE_SCORE_THRESHOLD, sc, alias)
    return best

def beep():
    # macOS built-in sound (lightweight)
    try:
        subprocess.run(["/usr/bin/afplay", "/System/Library/Sounds/Pop.aiff"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    except Exception:
        pass

# -----------------------------
# Memory (simple task list)
# -----------------------------

def db_init():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            done INTEGER NOT NULL DEFAULT 0,
            ts REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def db_add_task(text: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO tasks(text, done, ts) VALUES (?, 0, ?)", (text, now()))
    conn.commit()
    conn.close()

def db_list_tasks(done: Optional[int] = 0) -> List[Tuple[int, str, int, float]]:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    if done is None:
        cur.execute("SELECT id, text, done, ts FROM tasks ORDER BY id ASC")
    else:
        cur.execute("SELECT id, text, done, ts FROM tasks WHERE done=? ORDER BY id ASC", (done,))
    rows = cur.fetchall()
    conn.close()
    return rows

def db_complete_task(task_id: int) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE tasks SET done=1 WHERE id=?", (task_id,))
    conn.commit()
    changed = cur.rowcount > 0
    conn.close()
    return changed

# -----------------------------
# Brain state
# -----------------------------

@dataclass
class BrainState:
    name: str = "Demerzel"
    attention_state: str = "IDLE"          # IDLE | WAKING | LISTENING | THINKING | RESPONDING | CONFIRMING
    mode: str = "WAKE"                     # WAKE | COMMAND | FOLLOWUP | CONFIRM
    window_deadline: float = 0.0

    last_input: str = ""
    last_intent: str = ""
    last_spoken: str = ""

    pending_confirmation: Optional[Dict[str, Any]] = None
    turn_index: int = 0

# -----------------------------
# TTS with echo suppression hooks
# -----------------------------

class Speaker:
    def __init__(self):
        self._lock = threading.Lock()
        self._speaking_until = 0.0
        self._last_spoken = ""
        self._tts_guard_until = 0.0

    def speaking(self) -> bool:
        return now() < self._speaking_until

    def guard_active(self) -> bool:
        return now() < self._tts_guard_until

    def last_spoken(self) -> str:
        with self._lock:
            return self._last_spoken

    def _set_spoken(self, text: str, estimated_dur: float):
        with self._lock:
            self._last_spoken = text
            # speaking until includes the estimated duration
            self._speaking_until = now() + max(MIN_SPEAK_SEC, estimated_dur)
            # guard window starts AFTER speaking finishes
            self._tts_guard_until = self._speaking_until + TTS_GUARD_SEC

    def say(self, text: str):
        """
        macOS `say` is the default (most reliable).
        We estimate duration from word count to keep suppression tight.
        """
        text = (text or "").strip()
        if not text:
            return

        # Rough estimate: 2.5 words/sec
        wc = max(1, len(clean_text(text).split()))
        estimated = wc / 2.5
        self._set_spoken(text, estimated)

        # Speak (blocking). While speaking, ASR loop is ignoring mic frames.
        try:
            subprocess.run(["/usr/bin/say", text], check=False)
        except Exception:
            # Fallback: try pyttsx3 if installed
            try:
                import pyttsx3  # type: ignore
                engine = pyttsx3.init()
                engine.say(text)
                engine.runAndWait()
            except Exception:
                # Worst case: silent
                pass

# -----------------------------
# Intent parsing (simple, deterministic)
# -----------------------------

def parse_intent(text: str) -> Dict[str, Any]:
    t = clean_text(text)

    # Confirm/cancel
    if t in ("confirm", "confirmed", "yes confirm", "save", "yes"):
        return {"intent": "confirm"}
    if t in ("cancel", "never mind", "nevermind", "no"):
        return {"intent": "cancel"}

    # Time
    if re.search(r"\bwhat\s+time\s+is\s+it\b", t) or t in ("time", "tell me the time"):
        return {"intent": "time"}

    # Remember task
    m = re.match(r"remember\s+(.+)$", t)
    if m:
        return {"intent": "remember_task", "text": m.group(1).strip()}

    # List tasks
    if t in ("what are my tasks", "list tasks", "tasks", "what are my task", "what do i have to do"):
        return {"intent": "list_tasks"}

    # Complete task
    m2 = re.match(r"(complete|done|finish)\s+task\s+(\d+)$", t)
    if m2:
        return {"intent": "complete_task", "id": int(m2.group(2))}

    return {"intent": "unknown", "raw": t}

# -----------------------------
# Main loop
# -----------------------------

def main():
    db_init()

    speaker = Speaker()
    brain = BrainState()

    # Load model
    if not os.path.isdir(MODEL_DIR):
        print(f"[FATAL] Missing Vosk model folder: {MODEL_DIR}")
        print("Put the model folder in your project directory, or change MODEL_DIR.")
        sys.exit(1)

    model = Model(MODEL_DIR)
    rec = KaldiRecognizer(model, SAMPLE_RATE)
    rec.SetWords(True)

    pa = pyaudio.PyAudio()
    stream = pa.open(
        format=pyaudio.paInt16,
        channels=CHANNELS,
        rate=SAMPLE_RATE,
        input=True,
        frames_per_buffer=CHUNK
    )
    stream.start_stream()

    print("\n[RUN] Demerzel Step 12 running. Say 'DEMERZEL' to wake. Ctrl+C to stop.")
    print(f"[WAKE] threshold={WAKE_SCORE_THRESHOLD} aliases={len(WAKE_ALIASES)}")
    print(f"[CMD] command_window={COMMAND_WINDOW_SEC:.1f}s followup_window={FOLLOWUP_WINDOW_SEC:.1f}s confirm_window={CONFIRM_WINDOW_SEC:.1f}s")
    print(f"[ECHO] guard={TTS_GUARD_SEC:.2f}s similarity_drop>={CHAR_SIMILARITY_DROP:.2f}\n")

    try:
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)

            # --- Echo suppression gate ---
            # If we are speaking OR within the guard window after TTS, ignore mic frames entirely.
            if speaker.speaking() or speaker.guard_active():
                continue

            if rec.AcceptWaveform(data):
                res = json.loads(rec.Result() or "{}")
                text = clean_text(res.get("text", ""))

                if not text:
                    continue

                # Drop if too similar to what we just spoke (extra safety)
                last_spoken = speaker.last_spoken()
                if last_spoken and similarity(text, last_spoken) >= CHAR_SIMILARITY_DROP:
                    # self-echo (or close enough) -> ignore silently
                    continue

                # Print final ASR
                print(f"FINAL: {text}")

                # 1) WAKE detection when in WAKE mode
                if brain.mode == "WAKE":
                    is_wake, score, alias = contains_wake(text)
                    if is_wake:
                        brain.attention_state = "WAKING"
                        brain.mode = "COMMAND"
                        brain.window_deadline = now() + COMMAND_WINDOW_SEC
                        brain.last_input = text
                        brain.turn_index += 1
                        print(f"=== WAKE === name={WAKE_NAME.upper()} heard='{text}' best_alias='{alias}' score={score:.3f}")
                        beep()
                        speaker.say("Awake.")
                        print("[STATE] COMMAND (listening window)")
                    continue

                # 2) If command window expired, drop back to wake
                if brain.mode in ("COMMAND", "FOLLOWUP") and now() > brain.window_deadline:
                    brain.mode = "WAKE"
                    brain.attention_state = "IDLE"
                    print("[IDLE] Back to wake listening (window timeout).")
                    continue

                # 3) CONFIRM mode
                if brain.mode == "CONFIRM":
                    intent = parse_intent(text)
                    if intent["intent"] == "confirm" and brain.pending_confirmation:
                        payload = brain.pending_confirmation
                        if payload.get("type") == "remember_task":
                            db_add_task(payload["text"])
                            speaker.say("Saved.")
                            print("[CONFIRM] Saved task.")
                        brain.pending_confirmation = None

                        # After confirm, allow a follow-up window
                        brain.mode = "FOLLOWUP"
                        brain.attention_state = "LISTENING"
                        brain.window_deadline = now() + FOLLOWUP_WINDOW_SEC
                        continue

                    if intent["intent"] == "cancel":
                        speaker.say("Canceled.")
                        print("[CONFIRM] Canceled.")
                        brain.pending_confirmation = None
                        brain.mode = "FOLLOWUP"
                        brain.attention_state = "LISTENING"
                        brain.window_deadline = now() + FOLLOWUP_WINDOW_SEC
                        continue

                    # Unknown inside confirm window: prompt once, keep window running
                    speaker.say("Say confirm to save, or cancel.")
                    continue

                # 4) COMMAND / FOLLOWUP mode intents
                brain.attention_state = "THINKING"
                intent = parse_intent(text)
                brain.last_input = text
                brain.last_intent = intent["intent"]
                brain.turn_index += 1

                # Build an event trace (useful debugging)
                event = {
                    "ts": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime()),
                    "phase": "INTERPRET",
                    "data": {"intent": intent["intent"], "raw": text}
                }
                print("[INTENT]", json.dumps(event, indent=2))

                # Handle intents
                if intent["intent"] == "time":
                    brain.attention_state = "RESPONDING"
                    tstr = time.strftime("%-I:%M %p")
                    speaker.say(f"It is {tstr}.")
                    brain.mode = "FOLLOWUP"
                    brain.attention_state = "LISTENING"
                    brain.window_deadline = now() + FOLLOWUP_WINDOW_SEC
                    print("[STATE] FOLLOWUP (listening window)")
                    continue

                if intent["intent"] == "remember_task":
                    # Require confirmation
                    brain.attention_state = "CONFIRMING"
                    brain.mode = "CONFIRM"
                    brain.window_deadline = now() + CONFIRM_WINDOW_SEC
                    brain.pending_confirmation = {"type": "remember_task", "text": intent["text"]}
                    speaker.say(f"You want me to remember: {intent['text']}. Say confirm to save, or cancel.")
                    print("[STATE] CONFIRM (awaiting confirm/cancel)")
                    continue

                if intent["intent"] == "list_tasks":
                    brain.attention_state = "RESPONDING"
                    tasks = db_list_tasks(done=0)
                    if not tasks:
                        speaker.say("You have no open tasks.")
                    else:
                        # Speak only a short summary to avoid long TTS
                        speaker.say(f"You have {len(tasks)} open task{'s' if len(tasks)!=1 else ''}.")
                        # Print full list to console
                        for tid, ttext, done, ts in tasks:
                            print(f"  - Task {tid}: {ttext}")
                    brain.mode = "FOLLOWUP"
                    brain.attention_state = "LISTENING"
                    brain.window_deadline = now() + FOLLOWUP_WINDOW_SEC
                    continue

                if intent["intent"] == "complete_task":
                    brain.attention_state = "RESPONDING"
                    ok = db_complete_task(intent["id"])
                    speaker.say("Completed." if ok else "I could not find that task.")
                    brain.mode = "FOLLOWUP"
                    brain.attention_state = "LISTENING"
                    brain.window_deadline = now() + FOLLOWUP_WINDOW_SEC
                    continue

                # Unknown
                brain.attention_state = "RESPONDING"
                speaker.say("I heard you, but I don't have an action for that yet.")
                brain.mode = "FOLLOWUP"
                brain.attention_state = "LISTENING"
                brain.window_deadline = now() + FOLLOWUP_WINDOW_SEC
                continue

            else:
                # partial result (optional)
                pres = json.loads(rec.PartialResult() or "{}")
                p = clean_text(pres.get("partial", ""))
                if p:
                    # Avoid spam; print short partials only
                    if len(p) <= 30:
                        print(f"partial: {p}")

    except KeyboardInterrupt:
        print("\n[STOP] Ctrl+C received. Exiting cleanly.")
    finally:
        try:
            stream.stop_stream()
            stream.close()
        except Exception:
            pass
        try:
            pa.terminate()
        except Exception:
            pass


if __name__ == "__main__":
    main()

