#!/usr/bin/env python3
import os, json, time, re, queue, datetime, subprocess, difflib

import numpy as np
import sounddevice as sd
from vosk import Model, KaldiRecognizer

# =========================
# Step 4: Route + Respond
# =========================

# --- Wake identity (canonical name) ---
WAKE_CANON = "DEMERZEL"

# Common mishears we already saw; add more over time.
# IMPORTANT: This is only used for matching; we always report name=DEMERZEL.
WAKE_ALIASES = [
    "demerzel",
    "dem ezell",
    "dam ezell",
    "dammers",
    "dam mers",
    "demers",
    "dammerz",
    "damers",
]

# How "close" it must be to count as wake (0..1). Lower = more permissive.
WAKE_THRESHOLD = 0.78

# After wake, how long we listen for the command (seconds)
COMMAND_WINDOW_S = 4.0

# Pick an input device index (None = default)
INPUT_DEVICE = None

# Vosk model path
MODEL_PATH = os.environ.get("VOSK_MODEL_PATH", "models/vosk-model-small-en-us-0.15")

# -------------------------
# Utilities
# -------------------------

def now_iso():
    return datetime.datetime.now().replace(microsecond=0).isoformat()

def normalize_text(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9\s']", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def best_wake_match(heard: str):
    """
    Returns (match_string, score) using difflib similarity.
    We compare heard against aliases.
    """
    h = normalize_text(heard)
    if not h:
        return ("", 0.0)
    best = ("", 0.0)
    for alias in WAKE_ALIASES:
        a = normalize_text(alias)
        score = difflib.SequenceMatcher(None, h, a).ratio()
        if score > best[1]:
            best = (a, score)
    return best

def say(text: str):
    """
    macOS built-in TTS. If it fails, we still print.
    """
    text = (text or "").strip()
    if not text:
        return
    print(f'[SAY] {text}')
    try:
        subprocess.run(["say", text], check=False)
    except Exception:
        pass

def route_intent(raw_text: str):
    """
    Very simple router. We can expand later.
    Returns: (intent_type, response_text, payload_dict)
    """
    t = normalize_text(raw_text)

    # time
    if re.search(r"\bwhat time\b|\btime is it\b|\bcurrent time\b", t):
        tm = datetime.datetime.now().strftime("%-I:%M %p")
        return ("time", f"It is {tm}.", {"query": t, "time": tm})

    # remember
    m = re.search(r"\bremember (this|that)\b\s*(.*)", t)
    if m:
        note = (m.group(2) or "").strip()
        if not note:
            note = t
        return ("remember", "Okay. I'll remember that.", {"note": note})

    # default
    return ("unknown", "Okay. I heard you.", {"text": t})

# -------------------------
# Audio + Vosk
# -------------------------

q = queue.Queue()

def audio_callback(indata, frames, time_info, status):
    if status:
        # status is fine to ignore; we print for debugging
        print(status)
    q.put(bytes(indata))

def listen_once(recognizer, seconds: float):
    """
    Listen for up to `seconds` and return the best FINAL text we get (or "").
    """
    end = time.time() + seconds
    final_text = ""

    while time.time() < end:
        try:
            data = q.get(timeout=0.2)
        except queue.Empty:
            continue

        if recognizer.AcceptWaveform(data):
            res = json.loads(recognizer.Result() or "{}")
            txt = res.get("text", "") or ""
            if txt:
                final_text = txt
                # We keep listening until timeout so you can finish speaking.
        else:
            pres = json.loads(recognizer.PartialResult() or "{}")
            p = pres.get("partial", "") or ""
            if p:
                # Optional: comment this out if it’s too noisy
                print(f"partial: {p}")

    return final_text.strip()

def main():
    if not os.path.isdir(MODEL_PATH):
        print(f"[ERROR] Vosk model folder not found: {MODEL_PATH}")
        print("Expected something like: models/vosk-model-small-en-us-0.15/")
        return 2

    print("[RUN] Step 4: Demerzel gate + route + speak")
    print("Say 'Demerzel' to wake. Ctrl+C to stop.")

    model = Model(MODEL_PATH)

    # Use one recognizer for wake, one for command (keeps logic clean)
    wake_rec = KaldiRecognizer(model, 16000)
    cmd_rec  = KaldiRecognizer(model, 16000)

    with sd.RawInputStream(
        samplerate=16000,
        blocksize=8000,
        dtype="int16",
        channels=1,
        callback=audio_callback,
        device=INPUT_DEVICE
    ):
        while True:
            # --- Wake phase: listen in short bursts ---
            wake_text = listen_once(wake_rec, seconds=1.2)
            wake_text_n = normalize_text(wake_text)

            if not wake_text_n:
                continue

            match, score = best_wake_match(wake_text_n)

            if score >= WAKE_THRESHOLD:
                # A then B (very quick A)
                print(f"=== WAKE === name={WAKE_CANON} heard='{wake_text_n}' match='{match}' score={score:.2f}")
                say("Awake.")
                say("Listening.")

                # Command window
                cmd_text = listen_once(cmd_rec, seconds=COMMAND_WINDOW_S)
                cmd_text_n = normalize_text(cmd_text)

                if not cmd_text_n:
                    print("[NO COMMAND DETECTED]")
                    say("I didn't catch a command.")
                    print("[IDLE] Back to wake listening.")
                    continue

                intent_type, response_text, payload = route_intent(cmd_text_n)

                intent_obj = {
                    "ts": now_iso(),
                    "source": "voice",
                    "wake": {
                        "name": WAKE_CANON,
                        "heard": wake_text_n,
                        "match": match,
                        "score": round(score, 3),
                    },
                    "raw_text": cmd_text,
                    "normalized": cmd_text_n,
                    "intent_type": intent_type,
                    "payload": payload,
                }

                print("[INTENT]")
                print(json.dumps(intent_obj, indent=2))

                # Speak response (this is the new “alive” part)
                say(response_text)

                print("[IDLE] Back to wake listening.")

            # else: not close enough to wake; ignore

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\n[STOP] Ctrl+C received. Exiting cleanly.")
