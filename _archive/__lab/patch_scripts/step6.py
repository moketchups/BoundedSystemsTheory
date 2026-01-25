#!/usr/bin/env python3

import os
import sys
import json
import queue
import time
import re
import sounddevice as sd
from difflib import SequenceMatcher
from vosk import Model, KaldiRecognizer

# =========================
# CONFIG
# =========================
WAKE_CANON = "DEMERZEL"
WAKE_ALIASES = [
    "demerzel",
    "damers",
    "dammers",
    "dem erzell",
    "dam ezell",
    "dam ezel",
    "dam ers ell",
]

SAMPLE_RATE = 16000
MODEL_PATH = "models/vosk-model-small-en-us-0.15"

# =========================
# AUDIO QUEUE
# =========================
audio_q = queue.Queue()

def audio_callback(indata, frames, time_info, status):
    if status:
        print(status, file=sys.stderr)
    audio_q.put(bytes(indata))

# =========================
# UTILITIES
# =========================
def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def normalize(text):
    return re.sub(r"[^a-z0-9 ]+", "", text.lower()).strip()

def best_wake_match(text):
    text = normalize(text)
    best = ("", 0.0)
    for alias in WAKE_ALIASES:
        s = similarity(text, alias)
        if s > best[1]:
            best = (alias, s)
    return best

def say(text):
    os.system(f'say "{text}"')

# =========================
# MAIN LOOP
# =========================
def main():
    print("[RUN] Demerzel Step 6 running. Say 'Demerzel' to wake. Ctrl+C to stop.")

    model = Model(MODEL_PATH)
    rec = KaldiRecognizer(model, SAMPLE_RATE)
    rec.SetWords(True)

    with sd.RawInputStream(
        samplerate=SAMPLE_RATE,
        blocksize=8000,
        dtype="int16",
        channels=1,
        callback=audio_callback,
    ):
        awake = False
        last_wake = 0

        try:
            while True:
                data = audio_q.get()
                if rec.AcceptWaveform(data):
                    res = json.loads(rec.Result())
                    text = res.get("text", "").strip()
                    if not text:
                        continue

                    print(f"FINAL: {text}")

                    # =========================
                    # WAKE CHECK
                    # =========================
                    if not awake:
                        alias, score = best_wake_match(text)
                        if score >= 0.72:
                            awake = True
                            last_wake = time.time()
                            print(f"=== WAKE === name={WAKE_CANON} heard='{text}' match='{alias}' score={round(score,3)}")
                            print("A: Awake.")
                            say("Yes?")
                        continue

                    # =========================
                    # COMMAND MODE
                    # =========================
                    print("B: Listening for command...")

                    intent = normalize(text)

                    if "what time" in intent:
                        now = time.strftime("%I:%M %p").lstrip("0")
                        print("[INTENT] time")
                        say(f"It is {now}")
                    else:
                        print("[NO COMMAND DETECTED]")
                        say("I heard you, but I don't have an action for that yet.")

                    awake = False
                    print("[IDLE] Back to wake listening.")

                else:
                    partial = json.loads(rec.PartialResult()).get("partial", "")
                    if partial:
                        print(f"partial: {partial}")

        except KeyboardInterrupt:
            print("\n[STOP] Ctrl+C received. Exiting cleanly.")
            return

# =========================
# ENTRY
# =========================
if __name__ == "__main__":
    main()

