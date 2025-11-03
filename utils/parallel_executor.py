"""
并行执行器（简化版）
用于并行执行多个独立的任务
"""

import json
import logging
from typing import Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)


def parallel_review(
    content_data: dict,
    enable_engagement: bool = False
) -> Dict[str, Any]:
    """
    并行执行评审任务
    
    这是一个便捷函数，用于并行执行质量评审和合规性检查
    
    Args:
        content_data: 内容数据，包含：
            - title: 标题
            - content: 正文
            - topic: 话题（可选）
            - hashtags: 标签（可选）
        enable_engagement: 是否启用互动评审（较慢，约40秒）
        
    Returns:
        评审结果字典，包含：
        - quality: 质量评审结果
        - compliance: 合规性检查结果
        - engagement: 互动评审结果（如果启用）
        
    Example:
        >>> results = parallel_review({
        ...     "title": "悉尼旅游攻略",
        ...     "content": "分享我的悉尼之旅...",
        ...     "topic": "悉尼旅游"
        ... })
        >>> print(results['quality']['score'])
        >>> print(results['compliance']['passed'])
    """
    from agents.reviewers.quality_reviewer import review_quality
    from tools.review_tools_v1 import review_compliance
    
    logger.info(f"🚀 开始并行评审（互动评审：{'启用' if enable_engagement else '禁用'}）")
    
    # 定义评审任务
    tasks = {
        'quality': lambda: review_quality(content_data),
        'compliance': lambda: review_compliance(content_data)
    }
    
    # 可选：添加互动评审
    if enable_engagement:
        from agents.reviewers.engagement_reviewer import review_engagement
        tasks['engagement'] = lambda: review_engagement(content_data)
    
    # 并行执行
    results = {}
    max_workers = len(tasks)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        future_to_name = {executor.submit(func): name for name, func in tasks.items()}
        
        # 收集结果
        for future in as_completed(future_to_name):
            name = future_to_name[future]
            try:
                result_str = future.result()
                result_data = json.loads(result_str)
                results[name] = result_data
                logger.info(f"✅ {name} 评审完成")
            except Exception as e:
                logger.error(f"❌ {name} 评审失败: {str(e)}")
                results[name] = {
                    "error": str(e),
                    "success": False
                }
    
    logger.info(f"✅ 并行评审完成，共 {len(results)} 项任务")
    return results


# 导出
__all__ = ['parallel_review']
