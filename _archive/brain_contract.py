#!/usr/bin/env python3
"""
brain_contract.py
Step 13: a strict "contract" that decides what actions are allowed.

Contract for Step 13:
- Allowed intents: time
- Everything else gets a spoken deny message (not silent)
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class ContractDecision:
    allowed: bool
    speak: Optional[str] = None
    reason: Optional[str] = None


class BrainContract:
    def __init__(self):
        # Step 13 is intentionally strict:
        self.allowed_intents = {
            "time",
        }

        self.deny_unknown = "I didn’t catch a valid command."
        self.deny_not_allowed = "That action isn’t allowed yet."

    def check(self, intent_type: str, payload: Optional[Dict[str, Any]] = None) -> ContractDecision:
        intent_type = (intent_type or "").strip().lower()

        if not intent_type or intent_type == "unknown":
            return ContractDecision(
                allowed=False,
                speak=self.deny_unknown,
                reason="intent_unknown",
            )

        if intent_type in self.allowed_intents:
            return ContractDecision(allowed=True)

        return ContractDecision(
            allowed=False,
            speak=self.deny_not_allowed,
            reason=f"intent_not_allowed:{intent_type}",
        )
