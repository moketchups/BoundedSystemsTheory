"""
HSAP CLI - Command-line interface implementation.

Usage:
    hsap attest --file data.txt --source human
    hsap verify --id <item_id>
    hsap status
    hsap visualize --id <item_id> --output graph.png
"""

import json
import sys
from pathlib import Path
from typing import Optional

import click

from hsap.core.attestation import HSAPCore
from hsap.core.provenance import ProvenanceGraph


# Default parameters matching the 7-AI consensus
DEFAULT_GAMMA = 0.9
DEFAULT_TAU = 0.5


@click.group()
@click.option("--gamma", default=DEFAULT_GAMMA, help="Attestation decay factor (0 < γ < 1)")
@click.option("--tau", default=DEFAULT_TAU, help="Compliance threshold (0 ≤ τ ≤ 1)")
@click.option("--db", default=None, help="Path to provenance database")
@click.pass_context
def cli(ctx, gamma: float, tau: float, db: Optional[str]):
    """
    HSAP - Human Source Attestation Protocol

    Prevent AI model collapse by tracking data provenance
    and ensuring training data maintains human origins.
    """
    ctx.ensure_object(dict)
    ctx.obj["hsap"] = HSAPCore(gamma=gamma, tau=tau, db_path=db)


@cli.command()
@click.option("--file", "-f", required=True, type=click.Path(exists=True),
              help="Path to file to attest")
@click.option("--source", "-s", default="human",
              type=click.Choice(["human", "ai", "derived"]),
              help="Source type (human for root sources)")
@click.option("--parents", "-p", multiple=True,
              help="Parent item IDs (for derived data)")
@click.option("--author", "-a", default=None, help="Author name")
@click.option("--description", "-d", default=None, help="Description")
@click.option("--json-output", "-j", is_flag=True, help="Output as JSON")
@click.pass_context
def attest(ctx, file: str, source: str, parents: tuple, author: str,
           description: str, json_output: bool):
    """
    Create attestation for a data file.

    Examples:
        hsap attest --file dataset.txt --source human
        hsap attest --file generated.txt --source derived --parents abc123
    """
    hsap: HSAPCore = ctx.obj["hsap"]
    file_path = Path(file)

    # Read file content
    try:
        data = file_path.read_bytes()
    except Exception as e:
        click.echo(f"Error reading file: {e}", err=True)
        sys.exit(1)

    # Build metadata
    metadata = {"filename": file_path.name}
    if author:
        metadata["author"] = author
    if description:
        metadata["description"] = description

    # Create attestation
    parents_list = list(parents)

    # Validate: root sources can't have parents
    if not parents_list and source != "human":
        source = "human"  # Auto-correct to human if no parents

    result = hsap.attest(
        data=data,
        parents=parents_list,
        source_type=source,
        metadata=metadata,
    )

    if json_output:
        click.echo(json.dumps(result, indent=2))
    else:
        if result.get("already_exists"):
            click.echo(f"Data already attested:")
        else:
            click.echo(f"Attestation created:")

        click.echo(f"  Item ID: {result['item_id']}")
        click.echo(f"  Data Hash: {result['data_hash'][:16]}...")
        click.echo(f"  Depth d(x): {result['depth']}")
        click.echo(f"  Attestation A(x): {result['attestation_score']:.6f}")
        click.echo(f"  Source Type: {result['source_type']}")
        click.echo(f"  Compliant: {'Yes' if result['compliant'] else 'No'}")

        if result['parents']:
            click.echo(f"  Parents: {', '.join(result['parents'])}")


@cli.command()
@click.option("--id", "-i", "item_id", required=True, help="Item ID to verify")
@click.option("--json-output", "-j", is_flag=True, help="Output as JSON")
@click.pass_context
def verify(ctx, item_id: str, json_output: bool):
    """
    Verify an attestation by item ID.

    Examples:
        hsap verify --id abc123-def456
    """
    hsap: HSAPCore = ctx.obj["hsap"]

    result = hsap.verify(item_id)

    if json_output:
        click.echo(json.dumps(result, indent=2))
    else:
        if not result.get("valid"):
            click.echo(f"Verification FAILED: {result.get('error', 'Unknown error')}", err=True)
            sys.exit(1)

        click.echo(f"Verification PASSED:")
        click.echo(f"  Item ID: {result['item_id']}")
        click.echo(f"  Data Hash: {result['data_hash'][:16]}...")
        click.echo(f"  Depth d(x): {result['depth']}")
        click.echo(f"  Attestation A(x): {result['attestation_score']:.6f}")
        click.echo(f"  Source Type: {result['source_type']}")
        click.echo(f"  Compliant: {'Yes' if result['compliant'] else 'No'}")
        click.echo(f"  Lineage Depth: {result['lineage_depth']} items")
        click.echo(f"  Timestamp: {result['timestamp']}")


