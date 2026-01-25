from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
import time
from typing import Optional, Dict, Any

class IntentStatus(str, Enum):
    EMPTY = "EMPTY"
    PENDING = "PENDING"        # accumulating evidence
    COMMITTED = "COMMITTED"    # frozen decision
    EXECUTING = "EXECUTING"
    DONE = "DONE"
    CANCELED = "CANCELED"
    EXPIRED = "EXPIRED"

@dataclass
class Intent:
    intent_id: str
    intent_type: str
    raw_text: str
    confidence: float
    requires_confirm: bool
    created_at: float
    committed_at: Optional[float] = None
    status: IntentStatus = IntentStatus.PENDING
    meta: Optional[Dict[str, Any]] = None

class IntentLedger:
    """
    Single source of truth: ONLY committed intents may execute.
    Prevents 'jumping tracks' by freezing a decision until resolved.
    """
    def __init__(self, stability_hits_required: int = 2, stability_window_s: float = 2.0, intent_ttl_s: float = 8.0):
        self.stability_hits_required = stability_hits_required
        self.stability_window_s = stability_window_s
        self.intent_ttl_s = intent_ttl_s

        self._active: Optional[Intent] = None
        self._last_candidate_type: Optional[str] = None
        self._last_candidate_t: float = 0.0
        self._hits: int = 0

    def active(self) -> Optional[Intent]:
        self._expire_if_needed()
        return self._active

    def reset(self) -> None:
        self._active = None
        self._last_candidate_type = None
        self._last_candidate_t = 0.0
        self._hits = 0

    def _expire_if_needed(self) -> None:
        if not self._active:
            return
        if self._active.status in (IntentStatus.DONE, IntentStatus.CANCELED, IntentStatus.EXPIRED):
            return
        now = time.time()
        if self._active.committed_at and (now - self._active.committed_at) > self.intent_ttl_s:
            self._active.status = IntentStatus.EXPIRED

    def cancel(self, reason: str = "") -> None:
        if self._active and self._active.status not in (IntentStatus.DONE, IntentStatus.EXPIRED):
            self._active.status = IntentStatus.CANCELED
            self._active.meta = (self._active.meta or {})
            self._active.meta["cancel_reason"] = reason

    def mark_executing(self) -> None:
        if self._active and self._active.status == IntentStatus.COMMITTED:
            self._active.status = IntentStatus.EXECUTING

    def mark_done(self) -> None:
        if self._active and self._active.status in (IntentStatus.EXECUTING, IntentStatus.COMMITTED):
            self._active.status = IntentStatus.DONE

    def observe_candidate(self, intent_type: str, raw_text: str, confidence: float, requires_confirm: bool, meta: Optional[dict] = None) -> Optional[Intent]:
        """
        Feed routed 'candidates' here. This function decides whether to commit.
        Commitment rule: require N consistent hits within a time window.
        """
        now = time.time()
        # If we already have a committed/executing intent, do not allow new ones
        self._expire_if_needed()
        if self._active and self._active.status in (IntentStatus.COMMITTED, IntentStatus.EXECUTING):
            return self._active

        # Reset hit counter if candidate changed or window expired
        if self._last_candidate_type != intent_type or (now - self._last_candidate_t) > self.stability_window_s:
            self._hits = 0
            self._last_candidate_type = intent_type

        self._last_candidate_t = now
        self._hits += 1

        if self._hits >= self.stability_hits_required:
            self._active = Intent(
                intent_id=f"intent_{int(now*1000)}",
                intent_type=intent_type,
                raw_text=raw_text,
                confidence=float(confidence),
                requires_confirm=bool(requires_confirm),
                created_at=now,
                committed_at=now,
                status=IntentStatus.COMMITTED,
                meta=meta or {},
            )
            return self._active

        # Not committed yet
        self._active = Intent(
            intent_id=f"pending_{int(now*1000)}",
            intent_type=intent_type,
            raw_text=raw_text,
            confidence=float(confidence),
            requires_confirm=bool(requires_confirm),
            created_at=now,
            committed_at=None,
            status=IntentStatus.PENDING,
            meta=meta or {},
        )
        return self._active

    def can_execute(self) -> bool:
        self._expire_if_needed()
        return bool(self._active and self._active.status == IntentStatus.COMMITTED)

    def requires_confirm(self) -> bool:
        return bool(self._active and self._active.requires_confirm)

    def matches_confirm(self, text: str) -> bool:
        t = (text or "").strip().lower()
        return t in ("yes","y","confirm","confirmed","do it","ok","okay","yeah","sure")

    def matches_cancel(self, text: str) -> bool:
        t = (text or "").strip().lower()
        return t in ("no","n","cancel","stop","never mind","nevermind","abort")
