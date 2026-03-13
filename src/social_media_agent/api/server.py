"""
FastAPI server for Social Media Agent.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from social_media_agent.config import Config
from social_media_agent.memory import get_memory_service
from social_media_agent.orchestration.loop_controller import run_task_with_loop
from social_media_agent.tools.memory_tools import (
    list_recent_memories,
    save_memory,
    search_memory,
)
from social_media_agent.tools.scheduler_tools import (
    create_schedule,
    list_schedule,
    reschedule,
)


app = FastAPI(
    title="Social Media Agent API",
    version="1.2.0",
    description="Service endpoints for task execution, memory and scheduling.",
)


class RunTaskRequest(BaseModel):
    task: str = Field(..., min_length=1)
    max_iterations: int = Field(default=3, ge=1, le=10)
    quality_threshold: float = Field(default=8.0, ge=0.0, le=10.0)


class ScheduleCreateRequest(BaseModel):
    topic: str = Field(..., min_length=1)
    days: int = Field(default=7, ge=1, le=365)
    frequency: str = Field(default="daily")
    start_date: Optional[str] = None
    preferred_time: str = Field(default="20:00")
    platform: str = Field(default="xiaohongshu")


class ScheduleRescheduleRequest(BaseModel):
    item_id: int = Field(..., ge=1)
    new_time: str = Field(..., min_length=8)


class MemorySaveRequest(BaseModel):
    item_type: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
    metadata: Optional[Dict[str, Any]] = None
    source: str = Field(default="api")


class MemorySearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=50)
    item_type: Optional[str] = None


@app.get("/health")
def health() -> Dict[str, Any]:
    return {
        "success": True,
        "service": "social-media-agent",
        "time": datetime.now().isoformat(timespec="seconds"),
        "mock_mode": Config.MOCK_MODE,
    }


@app.post("/run-task")
def run_task(req: RunTaskRequest) -> Dict[str, Any]:
    result = run_task_with_loop(
        task=req.task,
        max_iterations=req.max_iterations,
        quality_threshold=req.quality_threshold,
    )
    code = 200 if result.get("success") else 422
    if code != 200:
        raise HTTPException(status_code=code, detail=result)
    return {"success": True, "data": result}


@app.post("/schedule/create")
def api_create_schedule(req: ScheduleCreateRequest) -> Dict[str, Any]:
    raw = create_schedule(
        topic=req.topic,
        days=req.days,
        frequency=req.frequency,
        start_date=req.start_date,
        preferred_time=req.preferred_time,
        platform=req.platform,
    )
    return _to_api_result(raw)


@app.get("/schedule/list")
def api_list_schedule(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
) -> Dict[str, Any]:
    raw = list_schedule(
        date_from=date_from,
        date_to=date_to,
        status=status,
        limit=limit,
    )
    return _to_api_result(raw)


@app.post("/schedule/reschedule")
def api_reschedule(req: ScheduleRescheduleRequest) -> Dict[str, Any]:
    raw = reschedule(item_id=req.item_id, new_time=req.new_time)
    return _to_api_result(raw)


@app.post("/memory/save")
def api_save_memory(req: MemorySaveRequest) -> Dict[str, Any]:
    raw = save_memory(
        item_type=req.item_type,
        content=req.content,
        metadata=json.dumps(req.metadata or {}, ensure_ascii=False),
        source=req.source,
    )
    return _to_api_result(raw)


@app.post("/memory/search")
def api_search_memory(req: MemorySearchRequest) -> Dict[str, Any]:
    raw = search_memory(query=req.query, top_k=req.top_k, item_type=req.item_type)
    return _to_api_result(raw)


@app.get("/memory/recent")
def api_recent_memory(limit: int = 20, item_type: Optional[str] = None) -> Dict[str, Any]:
    raw = list_recent_memories(limit=limit, item_type=item_type)
    return _to_api_result(raw)


@app.get("/memory/backend")
def api_memory_backend() -> Dict[str, Any]:
    service = get_memory_service()
    return {"success": True, "backend": service.backend}


def _to_api_result(raw: str) -> Dict[str, Any]:
    try:
        parsed = json.loads(raw) if isinstance(raw, str) else raw
    except Exception as e:
        raise HTTPException(status_code=500, detail={"success": False, "error": str(e)})

    if not parsed.get("success", False):
        raise HTTPException(status_code=422, detail=parsed)
    return parsed
