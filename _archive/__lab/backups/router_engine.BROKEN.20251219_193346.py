#!/usr/bin/env python3
"""
router_engine.py
Robust against hardware_executor naming differences.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional

from kernel_router import Intent, run_kernel, validate_kernel_result

# ---- Hardware executor (robust import) ----
import hardware_executor as _hw

if hasattr(_hw, "run_hardware_command"):
    _run_hardware_command = _hw.run_hardware_command
elif hasattr(_hw, "execute_hardware_command"):
    _run_hardware_command = _hw.execute_hardware_command
elif hasattr(_hw, "hardware_executor"):
    _run_hardware_command = _hw.hardware_executor
else:
    raise ImportError(
        "hardware_executor.py does not expose a known command function"
    )

from memory_store import MemoryStore

YES_SET = {"yes", "yeah", "yep", "correct", "do it", "confirm", "ok", "okay"}
NO_SET = {"no", "nope", "cancel", "stop", "dont", "don't", "never"}

INTENT_TO_HW_CMD = {
    Intent.PING: "PING",
    Intent.LED_ON: "LED ON",
    Intent.LED_OFF: "LED OFF",
}

_say = None

def set_say_fn(fn):
    global _say
    _say = fn

def _say_safe(msg: str):
    if callable(_say):
        _say(msg)
    else:
        print(msg)

@dataclass
class RouterState:
    awaiting_confirmation: bool = False
    pending_intent: Optional[Intent] = None
    pending_hw_cmd: Optional[str] = None

def process_final_text(state: RouterState, final_text: str, *, high_conf_threshold=0.8):
    text = (final_text or "").strip()
    if not text:
        return state

    result = run_kernel(text, high_conf_threshold=high_conf_threshold)
    validate_kernel_result(result)

    _say_safe("KERNEL_JSON:")
    _say_safe(str(result.to_dict()))

    if result.intent == Intent.UNKNOWN:
        for q in result.clarification_questions or []:
            _say_safe(f"CLARIFY: {q}")
        return state

    if result.intent == Intent.MEMORY_STORE:
        m = result.memory or {}
        MemoryStore().remember_fact(m.get("key"), m.get("value"))
        _say_safe("Okay.")
        return state

    if result.intent == Intent.MEMORY_RECALL:
        key = (result.memory or {}).get("key")
        val = MemoryStore().recall_fact(key)
        _say_safe(val if val else "I don't have that yet.")
        return state

    if result.intent not in INTENT_TO_HW_CMD:
        _say_safe("REFUSE: No execution mapping.")
        return state

    cmd = INTENT_TO_HW_CMD[result.intent]
    _say_safe(f"EXECUTING: {cmd}")
    out = _run_hardware_command(cmd)
    _say_safe(f"HARDWARE: {out}")
    return state
