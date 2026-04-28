"""
LangGraph state machine for the Financial AI pipeline (Task 1).

Architecture:
    planner → [fan-out] → rag_agent ─┐
                         financial_data → [merge via gather_evidence] → [fan-out] → advocate ─┐
                         regulation  ─┘                                   devil_advocate ─┘ → judge → END
                         graph_rag   ─┘

LangGraph v1.x does NOT automatically fan-out when you call add_edge() to
multiple nodes from one source.  The correct pattern is to use a router node
that returns a list of `Send` objects, one per worker.
"""
from langgraph.graph import StateGraph, END
from langgraph.types import Send

from graph.state import GraphState
from agents.planner import planner_node
from agents.workers.rag_agent import rag_agent_node
from agents.workers.financial_data_agent import financial_data_node
from agents.workers.regulation_agent import regulation_node
from agents.workers.graph_rag_agent import graph_rag_node

from agents.debate.advocate import advocate_node
from agents.debate.devil_advocate import devil_advocate_node
from agents.judge import judge_node


# ---------------------------------------------------------------------------
# Fan-out router
# ---------------------------------------------------------------------------

def _fan_out_to_workers(state: GraphState) -> list[Send]:
    """
    Called after the planner finishes.
    Returns one Send per worker so LangGraph executes them in parallel.
    Each worker receives the *full* current state as its input.
    """
    return [
        Send("rag_agent", state),
        Send("financial_data", state),
        Send("regulation", state),
        Send("graph_rag", state),
    ]

def _fan_out_to_debate(state: GraphState) -> list[Send]:
    """
    Called after all workers finish and evidence is gathered.
    Returns one Send per debate agent so they execute in parallel.
    """
    return [
        Send("advocate", state),
        Send("devil_advocate", state)
    ]

# ---------------------------------------------------------------------------
# Graph builder
# ---------------------------------------------------------------------------

def build_graph():
    g = StateGraph(GraphState)

    # Register original worker nodes
    g.add_node("planner", planner_node)
    g.add_node("rag_agent", rag_agent_node)
    g.add_node("financial_data", financial_data_node)
    g.add_node("regulation", regulation_node)
    g.add_node("graph_rag", graph_rag_node)

    # Register new debate and judge nodes
    g.add_node("advocate", advocate_node)
    g.add_node("devil_advocate", devil_advocate_node)
    g.add_node("judge", judge_node)

    # Add a dummy gather node to wait for workers
    g.add_node("gather_evidence", lambda state: {})

    # Add a dummy gather node to wait for debate
    g.add_node("gather_debate", lambda state: {})

    # Entry point
    g.set_entry_point("planner")

    # Parallel fan-out: planner → all 4 workers simultaneously
    g.add_conditional_edges("planner", _fan_out_to_workers)

    # All workers finish at gather_evidence
    g.add_edge("rag_agent", "gather_evidence")
    g.add_edge("financial_data", "gather_evidence")
    g.add_edge("regulation", "gather_evidence")
    g.add_edge("graph_rag", "gather_evidence")

    # Fanning out to debate layers
    g.add_conditional_edges("gather_evidence", _fan_out_to_debate)

    # Gather debate, then judge evaluates them
    g.add_edge("advocate", "gather_debate")
    g.add_edge("devil_advocate", "gather_debate")

    g.add_edge("gather_debate", "judge")
    g.add_edge("judge", END)

    return g.compile()
