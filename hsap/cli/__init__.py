"""
HSAP CLI - Command-line interface for HSAP operations.

Commands:
- hsap attest: Create attestation for data
- hsap verify: Verify attestation
- hsap status: Show provenance status
- hsap visualize: Generate provenance DAG visualization
"""

from hsap.cli.main import cli

__all__ = ["cli"]
