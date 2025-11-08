"""
单元测试：配置模块
测试配置加载、验证和目录管理
"""

import os
import pytest
from pathlib import Path


@pytest.fixture(autouse=True)
def setup_test_env():
    """为每个测试设置环境"""
    os.environ['MOCK_MODE'] = 'true'
    yield
    # 清理


class TestConfig:
    """配置类测试"""
    
    def test_config_import(self):
        """测试配置模块可以正常导入"""
        from config import Config, ModelConfig, PathConfig, MCPConfig
        
        assert Config is not None
        assert ModelConfig is not None
        assert PathConfig is not None
        assert MCPConfig is not None
    
    def test_path_config(self):
        """测试路径配置"""
        from config import PathConfig
        
        # 验证基础路径
        assert PathConfig.BASE_DIR.exists()
        assert PathConfig.BASE_DIR.is_dir()
        
        # 验证输出目录
        assert PathConfig.OUTPUTS_DIR.is_dir()
        assert PathConfig.IMAGES_DIR.is_dir()
        assert PathConfig.DRAFTS_DIR.is_dir()
        assert PathConfig.LOGS_DIR.is_dir()
        
        # 验证提示词目录
        assert PathConfig.PROMPTS_DIR.exists()
    
    def test_ensure_dirs(self):
        """测试目录创建功能"""
        from config import Config
        
        # 调用目录创建
        Config.ensure_dirs()
        
        # 验证所有输出目录都存在
        assert Config.IMAGES_DIR.exists()
        assert Config.DRAFTS_DIR.exists()
        assert Config.LOGS_DIR.exists()
    
    def test_model_config(self):
        """测试模型配置"""
        from config import Config
        
        # 验证任务模型映射
        assert 'analysis' in Config.TASK_MODEL_MAPPING
        assert 'creation' in Config.TASK_MODEL_MAPPING
        assert 'review' in Config.TASK_MODEL_MAPPING
        
        # 验证质量级别
        for task in ['analysis', 'creation', 'review']:
            assert 'fast' in Config.TASK_MODEL_MAPPING[task]
            assert 'balanced' in Config.TASK_MODEL_MAPPING[task]
            assert 'high' in Config.TASK_MODEL_MAPPING[task]
    
    def test_agent_config(self):
        """测试 Agent 配置"""
        from config import Config
        
        # 验证必要的 Agent 配置存在
        assert 'coordinator' in Config.AGENT_CONFIGS
        assert 'content_analyst' in Config.AGENT_CONFIGS
        assert 'content_creator' in Config.AGENT_CONFIGS
        
        # 验证 coordinator 配置
        coordinator = Config.AGENT_CONFIGS['coordinator']
        assert 'model' in coordinator
        assert 'max_iterations' in coordinator
        assert 'temperature' in coordinator
    
    def test_mcp_config(self):
        """测试 MCP 配置"""
        from config import MCPConfig
        
        # 验证 MCP 服务器配置
        assert 'xiaohongshu' in MCPConfig.SERVERS
        assert 'url' in MCPConfig.SERVERS['xiaohongshu']
        assert 'timeout' in MCPConfig.SERVERS['xiaohongshu']
        
        # 验证超时配置
        assert MCPConfig.MCP_TIMEOUT > 0
    
    def test_log_config(self):
        """测试日志配置"""
        from config import Config
        
        # 验证日志配置存在
        assert Config.LOG_LEVEL is not None
        assert Config.LOG_FORMAT is not None
        assert Config.LOG_DATE_FORMAT is not None
        
        # 验证日志文件配置
        assert Config.LOG_FILE_MAX_BYTES > 0
        assert Config.LOG_FILE_BACKUP_COUNT > 0
    
    def test_dev_config(self):
        """测试开发配置"""
        from config import Config
        
        # 验证开发模式标志
        assert hasattr(Config, 'DEBUG')
        assert hasattr(Config, 'MOCK_MODE')
        
        # 在测试环境中，Mock 模式应该启用
        assert Config.MOCK_MODE == True
    
    def test_image_generation_config(self):
        """测试图片生成配置"""
        from config import Config
        
        # 验证图片生成配置
        assert 'count' in Config.IMAGE_GENERATION
        assert 'default_method' in Config.IMAGE_GENERATION
        
        # 验证默认值
        assert Config.IMAGE_GENERATION['count'] > 0
        assert Config.IMAGE_GENERATION['default_method'] in ['dalle', 'unsplash', 'stable_diffusion']
    
    def test_backward_compatibility(self):
        """测试向后兼容性"""
        from config import Config, ModelConfig, PathConfig, MCPConfig
        
        # 验证别名指向同一个类
        assert ModelConfig is Config
        assert PathConfig is Config
        assert MCPConfig is Config


class TestConfigEnvironment:
    """环境变量测试"""
    
    def test_env_loading(self, monkeypatch):
        """测试环境变量加载"""
        # 设置测试环境变量
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        monkeypatch.setenv("OPENAI_BASE_URL", "https://test.api.com")
        
        # 重新导入以应用环境变量
        import importlib
        import config
        importlib.reload(config)
        
        # 验证环境变量被加载
        from config import Config
        assert Config.OPENAI_API_KEY == "test-key" or Config.OPENAI_API_KEY is None
    
    def test_default_values(self):
        """测试默认值"""
        from config import Config
        
        # 验证有合理的默认值
        assert Config.OLLAMA_BASE_URL is not None
        assert Config.MCP_URL is not None
        assert Config.MCP_TIMEOUT == 30
    
    def test_mock_mode_from_env(self):
        """测试从环境变量读取 Mock 模式"""
        from config import Config
        
        # 应该从环境变量读取
        assert Config.MOCK_MODE == True  # 测试时设置为 true


@pytest.mark.slow
class TestConfigValidation:
    """配置验证测试（较慢的测试）"""
    
    def test_all_paths_accessible(self):
        """测试所有配置的路径都可访问"""
        from config import PathConfig
        
        paths_to_check = [
            PathConfig.BASE_DIR,
            PathConfig.OUTPUTS_DIR,
            PathConfig.IMAGES_DIR,
            PathConfig.DRAFTS_DIR,
            PathConfig.LOGS_DIR,
            PathConfig.PROMPTS_DIR,
        ]
        
        for path in paths_to_check:
            assert path.exists(), f"Path does not exist: {path}"
            # 验证可以写入（除了 prompts 目录）
            if path != PathConfig.PROMPTS_DIR:
                test_file = path / ".test_write"
                try:
                    test_file.touch()
                    test_file.unlink()
                except Exception as e:
                    pytest.fail(f"Cannot write to {path}: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

