"""
Solomon Console Logger

Append-only JSONL log capturing all queries and responses.
Designed for later retrieval by human or Daneel.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class ConsoleLogger:
    """
    Append-only logger for Admin Console operations.

    Log format: JSONL (one JSON object per line)
    Location: logs/admin_console/YYYY-MM-DD.jsonl
    """

    def __init__(self, log_dir: Optional[Path] = None):
        if log_dir is None:
            # Default to project logs directory
            self.log_dir = Path(__file__).parent.parent.parent / "logs" / "admin_console"
        else:
            self.log_dir = Path(log_dir)

        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.session_id = str(uuid.uuid4())

    def _get_log_file(self) -> Path:
        """Get today's log file path."""
        today = datetime.now().strftime("%Y-%m-%d")
        return self.log_dir / f"{today}.jsonl"

    def log(
        self,
        query: Dict[str, Any],
        subsystems_invoked: List[str],
        responses: Dict[str, Any],
        three_six_nine: Dict[str, Any],
        synthesis: str
    ) -> str:
        """
        Log a complete query-response cycle.

        Returns:
            The entry ID for reference
        """
        entry_id = str(uuid.uuid4())[:8]

        entry = {
            "id": entry_id,
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "query": query,
            "subsystems_invoked": subsystems_invoked,
            "responses": responses,
            "three_six_nine": three_six_nine,
            "synthesis": synthesis
        }

        log_file = self._get_log_file()
        with open(log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

        return entry_id

    def read_today(self) -> List[Dict[str, Any]]:
        """Read all entries from today's log."""
        return self.read_date(datetime.now().strftime("%Y-%m-%d"))

    def read_date(self, date: str) -> List[Dict[str, Any]]:
        """Read all entries from a specific date (YYYY-MM-DD format)."""
        log_file = self.log_dir / f"{date}.jsonl"
        if not log_file.exists():
            return []

        entries = []
        with open(log_file, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    entries.append(json.loads(line))
        return entries

    def search(
        self,
        date: Optional[str] = None,
        subsystem: Optional[str] = None,
        domain: Optional[str] = None,
        text: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search log entries with filters.

        Args:
            date: Specific date (YYYY-MM-DD) or None for all
            subsystem: Filter by subsystem invoked
            domain: Filter by 3-6-9 domain (material/flux/unity)
            text: Search in query text or synthesis
        """
        # Get entries to search
        if date:
            entries = self.read_date(date)
        else:
            # Read all log files
            entries = []
            for log_file in sorted(self.log_dir.glob("*.jsonl")):
                with open(log_file, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            entries.append(json.loads(line))

        # Apply filters
        results = []
        for entry in entries:
            # Subsystem filter
            if subsystem and subsystem not in entry.get("subsystems_invoked", []):
                continue

            # Domain filter
            if domain:
                entry_domain = entry.get("three_six_nine", {}).get("domain")
                if entry_domain != domain:
                    continue

            # Text search
            if text:
                text_lower = text.lower()
                query_text = str(entry.get("query", "")).lower()
                synthesis = entry.get("synthesis", "").lower()
                if text_lower not in query_text and text_lower not in synthesis:
                    continue

            results.append(entry)

        return results

    def get_session_entries(self) -> List[Dict[str, Any]]:
        """Get all entries from current session."""
        today_entries = self.read_today()
        return [e for e in today_entries if e.get("session_id") == self.session_id]

    def export_session(self, output_path: Optional[Path] = None) -> Path:
        """Export current session to a standalone JSON file."""
        entries = self.get_session_entries()

        if output_path is None:
            output_path = self.log_dir / f"session_{self.session_id[:8]}.json"

        with open(output_path, "w") as f:
            json.dump({
                "session_id": self.session_id,
                "exported_at": datetime.now().isoformat(),
                "entries": entries
            }, f, indent=2)

        return output_path
