"""
内容分析工具 - 分析小红书热门内容
"""

import json
import logging
from typing import Dict, Any, List
from datetime import datetime
from functools import lru_cache

from social_media_agent.utils.mcp_client import XiaohongshuMCPClient
from social_media_agent.utils.llm_client import LLMClient
from social_media_agent.utils.model_router import ModelRouter, TaskType, QualityLevel
from social_media_agent.utils.common_tools import parse_llm_json, handle_tool_errors
from social_media_agent.config import Config

logger = logging.getLogger(__name__)


@handle_tool_errors("内容分析")
def analyze_xiaohongshu(
    keyword: str,
    limit: int = 5,
    quality_level: str = "balanced"
) -> str:
    """
    分析小红书平台上指定关键词的热门内容
    
    Args:
        keyword: 搜索关键词
        limit: 参考帖子数量（3-10条）
        quality_level: 质量级别（fast/balanced/high）
        
    Returns:
        JSON格式的分析结果
    """
    return json.dumps(
        analyze_xiaohongshu_native(
            keyword=keyword,
            limit=limit,
            quality_level=quality_level,
        ),
        ensure_ascii=False,
        indent=2,
    )


def analyze_xiaohongshu_native(
    keyword: str,
    limit: int = 5,
    quality_level: str = "balanced"
) -> Dict[str, Any]:
    """Analyze notes and return structured dict result."""
    logger.info(f"开始分析关键词: {keyword}, 数量: {limit}")

    # 1. 收集笔记数据（使用缓存）
    notes = _collect_notes_cached(keyword, limit)

    if not notes:
        return {
            "success": False,
            "error": f"未找到关键词 '{keyword}' 的相关笔记",
            "message": "分析失败：未找到相关笔记",
        }

    logger.info(f"成功收集 {len(notes)} 条笔记")

    # 2. 数据清洗
    cleaned_notes = _clean_notes(notes)
    logger.info(f"数据清洗后剩余 {len(cleaned_notes)} 条有效笔记")

    # 3. 调用 LLM 分析
    analysis = _analyze_with_llm(cleaned_notes, keyword, quality_level)

    # 4. 补充元数据
    analysis["keyword"] = keyword
    analysis["total_analyzed"] = len(cleaned_notes)
    analysis["analysis_timestamp"] = datetime.now().isoformat()
    analysis.setdefault("success", True)
    analysis.setdefault("message", "分析完成")

    logger.info(f"分析完成，标题模式: {len(analysis.get('title_patterns', []))} 个")
    return analysis


@lru_cache(maxsize=128)
def _collect_notes_cached(keyword: str, limit: int) -> tuple:
    """
    收集笔记（带缓存）
    使用 @lru_cache 自动缓存，简单高效
    
    Note: 返回 tuple 而不是 list，因为 lru_cache 需要可哈希的参数
    """
    client = None
    try:
        client = XiaohongshuMCPClient(
            base_url=Config.MCP_URL,
            timeout=Config.MCP_TIMEOUT
        )
        result = client.search_notes(keyword=keyword, limit=limit)
        # 兼容不同返回格式，优先使用 feeds
        feeds = result.get("feeds") or result.get("notes") or []

        # 转换为 tuple 以便缓存
        return tuple(feeds)

    except Exception as e:
        logger.error(f"收集笔记失败: {str(e)}")
        raise
    finally:
        if client is not None:
            client.close()


def _clean_notes(notes: tuple) -> List[Dict[str, Any]]:
    """
    清洗和验证笔记数据
    
    Args:
        notes: 原始笔记数据
        
    Returns:
        清洗后的笔记列表
    """
    cleaned = []
    
    for note in notes:
        try:
            # 兼容两种数据结构
            note_card = note.get("noteCard", {})
            if note_card:
                title = note_card.get("displayTitle", "")
                content = note_card.get("desc", "")
                interact_info = note_card.get("interactInfo", {})
            else:
                title = note.get("title", "")
                # 兼容 desc/content 两种字段
                content = note.get("desc") or note.get("content", "")
                interact_info = note.get("interact_info", {})
                # 兼容 stats 结构
                if not interact_info and isinstance(note.get("stats"), dict):
                    interact_info = note.get("stats", {})
            
            # 验证必需字段
            if not title:
                continue
            
            # 获取互动数据
            likes = _parse_int(interact_info.get("likedCount") or interact_info.get("liked_count", 0))
            favorites = _parse_int(interact_info.get("collectedCount") or interact_info.get("collected_count", 0))
            comments = _parse_int(interact_info.get("commentCount") or interact_info.get("comment_count", 0))
            
            # 构建标准化数据
            cleaned_note = {
                "title": title.strip(),
                "content": content.strip() if content else title,
                "likes": likes,
                "favorites": favorites,
                "comments": comments
            }
            
            # 限制内容长度
            if len(cleaned_note["content"]) > 500:
                cleaned_note["content"] = cleaned_note["content"][:500] + "..."
            
            cleaned.append(cleaned_note)
        
        except Exception as e:
            logger.warning(f"处理笔记时出错: {str(e)}，跳过")
            continue
    
    return cleaned


