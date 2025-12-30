#!/usr/bin/env python3
import os
import sys
import time
import json
import math
import queue
import signal
import sqlite3
import subprocess
from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple
from difflib import SequenceMatcher

import pyaudio
from vosk import Model, KaldiRecognizer

from brain_contract import BrainContract


# ----------------------------
# Config (matches your logs vibe)
# ----------------------------
WAKE_NAME = "DEMERZEL"
WAKE_ALIASES = ["demerzel", "damers", "dam ezell", "dam ezzel", "dam brazil"]
WAKE_THRESHOLD = 0.78

COMMAND_WINDOW = 5.0
FOLLOWUP_WINDOW = 7.0
CONFIRM_WINDOW = 8.0

ECHO_GUARD_SEC = 1.2
SILENCE_RESET_SEC = 0.9  # not strict VAD; just helps reset state
SIMILARITY_DROP = 0.78   # used to ignore repeated same phrase if it’s “echo-ish”

SAMPLE_RATE = 16000
CHANNELS = 1
FRAMES_PER_BUFFER = 4000

MODEL_DIR_CANDIDATES = [
    "vosk-model-small-en-us-0.15",
    "models/vosk-model-small-en-us-0.15",
]


# ----------------------------
# Helpers
# ----------------------------
def now_ts() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())

def norm_text(s: str) -> str:
    s = (s or "").strip().lower()
    # keep letters/numbers/spaces
    out = []
    for ch in s:
        if ch.isalnum() or ch.isspace():
            out.append(ch)
    return " ".join("".join(out).split())

def similarity(a: str, b: str) -> float:
    a = norm_text(a)
    b = norm_text(b)
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()

def best_wake_match(text: str) -> Tuple[str, float]:
    t = norm_text(text)
    best_alias = ""
    best_score = 0.0
    for alias in WAKE_ALIASES + [WAKE_NAME.lower()]:
        sc = similarity(t, alias)
        if sc > best_score:
            best_score = sc
            best_alias = alias
    return best_alias, best_score

def mac_say(msg: str):
    msg = (msg or "").strip()
    if not msg:
        return
    # macOS built-in TTS
    try:
        subprocess.run(["say", msg], check=False)
    except Exception:
        # fail silently if say is unavailable
        pass

def mac_beep():
    # quick, dependable “ack”
    sys.stdout.write("\a")
    sys.stdout.flush()

def find_model_dir() -> str:
    for d in MODEL_DIR_CANDIDATES:
        if os.path.isdir(d):
            return d
    raise FileNotFoundError(
        "Could not find Vosk model directory. Expected one of: "
        + ", ".join(MODEL_DIR_CANDIDATES)
    )


# ----------------------------
# Intent parsing (Step 13 only needs time, but we detect others to deny)
# ----------------------------
def parse_intent(final_text: str) -> Tuple[str, Dict[str, Any]]:
    t = norm_text(final_text)

    if not t:
        return "unknown", {"raw": final_text}

    # time
    if "time" in t and ("what" in t or "tell" in t or t == "time"):
        return "time", {}

    # remember/task-ish (will be denied by contract in step 13)
    if t.startswith("remember "):
        payload = {"text": t.replace("remember", "", 1).strip()}
        return "remember_task", payload

    if "what are my tasks" in t or "list tasks" in t or "my tasks" == t:
        return "list_tasks", {}

    if t.startswith("complete task"):
        # naive parse: "complete task 1"
        parts = t.split()
        tid = None
        for p in parts:
            if p.isdigit():
                tid = int(p)
                break
        return "complete_task", {"id": tid}

    if t in ("confirm", "confirmed"):
        return "confirm", {}

    if t in ("cancel", "never mind", "nevermind"):
        return "cancel", {}

    return "unknown", {"raw": final_text}


# ----------------------------
# Main loop
# ----------------------------
@dataclass
class State:
    attention: str = "IDLE"  # IDLE / COMMAND / FOLLOWUP / CONFIRMING
    last_heard_final: str = ""
    last_heard_time: float = 0.0
    pending_confirmation: Optional[Dict[str, Any]] = None
    last_action_spoken_at: float = 0.0


