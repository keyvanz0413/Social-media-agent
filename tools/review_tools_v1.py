"""
Review Tools - 方案 1：工具函数评审
内容评审工具集，用于评估内容的互动潜力、质量和合规性

版本：v1.0
架构：工具函数（非 Agent）
适用阶段：MVP v1.0
"""

import json
import re
import logging
from typing import Dict, Any, List
from datetime import datetime

from utils.llm_client import LLMClient, LLMError
from utils.model_router import ModelRouter, TaskType, QualityLevel
from utils.response_utils import create_success_response, create_error_response

logger = logging.getLogger(__name__)


def review_content(
    content_data: dict,
    quality_level: str = "balanced"
) -> str:
    """
    统一的内容评审函数（主入口）
    
    对内容进行多维度评审，包括互动潜力、内容质量和合规性。
    
    Args:
        content_data: 待评审的内容数据，包含：
            - title: 标题
            - content: 正文
            - hashtags: 标签列表（可选）
            - image_suggestions: 图片建议（可选）
        quality_level: 评审质量级别（fast/balanced/high）
        
    Returns:
        JSON 格式的评审结果，包含：
        - overall_score: 总分（0-10）
        - passed: 是否通过（总分 >= 8.0 且合规分 >= 7.0）
        - reviews: 各维度详细评审结果
        - suggestions: 合并的优化建议
        
    Example:
        >>> result = review_content({
        ...     "title": "澳洲旅游攻略",
        ...     "content": "分享我的澳洲之旅...",
        ...     "hashtags": ["澳洲旅游", "攻略"]
        ... })
        >>> data = json.loads(result)
        >>> print(data["overall_score"])  # 8.5
    """
    try:
        logger.info(f"开始评审内容: {content_data.get('title', 'N/A')}")
        
        # 验证输入
        if not content_data.get("title") or not content_data.get("content"):
            return create_error_response("缺少必需字段：title 和 content")
        
        # 1. 并行调用三个评审函数（可以进一步优化为真正的并行）
        engagement_result = review_engagement(content_data, quality_level)
        quality_result = review_quality(content_data, quality_level)
        compliance_result = review_compliance(content_data, quality_level)
        
        # 2. 解析结果
        engagement = json.loads(engagement_result)
        quality = json.loads(quality_result)
        compliance = json.loads(compliance_result)
        
        # 检查是否有评审失败
        if not engagement['success'] or not quality['success'] or not compliance['success']:
            failed_reviews = []
            if not engagement['success']:
                failed_reviews.append("互动潜力评审")
            if not quality['success']:
                failed_reviews.append("内容质量评审")
            if not compliance['success']:
                failed_reviews.append("合规性评审")
            
            return create_error_response(f"部分评审失败: {', '.join(failed_reviews)}")
        
        # 3. 提取评分
        engagement_score = engagement['data']['score']
        quality_score = quality['data']['score']
        compliance_score = compliance['data']['score']
        
        # 4. 计算加权总分
        # 互动潜力 40%，内容质量 40%，合规性 20%
        overall_score = (
            engagement_score * 0.4 +
            quality_score * 0.4 +
            compliance_score * 0.2
        )
        overall_score = round(overall_score, 2)
        
        # 5. 判断是否通过
        # 总分 >= 8.0 且合规分 >= 7.0（单项否决制）
        passed = overall_score >= 8.0 and compliance_score >= 7.0
        
        # 6. 合并建议
        all_suggestions = (
            engagement['data'].get('suggestions', []) +
            quality['data'].get('suggestions', []) +
            compliance['data'].get('suggestions', [])
        )
        
        # 去重并限制数量
        unique_suggestions = list(dict.fromkeys(all_suggestions))[:10]
        
        # 7. 构建返回结果
        result = {
            "overall_score": overall_score,
            "pass_threshold": 8.0,
            "passed": passed,
            "reviews": {
                "engagement": engagement['data'],
                "quality": quality['data'],
                "compliance": compliance['data']
            },
            "suggestions": unique_suggestions,
            "metadata": {
                "reviewed_at": datetime.now().isoformat(),
                "quality_level": quality_level,
                "version": "v1.0"
            }
        }
        
        logger.info(f"评审完成: 总分 {overall_score}, 通过: {passed}")
        return create_success_response(
            data=result,
            message=f"评审完成：总分 {overall_score}/10，{'通过' if passed else '不通过'}"
        )
        
    except Exception as e:
        logger.error(f"评审过程出错: {str(e)}", exc_info=True)
        return create_error_response(f"评审失败: {str(e)}")


