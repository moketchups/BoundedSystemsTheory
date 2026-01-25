from action_space.actions import ValidAction, ActionResult
from r_source.r_derivation import RDerived, RootSource


# Function signatures make invalid calls impossible
def execute(action: ValidAction, payload: RDerived, r_source: RootSource) -> ActionResult:
    """Execute a valid action.

    No safety check needed.
    If you're here, action is valid BY TYPE.
    Payload is R-derived BY CONSTRUCTION.
    """
    result_value = _dispatch(action, payload.value)
    result = RDerived.from_r(result_value, r_source)
    return ActionResult(action=action, output=result, success=True)


def _dispatch(action: ValidAction, value: object) -> object:
    """Dispatch action to handler. All handlers are valid by definition."""
    handlers = {
        ValidAction.SPEAK: lambda v: str(v),
        ValidAction.REMEMBER: lambda v: {"stored": v},
        ValidAction.QUERY: lambda v: {"query": v},
        ValidAction.HARDWARE_SAFE: lambda v: {"command": v},
    }
    return handlers[action](value)
