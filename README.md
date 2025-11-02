# Social Media Agent

基于 ConnectOnion 框架的智能社交媒体内容创作系统，支持从内容分析、智能创作、AI 图片生成、多维度评审到一键发布的全流程自动化。

## 项目简介

这是一个创新的 **Multi-Agent + Multi-Tool** 混合架构系统，通过 AI Agent 的智能决策和专业工具函数的协同工作，实现小红书内容的全自动化创作流程。

### 核心特性

- **🤖 智能协调**：主 Coordinator Agent 理解需求、制定计划、协调执行
- **📊 内容分析**：分析小红书热门内容，提取爆款特征和创作建议
- **✍️ 智能创作**：基于分析结果自动生成高质量帖子（标题、正文、标签）
- **🎨 AI 图片生成**：使用 DALL-E 3 或 Stable Diffusion 智能生成原创配图
- **🔍 多维度评审**：Agent + 函数混合评审（互动潜力、内容质量、合规性）
- **📤 一键发布**：自动发布到小红书平台

### 架构亮点

- **混合架构**：Agent 负责复杂决策，函数负责确定性任务
- **多模型协同**：智能路由不同 LLM（GPT-4o、Claude、Ollama）
- **MCP 集成**：通过 MCP 协议连接小红书 API
- **完善的容错**：降级策略、重试机制、错误处理

## 项目结构

```
Social-media-agent/
├── README.md                      # 项目说明（本文件）
├── requirements.txt               # Python 依赖
├── .env.example                   # 环境变量模板
├── config.py                      # 全局配置管理
│
├── agent.py                       # 🤖 主 Coordinator Agent
├── main.py                        # CLI 入口
├── xiaohongshu_manager.py         # 小红书 MCP 服务管理
│
├── agents/                        # Agent 定义
│   └── reviewers/                 # 评审 Agents
│       ├── engagement_reviewer.py # ✅ 互动潜力评审 Agent（已实现）
│       ├── quality_reviewer.py    # 内容质量评审 Agent（规划中）
│       └── compliance_reviewer.py # 合规性评审 Agent（规划中）
│
├── tools/                         # 工具函数
│   ├── content_analyst.py         # 内容分析工具
│   ├── content_creator.py         # 内容创作工具
│   ├── image_generator.py         # 图片生成工具
│   ├── publisher.py               # 发布工具
│   ├── review_tools.py            # ✅ 评审工具函数集（NEW）
│   └── review_tools_v1.py         # 函数式评审（向后兼容）
│
├── utils/                         # 工具类
│   ├── llm_client.py              # LLM 客户端
│   ├── model_router.py            # 模型路由器
│   ├── mcp_client.py              # MCP 客户端
│   ├── draft_manager.py           # 草稿管理器
│   ├── logger_config.py           # 日志配置
│   ├── response_utils.py          # 响应格式化
│   └── mock_data.py               # Mock 数据生成
│
├── prompts/                       # Prompt 模板
│   ├── coordinator.md             # 主协调 Prompt
│   ├── content_analyst.md         # 分析工具 Prompt
│   └── content_creator.md         # 创作工具 Prompt
│
├── tests/                         # 测试套件
│   ├── smoke_test.py              # 烟雾测试
│   ├── test_review_tools.py       # 评审工具测试
│   └── test_engagement_reviewer_agent.py  # ✅ Agent 测试
│
├── docs/                          # 文档
│   ├── AI_IMAGE_GENERATION.md     # AI 图片生成指南
│   ├── MULTI_AGENT_REVIEW_DESIGN.md  # ✅ 多Agent评审设计（NEW）
│   ├── REVIEW_IMPLEMENTATION_GUIDE.md # ✅ 实施指南（NEW）
│   ├── TEST_RESULTS_ANALYSIS.md   # ✅ 测试结果分析（NEW）
│   └── ARCHITECTURE.md            # ✅ 架构文档（NEW）
│
└── outputs/                       # 输出目录（gitignore）
    ├── drafts/                    # 草稿存储
    ├── images/                    # 图片缓存
    └── logs/                      # 日志文件
```

