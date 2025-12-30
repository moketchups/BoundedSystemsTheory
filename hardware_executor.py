#!/usr/bin/env python3
"""
hardware_executor.py (Mac side)

Purpose
- Runs on the Mac.
- Sends a single command string to the Raspberry Pi over SSH.
- The Pi forwards it to the Arduino over serial (via ~/arduino_cmd.py).
- Prints the single ACK line returned.

Contract
- Pi script MUST print exactly one final line starting with:
    "ACK ..."
  (Examples: "ACK READY", "ACK PING", "ACK LED ON", "ACK LED OFF")
- This executor accepts ANY "ACK ..." as success.
- If you want to enforce specific ACK payloads later, we can tighten it.

Usage
  python3 hardware_executor.py "PING"
  python3 hardware_executor.py "LED ON"
  python3 hardware_executor.py "LED OFF"
"""

from __future__ import annotations

import os
import shlex
import subprocess
import sys
from dataclasses import dataclass
from typing import Optional


# ----------------------------
# Config (edit only if needed)
# ----------------------------

PI_USER = os.environ.get("PI_USER", "moketchups")
PI_HOST = os.environ.get("PI_HOST", "192.168.0.161")

# Where the Pi-side command bridge lives:
# Based on your screenshots, this is: /home/moketchups/arduino_cmd.py
PI_CMD_PATH = os.environ.get("PI_CMD_PATH", "/home/moketchups/arduino_cmd.py")

# SSH options tuned for reliability / non-interactive operation.
# (BatchMode=yes will FAIL instead of prompting for password — which is what we want.)
SSH_OPTS = [
    "-o", "BatchMode=yes",
    "-o", "StrictHostKeyChecking=accept-new",
    "-o", "ConnectTimeout=5",
]


class HardwareError(RuntimeError):
    pass


@dataclass
class ExecResult:
    rc: int
    out: str
    err: str


def run_ssh(remote_command: str) -> ExecResult:
    """
    Runs a remote command on the Pi via SSH and returns stdout/stderr.
    """
    target = f"{PI_USER}@{PI_HOST}"
    cmd = ["ssh", *SSH_OPTS, target, remote_command]

    p = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
    )

    out = (p.stdout or "").strip()
    err = (p.stderr or "").strip()
    return ExecResult(p.returncode, out, err)


def normalize_ack_line(out: str) -> Optional[str]:
    """
    Extracts the last meaningful ACK line from stdout.
    Accepts any line starting with 'ACK ' or exactly 'ACK'.
    Returns that line, or None if not found.
    """
    if not out:
        return None

    lines = [ln.strip() for ln in out.splitlines() if ln.strip()]
    # Search from bottom upward for the most recent ACK line
    for ln in reversed(lines):
        if ln == "ACK" or ln.startswith("ACK "):
            return ln
    return None


def send_to_arduino(cmd: str) -> str:
    """
    Sends a command string to Arduino via Pi bridge and returns the ACK line.
    Raises HardwareError on failure.
    """
    cmd = (cmd or "").strip()
    if not cmd:
        raise HardwareError("Empty command. Usage: python3 hardware_executor.py \"PING\"")

    # Quote the command safely for remote shell
    safe_cmd = shlex.quote(cmd)

    # Remote invocation: python3 /home/moketchups/arduino_cmd.py "LED ON"
    remote = f"python3 {shlex.quote(PI_CMD_PATH)} {safe_cmd}"

    res = run_ssh(remote)

    if res.rc != 0:
        raise HardwareError(
            "Hardware SSH call failed.\n"
            f"RC: {res.rc}\n"
            f"REMOTE: {remote}\n"
            f"STDOUT:\n{res.out}\n"
            f"STDERR:\n{res.err}\n"
            "\nIf this says it prompted for password, your SSH key isn't being used."
        )

    ack = normalize_ack_line(res.out)
    if not ack:
        raise HardwareError(
            "ERROR: No ACK line found.\n"
            f"REMOTE: {remote}\n"
            f"STDOUT:\n{res.out}\n"
            f"STDERR:\n{res.err}\n"
            "\nExpected a line starting with: ACK ..."
        )

    return ack


def main() -> int:
    if len(sys.argv) < 2:
        print('Usage: python3 hardware_executor.py "PING"')
        return 2

    cmd = " ".join(sys.argv[1:]).strip()

    try:
        ack = send_to_arduino(cmd)
        print(ack)
        return 0
    except HardwareError as e:
        print(str(e), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

