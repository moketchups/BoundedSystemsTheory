#!/usr/bin/env python3
import json
import queue
import re
import subprocess
import sys
import threading
import time
from datetime import datetime
from difflib import SequenceMatcher

import sounddevice as sd
from vosk import Model, KaldiRecognizer

# =========================
# Step 7: Demerzel Gate v7
# - Half-duplex (don't listen while speaking)
# - Simple state machine: IDLE -> ACK -> COMMAND -> ACT -> IDLE
# - Robust wake-name matching (aliases + fuzzy)
# =========================

# ----- Settings -----
MODEL_PATH = "models/vosk-model-small-en-us-0.15"
SAMPLE_RATE = 16000
BLOCKSIZE = 8000  # audio chunk size
DEVICE = None     # set to int index if needed, else default input device

# Wake configuration
WAKE_CANON = "DEMERZEL"
# Add common mishears you observed (feel free to add more later)
WAKE_ALIASES = [
    "demerzel",
    "dem erzell",
    "dem ezell",
    "dam ezell",
    "damm ezell",
    "dammers",
    "damerzel",
    "demers",
    "demersel",
    "demmers",
]

WAKE_THRESHOLD = 0.72   # lower = easier to wake (more false wakes)
WAKE_COOLDOWN_S = 1.0   # prevents immediate re-wake spam

# Command configuration
COMMAND_WINDOW_S = 6.0  # how long we listen for command after wake
POST_SPEAK_DEAF_S = 0.6 # extra "deaf" time after speaking (echo protection)

# --------------------------
# Helpers: text normalization
# --------------------------
_word_re = re.compile(r"[a-z0-9]+")

def normalize_text(s: str) -> str:
    s = s.lower()
    words = _word_re.findall(s)
    return " ".join(words)

