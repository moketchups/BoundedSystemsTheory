"""Test hot-swap verification: add, verify, swap, rollback."""

import pytest
from constraint_compiler.hot_swap import HotSwapManager, SwapStatus
from constraint_compiler.type_generator import SafeNumber


class TestHotSwapLifecycle:
    """PRD: Add constraint, verify, swap, rollback."""

    def test_prepare_creates_pending_version(self):
        mgr = HotSwapManager()
        version = mgr.prepare_swap(
            constraint_id="prime-bound-100",
            compiled_type=SafeNumber,
            axiom_ids=["bit-symmetry"],
            proof_hash="abc123"
        )
        assert version.status == SwapStatus.PENDING
        assert version.version_id in mgr.pending_versions

    def test_verify_transitions_to_ready(self):
        mgr = HotSwapManager()
        version = mgr.prepare_swap(
            constraint_id="prime-bound-100",
            compiled_type=SafeNumber,
            axiom_ids=["bit-symmetry"],
            proof_hash="abc123"
        )
        result = mgr.verify_swap(version.version_id)
        assert result is True
        assert version.status == SwapStatus.READY

    def test_execute_swap_activates(self):
        mgr = HotSwapManager()
        version = mgr.prepare_swap(
            constraint_id="prime-bound-100",
            compiled_type=SafeNumber,
            axiom_ids=["bit-symmetry"],
            proof_hash="abc123"
        )
        mgr.verify_swap(version.version_id)
        result = mgr.execute_swap(version.version_id)
        assert result is True
        assert "prime-bound-100" in mgr.active_versions
        assert mgr.active_versions["prime-bound-100"].status == SwapStatus.ACTIVE

    def test_execute_without_verify_fails(self):
        mgr = HotSwapManager()
        version = mgr.prepare_swap(
            constraint_id="test",
            compiled_type=SafeNumber,
            axiom_ids=["bit-symmetry"],
            proof_hash="abc"
        )
        result = mgr.execute_swap(version.version_id)
        assert result is False

    def test_rollback_restores_previous(self):
        mgr = HotSwapManager()
        # First version
        v1 = mgr.prepare_swap("test", SafeNumber, ["bit-symmetry"], "v1")
        mgr.verify_swap(v1.version_id)
        mgr.execute_swap(v1.version_id)

        # Second version
        v2 = mgr.prepare_swap("test", SafeNumber, ["bit-symmetry"], "v2")
        mgr.verify_swap(v2.version_id)
        mgr.execute_swap(v2.version_id)

        # Rollback
        result = mgr.rollback("test")
        assert result is True
        assert mgr.active_versions["test"].proof_hash == "v1"

    def test_verify_fails_on_empty_axiom_ids(self):
        mgr = HotSwapManager()
        version = mgr.prepare_swap("test", SafeNumber, [""], "hash")
        result = mgr.verify_swap(version.version_id)
        assert result is False

    def test_verify_fails_on_non_callable_type(self):
        mgr = HotSwapManager()
        version = mgr.prepare_swap("test", "not_a_type", ["bit-symmetry"], "hash")
        result = mgr.verify_swap(version.version_id)
        assert result is False