@cli.command()
@click.option("--json-output", "-j", is_flag=True, help="Output as JSON")
@click.pass_context
def status(ctx, json_output: bool):
    """
    Show HSAP system status and statistics.
    """
    hsap: HSAPCore = ctx.obj["hsap"]

    stats = hsap.get_statistics()

    if json_output:
        click.echo(json.dumps(stats, indent=2))
    else:
        click.echo("HSAP System Status")
        click.echo("=" * 40)
        click.echo(f"  γ (gamma): {stats['gamma']}")
        click.echo(f"  τ (tau): {stats['tau']}")
        click.echo("")
        click.echo("Provenance Graph Statistics:")
        click.echo(f"  Total Items: {stats['total_items']}")
        click.echo(f"  Root Sources: {stats['root_sources']}")
        click.echo(f"  Derived Items: {stats['derived_items']}")
        click.echo(f"  Average Depth: {stats['average_depth']}")
        click.echo(f"  Max Depth: {stats['max_depth']}")
        click.echo(f"  Average A(x): {stats['average_attestation_score']:.4f}")


@cli.command()
@click.option("--id", "-i", "item_id", required=True, help="Item ID to visualize")
@click.option("--output", "-o", default="provenance.png",
              help="Output file path (PNG, PDF, or SVG)")
@click.option("--format", "-f", "fmt", default=None,
              type=click.Choice(["png", "pdf", "svg"]),
              help="Output format (auto-detected from extension)")
@click.pass_context
def visualize(ctx, item_id: str, output: str, fmt: Optional[str]):
    """
    Generate provenance DAG visualization for an item.

    Requires networkx and matplotlib (optional dependencies).

    Examples:
        hsap visualize --id abc123 --output graph.png
    """
    try:
        import networkx as nx
        import matplotlib.pyplot as plt
    except ImportError:
        click.echo("Visualization requires: pip install networkx matplotlib", err=True)
        sys.exit(1)

    hsap: HSAPCore = ctx.obj["hsap"]

    # Get lineage
    lineage = hsap.provenance.get_lineage(item_id)

    if not lineage:
        click.echo(f"Item {item_id} not found", err=True)
        sys.exit(1)

    # Build graph
    G = nx.DiGraph()

    for record in lineage:
        label = f"{record.item_id[:8]}...\nd={record.depth}\nA={record.attestation_score:.3f}"
        color = "lightgreen" if record.depth == 0 else "lightblue"
        G.add_node(record.item_id, label=label, color=color)

        for parent_id in record.parents:
            G.add_edge(parent_id, record.item_id)

    # Draw
    fig, ax = plt.subplots(figsize=(12, 8))

    pos = nx.spring_layout(G, k=2, iterations=50)
    colors = [G.nodes[n].get("color", "lightblue") for n in G.nodes()]
    labels = {n: G.nodes[n].get("label", n[:8]) for n in G.nodes()}

    nx.draw(G, pos, ax=ax, with_labels=False, node_color=colors,
            node_size=2000, arrows=True, arrowsize=20)
    nx.draw_networkx_labels(G, pos, labels, font_size=8, ax=ax)

    ax.set_title(f"HSAP Provenance Graph for {item_id[:16]}...")

    # Save
    output_path = Path(output)
    if fmt:
        output_path = output_path.with_suffix(f".{fmt}")

    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()

    click.echo(f"Provenance graph saved to: {output_path}")


@cli.command()
@click.pass_context
def init(ctx):
    """
    Initialize HSAP (generate keys, create database).
    """
    from hsap.core.crypto import generate_keypair

    click.echo("Initializing HSAP...")

    # Generate keypair
    private_bytes, public_bytes = generate_keypair()
    click.echo(f"  Generated Ed25519 keypair")

    # Initialize database by accessing it
    hsap: HSAPCore = ctx.obj["hsap"]
    stats = hsap.get_statistics()

    click.echo(f"  Initialized provenance database")
    click.echo(f"  Database location: {hsap.provenance.db_path}")
    click.echo("")
    click.echo("HSAP initialized successfully!")


@cli.command()
@click.option("--file", "-f", required=True, type=click.Path(exists=True),
              help="Path to file to check")
@click.pass_context
def check(ctx, file: str):
    """
    Check if a file's data has been attested.
    """
    from hsap.core.crypto import hash_data

    hsap: HSAPCore = ctx.obj["hsap"]
    file_path = Path(file)

    data = file_path.read_bytes()
    data_hash = hash_data(data)

    record = hsap.provenance.get_by_hash(data_hash)

    if record:
        click.echo(f"File IS attested:")
        click.echo(f"  Item ID: {record.item_id}")
        click.echo(f"  Depth: {record.depth}")
        click.echo(f"  A(x): {record.attestation_score:.6f}")
        click.echo(f"  Compliant: {'Yes' if record.attestation_score > hsap.tau else 'No'}")
    else:
        click.echo(f"File is NOT attested (hash: {data_hash[:16]}...)")


def main():
    """Entry point for CLI."""
    cli(obj={})


if __name__ == "__main__":
    main()
