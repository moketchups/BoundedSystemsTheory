"""
DEFINE ALLOWED ACTION TYPES - EXHAUSTIVE LIST
"""

import os

ALLOWED_ACTIONS = {
    'WRITE_FILE': {
        'params': ['file_path', 'content'],
        'validation': lambda p: isinstance(p.get('content'), str)
    },
    'BASH_COMMAND': {
        'params': ['command'],
        'validation': lambda p: (
            p.get('command', '').startswith('cd ') or
            p.get('command', '').startswith('python3 ') or
            p.get('command', '').startswith('echo ')
        )
    },
    'READ_FILE': {
        'params': ['file_path'],
        'validation': lambda p: os.path.exists(p.get('file_path', ''))
    },
    'NO_OP': {
        'params': [],
        'validation': lambda p: True
    }
}

# NO OTHER ACTIONS ALLOWED


def validate_action(action_type: str, params: dict) -> bool:
    """Validate action against allowed types"""
    if action_type not in ALLOWED_ACTIONS:
        return False

    action_def = ALLOWED_ACTIONS[action_type]

    # Check required params present
    for param in action_def['params']:
        if param not in params:
            return False

    # Run validation function
    return action_def['validation'](params)
