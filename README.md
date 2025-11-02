# 🚀 Social Media Multi-Agent System

基于 ConnectOnion 框架构建的**智能社交媒体内容创作系统**，融合多模型协同、MCP 集成和智能编排。

> 💡 **当前状态**：**MVP v0.2 (P0+P1 完成)** - 核心创作流程 + Mock模式 + 日志系统 + 自动化测试。

> 🎯 **核心理念**：通过智能 Agent 协调、多模型路由和专用工具函数，实现高质量内容的自动化创作。
> 
> 🏗️ **架构模式**：**单 Agent + 多工具**（简单高效，性能优异）

> ⚡ **最新更新** (2025-11-02)：
> - ✅ **P0**: CLI 主入口、草稿管理、统一响应格式
> - ✅ **P1**: Mock 模式、日志系统、烟雾测试
> - 🎭 无需真实 API 即可开发（Mock 模式）
> - 📋 专业的日志管理（彩色输出 + 文件记录）
> - 🧪 自动化测试（7 个核心测试，100% 通过）

## ✨ MVP 核心特性

### 🤖 智能协作架构

> **架构说明**：本系统采用 **"单 Agent + 多工具"** 架构，而非传统的 Multi-Agent 系统。  
> - **Coordinator Agent**: 真正的 AI Agent（使用 ConnectOnion 框架），负责理解意图、制定计划、协调流程
> - **工具函数（Tools）**: 封装好的专用函数，负责具体任务执行（分析、创作、发布等）
> - **设计理念**: 简单高效、易于维护、性能优异

#### ✅ 已实现的组件

**主协调器（Coordinator Agent）** - 真正的 Agent
- ✅ ConnectOnion Agent 框架集成
- ✅ 理解用户意图和需求
- ✅ 制定执行计划和工作流
- ✅ 自动调度工具函数
- ✅ 多轮对话和错误处理

**内容分析工具（Content Analyst Tool）**
- ✅ 小红书热门内容搜索与分析
- ✅ 标题模式、内容结构、用户需求提取
- ✅ 智能降级：LLM 失败时返回基础统计
- ✅ 数据验证与修复机制

**内容创作工具（Content Creator Tool）**
- ✅ 基于分析结果智能创作
- ✅ 多风格支持（casual/professional/storytelling）
- ✅ 自动生成标题、正文、话题标签
- ✅ 图片建议和元数据生成
- ✅ 自动保存草稿

**发布工具（Publisher Tool）**
- ✅ 小红书图文笔记发布
- ✅ 小红书视频笔记发布（支持）
- ✅ 登录状态检查
- ✅ 参数验证与错误处理

#### 🔜 规划中的组件

**评审 Agents（Reviewer Agents）** - v1.0 开发中 🚧
- **Engagement Reviewer Agent**: 互动潜力评审（点赞、收藏、评论预测）
- **Quality Reviewer Agent**: 内容质量评审（语法、逻辑、原创性）
- **Compliance Reviewer Agent**: 合规性评审（敏感词、广告法、平台规则）

> **设计理念**：评审需要多轮推理和工具使用，因此采用 Agent 而非简单工具函数
> - ✅ 每个评审员是独立 Agent（使用 ConnectOnion）
> - ✅ 可调用专用工具（搜索、检查、分析）
> - ✅ 多轮迭代评估，深度分析
> - ✅ 并行执行，提高效率

**智能图片生成** - v2.0+
- 支持 DALL-E 3、Midjourney、Stable Diffusion
- 图片质量预测与优化
  
**Creator Agent 升级** - v2.0+（可选）
- 具备自主迭代优化能力
- 根据评审反馈自动改进

### 🧠 智能模型路由

#### ✅ 已实现功能

**ModelRouter - 智能模型选择器**
- ✅ 任务类型自动识别（分析/创作/评审/推理/视觉）
- ✅ 三档质量级别（fast/balanced/high）
- ✅ 模型降级策略（主模型失败自动切换备用）
- ✅ 支持多提供商（OpenAI/Anthropic/Ollama）

**当前模型配置**
| 任务类型 | 主模型 | 备用模型 | 使用场景 |
|---------|-------|---------|---------|
| 内容分析 | GPT-4o | GPT-4o-mini | Agent A 分析热门内容 |
| 创意写作 | Claude-3.5-Sonnet | GPT-4o | Agent C 内容创作 |
| 快速评审 | GPT-4o-mini | - | 未来评审团队 |

**灵活配置**
- ✅ 支持通过环境变量切换模型
- ✅ 支持第三方 OpenAI 兼容平台（OpenRouter、硅基流动等）
- ✅ 支持本地 Ollama 模型（隐私保护）

#### 🔜 规划中的高级功能