def sim(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()

def best_wake_match(text_norm: str, aliases_norm: list[str]) -> dict:
    """
    Returns best match dict:
    { "best_alias": str, "score": float, "span": str }
    We search:
      - full text vs alias
      - sliding window (1..3 words) vs alias
    """
    if not text_norm:
        return {"best_alias": "", "score": 0.0, "span": ""}

    words = text_norm.split()
    best = {"best_alias": "", "score": 0.0, "span": ""}

    # Full-text compare
    for a in aliases_norm:
        sc = sim(text_norm, a)
        if sc > best["score"]:
            best = {"best_alias": a, "score": sc, "span": text_norm}

    # Sliding windows (1..3 words)
    for n in (1, 2, 3):
        for i in range(0, max(0, len(words) - n + 1)):
            span = " ".join(words[i:i+n])
            for a in aliases_norm:
                sc = sim(span, a)
                if sc > best["score"]:
                    best = {"best_alias": a, "score": sc, "span": span}

    return best

# --------------------------
# Half-duplex "say" on macOS
# --------------------------
class Speaker:
    def __init__(self):
        self._lock = threading.Lock()
        self._speaking_until = 0.0

    def is_deaf(self) -> bool:
        # We treat "speaking" + a small tail as deaf time
        return time.time() < self._speaking_until

    def say(self, text: str):
        text = (text or "").strip()
        if not text:
            return

        with self._lock:
            # Mark deaf for duration estimate + tail
            # (we can't perfectly know duration; we approximate)
            est = max(0.6, min(6.0, 0.06 * len(text)))
            self._speaking_until = time.time() + est + POST_SPEAK_DEAF_S

            print(f"[SAY] {text}")
            try:
                # macOS built-in TTS
                subprocess.run(["say", text], check=False)
            except Exception as e:
                print(f"[SAY-ERROR] {e}")

            # Extend a little after completion to avoid capturing the tail
            self._speaking_until = max(self._speaking_until, time.time() + POST_SPEAK_DEAF_S)

# --------------------------
# Intent parsing (simple)
# --------------------------
def parse_intent(cmd_norm: str) -> dict:
    """
    Returns:
      {"intent_type": str, "payload": dict}
    """
    if not cmd_norm:
        return {"intent_type": "none", "payload": {}}

    # Time
    if re.search(r"\b(what time is it|time)\b", cmd_norm):
        return {"intent_type": "time", "payload": {}}

    # Remember
    # "remember this buy milk" -> remember "buy milk"
    m = re.search(r"\bremember (this )?(?P<note>.+)\b", cmd_norm)
    if m:
        note = m.group("note").strip()
        return {"intent_type": "remember", "payload": {"note": note}}

    # Open Google (placeholder action)
    if re.search(r"\b(open google|google)\b", cmd_norm):
        return {"intent_type": "open_google", "payload": {}}

    return {"intent_type": "unknown", "payload": {"text": cmd_norm}}

def handle_intent(intent: dict) -> tuple[str, dict]:
    """
    Returns (spoken_response, extra_result_dict)
    """
    it = intent.get("intent_type", "unknown")

    if it == "time":
        now = datetime.now().strftime("%-I:%M %p")
        return f"It is {now}.", {"time": now}

    if it == "remember":
        note = intent.get("payload", {}).get("note", "").strip()
        if not note:
            return "What should I remember?", {"saved": False}
        # For now we only confirm; later we’ll persist to a file/db.
        return f"Okay. I'll remember: {note}.", {"saved": True, "note": note}

    if it == "open_google":
        # We don't actually open anything yet—just confirm.
        return "Okay. I can open Google once we wire actions.", {"wired": False}

    if it == "none":
        return "I didn't catch a command.", {}

    # unknown
    return "I heard you, but I don't have an action for that yet.", {"heard": intent.get("payload", {}).get("text", "")}

# --------------------------
# Audio / Vosk
# --------------------------
def main():
    print(f"[RUN] Demerzel Step 7 running. Say '{WAKE_CANON}' to wake. Ctrl+C to stop.")
    model = Model(MODEL_PATH)
    rec = KaldiRecognizer(model, SAMPLE_RATE)
    rec.SetWords(True)

    q = queue.Queue()
    speaker = Speaker()

    aliases_norm = [normalize_text(a) for a in WAKE_ALIASES]
    last_wake_t = 0.0

    # state variables
    state = "IDLE"
    command_deadline = 0.0
    last_final_text = ""

    def audio_callback(indata, frames, time_info, status):
        # Drop audio while we are speaking / in deaf period
        if speaker.is_deaf():
            return
        if status:
            # Non-fatal; print and continue
            print(f"[AUDIO] {status}", file=sys.stderr)
        q.put(bytes(indata))

    try:
        with sd.RawInputStream(
            samplerate=SAMPLE_RATE,
            blocksize=BLOCKSIZE,
            dtype="int16",
            channels=1,
            callback=audio_callback,
            device=DEVICE,
        ):
            print("[STATE] IDLE (wake listening)")

            while True:
                data = q.get()

                # If we became deaf mid-queue, flush stale audio quickly
                if speaker.is_deaf():
                    while not q.empty():
                        try:
                            q.get_nowait()
                        except queue.Empty:
                            break
                    continue

                if rec.AcceptWaveform(data):
                    res = json.loads(rec.Result() or "{}")
                    final_text = (res.get("text") or "").strip()
                    final_norm = normalize_text(final_text)

                    if final_text:
                        print(f"FINAL: {final_text}")
                        last_final_text = final_text

                    now = time.time()

                    # -------------------------
                    # State: IDLE (wake detect)
                    # -------------------------
                    if state == "IDLE":
                        if now - last_wake_t < WAKE_COOLDOWN_S:
                            continue

                        m = best_wake_match(final_norm, aliases_norm)
                        if m["score"] >= WAKE_THRESHOLD:
                            # We woke
                            last_wake_t = now
                            heard = m["span"]
                            best_alias = m["best_alias"]
                            print(f"=== WAKE === name={WAKE_CANON} heard='{heard}' best_alias='{best_alias}' score={m['score']:.3f}")

                            # A: super fast acknowledgement
                            speaker.say("Awake.")

                            # B: open command window
                            state = "COMMAND"
                            command_deadline = time.time() + COMMAND_WINDOW_S
                            print("[STATE] COMMAND (listening window)")
                            continue

                    # -------------------------
                    # State: COMMAND
                    # -------------------------
                    if state == "COMMAND":
                        # If time expired, return to idle
                        if time.time() > command_deadline:
                            print("[IDLE] Command window expired. Back to wake listening.")
                            state = "IDLE"
                            continue

                        # Ignore empty finals
                        if not final_norm:
                            continue

                        # IMPORTANT: prevent the wake-word itself from being treated as a command
                        m = best_wake_match(final_norm, aliases_norm)
                        if m["score"] >= WAKE_THRESHOLD and len(final_norm.split()) <= 3:
                            # user probably just repeated wake name; keep waiting
                            print("[COMMAND] Heard wake-like phrase; still waiting for a command...")
                            continue

                        intent = parse_intent(final_norm)

                        # Print intent object (for debugging / visibility)
                        intent_obj = {
                            "ts": datetime.now().isoformat(timespec="seconds"),
                            "source": "voice",
                            "wake": {
                                "name": WAKE_CANON,
                            },
                            "raw_text": final_text,
                            "normalized": final_norm,
                            "intent_type": intent.get("intent_type"),
                            "payload": intent.get("payload", {}),
                        }
                        print("[INTENT]")
                        print(json.dumps(intent_obj, indent=2))

                        # Act + speak result
                        response, extra = handle_intent(intent)
                        speaker.say(response)

                        # Done — back to IDLE
                        print("[IDLE] Back to wake listening.")
                        state = "IDLE"
                        continue

                else:
                    # Partial result (optional; can be noisy)
                    pres = json.loads(rec.PartialResult() or "{}")
                    p = (pres.get("partial") or "").strip()
                    if p:
                        print(f"partial: {p}")

    except KeyboardInterrupt:
        print("\n[STOP] Ctrl+C received. Exiting cleanly.")
        return


if __name__ == "__main__":
    main()

