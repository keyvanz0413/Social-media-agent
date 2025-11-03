"""
测试错误处理模块
"""

import pytest
import json
from utils.error_handler import (
    AgentError,
    NetworkError,
    APIError,
    ValidationError,
    ConfigurationError,
    ErrorSeverity,
    ErrorCategory,
    create_error_response,
    create_success_response,
    with_error_handling,
    with_retry,
    safe_json_parse,
    validate_required_fields,
    handle_api_error,
    ErrorRecoveryStrategy
)


def test_agent_error_creation():
    """测试AgentError创建"""
    error = AgentError(
        "测试错误",
        category=ErrorCategory.NETWORK,
        severity=ErrorSeverity.HIGH
    )
    
    assert error.message == "测试错误"
    assert error.category == ErrorCategory.NETWORK
    assert error.severity == ErrorSeverity.HIGH
    
    # 测试转换为字典
    error_dict = error.to_dict()
    assert error_dict["error"] == "测试错误"
    assert error_dict["category"] == "network"
    assert error_dict["severity"] == "high"


def test_specific_errors():
    """测试特定错误类型"""
    # 网络错误
    net_error = NetworkError("连接失败")
    assert net_error.category == ErrorCategory.NETWORK
    
    # API错误
    api_error = APIError("API调用失败")
    assert api_error.category == ErrorCategory.API
    
    # 验证错误
    val_error = ValidationError("数据验证失败")
    assert val_error.category == ErrorCategory.VALIDATION
    
    # 配置错误
    cfg_error = ConfigurationError("配置错误")
    assert cfg_error.category == ErrorCategory.CONFIGURATION


def test_create_error_response():
    """测试创建错误响应"""
    response = create_error_response("测试错误")
    data = json.loads(response)
    
    assert data["success"] is False
    assert "测试错误" in data["error"]


def test_create_success_response():
    """测试创建成功响应"""
    response = create_success_response(
        {"result": "ok"},
        message="操作成功"
    )
    data = json.loads(response)
    
    assert data["success"] is True
    assert data["message"] == "操作成功"
    assert data["data"]["result"] == "ok"


def test_with_error_handling_decorator():
    """测试错误处理装饰器"""
    
    @with_error_handling(fallback_value="default", reraise=False)
    def failing_function():
        raise ValueError("测试错误")
    
    result = failing_function()
    assert result == "default"


def test_with_error_handling_with_fallback_function():
    """测试带降级函数的错误处理"""
    
    def fallback():
        return "fallback_result"
    
    @with_error_handling(fallback_function=fallback, reraise=False)
    def failing_function():
        raise ValueError("测试错误")
    
    result = failing_function()
    assert result == "fallback_result"


def test_with_retry_decorator():
    """测试重试装饰器"""
    call_count = {"count": 0}
    
    @with_retry(max_attempts=3, delay=0.1)
    def unstable_function():
        call_count["count"] += 1
        if call_count["count"] < 3:
            raise ValueError("暂时失败")
        return "success"
    
    result = unstable_function()
    assert result == "success"
    assert call_count["count"] == 3


def test_safe_json_parse():
    """测试安全JSON解析"""
    # 正常解析
    data = safe_json_parse('{"key": "value"}')
    assert data["key"] == "value"
    
    # 解析失败，返回默认值
    data = safe_json_parse('invalid json', default={"error": True})
    assert data["error"] is True
    
    # 严格模式，抛出异常
    with pytest.raises(ValidationError):
        safe_json_parse('invalid json', strict=True)


def test_validate_required_fields():
    """测试必需字段验证"""
    # 正常情况
    data = {"name": "test", "age": 10}
    validate_required_fields(data, ["name", "age"])
    
    # 缺少字段
    with pytest.raises(ValidationError) as exc_info:
        validate_required_fields(data, ["name", "age", "email"])
    
    assert "email" in str(exc_info.value)


def test_handle_api_error():
    """测试API错误处理"""
    # 超时错误
    error = TimeoutError("连接超时")
    response = handle_api_error(error, "TestAPI")
    data = json.loads(response)
    
    assert data["success"] is False
    assert "suggestions" in data
    assert len(data["suggestions"]) > 0


def test_error_recovery_strategy():
    """测试错误恢复策略"""
    call_count = {"count": 0}
    
    def primary_func(value):
        call_count["count"] += 1
        raise ValueError("主函数失败")
    
    def fallback_func(value):
        call_count["count"] += 1
        return f"fallback_{value}"
    
    result = ErrorRecoveryStrategy.with_fallback_chain(
        primary_func,
        [fallback_func],
        "test"
    )
    
    assert result == "fallback_test"
    assert call_count["count"] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

