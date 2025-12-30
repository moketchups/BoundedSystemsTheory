#!/usr/bin/env python3
"""
Memory interception runner (v3).
- Does NOT modify baseline files.
- Patches RouterEngine.process to intercept recognized utterances BEFORE routing.
"""

import time
import run_voice_clean
import router_engine

def _now_ts():
    return time.strftime("%Y-%m-%d %H:%M:%S")

class _FallbackStore:
    def __init__(self):
        self.facts = {}
        self.notes = []

    def remember_fact(self, key: str, value: str):
        self.facts[key.strip().lower()] = {"value": value.strip(), "ts": _now_ts()}

    def recall_fact(self, key: str):
        item = self.facts.get(key.strip().lower())
        return item["value"] if item else None

    def remember_note(self, text: str):
        self.notes.append({"text": text.strip(), "ts": _now_ts()})
        self.notes = self.notes[-200:]

    def recall_recent_notes(self, n: int = 5):
        return [x["text"] for x in self.notes[-n:]]

def _get_store():
    for modname in ("memory_store", "demerzel_memory", "memory"):
        try:
            mod = __import__(modname)
            if hasattr(mod, "MemoryStore"):
                return mod.MemoryStore()
        except Exception:
            pass
    return _FallbackStore()

STORE = _get_store()

def _norm(s: str) -> str:
    return " ".join((s or "").strip().lower().split())

def _maybe_memory_handle(say_fn, text: str) -> bool:
    t = _norm(text)
    if not t:
        return False

    if t.startswith("remember my "):
        rest = t[len("remember my "):].strip()
        if " is " in rest:
            key, val = rest.split(" is ", 1)
            key, val = key.strip(), val.strip()
            if key and val:
                STORE.remember_fact(key, val)
                say_fn("Okay.")
                print(f"[MEMORY_V3] STORED fact: {key} = {val}")
                return True
        STORE.remember_note(rest)
        say_fn("Okay.")
        print(f"[MEMORY_V3] STORED note: {rest}")
        return True

    if t.startswith("note that "):
        rest = t[len("note that "):].strip()
        if " is " in rest:
            key, val = rest.split(" is ", 1)
            key, val = key.strip(), val.strip()
            if key and val:
                STORE.remember_fact(key, val)
                say_fn("Okay.")
                print(f"[MEMORY_V3] STORED fact: {key} = {val}")
                return True
        STORE.remember_note(rest)
        say_fn("Okay.")
        print(f"[MEMORY_V3] STORED note: {rest}")
        return True

    if t.startswith("what is my "):
        key = t[len("what is my "):].strip().rstrip("?")
        try:
            val = STORE.recall_fact(key)
        except Exception:
            val = None
        if val:
            say_fn(val)
            print(f"[MEMORY_V3] RECALL fact: {key} = {val}")
        else:
            say_fn(f"I don't have your {key} yet.")
            print(f"[MEMORY_V3] RECALL miss: {key}")
        return True

    if t in ("what do you remember", "what do you remember?", "what do you know", "what do you know?"):
        try:
            notes = STORE.recall_recent_notes(3)
        except Exception:
            notes = []
        if notes:
            say_fn("Here are the last notes I have.")
            for n in notes:
                say_fn(n)
            print("[MEMORY_V3] SPOKE recent notes")
        else:
            say_fn("I don't have any notes yet.")
            print("[MEMORY_V3] No notes to speak")
        return True

    return False

def _patch_routerengine():
    RE = getattr(router_engine, "RouterEngine", None)
    if RE is None:
        print("[MEMORY_V3] Could not find RouterEngine in router_engine. Aborting.")
        return False

    orig_process = RE.process

    def patched_process(self, final_text: str):
        say_fn = getattr(self, "say", None)
        # If RouterEngine doesn't have say(), fall back to no speech but still store.
        def _say(msg: str):
            if callable(say_fn):
                say_fn(msg)

        try:
            if _maybe_memory_handle(_say, final_text):
                return {
                    "intent": "MEMORY_CONSUMED",
                    "confidence": 1.0,
                    "raw_text": final_text,
                    "require_confirmation": False,
                    "ts": time.time(),
                }
        except Exception as e:
            print(f"[MEMORY_V3] intercept error: {e}")

        return orig_process(self, final_text)

    RE.process = patched_process
    return True

def main():
    ok = _patch_routerengine()
    if not ok:
        return
    print("[MEMORY_V3] Memory interception enabled (RouterEngine.process patched).")
    run_voice_clean.main()

if __name__ == "__main__":
    main()
