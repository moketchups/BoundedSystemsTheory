#!/usr/bin/env python3
"""
Memory polish v5:
- NO baseline edits
- Patches multiple likely entry points (RouterEngine.process, kernel_router.route, etc.)
- Intercepts "remember ..." and "what is my ..." / "recall ..." phrases BEFORE kernel clarifier
"""

import re
import time
import importlib
from typing import Optional

def _now_ts() -> float:
    return time.time()

def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())

# --- memory store (use existing if present) ---
_store = None
try:
    ms = importlib.import_module("memory_store")
    _store = getattr(ms, "MemoryStore", None)
    if _store:
        _store = _store()
except Exception:
    _store = None

def _speak(text: str):
    # Use existing say helper if available; else fallback to macOS `say`
    try:
        util = importlib.import_module("voice_utils")
        say = getattr(util, "say", None)
        if callable(say):
            say(text)
            return
    except Exception:
        pass
    import os
    os.system(f'say "{text.replace(chr(34), "")}"')

def _store_fact(key: str, value: str):
    if _store and hasattr(_store, "remember_fact"):
        _store.remember_fact(key, value)
        return True
    # fallback: try memory.py store if exists
    try:
        mem = importlib.import_module("memory")
        remember = getattr(mem, "remember_fact", None)
        if callable(remember):
            remember(key, value)
            return True
    except Exception:
        pass
    return False

def _recall_fact(key: str) -> Optional[str]:
    if _store and hasattr(_store, "recall_fact"):
        return _store.recall_fact(key)
    try:
        mem = importlib.import_module("memory")
        recall = getattr(mem, "recall_fact", None)
        if callable(recall):
            return recall(key)
    except Exception:
        pass
    return None

# --- phrase handlers ---
REMEMBER_RE = re.compile(r"^(?:our\s+)?remember(?:\s+that)?\s+(?P<body>.+)$", re.I)
EMAIL_RE = re.compile(r"\bemail\b", re.I)

def _maybe_intercept(text: str) -> bool:
    """
    Return True if consumed (do not pass to kernel).
    """
    raw = (text or "").strip()
    n = _norm(raw)

    if not n:
        return False

    # log what we see
    print(f"[MEMORY_V5] heard: {raw!r}")

    # Remember: "remember my email is X"
    m = REMEMBER_RE.match(raw.strip())
    if m:
        body = m.group("body").strip()

        # normalize common Vosk 'at / dot' patterns lightly
        body_norm = body.replace(" at ", "@").replace(" dot ", ".")
        body_norm = re.sub(r"\s+", " ", body_norm).strip()

        # If they said "my email is ..."
        if EMAIL_RE.search(body_norm):
            # try to extract right side after "is"
            parts = re.split(r"\bis\b", body_norm, maxsplit=1, flags=re.I)
            value = parts[1].strip() if len(parts) == 2 else body_norm
            ok = _store_fact("email", value)
            if ok:
                print(f"[MEMORY_V5] STORED fact: email = {value!r}")
                _speak("Okay.")
                return True

        # Generic "remember X is Y" => store key/value
        kv = re.split(r"\bis\b", body_norm, maxsplit=1, flags=re.I)
        if len(kv) == 2:
            k = _norm(kv[0])
            v = kv[1].strip()
            ok = _store_fact(k, v)
            if ok:
                print(f"[MEMORY_V5] STORED fact: {k} = {v!r}")
                _speak("Okay.")
                return True

        # If we can't store, still acknowledge so it doesn't feel dead
        _speak("Okay.")
        print("[MEMORY_V5] remember matched but no store backend found; acknowledged.")
        return True

    # Recall: "what is my email" / "recall my email"
    if "what is my email" in n or n == "my email" or n.startswith("recall my email"):
        val = _recall_fact("email")
        if val:
            print(f"[MEMORY_V5] RECALL email -> {val!r}")
            _speak(f"Your email is {val}.")
        else:
            _speak("I don't have your email yet.")
        return True

    # Generic: "what is my X" (try last word(s) as key)
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

# --- patch targets ---
def _patch_attr(modname: str, attr: str):
    try:
        mod = importlib.import_module(modname)
    except Exception:
        return False

    fn = getattr(mod, attr, None)
    if not callable(fn):
        return False

    # wrap
    def wrapped(*args, **kwargs):
        # try to locate text argument
        text = None
        for a in args[::-1]:
            if isinstance(a, str):
                text = a
                break
        if text is None:
            text = kwargs.get("text") or kwargs.get("final_text") or kwargs.get("utterance")

        if isinstance(text, str) and _maybe_intercept(text):
            # return a shape that won't crash most callers
            return {
                "intent": "MEMORY_CONSUMED",
                "confidence": 1.0,
                "raw_text": text,
                "require_confirmation": False,
                "ts": _now_ts(),
                "clarification_questions": [],
            }
        return fn(*args, **kwargs)

    setattr(mod, attr, wrapped)
    print(f"[MEMORY_V5] patched: {modname}.{attr}")
    return True

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
        print("[MEMORY_V5] patched: router_engine.RouterEngine.process")
        return True
    except Exception:
        return False

def main():
    print("[MEMORY_V5] Installing multi-entrypoint memory interception...")
    ok_any = False

    # Patch likely places
    ok_any |= _patch_routerengine_process()

    # Common alternates (names may vary)
    ok_any |= _patch_attr("kernel_router", "route")
    ok_any |= _patch_attr("kernel_router", "route_text")
    ok_any |= _patch_attr("brain_controller", "handle_final_text")
    ok_any |= _patch_attr("run_voice_clean", "handle_final_text")

    if not ok_any:
        print("[MEMORY_V5] WARNING: no patch points found; will still run voice loop.")

    # Run the normal voice loop entry point
    import run_voice_clean
    print("[MEMORY_V5] Starting voice loop (delegating to run_voice_clean.main())")
    run_voice_clean.main()

if __name__ == "__main__":
    main()
