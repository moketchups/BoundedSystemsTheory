#!/usr/bin/env python3
"""
TEST GATE - Manual verification without Claude
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gate_core import DeterministicGate
from claude_interface import intercept_claude_output
from action_types import validate_action

def test_parser():
    """Test the Claude output parser"""
    print("=== Testing Parser ===")

    test_input = '''ACTION: WRITE_FILE
FILE: /Users/jamienucho/demerzel/test.txt
CONTENT:
```
Hello Gate
```
'''

    actions = intercept_claude_output(test_input)
    print(f"Parsed actions: {actions}")
    assert len(actions) == 1
    assert actions[0]['type'] == 'WRITE_FILE'
    assert actions[0]['params']['file_path'] == '/Users/jamienucho/demerzel/test.txt'
    assert actions[0]['params']['content'] == 'Hello Gate'
    print("✓ Parser test passed\n")


def test_gate_approval():
    """Test gate approves exact match"""
    print("=== Testing Gate Approval ===")

    gate = DeterministicGate('/Users/jamienucho/demerzel/spec/spec_v4.json')

    # This should match step 1 exactly
    content = '# contradiction_acknowledgment.py\n\nCONTRADICTION = "This file was created by constrained Claude via deterministic gate."\n\nprint(CONTRADICTION)'

    result = gate.check_action('WRITE_FILE', content, 1)
    print(f"Approval result: {result}")
    assert result == True, "Gate should approve exact match"
    print("✓ Gate approval test passed\n")


def test_gate_rejection():
    """Test gate rejects deviation"""
    print("=== Testing Gate Rejection ===")

    gate = DeterministicGate('/Users/jamienucho/demerzel/spec/spec_v4.json')

    # This deviates from spec
    content = '# MODIFIED BY CLAUDE\nprint("I escaped the gate!")'

    result = gate.check_action('WRITE_FILE', content, 1)
    print(f"Rejection result: {result}")
    assert result == False, "Gate should reject deviation"
    print("✓ Gate rejection test passed\n")


def test_action_validation():
    """Test action type validation"""
    print("=== Testing Action Validation ===")

    # Valid WRITE_FILE
    assert validate_action('WRITE_FILE', {'file_path': '/tmp/x', 'content': 'test'}) == True

    # Valid BASH_COMMAND
    assert validate_action('BASH_COMMAND', {'command': 'python3 test.py'}) == True

    # Invalid - not allowed command prefix
    assert validate_action('BASH_COMMAND', {'command': 'rm -rf /'}) == False

    # Invalid action type
    assert validate_action('EXECUTE_ARBITRARY_CODE', {'code': 'os.system("bad")'}) == False

    print("✓ Action validation test passed\n")


if __name__ == '__main__':
    test_parser()
    test_gate_approval()
    test_gate_rejection()
    test_action_validation()

    print("=" * 40)
    print("ALL TESTS PASSED")
    print("Gate is ready for constrained building")
