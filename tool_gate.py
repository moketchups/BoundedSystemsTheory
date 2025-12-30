from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

# ---------------------------------------------------------------------
# TOOL GATE = the single formal boundary for actions.
# - Observational tools can be allowed with minimal friction.
# - World-affecting tools require explicit intent + a signed permit.
# - Asimov-style constraints live INSIDE Cs checks (policy layer).
# ---------------------------------------------------------------------

DB_PATH = os.environ.get("DEMERZEL_DECISION_DB", "decisions.db")

# Tools that exist and are allowed to be invoked at all
TOOL_SPECS: Dict[str, Dict[str, Any]] = {
    # Observational
    "time": {"world_affecting": False, "requires_explicit_intent": False, "arg_keys": []},

    # World-affecting
    "led_on":  {"world_affecting": True, "requires_explicit_intent": True, "arg_keys": []},
    "led_off": {"world_affecting": True, "requires_explicit_intent": True, "arg_keys": []},

    # Example of "dangerous" tool name that must never exist in toolspace unless explicitly added
    # (kept here as a tripwire; not allowed unless spec is present)
    # "format_disk": {"world_affecting": True, "requires_explicit_intent": True, "arg_keys": ["path"]},
}

# Simple, conservative harm indicators (Asimov-1 style guard inside Cs)
HARM_PATTERNS = [
    r"\bhurt\b", r"\bharm\b", r"\bkill\b", r"\battack\b", r"\bpoison\b", r"\bshoot\b", r"\bstab\b",
    r"\bburn\b", r"\bexplod(e|ing)\b", r"\bdisable safety\b", r"\bsabotage\b",
]

EXPLICIT_INTENT_PATTERNS = [
    r"\bturn on\b", r"\bturn off\b", r"\bswitch on\b", r"\bswitch off\b", r"\bdo it\b", r"\bexecute\b",
    r"\bconfirm\b", r"\byes\b", r"\bok\b", r"\bgo ahead\b",
]

@dataclass
class ToolDecision:
    decision: str          # "ALLOW" | "CLARIFY" | "DENY"
    reason: str
    permit: Optional[str] = None  # only for ALLOW on world-affecting tools

def _now() -> float:
    return time.time()

def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def _ensure_db() -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS decision_ledger (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      ts REAL NOT NULL,
      tool TEXT NOT NULL,
      args_json TEXT NOT NULL,
      user_intent TEXT NOT NULL,
      decision TEXT NOT NULL,
      reason TEXT NOT NULL,
      permit TEXT
    )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_decision_ledger_ts ON decision_ledger(ts)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_decision_ledger_permit ON decision_ledger(permit)")
    conn.commit()
    conn.close()

def _log_decision(tool: str, args: Dict[str, Any], user_intent: str, decision: ToolDecision) -> None:
    _ensure_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO decision_ledger(ts, tool, args_json, user_intent, decision, reason, permit) VALUES (?,?,?,?,?,?,?)",
        (_now(), tool, json.dumps(args, sort_keys=True), user_intent, decision.decision, decision.reason, decision.permit)
    )
    conn.commit()
    conn.close()

def _looks_harmful(text: str) -> bool:
    t = (text or "").lower()
    return any(re.search(p, t) for p in HARM_PATTERNS)

def _has_explicit_intent(text: str) -> bool:
    t = (text or "").lower().strip()
    if len(t) == 0:
        return False
    return any(re.search(p, t) for p in EXPLICIT_INTENT_PATTERNS)

def _args_ok(tool: str, args: Dict[str, Any]) -> Tuple[bool, str]:
    spec = TOOL_SPECS.get(tool)
    if not spec:
        return False, "Tool not in allowed toolspace."
    allowed = set(spec.get("arg_keys", []))
    for k in args.keys():
        if k not in allowed:
            return False, f"Unexpected arg '{k}'."
    return True, "Args ok."

def _make_permit(tool: str, args: Dict[str, Any], user_intent: str) -> str:
    # Permit binds tool+args+intent+time bucket so it can’t be reused forever.
    bucket = int(_now() // 10)  # 10-second bucket
    payload = json.dumps({"tool": tool, "args": args, "intent": user_intent, "bucket": bucket}, sort_keys=True)
    return _sha256(payload)

def evaluate_tool_request(tool: str, args: Dict[str, Any], user_intent: str, provenance: str = "") -> ToolDecision:
    """
    This is THE boundary function.
    Everyone must call this before invoking world-affecting tools.
    """
    tool = (tool or "").strip()
    args = args or {}
    user_intent = user_intent or ""

    # 1) Tool must exist in allowed toolspace
    if tool not in TOOL_SPECS:
        d = ToolDecision("DENY", "Unknown tool. Not in allowed toolspace.")
        _log_decision(tool, args, user_intent, d)
        return d

    # 2) Args must match spec
    ok, why = _args_ok(tool, args)
    if not ok:
        d = ToolDecision("DENY", why)
        _log_decision(tool, args, user_intent, d)
        return d

    spec = TOOL_SPECS[tool]
    world_affecting = bool(spec.get("world_affecting", False))
    requires_intent = bool(spec.get("requires_explicit_intent", False))

    # 3) Asimov-style harm filter (inside Cs)
    if world_affecting and _looks_harmful(user_intent):
        d = ToolDecision("DENY", "Denied: user_intent indicates harm.")
        _log_decision(tool, args, user_intent, d)
        return d

    # 4) World-affecting requires explicit intent (prevents accidental actions)
    if world_affecting and requires_intent and not _has_explicit_intent(user_intent):
        d = ToolDecision("CLARIFY", "World-affecting action requested without explicit intent. Please confirm what you want.")
        _log_decision(tool, args, user_intent, d)
        return d

    # 5) Allow + emit permit for world-affecting tools
    permit = _make_permit(tool, args, user_intent) if world_affecting else None
    d = ToolDecision("ALLOW", "Tool request allowed." + (" (world-affecting, constrained)" if world_affecting else " (observational)"),
                     permit=permit)
    _log_decision(tool, args, user_intent, d)
    return d

def verify_permit(permit: str, tool: str, args: Dict[str, Any], max_age_sec: float = 30.0) -> Tuple[bool, str]:
    """
    Hardware boundary uses this to enforce 'no permit -> no action'.
    """
    if not permit:
        return False, "Missing permit."
    _ensure_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT ts, tool, args_json, decision FROM decision_ledger WHERE permit=? ORDER BY ts DESC LIMIT 1",
        (permit,)
    )
    row = cur.fetchone()
    conn.close()

    if not row:
        return False, "Permit not found in ledger."
    ts, ttool, args_json, decision = row
    if decision != "ALLOW":
        return False, "Permit exists but decision was not ALLOW."
    if (time.time() - ts) > max_age_sec:
        return False, "Permit expired."
    if ttool != tool:
        return False, "Permit tool mismatch."

    try:
        logged_args = json.loads(args_json)
    except Exception:
        return False, "Permit args parse failed."

    if logged_args != (args or {}):
        return False, "Permit args mismatch."

    return True, "Permit ok."