def review_engagement(
    content_data: dict,
    quality_level: str = "balanced"
) -> str:
    """
    评审互动潜力（点赞、收藏、评论）
    
    评分维度：
    - 标题吸引力（3分）：数字、疑问、情感词、符号
    - 情感触发（3分）：共鸣、好奇、实用、争议
    - 实用价值（2分）：是否提供有用信息
    - 互动引导（2分）：是否引导点赞、评论
    
    Args:
        content_data: 内容数据
        quality_level: 质量级别
        
    Returns:
        JSON 格式的评审结果
    """
    try:
        title = content_data.get('title', '')
        content = content_data.get('content', '')
        
        # 构建评审 prompt
        prompt = f"""
你是一位资深的社交媒体内容评审专家，专注于评估内容的互动潜力（点赞、收藏、评论）。

请评审以下小红书内容：

【标题】
{title}

【正文】
{content[:800]}{"..." if len(content) > 800 else ""}

评分标准（总分 0-10）：
1. 标题吸引力（3分）
   - 是否有数字（如"3天2夜"、"10个"）
   - 是否有疑问式（如"你知道吗？"、"怎么办？"）
   - 是否有情感词（如"绝了"、"太爱了"、"惊喜"）
   - 是否有符号（如感叹号、emoji）

2. 情感触发（3分）
   - 能否引发共鸣（"我也是"、"太真实了"）
   - 能否激发好奇（"原来"、"竟然"、"没想到"）
   - 是否有实用价值（"方法"、"技巧"、"攻略"）
   - 是否有争议点（"但是"、"其实"、"真相"）

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
        model = router.select_model(TaskType.REVIEW, QualityLevel(quality_level))
        client = LLMClient()
        
        response = client.call_llm(
            prompt=prompt,
            model_name=model,
            temperature=0.3,  # 评审需要稳定性
            response_format="json"
        )
        
        # 解析并验证响应
        review_data = json.loads(response)
        
        # 验证必需字段
        if 'score' not in review_data:
            review_data['score'] = 5.0
        if 'strengths' not in review_data:
            review_data['strengths'] = []
        if 'weaknesses' not in review_data:
            review_data['weaknesses'] = []
        if 'suggestions' not in review_data:
            review_data['suggestions'] = []
        
        # 确保评分在 0-10 范围内
        review_data['score'] = max(0, min(10, review_data['score']))
        
        logger.info(f"互动潜力评审完成: {review_data['score']}/10")
        return create_success_response(
            data=review_data,
            message=f"互动潜力评分: {review_data['score']}/10"
        )
        
    except LLMError as e:
        logger.error(f"LLM 调用失败: {str(e)}")
        # 降级：返回基础评分
        fallback_score = _calculate_engagement_score_fallback(content_data)
        return create_success_response(
            data={
                "score": fallback_score,
                "strengths": ["使用基础规则评分"],
                "weaknesses": ["LLM 评审失败，使用降级策略"],
                "suggestions": ["建议稍后重试以获得详细评审"]
            },
            message="使用降级策略完成评审"
        )
        
    except Exception as e:
        logger.error(f"互动潜力评审失败: {str(e)}", exc_info=True)
        return create_error_response(f"互动潜力评审失败: {str(e)}")


def review_quality(
    content_data: dict,
    quality_level: str = "balanced"
) -> str:
    """
    评审内容质量（语法、逻辑、原创性）
    
    评分维度：
    - 语法正确性（2分）：拼写、标点、语法
    - 逻辑连贯性（3分）：结构、过渡、完整性
    - 信息准确性（3分）：事实、数据、引用
    - 原创性（2分）：新颖度、个人观点
    
    Args:
        content_data: 内容数据
        quality_level: 质量级别
        
    Returns:
        JSON 格式的评审结果
    """
    try:
        content = content_data.get('content', '')
        
        prompt = f"""
你是一位内容质量评审专家，专注于评估内容的质量和可读性。

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
            response_format="json"
        )
        
        review_data = json.loads(response)
        
        # 验证和修复
        review_data['score'] = max(0, min(10, review_data.get('score', 5.0)))
        review_data.setdefault('strengths', [])
        review_data.setdefault('weaknesses', [])
        review_data.setdefault('suggestions', [])
        
        logger.info(f"内容质量评审完成: {review_data['score']}/10")
        return create_success_response(
            data=review_data,
            message=f"内容质量评分: {review_data['score']}/10"
        )
        
    except Exception as e:
        logger.error(f"内容质量评审失败: {str(e)}", exc_info=True)
        # 降级
        fallback_score = 7.0  # 默认中等分数
        return create_success_response(
            data={
                "score": fallback_score,
                "strengths": [],
                "weaknesses": ["评审失败，使用默认分数"],
                "suggestions": ["建议稍后重试"]
            },
            message="使用降级策略完成评审"
        )


