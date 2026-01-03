#!/usr/bin/env python3
"""
router_engine.py

RouterEngine is the single canonical pipeline wrapper.

Goal:
- All entrypoints (voice + REPL) call RouterEngine.process().
- Router decision happens in kernel_router.route_text().
- Hardware execution happens ONLY at the engine boundary (in Step 6 we move it fully here).
- Every interaction is logged to the append-only action ledger.

Safety rule (important for Step 5):
- We only execute hardware IF kernel_router indicates a hw_cmd is ready AND it did not already
  execute it (no hw_ack present).
  This prevents double execution while we transition.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Any

from kernel_router import route_text, RouterState, RouterOutput
import action_ledger
import hardware_executor


def _get(d: Dict[str, Any], k: str) -> Any:
    try:
        return d.get(k)
    except Exception:
        return None


@dataclass
class RouterEngine:
    """
    Stateless wrapper: caller supplies RouterState, we return RouterOutput.
    The caller (brain_controller / REPL) owns state updates.
    """

    def process(self, raw_text: str, state: Optional[RouterState] = None) -> RouterOutput:
        st = state or RouterState()
        out = route_text(raw_text, st)

        # Decide whether we should execute hardware here.
        dbg = out.debug or {}
        hw_cmd = _get(dbg, "hw_cmd") or _get(dbg, "pending_hw_cmd")
        hw_ack = _get(dbg, "hw_ack")

        # Only execute if:
        #  - there is a hw_cmd
        #  - we are NOT in confirmation-awaiting state
        #  - and the router/kernel did not already execute it (no hw_ack)
        should_execute_hw = bool(hw_cmd) and (not out.new_state.awaiting_confirmation) and (not hw_ack)

        if should_execute_hw:
            try:
                ack = hardware_executor.send_to_arduino(str(hw_cmd))
                new_dbg = {**dbg, "hw_cmd": str(hw_cmd), "hw_ack": ack, "hw_executed_by": "router_engine"}
                out = RouterOutput(
                    speak=ack,  # override speak with real ACK line
                    new_state=out.new_state,
                    effects=out.effects,
                    debug=new_dbg,
                )
            except Exception as e:
                # Fail closed: no silent failure, speak the error
                msg = f"ERROR: hardware failed: {e}"
                new_dbg = {**dbg, "hw_cmd": str(hw_cmd), "error": repr(e), "hw_executed_by": "router_engine"}
                out = RouterOutput(
                    speak=msg,
                    new_state=out.new_state,
                    effects=out.effects,
                    debug=new_dbg,
                )

        # Ledger logging (must never crash)
        try:
            dbg2 = out.debug or {}
            ev = action_ledger.make_router_event(
                raw_text=str(_get(dbg2, "raw") or raw_text or ""),
                cleaned_text=str(_get(dbg2, "cleaned") or ""),
                mode=str(_get(dbg2, "mode") or ""),
                intent=str(_get(dbg2, "intent") or _get(dbg2, "pending_intent") or ""),
                confidence=_get(dbg2, "confidence"),
                confirm_required=_get(dbg2, "router_confirmation_required"),
                speak=str(out.speak or ""),
                effects=out.effects,
                error=str(_get(dbg2, "error") or "") or None,
                hw_cmd=str(_get(dbg2, "hw_cmd") or _get(dbg2, "pending_hw_cmd") or "") or None,
                hw_result=str(_get(dbg2, "hw_ack") or "") or None,
            )
            action_ledger.append_event(ev)
        except Exception:
            pass

        return out


# Back-compat alias (some older scripts may import Router)
Router = RouterEngine
