#!/usr/bin/env python3
"""
decision_ledger.py

SQLite decision ledger for Demerzel.

Requirements:
- Store request_hash, request_json, response_json, timestamps.
- Robust migrations: if table exists from older runs, add missing columns.
- Never crash the main loop because a column is missing or a timestamp is NULL.

This module intentionally:
- Allows responded_at_utc / updated_at_utc to be NULL for older rows.
- Fills timestamps automatically on insert.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from typing import Any, Dict, Optional


def utc_now_iso() -> str:
    # Use second precision to keep logs readable/deterministic enough for human audit
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


class DecisionLedger:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._migrate()

    def close(self):
        try:
            self.conn.close()
        except Exception:
            pass

    def _table_exists(self, name: str) -> bool:
        cur = self.conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,))
        return cur.fetchone() is not None

    def _columns(self, table: str) -> Dict[str, Dict[str, Any]]:
        cur = self.conn.cursor()
        cur.execute(f"PRAGMA table_info({table})")
        out: Dict[str, Dict[str, Any]] = {}
        for r in cur.fetchall():
            out[r["name"]] = dict(r)
        return out

    def _safe_add_column(self, table: str, col: str, ddl: str):
        cols = self._columns(table)
        if col not in cols:
            cur = self.conn.cursor()
            cur.execute(ddl)
            self.conn.commit()

    def _migrate(self):
        cur = self.conn.cursor()

        # Create (fresh install)
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS decision_ledger (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_hash TEXT NOT NULL,
                request_json TEXT NOT NULL,
                response_json TEXT NOT NULL,
                tool_results_json TEXT,
                created_at_utc TEXT NOT NULL,
                updated_at_utc TEXT,
                responded_at_utc TEXT
            )
            """
        )
        self.conn.commit()

        # Migrate older versions (add columns if missing)
        self._safe_add_column("decision_ledger", "tool_results_json",
                              "ALTER TABLE decision_ledger ADD COLUMN tool_results_json TEXT")
        self._safe_add_column("decision_ledger", "created_at_utc",
                              "ALTER TABLE decision_ledger ADD COLUMN created_at_utc TEXT")
        self._safe_add_column("decision_ledger", "updated_at_utc",
                              "ALTER TABLE decision_ledger ADD COLUMN updated_at_utc TEXT")
        self._safe_add_column("decision_ledger", "responded_at_utc",
                              "ALTER TABLE decision_ledger ADD COLUMN responded_at_utc TEXT")

        # Backfill created_at_utc if NULL/empty
        cols = self._columns("decision_ledger")
        if "created_at_utc" in cols:
            cur.execute(
                "UPDATE decision_ledger SET created_at_utc=? WHERE created_at_utc IS NULL OR created_at_utc=''",
                (utc_now_iso(),),
            )
            self.conn.commit()

        # Optional index for lookup
        cur.execute("CREATE INDEX IF NOT EXISTS idx_decision_ledger_request_hash ON decision_ledger(request_hash)")
        self.conn.commit()

    def insert_decision(
        self,
        request_hash: str,
        request_json: Dict[str, Any],
        response_json: Dict[str, Any],
        tool_results_json: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        Insert a full ledger entry. Always writes timestamps.
        Never relies on schema having NOT NULL responded_at_utc in older tables.
        """
        ts = utc_now_iso()

        req_s = json.dumps(request_json, ensure_ascii=False, sort_keys=True)
        resp_s = json.dumps(response_json, ensure_ascii=False, sort_keys=True)
        tool_s = json.dumps(tool_results_json, ensure_ascii=False, sort_keys=True) if tool_results_json is not None else None

        cur = self.conn.cursor()

        # We explicitly set all timestamp columns.
        cur.execute(
            """
            INSERT INTO decision_ledger(
                request_hash, request_json, response_json, tool_results_json,
                created_at_utc, updated_at_utc, responded_at_utc
            )
            VALUES(?,?,?,?,?,?,?)
            """,
            (request_hash, req_s, resp_s, tool_s, ts, ts, ts),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def append_tool_results(self, request_hash: str, tool_results_json: Dict[str, Any]) -> int:
        """
        Update tool_results_json for the newest row with this request_hash.
        Returns rowcount.
        """
        ts = utc_now_iso()
        tool_s = json.dumps(tool_results_json, ensure_ascii=False, sort_keys=True)
        cur = self.conn.cursor()
        cur.execute(
            """
            UPDATE decision_ledger
            SET tool_results_json=?, updated_at_utc=?
            WHERE id = (
                SELECT id FROM decision_ledger
                WHERE request_hash=?
                ORDER BY id DESC
                LIMIT 1
            )
            """,
            (tool_s, ts, request_hash),
        )
        self.conn.commit()
        return int(cur.rowcount)

    def fetch_last(self, n: int = 5):
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT id, request_hash, request_json, response_json, tool_results_json,
                   created_at_utc, updated_at_utc, responded_at_utc
            FROM decision_ledger
            ORDER BY id DESC
            LIMIT ?
            """,
            (int(n),),
        )
        return cur.fetchall()

