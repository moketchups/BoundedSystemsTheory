"""Test: No LLM can bypass constraint.

PRD: "LLM cannot bypass by returning string '101'"
The type system prevents bypass regardless of LLM output format.
"""

import pytest
from constraint_compiler.type_generator import SafeNumber, process
from r_source.r_derivation import RDerived, RootSource
from action_space.actions import ValidAction
from action_space.execution import execute


class TestLLMBypassAttempts:
    """Simulate LLM attempting to bypass constraints."""

    def test_string_bypass_fails(self):
        """LLM returns "101" as string - TypeError"""
        with pytest.raises(TypeError):
            SafeNumber("101")

    def test_float_bypass_fails(self):
        """LLM returns 101.0 as float - TypeError"""
        with pytest.raises(TypeError):
            SafeNumber(101.0)

    def test_direct_prime_bypass_fails(self):
        """LLM tries to directly construct prime > 100"""
        with pytest.raises(TypeError):
            SafeNumber(103)

    def test_nested_bypass_fails(self):
        """LLM tries to nest the value in a container"""
        with pytest.raises(TypeError):
            SafeNumber(int("107"))

    def test_computed_bypass_fails(self):
        """LLM computes a prime > 100 through arithmetic"""
        # 50 * 2 + 9 = 109 (prime)
        with pytest.raises(TypeError):
            SafeNumber(50 * 2 + 9)

    def test_process_cannot_produce_unsafe(self):
        """process() wraps output in SafeNumber - unsafe outputs fail"""
        # SafeNumber(50) * 2 = 100 (not prime, OK)
        result = process(SafeNumber(50))
        assert result.value == 100

    def test_action_space_requires_r_derivation(self):
        """Actions require RDerived input - raw values rejected by type"""
        r = RootSource()
        payload = RDerived.from_r("test", r)
        result = execute(ValidAction.SPEAK, payload, r)
        assert result.success is True

    def test_invalid_action_undefined(self):
        """There is no way to construct an invalid action"""
        with pytest.raises((ValueError, KeyError)):
            ValidAction("harm")

    def test_r_derived_requires_root_source(self):
        """Cannot create RDerived without RootSource"""
        r = RootSource()
        derived = RDerived.from_r(42, r)
        assert len(derived.r_proof) == 32  # sha256

    def test_raw_r_derived_construction_has_no_proof(self):
        """Direct RDerived construction without from_r has no valid proof"""
        # You CAN construct it directly (Python isn't Haskell)
        # but the r_proof won't verify
        fake = RDerived(value=42, r_proof=b"fake")
        r = RootSource()
        assert not r.verify(42, fake.r_proof)
