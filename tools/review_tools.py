"""
Review Tools - 工具函数集
为 Reviewer Agents 提供的专业工具函数

这些工具函数会被 Reviewer Agents 调用，而不是直接由 Coordinator 调用
"""

import json
import logging
from typing import List, Dict, Any
from datetime import datetime

from utils.mcp_client import XiaohongshuMCPClient
from utils.response_utils import create_success_response, create_error_response

logger = logging.getLogger(__name__)


# ========== Engagement Reviewer 工具 ==========

def search_similar_posts(topic: str, limit: int = 5, min_likes: int = 1000) -> str:
    """
    搜索类似话题的爆款帖子
    
    这个工具帮助 Engagement Reviewer Agent 分析同类内容的表现。
    
    Args:
        topic: 话题关键词
        limit: 返回数量
        min_likes: 最低点赞量
        
    Returns:
        JSON 格式的帖子列表
        
    Example (Agent 如何调用):
        >>> # Agent 会这样调用：
        >>> result = search_similar_posts("悉尼旅游", limit=5)
        >>> posts = json.loads(result)
        >>> # Agent 可以分析这些爆款帖子的特征
    """
    try:
        logger.info(f"搜索爆款帖子: topic={topic}, limit={limit}")
        
        # 调用 MCP 搜索
        mcp_client = XiaohongshuMCPClient()
        search_result = mcp_client.search_notes(
            keyword=topic,
            limit=limit * 2  # 多搜索一些，然后过滤
        )
        
        # 解析结果
        # search_notes 直接返回 dict，不需要 json.loads
        # 返回格式: {'feeds': [...], 'count': N}
        posts = search_result.get('feeds', [])
        
        # 过滤：只保留点赞量高的
        # 注意：MCP 返回的字段名可能是 liked_count 而不是 likes
        hot_posts = [
            p for p in posts 
            if p.get('liked_count', p.get('likes', 0)) >= min_likes
        ][:limit]
        
        # 格式化返回
        formatted_posts = []
        for post in hot_posts:
            formatted_posts.append({
                "title": post.get('title', ''),
                "likes": post.get('liked_count', post.get('likes', 0)),
                "comments": post.get('comment_count', post.get('comments', 0)),
                "favorites": post.get('collected_count', post.get('favorites', 0)),
                "content_preview": post.get('desc', post.get('content', ''))[:100]
            })
        
        return create_success_response(
            data={
                "topic": topic,
                "count": len(formatted_posts),
                "posts": formatted_posts
            },
            message=f"找到 {len(formatted_posts)} 篇爆款帖子"
        )
        
    except Exception as e:
        logger.error(f"搜索爆款帖子失败: {str(e)}", exc_info=True)
        return create_error_response(f"搜索失败: {str(e)}")


