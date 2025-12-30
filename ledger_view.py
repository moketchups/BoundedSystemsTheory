#!/usr/bin/env python3
import argparse
import json
import sqlite3
from typing import Any, Dict, Optional, Tuple


def _safe_json_loads(s: Optional[str]) -> Dict[str, Any]:
    if not s:
        return {}
    try:
        return json.loads(s)
    except Exception:
        return {"_error": "json_decode_failed", "_raw": s[:5000]}


def _one_line(s: str, limit: int = 140) -> str:
    s = (s or "").replace("\n", " ").replace("\r", " ").strip()
    if len(s) <= limit:
        return s
    return s[: limit - 3] + "..."


def _connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def _fetch_rows(conn: sqlite3.Connection, last_n: int):
    cur = conn.cursor()
    cur.execute(
        """
        SELECT request_hash, created_at_utc, responded_at_utc, request_json, response_json, tool_results_json, error_json
        FROM decision_ledger
        ORDER BY created_at_utc DESC
        LIMIT ?
        """,
        (last_n,),
    )
    return cur.fetchall()


def _extract_summary(request_obj: Dict[str, Any], response_obj: Dict[str, Any], tool_obj: Dict[str, Any]) -> Dict[str, Any]:
    state = request_obj.get("state")
    utter = request_obj.get("utterance_text", "")
    wake_detected = request_obj.get("wake_detected", False)

    decision = response_obj.get("decision", {}) or {}
    intent = decision.get("intent")
    actions = response_obj.get("actions", []) or []
    next_state = (response_obj.get("state_update", {}) or {}).get("next_state")

    # Tool results keyed by action_id
    tool_results = (tool_obj.get("results") or {}) if isinstance(tool_obj, dict) else {}

    # Make a compact action summary list
    action_summaries = []
    for a in actions:
        aid = a.get("action_id", "")
        tool = a.get("tool", "")
        args = a.get("args", {}) or {}
        arg_text = ""
        if tool == "system.say":
            arg_text = _one_line(str(args.get("text", "")), 90)
        elif tool == "tasks.add":
            arg_text = _one_line(str(args.get("text", "")), 90)
        elif tool in ("tasks.list_open", "tasks.clear_open", "system.beep", "system.time_say", "system.unknown_fallback"):
            arg_text = _one_line(json.dumps(args, ensure_ascii=False), 90) if args else ""
        else:
            arg_text = _one_line(json.dumps(args, ensure_ascii=False), 90) if args else ""

        # attach result if present
        res = tool_results.get(aid)
        res_ok = None
        res_hint = ""
        if isinstance(res, dict):
            res_ok = res.get("ok", None)
            # small helpful hints
            if tool == "tasks.add" and res_ok:
                res_hint = f"task_id={res.get('task_id')}"
            elif tool == "tasks.clear_open" and res_ok:
                res_hint = f"cleared={res.get('cleared')}"
            elif tool == "tasks.list_open" and res_ok:
                res_hint = f"count={res.get('count')}"
            elif tool == "system.unknown_fallback":
                res_hint = f"used_ollama={res.get('used_ollama')}"

        action_summaries.append(
            {
                "action_id": aid,
                "tool": tool,
                "args": arg_text,
                "ok": res_ok,
                "hint": res_hint,
            }
        )

    return {
        "state": state,
        "next_state": next_state,
        "wake_detected": wake_detected,
        "utterance": utter,
        "intent": intent,
        "actions": action_summaries,
    }


def _print_compact(row, idx: int, total: int, full: bool):
    req = _safe_json_loads(row["request_json"])
    resp = _safe_json_loads(row["response_json"])
    tool = _safe_json_loads(row["tool_results_json"])
    err = _safe_json_loads(row["error_json"])

    created = row["created_at_utc"]
    rhash = row["request_hash"]

    summ = _extract_summary(req, resp, tool)

    # Header
    print("=" * 90)
    print(f"[{total - idx}/{total}] {created}  hash={rhash[:16]}…")
    print(f"STATE: {summ['state']}  →  {summ['next_state']}")
    print(f"INTENT: {summ['intent']}   wake_detected={summ['wake_detected']}")
    print(f"UTTER: {_one_line(summ['utterance'], 120)}")

    # Actions
    if summ["actions"]:
        print("ACTIONS:")
        for a in summ["actions"]:
            ok_str = ""
            if a["ok"] is True:
                ok_str = " ✅"
            elif a["ok"] is False:
                ok_str = " ❌"
            hint = f" ({a['hint']})" if a["hint"] else ""
            argbit = f" | {a['args']}" if a["args"] else ""
            print(f"  - {a['tool']}{argbit}{ok_str}{hint}")
    else:
        print("ACTIONS: (none)")

    if err and err != {}:
        print(f"ERROR: {_one_line(json.dumps(err, ensure_ascii=False), 200)}")

    if full:
        print("\n--- REQUEST_JSON ---")
        print(json.dumps(req, indent=2, ensure_ascii=False))
        print("\n--- RESPONSE_JSON ---")
        print(json.dumps(resp, indent=2, ensure_ascii=False))
        print("\n--- TOOL_RESULTS_JSON ---")
        print(json.dumps(tool, indent=2, ensure_ascii=False))


def main():
    ap = argparse.ArgumentParser(description="View Demerzel decision_ledger entries (compact by default).")
    ap.add_argument("--db", default="demerzel_memory.db", help="Path to SQLite DB (default: demerzel_memory.db)")
    ap.add_argument("--last", type=int, default=10, help="Show last N entries (default: 10)")
    ap.add_argument("--full", action="store_true", help="Also print full JSON for each entry")
    args = ap.parse_args()

    conn = _connect(args.db)
    try:
        rows = _fetch_rows(conn, max(1, args.last))
        if not rows:
            print("No rows found in decision_ledger.")
            return

        total = len(rows)
        # rows are newest-first; print newest-first
        for idx, row in enumerate(rows):
            _print_compact(row, idx, total, full=args.full)

        print("=" * 90)
        print(f"Shown {total} entries from {args.db}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()

