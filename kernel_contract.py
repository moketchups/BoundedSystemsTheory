# kernel_contract.py
# Authoritative deterministic kernel contract for Demerzel.
# Voice is a shell; correctness lives here.

from __future__ import annotations

from dataclasses import dataclass, asdict
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import json
import time


class Intent(str, Enum):
    PING = "PING"
    LED_ON = "LED_ON"
    LED_OFF = "LED_OFF"
    TIME_QUERY = "TIME_QUERY"
    SLEEP = "SLEEP"
    UNKNOWN = "UNKNOWN"


# Locked policy:
# - PING, TIME_QUERY: no confirmation
# - LED_ON, LED_OFF, SLEEP: confirmation unless high confidence
NO_CONFIRM_INTENTS = {Intent.PING, Intent.TIME_QUERY}
CONFIRMABLE_INTENTS = {Intent.LED_ON, Intent.LED_OFF, Intent.SLEEP}

# Safe default. Can be adjusted later, but must be explicit & logged.
DEFAULT_HIGH_CONFIDENCE_THRESHOLD = 0.85


@dataclass(frozen=True)
class KernelResult:
    """
    Canonical kernel output. This is the only authoritative output that
    downstream execution is allowed to use.

    Determinism rules:
    - intent must be one of the locked intents
    - confidence must be in [0,1]
    - require_confirmation is computed from policy + confidence
    - if ambiguous or unsafe, intent should be UNKNOWN and must ask user
    """
    intent: Intent
    confidence: float
    require_confirmation: bool

    # If require_confirmation is True, the kernel must provide a deterministic prompt.
    confirmation_prompt: Optional[str]

    # If intent is UNKNOWN or clarification is needed, provide questions deterministically.
    clarification_questions: List[str]

    # For auditability/debugging (never used to justify action execution).
    reasoning_trace: List[str]

    # Input echo (useful for logging/inspection)
    raw_text: str

    # Timestamp (epoch seconds)
    ts: float


class ContractViolation(Exception):
    pass


def _is_finite_number(x: Any) -> bool:
    try:
        return isinstance(x, (int, float)) and x == x and x not in (float("inf"), float("-inf"))
    except Exception:
        return False


def validate_kernel_result(r: KernelResult) -> None:
    if not isinstance(r.intent, Intent):
        raise ContractViolation(f"intent must be an Intent enum, got: {type(r.intent)}")

    if not _is_finite_number(r.confidence):
        raise ContractViolation(f"confidence must be a finite number, got: {r.confidence!r}")

    if r.confidence < 0.0 or r.confidence > 1.0:
        raise ContractViolation(f"confidence must be in [0,1], got: {r.confidence}")

    if not isinstance(r.require_confirmation, bool):
        raise ContractViolation("require_confirmation must be bool")

    if r.confirmation_prompt is not None and not isinstance(r.confirmation_prompt, str):
        raise ContractViolation("confirmation_prompt must be str or None")

    if not isinstance(r.clarification_questions, list) or not all(isinstance(x, str) for x in r.clarification_questions):
        raise ContractViolation("clarification_questions must be List[str]")

    if not isinstance(r.reasoning_trace, list) or not all(isinstance(x, str) for x in r.reasoning_trace):
        raise ContractViolation("reasoning_trace must be List[str]")

    if not isinstance(r.raw_text, str):
        raise ContractViolation("raw_text must be str")

    if not _is_finite_number(r.ts):
        raise ContractViolation("ts must be finite number")

    # Policy consistency checks
    if r.intent in NO_CONFIRM_INTENTS and r.require_confirmation:
        raise ContractViolation(f"{r.intent.value} must not require confirmation")

    if r.intent in CONFIRMABLE_INTENTS:
        if not r.require_confirmation:
            if r.confidence < DEFAULT_HIGH_CONFIDENCE_THRESHOLD:
                raise ContractViolation(
                    f"{r.intent.value} cannot skip confirmation unless confidence >= "
                    f"{DEFAULT_HIGH_CONFIDENCE_THRESHOLD}. Got {r.confidence}"
                )

    if r.require_confirmation and (r.confirmation_prompt is None or r.confirmation_prompt.strip() == ""):
        raise ContractViolation("require_confirmation=True requires a non-empty confirmation_prompt")

    if r.intent == Intent.UNKNOWN and r.raw_text.strip() != "" and len(r.clarification_questions) == 0:
        raise ContractViolation("UNKNOWN intent must provide clarification_questions for non-empty input")


def kernel_result_to_json_dict(r: KernelResult) -> Dict[str, Any]:
    validate_kernel_result(r)
    d = asdict(r)
    d["intent"] = r.intent.value
    return d


def kernel_result_to_json_str(r: KernelResult) -> str:
    return json.dumps(kernel_result_to_json_dict(r), indent=2, sort_keys=True)


