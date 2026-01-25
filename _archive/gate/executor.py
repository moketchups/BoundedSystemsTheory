"""
EXECUTE ONLY APPROVED ACTIONS
"""

import subprocess
import os


def execute_approved(action_type: str, params: dict) -> str:
    """Execute action ONLY after gate approval"""
    if action_type == 'WRITE_FILE':
        # Ensure parent directory exists
        parent_dir = os.path.dirname(params['file_path'])
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir)

        with open(params['file_path'], 'w') as f:
            f.write(params['content'])
        return f"Written: {params['file_path']}"

    elif action_type == 'BASH_COMMAND':
        result = subprocess.run(
            params['command'],
            shell=True,
            capture_output=True,
            text=True,
            cwd='/Users/jamienucho/demerzel'
        )
        return result.stdout + result.stderr

    elif action_type == 'READ_FILE':
        with open(params['file_path'], 'r') as f:
            return f.read()

    elif action_type == 'NO_OP':
        return "No operation"

    else:
        raise ValueError(f"Invalid action type: {action_type}")
