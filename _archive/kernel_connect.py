#!/usr/bin/env python3
"""
kernel_connect.py

Deterministic intent kernel (no LLM).
Derives an intent + confidence from normalized text.

Important:
- This kernel DOES NOT execute anything.
- Confirmation policy is enforced at the execution boundary (kernel_router.py).
- The kernel may provide requires_confirmation/prompts for transparency, but the router is authoritative.

Intent allowlist (v1):
- ping
- led on / led off
- time
- sleep
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional
import re


class Intent(str, Enum):
    UNKNOWN = "unknown"
    PING = "ping"
    LED_ON = "led_on"
    LED_OFF = "led_off"
    TIME_QUERY = "time"
    SLEEP = "sleep"


@dataclass
class KernelResult:
    intent: Intent
    confidence: float
    # Optional hints (router is authoritative)
    requires_confirmation: bool = False
    confirmation_prompt: Optional[str] = None
    clarification_questions: Optional[List[str]] = None


def kernel_result_to_json_str(result: KernelResult) -> str:
    cq = result.clarification_questions or []
    return (
        "{"
        f"intent={result.intent.value!r}, "
        f"confidence={result.confidence:.2f}, "
        f"requires_confirmation={result.requires_confirmation}, "
        f"confirmation_prompt={result.confirmation_prompt!r}, "
        f"clarification_questions={cq!r}"
        "}"
    )


def validate_kernel_result(result: KernelResult) -> None:
    if not isinstance(result, KernelResult):
        raise TypeError("KernelResult must be a KernelResult dataclass instance")
    if not isinstance(result.intent, Intent):
        raise TypeError("KernelResult.intent must be an Intent")
    if not isinstance(result.confidence, (int, float)):
        raise TypeError("KernelResult.confidence must be numeric")
    if not (0.0 <= float(result.confidence) <= 1.0):
        raise ValueError("KernelResult.confidence must be within [0, 1]")
    if result.intent == Intent.UNKNOWN:
        if not result.clarification_questions:
            raise ValueError("UNKNOWN intent must include clarification_questions")


def _norm(text: str) -> str:
    t = (text or "").strip().lower()
    t = re.sub(r"[^a-z0-9\s']", " ", t)
    t = re.sub(r"\s+", " ", t).strip()

    # Fix "l e d" -> "led"
    t = re.sub(r"\bl\s*e\s*d\b", "led", t)
    # Fix "lead" -> "led"
    t = re.sub(r"\blead\b", "led", t)

    return t


def run_kernel(text: str) -> KernelResult:
    t = _norm(text)
    compact = t.replace(" ", "")

    if not t:
        return KernelResult(
            intent=Intent.UNKNOWN,
            confidence=0.0,
            clarification_questions=["Say one of: ping, led on, led off, time, sleep."],
        )

    # PING
    if t in {"ping", "test ping"}:
        return KernelResult(intent=Intent.PING, confidence=0.95)

    # TIME
    if t in {"time", "what time is it", "tell me the time"}:
        return KernelResult(intent=Intent.TIME_QUERY, confidence=0.95)

    # SLEEP
    if t in {"sleep", "go to sleep", "go idle"}:
        return KernelResult(
            intent=Intent.SLEEP,
            confidence=0.92,
            requires_confirmation=True,
            confirmation_prompt="Confirm sleep mode? (yes/no)",
        )

    # LED ON/OFF (variants)
    led_on_variants = {
        "led on",
        "turn on led",
        "turn led on",
        "turn on the led",
        "turn the led on",
        "light on",
        "turn on the light",
        "turn the light on",
    }
    led_off_variants = {
        "led off",
        "turn off led",
        "turn led off",
        "turn off the led",
        "turn the led off",
        "light off",
        "turn off the light",
        "turn the light off",
    }

    if t in led_on_variants or compact in {"ledon", "turnonled", "lighton"}:
        return KernelResult(
            intent=Intent.LED_ON,
            confidence=0.90,
            requires_confirmation=True,
            confirmation_prompt="Confirm LED ON? (yes/no)",
        )

    if t in led_off_variants or compact in {"ledoff", "turnoffled", "lightoff"}:
        return KernelResult(
            intent=Intent.LED_OFF,
            confidence=0.90,
            requires_confirmation=True,
            confirmation_prompt="Confirm LED OFF? (yes/no)",
        )

    # Partial cues (intentionally lower confidence)
    if ("led" in t or "light" in t) and "on" in t:
        return KernelResult(
            intent=Intent.LED_ON,
            confidence=0.78,
            requires_confirmation=True,
            confirmation_prompt="Confirm LED ON? (yes/no)",
        )

    if ("led" in t or "light" in t) and "off" in t:
        return KernelResult(
            intent=Intent.LED_OFF,
            confidence=0.78,
            requires_confirmation=True,
            confirmation_prompt="Confirm LED OFF? (yes/no)",
        )

    return KernelResult(
        intent=Intent.UNKNOWN,
        confidence=0.10,
        clarification_questions=["Say one of: ping, led on, led off, time, sleep."],
    )

