#!/usr/bin/env python3
import os
import re
import sys
import json
import time
import queue
import subprocess
from datetime import datetime
from difflib import SequenceMatcher

import sounddevice as sd
from vosk import Model, KaldiRecognizer

# =========================
# Step 5.1: Stronger wake matching (mishears -> canonical name)
# =========================

WAKE_CANON = "DEMERZEL"

# Common mishears (you can add more later, but you don't need to right now)
WAKE_ALIASES = [
    "demerzel",
    "dem er zel",
    "dem ezell",
    "dem ezel",
    "dam ezell",
    "dam ezel",
    "dammers",
    "damers",
    "demers",
    "dam mers",
    "dem mers",
    "demers l",
    "demmers",
]

# How strict should wake be?
# We combine several signals:
#  - similarity against aliases
#  - token/substring presence
#  - phonetic-ish simplification
WAKE_THRESHOLD = 0.84  # lower than before, but still guarded by multi-signal scoring

# Command listening
COMMAND_WINDOW_SECONDS = 4.0
SILENCE_TIMEOUT = 1.2

# Storage
MEMORY_FILE = os.path.join(os.path.dirname(__file__), "memory.json")

# Audio / Vosk
SAMPLE_RATE = 16000
BLOCK_SIZE = 8000
audio_q = queue.Queue()

def audio_callback(indata, frames, time_info, status):
    audio_q.put(bytes(indata))

def say(text: str):
    text = (text or "").strip()
    if not text:
        return
    try:
        subprocess.run(["say", text], check=False)
    except Exception:
        pass

