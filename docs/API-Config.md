# API 文档 - 配置参考

本文档详细说明 Social Media Agent 系统的所有配置项。

---

## 📋 目录

1. [环境变量配置](#环境变量配置)
2. [模型配置](#模型配置)
3. [Agent 配置](#agent-配置)
4. [MCP 服务配置](#mcp-服务配置)
5. [业务配置](#业务配置)
6. [性能配置](#性能配置)
7. [开发配置](#开发配置)

---

## 环境变量配置

### `.env` 文件

复制 `env.example` 创建你的配置文件：

```bash
cp env.example .env
```

### 必需配置

```bash
# ========== API Keys ==========
# 使用第三方 OpenAI 兼容 API 平台
OPENAI_API_KEY=your-api-key-here
OPENAI_BASE_URL=https://api.example.com/v1

# ========== MCP Server ==========
MCP_XIAOHONGSHU_URL=http://localhost:18060
```

### 可选配置

```bash
# ========== 业务配置 ==========
REVIEW_THRESHOLD=8.0          # 评审通过阈值 (0-10分)
MAX_REVISIONS=3               # 最大修改次数
AUTO_PUBLISH=false            # 是否自动发布

# ========== 开发配置 ==========
DEBUG=false                   # 调试模式
VERBOSE=false                 # 详细日志
MOCK_MODE=false               # 模拟模式（不调用真实 API）
LOG_LEVEL=INFO                # 日志级别 (DEBUG, INFO, WARNING, ERROR)
```

---

## 模型配置

### `ModelConfig` 类

位置：`config.py`

### 支持的模型

```python
MODELS = {
    "reasoning": {
        "name": "gpt-4o",
        "provider": "openai",
        "description": "深度推理、策略制定"
    },
    "creative": {
        "name": "claude-3-5-sonnet-20241022",
        "provider": "anthropic",
        "description": "创意写作、标题生成"
    },
    "fast": {
        "name": "gpt-4o-mini",
        "provider": "openai",
        "description": "快速任务、评分"
    },
    "vision": {
        "name": "qwen2.5-vl",
        "provider": "custom",
        "description": "多模态理解、图像分析"
    },
    "local": {
        "name": "llama3.2",
        "provider": "ollama",
        "description": "本地隐私任务"
    }
}
```

### 任务类型到模型的映射

```python
TASK_MODEL_MAPPING = {
    "analysis": {
        "fast": "gpt-4o-mini",
        "balanced": "gpt-4o",
        "high": "gpt-4o"
    },
    "creation": {
        "fast": "gpt-4o-mini",
        "balanced": "claude-3-5-sonnet-20241022",
        "high": "claude-3-5-sonnet-20241022"
    },
    "review": {
        "fast": "gpt-4o-mini",
        "balanced": "gpt-4o-mini",
        "high": "gpt-4o"
    }
}
```

### 降级策略配置

```python
FALLBACK_MODELS = {
    "gpt-4o": "gpt-4o-mini",
    "claude-3-5-sonnet-20241022": "gpt-4o",
    "gpt-4o-mini": None  # 无备用
}
```

### 模型详细信息

```python
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
        "description": "Claude 3.5 Sonnet 最新版",
        "strengths": ["创意写作", "长文本生成", "自然对话"],
        "cost_level": "high",
        "context_window": 200000
    }
}
```

### 使用方式

```python
from config import ModelConfig

# 获取 API 配置
api_config = ModelConfig.get_api_config()
# 返回：{"api_key": "...", "base_url": "..."}

# 访问模型配置
models = ModelConfig.MODELS
task_mapping = ModelConfig.TASK_MODEL_MAPPING
fallbacks = ModelConfig.FALLBACK_MODELS
```

---

## Agent 配置

### `AgentConfig` 类

位置：`config.py`

### Coordinator Agent 配置

```python
COORDINATOR = {
    "name": "social_media_coordinator",
    "max_iterations": 30,
    "model": "gpt-5-mini-2025-08-07",  # 快速决策、成本低
    "temperature": 0.7
}
```

### 子 Agent 配置

```python
SUB_AGENTS = {
    "content_analyst": {
        "model": "claude-3-7-sonnet-20250219",  # Claude 3.7：最强分析推理
        "temperature": 0.5,
        "max_tokens": 4000
    },
    "content_creator": {
        "model": "claude-opus-4-1-20250805",  # Claude Opus 4.1：最强创意写作
        "temperature": 0.9,
        "max_tokens": 3000
    },
    "reviewer_engagement": {
        "model": "claude-sonnet-4-20250514",  # Claude Sonnet 4：优秀的数据分析
        "temperature": 0.3,
        "max_tokens": 1000
    },
    "reviewer_quality": {
        "model": "claude-sonnet-4-20250514",  # Claude Sonnet 4：准确的质量评估
        "temperature": 0.3,
        "max_tokens": 1000
    },
    "reviewer_compliance": {
        "model": "gpt-4.1-mini-2025-04-14",  # GPT-4.1 Mini：快速合规检查
        "temperature": 0.1,
        "max_tokens": 1000
    }
}
```

### 使用方式

```python
from config import AgentConfig

# 获取 Coordinator 配置
coord_config = AgentConfig.COORDINATOR
model = coord_config["model"]
max_iter = coord_config["max_iterations"]

# 获取子 Agent 配置
creator_config = AgentConfig.SUB_AGENTS["content_creator"]
model_name = creator_config["model"]
temperature = creator_config["temperature"]
```

---

## MCP 服务配置

### `MCPConfig` 类

位置：`config.py`

### 服务器配置

```python
SERVERS = {
    "xiaohongshu": {
        "url": "http://localhost:18060",
        "enabled": True,
        "timeout": 30,
        "methods": {
            "fetch_top_posts": "获取热门帖子",
            "search_posts": "搜索帖子",
            "publish_post": "发布帖子",
            "get_post_stats": "获取帖子统计"
        }
    }
}
```

### 重试配置

```python
RETRY_CONFIG = {
    "max_retries": 3,
    "retry_delay": 2,  # 秒
    "exponential_backoff": True
}
```

### 使用方式

```python
from config import MCPConfig

# 获取小红书 MCP 服务配置
xhs_config = MCPConfig.SERVERS["xiaohongshu"]
url = xhs_config["url"]
timeout = xhs_config["timeout"]

# 获取重试配置
retry_config = MCPConfig.RETRY_CONFIG
max_retries = retry_config["max_retries"]
```

---

## 业务配置

### `BusinessConfig` 类

位置：`config.py`

### 内容分析配置

```python
CONTENT_ANALYSIS = {
    "top_n_posts": 5,              # 分析前 N 篇热门帖子
    "min_likes": 0,                # 最低点赞量（0=不过滤）
    "max_posts_age_days": 30,      # 最近 N 天的帖子
    "analysis_dimensions": [
        "title_style",
        "content_structure",
        "image_style",
        "emotional_tone",
        "engagement_triggers"
    ]
}
```

### 图片生成配置

```python
IMAGE_GENERATION = {
    "count": 7,                    # 默认生成图片数量
    "min_count": 5,
    "max_count": 9,
    "aspect_ratio": "9:16",        # 小红书推荐比例
    "quality": "hd",
    "style_preferences": [
        "natural",
        "bright",
        "high_saturation"
    ]
}
```

### 内容创作配置

```python
CONTENT_CREATION = {
    "title_length": (15, 25),      # 标题字数范围
    "content_length": (800, 1200), # 正文字数范围
    "tags_count": (5, 8),          # 标签数量
    "emoji_density": 0.05,         # emoji 密度（每 100 字）
    "paragraph_count": (5, 8)      # 段落数量
}
```

### 评审配置

```python
REVIEW = {
    "threshold": 8.0,              # 通过阈值
    "max_revisions": 3,            # 最多修改次数
    "weights": {                   # 各评审维度权重
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
        ]
    }
}
```

### 发布配置

```python
PUBLISHING = {
    "auto_publish": False,         # 是否自动发布
    "require_confirmation": True,  # 是否需要人工确认
    "save_drafts": True,           # 是否保存草稿
    "draft_retention_days": 30     # 草稿保留天数
}
```

### 使用方式

```python
from config import BusinessConfig

# 获取内容分析配置
top_n = BusinessConfig.CONTENT_ANALYSIS["top_n_posts"]

# 获取评审阈值
threshold = BusinessConfig.REVIEW["threshold"]

# 获取图片生成配置
img_count = BusinessConfig.IMAGE_GENERATION["count"]
```

---

## 性能配置

### `PerformanceConfig` 类

位置：`config.py`

### 缓存配置

```python
# 缓存配置
CACHE_ENABLED = True
CACHE_TTL = 86400              # 24 小时
CACHE_MAX_SIZE = 1000
```

### 并行执行配置

```python
# 并行执行
PARALLEL_REVIEWS = True         # 评审是否并行
MAX_WORKERS = 3                 # 最大并行数
```

### 超时配置

```python
TIMEOUT = {
    "llm_call": 60,             # LLM 调用超时
    "mcp_call": 30,             # MCP 调用超时
    "image_gen": 120,           # 图片生成超时
    "total_workflow": 600       # 整体流程超时（10分钟）
}
```

### 使用方式

```python
from config import PerformanceConfig

# 检查缓存是否启用
if PerformanceConfig.CACHE_ENABLED:
    ttl = PerformanceConfig.CACHE_TTL
    
# 获取超时配置
llm_timeout = PerformanceConfig.TIMEOUT["llm_call"]
```

---

## 路径配置

### `PathConfig` 类

位置：`config.py`

### 目录配置

```python
from pathlib import Path

BASE_DIR = Path(__file__).parent.absolute()

# 输出目录
OUTPUTS_DIR = BASE_DIR / "outputs"
IMAGES_DIR = OUTPUTS_DIR / "images"
DRAFTS_DIR = OUTPUTS_DIR / "drafts"
LOGS_DIR = OUTPUTS_DIR / "logs"

# 提示词目录
PROMPTS_DIR = BASE_DIR / "prompts"
```

### 使用方式

```python
from config import PathConfig

# 确保目录存在
PathConfig.ensure_dirs()

# 获取路径
drafts_dir = PathConfig.DRAFTS_DIR
images_dir = PathConfig.IMAGES_DIR
prompts_dir = PathConfig.PROMPTS_DIR
```

---

## 日志配置

### `LogConfig` 类

位置：`config.py`

### 配置选项

```python
LEVEL = "INFO"                  # 日志级别
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
```

### 使用方式

```python
from config import LogConfig
from utils.logger_config import setup_logging

# 设置日志系统
setup_logging(
    level=LogConfig.LEVEL,
    console_enabled=LogConfig.CONSOLE_ENABLED,
    file_enabled=LogConfig.FILE_ENABLED,
    colorize=LogConfig.CONSOLE_COLORIZE
)
```

---

## 开发配置

### `DevConfig` 类

位置：`config.py`

### 配置选项

```python
DEBUG = False                   # 调试模式
VERBOSE = False                 # 详细日志

# 模拟模式（不调用真实 API）
MOCK_MODE = False

# 跳过某些步骤（测试用）
SKIP_IMAGE_GENERATION = False
SKIP_PUBLISHING = True          # 默认不自动发布

# 测试数据
TEST_KEYWORD = "澳洲旅游"
TEST_OUTPUT_DIR = PathConfig.BASE_DIR / "test_outputs"
```

### 使用方式

```python
from config import DevConfig

# 检查是否为调试模式
if DevConfig.DEBUG:
    print("调试模式已启用")
    
# 检查是否跳过发布
if DevConfig.SKIP_PUBLISHING:
    print("跳过发布步骤")
```

---

## 配置最佳实践

### 1. 环境隔离

```bash
# 开发环境
.env.development

# 生产环境
.env.production

# 测试环境
.env.test
```

### 2. 敏感信息保护

```bash
# ❌ 不要将 .env 提交到 Git
echo ".env" >> .gitignore

# ✅ 提供示例配置
cp .env .env.example
# 然后删除 .env.example 中的敏感信息
```

### 3. 配置验证

```python
from config import ModelConfig, MCPConfig

def validate_config():
    """验证配置是否完整"""
    errors = []
    
    # 检查 API Key
    if not ModelConfig.OPENAI_API_KEY:
        errors.append("缺少 OPENAI_API_KEY")
    
    # 检查 MCP URL
    if not MCPConfig.SERVERS["xiaohongshu"]["url"]:
        errors.append("缺少 MCP_XIAOHONGSHU_URL")
    
    if errors:
        raise ValueError(f"配置错误: {', '.join(errors)}")
    
    print("✅ 配置验证通过")

# 在启动时调用
validate_config()
```

### 4. 动态配置

```python
import os
from config import AgentConfig

# 运行时修改配置
if os.getenv("USE_FAST_MODEL") == "true":
    AgentConfig.COORDINATOR["model"] = "gpt-4o-mini"
```

### 5. 配置导出

```python
from config import *

def export_config():
    """导出当前配置（用于调试）"""
    config = {
        "models": ModelConfig.MODELS,
        "agents": AgentConfig.SUB_AGENTS,
        "business": {
            "review_threshold": BusinessConfig.REVIEW["threshold"],
            "auto_publish": BusinessConfig.PUBLISHING["auto_publish"]
        },
        "performance": {
            "cache_enabled": PerformanceConfig.CACHE_ENABLED,
            "parallel_reviews": PerformanceConfig.PARALLEL_REVIEWS
        }
    }
    
    import json
    print(json.dumps(config, indent=2, ensure_ascii=False))

export_config()
```

---

## 📚 相关文档

- [工具函数参考](./API-Tools.md)
- [Agent 使用指南](./API-Agents.md)
- [架构设计](./Architecture.md)

---

**更新时间**: 2025-11-03  
**版本**: v0.7

