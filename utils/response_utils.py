"""
统一的工具返回格式
提供标准化的成功/失败响应结构
"""

import json
from typing import Any, Dict, Optional, List
from datetime import datetime


class ToolResponse:
    """统一的工具响应格式"""
    
    def __init__(
        self,
        success: bool,
        data: Any = None,
        message: str = "",
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        初始化工具响应
        
        Args:
            success: 是否成功
            data: 返回的数据
            message: 提示信息
            error: 错误信息（仅在失败时）
            metadata: 额外的元数据（如时间戳、版本等）
        """
        self.success = success
        self.data = data
        self.message = message
        self.error = error
        self.metadata = metadata or {}
        
        # 自动添加时间戳
        if 'timestamp' not in self.metadata:
            self.metadata['timestamp'] = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            'success': self.success,
            'message': self.message
        }
        
        if self.data is not None:
            result['data'] = self.data
        
        if self.error:
            result['error'] = self.error
        
        if self.metadata:
            result['metadata'] = self.metadata
        
        return result
    
    def to_json(self) -> str:
        """转换为 JSON 字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    def __str__(self) -> str:
        """字符串表示"""
        return self.to_json()
    
    @classmethod
    def success_response(
        cls,
        data: Any = None,
        message: str = "操作成功",
        metadata: Optional[Dict[str, Any]] = None
    ) -> 'ToolResponse':
        """
        创建成功响应
        
        Args:
            data: 返回的数据
            message: 成功提示信息
            metadata: 额外的元数据
            
        Returns:
            ToolResponse 对象
        """
        return cls(
            success=True,
            data=data,
            message=message,
            metadata=metadata
        )
    
    @classmethod
    def error_response(
        cls,
        error: str,
        message: str = "操作失败",
        data: Any = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> 'ToolResponse':
        """
        创建失败响应
        
        Args:
            error: 错误信息
            message: 失败提示信息
            data: 返回的数据（可选）
            metadata: 额外的元数据
            
        Returns:
            ToolResponse 对象
        """
        return cls(
            success=False,
            data=data,
            message=message,
            error=error,
            metadata=metadata
        )


def create_success_response(
    data: Any = None,
    message: str = "操作成功",
    **metadata
) -> str:
    """
    快捷创建成功响应的 JSON 字符串
    
    Args:
        data: 返回的数据
        message: 成功提示信息
        **metadata: 额外的元数据（作为关键字参数传入）
        
    Returns:
        JSON 字符串
        
    Example:
        >>> response = create_success_response(
        ...     data={'title': '标题', 'content': '内容'},
        ...     message='内容创作成功',
        ...     word_count=100
        ... )
        >>> print(response)
        {
          "success": true,
          "message": "内容创作成功",
          "data": {...},
          "metadata": {"word_count": 100, "timestamp": "..."}
        }
    """
    return ToolResponse.success_response(
        data=data,
        message=message,
        metadata=metadata if metadata else None
    ).to_json()


def create_error_response(
    error: str,
    message: str = "操作失败",
    data: Any = None,
    **metadata
) -> str:
    """
    快捷创建失败响应的 JSON 字符串
    
    Args:
        error: 错误信息
        message: 失败提示信息
        data: 返回的数据（可选）
        **metadata: 额外的元数据
        
    Returns:
        JSON 字符串
        
    Example:
        >>> response = create_error_response(
        ...     error='API 调用超时',
        ...     message='分析失败',
        ...     retry_after=60
        ... )
        >>> print(response)
        {
          "success": false,
          "message": "分析失败",
          "error": "API 调用超时",
          "metadata": {"retry_after": 60, "timestamp": "..."}
        }
    """
    return ToolResponse.error_response(
        error=error,
        message=message,
        data=data,
        metadata=metadata if metadata else None
    ).to_json()


def parse_tool_response(response_str: str) -> ToolResponse:
    """
    解析工具响应 JSON 字符串
    
    Args:
        response_str: JSON 格式的响应字符串
        
    Returns:
        ToolResponse 对象
        
    Raises:
        ValueError: 如果解析失败
    """
    try:
        data = json.loads(response_str)
        return ToolResponse(
            success=data.get('success', False),
            data=data.get('data'),
            message=data.get('message', ''),
            error=data.get('error'),
            metadata=data.get('metadata', {})
        )
    except json.JSONDecodeError as e:
        raise ValueError(f"无法解析响应 JSON: {str(e)}")
    except Exception as e:
        raise ValueError(f"解析响应失败: {str(e)}")


def is_success(response_str: str) -> bool:
    """
    检查工具响应是否成功
    
    Args:
        response_str: JSON 格式的响应字符串
        
    Returns:
        是否成功
    """
    try:
        response = parse_tool_response(response_str)
        return response.success
    except Exception:
        return False


def get_response_data(response_str: str) -> Any:
    """
    从响应中提取数据
    
    Args:
        response_str: JSON 格式的响应字符串
        
    Returns:
        响应中的数据，如果解析失败则返回 None
    """
    try:
        response = parse_tool_response(response_str)
        return response.data
    except Exception:
        return None


def get_response_error(response_str: str) -> Optional[str]:
    """
    从响应中提取错误信息
    
    Args:
        response_str: JSON 格式的响应字符串
        
    Returns:
        错误信息，如果没有错误则返回 None
    """
    try:
        response = parse_tool_response(response_str)
        return response.error
    except Exception:
        return None


# 向后兼容：提供旧的 JSON 解析函数
def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """
    安全地解析 JSON 字符串
    
    Args:
        json_str: JSON 字符串
        default: 解析失败时的默认值
        
    Returns:
        解析后的数据，失败时返回 default
    """
    try:
        return json.loads(json_str)
    except Exception:
        return default


__all__ = [
    'ToolResponse',
    'create_success_response',
    'create_error_response',
    'parse_tool_response',
    'is_success',
    'get_response_data',
    'get_response_error',
    'safe_json_loads'
]

