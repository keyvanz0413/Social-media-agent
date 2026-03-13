"""Smoke tests for fast confidence checks."""

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


@pytest.mark.smoke
def test_imports_smoke():
    from social_media_agent.config import Config
    from social_media_agent.tools.content_analyst import analyze_xiaohongshu
    from social_media_agent.tools.content_creator import create_content
    from social_media_agent.tools.publisher import publish_to_xiaohongshu
    from social_media_agent.tools.langchain_tools import get_structured_tools

    assert Config is not None
    assert callable(analyze_xiaohongshu)
    assert callable(create_content)
    assert callable(publish_to_xiaohongshu)
    assert len(get_structured_tools()) >= 10


@pytest.mark.smoke
def test_config_and_dirs_smoke():
    from social_media_agent.config import Config

    Config.ensure_dirs()
    assert Config.BASE_DIR.exists()
    assert Config.DRAFTS_DIR.exists()
    assert Config.LOGS_DIR.exists()


@pytest.mark.smoke
def test_content_pipeline_smoke(isolated_runtime):
    from social_media_agent.agents.reviewers.compliance_reviewer import review_compliance
    from social_media_agent.agents.reviewers.quality_reviewer import review_quality
    from social_media_agent.tools.content_analyst import analyze_xiaohongshu
    from social_media_agent.tools.content_creator import create_content

    analysis = json.loads(analyze_xiaohongshu(keyword="悉尼旅行", limit=3, quality_level="fast"))
    assert analysis.get("success", True) is True

    creation = json.loads(
        create_content(
            analysis_result=json.dumps(analysis, ensure_ascii=False),
            topic="悉尼旅行",
            style="casual",
            quality_level="fast",
        )
    )
    assert creation.get("title") or (creation.get("data") and creation["data"].get("title"))

    payload = creation.get("data") if "data" in creation else creation
    quality = json.loads(review_quality(payload, quality_level="fast"))
    compliance = json.loads(review_compliance(payload, quality_level="fast"))
    assert "data" in quality and "score" in quality["data"]
    assert "data" in compliance and "score" in compliance["data"]


@pytest.mark.smoke
def test_run_loop_smoke(isolated_runtime):
    from social_media_agent.orchestration.loop_controller import run_task_with_loop

    result = run_task_with_loop("写一篇悉尼旅行帖子，参考3篇", max_iterations=2, quality_threshold=7.0)
    assert "success" in result
    assert "message" in result
    assert "trace_path" in result

