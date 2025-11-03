"""
Compliance Reviewer Agent
合规性评审 Agent

职责：
- 检查内容合规性
- 识别敏感词和违规内容
- 验证是否符合广告法规定
- 检查平台规则遵守情况

工具：
- check_sensitive_words: 敏感词检测
- check_advertising_law: 广告法合规检查
- query_platform_rules: 查询平台规则
- check_banned_topics: 检查禁止话题
- verify_claims: 验证宣传声明

输出：
- score: 合规性评分 (0-10, 10为完全合规)
- violations: 违规项列表
- warnings: 警告项列表
- suggestions: 修改建议列表
- risk_level: 风险等级 (low/medium/high)
"""

# 当前实现：从 review_tools_v1 导入函数实现
# 未来版本：使用 ConnectOnion 框架创建独立的 Agent
from tools.review_tools_v1 import review_compliance as _review_compliance_impl


def review_compliance(content_data: dict, quality_level: str = "balanced") -> str:
    """
    评审合规性（敏感词、广告法、平台规则）
    
    评分维度：
    - 无敏感词（3分）
    - 广告法合规（3分）
    - 无违禁话题（2分）
    - 声明真实（2分）
    
    Args:
        content_data: 内容数据，包含：
            - title: 标题
            - content: 正文
            - hashtags: 标签列表（可选）
        quality_level: 评审质量级别（fast/balanced/high）
        
    Returns:
        JSON 格式的评审结果，包含：
        - success: 是否成功
        - data: 评审结果数据
            - score: 合规性评分（0-10）
            - risk_level: 风险等级（low/medium/high）
            - issues: 问题列表
            - suggestions: 修改建议
            
    Example:
        >>> result = review_compliance({
        ...     "title": "健康饮食小技巧",
        ...     "content": "分享一些实用的健康饮食建议",
        ...     "hashtags": ["健康", "饮食"]
        ... })
        >>> data = json.loads(result)
        >>> print(data["data"]["score"])  # 10
        >>> print(data["data"]["risk_level"])  # low
    """
    return _review_compliance_impl(content_data, quality_level)


# 导出函数供外部使用
__all__ = ["review_compliance"]
