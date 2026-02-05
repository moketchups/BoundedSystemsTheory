"""
HSAP - Human Source Attestation Protocol

A software system that prevents AI model collapse by ensuring training data
maintains verifiable connections to human-originated sources.

Built on Bounded Systems Theory (BST) mathematical foundations.
"""

__version__ = "1.0.0"

# Core imports (always available)
from hsap.core.attestation import HSAPCore
from hsap.core.provenance import ProvenanceGraph

__all__ = [
    "HSAPCore",
    "ProvenanceGraph",
]

# PyTorch imports (optional - only if torch is installed)
try:
    from hsap.pytorch.loss import EmpiricalDistrustLoss
    from hsap.pytorch.trainer import HSAPTrainer
    __all__.extend(["EmpiricalDistrustLoss", "HSAPTrainer"])
except ImportError:
    # PyTorch not installed - that's OK, core functionality still works
    pass
