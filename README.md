# Social Media Agent

基于 AI Agent 的智能社交媒体内容创作系统，支持**自动分析、创作、评审和发布**小红书内容。

**版本**: v1.0 | **状态**: ✅ 生产就绪

---

## 📑 目录

- [这是什么](#-这是什么)
- [核心功能](#-核心功能)
- [快速开始](#-快速开始)
  - [交互式模式](#方式-1交互式模式推荐)
  - [自定义参考数量](#-自定义参考数量功能)
  - [单任务模式](#方式-2单任务模式)
  - [Python API](#方式-3python-api)
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

**注意**：项目已配置顶级模型（Claude Opus 4.1, Claude 3.7, GPT-5 Mini 等），需要使用支持这些模型的第三方平台。

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

- **Agent 框架**: [ConnectOnion](https://github.com/connectonion/connectonion)
- **LLM 模型**: GPT-5 Mini / Claude Opus 4.1 / Claude 3.7 Sonnet / Qwen 3
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

## 🆕 版本更新

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

---

**立即开始**: `python main.py`
