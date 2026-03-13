"""
Memory tools for long-term context.
"""

import json
import logging
from typing import Any, Optional

from social_media_agent.memory import get_memory_service
from social_media_agent.utils.response_utils import (
    create_error_dict,
    create_success_dict,
)

logger = logging.getLogger(__name__)


def save_memory(
    item_type: str,
    content: str,
    metadata: Optional[Any] = None,
    source: str = "agent",
) -> str:
    """Save a memory item into long-term memory."""
    return json.dumps(
        save_memory_native(item_type=item_type, content=content, metadata=metadata, source=source),
        ensure_ascii=False,
    )


def save_memory_native(
    item_type: str,
    content: str,
    metadata: Optional[Any] = None,
    source: str = "agent",
) -> dict:
    """Save a memory item and return structured dict result."""
    try:
        parsed_metadata = _parse_metadata(metadata)
        service = get_memory_service()
        record = service.save_memory(
            item_type=item_type,
            content=content,
            metadata=parsed_metadata,
            source=source,
        )
        return create_success_dict(
            data=record,
            message="记忆保存成功",
            backend=service.backend,
        )
    except Exception as e:
        logger.error("保存记忆失败: %s", str(e), exc_info=True)
        return create_error_dict(
            error=str(e),
            message="记忆保存失败",
        )


def search_memory(
    query: str,
    top_k: int = 5,
    item_type: Optional[str] = None,
) -> str:
    """Search memory by semantic similarity."""
    return json.dumps(
        search_memory_native(query=query, top_k=top_k, item_type=item_type),
        ensure_ascii=False,
    )


def search_memory_native(
    query: str,
    top_k: int = 5,
    item_type: Optional[str] = None,
) -> dict:
    """Search memory and return structured dict result."""
    try:
        service = get_memory_service()
        rows = service.search_memory(query=query, top_k=top_k, item_type=item_type)
        return create_success_dict(
            data={"items": rows, "count": len(rows)},
            message="记忆检索成功",
            backend=service.backend,
        )
    except Exception as e:
        logger.error("检索记忆失败: %s", str(e), exc_info=True)
        return create_error_dict(
            error=str(e),
            message="记忆检索失败",
        )


def list_recent_memories(
    limit: int = 20,
    item_type: Optional[str] = None,
) -> str:
    """List recent memory items."""
    return json.dumps(
        list_recent_memories_native(limit=limit, item_type=item_type),
        ensure_ascii=False,
    )


def list_recent_memories_native(
    limit: int = 20,
    item_type: Optional[str] = None,
) -> dict:
    """List recent memory items and return structured dict result."""
    try:
        service = get_memory_service()
        rows = service.list_recent_memories(limit=limit, item_type=item_type)
        return create_success_dict(
            data={"items": rows, "count": len(rows)},
            message="最近记忆查询成功",
            backend=service.backend,
        )
    except Exception as e:
        logger.error("查询最近记忆失败: %s", str(e), exc_info=True)
        return create_error_dict(
            error=str(e),
            message="最近记忆查询失败",
        )


def _parse_metadata(metadata: Optional[str]):
    if metadata is None or metadata == "":
        return {}
    if isinstance(metadata, dict):
        return metadata
    if isinstance(metadata, str):
        try:
            parsed = json.loads(metadata)
            if isinstance(parsed, dict):
                return parsed
            return {"raw": parsed}
        except Exception:
            return {"raw": metadata}
    return {"raw": metadata}
