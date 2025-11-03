"""
通用工具函数

提供：
1. JSON 清理和解析
2. Agent 创建辅助函数
3. 错误处理装饰器
4. 简单缓存工具
"""

import json
import re
import sys
import warnings
import logging
from typing import Any, Dict, Callable
from functools import wraps

logger = logging.getLogger(__name__)


# ========== JSON 工具 ==========

def clean_json_response(response: str) -> str:
    """
    清理 LLM 返回的 JSON 响应
    移除 markdown 代码块标记
    
    Args:
        response: LLM 原始响应
        
    Returns:
        清理后的 JSON 字符串
    """
    cleaned = response.strip()
    
    # 移除 markdown 代码块
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    
    return cleaned.strip()


def parse_llm_json(response: str) -> Dict[str, Any]:
    """
    解析 LLM 返回的 JSON
    处理常见的格式问题（markdown 代码块、控制字符等）
    
    Args:
        response: LLM 原始响应
        
    Returns:
        解析后的字典
        
    Raises:
        ValueError: JSON 解析失败
        
    Example:
        >>> result = parse_llm_json('```json\\n{"title": "test"}\\n```')
        >>> print(result['title'])
        'test'
    """
    # 1. 清理响应
    cleaned = clean_json_response(response)
    
    try:
        # 2. 尝试解析（Python 3.9+ 支持 strict=False）
        if sys.version_info >= (3, 9):
            return json.loads(cleaned, strict=False)
        else:
            # 旧版本：清理控制字符
            cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', cleaned)
            return json.loads(cleaned)
    
    except json.JSONDecodeError as e:
        logger.warning(f"JSON 解析失败，尝试修复: {str(e)}")
        
        # 3. 尝试提取 JSON 对象
        json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if json_match:
            try:
                potential_json = json_match.group(0)
                if sys.version_info >= (3, 9):
                    return json.loads(potential_json, strict=False)
                else:
                    potential_json = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', potential_json)
                    return json.loads(potential_json)
            except Exception as repair_error:
                logger.error(f"JSON 修复失败: {str(repair_error)}")
        
        # 4. 解析失败
        raise ValueError(f"无法解析 LLM 返回的 JSON: {str(e)}")


# ========== Agent 工具 ==========

def create_agent_silent(
    name: str,
    system_prompt: str,
    tools: list,
    model: str,
    max_iterations: int = 10,
    **kwargs
):
    """
    创建 Agent（静默 ConnectOnion 的警告）
    
    Args:
        name: Agent 名称
        system_prompt: 系统提示词
        tools: 工具函数列表
        model: 模型名称
        max_iterations: 最大迭代次数
        **kwargs: 其他参数
        
    Returns:
        配置好的 Agent 实例
        
    Example:
        >>> agent = create_agent_silent(
        ...     name="test_agent",
        ...     system_prompt="你是一个测试助手",
        ...     tools=[tool1, tool2],
        ...     model="gpt-4o-mini"
        ... )
    """
    try:
        from connectonion import Agent
    except ImportError:
        raise ImportError("ConnectOnion 未安装，请运行: pip install connectonion")
    
    logger.info(f"创建 Agent: {name}, 模型: {model}")
    
    # 静默警告
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning, module="connectonion")
        agent = Agent(
            name=name,
            system_prompt=system_prompt,
            tools=tools,
            model=model,
            max_iterations=max_iterations,
            **kwargs
        )
    
    logger.info(f"Agent {name} 创建成功")
    return agent


# ========== 错误处理装饰器 ==========

def handle_tool_errors(operation_name: str):
    """
    装饰器：统一处理工具函数的错误
    
    Args:
        operation_name: 操作名称（用于日志）
        
    Returns:
        装饰器函数
        
    Example:
        >>> @handle_tool_errors("内容分析")
        ... def analyze_content(keyword: str):
        ...     # 函数逻辑
        ...     return result
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            func_logger = logging.getLogger(func.__module__)
            try:
                return func(*args, **kwargs)
            except Exception as e:
                func_logger.error(
                    f"{operation_name} 失败: {str(e)}", 
                    exc_info=True
                )
                # 返回标准错误格式
                return json.dumps({
                    "success": False,
                    "error": str(e),
                    "message": f"{operation_name} 失败"
                }, ensure_ascii=False)
        return wrapper
    return decorator


# ========== 简单缓存工具 ==========

import time
from typing import Optional

_simple_cache: Dict[str, tuple] = {}


def get_cache(key: str) -> Optional[Any]:
    """
    获取缓存
    
    Args:
        key: 缓存键
        
    Returns:
        缓存值，如果不存在或过期则返回 None
    """
    if key in _simple_cache:
        value, expire_time = _simple_cache[key]
        if time.time() < expire_time:
            return value
        else:
            # 过期，删除
            del _simple_cache[key]
    return None


def set_cache(key: str, value: Any, ttl: int = 1800):
    """
    设置缓存
    
    Args:
        key: 缓存键
        value: 缓存值
        ttl: 过期时间（秒），默认 30 分钟
    """
    expire_time = time.time() + ttl
    _simple_cache[key] = (value, expire_time)


def clear_cache():
    """清空所有缓存"""
    _simple_cache.clear()


def make_cache_key(*args, **kwargs) -> str:
    """
    生成缓存键
    
    Example:
        >>> key = make_cache_key("search", "澳洲", limit=5)
        >>> print(key)
        'search:澳洲:limit=5'
    """
    parts = [str(arg) for arg in args]
    if kwargs:
        sorted_kwargs = sorted(kwargs.items())
        kwargs_str = ":".join(f"{k}={v}" for k, v in sorted_kwargs)
        parts.append(kwargs_str)
    return ":".join(parts)


# 导出
__all__ = [
    # JSON 工具
    'clean_json_response',
    'parse_llm_json',
    
    # Agent 工具
    'create_agent_silent',
    
    # 错误处理
    'handle_tool_errors',
    
    # 缓存工具
    'get_cache',
    'set_cache',
    'clear_cache',
    'make_cache_key',
]