## 架构设计

### 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                    用户输入/CLI                               │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│              Coordinator Agent (主协调器)                     │
│  - 理解意图                                                   │
│  - 制定计划                                                   │
│  - 协调工具和 Agents                                          │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
        ┌──────────────┼──────────────┐
        ↓              ↓              ↓
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ 内容分析工具  │ │ 内容创作工具  │ │ 图片生成工具  │
│  (函数)      │ │  (函数)      │ │  (函数)      │
└──────────────┘ └──────────────┘ └──────────────┘
                       ↓
        ┌──────────────┴──────────────┐
        ↓                             ↓
┌──────────────────────┐    ┌──────────────────────┐
│  Engagement Reviewer │    │  合规性检查           │
│  Agent (智能评审)    │    │  (函数式评审)         │
│  - 搜索爆款帖子      │    │  - 敏感词检测         │
│  - 分析标题规律      │    │  - 广告法检查         │
│  - 检查情感触发      │    │  - 平台规则验证       │
│  - 综合评分决策      │    │                      │
└──────────────────────┘    └──────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│                    发布工具 (MCP)                            │
│                  发布到小红书平台                             │
└─────────────────────────────────────────────────────────────┘
```

### 设计理念

**混合架构 = Agent (智能决策) + 函数 (确定性任务)**

| 任务类型 | 实现方式 | 原因 |
|---------|---------|------|
| **主协调** | Agent | 需要理解复杂意图、制定计划 |
| **内容分析** | 函数 | 逻辑明确、可优化性能 |
| **内容创作** | 函数 | 结构化输出、稳定性高 |
| **图片生成** | 函数 | API 调用、确定性流程 |
| **互动潜力评审** | **Agent** ⭐ | 需要搜索对比、推理决策 |
| **内容质量评审** | 函数 | 规则明确、快速评分 |
| **合规性检查** | 函数 | 规则固定、无需推理 |
| **发布** | 函数 | API 调用、流程确定 |

详细架构文档：[ARCHITECTURE.md](docs/ARCHITECTURE.md)

## 快速开始

### 1. 环境准备

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env，填入你的 API Keys
```

### 2. 必需配置

在 `.env` 文件中配置：

```bash
# OpenAI（必需 - 用于 Agent 和图片生成）
OPENAI_API_KEY=sk-...

# 可选：Claude（更好的创作能力）
ANTHROPIC_API_KEY=sk-ant-...

# 可选：Ollama（本地模型）
OLLAMA_BASE_URL=http://localhost:11434

# 小红书 MCP 服务（发布功能需要）
MCP_SERVER_URL=http://localhost:18060
```

### 3. 启动 MCP 服务

```bash
# 在 xiaohongshu-mcp 目录启动服务
cd ../xiaohongshu-mcp
./xiaohongshu-mcp

# 或使用管理脚本
python xiaohongshu_manager.py start
```

### 4. 运行示例

```python
from agent import create_coordinator_agent

# 创建主协调器
coordinator = create_coordinator_agent()

# 自动完成全流程：分析、创作、生成图片、评审、发布
result = coordinator.input("发表一篇关于悉尼旅游的帖子")
```

## 核心功能详解

### 1. 内容分析

```python
from tools.content_analyst import agent_a_analyze_xiaohongshu

result = agent_a_analyze_xiaohongshu(
    topic="悉尼旅游",
    search_count=10
)
```

**输出**：
- 标题模式分析
- 用户需求洞察
- 创作建议

### 2. 智能创作

```python
from tools.content_creator import agent_c_create_content

result = agent_c_create_content(
    analysis_result=analysis_json,
    topic="悉尼旅游",
    style="casual"  # casual/professional/storytelling
)
```

**输出**：
- 吸引人的标题
- 结构化正文
- SEO 优化标签
- 图片建议列表

### 3. AI 图片生成 ⭐

```python
from tools.image_generator import generate_images_from_draft

result = generate_images_from_draft(
    draft_id=draft_id,
    method="dalle",  # DALL-E 3（推荐）
    count=4
)
```

