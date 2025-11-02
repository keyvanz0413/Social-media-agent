"""
Publisher Agent
发布内容到小红书平台
使用 MCP 客户端调用小红书发布功能
"""

import json
import logging
import re
from typing import Dict, Any, List, Optional
from pathlib import Path

from utils.mcp_client import XiaohongshuMCPClient, XiaohongshuMCPError
from config import MCPConfig, PathConfig

# 配置日志
logger = logging.getLogger(__name__)


def publish_to_xiaohongshu(
    title: str,
    content: str,
    images: Optional[List[str]] = None,
    video_path: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> str:
    """
    发布内容到小红书
    
    Args:
        title: 标题（不超过20字）
        content: 正文内容（不超过1000字）
        images: 图片路径列表（可选，支持本地路径或HTTP链接）
        video_path: 视频路径（可选，仅支持本地路径）
        tags: 标签列表（可选）
        
    Returns:
        JSON格式的发布结果，包含：
        - success: 是否成功
        - note_id: 笔记ID（如果成功）
        - url: 笔记链接（如果成功）
        - message: 状态消息
        - error: 错误信息（如果失败）
        
    Example:
        >>> result = publish_to_xiaohongshu(
        ...     title="澳洲旅游攻略",
        ...     content="分享我的澳洲旅行经历...",
        ...     images=["/path/to/image1.jpg", "/path/to/image2.jpg"],
        ...     tags=["澳洲", "旅游", "攻略"]
        ... )
        >>> print(result)
        '{"success": true, "note_id": "xxx", "message": "发布成功"}'
    """
    try:
        # 1. 验证输入参数
        validation_result = _validate_publish_params(title, content, images, video_path)
        if not validation_result["valid"]:
            return json.dumps({
                "success": False,
                "error": validation_result["error"],
                "message": "参数验证失败"
            }, ensure_ascii=False)
        
        # 2. 初始化 MCP 客户端
        mcp_url = MCPConfig.SERVERS["xiaohongshu"]["url"]
        timeout = MCPConfig.SERVERS["xiaohongshu"]["timeout"]
        
        logger.info(f"初始化MCP客户端，地址: {mcp_url}")
        client = XiaohongshuMCPClient(base_url=mcp_url, timeout=timeout)
        
        try:
            # 3. 检查登录状态
            logger.info("检查小红书登录状态...")
            login_status = client.check_login_status()
            
            if not login_status.get("is_logged_in", False):
                error_msg = "未登录小红书账号，请先登录"
                logger.error(error_msg)
                return json.dumps({
                    "success": False,
                    "error": error_msg,
                    "message": "发布失败：需要先登录小红书账号"
                }, ensure_ascii=False)
            
            username = login_status.get("username", "未知用户")
            logger.info(f"登录状态正常，用户: {username}")
            
            # 4. 处理标签（从content中提取或使用传入的tags）
            final_tags = tags or []
            if not final_tags:
                # 尝试从content中提取话题标签
                extracted_tags = _extract_tags_from_content(content)
                if extracted_tags:
                    final_tags = extracted_tags
                    logger.info(f"从内容中提取到标签: {final_tags}")
            
            # 5. 发布内容
            if video_path:
                # 发布视频笔记
                logger.info(f"开始发布视频笔记: {title}")
                result = client.publish_video(
                    title=title,
                    content=content,
                    video_path=video_path,
                    tags=final_tags
                )
                logger.info("视频笔记发布成功")
            else:
                # 发布图文笔记
                logger.info(f"开始发布图文笔记: {title}, 图片数量: {len(images) if images else 0}")
                
                # 处理图片路径（确保绝对路径）
                processed_images = _process_image_paths(images) if images else []
                
                result = client.publish_note(
                    title=title,
                    content=content,
                    images=processed_images,
                    tags=final_tags
                )
                logger.info("图文笔记发布成功")
            
            # 6. 格式化返回结果
            return json.dumps({
                "success": True,
                "note_id": result.get("note_id", ""),
                "url": result.get("url", ""),
                "message": "发布成功",
                "data": result
            }, ensure_ascii=False)
            
        except XiaohongshuMCPError as e:
            error_msg = f"MCP调用失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return json.dumps({
                "success": False,
                "error": error_msg,
                "message": "发布失败"
            }, ensure_ascii=False)
            
        finally:
            # 关闭客户端连接
            client.close()
            
    except Exception as e:
        error_msg = f"发布过程中发生未知错误: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return json.dumps({
            "success": False,
            "error": error_msg,
            "message": "发布失败"
        }, ensure_ascii=False)


