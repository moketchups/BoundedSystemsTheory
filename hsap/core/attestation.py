"""
HSAP Core Attestation - Main class implementing BST mathematical foundations.

Implements:
- D1: Root Source R = human-originated data with no AI in chain
- D3: Self-Referential Depth d(x) = 0 if root, else 1 + min(parent depths)
- D4: Attestation Function A(x) = γ^d(x)
- D5: HSAP-Compliant Dataset D_H = {x : d(x) < ∞ and A(x) > τ}
"""

import uuid
import json
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

from hsap.core.provenance import ProvenanceGraph, ProvenanceRecord
from hsap.core.crypto import sign_data, verify_signature, hash_data, hash_content


class HSAPCore:
    """
    Core HSAP implementation with mathematical foundations.

    Provides attestation and verification of data provenance,
    computing self-referential depth d(x) and attestation scores A(x).
    """

    def __init__(
        self,
        gamma: float = 0.9,
        tau: float = 0.5,
        db_path: Optional[str] = None,
    ):
        """
        Initialize HSAPCore.

        Args:
            gamma: Decay factor for attestation function (0 < γ < 1).
                   Default 0.9 means each derivation level reduces trust by 10%.
            tau: Compliance threshold for HSAP-compliant datasets.
                 Data with A(x) > τ is considered compliant.
            db_path: Path to SQLite database. Defaults to ~/.hsap/provenance.db
        """
        if not 0 < gamma < 1:
            raise ValueError("gamma must be between 0 and 1 (exclusive)")
        if not 0 <= tau <= 1:
            raise ValueError("tau must be between 0 and 1 (inclusive)")

        self.gamma = gamma
        self.tau = tau
        self.provenance = ProvenanceGraph(db_path)

    def calculate_depth(self, parents: Optional[List[str]] = None) -> int:
        """
        Calculate self-referential depth d(x) based on parents.

        D3: d(x) = 0 if x ∈ R (root source with no parents)
            d(x) = 1 + min{d(y) : y is parent of x} otherwise
            d(x) = ∞ if any parent is unattested

        Args:
            parents: List of parent item IDs. Empty or None for root sources.

        Returns:
            Computed depth value. Returns -1 for unattested (infinite depth).
        """
        if not parents:
            return 0  # Root source

        parent_depths = []
        for parent_id in parents:
            depth = self.provenance.get_depth(parent_id)
            if depth == -1:
                return -1  # Unattested parent means infinite depth
            parent_depths.append(depth)

        return 1 + min(parent_depths)

    def attestation_score(self, depth: int) -> float:
        """
        Calculate attestation score A(x) = γ^d(x).

        D4: A(x) = γ^d(x) where γ ∈ (0,1)
            A(x) = 0 for d(x) = ∞ (unattested data)

        Args:
            depth: Self-referential depth. -1 represents infinity.

        Returns:
            Attestation score between 0 and 1.
        """
        if depth == -1:
            return 0.0  # Unattested data
        return self.gamma ** depth

    def attest(
        self,
        data: Union[bytes, str],
        parents: Optional[List[str]] = None,
        source_type: str = "human",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a cryptographic attestation for data.

        Args:
            data: Raw bytes or string content to attest
            parents: List of parent item IDs. Empty for root sources.
            source_type: "human" for root sources, "ai" or "derived" for others
            metadata: Optional additional metadata (author, description, etc.)

        Returns:
            Attestation record containing:
            - item_id: Unique identifier
            - data_hash: SHA-256 hash of data
            - depth: Self-referential depth d(x)
            - attestation_score: A(x) = γ^d(x)
            - signature: Ed25519 signature
            - parents: List of parent IDs
            - source_type: Origin type
            - compliant: Whether A(x) > τ
        """
        # Convert string to bytes if needed
        if isinstance(data, str):
            data_bytes = data.encode("utf-8")
        else:
            data_bytes = data

        # Compute hash
        data_hash = hash_data(data_bytes)

        # Check if already attested
        existing = self.provenance.get_by_hash(data_hash)
        if existing:
            return {
                "item_id": existing.item_id,
                "data_hash": existing.data_hash,
                "depth": existing.depth,
                "attestation_score": existing.attestation_score,
                "signature": existing.signature,
                "parents": existing.parents,
                "source_type": existing.source_type,
                "compliant": existing.attestation_score > self.tau,
                "already_exists": True,
            }

        # Normalize parents
        parents = parents or []

        # Validate source_type for root sources
        if not parents and source_type not in ("human", "root"):
            source_type = "human"  # Root sources are human by definition

        # Calculate depth and attestation score
        depth = self.calculate_depth(parents)
        score = self.attestation_score(depth)

        # Generate unique ID
        item_id = str(uuid.uuid4())

        # Create attestation payload for signing
        attestation_payload = json.dumps({
            "item_id": item_id,
            "data_hash": data_hash,
            "depth": depth,
            "score": score,
            "parents": parents,
        }, sort_keys=True).encode("utf-8")

        # Sign the attestation
        signature = sign_data(attestation_payload)
        signature_hex = signature.hex()

        # Store in provenance graph
        self.provenance.add_item(
            item_id=item_id,
            data_hash=data_hash,
            parents=parents,
            depth=depth,
            attestation_score=score,
            signature=signature_hex,
            source_type=source_type,
            metadata=metadata,
        )

        return {
            "item_id": item_id,
            "data_hash": data_hash,
            "depth": depth,
            "attestation_score": score,
            "signature": signature_hex,
            "parents": parents,
            "source_type": source_type,
            "compliant": score > self.tau,
            "already_exists": False,
        }

    def verify(self, item_id: str) -> Dict[str, Any]:
        """
        Verify an attestation and return its status.

        Args:
            item_id: Unique identifier of the attested item

        Returns:
            Verification result containing:
            - valid: Whether the attestation exists and is valid
            - item_id: The item ID
            - depth: Self-referential depth
            - attestation_score: A(x)
            - compliant: Whether A(x) > τ
            - lineage: Full provenance chain
        """
        record = self.provenance.get_item(item_id)

        if record is None:
            return {
                "valid": False,
                "item_id": item_id,
                "error": "Item not found in provenance graph",
            }

        # Verify attestation score matches expected value
        expected_score = self.attestation_score(record.depth)
        score_valid = abs(record.attestation_score - expected_score) < 1e-10

        # Get lineage
        lineage = self.provenance.get_lineage(item_id)

        return {
            "valid": score_valid,
            "item_id": item_id,
            "data_hash": record.data_hash,
            "depth": record.depth,
            "attestation_score": record.attestation_score,
            "compliant": record.attestation_score > self.tau,
            "source_type": record.source_type,
            "parents": record.parents,
            "lineage_depth": len(lineage),
            "timestamp": record.timestamp,
        }

    def get_score(self, item_id: str) -> float:
        """
        Get attestation score for an item.

        Args:
            item_id: Unique identifier

        Returns:
            Attestation score A(x), or 0.0 if not found
        """
        return self.provenance.get_attestation_score(item_id)

    def get_scores_batch(self, item_ids: List[str]) -> List[float]:
        """
        Get attestation scores for multiple items.

        Args:
            item_ids: List of unique identifiers

        Returns:
            List of attestation scores (0.0 for unattested items)
        """
        return [self.get_score(item_id) for item_id in item_ids]

    def is_compliant(self, item_id: str) -> bool:
        """
        Check if an item meets HSAP compliance threshold.

        D5: x ∈ D_H iff d(x) < ∞ and A(x) > τ

        Args:
            item_id: Unique identifier

        Returns:
            True if compliant, False otherwise
        """
        score = self.get_score(item_id)
        return score > self.tau

    def filter_compliant(self, item_ids: List[str]) -> List[str]:
        """
        Filter a list of items to only HSAP-compliant ones.

        Args:
            item_ids: List of unique identifiers

        Returns:
            List of compliant item IDs (where A(x) > τ)
        """
        return [
            item_id for item_id in item_ids
            if self.is_compliant(item_id)
        ]

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the HSAP system.

        Returns:
            Dictionary with provenance statistics and parameters
        """
        stats = self.provenance.get_statistics()
        stats.update({
            "gamma": self.gamma,
            "tau": self.tau,
        })
        return stats

    def attest_root_source(
        self,
        data: Union[bytes, str],
        author: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Convenience method to attest human-originated root source data.

        Args:
            data: Raw bytes or string content
            author: Optional author name
            description: Optional description
            metadata: Optional additional metadata

        Returns:
            Attestation record with depth=0 and A(x)=1.0
        """
        meta = metadata or {}
        if author:
            meta["author"] = author
        if description:
            meta["description"] = description

        return self.attest(
            data=data,
            parents=[],
            source_type="human",
            metadata=meta,
        )

    def attest_derived(
        self,
        data: Union[bytes, str],
        parents: List[str],
        transformation: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Convenience method to attest AI-derived or transformed data.

        Args:
            data: Raw bytes or string content
            parents: List of parent item IDs (required, non-empty)
            transformation: Optional description of transformation applied
            metadata: Optional additional metadata

        Returns:
            Attestation record with computed depth and score
        """
        if not parents:
            raise ValueError("Derived data must have at least one parent")

        meta = metadata or {}
        if transformation:
            meta["transformation"] = transformation

        return self.attest(
            data=data,
            parents=parents,
            source_type="derived",
            metadata=meta,
        )
