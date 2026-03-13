# LangChain 学习指南（基于本项目）

目标：用本项目把 LangChain/LangGraph 的核心概念落地。

## 1. 你在这个项目里会学到什么

- Chat Model 如何接入与配置
- Tool 如何定义与注册
- Agent 如何在多工具间做决策
- 如何用循环控制器做“多轮自检”
- 如何用 LangGraph 实现状态机
- 如何把记忆系统接入到生成链路

## 2. LangChain 的最小心智模型

可以把一次任务看成 4 层：

1. Model：负责生成和推理
2. Prompt：约束输出和角色
3. Tools：把能力外接到模型
4. Runtime：组织调用顺序、状态和错误处理

本项目对应：

- Model：`agent.py` 里的 `_create_model`
- Prompt：`prompts/coordinator.md`
- Tools：`tools/langchain_tools.py`
- Runtime：`orchestration/loop_controller.py` + `orchestration/langgraph_workflow.py`

## 3. Agent 是怎么跑起来的

入口：`create_coordinator_agent()`

关键步骤：

1. 读取系统提示词
2. 构建聊天模型
3. 注入工具列表
4. 调用 `agent.invoke({"messages": [...]})`

你可以把它理解为：

- LLM 负责“决定下一步该用哪个工具”
- 工具函数负责“真的去执行动作”
- 返回结果再交给 LLM 汇总

## 4. Tool 设计要点（项目实践）

### 4.1 输入边界清晰

- 必填参数和默认值明确
- 参数类型固定，避免隐式猜测

### 4.2 输出结构统一

建议统一包含：

- `success`：是否成功
- `message`：可读描述
- `data`：有效载荷
- `error`：失败原因（失败时）

### 4.3 工具尽量单一职责

示例：

- 分析工具只做“抓取+总结”
- 创作工具只做“内容生成”
- 评审工具只做“评分与建议”

## 5. 状态机、节点、边（LangGraph）

本项目 `langgraph_workflow.py` 是一个标准状态机示例。

### 5.1 状态（State）

- 用 `WorkflowState` 保存任务上下文
- 任一节点都只读写状态，不直接依赖外部全局变量

### 5.2 节点（Node）

- `route`：识别任务类型
- `analyze`：执行分析
- `create`：执行创作
- `review`：执行评审
- `schedule`：执行排期

节点函数特点：

- 输入：当前状态
- 输出：状态增量（更新字段）

### 5.3 边（Edge）

- 固定边：`analyze -> create -> review`
- 条件边：`route` 根据 `mode` 跳到 `schedule` 或 `analyze`

### 5.4 结束条件

- 到达 `END` 节点时返回最终状态

## 6. Loop 与 Graph 的差异

- Loop：更灵活，适合“达标前反复优化”
- Graph：更确定，适合“步骤稳定、可视化强”

在项目中：

- `LOOP_ENGINE=loop`：走迭代闭环
- `LOOP_ENGINE=graph`：走状态图流程

## 7. 记忆系统如何接到链路里

在 `loop_controller.py` 中：

1. 开始创作前调用 `search_memory`
2. 把历史偏好和复盘结果拼成 `memory_context`
3. 注入分析/创作输入
4. 每轮评审后再 `save_memory`

这形成“检索增强 + 结果回写”的闭环。

## 8. 你可以马上练习的 5 个任务

1. 新增一个工具：`topic_cluster_tool`
2. 在 graph 中加一个 `polish` 节点
3. 给 memory 增加 `item_type=persona`
4. 增加一个 `POST /run-task-graph` API
5. 给 loop trace 增加 token/耗时统计

## 9. 开发检查清单

- 工具输入输出是否稳定且可测试
- 失败分支是否返回可诊断错误
- trace 是否可复盘
- 状态字段是否最小且自洽
- 单元测试是否覆盖关键分支

## 10. 推荐阅读顺序（对应代码）

1. `src/social_media_agent/agent.py`
2. `src/social_media_agent/tools/langchain_tools.py`
3. `src/social_media_agent/orchestration/loop_controller.py`
4. `src/social_media_agent/orchestration/langgraph_workflow.py`
5. `src/social_media_agent/memory/*`
