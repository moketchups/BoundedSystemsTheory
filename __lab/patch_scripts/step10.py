#!/usr/bin/env python3
import os
import sys
import json
import time
import queue
import re
import sqlite3
import subprocess
from datetime import datetime

import sounddevice as sd
from vosk import Model, KaldiRecognizer
from difflib import SequenceMatcher

# ============================================================
# Step 10 (fixed): Task queue brain + robust confirm/cancel
# - Confirm accepts: confirm/confirmed/yes/yeah/save/ok/okay/do it
# - Handles phrases like "say confirm" or "confirmed to save"
# - Adds confirm timeout so you can’t get trapped
# ============================================================

WAKE_CANON = "DEMERZEL"

WAKE_ALIASES = [
    "demerzel",
    "dammers",
    "damers",
    "dammerz",
    "dam ezell",
    "dam ezel",
    "dem ezell",
    "dem ezel",
]

WAKE_THRESHOLD = 0.72
WAKE_COOLDOWN_S = 1.25

CMD_START_GRACE_S = 4.0
CMD_END_SILENCE_S = 0.90

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models", "vosk-model-small-en-us-0.15")
SAMPLE_RATE = 16000

DB_PATH = os.path.join(os.path.dirname(__file__), "demerzel.db")

# Confirm state safety: don’t get stuck
CONFIRM_TIMEOUT_S = 10.0
CONFIRM_MAX_PROMPTS = 4

def say(text: str):
    text = str(text).strip()
    if not text:
        return
    try:
        subprocess.run(["say", text], check=False)
    except Exception:
        pass

def db_init():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            status TEXT NOT NULL,
            text TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def task_add(text: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tasks (created_at, status, text) VALUES (?, 'open', ?)",
        (datetime.utcnow().isoformat(), text.strip())
    )
    conn.commit()
    conn.close()