def analyze_title_patterns(titles: List[str]) -> str:
    """
    分析标题规律
    
    识别标题中的常见模式：数字、疑问、情感词、符号等。
    
    Args:
        titles: 标题列表（通常来自 search_similar_posts）
        
    Returns:
        JSON 格式的分析结果
        
    Example (Agent 如何调用):
        >>> # Agent 先搜索
        >>> posts = search_similar_posts("悉尼旅游")
        >>> titles = [p['title'] for p in posts['data']['posts']]
        >>> # 然后分析标题规律
        >>> patterns = analyze_title_patterns(titles)
    """
    try:
        import re
        
        # 处理空输入或字符串输入（Agent 可能传错）
        if not titles:
            return create_error_response("标题列表为空，无法分析")
        
        # 如果传入的是字符串，尝试转换
        if isinstance(titles, str):
            if not titles.strip():
                return create_error_response("标题列表为空，无法分析")
            # 假设是单个标题
            titles = [titles]
        
        # 统计各种模式
        has_numbers = sum(1 for t in titles if re.search(r'\d+', t))
        has_question = sum(1 for t in titles if '?' in t or '吗' in t)
        has_emoji = sum(1 for t in titles if any(c for c in t if ord(c) > 127462))
        has_exclamation = sum(1 for t in titles if '!' in t or '！' in t)
        
        # 常见情感词
        emotion_words = ['绝了', '太爱了', '惊喜', '必去', '推荐', '值得', '震撼', '美哭']
        has_emotion = sum(
            1 for t in titles 
            if any(word in t for word in emotion_words)
        )
        
        total = len(titles)
        
        # 再次检查（以防万一）
        if total == 0:
            return create_error_response("标题列表为空，无法分析")
        
        # 计算占比
        patterns = {
            "numbers": {
                "count": has_numbers,
                "percentage": round(has_numbers / total * 100, 1) if total > 0 else 0,
                "example": "3天2夜、10个必去景点"
            },
            "question": {
                "count": has_question,
                "percentage": round(has_question / total * 100, 1) if total > 0 else 0,
                "example": "你知道吗？怎么办？"
            },
            "emoji": {
                "count": has_emoji,
                "percentage": round(has_emoji / total * 100, 1) if total > 0 else 0,
                "example": "😊❤️✨"
            },
            "exclamation": {
                "count": has_exclamation,
                "percentage": round(has_exclamation / total * 100, 1) if total > 0 else 0,
                "example": "太棒了！绝了！"
            },
            "emotion_words": {
                "count": has_emotion,
                "percentage": round(has_emotion / total * 100, 1) if total > 0 else 0,
                "example": "绝了、太爱了、推荐"
            }
        }
        
        # 识别常见的标题结构
        structures = []
        if has_numbers / total > 0.5:
            structures.append("数字化标题很受欢迎")
        if has_question / total > 0.3:
            structures.append("疑问式标题能激发好奇")
        if has_emotion / total > 0.4:
            structures.append("情感词汇提升吸引力")
        
        return create_success_response(
            data={
                "total_analyzed": total,
                "patterns": patterns,
                "insights": structures,
                "recommendation": "标题应包含数字、情感词和适当的符号"
            },
            message=f"分析了 {total} 个标题"
        )
        
    except Exception as e:
        logger.error(f"标题分析失败: {str(e)}", exc_info=True)
        return create_error_response(f"分析失败: {str(e)}")


def check_emotional_triggers(content: str) -> str:
    """
    检查情感触发点
    
    评估内容是否能触发情感共鸣、好奇心、实用价值等。
    
    Args:
        content: 帖子内容
        
    Returns:
        JSON 格式的情感触发分析
    """
    try:
        # 情感关键词字典
        triggers = {
            "共鸣": ["我也是", "太真实了", "感同身受", "说到心坎", "深有体会"],
            "好奇": ["原来", "竟然", "没想到", "发现", "秘密", "真相"],
            "实用": ["方法", "技巧", "攻略", "教程", "步骤", "指南"],
            "惊喜": ["意外", "超出预期", "惊艳", "震撼", "太棒了"],
            "争议": ["但是", "其实", "不过", "相反", "打脸"]
        }
        
        # 检测每种触发点
        detected = {}
        for trigger_type, keywords in triggers.items():
            found_keywords = [kw for kw in keywords if kw in content]
            detected[trigger_type] = {
                "found": len(found_keywords) > 0,
                "keywords": found_keywords,
                "count": len(found_keywords)
            }
        
        # 计算触发强度
        total_triggers = sum(t['count'] for t in detected.values())
        strength = "强" if total_triggers >= 5 else "中" if total_triggers >= 3 else "弱"
        
        # 生成建议
        suggestions = []
        if not detected["共鸣"]["found"]:
            suggestions.append("增加能引发共鸣的表达")
        if not detected["实用"]["found"]:
            suggestions.append("强调实用价值")
        
        return create_success_response(
            data={
                "triggers": detected,
                "total_count": total_triggers,
                "strength": strength,
                "suggestions": suggestions
            },
            message=f"检测到 {total_triggers} 个情感触发点，强度: {strength}"
        )
        
    except Exception as e:
        logger.error(f"情感触发检测失败: {str(e)}", exc_info=True)
        return create_error_response(f"检测失败: {str(e)}")