**支持的方法**：
- `dalle`: DALL-E 3 AI 生成（推荐，高质量）
- `local`: Stable Diffusion 本地生成（免费）

详细指南：[AI 图片生成指南](docs/AI_IMAGE_GENERATION.md)

### 4. 智能评审 ⭐ NEW

#### 方案 A：Agent 评审（推荐用于互动潜力）

```python
from agents.reviewers.engagement_reviewer import review_engagement

result = review_engagement({
    "title": "悉尼旅游攻略｜3天2夜深度游",
    "content": "分享我的悉尼之旅...",
    "topic": "悉尼旅游"
})
```

**Agent 会自动**：
1. 搜索同话题的爆款帖子
2. 分析标题规律和模式
3. 检查情感触发点
4. 获取互动数据统计
5. 综合评分并给出建议

**特点**：
- ✅ 数据驱动（基于真实爆款数据）
- ✅ 智能推理（能思考和决策）
- ✅ 容错能力强（工具失败不崩溃）
- ⚠️ 稍慢（~40秒）
- ⚠️ 成本略高（~$0.005/次）

#### 方案 B：函数式评审（快速筛选）

```python
from tools.review_tools_v1 import review_content

result = review_content({
    "title": "标题",
    "content": "正文",
    "hashtags": ["标签1", "标签2"]
})
```

**特点**：
- ✅ 快速（~5秒）
- ✅ 低成本（~$0.001/次）
- ✅ 稳定可靠
- ❌ 无法搜索对比
- ❌ 规则固定

详细对比：[多Agent评审设计](docs/MULTI_AGENT_REVIEW_DESIGN.md)

### 5. 发布到小红书

```python
from tools.publisher import publish_to_xiaohongshu

result = publish_to_xiaohongshu(
    draft_id=draft_id,
    image_paths=["path/to/image1.jpg", "path/to/image2.jpg"]
)
```

## 测试

### 运行测试套件

```bash
# 基础功能测试
python tests/smoke_test.py

# 评审工具测试
python tests/test_review_tools.py

# Agent 评审测试
python tests/test_engagement_reviewer_agent.py
```

### 测试结果

最新测试结果显示：
- ✅ Engagement Reviewer Agent 运行正常
- ✅ 评分准确（4.0/10，符合预期）
- ✅ 容错能力强（工具失败不影响完成）
- ✅ 耗时合理（36.8秒）
- ✅ 成本可控（~$0.005/次）

详细分析：[测试结果分析](docs/TEST_RESULTS_ANALYSIS.md)

## 开发模式

### Mock 模式

无需真实 API 进行开发和测试：

```bash
export MOCK_MODE=true
python tests/smoke_test.py
```

### 调试模式

```bash
export DEBUG=true
python main.py --mode single --task "测试任务"
```

## 项目状态

**当前版本**: v0.4  
**状态**: ✅ 核心功能完成，Agent 评审系统验证通过

### 已实现功能

#### 基础功能
- ✅ Coordinator Agent（主协调器）
- ✅ 内容分析工具
- ✅ 内容创作工具
- ✅ AI 图片生成（DALL-E 3 + Stable Diffusion）
- ✅ 发布工具
- ✅ 多模型路由
- ✅ MCP 客户端集成
- ✅ 统一日志系统
- ✅ 草稿管理器

#### 评审系统 ⭐ NEW
- ✅ **Engagement Reviewer Agent**（互动潜力智能评审）
  - 搜索爆款帖子
  - 分析标题规律
  - 检查情感触发
  - 数据驱动评分
- ✅ 评审工具函数集（8个专业工具）
- ✅ 函数式评审（向后兼容）
- ✅ 混合评审架构
- ✅ 完整测试和文档

### 测试覆盖

- ✅ 核心模块导入测试
- ✅ 配置系统测试
- ✅ 日志系统测试
- ✅ Mock 数据测试
- ✅ 草稿管理测试
- ✅ 工具函数测试
- ✅ **Agent 评审测试** ⭐ NEW
- ✅ Bug 修复验证

