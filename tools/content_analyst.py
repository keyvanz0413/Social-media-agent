"""
Agent A: Content Analyst
分析小红书热门内容，提取创作灵感和数据洞察
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from utils.mcp_client import XiaohongshuMCPClient, XiaohongshuMCPError
from utils.cached_mcp_client import get_cached_mcp_client
from utils.cache_manager import get_cache_manager, cache_key
from utils.llm_client import LLMClient, LLMError
from utils.model_router import ModelRouter, TaskType, QualityLevel
from config import AgentConfig, PathConfig, BusinessConfig, MCPConfig

# 配置日志
logger = logging.getLogger(__name__)


def agent_a_analyze_xiaohongshu(
    keyword: str,
    limit: int = 5,
    quality_level: str = "balanced"
) -> str:
    """
    分析小红书平台上指定关键词的热门内容
    
    Args:
        keyword: 搜索关键词
        limit: 返回笔记数量，默认5条
        quality_level: 质量级别（fast/balanced/high），默认 balanced
        
    Returns:
        JSON格式的分析结果，包含：
        - keyword: 搜索关键词
        - total_analyzed: 分析的笔记数量
        - title_patterns: 标题模式列表
        - content_structure: 内容结构（开头、正文、结尾）
        - user_needs: 用户需求列表
        - hot_topics: 热门话题列表
        - interaction_stats: 互动数据统计
        - creation_suggestions: 创作建议列表
        
    Example:
        >>> result = agent_a_analyze_xiaohongshu("澳洲旅游", limit=5)
        >>> data = json.loads(result)
        >>> print(data["title_patterns"])
    """
    try:
        # 1. 收集笔记数据
        logger.info(f"开始分析关键词: {keyword}, 数量: {limit}")
        notes = _collect_notes(keyword, limit)
        
        if not notes or len(notes) == 0:
            error_msg = f"未找到关键词 '{keyword}' 的相关笔记"
            logger.error(error_msg)
            return json.dumps({
                "success": False,
                "error": error_msg,
                "message": "分析失败：未找到相关笔记"
            }, ensure_ascii=False)
        
        logger.info(f"成功收集 {len(notes)} 条笔记")
        
        # 2. 数据清洗和验证
        cleaned_notes = _clean_and_validate_notes(notes)
        if len(cleaned_notes) < 3:
            logger.warning(f"有效笔记数量不足: {len(cleaned_notes)}，建议增加搜索数量")
        
        logger.info(f"数据清洗后剩余 {len(cleaned_notes)} 条有效笔记")
        
        # 3. 调用 LLM 进行分析
        analysis = _analyze_with_llm(cleaned_notes, keyword, quality_level)
        
        # 4. 结果验证和修复（核心优化点）
        validated_result = _validate_and_fix_analysis_result(
            analysis=analysis,
            keyword=keyword,
            note_count=len(cleaned_notes),
            notes=cleaned_notes  # 用于降级统计
        )
        
        logger.info(f"分析完成，标题模式: {len(validated_result.get('title_patterns', []))} 个")
        return json.dumps(validated_result, ensure_ascii=False, indent=2)
        
    except XiaohongshuMCPError as e:
        error_msg = f"MCP 搜索失败: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return json.dumps({
            "success": False,
            "error": error_msg,
            "message": "分析失败：无法获取笔记数据"
        }, ensure_ascii=False)
        
    except LLMError as e:
        error_msg = f"LLM 分析失败: {str(e)}"
        logger.error(error_msg, exc_info=True)
        # 降级：返回基础统计结果
        logger.warning("使用降级策略：返回基础统计结果")
        fallback_result = _get_fallback_analysis(keyword, notes if 'notes' in locals() else [])
        return json.dumps(fallback_result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        error_msg = f"分析过程中发生未知错误: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return json.dumps({
            "success": False,
            "error": error_msg,
            "message": "分析失败"
        }, ensure_ascii=False)


def _collect_notes(keyword: str, limit: int, use_cache: bool = True) -> List[Dict[str, Any]]:
    """
    收集小红书笔记数据（带缓存支持）
    
    Args:
        keyword: 搜索关键词
        limit: 笔记数量
        use_cache: 是否使用缓存，默认True
        
    Returns:
        笔记列表
    """
    mcp_url = MCPConfig.SERVERS["xiaohongshu"]["url"]
    timeout = MCPConfig.SERVERS["xiaohongshu"]["timeout"]
    
    # 使用带缓存的客户端
    if use_cache:
        client = get_cached_mcp_client(base_url=mcp_url, cache_ttl=1800)  # 30分钟缓存
        logger.debug("使用带缓存的 MCP 客户端")
    else:
        client = XiaohongshuMCPClient(base_url=mcp_url, timeout=timeout)
        logger.debug("使用标准 MCP 客户端（无缓存）")
    
    try:
        # 搜索笔记（使用默认排序）
        result = client.search_notes(
            keyword=keyword,
            limit=limit
        )
        
        feeds = result.get("feeds", [])
        logger.info(f"搜索到 {len(feeds)} 条笔记")
        return feeds
        
    finally:
        client.close()


def _clean_and_validate_notes(notes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    清洗和验证笔记数据
    
    Args:
        notes: 原始笔记列表
        
    Returns:
        清洗后的笔记列表
    """
    cleaned = []
    min_likes = BusinessConfig.CONTENT_ANALYSIS.get("min_likes", 0)
    
    for note in notes:
        try:
            # 兼容两种数据结构：旧的直接结构和新的嵌套noteCard结构
            note_card = note.get("noteCard", {})
            if note_card:
                # 新结构：数据在noteCard中
                title = note_card.get("displayTitle", "")
                content = note_card.get("desc", "")  # 如果有desc字段
                interact_info = note_card.get("interactInfo", {})
                note_id = note.get("id", "")
                note_type = note_card.get("type", "normal")
            else:
                # 旧结构：数据在顶层
                title = note.get("title", "")
                content = note.get("desc", "")
                interact_info = note.get("interact_info", {})
                note_id = note.get("note_id", "")
                note_type = note.get("type", "normal")
            
            # 验证必需字段
            if not title:
                logger.debug("跳过无效笔记：缺少标题")
                continue
            
            # 获取互动数据（兼容不同字段名）
            likes = interact_info.get("likedCount", interact_info.get("liked_count", 0))
            # 处理字符串数字
            if isinstance(likes, str):
                likes = int(likes) if likes.isdigit() else 0
            
            # 过滤低互动内容（如果设置了阈值）
            if min_likes > 0 and likes < min_likes:
                logger.debug(f"跳过低互动笔记：{likes} < {min_likes}")
                continue
            
            # 获取收藏和评论数
            favorites = interact_info.get("collectedCount", interact_info.get("collected_count", 0))
            comments = interact_info.get("commentCount", interact_info.get("comment_count", 0))
            if isinstance(favorites, str):
                favorites = int(favorites) if favorites.isdigit() else 0
            if isinstance(comments, str):
                comments = int(comments) if comments.isdigit() else 0
            
            # 构建标准化数据
            cleaned_note = {
                "title": str(title).strip(),
                "content": str(content).strip() if content else f"笔记内容：{title}",  # 如果没有content，使用标题
                "likes": likes,
                "favorites": favorites,
                "comments": comments,
                "note_id": note_id,
                "type": note_type,
                "time": note.get("time", "")
            }
            
            # 限制内容长度（避免 token 过多）
            if len(cleaned_note["content"]) > 500:
                cleaned_note["content"] = cleaned_note["content"][:500] + "..."
            
            cleaned.append(cleaned_note)
            
        except Exception as e:
            logger.warning(f"处理笔记时出错: {str(e)}，跳过该笔记")
            continue
    
    return cleaned


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
        LLM 分析结果
    """
    # 加载系统提示词
    system_prompt = _load_system_prompt()
    
    # 构建用户提示词
    user_prompt = _build_analysis_prompt(notes, keyword)
    
    # 选择模型
    router = ModelRouter()
    quality = QualityLevel[quality_level.upper()] if quality_level.upper() in ["FAST", "BALANCED", "HIGH"] else QualityLevel.BALANCED
    model_name = router.select_model(TaskType.ANALYSIS, quality)
    logger.info(f"选择分析模型: {model_name} (质量级别: {quality.value})")
    
    # 获取配置
    analyst_config = AgentConfig.SUB_AGENTS.get("content_analyst", {
        "temperature": 0.5,
        "max_tokens": 4000
    })
    temperature = analyst_config["temperature"]
    max_tokens = analyst_config["max_tokens"]
    
    # 调用 LLM
    logger.info("调用 LLM 进行分析...")
    client = LLMClient()
    raw_response = client.call_llm(
        prompt=user_prompt,
        model_name=model_name,
        system_prompt=system_prompt,
        temperature=temperature,
        max_tokens=max_tokens
    )
    
    # 解析响应
    return _parse_llm_response(raw_response)


def _load_system_prompt() -> str:
    """加载系统提示词"""
    prompt_path = PathConfig.PROMPTS_DIR / "content_analyst.md"
    
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logger.warning(f"提示词文件不存在: {prompt_path}，使用默认提示词")
        return _get_default_system_prompt()
    except Exception as e:
        logger.error(f"读取提示词文件失败: {str(e)}，使用默认提示词")
        return _get_default_system_prompt()


def _get_default_system_prompt() -> str:
    """获取默认系统提示词"""
    return """你是一位资深的小红书内容分析师，擅长挖掘爆款内容的规律和用户需求。

