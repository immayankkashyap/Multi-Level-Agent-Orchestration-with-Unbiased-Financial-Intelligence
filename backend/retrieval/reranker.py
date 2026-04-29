import asyncio
from sentence_transformers import CrossEncoder

_reranker: CrossEncoder | None = None


def get_reranker() -> CrossEncoder:
    global _reranker
    if _reranker is None:
        # Using the powerful Gemma-based reranker (2B params)
        # Since a dedicated GPU is available, we load this on CUDA for maximum performance.
        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"
        _reranker = CrossEncoder("BAAI/bge-reranker-v2-gemma", device=device)
    return _reranker


async def rerank(query: str, raw_results: list, top_k: int = 5) -> list:
    """
    Re-ranks raw retrieval results using a cross-encoder.

    CrossEncoder.predict() is a synchronous blocking call (even on GPU).
    We run it in a thread pool so we don't block the asyncio event loop.
    """
    if not raw_results:
        return []

    reranker = get_reranker()
    pairs = [[query, r["text"]] for r in raw_results]

    # Offload blocking synchronous work to a thread
    loop = asyncio.get_event_loop()
    scores = await loop.run_in_executor(None, reranker.predict, pairs)

    scored = [
        {**r, "score": float(score)}
        for r, score in zip(raw_results, scores)
    ]
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]
