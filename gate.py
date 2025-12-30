#!/usr/bin/env python3
import json
import os
import queue
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from difflib import SequenceMatcher

import sounddevice as sd
from vosk import Model, KaldiRecognizer


# =========================
# SETTINGS (safe defaults)
# =========================
WAKE_CANON = "DEMERZEL"

# What Vosk might hear instead of "Demerzel"
# Add your own over time if you want, but this list is already enough to prove the structure.
WAKE_ALIASES = [
    "demerzel",
    "dem erzell",
    "dem ezell",
    "dam ezell",
    "dammers",
    "demers",
    "dem erzel",
    "demersel",
    "demer zell",
    "dammerzel",
]

# Fuzzy matching threshold for wake name (0..1)
WAKE_FUZZY_THRESHOLD = 0.78

# Cooldown after a wake to prevent re-waking instantly
WAKE_COOLDOWN_SEC = 1.2

# After wake, how long we listen for the command
COMMAND_WINDOW_SEC = 4.0

# If no new audio results come in for this long during command capture, we end early
COMMAND_SILENCE_EARLY_END_SEC = 1.2

# Optional: choose audio input device via env var (integer index)
# Example: INPUT_DEVICE=0 python gate.py
INPUT_DEVICE_ENV = os.getenv("INPUT_DEVICE", "").strip()

# Optional: if you want less noise, set to 0 to hide partials
PRINT_PARTIALS = 1


