"""
Image Generator Agent
根据内容描述生成或搜索合适的图片
支持多种图片生成方式：AI生成、免费图库搜索
"""

import json
import logging
import hashlib
import requests
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from utils.llm_client import LLMClient, LLMError
from config import PathConfig, BusinessConfig, ModelConfig

# 配置日志
logger = logging.getLogger(__name__)


def generate_images_for_content(
    image_suggestions: str,
    topic: str,
    count: Optional[int] = None,
    method: str = "dalle",
    save_to_disk: bool = True
) -> str:
    """
    使用 AI 生成图片
    
    Args:
        image_suggestions: 图片建议列表（JSON字符串），包含 description, purpose 等字段
        topic: 主题
        count: 生成图片数量，默认从配置读取
        method: 生成方法，支持：
            - "dalle": 使用 DALL-E 3 生成（推荐，高质量 AI 生成）
            - "local": 使用本地 Stable Diffusion（需要本地部署）
            - "unsplash": 从 Unsplash 搜索（已集成在 MCP，不推荐在此使用）
            - "pexels": 从 Pexels 搜索（已集成在 MCP，不推荐在此使用）
        save_to_disk: 是否保存到本地磁盘（默认 True）
        
        Returns:
        JSON格式的生成结果，包含：
        - success: 是否成功
        - images: 图片信息列表，每个包含：
            - path: 本地路径
            - url: 临时URL（DALL-E 生成）
            - description: 图片描述
            - source: 来源（dalle 或 stable-diffusion）
            - prompt: 生成提示词
        - topic: 主题
        - method: 使用的生成方法
        - message: 状态消息
        
    Example:
        >>> suggestions = '[{"description": "悉尼歌剧院日落美景", "purpose": "展示地标"}]'
        >>> result = generate_images_for_content(suggestions, "悉尼旅游", count=4, method="dalle")
        >>> print(result)
    """
    try:
        # 1. 解析图片建议
        logger.info(f"开始生成图片，主题: {topic}, 方法: {method}")
        suggestions = _parse_image_suggestions(image_suggestions)
        
        if not suggestions:
            logger.warning("图片建议为空，将根据主题生成默认建议")
            suggestions = [
                {
                    "description": f"{topic} 相关场景",
                    "purpose": "展示主题内容",
                    "position": 1
                }
            ]
        
        # 2. 确定生成数量
        target_count = count or BusinessConfig.IMAGE_GENERATION["count"]
        actual_count = min(target_count, len(suggestions))
        
        logger.info(f"目标生成 {actual_count} 张图片")
        
        # 3. 根据方法选择生成器（优先 AI 生成）
        if method == "dalle":
            images = _generate_from_dalle(suggestions[:actual_count], topic, save_to_disk)
        elif method == "local":
            images = _generate_from_local_sd(suggestions[:actual_count], topic, save_to_disk)
        elif method == "unsplash":
            logger.warning("Unsplash 已集成在 MCP 中，建议使用 MCP 调用。继续使用内置方法...")
            images = _generate_from_unsplash(suggestions[:actual_count], topic, save_to_disk)
        elif method == "pexels":
            logger.warning("Pexels 已集成在 MCP 中，建议使用 MCP 调用。继续使用内置方法...")
            images = _generate_from_pexels(suggestions[:actual_count], topic, save_to_disk)
        else:
            return json.dumps({
                "success": False,
                "error": f"不支持的生成方法: {method}。推荐使用 'dalle' 或 'local'",
                "message": "图片生成失败"
            }, ensure_ascii=False)
        
        # 4. 返回结果
        if not images:
            return json.dumps({
                "success": False,
                "error": "未能生成任何图片",
                "message": "图片生成失败",
                "method": method
            }, ensure_ascii=False)
        
        logger.info(f"成功生成 {len(images)} 张图片")
        
        return json.dumps({
            "success": True,
            "images": images,
            "topic": topic,
            "method": method,
            "count": len(images),
            "message": f"成功生成 {len(images)} 张图片"
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        error_msg = f"图片生成过程中发生错误: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return json.dumps({
            "success": False,
            "error": error_msg,
            "message": "图片生成失败"
        }, ensure_ascii=False)


