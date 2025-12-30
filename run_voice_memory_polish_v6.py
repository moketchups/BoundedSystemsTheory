#!/usr/bin/env python3
import re
import time
import importlib
from typing import Optional

def _now_ts() -> float:
    return time.time()

def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())

# Wake aliases that often leak into FINAL text
WAKE_ALIASES = {
    "demerzel",
    "dammers",
    "dam er zel",
    "dammerz",
    "dam brazil",
    "dam brazill",
    "dam roselle",
    "dam result",
}

def _strip_leading_wake(raw: str) -> str:
    s = _norm(raw)
    # If the text starts with any alias, drop it.
    for alias in sorted(WAKE_ALIASES, key=len, reverse=True):
        if s.startswith(alias + " "):
            return raw.split(" ", len(alias.split()))[-1].strip()
        if s == alias:
            return ""
    return raw.strip()

# --- memory store hookup (use your existing store if available) ---
_store = None
try:
    ms = importlib.import_module("memory_store")
    MemoryStore = getattr(ms, "MemoryStore", None)
    if MemoryStore:
        _store = MemoryStore()
except Exception:
    _store = None

def _speak(text: str):
    import os
    os.system(f'say "{text.replace(chr(34), "")}"')

def _store_fact(key: str, value: str) -> bool:
    try:
        if _store and hasattr(_store, "remember_fact"):
            _store.remember_fact(key, value)
            return True
    except Exception:
        pass
    return False

def _recall_fact(key: str) -> Optional[str]:
    try:
        if _store and hasattr(_store, "recall_fact"):
            return _store.recall_fact(key)
    except Exception:
        pass
    return None

REMEMBER_RE = re.compile(r"^(?:i\s+)?remember(?:\s+that)?\s+(?P<body>.+)$", re.I)
EMAIL_RE = re.compile(r"\bemail\b", re.I)

def _maybe_intercept(text: str) -> bool:
    raw0 = (text or "").strip()
    if not raw0:
        return False

    # key fix: strip leaked wake alias prefix
    raw = _strip_leading_wake(raw0)
    if not raw:
        return False

    print(f"[MEMORY_V6] heard: {raw0!r}  -> normalized: {raw!r}")

    n = _norm(raw)

    # Remember
    m = REMEMBER_RE.match(raw)
    if m:
        body = m.group("body").strip()
        body_norm = body.replace(" at ", "@").replace(" dot ", ".")
        body_norm = re.sub(r"\s+", " ", body_norm).strip()

        # Email special case
        if EMAIL_RE.search(body_norm):
            parts = re.split(r"\bis\b", body_norm, maxsplit=1, flags=re.I)
            value = parts[1].strip() if len(parts) == 2 else body_norm
            if _store_fact("email", value):
                print(f"[MEMORY_V6] STORED: email = {value!r}")
                _speak("Okay.")
                return True
            _speak("Okay.")
            print("[MEMORY_V6] remember matched but store backend failed; acknowledged.")
            return True

        # Generic "remember X is Y"
        kv = re.split(r"\bis\b", body_norm, maxsplit=1, flags=re.I)
        if len(kv) == 2:
            k = _norm(kv[0])
            v = kv[1].strip()
            if _store_fact(k, v):
                print(f"[MEMORY_V6] STORED: {k} = {v!r}")
                _speak("Okay.")
                return True

        _speak("Okay.")
        print("[MEMORY_V6] remember matched but no storable key/value; acknowledged.")
        return True

    # Recall email
    if "what is my email" in n or n == "my email" or n.startswith("recall my email"):
        val = _recall_fact("email")
        if val:
            print(f"[MEMORY_V6] RECALL email -> {val!r}")
            _speak(f"Your email is {val}.")
        else:
            _speak("I don't have your email yet.")
        return True

    # Generic recall: "what is my X"
    m2 = re.match(r"^what is my (.+)$", n)
    if m2:
        key = m2.group(1).strip()
        val = _recall_fact(key)
        if val:
            _speak(f"Your {key} is {val}.")
        else:
            _speak(f"I don't have your {key} yet.")
        return True

    return False

def _patch_routerengine_process():
    try:
        re_mod = importlib.import_module("router_engine")
        RouterEngine = getattr(re_mod, "RouterEngine", None)
        if not RouterEngine or not hasattr(RouterEngine, "process"):
            return False
        orig = RouterEngine.process

        def patched(self, text: str, *args, **kwargs):
            if isinstance(text, str) and _maybe_intercept(text):
                return {
                    "intent": "MEMORY_CONSUMED",
                    "confidence": 1.0,
                    "raw_text": text,
                    "require_confirmation": False,
                    "ts": _now_ts(),
                    "clarification_questions": [],
                }
            return orig(self, text, *args, **kwargs)

        RouterEngine.process = patched
        print("[MEMORY_V6] patched: router_engine.RouterEngine.process")
        return True
    except Exception as e:
        print(f"[MEMORY_V6] patch error: {e}")
        return False

def main():
    print("[MEMORY_V6] Installing memory interception...")
    _patch_routerengine_process()

    import run_voice_clean
    print("[MEMORY_V6] Starting voice loop (delegating to run_voice_clean.main())")
    run_voice_clean.main()

if __name__ == "__main__":
    main()
