# Social Media Agent

基于 AI Agent 的智能社交媒体内容创作系统，支持**自动分析、创作、评审和发布**小红书内容。

**版本**: v0.7 | **状态**: ✅ 生产就绪

---

## 🎯 这是什么

一个智能的小红书内容创作助手，通过 AI Agent 自动完成：

1. **分析**热门内容，提取爆款特征
2. **创作**高质量帖子（标题、正文、标签）
3. **生成** AI 原创配图
4. **评审**内容质量（5维度评估）
5. **发布**到小红书平台

**一句话使用**：
```python
agent.input("发表一篇关于悉尼旅游的帖子")
# 自动完成全流程：分析 → 创作 → 评审 → 发布
```

---

## ✨ 核心功能

- 🤖 **智能协调**：Coordinator Agent 理解需求、自动规划执行流程
- 📊 **内容分析**：搜索小红书热门内容，分析爆款特征
- ✍️ **智能创作**：基于分析结果生成优质内容
- 🎨 **AI 配图**：DALL-E 3 / Stable Diffusion 生成原创图片
- 🔍 **智能评审**：双 Agent 评审系统（质量 + 互动）+ 合规检查
- ⚡ **性能优化**：并行执行 + 智能缓存，提升 99%
- 📤 **一键发布**：自动发布到小红书

---

## 🚀 快速开始

### 1. 安装

```bash
pip install -r requirements.txt
```

### 2. 配置

```bash
# 复制配置文件
cp env.example .env

# 编辑 .env，添加以下配置：
OPENAI_API_KEY=你的第三方平台API_KEY
OPENAI_BASE_URL=你的第三方平台URL
```

**注意**：项目已配置顶级模型（Claude Opus 4.1, Claude 3.7, GPT-5 Mini 等），需要使用支持这些模型的第三方平台。

### 3. 使用

#### 方式 1：交互式模式（推荐）

```bash
# 启动交互式对话
python main.py

# 或跳过 MCP 检查（仅测试分析和创作）
python main.py --skip-mcp-check
```

交互式模式功能：
- 💬 自然语言对话，一句话完成任务
- 📋 内置命令：`help`（帮助）、`drafts`（查看草稿）、`clear`（清屏）
- 📁 自动保存草稿，支持历史查看
- ⚡ 智能错误处理，不会因错误退出

**使用示例**：
```
👤 你: 发表一篇关于悉尼旅游的帖子
🤖 Coordinator: 正在处理...
[自动完成：分析 → 创作 → 生成图片 → 评审 → 发布]

👤 你: drafts
📝 最近的草稿...

👤 你: exit
👋 再见！
```

详细说明请参考：[交互式模式使用指南](./docs/INTERACTIVE_MODE.md)

#### 方式 2：单任务模式

```bash
# 执行单个任务
python main.py --mode single --task "发表一篇关于澳洲旅游的帖子"

# 不自动保存草稿
python main.py --mode single --task "分析健身话题" --no-save-draft
```

#### 方式 3：Python API

```python
from agent import create_coordinator_agent

# 创建 Agent
coordinator = create_coordinator_agent()

# 一句话完成全流程
result = coordinator.input("发表一篇关于悉尼旅游的帖子")
```

**就这么简单！** Agent 会自动完成：分析 → 创作 → 生成图片 → 评审 → 发布

---

## 📊 性能表现

### 响应时间

| 场景 | 耗时 | 说明 |
|------|------|------|
| **首次评审** | ~47秒 | 完整流程（不含图片） |
| **缓存命中** | ~12秒 | 70%场景，节省75% ⚡ |
| **评审环节** | 15秒 → 0.001秒 | 并行+缓存，提升99.99% ✨ |

### 成本估算

- **单次**：~$0.02（不含图片）/ ~$0.18（含 DALL-E 图片）
- **月度**（每天10篇，70%缓存）：~$1.84/月
- **节省**：相比无缓存，节省 **70%** 💰

### 质量保证

- ✅ **5维质量评估**：语法、结构、可读性、深度、准确性
- ✅ **智能决策**：评分≥8直接发布，<6建议优化
- ✅ **测试覆盖**：18/18 通过（100%）

---

## 🏗️ 架构设计

```
Coordinator Agent (主协调)
  ↓
内容分析 → 内容创作 → AI 图片生成
  ↓
智能评审（并行执行）
  ├─ Quality Reviewer (5维质量)
  └─ Compliance Checker (合规检查)
  ↓
智能决策 → 发布
```

**核心优势**：
- **混合架构**：Agent（智能）+ 函数（高效）
- **并行执行**：质量+合规同时评审，节省时间
- **智能缓存**：相同内容秒级响应，节省成本

---

## 📂 项目结构

```
Social-media-agent/
├── agent.py              # 主协调 Agent
├── config.py             # 配置管理
├── agents/reviewers/     # 评审 Agents（质量、互动）
├── tools/                # 工具函数（分析、创作、评审等）
├── utils/                # 工具类（缓存、并行执行等）
├── prompts/              # System Prompts
└── tests/                # 测试套件（18个测试）
```

---

## 🛠️ 技术栈

- **Agent 框架**: [ConnectOnion](https://github.com/connectonion/connectonion)
- **LLM**: 顶级模型组合
  - Coordinator: GPT-5 Mini（快速协调）
  - Creator: Claude Opus 4.1（顶级创作）
  - Analyst: Claude 3.7 Sonnet（深度分析）
  - Reviewers: Claude Sonnet 4（准确评审）
- **图片生成**: DALL-E 3 / Stable Diffusion
- **MCP 服务**: [xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp)
- **语言**: Python 3.8+

---

## 📝 许可证

MIT License

---

## 👤 开发者

**Keyvan Zhuo**

---

## 🙏 致谢

- [ConnectOnion](https://github.com/connectonion/connectonion) - Agent 框架
- [xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp) - 小红书 MCP 服务

---

**完成度: 98% | 测试通过: 100% | 生产就绪: ✅**
