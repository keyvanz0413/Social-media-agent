"""
性能监控模块（简化版）
提供基础的计时功能
"""

import time
import logging
from typing import Optional, Dict, List

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


class PerformanceMetrics:
    """简化版性能指标收集器（向后兼容）。"""

    def __init__(self):
        self._durations: Dict[str, List[float]] = {}

    def record_duration(self, name: str, duration: float):
        self._durations.setdefault(name, []).append(float(duration))

    def get_stats(self, name: str) -> Dict[str, float]:
        values = self._durations.get(name, [])
        if not values:
            return {
                "count": 0,
                "calls": 0,
                "avg": 0.0,
                "avg_time": 0.0,
                "total_time": 0.0,
                "min": 0.0,
                "max": 0.0,
            }
        total = sum(values)
        avg = total / len(values)
        return {
            "count": len(values),
            "calls": len(values),
            "avg": avg,
            "avg_time": avg,
            "total_time": total,
            "min": min(values),
            "max": max(values),
        }


def log_performance(name: str):
    """向后兼容别名：与 log_execution_time 类似的性能日志装饰器。"""

    def decorator(func):
        from functools import wraps

        @wraps(func)
        def wrapper(*args, **kwargs):
            with Timer(name):
                return func(*args, **kwargs)

        return wrapper

    return decorator


# 导出
__all__ = ['Timer', 'log_execution_time', 'PerformanceMetrics', 'log_performance']
