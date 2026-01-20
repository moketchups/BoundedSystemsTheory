#!/usr/bin/env python3
"""
hardware_executor.py (Mac side)

Stable interface used by kernel_router.py

Contract:
- class HardwareExecutor with: ping(), led_on(), led_off()
- returns HWResult(ok, out, err, rc)

IMPORTANT:
Your Pi/Arduino currently expects commands with SPACES:
  "LED ON" and "LED OFF"
NOT underscores.
"""

from __future__ import annotations

from dataclasses import dataclass
import subprocess
import sys


@dataclass
class HWResult:
    ok: bool
    out: str
    err: str
    rc: int


class HardwareExecutor:
    def __init__(
        self,
        host: str = "192.168.0.161",
        user: str = "moketchups",
        remote_python: str = "python3",
        remote_script: str = "/home/moketchups/arduino_cmd.py",
        timeout_s: float = 8.0,
    ) -> None:
        self.host = host
        self.user = user
        self.remote_python = remote_python
        self.remote_script = remote_script
        self.timeout_s = timeout_s

    def _ssh_run(self, remote_cmd: str) -> HWResult:
        cmd = [
            "ssh",
            "-o", "BatchMode=yes",
            "-o", "StrictHostKeyChecking=accept-new",
            "-o", "ConnectTimeout=3",
            f"{self.user}@{self.host}",
            remote_cmd,
        ]
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
            return HWResult(ok=ok, out=out, err=err, rc=p.returncode)
        except subprocess.TimeoutExpired:
            return HWResult(ok=False, out="", err=f"timeout after {self.timeout_s}s", rc=124)
        except Exception as e:
            return HWResult(ok=False, out="", err=str(e), rc=1)

    def send(self, arduino_cmd: str) -> HWResult:
        # NOTE: arduino_cmd may contain spaces, so we wrap it in single quotes
        remote = f"{self.remote_python} {self.remote_script} '{arduino_cmd}'"
        return self._ssh_run(remote)

    def ping(self) -> HWResult:
        return self.send("PING")

    def led_on(self) -> HWResult:
        return self.send("LED ON")

    def led_off(self) -> HWResult:
        return self.send("LED OFF")


def _normalize_cli(s: str) -> str:
    t = s.strip().lower().replace("-", "_").replace(" ", "_")
    if t in ("ping",):
        return "PING"
    if t in ("led_on", "lights_on", "light_on"):
        return "LED ON"
    if t in ("led_off", "lights_off", "light_off"):
        return "LED OFF"
    return s.strip().upper()


if __name__ == "__main__":
    action = _normalize_cli(sys.argv[1]) if len(sys.argv) > 1 else "PING"
    hw = HardwareExecutor()
    r = hw.send(action)
    if r.ok:
        print(r.out)
        sys.exit(0)
    else:
        if r.err:
            print(f"ERR {r.err}")
        else:
            print("ERR unknown")
        if r.out:
            print(r.out)
        sys.exit(r.rc if r.rc != 0 else 1)
