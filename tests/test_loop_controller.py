"""
Unit tests for Reason->Act->Observe loop controller.
"""

import os

import pytest

os.environ["MOCK_MODE"] = "true"


@pytest.fixture
def isolated_runtime(tmp_path, monkeypatch):
    monkeypatch.setattr("social_media_agent.config.Config.SCHEDULE_DB_PATH", tmp_path / "schedule.db")
    monkeypatch.setattr("social_media_agent.config.Config.MEMORY_DIR", tmp_path / "memory")
    monkeypatch.setattr("social_media_agent.config.Config.MEMORY_INDEX_DIR", tmp_path / "memory" / "faiss_index")
    monkeypatch.setattr("social_media_agent.config.Config.MEMORY_RECORDS_PATH", tmp_path / "memory" / "records.jsonl")

    import social_media_agent.memory.memory_service as memory_service_module

    memory_service_module._MEMORY_SERVICE = None
    yield
    memory_service_module._MEMORY_SERVICE = None


@pytest.mark.unit
def test_content_loop_flow(isolated_runtime):
    from social_media_agent.orchestration.loop_controller import run_task_with_loop

    result = run_task_with_loop(
        task="写一篇悉尼旅行帖子，参考3篇",
        max_iterations=2,
        quality_threshold=7.0,
    )

    assert "trace_path" in result
    assert result["trace_path"]
    assert result["message"]


@pytest.mark.unit
def test_schedule_loop_flow(isolated_runtime):
    from social_media_agent.orchestration.loop_controller import run_task_with_loop

    result = run_task_with_loop(
        task="给我做一个7天的健身主题排期",
        max_iterations=2,
        quality_threshold=8.0,
    )

    assert result["success"] is True
    assert "排期创建完成" in result["message"]


@pytest.mark.unit
def test_memory_context_weight_and_truncation(isolated_runtime, monkeypatch):
    from social_media_agent.orchestration.loop_controller import _build_memory_context

    monkeypatch.setattr("social_media_agent.config.Config.MEMORY_CONTEXT_MAX_CHARS", 70)
    rows = [
        {"item_type": "review_summary", "content": "A" * 80, "score": 0.5},
        {"item_type": "user_preference", "content": "B" * 80, "score": 0.5},
        {"item_type": "review_summary", "content": "C" * 80, "score": 0.1},
    ]
    context = _build_memory_context(rows)

    assert context
    assert len(context) <= 70
    assert context.startswith("[user_preference")
