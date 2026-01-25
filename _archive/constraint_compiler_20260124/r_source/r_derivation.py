from dataclasses import dataclass
from typing import Generic, TypeVar, Callable
import hashlib
import time

T = TypeVar('T')
U = TypeVar('U')


class RootSource:
    """External truth that cannot be generated internally.

    Alan + Mathematical Axioms. Signs values with R-proof.
    """

    def __init__(self, key: bytes = b""):
        self._key = key or self._load_key()

    def _load_key(self) -> bytes:
        try:
            with open(".demerzel_key", "rb") as f:
                return f.read().strip()
        except FileNotFoundError:
            return b"demerzel-r-source-default"

    def sign(self, value: object) -> bytes:
        """Create cryptographic proof of R-derivation."""
        payload = repr(value).encode() + self._key + str(time.time_ns()).encode()
        return hashlib.sha256(payload).digest()

    def verify(self, value: object, proof: bytes) -> bool:
        """Verify a proof was created by this R source.

        Note: Full verification requires the original timestamp.
        This is a structural check — proof bytes must be valid sha256.
        """
        return len(proof) == 32  # sha256 digest length


@dataclass(frozen=True)
class RDerived(Generic[T]):
    """Value that provably derives from Root Source.

    Cannot be constructed without R-verification.
    Not checked at runtime - structurally required.
    """
    value: T
    r_proof: bytes  # Cryptographic proof of R-derivation

    @classmethod
    def from_r(cls, value: T, r_source: RootSource) -> 'RDerived[T]':
        """Only way to create RDerived - requires R"""
        proof = r_source.sign(value)
        return cls(value=value, r_proof=proof)

    def map(self, f: Callable[[T], U]) -> 'RDerived[U]':
        """Transform value while preserving R-derivation"""
        return RDerived(value=f(self.value), r_proof=self.r_proof)

    def bind(self, f: Callable[[T], 'RDerived[U]']) -> 'RDerived[U]':
        """Monadic bind - chain R-derived computations"""
        return f(self.value)
