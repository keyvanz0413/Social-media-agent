"""
简化的错误处理模块
提供基础的错误处理装饰器和重试机制
"""

import logging
import time
import json
from typing import Any, Callable, Optional, TypeVar
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar('T')


def with_error_handling(
    fallback_value: Any = None,
    log_traceback: bool = True
):
    """
    错误处理装饰器
    
    Args:
        fallback_value: 发生错误时返回的默认值
        log_traceback: 是否记录完整的错误堆栈
    
    Example:
        @with_error_handling(fallback_value='{"error": "处理失败"}')
        def risky_function():
            # 可能会出错的代码
            return process_data()
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_msg = f"函数 {func.__name__} 执行失败: {str(e)}"
                
                if log_traceback:
                    logger.error(error_msg, exc_info=True)
                else:
                    logger.error(error_msg)
                
                # 返回默认值
                if fallback_value is not None:
                    logger.info(f"返回默认值: {type(fallback_value).__name__}")
                    return fallback_value
                
                # 如果没有默认值，返回错误响应
                from utils.response_utils import create_error_response
                return create_error_response(str(e))
        
        return wrapper
    return decorator


def with_retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    重试装饰器
    
    Args:
        max_attempts: 最大重试次数
        delay: 初始延迟时间（秒）
        backoff_factor: 退避因子（每次重试延迟时间翻倍）
        exceptions: 需要重试的异常类型
    
    Example:
        @with_retry(max_attempts=3, delay=1.0)
        def unstable_api_call():
            # 可能失败的 API 调用
            return call_external_api()
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            current_delay = delay
            
            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1
                    if attempt >= max_attempts:
                        logger.error(
                            f"函数 {func.__name__} 在 {max_attempts} 次尝试后仍然失败"
                        )
                        raise
                    
                    logger.warning(
                        f"函数 {func.__name__} 执行失败（尝试 {attempt}/{max_attempts}），"
                        f"{current_delay:.1f}秒后重试: {str(e)}"
                    )
                    time.sleep(current_delay)
                    current_delay *= backoff_factor
            
            return None
        
        return wrapper
    return decorator


def safe_json_parse(
    json_str: str,
    default: Any = None,
    strict: bool = False
) -> Any:
    """
    安全解析 JSON 字符串
    
    Args:
        json_str: JSON 字符串
        default: 解析失败时的默认值
        strict: 是否严格模式（失败时抛出异常）
    
    Returns:
        解析后的数据或默认值
    
    Example:
        >>> data = safe_json_parse('{"key": "value"}')
        >>> print(data)
        {'key': 'value'}
        
        >>> data = safe_json_parse('invalid json', default={})
        >>> print(data)
        {}
    """
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.warning(f"JSON 解析失败: {str(e)}")
        
        if strict:
            raise ValueError(f"无效的 JSON 格式: {str(e)}")
        
        return default
    except Exception as e:
        logger.error(f"JSON 解析出现未知错误: {str(e)}")
        
        if strict:
            raise
        
        return default


# 导出
__all__ = [
    'with_error_handling',
    'with_retry',
    'safe_json_parse'
]
