#!/usr/bin/env python3
"""
SACRED TEST RUNNER (text-only)

Goal: prove the "constitution" is structurally correct without touching mic/Vosk.
We simulate wake and feed FINAL text deterministically.

Expected behavior (now 6 lines):
1) /wake           -> SAY: Yes.
2) what time is it -> SAY: It is ...
3) ping            -> SAY: pong
4) /wake           -> SAY: Yes.
5) led on          -> SAY: Confirm? yes or no.
6) yes             -> SAY: Done.

If outputs match the lines above, the constitution is structurally correct.
"""

import os
import subprocess
import sys
from typing import List

EXPECTED_PREFIXES = [
    "SAY: Yes.",
    "SAY: It is ",
    "SAY: pong",
    "SAY: Yes.",
    "SAY: Confirm? yes or no.",
    "SAY: Done.",
]


def run_brain_controller() -> subprocess.Popen:
    env = os.environ.copy()
    # Force text-only CLI loop in brain_controller.py
    env["DEMERZEL_TEXT_ONLY"] = "1"
    # Keep TTS default behavior (it’s already gated by your config elsewhere)
    cmd = [sys.executable, "-u", "brain_controller.py"]
    return subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        env=env,
        universal_newlines=True,
    )


def read_until_ready(proc: subprocess.Popen) -> None:
    assert proc.stdout is not None
    for line in proc.stdout:
        # Print everything (runner is simple + transparent)
        sys.stdout.write(line)
        sys.stdout.flush()
        if "Commands:" in line:
            return


def send(proc: subprocess.Popen, s: str) -> None:
    assert proc.stdin is not None
    proc.stdin.write(s + "\n")
    proc.stdin.flush()


def collect_say_lines(proc: subprocess.Popen, n: int) -> List[str]:
    """Collect next n lines that start with 'SAY:' from subprocess output."""
    out: List[str] = []
    assert proc.stdout is not None
    for line in proc.stdout:
        sys.stdout.write(line)
        sys.stdout.flush()
        if line.startswith("SAY:"):
            out.append(line.strip())
            if len(out) >= n:
                return out
    return out


def main() -> int:
    print("SACRED TEST RUNNER (text-only)\n")
    print("Expected behavior:")
    print("  1) /wake           -> SAY: Yes.")
    print("  2) what time is it -> SAY: It is ...")
    print("  3) ping            -> SAY: pong")
    print("  4) /wake           -> SAY: Yes.")
    print("  5) led on          -> SAY: Confirm? yes or no.")
    print("  6) yes             -> SAY: Done.\n")

    proc = run_brain_controller()

    try:
        read_until_ready(proc)

        # 1) /wake -> Yes
        send(proc, "/wake")
        got = collect_say_lines(proc, 1)

        # 2) time -> It is ...
        send(proc, "what time is it")
        got += collect_say_lines(proc, 1)

        # 3) ping -> pong
        send(proc, "ping")
        got += collect_say_lines(proc, 1)

        # 4) /wake -> Yes
        send(proc, "/wake")
        got += collect_say_lines(proc, 1)

        # 5) led on -> Confirm?
        send(proc, "led on")
        got += collect_say_lines(proc, 1)

        # 6) yes -> Done
        send(proc, "yes")
        got += collect_say_lines(proc, 1)

        print("\n---\nCollected SAY lines:")
        for line in got:
            print(line)

        # Validate prefixes
        ok = True
        if len(got) != len(EXPECTED_PREFIXES):
            ok = False
        else:
            for expected, actual in zip(EXPECTED_PREFIXES, got):
                if not actual.startswith(expected):
                    ok = False
                    break

        if ok:
            print("\nDONE. If outputs match the 6 lines above, the constitution is structurally correct.")
            return 0
        else:
            print("\nFAIL. Output did not match expected structure.")
            return 1

    finally:
        try:
            if proc.poll() is None:
                proc.terminate()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
