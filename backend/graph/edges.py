from graph.state import GraphState

def should_continue(state: GraphState) -> str:
    """
    Example edge routing function.
    """
    if state.get("error"):
        return "end"
    return "continue"
