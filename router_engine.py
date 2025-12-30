# router_engine.py
# Deterministic router/executor layer for Demerzel.
# Voice is a shell; correctness lives in kernel.
# This file only adds "best-effort speaking" for safe informational outputs.

from __future__ import annotations
import kernel_router

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
# =========================
# Unified speech surface
# =========================
def say(text: str) -> None:
    """Single speech surface: always prints + speaks via kernel_router._say on macOS."""
    try:
        kernel_router._say(text)
    except Exception as e:
        # Never go silent; always at least print the failure
        try:
            print(f"[TTS_ERROR] {e}", flush=True)
        except Exception:
            pass

def maybe_say(text: str) -> None:
    # Keep old callsites working
    say(text)

def macos_say(text: str) -> bool:
    # Keep old callsites working; return True if no exception
    try:
        say(text)
        return True
    except Exception:
        return False
