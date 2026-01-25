from dataclasses import dataclass, field
from typing import Dict, List
from enum import Enum
import time


class Layer(Enum):
    MACBOOK = "macbook"      # Constraint compiler
    PI = "pi"                # Distributed cognition
    ARDUINO = "arduino"      # Physical bridge


@dataclass
class LayerState:
    layer: Layer
    constraint_versions: Dict[str, str]  # constraint_id -> version_hash
    axiom_registry_hash: str
    last_sync: float  # timestamp
    health: str  # "healthy" | "degraded" | "failed" | "isolated"


class CrossLayerCoherence:
    def __init__(self):
        self.layer_states: Dict[Layer, LayerState] = {}
        self.coherence_log: List[dict] = []

    def register_layer(self, layer: Layer, state: LayerState):
        self.layer_states[layer] = state

    def check_version_sync(self) -> Dict[str, Dict[str, List[Layer]]]:
        """Find constraints with version mismatches across layers"""
        mismatches: Dict[str, Dict[str, List[Layer]]] = {}
        all_constraints: set = set()

        for state in self.layer_states.values():
            all_constraints.update(state.constraint_versions.keys())

        for constraint_id in all_constraints:
            versions: Dict[str, List[Layer]] = {}
            for layer, state in self.layer_states.items():
                v = state.constraint_versions.get(constraint_id, "MISSING")
                if v not in versions:
                    versions[v] = []
                versions[v].append(layer)

            if len(versions) > 1:
                mismatches[constraint_id] = versions

        return mismatches

    def check_axiom_coherence(self) -> bool:
        """Verify all layers have same axiom registry"""
        hashes = [s.axiom_registry_hash for s in self.layer_states.values()]
        return len(set(hashes)) == 1

    def reconcile(self, source_layer: Layer = Layer.MACBOOK) -> bool:
        """Push source layer state to all other layers"""
        source_state = self.layer_states[source_layer]

        for layer, state in self.layer_states.items():
            if layer == source_layer:
                continue
            # Push constraint versions
            state.constraint_versions = dict(source_state.constraint_versions)
            # Push axiom registry hash
            state.axiom_registry_hash = source_state.axiom_registry_hash
            state.last_sync = time.time()

        return self.check_version_sync() == {} and self.check_axiom_coherence()

    def detect_failure(self) -> List[Layer]:
        """Identify failed or degraded layers"""
        return [
            layer for layer, state in self.layer_states.items()
            if state.health in ["degraded", "failed"]
        ]

    def isolate_layer(self, layer: Layer):
        """Isolate failed layer, continue with remaining"""
        self.layer_states[layer].health = "isolated"
        self.coherence_log.append({
            "event": "layer_isolated",
            "layer": layer.value,
            "timestamp": time.time()
        })
