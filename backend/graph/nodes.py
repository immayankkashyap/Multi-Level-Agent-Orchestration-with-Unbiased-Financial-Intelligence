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
from typing import Any

from graph.state import GraphState
from agents.planner import planner_node
from agents.workers.rag_agent import rag_agent_node
from agents.workers.financial_data_agent import financial_data_node
from agents.workers.regulation_agent import regulation_node
from agents.workers.graph_rag_agent import graph_rag_node

from agents.debate.advocate import advocate_node
from agents.debate.devil_advocate import devil_advocate_node
from agents.judge import judge_node
from tracing.tracer import trace_action


# ---------------------------------------------------------------------------
# Fan-out router
# ---------------------------------------------------------------------------


def _trace_title(state: GraphState) -> str:
    query = state.get("trace_title") or state.get("query") or "Financial AI pipeline"
    return query[:120]


def _trace_step_payload(
    node_name: str,
    step: dict[str, Any],
    *,
    exclude: set[str] | None = None,
    summary: str | None = None,
    detail: str | None = None,
    status: str | None = None,
) -> dict[str, Any]:
    payload = {
        "node": node_name,
        **{
            key: value
            for key, value in step.items()
            if exclude is None or key not in exclude
        },
    }

    if summary is not None:
        payload["summary"] = summary
    if detail is not None:
        payload["detail"] = detail
    if status is not None:
        payload["status"] = status

    return payload


def _with_tracing(node_name: str, node_fn, *, start: bool = False, end: bool = False):
    async def _wrapped(state: GraphState) -> dict:
        title = _trace_title(state)
        started_here = False

        if start and not state.get("trace_started"):
            started_here = True
            await trace_action(
                "START",
                title=title,
                step_data={
                    "node": node_name,
                    "query": state.get("query", ""),
                },
            )

        try:
            result = await node_fn(state)
        except Exception as error:
            await trace_action(
                "STEP",
                step_data={
                    "node": node_name,
                    "status": "error",
                    "summary": f"{node_name} failed",
                    "detail": str(error),
                },
            )
            if started_here:
                await trace_action(
                    "END",
                    step_data={
                        "node": node_name,
                        "status": "error",
                        "summary": f"{node_name} failed",
                        "detail": str(error),
                    },
                )
            raise

        for step in result.get("steps", []):
            prompt = step.get("prompt")
            argument = step.get("argument")

            if prompt:
                await trace_action(
                    "STEP",
                    step_data=_trace_step_payload(
                        node_name,
                        step,
                        exclude={"argument"},
                        summary=f"{node_name} prompt sent",
                        detail=prompt,
                        status="running",
                    ),
                )

            await trace_action(
                "STEP",
                step_data=_trace_step_payload(node_name, step),
            )

            if argument is not None:
                await trace_action(
                    "STEP",
                    step_data=_trace_step_payload(
                        node_name,
                        step,
                        exclude={"prompt"},
                        summary=f"{node_name} argument generated",
                        detail=argument,
                        status="done",
                    ),
                )

        if start:
            result = {
                **result,
                "trace_started": True,
                "trace_title": title,
            }

        if end:
            final_step = result.get("steps", [{}])[-1]
            await trace_action(
                "END",
                step_data={
                    "node": node_name,
                    "status": "done",
                    "summary": final_step.get("summary", "Final decision complete"),
                    "detail": result.get("final_decision", ""),
                },
            )

        return result

    return _wrapped

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

    traced_planner = _with_tracing("planner", planner_node, start=True)
    traced_rag_agent = _with_tracing("rag_agent", rag_agent_node)
    traced_financial_data = _with_tracing("financial_data", financial_data_node)
    traced_regulation = _with_tracing("regulation", regulation_node)
    traced_graph_rag = _with_tracing("graph_rag", graph_rag_node)
    traced_advocate = _with_tracing("advocate", advocate_node)
    traced_devil_advocate = _with_tracing("devil_advocate", devil_advocate_node)
    traced_judge = _with_tracing("judge", judge_node, end=True)

    # Register original worker nodes
    g.add_node("planner", traced_planner)
    g.add_node("rag_agent", traced_rag_agent)
    g.add_node("financial_data", traced_financial_data)
    g.add_node("regulation", traced_regulation)
    g.add_node("graph_rag", traced_graph_rag)

    # Register new debate and judge nodes
    g.add_node("advocate", traced_advocate)
    g.add_node("devil_advocate", traced_devil_advocate)
    g.add_node("judge", traced_judge)

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
