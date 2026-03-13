"""
Scheduler service based on SQLite.
"""

from __future__ import annotations

import math
import sqlite3
from datetime import datetime, date, time, timedelta
from importlib import import_module
from pathlib import Path
from typing import Any, Dict, List, Optional


SUPPORTED_FREQUENCIES = {
    "daily": 1,
    "every_2_days": 2,
    "weekly": 7,
}


class ScheduleService:
    """Provide persistent schedule creation/query/update operations."""

    def __init__(self, db_path: Optional[Path] = None):
        # Resolve Config dynamically to avoid stale class references after module reload.
        runtime_config = import_module("social_media_agent.config").Config
        self.db_path = Path(db_path or runtime_config.SCHEDULE_DB_PATH)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS schedules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic TEXT NOT NULL,
                    platform TEXT NOT NULL DEFAULT 'xiaohongshu',
                    publish_time TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'planned',
                    notes TEXT DEFAULT '',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_schedules_time ON schedules(publish_time);"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_schedules_status ON schedules(status);"
            )

    def create_schedule(
        self,
        topic: str,
        days: int = 7,
        frequency: str = "daily",
        start_date: Optional[str] = None,
        preferred_time: str = "20:00",
        platform: str = "xiaohongshu",
    ) -> List[Dict[str, Any]]:
        if not topic or not topic.strip():
            raise ValueError("topic 不能为空")
        if days < 1:
            raise ValueError("days 必须 >= 1")
        if frequency not in SUPPORTED_FREQUENCIES:
            raise ValueError(
                f"frequency 不支持: {frequency}，可选: {', '.join(SUPPORTED_FREQUENCIES)}"
            )

        schedule_start = self._parse_date(start_date) if start_date else date.today()
        base_time = self._parse_time(preferred_time)
        step_days = SUPPORTED_FREQUENCIES[frequency]
        slots = max(1, math.ceil(days / step_days))
        created_at = datetime.now().isoformat(timespec="seconds")

        created_items: List[Dict[str, Any]] = []
        with self._connect() as conn:
            for i in range(slots):
                target_date = schedule_start + timedelta(days=i * step_days)
                target_dt = datetime.combine(target_date, base_time)
                resolved_dt = self._resolve_time_conflict(conn, platform, target_dt)
                publish_time = resolved_dt.isoformat(timespec="minutes")

                cursor = conn.execute(
                    """
                    INSERT INTO schedules(topic, platform, publish_time, status, created_at, updated_at)
                    VALUES (?, ?, ?, 'planned', ?, ?)
                    """,
                    (topic.strip(), platform.strip(), publish_time, created_at, created_at),
                )
                item_id = int(cursor.lastrowid)
                created_items.append(
                    {
                        "id": item_id,
                        "topic": topic.strip(),
                        "platform": platform.strip(),
                        "publish_time": publish_time,
                        "status": "planned",
                    }
                )

        return created_items

    def list_schedule(
        self,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        limit = max(1, min(limit, 500))

        query = "SELECT * FROM schedules WHERE 1=1"
        params: List[Any] = []

        if date_from:
            query += " AND publish_time >= ?"
            params.append(
                self._parse_datetime_filter(date_from, is_end=False).isoformat(
                    timespec="minutes"
                )
            )
        if date_to:
            query += " AND publish_time <= ?"
            params.append(
                self._parse_datetime_filter(date_to, is_end=True).isoformat(
                    timespec="minutes"
                )
            )
        if status:
            query += " AND status = ?"
            params.append(status)

        query += " ORDER BY publish_time ASC LIMIT ?"
        params.append(limit)

        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]

    def reschedule(self, item_id: int, new_time: str) -> Dict[str, Any]:
        target = self._parse_datetime(new_time)

        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, platform FROM schedules WHERE id = ?", (item_id,)
            ).fetchone()
            if not row:
                raise ValueError(f"schedule id 不存在: {item_id}")

            resolved_dt = self._resolve_time_conflict(
                conn, row["platform"], target, exclude_id=item_id
            )
            now = datetime.now().isoformat(timespec="seconds")
            publish_time = resolved_dt.isoformat(timespec="minutes")

            conn.execute(
                "UPDATE schedules SET publish_time = ?, updated_at = ? WHERE id = ?",
                (publish_time, now, item_id),
            )

            updated = conn.execute(
                "SELECT * FROM schedules WHERE id = ?", (item_id,)
            ).fetchone()
            return dict(updated)

    @staticmethod
    def _parse_date(value: str) -> date:
        return datetime.strptime(value, "%Y-%m-%d").date()

    @staticmethod
    def _parse_time(value: str) -> time:
        for fmt in ("%H:%M", "%H:%M:%S"):
            try:
                return datetime.strptime(value, fmt).time()
            except ValueError:
                continue
        raise ValueError("preferred_time 必须是 HH:MM 或 HH:MM:SS")

    @staticmethod
    def _parse_datetime(value: str) -> datetime:
        candidates = [
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d",
        ]
        for fmt in candidates:
            try:
                parsed = datetime.strptime(value, fmt)
                if fmt == "%Y-%m-%d":
                    return parsed.replace(hour=20, minute=0, second=0)
                return parsed
            except ValueError:
                continue
        raise ValueError("时间格式不合法，使用 YYYY-MM-DD 或 YYYY-MM-DD HH:MM")

    @staticmethod
    def _parse_datetime_filter(value: str, is_end: bool) -> datetime:
        parsed = ScheduleService._parse_datetime(value)
        if len(value) == 10:
            if is_end:
                return parsed.replace(hour=23, minute=59, second=59)
            return parsed.replace(hour=0, minute=0, second=0)
        return parsed

    def _resolve_time_conflict(
        self,
        conn: sqlite3.Connection,
        platform: str,
        candidate: datetime,
        exclude_id: Optional[int] = None,
    ) -> datetime:
        resolved = candidate
        for _ in range(48):
            sql = "SELECT 1 FROM schedules WHERE platform = ? AND publish_time = ?"
            params: List[Any] = [platform, resolved.isoformat(timespec="minutes")]
            if exclude_id is not None:
                sql += " AND id != ?"
                params.append(exclude_id)
            row = conn.execute(sql, params).fetchone()
            if not row:
                return resolved
            resolved += timedelta(minutes=30)
        raise ValueError("排期冲突过多，无法自动分配时间")