- **模型投票机制**：多模型生成 + 交叉评选
- **模型串联优化**：Claude 初稿 → GPT-4o 优化 → Claude 润色
- **动态成本优化**：根据预算自动调整质量级别

### 🔜 未来规划：多模态能力

> 以下功能将在后续版本中实现

- **视觉叙事分析**：分析图片序列的视觉节奏和情绪曲线
- **图片质量预测**：生成前预测评分，优化 prompt
- **OCR 辅助创作**：提取文字布局规律
- **图文匹配验证**：确保图片与文字语义一致

### 🎭 评审 Agents 架构设计（v1.0）

> **为什么评审需要是 Agent？**  
> 评审不是简单的打分，需要多轮推理、工具使用、深度分析，因此采用 Agent 架构。

#### 设计方案：3个独立评审 Agent

**1. Engagement Reviewer Agent（互动潜力评审）**
- **职责**：评估点赞、收藏、评论潜力
- **工具**：
  - `search_similar_posts`: 搜索类似爆款帖子对比
  - `analyze_title_pattern`: 分析标题吸引力规律
  - `check_emotional_triggers`: 检测情感触发点
  - `get_engagement_stats`: 获取同类内容互动数据
- **输出**：评分 + 优势 + 不足 + 优化建议

**2. Quality Reviewer Agent（内容质量评审）**
- **职责**：评估内容质量、语法、逻辑、原创性
- **工具**：
  - `check_grammar`: 语法检查
  - `check_logic`: 逻辑连贯性分析
  - `check_readability`: 可读性评估
  - `check_originality`: 原创性检测
  - `analyze_content_depth`: 内容深度分析
- **输出**：评分 + 质量问题 + 改进建议

**3. Compliance Reviewer Agent（合规性评审）**
- **职责**：检查内容合规性、敏感词、广告法
- **工具**：
  - `check_sensitive_words`: 敏感词检测
  - `check_advertising_law`: 广告法合规检查
  - `query_platform_rules`: 平台规则查询
  - `check_banned_topics`: 禁止话题检查
  - `verify_claims`: 验证宣传声明
- **输出**：评分 + 违规项 + 风险等级 + 修改建议

#### 工作流程

```
内容创作完成
    ↓
┌──────────────────────────────────────┐
│  并行调用 3个评审 Agents              │
│  - Engagement Reviewer               │
│  - Quality Reviewer                  │
│  - Compliance Reviewer               │
└──────────────────────────────────────┘
    ↓
汇总评审结果
    ↓
计算加权平均分
    ↓
    ├─ 分数 ≥ 8.0 → 通过 → 发布
    └─ 分数 < 8.0 → 不通过 → 反馈给创作工具 → 优化 → 重新评审
```

#### 架构优势

- ✅ **多轮推理**：Agent 可以深度分析，而非简单打分
- ✅ **工具使用**：可以搜索对比、查询规则、检测违规
- ✅ **并行执行**：3个 Agent 同时评审，提高效率
- ✅ **灵活扩展**：未来可增加更多评审维度
- ✅ **可解释性**：提供详细的评分依据和改进建议

---

### 🔌 MCP 集成

#### ✅ 已集成的 MCP 服务

**XiaohongshuMCPClient - 小红书 MCP 客户端**
- ✅ 笔记搜索（支持排序、过滤）
- ✅ 笔记详情获取
- ✅ 图文笔记发布
- ✅ 视频笔记发布
- ✅ 登录状态检查
- ✅ 自动重试机制（3次，指数退避）
- ✅ 完整的错误处理

**XiaohongshuManager - MCP 服务管理工具**
- ✅ 一键启动/停止 MCP 服务
- ✅ 登录工具集成
- ✅ 服务状态监控
- ✅ 日志查看

**使用方式**
```bash
# 启动 MCP 服务
python xiaohongshu_manager.py start

# 登录小红书
python xiaohongshu_manager.py login

# 查看服务状态
python xiaohongshu_manager.py status
```

**配置**
- 默认地址：`http://localhost:18060`
- 可通过环境变量 `MCP_XIAOHONGSHU_URL` 自定义

#### 🔜 未来规划

- **MCP 编排层**：智能负载均衡、结果聚合
- **多数据源支持**：抖音、知乎、微信等
- **图片生成 MCP**：DALL-E 3、Midjourney 集成
- **多模态 MCP**：Qwen2.5-VL 图像分析

## 📊 MVP 工作流程

### 当前实现的核心流程

