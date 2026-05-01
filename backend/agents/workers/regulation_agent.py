from datetime import datetime, timezone

from retrieval.qdrant_client import get_qdrant
from graph.state import Evidence, AgentStep, GraphState

# Mock embedding – replace with a real sentence-transformer when docs are ingested
_MOCK_VECTOR_DIM = 384


async def _mock_embed(text: str) -> list[float]:
    return [0.0] * _MOCK_VECTOR_DIM


async def regulation_node(state: GraphState) -> dict:
    """
    Regulatory search worker.
    Queries Qdrant's 'regulations' collection with a time-aware filter
    (only documents effective up to today).
    Gracefully degrades if Qdrant is unreachable.
    Returns only the keys this node updates.
    """
    step = AgentStep(
        agent_name="regulation",
        status="running",
        summary="Checking RBI/SEBI/IRDAI guidelines...",
        detail="Time-aware regulatory retrieval",
    )

    evidence: list[Evidence] = []
    today_iso = datetime.now(timezone.utc).date().isoformat()  # "YYYY-MM-DD"

    try:
        qdrant = get_qdrant()
        query_vector = await _mock_embed(state["query"])

        results = qdrant.query_points(
            collection_name="regulations",
            query=query_vector,
            limit=5,
        ).points

        # Qdrant range filters are numeric; this collection stores ISO date strings.
        # Apply the date check here so the query still works without a schema change.
        results = [
            hit
            for hit in results
            if hit.payload.get("effective_until", "") >= today_iso
        ]

        for hit in results:
            evidence.append(
                Evidence(
                    source=hit.payload.get("title", "Regulation"),
                    passage=hit.payload.get("text", ""),
                    relevance_score=hit.score,
                )
            )
        step["summary"] = f"{len(results)} regulations retrieved"

    except Exception:
        # Qdrant not running yet – skip gracefully
        step["summary"] = "Regulation retrieval skipped (Qdrant unavailable)"

    step["status"] = "done"
    return {"evidence": evidence, "steps": [step]}
