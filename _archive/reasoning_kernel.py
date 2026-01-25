#!/usr/bin/env python3
"""
reasoning_kernel.py

Deterministic rule kernel for Demerzel voice loop.

Exports expected by brain_controller.py:
- kernel
- ReasoningRequest
- to_json_dict
- canonical_json
- sha256_hex
- clean_text

Key fix vs prior version:
- Every action includes "action_id" (controller requires it).
"""

from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import Any, Dict, List, Optional
import json
import hashlib
import re
from datetime import datetime


# ----------------------------
# Utilities (stable exports)
# ----------------------------

def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def canonical_json(obj: Any) -> str:
    """Stable canonical JSON encoding (sorted keys, no whitespace)."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def to_json_dict(obj: Any) -> Dict[str, Any]:
    """Convert dataclass / dict-like / primitive into JSON-serializable dict."""
    if obj is None:
        return {}
    if isinstance(obj, dict):
        return obj
    if hasattr(obj, "__dataclass_fields__"):
        return asdict(obj)
    return {"value": str(obj)}


def clean_text(s: str) -> str:
    """Deterministic text normalization for rule matching."""
    if s is None:
        return ""
    s = s.strip().lower()
    s = s.replace("’", "'").replace("“", '"').replace("”", '"')
    s = re.sub(r"[^a-z0-9\s'\-]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


# ----------------------------
# Request model (stable export)
# ----------------------------

@dataclass
class ReasoningRequest:
    """
    Flexible request container.
    Must accept schema_version even if older controllers pass it.
    """
    utterance_text: str = ""
    state_before: str = "IDLE"
    wake_detected: bool = False
    wake_score: float = 0.0
    wake_best_alias: str = ""
    slots: Dict[str, Any] = field(default_factory=dict)
    extras: Dict[str, Any] = field(default_factory=dict)
    ts_local: str = ""
    schema_version: int = 1

    def __init__(self, **kwargs: Any) -> None:
        known = {
            "utterance_text", "state_before", "wake_detected", "wake_score",
            "wake_best_alias", "slots", "extras", "ts_local", "schema_version"
        }
        extras = dict(kwargs.get("extras") or {})
        for k, v in kwargs.items():
            if k not in known:
                extras[k] = v

        self.utterance_text = kwargs.get("utterance_text", "") or ""
        self.state_before = (kwargs.get("state_before", "IDLE") or "IDLE").upper()
        self.wake_detected = bool(kwargs.get("wake_detected", False))
        self.wake_score = float(kwargs.get("wake_score", 0.0) or 0.0)
        self.wake_best_alias = kwargs.get("wake_best_alias", "") or ""
        self.slots = dict(kwargs.get("slots") or {})
        self.extras = extras
        self.ts_local = kwargs.get("ts_local", "") or ""
        self.schema_version = int(kwargs.get("schema_version", 1) or 1)


# ----------------------------
# Kernel constants & rules
# ----------------------------

STATES = {"IDLE", "COMMAND", "CONFIRM", "FOLLOWUP"}

SOFT_WAKE_SCORE = 0.40
HARD_WAKE_SCORE = 0.55

DEFAULT_ACK_TEXT = "Awake."
UNKNOWN_TEXT = "I didn't catch that."

WAKE_VERBS = {
    "wake up", "wake", "wakeup",
    "hey", "hi", "yo", "okay", "ok",
    "listen", "hello",
}

END_PHRASES = {
    "go to sleep", "sleep", "that's all", "that is all", "never mind",
    "nevermind", "stop", "cancel", "done", "end"
}

TIME_PATTERNS = [
    r"\bwhat time is it\b",
    r"\btell me the time\b",
    r"\btime\?\b",
]

REMEMBER_PATTERNS = [
    r"^remember (.+)$",
    r"^remind me to (.+)$",
]

CLEAR_TASKS_PATTERNS = [
    r"^clear tasks$",
    r"^clear my tasks$",
    r"^clear all tasks$",
    r"^clear open tasks$",
]

CONFIRM_WORDS = {"confirm", "yes", "yep", "yeah", "do it", "correct"}
CANCEL_WORDS = {"cancel", "no", "nope", "stop", "nevermind", "never mind"}


def _matches_any(patterns: List[str], text: str) -> bool:
    return any(re.search(p, text) for p in patterns)


def _extract_remember_payload(text: str) -> Optional[str]:
    for p in REMEMBER_PATTERNS:
        m = re.match(p, text)
        if m:
            payload = (m.group(1) or "").strip()
            return payload if payload else None
    return None


def _is_alias_only_or_alias_wake(text: str, alias: str) -> bool:
    if not alias:
        return False
    t = text.strip()
    a = alias.strip().lower()

    if t == a:
        return True

    if a in t:
        for verb in sorted(WAKE_VERBS, key=len, reverse=True):
            if verb in t:
                if t.startswith(a) or t.startswith(verb):
                    return True
    return False


def _strip_alias_prefix(text: str, alias: str) -> str:
    if not alias:
        return text
    a = alias.lower().strip()
    t = text.strip()
    if t.startswith(a + " "):
        return t[len(a):].strip()
    if t == a:
        return ""
    return text


def _now_time_string() -> str:
    return datetime.now().strftime("%-I:%M %p")


# ----------------------------
# Deterministic classify
# ----------------------------

def _classify(state_before: str, normalized: str, alias: str, wake_score: float, wake_detected: bool) -> Dict[str, Any]:
    rule_trace: List[str] = []
    ambiguity: Dict[str, Any] = {}

    st = (state_before or "IDLE").upper()
    if st not in STATES:
        st = "IDLE"

    if st == "CONFIRM":
        if normalized in CONFIRM_WORDS:
            rule_trace.append("CONFIRM + confirm_word -> confirm")
            return {"intent": "confirm", "confidence": 1.0, "payload": {}, "notes": {"rule_trace": rule_trace, "ambiguity": ambiguity}}
        if normalized in CANCEL_WORDS:
            rule_trace.append("CONFIRM + cancel_word -> cancel")
            return {"intent": "cancel", "confidence": 1.0, "payload": {}, "notes": {"rule_trace": rule_trace, "ambiguity": ambiguity}}
        rule_trace.append("CONFIRM + unknown -> ambiguous_confirm")
        ambiguity = {"type": "confirm_expected", "expected": ["confirm", "cancel"], "got": normalized}
        return {"intent": "ambiguous", "confidence": 0.0, "payload": {"prompt": "Say confirm or cancel."}, "notes": {"rule_trace": rule_trace, "ambiguity": ambiguity}}

    if normalized in END_PHRASES:
        rule_trace.append("end_phrase -> end")
        return {"intent": "end", "confidence": 1.0, "payload": {}, "notes": {"rule_trace": rule_trace, "ambiguity": ambiguity}}

    if _is_alias_only_or_alias_wake(normalized, alias):
        rule_trace.append("alias+wakeverb or alias_only -> hard_wake")
        return {"intent": "hard_wake", "confidence": 1.0, "payload": {}, "notes": {"rule_trace": rule_trace, "ambiguity": ambiguity}}

    stripped = _strip_alias_prefix(normalized, alias)
    cmd = stripped if stripped != normalized else normalized
    if stripped != normalized:
        rule_trace.append("strip_alias_prefix")

    if _matches_any(TIME_PATTERNS, cmd):
        rule_trace.append("time_pattern -> time")
        return {"intent": "time", "confidence": 1.0, "payload": {}, "notes": {"rule_trace": rule_trace, "ambiguity": ambiguity}}

    remember_payload = _extract_remember_payload(cmd)
    if remember_payload:
        rule_trace.append("remember_pattern -> remember")
        return {"intent": "remember", "confidence": 1.0, "payload": {"task_text": remember_payload}, "notes": {"rule_trace": rule_trace, "ambiguity": ambiguity}}

    if _matches_any(CLEAR_TASKS_PATTERNS, cmd):
        rule_trace.append("clear_tasks_pattern -> clear_tasks")
        return {"intent": "clear_tasks", "confidence": 1.0, "payload": {}, "notes": {"rule_trace": rule_trace, "ambiguity": ambiguity}}

    if (wake_detected or wake_score >= SOFT_WAKE_SCORE) and st == "IDLE":
        rule_trace.append("IDLE + wake_score>=soft -> soft_wake_ack")
        return {"intent": "soft_wake_ack", "confidence": 1.0, "payload": {}, "notes": {"rule_trace": rule_trace, "ambiguity": ambiguity}}

    rule_trace.append("no_rule_match -> unknown")
    ambiguity = {"type": "no_rule_match", "got": cmd}
    return {"intent": "unknown", "confidence": 0.0, "payload": {}, "notes": {"rule_trace": rule_trace, "ambiguity": ambiguity}}


# ----------------------------
# Actions (controller expects action_id!)
# ----------------------------

def _make_action(action_id: str, tool: str, args: Dict[str, Any], destructive: bool = False, requires_confirm: bool = False) -> Dict[str, Any]:
    return {
        "action_id": action_id,
        "tool": tool,
        "args": args,
        "destructive": bool(destructive),
        "requires_confirm": bool(requires_confirm),
    }


# ----------------------------
# Kernel (stable export)
# ----------------------------

def kernel(req: Any) -> Dict[str, Any]:
    if isinstance(req, ReasoningRequest):
        r = req
    elif isinstance(req, dict):
        r = ReasoningRequest(**req)
    else:
        r = ReasoningRequest(utterance_text=str(req))

    state_before = (r.state_before or "IDLE").upper()
    if state_before not in STATES:
        state_before = "IDLE"

    alias = (r.wake_best_alias or "").strip().lower()
    utter = r.utterance_text or ""
    normalized = clean_text(utter)

    request_payload = {
        "schema_version": r.schema_version,
        "state_before": state_before,
        "wake_detected": bool(r.wake_detected),
        "wake_score": float(r.wake_score),
        "wake_best_alias": alias,
        "utterance": utter,
        "normalized": normalized,
        "slots": r.slots,
        "extras": r.extras,
        "ts_local": r.ts_local or datetime.now().isoformat(timespec="seconds"),
    }

    request_id = sha256_hex(canonical_json(request_payload))[:16]

    # Deterministic per-call action id generator
    action_counter = {"i": 0}
    def A(tool: str, args: Dict[str, Any], destructive: bool = False, requires_confirm: bool = False) -> Dict[str, Any]:
        action_counter["i"] += 1
        aid = f"{request_id}:{action_counter['i']}"
        return _make_action(aid, tool, args, destructive=destructive, requires_confirm=requires_confirm)

    cls = _classify(
        state_before=state_before,
        normalized=normalized,
        alias=alias,
        wake_score=r.wake_score,
        wake_detected=r.wake_detected,
    )

    intent = cls["intent"]
    conf = float(cls.get("confidence", 0.0))
    payload = cls.get("payload", {}) or {}
    notes = cls.get("notes", {}) or {}
    rule_trace = notes.get("rule_trace", [])
    ambiguity = notes.get("ambiguity", {})

    actions: List[Dict[str, Any]] = []
    next_state = "IDLE"

    if intent == "hard_wake":
        if r.wake_detected or r.wake_score >= HARD_WAKE_SCORE:
            rule_trace.append("hard_wake -> enter FOLLOWUP")
            actions.append(A("system.beep", {}))
            actions.append(A("system.say", {"text": DEFAULT_ACK_TEXT}))
            next_state = "FOLLOWUP"
        else:
            rule_trace.append("hard_wake_but_low_score -> soft_wake_ack")
            actions.append(A("system.beep", {}))
            actions.append(A("system.say", {"text": DEFAULT_ACK_TEXT}))
            next_state = "IDLE"

    elif intent == "time":
        rule_trace.append("time -> execute_now")
        actions.append(A("system.beep", {}))
        actions.append(A("system.say", {"text": DEFAULT_ACK_TEXT}))
        actions.append(A("system.say", {"text": f"It is {_now_time_string()}."}))
        next_state = "IDLE"

    elif intent == "remember":
        task_text = (payload.get("task_text") or "").strip()
        if not task_text:
            rule_trace.append("remember_missing_payload -> unknown")
            actions.append(A("system.say", {"text": UNKNOWN_TEXT}))
            next_state = "IDLE"
        else:
            rule_trace.append("remember -> require_confirm")
            actions.append(A("system.say", {"text": f"You want me to remember: {task_text}. Say confirm or cancel."}))
            next_state = "CONFIRM"
            payload = {"proposed_action": {"tool": "tasks.add", "args": {"text": task_text}}}

    elif intent == "clear_tasks":
        rule_trace.append("clear_tasks -> require_confirm")
        actions.append(A("system.say", {"text": "Clear all open tasks? Say confirm or cancel."}))
        next_state = "CONFIRM"
        payload = {"proposed_action": {"tool": "tasks.clear_open", "args": {}}}

    elif intent == "confirm":
        rule_trace.append("confirm -> commit_proposed_action")
        actions.append(A("system.say", {"text": "Okay."}))
        next_state = "FOLLOWUP"

    elif intent == "cancel":
        rule_trace.append("cancel -> discard_proposed_action")
        actions.append(A("system.say", {"text": "Okay."}))
        next_state = "FOLLOWUP"

    elif intent == "end":
        rule_trace.append("end -> IDLE")
        actions.append(A("system.say", {"text": "Okay."}))
        next_state = "IDLE"

    elif intent == "soft_wake_ack":
        rule_trace.append("soft_wake_ack -> IDLE")
        actions.append(A("system.beep", {}))
        actions.append(A("system.say", {"text": DEFAULT_ACK_TEXT}))
        next_state = "IDLE"

    elif intent == "ambiguous":
        prompt = payload.get("prompt") or "Please repeat."
        rule_trace.append("ambiguous -> prompt_user")
        actions.append(A("system.say", {"text": prompt}))
        next_state = state_before

    else:
        rule_trace.append("unknown -> say_not_caught")
        actions.append(A("system.say", {"text": UNKNOWN_TEXT}))
        next_state = "IDLE"

    out: Dict[str, Any] = {
        "ts": datetime.now().isoformat(timespec="seconds"),
        "request_id": request_id,
        "state_before": state_before,
        "wake_detected": bool(r.wake_detected),
        "utterance": utter,
        "decision": {"intent": intent, "confidence": conf},
        "next_state": next_state,
        "actions": actions,
        "notes": {"rule_trace": rule_trace, "ambiguity": ambiguity},
        "request_payload": request_payload,
        "deterministic": True,
    }

    if payload:
        out["intent_payload"] = payload

    return out

