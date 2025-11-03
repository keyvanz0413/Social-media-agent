"""
Agent C: Content Creator
基于分析结果创作高质量小红书内容
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from utils.llm_client import LLMClient, LLMError
from utils.model_router import ModelRouter, TaskType, QualityLevel
from config import AgentConfig, PathConfig

# 配置日志
logger = logging.getLogger(__name__)


def agent_c_create_content(
    analysis_result: str,
    topic: str,
    style: str = "casual",
    quality_level: str = "balanced"
) -> str:
    """
    基于内容分析结果创作小红书帖子
    
    Args:
        analysis_result: Agent A 的分析结果（JSON字符串）
        topic: 主题
        style: 风格（casual/professional/storytelling），默认 casual
        quality_level: 质量级别（fast/balanced/high），默认 balanced
        
    Returns:
        JSON格式的创作结果，包含：
        - title: 标题
        - alternative_titles: 备选标题列表
        - content: 正文内容
        - hashtags: 话题标签列表
        - image_suggestions: 图片建议列表
        - metadata: 元数据（字数、风格、目标受众等）
        
    Example:
        >>> analysis = '{"title_patterns": ["数字型", "疑问式"]}'
        >>> result = agent_c_create_content(analysis, "澳洲旅游", style="casual")
        >>> print(json.loads(result)["title"])
    """
    try:
        # 1. 解析分析结果
        logger.info(f"开始创作内容，主题: {topic}, 风格: {style}")
        analysis_data = _parse_analysis_result(analysis_result)
        
        # 2. 加载提示词
        system_prompt = _load_system_prompt()
        
        # 3. 构建用户提示词
        user_prompt = _build_user_prompt(
            analysis_data=analysis_data,
            topic=topic,
            style=style
        )
        
        # 4. 选择模型
        router = ModelRouter()
        quality = QualityLevel[quality_level.upper()] if quality_level.upper() in ["FAST", "BALANCED", "HIGH"] else QualityLevel.BALANCED
        model_name = router.select_model(TaskType.CREATION, quality)
        logger.info(f"选择模型: {model_name} (质量级别: {quality.value})")
        
        # 5. 获取 LLM 配置
        creator_config = AgentConfig.SUB_AGENTS["content_creator"]
        temperature = creator_config["temperature"]
        max_tokens = creator_config["max_tokens"]
        
        # 6. 调用 LLM 生成内容
        logger.info("调用 LLM 生成内容...")
        client = LLMClient()
        raw_response = client.call_llm(
            prompt=user_prompt,
            model_name=model_name,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # 7. 解析和验证返回结果
        logger.info("解析 LLM 返回结果...")
        result = _parse_llm_response(raw_response, topic, style)
        
        # 8. 自动保存草稿
        try:
            from utils.draft_manager import save_draft_from_content
            draft_id = save_draft_from_content(
                content_data=result,
                topic=topic,
                analysis_data=analysis_data
            )
            logger.info(f"草稿已保存: {draft_id}")
            
            # 在元数据中添加草稿ID
            if 'metadata' not in result:
                result['metadata'] = {}
            result['metadata']['draft_id'] = draft_id
        except Exception as e:
            logger.warning(f"保存草稿失败（非关键错误）: {str(e)}")
        
        # 9. 返回 JSON 格式字符串
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except json.JSONDecodeError as e:
        error_msg = f"JSON 解析失败: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return json.dumps({
            "success": False,
            "error": error_msg,
            "message": "内容创作失败：无法解析分析结果或LLM响应"
        }, ensure_ascii=False)
        
    except LLMError as e:
        error_msg = f"LLM 调用失败: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return json.dumps({
            "success": False,
            "error": error_msg,
            "message": "内容创作失败：LLM 调用出错"
        }, ensure_ascii=False)
        
    except Exception as e:
        error_msg = f"内容创作过程中发生未知错误: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return json.dumps({
            "success": False,
            "error": error_msg,
            "message": "内容创作失败"
        }, ensure_ascii=False)


def _parse_analysis_result(analysis_result) -> Dict[str, Any]:
    """
    解析分析结果 JSON 字符串或字典
    
    Args:
        analysis_result: 分析结果的 JSON 字符串或字典对象
        
    Returns:
        解析后的字典
    """
    try:
        # 如果已经是字典，直接使用
        if isinstance(analysis_result, dict):
            data = analysis_result
        else:
            # 尝试解析 JSON 字符串
            data = json.loads(analysis_result)
        
        # 如果是包含 success 字段的响应，提取实际数据
        if isinstance(data, dict) and "success" in data:
            if data.get("success"):
                # 提取实际的分析数据
                data = data.get("data", data)
            else:
                logger.warning("分析结果标记为失败，但继续尝试创作")
        
        return data
        
    except json.JSONDecodeError as e:
        logger.error(f"分析结果 JSON 解析失败: {str(e)}")
        # 返回空字典，让后续流程继续
        return {}
    except Exception as e:
        logger.error(f"分析结果解析出错: {str(e)}")
        return {}


def _load_system_prompt() -> str:
    """
    加载系统提示词
    
    Returns:
        系统提示词内容
    """
    prompt_path = PathConfig.PROMPTS_DIR / "content_creator.md"
    
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
    return """你是一位经验丰富的小红书内容创作者，擅长创作吸引人、有价值、易传播的爆款内容。

