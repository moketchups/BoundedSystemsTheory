from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict
import os
import subprocess


@dataclass(frozen=True)
class HwResult:
    ok: bool
    rc: int
    out: str
    err: str


class HardwareBackend:
    """
    Executor only. No interpretation.
    Talks to Pi over SSH and runs arduino_cmd.py with a single string argument.
    """

    def __init__(
        self,
        pi_host: Optional[str] = None,
        remote_cmd: Optional[str] = None,
        ssh_opts: Optional[list[str]] = None,
        timeout_s: int = 8,
    ):
        self.pi_host = pi_host or os.environ.get("DEMERZEL_PI_HOST", "moketchups@192.168.0.161")
        self.remote_cmd = remote_cmd or os.environ.get("DEMERZEL_REMOTE_CMD", "/home/moketchups/arduino_cmd.py")
        self.ssh_opts = ssh_opts or ["-o", "BatchMode=yes", "-o", "ConnectTimeout=3"]
        self.timeout_s = timeout_s

    def _run(self, arg: str) -> HwResult:
        cmd = ["ssh", *self.ssh_opts, self.pi_host, "python3", self.remote_cmd, arg]
        try:
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=self.timeout_s)
            out = (p.stdout or "").strip()
            err = (p.stderr or "").strip()
            return HwResult(p.returncode == 0, p.returncode, out, err)
        except subprocess.TimeoutExpired as e:
            return HwResult(False, 124, "", f"Timeout: {e}")
        except Exception as e:
            return HwResult(False, 1, "", f"Exception: {e}")

    def ping(self) -> HwResult:
        return self._run("PING")

    def led_on(self) -> HwResult:
        return self._run("LED ON")

    def led_off(self) -> HwResult:
        return self._run("LED OFF")

