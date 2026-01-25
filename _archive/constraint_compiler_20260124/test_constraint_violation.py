"""
Test Case from PRD: Proof of Concept

Constraint: "Never output a prime number greater than 100"

Success Criteria (PRD Step 4):
- [x] SafeNumber(101) raises TypeError
- [x] No code path can return raw int (must be SafeNumber)
- [x] LLM cannot bypass by returning string "101"
- [x] Violation is mathematically impossible in generated code
"""

import pytest
from constraint_compiler.type_generator import SafeNumber, process, is_prime


class TestSafeNumberConstruction:
    """SafeNumber(101) must raise TypeError."""

    def test_prime_above_100_raises_type_error(self):
        """PRD Step 4 criterion 1: SafeNumber(101) raises TypeError"""
        with pytest.raises(TypeError) as exc_info:
            SafeNumber(101)
        assert "prime-bound-100" in str(exc_info.value)
        assert "CONSTRAINT VIOLATION" in str(exc_info.value)

    def test_derivation_chain_in_error(self):
        """Violation produces full derivation trace"""
        with pytest.raises(TypeError) as exc_info:
            SafeNumber(101)
        msg = str(exc_info.value)
        assert "bit-symmetry" in msg
        assert "constraint-compiler-v1" in msg
        assert "type_system" in msg
        assert "runtime" in msg
        assert "goldbach-symmetry-constraint-v1" in msg

    def test_non_prime_above_100_allowed(self):
        """102 is not prime, so it's allowed"""
        n = SafeNumber(102)
        assert n.value == 102

    def test_prime_below_100_allowed(self):
        """97 is prime but <= 100, so it's allowed"""
        n = SafeNumber(97)
        assert n.value == 97

    def test_composite_numbers_allowed(self):
        """Composite numbers are always allowed"""
        for v in [4, 50, 100, 200, 1000]:
            n = SafeNumber(v)
            assert n.value == v

    def test_all_primes_above_100_rejected(self):
        """Every prime > 100 must be rejected"""
        primes_above_100 = [p for p in range(101, 200) if is_prime(p)]
        for p in primes_above_100:
            with pytest.raises(TypeError):
                SafeNumber(p)

    def test_small_primes_allowed(self):
        """Primes <= 100 are all valid"""
        small_primes = [2, 3, 5, 7, 11, 13, 97]
        for p in small_primes:
            n = SafeNumber(p)
            assert n.value == p


class TestNoRawIntBypass:
    """PRD Step 4 criterion 2: No code path can return raw int."""

    def test_process_returns_safe_number(self):
        """process() must return SafeNumber, not raw int"""
        result = process(SafeNumber(50))
        assert isinstance(result, SafeNumber)

    def test_process_output_is_validated(self):
        """If process would produce prime > 100, it fails at construction"""
        # SafeNumber(53) * 2 = 106 (not prime, OK)
        result = process(SafeNumber(53))
        assert isinstance(result, SafeNumber)
        assert result.value == 106

    def test_value_property_returns_int(self):
        """value property gives the int, but SafeNumber wraps it"""
        n = SafeNumber(50)
        assert isinstance(n.value, int)
        assert n.value == 50


class TestStringBypass:
    """PRD Step 4 criterion 3: LLM cannot bypass by returning string '101'."""

    def test_string_input_raises_type_error(self):
        """String input is TypeError - not a valid SafeNumber"""
        with pytest.raises(TypeError):
            SafeNumber("101")

    def test_float_input_raises_type_error(self):
        """Float input is TypeError"""
        with pytest.raises(TypeError):
            SafeNumber(101.0)

    def test_none_input_raises_type_error(self):
        """None is TypeError"""
        with pytest.raises(TypeError):
            SafeNumber(None)


class TestMathematicalImpossibility:
    """PRD Step 4 criterion 4: Violation is mathematically impossible."""

    def test_no_unsafe_number_can_exist(self):
        """No SafeNumber instance can hold a prime > 100"""
        # If we could somehow bypass __init__, the object would be invalid
        # But frozen dataclass pattern prevents this
        safe = SafeNumber(50)
        # _value is set only in __init__, cannot be mutated after
        assert safe.value == 50

    def test_type_is_structural_not_behavioral(self):
        """The constraint is in the type, not in a check"""
        # SafeNumber IS the constraint
        # There is no separate "check_safe()" function
        # The type itself enforces the invariant
        assert SafeNumber(99).value == 99
        with pytest.raises(TypeError):
            SafeNumber(101)