核心要求：
1. 标题：20字以内，使用数字、疑问、感叹，制造悬念
2. 正文：500-1000字，使用分点、序号，适当使用emoji
3. 标签：3-5个话题标签
4. 风格：根据要求选择 casual（休闲）/ professional（专业）/ storytelling（故事）

输出必须是有效的 JSON 格式。"""


def _build_user_prompt(
    analysis_data: Dict[str, Any],
    topic: str,
    style: str
) -> str:
    """
    构建用户提示词
    
    Args:
        analysis_data: 分析结果数据
        topic: 主题
        style: 风格
        
    Returns:
        完整的用户提示词
    """
    prompt_parts = []
    
    # 主题信息
    prompt_parts.append(f"## 创作主题\n{topic}\n")
    
    # 风格要求
    style_descriptions = {
        "casual": "休闲风格：轻松活泼，口语化强，使用较多 emoji，适合生活、美妆、美食等话题",
        "professional": "专业风格：严谨专业，逻辑清晰，较少使用 emoji，适合教育、职场、技能分享",
        "storytelling": "故事风格：叙事性强，有画面感，情感丰富，引人入胜，适合旅行、经历分享"
    }
    style_desc = style_descriptions.get(style, style_descriptions["casual"])
    prompt_parts.append(f"## 创作风格\n{style_desc}\n")
    
    # 分析结果信息
    if analysis_data:
        prompt_parts.append("## 内容分析结果（参考）")
        
        # 提取关键信息
        if "title_patterns" in analysis_data:
            prompt_parts.append(f"- 标题模式: {', '.join(analysis_data['title_patterns'][:3])}")
        
        if "user_needs" in analysis_data:
            prompt_parts.append(f"- 用户痛点: {', '.join(analysis_data['user_needs'][:3])}")
        
        if "hot_topics" in analysis_data:
            prompt_parts.append(f"- 热门话题: {', '.join(analysis_data['hot_topics'][:3])}")
        
        if "creation_suggestions" in analysis_data:
            suggestions = analysis_data['creation_suggestions']
            if suggestions and len(suggestions) > 0:
                first_suggestion = suggestions[0]
                # 确保 first_suggestion 是字典类型
                if isinstance(first_suggestion, dict):
                    prompt_parts.append(f"- 推荐角度: {first_suggestion.get('angle', '')}")
                elif isinstance(first_suggestion, str):
                    prompt_parts.append(f"- 推荐角度: {first_suggestion}")
        
        prompt_parts.append("")
    
    # 创作要求
    prompt_parts.append("## 创作要求")
    prompt_parts.append("请基于以上信息，创作一篇高质量的小红书帖子。")
    prompt_parts.append("")
    prompt_parts.append("⚠️ 重要：必须严格按照 JSON 格式输出，包含以下字段（按顺序）：")
    prompt_parts.append("1. title: 主标题（20字以内）")
    prompt_parts.append("2. alternative_titles: 备选标题列表（2-3个）")
    prompt_parts.append("3. hashtags: 话题标签列表（3-5个，格式如 #话题#）")
    prompt_parts.append("4. image_suggestions: 图片建议列表（至少4-6个建议，每个包含：")
    prompt_parts.append("   - position: 图片位置（1, 2, 3...）")
    prompt_parts.append("   - description: 详细的图片内容描述（用于 AI 生成图片）")
    prompt_parts.append("   - purpose: 图片用途说明")
    prompt_parts.append("5. content: 正文内容（500-1000字，使用格式化，适当使用emoji）")
    prompt_parts.append("6. metadata: 元数据（包含 word_count, estimated_reading_time, style, target_audience）")
    prompt_parts.append("")
    prompt_parts.append("⚠️ 特别注意：image_suggestions 必须包含至少 4-6 个详细的图片建议！")
    prompt_parts.append("请直接输出完整的 JSON，不要添加任何解释性文字。")
    
    return "\n".join(prompt_parts)


def _parse_llm_response(
    raw_response: str,
    topic: str,
    style: str
) -> Dict[str, Any]:
    """
    解析 LLM 返回的响应
    
    Args:
        raw_response: LLM 原始响应
        topic: 主题（用于回退）
        style: 风格（用于回退）
        
    Returns:
        解析后的结构化数据
    """
    # 清理响应（移除可能的 markdown 代码块标记）
    cleaned_response = raw_response.strip()
    
    # 移除 markdown 代码块标记
    if cleaned_response.startswith("```json"):
        cleaned_response = cleaned_response[7:]  # 移除 ```json
    elif cleaned_response.startswith("```"):
        cleaned_response = cleaned_response[3:]  # 移除 ```
    
    if cleaned_response.endswith("```"):
        cleaned_response = cleaned_response[:-3]  # 移除结尾的 ```
    
    cleaned_response = cleaned_response.strip()
    
    try:
        # 尝试使用 strict=False 来允许控制字符
        # Python 3.9+ 支持 strict 参数
        import sys
        if sys.version_info >= (3, 9):
            result = json.loads(cleaned_response, strict=False)
        else:
            # 对于旧版本，先清理控制字符
            import re
            # 移除所有控制字符（除了 \t, \n, \r 在字符串值内的）
            cleaned_response = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', cleaned_response)
            result = json.loads(cleaned_response)
        
        # 验证必需字段
        required_fields = ["title", "content", "hashtags"]
        for field in required_fields:
            if field not in result:
                logger.warning(f"LLM 响应缺少必需字段: {field}，使用默认值")
                if field == "title":
                    result["title"] = f"关于{topic}的分享"
                elif field == "content":
                    result["content"] = f"关于{topic}的内容..."
                elif field == "hashtags":
                    result["hashtags"] = [f"#{topic}#"]
        
        # 确保可选字段存在
        if "alternative_titles" not in result:
            result["alternative_titles"] = []
        
        if "image_suggestions" not in result:
            result["image_suggestions"] = []
        
        if "metadata" not in result:
            # 计算字数
            word_count = len(result.get("content", ""))
            result["metadata"] = {
                "word_count": word_count,
                "estimated_reading_time": f"{word_count // 200}分钟",
                "style": style,
                "target_audience": "小红书用户"
            }
        else:
            # 确保 metadata 包含必需字段
            metadata = result["metadata"]
            if "word_count" not in metadata:
                metadata["word_count"] = len(result.get("content", ""))
            if "style" not in metadata:
                metadata["style"] = style
        
        logger.info(f"内容创作成功，标题: {result.get('title', '')[:30]}...")
        return result
        
    except json.JSONDecodeError as e:
        logger.error(f"LLM 响应 JSON 解析失败: {str(e)}")
        logger.debug(f"原始响应前500字符: {raw_response[:500]}")
        
        # 尝试修复常见的JSON问题
        try:
            logger.info("尝试修复JSON...")
            import re
            
            # 1. 尝试查找JSON对象的开始和结束
            json_match = re.search(r'\{.*\}', cleaned_response, re.DOTALL)
            if json_match:
                potential_json = json_match.group(0)
                # 尝试解析找到的JSON
                result = json.loads(potential_json, strict=False)
                logger.info("✅ JSON修复成功")
                
                # 验证必需字段
                required_fields = ["title", "content", "hashtags"]
                for field in required_fields:
                    if field not in result:
                        logger.warning(f"修复后的JSON缺少字段: {field}，添加默认值")
                        if field == "title":
                            result["title"] = f"关于{topic}的分享"
                        elif field == "content":
                            result["content"] = result.get("raw_response", f"关于{topic}的内容...")
                        elif field == "hashtags":
                            result["hashtags"] = [f"#{topic}#"]
                
                # 确保其他可选字段存在
                if "alternative_titles" not in result:
                    result["alternative_titles"] = []
                if "image_suggestions" not in result:
                    result["image_suggestions"] = []
                if "metadata" not in result:
                    word_count = len(result.get("content", ""))
                    result["metadata"] = {
                        "word_count": word_count,
                        "estimated_reading_time": f"{word_count // 200}分钟",
                        "style": style,
                        "target_audience": "小红书用户"
                    }
                
                return result
        except Exception as repair_error:
            logger.warning(f"JSON修复失败: {str(repair_error)}")
        
        # 最终回退：返回一个基本结构
        logger.warning("使用回退方案创建基本内容结构")
        return {
            "title": f"关于{topic}的分享",
            "alternative_titles": [],
            "content": raw_response[:1000] if len(raw_response) > 1000 else raw_response,
            "hashtags": [f"#{topic}#"],
            "image_suggestions": [],
            "metadata": {
                "word_count": len(raw_response),
                "estimated_reading_time": f"{len(raw_response) // 200}分钟",
                "style": style,
                "target_audience": "小红书用户",
                "parse_error": True
            }
        }