```
用户输入："我想发表一篇关于澳洲旅游的帖子"
         ↓
┌─────────────────────────────────────────────┐
│   主协调 Agent (ConnectOnion)                │
│   - 理解用户意图                              │
│   - 制定执行计划                              │
│   - 调度工具函数（Tools）                     │
│   - 管理整体流程                              │
└─────────────────────────────────────────────┘
         ↓
┌──────────────────────────────────────────────────────┐
│  步骤 1：内容分析 (Agent A)                           │
│  ├─ 调用小红书 MCP 搜索热门笔记                       │
│  ├─ 使用 GPT-4o 分析爆款特征                          │
│  ├─ 提取标题模式、内容结构、用户需求                   │
│  └─ 生成创作建议                                      │
│  ✅ 已实现                                            │
└──────────────────────────────────────────────────────┘
         ↓
┌──────────────────────────────────────────────────────┐
│  步骤 2：内容创作 (Agent C)                           │
│  ├─ 基于分析结果选择合适的模型                         │
│  ├─ 使用 Claude-3.5-Sonnet 创作内容                  │
│  ├─ 生成标题、正文、话题标签                           │
│  └─ 提供图片建议和元数据                              │
│  ✅ 已实现                                            │
└──────────────────────────────────────────────────────┘
         ↓
┌──────────────────────────────────────────────────────┐
│  步骤 3：内容评审 (Reviewer Agents) - v1.0 新增 🚧   │
│  ├─ 并行调用 3个评审 Agents                           │
│  │  ├─ Engagement Reviewer: 互动潜力评分              │
│  │  ├─ Quality Reviewer: 内容质量评分                 │
│  │  └─ Compliance Reviewer: 合规性评分                │
│  ├─ 汇总评审结果，计算加权平均分                       │
│  ├─ 如果分数 < 8.0 → 反馈优化建议 → 重新创作          │
│  └─ 如果分数 ≥ 8.0 → 通过评审                         │
└──────────────────────────────────────────────────────┘
         ↓
┌──────────────────────────────────────────────────────┐
│  步骤 4：发布到小红书 (Publisher)                     │
│  ├─ 检查登录状态                                      │
│  ├─ 验证内容格式（标题≤20字，正文≤1000字）           │
│  ├─ 调用小红书 MCP 发布                               │
│  └─ 返回发布结果和笔记链接                            │
│  ✅ 已实现                                            │
└──────────────────────────────────────────────────────┘
         ↓
      成功发布！

> **注意**：步骤 3 评审系统（Reviewer Agents）正在 v1.0 开发中，当前 MVP 版本暂时跳过此步骤。
```

### 🔜 未来增强

以下功能将在后续版本实现：

- **多维度评审**：互动潜力、内容质量、合规检查、用户视角
- **自适应流程**：根据关键词热度自动调整流程
- **质量迭代**：评分不达标自动修改（最多3次）
- **多平台适配**：自动生成微信公众号、抖音等版本
- **效果追踪**：24小时后获取真实数据并学习

## 🏗️ 项目结构

```
Social-media-agent/
├── README.md                        # 📖 项目说明（当前文件）
├── DEVELOPMENT.md                   # 📝 开发文档（详细设计思路）
├── config.py                        # ⚙️ 全局配置 ✅
├── requirements.txt                 # 📦 依赖管理 ✅
├── env.example                      # 🔐 环境变量模板 ✅
│
├── main.py                          # 🚀 CLI 主入口 ⚠️ (部分实现)
├── agent.py                         # 🎯 主协调 Agent ✅
├── xiaohongshu_manager.py          # 🛠️ MCP 服务管理工具 ✅
│
├── agents/                          # 🤖 AI Agents（具备自主推理能力）
│   ├── __init__.py                 # ✅
│   ├── coordinator.py              # 📝 说明文档（实际在 agent.py）
│   └── reviewers/                  # 🔜 评审 Agents (v1.0 开发中)
│       ├── __init__.py             # ✅
│       ├── engagement_reviewer.py  # 🔜 互动潜力评审 Agent
│       ├── quality_reviewer.py     # 🔜 内容质量评审 Agent
│       └── compliance_reviewer.py  # 🔜 合规性评审 Agent
│
├── tools/                           # 🛠️ 工具函数（专用任务执行）
│   ├── __init__.py                 # ✅
│   ├── content_analyst.py          # ✅ 内容分析工具
│   ├── content_creator.py          # ✅ 内容创作工具
│   ├── publisher.py                # ✅ 发布工具
│   └── review_tools.py             # ✅ 评审工具函数集（供评审Agents使用）
│
├── utils/                           # 🛠️ 工具函数
│   ├── __init__.py                 # ✅
│   ├── llm_client.py               # ✅ 统一 LLM 客户端
│   ├── mcp_client.py               # ✅ 小红书 MCP 客户端
│   ├── model_router.py             # ✅ 智能模型路由
│   ├── response_utils.py           # ✅ 统一响应格式（v0.2 P0）
│   ├── draft_manager.py            # ✅ 草稿管理器（v0.2 P0）
│   ├── mock_data.py                # ✅ Mock 数据生成（v0.2 P1）
│   ├── logger_config.py            # ✅ 日志系统配置（v0.2 P1）
│   └── (其他工具)                  # 🔜 规划中
│
├── prompts/                         # 💭 提示词工程
│   ├── coordinator.md              # ✅ 主协调提示词
│   ├── content_analyst.md          # ✅ 分析师提示词
│   ├── content_creator.md          # ✅ 创作者提示词
│   └── (其他提示词)                # 🔜 规划中
│
├── outputs/                         # 📁 输出文件（自动创建）
│   ├── images/                     # 生成的图片
│   ├── drafts/                     # 草稿版本历史
│   └── logs/                       # 运行日志
│
└── tests/                           # 🧪 测试套件
    ├── __init__.py                 # ✅
    ├── smoke_test.py               # ✅ 烟雾测试（v0.2 P1）
    └── (其他测试)                  # 🔜 规划中
```

