"""Tests for router_engine integration."""
from __future__ import annotations
from router_engine import RouterEngine
from kernel_contract import HwResult

class FakeHW:
    def __init__(self):
        self.calls = []
    def send_to_arduino(self, cmd: str) -> HwResult:
        self.calls.append(cmd)
        return HwResult(ok=True, out=f"ACK {cmd}", err="")

def test_engine_routes_to_kernel():
    engine = RouterEngine(hardware=FakeHW())
    out = engine.route_text("unknown")
    assert out.did_execute is False

def test_engine_expands_time_placeholder():
    engine = RouterEngine(hardware=FakeHW())
    out = engine.route_text("what time")
    assert out.did_execute is True
    assert "__TIME__" not in out.speak
    assert ":" in out.speak

def test_engine_executes_hardware():
    fake = FakeHW()
    engine = RouterEngine(hardware=fake)
    out = engine.route_text("ping")
    assert out.did_execute is True
    assert fake.calls == ["PING"]

def test_engine_preserves_state():
    fake = FakeHW()
    engine = RouterEngine(hardware=fake)
    out1 = engine.route_text("led on")
    assert out1.did_execute is False
    out2 = engine.route_text("yes")
    assert out2.did_execute is False
    out3 = engine.route_text("i'm sure")
    assert out3.did_execute is True
    assert fake.calls == ["LED ON"]
