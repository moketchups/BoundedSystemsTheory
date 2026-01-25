#!/usr/bin/env python3
import os
import re
import sys
import json
import time
import queue
import sqlite3
import subprocess
from dataclasses import dataclass
from difflib import SequenceMatcher

# -------- Audio / ASR --------
import vosk
import pyaudio

# ============================
# Config (tuned for your setup)
# ============================
WAKE_NAME = "demerzel"
# Add a few common mishears you've seen ("damers", "dam ezell", etc.)
WAKE_ALIASES = [
    "demerzel",
    "demers",
    "damers",
    "dam erzell",
    "dam ezell",
    "dem erzell",
    "dem erzel",
    "damerzel",
    "demerzel",
]

WAKE_THRESHOLD = 0.78          # wake fuzzy match threshold
SIMILARITY_DROP = 0.78         # if command contains wake-ish word, ignore as wake echo

COMMAND_WINDOW_S = 5.0         # after wake, listen this long for a command
FOLLOWUP_WINDOW_S = 7.0        # after an answer, allow follow-up commands
CONFIRM_WINDOW_S = 8.0         # for "confirm/cancel" after remember

END_SILENCE_S = 0.9            # Vosk finalization behavior
GUARD_S = 1.2                  # small guard to prevent immediate re-wake from TTS bleed

# Vosk model path (you have this folder in your repo)
MODEL_DIR = "vosk-model-small-en-us-0.15"

DB_PATH = "demerzel_memory.db"  # durable tasks storage


# ============================
# Utilities
# ============================
def now_ts():
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())

def jlog(phase, data):
    print(json.dumps({"ts": now_ts(), "phase": phase, "data": data}, ensure_ascii=False))
    sys.stdout.flush()

def say(text):
    # Prefer macOS `say` to avoid pyttsx3 issues
    try:
        subprocess.run(["say", text], check=False)
    except Exception:
        # If `say` fails for any reason, just print
        pass

def beep():
    # Terminal beep; not always audible but harmless
    print("\a", end="")
    sys.stdout.flush()