请分析提供的小红书笔记数据，提取以下信息：
1. 标题模式（疑问式、数字型、情绪词等）
2. 内容结构特征（开头、正文、结尾的典型结构）
3. 用户需求痛点
4. 热门话题标签
5. 互动数据统计（平均点赞、收藏、评论数）
6. 创作建议（3-5个角度）

必须输出有效的 JSON 格式，严格按照要求的字段结构。"""


def _build_analysis_prompt(notes: List[Dict[str, Any]], keyword: str) -> str:
    """构建分析提示词"""
    prompt_parts = []
    
    prompt_parts.append(f"## 分析任务\n分析关键词 '{keyword}' 的小红书热门笔记，提取创作灵感和数据洞察。\n")
    
    prompt_parts.append(f"## 笔记数据（共 {len(notes)} 条）\n")
    
    # 添加笔记数据
    for i, note in enumerate(notes[:10], 1):  # 最多10条，避免 token 过多
        prompt_parts.append(f"### 笔记 {i}")
        prompt_parts.append(f"标题: {note['title']}")
        prompt_parts.append(f"内容: {note['content']}")
        prompt_parts.append(f"互动数据: 点赞 {note['likes']}, 收藏 {note['favorites']}, 评论 {note['comments']}")
        prompt_parts.append("")
    
    # 添加所有笔记的互动统计（如果超过10条）
    if len(notes) > 10:
        all_stats = _calculate_basic_stats(notes)
        prompt_parts.append(f"### 整体统计（{len(notes)} 条笔记）")
        prompt_parts.append(f"平均点赞: {all_stats.get('avg_likes', 0)}")
        prompt_parts.append(f"平均收藏: {all_stats.get('avg_favorites', 0)}")
        prompt_parts.append(f"平均评论: {all_stats.get('avg_comments', 0)}")
        prompt_parts.append("")
    
    prompt_parts.append("## 输出要求")
    prompt_parts.append("请返回 JSON 格式，包含以下字段：")
    prompt_parts.append("- title_patterns: 标题模式列表（字符串数组）")
    prompt_parts.append("- content_structure: 内容结构（对象，包含 opening, body, closing）")
    prompt_parts.append("- user_needs: 用户需求列表（字符串数组）")
    prompt_parts.append("- hot_topics: 热门话题列表（字符串数组）")
    prompt_parts.append("- interaction_stats: 互动统计（对象，包含 avg_likes, avg_favorites, avg_comments）")
    prompt_parts.append("- creation_suggestions: 创作建议列表（对象数组，每个包含 angle, reason, examples）")
    prompt_parts.append("")
    prompt_parts.append("请直接输出 JSON，不要添加任何解释性文字。")
    
    return "\n".join(prompt_parts)


def _parse_llm_response(raw_response: str) -> Dict[str, Any]:
    """解析 LLM 响应"""
    # 清理响应（移除 markdown 代码块）
    cleaned = raw_response.strip()
    
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    
    cleaned = cleaned.strip()
    
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.error(f"LLM 响应 JSON 解析失败: {str(e)}")
        logger.debug(f"原始响应前500字符: {cleaned[:500]}")
        raise LLMError(f"JSON 解析失败: {str(e)}")


def _validate_and_fix_analysis_result(
    analysis: Dict[str, Any],
    keyword: str,
    note_count: int,
    notes: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    验证并修复分析结果（核心优化点）
    
    确保：
    1. 必需字段存在且类型正确
    2. 数据合理性
    3. 即使部分字段缺失也能返回可用结果
    """
    result = {}
    
    # 1. 确保是字典类型
    if not isinstance(analysis, dict):
        logger.warning("LLM 返回结果不是字典类型，使用空字典")
        analysis = {}
    
    # 2. 验证和修复必需字段
    # title_patterns
    if "title_patterns" in analysis and isinstance(analysis["title_patterns"], list):
        result["title_patterns"] = [str(p) for p in analysis["title_patterns"] if p]
    else:
        logger.warning("title_patterns 缺失或类型错误，使用空列表")
        result["title_patterns"] = []
    
    # content_structure
    if "content_structure" in analysis and isinstance(analysis["content_structure"], dict):
        cs = analysis["content_structure"]
        result["content_structure"] = {
            "opening": str(cs.get("opening", "")),
            "body": str(cs.get("body", "")),
            "closing": str(cs.get("closing", ""))
        }
    else:
        logger.warning("content_structure 缺失或类型错误，使用默认值")
        result["content_structure"] = {
            "opening": "开头特征（待补充）",
            "body": "正文特征（待补充）",
            "closing": "结尾特征（待补充）"
        }
    
    # user_needs
    if "user_needs" in analysis and isinstance(analysis["user_needs"], list):
        result["user_needs"] = [str(n) for n in analysis["user_needs"] if n]
    else:
        logger.warning("user_needs 缺失或类型错误，使用空列表")
        result["user_needs"] = []
    
    # hot_topics
    if "hot_topics" in analysis and isinstance(analysis["hot_topics"], list):
        result["hot_topics"] = [str(t) for t in analysis["hot_topics"] if t]
    else:
        logger.warning("hot_topics 缺失或类型错误，使用空列表")
        result["hot_topics"] = []
    
    # interaction_stats
    if "interaction_stats" in analysis and isinstance(analysis["interaction_stats"], dict):
        stats = analysis["interaction_stats"]
        # 验证数值合理性
        result["interaction_stats"] = {
            "avg_likes": max(0, int(stats.get("avg_likes", 0))),
            "avg_favorites": max(0, int(stats.get("avg_favorites", 0))),
            "avg_comments": max(0, int(stats.get("avg_comments", 0)))
        }
    else:
        logger.warning("interaction_stats 缺失或类型错误，从笔记数据计算")
        # 降级：从实际笔记数据计算统计
        calculated_stats = _calculate_basic_stats(notes)
        result["interaction_stats"] = calculated_stats
    
    # creation_suggestions
    if "creation_suggestions" in analysis and isinstance(analysis["creation_suggestions"], list):
        suggestions = []
        for sug in analysis["creation_suggestions"]:
            if isinstance(sug, dict):
                suggestions.append({
                    "angle": str(sug.get("angle", "")),
                    "reason": str(sug.get("reason", "")),
                    "examples": [str(e) for e in sug.get("examples", [])] if isinstance(sug.get("examples"), list) else []
                })
        result["creation_suggestions"] = suggestions
    else:
        logger.warning("creation_suggestions 缺失或类型错误，使用默认建议")
        result["creation_suggestions"] = [
            {
                "angle": f"分享{keyword}的实用经验",
                "reason": "基于热门内容的通用角度",
                "examples": []
            }
        ]
    
    # 3. 补充元数据（始终补充）
    result["keyword"] = keyword
    result["total_analyzed"] = note_count
    result["analysis_timestamp"] = datetime.now().isoformat()
    
    # 4. 数据质量检查
    if len(result["title_patterns"]) == 0:
        logger.warning("title_patterns 为空，尝试从标题提取")
        result["title_patterns"] = _extract_title_patterns_from_notes(notes)
    
    logger.info(f"结果验证完成，已修复 {sum(1 for k in ['title_patterns', 'user_needs', 'hot_topics'] if len(result.get(k, [])) > 0)} 个主要字段")
    
    return result