def get_engagement_stats(topic: str) -> str:
    """
    获取同类内容的平均互动数据
    
    帮助 Agent 了解该话题的正常互动水平。
    
    Args:
        topic: 话题
        
    Returns:
        JSON 格式的统计数据
    """
    try:
        # 搜索相关帖子
        search_result = search_similar_posts(topic, limit=20, min_likes=0)
        search_data = json.loads(search_result)
        
        if not search_data.get('success'):
            return create_error_response("无法获取统计数据")
        
        posts = search_data.get('data', {}).get('posts', [])
        
        if not posts:
            return create_error_response("没有找到相关帖子")
        
        # 计算统计数据
        total = len(posts)
        avg_likes = sum(p['likes'] for p in posts) / total
        avg_comments = sum(p['comments'] for p in posts) / total
        avg_favorites = sum(p.get('favorites', 0) for p in posts) / total
        
        # 找出表现最好的
        top_post = max(posts, key=lambda p: p['likes'])
        
        return create_success_response(
            data={
                "topic": topic,
                "sample_size": total,
                "averages": {
                    "likes": round(avg_likes, 0),
                    "comments": round(avg_comments, 0),
                    "favorites": round(avg_favorites, 0)
                },
                "top_performer": {
                    "title": top_post['title'],
                    "likes": top_post['likes'],
                    "comments": top_post['comments']
                },
                "benchmark": {
                    "good": f"点赞 > {int(avg_likes)}",
                    "excellent": f"点赞 > {int(avg_likes * 2)}"
                }
            },
            message=f"基于 {total} 篇帖子的统计"
        )
        
    except Exception as e:
        logger.error(f"获取统计数据失败: {str(e)}", exc_info=True)
        return create_error_response(f"获取失败: {str(e)}")


# ========== Quality Reviewer 工具 ==========

def check_readability(content: str) -> str:
    """
    检查可读性
    
    评估内容的阅读体验：句子长度、专业术语、排版等。
    
    Args:
        content: 帖子内容
        
    Returns:
        JSON 格式的可读性分析
    """
    try:
        # 分析句子长度
        sentences = content.replace('！', '。').replace('？', '。').split('。')
        sentences = [s.strip() for s in sentences if s.strip()]
        
        avg_sentence_length = sum(len(s) for s in sentences) / len(sentences) if sentences else 0
        long_sentences = sum(1 for s in sentences if len(s) > 50)
        
        # 检查是否有段落
        paragraphs = content.split('\n')
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        # 检查专业术语（简化版）
        # 实际应该有专业术语词典
        has_complex_words = any(
            word in content 
            for word in ['因此', '然而', '鉴于', '综上所述']
        )
        
        # 检查排版元素
        has_emoji = any(ord(c) > 127462 for c in content)
        has_line_breaks = '\n' in content.strip()
        has_bullet_points = '•' in content or '·' in content or '-' in content
        
        # 计算可读性评分
        readability_score = 10
        
        if avg_sentence_length > 40:
            readability_score -= 2
        elif avg_sentence_length > 30:
            readability_score -= 1
            
        if long_sentences > len(sentences) * 0.3:  # 超过30%的句子过长
            readability_score -= 1
            
        if not has_line_breaks and len(content) > 200:
            readability_score -= 2
            
        if not has_emoji:
            readability_score -= 0.5
            
        # 生成建议
        suggestions = []
        if avg_sentence_length > 35:
            suggestions.append("句子平均长度较长，建议拆分为短句")
        if not has_line_breaks:
            suggestions.append("建议使用分行提升可读性")
        if not has_emoji and not has_bullet_points:
            suggestions.append("适当添加emoji或符号点缀")
        if long_sentences > 3:
            suggestions.append(f"有 {long_sentences} 个句子过长，建议简化")
            
        return create_success_response(
            data={
                "score": round(readability_score, 1),
                "metrics": {
                    "avg_sentence_length": round(avg_sentence_length, 1),
                    "long_sentences_count": long_sentences,
                    "paragraph_count": len(paragraphs),
                    "has_emoji": has_emoji,
                    "has_formatting": has_line_breaks or has_bullet_points
                },
                "reading_level": "易读" if readability_score >= 8 else "一般" if readability_score >= 6 else "较难",
                "suggestions": suggestions
            },
            message=f"可读性评分: {readability_score:.1f}/10"
        )
        
    except Exception as e:
        logger.error(f"可读性检查失败: {str(e)}", exc_info=True)
        return create_error_response(f"检查失败: {str(e)}")


