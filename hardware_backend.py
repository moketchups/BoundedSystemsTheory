from __future__ import annotations

import subprocess
from typing import Any, Dict, Optional, Tuple

from tool_gate import verify_permit

# ---------------------------------------------------------------------
# HARDWARE BACKEND = actuator boundary.
# Rule: no permit -> no world-affecting execution.
# This is how we remove bypass holes.
# ---------------------------------------------------------------------

def run_hardware_tool(tool: str, args: Dict[str, Any], permit: Optional[str]) -> Tuple[bool, str]:
    """
    tool: 'led_on' | 'led_off' | etc
    args: must match tool spec (currently empty dict for led tools)
    permit: must be a valid, recent ToolGate permit for this tool+args
    """
    ok, why = verify_permit(permit or "", tool, args or {}, max_age_sec=30.0)
    if not ok:
        return False, f"[DENY] Hardware execution blocked: {why}"

    # Map tools -> executor commands.
    # Keep this minimal and explicit.
    if tool == "led_on":
        cmd = ["python3", "hardware_executor.py", "LED_ON"]
    elif tool == "led_off":
        cmd = ["python3", "hardware_executor.py", "LED_OFF"]
    else:
        return False, f"[DENY] Unknown hardware tool: {tool}"

    try:
        p = subprocess.run(cmd, capture_output=True, text=True)
        out = (p.stdout or "").strip()
        err = (p.stderr or "").strip()
        if p.returncode != 0:
            return False, f"[ERR] hardware_executor failed rc={p.returncode} stderr={err} stdout={out}"
        if not out:
            # still show stderr if any
            return False, f"[ERR] hardware_executor returned empty output. stderr={err}"
        return True, out
    except Exception as e:
        return False, f"[ERR] Exception running hardware_executor: {e}"
