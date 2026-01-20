#!/usr/bin/env python3
"""
run_demerzel.py

One entrypoint so we stop "random-command drifting".

Commands:
  python3 run_demerzel.py check   # compile + pytest + wiring_check
  python3 run_demerzel.py repl    # deterministic router REPL
  python3 run_demerzel.py voice   # live mic (brain_controller)
"""

from __future__ import annotations

import argparse
import subprocess
import sys


CORE_FILES = [
    "brain_controller.py",
    "kernel_router.py",
    "router_engine.py",
    "hardware_executor.py",
    "action_ledger.py",
]


def _run(cmd: list[str]) -> int:
    print(f"\n$ {' '.join(cmd)}")
    return subprocess.call(cmd)


def cmd_check() -> int:
    # 1) Syntax/compile check
    for f in CORE_FILES:
        rc = _run([sys.executable, "-m", "py_compile", f])
        if rc != 0:
            print(f"[FAIL] py_compile: {f}")
            return rc

    # 2) Unit tests
    rc = _run(["pytest", "-q"])
    if rc != 0:
        print("[FAIL] pytest")
        return rc

    # 3) Topology check (no bypass paths)
    rc = _run([sys.executable, "wiring_check.py"])
    if rc != 0:
        print("[FAIL] wiring_check")
        return rc

    print("\n[OK] Baseline is intact (compile + tests + wiring).")
    print("Next: python3 run_demerzel.py repl  OR  python3 run_demerzel.py voice")
    return 0


def cmd_repl() -> int:
    return _run([sys.executable, "run_router_repl.py"])


def cmd_voice() -> int:
    return _run([sys.executable, "brain_controller.py"])


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=["check", "repl", "voice"])
    args = p.parse_args(argv)

    if args.mode == "check":
        return cmd_check()
    if args.mode == "repl":
        return cmd_repl()
    if args.mode == "voice":
        return cmd_voice()

    return 2


if __name__ == "__main__":
    raise SystemExit(main())

