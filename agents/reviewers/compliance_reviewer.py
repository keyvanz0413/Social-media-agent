"""
Compliance Reviewer（简化版）
合规性评审

职责：
- 检查敏感词
- 检查广告法合规性
- 检查平台规则

输出：
- score: 合规评分 (0-10)
- issues: 问题列表
- suggestions: 修复建议

注意：使用基于规则的简单检查
"""

import logging
from typing import List

from utils.response_utils import create_success_response, create_error_response

logger = logging.getLogger(__name__)


def review_compliance(content_data: dict, quality_level: str = "balanced") -> str:
    """
    评审合规性
    
    Args:
        content_data: 内容数据
        quality_level: 质量级别（保留参数以兼容）
        
    Returns:
        JSON 格式的评审结果
    """
    try:
        title = content_data.get('title', '')
        content = content_data.get('content', '')
        full_text = f"{title}\n{content}"
        
        # 1. 敏感词检测
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


def _check_sensitive_words(text: str) -> List[str]:
    """检测敏感词"""
    issues = []
    
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
    
    extreme_words = [
        '最好', '第一', '最强', '最大', '最佳',
        '顶级', '极致', '完美', '绝对', '唯一'
    ]
    
    for word in extreme_words:
        if word in text:
            issues.append(f"包含广告法禁用词: {word}")
    
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
    
    if len(title) > 20:
        issues.append(f"标题过长（{len(title)}字），建议不超过20字")
    
    if len(content) > 1000:
        issues.append(f"正文过长（{len(content)}字），建议不超过1000字")
    
    if any(word in content for word in ['微信', 'VX', 'WeChat', 'QQ', '加我']):
        issues.append("可能包含违规引流信息")
    
    return issues


# 导出
__all__ = [
    "review_compliance"
]
