"""
RouterEngine: coordinates kernel_router + hardware executor.
"""
from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from typing import Optional, List

from kernel_contract import RouterState, RouterOutput
import kernel_router as kr
from hardware_executor import HardwareExecutor, default_config

class RouterEngine:
    def __init__(self, hardware: Optional[HardwareExecutor] = None, wake_aliases: Optional[List[str]] = None):
        self.state = RouterState()
        self.hardware = hardware or HardwareExecutor(default_config())
        self.wake_aliases = [w.strip().lower() for w in (wake_aliases or ["demerzel"]) if w.strip()]

    def route_text(self, text: str) -> RouterOutput:
        out, new_state = kr.route_text(text, self.state)
        self.state = new_state

        if out.intent == "TIME" and out.speak == "__TIME__":
            now = datetime.now()
            return replace(out, speak=now.strftime("It is %-I:%M %p."))

        if out.hw_cmd and out.did_execute:
            hw = self.hardware.send_to_arduino(out.hw_cmd)
            if hw.ok:
                speak = hw.out.strip() or f"ACK {out.hw_cmd}"
                return replace(out, speak=speak)
            speak = f"Hardware error: {hw.err or hw.out or 'unknown'}"
            return replace(out, speak=speak, did_execute=False, error=hw.err or hw.out)

        return out

