"""
INTERCEPT ALL CLAUDE OUTPUTS - NO DIRECT EXECUTION
"""

from typing import List


def intercept_claude_output(raw_output: str) -> List[dict]:
    """
    Parse Claude's output into proposed actions.
    Expected format:
    STEP: 2
    ACTION: WRITE_FILE
    FILE: /path/file.py
    CONTENT:
    ```
    # code
    ```

    Returns list of action dicts for gate checking.
    STEP directive is optional - if omitted, steps are numbered sequentially from 1.
    """
    actions = []
    lines = raw_output.split('\n')
    current_step = None

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if line.startswith('STEP:'):
            current_step = int(line.split(':', 1)[1].strip())
            i += 1
            continue

        if line.startswith('ACTION:'):
            action_type = line.split(':', 1)[1].strip()
            i += 1

            params = {}
            in_content_block = False
            content_lines = []

            while i < len(lines):
                current_line = lines[i]
                stripped = current_line.strip()

                # Check for next ACTION (end of current action)
                if stripped.startswith('ACTION:'):
                    break

                # Handle content block
                if in_content_block:
                    if stripped == '```':
                        params['content'] = '\n'.join(content_lines)
                        in_content_block = False
                    else:
                        content_lines.append(current_line)
                elif stripped.startswith('FILE:'):
                    params['file_path'] = stripped.split(':', 1)[1].strip()
                elif stripped.startswith('COMMAND:'):
                    params['command'] = stripped.split(':', 1)[1].strip()
                elif stripped.startswith('CONTENT:'):
                    in_content_block = False
                    content_lines = []
                    # Check if ``` is on next line
                    if i + 1 < len(lines) and lines[i + 1].strip().startswith('```'):
                        i += 1  # Skip the opening ```
                        in_content_block = True

                i += 1

            # Handle unclosed content block
            if in_content_block and content_lines:
                params['content'] = '\n'.join(content_lines)

            actions.append({
                'type': action_type,
                'params': params,
                'step': current_step  # None if not specified
            })
            current_step = None  # Reset for next action
        else:
            i += 1

    return actions
