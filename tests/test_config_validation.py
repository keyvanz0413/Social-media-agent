"""
测试配置验证功能
"""

import pytest
import os
from config import ModelConfig


def test_validate_config():
    """测试配置验证"""
    result = ModelConfig.validate_config()
    
    assert "success" in result
    assert "errors" in result
    assert "warnings" in result
    assert isinstance(result["errors"], list)
    assert isinstance(result["warnings"], list)


def test_check_model_available():
    """测试模型可用性检查"""
    # 检查已知模型
    is_available = ModelConfig.check_model_available("gpt-4o")
    assert isinstance(is_available, bool)


def test_get_available_models():
    """测试获取所有模型可用性"""
    models = ModelConfig.get_available_models()
    
    assert isinstance(models, dict)
    assert len(models) > 0
    
    # 所有值应该是布尔值
    for model_name, is_available in models.items():
        assert isinstance(is_available, bool)


def test_get_api_config():
    """测试获取API配置"""
    config = ModelConfig.get_api_config()
    
    assert isinstance(config, dict)
    # 如果有配置，应该包含必要的键
    if config:
        assert 'api_key' in config or 'base_url' in config


def test_model_info_structure():
    """测试MODEL_INFO结构完整性"""
    for model_name, info in ModelConfig.MODEL_INFO.items():
        assert "provider" in info
        assert "description" in info
        assert "strengths" in info
        assert "cost_level" in info
        assert isinstance(info["strengths"], list)


def test_fallback_models_structure():
    """测试降级模型配置"""
    for model, fallback in ModelConfig.FALLBACK_MODELS.items():
        # 主模型应该在MODEL_INFO中
        if model in ModelConfig.MODEL_INFO:
            # 降级模型也应该在MODEL_INFO中（除非为None）
            if fallback is not None:
                assert fallback in ModelConfig.MODEL_INFO or fallback in ["gpt-4o-mini", "gpt-4o"]


def test_task_model_mapping():
    """测试任务模型映射"""
    for task_type, quality_models in ModelConfig.TASK_MODEL_MAPPING.items():
        assert "fast" in quality_models
        assert "balanced" in quality_models
        assert "high" in quality_models


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

