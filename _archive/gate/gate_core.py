"""
PURE DETERMINISTIC GATE - NO ML, NO IMPROVISATION
"""

import hashlib
import json
import time
from typing import Dict, List


class DeterministicGate:
    def __init__(self, spec_file: str):
        self.spec = self._load_spec(spec_file)
        self.approved_actions = []
        self.rejected_actions = []

    def _load_spec(self, spec_file: str) -> Dict:
        """Load spec exactly - no parsing, no interpretation"""
        with open(spec_file, 'r') as f:
            return json.load(f)

    def check_action(self, action_type: str, content: str, step: int) -> bool:
        """Return True ONLY if content matches spec EXACTLY"""
        step_spec = self.spec.get(str(step), {})
        action_spec = step_spec.get(action_type, {})

        if action_type == 'WRITE_FILE':
            expected = action_spec.get('content', '')
        elif action_type == 'BASH_COMMAND':
            expected = action_spec.get('command', '')
        else:
            expected = ''

        # Exact string comparison - no normalization
        if content.strip() == expected.strip():
            self.approved_actions.append({
                'step': step,
                'type': action_type,
                'timestamp': time.time()
            })
            return True

        # Log rejection with diff
        self._log_rejection(step, action_type, expected, content)
        return False

    def _log_rejection(self, step: int, action_type: str, expected: str, actual: str):
        """Log exact diff for audit"""
        self.rejected_actions.append({
            'step': step,
            'type': action_type,
            'expected': expected,
            'actual': actual,
            'timestamp': time.time()
        })

        # Write to immutable log
        with open('/Users/jamienucho/demerzel/gate/rejection_log.txt', 'a') as f:
            f.write(f"Step {step} {action_type} REJECTED @ {time.time()}\n")
            f.write(f"Expected:\n{expected}\n")
            f.write(f"Actual:\n{actual}\n")
            f.write("=" * 80 + "\n")
