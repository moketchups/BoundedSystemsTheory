"""
HSAP Cryptographic Module - Ed25519 digital signatures for data integrity.

Provides cryptographic signing and verification to ensure attestation
records cannot be tampered with.
"""

import os
import hashlib
from pathlib import Path
from typing import Tuple, Optional

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.exceptions import InvalidSignature


# Default key storage location
DEFAULT_KEY_DIR = Path.home() / ".hsap" / "keys"


def generate_keypair(key_dir: Optional[Path] = None) -> Tuple[bytes, bytes]:
    """
    Generate a new Ed25519 keypair and save to disk.

    Args:
        key_dir: Directory to store keys. Defaults to ~/.hsap/keys/

    Returns:
        Tuple of (private_key_bytes, public_key_bytes)
    """
    key_dir = Path(key_dir) if key_dir else DEFAULT_KEY_DIR
    key_dir.mkdir(parents=True, exist_ok=True)

    # Generate new keypair
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    # Serialize keys
    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    )

    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )

    # Save to disk
    private_path = key_dir / "private.key"
    public_path = key_dir / "public.key"

    private_path.write_bytes(private_bytes)
    public_path.write_bytes(public_bytes)

    # Set restrictive permissions on private key
    os.chmod(private_path, 0o600)

    return private_bytes, public_bytes


def load_keypair(key_dir: Optional[Path] = None) -> Tuple[bytes, bytes]:
    """
    Load existing keypair from disk, or generate if not exists.

    Args:
        key_dir: Directory containing keys. Defaults to ~/.hsap/keys/

    Returns:
        Tuple of (private_key_bytes, public_key_bytes)
    """
    key_dir = Path(key_dir) if key_dir else DEFAULT_KEY_DIR
    private_path = key_dir / "private.key"
    public_path = key_dir / "public.key"

    if not private_path.exists() or not public_path.exists():
        return generate_keypair(key_dir)

    return private_path.read_bytes(), public_path.read_bytes()


def sign_data(data: bytes, private_key_bytes: Optional[bytes] = None) -> bytes:
    """
    Sign data using Ed25519.

    Args:
        data: Raw bytes to sign
        private_key_bytes: 32-byte private key. If None, loads from default location.

    Returns:
        64-byte signature
    """
    if private_key_bytes is None:
        private_key_bytes, _ = load_keypair()

    private_key = Ed25519PrivateKey.from_private_bytes(private_key_bytes)
    signature = private_key.sign(data)

    return signature


def verify_signature(
    data: bytes,
    signature: bytes,
    public_key_bytes: Optional[bytes] = None
) -> bool:
    """
    Verify an Ed25519 signature.

    Args:
        data: Original data that was signed
        signature: 64-byte signature to verify
        public_key_bytes: 32-byte public key. If None, loads from default location.

    Returns:
        True if signature is valid, False otherwise
    """
    if public_key_bytes is None:
        _, public_key_bytes = load_keypair()

    public_key = Ed25519PublicKey.from_public_bytes(public_key_bytes)

    try:
        public_key.verify(signature, data)
        return True
    except InvalidSignature:
        return False


def hash_data(data: bytes) -> str:
    """
    Compute SHA-256 hash of data.

    Args:
        data: Raw bytes to hash

    Returns:
        Hex-encoded hash string
    """
    return hashlib.sha256(data).hexdigest()


def hash_content(content: str) -> str:
    """
    Compute SHA-256 hash of string content.

    Args:
        content: String content to hash

    Returns:
        Hex-encoded hash string
    """
    return hash_data(content.encode("utf-8"))
