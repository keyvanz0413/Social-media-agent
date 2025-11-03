"""
测试性能监控模块
"""

import pytest
import time
from utils.performance_monitor import (
    PerformanceMetrics,
    get_metrics,
    log_performance,
    log_api_call,
    Timer,
    profile_memory,
    get_system_stats
)


def test_performance_metrics():
    """测试性能指标收集器"""
    metrics = PerformanceMetrics()
    
    # 记录执行时间
    metrics.record_duration("test_func", 1.5)
    metrics.record_duration("test_func", 2.0)
    
    # 获取统计
    stats = metrics.get_stats("test_func")
    
    assert stats["calls"] == 2
    assert stats["avg_time"] == 1.75
    assert stats["min_time"] == 1.5
    assert stats["max_time"] == 2.0


def test_log_performance_decorator():
    """测试性能监控装饰器"""
    
    @log_performance
    def sample_function():
        time.sleep(0.1)
        return "result"
    
    result = sample_function()
    assert result == "result"
    
    # 验证指标已记录
    metrics = get_metrics()
    func_name = f"{sample_function.__module__}.{sample_function.__name__}"
    stats = metrics.get_stats(func_name)
    assert stats["calls"] >= 1


def test_log_performance_with_threshold():
    """测试带警告阈值的性能监控"""
    
    @log_performance(warn_threshold=0.05)
    def slow_function():
        time.sleep(0.1)
        return "done"
    
    result = slow_function()
    assert result == "done"


def test_log_api_call_decorator():
    """测试API调用监控装饰器"""
    
    @log_api_call(service_name="TestAPI")
    def call_test_api():
        time.sleep(0.05)
        return {"status": "ok"}
    
    result = call_test_api()
    assert result["status"] == "ok"


def test_timer_context_manager():
    """测试计时器上下文管理器"""
    
    with Timer("测试操作") as timer:
        time.sleep(0.1)
    
    assert timer.elapsed >= 0.1


def test_profile_memory_decorator():
    """测试内存分析装饰器"""
    
    @profile_memory
    def memory_test():
        data = [0] * 1000000
        return len(data)
    
    result = memory_test()
    assert result == 1000000


def test_get_system_stats():
    """测试获取系统统计"""
    stats = get_system_stats()
    
    assert "cpu_percent" in stats
    assert "memory_mb" in stats
    assert "num_threads" in stats
    assert stats["cpu_percent"] >= 0


def test_metrics_stats_summary():
    """测试指标统计摘要"""
    metrics = PerformanceMetrics()
    
    # 记录多个函数的执行
    metrics.record_duration("func1", 1.0)
    metrics.record_duration("func1", 1.5)
    metrics.record_duration("func2", 0.5)
    metrics.record_error("func2")
    
    # 获取全局统计
    stats = metrics.get_stats()
    
    assert stats["total_calls"] == 3
    assert stats["total_errors"] == 1
    assert len(stats["functions"]) == 2


def test_metrics_save_to_file(tmp_path):
    """测试保存指标到文件"""
    import json
    
    metrics = PerformanceMetrics()
    metrics.record_duration("test_func", 1.0)
    
    file_path = tmp_path / "metrics.json"
    metrics.save_to_file(str(file_path))
    
    # 验证文件已创建
    assert file_path.exists()
    
    # 验证内容
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    assert "total_calls" in data
    assert data["total_calls"] >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