**图例**：✅ 已实现 | ⚠️ 部分实现 | 🔜 规划中

## 🚀 快速开始

### ⚡ 零配置快速体验（Mock 模式）

**无需任何 API Key，5 分钟体验完整系统：**

```bash
# 1. 克隆项目
git clone <your-repo-url>
cd Social-media-agent

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启用 Mock 模式（无需配置 API Key）
export MOCK_MODE=true

# 4. 运行烟雾测试
python tests/smoke_test.py
# ✅ 7/7 测试通过，系统正常！

# 5. 体验创作功能
python main.py --skip-mcp-check --mode single --task "创作一篇关于咖啡的帖子"
# ✅ 草稿已保存，可在 outputs/drafts/ 查看
```

**🎉 恭喜！你已经成功运行了 Social Media Multi-Agent System！**

Mock 模式特别适合：
- 🔍 了解系统功能
- 🧪 开发和调试
- 📚 学习代码结构
- 🎭 演示展示

---

### 🔧 生产环境配置

如果要创作真实内容并发布到小红书，需要配置 API：

#### 1. 克隆项目
```bash
git clone <your-repo-url>
cd Social-media-agent
```

#### 2. 安装 Python 依赖
```bash
pip install -r requirements.txt
```

**核心依赖**：
- `connectonion>=0.0.4` - Multi-Agent 框架
- `openai>=1.0.0` - OpenAI API 客户端
- `anthropic>=0.21.0` - Claude API 客户端（可选）
- `requests>=2.31.0` - HTTP 请求
- `tenacity>=8.2.0` - 重试机制
- `python-dotenv>=1.0.0` - 环境变量管理

#### 3. 配置环境变量
```bash
cp env.example .env
nano .env  # 或使用你喜欢的编辑器
```

**必需配置（至少配置一个 LLM）：**
```bash
# OpenAI（推荐 - 功能最全）
OPENAI_API_KEY=sk-your-openai-key-here

# Claude（可选 - 创意写作强）
ANTHROPIC_API_KEY=sk-ant-your-key-here

# 本地 Ollama（可选 - 免费隐私）
OLLAMA_BASE_URL=http://localhost:11434/v1
```

**可选配置：**
```bash
# 小红书 MCP 服务地址（默认：http://localhost:18060）
MCP_XIAOHONGSHU_URL=http://localhost:18060

# 第三方 OpenAI 兼容平台（如硅基流动、OpenRouter）
OPENAI_BASE_URL=https://api.siliconflow.cn/v1
```

#### 4. 配置小红书 MCP（发布功能必需）

**安装 MCP 服务**：

参考 [xiaohongshu-mcp](../xiaohongshu-mcp/) 项目文档，或使用项目内置的管理工具：

```bash
# 启动 MCP 服务
python xiaohongshu_manager.py start

# 登录小红书账号（会打开浏览器）
python xiaohongshu_manager.py login

# 检查服务状态
python xiaohongshu_manager.py status
```

**输出示例**：
```
✅ 服务正在运行 (PID: 12345)
✅ 健康检查通过
✅ 已登录小红书
ℹ️  服务地址: http://localhost:18060
```

#### 5. 配置本地 Ollama（可选 - 用于隐私保护）
```bash
# 安装 Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 下载模型
ollama pull llama3.2

# 启动服务（通常自动启动）
ollama serve
```

### 使用方式

#### 方式 0：CLI 主入口（MVP v0.2 - 推荐 ✨）

**新增的命令行工具，提供完整的环境管理和任务执行：**

