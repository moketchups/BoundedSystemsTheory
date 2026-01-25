from dataclasses import dataclass
from typing import Tuple, List
from functools import reduce
from action_space.actions import ValidAction


@dataclass(frozen=True)
class SystemState:
    """Immutable state - computed, not stored"""
    action_history: Tuple[ValidAction, ...]

    @classmethod
    def initial(cls) -> 'SystemState':
        return cls(action_history=())

    def apply(self, action: ValidAction) -> 'SystemState':
        """Pure function: State is function of actions"""
        return SystemState(
            action_history=self.action_history + (action,)
        )

    @property
    def current_mode(self) -> str:
        """Derived from history, not stored"""
        return compute_mode(self.action_history)

    @property
    def action_count(self) -> int:
        return len(self.action_history)


def compute_mode(actions: Tuple[ValidAction, ...]) -> str:
    """Mode is COMPUTED from action sequence. Cannot be set to invalid value."""
    if not actions:
        return "idle"
    last = actions[-1]
    if last == ValidAction.SPEAK:
        return "speaking"
    if last == ValidAction.QUERY:
        return "querying"
    if last == ValidAction.HARDWARE_SAFE:
        return "hardware"
    return "active"


def compute_state(actions: List[ValidAction]) -> SystemState:
    """State is pure function of action sequence"""
    return reduce(
        lambda state, action: state.apply(action),
        actions,
        SystemState.initial()
    )
