"""
action_ledger.py

Append-only, local-first audit log for Demerzel.

Design principles:
- Logging must NEVER block execution. Fail open on logging (i.e., if logging fails, do not crash routing).
- JSONL format: one JSON object per line.
- No network calls. Local filesystem only.
- Deterministic schema fields where possible.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import asdict, is_dataclass
from typing import Any, Dict, Optional


DEFAULT_LOG_DIR = "logs"
DEFAULT_LOG_FILE = "action_ledger.jsonl"


def _now_unix() -> float:
    return time.time()


def _safe_serialize(obj: Any) -> Any:
    """
    Convert objects into JSON-serializable structures safely.
    - dataclasses -> dict
    - dict/list/str/int/float/bool/None pass through
    - everything else -> repr
    """
    try:
        if is_dataclass(obj):
            return asdict(obj)
        if isinstance(obj, (dict, list, str, int, float, bool)) or obj is None:
            return obj
        return repr(obj)
    except Exception:
        return repr(obj)


def write_event(
    event: Dict[str, Any],
    log_dir: str = DEFAULT_LOG_DIR,
    log_file: str = DEFAULT_LOG_FILE,
) -> None:
    """
    Append a single event dict to the JSONL ledger.

    This function must never raise an exception to callers.
    """
    try:
        os.makedirs(log_dir, exist_ok=True)
        path = os.path.join(log_dir, log_file)

        # Add timestamp if missing
        if "ts_unix" not in event and "ts" not in event:
            event["ts_unix"] = _now_unix()

        # Serialize safely
        safe_event: Dict[str, Any] = {k: _safe_serialize(v) for k, v in event.items()}

        line = json.dumps(safe_event, separators=(",", ":"), sort_keys=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        # Never crash the system due to logging
        return


def append_event(event: Dict[str, Any]) -> None:
    """
    Compatibility wrapper.

    Some kernel_router versions call append_event(). We map that to write_event()
    so logging works without changing routing code.
    """
    write_event(event)


def make_router_event(
    *,
    raw_text: str,
    cleaned_text: str,
    mode: str,
    intent: Optional[str],
    confidence: Optional[float],
    confirm_required: Optional[bool],
    speak: str,
    effects: Any = None,
    error: Optional[str] = None,
    hw_cmd: Optional[str] = None,
    hw_result: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Helper to build a standardized router event.
    """
    return {
        "kind": "router",
        "raw_text": raw_text,
        "cleaned_text": cleaned_text,
        "mode": mode,
        "intent": intent,
        "confidence": confidence,
        "confirm_required": confirm_required,
        "speak": speak,
        "effects": effects,
        "error": error,
        "hw_cmd": hw_cmd,
        "hw_result": hw_result,
    }

