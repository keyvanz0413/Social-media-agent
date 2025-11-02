# Social Media Agent

基于 ConnectOnion 框架的智能社交媒体内容创作系统，自动化分析、创作、评审和发布小红书内容。

## 项目简介

这是一个 Multi-Agent 系统，通过 AI Agent 协调多个工具函数，实现从内容分析到发布的全流程自动化。

### 核心功能

- **内容分析**：分析小红书热门内容，提取爆款特征和创作建议
- **智能创作**：基于分析结果自动生成高质量帖子（标题、正文、标签）
- **AI 图片生成** ⭐：使用 DALL-E 3 或 Stable Diffusion 智能生成原创配图
- **内容评审**：多维度评估内容质量（互动潜力、内容质量、合规性）
- **一键发布**：自动发布到小红书平台

### 技术特点

- **单 Agent + 多工具**：简单高效的架构设计
- **多模型协同**：智能路由不同 LLM（GPT-4o、Claude、Ollama）
- **MCP 集成**：通过 MCP 协议连接小红书 API
- **完善的容错**：降级策略、重试机制、错误处理

## 项目结构

```
Social-media-agent/
├── agent.py                    # 主协调 Agent (ConnectOnion)
├── main.py                     # CLI 入口
├── config.py                   # 全局配置
│
├── tools/                      # 工具函数
│   ├── content_analyst.py      # 内容分析工具
│   ├── content_creator.py      # 内容创作工具
│   ├── image_generator.py      # 图片生成工具 ⭐
│   ├── publisher.py            # 发布工具
│   └── review_tools_v1.py      # 评审工具
│
├── utils/                      # 工具类
│   ├── llm_client.py           # LLM 客户端
│   ├── model_router.py         # 模型路由器
│   ├── mcp_client.py           # MCP 客户端
│   ├── draft_manager.py        # 草稿管理器
│   ├── logger_config.py        # 日志配置
│   ├── response_utils.py       # 响应格式化
│   └── mock_data.py            # Mock 数据生成
│
├── prompts/                    # Prompt 模板
│   ├── coordinator.md          # 主协调 Prompt
│   ├── content_analyst.md      # 分析工具 Prompt
│   └── content_creator.md      # 创作工具 Prompt
│
├── agents/                     # Agent 定义
│   └── reviewers/              # 评审 Agents
│
├── tests/                      # 测试套件
│   ├── smoke_test.py           # 烟雾测试
│   └── test_review_tools.py   # 评审工具测试
│
├── docs/                       # 文档
│   └── AI_IMAGE_GENERATION.md  # AI 图片生成指南
│
├── outputs/                    # 输出目录（已在.gitignore中）
│   ├── drafts/                 # 草稿存储
│   ├── images/                 # 图片缓存
│   └── logs/                   # 日志文件
│
├── xiaohongshu_manager.py      # 小红书 MCP 服务管理
├── requirements.txt            # 依赖管理
└── .env.example                # 环境变量示例
```

## 快速开始

### 1. 环境配置

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 API Keys
```

### 2. 配置 API Keys

在 `.env` 文件中配置：

```bash
# OpenAI（必需）
OPENAI_API_KEY=sk-...

# 可选：Claude
ANTHROPIC_API_KEY=sk-ant-...

# 可选：Ollama（本地模型）
OLLAMA_BASE_URL=http://localhost:11434

# 小红书 MCP 服务
MCP_SERVER_URL=http://localhost:8080
```

### 3. 启动小红书 MCP 服务

```bash
# 在 xiaohongshu-mcp 目录启动服务
cd ../xiaohongshu-mcp
./xiaohongshu-mcp
```

### 4. 运行示例

```python
from agent import create_coordinator_agent

# 创建协调器
coordinator = create_coordinator_agent()

# 自动完成全流程：分析、创作、生成图片、发布
result = coordinator.input("发表一篇关于悉尼旅游的帖子")
```

## 主要工具

### 1. 内容分析 (`content_analyst.py`)

分析小红书热门内容，提取标题模式、用户需求、创作建议。

```python
from tools.content_analyst import agent_a_analyze_content

result = agent_a_analyze_content(
    topic="悉尼旅游",
    search_count=10
)
```

### 2. 内容创作 (`content_creator.py`)

基于分析结果创作内容，生成标题、正文、标签、图片建议。

```python
from tools.content_creator import agent_c_create_content

