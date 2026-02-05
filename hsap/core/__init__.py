"""
HSAP Core - Mathematical foundations and cryptographic attestation.

Implements:
- D1: Root Source R = human-originated data with no AI in chain
- D3: Self-Referential Depth d(x) = 0 if root, else 1 + min(parent depths)
- D4: Attestation Function A(x) = γ^d(x)
"""

from hsap.core.attestation import HSAPCore
from hsap.core.provenance import ProvenanceGraph
from hsap.core.crypto import sign_data, verify_signature, generate_keypair

__all__ = [
    "HSAPCore",
    "ProvenanceGraph",
    "sign_data",
    "verify_signature",
    "generate_keypair",
]
