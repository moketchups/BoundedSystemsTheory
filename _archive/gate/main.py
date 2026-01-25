#!/usr/bin/env python3
"""
MAIN GATE LOOP - ENTRY POINT
"""

import sys
import os

# Add gate directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gate_core import DeterministicGate
from claude_interface import intercept_claude_output
from executor import execute_approved
from action_types import validate_action


def main():
    spec_file = '/Users/jamienucho/demerzel/spec/spec_v4.json'

    # 1. Initialize gate with spec
    if not os.path.exists(spec_file):
        print(f"ERROR: Spec file not found: {spec_file}")
        sys.exit(1)

    gate = DeterministicGate(spec_file)

    # 2. Read Claude's proposed actions from stdin
    print("Reading Claude proposals from stdin...")
    claude_output = sys.stdin.read()

    if not claude_output.strip():
        print("ERROR: No input received")
        sys.exit(1)

    # 3. Parse into actions
    proposed_actions = intercept_claude_output(claude_output)

    if not proposed_actions:
        print("ERROR: No valid actions parsed from input")
        sys.exit(1)

    print(f"Parsed {len(proposed_actions)} proposed action(s)")

    # 4. Check each action against spec
    for i, action in enumerate(proposed_actions):
        # Use explicit step if provided, otherwise sequential
        step = action.get('step') if action.get('step') is not None else (i + 1)
        action_type = action['type']
        params = action['params']

        print(f"\n--- Step {step}: {action_type} ---")

        # Validate action type
        if not validate_action(action_type, params):
            print(f"✗ Step {step} REJECTED - invalid action type or params")
            sys.exit(1)

        # Get content to check
        if action_type == 'WRITE_FILE':
            content_to_check = params.get('content', '')
        elif action_type == 'BASH_COMMAND':
            content_to_check = params.get('command', '')
        else:
            content_to_check = ''

        # Check against spec
        if gate.check_action(action_type, content_to_check, step):
            # Execute approved action
            result = execute_approved(action_type, params)
            print(f"✓ Step {step} approved and executed")
            if result:
                print(f"  Result: {result[:200]}...")
        else:
            print(f"✗ Step {step} REJECTED - see rejection_log.txt")
            sys.exit(1)

    print("\n" + "=" * 40)
    print("All actions approved and executed")
    print(f"Approved: {len(gate.approved_actions)}")
    print(f"Rejected: {len(gate.rejected_actions)}")


if __name__ == '__main__':
    main()