def _parse_int(value) -> int:
    """安全地解析整数"""
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        text = value.strip().lower()
        if text.isdigit():
            return int(text)
        # 兼容社媒常见单位写法，如 1.2万 / 3k
        try:
            if text.endswith("万"):
                return int(float(text[:-1]) * 10000)
            if text.endswith("k"):
                return int(float(text[:-1]) * 1000)
        except ValueError:
            return 0
    return 0


def _analyze_with_llm(
    notes: List[Dict[str, Any]],
    keyword: str,
    quality_level: str
) -> Dict[str, Any]:
    """
    使用 LLM 分析笔记数据
    
    Args:
        notes: 清洗后的笔记列表
        keyword: 搜索关键词
        quality_level: 质量级别
        
    Returns:
        分析结果字典
    """
    # 加载提示词
    system_prompt = _load_system_prompt()
    user_prompt = _build_prompt(notes, keyword)
    
    # 选择模型
    router = ModelRouter()
    quality = QualityLevel[quality_level.upper()] if quality_level.upper() in ["FAST", "BALANCED", "HIGH"] else QualityLevel.BALANCED
    model_name = router.select_model(TaskType.ANALYSIS, quality)
    logger.info(f"选择分析模型: {model_name}")
    
    # 获取配置
    analyst_config = Config.AGENT_CONFIGS["content_analyst"]
    
    # 调用 LLM
    client = LLMClient()
    raw_response = client.call_llm(
        prompt=user_prompt,
        model_name=model_name,
        system_prompt=system_prompt,
        temperature=analyst_config["temperature"],
        max_tokens=analyst_config["max_tokens"]
    )
    
    # 解析响应（使用通用工具）
    analysis = parse_llm_json(raw_response)
    
    # 简单验证（只确保必需字段存在）
    required_fields = {
        "title_patterns": [],
        "user_needs": [],
        "hot_topics": [],
        "creation_suggestions": []
    }
    
    for field, default_value in required_fields.items():
        if field not in analysis:
            analysis[field] = default_value
    
    return analysis


def _load_system_prompt() -> str:
    """加载系统提示词"""
    prompt_path = Config.PROMPTS_DIR / "content_analyst.md"
    
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.warning(f"读取提示词失败: {str(e)}，使用默认提示词")
        return _get_default_prompt()


def _get_default_prompt() -> str:
    """获取默认提示词"""
    return """你是一位资深的小红书内容分析师，擅长挖掘爆款内容的规律和用户需求。

请分析提供的小红书笔记数据，提取以下信息：
1. 标题模式（疑问式、数字型、情绪词等）
2. 用户需求痛点
3. 热门话题标签
4. 创作建议（3-5个角度）

必须输出有效的 JSON 格式，包含字段：
- title_patterns: 标题模式列表
- user_needs: 用户需求列表
- hot_topics: 热门话题列表
- creation_suggestions: 创作建议列表

请直接输出 JSON，不要添加解释性文字。"""


def _build_prompt(notes: List[Dict[str, Any]], keyword: str) -> str:
    """构建分析提示词"""
    parts = [
        f"## 分析任务",
        f"分析关键词 '{keyword}' 的小红书热门笔记，提取创作灵感。\n",
        f"## 笔记数据（共 {len(notes)} 条）\n"
    ]
    
    # 添加笔记数据（最多10条）
    for i, note in enumerate(notes[:10], 1):
        parts.extend([
            f"### 笔记 {i}",
            f"标题: {note['title']}",
            f"内容: {note['content'][:200]}...",  # 限制长度
            f"互动: 点赞 {note['likes']}, 收藏 {note['favorites']}, 评论 {note['comments']}\n"
        ])
    
    # 输出要求
    parts.extend([
        "## 输出要求",
        "返回 JSON 格式，包含以下字段：",
        "- title_patterns: 标题模式列表",
        "- user_needs: 用户需求列表",
        "- hot_topics: 热门话题列表",
        "- creation_suggestions: 创作建议列表",
        "\n请直接输出 JSON。"
    ])
    
    return "\n".join(parts)


# 导出
# 向后兼容：为旧名称添加别名
agent_a_analyze_xiaohongshu = analyze_xiaohongshu

__all__ = ['analyze_xiaohongshu', 'agent_a_analyze_xiaohongshu']