def normalize(text: str) -> str:
    t = text.lower().strip()
    t = re.sub(r"[^a-z0-9\s']", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t

def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()

def best_alias_match(text: str):
    t = normalize(text)
    best = ("", 0.0)
    for alias in WAKE_ALIASES:
        s = similarity(t, alias)
        if s > best[1]:
            best = (alias, s)
    return best[0], best[1]

def contains_wake_echo(text: str) -> bool:
    t = normalize(text)
    # If command is basically wake-word again, treat as echo
    alias, score = best_alias_match(t)
    return score >= SIMILARITY_DROP

# ============================
# Task DB
# ============================
def db_init():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            done INTEGER NOT NULL DEFAULT 0,
            created_ts TEXT NOT NULL,
            done_ts TEXT
        );
    """)
    conn.commit()
    return conn

def db_add_task(conn, text: str) -> int:
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tasks (text, done, created_ts) VALUES (?, 0, ?)",
        (text.strip(), now_ts()),
    )
    conn.commit()
    return cur.lastrowid

def db_list_open_tasks(conn):
    cur = conn.cursor()
    cur.execute("SELECT id, text FROM tasks WHERE done=0 ORDER BY id ASC")
    return cur.fetchall()

def db_complete_task(conn, task_id: int) -> bool:
    cur = conn.cursor()
    cur.execute("SELECT id FROM tasks WHERE id=? AND done=0", (task_id,))
    row = cur.fetchone()
    if not row:
        return False
    cur.execute(
        "UPDATE tasks SET done=1, done_ts=? WHERE id=?",
        (now_ts(), task_id),
    )
    conn.commit()
    return True

# ============================
# Intents
# ============================
@dataclass
class Intent:
    name: str
    payload: dict

def parse_intent(text: str) -> Intent:
    t = normalize(text)

    # TIME
    if re.search(r"\b(what time is it|tell me the time|time)\b", t):
        return Intent("time", {})

    # LIST TASKS
    if re.search(r"\b(what are my tasks|list tasks|show tasks|tasks)\b", t):
        return Intent("list_tasks", {})

    # COMPLETE TASK
    m = re.search(r"\b(complete|finish|done|mark)\s+(task\s*)?(\d+)\b", t)
    if m:
        return Intent("complete_task", {"id": int(m.group(3))})

    # REMEMBER TASK
    # "remember buy milk", "remember to buy milk", "remind me to buy milk"
    m = re.search(r"\b(remember|remind me)\b\s+(to\s+)?(.+)$", t)
    if m:
        task_text = m.group(3).strip()
        # guard against empty
        if task_text:
            return Intent("remember_task", {"text": task_text})

    return Intent("unknown", {"raw": text})

def render_time():
    # local time
    return time.strftime("%-I:%M %p", time.localtime())

# ============================
# Brain Contract (the “rules”)
# ============================
def allow_intent(intent_name: str) -> bool:
    # Step 14: allow these
    return intent_name in {"time", "remember_task", "list_tasks", "complete_task"}

# ============================
# State Machine
# ============================
class Mode:
    IDLE = "IDLE"
    COMMAND = "COMMAND"
    CONFIRMING = "CONFIRMING"
    FOLLOWUP = "FOLLOWUP"

@dataclass
class PendingConfirm:
    kind: str
    payload: dict

def is_confirm(text: str) -> bool:
    t = normalize(text)
    return bool(re.search(r"\b(confirm|confirmed|yes|yep|do it|save)\b", t))

def is_cancel(text: str) -> bool:
    t = normalize(text)
    return bool(re.search(r"\b(cancel|no|nope|never mind|discard)\b", t))

# ============================
# Vosk Streaming
# ============================
class VoskListener:
    def __init__(self, model_dir: str, sample_rate=16000):
        if not os.path.isdir(model_dir):
            raise RuntimeError(f"Missing Vosk model dir: {model_dir}")
        self.model = vosk.Model(model_dir)
        self.sample_rate = sample_rate
        self.rec = vosk.KaldiRecognizer(self.model, self.sample_rate)
        self.rec.SetWords(False)

        self.p = pyaudio.PyAudio()
        self.q = queue.Queue()

        def callback(in_data, frame_count, time_info, status):
            self.q.put(in_data)
            return (None, pyaudio.paContinue)

        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=8000,
            stream_callback=callback,
        )

    def start(self):
        self.stream.start_stream()

    def stop(self):
        try:
            self.stream.stop_stream()
            self.stream.close()
        finally:
            self.p.terminate()

    def poll_text(self):
        """
        Returns:
          (kind, text)
          kind: "partial" | "final" | None
        """
        try:
            data = self.q.get(timeout=0.1)
        except queue.Empty:
            return (None, "")

        if self.rec.AcceptWaveform(data):
            res = json.loads(self.rec.Result())
            text = res.get("text", "") or ""
            return ("final", text.strip())
        else:
            res = json.loads(self.rec.PartialResult())
            text = res.get("partial", "") or ""
            return ("partial", text.strip())


# ============================
# Main loop
# ============================
def main():
    conn = db_init()

    listener = VoskListener(MODEL_DIR)
    listener.start()

    mode = Mode.IDLE
    mode_deadline = None
    pending = None  # PendingConfirm

    last_say_ts = 0.0

    print(f"[RUN] Demerzel Step 14 running. Say '{WAKE_NAME.upper()}' to wake. Ctrl+C to stop.")
    print(f"[WAKE] threshold={WAKE_THRESHOLD} aliases={len(WAKE_ALIASES)}")
    print(f"[CMD] command_window={COMMAND_WINDOW_S}s followup_window={FOLLOWUP_WINDOW_S}s confirm_window={CONFIRM_WINDOW_S}s")
    print(f"[ECHO] guard={GUARD_S}s similarity_drop={SIMILARITY_DROP}")
    sys.stdout.flush()

    def set_mode(new_mode, seconds):
        nonlocal mode, mode_deadline
        mode = new_mode
        mode_deadline = time.time() + seconds if seconds else None
        jlog("STATE", {"attention_state": new_mode, "window": seconds})

    def respond(text):
        nonlocal last_say_ts
        jlog("DELIBERATE", {"speak": text, "actions": []})
        print(f"[SAY] {text}")
        beep()
        say(text)
        last_say_ts = time.time()
        # after any response, we allow followups
        set_mode(Mode.FOLLOWUP, FOLLOWUP_WINDOW_S)

    def refuse():
        respond("I heard you, but I don't have an action for that yet.")

    def handle_intent(intent: Intent):
        # contract check
        if not allow_intent(intent.name):
            refuse()
            return

        if intent.name == "time":
            respond(f"It is {render_time()}.")
            return

        if intent.name == "remember_task":
            # Require confirm
            task_text = intent.payload["text"].strip()
            nonlocal pending
            pending = PendingConfirm(kind="remember_task", payload={"text": task_text})
            jlog("DELIBERATE", {"speak": f"You want me to remember: {task_text}. Say confirm to save, or cancel.", "actions": []})
            print(f"[SAY] You want me to remember: {task_text}. Say confirm to save, or cancel.")
            beep()
            say(f"You want me to remember: {task_text}. Say confirm to save, or cancel.")
            set_mode(Mode.CONFIRMING, CONFIRM_WINDOW_S)
            return

        if intent.name == "list_tasks":
            tasks = db_list_open_tasks(conn)
            if not tasks:
                respond("You have no open tasks.")
            else:
                # Speak compactly
                lines = [f"Task {tid}: {txt}" for tid, txt in tasks[:5]]
                extra = ""
                if len(tasks) > 5:
                    extra = f" And {len(tasks)-5} more."
                respond("You have " + str(len(tasks)) + " open tasks. " + " ".join(lines) + extra)
            return

        if intent.name == "complete_task":
            tid = int(intent.payload["id"])
            ok = db_complete_task(conn, tid)
            if ok:
                respond(f"Completed task {tid}.")
            else:
                respond(f"I couldn't find an open task {tid}.")
            return

        refuse()

    try:
        # Start idle listening
        set_mode(Mode.IDLE, None)

        while True:
            # Timeouts
            if mode_deadline and time.time() > mode_deadline:
                print(f"[{mode}] window timeout -> back to IDLE")
                set_mode(Mode.IDLE, None)
                pending = None

            kind, text = listener.poll_text()
            if kind is None:
                continue

            if kind == "partial" and text:
                print(f"partial: {text}")
                continue

            if kind == "final":
                if not text:
                    continue
                print(f"FINAL: {text}")

                # Guard against immediate re-wake from TTS bleed
                if (time.time() - last_say_ts) < GUARD_S:
                    continue

                raw = text
                norm = normalize(raw)

                # -----------------
                # IDLE: wait for wake
                # -----------------
                if mode == Mode.IDLE:
                    alias, score = best_alias_match(norm)
                    if score >= WAKE_THRESHOLD:
                        print(f"=== WAKE === name={WAKE_NAME.upper()} heard='{raw}' best_alias='{alias}' score={score:.3f}")
                        # Quick ack (A then B)
                        jlog("DELIBERATE", {"speak": "Awake.", "actions": []})
                        print("[SAY] Awake.")
                        beep()
                        say("Awake.")
                        set_mode(Mode.COMMAND, COMMAND_WINDOW_S)
                    continue

                # -----------------
                # CONFIRMING: expect confirm/cancel
                # -----------------
                if mode == Mode.CONFIRMING:
                    if is_cancel(norm):
                        pending = None
                        respond("Canceled.")
                        continue
                    if is_confirm(norm):
                        if pending and pending.kind == "remember_task":
                            task_text = pending.payload["text"]
                            task_id = db_add_task(conn, task_text)
                            pending = None
                            respond(f"Saved. Task {task_id}: {task_text}")
                            continue
                        pending = None
                        respond("Confirmed.")
                        continue

                    # Not confirm/cancel -> keep waiting (until timeout)
                    jlog("INTERPRET", {"intent": "unknown", "confidence": 0.3, "raw": raw})
                    print("[CONFIRM] Waiting for 'confirm' or 'cancel'...")
                    continue

                # -----------------
                # COMMAND or FOLLOWUP: interpret text
                # -----------------
                if mode in (Mode.COMMAND, Mode.FOLLOWUP):
                    # If user basically says wake word again, ignore as echo / non-command
                    if contains_wake_echo(norm):
                        jlog("INTERPRET", {"intent": "unknown", "confidence": 0.3, "raw": raw})
                        print("[COMMAND] Wake-echo/no-op.")
                        continue

                    intent = parse_intent(raw)
                    # crude confidence: known intents = 0.9 else 0.3
                    conf = 0.9 if intent.name != "unknown" else 0.3
                    jlog("INTERPRET", {"intent": intent.name, "confidence": conf, "raw": raw})

                    if intent.name == "unknown":
                        respond("I didn't catch a valid command.")
                        continue

                    handle_intent(intent)
                    continue

    except KeyboardInterrupt:
        print("\n[STOP] Ctrl+C received. Exiting cleanly.")
    finally:
        try:
            listener.stop()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass

if __name__ == "__main__":
    main()
