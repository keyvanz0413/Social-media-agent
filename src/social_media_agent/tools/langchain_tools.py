"""
LangChain StructuredTool registry.

This module provides:
1) Pydantic args schema for each tool
2) Adapter functions that normalize input/output
3) A single factory to build StructuredTool objects
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Literal, Optional

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from social_media_agent.agents.reviewers.compliance_reviewer import review_compliance_native
from social_media_agent.agents.reviewers.engagement_reviewer import review_engagement_native
from social_media_agent.agents.reviewers.quality_reviewer import review_quality_native
from social_media_agent.tools.content_analyst import analyze_xiaohongshu_native
from social_media_agent.tools.content_creator import create_content_native
from social_media_agent.tools.image_generator import (
    generate_images_for_content_native,
    generate_images_from_draft_native,
)
from social_media_agent.tools.memory_tools import (
    list_recent_memories_native,
    save_memory_native,
    search_memory_native,
)
from social_media_agent.tools.publisher import publish_to_xiaohongshu_native
from social_media_agent.tools.scheduler_tools import (
    create_schedule_native,
    list_schedule_native,
    reschedule_native,
)


class AnalyzeXiaohongshuArgs(BaseModel):
    keyword: str = Field(..., description="搜索关键词")
    limit: int = Field(5, ge=3, le=10, description="参考帖子数量（3-10）")
    quality_level: Literal["fast", "balanced", "high"] = Field(
        "balanced", description="质量级别"
    )


class CreateContentArgs(BaseModel):
    analysis_result: Any = Field(..., description="分析结果（dict 或 JSON 字符串）")
    topic: str = Field(..., description="创作主题")
    style: Literal["casual", "professional", "storytelling"] = Field(
        "casual", description="文风"
    )
    quality_level: Literal["fast", "balanced", "high"] = Field(
        "balanced", description="质量级别"
    )


class GenerateImagesForContentArgs(BaseModel):
    image_suggestions: Any = Field(..., description="图片建议（list 或 JSON 字符串）")
    topic: str = Field(..., description="主题")
    count: Optional[int] = Field(None, ge=1, le=12, description="生成数量")
    method: Literal["dalle", "local", "unsplash", "pexels"] = Field(
        "dalle", description="生成方式"
    )
    save_to_disk: bool = Field(True, description="是否保存到本地")


class GenerateImagesFromDraftArgs(BaseModel):
    draft_id: str = Field(..., description="草稿 ID")
    method: Literal["dalle", "local", "unsplash", "pexels"] = Field(
        "dalle", description="生成方式"
    )
    count: Optional[int] = Field(None, ge=1, le=12, description="生成数量")


class ReviewContentArgs(BaseModel):
    content_data: Dict[str, Any] = Field(..., description="待评审内容")
    quality_level: Literal["fast", "balanced", "high"] = Field(
        "balanced", description="质量级别"
    )


class PublishArgs(BaseModel):
    title: str = Field(..., description="标题（<=20字）")
    content: str = Field(..., description="正文（<=1000字）")
    images: Optional[List[str]] = Field(None, description="图片路径或 URL 列表")
    video_path: Optional[str] = Field(None, description="视频路径")
    tags: Optional[List[str]] = Field(None, description="标签列表")


class SaveMemoryArgs(BaseModel):
    item_type: str = Field(..., description="记忆类型，如 user_preference/review_summary")
    content: str = Field(..., description="记忆内容")
    metadata: Optional[Dict[str, Any]] = Field(None, description="附加元数据")
    source: str = Field("agent", description="来源")


class SearchMemoryArgs(BaseModel):
    query: str = Field(..., description="检索 query")
    top_k: int = Field(5, ge=1, le=20, description="返回条数")
    item_type: Optional[str] = Field(None, description="记忆类型过滤")


class ListRecentMemoriesArgs(BaseModel):
    limit: int = Field(20, ge=1, le=100, description="返回条数")
    item_type: Optional[str] = Field(None, description="记忆类型过滤")


class CreateScheduleArgs(BaseModel):
    topic: str = Field(..., description="排期主题")
    days: int = Field(7, ge=1, le=365, description="覆盖天数")
    frequency: Literal["daily", "every_2_days", "weekly"] = Field(
        "daily", description="频率"
    )
    start_date: Optional[str] = Field(None, description="开始日期 YYYY-MM-DD")
    preferred_time: str = Field("20:00", description="发布时间 HH:MM")
    platform: str = Field("xiaohongshu", description="平台")


class ListScheduleArgs(BaseModel):
    date_from: Optional[str] = Field(None, description="开始时间过滤")
    date_to: Optional[str] = Field(None, description="结束时间过滤")
    status: Optional[str] = Field(None, description="状态过滤")
    limit: int = Field(50, ge=1, le=500, description="返回条数")


class RescheduleArgs(BaseModel):
    item_id: int = Field(..., ge=1, description="排期 ID")
    new_time: str = Field(..., description="新时间 YYYY-MM-DD HH:MM")


def _analyze_xiaohongshu_adapter(keyword: str, limit: int = 5, quality_level: str = "balanced") -> Dict[str, Any]:
    return analyze_xiaohongshu_native(keyword=keyword, limit=limit, quality_level=quality_level)


def _create_content_adapter(
    analysis_result: Any,
    topic: str,
    style: str = "casual",
    quality_level: str = "balanced",
) -> Dict[str, Any]:
    return create_content_native(
        analysis_result=analysis_result,
        topic=topic,
        style=style,
        quality_level=quality_level,
    )


def _generate_images_for_content_adapter(
    image_suggestions: Any,
    topic: str,
    count: Optional[int] = None,
    method: str = "dalle",
    save_to_disk: bool = True,
) -> Dict[str, Any]:
    suggestions = image_suggestions
    if isinstance(suggestions, (dict, list)):
        suggestions = json.dumps(suggestions, ensure_ascii=False)
    return generate_images_for_content_native(
        image_suggestions=suggestions,
        topic=topic,
        count=count,
        method=method,
        save_to_disk=save_to_disk,
    )


def _generate_images_from_draft_adapter(
    draft_id: str,
    method: str = "dalle",
    count: Optional[int] = None,
) -> Dict[str, Any]:
    return generate_images_from_draft_native(draft_id=draft_id, method=method, count=count)


def _review_engagement_adapter(content_data: Dict[str, Any], quality_level: str = "balanced") -> Dict[str, Any]:
    _ = quality_level
    return review_engagement_native(content_data=content_data)


def _review_quality_adapter(content_data: Dict[str, Any], quality_level: str = "balanced") -> Dict[str, Any]:
    return review_quality_native(content_data=content_data, quality_level=quality_level)


def _review_compliance_adapter(content_data: Dict[str, Any], quality_level: str = "balanced") -> Dict[str, Any]:
    return review_compliance_native(content_data=content_data, quality_level=quality_level)


def _publish_to_xiaohongshu_adapter(
    title: str,
    content: str,
    images: Optional[List[str]] = None,
    video_path: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    return publish_to_xiaohongshu_native(
        title=title,
        content=content,
        images=images,
        video_path=video_path,
        tags=tags,
    )


def _save_memory_adapter(
    item_type: str,
    content: str,
    metadata: Optional[Dict[str, Any]] = None,
    source: str = "agent",
) -> Dict[str, Any]:
    return save_memory_native(
        item_type=item_type,
        content=content,
        metadata=metadata,
        source=source,
    )


def _search_memory_adapter(
    query: str,
    top_k: int = 5,
    item_type: Optional[str] = None,
) -> Dict[str, Any]:
    return search_memory_native(query=query, top_k=top_k, item_type=item_type)


def _list_recent_memories_adapter(
    limit: int = 20,
    item_type: Optional[str] = None,
) -> Dict[str, Any]:
    return list_recent_memories_native(limit=limit, item_type=item_type)


def _create_schedule_adapter(
    topic: str,
    days: int = 7,
    frequency: str = "daily",
    start_date: Optional[str] = None,
    preferred_time: str = "20:00",
    platform: str = "xiaohongshu",
) -> Dict[str, Any]:
    return create_schedule_native(
        topic=topic,
        days=days,
        frequency=frequency,
        start_date=start_date,
        preferred_time=preferred_time,
        platform=platform,
    )


def _list_schedule_adapter(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
) -> Dict[str, Any]:
    return list_schedule_native(date_from=date_from, date_to=date_to, status=status, limit=limit)


def _reschedule_adapter(item_id: int, new_time: str) -> Dict[str, Any]:
    return reschedule_native(item_id=item_id, new_time=new_time)


def get_structured_tools() -> List[StructuredTool]:
    """Build all StructuredTool instances with explicit schema."""
    return [
        StructuredTool.from_function(
            func=_analyze_xiaohongshu_adapter,
            name="analyze_xiaohongshu",
            description="分析小红书指定关键词的热门内容，提取标题模式、用户需求与创作建议。",
            args_schema=AnalyzeXiaohongshuArgs,
        ),
        StructuredTool.from_function(
            func=_create_content_adapter,
            name="create_content",
            description="基于分析结果生成内容草稿，输出标题、正文、标签与配图建议。",
            args_schema=CreateContentArgs,
        ),
        StructuredTool.from_function(
            func=_generate_images_for_content_adapter,
            name="generate_images_for_content",
            description="根据图片建议为内容生成配图。",
            args_schema=GenerateImagesForContentArgs,
        ),
        StructuredTool.from_function(
            func=_generate_images_from_draft_adapter,
            name="generate_images_from_draft",
            description="读取草稿并生成图片。",
            args_schema=GenerateImagesFromDraftArgs,
        ),
        StructuredTool.from_function(
            func=_review_engagement_adapter,
            name="review_engagement",
            description="评估内容互动潜力（点赞/收藏/评论）。",
            args_schema=ReviewContentArgs,
        ),
        StructuredTool.from_function(
            func=_review_quality_adapter,
            name="review_quality",
            description="评估内容质量（语法、结构、可读性）。",
            args_schema=ReviewContentArgs,
        ),
        StructuredTool.from_function(
            func=_review_compliance_adapter,
            name="review_compliance",
            description="评估内容合规性（平台规范与风险项）。",
            args_schema=ReviewContentArgs,
        ),
        StructuredTool.from_function(
            func=_publish_to_xiaohongshu_adapter,
            name="publish_to_xiaohongshu",
            description="发布内容到小红书。",
            args_schema=PublishArgs,
        ),
        StructuredTool.from_function(
            func=_save_memory_adapter,
            name="save_memory",
            description="保存长期记忆条目（偏好/复盘/上下文）。",
            args_schema=SaveMemoryArgs,
        ),
        StructuredTool.from_function(
            func=_search_memory_adapter,
            name="search_memory",
            description="检索长期记忆（语义相似 + 类型过滤）。",
            args_schema=SearchMemoryArgs,
        ),
        StructuredTool.from_function(
            func=_list_recent_memories_adapter,
            name="list_recent_memories",
            description="查询最近写入的记忆。",
            args_schema=ListRecentMemoriesArgs,
        ),
        StructuredTool.from_function(
            func=_create_schedule_adapter,
            name="create_schedule",
            description="创建内容排期计划。",
            args_schema=CreateScheduleArgs,
        ),
        StructuredTool.from_function(
            func=_list_schedule_adapter,
            name="list_schedule",
            description="查询排期计划列表。",
            args_schema=ListScheduleArgs,
        ),
        StructuredTool.from_function(
            func=_reschedule_adapter,
            name="reschedule",
            description="调整排期项发布时间。",
            args_schema=RescheduleArgs,
        ),
    ]
