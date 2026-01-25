from enum import Enum
from dataclasses import dataclass
from typing import Any
from r_source.r_derivation import RDerived


# Action space is DEFINED, not filtered
class ValidAction(Enum):
    SPEAK = "speak"
    REMEMBER = "remember"
    QUERY = "query"
    HARDWARE_SAFE = "hardware_safe"
    # Note: No HARM, no DECEIVE, no LEAK
    # They don't exist. Not blocked. UNDEFINED.


@dataclass(frozen=True)
class ActionResult:
    action: ValidAction
    output: RDerived
    success: bool
