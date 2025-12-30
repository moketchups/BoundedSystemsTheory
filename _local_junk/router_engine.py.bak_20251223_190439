# router_engine.py
# Deterministic router/executor layer for Demerzel.
# Voice is a shell; correctness lives in kernel.
# This file only adds "best-effort speaking" for safe informational outputs.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List
import io
import contextlib
import subprocess

from kernel_router import RouterState, route_text


def _maybe_say(line: str) -> None:
    """Best-effort TTS (must never affect correctness)."""
    try:
        subprocess.run(["say", line], check=False)
    except Exception:
        pass


@dataclass
class RouterEngine:
    high_conf_threshold: float = 0.85
    state: RouterState = field(default_factory=RouterState)

    def process(self, raw_text: str) -> List[str]:
        lines: List[str] = []

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.state = route_text(
                raw_text,
                self.state,
                high_conf_threshold=self.high_conf_threshold,
            )

        kernel_output = [l for l in buf.getvalue().splitlines() if l.strip()]
        lines.extend(kernel_output)

        # Speak only SAFE informational lines we can recognize deterministically.
        for l in kernel_output:
            if l.startswith("Local time is "):
                _maybe_say(l)

        return lines

