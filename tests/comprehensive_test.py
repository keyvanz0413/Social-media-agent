"""Comprehensive integration tests for major product flows."""

import json
import os

import pytest

os.environ["MOCK_MODE"] = "true"


@pytest.fixture
def isolated_runtime(tmp_path, monkeypatch):
    monkeypatch.setattr("social_media_agent.config.Config.SCHEDULE_DB_PATH", tmp_path / "schedule.db")
    monkeypatch.setattr("social_media_agent.config.Config.MEMORY_DIR", tmp_path / "memory")
    monkeypatch.setattr("social_media_agent.config.Config.MEMORY_INDEX_DIR", tmp_path / "memory" / "faiss_index")
    monkeypatch.setattr("social_media_agent.config.Config.MEMORY_RECORDS_PATH", tmp_path / "memory" / "records.jsonl")
    monkeypatch.setattr("social_media_agent.config.Config.LOGS_DIR", tmp_path / "logs")

    import social_media_agent.memory.memory_service as memory_service_module

    memory_service_module._MEMORY_SERVICE = None
    yield
    memory_service_module._MEMORY_SERVICE = None


@pytest.mark.integration
def test_end_to_end_content_flow(isolated_runtime):
    from social_media_agent.tools.content_analyst import analyze_xiaohongshu
    from social_media_agent.tools.content_creator import create_content
    from social_media_agent.tools.review_tools_v1 import review_content

    analysis = json.loads(analyze_xiaohongshu(keyword="北海道旅行", limit=3, quality_level="fast"))
    assert analysis.get("success", True) is True

    creation = json.loads(
        create_content(
            analysis_result=json.dumps(analysis, ensure_ascii=False),
            topic="北海道旅行",
            style="casual",
            quality_level="fast",
        )
    )
    payload = creation.get("data") if "data" in creation else creation
    assert payload.get("title")
    assert payload.get("content")

    reviewed = json.loads(review_content(payload, quality_level="fast"))
    assert reviewed["success"] is True
    assert reviewed["data"]["overall_score"] >= 0


@pytest.mark.integration
def test_scheduler_memory_flow(isolated_runtime):
    from social_media_agent.tools.memory_tools import save_memory_native, search_memory_native
    from social_media_agent.tools.scheduler_tools import create_schedule_native, list_schedule_native, reschedule_native

    s = create_schedule_native(topic="悉尼健身", days=3, frequency="daily", start_date="2026-03-10")
    assert s["success"] is True
    item_id = s["data"]["items"][0]["id"]

    listed = list_schedule_native(date_from="2026-03-10", date_to="2026-03-20")
    assert listed["success"] is True
    assert listed["data"]["count"] >= 3

    rs = reschedule_native(item_id=item_id, new_time="2026-03-12 09:00")
    assert rs["success"] is True

    saved = save_memory_native(item_type="user_preference", content="偏好短标题", metadata={"lang": "zh"})
    assert saved["success"] is True

    searched = search_memory_native(query="短标题", top_k=3)
    assert searched["success"] is True
    assert searched["data"]["count"] >= 1


@pytest.mark.integration
def test_langgraph_and_loop_engines(isolated_runtime, monkeypatch):
    from social_media_agent.main import _run_controlled_workflow
    from social_media_agent.orchestration.langgraph_workflow import run_task_with_langgraph
    from social_media_agent.orchestration.loop_controller import run_task_with_loop

    graph = run_task_with_langgraph("写一篇悉尼旅行帖子，参考3篇", quality_threshold=7.0)
    assert "trace_path" in graph
    assert graph["mode"] == "content"

    loop = run_task_with_loop("写一篇悉尼旅行帖子，参考3篇", max_iterations=2, quality_threshold=7.0)
    assert "trace_path" in loop

    monkeypatch.setattr("social_media_agent.config.Config.LOOP_ENGINE", "graph")
    routed = _run_controlled_workflow("给我做一个7天的健身主题排期")
    assert routed["mode"] == "schedule"


@pytest.mark.integration
def test_structured_tools_invoke_core(isolated_runtime):
    from social_media_agent.tools.langchain_tools import get_structured_tools

    tools = {t.name: t for t in get_structured_tools()}

    a = tools["analyze_xiaohongshu"].invoke({"keyword": "悉尼旅行", "limit": 3, "quality_level": "fast"})
    assert a.get("success", True) is True

    c = tools["create_content"].invoke(
        {
            "analysis_result": a,
            "topic": "悉尼旅行",
            "style": "casual",
            "quality_level": "fast",
        }
    )
    assert c.get("success", True) is True

    m = tools["save_memory"].invoke(
        {
            "item_type": "review_summary",
            "content": "标题需要更短",
            "metadata": {"source": "integration"},
            "source": "integration_test",
        }
    )
    assert m["success"] is True