# =========================
# Helpers
# =========================
def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def normalize_text(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def best_fuzzy_score(text_norm: str) -> tuple[float, str]:
    """
    Returns (best_score, best_alias) comparing normalized text against aliases.
    We compare both:
      - whole string similarity
      - token-window similarity (handles phrases like "dam ezell wake up")
    """
    if not text_norm:
        return 0.0, ""

    aliases = [normalize_text(a) for a in WAKE_ALIASES] + [normalize_text(WAKE_CANON)]
    best = (0.0, "")

    # Whole-string similarity
    for a in aliases:
        score = SequenceMatcher(None, text_norm, a).ratio()
        if score > best[0]:
            best = (score, a)

    # Token-window similarity
    toks = text_norm.split()
    for a in aliases:
        a_toks = a.split()
        if not a_toks:
            continue
        w = len(a_toks)
        if len(toks) < w:
            continue
        for i in range(0, len(toks) - w + 1):
            window = " ".join(toks[i : i + w])
            score = SequenceMatcher(None, window, a).ratio()
            if score > best[0]:
                best = (score, a)

    return best


def looks_like_wake(text: str) -> tuple[bool, dict]:
    """
    Decide if text indicates wake. Returns (is_wake, details)
    """
    raw = (text or "").strip()
    norm = normalize_text(raw)

    best_score, best_alias = best_fuzzy_score(norm)
    is_wake = best_score >= WAKE_FUZZY_THRESHOLD

    details = {
        "raw": raw,
        "normalized": norm,
        "best_alias": best_alias,
        "score": round(best_score, 2),
        "threshold": WAKE_FUZZY_THRESHOLD,
    }
    return is_wake, details


def make_intent(raw_text: str, wake_meta: dict) -> dict:
    norm = normalize_text(raw_text or "")
    return {
        "ts": now_iso(),
        "source": "voice",
        "wake": wake_meta,
        "raw_text": (raw_text or "").strip(),
        "normalized": norm,
    }


def print_intent(intent: dict) -> None:
    # Very obvious, copy/paste-friendly
    print("\n[INTENT]", flush=True)
    print(json.dumps(intent, ensure_ascii=False), flush=True)


# =========================
# Audio plumbing
# =========================
q_audio: "queue.Queue[bytes]" = queue.Queue()


def audio_callback(indata, frames, time_info, status):
    if status:
        # Keep running; just show the status
        print(f"[audio] {status}", file=sys.stderr, flush=True)
    q_audio.put(bytes(indata))


@dataclass
class WakeMeta:
    name: str
    heard: str
    match: str
    score: float

    def as_dict(self):
        return {
            "name": self.name,
            "heard": self.heard,
            "match": self.match,
            "score": round(self.score, 2),
        }


def choose_input_device():
    if INPUT_DEVICE_ENV:
        try:
            return int(INPUT_DEVICE_ENV)
        except ValueError:
            pass
    # default device chosen by sounddevice
    return None


# =========================
# Core loop
# =========================
def main():
    model_path = os.getenv("VOSK_MODEL_PATH", "models/vosk-model-small-en-us-0.15")
    if not os.path.isdir(model_path):
        print(f"[FATAL] Vosk model folder not found: {model_path}")
        print("Set VOSK_MODEL_PATH or put the model under models/ as expected.")
        sys.exit(1)

    print(f"[BOOT] Loading Vosk model from: {model_path}", flush=True)
    model = Model(model_path)

    device = choose_input_device()

    # 16k is typical for Vosk; sounddevice will handle conversion if needed
    samplerate = 16000

    rec = KaldiRecognizer(model, samplerate)
    rec.SetWords(True)

    last_wake_time = 0.0
    in_command_mode = False

    wake_meta = None  # WakeMeta
    command_started = 0.0
    last_result_time = 0.0
    command_buffer = []

    print(f"[RUN] {WAKE_CANON} gate running. Say '{WAKE_CANON}' to wake. Press Ctrl+C to stop.", flush=True)

    try:
        with sd.RawInputStream(
            samplerate=samplerate,
            blocksize=8000,
            dtype="int16",
            channels=1,
            callback=audio_callback,
            device=device,
        ):
            while True:
                data = q_audio.get()

                # Feed recognizer
                is_final = rec.AcceptWaveform(data)

                if PRINT_PARTIALS and not is_final:
                    partial = rec.PartialResult()
                    try:
                        p = json.loads(partial).get("partial", "")
                    except Exception:
                        p = ""
                    if p:
                        print(f"partial: {p}", flush=True)
                    continue

                if is_final:
                    result = rec.Result()
                    try:
                        text = json.loads(result).get("text", "")
                    except Exception:
                        text = ""

                    text = (text or "").strip()
                    if not text:
                        continue

                    print(f"FINAL: {text}", flush=True)
                    now_t = time.time()

                    if not in_command_mode:
                        # WAKE LISTENING
                        if (now_t - last_wake_time) < WAKE_COOLDOWN_SEC:
                            continue

                        is_wake, details = looks_like_wake(text)

                        if is_wake:
                            last_wake_time = now_t
                            wake_meta = WakeMeta(
                                name=WAKE_CANON,
                                heard=details["raw"],
                                match=details["best_alias"],
                                score=details["score"],
                            )

                            print(
                                f"\n=== WAKE === name={wake_meta.name} heard='{wake_meta.heard}' match='{wake_meta.match}' score={wake_meta.score:.2f}",
                                flush=True,
                            )

                            # A then B (A must be very quick)
                            print("A: Awake.", flush=True)
                            print("B: Listening for command...", flush=True)

                            # Enter command mode
                            in_command_mode = True
                            command_started = now_t
                            last_result_time = now_t
                            command_buffer = []
                        else:
                            # Not a wake. Keep listening.
                            continue

                    else:
                        # COMMAND MODE: everything becomes an intent object
                        last_result_time = now_t
                        command_buffer.append(text)

                        # If the user says the wake name again during command mode, ignore it (don’t re-wake)
                        # We only care about collecting content for intent.
                        # We’ll end the window by time/silence, not by keyword.

                # Handle command-mode timing outside final-only branch too
                if in_command_mode:
                    now_t = time.time()
                    elapsed = now_t - command_started
                    since_last = now_t - last_result_time

                    if elapsed >= COMMAND_WINDOW_SEC or since_last >= COMMAND_SILENCE_EARLY_END_SEC:
                        raw_cmd = " ".join(command_buffer).strip()

                        # ALWAYS emit an intent object in Step 3, even if empty.
                        # Empty just means: user didn’t say anything meaningful in the window.
                        intent = make_intent(raw_cmd, wake_meta.as_dict() if wake_meta else {})
                        print_intent(intent)

                        # Return to wake listening
                        print("[IDLE] Back to wake listening.\n", flush=True)
                        in_command_mode = False
                        wake_meta = None
                        command_buffer = []

    except KeyboardInterrupt:
        print("\n[STOP] Ctrl+C received. Exiting cleanly.", flush=True)
        return


if __name__ == "__main__":
    main()
