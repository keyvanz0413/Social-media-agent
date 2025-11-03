"""
性能监控模块
提供函数执行时间、资源使用、API调用统计等监控功能
"""

import time
import logging
import functools
import psutil
from typing import Callable, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import json
from collections import defaultdict

logger = logging.getLogger(__name__)


class PerformanceMetrics:
    """性能指标收集器"""
    
    def __init__(self):
        self.metrics = defaultdict(list)
        self.function_calls = defaultdict(int)
        self.function_durations = defaultdict(list)
        self.errors = defaultdict(int)
    
    def record_duration(self, func_name: str, duration: float):
        """记录函数执行时间"""
        self.function_durations[func_name].append(duration)
        self.function_calls[func_name] += 1
    
    def record_error(self, func_name: str):
        """记录错误"""
        self.errors[func_name] += 1
    
    def record_metric(self, metric_name: str, value: Any):
        """记录自定义指标"""
        self.metrics[metric_name].append({
            "value": value,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_stats(self, func_name: Optional[str] = None) -> Dict[str, Any]:
        """
        获取统计信息
        
        Args:
            func_name: 函数名（可选），如果提供则返回该函数的统计
        
        Returns:
            统计信息字典
        """
        if func_name:
            durations = self.function_durations.get(func_name, [])
            return {
                "function": func_name,
                "calls": self.function_calls.get(func_name, 0),
                "errors": self.errors.get(func_name, 0),
                "total_time": sum(durations),
                "avg_time": sum(durations) / len(durations) if durations else 0,
                "min_time": min(durations) if durations else 0,
                "max_time": max(durations) if durations else 0
            }
        
        # 返回全局统计
        return {
            "total_calls": sum(self.function_calls.values()),
            "total_errors": sum(self.errors.values()),
            "functions": {
                name: self.get_stats(name)
                for name in self.function_calls.keys()
            }
        }
    
    def print_summary(self):
        """打印性能摘要"""
        stats = self.get_stats()
        
        print("\n" + "=" * 70)
        print("📊 性能监控摘要")
        print("=" * 70)
        print(f"\n总调用次数: {stats['total_calls']}")
        print(f"总错误次数: {stats['total_errors']}")
        
        print("\n函数执行统计:")
        print("-" * 70)
        print(f"{'函数名':<40} {'调用次数':<10} {'平均耗时':<15}")
        print("-" * 70)
        
        for func_name, func_stats in sorted(
            stats['functions'].items(),
            key=lambda x: x[1]['avg_time'],
            reverse=True
        ):
            print(
                f"{func_name:<40} "
                f"{func_stats['calls']:<10} "
                f"{func_stats['avg_time']:.3f}s"
            )
        
        print("=" * 70 + "\n")
    
    def save_to_file(self, file_path: str):
        """保存统计信息到文件"""
        stats = self.get_stats()
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        logger.info(f"性能统计已保存到: {file_path}")


# 全局性能指标收集器
_global_metrics = PerformanceMetrics()


def get_metrics() -> PerformanceMetrics:
    """获取全局性能指标收集器"""
    return _global_metrics


def log_performance(
    func: Optional[Callable] = None,
    *,
    log_args: bool = False,
    log_result: bool = False,
    log_memory: bool = False,
    warn_threshold: Optional[float] = None
):
    """
    性能监控装饰器
    
    Args:
        func: 被装饰的函数
        log_args: 是否记录函数参数
        log_result: 是否记录函数返回值
        log_memory: 是否记录内存使用
        warn_threshold: 警告阈值（秒），超过此时间会发出警告
    
    Example:
        @log_performance(warn_threshold=5.0)
        def slow_function():
            time.sleep(6)
    """
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            func_name = f"{f.__module__}.{f.__name__}"
            
            # 记录开始信息
            start_time = time.time()
            start_memory = psutil.Process().memory_info().rss / 1024 / 1024 if log_memory else 0
            
            # 记录参数
            if log_args:
                logger.debug(f"{func_name} 开始执行，参数: args={args}, kwargs={kwargs}")
            else:
                logger.debug(f"{func_name} 开始执行")
            
            try:
                # 执行函数
                result = f(*args, **kwargs)
                
                # 计算执行时间
                duration = time.time() - start_time
                
                # 记录到指标收集器
                _global_metrics.record_duration(func_name, duration)
                
                # 记录内存使用
                memory_info = ""
                if log_memory:
                    end_memory = psutil.Process().memory_info().rss / 1024 / 1024
                    memory_delta = end_memory - start_memory
                    memory_info = f", 内存变化: {memory_delta:+.2f}MB"
                
                # 记录执行信息
                log_msg = f"{func_name} 执行完成，耗时: {duration:.3f}s{memory_info}"
                
                # 根据阈值决定日志级别
                if warn_threshold and duration > warn_threshold:
                    logger.warning(f"⚠️  {log_msg} (超过阈值 {warn_threshold}s)")
                else:
                    logger.info(log_msg)
                
                # 记录返回值
                if log_result:
                    logger.debug(f"{func_name} 返回值: {result}")
                
                return result
            
            except Exception as e:
                # 记录错误
                duration = time.time() - start_time
                _global_metrics.record_error(func_name)
                
                logger.error(
                    f"{func_name} 执行失败，耗时: {duration:.3f}s，错误: {str(e)}",
                    exc_info=True
                )
                raise
        
        return wrapper
    
    # 支持 @log_performance 和 @log_performance() 两种用法
    if func is None:
        return decorator
    else:
        return decorator(func)


def log_api_call(service_name: str = "API"):
    """
    API调用监控装饰器
    
    Args:
        service_name: 服务名称
    
    Example:
        @log_api_call(service_name="OpenAI")
        def call_openai_api():
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            func_name = f"{func.__module__}.{func.__name__}"
            
            start_time = time.time()
            logger.info(f"📡 {service_name} API 调用开始: {func_name}")
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                logger.info(
                    f"✅ {service_name} API 调用成功: {func_name}, "
                    f"耗时: {duration:.3f}s"
                )
                
                # 记录API调用指标
                _global_metrics.record_metric(
                    f"api_call_{service_name.lower()}",
                    {
                        "function": func_name,
                        "duration": duration,
                        "status": "success"
                    }
                )
                
                return result
            
            except Exception as e:
                duration = time.time() - start_time
                
                logger.error(
                    f"❌ {service_name} API 调用失败: {func_name}, "
                    f"耗时: {duration:.3f}s, 错误: {str(e)}"
                )
                
                # 记录API错误
                _global_metrics.record_metric(
                    f"api_call_{service_name.lower()}",
                    {
                        "function": func_name,
                        "duration": duration,
                        "status": "error",
                        "error": str(e)
                    }
                )
                
                raise
        
        return wrapper
    return decorator


class Timer:
    """计时器上下文管理器"""
    
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
        
        log_func = getattr(logger, self.log_level)
        
        if exc_type is None:
            log_func(f"⏱️  {self.name} 完成，耗时: {duration:.3f}s")
        else:
            logger.error(f"⏱️  {self.name} 失败，耗时: {duration:.3f}s")
    
    @property
    def elapsed(self) -> float:
        """获取已经过的时间"""
        if self.start_time is None:
            return 0.0
        
        if self.end_time is None:
            return time.time() - self.start_time
        
        return self.end_time - self.start_time


def profile_memory(func: Callable) -> Callable:
    """
    内存使用分析装饰器
    
    Example:
        @profile_memory
        def memory_intensive_function():
            data = [0] * 10000000
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        import gc
        
        # 强制垃圾回收
        gc.collect()
        
        # 记录开始内存
        process = psutil.Process()
        mem_before = process.memory_info().rss / 1024 / 1024
        
        # 执行函数
        result = func(*args, **kwargs)
        
        # 记录结束内存
        mem_after = process.memory_info().rss / 1024 / 1024
        mem_delta = mem_after - mem_before
        
        func_name = f"{func.__module__}.{func.__name__}"
        logger.info(
            f"💾 {func_name} 内存使用: {mem_before:.2f}MB → {mem_after:.2f}MB "
            f"(变化: {mem_delta:+.2f}MB)"
        )
        
        return result
    
    return wrapper


def get_system_stats() -> Dict[str, Any]:
    """获取系统资源使用统计"""
    process = psutil.Process()
    
    return {
        "cpu_percent": process.cpu_percent(interval=0.1),
        "memory_mb": process.memory_info().rss / 1024 / 1024,
        "memory_percent": process.memory_percent(),
        "num_threads": process.num_threads(),
        "timestamp": datetime.now().isoformat()
    }


def print_system_stats():
    """打印系统资源使用情况"""
    stats = get_system_stats()
    
    print("\n" + "=" * 50)
    print("💻 系统资源使用")
    print("=" * 50)
    print(f"CPU使用率: {stats['cpu_percent']:.1f}%")
    print(f"内存使用: {stats['memory_mb']:.1f}MB ({stats['memory_percent']:.1f}%)")
    print(f"线程数: {stats['num_threads']}")
    print("=" * 50 + "\n")


# 导出
__all__ = [
    'PerformanceMetrics',
    'get_metrics',
    'log_performance',
    'log_api_call',
    'Timer',
    'profile_memory',
    'get_system_stats',
    'print_system_stats'
]

