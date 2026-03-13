"""
Unit tests for memory tools.
"""

import json

import pytest


@pytest.fixture
def isolated_memory_paths(tmp_path, monkeypatch):
    memory_dir = tmp_path / "memory"
    monkeypatch.setattr("social_media_agent.config.Config.MEMORY_DIR", memory_dir)
    monkeypatch.setattr(
        "social_media_agent.config.Config.MEMORY_INDEX_DIR", memory_dir / "faiss_index"
    )
    monkeypatch.setattr(
        "social_media_agent.config.Config.MEMORY_RECORDS_PATH", memory_dir / "records.jsonl"
    )

    import social_media_agent.memory.memory_service as memory_service_module

    memory_service_module._MEMORY_SERVICE = None
    yield
    memory_service_module._MEMORY_SERVICE = None


@pytest.mark.unit
def test_save_and_search_memory(isolated_memory_paths):
    from social_media_agent.tools.memory_tools import save_memory, search_memory

    save_resp = json.loads(
        save_memory(
            item_type="user_preference",
            content="用户偏好：旅行内容用轻松口语，结尾加行动建议",
            metadata='{"channel":"xiaohongshu"}',
        )
    )
    assert save_resp["success"] is True

    search_resp = json.loads(search_memory(query="旅行内容口语风格", top_k=3))
    assert search_resp["success"] is True
    assert search_resp["data"]["count"] >= 1
    assert search_resp["metadata"]["backend"] in {"faiss", "fallback"}


@pytest.mark.unit
def test_list_recent_memories_with_filter(isolated_memory_paths):
    from social_media_agent.tools.memory_tools import save_memory, list_recent_memories

    json.loads(save_memory(item_type="review_summary", content="质量评分低，建议补充步骤细节"))
    json.loads(save_memory(item_type="user_preference", content="标题尽量控制在18字以内"))

    recent_all = json.loads(list_recent_memories(limit=10))
    assert recent_all["success"] is True
    assert recent_all["data"]["count"] >= 2

    recent_filtered = json.loads(list_recent_memories(limit=10, item_type="review_summary"))
    assert recent_filtered["success"] is True
    assert recent_filtered["data"]["count"] >= 1
    for item in recent_filtered["data"]["items"]:
        assert item["item_type"] == "review_summary"
