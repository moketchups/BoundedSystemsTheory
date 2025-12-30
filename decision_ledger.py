#!/usr/bin/env python3
"""
decision_ledger.py

Robust SQLite decision ledger with real migrations.

This version is SAFE against:
- older schemas
- missing columns
- extra legacy columns (e.g. responded_at_utc NOT NULL)

Design:
- request_hash is the stable key
- responded_at_utc (if present) is treated as an alias of updated_at_utc
"""

import json
import sqlite3
from datetime import datetime
from typing import Any, Dict


def now_utc_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


class DecisionLedger:
    def __init__(self, path: str):
        self.path = path
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self._migrate()

    # -------------------------
    # Migration
    # -------------------------

    def _migrate(self) -> None:
        cur = self.conn.cursor()

        # Base table (minimum viable)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS decision_ledger (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_hash TEXT NOT NULL UNIQUE,
            request_json TEXT NOT NULL,
            response_json TEXT NOT NULL
        )
        """)
        self.conn.commit()

        # Inspect existing columns
        cur.execute("PRAGMA table_info(decision_ledger)")
        cols = {row["name"] for row in cur.fetchall()}

        def add_col(name: str, ddl: str):
            if name not in cols:
                cur.execute(ddl)

        # Modern columns
        add_col("tool_results_json",
                "ALTER TABLE decision_ledger ADD COLUMN tool_results_json TEXT")
        add_col("created_at_utc",
                "ALTER TABLE decision_ledger ADD COLUMN created_at_utc TEXT")
        add_col("updated_at_utc",
                "ALTER TABLE decision_ledger ADD COLUMN updated_at_utc TEXT")

        # Legacy compatibility column
        if "responded_at_utc" not in cols:
            # Only add if missing — do NOT require NOT NULL
            add_col("responded_at_utc",
                    "ALTER TABLE decision_ledger ADD COLUMN responded_at_utc TEXT")

        self.conn.commit()

        # Backfill timestamps everywhere
        ts = now_utc_iso()
        cur.execute("""
        UPDATE decision_ledger
        SET
            created_at_utc = COALESCE(created_at_utc, ?),
            updated_at_utc = COALESCE(updated_at_utc, ?),
            responded_at_utc = COALESCE(responded_at_utc, ?)
        """, (ts, ts, ts))
        self.conn.commit()

    # -------------------------
    # Inserts / updates
    # -------------------------

    def insert_decision(self, request_hash: str, request_json: str, response_json: str) -> None:
        ts = now_utc_iso()
        cur = self.conn.cursor()

        try:
            cur.execute("""
            INSERT INTO decision_ledger (
                request_hash,
                request_json,
                response_json,
                tool_results_json,
                created_at_utc,
                updated_at_utc,
                responded_at_utc
            )
            VALUES (?, ?, ?, NULL, ?, ?, ?)
            ON CONFLICT(request_hash) DO UPDATE SET
                request_json = excluded.request_json,
                response_json = excluded.response_json,
                updated_at_utc = excluded.updated_at_utc,
                responded_at_utc = excluded.responded_at_utc
            """, (request_hash, request_json, response_json, ts, ts, ts))
            self.conn.commit()
            return
        except sqlite3.OperationalError:
            pass  # fall through for older SQLite

        # Manual upsert fallback
        cur.execute(
            "SELECT request_hash FROM decision_ledger WHERE request_hash=?",
            (request_hash,)
        )
        exists = cur.fetchone() is not None

        if not exists:
            cur.execute("""
            INSERT INTO decision_ledger (
                request_hash,
                request_json,
                response_json,
                tool_results_json,
                created_at_utc,
                updated_at_utc,
                responded_at_utc
            )
            VALUES (?, ?, ?, NULL, ?, ?, ?)
            """, (request_hash, request_json, response_json, ts, ts, ts))
        else:
            cur.execute("""
            UPDATE decision_ledger
            SET
                request_json=?,
                response_json=?,
                updated_at_utc=?,
                responded_at_utc=?
            WHERE request_hash=?
            """, (request_json, response_json, ts, ts, request_hash))

        self.conn.commit()

    def append_tool_results(self, request_hash: str, tool_results: Dict[str, Any]) -> None:
        ts = now_utc_iso()
        cur = self.conn.cursor()
        cur.execute("""
        UPDATE decision_ledger
        SET
            tool_results_json=?,
            updated_at_utc=?,
            responded_at_utc=?
        WHERE request_hash=?
        """, (json.dumps(tool_results, sort_keys=True), ts, ts, request_hash))
        self.conn.commit()

    def close(self) -> None:
        try:
            self.conn.close()
        except Exception:
            pass