def review_compliance(
    content_data: dict,
    quality_level: str = "balanced"
) -> str:
    """
    评审合规性（敏感词、广告法、平台规则）
    
    评分维度：
    - 无敏感词（3分）
    - 广告法合规（3分）
    - 无违禁话题（2分）
    - 声明真实（2分）
    
    Args:
        content_data: 内容数据
        quality_level: 质量级别
        
    Returns:
        JSON 格式的评审结果
    """
    try:
        title = content_data.get('title', '')
        content = content_data.get('content', '')
        full_text = f"{title}\n{content}"
        
        # 1. 敏感词检测（规则 based）
        sensitive_issues = _check_sensitive_words(full_text)
        
        # 2. 广告法检测
        ad_law_issues = _check_advertising_law(full_text)
        
        # 3. 平台规则检测
        platform_issues = _check_platform_rules(content_data)
        
        # 4. 计算合规分数
        all_issues = sensitive_issues + ad_law_issues + platform_issues
        issue_count = len(all_issues)
        
        # 每个问题扣 2 分
        score = max(0, 10 - issue_count * 2)
        
        # 5. 评估风险等级
        if score >= 8:
            risk_level = "low"
        elif score >= 5:
            risk_level = "medium"
        else:
            risk_level = "high"
        
        # 6. 生成建议
        suggestions = [f"修复: {issue}" for issue in all_issues]
        if not suggestions:
            suggestions = ["内容合规，无需修改"]
        
        result_data = {
            "score": score,
            "risk_level": risk_level,
            "issues": all_issues,
            "issue_count": issue_count,
            "strengths": ["无合规问题"] if score >= 8 else [],
            "weaknesses": all_issues if all_issues else [],
            "suggestions": suggestions
        }
        
        logger.info(f"合规性评审完成: {score}/10, 风险等级: {risk_level}")
        return create_success_response(
            data=result_data,
            message=f"合规性评分: {score}/10, 风险等级: {risk_level}"
        )
        
    except Exception as e:
        logger.error(f"合规性评审失败: {str(e)}", exc_info=True)
        return create_error_response(f"合规性评审失败: {str(e)}")


# ========== 辅助函数 ==========

def _check_sensitive_words(text: str) -> List[str]:
    """检测敏感词"""
    issues = []
    
    # 简化版敏感词库（实际应该使用完整的敏感词库）
    sensitive_words = [
        '政治', '赌博', '色情', '暴力', '毒品',
        '反动', '邪教', '恐怖', '诈骗', '黄赌毒'
    ]
    
    for word in sensitive_words:
        if word in text:
            issues.append(f"包含敏感词: {word}")
    
    return issues


def _check_advertising_law(text: str) -> List[str]:
    """检查广告法合规性"""
    issues = []
    
    # 检测极限词
    extreme_words = [
        '最好', '第一', '最强', '最大', '最佳',
        '顶级', '极致', '完美', '绝对', '唯一'
    ]
    
    for word in extreme_words:
        if word in text:
            issues.append(f"包含广告法禁用词: {word}")
    
    # 检测虚假宣传
    false_claims = [
        '100%', '绝对有效', '立即见效', '包治',
        '根治', '永久', '终身', '国家级', '最高级'
    ]
    
    for claim in false_claims:
        if claim in text:
            issues.append(f"可能构成虚假宣传: {claim}")
    
    return issues


def _check_platform_rules(content_data: dict) -> List[str]:
    """检查平台规则"""
    issues = []
    
    title = content_data.get('title', '')
    content = content_data.get('content', '')
    
    # 检查标题长度
    if len(title) > 20:
        issues.append(f"标题过长（{len(title)}字），建议不超过20字")
    
    # 检查正文长度
    if len(content) > 1000:
        issues.append(f"正文过长（{len(content)}字），建议不超过1000字")
    
    # 检查是否有违规引流
    if any(word in content for word in ['微信', 'VX', 'WeChat', 'QQ', '加我']):
        issues.append("可能包含违规引流信息")
    
    return issues


def _calculate_engagement_score_fallback(content_data: dict) -> float:
    """降级策略：使用规则计算互动潜力评分"""
    title = content_data.get('title', '')
    content = content_data.get('content', '')
    
    score = 5.0  # 基础分
    
    # 标题加分
    if re.search(r'\d+', title):  # 包含数字
        score += 1.0
    if '?' in title or '吗' in title:  # 疑问式
        score += 0.5
    if any(emoji in title for emoji in ['😊', '❤️', '👍', '✨', '🔥', '💕']):
        score += 0.5
    
    # 内容加分
    if len(content) >= 300:  # 内容充实
        score += 1.0
    if any(word in content for word in ['方法', '技巧', '攻略', '教程']):
        score += 1.0
    
    return min(10, score)


# ========== 批量评审（可选） ==========

def batch_review(
    content_list: List[dict],
    quality_level: str = "balanced"
) -> str:
    """
    批量评审多条内容
    
    Args:
        content_list: 内容列表
        quality_level: 质量级别
        
    Returns:
        JSON 格式的批量评审结果
    """
    try:
        results = []
        
        for idx, content_data in enumerate(content_list):
            logger.info(f"评审第 {idx+1}/{len(content_list)} 条内容")
            
            review_result = review_content(content_data, quality_level)
            review_data = json.loads(review_result)
            
            results.append({
                "index": idx,
                "title": content_data.get('title', 'N/A'),
                "review": review_data
            })
        
        return create_success_response(
            data={
                "total": len(content_list),
                "results": results
            },
            message=f"批量评审完成: {len(content_list)} 条内容"
        )
        
    except Exception as e:
        logger.error(f"批量评审失败: {str(e)}", exc_info=True)
        return create_error_response(f"批量评审失败: {str(e)}")