```bash
# 1. 检查环境配置（推荐首次运行）
python main.py --check

# 2. 单任务模式 - 执行一个创作任务
python main.py --mode single --task "发表一篇关于澳洲旅游的帖子"

# 3. 跳过 MCP 检查 - 仅测试分析和创作功能
python main.py --skip-mcp-check --mode single --task "创作关于咖啡的内容"

# 4. 不保存草稿
python main.py --mode single --task "测试内容" --no-save-draft

# 5. 查看帮助信息
python main.py --help
```

**输出示例：**
```
============================================================
🤖 社交媒体 Multi-Agent 系统 - MVP v0.2
============================================================

🔧 正在初始化环境...
✅ 输出目录已创建
✅ OpenAI API Key 已配置
✅ Anthropic API Key 已配置
✅ 环境初始化完成

🔌 正在检查小红书 MCP 服务...
✅ MCP 服务连接正常
✅ 已登录小红书账号: username
✅ 初始化完成

============================================================
📋 任务: 发表一篇关于澳洲旅游的帖子
============================================================

🚀 正在初始化 Coordinator Agent...
✅ Agent 已就绪

🤖 Coordinator: 正在处理任务...

[执行流程...]

✅ 草稿已保存: 20251102_143052_澳洲旅游
📁 保存路径: outputs/drafts/20251102_143052_澳洲旅游.json

✅ 任务完成！
```

#### 方式 1：直接运行 Agent（MVP v0.1 - 交互式）

```bash
# 进入 Python 环境或创建测试脚本
python agent.py
```

**当前 MVP 交互示例：**
```
🚀 正在初始化 Coordinator Agent...
✅ Coordinator Agent 已就绪！

============================================================
💡 提示：输入你的需求，例如 '发表一篇关于澳洲旅游的帖子'
💡 输入 'exit' 或 'quit' 退出

============================================================

👤 你: 发表一篇关于澳洲旅游的帖子

🤖 Coordinator: 正在处理...

┌─ 步骤 1：分析小红书热门内容 ────────────┐
│ 🔍 搜索关键词: 澳洲旅游                   │
│ ✅ 找到 5 篇热门笔记                      │
│ 🧠 使用 GPT-4o 分析爆款特征...           │
│ ✅ 分析完成                               │
│   - 标题模式: 数字型、疑问式             │
│   - 用户需求: 实用攻略、省钱技巧         │
│   - 热门话题: 大洋路、悉尼、墨尔本       │
└──────────────────────────────────────────┘

┌─ 步骤 2：创作小红书内容 ─────────────────┐
│ ✍️  使用 Claude-3.5-Sonnet 创作...       │
│ ✅ 内容创作完成                           │
│   - 标题: 🦘澳洲大洋路3天2夜攻略！       │
│   - 字数: 856 字                         │
│   - 标签: #澳洲旅游 #大洋路 #自驾游      │
└──────────────────────────────────────────┘

🤖 Coordinator: 内容创作完成！以下是草稿预览：

【标题】🦘澳洲大洋路3天2夜攻略！人均不到3k
【正文】（前200字）
澳洲大洋路真的太美了！这次3天2夜的自驾之旅...
（完整内容已保存到 outputs/drafts/）

💡 提示：如需发布，请确保：
   1. 小红书 MCP 服务已启动（python xiaohongshu_manager.py start）
   2. 已登录小红书账号（python xiaohongshu_manager.py login）
   3. 准备好至少 1 张图片

👤 你: exit
👋 再见！
```

#### 方式 2：Python API 调用（MVP 已实现）

```python
from agent import create_coordinator_agent

# 创建主协调 Agent
coordinator = create_coordinator_agent()

# 调用 Agent（自动执行完整流程）
result = coordinator.input("发表一篇关于澳洲旅游的帖子")
print(result)
```

#### 方式 3：直接调用工具函数（适合集成）

```python
from tools.content_analyst import agent_a_analyze_xiaohongshu
from tools.content_creator import agent_c_create_content
from tools.publisher import publish_to_xiaohongshu
import json

# 步骤 1：分析热门内容
analysis_result = agent_a_analyze_xiaohongshu(
    keyword="澳洲旅游",
    limit=5,
    quality_level="balanced"
)
print("分析结果：", json.loads(analysis_result)["title_patterns"])

# 步骤 2：创作内容
content_result = agent_c_create_content(
    analysis_result=analysis_result,
    topic="澳洲旅游",
    style="casual",  # casual / professional / storytelling
    quality_level="balanced"
)
content_data = json.loads(content_result)
print("标题：", content_data["title"])
print("字数：", content_data["metadata"]["word_count"])

# 步骤 3：发布到小红书（需要配置 MCP 和图片）
# publish_result = publish_to_xiaohongshu(
#     title=content_data["title"],
#     content=content_data["content"],
#     images=["path/to/image1.jpg"],  # 需要准备图片
#     tags=content_data["hashtags"]
# )
```

