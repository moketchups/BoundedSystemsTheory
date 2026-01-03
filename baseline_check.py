#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys

def run(cmd: list[str]) -> int:
    print("\n$ " + " ".join(cmd))
    return subprocess.call(cmd)

def main() -> int:
    if run([sys.executable, "wiring_check.py"]) != 0:
        print("\n[FAIL] wiring_check failed")
        return 1

    if run(["pytest", "-q"]) != 0:
        print("\n[FAIL] pytest failed")
        return 1

    print("\n[PASS] baseline is intact (topology + invariants).")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

