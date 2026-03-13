"""
API tests for FastAPI service layer.
"""

import os

import pytest
from fastapi.testclient import TestClient

os.environ["MOCK_MODE"] = "true"


@pytest.fixture
def api_client(tmp_path, monkeypatch):
    monkeypatch.setattr("social_media_agent.config.Config.SCHEDULE_DB_PATH", tmp_path / "schedule.db")
    monkeypatch.setattr("social_media_agent.config.Config.MEMORY_DIR", tmp_path / "memory")
    monkeypatch.setattr("social_media_agent.config.Config.MEMORY_INDEX_DIR", tmp_path / "memory" / "faiss_index")
    monkeypatch.setattr("social_media_agent.config.Config.MEMORY_RECORDS_PATH", tmp_path / "memory" / "records.jsonl")

    import social_media_agent.memory.memory_service as memory_service_module

    memory_service_module._MEMORY_SERVICE = None
    from social_media_agent.api.server import app

    client = TestClient(app)
    yield client
    memory_service_module._MEMORY_SERVICE = None


@pytest.mark.unit
def test_health(api_client):
    resp = api_client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True


@pytest.mark.unit
def test_run_task(api_client):
    resp = api_client.post(
        "/run-task",
        json={"task": "写一篇悉尼旅行帖子，参考3篇", "max_iterations": 2, "quality_threshold": 7.0},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "trace_path" in data["data"]


@pytest.mark.unit
def test_schedule_endpoints(api_client):
    create_resp = api_client.post(
        "/schedule/create",
        json={"topic": "澳洲健身", "days": 5, "frequency": "daily", "start_date": "2026-03-08"},
    )
    assert create_resp.status_code == 200
    create_data = create_resp.json()
    assert create_data["success"] is True
    item_id = create_data["data"]["items"][0]["id"]

    list_resp = api_client.get("/schedule/list", params={"date_from": "2026-03-08", "date_to": "2026-03-20"})
    assert list_resp.status_code == 200
    assert list_resp.json()["success"] is True

    rs_resp = api_client.post("/schedule/reschedule", json={"item_id": item_id, "new_time": "2026-03-10 09:30"})
    assert rs_resp.status_code == 200
    assert rs_resp.json()["success"] is True


@pytest.mark.unit
def test_memory_endpoints(api_client):
    save_resp = api_client.post(
        "/memory/save",
        json={"item_type": "user_preference", "content": "用户偏好短标题", "metadata": {"lang": "zh"}},
    )
    assert save_resp.status_code == 200
    assert save_resp.json()["success"] is True

    search_resp = api_client.post("/memory/search", json={"query": "短标题", "top_k": 3})
    assert search_resp.status_code == 200
    assert search_resp.json()["success"] is True
    assert search_resp.json()["data"]["count"] >= 1

    recent_resp = api_client.get("/memory/recent", params={"limit": 10})
    assert recent_resp.status_code == 200
    assert recent_resp.json()["success"] is True
