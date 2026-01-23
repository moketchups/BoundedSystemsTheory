"""
r_provenance_logger.py - R->C->I Provenance Logging

R -> C -> I Architecture:
Logs complete R->C->I provenance for each response.
Audit trail proving every output derives from R.
"""

import json
import os
from datetime import datetime
from typing import Optional
from r_derivation_tracker import RDerived
from r_coherence_checker import CoherenceResult


class RProvenanceLogger:
    """Logs complete R->C->I provenance for each response."""

    def __init__(self, log_dir: str = "logs/r_provenance"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        self._last_entry: Optional[dict] = None

    def log_response_provenance(
        self,
        user_query: str,
        context: Optional[RDerived],
        classification: Optional[RDerived],
        response: Optional[RDerived],
        coherence_result: CoherenceResult,
        final_output: str
    ):
        """Store full R->C->I trace for this response."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'user_query': user_query,
            'context': self._derivation_to_dict(context) if context else None,
            'classification': self._derivation_to_dict(classification) if classification else None,
            'response': self._derivation_to_dict(response) if response else None,
            'coherence_result': {
                'coherent': coherence_result.coherent,
                'violations': coherence_result.violations,
                'recommendation': coherence_result.recommendation,
            },
            'final_output': final_output,
        }

        self._last_entry = entry

        # Write to log file
        log_file = os.path.join(self.log_dir, f"provenance_{datetime.now().strftime('%Y%m%d')}.jsonl")
        with open(log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')

    def get_last_provenance(self) -> Optional[dict]:
        """Retrieve last logged provenance."""
        if self._last_entry:
            return self._last_entry
        # Try reading from most recent log file
        try:
            files = sorted(
                [f for f in os.listdir(self.log_dir) if f.startswith('provenance_')],
                reverse=True
            )
            if files:
                log_file = os.path.join(self.log_dir, files[0])
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    if lines:
                        return json.loads(lines[-1])
        except (OSError, json.JSONDecodeError):
            pass
        return None

    def verify_log_integrity(self) -> bool:
        """Check all logged entries have valid R-derivation chains."""
        try:
            for filename in os.listdir(self.log_dir):
                if not filename.startswith('provenance_'):
                    continue
                filepath = os.path.join(self.log_dir, filename)
                with open(filepath, 'r') as f:
                    for line in f:
                        entry = json.loads(line)
                        # Every entry must have coherence_result
                        if 'coherence_result' not in entry:
                            return False
                        # At least classification or response must have derivation
                        if entry.get('classification') is None and entry.get('response') is None:
                            return False
        except (OSError, json.JSONDecodeError):
            return False
        return True

    def _derivation_to_dict(self, r_derived: RDerived) -> dict:
        """Convert RDerived to serializable dict."""
        return {
            'value': str(r_derived.value)[:200],
            'axiom': r_derived.derivation.axiom,
            'source_doc': r_derived.derivation.source_doc,
            'derivation_path': r_derived.derivation.derivation_path,
            'verified': r_derived.verified,
        }
