#!/usr/bin/env python3
import os
import re
import time
import json
import queue
import subprocess
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, Any, List, Tuple
from difflib import SequenceMatcher

import sounddevice as sd
from vosk import Model, KaldiRecognizer

# ============================================================
# Demerzel Step 11: TURN-TAKING LOCK (offline)
# Goal:
#   - One wake -> one command -> one resolution
#   - Never listen while speaking
#   - Confirming is a hard lock: only confirm/cancel accepted
#   - No wake triggers during LISTENING/THINKING/RESPONDING/CONFIRMING
# ============================================================

# ---------- Wake settings ----------
WAKE_NAME = "demerzel"
WAKE_ALIASES = [
    "demerzel", "dammers", "damers", "dammerz", "dam ezell", "dem ezell", "dem ezel",
]
WAKE_THRESHOLD = 0.72
WAKE_COOLDOWN_S = 1.0

# ---------- Command capture ----------
CMD_START_GRACE_S = 4.0
CMD_END_SILENCE_S = 0.9
CMD_MAX_S = 7.0

# ---------- Confirm lock ----------
CONFIRM_TIMEOUT_S = 10.0

# ---------- Audio / Vosk ----------
SAMPLE_RATE = 16000
BLOCKSIZE = 8000
MODEL_DIR = os.path.join(os.path.dirname(__file__), "models", "vosk-model-small-en-us-0.15")

# ---------- TTS ----------
def say(text: str):
    text = (text or "").strip()
    if not text:
        return
    try:
        subprocess.run(["say", text], check=False)
    except Exception:
        pass

# ---------- Simple beep ----------
def beep():
    # Using macOS beep (no audio libs needed)
    try:
        subprocess.run(["printf", "\a"], check=False)
    except Exception:
        pass

