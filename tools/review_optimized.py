"""
优化的评审工具
集成了并行执行和缓存机制，提升性能
"""

import json
import logging
import hashlib
from typing import Dict, Any, Optional

from utils.parallel_executor import parallel_review, ParallelExecutor, Task
from utils.cache_manager import get_cache_manager, cache_key

logger = logging.getLogger(__name__)


def review_content_optimized(
    content_data: dict,
    enable_engagement: bool = False,
    use_cache: bool = True,
    cache_ttl: int = 3600
) -> Dict[str, Any]:
    """
    优化的内容评审函数（并行+缓存）
    
    特点：
    - 质量评审和合规检查并行执行
    - 自动缓存评审结果
    - 可选启用互动评审
    
    Args:
        content_data: 内容数据
            - title: 标题
            - content: 正文
            - topic: 话题（可选）
            - hashtags: 标签（可选）
        enable_engagement: 是否启用互动评审（较慢，约40秒）
        use_cache: 是否使用缓存
        cache_ttl: 缓存过期时间（秒），默认1小时
        
    Returns:
        评审结果字典，包含：
        - quality: 质量评审结果
        - compliance: 合规性检查结果
        - engagement: 互动评审结果（如果启用）
        - overall: 综合评审结果
        - performance: 性能统计
        
    Example:
        >>> result = review_content_optimized({
        ...     "title": "悉尼旅游攻略",
        ...     "content": "分享我的悉尼之旅...",
        ...     "topic": "悉尼旅游"
        ... })
        >>> print(result['overall']['score'])  # 综合评分
        >>> print(result['performance']['elapsed_time'])  # 耗时
    """
    import time
    start_time = time.time()
    
    # 生成缓存键
    content_hash = _hash_content(content_data)
    cache_manager = get_cache_manager()
    key = cache_key(
        "review",
        content_hash,
        engagement=enable_engagement
    )
    
    # 尝试从缓存获取
    if use_cache:
        cached_result = cache_manager.get(key)
        if cached_result:
            logger.info("✅ 使用缓存的评审结果")
            cached_result['performance']['from_cache'] = True
            return cached_result
    
    # 并行执行评审
    logger.info(f"🚀 开始并行评审（互动评审：{'启用' if enable_engagement else '禁用'}）")
    
    results = parallel_review(
        content_data=content_data,
        enable_engagement=enable_engagement
    )
    
    # 解析和整合结果
    quality_result = results.get('quality', {})
    compliance_result = results.get('compliance', {})
    engagement_result = results.get('engagement', {}) if enable_engagement else None
    
    # 计算综合评分
    overall = _calculate_overall_score(
        quality_result,
        compliance_result,
        engagement_result
    )
    
    # 性能统计
    elapsed_time = time.time() - start_time
    performance = {
        "elapsed_time": round(elapsed_time, 2),
        "from_cache": False,
        "parallel_execution": True,
        "tasks_count": len(results)
    }
    
    # 构建最终结果
    final_result = {
        "quality": quality_result,
        "compliance": compliance_result,
        "overall": overall,
        "performance": performance
    }
    
    if engagement_result:
        final_result["engagement"] = engagement_result
    
    # 缓存结果
    if use_cache:
        cache_manager.set(key, final_result, ttl=cache_ttl)
        logger.info(f"💾 评审结果已缓存（TTL: {cache_ttl}秒）")
    
    logger.info(
        f"✅ 评审完成（{elapsed_time:.1f}秒）: "
        f"综合评分 {overall['score']:.1f}/10"
    )
    
    return final_result


def _hash_content(content_data: dict) -> str:
    """
    计算内容的哈希值
    
    Args:
        content_data: 内容数据
        
    Returns:
        MD5哈希字符串
    """
    # 只使用title和content计算哈希
    key_content = f"{content_data.get('title', '')}\n{content_data.get('content', '')}"
    return hashlib.md5(key_content.encode()).hexdigest()[:16]


def _calculate_overall_score(
    quality_result: dict,
    compliance_result: dict,
    engagement_result: Optional[dict] = None
) -> dict:
    """
    计算综合评审结果
    
    Args:
        quality_result: 质量评审结果
        compliance_result: 合规性检查结果
        engagement_result: 互动评审结果（可选）
        
    Returns:
        综合评审结果
    """
    # 提取评分
    quality_score = quality_result.get('score', 0)
    
    # 合规性处理
    if 'data' in compliance_result:
        compliance_passed = compliance_result['data'].get('overall', {}).get('passed', False)
        compliance_score = compliance_result['data'].get('overall', {}).get('score', 0)
    else:
        compliance_passed = compliance_result.get('passed', True)
        compliance_score = compliance_result.get('score', 10)
    
    # 互动评审（如果有）
    engagement_score = engagement_result.get('score', 0) if engagement_result else None
    
    # 计算综合评分
    if engagement_score is not None:
        # 包含互动评审：(质量 + 互动) / 2
        overall_score = (quality_score + engagement_score) / 2
    else:
        # 仅质量评分
        overall_score = quality_score
    
    # 决策逻辑
    if not compliance_passed:
        decision = "MUST_OPTIMIZE"
        reason = "存在合规性风险"
        action_text = "❌ 必须优化"
    elif overall_score >= 8.0:
        decision = "PUBLISH"
        reason = "内容质量优秀"
        action_text = "✅ 可以发布"
    elif overall_score >= 6.0:
        decision = "ASK_USER"
        reason = "内容质量良好，可以优化"
        action_text = "⚠️  建议询问用户"
    else:
        decision = "RECOMMEND_OPTIMIZE"
        reason = "内容质量有待提升"
        action_text = "⚠️  建议优化"
    
    # 收集所有建议
    all_suggestions = []
    all_suggestions.extend(quality_result.get('suggestions', []))
    if engagement_result:
        all_suggestions.extend(engagement_result.get('suggestions', []))
    
    return {
        "score": round(overall_score, 1),
        "quality_score": quality_score,
        "compliance_passed": compliance_passed,
        "compliance_score": compliance_score,
        "engagement_score": engagement_score,
        "decision": decision,
        "reason": reason,
        "action_text": action_text,
        "suggestions": all_suggestions[:5]  # 最多5条建议
    }


def clear_review_cache() -> int:
    """
    清除所有评审缓存
    
    Returns:
        清除的数量
    """
    cache_manager = get_cache_manager()
    
    # 清除所有以"review:"开头的缓存
    count = 0
    for key in list(cache_manager._memory_cache.keys()):
        if key.startswith("review:"):
            cache_manager.delete(key)
            count += 1
    
    logger.info(f"已清除 {count} 个评审缓存")
    return count


def get_review_cache_stats() -> dict:
    """
    获取评审缓存统计
    
    Returns:
        缓存统计信息
    """
    cache_manager = get_cache_manager()
    return cache_manager.get_stats()


__all__ = [
    'review_content_optimized',
    'clear_review_cache',
    'get_review_cache_stats'
]

