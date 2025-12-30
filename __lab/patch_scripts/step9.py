#!/usr/bin/env python3
import os
import re
import json
import time
import queue
import sqlite3
import hashlib
import subprocess
from dataclasses import dataclass
from difflib import SequenceMatcher

import numpy as np
import sounddevice as sd
from vosk import Model, KaldiRecognizer

from cryptography.fernet import Fernet


# =========================
# Step 9: Memory (encrypted + consent) + voice responses
# =========================

# --- Wake config (tune later; keep stable now) ---
WAKE_CANON = "DEMERZEL"

# Add common mishears you’ve seen so far. You can add more later without changing logic.
WAKE_ALIASES = [
    "demerzel",
    "dem erzell",
    "dam ezell",
    "dammers",
    "dammers l",
    "dammers ill",
    "damers",
]

WAKE_THRESHOLD = 0.72      # similarity threshold
WAKE_COOLDOWN = 1.25       # seconds: ignore repeated wakes
START_GRACE = 4.0          # seconds after "Awake" to start talking
END_SILENCE = 0.90         # seconds of silence to end command
ECHO_GUARD = 1.20          # seconds after we speak to ignore our own audio

# --- Audio / Vosk ---
SAMPLE_RATE = 16000
BLOCKSIZE = 8000

# Use the same model you already have. If your model folder differs, change this path.
VOSK_MODEL_PATH = os.environ.get("VOSK_MODEL_PATH", "models/vosk-model-small-en-us-0.15")

# --- Memory storage ---
DB_PATH = os.path.join(os.path.dirname(__file__), "demerzel_memory.db")
KEY_PATH = os.path.join(os.path.dirname(__file__), ".demerzel_key")


# -------------------------
# Helpers
# -------------------------

def now_ts():
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())

def say(text: str):
    """Voice output (macOS). Also prints."""
    text = (text or "").strip()
    if not text:
        return
    print(f"[SAY] {text}")
    try:
        # macOS built-in TTS
        subprocess.run(["say", text], check=False)
    except Exception:
        pass

def beep():
    # terminal bell (works in many terminals)
    try:
        print("\a", end="", flush=True)
    except Exception:
        pass

def normalize_text(t: str) -> str:
    t = (t or "").lower().strip()
    # keep words/numbers/spaces only
    t = re.sub(r"[^a-z0-9\s']", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t

def best_wake_alias(heard: str):
    """
    Returns (best_alias, best_score).
    We match on normalized text similarity.
    """
    h = normalize_text(heard)
    if not h:
        return None, 0.0

    best_alias = None
    best_score = 0.0

    for a in WAKE_ALIASES:
        aa = normalize_text(a)
        if not aa:
            continue
        # Similarity on the full string
        score = SequenceMatcher(None, h, aa).ratio()
        # Also allow substring-ish matches: if alias appears inside heard
        if aa in h:
            score = max(score, 0.95)
        if score > best_score:
            best_score = score
            best_alias = a

    return best_alias, best_score

def load_fernet():
    """
    Local-only key, stored in .demerzel_key
    If file doesn’t exist, generate it.
    """
    if os.path.exists(KEY_PATH):
        with open(KEY_PATH, "rb") as f:
            key = f.read().strip()
    else:
        key = Fernet.generate_key()
        with open(KEY_PATH, "wb") as f:
            f.write(key)
        try:
            os.chmod(KEY_PATH, 0o600)
        except Exception:
            pass
    return Fernet(key)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            kind TEXT NOT NULL,
            content_enc BLOB NOT NULL,
            content_hash TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def mem_write(fernet: Fernet, kind: str, content: str):
    content = content.strip()
    enc = fernet.encrypt(content.encode("utf-8"))
    h = hashlib.sha256(content.encode("utf-8")).hexdigest()

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO memories (created_at, kind, content_enc, content_hash) VALUES (?, ?, ?, ?)",
        (now_ts(), kind, enc, h)
    )
    conn.commit()
    conn.close()

def mem_list_recent(fernet: Fernet, limit: int = 5):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT created_at, kind, content_enc FROM memories ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    rows = cur.fetchall()
    conn.close()

    out = []
    for created_at, kind, enc in rows:
        try:
            content = fernet.decrypt(enc).decode("utf-8", errors="replace")
        except Exception:
            content = "<decrypt failed>"
        out.append((created_at, kind, content))
    return out

