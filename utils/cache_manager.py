"""
缓存管理器
用于缓存搜索结果、评审结果等，提升性能并降低成本
"""

import json
import hashlib
import logging
import time
from typing import Any, Optional, Dict
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

from config import PathConfig

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """缓存条目"""
    key: str
    value: Any
    created_at: float
    expires_at: Optional[float] = None
    hit_count: int = 0
    
    def is_expired(self) -> bool:
        """检查是否过期"""
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'CacheEntry':
        """从字典创建"""
        return cls(**data)


class CacheManager:
    """
    缓存管理器
    
    特点：
    - 内存缓存 + 磁盘持久化
    - TTL（过期时间）支持
    - 命中统计
    - 自动清理过期缓存
    """
    
    def __init__(
        self,
        cache_dir: Path = None,
        default_ttl: int = 3600,  # 默认1小时
        max_memory_items: int = 100
    ):
        """
        初始化缓存管理器
        
        Args:
            cache_dir: 缓存目录
            default_ttl: 默认过期时间（秒）
            max_memory_items: 内存中最多保留的缓存项数
        """
        self.cache_dir = cache_dir or (PathConfig.OUTPUTS_DIR / "cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.default_ttl = default_ttl
        self.max_memory_items = max_memory_items
        
        # 内存缓存
        self._memory_cache: Dict[str, CacheEntry] = {}
        
        # 统计
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0
        }
        
        logger.info(f"缓存管理器初始化: {self.cache_dir}")
    
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存
        
        Args:
            key: 缓存键
            
        Returns:
            缓存值，不存在或过期返回 None
        """
        # 1. 先查内存缓存
        if key in self._memory_cache:
            entry = self._memory_cache[key]
            
            if entry.is_expired():
                logger.debug(f"缓存过期: {key}")
                del self._memory_cache[key]
                self._delete_disk_cache(key)
                self.stats["misses"] += 1
                return None
            
            # 命中
            entry.hit_count += 1
            self.stats["hits"] += 1
            logger.debug(f"缓存命中（内存）: {key}")
            return entry.value
        
        # 2. 查磁盘缓存
        entry = self._load_disk_cache(key)
        if entry:
            if entry.is_expired():
                logger.debug(f"缓存过期: {key}")
                self._delete_disk_cache(key)
                self.stats["misses"] += 1
                return None
            
            # 加载到内存
            self._memory_cache[key] = entry
            self._evict_if_needed()
            
            entry.hit_count += 1
            self.stats["hits"] += 1
            logger.debug(f"缓存命中（磁盘）: {key}")
            return entry.value
        
        # 3. 未命中
        self.stats["misses"] += 1
        logger.debug(f"缓存未命中: {key}")
        return None
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> None:
        """
        设置缓存
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒），None使用默认值
        """
        if ttl is None:
            ttl = self.default_ttl
        
        now = time.time()
        expires_at = now + ttl if ttl > 0 else None
        
        entry = CacheEntry(
            key=key,
            value=value,
            created_at=now,
            expires_at=expires_at
        )
        
        # 保存到内存
        self._memory_cache[key] = entry
        self._evict_if_needed()
        
        # 保存到磁盘
        self._save_disk_cache(entry)
        
        self.stats["sets"] += 1
        logger.debug(f"缓存已设置: {key} (TTL: {ttl}秒)")
    
    def delete(self, key: str) -> bool:
        """
        删除缓存
        
        Args:
            key: 缓存键
            
        Returns:
            是否成功删除
        """
        deleted = False
        
        if key in self._memory_cache:
            del self._memory_cache[key]
            deleted = True
        
        if self._delete_disk_cache(key):
            deleted = True
        
        if deleted:
            logger.debug(f"缓存已删除: {key}")
        
        return deleted
    
    def clear(self) -> None:
        """清空所有缓存"""
        self._memory_cache.clear()
        
        # 清空磁盘缓存
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                cache_file.unlink()
            except Exception as e:
                logger.warning(f"删除缓存文件失败: {cache_file}, {str(e)}")
        
        logger.info("所有缓存已清空")
    
    def cleanup_expired(self) -> int:
        """
        清理过期缓存
        
        Returns:
            清理的数量
        """
        count = 0
        
        # 清理内存
        expired_keys = [
            k for k, v in self._memory_cache.items()
            if v.is_expired()
        ]
        for key in expired_keys:
            del self._memory_cache[key]
            count += 1
        
        # 清理磁盘
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    entry = CacheEntry.from_dict(data)
                    if entry.is_expired():
                        cache_file.unlink()
                        count += 1
            except Exception as e:
                logger.warning(f"清理缓存文件失败: {cache_file}, {str(e)}")
        
        if count > 0:
            logger.info(f"清理了 {count} 个过期缓存")
        
        return count
    
    def get_stats(self) -> dict:
        """
        获取缓存统计
        
        Returns:
            统计信息字典
        """
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = (
            self.stats["hits"] / total_requests * 100
            if total_requests > 0 else 0
        )
        
        return {
            **self.stats,
            "hit_rate": f"{hit_rate:.1f}%",
            "memory_items": len(self._memory_cache),
            "total_requests": total_requests
        }
    
    def _evict_if_needed(self) -> None:
        """如果内存缓存超限，淘汰最少使用的项"""
        if len(self._memory_cache) <= self.max_memory_items:
            return
        
        # 按命中次数排序，删除最少使用的
        items = sorted(
            self._memory_cache.items(),
            key=lambda x: x[1].hit_count
        )
        
        to_remove = len(self._memory_cache) - self.max_memory_items
        for key, _ in items[:to_remove]:
            del self._memory_cache[key]
            logger.debug(f"缓存淘汰: {key}")
    
    def _get_cache_path(self, key: str) -> Path:
        """获取缓存文件路径"""
        # 使用MD5哈希作为文件名
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.json"
    
    def _save_disk_cache(self, entry: CacheEntry) -> None:
        """保存缓存到磁盘"""
        try:
            cache_path = self._get_cache_path(entry.key)
            with open(cache_path, 'w') as f:
                json.dump(entry.to_dict(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"保存缓存到磁盘失败: {entry.key}, {str(e)}")
    
    def _load_disk_cache(self, key: str) -> Optional[CacheEntry]:
        """从磁盘加载缓存"""
        try:
            cache_path = self._get_cache_path(key)
            if not cache_path.exists():
                return None
            
            with open(cache_path, 'r') as f:
                data = json.load(f)
                return CacheEntry.from_dict(data)
        except Exception as e:
            logger.warning(f"从磁盘加载缓存失败: {key}, {str(e)}")
            return None
    
    def _delete_disk_cache(self, key: str) -> bool:
        """删除磁盘缓存"""
        try:
            cache_path = self._get_cache_path(key)
            if cache_path.exists():
                cache_path.unlink()
                return True
            return False
        except Exception as e:
            logger.warning(f"删除磁盘缓存失败: {key}, {str(e)}")
            return False


# 全局缓存实例
_global_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """
    获取全局缓存管理器实例
    
    Returns:
        CacheManager 实例
    """
    global _global_cache_manager
    
    if _global_cache_manager is None:
        _global_cache_manager = CacheManager()
    
    return _global_cache_manager


def cache_key(*args, **kwargs) -> str:
    """
    生成缓存键
    
    Args:
        *args: 位置参数
        **kwargs: 关键字参数
        
    Returns:
        缓存键字符串
        
    Example:
        >>> key = cache_key("search", "悉尼旅游", limit=5)
        >>> print(key)
        search:悉尼旅游:limit=5
    """
    parts = [str(arg) for arg in args]
    
    if kwargs:
        sorted_kwargs = sorted(kwargs.items())
        kwargs_str = ":".join(f"{k}={v}" for k, v in sorted_kwargs)
        parts.append(kwargs_str)
    
    return ":".join(parts)


__all__ = [
    'CacheManager',
    'CacheEntry',
    'get_cache_manager',
    'cache_key'
]