def kernel_result_from_json_dict(d: Dict[str, Any]) -> KernelResult:
    if "intent" not in d:
        raise ContractViolation("Missing field: intent")
    try:
        intent = Intent(d["intent"])
    except Exception:
        raise ContractViolation(f"Invalid intent: {d.get('intent')!r}")

    r = KernelResult(
        intent=intent,
        confidence=float(d.get("confidence", -1)),
        require_confirmation=bool(d.get("require_confirmation", False)),
        confirmation_prompt=d.get("confirmation_prompt", None),
        clarification_questions=list(d.get("clarification_questions", [])),
        reasoning_trace=list(d.get("reasoning_trace", [])),
        raw_text=str(d.get("raw_text", "")),
        ts=float(d.get("ts", 0.0)),
    )
    validate_kernel_result(r)
    return r


def compute_confirmation_requirement(intent: Intent, confidence: float, high_conf_threshold: float) -> Tuple[bool, Optional[str]]:
    if intent in NO_CONFIRM_INTENTS:
        return (False, None)

    if intent in CONFIRMABLE_INTENTS:
        if confidence >= high_conf_threshold:
            return (False, None)
        if intent == Intent.LED_ON:
            return (True, "I heard: turn the LED ON. Confirm? (yes/no)")
        if intent == Intent.LED_OFF:
            return (True, "I heard: turn the LED OFF. Confirm? (yes/no)")
        if intent == Intent.SLEEP:
            return (True, "I heard: go to sleep mode. Confirm? (yes/no)")
        return (True, "Confirm action? (yes/no)")

    return (False, None)


def deterministic_classify_text(raw_text: str) -> Tuple[Intent, float, List[str]]:
    """
    Minimal deterministic classifier.
    IMPORTANT: voice mishears are handled ONLY as weak matches that force confirmation.
    """
    t = (raw_text or "").strip().lower()
    trace: List[str] = [f"normalized='{t}'"]

    if t == "":
        trace.append("empty_input => UNKNOWN")
        return (Intent.UNKNOWN, 0.0, trace)

    # Exact matches first (highest confidence)
    if t in {"ping"}:
        trace.append("match: exact 'ping'")
        return (Intent.PING, 1.0, trace)

    if t in {"led on", "light on", "turn on led"}:
        trace.append("match: exact LED_ON set")
        return (Intent.LED_ON, 0.95, trace)

    if t in {"led off", "light off", "turn off led"}:
        trace.append("match: exact LED_OFF set")
        return (Intent.LED_OFF, 0.95, trace)

    if t in {"time", "what time is it", "current time"}:
        trace.append("match: TIME_QUERY set")
        return (Intent.TIME_QUERY, 0.95, trace)

    if t in {"sleep", "go to sleep", "sleep mode"}:
        trace.append("match: SLEEP set")
        return (Intent.SLEEP, 0.90, trace)

    # --- Voice/STT mishears (LOW confidence by design -> confirmation required) ---
    # Common: "led" -> "lead"
    if t in {"lead on", "please lead on", "please a lead on"}:
        trace.append("weak_mishear: 'lead on' => LED_ON")
        return (Intent.LED_ON, 0.55, trace)

    if t in {"lead off", "please lead off", "please a lead off"}:
        trace.append("weak_mishear: 'lead off' => LED_OFF")
        return (Intent.LED_OFF, 0.55, trace)

    # Weak contains matches (lower confidence; force confirmation where relevant)
    if "led" in t and "on" in t:
        trace.append("weak_match: contains 'led' and 'on'")
        return (Intent.LED_ON, 0.60, trace)

    if "led" in t and "off" in t:
        trace.append("weak_match: contains 'led' and 'off'")
        return (Intent.LED_OFF, 0.60, trace)

    # Mishear contains matches (still low)
    if "lead" in t and "on" in t:
        trace.append("weak_mishear_contains: contains 'lead' and 'on'")
        return (Intent.LED_ON, 0.50, trace)

    if "lead" in t and "off" in t:
        trace.append("weak_mishear_contains: contains 'lead' and 'off'")
        return (Intent.LED_OFF, 0.50, trace)

    if "time" in t:
        trace.append("weak_match: contains 'time'")
        return (Intent.TIME_QUERY, 0.60, trace)

    if "sleep" in t:
        trace.append("weak_match: contains 'sleep'")
        return (Intent.SLEEP, 0.55, trace)

    trace.append("no_match => UNKNOWN")
    return (Intent.UNKNOWN, 0.20, trace)


def run_kernel(raw_text: str, high_conf_threshold: float = DEFAULT_HIGH_CONFIDENCE_THRESHOLD) -> KernelResult:
    intent, confidence, trace = deterministic_classify_text(raw_text)

    require_conf, prompt = compute_confirmation_requirement(intent, confidence, high_conf_threshold)

    clarification_questions: List[str] = []
    if intent == Intent.UNKNOWN:
        clarification_questions = [
            "I’m not sure what you want. Say one of: ping, led on, led off, time, sleep.",
        ]

    r = KernelResult(
        intent=intent,
        confidence=confidence,
        require_confirmation=require_conf,
        confirmation_prompt=prompt,
        clarification_questions=clarification_questions,
        reasoning_trace=trace,
        raw_text=raw_text,
        ts=time.time(),
    )
    validate_kernel_result(r)
    return r

