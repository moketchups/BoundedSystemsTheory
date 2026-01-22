import router_engine as re_mod


def test_router_engine_accepts_wake_aliases_kwarg():
    eng = re_mod.RouterEngine(wake_aliases=["demerzel", "dimmer-zel"])
    assert isinstance(eng.wake_aliases, list)
    assert "demerzel" in eng.wake_aliases


def test_route_text_returns_router_output():
    """Test that route_text returns RouterOutput (new API)."""
    eng = re_mod.RouterEngine(wake_aliases=["demerzel"])
    out = eng.route_text("ping")

    # New contract: returns RouterOutput dataclass
    assert hasattr(out, 'intent')
    assert hasattr(out, 'did_execute')
    assert hasattr(out, 'hw_cmd')
    assert hasattr(out, 'speak')
    assert hasattr(out, 'sleep_mode')

