# 项目细节解析

本文档按“入口 -> 编排 -> 工具 -> 存储”讲清代码。

## 1. 入口层

### 1.1 CLI

文件：`src/social_media_agent/main.py`

- `run_interactive_mode()`：交互式会话
- `run_single_task(task)`：单任务模式
- `_run_controlled_workflow(task)`：根据 `LOOP_ENGINE` 走 loop 或 graph

### 1.2 API

文件：`src/social_media_agent/api/server.py`

- 以 HTTP 封装任务执行、排期和记忆能力
- `_to_api_result()` 统一解析工具输出并抛 `HTTPException`

## 2. 编排层

### 2.1 Loop Controller

文件：`src/social_media_agent/orchestration/loop_controller.py`

关键点：

- `run_task_with_loop` 负责全链路追踪
- 内容任务包含“记忆检索 -> 分析 -> 创作 -> 评审 -> 迭代”
- `_build_feedback_hint` 把评审建议回灌到下一轮创作
- `_build_memory_context` 对记忆进行去重、截断、排序后注入 prompt

### 2.2 LangGraph Workflow

文件：`src/social_media_agent/orchestration/langgraph_workflow.py`

关键点：

- `WorkflowState` 是统一状态容器
- 节点函数只做单一职责更新
- 条件边 `_route_next` 根据 `mode` 决定分支

## 3. 工具层

目录：`src/social_media_agent/tools/`

- `content_analyst.py`：话题分析
- `content_creator.py`：内容生成
- `image_generator.py`：图片生成
- `memory_tools.py`：记忆写入/检索
- `scheduler_tools.py`：排期增查改
- `publisher.py`：发布能力
- `langchain_tools.py`：统一工具注册

工具输出推荐格式（项目当前实践）：

```json
{
  "success": true,
  "message": "...",
  "data": {}
}
```

## 4. 评审层

目录：`src/social_media_agent/agents/reviewers/`

- `quality_reviewer.py`：质量评分与建议
- `engagement_reviewer.py`：互动潜力评估
- `compliance_reviewer.py`：合规风险检查

Loop/Graph 都依赖评审结果决定是否继续迭代或结束。

## 5. 记忆系统（FAISS）

目录：`src/social_media_agent/memory/`

- `embeddings.py`：文本向量化
- `vector_store.py`：向量索引与检索
- `memory_service.py`：对外统一读写接口

运行产物：

- `outputs/memory/records.jsonl`：原始条目
- `outputs/memory/faiss_index/`：向量索引

检索路径：

1. 文本转向量
2. 在 FAISS 索引中近邻搜索
3. 回查记录并返回 `top_k`
4. 上层按类型和分数做二次筛选

## 6. 排期系统

目录：`src/social_media_agent/scheduler/`

- `scheduler_service.py` 使用 SQLite 保存计划
- 通过工具层暴露 `create/list/reschedule`

## 7. 配置中心

文件：`src/social_media_agent/config.py`

关注几类配置：

- 模型与 Key：`OPENAI_API_KEY`、`ANTHROPIC_API_KEY`
- 路径：`OUTPUTS_DIR`、`MEMORY_DIR`、`SCHEDULE_DB_PATH`
- 执行：`LOOP_ENGINE`、`LOOP_MAX_ITERATIONS`

## 8. 测试结构

目录：`tests/`

- `smoke_test.py`：快速连通性
- `comprehensive_test.py`：集成回归
- `test_langgraph_workflow.py`：状态图流程
- `test_memory.py` / `test_scheduler.py`：存储能力
- `test_langchain_tools.py`：工具注册与参数契约

## 9. 代码阅读建议

1. 先读 `main.py` 了解入口和执行分流。
2. 再读 `loop_controller.py` 看闭环。
3. 然后读 `langgraph_workflow.py` 理解状态机实现。
4. 最后按业务看 `tools/`、`memory/`、`scheduler/`。