# ---------- Text helpers ----------
def norm(s: str) -> str:
    s = (s or "").lower().strip()
    s = re.sub(r"[^a-z0-9\s']", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def sim(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()

def wake_score(text: str) -> Tuple[str, float]:
    t = norm(text)
    best_alias, best_score = "", 0.0

    for alias in WAKE_ALIASES + [WAKE_NAME]:
        a = norm(alias)
        if not a:
            continue
        # containment shortcut
        if a in t:
            score = 1.0
        else:
            score = sim(t, a)
        if score > best_score:
            best_score = score
            best_alias = a

    # also scan windows (handles "dammers what time is it")
    words = t.split()
    for alias in WAKE_ALIASES + [WAKE_NAME]:
        a = norm(alias)
        aw = a.split()
        n = len(aw)
        if n == 0:
            continue
        for i in range(0, max(1, len(words) - n + 1)):
            window = " ".join(words[i:i+n])
            score = sim(window, a)
            if score > best_score:
                best_score = score
                best_alias = a

    return best_alias, best_score

# ---------- Brain-lite intents (only for proof of turnlock) ----------
def parse_intent(text: str) -> Dict[str, Any]:
    t = norm(text)

    if not t:
        return {"intent": "none"}

    # confirm/cancel variants
    if any(w in t.split() for w in ["confirm", "confirmed", "yes", "yeah", "yep", "save", "ok", "okay"]):
        return {"intent": "confirm"}
    if "never mind" in t or "nevermind" in t or any(w in t.split() for w in ["cancel", "no", "stop", "abort"]):
        return {"intent": "cancel"}

    if "what time" in t or t == "time":
        return {"intent": "time"}

    m = re.search(r"\bremember\b\s+(.*)$", t)
    if m:
        payload = m.group(1).strip()
        return {"intent": "remember", "text": payload}

    if "what are my tasks" in t or "list tasks" in t or "my tasks" == t:
        return {"intent": "list_tasks"}

    return {"intent": "unknown", "raw": text}

# ---------- Turn lock state machine ----------
class Mode(str, Enum):
    IDLE = "IDLE"               # only wake listening
    WAKING = "WAKING"           # brief ack
    LISTENING = "LISTENING"     # capture one command
    THINKING = "THINKING"       # decide response
    CONFIRMING = "CONFIRMING"   # hard lock confirm/cancel
    RESPONDING = "RESPONDING"   # speaking (mic ignored)

@dataclass
class TurnLock:
    mode: Mode = Mode.IDLE
    last_wake_ts: float = 0.0
    # command window
    cmd_started_ts: float = 0.0
    cmd_last_voice_ts: float = 0.0
    cmd_buffer: str = ""
    # confirm lock
    pending: Optional[Dict[str, Any]] = None
    confirm_deadline: float = 0.0

    def set_mode(self, m: Mode):
        self.mode = m
        print(f"[MODE] -> {m.value}")

# ---------- Main ----------
def main():
    if not os.path.isdir(MODEL_DIR):
        print(f"[ERROR] Missing Vosk model at: {MODEL_DIR}")
        print("Put your model in ./models/vosk-model-small-en-us-0.15")
        sys.exit(1)

    model = Model(MODEL_DIR)
    rec = KaldiRecognizer(model, SAMPLE_RATE)
    rec.SetWords(False)

    q = queue.Queue()
    lock = TurnLock()

    def cb(indata, frames, time_info, status):
        q.put(bytes(indata))

    print("[RUN] turnlock.py running (offline). Say 'Demerzel' to wake. Ctrl+C to stop.")
    print("[RULES] one wake -> one command. No listening while speaking. Confirm is a lock.")
    print(f"[WAKE] threshold={WAKE_THRESHOLD} aliases={len(WAKE_ALIASES)}")

    try:
        with sd.RawInputStream(
            samplerate=SAMPLE_RATE,
            blocksize=BLOCKSIZE,
            dtype="int16",
            channels=1,
            callback=cb
        ):
            while True:
                data = q.get()
                now = time.time()

                # CONFIRM timeout
                if lock.mode == Mode.CONFIRMING and now > lock.confirm_deadline:
                    lock.pending = None
                    lock.set_mode(Mode.RESPONDING)
                    say("Timed out. Canceling.")
                    lock.set_mode(Mode.IDLE)

                # We DO NOT accept wake triggers unless IDLE.
                # We also ignore mic input during RESPONDING (hard rule).
                if lock.mode == Mode.RESPONDING:
                    # Drain recognizer but do nothing
                    rec.AcceptWaveform(data)
                    continue

                if rec.AcceptWaveform(data):
                    res = json.loads(rec.Result() or "{}")
                    final_text = (res.get("text") or "").strip()
                    if final_text:
                        print(f"FINAL: {final_text}")

                    # ========== MODE: IDLE (wake only) ==========
                    if lock.mode == Mode.IDLE:
                        if (now - lock.last_wake_ts) < WAKE_COOLDOWN_S:
                            continue
                        alias, score = wake_score(final_text)
                        if alias and score >= WAKE_THRESHOLD:
                            lock.last_wake_ts = now
                            print(f"=== WAKE === heard='{final_text}' best='{alias}' score={score:.3f}")

                            # A then B: fast ack then listening
                            lock.set_mode(Mode.WAKING)
                            beep()
                            lock.set_mode(Mode.RESPONDING)
                            say("Awake.")
                            lock.set_mode(Mode.RESPONDING)
                            say("Listening.")
                            lock.set_mode(Mode.LISTENING)

                            lock.cmd_started_ts = now
                            lock.cmd_last_voice_ts = 0.0
                            lock.cmd_buffer = ""
                            continue

                    # ========== MODE: LISTENING (one command) ==========
                    if lock.mode == Mode.LISTENING:
                        # Grace: user must start speaking within CMD_START_GRACE_S
                        if lock.cmd_last_voice_ts == 0.0:
                            if norm(final_text):
                                lock.cmd_last_voice_ts = now
                                lock.cmd_buffer = final_text
                            else:
                                if (now - lock.cmd_started_ts) > CMD_START_GRACE_S:
                                    lock.set_mode(Mode.RESPONDING)
                                    say("No command heard.")
                                    lock.set_mode(Mode.IDLE)
                                    continue
                        else:
                            if norm(final_text):
                                lock.cmd_last_voice_ts = now
                                lock.cmd_buffer = (lock.cmd_buffer + " " + final_text).strip()

                        # silence end OR hard max window
                        if lock.cmd_last_voice_ts != 0.0:
                            if (now - lock.cmd_last_voice_ts) > CMD_END_SILENCE_S or (now - lock.cmd_started_ts) > CMD_MAX_S:
                                command = lock.cmd_buffer.strip()
                                print(f"[COMMAND] {command}")
                                lock.set_mode(Mode.THINKING)

                                intent = parse_intent(command)
                                print("[INTENT]", intent)

                                # Minimal action demo to prove turn discipline:
                                if intent["intent"] == "time":
                                    tm = time.strftime("%-I:%M %p")
                                    lock.set_mode(Mode.RESPONDING)
                                    say(f"It is {tm}.")
                                    lock.set_mode(Mode.IDLE)

                                elif intent["intent"] == "remember":
                                    txt = (intent.get("text") or "").strip()
                                    if not txt:
                                        lock.set_mode(Mode.RESPONDING)
                                        say("What should I remember?")
                                        lock.set_mode(Mode.IDLE)
                                    else:
                                        lock.pending = {"type": "remember", "text": txt}
                                        lock.confirm_deadline = time.time() + CONFIRM_TIMEOUT_S
                                        lock.set_mode(Mode.CONFIRMING)
                                        lock.set_mode(Mode.RESPONDING)
                                        say(f"You want me to remember: {txt}. Say confirm or cancel.")
                                        lock.set_mode(Mode.CONFIRMING)

                                elif intent["intent"] == "list_tasks":
                                    lock.set_mode(Mode.RESPONDING)
                                    say("Tasks are handled by the Brain module. This file only proves turn taking.")
                                    lock.set_mode(Mode.IDLE)

                                else:
                                    lock.set_mode(Mode.RESPONDING)
                                    say("I heard you.")
                                    lock.set_mode(Mode.IDLE)

                                continue

                    # ========== MODE: CONFIRMING (lock) ==========
                    if lock.mode == Mode.CONFIRMING:
                        # In confirming, ONLY accept confirm/cancel, ignore everything else
                        intent = parse_intent(final_text)

                        if intent["intent"] == "confirm":
                            pending = lock.pending
                            lock.pending = None
                            lock.set_mode(Mode.RESPONDING)
                            say("Confirmed.")
                            # (In real system: apply pending actions to Brain)
                            lock.set_mode(Mode.IDLE)

                        elif intent["intent"] == "cancel":
                            lock.pending = None
                            lock.set_mode(Mode.RESPONDING)
                            say("Canceled.")
                            lock.set_mode(Mode.IDLE)

                        else:
                            lock.set_mode(Mode.RESPONDING)
                            say("Say confirm or cancel.")
                            lock.set_mode(Mode.CONFIRMING)

                else:
                    # Partial results are ignored for actions (we only act on FINAL)
                    pres = json.loads(rec.PartialResult() or "{}")
                    p = (pres.get("partial") or "").strip()
                    if p:
                        print(f"partial: {p}")

    except KeyboardInterrupt:
        print("\n[STOP] Exiting.")

if __name__ == "__main__":
    main()

