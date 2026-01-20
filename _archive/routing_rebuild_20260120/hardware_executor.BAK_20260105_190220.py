#!/usr/bin/env python3
"""
hardware_executor.py (Mac side)

Purpose:
- Called by kernel_router (as a class) via:
    hw = HardwareExecutor()
    hw.ping(), hw.led_on(), hw.led_off()
- Also callable directly from CLI:
    python3 hardware_executor.py ping
    python3 hardware_executor.py led_on
    python3 hardware_executor.py led_off
"""

from __future__ import annotations

import os
import shlex
import subprocess
import sys
from dataclasses import dataclass


# ---- Defaults (match your setup) ----
DEFAULT_SSH_USER = os.environ.get("DEMERZEL_PI_USER", "moketchups")
DEFAULT_SSH_HOST = os.environ.get("DEMERZEL_PI_HOST", "192.168.0.161")
DEFAULT_REMOTE_PY = os.environ.get("DEMERZEL_PI_PY", "python3")
DEFAULT_REMOTE_CMD = os.environ.get("DEMERZEL_PI_CMD", "/home/moketchups/arduino_cmd.py")

DEFAULT_TIMEOUT_S = float(os.environ.get("DEMERZEL_SSH_TIMEOUT", "8.0"))


@dataclass
class HWResult:
    ok: bool
    out: str = ""
    err: str = ""
    rc: int = 0


def _normalize_action(s: str) -> str:
    """
    Accepts: ping, PING, led_on, LED ON, lights on, etc.
    Returns one of: PING, LED_ON, LED_OFF
    """
    t = s.strip().lower().replace("-", "_")
    t = t.replace("  ", " ")
    t = t.replace(" ", "_")

    if t in ("ping",):
        return "PING"
    if t in ("led_on", "lights_on", "light_on"):
        return "LED_ON"
    if t in ("led_off", "lights_off", "light_off"):
        return "LED_OFF"

    # allow exact pass-through for advanced use
    return s.strip().upper()


class HardwareExecutor:
    def __init__(
        self,
        user: str = DEFAULT_SSH_USER,
        host: str = DEFAULT_SSH_HOST,
        remote_py: str = DEFAULT_REMOTE_PY,
        remote_cmd: str = DEFAULT_REMOTE_CMD,
        timeout_s: float = DEFAULT_TIMEOUT_S,
    ):
        self.user = user
        self.host = host
        self.remote_py = remote_py
        self.remote_cmd = remote_cmd
        self.timeout_s = timeout_s

    # --- Methods the router expects ---
    def ping(self) -> HWResult:
        return self.send("PING")

    def led_on(self) -> HWResult:
        return self.send("LED_ON")

    def led_off(self) -> HWResult:
        return self.send("LED_OFF")

    # --- Generic executor ---
    def send(self, action: str, debug: bool = False) -> HWResult:
        action = _normalize_action(action)

        ssh_target = f"{self.user}@{self.host}"

        # IMPORTANT: remote side expects arduino_cmd.py argument like:
        #   python3 /home/moketchups/arduino_cmd.py PING
        # or LED ON / LED OFF depending on your Pi script.
        # We'll send LED ON / LED OFF because your logs showed that format working.
        if action == "PING":
            remote_arg = "PING"
        elif action == "LED_ON":
            remote_arg = "LED ON"
        elif action == "LED_OFF":
            remote_arg = "LED OFF"
        else:
            remote_arg = action

        remote_cmd = f"{self.remote_py} {shlex.quote(self.remote_cmd)} {shlex.quote(remote_arg)}"

        cmd = [
            "ssh",
            "-o", "BatchMode=yes",
            "-o", "ConnectTimeout=3",
            ssh_target,
            remote_cmd,
        ]

        if debug:
            print(f"[debug] SSH target={ssh_target}")
            print(f"[debug] remote={remote_cmd}")

        try:
            p = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout_s,
            )
        except subprocess.TimeoutExpired:
            return HWResult(ok=False, err=f"timeout after {self.timeout_s:.1f}s", rc=124)

        out = (p.stdout or "").strip()
        err = (p.stderr or "").strip()
        ok = (p.returncode == 0)

        return HWResult(ok=ok, out=out, err=err, rc=p.returncode)


def main(argv: list[str]) -> int:
    # usage:
    #   python3 hardware_executor.py ping
    #   python3 hardware_executor.py led_on
    #   python3 hardware_executor.py led_off
    #   python3 hardware_executor.py --debug ping
    debug = False
    args = argv[1:]

    if not args:
        action = "PING"
    else:
        if args[0] == "--debug":
            debug = True
            args = args[1:]
        action = args[0] if args else "PING"

    hw = HardwareExecutor()
    r = hw.send(action, debug=debug)

    if r.ok:
        # print ONLY stdout for clean piping
        if r.out:
            print(r.out)
        return 0

    # error path
    if r.err:
        print(f"ERR {r.err}")
    else:
        print("ERR unknown")

    if r.out:
        print(r.out)

    return r.rc if r.rc != 0 else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
