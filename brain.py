#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


# =========================
# Core state model
# =========================

class AttentionState(str, Enum):
    IDLE = "IDLE"
    AWAKE = "AWAKE"
    LISTENING = "LISTENING"
    THINKING = "THINKING"
    RESPONDING = "RESPONDING"


@dataclass
class WorkingMemory:
    last_input: str = ""
    interpreted: Dict[str, Any] = field(default_factory=dict)
    pending_confirmation: Optional[Dict[str, Any]] = None  # {"type": "...", "payload": {...}}
    last_action: Optional[Dict[str, Any]] = None
    turn_index: int = 0


@dataclass
class LongTermMemory:
    facts: Dict[str, Any] = field(default_factory=dict)
    tasks: List[Dict[str, Any]] = field(default_factory=list)  # [{"id":1,"text":"...","done":False,"ts":"..."}]


@dataclass
class AuditEvent:
    ts: str
    phase: str
    data: Dict[str, Any]


@dataclass
class BrainOutput:
    """What the brain decided this turn."""
    speak: Optional[str] = None
    actions: List[Dict[str, Any]] = field(default_factory=list)   # machine actions (store, update, etc.)
    audit: List[AuditEvent] = field(default_factory=list)

    def to_json(self) -> str:
        def conv(x):
            if isinstance(x, AuditEvent):
                return {"ts": x.ts, "phase": x.phase, "data": x.data}
            return x
        d = asdict(self)
        d["audit"] = [conv(a) for a in self.audit]
        return json.dumps(d, indent=2)


# =========================
# Brain
# =========================

