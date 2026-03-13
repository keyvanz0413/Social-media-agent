"""
Scheduler tools for planning content calendars.
"""

import json
import logging
from typing import Optional

from social_media_agent.scheduler import ScheduleService
from social_media_agent.utils.response_utils import (
    create_error_dict,
    create_success_dict,
)

logger = logging.getLogger(__name__)


def create_schedule(
    topic: str,
    days: int = 7,
    frequency: str = "daily",
    start_date: Optional[str] = None,
    preferred_time: str = "20:00",
    platform: str = "xiaohongshu",
) -> str:
    """Create a schedule plan for a topic."""
    return json.dumps(
        create_schedule_native(
            topic=topic,
            days=days,
            frequency=frequency,
            start_date=start_date,
            preferred_time=preferred_time,
            platform=platform,
        ),
        ensure_ascii=False,
    )


def create_schedule_native(
    topic: str,
    days: int = 7,
    frequency: str = "daily",
    start_date: Optional[str] = None,
    preferred_time: str = "20:00",
    platform: str = "xiaohongshu",
) -> dict:
    """Create a schedule plan and return structured dict result."""
    try:
        service = ScheduleService()
        items = service.create_schedule(
            topic=topic,
            days=days,
            frequency=frequency,
            start_date=start_date,
            preferred_time=preferred_time,
            platform=platform,
        )
        logger.info("排期创建成功: topic=%s count=%s", topic, len(items))
        return create_success_dict(
            data={"items": items, "count": len(items)},
            message="排期创建成功",
            topic=topic,
            frequency=frequency,
            days=days,
        )
    except Exception as e:
        logger.error("排期创建失败: %s", str(e), exc_info=True)
        return create_error_dict(
            error=str(e),
            message="排期创建失败",
        )


def list_schedule(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
) -> str:
    """List schedule items with optional filters."""
    return json.dumps(
        list_schedule_native(
            date_from=date_from,
            date_to=date_to,
            status=status,
            limit=limit,
        ),
        ensure_ascii=False,
    )


def list_schedule_native(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
) -> dict:
    """List schedule items and return structured dict result."""
    try:
        service = ScheduleService()
        items = service.list_schedule(
            date_from=date_from,
            date_to=date_to,
            status=status,
            limit=limit,
        )
        return create_success_dict(
            data={"items": items, "count": len(items)},
            message="查询排期成功",
            date_from=date_from,
            date_to=date_to,
            status=status,
        )
    except Exception as e:
        logger.error("查询排期失败: %s", str(e), exc_info=True)
        return create_error_dict(
            error=str(e),
            message="查询排期失败",
        )


def reschedule(
    item_id: int,
    new_time: str,
) -> str:
    """Update schedule item publish time."""
    return json.dumps(reschedule_native(item_id=item_id, new_time=new_time), ensure_ascii=False)


def reschedule_native(
    item_id: int,
    new_time: str,
) -> dict:
    """Update schedule item publish time and return structured dict result."""
    try:
        service = ScheduleService()
        item = service.reschedule(item_id=item_id, new_time=new_time)
        return create_success_dict(
            data=item,
            message="改期成功",
            item_id=item_id,
        )
    except Exception as e:
        logger.error("改期失败: %s", str(e), exc_info=True)
        return create_error_dict(
            error=str(e),
            message="改期失败",
            item_id=item_id,
        )
