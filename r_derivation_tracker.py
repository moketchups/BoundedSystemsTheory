"""
r_derivation_tracker.py - Core R-Derivation Type System

R -> C -> I Architecture:
Wraps all data flowing through the system with its R provenance.
Every fact, classification, and response carries its mathematical birth certificate.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import TypeVar, Generic, List

T = TypeVar('T')


@dataclass
class DerivationNode:
    """A node in the R-derivation chain."""
    axiom: str                      # e.g. 'demerzel-purpose-axiom-v1'
    source_doc: str                 # e.g. 'DONE_ROOT_SOURCE_FOR_UPLOAD_extracted.txt'
    derivation_path: List[str]      # e.g. ['goldbach-symmetry', 'bounded-system-proof']


@dataclass
class RDerived(Generic[T]):
    """Data wrapped with its R-derivation proof."""
    value: T
    derivation: DerivationNode
    timestamp: datetime = field(default_factory=datetime.now)
    verified: bool = False


class RDerivationTracker:
    """Tracks R-derivation provenance across the pipeline."""

    def tag_with_r(self, component: str, data: T, axiom: str, source_doc: str, path: List[str]) -> RDerived[T]:
        """Wrap data with its R derivation proof."""
        node = DerivationNode(axiom=axiom, source_doc=source_doc, derivation_path=path)
        return RDerived(value=data, derivation=node)

    def verify_chain(self, input_tag: RDerived, output_tag: RDerived) -> bool:
        """
        Verify output correctly derives from input.
        Output axiom must match input axiom, and output path must extend input path.
        """
        if input_tag.derivation.axiom != output_tag.derivation.axiom:
            return False
        # Output path must start with input path (extension)
        in_path = input_tag.derivation.derivation_path
        out_path = output_tag.derivation.derivation_path
        if len(out_path) < len(in_path):
            return False
        return out_path[:len(in_path)] == in_path

    def get_full_derivation(self, *tags: RDerived) -> List[DerivationNode]:
        """Return complete R->C->I path from all tagged components."""
        return [tag.derivation for tag in tags]