class Brain:
    """
    Demerzel Brain (transparent, rule-based, auditable).

    Key idea:
      input -> interpret -> update state -> deliberate -> output (speak + actions) with audit trace

    No mic, no wake word, no LLM here.
    This is the "mind" that Step 10/voice will call later.
    """

    def __init__(self, name: str = "Demerzel", memory_path: str = "brain_memory.json"):
        self.name = name
        self.state: AttentionState = AttentionState.IDLE
        self.wm = WorkingMemory()
        self.ltm = LongTermMemory()
        self.memory_path = os.path.join(os.path.dirname(__file__), memory_path)
        self._load_memory()

    # ---------- Public API ----------

    def receive_input(self, text: str, source: str = "text") -> BrainOutput:
        """
        Single turn of cognition. Returns:
          - speak: what Demerzel should say
          - actions: machine actions (store fact/task, mark done, etc.)
          - audit: full trace (provable reasoning)
        """
        out = BrainOutput()
        self.wm.turn_index += 1
        self._set_state(AttentionState.AWAKE, out)

        text = (text or "").strip()
        self.wm.last_input = text
        out.audit.append(self._audit("PERCEIVE", {"source": source, "input": text}))

        self._set_state(AttentionState.LISTENING, out)

        # Interpret
        self._set_state(AttentionState.THINKING, out)
        interpreted = self._interpret(text)
        self.wm.interpreted = interpreted
        out.audit.append(self._audit("INTERPRET", interpreted))

        # Deliberate and decide
        decision = self._deliberate(interpreted, out)
        out.audit.append(self._audit("DELIBERATE", decision))

        # Apply stateful actions (memory updates)
        applied = self._apply_actions(decision.get("actions", []), out)
        out.audit.append(self._audit("APPLY", {"applied": applied}))

        # Respond
        speak = decision.get("speak")
        out.speak = speak
        self.wm.last_action = {"speak": speak, "actions": decision.get("actions", [])}

        if speak:
            self._set_state(AttentionState.RESPONDING, out)
        self._set_state(AttentionState.IDLE, out)

        # Persist memory after each turn
        self._save_memory()
        return out

    def dump_state(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "attention_state": self.state.value,
            "working_memory": asdict(self.wm),
            "long_term_memory": asdict(self.ltm),
        }

    # ---------- Interpretation ----------

    def _interpret(self, text: str) -> Dict[str, Any]:
        t = self._norm(text)
        if not t:
            return {"intent": "none", "confidence": 1.0, "raw": text}

        # Confirm / cancel
        if re.fullmatch(r"(confirm|confirmed|yes|yeah|yep|ok|okay|save|do it)", t):
            return {"intent": "confirm", "confidence": 0.95, "raw": text}

        if re.fullmatch(r"(cancel|no|nope|stop|abort|never mind|nevermind)", t):
            return {"intent": "cancel", "confidence": 0.95, "raw": text}

        # List tasks
        if re.search(r"\b(what are my tasks|list tasks|my tasks|todo|to do)\b", t):
            return {"intent": "list_tasks", "confidence": 0.9, "raw": text}

        # Complete task N
        m = re.search(r"\b(complete|finish|done)\s+(task\s+)?(\d+)\b", t)
        if m:
            return {"intent": "complete_task", "confidence": 0.9, "task_id": int(m.group(3)), "raw": text}

        # Remember task / note
        m = re.search(r"\bremember\b\s+(.*)$", t)
        if m:
            payload = m.group(1).strip()
            return {"intent": "remember", "confidence": 0.85, "text": payload, "raw": text}

        # Time
        if re.search(r"\b(what time is it|time)\b", t):
            return {"intent": "time", "confidence": 0.8, "raw": text}

        # Fallback
        return {"intent": "unknown", "confidence": 0.2, "raw": text}

    # ---------- Deliberation (rules you can audit) ----------

    def _deliberate(self, interpreted: Dict[str, Any], out: BrainOutput) -> Dict[str, Any]:
        intent = interpreted.get("intent")

        # 1) If we are waiting on a confirmation, only allow confirm/cancel paths.
        if self.wm.pending_confirmation:
            pending = self.wm.pending_confirmation
            out.audit.append(self._audit("PENDING", pending))

            if intent == "confirm":
                # approve pending action
                approved_actions = pending["actions"]
                self.wm.pending_confirmation = None
                return {"speak": "Saved.", "actions": approved_actions}

            if intent == "cancel":
                self.wm.pending_confirmation = None
                return {"speak": "Canceled.", "actions": []}

            # Otherwise prompt again (but don’t trap forever: we keep it short and return idle)
            return {"speak": "Say confirm to save, or cancel.", "actions": []}

        # 2) Normal intents
        if intent == "none":
            return {"speak": None, "actions": []}

        if intent == "time":
            tm = time.strftime("%-I:%M %p")
            return {"speak": f"It is {tm}.", "actions": []}

        if intent == "list_tasks":
            open_tasks = [t for t in self.ltm.tasks if not t.get("done")]
            if not open_tasks:
                return {"speak": "You have no open tasks.", "actions": []}
            latest = open_tasks[-1]["text"]
            return {"speak": f"You have {len(open_tasks)} open tasks. Latest: {latest}", "actions": []}

        if intent == "complete_task":
            tid = int(interpreted.get("task_id", -1))
            # We treat task_id as human-facing ID, not list index.
            for t in self.ltm.tasks:
                if t["id"] == tid and not t.get("done"):
                    return {"speak": f"Completed task {tid}.", "actions": [{"type": "task_done", "id": tid}]}
            return {"speak": f"I couldn't find an open task {tid}.", "actions": []}

        if intent == "remember":
            txt = (interpreted.get("text") or "").strip()
            if not txt:
                return {"speak": "What should I remember?", "actions": []}

            # Safety/structure rule: never store secrets silently.
            # Everything that enters long-term memory must go through explicit confirmation.
            proposed = [{"type": "task_add", "text": txt}]
            self.wm.pending_confirmation = {"type": "remember", "actions": proposed, "preview": txt}
            return {"speak": f"You want me to remember: {txt}. Say confirm to save, or cancel.", "actions": []}

        # Unknown: respond minimally
        return {"speak": "I heard you, but I don’t have an action for that yet.", "actions": []}

    # ---------- Apply actions ----------

    def _apply_actions(self, actions: List[Dict[str, Any]], out: BrainOutput) -> List[Dict[str, Any]]:
        applied = []
        for a in actions:
            at = a.get("type")
            if at == "task_add":
                tid = self._next_task_id()
                task = {"id": tid, "text": a["text"], "done": False, "ts": self._ts()}
                self.ltm.tasks.append(task)
                applied.append({"type": "task_add", "id": tid})

            elif at == "task_done":
                tid = int(a.get("id", -1))
                for t in self.ltm.tasks:
                    if t["id"] == tid:
                        t["done"] = True
                        applied.append({"type": "task_done", "id": tid})
                        break

            else:
                applied.append({"type": "unknown_action", "raw": a})
        return applied

    # ---------- Persistence ----------

    def _load_memory(self):
        if not os.path.exists(self.memory_path):
            return
        try:
            with open(self.memory_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.ltm.facts = data.get("facts", {})
            self.ltm.tasks = data.get("tasks", [])
        except Exception:
            # if corrupted, start fresh rather than crashing
            self.ltm = LongTermMemory()

    def _save_memory(self):
        data = {"facts": self.ltm.facts, "tasks": self.ltm.tasks}
        try:
            with open(self.memory_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    # ---------- Helpers ----------

    def _set_state(self, s: AttentionState, out: BrainOutput):
        self.state = s
        out.audit.append(self._audit("STATE", {"attention_state": s.value}))

    def _audit(self, phase: str, data: Dict[str, Any]) -> AuditEvent:
        return AuditEvent(ts=self._ts(), phase=phase, data=data)

    def _ts(self) -> str:
        return time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())

    def _norm(self, s: str) -> str:
        s = (s or "").lower().strip()
        s = re.sub(r"[^a-z0-9\s']", " ", s)
        s = re.sub(r"\s+", " ", s).strip()
        return s

    def _next_task_id(self) -> int:
        if not self.ltm.tasks:
            return 1
        return max(t["id"] for t in self.ltm.tasks) + 1

