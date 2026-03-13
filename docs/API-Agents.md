# Agent API 使用说明

本文档聚焦项目内可直接调用的 Agent 与编排入口。

## 1. 协调 Agent

文件：`src/social_media_agent/agent.py`

### 1.1 创建 Agent

```python
from social_media_agent.agent import create_coordinator_agent

agent = create_coordinator_agent()
```

### 1.2 调用方式

```python
result = agent.invoke({
    "messages": [{"role": "user", "content": "写一篇悉尼旅行帖子"}]
})
```

### 1.3 说明

- `create_coordinator_agent()` 会加载系统提示词和工具列表。
- 工具在 `src/social_media_agent/tools/langchain_tools.py` 注册。
- 适合对话式、多工具调度任务。

## 2. 可控执行入口（推荐）

文件：`src/social_media_agent/orchestration/loop_controller.py`

```python
from social_media_agent.orchestration.loop_controller import run_task_with_loop

result = run_task_with_loop(
    task="写一篇北海道旅行攻略，参考5篇帖子",
    max_iterations=3,
    quality_threshold=8.0,
)
print(result["success"], result["message"], result["trace_path"])
```

返回结构示例：

```json
{
  "success": true,
  "message": "任务完成（第2轮通过）。标题：...",
  "result": {"creation": {}, "quality": {}, "compliance": {}},
  "trace_path": "outputs/logs/loop_trace_...json"
}
```

## 3. 状态图执行入口

文件：`src/social_media_agent/orchestration/langgraph_workflow.py`

```python
from social_media_agent.orchestration.langgraph_workflow import run_task_with_langgraph

result = run_task_with_langgraph(
    task="帮我做7天排期，每天20:00发布",
    quality_threshold=8.0,
)
```

适合场景：

- 步骤稳定、状态明确
- 需要图式节点拆分与条件分支

## 4. CLI 与 HTTP

### 4.1 CLI

```bash
python main.py
python main.py --task "写一篇墨尔本美食帖子"
python main.py --check
```

### 4.2 FastAPI

启动：

```bash
uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
```

核心接口：

- `POST /run-task`
- `POST /schedule/create`
- `GET /schedule/list`
- `POST /schedule/reschedule`
- `POST /memory/save`
- `POST /memory/search`
- `GET /memory/recent`

## 5. 运行参数建议

- `LOOP_ENGINE=loop`：默认可控循环
- `LOOP_ENGINE=graph`：切换状态图流程
- `LOOP_MAX_ITERATIONS=3`：内容迭代轮次
- `LOOP_QUALITY_THRESHOLD=8.0`：质量阈值

## 6. 常见问题

### 6.1 为什么 `run-task` 会返回 422

通常是内容评审未达阈值或工具执行失败。请查看：

- HTTP 返回体 `detail`
- `trace_path` 对应日志

### 6.2 何时用 Agent，何时用 Loop/Graph

- 对话探索、自由调度：用 `create_coordinator_agent()`
- 生产执行、稳定输出：优先 `run_task_with_loop()`
- 需要显式状态节点：用 `run_task_with_langgraph()`
