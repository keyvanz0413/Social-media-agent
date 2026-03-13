"""Unit tests for LangGraph workflow orchestration."""

import os

import pytest

os.environ["MOCK_MODE"] = "true"


@pytest.mark.unit
def test_langgraph_content_flow(tmp_path, monkeypatch):
    monkeypatch.setattr("social_media_agent.config.Config.LOGS_DIR", tmp_path / "logs")
    from social_media_agent.orchestration.langgraph_workflow import run_task_with_langgraph

    result = run_task_with_langgraph("写一篇悉尼旅行帖子，参考3篇", quality_threshold=7.0)
    assert "trace_path" in result
    assert result["mode"] == "content"
    assert result["message"]


@pytest.mark.unit
def test_langgraph_schedule_flow(tmp_path, monkeypatch):
    monkeypatch.setattr("social_media_agent.config.Config.LOGS_DIR", tmp_path / "logs")
    monkeypatch.setattr("social_media_agent.config.Config.SCHEDULE_DB_PATH", tmp_path / "schedule.db")

    from social_media_agent.orchestration.langgraph_workflow import run_task_with_langgraph

    result = run_task_with_langgraph("给我做一个7天的健身主题排期")
    assert result["mode"] == "schedule"
    assert result["success"] is True

