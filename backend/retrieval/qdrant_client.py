from qdrant_client import QdrantClient
from config.settings import settings

_client: QdrantClient | None = None


def get_qdrant() -> QdrantClient:
    """
    Lazy singleton.
    `check_compatibility=False` suppresses the version-mismatch warning
    that appears when Qdrant server is unreachable or on a different version.
    """
    global _client
    if _client is None:
        _client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
            check_compatibility=False,
        )
    return _client