#### 方式 4：Mock 模式开发（MVP v0.2 P1 - 新增 🎭）

**无需配置真实 API，立即开始开发：**

```bash
# 1. 在 .env 文件中启用 Mock 模式
echo "MOCK_MODE=true" >> .env

# 或通过环境变量
export MOCK_MODE=true

# 2. 运行系统（所有 API 调用都会被模拟）
python main.py --skip-mcp-check --mode single --task "创作一篇关于咖啡的帖子"

# 3. 运行烟雾测试（自动启用 Mock 模式）
python tests/smoke_test.py
```

**Mock 模式特性：**
- 🚀 **零配置** - 无需 API Key，立即开始
- 💰 **零成本** - 不消耗真实 API 额度
- 🔒 **隐私保护** - 所有数据都是模拟的
- ⚡ **快速响应** - < 1ms，无网络延迟
- 🎯 **可预测** - 固定的模拟数据，便于测试

**Mock 模式输出示例：**
```
ℹ️  INFO LoggerManager - 🎭 Mock 模式已启用
🎭 Mock 模式：模拟 LLM 调用 (gpt-4o-mini)
🎭 Mock 模式：模拟搜索笔记 (咖啡)
✅ 草稿已保存: 20251102_143052_咖啡
```

**何时使用 Mock 模式：**
- ✅ 开发新功能时
- ✅ 调试代码逻辑时
- ✅ 运行测试时
- ✅ 演示系统时
- ❌ 创作真实内容时（需要关闭）

#### 方式 5：日志系统（MVP v0.2 P1 - 新增 📋）

**专业的日志管理系统，带彩色输出：**

```python
from utils.logger_config import get_logger, log_execution

# 获取 Logger
logger = get_logger(__name__)

# 不同级别的日志
logger.debug("调试信息")    # 🔍 DEBUG
logger.info("普通信息")     # ℹ️  INFO  
logger.warning("警告信息")  # ⚠️  WARNING
logger.error("错误信息")    # ❌ ERROR
logger.critical("严重错误") # 🔥 CRITICAL

# 使用装饰器自动记录函数执行
@log_execution()
def my_function():
    # 函数执行时间会被自动记录
    pass
```

**日志输出示例：**
```
ℹ️  INFO LoggerManager - 日志系统已初始化
ℹ️  INFO LoggerManager - 日志级别: INFO
ℹ️  INFO LoggerManager - 控制台输出: 启用
ℹ️  INFO LoggerManager - 文件输出: 启用
ℹ️  INFO LoggerManager - 日志文件: outputs/logs/agent.log
```

**日志配置：**
```python
from utils.logger_config import setup_logging

setup_logging(
    level='DEBUG',        # 日志级别
    console_enabled=True, # 控制台输出
    file_enabled=True,    # 文件输出
    colorize=True         # 彩色输出
)
```

**日志文件管理：**
- 自动轮转（10MB per file）
- 保留 5 个历史文件
- UTF-8 编码支持
- 详细的时间戳和模块信息

#### 方式 6：MCP 服务管理

```bash
# 启动 MCP 服务
python xiaohongshu_manager.py start

# 登录小红书
python xiaohongshu_manager.py login

# 查看服务状态
python xiaohongshu_manager.py status

# 查看日志
python xiaohongshu_manager.py logs 50

# 重启服务
python xiaohongshu_manager.py restart

# 停止服务
python xiaohongshu_manager.py stop
```

#### 方式 7：运行测试（MVP v0.2 P1 - 新增 🧪）

**烟雾测试 - 快速验证核心功能：**

```bash
# 运行烟雾测试（自动启用 Mock 模式）
python tests/smoke_test.py

# 输出示例：
# 🧪 开始烟雾测试（Smoke Test）
# ✅ 通过: 核心模块导入
# ✅ 通过: 配置系统
# ✅ 通过: 日志系统
# ✅ 通过: Mock 数据生成
# ✅ 通过: 草稿管理器
# ✅ 通过: 子 Agent 功能
# ✅ 通过: 统一响应格式
# 
# 总计: 7 个测试
# 通过: 7 个 ✅
# 失败: 0 个 ❌
# 成功率: 100.0%
# 
# 🎉 所有烟雾测试通过！系统核心功能正常。
```

**功能测试 - 测试 MVP v0.2 新功能：**

```bash
# 运行 MVP v0.2 功能测试
python test_mvp02.py

# 测试内容：
# - 统一响应格式工具
# - 草稿管理器
# - 环境初始化
# - MCP 连接验证
```

**测试特性：**
- ✅ 自动启用 Mock 模式
- ✅ 不依赖外部 API
- ✅ 快速执行（< 5 秒）
- ✅ 详细的测试报告
- ✅ 自动清理测试数据

