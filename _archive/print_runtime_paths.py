#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import os
import sys
import importlib

MODULES = [
    "brain_controller",
    "kernel_connect",
    "kernel_router",
    "hardware_executor",
]

DOCS = [
    "EXECUTION_SAFETY_CONTRACT.md",
    "ROUTER_INVARIANTS.md",
    "BASELINE.md",
]

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

def main() -> int:
    print("== Runtime ==")
    print("cwd:", os.getcwd())
    print("python:", sys.executable)
    print("version:", sys.version.replace("\n", " "))
    print()

    print("== Module file paths ==")
    for name in MODULES:
        try:
            m = importlib.import_module(name)
            print(f"{name}: {getattr(m, '__file__', None)}")
        except Exception as e:
            print(f"{name}: IMPORT ERROR: {e}")
    print()

    print("== Governance doc hashes ==")
    for fn in DOCS:
        if os.path.exists(fn):
            print(f"{fn}: {sha256_file(fn)}")
        else:
            print(f"{fn}: MISSING")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

