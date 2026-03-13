"""
Reason -> Act -> Observe loop controller.
"""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime
from importlib import import_module
from pathlib import Path
from typing import Any, Dict, Optional

from social_media_agent.agents.reviewers.compliance_reviewer import review_compliance
from social_media_agent.agents.reviewers.quality_reviewer import review_quality
from social_media_agent.config import Config
from social_media_agent.memory import get_memory_service
from social_media_agent.tools.content_analyst import analyze_xiaohongshu
from social_media_agent.tools.content_creator import create_content
from social_media_agent.tools.scheduler_tools import create_schedule

logger = logging.getLogger(__name__)

MEMORY_TYPE_WEIGHTS = {
    "user_preference": 1.3,
    "review_summary": 1.1,
    "memory": 1.0,
}


def _runtime_config():
    """Get Config class at runtime to avoid stale references after module reloads."""
    return import_module("social_media_agent.config").Config


def run_task_with_loop(
    task: str,
    max_iterations: int = 3,
    quality_threshold: float = 8.0,
) -> Dict[str, Any]:
    """
    Execute task with a controlled Reason->Act->Observe loop.
    """
    started_at = datetime.now()
    trace = {
        "task": task,
        "started_at": started_at.isoformat(timespec="seconds"),
        "mode": "content",
        "steps": [],
    }

    if _is_schedule_task(task):
        trace["mode"] = "schedule"
        result = _run_schedule_loop(task=task, trace=trace)
    else:
        result = _run_content_loop(
            task=task,
            trace=trace,
            max_iterations=max(1, max_iterations),
            quality_threshold=quality_threshold,
        )

    finished_at = datetime.now()
    trace["finished_at"] = finished_at.isoformat(timespec="seconds")
    trace["duration_sec"] = round((finished_at - started_at).total_seconds(), 3)
    trace["success"] = result.get("success", False)

    trace_path = _write_trace(trace)
    result["trace_path"] = str(trace_path)
    return result


def _run_schedule_loop(task: str, trace: Dict[str, Any]) -> Dict[str, Any]:
    topic = _extract_topic(task)
    days = _extract_days(task)
    frequency = _extract_frequency(task)
    preferred_time = _extract_time(task) or "20:00"

    _append_step(
        trace,
        phase="reason",
        detail="识别为排期任务，进入排期工具链",
        context={"topic": topic, "days": days, "frequency": frequency},
    )

    raw = create_schedule(
        topic=topic,
        days=days,
        frequency=frequency,
        preferred_time=preferred_time,
    )
    parsed = _safe_json(raw)
    _append_step(trace, phase="act", detail="调用 create_schedule", context={"raw": parsed})

    if not parsed.get("success"):
        return {
            "success": False,
            "message": f"排期失败: {parsed.get('error', '未知错误')}",
            "result": parsed,
        }

    count = parsed.get("data", {}).get("count", 0)
    msg = f"排期创建完成：主题「{topic}」，共 {count} 条。"
    return {"success": True, "message": msg, "result": parsed}