## 📈 MVP 性能指标

| 指标 | MVP 实际值 | 说明 |
|------|-----------|------|
| 端到端耗时 | 30-60秒 | 分析(10s) + 创作(20-40s) |
| 平均成本 | $0.03-0.08 | GPT-4o-mini 或 Claude 模式 |
| 内容质量 | 可用 | 基于真实热门内容分析 |
| 系统稳定性 | 良好 | 带降级策略和错误处理 |
| MCP 连接 | 稳定 | 3次重试 + 指数退避 |

**性能优化方向**（未来版本）：
- ⏱️ 并行评审可节省 30-50% 时间
- 💰 渐进式质量控制可节省 40% 成本
- 🔄 智能缓存可减少重复调用

## 📚 详细文档

- **[开发文档](DEVELOPMENT.md)** - 完整的设计思路、技术选型和实现方案
- **[配置文档](config.py)** - 所有可配置参数的说明
- **API文档** - 待实现后补充

## 🛣️ 开发路线图

### ✅ MVP v0.1（已完成）

**核心功能**：
- [x] 项目架构设计
- [x] 配置系统（PathConfig、ModelConfig等）
- [x] 智能模型路由（ModelRouter）
- [x] LLM 客户端封装（OpenAI/Claude/Ollama）
- [x] 小红书 MCP 客户端集成
- [x] 内容分析 Agent（Agent A）
- [x] 内容创作 Agent（Agent C）
- [x] 发布工具（Publisher）
- [x] 主协调 Agent（ConnectOnion 集成）
- [x] MCP 服务管理工具
- [x] 错误处理与降级策略
- [x] 提示词工程（3个核心提示词）

**Bug 修复**：
- [x] 路径问题修复（统一使用 pathlib.Path）

### ✅ MVP v0.2（P0 + P1 已完成）

**优先级 P0（✅ 已完成）**：
- [x] CLI 主入口完善（main.py）
  - [x] 环境初始化（setup_environment）
  - [x] MCP 连接验证（validate_mcp_connection）
  - [x] 单任务模式（run_single_task）
- [x] 草稿持久化（自动保存到 outputs/drafts）
- [x] 统一工具返回格式（success/data/message）

**P0 新增功能：**
- ✅ 完整的环境检查系统（LLM API、MCP 服务、目录结构）
- ✅ 智能草稿管理器（自动保存、历史查看、草稿清理）
- ✅ 标准化响应格式（success/data/message/error/metadata）
- ✅ 增强的 CLI 命令行参数（--check、--skip-mcp-check、--no-save-draft）
- ✅ 详细的错误提示和故障排除建议

**优先级 P1（✅ 已完成）**：
- [x] Mock 模式（DevConfig.MOCK_MODE）
- [x] 基础日志系统配置
- [x] 简单的烟雾测试

**P1 新增功能：**
- ✅ 🎭 **Mock 模式** - 完整的模拟数据系统（无需真实 API 即可开发）
  - Mock 数据生成器（小红书搜索、内容分析、内容创作等）
  - 集成到 LLM 客户端和 MCP 客户端
  - 支持环境变量控制
- ✅ 📋 **统一日志系统** - 专业的日志管理
  - 带颜色和图标的控制台输出
  - 自动轮转的文件日志
  - Logger 管理器和便捷函数
  - 日志级别动态调整
- ✅ 🧪 **烟雾测试** - 快速验证核心功能
  - 7 个核心测试（100% 通过率）
  - 自动化测试执行
  - 详细的测试报告

**测试覆盖：**
- ✅ 功能测试脚本（test_mvp02.py）
- ✅ 烟雾测试套件（tests/smoke_test.py）- 100% 通过
- ✅ 所有代码通过 Linter 检查

**详细日志：**
- 📄 [MVP_V02_CHANGELOG.md](MVP_V02_CHANGELOG.md) - P0 详细更新日志
- 📄 [MVP_V02_P1_CHANGELOG.md](MVP_V02_P1_CHANGELOG.md) - P1 详细更新日志

### 🔜 v1.0（规划中 - 2-4周）

**增强功能**：
- [ ] 多维度评审（Agent D/E/F/G）
- [ ] 评审投票机制
- [ ] 质量迭代（自动修改）
- [ ] 图片生成（Agent B）
- [ ] 多模态分析（视觉叙事）

**性能优化**：
- [ ] 并行评审
- [ ] 智能缓存
- [ ] 模型串联优化

**工程化**：
- [ ] 完整测试覆盖
- [ ] CI/CD 配置
- [ ] 部署文档

### 🌟 v2.0+（未来愿景）

- [ ] 多平台适配（微信、抖音等）
- [ ] 效果追踪与学习
- [ ] A/B测试系统
- [ ] Web UI
- [ ] 生产级监控和告警

