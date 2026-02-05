#!/usr/bin/env python3
"""
HSAP v1.1 CLI - Command-line tool for publishers and verifiers.

Commands:
    hsap keygen          Generate Ed25519 keypair
    hsap attest          Attest a file or directory
    hsap verify          Verify content attestation
    hsap register        Register as a publisher
    hsap serve           Serve attestations locally
"""

import click
import hashlib
import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey


HSAP_DIR = Path.home() / ".hsap"
KEYS_DIR = HSAP_DIR / "keys"
ATTESTATIONS_DIR = HSAP_DIR / "attestations"


def ensure_dirs():
    """Ensure HSAP directories exist."""
    HSAP_DIR.mkdir(exist_ok=True)
    KEYS_DIR.mkdir(exist_ok=True)
    ATTESTATIONS_DIR.mkdir(exist_ok=True)


def hash_content(content: bytes) -> str:
    """Compute SHA-256 hash."""
    return hashlib.sha256(content).hexdigest()


def load_private_key(key_path: Optional[Path] = None) -> Ed25519PrivateKey:
    """Load private key from file."""
    key_path = key_path or (KEYS_DIR / "private.pem")
    if not key_path.exists():
        raise click.ClickException(f"Private key not found at {key_path}. Run 'hsap keygen' first.")

    with open(key_path, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)


def load_public_key(key_path: Optional[Path] = None) -> Ed25519PublicKey:
    """Load public key from file."""
    key_path = key_path or (KEYS_DIR / "public.pem")
    if not key_path.exists():
        raise click.ClickException(f"Public key not found at {key_path}. Run 'hsap keygen' first.")

    with open(key_path, "rb") as f:
        return serialization.load_pem_public_key(f.read())


@click.group()
@click.version_option(version="1.1.0")
def cli():
    """HSAP - Human Source Attestation Protocol CLI"""
    ensure_dirs()


@cli.command()
@click.option("--output", "-o", type=click.Path(), help="Output directory for keys")
@click.option("--force", "-f", is_flag=True, help="Overwrite existing keys")
def keygen(output: Optional[str], force: bool):
    """Generate Ed25519 keypair for signing attestations."""
    output_dir = Path(output) if output else KEYS_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    private_path = output_dir / "private.pem"
    public_path = output_dir / "public.pem"

    if private_path.exists() and not force:
        raise click.ClickException(f"Keys already exist at {output_dir}. Use --force to overwrite.")

    # Generate keypair
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    # Save private key
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    with open(private_path, "wb") as f:
        f.write(private_pem)
    os.chmod(private_path, 0o600)

    # Save public key
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    with open(public_path, "wb") as f:
        f.write(public_pem)

    click.echo(f"Generated Ed25519 keypair:")
    click.echo(f"  Private key: {private_path}")
    click.echo(f"  Public key:  {public_path}")
    click.echo(f"\nCopy {public_path} to your server at /.well-known/hsap/pubkey.pem")


@cli.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--depth", "-d", type=int, default=0, help="Derivation depth (0 = human source)")
@click.option("--output", "-o", type=click.Path(), help="Output directory for attestations")
@click.option("--recursive", "-r", is_flag=True, help="Process directories recursively")
@click.option("--key", "-k", type=click.Path(exists=True), help="Path to private key")
@click.option("--domain", type=str, required=True, help="Publisher domain")
def attest(path: str, depth: int, output: Optional[str], recursive: bool, key: Optional[str], domain: str):
    """Create attestation(s) for file(s)."""
    source_path = Path(path)
    output_dir = Path(output) if output else ATTESTATIONS_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    private_key = load_private_key(Path(key) if key else None)

    files_to_attest = []
    if source_path.is_file():
        files_to_attest.append(source_path)
    elif source_path.is_dir():
        if recursive:
            files_to_attest.extend(source_path.rglob("*"))
        else:
            files_to_attest.extend(source_path.glob("*"))
        files_to_attest = [f for f in files_to_attest if f.is_file()]

    if not files_to_attest:
        raise click.ClickException("No files found to attest")

    click.echo(f"Attesting {len(files_to_attest)} file(s)...")

    for file_path in files_to_attest:
        try:
            with open(file_path, "rb") as f:
                content = f.read()

            content_hash = hash_content(content)
            timestamp = datetime.now(timezone.utc).isoformat()

            # Create attestation data to sign
            attestation_data = {
                "hash": content_hash,
                "depth": depth,
                "timestamp": timestamp,
                "publisher": domain
            }

            # Sign
            message = json.dumps(attestation_data, sort_keys=True).encode()
            signature = private_key.sign(message)

            # Full attestation record
            attestation = {
                "hsap_version": "1.1",
                "hash": content_hash,
                "derivation_depth": depth,
                "timestamp": timestamp,
                "publisher": domain,
                "source_file": str(file_path.name),
                "signature": f"ed25519:{signature.hex()}"
            }

            # Save attestation
            attestation_path = output_dir / f"{content_hash}.json"
            with open(attestation_path, "w") as f:
                json.dump(attestation, f, indent=2)

            click.echo(f"  {file_path.name} -> {content_hash[:16]}...")

        except Exception as e:
            click.echo(f"  ERROR {file_path.name}: {e}", err=True)

    click.echo(f"\nAttestations saved to: {output_dir}")
    click.echo(f"Copy to your server at /.well-known/hsap/attestations/")