result = agent_c_create_content(
    analysis_result=analysis_json,
    topic="悉尼旅游"
)
```

### 3. AI 图片生成 (`image_generator.py`) ⭐

使用 AI 生成原创图片，支持 DALL-E 3 和 Stable Diffusion。

```python
from tools.image_generator import generate_images_from_draft

result = generate_images_from_draft(
    draft_id=draft_id,
    method="dalle",  # 或 "local" 使用 Stable Diffusion
    count=4
)
```

详细文档：[AI 图片生成指南](docs/AI_IMAGE_GENERATION.md)

### 4. 内容评审 (`review_tools_v1.py`)

多维度评估内容质量：

- **互动潜力**：标题吸引力、话题热度、情感共鸣
- **内容质量**：信息价值、结构完整性、可读性
- **合规性**：敏感词检测、广告识别、版权风险

```python
from tools.review_tools_v1 import review_content

result = review_content(
    title="标题",
    content="正文",
    tags=["标签1", "标签2"]
)
```

### 5. 发布工具 (`publisher.py`)

发布内容到小红书平台。

```python
from tools.publisher import publish_to_xiaohongshu

result = publish_to_xiaohongshu(
    draft_id=draft_id,
    image_paths=["path/to/image1.jpg", "path/to/image2.jpg"]
)
```

## 架构设计

### 工作流程

```
用户输入
    ↓
Coordinator Agent (理解意图、制定计划)
    ↓
┌────────────────────────────────────┐
│  1. 内容分析                        │
│     - 搜索小红书热门内容             │
│     - 分析爆款特征                   │
│     - 生成创作建议                   │
└────────────────────────────────────┘
    ↓
┌────────────────────────────────────┐
│  2. 内容创作                        │
│     - 基于分析结果                   │
│     - 生成标题、正文、标签           │
│     - 提供图片建议                   │
└────────────────────────────────────┘
    ↓
┌────────────────────────────────────┐
│  3. AI 图片生成 ⭐                  │
│     - 使用 DALL-E 3 或 SD 生成      │
│     - 自动下载保存                   │
│     - 支持多种来源                   │
└────────────────────────────────────┘
    ↓
┌────────────────────────────────────┐
│  4. 内容评审                        │
│     - 互动潜力评分                   │
│     - 内容质量评分                   │
│     - 合规性检查                     │
│     - 生成优化建议                   │
└────────────────────────────────────┘
    ↓
    ├─ 通过 (≥8.0分) → 发布
    └─ 不通过 → 优化或通知用户
    ↓
┌────────────────────────────────────┐
│  5. 发布到小红书                    │
│     - 检查登录状态                   │
│     - 验证内容格式                   │
│     - 调用 MCP 发布                  │
└────────────────────────────────────┘
    ↓
发布成功
```

## 技术栈

- **Agent 框架**: ConnectOnion
- **LLM**: OpenAI (GPT-4o, GPT-4o-mini), Anthropic (Claude-3.5-Sonnet), Ollama
- **图片生成**: DALL-E 3, Stable Diffusion
- **协议**: MCP (Model Context Protocol)
- **语言**: Python 3.8+

## 环境要求

- Python 3.8+
- OpenAI API Key（必需）
- 小红书 MCP 服务（发布功能需要）
- **可选**：
  - Anthropic API Key（使用 Claude）
  - Ollama（本地模型）
  - Stable Diffusion WebUI（本地图片生成）

## 开发模式

### Mock 模式

支持无需真实 API 的开发和测试：

```bash
export MOCK_MODE=true
python tests/smoke_test.py
```

### 调试模式

```bash
export DEBUG=true
python main.py --mode single --task "测试任务"
```

## 测试

```bash
# 运行烟雾测试
python tests/smoke_test.py

# 测试图片生成
python tests/test_image_generator.py

# 测试评审工具
python tests/test_review_tools.py
```

## 项目状态

**版本**: v0.3 (MVP)  
**状态**: ✅ 核心功能完成，稳定运行

### 已实现功能

- ✅ Coordinator Agent（ConnectOnion）
- ✅ 内容分析工具
- ✅ 内容创作工具
- ✅ **AI 图片生成工具**（DALL-E 3 + Stable Diffusion）
- ✅ 发布工具
- ✅ 评审工具
- ✅ 多模型路由
- ✅ MCP 客户端集成
- ✅ Mock 模式支持
- ✅ 统一日志系统
- ✅ 草稿管理器

## 许可证

MIT License

## 维护者

AI Development Team

---

**最后更新**: 2025-11-02  
**当前版本**: v0.3  
**核心功能**: AI 图片生成、内容分析、智能创作、评审发布
