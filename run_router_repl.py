#!/usr/bin/env python3
"""
run_router_repl.py

Deterministic typed REPL for testing Demerzel routing without audio/STT.

This REPL intentionally goes through RouterEngine so the REPL and voice entrypoints
can share the same pipeline.

Usage:
    python3 run_router_repl.py
"""

from router_engine import RouterEngine
from kernel_router import RouterState


def main() -> None:
    eng = RouterEngine()
    st = RouterState()

    print("[REPL] Type text. Ctrl+C / Ctrl+D to exit.")
    while True:
        try:
            s = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[EXIT]")
            return

        if not s:
            continue

        out = eng.process(s, st)
        st = out.new_state

        if out.speak:
            print(out.speak)

        dbg = out.debug or {}
        print(
            f"[debug] mode={dbg.get('mode')} intent={dbg.get('intent')} "
            f"confidence={dbg.get('confidence')} confirm_required={dbg.get('router_confirmation_required')}"
        )

        if getattr(out, "effects", None) and out.effects.enter_sleep_mode:
            print("[effect] enter_sleep_mode=True")


if __name__ == "__main__":
    main()
