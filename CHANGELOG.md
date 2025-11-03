# 更新日志 (Changelog)

本文件记录项目的主要更新和变更。

---

## [v0.7.2] - 2025-11-03

### ✨ 新增功能

#### 1. 完善交互式模式

**位置**: `main.py`

- ✅ **完整的交互式对话循环**
  - 自然语言交互，一句话完成任务
  - 支持连续对话，无需重启
  - 优雅的错误处理，不会因错误退出
  
- ✅ **内置命令系统**
  ```bash
  help / 帮助 / h      # 显示帮助信息
  drafts / 草稿 / d    # 查看最近的草稿
  clear / 清屏 / cls   # 清空屏幕
  exit / quit / 退出 / q # 退出程序
  ```

- ✅ **草稿管理集成**
  - 实时查看历史草稿
  - 显示草稿详细信息（ID、主题、标题、时间）
  - 自动格式化时间显示

- ✅ **友好的用户界面**
  ```
  👤 你: 发表一篇关于悉尼旅游的帖子
  🤖 Coordinator: 正在处理...
  [自动完成全流程]
  ```

- ✅ **智能错误提示**
  - 详细的错误信息和解决建议
  - Ctrl+C 中断支持
  - 错误后可继续使用

#### 2. 辅助函数

**新增函数**:
- `print_help()`: 显示使用指南和命令帮助
- `show_drafts()`: 显示草稿列表，支持格式化显示

### 🔧 修复和改进

#### 1. 修复 main.py 缩进问题

**问题**: 第 366-382 行存在缩进错误，导致语法错误

**修复**:
```diff
- try:
- if args.mode == "interactive":
+ try:
+     if args.mode == "interactive":
```

#### 2. 改进命令行参数

- 保持原有的 `--mode`, `--task`, `--task-file` 参数
- 优化默认模式为交互式
- 改进帮助信息和示例

### 📚 文档完善

#### 1. 交互式模式使用指南

**新增文档**: `docs/INTERACTIVE_MODE.md`

内容包括：
- 📖 启动方式和使用示例
- 🔧 命令列表和功能说明
- 💡 最佳实践和技巧
- 🔍 故障排查指南
- 📊 技术细节和扩展方法
- **页数**: ~350 行

#### 2. 更新主 README

**位置**: `README.md`

- ✅ 添加三种使用方式
  1. 交互式模式（推荐）
  2. 单任务模式
  3. Python API
- ✅ 详细的命令示例
- ✅ 功能特性说明
- ✅ 链接到详细文档

### 📊 测试验证

- ✅ 交互式循环正常工作
- ✅ 所有命令正常执行
- ✅ 草稿管理集成正常
- ✅ 错误处理正确
- ✅ 语法检查通过（无 linter 错误）

### 🎯 完成度

- **交互式模式**: ✅ 100%
- **命令系统**: ✅ 100%
- **草稿集成**: ✅ 100%
- **文档完善**: ✅ 100%
- **错误修复**: ✅ 100%

### 💡 使用示例

```bash
# 启动交互式模式
python main.py

# 交互示例
👤 你: 发表一篇关于悉尼旅游的帖子
🤖 Coordinator: 正在处理...
[自动完成：分析 → 创作 → 生成图片 → 评审 → 发布]

👤 你: drafts
📝 最近的草稿（最多显示 5 个）
1. [悉尼旅游] 悉尼三日游｜超全攻略分享
   ID: 20251103_100335_悉尼旅游
   时间: 2025-11-03 10:03:35

👤 你: help
📖 使用指南...

👤 你: exit
👋 再见！
```

---

## [v0.7.1] - 2025-11-03

### ✨ 新增功能

#### 1. 模型自动降级策略

**位置**: `utils/model_router.py`

- ✅ **自动降级链**: 当主模型失败时，自动尝试备用模型
  ```python
  # 降级链示例
  gpt-4o → gpt-4o-mini
  claude-3-5-sonnet → gpt-4o → gpt-4o-mini
  ```

- ✅ **自动降级调用**: `call_with_fallback()` 方法
  ```python
  result, used_model = router.call_with_fallback(
      "gpt-4o",
      call_function,
      max_retries=3,
      retry_delay=1.0
  )
  ```

- ✅ **装饰器模式**: `@with_fallback` 装饰器
  ```python
  @with_fallback("gpt-4o", max_retries=3)
  def analyze_content(model: str, prompt: str):
      return llm.chat(...)
  ```

- ✅ **智能模型选择**: `select_best_available_model()` 函数
  - 自动检查模型可用性
  - 选择降级链中第一个可用的模型

#### 2. 模型健康检查和可用性检测

**位置**: `utils/model_router.py`

- ✅ **配置检查**: 检查 API key 是否配置
  ```python
  is_available = router.check_model_availability("gpt-4o")
  ```

- ✅ **实际调用测试**: 可选的实际模型测试
  ```python
  def test_call(model):
      return llm.chat(model=model, messages=[...])
  
  is_available = router.check_model_availability("gpt-4o", test_call)
  ```

