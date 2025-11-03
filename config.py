"""
全局配置文件
管理模型、路径、API 等配置
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Config:
    """统一的配置类"""
    
    # ========== API 配置 ==========
    
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    
    # ========== 路径配置 ==========
    
    BASE_DIR = Path(__file__).parent.absolute()
    
    # 输出目录
    OUTPUTS_DIR = BASE_DIR / "outputs"
    IMAGES_DIR = OUTPUTS_DIR / "images"
    DRAFTS_DIR = OUTPUTS_DIR / "drafts"
    LOGS_DIR = OUTPUTS_DIR / "logs"
    
    # 提示词目录
    PROMPTS_DIR = BASE_DIR / "prompts"
    
    # ========== MCP 配置 ==========
    
    MCP_URL = os.getenv("MCP_XIAOHONGSHU_URL", "http://localhost:18060")
    MCP_TIMEOUT = 30
    
    # ========== 模型配置 ==========
    
    # 主要模型分配（直接指定，简化结构）
    MODELS = {
        "coordinator": "gpt-5-mini-2025-08-07",
        "analyst": "claude-3-7-sonnet-20250219",
        "creator": "claude-opus-4-1-20250805",
        "reviewer": "gpt-4o-mini",
    }
    
    # 任务类型到模型的映射（用于 ModelRouter）
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
        },
        "reasoning": {
            "fast": "gpt-4o-mini",
            "balanced": "gpt-4o",
            "high": "gpt-4o"
        }
    }
    
    # ========== Agent 配置 ==========
    
    AGENT_CONFIGS = {
        "coordinator": {
            "model": "gpt-5-mini-2025-08-07",
            "max_iterations": 30,
            "temperature": 0.7
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
    
    # ========== 业务配置 ==========
    
    # 内容分析配置
    DEFAULT_ANALYSIS_LIMIT = 5  # 默认分析帖子数量
    
    # 图片生成配置
    DEFAULT_IMAGE_COUNT = 7
    
    # ========== 日志配置 ==========
    
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    
    # 日志文件配置
    LOG_FILE_ENABLED = True
    LOG_FILE_MAX_BYTES = 10 * 1024 * 1024  # 10MB
    LOG_FILE_BACKUP_COUNT = 5
    
    # 控制台日志
    LOG_CONSOLE_ENABLED = True
    LOG_CONSOLE_COLORIZE = True
    
    # ========== 性能配置 ==========
    
    # 缓存配置（简化）
    CACHE_ENABLED = True
    CACHE_TTL = 1800  # 30分钟（只用于 MCP 搜索缓存）
    
    # 超时配置
    TIMEOUT_LLM = 60
    TIMEOUT_MCP = 30
    TIMEOUT_IMAGE = 120
    
    # ========== 开发配置 ==========
    
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    VERBOSE = os.getenv("VERBOSE", "false").lower() == "true"
    MOCK_MODE = os.getenv("MOCK_MODE", "false").lower() == "true"
    
    # ========== 辅助方法 ==========
    
    @classmethod
    def ensure_dirs(cls):
        """确保所有输出目录存在"""
        for dir_path in [cls.IMAGES_DIR, cls.DRAFTS_DIR, cls.LOGS_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_api_config(cls) -> dict:
        """获取 API 配置（用于初始化客户端）"""
        config = {}
        if cls.OPENAI_API_KEY:
            config['api_key'] = cls.OPENAI_API_KEY
        if cls.OPENAI_BASE_URL:
            config['base_url'] = cls.OPENAI_BASE_URL
        return config


# 初始化目录
Config.ensure_dirs()


# 向后兼容别名
ModelConfig = Config
AgentConfig = Config
PathConfig = Config
LogConfig = Config
MCPConfig = Config
DevConfig = Config
BusinessConfig = Config  # 业务配置别名


# 导出
__all__ = [
    'Config',
    'ModelConfig',
    'AgentConfig',
    'PathConfig',
    'LogConfig',
    'MCPConfig',
    'DevConfig',
    'BusinessConfig',
]

