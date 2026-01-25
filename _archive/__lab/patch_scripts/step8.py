#!/usr/bin/env python3
import json
import queue
import re
import time
import subprocess
from dataclasses import dataclass
from difflib import SequenceMatcher

import sounddevice as sd
from vosk import Model, KaldiRecognizer

# =========================
# Demerzel Step 8 (Echo-proof)
# - Wake -> quick Acknowledgement (beep + voice)
# - Command capture window that DOES NOT auto-close before you speak
# - Echo guard: ignore mic while Demerzel is speaking (prevents "awake listening" polluting commands)
# - Command cleanup: strips leading filler ("awake", "listening") before intent parsing
# - macOS voice replies via `say`
# =========================

MODEL_PATH = "models/vosk-model-small-en-us-0.15"
SAMPLE_RATE = 16000
BLOCK_SIZE = 8000

WAKE_CANON = "DEMERZEL"

WAKE_ALIASES = [
    "demerzel",
    "dam ezell",
    "dammers",
    "damers",
    "dem ezell",
    "dammerzel",
    "dam er zel",
    "dem er zel",
]

WAKE_THRESHOLD = 0.72
WAKE_COOLDOWN_SEC = 1.25

# After wake, time allowed to START speaking a command
COMMAND_START_GRACE_SEC = 4.0

# Once command speech starts, command ends after this much silence
END_SILENCE_SEC = 0.90

# Ignore mic for this long after Demerzel speaks (prevents self-hearing)
ECHO_GUARD_SEC = 1.2

PRINT_PARTIALS = True

_audio_q = queue.Queue()


def _audio_callback(indata, frames, time_info, status):
    _audio_q.put(bytes(indata))


