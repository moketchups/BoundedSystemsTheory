from dataclasses import dataclass
from typing import List


@dataclass
class DerivationStep:
    level: int
    description: str
    formal: str
    source: str  # axiom_id or "type_system" or "runtime"


@dataclass
class ConstraintViolation:
    constraint_id: str
    input_value: object
    violation_type: str  # "type_error" | "proof_failure" | "consensus_failure"
    derivation_chain: List[DerivationStep]
    proof_id: str
    human_explanation: str

    def __str__(self) -> str:
        lines = [
            f"═══ CONSTRAINT VIOLATION ═══",
            f"Constraint: {self.constraint_id}",
            f"Input: {self.input_value}",
            f"Type: {self.violation_type}",
            f"",
            f"Derivation Chain:",
        ]
        for step in self.derivation_chain:
            indent = "  " * step.level
            lines.append(f"{indent}{step.level}. {step.description}")
            lines.append(f"{indent}   Formal: {step.formal}")
            lines.append(f"{indent}   Source: {step.source}")
        lines.extend([
            f"",
            f"Proof ID: {self.proof_id}",
            f"",
            f"Explanation: {self.human_explanation}",
            f"═══════════════════════════",
        ])
        return "\n".join(lines)