def _run_content_loop(
    task: str,
    trace: Dict[str, Any],
    max_iterations: int,
    quality_threshold: float,
) -> Dict[str, Any]:
    topic = _extract_topic(task)
    limit = _extract_limit(task)
    memory_service = get_memory_service()

    memory_hits = memory_service.search_memory(query=topic, top_k=3, item_type="review_summary")
    preference_hits = memory_service.search_memory(query=topic, top_k=2, item_type="user_preference")
    memory_context = _build_memory_context(memory_hits + preference_hits)
    _append_step(
        trace,
        phase="observe",
        detail="检索历史记忆",
        context={
            "memory_hits": len(memory_hits),
            "preference_hits": len(preference_hits),
            "memory_context_preview": memory_context[:120],
        },
    )

    raw_analysis = analyze_xiaohongshu(keyword=topic, limit=limit, quality_level="balanced")
    analysis = _safe_json(raw_analysis)
    _append_step(
        trace,
        phase="act",
        detail="调用 analyze_xiaohongshu",
        context={"limit": limit, "analysis_keys": list(analysis.keys())[:8]},
    )

    feedback_hint = ""
    best_payload: Optional[Dict[str, Any]] = None
    best_score = -1.0

    for i in range(1, max_iterations + 1):
        reason = "首次生成内容草稿" if i == 1 else "上一轮评分不足，执行重写"
        _append_step(trace, phase="reason", detail=reason, context={"iteration": i})

        analysis_for_creation = _inject_feedback(analysis, feedback_hint, memory_context)
        raw_creation = create_content(
            analysis_result=json.dumps(analysis_for_creation, ensure_ascii=False),
            topic=topic,
            style="casual",
            quality_level="balanced",
        )
        creation = _safe_json(raw_creation)
        content_payload = _extract_creation_payload(creation)
        _append_step(
            trace,
            phase="act",
            detail="调用 create_content",
            context={"iteration": i, "title": content_payload.get("title", "")[:30]},
        )

        raw_quality = review_quality(content_payload, quality_level="balanced")
        raw_compliance = review_compliance(content_payload, quality_level="balanced")
        quality = _safe_json(raw_quality)
        compliance = _safe_json(raw_compliance)

        quality_score = float(quality.get("data", {}).get("score", 0))
        compliance_score = float(compliance.get("data", {}).get("score", 0))
        passed = quality_score >= quality_threshold and compliance_score >= 7.0

        _append_step(
            trace,
            phase="observe",
            detail="评审结果",
            context={
                "iteration": i,
                "quality_score": quality_score,
                "compliance_score": compliance_score,
                "passed": passed,
            },
        )

        memory_service.save_memory(
            item_type="review_summary",
            content=f"主题:{topic}; 质量:{quality_score}; 合规:{compliance_score}; 第{i}轮",
            metadata={"task": task, "iteration": i, "passed": passed},
            source="loop_controller",
        )

        if quality_score > best_score:
            best_score = quality_score
            best_payload = {
                "creation": creation,
                "content": content_payload,
                "quality": quality,
                "compliance": compliance,
                "iteration": i,
                "passed": passed,
            }

        if passed:
            title = content_payload.get("title", "未命名草稿")
            return {
                "success": True,
                "message": f"任务完成（第{i}轮通过）。标题：{title}",
                "result": best_payload,
            }

        feedback_hint = _build_feedback_hint(quality=quality, compliance=compliance)

    title = (best_payload or {}).get("content", {}).get("title", "未命名草稿")
    return {
        "success": False,
        "message": f"达到最大迭代次数({max_iterations})，最佳草稿标题：{title}",
        "result": best_payload,
    }


def _extract_creation_payload(creation: Dict[str, Any]) -> Dict[str, Any]:
    if "success" in creation:
        return creation.get("data") or {}
    return creation


def _inject_feedback(analysis: Dict[str, Any], feedback: str, memory_context: str = "") -> Dict[str, Any]:
    updated = dict(analysis or {})
    if feedback:
        updated["rewrite_feedback"] = feedback
    if memory_context:
        updated["memory_context"] = memory_context
        existing = updated.get("creation_suggestions")
        # 把记忆信息显式并入创作建议，确保 creator prompt 能看到
        if isinstance(existing, list):
            updated["creation_suggestions"] = existing + [f"结合历史记忆：{memory_context}"]
        elif isinstance(existing, dict):
            merged = dict(existing)
            merged["memory_context"] = memory_context
            updated["creation_suggestions"] = merged
        else:
            updated["creation_suggestions"] = [f"结合历史记忆：{memory_context}"]
    return updated


