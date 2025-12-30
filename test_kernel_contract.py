# test_kernel_contract.py
# Deterministic contract tests for Demerzel kernel.
# Run: python3 test_kernel_contract.py

from kernel_contract import run_kernel, Intent

HIGH = 0.85

def assert_true(x, msg):
    if not x:
        raise SystemExit(f"FAIL: {msg}")

def test_ping():
    r = run_kernel("ping", high_conf_threshold=HIGH)
    assert_true(r.intent == Intent.PING, "ping intent")
    assert_true(r.require_confirmation is False, "ping no confirmation")

def test_led_on_requires_confirmation_when_low_conf():
    r = run_kernel("lead on", high_conf_threshold=HIGH)  # common Vosk mishear
    assert_true(r.intent == Intent.LED_ON, "lead on maps to LED_ON")
    assert_true(r.confidence < HIGH, "lead on must be low confidence")
    assert_true(r.require_confirmation is True, "LED_ON requires confirmation when low confidence")
    assert_true(r.confirmation_prompt is not None, "confirmation prompt required")

def test_unknown_requires_clarify():
    r = run_kernel("dam brazil", high_conf_threshold=HIGH)
    assert_true(r.intent == Intent.UNKNOWN, "unknown intent")
    assert_true(len(r.clarification_questions) >= 1, "unknown must ask clarification")

def main():
    test_ping()
    test_led_on_requires_confirmation_when_low_conf()
    test_unknown_requires_clarify()
    print("ALL TESTS PASSED")

if __name__ == "__main__":
    main()

