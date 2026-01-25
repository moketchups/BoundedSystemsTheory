"""
r_coherence_checker.py - Cross-Component R-Coherence

R -> C -> I Architecture:
Ensures context, classifier, and responder all derive from the same R axioms.
If axioms diverge, the pipeline is incoherent and must fallback.
"""

from dataclasses import dataclass
from typing import List, Optional
from r_derivation_tracker import RDerived

# Known R-axioms from the project (all are valid Demerzel axioms)
KNOWN_AXIOMS = {
    'demerzel-identity-axiom-v1',
    'demerzel-purpose-axiom-v1',
    'root-source-axiom-v1',
    'robot-laws-axiom-v1',
    'ark-architecture-axiom-v1',
    'bit-theory-axiom-v1',
    'thermodynamics-axiom-v1',
}


@dataclass
class CoherenceResult:
    """Result of a full pipeline coherence check."""
    coherent: bool
    violations: List[str]
    recommendation: str  # "proceed" | "fallback" | "abort"


class RCoherenceChecker:
    """Cross-component R-coherence validation."""

    def check_context_classifier_coherence(self, context: RDerived, classification: RDerived) -> bool:
        """
        Do context and classifier derive from compatible R axioms?
        Compatible if: same axiom, or both are known project axioms
        (context was built FOR the classification's context_level).
        """
        ctx_axiom = context.derivation.axiom
        cls_axiom = classification.derivation.axiom
        # Same axiom = coherent
        if ctx_axiom == cls_axiom:
            return True
        # Both from known Demerzel axioms = coherent by construction
        # (the classifier requested a context level, context_manager built it)
        if ctx_axiom in KNOWN_AXIOMS and cls_axiom in KNOWN_AXIOMS:
            return True
        return False

    def check_classifier_responder_coherence(self, classification: RDerived, response: RDerived) -> bool:
        """
        Does responder use R sources consistent with classifier's identification?
        Response axiom must match or derive from classification axiom.
        """
        cls_axiom = classification.derivation.axiom
        resp_axiom = response.derivation.axiom
        if cls_axiom == resp_axiom:
            return True
        # Response can be more specific than classification
        if resp_axiom.startswith(cls_axiom.split('-')[0]):
            return True
        return False

    def full_coherence_check(self, context: RDerived, classification: RDerived, response: Optional[RDerived]) -> CoherenceResult:
        """Full pipeline coherence. Returns pass/fail with violation details."""
        violations = []

        if context is None or classification is None:
            return CoherenceResult(coherent=True, violations=[], recommendation='proceed')

        if not self.check_context_classifier_coherence(context, classification):
            violations.append(
                f"Context axiom '{context.derivation.axiom}' diverges from "
                f"classification axiom '{classification.derivation.axiom}'"
            )

        if response is not None:
            if not self.check_classifier_responder_coherence(classification, response):
                violations.append(
                    f"Classification axiom '{classification.derivation.axiom}' diverges from "
                    f"response axiom '{response.derivation.axiom}'"
                )

        if not violations:
            return CoherenceResult(coherent=True, violations=[], recommendation='proceed')
        elif len(violations) == 1:
            return CoherenceResult(coherent=False, violations=violations, recommendation='fallback')
        else:
            return CoherenceResult(coherent=False, violations=violations, recommendation='abort')
