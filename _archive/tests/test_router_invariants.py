"""Core invariant tests for kernel_router."""
from __future__ import annotations
import kernel_router as kr
from kernel_contract import RouterState, Intent

def test_sleep_requires_confirmation():
    st0 = RouterState()
    out, new_state = kr.route_text("sleep", st0)
    assert out.did_execute is False
    assert new_state.pending_intent == Intent.SLEEP
    assert new_state.confirm_stage == 1
    assert "Confirm sleep" in out.speak

def test_sleep_yes_executes_and_enters_sleep_mode():
    st0 = RouterState()
    out1, st1 = kr.route_text("sleep", st0)
    out2, st2 = kr.route_text("yes", st1)
    assert out2.did_execute is True
    assert out2.sleep_mode is True
    assert st2.pending_intent is None

def test_sleep_no_cancels():
    st0 = RouterState()
    out1, st1 = kr.route_text("sleep", st0)
    out2, st2 = kr.route_text("no", st1)
    assert out2.did_execute is False
    assert out2.sleep_mode is False
    assert st2.pending_intent is None

def test_high_risk_hardware_is_two_step():
    st0 = RouterState()
    out1, st1 = kr.route_text("led on", st0)
    assert out1.did_execute is False
    assert st1.confirm_stage == 1
    out2, st2 = kr.route_text("yes", st1)
    assert out2.did_execute is False
    assert st2.confirm_stage == 2
    out3, st3 = kr.route_text("i'm sure", st2)
    assert out3.did_execute is True

def test_ping_executes_immediately():
    st0 = RouterState()
    out, new_state = kr.route_text("ping", st0)
    assert out.did_execute is True
    assert out.intent == Intent.PING

def test_route_text_signature():
    st0 = RouterState()
    result = kr.route_text("test", st0)
    assert isinstance(result, tuple)
    assert len(result) == 2
