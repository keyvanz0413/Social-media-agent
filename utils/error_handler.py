"""
统一错误处理模块
提供标准化的错误处理、降级策略和错误响应格式
"""

import logging
import json
import traceback
from typing import Any, Callable, Dict, Optional, TypeVar, Union
from functools import wraps
from enum import Enum

logger = logging.getLogger(__name__)

T = TypeVar('T')


class ErrorSeverity(Enum):
    """错误严重程度"""
    LOW = "low"           # 轻微错误，可以继续
    MEDIUM = "medium"     # 中等错误，需要降级
    HIGH = "high"         # 严重错误，需要中止
    CRITICAL = "critical" # 致命错误，系统级问题


class ErrorCategory(Enum):
    """错误类别"""
    NETWORK = "network"           # 网络错误
    API = "api"                   # API调用错误
    VALIDATION = "validation"     # 数据验证错误
    CONFIGURATION = "configuration" # 配置错误
    RESOURCE = "resource"         # 资源错误（内存、磁盘等）
    BUSINESS = "business"         # 业务逻辑错误
    UNKNOWN = "unknown"           # 未知错误


class AgentError(Exception):
    """Agent基础异常类"""
    
    def __init__(
        self,
        message: str,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    ):
        super().__init__(message)
        self.message = message
        self.category = category
        self.severity = severity
        self.details = details or {}
        self.original_error = original_error
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "error": self.message,
            "category": self.category.value,
            "severity": self.severity.value,
            "details": self.details,
            "original_error": str(self.original_error) if self.original_error else None
        }
    
    def to_json(self) -> str:
        """转换为JSON格式"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


class NetworkError(AgentError):
    """网络相关错误"""
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.MEDIUM,
            **kwargs
        )


class APIError(AgentError):
    """API调用错误"""
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.API,
            severity=ErrorSeverity.MEDIUM,
            **kwargs
        )


class ValidationError(AgentError):
    """数据验证错误"""
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.LOW,
            **kwargs
        )


class ConfigurationError(AgentError):
    """配置错误"""
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.CONFIGURATION,
            severity=ErrorSeverity.HIGH,
            **kwargs
        )


def create_error_response(
    error: Union[Exception, str],
    success: bool = False,
    additional_info: Optional[Dict[str, Any]] = None
) -> str:
    """
    创建标准化的错误响应
    
    Args:
        error: 错误对象或错误消息
        success: 是否成功
        additional_info: 额外信息
    
    Returns:
        JSON格式的错误响应
    """
    response = {
        "success": success,
        "error": str(error),
        "message": "操作失败",
    }
    
    # 如果是AgentError，添加详细信息
    if isinstance(error, AgentError):
        response.update({
            "category": error.category.value,
            "severity": error.severity.value,
            "details": error.details
        })
    
    # 添加额外信息
    if additional_info:
        response.update(additional_info)
    
    return json.dumps(response, ensure_ascii=False, indent=2)


def create_success_response(
    data: Any,
    message: str = "操作成功",
    additional_info: Optional[Dict[str, Any]] = None
) -> str:
    """
    创建标准化的成功响应
    
    Args:
        data: 返回数据
        message: 成功消息
        additional_info: 额外信息
    
    Returns:
        JSON格式的成功响应
    """
    response = {
        "success": True,
        "message": message,
        "data": data
    }
    
    if additional_info:
        response.update(additional_info)
    
    return json.dumps(response, ensure_ascii=False, indent=2)


def with_error_handling(
    fallback_value: Any = None,
    fallback_function: Optional[Callable] = None,
    log_traceback: bool = True,
    reraise: bool = False
):
    """
    错误处理装饰器
    
    Args:
        fallback_value: 发生错误时返回的默认值
        fallback_function: 降级函数，发生错误时调用
        log_traceback: 是否记录完整的错误堆栈
        reraise: 是否重新抛出异常
    
    Example:
        @with_error_handling(fallback_value="{}", log_traceback=True)
        def my_function():
            # 可能会出错的代码
            pass
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # 记录错误
                error_msg = f"函数 {func.__name__} 执行失败: {str(e)}"
                
                if log_traceback:
                    logger.error(error_msg, exc_info=True)
                else:
                    logger.error(error_msg)
                
                # 尝试降级函数
                if fallback_function:
                    try:
                        logger.info(f"尝试降级策略: {fallback_function.__name__}")
                        return fallback_function(*args, **kwargs)
                    except Exception as fallback_error:
                        logger.error(f"降级策略也失败: {str(fallback_error)}")
                
                # 重新抛出异常
                if reraise:
                    raise
                
                # 返回默认值
                if fallback_value is not None:
                    logger.info(f"返回默认值: {type(fallback_value).__name__}")
                    return fallback_value
                
                # 返回错误响应
                return create_error_response(e)
        
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
        backoff_factor: 退避因子
        exceptions: 需要重试的异常类型
    
    Example:
        @with_retry(max_attempts=3, delay=1.0)
        def unstable_function():
            # 可能失败的函数
            pass
    """
    import time
    
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
    安全解析JSON字符串
    
    Args:
        json_str: JSON字符串
        default: 解析失败时的默认值
        strict: 是否严格模式（失败时抛出异常）
    
    Returns:
        解析后的数据或默认值
    """
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.warning(f"JSON解析失败: {str(e)}")
        
        if strict:
            raise ValidationError(
                f"无效的JSON格式: {str(e)}",
                details={"json_str": json_str[:100]}
            )
        
        return default
    except Exception as e:
        logger.error(f"JSON解析出现未知错误: {str(e)}")
        
        if strict:
            raise
        
        return default


