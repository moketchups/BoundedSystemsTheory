"""
HSAP v1.1 Client Library
Python client for verifying and creating attestations.

Usage:
    from hsap.v1_1.client import HSAPClient

    client = HSAPClient(registry_url="https://registry.hsap.io")

    # Verify content
    result = client.verify(content="Human-written text")
    print(result.score)  # 1.0 for human source

    # Batch verify
    results = client.verify_batch(contents=["text1", "text2", "text3"])
"""

from .hsap_client import HSAPClient, AttestationResult, VerificationResult

__all__ = ["HSAPClient", "AttestationResult", "VerificationResult"]