- ✅ **批量检查**: 检查所有模型的可用性
  ```python
  availability = router.get_available_models()
  # {'gpt-4o': True, 'claude-3.5-sonnet': False, ...}
  ```

- ✅ **降级链查询**: 获取完整的降级路径
  ```python
  chain = router.get_fallback_chain("gpt-4o")
  # ['gpt-4o', 'gpt-4o-mini']
  ```

### 🔧 修复和改进

#### 1. .gitignore 配置优化

**问题**: 之前的配置忽略了 `docs/` 和 `tests/` 目录

**修复**:
```diff
- # Documentation and tests
- docs/
- tests/

+ # Markdown files (except in specific directories)
+ # 注意：我们保留 docs/ 和部分 .md 文件，只忽略临时生成的文档
+ *.md
+ !prompts/*.md
+ !docs/**/*.md
+ !README.md
+ !PROJECT_SUMMARY.md
+ !CHANGELOG.md
```

### 📚 文档完善

#### 1. 新增完整 API 文档

**位置**: `docs/` 目录

- ✅ **工具函数参考** (`docs/API-Tools.md`)
  - 6 大类工具函数详细文档
  - 参数说明、返回值、使用示例
  - 完整工作流示例
  - 错误处理和最佳实践
  - **页数**: ~400 行

- ✅ **Agent 使用指南** (`docs/API-Agents.md`)
  - Coordinator Agent 使用方法
  - Quality Reviewer Agent
  - Engagement Reviewer Agent
  - 交互示例和最佳实践
  - 故障排查指南
  - **页数**: ~350 行

- ✅ **配置参考** (`docs/API-Config.md`)
  - 环境变量配置
  - 模型配置和降级策略
  - Agent 配置
  - 业务配置
  - 性能配置
  - 配置最佳实践
  - **页数**: ~450 行

- ✅ **架构设计** (`docs/Architecture.md`)
  - 系统架构设计
  - 核心模块详解
  - 数据流图
  - 技术栈选型
  - 设计原则
  - 性能优化策略
  - 扩展性设计
  - **页数**: ~500 行

- ✅ **文档中心** (`docs/README.md`)
  - 文档导航和索引
  - 快速导航指南
  - 学习路径推荐
  - 实用工具和约定
  - **页数**: ~200 行

**总计**: 约 1900 行完整文档

### 📊 测试验证

- ✅ 模型路由器测试通过
- ✅ 降级链正常工作
- ✅ 模型可用性检查正常
- ✅ 智能选择最佳可用模型正常

### 🎯 完成度

- **模型自动降级**: ✅ 100%
- **健康检查功能**: ✅ 100%
- **.gitignore 修复**: ✅ 100%
- **API 文档**: ✅ 100%

---

## [v0.7] - 2025-11-02

### 核心功能

- ✅ Coordinator Agent（主协调器）
- ✅ 内容分析工具
- ✅ 内容创作工具
- ✅ 图片生成工具
- ✅ 三层评审系统（质量、互动、合规）
- ✅ 发布工具
- ✅ 性能优化（缓存 + 并行）

---

## 版本对比

| 功能 | v0.7 | v0.7.1 | v0.7.2 |
|------|------|--------|--------|
| **核心功能** | ✅ | ✅ | ✅ |
| **评审系统** | ✅ | ✅ | ✅ |
| **性能优化** | ✅ | ✅ | ✅ |
| **模型自动降级** | ❌ | ✅ ⭐ | ✅ |
| **健康检查** | ❌ | ✅ ⭐ | ✅ |
| **完整 API 文档** | ❌ | ✅ ⭐ | ✅ |
| **配置优化** | ❌ | ✅ | ✅ |
| **交互式模式** | ❌ | ❌ | ✅ ⭐ |
| **命令系统** | ❌ | ❌ | ✅ ⭐ |
| **草稿集成** | ❌ | ❌ | ✅ ⭐ |

---

## 下一步计划

### 短期 (Week 1-2)

1. ✅ ~~**完善交互式模式** (main.py)~~ - **已完成 (v0.7.2)**
   - ✅ 实现 `run_interactive_mode()`
   - ✅ 添加内置命令系统
   - ✅ 集成草稿管理

2. **实现批量处理** (main.py)
   - 实现 `run_batch_mode()`
   - 支持从文件读取任务列表
   - 批量任务进度显示

3. **增强草稿管理**
   - 草稿编辑功能
   - 草稿历史版本
   - 草稿导出功能

### 中期 (Week 3-4)

4. **Web UI 开发** (可选)
   - FastAPI Backend
   - React/Vue Frontend
   - 实时进度显示

5. **多平台支持** (可选)
   - 抖音集成
   - 微博集成
   - 知乎集成

### 长期 (Month 2+)

6. **高级分析功能**
   - 竞品分析
   - 趋势预测
   - 用户画像分析

7. **自动化调度**
   - 定时任务
   - 最佳发布时间推荐
   - 内容日历管理

---

## 贡献者

- **Keyvan Zhuo** - 主要开发者

---

**最后更新**: 2025-11-03  
**当前版本**: v0.7.2

