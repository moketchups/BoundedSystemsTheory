from state_engine.state import SystemState
from action_space.actions import ValidAction


def transition(state: SystemState, action: ValidAction) -> SystemState:
    """Pure state transition. No side effects. No mutation."""
    return state.apply(action)
