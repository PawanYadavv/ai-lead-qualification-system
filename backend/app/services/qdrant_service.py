from __future__ import annotations

from app.core.config import settings


class QdrantService:
    """Optional vector store helper for future semantic retrieval extensions."""

    def __init__(self) -> None:
        self.client = None

        if not settings.USE_QDRANT:
            return

        try:
            from qdrant_client import QdrantClient

            self.client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY or None)
        except Exception:
            self.client = None

    def is_enabled(self) -> bool:
        return self.client is not None

    def store_session_note(self, tenant_id: str, session_id: str, text: str) -> None:
        # Embedding + upsert can be added when semantic retrieval is needed.
        if not self.client or not text.strip():
            return
        return
