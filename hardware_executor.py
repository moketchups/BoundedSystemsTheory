# hardware_executor.py
from __future__ import annotations

from dataclasses import dataclass
import subprocess
from typing import Optional, List


PI_USER = "moketchups"
PI_HOST = "192.168.0.161"
PI_ARDUINO_CMD = "/home/moketchups/arduino_cmd.py"


@dataclass
class HWResult:
    ok: bool
    out: str = ""
    err: str = ""
    rc: int = 0


def _run(cmd: List[str], timeout_s: float = 8.0) -> HWResult:
    try:
        p = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
        out = (p.stdout or "").strip()
        err = (p.stderr or "").strip()
        return HWResult(ok=(p.returncode == 0), out=out, err=err, rc=p.returncode)
    except subprocess.TimeoutExpired as e:
        return HWResult(ok=False, out="", err=f"timeout after {timeout_s}s", rc=124)
    except Exception as e:
        return HWResult(ok=False, out="", err=str(e), rc=1)


def send_to_arduino(arduino_command: str, timeout_s: float = 8.0) -> HWResult:
    """
    Module-level function expected by some router versions.
    Sends a single command to the Pi-side arduino_cmd.py over SSH.
    """
    remote = f"python3 {PI_ARDUINO_CMD} {arduino_command}"
    cmd = ["ssh", f"{PI_USER}@{PI_HOST}", remote]
    return _run(cmd, timeout_s=timeout_s)


class HardwareExecutor:
    """
    Class-based API expected by other versions.
    """
    def __init__(self, timeout_s: float = 8.0):
        self.timeout_s = timeout_s

    def send_to_arduino(self, arduino_command: str) -> HWResult:
        return send_to_arduino(arduino_command, timeout_s=self.timeout_s)

    def ping(self) -> HWResult:
        return self.send_to_arduino("PING")

    def led_on(self) -> HWResult:
        return self.send_to_arduino("LED ON")

    def led_off(self) -> HWResult:
        return self.send_to_arduino("LED OFF")


def _demo():
    hw = HardwareExecutor()
    for c in ["PING", "LED ON", "LED OFF"]:
        r = hw.send_to_arduino(c)
        print(f"{c} -> ok={r.ok} rc={r.rc} out='{r.out}' err='{r.err}'")


if __name__ == "__main__":
    _demo()

