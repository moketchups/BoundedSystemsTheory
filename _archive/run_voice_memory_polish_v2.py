#!/usr/bin/env python3
"""
Memory interception runner for Demerzel (v2).
- Does NOT modify baseline files.
- Patches BrainController.run to intercept recognized utterances BEFORE routing.
"""

import time
import inspect
import run_voice_clean

# --- Simple memory store (uses your existing MemoryStore if present, else fallback dict) ---

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
    # Try to import your real store if it exists in repo
    for modname in ("memory_store", "demerzel_memory", "memory"):
        try:
            mod = __import__(modname)
            if hasattr(mod, "MemoryStore"):
                return mod.MemoryStore()
        except Exception:
            pass
    return _FallbackStore()

STORE = _get_store()

# --- Text helpers ---

def _norm(s: str) -> str:
    return " ".join((s or "").strip().lower().split())

def _strip_wake_prefix(t: str) -> str:
    # Sometimes the wake alias bleeds into remainder ("dam brazil", "dammers", etc.)
    # If it starts with "our" / "okay" etc, leave it. We'll just lightly trim known junk.
    junk_prefixes = ("dam ", "dammers", "dan ", "the amazon", "amazon", "out")
    tt = (t or "").strip()
    low = tt.lower()
    for jp in junk_prefixes:
        if low.startswith(jp):
            return tt[len(jp):].strip()
    return tt

def _maybe_memory_handle(say_fn, text: str) -> bool:
    """
    Return True if consumed (do not route).
    """
    t0 = _strip_wake_prefix(_norm(text))
    if not t0:
        return False

    # Robust triggers:
    # "remember my X is Y"
    # "note that X is Y"
    # "what is my X"
    # "what do you remember"
    # "forget my X"
    if t0.startswith("remember my "):
        rest = t0[len("remember my "):].strip()
        # split on " is "
        if " is " in rest:
            key, val = rest.split(" is ", 1)
            key, val = key.strip(), val.strip()
            if key and val:
                STORE.remember_fact(key, val)
                say_fn("Okay.")
                print(f"[MEMORY_V2] STORED fact: {key} = {val}")
                return True
        # if no "is", store as note
        STORE.remember_note(rest)
        say_fn("Okay.")
        print(f"[MEMORY_V2] STORED note: {rest}")
        return True

    if t0.startswith("note that "):
        rest = t0[len("note that "):].strip()
        if " is " in rest:
            key, val = rest.split(" is ", 1)
            key, val = key.strip(), val.strip()
            if key and val:
                STORE.remember_fact(key, val)
                say_fn("Okay.")
                print(f"[MEMORY_V2] STORED fact: {key} = {val}")
                return True
        STORE.remember_note(rest)
        say_fn("Okay.")
        print(f"[MEMORY_V2] STORED note: {rest}")
        return True

    if t0.startswith("forget my "):
        key = t0[len("forget my "):].strip()
        # best-effort: if fallback, delete; if real store, ignore if unsupported
        try:
            if hasattr(STORE, "data") and "facts" in getattr(STORE, "data", {}):
                STORE.data["facts"].pop(key.strip().lower(), None)
                STORE.save()
            elif isinstance(STORE, _FallbackStore):
                STORE.facts.pop(key.strip().lower(), None)
            say_fn("Okay.")
            print(f"[MEMORY_V2] FORGOT fact: {key}")
            return True
        except Exception as e:
            print(f"[MEMORY_V2] FORGET failed: {e}")
            return False

    if t0 in ("what do you remember", "what do you remember?", "what do you know", "what do you know?"):
        # Speak recent notes if any, else say nothing stored
        notes = []
        try:
            notes = STORE.recall_recent_notes(3)
        except Exception:
            notes = []
        if notes:
            say_fn("Here are the last notes I have.")
            for n in notes:
                say_fn(n)
            print("[MEMORY_V2] SPOKE recent notes")
        else:
            say_fn("I don't have any notes yet.")
            print("[MEMORY_V2] No notes to speak")
        return True

    if t0.startswith("what is my "):
        key = t0[len("what is my "):].strip().rstrip("?")
        val = None
        try:
            val = STORE.recall_fact(key)
        except Exception:
            val = None
        if val:
            say_fn(val)
            print(f"[MEMORY_V2] RECALL fact: {key} = {val}")
        else:
            say_fn(f"I don't have your {key} yet.")
            print(f"[MEMORY_V2] RECALL miss: {key}")
        return True

    return False

# --- Patch BrainController.run ---

def _patch_braincontroller():
    # Locate BrainController class in run_voice_clean module
    BC = getattr(run_voice_clean, "BrainController", None)
    if BC is None:
        print("[MEMORY_V2] Could not find BrainController in run_voice_clean. Aborting.")
        return False

    orig_run = BC.run

    def patched_run(self, *args, **kwargs):
        # We wrap the engine.process method to intercept *final_text* right before routing
        engine = getattr(self, "engine", None)
        say_fn = getattr(self, "say", None)
        if engine is None or say_fn is None:
            return orig_run(self, *args, **kwargs)

        orig_process = engine.process

        def patched_process(final_text: str):
            try:
                if _maybe_memory_handle(say_fn, final_text):
                    return {"intent": "MEMORY_CONSUMED", "confidence": 1.0, "raw_text": final_text, "require_confirmation": False}
            except Exception as e:
                print(f"[MEMORY_V2] intercept error: {e}")
            return orig_process(final_text)

        engine.process = patched_process
        try:
            return orig_run(self, *args, **kwargs)
        finally:
            engine.process = orig_process

    BC.run = patched_run
    return True

def main():
    ok = _patch_braincontroller()
    if not ok:
        return
    print("[MEMORY_V2] Memory interception enabled (BrainController.run wrapper).")
    # Delegate to normal entry point
    run_voice_clean.main()

if __name__ == "__main__":
    main()
