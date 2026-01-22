"""
Kernel contract: shared data structures for router.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from enum import Enum, auto

class Intent(Enum):
    UNKNOWN = auto()
    PING = auto()
    LED_ON = auto()
    LED_OFF = auto()
    TIME = auto()
    SLEEP = auto()
    CANCEL = auto()
    EXECUTE_CODE = auto()
    DISCUSS = auto()  # Theoretical/philosophical queries

@dataclass
class RouterState:
    """Router state for confirmations"""
    pending_intent: Optional[Intent] = None
    pending_cmd: Optional[str] = None
    pending_code: Optional[str] = None
    confirm_stage: int = 0
    last_prompt: str = ""

@dataclass
class RouterOutput:
    """Output from router"""
    speak: str = ""
    intent: Intent = Intent.UNKNOWN
    hw_cmd: Optional[str] = None
    code_to_execute: Optional[str] = None
    did_execute: bool = False
    sleep_mode: bool = False
    error: Optional[str] = None

@dataclass
class HwResult:
    """Hardware execution result"""
    ok: bool
    out: str = ""
    err: str = ""
