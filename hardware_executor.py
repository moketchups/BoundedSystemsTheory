"""
HardwareExecutor: single place that actually calls the Pi / Arduino.
"""
from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from typing import Optional


@dataclass
class HwResult:
    """Hardware execution result"""
    ok: bool
    out: str = ""
    err: str = ""
    rc: int = 0

@dataclass
class HardwareExecutorConfig:
    pi_host: str
    pi_user: str
    arduino_cmd_path: str
    ssh_key_path: Optional[str] = None
    connect_timeout_s: int = 6
    cmd_timeout_s: int = 10

def _env(name: str, default: str) -> str:
    v = os.environ.get(name, "").strip()
    return v or default

def default_config() -> HardwareExecutorConfig:
    return HardwareExecutorConfig(
        pi_host=_env("DEMERZEL_PI_HOST", "192.168.0.161"),
        pi_user=_env("DEMERZEL_PI_USER", "moketchups"),
        arduino_cmd_path=_env("DEMERZEL_ARDUINO_CMD", "/home/moketchups/arduino_cmd.py"),
        ssh_key_path=os.environ.get("DEMERZEL_SSH_KEY") or None,
    )

class HardwareExecutor:
    def __init__(self, cfg: Optional[HardwareExecutorConfig] = None):
        self.cfg = cfg or default_config()

    def send_to_arduino(self, cmd: str) -> HwResult:
        remote = f'python3 {self.cfg.arduino_cmd_path} "{cmd}"'
        ssh = ["ssh", "-o", "BatchMode=yes", "-o", f"ConnectTimeout={self.cfg.connect_timeout_s}"]
        if self.cfg.ssh_key_path:
            ssh += ["-i", self.cfg.ssh_key_path]
        ssh += [f"{self.cfg.pi_user}@{self.cfg.pi_host}", remote]
        try:
            proc = subprocess.run(ssh, capture_output=True, text=True, timeout=self.cfg.cmd_timeout_s)
            out = (proc.stdout or "").strip()
            err = (proc.stderr or "").strip()
            return HwResult(ok=(proc.returncode == 0), out=out, err=err)
        except subprocess.TimeoutExpired as e:
            return HwResult(ok=False, rc=124, out=(e.stdout or "").strip(), err="timeout")
        except Exception as e:
            return HwResult(ok=False, out="", err=str(e))

