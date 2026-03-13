"""
Unit tests for scheduler tools and service.
"""

import json
from pathlib import Path

import pytest

from social_media_agent.scheduler import ScheduleService
from social_media_agent.tools.scheduler_tools import (
    create_schedule,
    list_schedule,
    reschedule,
)


@pytest.fixture
def isolated_schedule_db(tmp_path, monkeypatch):
    db_path = tmp_path / "schedule_test.db"
    monkeypatch.setattr("social_media_agent.config.Config.SCHEDULE_DB_PATH", db_path)
    return db_path


@pytest.mark.unit
def test_create_and_list_schedule(isolated_schedule_db):
    result = create_schedule(
        topic="悉尼旅行",
        days=5,
        frequency="daily",
        start_date="2026-03-10",
        preferred_time="19:30",
    )
    payload = json.loads(result)
    assert payload["success"] is True
    assert payload["data"]["count"] == 5

    listed = json.loads(list_schedule(date_from="2026-03-10", date_to="2026-03-20"))
    assert listed["success"] is True
    assert listed["data"]["count"] >= 5


@pytest.mark.unit
def test_reschedule_item(isolated_schedule_db):
    created = json.loads(
        create_schedule(
            topic="北海道攻略",
            days=1,
            frequency="daily",
            start_date="2026-03-11",
            preferred_time="20:00",
        )
    )
    item_id = created["data"]["items"][0]["id"]

    updated = json.loads(reschedule(item_id=item_id, new_time="2026-03-12 09:00"))
    assert updated["success"] is True
    assert updated["data"]["id"] == item_id
    assert updated["data"]["publish_time"].startswith("2026-03-12T09:00")


@pytest.mark.unit
def test_conflict_auto_shift(isolated_schedule_db):
    service = ScheduleService(Path(isolated_schedule_db))
    first = service.create_schedule(
        topic="冲突测试A",
        days=1,
        frequency="daily",
        start_date="2026-03-13",
        preferred_time="10:00",
    )[0]
    second = service.create_schedule(
        topic="冲突测试B",
        days=1,
        frequency="daily",
        start_date="2026-03-13",
        preferred_time="10:00",
    )[0]

    assert first["publish_time"] != second["publish_time"]
    assert second["publish_time"].endswith("10:30")