def _validate_publish_params(
    title: str,
    content: str,
    images: Optional[List[str]],
    video_path: Optional[str]
) -> Dict[str, Any]:
    """
    验证发布参数
    
    Returns:
        {"valid": bool, "error": str}
    """
    # 验证标题
    if not title or not title.strip():
        return {"valid": False, "error": "标题不能为空"}
    
    if len(title) > 20:
        return {"valid": False, "error": f"标题不能超过20字（当前: {len(title)}字）"}
    
    # 验证正文
    if not content or not content.strip():
        return {"valid": False, "error": "正文内容不能为空"}
    
    if len(content) > 1000:
        return {"valid": False, "error": f"正文不能超过1000字（当前: {len(content)}字）"}
    
    # 验证图片和视频
    if video_path and images:
        return {"valid": False, "error": "不能同时指定视频和图片，请选择一种类型"}
    
    if not video_path and (not images or len(images) == 0):
        return {"valid": False, "error": "必须提供至少一张图片或一个视频"}
    
    # 验证视频路径（如果提供）
    if video_path:
        video_path_obj = Path(video_path)
        if not video_path_obj.exists():
            return {"valid": False, "error": f"视频文件不存在: {video_path}"}
        
        if not video_path_obj.is_file():
            return {"valid": False, "error": f"视频路径不是文件: {video_path}"}
        
        # 检查视频格式（可选）
        valid_extensions = [".mp4", ".mov", ".avi", ".mkv"]
        if video_path_obj.suffix.lower() not in valid_extensions:
            logger.warning(f"视频格式可能不支持: {video_path_obj.suffix}")
    
    # 验证图片路径（如果提供）
    if images:
        for img_path in images:
            # HTTP链接跳过文件系统检查
            if img_path.startswith(("http://", "https://")):
                continue
            
            img_path_obj = Path(img_path)
            if not img_path_obj.exists():
                return {"valid": False, "error": f"图片文件不存在: {img_path}"}
            
            if not img_path_obj.is_file():
                return {"valid": False, "error": f"图片路径不是文件: {img_path}"}
    
    return {"valid": True, "error": None}


def _process_image_paths(images: List[str]) -> List[str]:
    """
    处理图片路径，确保返回绝对路径
    
    Args:
        images: 图片路径列表（可能是相对路径或HTTP链接）
        
    Returns:
        处理后的图片路径列表
    """
    processed = []
    
    for img_path in images:
        # HTTP链接直接使用
        if img_path.startswith(("http://", "https://")):
            processed.append(img_path)
            continue
        
        # 本地路径转换为绝对路径
        img_path_obj = Path(img_path)
        
        if not img_path_obj.is_absolute():
            # 如果是相对路径，尝试从多个可能的基准路径解析
            # 1. 当前工作目录
            abs_path = Path.cwd() / img_path_obj
            if abs_path.exists():
                processed.append(str(abs_path.absolute()))
                continue
            
            # 2. 图片输出目录
            abs_path = PathConfig.IMAGES_DIR / img_path_obj
            if abs_path.exists():
                processed.append(str(abs_path.absolute()))
                continue
            
            # 3. 如果都不存在，仍然使用原路径（让MCP服务器处理）
            logger.warning(f"相对路径未找到，使用原路径: {img_path}")
            processed.append(str(img_path_obj.resolve()))
        else:
            processed.append(str(img_path_obj.absolute()))
    
    return processed


def _extract_tags_from_content(content: str) -> List[str]:
    """
    从内容中提取话题标签（简单的提取逻辑）
    
    注意：这是一个简单实现，更好的方式可能需要使用LLM来分析
    
    Args:
        content: 正文内容
        
    Returns:
        提取的标签列表
    """
    tags = []
    
    # 查找 #话题# 格式的标签
    hashtag_pattern = r'#([^#]+)#'
    matches = re.findall(hashtag_pattern, content)
    
    for match in matches:
        tag = match.strip()
        if tag and len(tag) <= 10:  # 标签长度限制
            tags.append(tag)
    
    # 如果找到标签，返回前5个
    return tags[:5] if tags else []


