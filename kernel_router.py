# kernel_router.py
# Deterministic wiring: kernel -> (optional confirmation) -> hardware executor
# Voice is a shell; this router is authoritative.

from __future__ import annotations

import subprocess
import os
import sys
from dataclasses import dataclass
from typing import Optional

from kernel_contract import (
    Intent,
    run_kernel,
    kernel_result_to_json_str,
    validate_kernel_result,
)

# Map kernel intents to hardware commands (strings passed to hardware_executor.py)
INTENT_TO_HW_CMD = {
    Intent.PING: "PING",
    Intent.LED_ON: "LED ON",
    Intent.LED_OFF: "LED OFF",
    # TIME_QUERY and SLEEP are handled locally or by higher-level orchestration.
}

YES_SET = {"yes", "y"}
NO_SET = {"no", "n"}


@dataclass
class RouterState:
    """
    Router state is explicit and minimal.
    If awaiting_confirmation is True, the only accepted next inputs are yes/no.
    """
    awaiting_confirmation: bool = False
    pending_intent: Optional[Intent] = None
    pending_hw_cmd: Optional[str] = None
    pending_prompt: Optional[str] = None


def _say(s: str) -> None:
    """Single output surface: prints + speaks on macOS."""
    # Always log
    try:
        print(s, flush=True)
    except Exception:
        pass

    # Speak (macOS)
    try:
        import subprocess
        # Use default voice; fast and reliable
        subprocess.run(["say", s], check=False)
    except Exception as e:
        # Never crash the system because TTS failed
        try:
            print(f"[TTS_ERROR] {e}", flush=True)
        except Exception:
            pass


def _run_hardware_command(hw_cmd: str) -> str:
    """
    Executes hardware command through the existing stable hardware_executor.py.
    This keeps the hardware layer sealed as a black box.
    """
    # You can change python3 -> python if needed, but keep it explicit.
    cmd = ["python3", "hardware_executor.py", hw_cmd]
    completed = subprocess.run(cmd, capture_output=True, text=True)

    # Always surface stderr explicitly (no silent failures)
    if completed.returncode != 0:
        raise RuntimeError(
            f"Hardware executor failed (exit={completed.returncode}).\n"
            f"STDOUT:\n{completed.stdout}\n"
            f"STDERR:\n{completed.stderr}\n"
        )

    # Return stdout (hardware_executor.py already parses ACK line)
    return completed.stdout.strip()


def _handle_safe_local_intents(intent: Intent) -> Optional[str]:
    """
    Deterministic local handling for non-hardware actions.
    Returns a user-visible response string, or None if not handled.
    """
    if intent == Intent.TIME_QUERY:
        # Local time query (no hardware)
        import datetime
        now = datetime.datetime.now()
        # Deterministic formatting
        return now.strftime("Local time is %H:%M:%S.")
    if intent == Intent.SLEEP:
        # We do NOT execute any "sleep mode" changes here yet.
        # It is confirmable by policy, but actual behavior is not defined in hardware layer.
        return "Sleep intent acknowledged. (No sleep action is implemented yet.)"
    return None


def route_text(raw_text: str, state: RouterState, high_conf_threshold: float = 0.85) -> RouterState:
    """
    Main deterministic router entrypoint.
    - If awaiting confirmation: interpret raw_text as yes/no ONLY.
    - Else: run kernel, validate contract, enforce confirmation policy, execute if allowed.
    """
    t = (raw_text or "").strip()

    # --- Confirmation step ---
    if state.awaiting_confirmation:
        ans = t.lower()
        if ans in YES_SET:
            if not state.pending_hw_cmd or not state.pending_intent:
                # Should never happen; explicit failure
                state = RouterState()
                _say("ERROR: confirmation state corrupted; cleared.")
                return state

            _say(f"CONFIRMED: executing {state.pending_intent.value}")
            try:
                out = _run_hardware_command(state.pending_hw_cmd)
                _say(f"HARDWARE: {out}")
            except Exception as e:
                _say(f"ERROR: {e}")
            return RouterState()  # clear state

        if ans in NO_SET:
            _say("CANCELLED.")
            return RouterState()  # clear state

        # Not yes/no: keep waiting, be explicit
        _say("Awaiting confirmation. Reply 'yes' or 'no'.")
        return state

    # --- Normal routing step ---
    result = run_kernel(t, high_conf_threshold=high_conf_threshold)
    validate_kernel_result(result)

    # Always show the authoritative kernel JSON (auditable boundary)
    if os.getenv('DEMERZEL_DEBUG_KERNEL_JSON') == '1':
        print("KERNEL_JSON:", flush=True)
        print(kernel_result_to_json_str(result), flush=True)

    # UNKNOWN: never execute
    if result.intent == Intent.UNKNOWN:
        for q in result.clarification_questions:
            _say(f"CLARIFY: {q}")
        return state

    # Handle local-only intents (no hardware)
    local_resp = _handle_safe_local_intents(result.intent)
    if local_resp is not None:
        # If kernel demanded confirmation, obey it even for local actions.
        if result.require_confirmation:
            _say(result.confirmation_prompt or "Confirm? (yes/no)")
            return RouterState(
                awaiting_confirmation=True,
                pending_intent=result.intent,
                pending_hw_cmd=None,
                pending_prompt=result.confirmation_prompt,
            )
        _say(local_resp)
        return state

    # Hardware-mapped intents only
    if result.intent not in INTENT_TO_HW_CMD:
        _say(f"REFUSE: Intent {result.intent.value} has no execution mapping.")
        return state

    hw_cmd = INTENT_TO_HW_CMD[result.intent]

    # Confirmation gate
    if result.require_confirmation:
        _say(result.confirmation_prompt or "Confirm? (yes/no)")
        return RouterState(
            awaiting_confirmation=True,
            pending_intent=result.intent,
            pending_hw_cmd=hw_cmd,
            pending_prompt=result.confirmation_prompt,
        )

    # Execute immediately (only possible for non-confirm intents or high confidence confirmables)
    _say(f"EXECUTING: {result.intent.value}")
    try:
        out = _run_hardware_command(hw_cmd)
        _say(f"HARDWARE: {out}")
    except Exception as e:
        _say(f"ERROR: {e}")

    return state


def repl() -> None:
    """
    Deterministic interactive test loop (text-based).
    This proves the gate independent of voice.
    """
    _say("Demerzel Router REPL (type 'quit' to exit)")
    state = RouterState()

    while True:
        try:
            raw = input("> ")
        except (EOFError, KeyboardInterrupt):
            _say("\nExiting.")
            return

        if raw.strip().lower() in {"quit", "exit"}:
            _say("Bye.")
            return

        state = route_text(raw, state)


if __name__ == "__main__":
    repl()