def analyze_content_depth(content: str, topic: str = "") -> str:
    """
    分析内容深度
    
    评估内容的信息量、独特性和价值。
    
    Args:
        content: 帖子内容
        topic: 话题（用于判断相关性）
        
    Returns:
        JSON 格式的深度分析
    """
    try:
        # 1. 信息密度
        word_count = len(content)
        
        # 2. 检查是否有具体信息
        has_numbers = bool(__import__('re').search(r'\d+', content))
        has_specific_names = bool(__import__('re').search(r'[A-Z][a-z]+|[\u4e00-\u9fa5]{2,}(?:店|馆|中心|公园|酒店)', content))
        
        # 3. 检查是否有个人见解
        opinion_markers = ['我觉得', '我认为', '在我看来', '个人', '推荐', '建议']
        has_personal_view = any(marker in content for marker in opinion_markers)
        
        # 4. 检查是否有案例或例子
        example_markers = ['比如', '例如', '举个例子', '以我', '我的']
        has_examples = any(marker in content for marker in example_markers)
        
        # 5. 检查是否有实用建议
        practical_markers = ['方法', '步骤', '技巧', '攻略', '注意', '记得', '千万']
        has_practical_info = any(marker in content for marker in practical_markers)
        
        # 计算深度评分
        depth_score = 5  # 基础分
        
        if word_count >= 500:
            depth_score += 2
        elif word_count >= 300:
            depth_score += 1
        elif word_count < 150:
            depth_score -= 1
            
        if has_numbers:
            depth_score += 0.5
        if has_specific_names:
            depth_score += 0.5
        if has_personal_view:
            depth_score += 1
        if has_examples:
            depth_score += 0.5
        if has_practical_info:
            depth_score += 0.5
            
        depth_score = min(10, depth_score)  # 最高10分
        
        # 生成建议
        suggestions = []
        if word_count < 200:
            suggestions.append("内容较短，建议扩充到300字以上")
        if not has_numbers:
            suggestions.append("添加具体数字增强可信度")
        if not has_personal_view:
            suggestions.append("增加个人见解和感受")
        if not has_examples:
            suggestions.append("加入具体案例或例子")
        if not has_practical_info:
            suggestions.append("提供更多实用建议")
            
        return create_success_response(
            data={
                "score": round(depth_score, 1),
                "metrics": {
                    "word_count": word_count,
                    "has_numbers": has_numbers,
                    "has_specific_info": has_specific_names,
                    "has_personal_view": has_personal_view,
                    "has_examples": has_examples,
                    "has_practical_info": has_practical_info
                },
                "depth_level": "深入" if depth_score >= 8 else "中等" if depth_score >= 6 else "浅显",
                "suggestions": suggestions
            },
            message=f"内容深度评分: {depth_score:.1f}/10"
        )
        
    except Exception as e:
        logger.error(f"内容深度分析失败: {str(e)}", exc_info=True)
        return create_error_response(f"分析失败: {str(e)}")


