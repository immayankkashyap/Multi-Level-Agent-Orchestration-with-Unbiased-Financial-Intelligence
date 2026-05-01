from retrieval.qdrant_client import get_qdrant


class HybridRetriever:
    def __init__(self, collection_name: str = "documents"):
        self.collection_name = collection_name
        # Do NOT call get_qdrant() here – defer until first search so the
        # module can be safely imported before Qdrant is running.

    async def search(self, query: str, top_k: int = 5) -> list:
        """
        Hybrid dense + BM25 retrieval.
        Currently returns a mock result; real ingestion will be added later.
        """
        # TODO: replace with real qdrant hybrid search once documents are ingested
        return [
            {
                "source": "Mock Financial Report",
                "text": f"Simulated retrieval content for query: {query}",
                "score": 0.5,
            }
        ]
