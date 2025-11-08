"""
配置管理模块
集中管理所有配置项：API密钥、路径、模型配置等
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Config:
    """统一配置类"""
    
    # API配置
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    
    # 路径配置
    BASE_DIR = Path(__file__).parent.absolute()
    OUTPUTS_DIR = BASE_DIR / "outputs"
    IMAGES_DIR = OUTPUTS_DIR / "images"
    DRAFTS_DIR = OUTPUTS_DIR / "drafts"
    LOGS_DIR = OUTPUTS_DIR / "logs"
    PROMPTS_DIR = BASE_DIR / "prompts"
    
    # MCP配置
    MCP_URL = os.getenv("MCP_XIAOHONGSHU_URL", "http://localhost:18060")
    MCP_TIMEOUT = 30
    
    SERVERS = {
        "xiaohongshu": {
            "url": MCP_URL,
            "timeout": MCP_TIMEOUT
        }
    }
    
    # 模型配置
    TASK_MODEL_MAPPING = {
        "analysis": {
            "fast": "qwen-turbo",
            "balanced": "qwen-plus",
            "high": "qwen-max-latest"
        },
        "creation": {
            "fast": "gpt-4o-mini",
            "balanced": "claude-opus-4-1-20250805",
            "high": "claude-opus-4-1-20250805"
        },
        "review": {
            "fast": "gpt-4o-mini",
            "balanced": "gpt-4o-mini",
            "high": "gpt-4o"
        }
    }
    
    # LangChain Agent配置
    AGENT_CONFIGS = {
        "coordinator": {
            "name": "social_media_coordinator",
            "model": "claude-sonnet-4-20250514",  # LangChain 1.0 推荐模型
            "max_iterations": 30,
            "temperature": 0.7,
            "streaming": True  # LangChain 1.0 支持流式输出
        },
        "content_analyst": {
            "temperature": 0.5,
            "max_tokens": 4000
        },
        "content_creator": {
            "temperature": 0.9,
            "max_tokens": 5000
        },
        "reviewer_quality": {
            "temperature": 0.3,
            "max_tokens": 1000
        },
        "reviewer_engagement": {
            "temperature": 0.3,
            "max_tokens": 1000
        }
    }
    
    # 业务配置
    IMAGE_GENERATION = {
        "count": 7,
        "default_method": "dalle"
    }
    
    # 日志配置
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    LOG_FILE_ENABLED = True
    LOG_FILE_MAX_BYTES = 10 * 1024 * 1024  # 10MB
    LOG_FILE_BACKUP_COUNT = 5
    LOG_CONSOLE_ENABLED = True
    LOG_CONSOLE_COLORIZE = True
    
    # 开发配置
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    MOCK_MODE = os.getenv("MOCK_MODE", "false").lower() == "true"
    
    @classmethod
    def ensure_dirs(cls):
        """确保输出目录存在"""
        for dir_path in [cls.IMAGES_DIR, cls.DRAFTS_DIR, cls.LOGS_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)


# 初始化目录
Config.ensure_dirs()

# 向后兼容（保留主要别名）
ModelConfig = Config
PathConfig = Config
MCPConfig = Config
LogConfig = Config
DevConfig = Config
BusinessConfig = Config

__all__ = ['Config', 'ModelConfig', 'PathConfig', 'MCPConfig', 'LogConfig', 'DevConfig', 'BusinessConfig']

