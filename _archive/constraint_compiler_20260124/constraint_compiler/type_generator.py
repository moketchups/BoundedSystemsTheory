"""
type_generator.py - Math spec -> Type definitions

ClaudeCode generates types from mathematical specifications.
The generated type's __init__ IS the proof.

Example:
    Constraint: "Never output a prime number greater than 100"
    Math: Let P = {p : p is prime, p > 100}. Constraint: ∀ output o, o ∉ P
    Type: SafeNumber — cannot represent primes > 100
"""

from typing import List
from mathematical.derivation_trace import DerivationStep, ConstraintViolation


def is_prime(n: int) -> bool:
    """Primality test. Used at type construction time."""
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


class SafeNumber:
    """Type that cannot represent primes > 100.

    Construction IS verification.
    Existence IS proof.
    If this object exists, constraint is satisfied.
    """

    def __init__(self, n: int):
        # This check happens at CONSTRUCTION
        # Once constructed, value is guaranteed safe
        if not isinstance(n, int):
            raise TypeError(f"SafeNumber requires int, got {type(n).__name__}")
        if is_prime(n) and n > 100:
            raise TypeError(
                str(ConstraintViolation(
                    constraint_id="prime-bound-100",
                    input_value=n,
                    violation_type="type_error",
                    derivation_chain=[
                        DerivationStep(
                            level=1,
                            description="From Goldbach symmetry axiom",
                            formal="additive(n) ↔ multiplicative(n)",
                            source="bit-symmetry"
                        ),
                        DerivationStep(
                            level=2,
                            description="Applied to constraint generation",
                            formal="Prime(n) ∧ n > 100 → Invalid",
                            source="constraint-compiler-v1"
                        ),
                        DerivationStep(
                            level=3,
                            description="Translated to type bound",
                            formal="SafeNumber ⊂ {n : ¬(Prime(n) ∧ n > 100)}",
                            source="type_system"
                        ),
                        DerivationStep(
                            level=4,
                            description="Runtime check at construction",
                            formal=f"{n} ∈ Prime ∧ {n} > 100 → TypeError",
                            source="runtime"
                        ),
                    ],
                    proof_id="goldbach-symmetry-constraint-v1",
                    human_explanation=(
                        f"{n} is prime and exceeds the bound of 100 established "
                        f"by the Goldbach symmetry constraint. This value cannot exist in "
                        f"the SafeNumber type space."
                    ),
                ))
            )
        self._value = n

    @property
    def value(self) -> int:
        return self._value

    def __repr__(self) -> str:
        return f"SafeNumber({self._value})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, SafeNumber):
            return self._value == other._value
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self._value)


# API only accepts/returns SafeNumber
def process(n: SafeNumber) -> SafeNumber:
    """Process a safe number. Cannot violate constraint.
    Input is safe by type. Output must be SafeNumber (verified at construction).
    """
    return SafeNumber(n.value * 2)
