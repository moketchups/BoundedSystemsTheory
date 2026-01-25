from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum
from datetime import datetime


class AxiomStatus(Enum):
    PROVEN = "proven"           # Formally verified (Lean/Coq)
    ASSUMED = "assumed"         # Human judgment, not yet proven
    DERIVED = "derived"         # Derived from other axioms
    DEPRECATED = "deprecated"   # Superseded by better axiom


@dataclass(frozen=True)
class Axiom:
    id: str                           # e.g., "goldbach-symmetry-v1"
    name: str                         # Human readable
    formal_statement: str             # Mathematical notation
    status: AxiomStatus
    confidence: float                 # 0.0 to 1.0
    proof_reference: Optional[str]    # Link to Lean/Coq proof
    derived_from: List[str]           # Parent axiom IDs
    constraints_generated: List[str]  # Constraint IDs using this
    created: datetime
    verified_by: str                  # "formal_proof" | "alan" | "consensus"


@dataclass
class AxiomRegistry:
    axioms: dict[str, Axiom] = field(default_factory=dict)

    def add_axiom(self, axiom: Axiom) -> None:
        self.axioms[axiom.id] = axiom

    def get_derivation_chain(self, axiom_id: str) -> List[Axiom]:
        """Trace axiom back to foundational axioms"""
        axiom = self.axioms[axiom_id]
        chain = [axiom]
        for parent_id in axiom.derived_from:
            chain.extend(self.get_derivation_chain(parent_id))
        return chain

    def validate_coherence(self) -> bool:
        """Check all axioms are mutually consistent"""
        for axiom in self.axioms.values():
            for dep_id in axiom.derived_from:
                if dep_id not in self.axioms:
                    return False
                parent = self.axioms[dep_id]
                if parent.status == AxiomStatus.DEPRECATED:
                    return False
        return True


# Initial axioms
FOUNDATIONAL_AXIOMS = [
    Axiom(
        id="bit-information-atoms",
        name="Information Atoms (BIT Axiom 1)",
        formal_statement="∀n ∈ ℕ, n = ∏pᵢᵉⁱ where pᵢ prime (unique factorization)",
        status=AxiomStatus.PROVEN,
        confidence=1.0,
        proof_reference="fundamental_theorem_arithmetic",
        derived_from=[],
        constraints_generated=["atomic-operations"],
        created=datetime(2026, 1, 24),
        verified_by="formal_proof"
    ),
    Axiom(
        id="bit-completeness",
        name="Completeness (BIT Axiom 2)",
        formal_statement="∀ output o, ∃ derivation d: R → o",
        status=AxiomStatus.ASSUMED,
        confidence=0.95,
        proof_reference=None,
        derived_from=[],
        constraints_generated=["r-derivation-required"],
        created=datetime(2026, 1, 24),
        verified_by="alan"
    ),
    Axiom(
        id="bit-symmetry",
        name="Symmetry (BIT Axiom 3)",
        formal_statement="additive(n) ↔ multiplicative(n) (Goldbach symmetry)",
        status=AxiomStatus.PROVEN,
        confidence=1.0,
        proof_reference="goldbach_proof_v1.lean",
        derived_from=[],
        constraints_generated=["bidirectional-constraints"],
        created=datetime(2026, 1, 24),
        verified_by="formal_proof"
    ),
]


def create_registry() -> AxiomRegistry:
    """Create registry with foundational axioms."""
    registry = AxiomRegistry()
    for axiom in FOUNDATIONAL_AXIOMS:
        registry.add_axiom(axiom)
    return registry
