"""Test cross-layer coherence: Mac/Pi/Arduino sync."""

import pytest
import time
from distributed.cross_layer_coherence import (
    CrossLayerCoherence, Layer, LayerState
)


def make_state(layer: Layer, versions: dict = None, axiom_hash: str = "abc") -> LayerState:
    return LayerState(
        layer=layer,
        constraint_versions=versions or {"prime-bound-100": "v1"},
        axiom_registry_hash=axiom_hash,
        last_sync=time.time(),
        health="healthy"
    )


class TestVersionSync:
    """All layers must have matching constraint versions."""

    def test_synced_layers_have_no_mismatches(self):
        clc = CrossLayerCoherence()
        clc.register_layer(Layer.MACBOOK, make_state(Layer.MACBOOK))
        clc.register_layer(Layer.PI, make_state(Layer.PI))
        clc.register_layer(Layer.ARDUINO, make_state(Layer.ARDUINO))
        assert clc.check_version_sync() == {}

    def test_version_mismatch_detected(self):
        clc = CrossLayerCoherence()
        clc.register_layer(Layer.MACBOOK, make_state(Layer.MACBOOK, {"c1": "v2"}))
        clc.register_layer(Layer.PI, make_state(Layer.PI, {"c1": "v1"}))
        mismatches = clc.check_version_sync()
        assert "c1" in mismatches

    def test_missing_constraint_detected(self):
        clc = CrossLayerCoherence()
        clc.register_layer(Layer.MACBOOK, make_state(Layer.MACBOOK, {"c1": "v1"}))
        clc.register_layer(Layer.PI, make_state(Layer.PI, {}))
        mismatches = clc.check_version_sync()
        assert "c1" in mismatches


class TestAxiomCoherence:
    """All layers must share axiom registry."""

    def test_matching_hashes_coherent(self):
        clc = CrossLayerCoherence()
        clc.register_layer(Layer.MACBOOK, make_state(Layer.MACBOOK, axiom_hash="same"))
        clc.register_layer(Layer.PI, make_state(Layer.PI, axiom_hash="same"))
        assert clc.check_axiom_coherence() is True

    def test_mismatched_hashes_incoherent(self):
        clc = CrossLayerCoherence()
        clc.register_layer(Layer.MACBOOK, make_state(Layer.MACBOOK, axiom_hash="a"))
        clc.register_layer(Layer.PI, make_state(Layer.PI, axiom_hash="b"))
        assert clc.check_axiom_coherence() is False


class TestReconciliation:
    """MacBook is source of truth. Reconcile pushes to other layers."""

    def test_reconcile_syncs_versions(self):
        clc = CrossLayerCoherence()
        clc.register_layer(Layer.MACBOOK, make_state(Layer.MACBOOK, {"c1": "v2"}, "new_hash"))
        clc.register_layer(Layer.PI, make_state(Layer.PI, {"c1": "v1"}, "old_hash"))
        clc.register_layer(Layer.ARDUINO, make_state(Layer.ARDUINO, {}, "old_hash"))

        result = clc.reconcile(source_layer=Layer.MACBOOK)
        assert result is True
        assert clc.check_version_sync() == {}
        assert clc.check_axiom_coherence() is True


class TestFailureDetection:
    """Detect and isolate failed layers."""

    def test_detect_degraded_layer(self):
        clc = CrossLayerCoherence()
        bad_state = make_state(Layer.PI)
        bad_state.health = "degraded"
        clc.register_layer(Layer.MACBOOK, make_state(Layer.MACBOOK))
        clc.register_layer(Layer.PI, bad_state)
        assert Layer.PI in clc.detect_failure()

    def test_isolate_layer(self):
        clc = CrossLayerCoherence()
        clc.register_layer(Layer.PI, make_state(Layer.PI))
        clc.isolate_layer(Layer.PI)
        assert clc.layer_states[Layer.PI].health == "isolated"
        assert len(clc.coherence_log) == 1
        assert clc.coherence_log[0]["event"] == "layer_isolated"