## ❓ 常见问题

### Q: 必须配置所有 LLM API 吗？

A: 不需要。至少配置以下之一即可：
- **OpenAI**（推荐）：分析和创作都可用
- **Claude**：主要用于创作，分析会降级到 OpenAI 或失败
- **Ollama**：本地免费，但质量可能不如商业模型

### Q: 如何不依赖小红书 MCP 进行测试？

A: 有两种方式：
1. **只测试分析和创作**：不调用 `publish_to_xiaohongshu`
2. **Mock 模式**（✅ 已实现）：设置 `MOCK_MODE=true` 使用模拟数据

```bash
# 启用 Mock 模式
export MOCK_MODE=true
python main.py --skip-mcp-check --mode single --task "测试任务"
```

### Q: 为什么提示 "MCP 连接失败"？

A: 检查以下几点：
1. MCP 服务是否启动：`python xiaohongshu_manager.py status`
2. 端口是否正确：默认 `18060`，检查 `.env` 中的 `MCP_XIAOHONGSHU_URL`
3. 防火墙是否拦截本地连接

### Q: 路径错误 "TypeError: unsupported operand type(s)"？

A: 已在 v0.1 修复。请确保使用最新代码，所有路径已统一为 `pathlib.Path` 对象。

### Q: 成本大概多少？

A: MVP 版本（单次创作）：
- **使用 GPT-4o-mini**：约 $0.01-0.02
- **使用 Claude-3.5-Sonnet**：约 $0.03-0.05
- **混合模式**（分析用 mini，创作用 Claude）：约 $0.03-0.04

### Q: 如何切换模型或质量级别？

A: 在调用工具函数时指定：
```python
# 快速模式（使用便宜模型）
result = agent_a_analyze_xiaohongshu(keyword, quality_level="fast")

# 高质量模式（使用最强模型）
result = agent_c_create_content(analysis, topic, quality_level="high")
```

或在 `config.py` 中修改默认配置。

### Q: Mock 模式和真实模式有什么区别？

A: **Mock 模式**（开发/测试）vs **真实模式**（生产）：

| 特性 | Mock 模式 | 真实模式 |
|------|----------|----------|
| API 调用 | ❌ 模拟 | ✅ 真实 |
| 成本 | 💰 $0 | 💰 有成本 |
| 响应速度 | ⚡ < 1ms | ⏱️ 网络延迟 |
| 数据质量 | 📊 固定模拟 | 📊 真实动态 |
| 适用场景 | 🧪 开发/测试 | 🚀 生产创作 |

**何时使用 Mock 模式：**
- 开发新功能
- 调试代码
- 运行测试
- 演示系统

**何时使用真实模式：**
- 创作真实内容
- 发布到小红书
- 性能基准测试

### Q: 如何查看日志？

A: 系统提供两种日志查看方式：

**1. 控制台日志**（实时彩色输出）：
```bash
python main.py  # 日志会实时显示在控制台
```

**2. 文件日志**（详细记录）：
```bash
# 查看日志文件
cat outputs/logs/agent.log

# 实时查看日志
tail -f outputs/logs/agent.log

# 搜索特定内容
grep "ERROR" outputs/logs/agent.log
```

**日志级别：**
- `DEBUG` - 详细调试信息
- `INFO` - 一般信息（默认）
- `WARNING` - 警告信息
- `ERROR` - 错误信息
- `CRITICAL` - 严重错误

### Q: 烟雾测试失败怎么办？

A: 如果烟雾测试失败：

1. **检查依赖**：
```bash
pip install -r requirements.txt
```

2. **查看详细错误**：
```bash
python tests/smoke_test.py  # 会显示详细的错误堆栈
```

3. **常见问题**：
   - 缺少 `connectonion` 库：`pip install connectonion`
   - 路径问题：确保在项目根目录运行
   - 权限问题：检查 `outputs/` 目录的写权限

4. **获取帮助**：
   - 查看 [DEVELOPMENT.md](DEVELOPMENT.md)
   - 提交 [GitHub Issue](../../issues)

### Q: 未来会支持其他平台吗？

A: 是的！v2.0 计划支持微信公众号、抖音等。当前 MVP 专注于小红书。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

**贡献指南**：
1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

MIT License

## 📮 联系方式

- 提交 Issue：[GitHub Issues](../../issues)
- 查看文档：[DEVELOPMENT.md](DEVELOPMENT.md)

---

**⭐ 如果这个项目对你有帮助，请给个 Star！**

**最后更新**：2025-11-02 | **版本**：MVP v0.2 (P0+P1) | **详细日志**：[P0更新](MVP_V02_CHANGELOG.md) | [P1更新](MVP_V02_P1_CHANGELOG.md)