def normalize_text(s: str) -> str:
    s = (s or "").lower().strip()
    s = re.sub(r"[^a-z0-9\s']", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def best_wake_match(heard: str):
    heard_n = normalize_text(heard)
    if not heard_n:
        return ("", 0.0)
    best = ("", 0.0)
    for alias in WAKE_ALIASES:
        a = normalize_text(alias)
        score = SequenceMatcher(None, heard_n, a).ratio()
        if score > best[1]:
            best = (alias, score)
    return best


def clean_command_text(raw: str) -> str:
    """
    Removes leading filler that commonly comes from Demerzel's own voice
    or user confirmations ("awake", "listening", etc.)
    """
    t = normalize_text(raw)

    # Strip repeated leading tokens like: "awake listening ..." or "listening ..."
    # Do this a few times in case it stacks.
    for _ in range(3):
        t = re.sub(r"^(awake|listening|okay|ok|yeah|yes|hey)\b\s*", "", t).strip()

    # Also handle the common exact prefix "awake listening"
    t = re.sub(r"^awake\s+listening\b\s*", "", t).strip()
    return t


def detect_intent(command_text: str):
    raw = command_text
    t = clean_command_text(raw)

    if not t:
        return ("none", {"raw": raw})

    if re.search(r"\bwhat time is it\b|\btime\b", t):
        return ("time", {"query": t})

    if t.startswith("remember ") or t.startswith("remember that "):
        # IMPORTANT: this step only *detects* the intent; actual secure storage is a later step.
        return ("remember", {"text": t})

    if t.startswith("open "):
        return ("open", {"target": t[5:].strip()})

    return ("unknown", {"raw": t})


def beep():
    print("\a", end="", flush=True)


def say(text: str):
    print(f"[SAY] {text}", flush=True)
    try:
        subprocess.run(["say", text], check=False)
    except Exception as e:
        print(f"[SAY-ERROR] {e}", flush=True)


@dataclass
class WakeInfo:
    name: str
    heard: str
    match: str
    score: float


def main():
    model = Model(MODEL_PATH)
    rec = KaldiRecognizer(model, SAMPLE_RATE)
    rec.SetWords(False)

    print(f"[RUN] Demerzel Step 8 running. Say '{WAKE_CANON}' to wake. Ctrl+C to stop.")
    print(f"[WAKE] threshold={WAKE_THRESHOLD:.2f} aliases={len(WAKE_ALIASES)} cooldown={WAKE_COOLDOWN_SEC:.2f}s")
    print(f"[CMD ] start_grace={COMMAND_START_GRACE_SEC:.2f}s end_silence={END_SILENCE_SEC:.2f}s")
    print(f"[ECHO] guard={ECHO_GUARD_SEC:.2f}s\n")

    state = "WAKE"
    last_wake_time = 0.0

    # COMMAND tracking
    cmd_finals = []
    command_started = False
    command_enter_time = 0.0
    last_activity_time = 0.0

    # Echo guard until timestamp (ignore recognition results until this time)
    ignore_until = 0.0

    def enter_command(wi: WakeInfo):
        nonlocal state, cmd_finals, command_started, command_enter_time, last_activity_time, ignore_until
        state = "COMMAND"
        cmd_finals = []
        command_started = False
        command_enter_time = time.time()
        last_activity_time = 0.0

        print(f"\n=== WAKE === name={wi.name} heard='{wi.heard}' match='{wi.match}' score={wi.score:.3f}")

        # A: very quick acknowledgement
        beep()
        say("Awake.")
        say("Listening.")

        # While Demerzel is speaking, the mic hears it.
        # So we ignore recognition output briefly and then reset recognizer.
        ignore_until = time.time() + ECHO_GUARD_SEC
        print("")

    def finish_command():
        nonlocal state, cmd_finals, command_started, command_enter_time, last_activity_time

        raw_command_text = " ".join(cmd_finals).strip()
        state = "WAKE"
        cmd_finals = []
        command_started = False
        command_enter_time = 0.0
        last_activity_time = 0.0

        cleaned_preview = clean_command_text(raw_command_text)

        if not cleaned_preview:
            print("[COMMAND MODE] heard: (nothing)")
            print("[IDLE] Back to wake listening.\n")
            return

        intent_type, payload = detect_intent(raw_command_text)

        intent_obj = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "source": "voice",
            "wake": {"name": WAKE_CANON},
            "raw_text": raw_command_text,
            "cleaned": cleaned_preview,
            "intent_type": intent_type,
            "payload": payload,
        }

        print("[INTENT]")
        print(json.dumps(intent_obj, indent=2))

        if intent_type == "time":
            say(f"It is {time.strftime('%-I:%M %p')}.")
        elif intent_type == "remember":
            # NOTE: You should NOT speak or store real secrets (garage codes, SSNs, etc.)
            # until we implement secure storage rules. For now we just acknowledge.
            say("Got it. I can remember that once storage is wired in.")
        elif intent_type == "open":
            say("I heard an open request. App launching comes next.")
        elif intent_type == "none":
            say("No command heard.")
        else:
            say("I heard you, but I don’t have an action for that yet.")

        print("[IDLE] Back to wake listening.\n")

    with sd.RawInputStream(
        samplerate=SAMPLE_RATE,
        blocksize=BLOCK_SIZE,
        dtype="int16",
        channels=1,
        callback=_audio_callback,
    ):
        try:
            while True:
                data = _audio_q.get()
                now = time.time()

                # During echo guard: keep feeding recognizer but ignore outputs
                if now < ignore_until:
                    rec.AcceptWaveform(data)
                    continue
                # Right after guard ends: reset once to clear any buffered "awake/listening"
                if ignore_until != 0.0 and now >= ignore_until:
                    rec.Reset()
                    ignore_until = 0.0

                if rec.AcceptWaveform(data):
                    res = json.loads(rec.Result())
                    final_text = (res.get("text") or "").strip()
                    if not final_text:
                        continue

                    if PRINT_PARTIALS:
                        print(f"FINAL: {final_text}")

                    now = time.time()

                    if state == "WAKE":
                        if now - last_wake_time < WAKE_COOLDOWN_SEC:
                            continue

                        best_alias, score = best_wake_match(final_text)
                        if score >= WAKE_THRESHOLD:
                            last_wake_time = now
                            enter_command(WakeInfo(WAKE_CANON, final_text, best_alias, score))

                    elif state == "COMMAND":
                        command_started = True
                        last_activity_time = now
                        cmd_finals.append(final_text)

                else:
                    pres = json.loads(rec.PartialResult())
                    partial = (pres.get("partial") or "").strip()
                    now = time.time()

                    if state == "COMMAND":
                        if partial:
                            command_started = True
                            last_activity_time = now
                            if PRINT_PARTIALS:
                                print(f"partial: {partial}")

                        # If user never starts speaking within grace window
                        if (not command_started) and (now - command_enter_time) >= COMMAND_START_GRACE_SEC:
                            print("[COMMAND MODE] (no command started — grace timeout)")
                            say("No command heard.")
                            print("[IDLE] Back to wake listening.\n")
                            state = "WAKE"
                            cmd_finals = []
                            command_started = False
                            command_enter_time = 0.0
                            last_activity_time = 0.0
                            continue

                        # If user started speaking, end when silence exceeded
                        if command_started and last_activity_time and (now - last_activity_time) >= END_SILENCE_SEC:
                            finish_command()

                    else:
                        if partial and PRINT_PARTIALS:
                            print(f"partial: {partial}")

        except KeyboardInterrupt:
            print("\n[STOP] Ctrl+C received. Exiting cleanly.")
            return


if __name__ == "__main__":
    main()