def validate_required_fields(
    data: Dict[str, Any],
    required_fields: list,
    field_name: str = "数据"
) -> None:
    """
    验证必需字段是否存在
    
    Args:
        data: 数据字典
        required_fields: 必需字段列表
        field_name: 字段名称（用于错误消息）
    
    Raises:
        ValidationError: 如果缺少必需字段
    """
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        raise ValidationError(
            f"{field_name}缺少必需字段: {', '.join(missing_fields)}",
            details={
                "missing_fields": missing_fields,
                "required_fields": required_fields,
                "available_fields": list(data.keys())
            }
        )


def handle_api_error(error: Exception, api_name: str = "API") -> str:
    """
    处理API错误，返回友好的错误消息
    
    Args:
        error: 异常对象
        api_name: API名称
    
    Returns:
        JSON格式的错误响应
    """
    error_msg = str(error)
    
    # 根据错误类型提供具体建议
    suggestions = []
    
    if "timeout" in error_msg.lower():
        suggestions.append("请检查网络连接")
        suggestions.append("可能是服务响应较慢，请稍后重试")
    elif "401" in error_msg or "unauthorized" in error_msg.lower():
        suggestions.append("请检查API Key是否正确配置")
        suggestions.append("请确认API Key是否过期")
    elif "429" in error_msg or "rate limit" in error_msg.lower():
        suggestions.append("API调用频率超限，请稍后重试")
        suggestions.append("考虑启用缓存以减少API调用")
    elif "500" in error_msg or "503" in error_msg:
        suggestions.append("服务端错误，请稍后重试")
    
    return create_error_response(
        error,
        additional_info={
            "api_name": api_name,
            "suggestions": suggestions
        }
    )


class ErrorRecoveryStrategy:
    """错误恢复策略"""
    
    @staticmethod
    def with_fallback_chain(
        primary_func: Callable,
        fallback_funcs: list,
        *args,
        **kwargs
    ) -> Any:
        """
        使用降级链执行函数
        
        Args:
            primary_func: 主函数
            fallback_funcs: 降级函数列表
            *args, **kwargs: 函数参数
        
        Returns:
            执行结果
        """
        funcs = [primary_func] + fallback_funcs
        last_error = None
        
        for i, func in enumerate(funcs):
            try:
                logger.info(f"尝试执行: {func.__name__} (策略 {i+1}/{len(funcs)})")
                result = func(*args, **kwargs)
                
                if i > 0:
                    logger.warning(f"主函数失败，使用降级策略 {i}: {func.__name__}")
                
                return result
            except Exception as e:
                last_error = e
                logger.warning(f"策略 {i+1} 失败: {str(e)}")
                continue
        
        # 所有策略都失败
        logger.error(f"所有降级策略都失败，最后一个错误: {str(last_error)}")
        raise last_error


# 导出
__all__ = [
    'AgentError',
    'NetworkError',
    'APIError',
    'ValidationError',
    'ConfigurationError',
    'ErrorSeverity',
    'ErrorCategory',
    'create_error_response',
    'create_success_response',
    'with_error_handling',
    'with_retry',
    'safe_json_parse',
    'validate_required_fields',
    'handle_api_error',
    'ErrorRecoveryStrategy'
]

