#!/usr/bin/env python3
import re, time, importlib
from typing import Optional

def _now_ts() -> float:
    return time.time()

def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())

def _speak(text: str):
    import os
    os.system(f'say "{text.replace(chr(34), "")}"')

# --- memory store hookup (use existing memory_store if present) ---
_store = None
try:
    ms = importlib.import_module("memory_store")
    MemoryStore = getattr(ms, "MemoryStore", None)
    if MemoryStore:
        _store = MemoryStore()
except Exception:
    _store = None

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

# --- parsing ---
WAKE_ALIASES = {
    "demerzel","dammers","dam er zel","dammerz","dam brazil","dam brazill","dam roselle","dam result"
}

def _strip_leading_wake(s: str) -> str:
    n = _norm(s)
    for a in sorted(WAKE_ALIASES, key=len, reverse=True):
        if n == a:
            return ""
        if n.startswith(a + " "):
            # drop same number of words as alias
            drop = len(a.split())
            parts = s.strip().split()
            return " ".join(parts[drop:]).strip()
    return s.strip()

REMEMBER_RE = re.compile(r"^(?:i\s+)?remember(?:\s+that)?\s+(?P<body>.+)$", re.I)
EMAIL_RE = re.compile(r"\bemail\b", re.I)

def _maybe_intercept(raw_in: str) -> bool:
    raw0 = (raw_in or "").strip()
    if not raw0:
        return False

    raw = _strip_leading_wake(raw0)
    if not raw:
        return False

    # IMPORTANT: print every time we intercept-check (so we can prove it's hit)
    print(f"[MEMORY_V7] heard: {raw0!r} -> {raw!r}")

    n = _norm(raw)

    # REMEMBER ...
    m = REMEMBER_RE.match(raw)
    if m:
        body = m.group("body").strip()
        body_norm = body.replace(" at ", "@").replace(" dot ", ".")
        body_norm = re.sub(r"\s+", " ", body_norm).strip()

        # Email special case
        if EMAIL_RE.search(body_norm):
            parts = re.split(r"\bis\b", body_norm, maxsplit=1, flags=re.I)
            value = parts[1].strip() if len(parts) == 2 else body_norm
            ok = _store_fact("email", value)
            print(f"[MEMORY_V7] STORE email ok={ok} value={value!r}")
            _speak("Okay.")
            return True

        # Generic: "remember X is Y"
        kv = re.split(r"\bis\b", body_norm, maxsplit=1, flags=re.I)
        if len(kv) == 2:
            k = _norm(kv[0])
            v = kv[1].strip()
            ok = _store_fact(k, v)
            print(f"[MEMORY_V7] STORE key={k!r} ok={ok} value={v!r}")
            _speak("Okay.")
            return True

        _speak("Okay.")
        print("[MEMORY_V7] remember matched but no key/value; acknowledged.")
        return True

    # RECALL email
    if "what is my email" in n or n == "my email" or n.startswith("recall my email"):
        val = _recall_fact("email")
        print(f"[MEMORY_V7] RECALL email -> {val!r}")
        _speak(f"Your email is {val}." if val else "I don't have your email yet.")
        return True

    # Generic recall: "what is my X"
    m2 = re.match(r"^what is my (.+)$", n)
    if m2:
        key = m2.group(1).strip()
        val = _recall_fact(key)
        print(f"[MEMORY_V7] RECALL {key!r} -> {val!r}")
        _speak(f"Your {key} is {val}." if val else f"I don't have your {key} yet.")
        return True

    return False

def _make_consumed_result(text: str):
    return {
        "intent": "MEMORY_CONSUMED",
        "confidence": 1.0,
        "raw_text": text,
        "require_confirmation": False,
        "ts": _now_ts(),
        "clarification_questions": [],
    }

def _patch_attr(modname: str, clsname: str, fnname: str) -> bool:
    try:
        mod = importlib.import_module(modname)
        cls = getattr(mod, clsname, None)
        if not cls or not hasattr(cls, fnname):
            return False
        orig = getattr(cls, fnname)

        def wrapped(self, text: str, *args, **kwargs):
            if isinstance(text, str) and _maybe_intercept(text):
                return _make_consumed_result(text)
            return orig(self, text, *args, **kwargs)

        setattr(cls, fnname, wrapped)
        print(f"[MEMORY_V7] patched: {modname}.{clsname}.{fnname}")
        return True
    except Exception as e:
        print(f"[MEMORY_V7] patch failed: {modname}.{clsname}.{fnname} err={e}")
        return False

def _patch_func(modname: str, fnname: str) -> bool:
    try:
        mod = importlib.import_module(modname)
        if not hasattr(mod, fnname):
            return False
        orig = getattr(mod, fnname)

        def wrapped(text: str, *args, **kwargs):
            if isinstance(text, str) and _maybe_intercept(text):
                return _make_consumed_result(text)
            return orig(text, *args, **kwargs)

        setattr(mod, fnname, wrapped)
        print(f"[MEMORY_V7] patched: {modname}.{fnname}")
        return True
    except Exception as e:
        print(f"[MEMORY_V7] patch failed: {modname}.{fnname} err={e}")
        return False

def main():
    print("[MEMORY_V7] Installing memory interception (multi-patch)...")

    ok = False
    # try all likely call sites
    ok |= _patch_attr("router_engine", "RouterEngine", "process")
    ok |= _patch_attr("kernel_router", "RouterEngine", "process")
    ok |= _patch_func("kernel_router", "route_text")      # common direct function path
    ok |= _patch_func("router_engine", "route_text")      # if exists

    if not ok:
        print("[MEMORY_V7] WARNING: no patch points found. Will still run voice loop.")

    import run_voice_clean
    print("[MEMORY_V7] Starting voice loop (delegating to run_voice_clean.main())")
    run_voice_clean.main()

if __name__ == "__main__":
    main()
