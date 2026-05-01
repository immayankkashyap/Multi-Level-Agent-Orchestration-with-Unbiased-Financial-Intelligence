"""
GraphState for the LangGraph pipeline.

IMPORTANT: `evidence` and `steps` are written to by multiple parallel nodes.
LangGraph v1.x requires Annotated reducers so parallel node outputs are
MERGED (appended) instead of the last writer winning.
"""
import operator
from typing import Annotated, List, Optional
from typing_extensions import NotRequired, TypedDict


class AgentStep(TypedDict):
    agent_name: str         # e.g. 'rag_agent'
    status: str             # 'running' | 'done' | 'error'
    summary: str            # one-liner for the UI thinking indicator
    detail: str             # full log for the thinking dropdown
    prompt: NotRequired[str]
    argument: NotRequired[str]


class Evidence(TypedDict):
    source: str             # document title or URL
    passage: str            # extracted text
    relevance_score: float  # 0.0 - 1.0


class GraphState(TypedDict):
    query: str
    user_id: str
    tier: str                                            # 'free' | 'pro' | 'enterprise'
    trace_started: bool
    trace_title: str
    sub_tasks: List[str]                                 # planner decomposition
    steps: Annotated[List[AgentStep], operator.add]      # merged across parallel nodes
    evidence: Annotated[List[Evidence], operator.add]    # merged across parallel nodes
    advocate_arg: str                                    # Layer 3 input (Developer B)
    devil_arg: str
    final_decision: str
    confidence: float
    bias_report: dict
    error: Optional[str]