### 规划中功能

#### v0.5 (1-2周)
- [ ] Quality Reviewer Agent 实现
- [ ] 评审系统集成到 Coordinator
- [ ] 并行评审优化
- [ ] 完整流程测试

#### v1.0 (1个月)
- [ ] 多 Agent 协同工作
- [ ] 自动优化建议应用
- [ ] 性能和成本优化
- [ ] Web UI 界面（可选）

## 技术栈

- **Agent 框架**: ConnectOnion
- **LLM**: 
  - OpenAI (GPT-4o, GPT-4o-mini)
  - Anthropic (Claude-3.5-Sonnet)
  - Ollama (本地模型)
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

## 成本估算

### 单次完整流程
- 内容分析：~$0.01
- 内容创作：~$0.02
- 图片生成（4张）：~$0.16 (DALL-E) 或 免费 (SD)
- Agent 评审：~$0.005
- **总计**：~$0.195/篇 或 ~$0.035/篇（不含图片）

### 月度成本（假设每天 1 篇）
- 包含 DALL-E 图片：~$5.85/月
- 使用 SD 本地图片：~$1.05/月

## 文档

- [架构设计](docs/ARCHITECTURE.md) - 系统架构详解
- [AI 图片生成指南](docs/AI_IMAGE_GENERATION.md) - DALL-E 3 / SD 使用指南
- [多Agent评审设计](docs/MULTI_AGENT_REVIEW_DESIGN.md) - 评审系统设计
- [实施指南](docs/REVIEW_IMPLEMENTATION_GUIDE.md) - 开发实施步骤
- [测试结果分析](docs/TEST_RESULTS_ANALYSIS.md) - Agent 测试分析

## 常见问题

### Q: Agent 和函数有什么区别？

**函数**：执行固定逻辑，like `if-else`
```python
def review(content):
    score = 5
    if '数字' in title: score += 1
    return score
```

**Agent**：能思考、决策、使用工具
```python
agent = Agent(tools=[search_posts, analyze_patterns, ...])
# Agent 会自己决定：先搜索，再分析，然后评分
```

### Q: 什么时候用 Agent，什么时候用函数？

| 场景 | 推荐 | 原因 |
|------|------|------|
| 固定规则检查 | 函数 | 快速、稳定、低成本 |
| 需要搜索对比数据 | Agent | 需要动态决策 |
| 需要推理判断 | Agent | Agent 能思考 |
| 简单评分 | 函数 | 函数足够 |

### Q: 评审系统的成本会不会太高？

**对比**：
- 图片生成（4张）：$0.16
- Agent 评审：$0.005
- 占比：~3%

**结论**：成本很低，完全可接受

### Q: Agent 评审准确吗？

**实测数据**：
- 评分准确（4.0/10，符合预期）
- 识别优势和不足准确
- 建议具体可执行
- 基于真实爆款数据

详见：[测试结果分析](docs/TEST_RESULTS_ANALYSIS.md)

## 许可证

MIT License

## 维护者

AI Development Team

## 更新日志

### v0.4 (2025-11-03) ⭐ 当前版本
- ✅ 实现 Engagement Reviewer Agent
- ✅ 添加 8 个评审工具函数
- ✅ 完成 Agent 测试并修复 bug
- ✅ 创建完整的设计和实施文档
- ✅ 验证混合架构的可行性

### v0.3 (2025-11-02)
- ✅ AI 图片生成工具（DALL-E 3、Stable Diffusion）
- ✅ 图片生成详细文档

### v0.2 (2025-11-01)
- ✅ 基础评审工具（函数式）
- ✅ 草稿管理系统
- ✅ 统一日志系统

### v0.1 (2025-10-31)
- ✅ 核心工作流程
- ✅ MCP 集成
- ✅ 多模型路由

---

**最后更新**: 2025-11-03  
**当前版本**: v0.4  
**核心特性**: 混合架构（Agent + 函数）、智能评审、AI 图片生成、全流程自动化
