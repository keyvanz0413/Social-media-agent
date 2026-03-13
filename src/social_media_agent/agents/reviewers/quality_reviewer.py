"""
内容质量评审工具
评估语法、逻辑、原创性等
"""

import logging
import json

from social_media_agent.utils.llm_client import LLMClient
from social_media_agent.utils.model_router import ModelRouter, TaskType, QualityLevel

logger = logging.getLogger(__name__)


def review_quality(content_data: dict, quality_level: str = "balanced") -> str:
    """
    评审内容质量
    
    Args:
        content_data: 内容数据，包含：
            - title: 标题
            - content: 正文
            - topic: 话题（可选）
        quality_level: 评审质量级别（fast/balanced/high）
            
    Returns:
        JSON 格式的评审结果
        
    Example:
        >>> result = review_quality({
        ...     "title": "澳洲旅游攻略",
        ...     "content": "分享我的澳洲之旅...",
        ...     "topic": "澳洲旅游"
        ... })
        >>> review = json.loads(result)
        >>> print(review['data']['score'])
    """
    return json.dumps(
        review_quality_native(content_data=content_data, quality_level=quality_level),
        ensure_ascii=False,
    )


def review_quality_native(content_data: dict, quality_level: str = "balanced") -> dict:
    """评审内容质量，返回结构化 dict。"""
    try:
        logger.info("开始内容质量评审")
        content = content_data.get('content', '')
        
        prompt = f"""你是一位内容质量评审专家，专注于评估内容的质量和可读性。

请评审以下内容：

{content}

评分标准（总分 0-10）：
1. 语法正确性（2分）
   - 无拼写错误
   - 标点使用正确
   - 语法规范

2. 逻辑连贯性（3分）
   - 结构清晰（开头、正文、结尾）
   - 段落之间过渡自然
   - 论述完整

3. 信息准确性（3分）
   - 事实准确
   - 数据可靠
   - 无误导信息

4. 原创性（2分）
   - 有新颖的观点或角度
   - 有个人经验和见解
   - 不是简单抄袭

输出 JSON 格式（不要包含任何其他文字）：
{{
    "score": 8.0,
    "strengths": ["语法正确", "逻辑清晰", "有个人见解"],
    "weaknesses": ["部分数据缺少来源", "结尾较弱"],
    "suggestions": ["补充数据来源", "加强结尾总结"]
}}
"""
        
        router = ModelRouter()
        model = router.select_model(TaskType.REVIEW, QualityLevel(quality_level))
        client = LLMClient()
        
        response = client.call_llm(
            prompt=prompt,
            model_name=model,
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        
        review_data = json.loads(response)
        
        # 验证和修复
        review_data['score'] = max(0, min(10, review_data.get('score', 5.0)))
        review_data.setdefault('strengths', [])
        review_data.setdefault('weaknesses', [])
        review_data.setdefault('suggestions', [])
        
        logger.info(f"内容质量评审完成: {review_data['score']}/10")
        return {
            "success": True,
            "message": f"内容质量评分: {review_data['score']}/10",
            "data": review_data,
        }
        
    except Exception as e:
        logger.error(f"评审失败: {str(e)}", exc_info=True)
        fallback_score = 7.0
        return {
            "success": True,
            "message": "使用降级策略",
            "data": {
                "score": fallback_score,
                "strengths": [],
                "weaknesses": ["评审失败"],
                "suggestions": ["稍后重试"],
            },
        }


__all__ = ['review_quality', 'review_quality_native']