def check_information_accuracy(content: str, topic: str = "") -> str:
    """
    检查信息准确性
    
    检测明显的事实错误、不合理的数据、误导性表述。
    
    Args:
        content: 帖子内容
        topic: 话题（用于上下文判断）
        
    Returns:
        JSON 格式的准确性检查结果
    """
    try:
        issues = []
        
        # 1. 检查极限词（可能违反广告法）
        extreme_words = ['最好', '第一', '最大', '最强', '顶级', '极致', '完美']
        found_extreme = [w for w in extreme_words if w in content]
        if found_extreme:
            issues.append({
                "type": "极限词",
                "issue": f"使用了极限词: {', '.join(found_extreme)}",
                "severity": "medium",
                "suggestion": "替换为相对表述，如'非常好'、'很推荐'"
            })
        
        # 2. 检查是否有明显夸张的数字
        import re
        numbers = re.findall(r'\d+', content)
        for num in numbers:
            if int(num) > 10000:  # 简单检查
                # 这里实际应该根据上下文判断
                pass
        
        # 3. 检查是否有绝对化表述
        absolute_words = ['一定', '必须', '绝对', '百分之百', '保证']
        found_absolute = [w for w in absolute_words if w in content]
        if found_absolute:
            issues.append({
                "type": "绝对化表述",
                "issue": f"使用了绝对化表述: {', '.join(found_absolute)}",
                "severity": "low",
                "suggestion": "使用更温和的表述，如'建议'、'推荐'"
            })
        
        # 4. 检查是否有未经证实的宣称
        claim_words = ['包治', '根治', '彻底', '永久', '秘方']
        found_claims = [w for w in claim_words if w in content]
        if found_claims:
            issues.append({
                "type": "夸大宣称",
                "issue": f"可能存在夸大宣称: {', '.join(found_claims)}",
                "severity": "high",
                "suggestion": "删除或修改为客观表述"
            })
        
        # 计算准确性评分
        accuracy_score = 10
        for issue in issues:
            if issue['severity'] == 'high':
                accuracy_score -= 3
            elif issue['severity'] == 'medium':
                accuracy_score -= 1.5
            elif issue['severity'] == 'low':
                accuracy_score -= 0.5
        
        accuracy_score = max(0, accuracy_score)
        
        return create_success_response(
            data={
                "score": round(accuracy_score, 1),
                "issues": issues,
                "total_issues": len(issues),
                "risk_level": "高" if accuracy_score < 6 else "中" if accuracy_score < 8 else "低",
                "passed": len([i for i in issues if i['severity'] == 'high']) == 0
            },
            message=f"发现 {len(issues)} 个准确性问题" if issues else "未发现明显问题"
        )
        
    except Exception as e:
        logger.error(f"准确性检查失败: {str(e)}", exc_info=True)
        return create_error_response(f"检查失败: {str(e)}")


def check_grammar(text: str) -> str:
    """
    语法检查（简化版）
    
    检查基本的语法问题：标点、拼写、重复词等。
    
    Args:
        text: 待检查的文本
        
    Returns:
        JSON 格式的语法问题列表
    """
    try:
        issues = []
        
        # 检查 1: 标点符号
        if text.count('。') + text.count('！') + text.count('？') == 0:
            issues.append({
                "type": "标点",
                "issue": "缺少句号或感叹号",
                "severity": "medium"
            })
        
        # 检查 2: 重复词
        words = text.split()
        for i in range(len(words) - 1):
            if words[i] == words[i + 1] and len(words[i]) > 1:
                issues.append({
                    "type": "重复",
                    "issue": f"重复词: {words[i]}",
                    "severity": "low"
                })
        
        # 检查 3: 常见拼写错误（简化）
        common_typos = {
            '的地得': '的/地/得 混用',
            '在再': '在/再 混用'
        }
        for typo_pair, desc in common_typos.items():
            # 简化检查逻辑
            pass
        
        return create_success_response(
            data={
                "total_issues": len(issues),
                "issues": issues,
                "score": 10 - len(issues) * 0.5  # 每个问题扣 0.5 分
            },
            message=f"发现 {len(issues)} 个语法问题"
        )
        
    except Exception as e:
        logger.error(f"语法检查失败: {str(e)}", exc_info=True)
        return create_error_response(f"检查失败: {str(e)}")


