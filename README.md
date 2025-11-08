# Social Media Agent

基于 **LangChain 1.0** 的智能社交媒体内容创作系统，支持**自动分析、创作、评审和发布**小红书内容。

**版本**: v1.0 (LangChain 1.0) | **状态**: ✅ 生产就绪 | **框架**: LangChain + LangGraph

![Agent Tests CI](https://github.com/yourusername/Social-media-agent/actions/workflows/agent-tests.yml/badge.svg)

---

## 📑 目录

- [这是什么](#-这是什么)
- [核心功能](#-核心功能)
- [快速开始](#-快速开始)
  - [交互式模式](#方式-1交互式模式推荐)
  - [自定义参考数量](#-自定义参考数量功能)
  - [单任务模式](#方式-2单任务模式)
  - [Python API](#方式-3python-api)
- [测试和CI/CD](#-测试和cicd)
- [性能表现](#-性能表现)
- [架构设计](#️-架构设计)
- [版本更新](#-版本更新)
- [相关文档](#-相关文档)

---

## 🎯 这是什么

一个智能的小红书内容创作助手，通过 AI Agent 自动完成：

1. **分析**热门内容，提取爆款特征（可自定义参考数量）
2. **创作**高质量帖子（标题、正文、标签）
3. **生成** AI 原创配图（DALL-E 3）
4. **评审**内容质量（多维度评估）
5. **发布**到小红书平台

### 一句话使用

```python
agent.input("发表一篇关于悉尼旅游的帖子")
# 自动完成全流程：分析 → 创作 → 图片 → 评审 → 发布
```

---

## ✨ 核心功能

- **智能协调**：Coordinator Agent 理解需求、自动规划执行流程
- **灵活分析**：自定义参考帖子数量（3-10篇），快速或深度任你选择
- **内容洞察**：搜索小红书热门内容，提取爆款特征和用户需求
- **智能创作**：基于分析结果生成优质内容（标题+正文+标签）
- **AI 配图**：DALL-E 3 / Stable Diffusion 生成原创图片
- **智能评审**：多维度质量评估（语法、结构、可读性、深度、准确性）+ 合规检查
- **性能优化**：并行执行 + 智能缓存
- **一键发布**：自动发布到小红书平台

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

**注意**：项目已配置模型（Claude Opus 4.1, Claude 3.7, GPT-5 Mini 等），需要使用支持这些模型的第三方平台。

### 3. 使用

#### 方式 1：交互式模式（推荐）

```bash
# 启动交互式对话
python main.py

# 或跳过 MCP 检查（仅测试分析和创作）
python main.py --skip-mcp-check
```

**特点**：
- 自然对话：一句话完成任务
- 灵活控制：自定义参考帖子数量（3-10篇）
- 便捷命令：`help`、`drafts`、`clear`
- 自动保存：草稿自动保存，支持历史查看
- 智能容错：错误不会中断对话

---

### 💡 使用示例

#### 示例 1：标准流程（默认参考5篇）

```
👤 你: 发表一篇关于悉尼旅游的帖子

🤖 Coordinator: 正在处理...
• 分析了5篇热门帖子
• 发现标题模式：数字型、个人体验
• 创作完成：《悉尼旅游｜3天2夜深度游✨》
• 生成了4张AI图片
• 质量评分：8.5/10 ✅
• 已发布到小红书
```

#### 示例 2：深度分析（自定义参考10篇）

```
👤 你: 写一篇北海道旅游攻略，参考10篇爆款帖子

🤖 Coordinator: 正在分析10篇热门帖子...
• 发现丰富的行程规划、美食推荐模式
• 用户需求：详细行程、交通攻略、温泉体验
• 创作完成，内容更全面深入
• [继续完成图片生成、评审、发布]
```

#### 示例 3：快速创作（只参考3篇）

```
👤 你: 创作美食内容，只看3篇就好

🤖 Coordinator: 正在分析3篇帖子...
• 快速分析完成
• [快速创作和发布]
```

#### 示例 4：其他命令

```
👤 你: drafts
📝 最近的草稿（共5个）...

👤 你: help
💡 使用指南...

👤 你: exit
👋 再见！
```

---

### 🎯 自定义参考数量功能

系统支持多种自然表达方式：

| 用户表达 | 识别结果 | 适用场景 |
|---------|---------|---------|
| "发表一篇旅游帖子" | 默认5篇 | 标准创作 |
| "参考10篇爆款帖子" | 分析10篇 | 深度分析 |
| "只看3篇就好" | 分析3篇 | 快速创作 |
| "多看一些，至少8篇" | 分析8篇 | 全面了解 |

**使用建议**：
- 快速创作：3篇
- 平衡模式：5-7篇（推荐）
- 深度分析：8-10篇

#### 方式 2：单任务模式

适合命令行批量执行或脚本调用：

```bash
# 标准任务（默认参考5篇）
python main.py --mode single --task "发表一篇关于澳洲旅游的帖子"

# 自定义参考数量
python main.py --mode single --task "写一篇北海道攻略，参考10篇爆款帖子"

# 快速创作（3篇）
python main.py --mode single --task "创作美食内容，只看3篇就好"

# 不自动保存草稿
python main.py --mode single --task "分析健身话题" --no-save-draft
```

#### 方式 3：Python API

适合集成到其他应用或自定义工作流：

```python
from agent import create_coordinator_agent

# 创建 Agent
coordinator = create_coordinator_agent()

# 标准用法（默认参考5篇）
result = coordinator.input("发表一篇关于悉尼旅游的帖子")

# 自定义参考数量（深度分析）
result = coordinator.input("写一篇北海道攻略，参考10篇爆款帖子")

# 快速创作（参考3篇）
result = coordinator.input("创作美食内容，只看3篇就好")
```

#### 方式 4：直接调用工具函数

适合高级用户和自定义场景：

```python
from tools.content_analyst import agent_a_analyze_xiaohongshu

# 默认分析5篇
analysis = agent_a_analyze_xiaohongshu("北海道旅游")

# 自定义分析10篇
analysis = agent_a_analyze_xiaohongshu("北海道旅游", limit=10)

# 快速分析3篇
analysis = agent_a_analyze_xiaohongshu("北海道旅游", limit=3)
```

**就这么简单！** Agent 会自动完成：分析 → 创作 → 生成图片 → 评审 → 发布

---

## 🧪 测试和CI/CD

### 快速测试

```bash
# 快速烟雾测试（推荐，日常开发使用）
./scripts/quick_test.sh        # macOS/Linux
scripts\quick_test.bat          # Windows
```

### 完整测试

```bash
# 运行完整的CI/CD测试流程（排除MCP测试）
./scripts/run_ci_tests.sh       # macOS/Linux
scripts\run_ci_tests.bat        # Windows

# 或使用pytest
pytest -v -m "not mcp"          # 运行所有非MCP测试
pytest -v -m "not mcp and not slow"  # 排除慢速测试
```

### 测试说明

本项目配置了完整的CI/CD测试流程，**只测试Agent功能，不测试MCP功能**（MCP需要单独的服务器）。

测试覆盖：
- ✅ **烟雾测试**: 核心模块导入、配置、日志、Mock数据
- ✅ **单元测试**: 配置模块、工具函数、工具模块
- ✅ **集成测试**: 完整的Agent工作流（分析→创作→评审）
- ✅ **代码质量**: Flake8语法检查、Black格式检查

MCP测试排除原因：
- MCP功能需要单独运行 `npx @modelcontextprotocol/server-xiaohongshu`
- CI环境使用Mock模式，无需真实MCP服务
- 通过 `@pytest.mark.mcp` 标记排除

### CI/CD配置

项目使用 GitHub Actions 自动化测试：
- 推送到 `main` 或 `develop` 分支时自动运行
- Pull Request 时自动验证
- 测试失败会阻止合并

详细文档：[CI/CD 配置说明](./docs/CI-CD.md)

---

## 📊 性能表现

### 响应时间

| 场景 | 耗时 |
|------|------|
| 首次请求 | ~47秒 |
| 缓存命中 | ~12秒 |

### 成本估算

- 单次运行：~$0.02（不含图片）/ ~$0.18（含图片）
- 月度成本（每天10篇）：~$1.84/月

### 质量保证

- 5维质量评估：语法、结构、可读性、深度、准确性
- 智能决策机制：自动判断内容质量
- 完善的错误处理和自动恢复

---

## 🏗️ 架构设计

```
Coordinator Agent
  ↓
内容分析 → 内容创作 → AI 图片生成
  ↓
智能评审（并行执行）
  ├─ Quality Reviewer
  └─ Compliance Checker
  ↓
智能决策 → 发布
```

**特点**：
- 混合架构：Agent + 工具函数
- 并行执行：多维度同时评审
- 智能缓存：提升响应速度

---

## 📂 项目结构

```
Social-media-agent/
├── agent.py              # 主协调 Agent
├── config.py             # 配置管理
├── agents/reviewers/     # 评审 Agents
├── tools/                # 工具函数
├── utils/                # 工具类
├── prompts/              # 提示词
└── tests/                # 测试代码
```

---

## 🛠️ 技术栈

- **Agent 框架**: [LangChain 1.0](https://docs.langchain.com) + [LangGraph](https://langchain-ai.github.io/langgraph/)
- **LLM 模型**: Claude Sonnet 4 / GPT-4o / Claude Opus 4.1 / Qwen 3
- **图片生成**: DALL-E 3 / Stable Diffusion
- **MCP 服务**: [xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp)
- **语言**: Python 3.11+

### 🆕 LangChain 1.0 升级

本项目已从 ConnectOnion 迁移到 **LangChain 1.0**，带来以下改进：

✨ **核心优势**:
- 更简洁的 API（代码量减少 60%+）
- 基于 LangGraph 的持久化执行
- 流式输出支持（实时查看思考过程）
- Human-in-the-loop 功能
- LangSmith 深度可观测性

📖 **详细迁移文档**: [LANGCHAIN-1.0-MIGRATION.md](./docs/LANGCHAIN-1.0-MIGRATION.md)

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

## 🆕 版本更新

### v2.0 (2025-11-04) - LangChain 1.0 重构版 🎉

**重大升级**: 从 ConnectOnion 迁移到 LangChain 1.0

**核心改进**:
- ✅ 使用 LangChain 1.0 的 `create_agent()` API
- ✅ 集成 LangGraph 实现持久化执行
- ✅ 支持流式输出，实时查看处理过程
- ✅ 统一模型接口，支持 OpenAI/Anthropic/第三方平台
- ✅ 代码简化 60%+，可维护性大幅提升
- ✅ 完整的迁移文档和最佳实践指南

**技术栈**:
- LangChain: 1.0.2
- LangChain-OpenAI: 1.0.1
- LangChain-Anthropic: 1.0.1
- LangGraph: 1.0.1

**迁移指南**: 查看 [LANGCHAIN-1.0-MIGRATION.md](./docs/LANGCHAIN-1.0-MIGRATION.md)

---

### v1.0 (2025-11-03)

- 优化架构设计，提升代码可维护性
- 统一工具函数，减少代码重复
- 完善错误处理和缓存机制
- 优化模型路由和配置管理

---

### v0.9 (2025-11-03)

- 修复 JSON 解析失败问题，提升创作成功率
- 修复评审函数参数传递问题
- 优化日志输出，提升用户体验
- 完善错误处理和降级策略

---

### v0.8 (2025-11-03)

- 支持自定义参考帖子数量（3-10篇）
- 修复 MCP 搜索和内容创作相关问题
- 优化内容字段生成和错误处理

---

## 📚 文档

- [架构设计](./docs/Architecture.md)
- [API 文档](./docs/API-Agents.md)
- [CI/CD 配置说明](./docs/CI-CD.md)
- [LangChain 1.0 迁移指南](./docs/LANGCHAIN-1.0-MIGRATION.md)

---

**立即开始**: `python main.py`