def task_list(open_only=True, limit=20):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    if open_only:
        cur.execute("SELECT id, text FROM tasks WHERE status='open' ORDER BY id DESC LIMIT ?", (limit,))
    else:
        cur.execute("SELECT id, status, text FROM tasks ORDER BY id DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows

def task_complete(task_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE tasks SET status='done' WHERE id=?", (task_id,))
    conn.commit()
    changed = cur.rowcount
    conn.close()
    return changed > 0

def task_clear_done():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE status='done'")
    conn.commit()
    deleted = cur.rowcount
    conn.close()
    return deleted

def normalize_text(s: str) -> str:
    s = (s or "").lower().strip()
    s = re.sub(r"[^a-z0-9\s']", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()

def best_wake_alias(heard: str):
    heard_n = normalize_text(heard)
    if not heard_n:
        return None, 0.0, ""

    best_alias = None
    best_score = 0.0

    for alias in WAKE_ALIASES:
        alias_n = normalize_text(alias)
        sc = similarity(heard_n, alias_n)
        if sc > best_score:
            best_score = sc
            best_alias = alias

    words = heard_n.split()
    for alias in WAKE_ALIASES:
        alias_n = normalize_text(alias)
        alias_words = alias_n.split()
        n = len(alias_words)
        if n == 0:
            continue
        for i in range(0, max(1, len(words) - n + 1)):
            window = " ".join(words[i:i+n])
            sc = similarity(window, alias_n)
            if sc > best_score:
                best_score = sc
                best_alias = alias

    return best_alias, best_score, best_alias or ""

def parse_intent(command_text: str):
    raw = command_text or ""
    cleaned = normalize_text(raw)

    if re.search(r"\b(what time is it|tell me the time|time)\b", cleaned):
        return {"intent_type": "time", "payload": {}}

    if re.search(r"\b(what are my tasks|list tasks|my tasks|what do i need to do|todo|to do)\b", cleaned):
        return {"intent_type": "list_tasks", "payload": {}}

    m = re.search(r"\b(complete|done|finish|mark done)\s+(task\s+)?(\d+)\b", cleaned)
    if m:
        return {"intent_type": "complete_task", "payload": {"id": int(m.group(3))}}

    if re.search(r"\b(clear done|clear completed|delete done|purge done)\b", cleaned):
        return {"intent_type": "clear_done", "payload": {}}

    if re.search(r"\b(help|what can you do|commands)\b", cleaned):
        return {"intent_type": "help", "payload": {}}

    m = re.search(r"\b(remember|remember to|add task|todo|to do)\b\s*(.*)$", cleaned)
    if m:
        text = (m.group(2) or "").strip()
        return {"intent_type": "remember_task", "payload": {"text": text}}

    return {"intent_type": "unknown", "payload": {"raw": raw, "cleaned": cleaned}}

class State:
    WAKE = "wake"
    COMMAND = "command"
    CONFIRM = "confirm"

# Robust confirm/cancel
CONFIRM_WORDS = {"confirm", "confirmed", "yes", "yeah", "yep", "save", "ok", "okay", "do it"}
CANCEL_WORDS = {"cancel", "never mind", "nevermind", "no", "stop", "abort"}

def is_confirm(s: str) -> bool:
    s = normalize_text(s)
    # handle phrases like: "say confirm", "confirmed to save", "yes confirm"
    tokens = s.split()
    if any(t in CONFIRM_WORDS for t in tokens):
        return True
    if "confirm" in s or "confirmed" in s:
        return True
    return False

def is_cancel(s: str) -> bool:
    s = normalize_text(s)
    tokens = s.split()
    if any(t in {"cancel", "no", "stop", "abort"} for t in tokens):
        return True
    if "never mind" in s or "nevermind" in s:
        return True
    return False

def main():
    db_init()

    if not os.path.isdir(MODEL_DIR):
        print(f"[ERROR] Vosk model not found at: {MODEL_DIR}")
        sys.exit(1)

    model = Model(MODEL_DIR)
    rec = KaldiRecognizer(model, SAMPLE_RATE)
    rec.SetWords(False)

    audio_q = queue.Queue()

    def audio_callback(indata, frames, time_info, status):
        audio_q.put(bytes(indata))

    state = State.WAKE
    last_wake_ts = 0.0

    cmd_started_ts = None
    cmd_last_voice_ts = None
    cmd_buffer = ""

    pending_task_text = ""

    confirm_started_ts = None
    confirm_prompts = 0

    print(f"[RUN] Demerzel Step 10 running. Say '{WAKE_CANON}' to wake. Ctrl+C to stop.")
    print(f"[WAKE] threshold={WAKE_THRESHOLD:.2f} aliases={len(WAKE_ALIASES)} cooldown={WAKE_COOLDOWN_S:.2f}s")
    print(f"[CMD] start_grace={CMD_START_GRACE_S:.2f}s end_silence={CMD_END_SILENCE_S:.2f}s")
    print(f"[CONFIRM] timeout={CONFIRM_TIMEOUT_S:.1f}s max_prompts={CONFIRM_MAX_PROMPTS}")

    try:
        with sd.RawInputStream(
            samplerate=SAMPLE_RATE,
            blocksize=8000,
            dtype="int16",
            channels=1,
            callback=audio_callback,
        ):
            while True:
                data = audio_q.get()
                now = time.time()

                # Confirm-state timeout safety (runs even without speech)
                if state == State.CONFIRM and confirm_started_ts is not None:
                    if (now - confirm_started_ts) > CONFIRM_TIMEOUT_S:
                        say("Timed out. Canceling.")
                        print("[CONFIRM] Timeout -> cancel")
                        pending_task_text = ""
                        state = State.WAKE
                        confirm_started_ts = None
                        confirm_prompts = 0

                if rec.AcceptWaveform(data):
                    res = json.loads(rec.Result() or "{}")
                    final_text = res.get("text", "").strip()
                    final_norm = normalize_text(final_text)

                    if final_text:
                        print(f"FINAL: {final_text}")

                    # -------------------------
                    # WAKE
                    # -------------------------
                    if state == State.WAKE:
                        if (now - last_wake_ts) < WAKE_COOLDOWN_S:
                            continue

                        alias, score, _ = best_wake_alias(final_text)
                        if alias and score >= WAKE_THRESHOLD:
                            last_wake_ts = now
                            print(f"=== WAKE === name={WAKE_CANON} heard='{final_text}' best_alias='{alias}' score={score:.3f}")
                            say("Awake.")
                            say("Listening.")
                            state = State.COMMAND
                            cmd_started_ts = now
                            cmd_last_voice_ts = None
                            cmd_buffer = ""
                            continue

                    # -------------------------
                    # COMMAND
                    # -------------------------
                    if state == State.COMMAND:
                        if cmd_last_voice_ts is None:
                            if final_norm:
                                cmd_last_voice_ts = now
                                cmd_buffer = final_text
                            else:
                                if (now - cmd_started_ts) > CMD_START_GRACE_S:
                                    print("[COMMAND MODE] (no command started — grace timeout)")
                                    say("No command heard.")
                                    state = State.WAKE
                                    continue
                        else:
                            if final_norm:
                                cmd_last_voice_ts = now
                                cmd_buffer = (cmd_buffer + " " + final_text).strip()

                        if cmd_last_voice_ts is not None and final_norm == "":
                            if (now - cmd_last_voice_ts) > CMD_END_SILENCE_S:
                                command = cmd_buffer.strip()
                                print(f"[COMMAND MODE] FINAL: {command}")

                                intent = parse_intent(command)
                                event = {
                                    "ts": datetime.utcnow().isoformat(),
                                    "source": "voice",
                                    "wake": {"name": WAKE_CANON},
                                    "raw_text": command,
                                    "normalized": normalize_text(command),
                                    "intent_type": intent["intent_type"],
                                    "payload": intent["payload"],
                                }
                                print("[INTENT]")
                                print(json.dumps(event, indent=2))

                                it = intent["intent_type"]

                                if it == "time":
                                    t = datetime.now().strftime("%-I:%M %p")
                                    say(f"It is {t}.")
                                    print(f"[SAY] It is {t}.")

                                elif it == "list_tasks":
                                    rows = task_list(open_only=True, limit=10)
                                    if not rows:
                                        say("You have no open tasks.")
                                    else:
                                        say(f"You have {len(rows)} open tasks.")
                                        for tid, text in reversed(rows):
                                            say(f"Task {tid}. {text}")

                                elif it == "complete_task":
                                    tid = int(intent["payload"]["id"])
                                    ok = task_complete(tid)
                                    say(f"Completed task {tid}." if ok else f"I couldn't find task {tid}.")

                                elif it == "clear_done":
                                    n = task_clear_done()
                                    say(f"Cleared {n} completed tasks.")

                                elif it == "help":
                                    say("Say: remember buy milk. What are my tasks. Complete task one.")

                                elif it == "remember_task":
                                    text = (intent["payload"].get("text") or "").strip()
                                    if not text:
                                        say("Tell me what to remember.")
                                    else:
                                        pending_task_text = text
                                        say(f"You want me to remember: {text}. Say confirm to save, or cancel.")
                                        state = State.CONFIRM
                                        confirm_started_ts = time.time()
                                        confirm_prompts = 0
                                        continue

                                else:
                                    say("I heard you, but I don't have an action for that yet.")

                                print("[IDLE] Back to wake listening.")
                                state = State.WAKE
                                cmd_started_ts = None
                                cmd_last_voice_ts = None
                                cmd_buffer = ""
                                continue

                    # -------------------------
                    # CONFIRM
                    # -------------------------
                    if state == State.CONFIRM:
                        if not final_text:
                            continue

                        if is_confirm(final_text):
                            task_add(pending_task_text)
                            say("Saved.")
                            print("[CONFIRM] Saved task.")
                            pending_task_text = ""
                            state = State.WAKE
                            confirm_started_ts = None
                            confirm_prompts = 0
                            continue

                        if is_cancel(final_text):
                            say("Canceled.")
                            print("[CONFIRM] Canceled task.")
                            pending_task_text = ""
                            state = State.WAKE
                            confirm_started_ts = None
                            confirm_prompts = 0
                            continue

                        confirm_prompts += 1
                        if confirm_prompts >= CONFIRM_MAX_PROMPTS:
                            say("Too many tries. Canceling.")
                            print("[CONFIRM] Max prompts -> cancel")
                            pending_task_text = ""
                            state = State.WAKE
                            confirm_started_ts = None
                            confirm_prompts = 0
                            continue

                        say("Say confirm, yes, or cancel.")
                        print("[CONFIRM] Awaiting confirm/cancel.")
                        continue

                else:
                    pres = json.loads(rec.PartialResult() or "{}")
                    p = pres.get("partial", "")
                    if p:
                        print(f"partial: {p}")

    except KeyboardInterrupt:
        print("\n[STOP] Ctrl+C received. Exiting cleanly.")
        return

if __name__ == "__main__":
    main()

