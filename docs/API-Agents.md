# API 文档 - Agent 使用指南

本文档介绍如何使用 Social Media Agent 系统中的各个 AI Agent。

---

## 📋 目录

1. [Agent 系统概述](#agent-系统概述)
2. [Coordinator Agent](#coordinator-agent)
3. [Quality Reviewer Agent](#quality-reviewer-agent)
4. [Engagement Reviewer Agent](#engagement-reviewer-agent)
5. [使用示例](#使用示例)
6. [最佳实践](#最佳实践)

---

## Agent 系统概述

### 架构设计

```
Coordinator Agent (主协调器)
  ├── 工具函数
  │   ├── 内容分析工具
  │   ├── 内容创作工具
  │   ├── 图片生成工具
  │   └── 发布工具
  └── 评审 Agents
      ├── Quality Reviewer (质量评审)
      └── Engagement Reviewer (互动评审)
```

### Agent 类型

| Agent | 类型 | 职责 | 模型 |
|-------|------|------|------|
| **Coordinator** | 主协调 | 理解需求、规划流程、调度执行 | GPT-5 Mini |
| **Quality Reviewer** | 评审 | 5维度质量评估、优化建议 | Claude Sonnet 4 |
| **Engagement Reviewer** | 评审 | 互动潜力评估、数据驱动分析 | Claude Sonnet 4 |

---

## Coordinator Agent

### 概述

Coordinator Agent 是系统的核心，负责：
- 理解用户的创作需求
- 制定执行计划
- 调度工具和子 Agent
- 协调整个工作流程

### 创建和使用

#### 基础用法

```python
from agent import create_coordinator_agent

# 创建 Agent
coordinator = create_coordinator_agent()

# 执行任务
result = coordinator.input("发表一篇关于澳洲旅游的帖子")
print(result)
```

#### 自定义配置

```python
from connectonion import Agent
from config import AgentConfig, PathConfig
from tools.content_analyst import agent_a_analyze_xiaohongshu
from tools.content_creator import agent_c_create_content
# ... 其他工具导入

# 加载系统提示词
with open(PathConfig.PROMPTS_DIR / "coordinator.md", "r") as f:
    system_prompt = f.read()

# 创建自定义 Agent
coordinator = Agent(
    name="my_coordinator",
    system_prompt=system_prompt,
    tools=[
        agent_a_analyze_xiaohongshu,
        agent_c_create_content,
        # ... 其他工具
    ],
    max_iterations=30,
    model="gpt-5-mini-2025-08-07"
)

# 使用
result = coordinator.input("创作一篇小红书帖子")
```

### 可用工具

Coordinator Agent 可以调用以下工具：

1. **内容创作工具**
   - `agent_a_analyze_xiaohongshu` - 分析热门内容
   - `agent_c_create_content` - 创作内容
   - `generate_images_for_content` - 生成图片
   - `generate_images_from_draft` - 从草稿生成图片

2. **评审工具**
   - `review_engagement` - 互动评审（Agent）
   - `review_quality` - 质量评审（Agent）
   - `review_compliance` - 合规检查（函数）

3. **发布工具**
   - `publish_to_xiaohongshu` - 发布到小红书

### 工作流程

Coordinator Agent 通常按以下流程执行：

```
1. 理解需求
   ↓
2. 分析热门内容（agent_a_analyze_xiaohongshu）
   ↓
3. 创作内容（agent_c_create_content）
   ↓
4. 生成图片（generate_images_from_draft）
   ↓
5. 评审内容（review_quality, review_engagement, review_compliance）
   ↓
6. 决策（通过/修改/拒绝）
   ↓
7. 发布（publish_to_xiaohongshu）
```

### 交互示例

#### 示例 1：完整流程

```python
coordinator = create_coordinator_agent()

# 用户需求
user_request = "发表一篇关于悉尼旅游的帖子，要轻松活泼的风格"

# Agent 会自动执行：
# 1. 搜索"悉尼旅游"的热门内容
# 2. 分析标题模式和用户需求
# 3. 创作轻松风格的内容
# 4. 生成配图
# 5. 评审质量和互动潜力
# 6. 发布到小红书
result = coordinator.input(user_request)
```

#### 示例 2：仅分析和创作

```python
coordinator = create_coordinator_agent()

result = coordinator.input(
    "帮我分析一下'澳洲留学'这个话题的热门内容，然后写一篇专业风格的帖子，不要发布"
)
# Agent 会停止在创作环节，不会发布
```

#### 示例 3：分步执行

```python
coordinator = create_coordinator_agent()

# 第一步：分析
analysis_request = "分析小红书上关于'墨尔本美食'的热门内容"
result1 = coordinator.input(analysis_request)

# 第二步：基于分析创作
creation_request = "基于刚才的分析，创作一篇关于墨尔本美食的帖子"
result2 = coordinator.input(creation_request)
```

---

## Quality Reviewer Agent

### 概述

Quality Reviewer Agent 负责内容质量评审，采用5维度评估：
1. **语法准确性** (Grammar)
2. **结构清晰度** (Structure)
3. **可读性** (Readability)
4. **内容深度** (Depth)
5. **准确性** (Accuracy)

### 创建和使用

#### 基础用法

```python
from agents.reviewers.quality_reviewer import review_quality
import json

# 评审内容
result = review_quality(
    title="澳洲旅游必去的10个景点🌟",
    content="想去澳洲玩吗？这10个地方千万不能错过...",
    topic="澳洲旅游"
)

# 解析结果
data = json.loads(result)
print(f"总分: {data['score']}/10")
print(f"决策: {data['decision']}")
print(f"建议: {data['suggestions']}")
```

#### 创建自定义 Quality Reviewer

```python
from agents.reviewers.quality_reviewer import create_quality_reviewer_agent
from connectonion import Agent

# 创建 Agent 实例
agent = create_quality_reviewer_agent()

# 使用 Agent 进行评审
result = agent.input(
    "请评审以下内容的质量：\n"
    f"标题：澳洲旅游攻略\n"
    f"正文：...（完整内容）\n"
    f"主题：澳洲旅游"
)
print(result)
```

### 评分标准

| 维度 | 权重 | 评分标准 |
|------|------|----------|
| **语法** | 20% | 无拼写错误、语法正确、标点规范 |
| **结构** | 25% | 逻辑清晰、段落合理、层次分明 |
| **可读性** | 25% | 易于理解、表达流畅、用词恰当 |
| **深度** | 15% | 内容充实、有见解、有价值 |
| **准确性** | 15% | 信息准确、事实可靠、无误导 |

### 决策逻辑

```python
if score >= 8.0:
    decision = "approve"      # 通过，可直接发布
elif score >= 6.0:
    decision = "revise"       # 建议修改后发布
else:
    decision = "reject"       # 不建议发布，需重新创作
```

### 可用工具

Quality Reviewer Agent 内置5个专业工具：

1. `check_grammar()` - 检查语法和拼写
2. `evaluate_structure()` - 评估内容结构
3. `assess_readability()` - 评估可读性
4. `analyze_depth()` - 分析内容深度
5. `verify_accuracy()` - 验证准确性

---

## Engagement Reviewer Agent

### 概述

Engagement Reviewer Agent 负责评估内容的互动潜力，采用数据驱动的方法：
- 搜索相关爆款内容
- 对比标题吸引力
- 分析用户需求匹配度
- 评估互动触发点

### 创建和使用

#### 基础用法

```python
from agents.reviewers.engagement_reviewer import review_engagement
import json

# 评审互动潜力
result = review_engagement(
    title="澳洲旅游必去的10个景点🌟",
    content="想去澳洲玩吗？这10个地方千万不能错过...",
    topic="澳洲旅游"
)

# 解析结果
data = json.loads(result)
print(f"互动潜力: {data['score']}/10")
print(f"决策: {data['decision']}")
print(f"优化建议: {data['suggestions']}")
```

### 评估维度

1. **标题吸引力** (35%)
   - 与爆款标题对比
   - 情感共鸣
   - 好奇心激发

2. **内容实用性** (30%)
   - 用户需求匹配度
   - 信息价值
   - 可操作性

3. **情感共鸣** (20%)
   - 情感表达
   - 共鸣点
   - 故事性

4. **互动触发** (15%)
   - 提问引导
   - 互动元素
   - 讨论话题

### 可用工具

Engagement Reviewer Agent 内置4个评审工具：

1. `search_similar_content()` - 搜索相似爆款内容
2. `compare_title_attractiveness()` - 对比标题吸引力
3. `evaluate_user_needs_match()` - 评估用户需求匹配
4. `assess_interaction_triggers()` - 评估互动触发点

---

## 使用示例

### 示例 1：端到端完整流程

```python
from agent import create_coordinator_agent

# 创建主协调 Agent
coordinator = create_coordinator_agent()

# 一句话完成全流程
result = coordinator.input("发表一篇关于澳洲旅游的帖子")

# Coordinator 会自动：
# 1. 分析澳洲旅游话题
# 2. 创作高质量内容
# 3. 生成配图
# 4. 质量评审
# 5. 互动评审
# 6. 合规检查
# 7. 发布到小红书

print(result)
```

### 示例 2：独立使用评审 Agents

```python
from agents.reviewers.quality_reviewer import review_quality
from agents.reviewers.engagement_reviewer import review_engagement
import json

# 准备内容
content_data = {
    "title": "澳洲旅游攻略 | 悉尼必打卡的10个地方✨",
    "content": "详细的正文内容...",
    "topic": "澳洲旅游"
}

# 1. 质量评审
quality_result = review_quality(**content_data)
quality_data = json.loads(quality_result)
print(f"质量得分: {quality_data['score']}/10")

# 2. 互动评审
engagement_result = review_engagement(**content_data)
engagement_data = json.loads(engagement_result)
print(f"互动潜力: {engagement_data['score']}/10")

# 3. 综合决策
avg_score = (quality_data['score'] + engagement_data['score']) / 2
if avg_score >= 8.0:
    print("✅ 内容优秀，可以发布")
elif avg_score >= 6.0:
    print("⚠️ 内容尚可，建议优化")
else:
    print("❌ 内容质量不足，建议重新创作")
```

### 示例 3：并行评审（优化性能）

```python
from tools.review_optimized import review_content_optimized

# 并行执行所有评审（质量 + 互动 + 合规）
result = review_content_optimized(
    content_data={
        "title": "标题",
        "content": "正文",
        "topic": "话题"
    },
    enable_quality=True,
    enable_engagement=True,
    enable_compliance=True,
    use_cache=True
)

print(f"综合得分: {result['final_score']}/10")
print(f"决策: {result['decision']}")
print(f"耗时: {result['performance']['total_time']:.2f}秒")

# 查看详细评审结果
print("\n质量评审:")
print(f"  分数: {result['reviews']['quality']['score']}")
print(f"  建议: {result['reviews']['quality']['suggestions']}")

print("\n互动评审:")
print(f"  分数: {result['reviews']['engagement']['score']}")
print(f"  建议: {result['reviews']['engagement']['suggestions']}")
```

### 示例 4：自定义 Agent 配置

```python
from connectonion import Agent
from config import PathConfig

# 加载自定义提示词
with open("my_custom_prompt.md", "r") as f:
    custom_prompt = f.read()

# 创建自定义 Coordinator
coordinator = Agent(
    name="my_custom_coordinator",
    system_prompt=custom_prompt,
    tools=[...],  # 你的工具列表
    max_iterations=50,  # 增加迭代次数
    model="claude-opus-4-1-20250805"  # 使用更强的模型
)

result = coordinator.input("创作一篇深度文章")
```

---

## 最佳实践

### 1. Agent 选择策略

```python
# ✅ 推荐：使用 Coordinator Agent（自动化）
coordinator = create_coordinator_agent()
result = coordinator.input("发表一篇关于旅游的帖子")

# ⚠️ 适用场景：需要精细控制每个步骤
# 手动调用各个工具和评审 Agent
```

### 2. 评审策略

```python
# 场景 1：快速发布（仅合规检查）
result = review_content_optimized(
    content_data=content,
    enable_quality=False,
    enable_engagement=False,
    enable_compliance=True
)

# 场景 2：平衡模式（质量 + 合规）
result = review_content_optimized(
    content_data=content,
    enable_quality=True,
    enable_engagement=False,
    enable_compliance=True
)

# 场景 3：完整评审（全部启用）
result = review_content_optimized(
    content_data=content,
    enable_quality=True,
    enable_engagement=True,
    enable_compliance=True
)
```

### 3. 错误处理

```python
try:
    coordinator = create_coordinator_agent()
    result = coordinator.input("创作任务")
except ImportError:
    print("ConnectOnion 框架未安装")
    print("安装命令: pip install connectonion")
except Exception as e:
    print(f"执行失败: {str(e)}")
    # 记录日志、通知用户等
```

### 4. 性能优化

```python
# 使用缓存（相同内容不重复评审）
result = review_content_optimized(
    content_data=content,
    use_cache=True  # 启用缓存
)

# 禁用某些评审（节省时间和成本）
result = review_content_optimized(
    content_data=content,
    enable_engagement=False  # 禁用互动评审
)
```

### 5. 日志和调试

```python
import logging

# 设置日志级别
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建 Agent（会自动记录日志）
coordinator = create_coordinator_agent()

# 查看执行过程
result = coordinator.input("创作任务")
# 日志会显示：
# - 调用了哪些工具
# - 每个步骤的结果
# - 模型选择和降级情况
# - 性能统计
```

---

## 🔧 故障排查

### 问题 1：Agent 创建失败

```python
# 错误：ImportError: No module named 'connectonion'
# 解决：安装 ConnectOnion 框架
pip install connectonion
```

### 问题 2：模型调用失败

```python
# 错误：API key required
# 解决：配置 .env 文件
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://api.example.com/v1
```

### 问题 3：评审 Agent 失败

```python
# 错误：Anthropic API key required
# 解决：两种方案

# 方案 1：配置 Anthropic API key
ANTHROPIC_API_KEY=your-anthropic-key

# 方案 2：修改模型配置（config.py）
# 使用 OpenAI 兼容的第三方平台
AgentConfig.SUB_AGENTS["reviewer_quality"]["model"] = "gpt-4o"
```

### 问题 4：Agent 执行超时

```python
# 解决：增加超时时间或迭代次数
coordinator = Agent(
    name="coordinator",
    system_prompt=system_prompt,
    tools=tools,
    max_iterations=50,  # 增加迭代次数
    model="gpt-4o"
)
```

---

## 📚 相关文档

- [工具函数参考](./API-Tools.md)
- [配置参考](./API-Config.md)
- [架构设计](./Architecture.md)

---

**更新时间**: 2025-11-03  
**版本**: v0.7