def normalize_text(t: str) -> str:
    t = (t or "").lower().strip()
    t = re.sub(r"[^a-z0-9\s']", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t

def squeeze(t: str) -> str:
    """Aggressive simplification for matching: remove spaces, punctuation, repeated letters."""
    t = normalize_text(t)
    t = t.replace("'", "")
    t = re.sub(r"\s+", "", t)
    # collapse repeated letters: dammmers -> damers
    t2 = []
    prev = ""
    for ch in t:
        if ch != prev:
            t2.append(ch)
        prev = ch
    return "".join(t2)

def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()

def wake_score(heard_text: str):
    """
    Returns: (best_alias, score, heard_normalized)

    Score is a blend of:
      1) best similarity vs aliases (normalized)
      2) best similarity vs aliases (squeezed)
      3) substring/token bonuses for partial matches
    """
    heard_norm = normalize_text(heard_text)
    heard_sq = squeeze(heard_text)

    best_alias = ""
    best_sim_norm = 0.0
    best_sim_sq = 0.0

    for alias in WAKE_ALIASES:
        a_norm = normalize_text(alias)
        a_sq = squeeze(alias)

        best_sim_norm = max(best_sim_norm, similarity(heard_norm, a_norm))
        best_sim_sq = max(best_sim_sq, similarity(heard_sq, a_sq))

        # keep a representative alias (for printing)
        if best_sim_sq >= best_sim_sq:
            best_alias = alias

    # Token / substring bonuses
    bonus = 0.0
    tokens = heard_norm.split()

    # If it contains something close to "dem"/"dam" plus "zel"/"zell"/"mers"/"mers"
    if any(t in {"dem", "dam", "dems", "dams"} for t in tokens):
        bonus += 0.03
    if any(t in {"zel", "zell", "ezel", "ezell"} for t in tokens):
        bonus += 0.03
    if any(t in {"mers", "murs", "mersl", "dammers", "damers", "demers"} for t in tokens):
        bonus += 0.02

    # If squeezed contains "damer" or "demer" fragments
    if "demer" in heard_sq or "damer" in heard_sq:
        bonus += 0.04
    if "zel" in heard_sq or "zell" in heard_sq or "ezel" in heard_sq:
        bonus += 0.03

    # Final blended score:
    # - squeezed similarity tends to be the strongest for this kind of mishearing
    score = (0.55 * best_sim_sq) + (0.40 * best_sim_norm) + bonus
    score = min(1.0, score)

    # pick an alias to display: closest by squeezed similarity
    best_alias = max(WAKE_ALIASES, key=lambda a: similarity(heard_sq, squeeze(a)))
    return best_alias, score, heard_norm

def find_model_path():
    here = os.path.dirname(__file__)
    candidates = [
        os.path.join(here, "models", "vosk-model-small-en-us-0.15"),
        os.path.join(here, "vosk-model-small-en-us-0.15"),
        os.environ.get("VOSK_MODEL_PATH", "").strip() or None,
    ]
    for c in candidates:
        if c and os.path.isdir(c):
            return c
    return None

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return []
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []

def save_memory(items):
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(items, f, indent=2)
    except Exception:
        pass

def intent_from_command(cmd_raw: str):
    cmd = normalize_text(cmd_raw)

    if cmd in {"stop", "cancel", "never mind", "nevermind"}:
        return {"intent_type": "cancel", "payload": {}, "normalized": cmd, "raw_text": cmd_raw}

    if re.search(r"\b(what time is it|time)\b", cmd):
        return {"intent_type": "time", "payload": {}, "normalized": cmd, "raw_text": cmd_raw}

    if re.search(r"\bopen google\b", cmd):
        return {"intent_type": "open_url", "payload": {"url": "https://www.google.com"}, "normalized": cmd, "raw_text": cmd_raw}
    if re.search(r"\bopen youtube\b", cmd):
        return {"intent_type": "open_url", "payload": {"url": "https://www.youtube.com"}, "normalized": cmd, "raw_text": cmd_raw}
    if re.search(r"\bopen chatgpt\b", cmd):
        return {"intent_type": "open_url", "payload": {"url": "https://chatgpt.com"}, "normalized": cmd, "raw_text": cmd_raw}

    if re.search(r"\bopen notes\b", cmd):
        return {"intent_type": "open_app", "payload": {"app": "Notes"}, "normalized": cmd, "raw_text": cmd_raw}
    if re.search(r"\bopen calendar\b", cmd):
        return {"intent_type": "open_app", "payload": {"app": "Calendar"}, "normalized": cmd, "raw_text": cmd_raw}

    m = re.search(r"\bremember\s+(.*)$", cmd)
    if m and m.group(1).strip():
        return {"intent_type": "remember", "payload": {"text": m.group(1).strip()}, "normalized": cmd, "raw_text": cmd_raw}

    if re.search(r"\b(list notes|show notes|what did you remember)\b", cmd):
        return {"intent_type": "list_memory", "payload": {}, "normalized": cmd, "raw_text": cmd_raw}

    if re.search(r"\b(forget notes|clear notes|delete notes)\b", cmd):
        return {"intent_type": "clear_memory", "payload": {}, "normalized": cmd, "raw_text": cmd_raw}

    return {"intent_type": "unknown", "payload": {}, "normalized": cmd, "raw_text": cmd_raw}

def route_intent(intent: dict):
    itype = intent.get("intent_type")
    payload = intent.get("payload") or {}

    if itype == "cancel":
        say("Canceled.")
        return

    if itype == "time":
        now = datetime.now().strftime("%-I:%M %p")
        say(f"It is {now}.")
        print(f"[SAY] It is {now}.")
        return

    if itype == "open_url":
        url = payload.get("url", "")
        if url:
            say("Opening.")
            subprocess.run(["open", url], check=False)
            print(f"[ACTION] open url: {url}")
        else:
            say("I couldn't find the URL.")
        return

    if itype == "open_app":
        app = payload.get("app", "")
        if app in {"Notes", "Calendar"}:
            say(f"Opening {app}.")
            subprocess.run(["open", "-a", app], check=False)
            print(f"[ACTION] open app: {app}")
        else:
            say("That app is not allowed yet.")
        return

    if itype == "remember":
        text = (payload.get("text") or "").strip()
        if not text:
            say("I didn't catch what to remember.")
            return
        mem = load_memory()
        item = {"ts": datetime.now().isoformat(timespec="seconds"), "text": text}
        mem.append(item)
        save_memory(mem)
        say("Saved.")
        print(f"[MEMORY] saved: {item}")
        return

    if itype == "list_memory":
        mem = load_memory()
        if not mem:
            say("No notes yet.")
            print("[MEMORY] empty")
            return
        say(f"You have {len(mem)} notes.")
        print("[MEMORY] notes:")
        for i, item in enumerate(mem[-10:], start=max(1, len(mem)-9)):
            print(f"  {i}. {item.get('text')}  ({item.get('ts')})")
        return

    if itype == "clear_memory":
        save_memory([])
        say("Cleared.")
        print("[MEMORY] cleared")
        return

    say("I heard you, but I don't have an action for that yet.")
    print("[NO COMMAND DETECTED]")

def listen_for_command(cmd_rec: KaldiRecognizer) -> str:
    cmd_rec.Reset()
    start = time.time()
    last_voice = time.time()
    best_final = ""

    while (time.time() - start) < COMMAND_WINDOW_SECONDS:
        try:
            data = audio_q.get(timeout=0.25)
        except queue.Empty:
            data = None

        if not data:
            if best_final and (time.time() - last_voice) > SILENCE_TIMEOUT:
                break
            continue

        if cmd_rec.AcceptWaveform(data):
            res = json.loads(cmd_rec.Result() or "{}")
            t = (res.get("text") or "").strip()
            if t:
                best_final = t
                last_voice = time.time()
        else:
            pres = json.loads(cmd_rec.PartialResult() or "{}")
            pt = (pres.get("partial") or "").strip()
            if pt:
                last_voice = time.time()

    res = json.loads(cmd_rec.FinalResult() or "{}")
    t = (res.get("text") or "").strip()
    if t:
        best_final = t

    return best_final.strip()

def listen_loop():
    model_path = find_model_path()
    if not model_path:
        print("ERROR: Could not find Vosk model folder.")
        sys.exit(1)

    print("[RUN] Demerzel Step 5.1 running. Say 'Demerzel' to wake. Ctrl+C to stop.")
    model = Model(model_path)
    rec = KaldiRecognizer(model, SAMPLE_RATE); rec.SetWords(False)
    cmd_rec = KaldiRecognizer(model, SAMPLE_RATE); cmd_rec.SetWords(False)

    with sd.RawInputStream(
        samplerate=SAMPLE_RATE,
        blocksize=BLOCK_SIZE,
        dtype="int16",
        channels=1,
        callback=audio_callback,
    ):
        while True:
            data = audio_q.get()
            if rec.AcceptWaveform(data):
                res = json.loads(rec.Result() or "{}")
                final_text = (res.get("text") or "").strip()
                if not final_text:
                    continue

                alias, score, heard = wake_score(final_text)
                print(f"FINAL: {final_text}")

                if score >= WAKE_THRESHOLD:
                    print(f"=== WAKE === name={WAKE_CANON} heard='{heard}' match='{alias}' score={score:.3f}")
                    say("Awake.")
                    print("A: Awake.")
                    print("B: Listening for command...")

                    cmd_text = listen_for_command(cmd_rec)
                    if not cmd_text:
                        say("No command.")
                        print("[NO COMMAND DETECTED]")
                        print("[IDLE] Back to wake listening.")
                        continue

                    intent = intent_from_command(cmd_text)
                    envelope = {
                        "ts": datetime.now().isoformat(timespec="seconds"),
                        "source": "voice",
                        "wake": {"name": WAKE_CANON, "heard": heard, "match": alias, "score": score},
                        "raw_text": cmd_text,
                        "normalized": intent.get("normalized", ""),
                        "intent_type": intent.get("intent_type", "unknown"),
                        "payload": intent.get("payload", {}),
                    }
                    print("[INTENT]")
                    print(json.dumps(envelope, indent=2))
                    route_intent(intent)
                    print("[IDLE] Back to wake listening.")

def main():
    try:
        listen_loop()
    except KeyboardInterrupt:
        print("\n[STOP] Ctrl+C received. Exiting cleanly.")
        sys.exit(0)

if __name__ == "__main__":
    main()
