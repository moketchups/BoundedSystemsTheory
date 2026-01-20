#!/usr/bin/env python3
"""
hardware_executor.py (Mac side)

Runs hardware commands by SSHing into the Pi and calling arduino_cmd.py.

Goals:
- Stable contract for the rest of Demerzel:
    - class HardwareExecutor
    - .send(action: str) -> HWResult
    - .send_to_arduino(action: str) -> HWResult  (alias for back-compat)
- Useful error reporting (no more mystery "Hardware call failed")
"""

from __future__ import annotations

from dataclasses import dataclass
import os
import shlex
import subprocess
import sys
from typing import List, Optional


@dataclass
class HWResult:
    ok: bool
    out: str = ""
    err: str = ""
    rc: int = 0
    debug: str = ""  # command + context


class HardwareExecutor:
    def __init__(
        self,
        pi_user: Optional[str] = None,
        pi_host: Optional[str] = None,
        remote_script: Optional[str] = None,
        timeout_s: float = 8.0,
    ):
        # Allow env overrides so you don't have to edit code.
        self.pi_user = pi_user or os.getenv("PI_USER", "moketchups")
        self.pi_host = pi_host or os.getenv("PI_HOST", "192.168.0.161")
        self.remote_script = remote_script or os.getenv(
            "PI_ARDUINO_CMD", "/home/moketchups/arduino_cmd.py"
        )
        self.timeout_s = float(os.getenv("HW_TIMEOUT_S", str(timeout_s)))

        # Good SSH defaults for this use case.
        self.ssh_base: List[str] = [
            "ssh",
            "-o", "BatchMode=yes",
            "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null",
            "-o", "ConnectTimeout=3",
        ]

    def _normalize_action(self, a: str) -> str:
        """
        Map common inputs to the Pi script's expected command strings.
        We choose the 'space' versions because that's what your Pi side previously used.
        """
        s = (a or "").strip()
        if not s:
            return "PING"

        low = s.lower().replace("-", "_").replace(" ", "_")

        if low in ("ping",):
            return "PING"

        if low in ("led_on", "lights_on", "light_on"):
            return "LED ON"

        if low in ("led_off", "lights_off", "light_off"):
            return "LED OFF"

        # If caller already passed "LED ON" / "LED OFF" / "PING", keep it.
        up = s.upper()
        if up in ("PING", "LED ON", "LED OFF"):
            return up

        # Fall back: uppercase raw string (lets you add new commands later).
        return s.strip().upper()

    def send(self, action: str) -> HWResult:
        action_norm = self._normalize_action(action)

        remote_cmd = f"python3 {shlex.quote(self.remote_script)} {shlex.quote(action_norm)}"
        target = f"{self.pi_user}@{self.pi_host}"
        cmd = self.ssh_base + [target, remote_cmd]

        debug = f"SSH target={target} remote={remote_cmd}"

        try:
            p = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout_s,
            )
            out = (p.stdout or "").strip()
            err = (p.stderr or "").strip()
            ok = (p.returncode == 0)

            # If Pi script prints ACK ... but returns nonzero, still show both.
            return HWResult(ok=ok, out=out, err=err, rc=p.returncode, debug=debug)

        except subprocess.TimeoutExpired as e:
            return HWResult(
                ok=False,
                out=(e.stdout or "").strip() if e.stdout else "",
                err=f"TIMEOUT after {self.timeout_s}s",
                rc=124,
                debug=debug,
            )
        except Exception as e:
            return HWResult(ok=False, out="", err=f"EXCEPTION: {e}", rc=1, debug=debug)

    # Back-compat alias (you hit this exact mismatch earlier)
    def send_to_arduino(self, action: str) -> HWResult:
        return self.send(action)


def _main() -> int:
    action = "PING"
    debug = False

    args = sys.argv[1:]
    if "--debug" in args:
        debug = True
        args = [a for a in args if a != "--debug"]

    if args:
        action = " ".join(args)

    hw = HardwareExecutor()
    r = hw.send(action)

    if debug:
        print(f"[debug] {r.debug}")
        print(f"[debug] rc={r.rc} ok={r.ok}")

    if r.ok:
        if r.out:
            print(r.out)
        else:
            # success but no output (rare, but don't make it look like a crash)
            print("OK")
        return 0

    # Fail: print the most useful info we have.
    if r.err:
        print(f"ERR {r.err}")
    else:
        print("ERR unknown")

    if r.out:
        print(r.out)

    return r.rc if r.rc != 0 else 1


if __name__ == "__main__":
    raise SystemExit(_main())