def _build_feedback_hint(quality: Dict[str, Any], compliance: Dict[str, Any]) -> str:
    q_suggestions = quality.get("data", {}).get("suggestions", []) or []
    c_suggestions = compliance.get("data", {}).get("suggestions", []) or []
    merged = (q_suggestions + c_suggestions)[:4]
    if not merged:
        return "请强化结构清晰度和可读性。"
    return "；".join(merged)


def _build_memory_context(items: Any) -> str:
    rows = list(items or [])
    scored_rows = sorted(rows, key=_memory_rank_score, reverse=True)

    lines = []
    seen = set()
    max_chars = max(40, int(_runtime_config().MEMORY_CONTEXT_MAX_CHARS))
    current_len = 0

    for row in scored_rows:
        text = (row.get("content") or "").strip()
        if not text:
            continue

        dedupe_key = text[:60]
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)

        item_type = row.get("item_type", "memory")
        score = row.get("score")
        if score is None:
            line = f"[{item_type}] {text[:80]}"
        else:
            line = f"[{item_type}|score={score}] {text[:80]}"

        new_len = current_len + len(line) + (1 if lines else 0)
        if new_len > max_chars:
            if not lines:
                lines.append(line[:max_chars])
            break

        lines.append(line)
        current_len = new_len
        if len(lines) >= 4:
            break
    return "；".join(lines)


def _memory_rank_score(row: Dict[str, Any]) -> float:
    item_type = row.get("item_type", "memory")
    weight = MEMORY_TYPE_WEIGHTS.get(item_type, 1.0)
    raw_score = row.get("score")
    if raw_score is None:
        base = 0.5
    else:
        try:
            score_val = float(raw_score)
            # fallback 通常是相似度(0~1, 越大越好)
            if 0.0 <= score_val <= 1.0:
                base = score_val
            # faiss 常见是距离(>=0, 越小越好)
            elif score_val >= 0:
                base = 1.0 / (1.0 + score_val)
            else:
                base = 0.5
        except Exception:
            base = 0.5
    return base * weight


def _is_schedule_task(task: str) -> bool:
    keywords = ("排期", "日历", "计划", "连更", "schedule")
    lower = (task or "").lower()
    return any(k in task for k in keywords if k != "schedule") or "schedule" in lower


def _extract_limit(task: str) -> int:
    m = re.search(r"(参考|看|分析)\s*(\d+)\s*篇", task)
    if m:
        return max(3, min(10, int(m.group(2))))
    m = re.search(r"(\d+)\s*篇", task)
    if m:
        return max(3, min(10, int(m.group(1))))
    return 5


def _extract_days(task: str) -> int:
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
    m = re.search(r"(\d{1,2}):(\d{2})", task)
    if m:
        hh = max(0, min(23, int(m.group(1))))
        mm = max(0, min(59, int(m.group(2))))
        return f"{hh:02d}:{mm:02d}"
    return None


def _extract_topic(task: str) -> str:
    text = (task or "").strip()
    text = re.sub(r"^(写|创作|发布|发表|做|生成)一篇", "", text)
    text = re.sub(r"(帖子|笔记|内容|攻略)", "", text)
    text = re.sub(r"参考\d+篇.*$", "", text)
    text = text.strip("，。！？,.! ")
    return text[:30] if text else "通用主题"


def _safe_json(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            return json.loads(value)
        except Exception:
            return {"success": False, "error": f"JSON解析失败: {value[:120]}"}
    return {"success": False, "error": "未知响应格式"}


def _append_step(trace: Dict[str, Any], phase: str, detail: str, context: Optional[Dict[str, Any]] = None) -> None:
    trace["steps"].append(
        {
            "at": datetime.now().isoformat(timespec="seconds"),
            "phase": phase,
            "detail": detail,
            "context": context or {},
        }
    )


def _write_trace(trace: Dict[str, Any]) -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = _runtime_config().LOGS_DIR / f"loop_trace_{ts}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(trace, f, ensure_ascii=False, indent=2)
    return path