def _calculate_basic_stats(notes: List[Dict[str, Any]]) -> Dict[str, int]:
    """从笔记数据计算基础统计"""
    if not notes:
        return {"avg_likes": 0, "avg_favorites": 0, "avg_comments": 0}
    
    total_likes = sum(n.get("likes", 0) for n in notes)
    total_favorites = sum(n.get("favorites", 0) for n in notes)
    total_comments = sum(n.get("comments", 0) for n in notes)
    count = len(notes)
    
    return {
        "avg_likes": int(total_likes / count) if count > 0 else 0,
        "avg_favorites": int(total_favorites / count) if count > 0 else 0,
        "avg_comments": int(total_comments / count) if count > 0 else 0
    }


def _extract_title_patterns_from_notes(notes: List[Dict[str, Any]]) -> List[str]:
    """从笔记标题中提取模式（简单启发式）"""
    patterns = []
    
    for note in notes[:5]:  # 只看前5条
        title = note.get("title", "")
        if not title:
            continue
        
        # 简单模式检测
        if any(char.isdigit() for char in title):
            patterns.append("数字型")
        if "？" in title or "?" in title:
            patterns.append("疑问式")
        if "！" in title or "!" in title:
            patterns.append("感叹式")
        if "攻略" in title or "指南" in title:
            patterns.append("攻略型")
    
    # 去重
    return list(set(patterns)) if patterns else ["通用型"]


