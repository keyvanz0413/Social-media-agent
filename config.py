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
    # 💡 提示：如果使用第三方平台（如 OpenRouter、SiliconFlow 等），
    #         可以在 .env 中配置 OPENAI_BASE_URL，然后直接使用任何模型名称
    #         系统会自动通过 OpenAI 兼容接口调用（包括 Claude、GPT、Gemini 等）
    MODELS = {
        "reasoning": {
            "name": "gpt-4o",
            "provider": "openai",  # 如果用第三方平台，会自动走 OpenAI 兼容接口
            "description": "深度推理、策略制定",
            "use_cases": ["content_analysis", "strategy", "complex_reasoning"]
        },
        "creative": {
            "name": "claude-3-5-sonnet-20241022",  # 使用第三方平台支持的最新版本
            "provider": "anthropic",  # 如果用第三方平台，会自动走 OpenAI 兼容接口
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
        "claude-3-5-sonnet-20241022": "gpt-4o",
        "claude-3.5-sonnet": "gpt-4o",  # 兼容旧配置
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
            "balanced": "claude-3-5-sonnet-20241022",  # 最新版 Claude 3.5 Sonnet
            "high": "claude-3-5-sonnet-20241022"
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
        "claude-3-5-sonnet-20241022": {
            "provider": "anthropic",
            "description": "Claude 3.5 Sonnet 最新版 (2024-10-22)",
            "strengths": ["创意写作", "长文本生成", "自然对话", "代码生成"],
            "cost_level": "high",
            "context_window": 200000
        },
        "claude-3.5-sonnet": {
            "provider": "anthropic",
            "description": "Claude 3.5 Sonnet (通用别名)",
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
    
    @classmethod
    def validate_config(cls) -> Dict[str, Any]:
        """
        验证配置完整性和正确性
        
        Returns:
            验证结果字典，包含 success, errors, warnings
        """
        result = {
            "success": True,
            "errors": [],
            "warnings": []
        }
        
        # 1. 检查至少有一个LLM API配置
        has_llm = False
        
        if cls.OPENAI_API_KEY:
            has_llm = True
            # 验证API Key格式
            if not cls.OPENAI_API_KEY.startswith(('sk-', 'sess-')):
                result["warnings"].append(
                    "OpenAI API Key 格式可能不正确（通常以 sk- 或 sess- 开头）"
                )
        
        if cls.ANTHROPIC_API_KEY:
            has_llm = True
            if not cls.ANTHROPIC_API_KEY.startswith('sk-'):
                result["warnings"].append(
                    "Anthropic API Key 格式可能不正确（通常以 sk- 开头）"
                )
        
        if cls.OLLAMA_BASE_URL:
            has_llm = True
        
        if not has_llm:
            result["errors"].append(
                "至少需要配置一个 LLM API（OpenAI、Anthropic 或 Ollama）"
            )
            result["success"] = False
        
        # 2. 检查关键模型配置
        required_models = ["reasoning", "creative", "fast"]
        for model_type in required_models:
            if model_type not in cls.MODELS:
                result["errors"].append(f"缺少关键模型配置: {model_type}")
                result["success"] = False
        
        # 3. 检查降级链完整性
        for model, fallback in cls.FALLBACK_MODELS.items():
            if fallback and fallback not in cls.MODEL_INFO:
                result["warnings"].append(
                    f"模型 {model} 的降级模型 {fallback} 未在 MODEL_INFO 中定义"
                )
        
        # 4. 检查任务模型映射
        for task_type, quality_models in cls.TASK_MODEL_MAPPING.items():
            for quality_level, model_name in quality_models.items():
                if model_name not in cls.MODEL_INFO:
                    result["warnings"].append(
                        f"任务 {task_type}/{quality_level} 配置的模型 {model_name} "
                        f"未在 MODEL_INFO 中定义"
                    )
        
        return result
    
    @classmethod
    def check_model_available(cls, model_name: str) -> bool:
        """
        检查模型是否可用
        
        Args:
            model_name: 模型名称
        
        Returns:
            是否可用
        """
        # 检查模型是否在 MODEL_INFO 中
        if model_name not in cls.MODEL_INFO:
            return False
        
        model_info = cls.MODEL_INFO[model_name]
        provider = model_info.get("provider")
        
        # 根据提供商检查API配置
        if provider == "openai":
            return cls.OPENAI_API_KEY is not None
        elif provider == "anthropic":
            return cls.ANTHROPIC_API_KEY is not None
        elif provider == "ollama":
            return cls.OLLAMA_BASE_URL is not None
        elif provider == "custom":
            # 自定义模型需要至少一个API配置
            return cls.OPENAI_API_KEY is not None or cls.ANTHROPIC_API_KEY is not None
        
        return False
    
    @classmethod
    def get_available_models(cls) -> Dict[str, bool]:
        """
        获取所有模型的可用性状态
        
        Returns:
            模型名称到可用性的映射
        """
        return {
            model_name: cls.check_model_available(model_name)
            for model_name in cls.MODEL_INFO.keys()
        }
    
    @classmethod
    def print_config_summary(cls):
        """打印配置摘要（用于调试）"""
        print("\n" + "=" * 60)
        print("📋 模型配置摘要")
        print("=" * 60)
        
        # API配置
        print("\n🔑 API配置:")
        print(f"  OpenAI API: {'✅ 已配置' if cls.OPENAI_API_KEY else '❌ 未配置'}")
        if cls.OPENAI_BASE_URL:
            print(f"  Base URL: {cls.OPENAI_BASE_URL}")
        print(f"  Anthropic API: {'✅ 已配置' if cls.ANTHROPIC_API_KEY else '❌ 未配置'}")
        print(f"  Ollama: {'✅ 已配置' if cls.OLLAMA_BASE_URL else '❌ 未配置'}")
        
        # 模型可用性
        print("\n🤖 模型可用性:")
        available_models = cls.get_available_models()
        for model_name, is_available in available_models.items():
            status = "✅" if is_available else "❌"
            print(f"  {status} {model_name}")
        
        print("\n" + "=" * 60 + "\n")


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
        "min_likes": 0,  # 最低点赞量（0=不过滤）
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
        "model": "gpt-5-mini-2025-08-07",  # 快速决策、成本低
        "temperature": 0.7
    }
    
    # 子 Agent 配置（已根据平台可用模型优化）
    SUB_AGENTS = {
        "content_analyst": {
            "model": "claude-3-7-sonnet-20250219",  # Claude 3.7：最强分析推理
            "temperature": 0.5,
            "max_tokens": 4000
        },
        "image_generator": {
            "model": "Qwen/Qwen3-VL-32B-Instruct",  # Qwen 3 VL：多模态视觉
            "temperature": 0.8,
            "max_tokens": 2000
        },
        "content_creator": {
            "model": "claude-opus-4-1-20250805",  # Claude Opus 4.1：最强创意写作
            "temperature": 0.9,
            "max_tokens": 5000  # 增加限制，确保能生成完整的内容（包括 image_suggestions）
        },
        "reviewer_engagement": {
            "model": "claude-sonnet-4-20250514",  # Claude Sonnet 4：优秀的数据分析
            "temperature": 0.3,
            "max_tokens": 1000
        },
        "reviewer_quality": {
            "model": "gpt-4o-mini",  # 改用 GPT-4o-mini：快速、稳定、成本低
            "temperature": 0.3,
            "max_tokens": 1000
        },
        "reviewer_compliance": {
            "model": "gpt-4.1-mini-2025-04-14",  # GPT-4.1 Mini：快速合规检查
            "temperature": 0.1,
            "max_tokens": 1000
        }
    }


# ========== 路径配置 ==========

class PathConfig:
    """文件路径配置"""
    
    from pathlib import Path as _Path
    
    BASE_DIR = _Path(__file__).parent.absolute()
    
    # 输出目录
    OUTPUTS_DIR = BASE_DIR / "outputs"
    IMAGES_DIR = OUTPUTS_DIR / "images"
    DRAFTS_DIR = OUTPUTS_DIR / "drafts"
    LOGS_DIR = OUTPUTS_DIR / "logs"
    
    # 提示词目录
    PROMPTS_DIR = BASE_DIR / "prompts"
    
    # 确保目录存在
    @classmethod
    def ensure_dirs(cls):
        """确保所有输出目录存在"""
        for dir_path in [cls.IMAGES_DIR, cls.DRAFTS_DIR, cls.LOGS_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)


# ========== 日志配置 ==========

class LogConfig:
    """日志系统配置"""
    
    LEVEL = os.getenv("LOG_LEVEL", "INFO")
    FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    
    # 日志文件
    FILE_ENABLED = True
    FILE_PATH = PathConfig.LOGS_DIR / "agent.log"
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
    TEST_OUTPUT_DIR = PathConfig.BASE_DIR / "test_outputs"


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

