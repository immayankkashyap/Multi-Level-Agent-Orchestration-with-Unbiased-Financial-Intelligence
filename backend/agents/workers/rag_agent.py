from retrieval.hybrid_retriever import HybridRetriever
from retrieval.query_rewriter import rewrite_query
from retrieval.reranker import rerank
from graph.state import Evidence, AgentStep, GraphState

_retriever = HybridRetriever()


async def rag_agent_node(state: GraphState) -> dict:
    """
    Hybrid RAG worker.
    1. Rewrites the query for better retrieval.
    2. Runs hybrid dense + BM25 search.
    3. Re-ranks with a cross-encoder.
    Returns only the keys this node updates.
    """
    step = AgentStep(
        agent_name="rag_agent",
        status="running",
        summary="Searching knowledge base...",
        detail="Running hybrid vector + BM25 retrieval",
    )

    rewritten = await rewrite_query(state["query"])
    # Use smaller top_k to limit Qdrant reads on free-tier clusters
    raw_results = await _retriever.search(rewritten, top_k=5)
    reranked = await rerank(rewritten, raw_results, top_k=5)

    evidence = [
        Evidence(
            source=r["source"],
            passage=r["text"],
            relevance_score=r["score"],
        )
        for r in reranked
    ]

    step["status"] = "done"
    step["summary"] = f"Found {len(evidence)} relevant passages"

    return {"evidence": evidence, "steps": [step]}
