"""
全局配置文件
管理模型、MCP 服务器、业务参数等配置
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# ========== 模型配置 ==========

class ModelConfig:
    """多模型协同配置"""
    
    # 模型角色分配
    MODELS = {
        "reasoning": {
            "name": "gpt-4o",
            "provider": "openai",
            "description": "深度推理、策略制定",
            "use_cases": ["content_analysis", "strategy", "complex_reasoning"]
        },
        "creative": {
            "name": "claude-3.5-sonnet",
            "provider": "anthropic",
            "description": "创意写作、标题生成",
            "use_cases": ["title_generation", "creative_writing", "storytelling"]
        },
        "fast": {
            "name": "gpt-4o-mini",
            "provider": "openai",
            "description": "快速任务、评分",
            "use_cases": ["review", "scoring", "simple_tasks"]
        },
        "vision": {
            "name": "qwen2.5-vl",
            "provider": "custom",
            "description": "多模态理解、图像分析",
            "use_cases": ["image_analysis", "ocr", "image_text_matching"]
        },
        "local": {
            "name": "llama3.2",
            "provider": "ollama",
            "description": "本地隐私任务",
            "use_cases": ["compliance_check", "sensitive_data"]
        }
    }
    
    # API Keys 和 Base URLs
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")  # 可选，用于第三方 API
    
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    
    # 第三方平台配置示例
    # 如果使用第三方平台（如 OpenRouter, 硅基流动等），只需配置 OPENAI_API_KEY 和 OPENAI_BASE_URL
    # 然后在下面的 MODELS 中指定可用的模型名称
    
    # 支持的第三方平台示例：
    THIRD_PARTY_PLATFORMS = {
        "openrouter": {
            "base_url": "https://openrouter.ai/api/v1",
            "models": ["gpt-4o", "claude-3.5-sonnet", "llama-3.1-70b", "deepseek-chat"],
            "description": "一个 API 访问多个模型"
        },
        "siliconflow": {
            "base_url": "https://api.siliconflow.cn/v1",
            "models": ["Qwen/Qwen2.5-7B-Instruct", "deepseek-ai/DeepSeek-V2.5", "claude-3-5-sonnet"],
            "description": "国内高性价比平台"
        },
        "groq": {
            "base_url": "https://api.groq.com/openai/v1",
            "models": ["llama-3.1-70b-versatile", "mixtral-8x7b-32768"],
            "description": "超快推理速度"
        },
        "deepseek": {
            "base_url": "https://api.deepseek.com/v1",
            "models": ["deepseek-chat", "deepseek-coder"],
            "description": "国产高性价比模型"
        },
        "moonshot": {
            "base_url": "https://api.moonshot.cn/v1",
            "models": ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"],
            "description": "Kimi 模型"
        }
    }
    
    # 备用模型（降级策略）
    FALLBACK_MODELS = {
        "gpt-4o": "gpt-4o-mini",
        "claude-3.5-sonnet": "gpt-4o",
        "qwen2.5-vl": "gpt-4o-vision",
        "gpt-4o-mini": None,  # 已经是最便宜的，无法继续降级
    }
    
    # 任务类型到模型的映射
    # 支持三种质量级别：fast（快速）、balanced（平衡）、high（高质量）
    TASK_MODEL_MAPPING = {
        "analysis": {
            "fast": "gpt-4o-mini",
            "balanced": "gpt-4o",
            "high": "gpt-4o"
        },
        "creation": {
            "fast": "gpt-4o-mini",
            "balanced": "claude-3.5-sonnet",
            "high": "claude-3.5-sonnet"
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
        },
        "vision": {
            "fast": "gpt-4o-vision",
            "balanced": "qwen2.5-vl",
            "high": "gpt-4o-vision"
        }
    }
    
    # 模型详细信息（描述、特点、最佳用途）
    MODEL_INFO = {
        "gpt-4o": {
            "provider": "openai",
            "description": "OpenAI 最新旗舰模型",
            "strengths": ["深度推理", "复杂问题求解", "策略制定"],
            "cost_level": "high",
            "context_window": 128000
        },
        "gpt-4o-mini": {
            "provider": "openai",
            "description": "GPT-4o 的轻量版本",
            "strengths": ["快速响应", "成本低", "适合简单任务"],
            "cost_level": "low",
            "context_window": 128000
        },
        "claude-3.5-sonnet": {
            "provider": "anthropic",
            "description": "Claude 最强模型",
            "strengths": ["创意写作", "长文本生成", "自然对话"],
            "cost_level": "high",
            "context_window": 200000
        },
        "qwen2.5-vl": {
            "provider": "custom",
            "description": "通义千问视觉语言模型",
            "strengths": ["图片理解", "多模态分析", "OCR"],
            "cost_level": "medium",
            "context_window": 32000
        },
        "gpt-4o-vision": {
            "provider": "openai",
            "description": "GPT-4o 视觉版本",
            "strengths": ["图片理解", "视觉分析"],
            "cost_level": "high",
            "context_window": 128000
        }
    }
    
    @classmethod
    def get_api_config(cls) -> Dict[str, Any]:
        """
        获取 API 配置，用于初始化 Agent
        
        Returns:
            包含 API Key 和 Base URL 的字典
        """
        config = {}
        
        if cls.OPENAI_API_KEY:
            config['api_key'] = cls.OPENAI_API_KEY
        
        if cls.OPENAI_BASE_URL:
            config['base_url'] = cls.OPENAI_BASE_URL
        
        return config


# ========== MCP 服务器配置 ==========

class MCPConfig:
    """MCP 服务器集成配置"""
    
    SERVERS = {
        "xiaohongshu": {
            "url": os.getenv("MCP_XIAOHONGSHU_URL", "http://localhost:18060"),
            "enabled": True,
            "timeout": 30,
            "methods": {
                "fetch_top_posts": "获取热门帖子",
                "search_posts": "搜索帖子",
                "publish_post": "发布帖子",
                "get_post_stats": "获取帖子统计"
            }
        },
        "image_gen": {
            "url": os.getenv("MCP_IMAGE_GEN_URL", "http://localhost:8002"),
            "enabled": True,
            "timeout": 120,  # 图片生成可能需要更长时间
            "methods": {
                "generate_dalle": "DALL-E 3 生成",
                "generate_midjourney": "Midjourney 生成",
                "fetch_unsplash": "Unsplash 搜索",
                "fetch_pexels": "Pexels 搜索"
            }
        },
        "multimodal": {
            "url": os.getenv("MCP_MULTIMODAL_URL", "http://localhost:8003"),
            "enabled": True,
            "timeout": 30,
            "methods": {
                "analyze_image": "图像分析",
                "extract_text": "OCR 文字提取",
                "check_image_quality": "图片质量检查",
                "match_image_text": "图文匹配度评估"
            }
        },
        "compliance": {
            "url": os.getenv("MCP_COMPLIANCE_URL", "http://localhost:8004"),
            "enabled": True,
            "timeout": 10,
            "methods": {
                "check_sensitive_words": "敏感词检测",
                "check_advertising_law": "广告法检查",
                "check_platform_rules": "平台规则检查"
            }
        }
    }
    
    # MCP 调用重试配置
    RETRY_CONFIG = {
        "max_retries": 3,
        "retry_delay": 2,  # 秒
        "exponential_backoff": True
    }


# ========== 业务配置 ==========

class BusinessConfig:
    """业务逻辑配置"""
    
    # 内容分析配置
    CONTENT_ANALYSIS = {
        "top_n_posts": 5,  # 分析前 N 篇热门帖子
        "min_likes": 5000,  # 最低点赞量
        "max_posts_age_days": 30,  # 最近 N 天的帖子
        "analysis_dimensions": [
            "title_style",
            "content_structure",
            "image_style",
            "emotional_tone",
            "engagement_triggers"
        ]
    }
    
    # 图片生成配置
    IMAGE_GENERATION = {
        "count": 7,  # 默认生成图片数量
        "min_count": 5,
        "max_count": 9,
        "aspect_ratio": "9:16",  # 小红书推荐比例
        "quality": "hd",
        "style_preferences": [
            "natural",
            "bright",
            "high_saturation"
        ]
    }
    
    # 内容创作配置
    CONTENT_CREATION = {
        "title_length": (15, 25),  # 标题字数范围
        "content_length": (800, 1200),  # 正文字数范围
        "tags_count": (5, 8),  # 标签数量
        "emoji_density": 0.05,  # emoji 密度（每 100 字）
        "paragraph_count": (5, 8)  # 段落数量
    }
    
    # 评审配置
    REVIEW = {
        "threshold": 8.0,  # 通过阈值
        "max_revisions": 3,  # 最多修改次数
        "weights": {  # 各评审维度权重
            "engagement": 0.4,
            "quality": 0.35,
            "compliance": 0.25
        },
        "dimensions": {
            "engagement": [
                "title_attractiveness",
                "content_usefulness",
                "emotional_resonance",
                "interaction_triggers"
            ],
            "quality": [
                "grammar",
                "logic",
                "originality",
                "readability"
            ],
            "compliance": [
                "sensitive_words",
                "advertising_law",
                "platform_rules"
            ]
        }
    }
    
    # 发布配置
    PUBLISHING = {
        "auto_publish": False,  # 是否自动发布
        "require_confirmation": True,  # 是否需要人工确认
        "save_drafts": True,  # 是否保存草稿
        "draft_retention_days": 30  # 草稿保留天数
    }


# ========== Agent 配置 ==========

class AgentConfig:
    """Agent 执行配置"""
    
    # 主协调 Agent
    COORDINATOR = {
        "name": "social_media_coordinator",
        "max_iterations": 30,
        "model": ModelConfig.MODELS["reasoning"]["name"],
        "temperature": 0.7
    }
    
    # 子 Agent 配置
    SUB_AGENTS = {
        "content_analyst": {
            "model": ModelConfig.MODELS["reasoning"]["name"],
            "temperature": 0.5,
            "max_tokens": 4000
        },
        "image_generator": {
            "model": ModelConfig.MODELS["vision"]["name"],
            "temperature": 0.8,
            "max_tokens": 2000
        },
        "content_creator": {
            "model": ModelConfig.MODELS["creative"]["name"],
            "temperature": 0.9,
            "max_tokens": 3000
        },
        "reviewer_engagement": {
            "model": ModelConfig.MODELS["fast"]["name"],
            "temperature": 0.3,
            "max_tokens": 1000
        },
        "reviewer_quality": {
            "model": ModelConfig.MODELS["fast"]["name"],
            "temperature": 0.3,
            "max_tokens": 1000
        },
        "reviewer_compliance": {
            "model": ModelConfig.MODELS["local"]["name"],
            "temperature": 0.1,
            "max_tokens": 1000
        }
    }


# ========== 路径配置 ==========

class PathConfig:
    """文件路径配置"""
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # 输出目录
    OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
    IMAGES_DIR = os.path.join(OUTPUTS_DIR, "images")
    DRAFTS_DIR = os.path.join(OUTPUTS_DIR, "drafts")
    LOGS_DIR = os.path.join(OUTPUTS_DIR, "logs")
    
    # 提示词目录
    PROMPTS_DIR = os.path.join(BASE_DIR, "prompts")
    
    # 确保目录存在
    @classmethod
    def ensure_dirs(cls):
        """确保所有输出目录存在"""
        for dir_path in [cls.IMAGES_DIR, cls.DRAFTS_DIR, cls.LOGS_DIR]:
            os.makedirs(dir_path, exist_ok=True)


# ========== 日志配置 ==========

class LogConfig:
    """日志系统配置"""
    
    LEVEL = os.getenv("LOG_LEVEL", "INFO")
    FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    
    # 日志文件
    FILE_ENABLED = True
    FILE_PATH = os.path.join(PathConfig.LOGS_DIR, "agent.log")
    FILE_MAX_BYTES = 10 * 1024 * 1024  # 10MB
    FILE_BACKUP_COUNT = 5
    
    # 控制台输出
    CONSOLE_ENABLED = True
    CONSOLE_COLORIZE = True


# ========== 性能配置 ==========

class PerformanceConfig:
    """性能优化配置"""
    
    # 缓存配置
    CACHE_ENABLED = True
    CACHE_TTL = 86400  # 24 小时
    CACHE_MAX_SIZE = 1000
    
    # 并行执行
    PARALLEL_REVIEWS = True  # 评审是否并行
    MAX_WORKERS = 3  # 最大并行数
    
    # 超时配置
    TIMEOUT = {
        "llm_call": 60,  # LLM 调用超时
        "mcp_call": 30,  # MCP 调用超时
        "image_gen": 120,  # 图片生成超时
        "total_workflow": 600  # 整体流程超时（10分钟）
    }


# ========== 开发配置 ==========

class DevConfig:
    """开发和调试配置"""
    
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    VERBOSE = os.getenv("VERBOSE", "false").lower() == "true"
    
    # 模拟模式（不调用真实 API）
    MOCK_MODE = os.getenv("MOCK_MODE", "false").lower() == "true"
    
    # 跳过某些步骤（测试用）
    SKIP_IMAGE_GENERATION = False
    SKIP_PUBLISHING = True  # 默认不自动发布
    
    # 测试数据
    TEST_KEYWORD = "澳洲旅游"
    TEST_OUTPUT_DIR = os.path.join(PathConfig.BASE_DIR, "test_outputs")


# ========== 导出配置 ==========

# 初始化目录
PathConfig.ensure_dirs()

# 导出所有配置
__all__ = [
    "ModelConfig",
    "MCPConfig",
    "BusinessConfig",
    "AgentConfig",
    "PathConfig",
    "LogConfig",
    "PerformanceConfig",
    "DevConfig"
]

