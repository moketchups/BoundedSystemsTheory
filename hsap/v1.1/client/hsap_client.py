"""
HSAP v1.1 Client - Core client library for attestation verification.
"""

import hashlib
import json
import asyncio
from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Union
from concurrent.futures import ThreadPoolExecutor
import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.exceptions import InvalidSignature


@dataclass
class AttestationResult:
    """Result of an attestation lookup."""
    content_hash: str
    publisher: str
    depth: int
    score: float
    signature: str
    timestamp: str
    valid: bool
    raw: Dict[str, Any]


@dataclass
class VerificationResult:
    """Result of content verification."""
    content_hash: str
    verified: bool
    score: float  # Best score from all attestations (0.0 if unverified)
    attestations: List[AttestationResult]
    error: Optional[str] = None


class HSAPClient:
    """
    HSAP Client for verifying content attestations.

    Example:
        client = HSAPClient()
        result = client.verify("Some content to check")
        if result.verified:
            print(f"Attestation score: {result.score}")
    """

    DEFAULT_REGISTRY = "http://localhost:8000"  # Change to production URL

    def __init__(
        self,
        registry_url: str = None,
        gamma: float = 0.9,
        tau: float = 0.5,
        timeout: int = 10,
        cache_ttl: int = 3600,
    ):
        """
        Initialize HSAP client.

        Args:
            registry_url: URL of the HSAP registry service
            gamma: Attestation decay factor (0 < γ < 1)
            tau: Compliance threshold
            timeout: Request timeout in seconds
            cache_ttl: Cache TTL in seconds
        """
        self.registry_url = (registry_url or self.DEFAULT_REGISTRY).rstrip("/")
        self.gamma = gamma
        self.tau = tau
        self.timeout = timeout
        self.cache_ttl = cache_ttl

        # Caches
        self._lookup_cache: Dict[str, List[str]] = {}
        self._pubkey_cache: Dict[str, Ed25519PublicKey] = {}

        # Session for connection pooling
        self._session = requests.Session()

    def hash_content(self, content: Union[str, bytes]) -> str:
        """Compute SHA-256 hash of content."""
        if isinstance(content, str):
            content = content.encode("utf-8")
        return hashlib.sha256(content).hexdigest()

    def calculate_score(self, depth: int) -> float:
        """Calculate attestation score A(x) = γ^d(x)."""
        return self.gamma ** depth

    def is_compliant(self, score: float) -> bool:
        """Check if attestation score meets compliance threshold."""
        return score > self.tau

    def lookup(self, content_hash: str) -> List[str]:
        """
        Look up attestation servers for a content hash.

        Args:
            content_hash: SHA-256 hash of content

        Returns:
            List of publisher domains with attestations
        """
        # Check cache
        if content_hash in self._lookup_cache:
            return self._lookup_cache[content_hash]

        try:
            response = self._session.get(
                f"{self.registry_url}/lookup/{content_hash}",
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            servers = data.get("servers", [])

            # Cache result
            self._lookup_cache[content_hash] = servers
            return servers

        except requests.RequestException as e:
            # Registry unavailable - return empty
            return []

    def get_publisher_pubkey(self, domain: str) -> Optional[Ed25519PublicKey]:
        """Fetch and cache publisher's public key."""
        if domain in self._pubkey_cache:
            return self._pubkey_cache[domain]

        try:
            url = f"https://{domain}/.well-known/hsap/pubkey.pem"
            response = self._session.get(url, timeout=self.timeout)
            response.raise_for_status()

            pem_data = response.text.encode()
            public_key = serialization.load_pem_public_key(pem_data)

            if isinstance(public_key, Ed25519PublicKey):
                self._pubkey_cache[domain] = public_key
                return public_key

        except Exception:
            pass

        return None

    def fetch_attestation(self, domain: str, content_hash: str) -> Optional[AttestationResult]:
        """
        Fetch attestation from a publisher.

        Args:
            domain: Publisher domain
            content_hash: SHA-256 content hash

        Returns:
            AttestationResult or None if not found/invalid
        """
        try:
            url = f"https://{domain}/.well-known/hsap/attestations/{content_hash}.json"
            response = self._session.get(url, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()

            # Verify signature
            pubkey = self.get_publisher_pubkey(domain)
            valid = False

            if pubkey and "signature" in data:
                try:
                    # Reconstruct signed message
                    signed_data = json.dumps({
                        "hash": data.get("hash"),
                        "depth": data.get("depth", data.get("derivation_depth", 0)),
                        "timestamp": data.get("timestamp"),
                        "publisher": domain
                    }, sort_keys=True).encode()

                    signature = bytes.fromhex(data["signature"].replace("ed25519:", ""))
                    pubkey.verify(signature, signed_data)
                    valid = True
                except (InvalidSignature, ValueError):
                    valid = False

            depth = data.get("depth", data.get("derivation_depth", 0))
            score = self.calculate_score(depth)

            return AttestationResult(
                content_hash=content_hash,
                publisher=domain,
                depth=depth,
                score=score,
                signature=data.get("signature", ""),
                timestamp=data.get("timestamp", ""),
                valid=valid,
                raw=data
            )

        except Exception:
            return None

    def verify(self, content: Union[str, bytes]) -> VerificationResult:
        """
        Verify content and return attestation information.

        Args:
            content: Content to verify (string or bytes)

        Returns:
            VerificationResult with attestation details
        """
        content_hash = self.hash_content(content)
        return self.verify_hash(content_hash)

    def verify_hash(self, content_hash: str) -> VerificationResult:
        """
        Verify content by hash.

        Args:
            content_hash: SHA-256 hash of content

        Returns:
            VerificationResult with attestation details
        """
        # Look up publishers
        servers = self.lookup(content_hash)

        if not servers:
            return VerificationResult(
                content_hash=content_hash,
                verified=False,
                score=0.0,
                attestations=[],
                error="No attestations found"
            )

        # Fetch attestations from all publishers
        attestations = []
        for domain in servers:
            result = self.fetch_attestation(domain, content_hash)
            if result:
                attestations.append(result)

        if not attestations:
            return VerificationResult(
                content_hash=content_hash,
                verified=False,
                score=0.0,
                attestations=[],
                error="Could not fetch attestations"
            )

        # Find best (highest) valid score
        valid_attestations = [a for a in attestations if a.valid]
        if valid_attestations:
            best_score = max(a.score for a in valid_attestations)
        else:
            best_score = max(a.score for a in attestations)  # Use unverified if no valid

        return VerificationResult(
            content_hash=content_hash,
            verified=len(valid_attestations) > 0,
            score=best_score,
            attestations=attestations
        )

    def verify_batch(
        self,
        contents: List[Union[str, bytes]],
        max_workers: int = 10
    ) -> List[VerificationResult]:
        """
        Verify multiple contents in parallel.

        Args:
            contents: List of contents to verify
            max_workers: Maximum parallel workers

        Returns:
            List of VerificationResults in same order as input
        """
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(self.verify, contents))
        return results

    def get_scores_batch(
        self,
        contents: List[Union[str, bytes]],
        max_workers: int = 10
    ) -> List[float]:
        """
        Get attestation scores for multiple contents.

        Convenience method for training integration.

        Args:
            contents: List of contents
            max_workers: Maximum parallel workers

        Returns:
            List of scores (0.0 for unattested content)
        """
        results = self.verify_batch(contents, max_workers)
        return [r.score for r in results]

    def filter_compliant(
        self,
        contents: List[Union[str, bytes]],
        max_workers: int = 10
    ) -> List[tuple]:
        """
        Filter contents to only HSAP-compliant items.

        Args:
            contents: List of contents to filter
            max_workers: Maximum parallel workers

        Returns:
            List of (content, score) tuples for compliant items only
        """
        results = self.verify_batch(contents, max_workers)
        compliant = []
        for content, result in zip(contents, results):
            if self.is_compliant(result.score):
                compliant.append((content, result.score))
        return compliant


# Convenience functions
def verify(content: Union[str, bytes], registry_url: str = None) -> VerificationResult:
    """Quick verification of single content."""
    client = HSAPClient(registry_url=registry_url)
    return client.verify(content)


def get_score(content: Union[str, bytes], registry_url: str = None) -> float:
    """Get attestation score for content."""
    result = verify(content, registry_url)
    return result.score
