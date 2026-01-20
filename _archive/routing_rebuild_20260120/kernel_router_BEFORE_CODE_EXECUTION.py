"""
Kernel router: deterministic text -> decision/state.
NO hardware, NO audio, NO time.
"""
from __future__ import annotations

from dataclasses import replace
from typing import Tuple

from kernel_contract import RouterState, RouterOutput, Intent
import boundary_gate as bg

HIGH_RISK: set[Intent] = {"LED_ON", "LED_OFF"}  # sleep is confirmed but not stage-2 high risk

def _intent_from_text(t: str) -> Tuple[Intent, str]:
    """
    Returns (intent, hw_cmd).
    hw_cmd is used only for hardware intents.
    """
    if not t:
        return "UNKNOWN", ""
    if "ping" in t:
        return "PING", "PING"
    if "led" in t and ("on" in t or "off" in t):
        if "on" in t and "off" not in t:
            return "LED_ON", "LED ON"
        if "off" in t:
            return "LED_OFF", "LED OFF"
    if "time" in t or "what time" in t:
        return "TIME", ""
    if t in {"sleep", "go to sleep"} or ("sleep" in t and "mode" in t):
        return "SLEEP", ""
    if bg.is_no(t):
        return "CANCEL", ""
    return "UNKNOWN", ""

def route_text(text: str, st: RouterState) -> Tuple[RouterOutput, RouterState]:
    t = bg.normalize(text)

    # If we're in a confirmation flow
    if st.pending_intent is not None:
        if bg.is_no(t):
            new_st = replace(st, pending_intent=None, pending_cmd=None, confirm_stage=0, last_prompt="")
            return RouterOutput(speak="Cancelled.", intent="CANCEL"), new_st

        # Sleep confirmation (single-stage)
        if st.pending_intent == "SLEEP":
            if bg.is_yes(t):
                new_st = replace(st, pending_intent=None, pending_cmd=None, confirm_stage=0, last_prompt="")
                return RouterOutput(
                    speak="Sleeping.",
                    intent="SLEEP",
                    did_execute=True,
                    sleep_mode=True,
                ), new_st
            return RouterOutput(
                speak="Confirm sleep. Please say yes or no.",
                intent="SLEEP",
            ), st

        # High-risk hardware confirmation (two-stage)
        if st.pending_intent in HIGH_RISK:
            if st.confirm_stage == 1:
                if bg.is_yes(t):
                    new_st = replace(st, confirm_stage=2)
                    return RouterOutput(
                        speak="Are you sure? This is HIGH risk. Say \"I'm sure\" to proceed or \"no\" to cancel.",
                        intent=st.pending_intent,
                    ), new_st
                return RouterOutput(
                    speak=f"Confirm HIGH action requested: {st.pending_cmd}. Please say yes or no.",
                    intent=st.pending_intent,
                ), st

            if st.confirm_stage == 2:
                if bg.is_stage2(t):
                    new_st = replace(st, pending_intent=None, pending_cmd=None, confirm_stage=0, last_prompt="")
                    return RouterOutput(
                        speak="",
                        intent=st.pending_intent,
                        did_execute=True,
                        hw_cmd=st.pending_cmd,
                    ), new_st
                return RouterOutput(
                    speak="Say \"I'm sure\" to proceed or \"no\" to cancel.",
                    intent=st.pending_intent,
                ), st

    # Normal routing
    intent, cmd = _intent_from_text(t)

    if intent in {"LED_ON", "LED_OFF"}:
        new_st = replace(st, pending_intent=intent, pending_cmd=cmd, confirm_stage=1)
        return RouterOutput(
            speak=f"Confirm HIGH action requested: {cmd}. Please say yes or no.",
            intent=intent,
            did_execute=False,
        ), new_st

    if intent == "SLEEP":
        new_st = replace(st, pending_intent="SLEEP", pending_cmd=None, confirm_stage=1)
        return RouterOutput(
            speak="Confirm sleep. Please say yes or no.",
            intent="SLEEP",
        ), new_st

    if intent == "PING":
        return RouterOutput(speak="", intent="PING", did_execute=True, hw_cmd="PING"), st

    if intent == "TIME":
        return RouterOutput(speak="__TIME__", intent="TIME", did_execute=True), st

    if intent == "CANCEL":
        return RouterOutput(speak="Okay.", intent="CANCEL"), st

    return RouterOutput(speak="Sorry — I didn't catch that.", intent="UNKNOWN"), st