def mem_search(fernet: Fernet, query: str, limit: int = 5):
    qn = normalize_text(query)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT created_at, kind, content_enc FROM memories ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()

    matches = []
    for created_at, kind, enc in rows:
        try:
            content = fernet.decrypt(enc).decode("utf-8", errors="replace")
        except Exception:
            continue
        if qn and qn in normalize_text(content):
            matches.append((created_at, kind, content))
            if len(matches) >= limit:
                break
    return matches


# -------------------------
# Intent parsing
# -------------------------

@dataclass
class Intent:
    intent_type: str
    payload: dict

def parse_intent(raw: str) -> Intent:
    t = normalize_text(raw)

    # "remember buy milk"
    m = re.match(r"^remember\s+(.+)$", t)
    if m:
        return Intent("remember", {"text": m.group(1).strip()})

    # "recall milk" or "remember what did i say"
    m = re.match(r"^(recall|find|search)\s+(.+)$", t)
    if m:
        return Intent("recall", {"query": m.group(2).strip()})

    # "what did i ask you to remember" / "what do you remember"
    if re.search(r"\bwhat\b.*\bremember\b", t) or "what do you remember" in t:
        return Intent("list_memory", {})

    # time
    if re.search(r"\bwhat time is it\b|\btime\b", t):
        return Intent("time", {})

    return Intent("unknown", {"raw": raw})


# -------------------------
# Audio streaming / state machine
# -------------------------

def main():
    init_db()
    fernet = load_fernet()

    if not os.path.isdir(VOSK_MODEL_PATH):
        print(f"[ERROR] Vosk model not found at: {VOSK_MODEL_PATH}")
        print("Set VOSK_MODEL_PATH or put your model in models/...")
        return

    model = Model(VOSK_MODEL_PATH)
    rec = KaldiRecognizer(model, SAMPLE_RATE)
    rec.SetWords(True)

    audio_q = queue.Queue()

    def audio_cb(indata, frames, t, status):
        if status:
            # Ignore transient warnings
            pass
        audio_q.put(bytes(indata))

    print(f"[RUN] Demerzel Step 9 running. Say '{WAKE_CANON}' to wake. Ctrl+C to stop.")
    print(f"[WAKE] threshold={WAKE_THRESHOLD} aliases={len(WAKE_ALIASES)} cooldown={WAKE_COOLDOWN}s")
    print(f"[CMD]  start_grace={START_GRACE}s end_silence={END_SILENCE}s")
    print(f"[ECHO] guard={ECHO_GUARD}s")
    print(f"[MEM]  db={DB_PATH} key={KEY_PATH}")

    last_wake_time = 0.0
    last_say_time = 0.0

    state = "WAKE"  # or "COMMAND" or "CONFIRM"
    cmd_started_at = None
    cmd_audio_started = False
    cmd_last_voice_time = None
    cmd_text_final = None

    pending_memory_text = None
    confirm_deadline = None

    with sd.RawInputStream(
        samplerate=SAMPLE_RATE,
        blocksize=BLOCKSIZE,
        dtype="int16",
        channels=1,
        callback=audio_cb,
    ):
        try:
            while True:
                data = audio_q.get()

                # Feed Vosk
                if rec.AcceptWaveform(data):
                    res = json.loads(rec.Result())
                    final_text = (res.get("text") or "").strip()
                    if final_text:
                        print(f"FINAL: {final_text}")
                        handle_final(
                            final_text,
                            fernet,
                            lambda s: _say_and_mark(s, lambda: nonlocal_set('last_say_time'), set_last_say_time=lambda v: None),
                        )
                    continue

                # Partial result
                pres = json.loads(rec.PartialResult())
                partial = (pres.get("partial") or "").strip()
                if partial:
                    print(f"partial: {partial}")

                # Main state machine runs on partials too, but commits on finals.
                # We'll use finals for decisions to avoid noise.

                # We still need to process FINALs through our state machine, so we do it below:
                # Instead of relying on handle_final above, we implement full state machine here.
                # To keep things simple: We'll re-check on FINAL only.
                # (We already print finals; now apply logic.)
                if rec.AcceptWaveform(data):
                    pass

        except KeyboardInterrupt:
            print("\n[STOP] Ctrl+C received. Exiting cleanly.")
            return


