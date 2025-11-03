# 交互式模式使用指南

## 概述

交互式模式是 Social Media Agent 的主要使用方式，提供了友好的对话界面，让你可以轻松地与 AI Agent 协作创作小红书内容。

## 启动方式

```bash
# 方式 1：直接运行（默认交互模式）
python main.py

# 方式 2：显式指定交互模式
python main.py --mode interactive

# 方式 3：跳过 MCP 检查（仅测试分析和创作）
python main.py --skip-mcp-check
```

## 功能特性

### 1. 智能对话
- 支持自然语言对话
- Agent 会理解你的意图并自动执行相应的工作流
- 实时反馈执行进度

### 2. 内置命令

| 命令 | 别名 | 功能 |
|------|------|------|
| `help` | `帮助`, `h` | 显示帮助信息 |
| `drafts` | `草稿`, `d` | 查看最近的草稿 |
| `clear` | `清屏`, `cls` | 清空屏幕 |
| `exit` / `quit` | `退出`, `q` | 退出程序 |

### 3. 草稿管理
- 自动保存创作的内容
- 可以查看历史草稿
- 草稿文件保存在 `outputs/drafts/` 目录

### 4. 错误处理
- 遇到错误不会退出，可以继续使用
- Ctrl+C 可以中断当前任务
- 详细的错误提示和解决建议

## 使用示例

### 示例 1：创作一篇帖子

```
👤 你: 发表一篇关于澳洲旅游的帖子

🤖 Coordinator: 正在处理...
[Agent 会自动执行以下步骤]
1. 分析小红书上关于"澳洲旅游"的热门内容
2. 基于分析结果创作新的内容
3. 生成配图
4. 发布到小红书

🤖 Coordinator: [显示执行结果]
```

### 示例 2：只分析不创作

```
👤 你: 分析一下健身话题的热门内容

🤖 Coordinator: 正在处理...
[Agent 会调用分析工具，返回分析结果]
```

### 示例 3：查看草稿

```
👤 你: drafts

📝 最近的草稿（最多显示 5 个）
══════════════════════════════════════════════════════════════════════

1. [澳洲旅游] 🌟澳洲旅游攻略｜这些绝美景点一定要去！
   ID: 20251103_100335_澳洲旅游
   时间: 2025-11-03 10:03:35

2. [悉尼旅游] 悉尼三日游｜超全攻略分享
   ID: 20251103_000928_悉尼旅游
   时间: 2025-11-03 00:09:28

💾 草稿目录: /path/to/outputs/drafts
──────────────────────────────────────────────────────────────────────
```

## 工作流程

交互式模式会自动协调各个 Agent 完成以下工作：

```
用户输入 → 意图识别 → 任务分解 → 执行步骤 → 返回结果
                          ↓
                    1. 内容分析
                    2. 内容创作
                    3. 图片生成
                    4. 质量评审
                    5. 内容发布
```

## 最佳实践

### 1. 清晰的需求描述
✅ 好的示例：
- "发表一篇关于澳洲旅游的帖子"
- "创作一篇关于健身的小红书内容，风格要轻松有趣"
- "分析一下美食话题的热门内容"

❌ 不好的示例：
- "写点什么" （太模糊）
- "帮我" （没有说明具体需求）

### 2. 渐进式交互
你可以分步骤与 Agent 交互：
```
第 1 轮：分析健身话题
第 2 轮：基于分析结果创作一篇内容
第 3 轮：修改标题，让它更吸引人
```

### 3. 充分利用命令
- 使用 `help` 随时查看可用功能
- 使用 `drafts` 查看之前的创作
- 使用 Ctrl+C 中断长时间任务

## 故障排查

### 问题 1：Agent 初始化失败

**错误信息**：
```
❌ ConnectOnion 框架未安装
```

**解决方案**：
```bash
pip install connectonion
```

### 问题 2：MCP 服务连接失败

**错误信息**：
```
❌ MCP 服务无响应
```

**解决方案**：
1. 启动 MCP 服务：
   ```bash
   cd xiaohongshu-mcp
   python xiaohongshu_manager.py start
   ```
2. 或者跳过 MCP 检查（仅测试分析和创作）：
   ```bash
   python main.py --skip-mcp-check
   ```

### 问题 3：API Key 未配置

**错误信息**：
```
⚠️ OpenAI API Key 未配置
```

**解决方案**：
在 `.env` 文件中配置 API Key：
```env
OPENAI_API_KEY=your_api_key_here
# 或
ANTHROPIC_API_KEY=your_api_key_here
```

## 技术细节

### 代码结构

```python
def run_interactive_mode():
    """交互式模式主函数"""
    # 1. 创建 Coordinator Agent
    coordinator = create_coordinator_agent()
    
    # 2. 初始化草稿管理器
    draft_manager = get_draft_manager()
    
    # 3. 显示帮助信息
    print_help()
    
    # 4. 交互循环
    while True:
        user_input = input("\n👤 你: ")
        
        # 处理特殊命令
        if user_input in ['exit', 'quit']:
            break
        if user_input == 'help':
            print_help()
            continue
        if user_input == 'drafts':
            show_drafts(draft_manager)
            continue
        
        # 调用 Agent
        result = coordinator.input(user_input)
        print(result)
```

### 扩展功能

如果你想添加更多命令，可以在 `run_interactive_mode()` 中添加：

```python
# 添加历史记录命令
if user_input.lower() in ['history', '历史']:
    show_conversation_history()
    continue

# 添加配置命令
if user_input.lower() in ['config', '配置']:
    show_current_config()
    continue
```

## 参考资料

- [Coordinator Agent 文档](./API-Agents.md)
- [工具函数文档](./API-Tools.md)
- [配置说明](./API-Config.md)
- [架构设计](./Architecture.md)

## 更新日志

### v0.2 (2025-11-03)
- ✨ 完善交互式模式
- ✨ 添加内置命令（help, drafts, clear, exit）
- ✨ 集成草稿管理功能
- ✨ 改进错误处理和用户提示
- ✨ 添加使用说明和示例

### v0.1 (2025-11-02)
- 🎉 初始版本

