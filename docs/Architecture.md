# 架构说明

本文档描述当前代码结构、运行路径和关键状态流。

## 1. 总体分层

```text
入口层
  - main.py / agent.py / api_server.py (兼容入口)
  - src/social_media_agent/main.py (CLI)
  - src/social_media_agent/api/server.py (HTTP)

编排层
  - orchestration/loop_controller.py
  - orchestration/langgraph_workflow.py

能力层
  - tools/*
  - agents/reviewers/*
  - memory/*
  - scheduler/*

基础设施层
  - utils/*
  - config.py
  - core/errors.py
```

## 2. 关键目录职责

- `src/social_media_agent/tools/`：可调用工具，承担分析、创作、评审、排期、发布、记忆读写。
- `src/social_media_agent/agents/reviewers/`：质量/互动/合规评审逻辑。
- `src/social_media_agent/memory/`：向量存储和检索，包含 FAISS 与降级路径。
- `src/social_media_agent/scheduler/`：基于 SQLite 的排期服务。
- `src/social_media_agent/orchestration/`：两条执行链路（循环控制器 + 状态图工作流）。

## 3. 两条执行链路

### 3.1 Loop Controller

文件：`orchestration/loop_controller.py`

- 入口：`run_task_with_loop(task, max_iterations, quality_threshold)`
- 典型流程：
  1. 判断任务类型（内容/排期）
  2. 内容任务先检索历史记忆
  3. 调分析工具、生成草稿
  4. 质量与合规评审
  5. 不达标则带反馈继续迭代
  6. 写入 trace 日志到 `outputs/logs/`

该流程适合“需要重试和逐轮优化”的任务。

### 3.2 LangGraph Workflow

文件：`orchestration/langgraph_workflow.py`

- 状态对象：`WorkflowState`
- 节点：`route -> schedule | analyze -> create -> review`
- 条件边：由 `route` 判断下一跳
- 输出：结构化结果 + graph trace

该流程适合“步骤固定、可视化明确”的任务。

## 4. 数据存储

### 4.1 记忆系统

- 记录文件：`outputs/memory/records.jsonl`
- 索引目录：`outputs/memory/faiss_index/`
- 作用：保存偏好、复盘、上下文片段并支持语义检索

### 4.2 排期系统

- 数据库：`outputs/schedule.db`
- 能力：创建计划、过滤查询、改期

### 4.3 运行产物

- 日志：`outputs/logs/`
- 草稿：`outputs/drafts/`
- 图片：`outputs/images/`

## 5. 入口与桥接层

项目采用 `src` 布局，同时保留顶层兼容入口：

- 顶层 `main.py` 转发到 `social_media_agent.main.main`
- 顶层 `api_server.py` 暴露 `app`
- 顶层 `social_media_agent/__init__.py` 把导入路径桥接到 `src/social_media_agent`

这让脚本、CLI、HTTP 服务和旧调用方式可以共存。

## 6. 错误处理与可观测性

- 统一错误码定义在 `core/errors.py`
- 关键路径输出结构化 `success/error/data/message`
- loop/graph 都会写 trace 文件，方便复盘失败节点和评分变化

## 7. 扩展建议（与现有结构兼容）

- 新增工具：在 `tools/` 增加模块，并在工具注册处暴露。
- 新增工作流节点：在 `langgraph_workflow.py` 添加 node + edge。
- 新增记忆类型：扩展 `item_type` 约定和检索权重。
- 新增平台：复用 `scheduler` + `publisher`，增加平台适配器。
