"""
HSAP Provenance Graph - SQLite-backed DAG for tracking data lineage.

Implements provenance chain storage and retrieval for computing
self-referential depth d(x).
"""

import sqlite3
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict


# Default database location
DEFAULT_DB_PATH = Path.home() / ".hsap" / "provenance.db"


@dataclass
class ProvenanceRecord:
    """A single record in the provenance graph."""
    item_id: str
    data_hash: str
    parents: List[str]
    depth: int
    attestation_score: float
    signature: str
    source_type: str  # "human" or "ai" or "derived"
    timestamp: str
    metadata: Dict[str, Any]


class ProvenanceGraph:
    """
    SQLite-backed provenance graph for tracking data lineage.

    Stores a DAG of data items where:
    - Root sources (human-originated) have no parents and depth=0
    - Derived data points to parents and depth=1+min(parent depths)
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize provenance graph with SQLite backend.

        Args:
            db_path: Path to SQLite database. Defaults to ~/.hsap/provenance.db
        """
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS provenance (
                    item_id TEXT PRIMARY KEY,
                    data_hash TEXT NOT NULL,
                    parents TEXT NOT NULL,
                    depth INTEGER NOT NULL,
                    attestation_score REAL NOT NULL,
                    signature TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    metadata TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_depth ON provenance(depth)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_data_hash ON provenance(data_hash)
            """)
            conn.commit()

    def add_item(
        self,
        item_id: str,
        data_hash: str,
        parents: List[str],
        depth: int,
        attestation_score: float,
        signature: str,
        source_type: str = "derived",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Add an item to the provenance graph.

        Args:
            item_id: Unique identifier for this data item
            data_hash: SHA-256 hash of the data content
            parents: List of parent item IDs (empty for root sources)
            depth: Self-referential depth d(x)
            attestation_score: Computed A(x) = γ^d(x)
            signature: Ed25519 signature of the attestation
            source_type: "human", "ai", or "derived"
            metadata: Optional additional metadata

        Returns:
            True if item was added, False if item_id already exists
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        metadata = metadata or {}

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO provenance
                    (item_id, data_hash, parents, depth, attestation_score,
                     signature, source_type, timestamp, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        item_id,
                        data_hash,
                        json.dumps(parents),
                        depth,
                        attestation_score,
                        signature,
                        source_type,
                        timestamp,
                        json.dumps(metadata),
                    ),
                )
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_item(self, item_id: str) -> Optional[ProvenanceRecord]:
        """
        Retrieve a single item from the provenance graph.

        Args:
            item_id: Unique identifier of the item

        Returns:
            ProvenanceRecord or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM provenance WHERE item_id = ?",
                (item_id,),
            )
            row = cursor.fetchone()

        if row is None:
            return None

        return ProvenanceRecord(
            item_id=row["item_id"],
            data_hash=row["data_hash"],
            parents=json.loads(row["parents"]),
            depth=row["depth"],
            attestation_score=row["attestation_score"],
            signature=row["signature"],
            source_type=row["source_type"],
            timestamp=row["timestamp"],
            metadata=json.loads(row["metadata"]),
        )

    def get_depth(self, item_id: str) -> int:
        """
        Get the self-referential depth d(x) for an item.

        Args:
            item_id: Unique identifier of the item

        Returns:
            Depth value, or -1 if item not found (treated as infinity)
        """
        item = self.get_item(item_id)
        if item is None:
            return -1  # Represents infinity (unattested)
        return item.depth

    def get_attestation_score(self, item_id: str) -> float:
        """
        Get the attestation score A(x) for an item.

        Args:
            item_id: Unique identifier of the item

        Returns:
            Attestation score, or 0.0 if item not found (unattested)
        """
        item = self.get_item(item_id)
        if item is None:
            return 0.0  # Unattested data has A(x) = 0
        return item.attestation_score

    def get_lineage(self, item_id: str) -> List[ProvenanceRecord]:
        """
        Retrieve the full provenance chain for an item.

        Args:
            item_id: Unique identifier of the item

        Returns:
            List of ProvenanceRecords from root to this item
        """
        lineage = []
        visited = set()
        stack = [item_id]

        while stack:
            current_id = stack.pop()
            if current_id in visited:
                continue
            visited.add(current_id)

            item = self.get_item(current_id)
            if item is None:
                continue

            lineage.append(item)
            stack.extend(item.parents)

        # Sort by depth (root sources first)
        lineage.sort(key=lambda x: x.depth)
        return lineage

    def exists(self, item_id: str) -> bool:
        """Check if an item exists in the provenance graph."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT 1 FROM provenance WHERE item_id = ?",
                (item_id,),
            )
            return cursor.fetchone() is not None

    def exists_by_hash(self, data_hash: str) -> bool:
        """Check if data with this hash already exists."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT 1 FROM provenance WHERE data_hash = ?",
                (data_hash,),
            )
            return cursor.fetchone() is not None

    def get_by_hash(self, data_hash: str) -> Optional[ProvenanceRecord]:
        """Retrieve an item by its data hash."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM provenance WHERE data_hash = ?",
                (data_hash,),
            )
            row = cursor.fetchone()

        if row is None:
            return None

        return ProvenanceRecord(
            item_id=row["item_id"],
            data_hash=row["data_hash"],
            parents=json.loads(row["parents"]),
            depth=row["depth"],
            attestation_score=row["attestation_score"],
            signature=row["signature"],
            source_type=row["source_type"],
            timestamp=row["timestamp"],
            metadata=json.loads(row["metadata"]),
        )

    def count(self) -> int:
        """Get total number of items in the provenance graph."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM provenance")
            return cursor.fetchone()[0]

    def get_root_sources(self) -> List[ProvenanceRecord]:
        """Get all root sources (depth=0)."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM provenance WHERE depth = 0"
            )
            rows = cursor.fetchall()

        return [
            ProvenanceRecord(
                item_id=row["item_id"],
                data_hash=row["data_hash"],
                parents=json.loads(row["parents"]),
                depth=row["depth"],
                attestation_score=row["attestation_score"],
                signature=row["signature"],
                source_type=row["source_type"],
                timestamp=row["timestamp"],
                metadata=json.loads(row["metadata"]),
            )
            for row in rows
        ]

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the provenance graph."""
        with sqlite3.connect(self.db_path) as conn:
            total = conn.execute("SELECT COUNT(*) FROM provenance").fetchone()[0]
            roots = conn.execute(
                "SELECT COUNT(*) FROM provenance WHERE depth = 0"
            ).fetchone()[0]
            avg_depth = conn.execute(
                "SELECT AVG(depth) FROM provenance"
            ).fetchone()[0] or 0
            avg_score = conn.execute(
                "SELECT AVG(attestation_score) FROM provenance"
            ).fetchone()[0] or 0
            max_depth = conn.execute(
                "SELECT MAX(depth) FROM provenance"
            ).fetchone()[0] or 0

        return {
            "total_items": total,
            "root_sources": roots,
            "derived_items": total - roots,
            "average_depth": round(avg_depth, 2),
            "average_attestation_score": round(avg_score, 4),
            "max_depth": max_depth,
        }
