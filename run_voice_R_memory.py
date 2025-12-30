#!/usr/bin/env python3
import os
import re
import sys
import traceback

from memory_store import MemoryStore

def say(text: str) -> None:
    # macOS TTS
    os.system(f"say {text!r} >/dev/null 2>&1")

def _memory_path() -> str:
    return os.path.expanduser("~/.demerzel/memory.json")

REMEMBER_PATTERNS = [
    # "remember that my wifi password is 1234"
    re.compile(r"^\s*(remember|note)\s+(that\s+)?(.+)\s*$", re.IGNORECASE),
]

FACT_PATTERNS = [
    # "remember my email is amb330@gmail.com"
    re.compile(r"^\s*(remember|note)\s+(that\s+)?(?P<k>my\s+[\w\s\-]+?)\s+(is|=)\s+(?P<v>.+)\s*$", re.IGNORECASE),
    # "my email is ..."
    re.compile(r"^\s*(?P<k>my\s+[\w\s\-]+?)\s+(is|=)\s+(?P<v>.+)\s*$", re.IGNORECASE),
]

RECALL_PATTERNS = [
    # "what do you remember"
    re.compile(r"^\s*(what do you remember|list memories|list memory)\s*$", re.IGNORECASE),
    # "what is my email"
    re.compile(r"^\s*(what is|what's)\s+(?P<k>my\s+[\w\s\-]+?)\s*\??\s*$", re.IGNORECASE),
    # "recall my email"
    re.compile(r"^\s*(recall|remember)\s+(?P<k>my\s+[\w\s\-]+?)\s*\??\s*$", re.IGNORECASE),
    # "recent notes"
    re.compile(r"^\s*(recent notes|last notes|what did i say)\s*$", re.IGNORECASE),
]

def install_router_patch(store: MemoryStore) -> None:
    import router_engine as _re

    orig_process = _re.RouterEngine.process

    def patched_process(self, *args, **kwargs):
        # Be flexible about signature: try to locate the "text" argument.
        text = None
        if args:
            # common case: process(text)
            if isinstance(args[0], str):
                text = args[0]
        if text is None:
            text = kwargs.get("text") if isinstance(kwargs, dict) else None

        if isinstance(text, str):
            t = text.strip()

            # 1) Recall flows
            for pat in RECALL_PATTERNS:
                m = pat.match(t)
                if not m:
                    continue

                if m.groupdict().get("k"):
                    key = m.group("k")
                    val = store.recall_fact(key)
                    if val:
                        reply = f"Your {key.replace('my ', '')} is {val}."
                    else:
                        reply = f"I don't have your {key.replace('my ', '')} yet."
                    print(f"[R] RECALL fact: {key} -> {val}")
                    say(reply)
                    # Return a neutral kernel-like object so baseline doesn't scold you.
                    return {
                        "clarification_questions": [],
                        "confidence": 1.0,
                        "confirmation_prompt": None,
                        "intent": "UNKNOWN",
                        "raw_text": text,
                        "reasoning_trace": {"handled_by": "R_MEMORY", "reply": reply},
                        "require_confirmation": False,
                        "ts": __import__("time").time(),
                    }

                if pat.pattern.lower().find("what do you remember") >= 0 or "list" in pat.pattern.lower():
                    facts = store.recall_all_facts()
                    if not facts:
                        reply = "I don't have any saved facts yet."
                    else:
                        # keep spoken short
                        keys = sorted(facts.keys())[:10]
                        reply = "I remember: " + ", ".join([k.replace("my ", "") for k in keys]) + "."
                    print(f"[R] RECALL all facts: {len(store.recall_all_facts())}")
                    say(reply)
                    return {
                        "clarification_questions": [],
                        "confidence": 1.0,
                        "confirmation_prompt": None,
                        "intent": "UNKNOWN",
                        "raw_text": text,
                        "reasoning_trace": {"handled_by": "R_MEMORY", "reply": reply},
                        "require_confirmation": False,
                        "ts": __import__("time").time(),
                    }

                if "notes" in t.lower() or "what did i say" in t.lower():
                    notes = store.recall_recent_notes(5)
                    if not notes:
                        reply = "No recent notes."
                    else:
                        reply = "Recent notes: " + " ... ".join(notes[:3])
                    print(f"[R] RECALL notes: {len(notes)}")
                    say(reply)
                    return {
                        "clarification_questions": [],
                        "confidence": 1.0,
                        "confirmation_prompt": None,
                        "intent": "UNKNOWN",
                        "raw_text": text,
                        "reasoning_trace": {"handled_by": "R_MEMORY", "reply": reply},
                        "require_confirmation": False,
                        "ts": __import__("time").time(),
                    }

            # 2) Remember flows (facts)
            for pat in FACT_PATTERNS:
                m = pat.match(t)
                if not m:
                    continue
                gd = m.groupdict()
                if gd.get("k") and gd.get("v"):
                    k = gd["k"].strip()
                    v = gd["v"].strip()
                    store.remember_fact(k, v)
                    reply = f"Got it. I'll remember your {k.replace('my ', '')}."
                    print(f"[R] REMEMBER fact: {k} = {v}")
                    say(reply)
                    return {
                        "clarification_questions": [],
                        "confidence": 1.0,
                        "confirmation_prompt": None,
                        "intent": "UNKNOWN",
                        "raw_text": text,
                        "reasoning_trace": {"handled_by": "R_MEMORY", "saved_fact": {k: v}},
                        "require_confirmation": False,
                        "ts": __import__("time").time(),
                    }

            # 3) Remember flows (notes)
            for pat in REMEMBER_PATTERNS:
                m = pat.match(t)
                if not m:
                    continue
                payload = m.group(3).strip()
                # if it looked like a fact, FACT_PATTERNS would have caught it first
                store.remember_note(payload)
                reply = "Noted."
                print(f"[R] REMEMBER note: {payload}")
                say(reply)
                return {
                    "clarification_questions": [],
                    "confidence": 1.0,
                    "confirmation_prompt": None,
                    "intent": "UNKNOWN",
                    "raw_text": text,
                    "reasoning_trace": {"handled_by": "R_MEMORY", "saved_note": payload},
                    "require_confirmation": False,
                    "ts": __import__("time").time(),
                }

        # Fall back to baseline behavior
        return orig_process(self, *args, **kwargs)

    _re.RouterEngine.process = patched_process
    print("[R] RouterEngine.process patched (R memory enabled).")

def main():
    store = MemoryStore(_memory_path())
    store.load()

    try:
        install_router_patch(store)
    except Exception:
        print("[R] Failed to patch router. Stack:")
        traceback.print_exc()
        sys.exit(1)

    # Start your normal wake-polished voice loop (baseline)
    try:
        from run_voice_clean import main as baseline_main
    except Exception:
        print("[R] Could not import run_voice_clean.main. Stack:")
        traceback.print_exc()
        sys.exit(1)

    print("[R] Starting Demerzel with R (memory) enabled.")
    baseline_main()

if __name__ == "__main__":
    main()