# NOTE: We can’t use "nonlocal" the way I started above in a nested helper without restructuring.
# So: implement the logic inline, cleanly, below.

def _in_echo_guard(last_say_time: float) -> bool:
    return (time.time() - last_say_time) < ECHO_GUARD


# Re-implement main with correct state machine (single function, no confusing closures)
def main():
    init_db()
    fernet = load_fernet()

    if not os.path.isdir(VOSK_MODEL_PATH):
        print(f"[ERROR] Vosk model not found at: {VOSK_MODEL_PATH}")
        print("Set VOSK_MODEL_PATH or put your model in models/...")
        return

    model = Model(VOSK_MODEL_PATH)
    rec = KaldiRecognizer(model, SAMPLE_RATE)
    rec.SetWords(True)

    audio_q = queue.Queue()

    def audio_cb(indata, frames, t, status):
        if status:
            pass
        audio_q.put(bytes(indata))

    print(f"[RUN] Demerzel Step 9 running. Say '{WAKE_CANON}' to wake. Ctrl+C to stop.")
    print(f"[WAKE] threshold={WAKE_THRESHOLD} aliases={len(WAKE_ALIASES)} cooldown={WAKE_COOLDOWN}s")
    print(f"[CMD]  start_grace={START_GRACE}s end_silence={END_SILENCE}s")
    print(f"[ECHO] guard={ECHO_GUARD}s")
    print(f"[MEM]  db={DB_PATH} key={KEY_PATH}")

    state = "WAKE"   # WAKE -> COMMAND -> (optional CONFIRM) -> WAKE
    last_wake_time = 0.0
    last_say_time = 0.0

    cmd_deadline_start = None      # must start speaking by this time
    cmd_last_activity = None       # last time we saw speech
    cmd_buffer_final = ""          # final transcript of command window

    pending_memory_text = None
    confirm_deadline = None

    def guarded_say(text: str):
        nonlocal last_say_time
        beep()
        say(text)
        last_say_time = time.time()

    with sd.RawInputStream(
        samplerate=SAMPLE_RATE,
        blocksize=BLOCKSIZE,
        dtype="int16",
        channels=1,
        callback=audio_cb,
    ):
        try:
            while True:
                data = audio_q.get()

                # Ignore our own TTS output for a short guard window
                if _in_echo_guard(last_say_time):
                    continue

                if rec.AcceptWaveform(data):
                    res = json.loads(rec.Result())
                    final_text = (res.get("text") or "").strip()
                    if final_text:
                        print(f"FINAL: {final_text}")

                        # ----- CONFIRM state -----
                        if state == "CONFIRM":
                            t = normalize_text(final_text)
                            if time.time() > (confirm_deadline or 0):
                                guarded_say("Confirm window expired. Not saving.")
                                state = "WAKE"
                                pending_memory_text = None
                                confirm_deadline = None
                                continue

                            if t in ("confirm", "yes", "save it", "save"):
                                mem_write(fernet, "note", pending_memory_text)
                                guarded_say("Saved.")
                                state = "WAKE"
                                pending_memory_text = None
                                confirm_deadline = None
                                continue

                            if t in ("cancel", "no", "never mind", "dont", "don't"):
                                guarded_say("Cancelled.")
                                state = "WAKE"
                                pending_memory_text = None
                                confirm_deadline = None
                                continue

                            guarded_say("Say confirm to save, or cancel.")
                            continue

                        # ----- WAKE state -----
                        if state == "WAKE":
                            # Check wake match
                            alias, score = best_wake_alias(final_text)
                            now = time.time()
                            if score >= WAKE_THRESHOLD and (now - last_wake_time) >= WAKE_COOLDOWN:
                                last_wake_time = now
                                print(f"[WAKE-CHECK] heard='{final_text}' best_alias='{alias}' score={score:.3f}")
                                print(f"=== WAKE === name={WAKE_CANON} heard='{final_text}' match='{alias}' score={score:.3f}")

                                guarded_say("Awake.")
                                guarded_say("Listening.")

                                state = "COMMAND"
                                cmd_deadline_start = time.time() + START_GRACE
                                cmd_last_activity = None
                                cmd_buffer_final = ""
                                continue

                            # Otherwise ignore in WAKE
                            continue

                        # ----- COMMAND state -----
                        if state == "COMMAND":
                            now = time.time()

                            # If user never starts talking, exit
                            if cmd_last_activity is None and now > (cmd_deadline_start or 0):
                                print("[COMMAND MODE] (no command started — grace timeout)")
                                guarded_say("No command heard.")
                                print("[IDLE] Back to wake listening.")
                                state = "WAKE"
                                continue

                            # Treat any final_text here as command speech
                            cmd_last_activity = now
                            cmd_buffer_final = (cmd_buffer_final + " " + final_text).strip()

                            # Decide if this final_text looks like a complete command:
                            # We'll use end_silence logic via time checks in partial section below,
                            # BUT also allow one-shot commands:
                            if len(cmd_buffer_final.split()) >= 2:
                                # Commit after a short pause (handled below) OR if user says a clear short command
                                pass

                    continue  # done with FINAL handling

                # Partial (for command window timing)
                pres = json.loads(rec.PartialResult())
                partial = (pres.get("partial") or "").strip()
                if partial:
                    # print partials already helpful; leave as-is
                    # Determine speech activity during COMMAND
                    if state == "COMMAND":
                        now = time.time()

                        # If user never starts, keep waiting until grace timeout handled in FINAL section.
                        if cmd_last_activity is None:
                            # Any partial means they started speaking
                            cmd_last_activity = now
                        else:
                            cmd_last_activity = now

                # End-of-command detection for COMMAND state:
                if state == "COMMAND" and cmd_last_activity is not None:
                    if (time.time() - cmd_last_activity) >= END_SILENCE and cmd_buffer_final:
                        raw = cmd_buffer_final.strip()
                        cleaned = normalize_text(raw)

                        intent = parse_intent(raw)

                        event = {
                            "ts": now_ts(),
                            "source": "voice",
                            "wake": {"name": WAKE_CANON},
                            "raw_text": raw,
                            "cleaned": cleaned,
                            "intent_type": intent.intent_type,
                            "payload": intent.payload,
                        }
                        print("[INTENT]")
                        print(json.dumps(event, indent=2))

                        # Route intent
                        if intent.intent_type == "time":
                            # Keep it simple: local time
                            t = time.strftime("%-I:%M %p")
                            guarded_say(f"It is {t}.")
                            print("[IDLE] Back to wake listening.")
                            state = "WAKE"

                        elif intent.intent_type == "remember":
                            # Explicit consent gate
                            pending_memory_text = intent.payload.get("text", "").strip()
                            if not pending_memory_text:
                                guarded_say("What should I remember?")
                                # stay in COMMAND? safer to drop to WAKE
                                state = "WAKE"
                            else:
                                guarded_say(f"You want me to remember: {pending_memory_text}. Say confirm to save, or cancel.")
                                state = "CONFIRM"
                                confirm_deadline = time.time() + 5.0

                        elif intent.intent_type == "list_memory":
                            items = mem_list_recent(fernet, limit=5)
                            if not items:
                                guarded_say("I have no saved memories yet.")
                            else:
                                # Speak a short summary
                                guarded_say(f"I have {len(items)} recent memories. The latest is: {items[0][2]}")
                            state = "WAKE"

                        elif intent.intent_type == "recall":
                            q = intent.payload.get("query", "").strip()
                            matches = mem_search(fernet, q, limit=3)
                            if not matches:
                                guarded_say("I don’t have anything matching that yet.")
                            else:
                                guarded_say(f"I found: {matches[0][2]}")
                            state = "WAKE"

                        else:
                            guarded_say("I heard you, but I don’t have an action for that yet.")
                            state = "WAKE"

                        # Reset command buffers
                        cmd_deadline_start = None
                        cmd_last_activity = None
                        cmd_buffer_final = ""

        except KeyboardInterrupt:
            print("\n[STOP] Ctrl+C received. Exiting cleanly.")
            return


if __name__ == "__main__":
    main()

