"""
带缓存的 MCP 客户端包装器
提供缓存功能，减少重复搜索，提升性能
"""

import json
import logging
from typing import Dict, Any, Optional

from .mcp_client import XiaohongshuMCPClient, XiaohongshuMCPError
from .cache_manager import get_cache_manager, cache_key

logger = logging.getLogger(__name__)


class CachedXiaohongshuMCPClient(XiaohongshuMCPClient):
    """
    带缓存的小红书 MCP 客户端
    
    在原有功能基础上添加了缓存支持，避免重复搜索
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:18060",
        timeout: int = 30,
        max_retries: int = 3,
        cache_enabled: bool = True,
        cache_ttl: int = 1800  # 默认30分钟
    ):
        """
        初始化带缓存的 MCP 客户端
        
        Args:
            base_url: MCP 服务器地址
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
            cache_enabled: 是否启用缓存
            cache_ttl: 缓存过期时间（秒）
        """
        super().__init__(base_url, timeout, max_retries)
        
        self.cache_enabled = cache_enabled
        self.cache_ttl = cache_ttl
        self.cache_manager = get_cache_manager() if cache_enabled else None
        
        if cache_enabled:
            logger.info(f"缓存已启用，TTL: {cache_ttl}秒")
    
    def search_notes(
        self,
        keyword: str,
        limit: int = 10,
        sort_type: str = "general",
        note_type: int = 0
    ) -> Dict[str, Any]:
        """
        搜索小红书笔记（带缓存）
        
        Args:
            keyword: 搜索关键词
            limit: 返回数量
            sort_type: 排序类型
            note_type: 笔记类型
            
        Returns:
            搜索结果
        """
        # 生成缓存键
        key = cache_key(
            "mcp_search",
            keyword,
            limit=limit,
            sort_type=sort_type,
            note_type=note_type
        )
        
        # 尝试从缓存获取
        if self.cache_enabled:
            cached_result = self.cache_manager.get(key)
            if cached_result:
                logger.info(f"✅ 使用缓存的搜索结果: {keyword}")
                return cached_result
        
        # 调用父类方法进行实际搜索
        logger.info(f"🔍 执行 MCP 搜索: {keyword}")
        result = super().search_notes(keyword, limit, sort_type, note_type)
        
        # 缓存结果
        if self.cache_enabled and result:
            self.cache_manager.set(key, result, ttl=self.cache_ttl)
            logger.info(f"💾 搜索结果已缓存: {keyword}")
        
        return result
    
    def get_note_detail(
        self,
        note_id: str,
        xsec_token: str = ""
    ) -> Dict[str, Any]:
        """
        获取笔记详情（带缓存）
        
        Args:
            note_id: 笔记ID
            xsec_token: 安全令牌
            
        Returns:
            笔记详情
        """
        # 生成缓存键
        key = cache_key("mcp_note_detail", note_id)
        
        # 尝试从缓存获取
        if self.cache_enabled:
            cached_result = self.cache_manager.get(key)
            if cached_result:
                logger.info(f"✅ 使用缓存的笔记详情: {note_id}")
                return cached_result
        
        # 调用父类方法
        logger.info(f"🔍 获取笔记详情: {note_id}")
        result = super().get_note_detail(note_id, xsec_token)
        
        # 缓存结果
        if self.cache_enabled and result:
            self.cache_manager.set(key, result, ttl=self.cache_ttl)
            logger.info(f"💾 笔记详情已缓存: {note_id}")
        
        return result
    
    def clear_cache(self) -> None:
        """清除所有缓存"""
        if self.cache_enabled:
            # 只清除 MCP 相关的缓存
            count = 0
            for key in list(self.cache_manager._memory_cache.keys()):
                if key.startswith("mcp_"):
                    self.cache_manager.delete(key)
                    count += 1
            
            logger.info(f"已清除 {count} 个 MCP 缓存")
    
    def get_cache_stats(self) -> dict:
        """获取缓存统计"""
        if self.cache_enabled:
            return self.cache_manager.get_stats()
        return {"cache_enabled": False}


def get_cached_mcp_client(
    base_url: str = "http://localhost:18060",
    cache_ttl: int = 1800
) -> CachedXiaohongshuMCPClient:
    """
    获取带缓存的 MCP 客户端实例
    
    Args:
        base_url: MCP 服务器地址
        cache_ttl: 缓存过期时间（秒）
        
    Returns:
        带缓存的 MCP 客户端
        
    Example:
        >>> client = get_cached_mcp_client()
        >>> # 第一次搜索会调用 MCP
        >>> result1 = client.search_notes("悉尼旅游", limit=5)
        >>> # 第二次搜索会使用缓存（30分钟内）
        >>> result2 = client.search_notes("悉尼旅游", limit=5)
    """
    return CachedXiaohongshuMCPClient(
        base_url=base_url,
        cache_enabled=True,
        cache_ttl=cache_ttl
    )


__all__ = [
    'CachedXiaohongshuMCPClient',
    'get_cached_mcp_client'
]

