"""
Kernel router: deterministic text -> decision/state.
No hardware, NO audio, NO time.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Tuple

from kernel_contract import RouterState, RouterOutput, Intent
import boundary_gate as bg

HIGH_RISK: set[Intent] = {Intent.LED_ON, Intent.LED_OFF}

def _intent_from_text(t: str) -> Tuple[Intent, str]:
    """
    Returns (intent, hw_cmd).
    hw_cmd is used only for hardware intents.
    """
    if not t:
        return Intent.UNKNOWN, ""
    if "ping" in t:
        return Intent.PING, "PING"
    if "led" in t and ("on" in t or "off" in t):
        if "on" in t and "off" not in t:
            return Intent.LED_ON, "LED ON"
        if "off" in t:
            return Intent.LED_OFF, "LED OFF"
    if "discuss" in t:
        return Intent.DISCUSS, ""
    if "time" in t or "what time" in t:
        return Intent.TIME, ""
    if ("sleep" in t) or ("go to sleep" in t) or ("sleep" in t and "mode" in t):
        return Intent.SLEEP, ""
    if bg.is_no(t):
        return Intent.CANCEL, ""
    
    # Code execution intent
    if "execute code" in t or "run code" in t or "execute python" in t:
        return Intent.EXECUTE_CODE, ""
    
    return Intent.UNKNOWN, ""


def route_text(text: str, st: RouterState) -> Tuple[RouterOutput, RouterState]:
    t = bg.normalize(text)

    # If we're in a confirmation flow
    if st.pending_intent is not None:
        if bg.is_no(t):
            new_st = replace(st, pending_intent=None, pending_cmd=None, confirm_stage=0, last_prompt="")
            return RouterOutput(speak="Cancelled.", intent=Intent.CANCEL), new_st

        # Sleep confirmation (single-stage)
        if st.pending_intent == Intent.SLEEP:
            if bg.is_yes(t):
                new_st = replace(st, pending_intent=None, pending_cmd=None, confirm_stage=0, last_prompt="")
                return RouterOutput(
                    speak="Sleeping.",
                    intent=Intent.SLEEP,
                    did_execute=True,
                    sleep_mode=True,
                ), new_st
            return RouterOutput(
                speak="Confirm sleep. Please say yes or no.",
                intent=Intent.SLEEP,
            ), st

        # High-risk hardware confirmation (two-stage)
        if st.pending_intent in HIGH_RISK:
            if st.confirm_stage == 1:
                if bg.is_yes(t):
                    new_st = replace(st, confirm_stage=2)
                    return RouterOutput(
                        speak=f"Are you sure? This is HIGH risk. Say \"I'm sure\" to proceed or \"no\" to cancel.",
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
        
        # Code execution confirmation (two-stage for HIGH_RISK code)
        if st.pending_intent == Intent.EXECUTE_CODE:
            if st.confirm_stage == 1:
                if bg.is_yes(t):
                    new_st = replace(st, confirm_stage=2)
                    return RouterOutput(
                        speak=f"Are you sure? This code has HIGH risk patterns. Say \"I'm sure\" to proceed or \"no\" to cancel.",
                        intent=Intent.EXECUTE_CODE,
                    ), new_st
                return RouterOutput(
                    speak=f"Confirm code execution. This code will modify files or perform risky operations. Please say yes or no.",
                    intent=Intent.EXECUTE_CODE,
                ), st
            
            if st.confirm_stage == 2:
                if bg.is_stage2(t):
                    new_st = replace(st, pending_intent=None, pending_cmd=None, pending_code=None, confirm_stage=0, last_prompt="")
                    return RouterOutput(
                        speak="",
                        intent=Intent.EXECUTE_CODE,
                        did_execute=True,
                        code_to_execute=st.pending_code,
                    ), new_st
                return RouterOutput(
                    speak="Say \"I'm sure\" to proceed or \"no\" to cancel.",
                    intent=Intent.EXECUTE_CODE,
                ), st

    # Normal routing
    intent, cmd = _intent_from_text(t)

    if intent in {Intent.LED_ON, Intent.LED_OFF}:
        new_st = replace(st, pending_intent=intent, pending_cmd=cmd, confirm_stage=1)
        return RouterOutput(
            speak=f"Confirm HIGH action requested: {cmd}. Please say yes or no.",
            intent=intent,
            did_execute=False,
        ), new_st

    if intent == Intent.SLEEP:
        new_st = replace(st, pending_intent=Intent.SLEEP, confirm_stage=1)
        return RouterOutput(
            speak="Confirm sleep. Please say yes or no.",
            intent=Intent.SLEEP,
        ), new_st

    if intent == Intent.PING:
        return RouterOutput(speak="ACK PING", intent=Intent.PING, hw_cmd="PING", did_execute=True), st

    if intent == Intent.TIME:
        return RouterOutput(speak="__TIME__", intent=Intent.TIME, did_execute=True), st

    if intent == Intent.CANCEL:
        return RouterOutput(speak="Nothing to cancel.", intent=Intent.CANCEL), st

    return RouterOutput(speak="I don't understand that command.", intent=Intent.UNKNOWN), st
