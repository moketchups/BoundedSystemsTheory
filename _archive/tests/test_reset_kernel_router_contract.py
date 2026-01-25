"""Tests for kernel_router contract stability."""
from __future__ import annotations
import kernel_router as kr
from kernel_contract import RouterState, Intent

def test_exports_exist():
    assert hasattr(kr, "HIGH_RISK")
    assert hasattr(kr, "route_text")

def test_unknown_does_not_execute():
    st0 = RouterState()
    out, new_st = kr.route_text("unknown command", st0)
    assert out.did_execute is False
    assert out.intent == Intent.UNKNOWN

def test_sleep_single_confirmation():
    st0 = RouterState()
    out1, st1 = kr.route_text("sleep", st0)
    assert st1.pending_intent == Intent.SLEEP
    assert st1.confirm_stage == 1
    out2, st2 = kr.route_text("yes", st1)
    assert out2.did_execute is True
    assert out2.sleep_mode is True

def test_led_two_step_confirmation():
    st0 = RouterState()
    out1, st1 = kr.route_text("led on", st0)
    assert st1.confirm_stage == 1
    out2, st2 = kr.route_text("yes", st1)
    assert st2.confirm_stage == 2
    out3, st3 = kr.route_text("i'm sure", st2)
    assert out3.did_execute is True
    assert out3.hw_cmd == "LED ON"

def test_cancel_clears_pending_state():
    st0 = RouterState()
    out1, st1 = kr.route_text("led on", st0)
    assert st1.pending_intent == Intent.LED_ON
    out2, st2 = kr.route_text("no", st1)
    assert st2.pending_intent is None