@cli.command()
@click.argument("content", type=str)
@click.option("--registry", "-r", type=str, default="http://localhost:8000", help="Registry URL")
@click.option("--file", "-f", is_flag=True, help="Treat CONTENT as a file path")
def verify(content: str, registry: str, file: bool):
    """Verify content attestation."""
    # Import client here to avoid circular imports
    sys.path.insert(0, str(Path(__file__).parent.parent / "client"))
    from hsap_client import HSAPClient

    client = HSAPClient(registry_url=registry)

    if file:
        with open(content, "rb") as f:
            data = f.read()
    else:
        data = content

    result = client.verify(data)

    click.echo(f"Content Hash: {result.content_hash}")
    click.echo(f"Verified: {'Yes' if result.verified else 'No'}")
    click.echo(f"Score A(x): {result.score:.4f}")
    click.echo(f"Compliant: {'Yes' if client.is_compliant(result.score) else 'No'}")

    if result.attestations:
        click.echo(f"\nAttestations found: {len(result.attestations)}")
        for att in result.attestations:
            valid_str = "valid" if att.valid else "INVALID"
            click.echo(f"  - {att.publisher}: depth={att.depth}, score={att.score:.4f} ({valid_str})")

    if result.error:
        click.echo(f"\nError: {result.error}")


@cli.command()
@click.option("--domain", "-d", type=str, required=True, help="Your domain")
@click.option("--email", "-e", type=str, required=True, help="Contact email")
@click.option("--org", "-o", type=str, help="Organization name")
@click.option("--registry", "-r", type=str, default="http://localhost:8000", help="Registry URL")
@click.option("--key", "-k", type=click.Path(exists=True), help="Path to public key")
def register(domain: str, email: str, org: Optional[str], registry: str, key: Optional[str]):
    """Register as a publisher with the registry."""
    import requests

    # Load public key
    public_key_path = Path(key) if key else (KEYS_DIR / "public.pem")
    if not public_key_path.exists():
        raise click.ClickException(f"Public key not found at {public_key_path}. Run 'hsap keygen' first.")

    with open(public_key_path, "r") as f:
        public_key_pem = f.read()

    # Register with registry
    response = requests.post(
        f"{registry}/register-publisher",
        json={
            "domain": domain,
            "public_key": public_key_pem,
            "contact_email": email,
            "organization": org
        }
    )

    if response.status_code != 200:
        raise click.ClickException(f"Registration failed: {response.text}")

    data = response.json()

    click.echo(f"Registration submitted for: {domain}")
    click.echo(f"\nVerification required. Choose one method:")
    click.echo(f"\n1. DNS TXT Record:")
    click.echo(f"   Name:  {data['verification_methods']['dns']['name']}")
    click.echo(f"   Value: {data['verification_methods']['dns']['value']}")
    click.echo(f"\n2. File Verification:")
    click.echo(f"   URL:     {data['verification_methods']['file']['url']}")
    click.echo(f"   Content: {data['verification_methods']['file']['content']}")
    click.echo(f"\nAfter placing the token, verify with:")
    click.echo(f"   hsap verify-domain --domain {domain} --registry {registry}")


@cli.command("verify-domain")
@click.option("--domain", "-d", type=str, required=True, help="Domain to verify")
@click.option("--method", "-m", type=click.Choice(["dns", "file"]), default="file", help="Verification method")
@click.option("--registry", "-r", type=str, default="http://localhost:8000", help="Registry URL")
def verify_domain(domain: str, method: str, registry: str):
    """Verify domain ownership with the registry."""
    import requests

    response = requests.post(
        f"{registry}/verify-publisher",
        params={"domain": domain, "method": method}
    )

    if response.status_code == 200:
        click.echo(f"Domain verified: {domain}")
        click.echo("You can now submit attestations to the registry.")
    else:
        raise click.ClickException(f"Verification failed: {response.text}")


@cli.command()
@click.option("--port", "-p", type=int, default=8080, help="Port to serve on")
@click.option("--dir", "-d", type=click.Path(exists=True), help="Attestations directory")
def serve(port: int, dir: Optional[str]):
    """Serve attestations locally for testing."""
    from http.server import HTTPServer, SimpleHTTPRequestHandler
    import functools

    attestations_dir = Path(dir) if dir else ATTESTATIONS_DIR

    # Create .well-known structure
    well_known = attestations_dir.parent / ".well-known" / "hsap"
    well_known.mkdir(parents=True, exist_ok=True)

    # Symlink attestations
    att_link = well_known / "attestations"
    if not att_link.exists():
        att_link.symlink_to(attestations_dir)

    # Copy pubkey if exists
    pubkey_src = KEYS_DIR / "public.pem"
    pubkey_dst = well_known / "pubkey.pem"
    if pubkey_src.exists() and not pubkey_dst.exists():
        import shutil
        shutil.copy(pubkey_src, pubkey_dst)

    os.chdir(attestations_dir.parent)

    handler = functools.partial(SimpleHTTPRequestHandler, directory=str(attestations_dir.parent))
    server = HTTPServer(("0.0.0.0", port), handler)

    click.echo(f"Serving attestations at http://localhost:{port}/.well-known/hsap/")
    click.echo("Press Ctrl+C to stop")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        click.echo("\nStopped")


@cli.command()
@click.option("--registry", "-r", type=str, default="http://localhost:8000", help="Registry URL")
def stats(registry: str):
    """Show registry statistics."""
    import requests

    response = requests.get(f"{registry}/stats")
    if response.status_code != 200:
        raise click.ClickException(f"Failed to get stats: {response.text}")

    data = response.json()

    click.echo("HSAP Registry Statistics")
    click.echo("=" * 40)
    click.echo(f"Total Publishers:    {data['total_publishers']}")
    click.echo(f"Verified Publishers: {data['verified_publishers']}")
    click.echo(f"Total Attestations:  {data['total_attestations']}")
    click.echo(f"Lookups (24h):       {data['lookups_24h']}")


if __name__ == "__main__":
    cli()
