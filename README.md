# Social Media Agent

一个面向内容调研、创作、评审、排期和记忆管理的社媒智能体项目。

## 核心能力

- 话题调研：分析参考内容并提取创作建议
- 内容生成：生成标题、正文、标签、配图建议
- 质量把关：质量评审、互动评审、合规评审
- 发布排期：创建、查询、改期内容计划
- 长期记忆：保存任务日志与偏好，支持语义检索
- 服务化调用：提供 FastAPI 接口
- 双执行引擎：Loop Controller 与 LangGraph Workflow

## 项目结构

```text
Social-media-agent/
├── src/social_media_agent/              # 主实现
│   ├── agent.py                         # 协调 Agent 构建
│   ├── main.py                          # CLI 入口
│   ├── api/server.py                    # FastAPI 服务
│   ├── orchestration/                   # 执行编排（loop/graph）
│   ├── tools/                           # 业务工具
│   ├── agents/reviewers/                # 评审模块
│   ├── memory/                          # 记忆系统（FAISS + fallback）
│   ├── scheduler/                       # 排期系统（SQLite）
│   └── utils/                           # 通用组件
├── social_media_agent/                  # 顶层兼容包（桥接到 src）
├── main.py / agent.py / api_server.py   # 顶层兼容入口
├── tests/                               # pytest 测试
├── scripts/                             # 测试脚本
├── outputs/                             # 运行产物（日志/草稿/索引）
└── docs/                                # 项目文档
```

## 为什么有两层 `social_media_agent`

- `src/social_media_agent/` 是实际业务代码。
- 根目录 `social_media_agent/` 是兼容桥接层，用于让 `python main.py`、旧脚本和某些工具在不改导入路径时仍可运行。
- `main.py`、`agent.py`、`api_server.py` 也是同样的兼容入口，便于 CLI、服务启动和外部调用。

## 环境准备

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp env.example .env
```

Windows:

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy env.example .env
```

至少配置一个模型 Key：

- `OPENAI_API_KEY`
- 或 `ANTHROPIC_API_KEY`

常用配置：

- `OPENAI_BASE_URL`：兼容网关地址
- `MCP_XIAOHONGSHU_URL`：MCP 服务地址
- `MOCK_MODE=true`：本地联调模式
- `LOOP_ENGINE=loop|graph`：选择执行引擎

## 运行

交互模式：

```bash
python main.py
```

单任务：

```bash
python main.py --task "写一篇北海道旅游攻略，参考10篇帖子"
```

配置检查：

```bash
python main.py --check
```

## API 服务

启动：

```bash
uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
```

主要接口：

- `GET /health`
- `POST /run-task`
- `POST /schedule/create`
- `GET /schedule/list`
- `POST /schedule/reschedule`
- `POST /memory/save`
- `POST /memory/search`
- `GET /memory/recent`

## 测试

```bash
pytest -q
```

分类执行：

```bash
pytest -q -m smoke tests/smoke_test.py
pytest -q -m unit tests
pytest -q -m integration tests/comprehensive_test.py
```

脚本：

```bash
./scripts/quick_test.sh
./scripts/run_ci_tests.sh
```

Windows:

```bat
scripts\quick_test.bat
scripts\run_ci_tests.bat
```

## 文档入口

- [文档总览](./docs/README.md)
- [架构说明](./docs/Architecture.md)
- [项目细节解析](./docs/Project-Deep-Dive.md)
- [LangChain 学习指南（基于本项目）](./docs/LangChain-Guide.md)
- [Agent API](./docs/API-Agents.md)
- [Config API](./docs/API-Config.md)
- [Tools API](./docs/API-Tools.md)
- [测试与 CI](./docs/CI-CD.md)
