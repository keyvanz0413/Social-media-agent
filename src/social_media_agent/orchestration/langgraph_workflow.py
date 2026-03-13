"""LangGraph-based deterministic workflow for content/schedule tasks."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Literal, Optional, TypedDict

from langgraph.graph import END, StateGraph

from social_media_agent.agents.reviewers.compliance_reviewer import review_compliance_native
from social_media_agent.agents.reviewers.quality_reviewer import review_quality_native
from social_media_agent.config import Config
from social_media_agent.core.errors import ErrorCode
from social_media_agent.tools.content_analyst import analyze_xiaohongshu_native
from social_media_agent.tools.content_creator import create_content_native
from social_media_agent.tools.scheduler_tools import create_schedule_native


class WorkflowState(TypedDict, total=False):
    task: str
    mode: Literal["content", "schedule"]
    topic: str
    limit: int
    analysis: Dict[str, Any]
    creation: Dict[str, Any]
    quality: Dict[str, Any]
    compliance: Dict[str, Any]
    success: bool
    message: str
    error_code: str
    trace_id: str


def run_task_with_langgraph(task: str, quality_threshold: float = 8.0) -> Dict[str, Any]:
    """Execute task via LangGraph and return structured result."""
    trace_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    graph = _build_graph(quality_threshold=quality_threshold)
    final_state = graph.invoke({"task": task, "trace_id": trace_id})
    result = {
        "success": bool(final_state.get("success", False)),
        "message": final_state.get("message", ""),
        "mode": final_state.get("mode", "content"),
        "result": {
            "analysis": final_state.get("analysis"),
            "creation": final_state.get("creation"),
            "quality": final_state.get("quality"),
            "compliance": final_state.get("compliance"),
        },
    }
    if final_state.get("error_code"):
        result["error_code"] = final_state["error_code"]
    trace_path = _write_graph_trace(final_state)
    result["trace_path"] = str(trace_path)
    return result


def _build_graph(quality_threshold: float):
    graph = StateGraph(WorkflowState)
    graph.add_node("route", _route_task)
    graph.add_node("schedule", _do_schedule)
    graph.add_node("analyze", _do_analyze)
    graph.add_node("create", _do_create)
    graph.add_node("review", lambda s: _do_review(s, quality_threshold=quality_threshold))

    graph.set_entry_point("route")
    graph.add_conditional_edges(
        "route",
        _route_next,
        {"schedule": "schedule", "content": "analyze"},
    )
    graph.add_edge("schedule", END)
    graph.add_edge("analyze", "create")
    graph.add_edge("create", "review")
    graph.add_edge("review", END)
    return graph.compile()


def _route_task(state: WorkflowState) -> WorkflowState:
    task = state.get("task", "")
    mode = "schedule" if _is_schedule_task(task) else "content"
    return {"mode": mode, "task": task, "topic": _extract_topic(task), "limit": _extract_limit(task)}


def _route_next(state: WorkflowState) -> str:
    return "schedule" if state.get("mode") == "schedule" else "content"


def _do_schedule(state: WorkflowState) -> WorkflowState:
    task = state.get("task", "")
    payload = create_schedule_native(
        topic=_extract_topic(task),
        days=_extract_days(task),
        frequency=_extract_frequency(task),
        preferred_time=_extract_time(task) or "20:00",
    )
    success = bool(payload.get("success"))
    return {
        "success": success,
        "message": payload.get("message", "排期执行完成"),
        "creation": payload.get("data"),
        "error_code": None if success else ErrorCode.SCHEDULER_ERROR.value,
    }


def _do_analyze(state: WorkflowState) -> WorkflowState:
    payload = analyze_xiaohongshu_native(
        keyword=state.get("topic", "通用主题"),
        limit=state.get("limit", 5),
        quality_level="balanced",
    )
    success = bool(payload.get("success", True))
    return {
        "analysis": payload,
        "success": success,
        "message": payload.get("message", "分析完成"),
        "error_code": None if success else ErrorCode.LLM_ERROR.value,
    }


def _do_create(state: WorkflowState) -> WorkflowState:
    analysis = state.get("analysis") or {}
    payload = create_content_native(
        analysis_result=analysis,
        topic=state.get("topic", "通用主题"),
        style="casual",
        quality_level="balanced",
    )
    success = bool(payload.get("success", True))
    return {
        "creation": payload,
        "success": success,
        "message": payload.get("message", "创作完成"),
        "error_code": None if success else ErrorCode.LLM_ERROR.value,
    }


def _do_review(state: WorkflowState, quality_threshold: float) -> WorkflowState:
    creation = state.get("creation") or {}
    content = creation.get("data") if "data" in creation else creation
    quality = review_quality_native(content, quality_level="balanced")
    compliance = review_compliance_native(content, quality_level="balanced")
    quality_score = float(quality.get("data", {}).get("score", 0))
    compliance_score = float(compliance.get("data", {}).get("score", 0))
    passed = quality_score >= quality_threshold and compliance_score >= 7.0
    return {
        "quality": quality,
        "compliance": compliance,
        "success": passed,
        "message": (
            f"评审通过（质量 {quality_score}/10，合规 {compliance_score}/10）"
            if passed
            else f"评审未通过（质量 {quality_score}/10，合规 {compliance_score}/10）"
        ),
        "error_code": None if passed else ErrorCode.REVIEW_ERROR.value,
    }


def _write_graph_trace(state: WorkflowState) -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = Config.LOGS_DIR / f"graph_trace_{ts}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    return path


def _is_schedule_task(task: str) -> bool:
    keywords = ("排期", "日历", "计划", "连更", "schedule")
    lower = (task or "").lower()
    return any(k in task for k in keywords if k != "schedule") or "schedule" in lower


def _extract_limit(task: str) -> int:
    import re

    m = re.search(r"(参考|看|分析)\s*(\d+)\s*篇", task)
    if m:
        return max(3, min(10, int(m.group(2))))
    m = re.search(r"(\d+)\s*篇", task)
    if m:
        return max(3, min(10, int(m.group(1))))
    return 5


def _extract_days(task: str) -> int:
    import re

    m = re.search(r"(\d+)\s*天", task)
    if m:
        return max(1, int(m.group(1)))
    m = re.search(r"(\d+)\s*周", task)
    if m:
        return max(1, int(m.group(1))) * 7
    return 7


def _extract_frequency(task: str) -> str:
    if "每周" in task or "weekly" in task.lower():
        return "weekly"
    if "隔天" in task or "每两天" in task:
        return "every_2_days"
    return "daily"


def _extract_time(task: str) -> Optional[str]:
    import re

    m = re.search(r"(\d{1,2}):(\d{2})", task)
    if m:
        hh = max(0, min(23, int(m.group(1))))
        mm = max(0, min(59, int(m.group(2))))
        return f"{hh:02d}:{mm:02d}"
    return None


def _extract_topic(task: str) -> str:
    import re

    text = (task or "").strip()
    text = re.sub(r"^(写|创作|发布|发表|做|生成)一篇", "", text)
    text = re.sub(r"(帖子|笔记|内容|攻略)", "", text)
    text = re.sub(r"参考\d+篇.*$", "", text)
    text = text.strip("，。！？,.! ")
    return text[:30] if text else "通用主题"