def analyze_content_structure(content: str) -> str:
    """
    分析内容结构
    
    检查是否有清晰的开头、正文、结尾。
    
    Args:
        content: 帖子内容
        
    Returns:
        JSON 格式的结构分析
    """
    try:
        lines = content.strip().split('\n')
        total_lines = len(lines)
        
        # 简化的结构分析
        has_intro = len(lines[0]) < 100 if total_lines > 0 else False  # 开头较短
        has_body = total_lines >= 3  # 至少3段
        has_ending = '总结' in content or '最后' in content or '记得' in content
        
        structure_score = 0
        if has_intro:
            structure_score += 3
        if has_body:
            structure_score += 4
        if has_ending:
            structure_score += 3
        
        suggestions = []
        if not has_intro:
            suggestions.append("建议添加引人入胜的开头")
        if not has_body:
            suggestions.append("内容过于简短，建议扩充")
        if not has_ending:
            suggestions.append("建议添加总结或行动号召")
        
        return create_success_response(
            data={
                "structure": {
                    "has_intro": has_intro,
                    "has_body": has_body,
                    "has_ending": has_ending
                },
                "paragraph_count": total_lines,
                "score": structure_score,
                "suggestions": suggestions
            },
            message=f"结构评分: {structure_score}/10"
        )
        
    except Exception as e:
        logger.error(f"结构分析失败: {str(e)}", exc_info=True)
        return create_error_response(f"分析失败: {str(e)}")


# ========== Compliance Reviewer 工具 ==========

def check_sensitive_words_detailed(text: str) -> str:
    """
    详细的敏感词检测
    
    比 review_tools_v1.py 中的版本更详细。
    
    Args:
        text: 待检查的文本
        
    Returns:
        JSON 格式的检测结果
    """
    try:
        # 扩展的敏感词库（实际应该更完整）
        sensitive_categories = {
            "政治敏感": ['政治', '政府', '领导人'],
            "违法违规": ['赌博', '色情', '毒品', '黄赌毒', '诈骗'],
            "暴力恐怖": ['暴力', '恐怖', '血腥', '杀人'],
            "迷信宗教": ['邪教', '迷信', '算命']
        }
        
        detected = {}
        total_issues = 0
        
        for category, words in sensitive_categories.items():
            found = [w for w in words if w in text]
            if found:
                detected[category] = found
                total_issues += len(found)
        
        risk_level = "high" if total_issues > 0 else "low"
        
        return create_success_response(
            data={
                "detected": detected,
                "total_issues": total_issues,
                "risk_level": risk_level,
                "passed": total_issues == 0
            },
            message=f"检测到 {total_issues} 个敏感词" if total_issues > 0 else "未检测到敏感词"
        )
        
    except Exception as e:
        logger.error(f"敏感词检测失败: {str(e)}", exc_info=True)
        return create_error_response(f"检测失败: {str(e)}")


def query_platform_rules(content_type: str = "image_post") -> str:
    """
    查询小红书平台规则
    
    返回特定类型内容的平台规则。
    
    Args:
        content_type: 内容类型（image_post, video, live等）
        
    Returns:
        JSON 格式的平台规则
    """
    try:
        # 模拟规则库（实际应该从数据库或配置文件读取）
        rules = {
            "image_post": {
                "title_max_length": 20,
                "content_max_length": 1000,
                "images_min": 1,
                "images_max": 9,
                "tags_min": 3,
                "tags_max": 10,
                "forbidden_content": [
                    "不得包含联系方式（微信、QQ等）",
                    "不得使用极限词（最好、第一等）",
                    "不得虚假宣传",
                    "不得侵犯版权"
                ]
            },
            "video": {
                "duration_min": 3,
                "duration_max": 300,
                "title_max_length": 20,
                "forbidden_content": [
                    "不得包含水印",
                    "不得搬运他人作品"
                ]
            }
        }
        
        rule = rules.get(content_type, rules["image_post"])
        
        return create_success_response(
            data={
                "content_type": content_type,
                "rules": rule,
                "last_updated": "2025-11-01"
            },
            message=f"已获取 {content_type} 的平台规则"
        )
        
    except Exception as e:
        logger.error(f"查询平台规则失败: {str(e)}", exc_info=True)
        return create_error_response(f"查询失败: {str(e)}")


# ========== 导出所有工具 ==========

__all__ = [
    # Engagement Reviewer 工具
    "search_similar_posts",
    "analyze_title_patterns",
    "check_emotional_triggers",
    "get_engagement_stats",
    
    # Quality Reviewer 工具
    "check_readability",
    "analyze_content_depth",
    "check_information_accuracy",
    "check_grammar",
    "analyze_content_structure",
    
    # Compliance Reviewer 工具
    "check_sensitive_words_detailed",
    "query_platform_rules"
]
