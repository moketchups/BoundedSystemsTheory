#!/usr/bin/env python3
"""
Memory-polish runner for Demerzel (MAC).

- Does NOT modify baseline files.
- Patches RouterEngine.process at runtime:
    * "remember ..."  -> store fact + speak "Okay."
    * "what's my ..." -> recall fact + speak answer
    * "forget ..."    -> delete fact + speak "Okay."
- Then delegates to run_voice_clean.main()
"""

import re
import json
import time
import subprocess
from pathlib import Path

# ----------------------------
# Voice output (MAC)
# ----------------------------
def say(text: str):
    text = (text or "").strip()
    if not text:
        return
    try:
        subprocess.run(["say", text], check=False)
    except Exception:
        print(f"[SAY_FALLBACK] {text}")

# ----------------------------
# Minimal memory store (JSON)
# ----------------------------
MEM_FILE = Path.home() / ".demerzel_memory.json"

def _load_mem():
    if MEM_FILE.exists():
        try:
            return json.loads(MEM_FILE.read_text())
        except Exception:
            return {"facts": {}}
    return {"facts": {}}

def _save_mem(db):
    try:
        MEM_FILE.write_text(json.dumps(db, indent=2, sort_keys=True))
    except Exception as e:
        print("[MEMORY] Failed to save:", e)

def mem_set(key: str, value: str):
    db = _load_mem()
    db.setdefault("facts", {})
    db["facts"][key] = {"value": value, "ts": time.time()}
    _save_mem(db)

def mem_get(key: str):
    db = _load_mem()
    v = db.get("facts", {}).get(key)
    return v.get("value") if isinstance(v, dict) else None

def mem_forget(key: str):
    db = _load_mem()
    if key in db.get("facts", {}):
        db["facts"].pop(key, None)
        _save_mem(db)
        return True
    return False

# ----------------------------
# Parsing / normalization
# ----------------------------
KEY_ALIASES = {
    "email": ["email", "e mail", "gmail", "email address"],
    "phone": ["phone", "phone number", "cell", "cellphone", "mobile"],
    "garage_code": ["garage code", "garage door code", "garage"],
}

def normalize_space(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())

def resolve_key(text: str):
    t = normalize_space(text)
    # direct "my email" style
    t = t.replace("what's", "what is")
    t = t.replace("whats", "what is")
    t = t.replace("e-mail", "email")
    # find best alias match
    for key, aliases in KEY_ALIASES.items():
        for a in aliases:
            if a in t:
                return key
    # fallback: last token-ish (very conservative)
    return None

REMEMBER_RE = re.compile(r"^\s*remember(?:\s+that)?\s+my\s+(.+?)\s+(?:is|equals|=)\s+(.+?)\s*$", re.I)
RECALL_RE   = re.compile(r"^\s*(?:what(?:'s|\s+is)|tell\s+me)\s+my\s+(.+?)\s*$", re.I)
FORGET_RE   = re.compile(r"^\s*forget\s+my\s+(.+?)\s*$", re.I)

def try_memory_intercept(final_text: str) -> bool:
    """
    Returns True if handled (consume; do not route).
    """
    raw = (final_text or "").strip()
    if not raw:
        return False

    m = REMEMBER_RE.match(raw)
    if m:
        key_phrase = m.group(1).strip()
        value = m.group(2).strip()
        key = resolve_key(key_phrase) or normalize_space(key_phrase).replace(" ", "_")
        mem_set(key, value)
        say("Okay.")
        print(f"[MEMORY] stored {key} = (hidden)")
        return True

    m = FORGET_RE.match(raw)
    if m:
        key_phrase = m.group(1).strip()
        key = resolve_key(key_phrase) or normalize_space(key_phrase).replace(" ", "_")
        existed = mem_forget(key)
        say("Okay.")
        print(f"[MEMORY] forgot {key} (existed={existed})")
        return True

    m = RECALL_RE.match(raw)
    if m:
        key_phrase = m.group(1).strip()
        key = resolve_key(key_phrase) or normalize_space(key_phrase).replace(" ", "_")
        value = mem_get(key)
        if value:
            say(f"Your {key_phrase} is {value}.")
            print(f"[MEMORY] recall {key} -> {value}")
        else:
            say(f"I don't have your {key_phrase} yet.")
            print(f"[MEMORY] recall {key} -> None")
        return True

    return False

# ----------------------------
# Patch RouterEngine.process
# ----------------------------
def patch_router_engine():
    import router_engine

    if not hasattr(router_engine, "RouterEngine"):
        print("[MEMORY_POLISH] Could not find RouterEngine in router_engine.py")
        return False

    Orig = router_engine.RouterEngine.process

    def patched(self, final_text: str):
        if try_memory_intercept(final_text):
            # consumed — do not route into "ping/led/time/sleep" clarifier
            return None
        return Orig(self, final_text)

    router_engine.RouterEngine.process = patched
    print("[MEMORY_POLISH] RouterEngine.process patched (remember/recall/forget enabled).")
    return True

def main():
    ok = patch_router_engine()
    if not ok:
        print("[MEMORY_POLISH] Aborting (patch failed).")
        return

    import run_voice_clean
    print("[MEMORY_POLISH] Starting voice loop (delegating to run_voice_clean.main())...")
    run_voice_clean.main()

if __name__ == "__main__":
    main()