def _get_fallback_analysis(keyword: str, notes: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    降级策略：LLM 失败时返回基础统计结果
    
    Args:
        keyword: 搜索关键词
        notes: 笔记列表
        
    Returns:
        基础分析结果
    """
    logger.info("使用降级策略生成基础分析结果")
    
    cleaned_notes = _clean_and_validate_notes(notes) if notes else []
    
    # 计算基础统计
    stats = _calculate_basic_stats(cleaned_notes)
    
    # 提取标题模式
    title_patterns = _extract_title_patterns_from_notes(cleaned_notes)
    
    return {
        "keyword": keyword,
        "total_analyzed": len(cleaned_notes),
        "title_patterns": title_patterns,
        "content_structure": {
            "opening": "热门笔记通常以问题或场景切入",
            "body": "正文多采用分点、序号等方式呈现",
            "closing": "结尾常引导互动或总结要点"
        },
        "user_needs": [f"关于{keyword}的实用信息"],
        "hot_topics": [keyword],
        "interaction_stats": stats,
        "creation_suggestions": [
            {
                "angle": f"分享{keyword}的实用经验",
                "reason": "基于热门趋势的通用建议",
                "examples": []
            }
        ],
        "fallback_mode": True,
        "message": "使用基础统计模式（LLM 分析失败）"
    }

