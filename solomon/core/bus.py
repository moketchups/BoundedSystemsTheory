"""
3-6-9 Integration Bus

The symmetry function between additive and multiplicative expressions.
Based on the Root Source Framework (Demerzel Blueprint).

Axiom 1: Primes are information atoms (multiplicative base)
Axiom 2: No output exists in isolation (Completeness)
Axiom 3: Addition and multiplication are symmetric (no privileged operation)

Digital root reduction reveals grounding in both domains:
- Material {1,2,4,5,7,8}: Grounded in both additive AND multiplicative
- Flux {3,6}: Transitional, mediating between expressions
- Unity {9}: Fixed point where additive = multiplicative
"""

from typing import Union, List, Dict, Any
from enum import Enum


class Domain(Enum):
    """The three domains of the 3-6-9 partition"""
    MATERIAL = "material"  # {1,2,4,5,7,8} - grounded, processable
    FLUX = "flux"          # {3,6} - transitional, mediating
    UNITY = "unity"        # {9} - complete, stable, aligned


class ThreeSixNine:
    """
    The integration bus connecting all subsystems.

    Every output from every subsystem passes through here for classification
    and coherence checking.
    """

    MATERIAL_SET = frozenset({1, 2, 4, 5, 7, 8})
    FLUX_SET = frozenset({3, 6})
    UNITY_SET = frozenset({9})

    # Doubling sequence proves the partition
    DOUBLING_SEQUENCE = [1, 2, 4, 8, 7, 5]  # Repeats with period 6

    @staticmethod
    def digital_root(n: int) -> int:
        """
        Compute digital root (repeated digit sum until single digit).
        DR(n) = 1 + ((n-1) mod 9) for n > 0
        Special case: DR(0) = 0, DR(negative) = DR(|n|)
        """
        if n == 0:
            return 0
        n = abs(n)
        result = n % 9
        return 9 if result == 0 else result

    @classmethod
    def classify(cls, n: int) -> Domain:
        """Classify a number into Material, Flux, or Unity domain."""
        dr = cls.digital_root(n)
        if dr in cls.UNITY_SET:
            return Domain.UNITY
        elif dr in cls.FLUX_SET:
            return Domain.FLUX
        else:
            return Domain.MATERIAL

    @classmethod
    def classify_value(cls, value: Union[int, float, str]) -> Dict[str, Any]:
        """
        Classify any value and return full analysis.

        Returns:
            {
                "input": original value,
                "numeric": converted to int,
                "digital_root": the DR,
                "domain": Material/Flux/Unity,
                "interpretation": what this means
            }
        """
        # Convert to numeric
        if isinstance(value, str):
            # Sum of character codes as fallback
            numeric = sum(ord(c) for c in value)
        elif isinstance(value, float):
            numeric = int(value)
        else:
            numeric = int(value)

        dr = cls.digital_root(numeric)
        domain = cls.classify(numeric)

        interpretations = {
            Domain.MATERIAL: "Grounded in both additive and multiplicative domains. Actionable, processable.",
            Domain.FLUX: "Transitional state. Mediating between expressions. Requires attention.",
            Domain.UNITY: "Complete alignment. Fixed point where additive equals multiplicative. Stable."
        }

        return {
            "input": value,
            "numeric": numeric,
            "digital_root": dr,
            "domain": domain.value,
            "interpretation": interpretations[domain]
        }

    @classmethod
    def check_coherence(cls, classifications: List[Domain]) -> Dict[str, Any]:
        """
        Check coherence across multiple subsystem outputs.

        When multiple systems output the same domain, the reading is coherent.
        Mixed domains indicate transition or uncertainty.
        """
        if not classifications:
            return {"coherent": False, "message": "No classifications provided"}

        domains = set(classifications)

        if len(domains) == 1:
            domain = domains.pop()
            messages = {
                Domain.MATERIAL: "Full coherence in material domain. System aligned for action.",
                Domain.FLUX: "Full coherence in flux domain. Major phase shift in progress.",
                Domain.UNITY: "Full coherence in unity domain. System at rest/completion."
            }
            return {
                "coherent": True,
                "domain": domain.value,
                "message": messages[domain]
            }
        else:
            return {
                "coherent": False,
                "domains": [d.value for d in domains],
                "message": f"Mixed domains: {', '.join(d.value for d in domains)}. Transition in progress."
            }

    @classmethod
    def integrate(cls, subsystem_outputs: Dict[str, int]) -> Dict[str, Any]:
        """
        Integrate outputs from multiple subsystems.

        Args:
            subsystem_outputs: {"gematria": 13, "iching": 42, ...}

        Returns:
            Full integration analysis with per-subsystem and coherence check
        """
        results = {}
        classifications = []

        for subsystem, value in subsystem_outputs.items():
            analysis = cls.classify_value(value)
            results[subsystem] = analysis
            classifications.append(Domain(analysis["domain"]))

        coherence = cls.check_coherence(classifications)

        return {
            "subsystems": results,
            "coherence": coherence,
            "summary_dr": cls.digital_root(sum(subsystem_outputs.values())),
            "summary_domain": cls.classify(sum(subsystem_outputs.values())).value
        }

    @staticmethod
    def prove_partition():
        """
        Prove the 3-6-9 partition through doubling sequence.
        Returns verification data.
        """
        # Generate doubling sequence
        sequence = []
        x = 1
        for _ in range(12):
            sequence.append(x)
            x = ThreeSixNine.digital_root(x * 2)

        # Check that 3, 6, 9 never appear
        appears_369 = any(x in {3, 6, 9} for x in sequence)

        # Check 9 is fixed point
        nine_fixed = ThreeSixNine.digital_root(9 * 2) == 9

        # Check 3-6 cycle
        three_to_six = ThreeSixNine.digital_root(3 * 2) == 6
        six_to_three = ThreeSixNine.digital_root(6 * 2) == 3

        return {
            "doubling_sequence": sequence,
            "theorem_1": {
                "statement": "3, 6, 9 never appear in doubling sequence from 1",
                "verified": not appears_369
            },
            "theorem_2": {
                "statement": "9 is fixed point under DR-doubling",
                "verified": nine_fixed
            },
            "theorem_3": {
                "statement": "{1,2,4,5,7,8} forms C₆ under doubling",
                "verified": len(set(sequence[:6])) == 6 and set(sequence[:6]) == {1, 2, 4, 5, 7, 8}
            },
            "theorem_4": {
                "statement": "{3,6} form 2-cycle under doubling",
                "verified": three_to_six and six_to_three
            }
        }