def _parse_image_suggestions(suggestions_str: str) -> List[Dict[str, Any]]:
    """
    解析图片建议字符串
    
    Args:
        suggestions_str: JSON字符串或列表
        
    Returns:
        解析后的图片建议列表
    """
    try:
        # 如果是字符串，尝试解析
        if isinstance(suggestions_str, str):
            suggestions = json.loads(suggestions_str)
        else:
            suggestions = suggestions_str
        
        # 确保是列表
        if not isinstance(suggestions, list):
            logger.warning(f"图片建议不是列表格式，收到: {type(suggestions)}")
            return []
        
        return suggestions
        
    except json.JSONDecodeError as e:
        logger.error(f"解析图片建议失败: {str(e)}")
        return []


def _generate_from_unsplash(
    suggestions: List[Dict[str, Any]],
    topic: str,
    save_to_disk: bool
) -> List[Dict[str, Any]]:
    """
    从 Unsplash 搜索图片（免费、无需API Key、高质量）
    
    使用 Unsplash 的公开 API：https://unsplash.com/developers
    """
    logger.info("使用 Unsplash 搜索图片")
    
    # Unsplash API 配置
    # 注意：Unsplash 有公开的 Source API，不需要注册即可使用
    # 但建议注册获取 Access Key 以获得更高的请求限制
    access_key = ModelConfig.OPENAI_API_KEY  # 可以在环境变量中配置 UNSPLASH_ACCESS_KEY
    
    images = []
    
    for idx, suggestion in enumerate(suggestions):
        try:
            # 1. 提取搜索关键词
            description = suggestion.get("description", topic)
            search_query = _extract_search_keywords(description, topic)
            
            logger.info(f"搜索图片 {idx + 1}/{len(suggestions)}: {search_query}")
            
            # 2. 调用 Unsplash API（使用 Source API - 无需认证）
            # Source API: https://source.unsplash.com/
            # 格式: https://source.unsplash.com/featured/?{query}
            # 或者使用正式 API: https://api.unsplash.com/search/photos
            
            # 方法1: 使用 Source API（简单但功能有限）
            # image_url = f"https://source.unsplash.com/1080x1920/?{search_query}"
            
            # 方法2: 使用正式搜索 API（更灵活）
            api_url = "https://api.unsplash.com/search/photos"
            params = {
                "query": search_query,
                "page": 1,
                "per_page": 1,
                "orientation": "portrait",  # 小红书推荐竖屏
            }
            
            headers = {}
            if access_key and access_key.startswith("unsplash_"):
                headers["Authorization"] = f"Client-ID {access_key}"
            
            # 发送请求
            response = requests.get(api_url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("results") and len(data["results"]) > 0:
                    photo = data["results"][0]
                    image_url = photo["urls"]["regular"]  # 或 "full", "raw", "small"
                    
                    logger.info(f"找到图片: {image_url}")
                    
                    # 3. 保存到本地（如果需要）
                    local_path = None
                    if save_to_disk:
                        local_path = _download_and_save_image(
                            image_url,
                            topic,
                            idx,
                            source="unsplash"
                        )
                    
                    # 4. 添加到结果
                    images.append({
                        "path": local_path,
                        "url": image_url,
                        "description": description,
                        "source": "unsplash",
                        "position": idx + 1,
                        "photographer": photo.get("user", {}).get("name", "Unknown"),
                        "photographer_url": photo.get("user", {}).get("links", {}).get("html", "")
                    })
                else:
                    logger.warning(f"未找到匹配图片: {search_query}")
            else:
                # 如果 API 调用失败，降级使用 Source API
                logger.warning(f"Unsplash API 调用失败 ({response.status_code})，使用 Source API")
                image_url = f"https://source.unsplash.com/1080x1920/?{search_query}"
                
                local_path = None
                if save_to_disk:
                    local_path = _download_and_save_image(
                        image_url,
                        topic,
                        idx,
                        source="unsplash"
                    )
                
                images.append({
                    "path": local_path,
                    "url": image_url,
                    "description": description,
                    "source": "unsplash",
                    "position": idx + 1
                })
                
        except Exception as e:
            logger.error(f"搜索第 {idx + 1} 张图片失败: {str(e)}", exc_info=True)
            continue
    
    return images


def _generate_from_pexels(
    suggestions: List[Dict[str, Any]],
    topic: str,
    save_to_disk: bool
) -> List[Dict[str, Any]]:
    """
    从 Pexels 搜索图片（免费、需要API Key）
    
    注册地址: https://www.pexels.com/api/
    """
    logger.info("使用 Pexels 搜索图片")
    
    # Pexels API Key（需要在环境变量中配置）
    import os
    api_key = os.getenv("PEXELS_API_KEY")
    
    if not api_key:
        logger.error("PEXELS_API_KEY 未配置，无法使用 Pexels")
        return []
    
    images = []
    
    for idx, suggestion in enumerate(suggestions):
        try:
            description = suggestion.get("description", topic)
            search_query = _extract_search_keywords(description, topic)
            
            logger.info(f"搜索图片 {idx + 1}/{len(suggestions)}: {search_query}")
            
            # 调用 Pexels API
            api_url = "https://api.pexels.com/v1/search"
            headers = {"Authorization": api_key}
            params = {
                "query": search_query,
                "page": 1,
                "per_page": 1,
                "orientation": "portrait"
            }
            
            response = requests.get(api_url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("photos") and len(data["photos"]) > 0:
                    photo = data["photos"][0]
                    image_url = photo["src"]["large2x"]  # 或 "original", "large", "medium"
                    
                    logger.info(f"找到图片: {image_url}")
                    
                    # 保存到本地
                    local_path = None
                    if save_to_disk:
                        local_path = _download_and_save_image(
                            image_url,
                            topic,
                            idx,
                            source="pexels"
                        )
                    
                    images.append({
                        "path": local_path,
                        "url": image_url,
                        "description": description,
                        "source": "pexels",
                        "position": idx + 1,
                        "photographer": photo.get("photographer", "Unknown"),
                        "photographer_url": photo.get("photographer_url", "")
                    })
                else:
                    logger.warning(f"未找到匹配图片: {search_query}")
            else:
                logger.error(f"Pexels API 调用失败: {response.status_code}")
                
        except Exception as e:
            logger.error(f"搜索第 {idx + 1} 张图片失败: {str(e)}", exc_info=True)
            continue
    
    return images


def _generate_from_dalle(
    suggestions: List[Dict[str, Any]],
    topic: str,
    save_to_disk: bool
) -> List[Dict[str, Any]]:
    """
    使用 DALL-E 3 生成图片（需要 OpenAI API Key，较贵）
    """
    logger.info("使用 DALL-E 3 生成图片")
    
    if not ModelConfig.OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY 未配置，无法使用 DALL-E")
        return []
    
    try:
        from openai import OpenAI
        client = OpenAI(
            api_key=ModelConfig.OPENAI_API_KEY,
            base_url=ModelConfig.OPENAI_BASE_URL
        )
    except ImportError:
        logger.error("openai 库未安装，无法使用 DALL-E")
        return []
    
    images = []
    
    for idx, suggestion in enumerate(suggestions):
        try:
            description = suggestion.get("description", topic)
            
            # 使用 LLM 生成更详细的英文提示词
            prompt = _create_dalle_prompt(description, topic)
            
            logger.info(f"生成图片 {idx + 1}/{len(suggestions)}: {prompt[:100]}...")
            
            # 调用 DALL-E API
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1792",  # 竖屏比例，接近小红书的 9:16
                quality="hd",
                n=1
            )
            
            image_url = response.data[0].url
            
            logger.info(f"图片生成成功: {image_url}")
            
            # 保存到本地
            local_path = None
            if save_to_disk:
                local_path = _download_and_save_image(
                    image_url,
                    topic,
                    idx,
                    source="dalle"
                )
            
            images.append({
                "path": local_path,
                "url": image_url,
                "description": description,
                "source": "dalle",
                "position": idx + 1,
                "prompt": prompt
            })
            
        except Exception as e:
            logger.error(f"生成第 {idx + 1} 张图片失败: {str(e)}", exc_info=True)
            continue
    
    return images


def _generate_from_local_sd(
    suggestions: List[Dict[str, Any]],
    topic: str,
    save_to_disk: bool
) -> List[Dict[str, Any]]:
    """
    使用本地 Stable Diffusion 生成图片（需要本地部署）
    
    可以使用 Automatic1111 WebUI API 或 ComfyUI API
    """
    logger.info("使用本地 Stable Diffusion 生成图片")
    
    import os
    sd_url = os.getenv("SD_API_URL", "http://localhost:7860")
    
    images = []
    
    for idx, suggestion in enumerate(suggestions):
        try:
            description = suggestion.get("description", topic)
            prompt = _create_sd_prompt(description, topic)
            
            logger.info(f"生成图片 {idx + 1}/{len(suggestions)}: {prompt[:100]}...")
            
            # 调用 Stable Diffusion WebUI API
            api_url = f"{sd_url}/sdapi/v1/txt2img"
            payload = {
                "prompt": prompt,
                "negative_prompt": "low quality, blurry, distorted, watermark, text",
                "steps": 30,
                "width": 768,
                "height": 1344,  # 接近 9:16
                "cfg_scale": 7,
                "sampler_name": "DPM++ 2M Karras"
            }
            
            response = requests.post(api_url, json=payload, timeout=120)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("images") and len(data["images"]) > 0:
                    # SD WebUI 返回 base64 编码的图片
                    import base64
                    image_base64 = data["images"][0]
                    
                    # 保存到本地
                    local_path = _save_base64_image(
                        image_base64,
                        topic,
                        idx,
                        source="stable-diffusion"
                    )
                    
                    images.append({
                        "path": local_path,
                        "url": None,
                        "description": description,
                        "source": "stable-diffusion",
                        "position": idx + 1,
                        "prompt": prompt
                    })
                    
                    logger.info(f"图片生成成功: {local_path}")
            else:
                logger.error(f"SD API 调用失败: {response.status_code}")
                
        except Exception as e:
            logger.error(f"生成第 {idx + 1} 张图片失败: {str(e)}", exc_info=True)
            continue
    
    return images


def _extract_search_keywords(description: str, topic: str) -> str:
    """
    从描述中提取搜索关键词（英文）
    
    使用 LLM 将中文描述翻译成适合搜索的英文关键词
    """
    try:
        # 使用快速模型翻译
        client = LLMClient()
        
        prompt = f"""请将以下图片描述转换为适合在图片库（如Unsplash）搜索的英文关键词。
要求：
1. 提取核心视觉元素
2. 使用简洁的英文关键词
3. 用空格分隔多个关键词
4. 不超过5个关键词

描述：{description}
主题：{topic}

只输出关键词，不要其他内容。例如：beach sunset ocean waves"""

        keywords = client.call_llm(
            prompt=prompt,
            model_name="gpt-4o-mini",
            temperature=0.3,
            max_tokens=50
        ).strip()
        
        logger.debug(f"提取关键词: {description} → {keywords}")
        return keywords
        
    except Exception as e:
        logger.warning(f"关键词提取失败，使用原始描述: {str(e)}")
        # 降级：简单处理
        return topic.replace("旅游", "travel").replace("美食", "food")


def _create_dalle_prompt(description: str, topic: str) -> str:
    """
    创建适合 DALL-E 的提示词（详细的英文描述）
    """
    try:
        client = LLMClient()
        
        prompt = f"""请将以下图片需求转换为适合 DALL-E 3 的英文提示词。
要求：
1. 详细描述视觉元素、色彩、氛围
2. 使用专业的摄影术语
3. 适合小红书风格（明亮、清晰、吸引人）
4. 输出纯英文，不超过200字

描述：{description}
主题：{topic}

只输出英文提示词，不要其他内容。"""

        dalle_prompt = client.call_llm(
            prompt=prompt,
            model_name="gpt-4o-mini",
            temperature=0.7,
            max_tokens=200
        ).strip()
        
        return dalle_prompt
        
    except Exception as e:
        logger.warning(f"DALL-E 提示词生成失败，使用简化版本: {str(e)}")
        return f"High quality photo of {description}, bright and clear, suitable for social media"


def _create_sd_prompt(description: str, topic: str) -> str:
    """
    创建适合 Stable Diffusion 的提示词
    """
    # SD 提示词通常需要更详细的标签式描述
    try:
        client = LLMClient()
        
        prompt = f"""请将以下图片需求转换为适合 Stable Diffusion 的英文提示词。
要求：
1. 使用标签式描述，用逗号分隔
2. 包含画质标签：masterpiece, best quality, high resolution
3. 描述风格、光线、构图
4. 输出纯英文

描述：{description}
主题：{topic}

只输出英文提示词（标签式），不要其他内容。"""

        sd_prompt = client.call_llm(
            prompt=prompt,
            model_name="gpt-4o-mini",
            temperature=0.7,
            max_tokens=150
        ).strip()
        
        return sd_prompt
        
    except Exception as e:
        logger.warning(f"SD 提示词生成失败，使用简化版本: {str(e)}")
        return f"masterpiece, best quality, high resolution, {description}, bright lighting, photorealistic"


def _download_and_save_image(
    image_url: str,
    topic: str,
    index: int,
    source: str = "unknown"
) -> Optional[str]:
    """
    下载并保存图片到本地
    
    Returns:
        保存的文件路径，如果失败返回 None
    """
    try:
        # 1. 下载图片
        logger.info(f"下载图片: {image_url}")
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        
        # 2. 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # 生成唯一文件名（使用URL哈希避免重复）
        url_hash = hashlib.md5(image_url.encode()).hexdigest()[:8]
        filename = f"{timestamp}_{topic}_{index + 1}_{source}_{url_hash}.jpg"
        
        # 3. 保存到本地
        save_path = PathConfig.IMAGES_DIR / filename
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(save_path, "wb") as f:
            f.write(response.content)
        
        logger.info(f"图片已保存: {save_path}")
        return str(save_path.absolute())
        
    except Exception as e:
        logger.error(f"下载或保存图片失败: {str(e)}", exc_info=True)
        return None


def _save_base64_image(
    image_base64: str,
    topic: str,
    index: int,
    source: str = "generated"
) -> Optional[str]:
    """
    保存 base64 编码的图片
    """
    try:
        import base64
        
        # 解码 base64
        image_data = base64.b64decode(image_base64)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{topic}_{index + 1}_{source}.png"
        
        # 保存到本地
        save_path = PathConfig.IMAGES_DIR / filename
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(save_path, "wb") as f:
            f.write(image_data)
        
        logger.info(f"图片已保存: {save_path}")
        return str(save_path.absolute())
        
    except Exception as e:
        logger.error(f"保存 base64 图片失败: {str(e)}", exc_info=True)
        return None


# 便捷函数：从草稿生成图片
def generate_images_from_draft(
    draft_id: str,
    method: str = "dalle",
    count: Optional[int] = None
) -> str:
    """
    从草稿文件读取图片建议并使用 AI 生成图片
    
    Args:
        draft_id: 草稿ID
        method: 生成方法（dalle 或 local，默认 dalle）
        count: 图片数量
        
    Returns:
        JSON格式的生成结果
    """
    try:
        # 1. 读取草稿文件
        draft_path = PathConfig.DRAFTS_DIR / f"{draft_id}.json"
        
        if not draft_path.exists():
            return json.dumps({
                "success": False,
                "error": f"草稿文件不存在: {draft_id}",
                "message": "图片生成失败"
            }, ensure_ascii=False)
        
        with open(draft_path, "r", encoding="utf-8") as f:
            draft_data = json.load(f)
        
        # 2. 提取图片建议
        content = draft_data.get("content", {})
        image_suggestions = content.get("image_suggestions", [])
        topic = draft_data.get("topic", "未知主题")
        
        # 3. 生成图片
        result = generate_images_for_content(
            image_suggestions=json.dumps(image_suggestions, ensure_ascii=False),
            topic=topic,
            count=count,
            method=method,
            save_to_disk=True
        )
        
        # 4. 更新草稿文件（添加生成的图片信息）
        result_data = json.loads(result)
        if result_data.get("success"):
            draft_data["generated_images"] = result_data["images"]
            draft_data["image_generation_method"] = method
            draft_data["image_generation_timestamp"] = datetime.now().isoformat()
            
            with open(draft_path, "w", encoding="utf-8") as f:
                json.dump(draft_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"草稿已更新，包含生成的图片信息: {draft_id}")
        
        return result
        
    except Exception as e:
        error_msg = f"从草稿生成图片失败: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return json.dumps({
            "success": False,
            "error": error_msg,
            "message": "图片生成失败"
        }, ensure_ascii=False)


if __name__ == "__main__":
    # 测试代码
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # 测试图片生成
    test_suggestions = json.dumps([
        {
            "description": "Sydney Opera House at sunset with harbor views",
            "purpose": "展示悉尼地标",
            "position": 1
        },
        {
            "description": "Beautiful beach with clear blue water in Sydney",
            "purpose": "展示海滩景色",
            "position": 2
        }
    ], ensure_ascii=False)
    
    result = generate_images_for_content(
        image_suggestions=test_suggestions,
        topic="悉尼旅游",
        count=2,
        method="unsplash",
        save_to_disk=True
    )
    
    print("\n" + "=" * 60)
    print("图片生成结果:")
    print("=" * 60)
    print(result)

