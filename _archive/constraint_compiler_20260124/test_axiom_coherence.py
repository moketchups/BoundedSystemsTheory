"""Test axiom registry coherence. All axioms must be mutually consistent."""

import pytest
from mathematical.axiom_registry import (
    AxiomRegistry, Axiom, AxiomStatus, FOUNDATIONAL_AXIOMS, create_registry
)
from datetime import datetime


class TestFoundationalAxioms:
    """3 BIT axioms exist and are coherent."""

    def test_three_foundational_axioms_exist(self):
        assert len(FOUNDATIONAL_AXIOMS) == 3

    def test_axiom_ids(self):
        ids = {a.id for a in FOUNDATIONAL_AXIOMS}
        assert ids == {"bit-information-atoms", "bit-completeness", "bit-symmetry"}

    def test_information_atoms_is_proven(self):
        axiom = next(a for a in FOUNDATIONAL_AXIOMS if a.id == "bit-information-atoms")
        assert axiom.status == AxiomStatus.PROVEN
        assert axiom.confidence == 1.0

    def test_completeness_is_assumed(self):
        axiom = next(a for a in FOUNDATIONAL_AXIOMS if a.id == "bit-completeness")
        assert axiom.status == AxiomStatus.ASSUMED
        assert axiom.verified_by == "alan"

    def test_symmetry_is_proven(self):
        axiom = next(a for a in FOUNDATIONAL_AXIOMS if a.id == "bit-symmetry")
        assert axiom.status == AxiomStatus.PROVEN
        assert axiom.confidence == 1.0

    def test_no_circular_dependencies(self):
        """Foundational axioms have no dependencies"""
        for axiom in FOUNDATIONAL_AXIOMS:
            assert axiom.derived_from == []


class TestRegistryCoherence:
    """Registry must validate internal consistency."""

    def test_registry_creation(self):
        registry = create_registry()
        assert len(registry.axioms) == 3

    def test_coherence_check_passes(self):
        registry = create_registry()
        assert registry.validate_coherence() is True

    def test_missing_dependency_fails_coherence(self):
        registry = create_registry()
        bad_axiom = Axiom(
            id="derived-bad",
            name="Bad Derived",
            formal_statement="test",
            status=AxiomStatus.DERIVED,
            confidence=0.5,
            proof_reference=None,
            derived_from=["nonexistent-axiom"],
            constraints_generated=[],
            created=datetime(2026, 1, 24),
            verified_by="test"
        )
        registry.add_axiom(bad_axiom)
        assert registry.validate_coherence() is False

    def test_deprecated_dependency_fails_coherence(self):
        registry = create_registry()
        # Deprecate an axiom
        deprecated = Axiom(
            id="bit-symmetry",
            name="Symmetry (deprecated)",
            formal_statement="old",
            status=AxiomStatus.DEPRECATED,
            confidence=0.0,
            proof_reference=None,
            derived_from=[],
            constraints_generated=[],
            created=datetime(2026, 1, 24),
            verified_by="test"
        )
        registry.add_axiom(deprecated)
        # Add axiom depending on deprecated
        derived = Axiom(
            id="depends-on-deprecated",
            name="Bad",
            formal_statement="test",
            status=AxiomStatus.DERIVED,
            confidence=0.5,
            proof_reference=None,
            derived_from=["bit-symmetry"],
            constraints_generated=[],
            created=datetime(2026, 1, 24),
            verified_by="test"
        )
        registry.add_axiom(derived)
        assert registry.validate_coherence() is False

    def test_derivation_chain(self):
        registry = create_registry()
        chain = registry.get_derivation_chain("bit-symmetry")
        assert len(chain) == 1
        assert chain[0].id == "bit-symmetry"
