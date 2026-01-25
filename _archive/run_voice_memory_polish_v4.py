#!/usr/bin/env python3
"""
Memory interception runner (v4)
- Patches RouterEngine.process
- Strips wake-word aliases if they appear in the utterance
- Matches 'remember' / 'what is my' even if preceded by wake word
- Prints debug of the exact final_text seen by RouterEngine
"""

import time
import run_voice_clean
import router_engine

def _now_ts():
    return time.strftime("%Y-%m-%d %H:%M:%S")

# Expand this list if you add more aliases later.
WAKE_ALIASES = [
    "demerzel", "demers", "damers",
    "dam brazil", "dan brazil", "dam brazzil",
    "dam er zel", "dan er zel", "dam rochelle", "dan rozelle",
]

def _norm(s: str) -> str:
    return " ".join((s or "").strip().lower().split())

def _strip_wake_alias_prefix(t: str) -> str:
    tt = _norm(t)
    # Remove leading "demerzel ..." style
    for a in sorted(WAKE_ALIASES, key=len, reverse=True):
        a = _norm(a)
        if tt.startswith(a + " "):
            return tt[len(a):].strip()
        if tt == a:
            return ""
    return tt

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

def _maybe_memory_handle(say_fn, final_text: str) -> bool:
    raw = final_text or ""
    t0 = _norm(raw)
    t = _strip_wake_alias_prefix(t0)

    # If wake word is embedded (e.g., "remember ... demerzel ..."), keep the part after it if present.
    # But mostly we care about leading aliases; t already handles that.

    if not t:
        return False

    # Match "remember ..." anywhere at the start after stripping wake alias
    if t.startswith("remember "):
        rest = t[len("remember "):].strip()
        # Support: "remember my email is X"
        if rest.startswith("my "):
            rest2 = rest[len("my "):].strip()
            if " is " in rest2:
                key, val = rest2.split(" is ", 1)
                key, val = key.strip(), val.strip()
                if key and val:
                    STORE.remember_fact(key, val)
                    say_fn("Okay.")
                    print(f"[MEMORY_V4] STORED fact: {key} = {val}")
                    return True
            # No "is" -> treat as a note
            STORE.remember_note(rest2)
            say_fn("Okay.")
            print(f"[MEMORY_V4] STORED note: {rest2}")
            return True

        # Support: "remember that X"
        if rest.startswith("that "):
            rest = rest[len("that "):].strip()

        # "X is Y" => fact, else note
        if " is " in rest:
            key, val = rest.split(" is ", 1)
            key, val = key.strip(), val.strip()
            if key and val:
                STORE.remember_fact(key, val)
                say_fn("Okay.")
                print(f"[MEMORY_V4] STORED fact: {key} = {val}")
                return True

        STORE.remember_note(rest)
        say_fn("Okay.")
        print(f"[MEMORY_V4] STORED note: {rest}")
        return True

    # Recall
    if t.startswith("what is my "):
        key = t[len("what is my "):].strip().rstrip("?")
        try:
            val = STORE.recall_fact(key)
        except Exception:
            val = None
        if val:
            say_fn(val)
            print(f"[MEMORY_V4] RECALL fact: {key} = {val}")
        else:
            say_fn(f"I don't have your {key} yet.")
            print(f"[MEMORY_V4] RECALL miss: {key}")
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
            print("[MEMORY_V4] SPOKE recent notes")
        else:
            say_fn("I don't have any notes yet.")
            print("[MEMORY_V4] No notes to speak")
        return True

    return False

def _patch_routerengine():
    RE = getattr(router_engine, "RouterEngine", None)
    if RE is None:
        print("[MEMORY_V4] Could not find RouterEngine in router_engine. Aborting.")
        return False

    orig_process = RE.process

    def patched_process(self, final_text: str):
        # DEBUG: show exactly what RouterEngine received
        print(f"[MEMORY_V4] heard: {final_text!r}")

        say_fn = getattr(self, "say", None)
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
            print(f"[MEMORY_V4] intercept error: {e}")

        return orig_process(self, final_text)

    RE.process = patched_process
    return True

def main():
    ok = _patch_routerengine()
    if not ok:
        return
    print("[MEMORY_V4] Memory interception enabled (RouterEngine.process patched).")
    run_voice_clean.main()

if __name__ == "__main__":
    main()