def main():
    model_dir = find_model_dir()
    model = Model(model_dir)
    rec = KaldiRecognizer(model, SAMPLE_RATE)
    rec.SetWords(True)

    contract = BrainContract()
    st = State()

    pa = pyaudio.PyAudio()
    stream = pa.open(
        format=pyaudio.paInt16,
        channels=CHANNELS,
        rate=SAMPLE_RATE,
        input=True,
        frames_per_buffer=FRAMES_PER_BUFFER,
    )
    stream.start_stream()

    print(f"[RUN] Demerzel Step 13 running. Say '{WAKE_NAME}' to wake. Ctrl+C to stop.")
    print(f"[WAKE] threshold={WAKE_THRESHOLD} aliases={len(WAKE_ALIASES) + 1}")
    print(f"[CMD] command_window={COMMAND_WINDOW:.1f}s followup_window={FOLLOWUP_WINDOW:.1f}s confirm_window={CONFIRM_WINDOW:.1f}s")
    print(f"[ECHO] guard={ECHO_GUARD_SEC:.1f}s similarity_drop={SIMILARITY_DROP:.2f}")

    stop_flag = {"stop": False}

    def handle_sigint(sig, frame):
        stop_flag["stop"] = True
    signal.signal(signal.SIGINT, handle_sigint)

    def set_state(new_state: str):
        st.attention = new_state

    def in_echo_guard() -> bool:
        return (time.time() - st.last_action_spoken_at) < ECHO_GUARD_SEC

    def speak(msg: str):
        st.last_action_spoken_at = time.time()
        print(f"[SAY] {msg}")
        mac_say(msg)

    # timers
    command_deadline = 0.0
    followup_deadline = 0.0
    confirm_deadline = 0.0

    try:
        while not stop_flag["stop"]:
            data = stream.read(FRAMES_PER_BUFFER, exception_on_overflow=False)

            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                final_text = result.get("text", "").strip()

                if final_text:
                    print(f"FINAL: {final_text}")

                # echo-ish drop: if we just spoke and the recognizer “hears” the TTS back, ignore very-similar repeats
                if final_text and in_echo_guard():
                    if similarity(final_text, st.last_heard_final) >= SIMILARITY_DROP:
                        continue

                # track last
                if final_text:
                    st.last_heard_final = final_text
                    st.last_heard_time = time.time()

                # --- IDLE: wait for wake ---
                if st.attention == "IDLE":
                    if not final_text:
                        continue

                    alias, score = best_wake_match(final_text)
                    if score >= WAKE_THRESHOLD:
                        print(f"=== WAKE === name={WAKE_NAME} heard='{alias}' best_alias='{alias}' score={score:.3f}")
                        mac_beep()
                        speak("Awake.")
                        speak("Listening.")
                        set_state("COMMAND")
                        command_deadline = time.time() + COMMAND_WINDOW
                    continue

                # --- COMMAND window: interpret intent ---
                if st.attention == "COMMAND":
                    if time.time() > command_deadline:
                        print("[COMMAND MODE] (no command started — window timeout)")
                        speak("No command heard.")
                        set_state("IDLE")
                        continue

                    if not final_text:
                        continue

                    intent_type, payload = parse_intent(final_text)

                    # Log intent packet like your prints
                    pkt = {
                        "ts": now_ts(),
                        "source": "voice",
                        "wake": {"name": WAKE_NAME},
                        "raw_text": final_text,
                        "normalized": norm_text(final_text),
                        "intent_type": intent_type,
                        "payload": payload,
                    }
                    print("[INTENT]")
                    print(json.dumps(pkt, indent=2))

                    decision = contract.check(intent_type, payload)

                    if not decision.allowed:
                        # Step 13 fix: never silent on deny/unknown
                        speak(decision.speak or "No.")
                        set_state("IDLE")
                        continue

                    # Allowed actions (Step 13: only time)
                    if intent_type == "time":
                        # local time
                        speak(time.strftime("It is %I:%M %p.", time.localtime()).lstrip("0"))
                        set_state("FOLLOWUP")
                        followup_deadline = time.time() + FOLLOWUP_WINDOW
                        continue

                    # fallback (shouldn't happen due to contract)
                    speak("No.")
                    set_state("IDLE")
                    continue

                # --- FOLLOWUP window (Step 13: still strict; anything else denied) ---
                if st.attention == "FOLLOWUP":
                    if time.time() > followup_deadline:
                        set_state("IDLE")
                        print("[IDLE] Back to wake listening.")
                        continue

                    if not final_text:
                        continue

                    intent_type, payload = parse_intent(final_text)

                    pkt = {
                        "ts": now_ts(),
                        "source": "voice",
                        "wake": {"name": WAKE_NAME},
                        "raw_text": final_text,
                        "normalized": norm_text(final_text),
                        "intent_type": intent_type,
                        "payload": payload,
                    }
                    print("[INTENT]")
                    print(json.dumps(pkt, indent=2))

                    decision = contract.check(intent_type, payload)
                    if not decision.allowed:
                        speak(decision.speak or "No.")
                        set_state("IDLE")
                        continue

                    if intent_type == "time":
                        speak(time.strftime("It is %I:%M %p.", time.localtime()).lstrip("0"))
                        followup_deadline = time.time() + FOLLOWUP_WINDOW
                        continue

                    speak("No.")
                    set_state("IDLE")
                    continue

            else:
                # partial results (nice for debugging like your logs)
                pres = json.loads(rec.PartialResult())
                p = pres.get("partial", "").strip()
                if p:
                    print(f"partial: {p}")

                # timeout checks even without final speech
                if st.attention == "COMMAND" and time.time() > command_deadline:
                    print("[COMMAND MODE] (no command started — window timeout)")
                    speak("No command heard.")
                    set_state("IDLE")

                if st.attention == "FOLLOWUP" and time.time() > followup_deadline:
                    set_state("IDLE")
                    print("[IDLE] Back to wake listening.")

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
        print("\n[STOP] Ctrl+C received. Exiting cleanly.")


if __name__ == "__main__":
    main()
