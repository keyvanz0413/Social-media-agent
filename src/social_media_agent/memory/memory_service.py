"""
High-level memory service API.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from social_media_agent.config import Config
from social_media_agent.memory.vector_store import MemoryVectorStore


class MemoryService:
    """Domain-level API for writing and retrieving memory."""

    def __init__(self):
        self.store = MemoryVectorStore()

    @property
    def backend(self) -> str:
        return self.store.backend

    def save_memory(
        self,
        item_type: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        source: str = "manual",
    ) -> Dict[str, Any]:
        return self.store.add_memory(
            item_type=item_type,
            content=content,
            metadata=metadata,
            source=source,
        )

    def search_memory(
        self,
        query: str,
        top_k: Optional[int] = None,
        item_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        k = top_k if top_k is not None else Config.MEMORY_TOP_K
        return self.store.search(query=query, top_k=k, item_type=item_type)

    def list_recent_memories(
        self,
        limit: int = 20,
        item_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        return self.store.list_recent(limit=limit, item_type=item_type)


_MEMORY_SERVICE: Optional[MemoryService] = None


def get_memory_service() -> MemoryService:
    global _MEMORY_SERVICE
    if _MEMORY_SERVICE is None:
        _MEMORY_SERVICE = MemoryService()
    return _MEMORY_SERVICE
