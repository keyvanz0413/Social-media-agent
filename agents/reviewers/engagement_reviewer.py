"""
互动潜力评审工具
评估内容的点赞、收藏、评论潜力
"""

import logging
import json

from utils.llm_client import LLMClient
from utils.model_router import ModelRouter, TaskType, QualityLevel
from utils.response_utils import create_success_response, create_error_response

logger = logging.getLogger(__name__)


def _evaluate_engagement(content_data: dict) -> dict:
    """使用LLM评估互动潜力"""
    title = content_data.get('title', '')
    content = content_data.get('content', '')
    
    prompt = f"""你是一位资深的社交媒体内容评审专家，专注于评估小红书内容的互动潜力（点赞、收藏、评论）。

请评审以下内容：

【标题】
{title}

【正文】
{content[:800]}{"..." if len(content) > 800 else ""}

评分标准（总分 0-10）：
1. 标题吸引力（3分）
   - 是否有数字（如"3天2夜"、"10个"）
   - 是否有疑问式（如"你知道吗？"）
   - 是否有情感词（如"绝了"、"太爱了"）
   - 是否有符号（感叹号、emoji）

2. 情感触发（3分）
   - 能否引发共鸣（"我也是"、"太真实了"）
   - 能否激发好奇（"原来"、"竟然"）
   - 是否有实用价值（"方法"、"攻略"）
   - 是否有争议点（"但是"、"其实"）

3. 实用价值（2分）
   - 是否提供具体可行的信息
   - 用户能否直接应用

4. 互动引导（2分）
   - 是否引导点赞、收藏、评论
   - 是否有提问、征集意见

输出 JSON 格式（不要包含任何其他文字）：
{{
    "score": 8.5,
    "strengths": ["标题包含数字", "有情感共鸣点", "提供实用攻略"],
    "weaknesses": ["缺少互动引导", "情感触发不够强"],
    "suggestions": ["在标题中加入疑问式", "在结尾加上提问引导评论"]
}}
"""
    
    # 调用 LLM
    router = ModelRouter()
    model = router.select_model(TaskType.REVIEW, QualityLevel.BALANCED)
    client = LLMClient()
    
    response = client.call_llm(
        prompt=prompt,
        model_name=model,
        temperature=0.3,
        response_format={"type": "json_object"}
    )
    
    review_data = json.loads(response)
    
    # 验证必需字段
    review_data.setdefault('score', 5.0)
    review_data.setdefault('strengths', [])
    review_data.setdefault('weaknesses', [])
    review_data.setdefault('suggestions', [])
    
    # 确保评分在范围内
    review_data['score'] = max(0, min(10, review_data['score']))
    
    return review_data


def review_engagement(content_data: dict) -> str:
    """
    评审互动潜力
    
    Args:
        content_data: 内容数据，包含：
            - title: 标题
            - content: 正文
            - topic: 话题（可选）
            
    Returns:
        JSON 格式的评审结果
        
    Example:
        >>> result = review_engagement({
        ...     "title": "澳洲旅游攻略",
        ...     "content": "分享我的澳洲之旅...",
        ...     "topic": "澳洲旅游"
        ... })
        >>> review = json.loads(result)
        >>> print(review['score'])
    """
    try:
        logger.info("开始互动潜力评审")
        review_data = _evaluate_engagement(content_data)
        logger.info(f"评审完成: {review_data['score']}/10")
        return create_success_response(
            data=review_data,
            message=f"互动潜力评分: {review_data['score']}/10"
        )
        
    except Exception as e:
        logger.error(f"评审失败: {str(e)}", exc_info=True)
        return create_error_response(f"评审失败: {str(e)}")


__all__ = ['review_engagement']

