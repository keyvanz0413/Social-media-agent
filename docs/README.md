# Social Media Agent - 文档中心

欢迎来到 Social Media Agent 系统的文档中心！

---

## 📚 文档目录

### 快速开始

- [**项目 README**](../README.md) - 项目概述、快速开始、功能特性
- [**项目总结**](../PROJECT_SUMMARY.md) - 完成度、性能指标、技术亮点

### API 文档

1. [**工具函数参考**](./API-Tools.md) ⭐
   - 所有可用工具函数的详细文档
   - 参数说明、返回值、使用示例
   - 完整工作流示例

2. [**Agent 使用指南**](./API-Agents.md) 🤖
   - Coordinator Agent 使用方法
   - Quality Reviewer Agent
   - Engagement Reviewer Agent
   - 最佳实践和故障排查

3. [**配置参考**](./API-Config.md) ⚙️
   - 环境变量配置
   - 模型配置
   - Agent 配置
   - 业务配置
   - 性能配置

4. [**架构设计**](./Architecture.md) 🏗️
   - 系统架构
   - 核心模块
   - 数据流
   - 技术栈
   - 设计原则
   - 性能优化

---

## 🚀 快速导航

### 我想...

#### 开始使用系统
→ 阅读 [项目 README](../README.md) → [工具函数参考](./API-Tools.md)

#### 理解如何使用 Agent
→ 阅读 [Agent 使用指南](./API-Agents.md)

#### 配置系统
→ 阅读 [配置参考](./API-Config.md)

#### 理解系统设计
→ 阅读 [架构设计](./Architecture.md)

#### 使用工具函数
→ 阅读 [工具函数参考](./API-Tools.md)

#### 优化性能
→ 阅读 [架构设计 - 性能优化](./Architecture.md#性能优化)

#### 扩展系统
→ 阅读 [架构设计 - 扩展性设计](./Architecture.md#扩展性设计)

---

## 📖 文档概览

### 1. 工具函数参考 (API-Tools.md)

**适合人群**: 开发者、使用者

**内容**:
- ✅ 6 大类工具函数
- ✅ 详细的参数和返回值说明
- ✅ 丰富的代码示例
- ✅ 完整工作流示例
- ✅ 错误处理和最佳实践

**关键章节**:
- 内容分析工具 (`agent_a_analyze_xiaohongshu`)
- 内容创作工具 (`agent_c_create_content`)
- 图片生成工具 (`generate_images_*`)
- 评审工具 (`review_quality`, `review_engagement`)
- 发布工具 (`publish_to_xiaohongshu`)
- 模型路由工具 (`ModelRouter`)

### 2. Agent 使用指南 (API-Agents.md)

**适合人群**: Agent 开发者、高级用户

**内容**:
- ✅ Agent 系统概述
- ✅ 3 个 Agent 的详细使用方法
- ✅ 交互示例
- ✅ 自定义配置
- ✅ 最佳实践
- ✅ 故障排查

**关键章节**:
- Coordinator Agent - 主协调器
- Quality Reviewer Agent - 质量评审
- Engagement Reviewer Agent - 互动评审
- 并行评审优化

### 3. 配置参考 (API-Config.md)

**适合人群**: 运维、配置管理员

**内容**:
- ✅ 所有配置项说明
- ✅ 环境变量设置
- ✅ 模型配置和降级策略
- ✅ 业务参数调整
- ✅ 性能优化配置
- ✅ 配置最佳实践

**关键章节**:
- 环境变量配置 (`.env`)
- 模型配置 (`ModelConfig`)
- Agent 配置 (`AgentConfig`)
- 性能配置 (`PerformanceConfig`)

### 4. 架构设计 (Architecture.md)

**适合人群**: 架构师、技术负责人

**内容**:
- ✅ 系统架构设计
- ✅ 核心模块说明
- ✅ 数据流图
- ✅ 技术栈选型
- ✅ 设计原则
- ✅ 性能优化策略
- ✅ 扩展性设计

**关键章节**:
- 整体架构（分层设计）
- 混合架构原则
- 缓存策略
- 并行执行
- 多平台扩展

---

## 💡 使用建议

### 新手入门路径

```
1. 阅读 项目 README
   ↓
2. 按照快速开始配置环境
   ↓
3. 阅读 工具函数参考 中的"使用示例"
   ↓
4. 运行完整工作流示例
   ↓
5. 根据需要查阅其他文档
```

### 开发者学习路径

```
1. 阅读 架构设计 了解整体设计
   ↓
2. 阅读 Agent 使用指南 了解 Agent 机制
   ↓
3. 阅读 工具函数参考 了解 API
   ↓
4. 阅读 配置参考 了解配置选项
   ↓
5. 开始开发和扩展
```

### 运维部署路径

```
1. 阅读 配置参考 了解所有配置项
   ↓
2. 阅读 架构设计 - 安全性和隐私
   ↓
3. 配置环境变量和 API Keys
   ↓
4. 运行测试验证
   ↓
5. 部署到生产环境
```

---

## 🔧 实用工具

### 代码示例

所有文档都包含完整的代码示例，可以直接复制使用：

```python
# 示例：完整工作流
from agent import create_coordinator_agent

coordinator = create_coordinator_agent()
result = coordinator.input("发表一篇关于澳洲旅游的帖子")
print(result)
```

### 配置模板

参考 `env.example` 创建你的配置：

```bash
cp env.example .env
# 编辑 .env 添加你的 API Keys
```

### 测试命令

```bash
# 运行所有测试
pytest tests/ -v

# 测试模型路由器
python utils/model_router.py

# 测试评审系统
python tests/test_review_tools.py
```

---

## 📝 文档约定

### 代码块

- **Python 代码**: 使用 `python` 标记
- **Bash 命令**: 使用 `bash` 标记
- **配置文件**: 使用具体语言标记（如 `yaml`, `json`）

### 符号说明

- ✅ 已完成功能
- ⚠️ 需要注意的事项
- ❌ 不推荐的做法
- 💡 提示和建议
- ⭐ 重点推荐
- 🔧 配置相关
- 🚀 性能优化

### 示例类型

- **基础用法**: 最简单的使用方式
- **高级用法**: 带自定义配置的用法
- **完整示例**: 端到端的完整流程
- **最佳实践**: 推荐的使用方式

---

## 🤝 贡献文档

如果你发现文档有误或需要改进，欢迎：

1. 提交 Issue 说明问题
2. 提交 Pull Request 改进文档
3. 在社区讨论中提出建议

---

## 📮 获取帮助

- **GitHub Issues**: [提交问题](https://github.com/your-repo/issues)
- **文档问题**: 查看 [故障排查章节](./API-Agents.md#故障排查)
- **配置问题**: 查看 [配置参考](./API-Config.md)

---

## 📅 更新日志

| 日期 | 版本 | 更新内容 |
|------|------|----------|
| 2025-11-03 | v1.0 | 初始版本，包含完整的 API 文档 |

---

**文档维护**: Keyvan Zhuo  
**最后更新**: 2025-11-03  
**文档版本**: v1.0  
**系统版本**: v0.7

