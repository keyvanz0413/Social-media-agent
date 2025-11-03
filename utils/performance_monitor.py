"""
性能监控模块（简化版）
提供基础的计时功能
"""

import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class Timer:
    """
    计时器上下文管理器
    
    Example:
        >>> with Timer("数据处理"):
        ...     # 执行耗时操作
        ...     process_data()
        
        >>> timer = Timer("API调用")
        >>> with timer:
        ...     call_api()
        >>> print(f"耗时: {timer.elapsed:.2f}秒")
    """
    
    def __init__(self, name: str = "操作", log_level: str = "info"):
        """
        初始化计时器
        
        Args:
            name: 操作名称
            log_level: 日志级别 (debug/info/warning/error)
        """
        self.name = name
        self.log_level = log_level
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        logger.debug(f"⏱️  {self.name} 开始")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        
        log_func = getattr(logger, self.log_level, logger.info)
        
        if exc_type is None:
            log_func(f"⏱️  {self.name} 完成，耗时: {duration:.2f}s")
        else:
            logger.error(f"⏱️  {self.name} 失败，耗时: {duration:.2f}s")
        
        # 不抑制异常
        return False
    
    @property
    def elapsed(self) -> float:
        """获取已经过的时间（秒）"""
        if self.start_time is None:
            return 0.0
        
        if self.end_time is None:
            return time.time() - self.start_time
        
        return self.end_time - self.start_time


def log_execution_time(func):
    """
    简单的执行时间记录装饰器
    
    Example:
        @log_execution_time
        def slow_function():
            time.sleep(2)
    """
    from functools import wraps
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start
            logger.info(f"⏱️  {func.__name__} 执行完成，耗时: {elapsed:.2f}s")
            return result
        except Exception as e:
            elapsed = time.time() - start
            logger.error(f"⏱️  {func.__name__} 执行失败，耗时: {elapsed:.2f}s")
            raise
    
    return wrapper


# 导出
__all__ = ['Timer', 'log_execution_time']
