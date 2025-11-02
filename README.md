# Social Media Agent

基于 ConnectOnion 框架的智能社交媒体内容创作系统，自动化分析、创作、评审和发布小红书内容。

## 项目简介

这是一个 Multi-Agent 系统，通过 AI Agent 协调多个工具函数，实现从内容分析到发布的全流程自动化。

### 核心功能

- **内容分析**：分析小红书热门内容，提取爆款特征和创作建议
- **智能创作**：基于分析结果自动生成高质量帖子（标题、正文、标签）
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
│   └── reviewers/              # 评审 Agents（规划中）
│
├── tests/                      # 测试套件
│   ├── smoke_test.py           # 烟雾测试
│   └── test_review_tools.py   # 评审工具测试
│
├── outputs/                    # 输出目录
│   ├── drafts/                 # 草稿存储
│   ├── images/                 # 图片缓存
│   └── logs/                   # 日志文件
│
├── xiaohongshu_manager.py      # 小红书 MCP 服务管理
└── requirements.txt            # 依赖管理
```

## 文件说明

### 核心文件

| 文件 | 作用 |
|------|------|
| `agent.py` | 主协调 Agent，使用 ConnectOnion 框架，负责理解意图、制定计划、调度工具 |
| `main.py` | CLI 主入口，提供命令行界面和环境初始化 |
| `config.py` | 全局配置管理，包括模型配置、MCP 配置、路径配置等 |

### 工具函数（Tools）

| 文件 | 作用 |
|------|------|
| `tools/content_analyst.py` | 分析小红书热门内容，提取标题模式、用户需求、创作建议 |
| `tools/content_creator.py` | 基于分析结果创作内容，生成标题、正文、标签、图片建议 |
| `tools/publisher.py` | 发布内容到小红书，支持图文和视频笔记 |
| `tools/review_tools_v1.py` | 评审工具，评估互动潜力、内容质量、合规性 |

### 工具类（Utils）

| 文件 | 作用 |
|------|------|
| `utils/llm_client.py` | 统一 LLM 客户端，支持 OpenAI、Anthropic、Ollama |
| `utils/model_router.py` | 智能模型路由，根据任务类型和质量级别选择最佳模型 |
| `utils/mcp_client.py` | 小红书 MCP 客户端，封装搜索、详情、发布等接口 |
| `utils/draft_manager.py` | 草稿管理器，自动保存和管理内容草稿 |
| `utils/logger_config.py` | 日志系统配置，支持彩色控制台输出和文件记录 |
| `utils/response_utils.py` | 统一响应格式，标准化工具函数返回值 |
| `utils/mock_data.py` | Mock 数据生成器，支持无 API 开发和测试 |

### Prompt 模板

| 文件 | 作用 |
|------|------|
| `prompts/coordinator.md` | 主协调 Agent 的系统提示词 |
| `prompts/content_analyst.md` | 内容分析工具的 Prompt 模板 |
| `prompts/content_creator.md` | 内容创作工具的 Prompt 模板 |

### 管理工具

| 文件 | 作用 |
|------|------|
| `xiaohongshu_manager.py` | 小红书 MCP 服务管理工具（启动、停止、登录） |
| `test_progress.py` | 测试进度管理工具 |

## 当前状态

**版本**: MVP v0.2  
**状态**: ✅ 核心功能完成，稳定运行

### 已实现功能

- ✅ Coordinator Agent（ConnectOnion）
- ✅ 内容分析工具
- ✅ 内容创作工具
- ✅ 发布工具
- ✅ 评审工具（v1.0）
- ✅ 多模型路由
- ✅ MCP 客户端集成
- ✅ Mock 模式支持
- ✅ 统一日志系统
- ✅ 草稿管理器
- ✅ 烟雾测试

### 测试覆盖

- ✅ 核心模块导入测试
- ✅ 配置系统测试
- ✅ 日志系统测试
- ✅ Mock 数据测试
- ✅ 草稿管理测试
- ✅ 工具函数测试
- ✅ 评审工具测试

## TODO

### v1.0 规划（1-2周）

**优先级 P0**:
- [ ] 集成评审工具到 Coordinator Agent
- [ ] 更新 Coordinator Prompt（添加评审步骤）
- [ ] 完整流程测试（分析 → 创作 → 评审 → 发布）
- [ ] 性能优化（评审并行化）

**优先级 P1**:
- [ ] 评审工具优化
  - [ ] 完善敏感词库
  - [ ] 优化评分权重
  - [ ] 增强降级策略
- [ ] 评审报告生成
- [ ] 批量内容评审支持

**优先级 P2**:
- [ ] 自动重试机制（评审不通过时）
- [ ] 评审历史记录
- [ ] 评审指标监控

### v1.5-2.0 规划（根据需求）

**评审升级**:
- [ ] 评估是否需要升级到 Reviewer Agents
- [ ] 实现 Engagement Reviewer Agent（如需要）
- [ ] 实现 Quality Reviewer Agent（如需要）
- [ ] 实现 Compliance Reviewer Agent（如需要）
- [ ] 实现评审工具函数（搜索、查询等）

**功能增强**:
- [ ] Creator Agent 自主迭代能力
- [ ] 图片生成集成（DALL-E 3）
- [ ] 多平台适配（抖音、知乎）
- [ ] 效果追踪系统

### v2.0+ 愿景

**高级功能**:
- [ ] 多模态分析（图片理解）
- [ ] 视觉叙事分析
- [ ] A/B 测试系统
- [ ] 智能发布时间建议
- [ ] Web UI 界面

**工程化**:
- [ ] CI/CD 配置
- [ ] Docker 部署
- [ ] 性能监控和告警
- [ ] 成本优化系统

## 技术栈

- **Agent 框架**: ConnectOnion
- **LLM**: OpenAI (GPT-4o, GPT-4o-mini), Anthropic (Claude-3.5-Sonnet), Ollama
- **协议**: MCP (Model Context Protocol)
- **语言**: Python 3.8+
- **依赖管理**: pip + requirements.txt

## 环境要求

- Python 3.8+
- OpenAI API Key (或 Anthropic API Key，或 Ollama)
- 小红书 MCP 服务（发布功能需要）

## 架构设计

### 设计理念

**"单 Agent + 多工具"** 架构：
- **Coordinator Agent**：真正的 AI Agent（ConnectOnion），负责理解意图、制定计划、协调流程
- **工具函数（Tools）**：封装好的专用函数，负责具体任务执行
- **设计优势**：简单高效、性能优异、易于维护

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
│  3. 内容评审                        │
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
│  4. 发布到小红书                    │
│     - 检查登录状态                   │
│     - 验证内容格式                   │
│     - 调用 MCP 发布                  │
└────────────────────────────────────┘
    ↓
发布成功
```

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

## 许可证

MIT License

## 维护者

AI Development Team

---

**最后更新**: 2025-11-02  
**当前版本**: MVP v0.2  
**下一版本**: v1.0（评审工具集成）
