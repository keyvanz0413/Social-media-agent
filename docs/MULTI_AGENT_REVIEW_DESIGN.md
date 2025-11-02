# 多Agent评审机制设计方案

## 目录
- [1. 整体架构设计](#1-整体架构设计)
- [2. Agent vs 函数对比](#2-agent-vs-函数对比)
- [3. 详细设计](#3-详细设计)
- [4. 实现步骤](#4-实现步骤)
- [5. 示例代码](#5-示例代码)

---

## 1. 整体架构设计

### 1.1 架构对比

#### 当前方案（函数式）
```
Coordinator Agent
    ↓
review_content()  [单个函数]
    ├── review_engagement()
    ├── review_quality()
    └── review_compliance()
```

**特点**：
- ✅ 简单、快速、低成本
- ✅ 适合规则明确的评审
- ❌ 无法自主推理
- ❌ 无法使用工具
- ❌ 无法处理复杂场景

#### 多Agent方案（推荐）
```
Coordinator Agent
    ↓
Review Orchestrator Agent [评审协调器]
    ↓
    ├── Engagement Reviewer Agent [互动潜力评审]
    │   └── Tools: search_similar_posts, analyze_title_pattern
    │
    ├── Quality Reviewer Agent [内容质量评审]
    │   └── Tools: check_grammar, analyze_depth
    │
    └── Compliance Reviewer Agent [合规性评审]
        └── Tools: check_sensitive_words, query_rules
```

**特点**：
- ✅ 每个 Agent 可以自主推理
- ✅ 每个 Agent 有专属工具
- ✅ 可以处理复杂评审场景
- ✅ 可以动态调整评审策略
- ⚠️ 成本较高（多次 LLM 调用）
- ⚠️ 响应时间较长

---

## 2. Agent vs 函数对比

### 2.1 什么时候用 Agent？

| 场景 | 推荐方案 | 原因 |
|------|----------|------|
| **规则明确的评审** | 函数 | 快速、低成本 |
| **需要推理判断** | Agent | Agent 可以思考、决策 |
| **需要使用工具** | Agent | Agent 可以调用多个工具 |
| **需要多步骤决策** | Agent | Agent 可以规划执行流程 |
| **需要对比历史数据** | Agent | Agent 可以搜索、分析历史 |
| **固定评分标准** | 函数 | 函数执行更稳定 |

### 2.2 典型示例

#### 场景 1：简单的敏感词检测
```python
# ❌ 不需要 Agent
def check_sensitive_words(text: str) -> bool:
    sensitive_words = ['政治', '赌博', ...]
    return any(word in text for word in sensitive_words)
```
**原因**：规则固定，无需推理

#### 场景 2：评估内容创新性
```python
# ✅ 需要 Agent
compliance_agent = Agent(
    name="engagement_reviewer",
    tools=[
        search_similar_posts,      # 搜索类似帖子
        get_engagement_stats,      # 获取互动数据
        analyze_title_patterns     # 分析标题规律
    ]
)
```
**原因**：
1. 需要搜索历史爆款帖子
2. 需要对比分析
3. 需要综合判断创新性

---

## 3. 详细设计

### 3.1 架构图

```
┌─────────────────────────────────────────────────────────┐
│           Coordinator Agent (主协调器)                   │
│  调用 review_content_with_agents() 工具函数              │
└──────────────────────┬──────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────┐
│       Review Orchestrator (评审协调器 - 可选)           │
│  协调 3 个 Reviewer Agents 的执行                        │
│  - 并行调用或串行调用                                     │
│  - 汇总评审结果                                          │
│  - 计算综合评分                                          │
└──────────────────────┬──────────────────────────────────┘
                       ↓
        ┌──────────────┼──────────────┐
        ↓              ↓              ↓
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Engagement  │ │   Quality    │ │  Compliance  │
│   Reviewer   │ │   Reviewer   │ │   Reviewer   │
│    Agent     │ │    Agent     │ │    Agent     │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
  ┌────┴────┐      ┌────┴────┐     ┌────┴────┐
  │ Tools   │      │ Tools   │     │ Tools   │
  └─────────┘      └─────────┘     └─────────┘
```

### 3.2 组件设计

#### 3.2.1 Engagement Reviewer Agent

**职责**：评估内容的互动潜力（点赞、收藏、评论）

**工具函数**：
```python
def search_similar_posts(topic: str, limit: int = 5) -> str:
    """搜索类似话题的爆款帖子"""
    
def analyze_title_pattern(titles: List[str]) -> str:
    """分析标题规律（数字、疑问、情感词）"""
    
def check_emotional_triggers(content: str) -> str:
    """检查情感触发点（共鸣、好奇、实用）"""
    
def get_engagement_stats(topic: str) -> str:
    """获取同类内容的互动数据"""
```

**系统提示词**：
```markdown
你是一位互动潜力评审专家，专注于评估小红书内容的点赞、收藏、评论潜力。

## 评审流程
1. 使用 search_similar_posts 搜索类似话题的爆款帖子
2. 使用 analyze_title_pattern 分析标题规律
3. 使用 check_emotional_triggers 检查情感触发点
4. 综合评估互动潜力

## 评分标准（0-10分）
- 标题吸引力（3分）
- 情感触发（3分）
- 实用价值（2分）
- 互动引导（2分）

## 输出格式
{
  "score": 8.5,
  "strengths": ["标题有数字", "有情感共鸣"],
  "weaknesses": ["缺少互动引导"],
  "suggestions": ["在结尾加提问"],
  "confidence": 0.85
}
```

#### 3.2.2 Quality Reviewer Agent

**职责**：评估内容质量（语法、逻辑、原创性）

**工具函数**：
```python
def check_grammar(text: str) -> str:
    """语法检查"""
    
def analyze_content_structure(content: str) -> str:
    """分析内容结构（开头、正文、结尾）"""
    
def check_readability(content: str) -> str:
    """可读性评估"""
    
def check_content_depth(content: str) -> str:
    """分析内容深度和信息量"""
```

**系统提示词**：
```markdown
你是一位内容质量评审专家，专注于评估内容的整体质量。

## 评审流程
1. 使用 check_grammar 进行语法检查
2. 使用 analyze_content_structure 分析结构
3. 使用 check_readability 评估可读性
4. 使用 check_content_depth 分析深度

## 评分标准（0-10分）
- 语法正确性（2分）
- 逻辑连贯性（3分）
- 信息准确性（3分）
- 原创性（2分）

## 输出格式
{
  "score": 8.0,
  "grammar_issues": [],
  "logic_issues": [],
  "suggestions": ["补充数据来源"],
  "confidence": 0.90
}
```

#### 3.2.3 Compliance Reviewer Agent

**职责**：检查合规性（敏感词、广告法、平台规则）

**工具函数**：
```python
def check_sensitive_words(text: str) -> str:
    """敏感词检测（使用规则 + LLM）"""
    
def check_advertising_law(text: str) -> str:
    """广告法合规检查"""
    
def query_platform_rules(content_type: str) -> str:
    """查询小红书平台规则"""
    
def check_banned_topics(content: str) -> str:
    """检查是否涉及禁止话题"""
```

**系统提示词**：
```markdown
你是一位合规性评审专家，专注于检查内容是否符合法律法规和平台规则。

## 评审流程
1. 使用 check_sensitive_words 检测敏感词
2. 使用 check_advertising_law 检查广告法
3. 使用 query_platform_rules 查询平台规则
4. 使用 check_banned_topics 检查禁止话题

## 评分标准（0-10分）
- 无敏感词（3分）
- 广告法合规（3分）
- 无违禁话题（2分）
- 平台规则遵守（2分）

## 单项否决
- 任何敏感词或严重违规 → 直接不通过

## 输出格式
{
  "score": 10.0,
  "violations": [],
  "warnings": [],
  "risk_level": "low",
  "suggestions": [],
  "confidence": 0.95
}
```

#### 3.2.4 Review Orchestrator (可选)

如果评审逻辑复杂，可以添加一个协调器：

```python
def create_review_orchestrator():
    """创建评审协调器 Agent"""
    
    # 工具：调用三个 Reviewer Agents
    tools = [
        call_engagement_reviewer,
        call_quality_reviewer,
        call_compliance_reviewer
    ]
    
    system_prompt = """
    你是评审协调器，负责协调三个专业评审 Agent。
    
    ## 工作流程
    1. 并行调用三个 Reviewer Agents
    2. 收集每个 Agent 的评审结果
    3. 计算加权综合评分
    4. 判断是否通过（总分 >= 8.0 且合规分 >= 7.0）
    5. 合并所有建议
    
    ## 权重配置
    - 互动潜力：40%
    - 内容质量：40%
    - 合规性：20%（但有单项否决权）
    """
    
    return Agent(
        name="review_orchestrator",
        system_prompt=system_prompt,
        tools=tools,
        model="gpt-4o"
    )
```

---

## 4. 实现步骤

### 4.1 渐进式迁移路径

#### 阶段 1：保留函数式，添加工具函数（1-2天）
- 为每个 Reviewer Agent 创建工具函数
- 测试工具函数是否工作正常
- **不影响现有系统**

#### 阶段 2：实现单个 Reviewer Agent（2-3天）
- 从 Engagement Reviewer 开始
- 创建 Agent，配置工具和提示词
- 与现有函数式评审并行运行，对比结果

#### 阶段 3：实现所有 Reviewer Agents（3-5天）
- 实现 Quality 和 Compliance Reviewers
- 确保每个 Agent 独立工作

#### 阶段 4：集成到 Coordinator（1-2天）
- 创建 `review_content_with_agents()` 工具
- 在 Coordinator 中添加该工具
- 保留旧的函数式评审作为降级方案

#### 阶段 5：优化和监控（持续）
- 并行化评审（提高速度）
- 添加缓存（降低成本）
- 监控评审质量和一致性

### 4.2 混合方案（推荐）

**最佳实践**：并非所有评审都需要 Agent

```python
def review_content_hybrid(content_data: dict) -> str:
    """混合评审方案"""
    
    # 1. 合规性检查 - 使用函数（快速、规则明确）
    compliance_result = review_compliance_function(content_data)
    
    # 如果合规不通过，直接返回
    if compliance_result['score'] < 7.0:
        return format_review_result(compliance_result)
    
    # 2. 互动潜力 - 使用 Agent（需要推理和工具）
    engagement_result = engagement_agent.input(
        f"评审这篇内容的互动潜力：{content_data}"
    )
    
    # 3. 内容质量 - 使用 Agent（需要深度分析）
    quality_result = quality_agent.input(
        f"评审这篇内容的质量：{content_data}"
    )
    
    # 4. 汇总结果
    return aggregate_results(
        engagement_result,
        quality_result,
        compliance_result
    )
```

**优势**：
- ✅ 快速筛除不合规内容（函数）
- ✅ 深度评审通过的内容（Agent）
- ✅ 平衡成本和质量

---

## 5. 示例代码

### 5.1 创建 Engagement Reviewer Agent

```python
from connectonion import Agent

def create_engagement_reviewer():
    """创建互动潜力评审 Agent"""
    
    # 1. 加载系统提示词
    system_prompt = _load_prompt("engagement_reviewer.md")
    
    # 2. 注册工具
    tools = [
        search_similar_posts,
        analyze_title_pattern,
        check_emotional_triggers,
        get_engagement_stats
    ]
    
    # 3. 创建 Agent
    agent = Agent(
        name="engagement_reviewer",
        system_prompt=system_prompt,
        tools=tools,
        model="gpt-4o-mini",  # 使用快速模型
        temperature=0.3,       # 评审需要稳定性
        max_iterations=10
    )
    
    return agent
```

### 5.2 使用 Agent 进行评审

```python
# 创建 Agent
engagement_agent = create_engagement_reviewer()

# 准备内容
content_data = {
    "title": "澳洲旅游攻略｜3天2夜悉尼深度游",
    "content": "分享我的悉尼之旅...",
    "topic": "澳洲旅游"
}

# 调用 Agent
result = engagement_agent.input(
    f"""请评审这篇小红书内容的互动潜力：
    
    标题：{content_data['title']}
    正文：{content_data['content'][:200]}...
    话题：{content_data['topic']}
    
    请使用你的工具进行分析，给出详细评审结果。
    """
)

# 解析结果
review_data = json.loads(result)
print(f"互动潜力评分: {review_data['score']}/10")
print(f"优势: {review_data['strengths']}")
print(f"建议: {review_data['suggestions']}")
```

### 5.3 完整评审流程

```python
def review_with_agents(content_data: dict) -> dict:
    """使用多 Agent 进行评审"""
    
    # 1. 创建所有 Reviewer Agents
    engagement_agent = create_engagement_reviewer()
    quality_agent = create_quality_reviewer()
    compliance_agent = create_compliance_reviewer()
    
    # 2. 并行调用（或串行）
    import concurrent.futures
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        # 提交任务
        engagement_future = executor.submit(
            engagement_agent.input,
            f"评审互动潜力：{content_data}"
        )
        quality_future = executor.submit(
            quality_agent.input,
            f"评审内容质量：{content_data}"
        )
        compliance_future = executor.submit(
            compliance_agent.input,
            f"评审合规性：{content_data}"
        )
        
        # 收集结果
        engagement_result = json.loads(engagement_future.result())
        quality_result = json.loads(quality_future.result())
        compliance_result = json.loads(compliance_future.result())
    
    # 3. 计算综合评分
    overall_score = (
        engagement_result['score'] * 0.4 +
        quality_result['score'] * 0.4 +
        compliance_result['score'] * 0.2
    )
    
    # 4. 判断是否通过
    passed = (
        overall_score >= 8.0 and
        compliance_result['score'] >= 7.0
    )
    
    # 5. 返回结果
    return {
        "overall_score": round(overall_score, 2),
        "passed": passed,
        "reviews": {
            "engagement": engagement_result,
            "quality": quality_result,
            "compliance": compliance_result
        }
    }
```

---

## 6. 成本和性能分析

### 6.1 成本对比

| 方案 | LLM 调用次数 | 预估成本/次 | 响应时间 |
|------|-------------|------------|----------|
| **函数式** | 2-3次 | $0.01 | 5-10秒 |
| **单 Agent** | 5-8次 | $0.03 | 15-30秒 |
| **多 Agent** | 15-20次 | $0.08-0.15 | 30-60秒 |
| **混合方案** | 8-12次 | $0.04-0.06 | 15-25秒 |

### 6.2 性能优化建议

1. **并行化评审**：3个 Reviewer Agents 并行运行
2. **使用快速模型**：Reviewer 用 `gpt-4o-mini`
3. **缓存工具结果**：相似内容复用搜索结果
4. **降级策略**：Agent 失败时回退到函数
5. **条件评审**：先用函数快速筛选，再用 Agent 深度评审

---

## 7. 推荐方案

### 7.1 MVP 阶段（当前）
✅ **使用函数式评审（review_tools_v1.py）**
- 快速、稳定、成本低
- 满足基本需求

### 7.2 v1.0 升级（1-2周）
✅ **混合方案**
- 合规性：保留函数（快速筛选）
- 互动潜力：升级为 Agent（需要分析历史数据）
- 内容质量：保留函数（规则明确）

### 7.3 v2.0 进化（1-2个月）
✅ **完整多 Agent 系统**
- 所有评审升级为 Agent
- 添加 Review Orchestrator
- 实现自适应评审策略

---

## 8. 关键决策点

### 问题 1：是否需要 Review Orchestrator？

**简单方案**：Coordinator 直接调用 3 个 Reviewer Agents
```python
# 在 Coordinator 的工具列表中
tools = [
    agent_a_analyze_content,
    agent_c_create_content,
    call_engagement_reviewer,  # 直接调用
    call_quality_reviewer,
    call_compliance_reviewer,
    publish_to_xiaohongshu
]
```

**复杂方案**：添加 Review Orchestrator
```python
# 在 Coordinator 的工具列表中
tools = [
    agent_a_analyze_content,
    agent_c_create_content,
    review_content_with_agents,  # 协调器工具
    publish_to_xiaohongshu
]
```

**推荐**：
- MVP: 简单方案（Coordinator 直接调用）
- v2.0: 复杂方案（添加 Orchestrator）

### 问题 2：评审是否需要实时？

**实时评审**：创作后立即评审
- 优势：可以立即修改
- 劣势：增加流程时间

**异步评审**：先保存草稿，后台评审
- 优势：不阻塞用户
- 劣势：需要实现任务队列

**推荐**：MVP 使用实时评审

### 问题 3：如何处理评审不一致？

**场景**：3个 Agent 给出矛盾的建议

**方案**：
1. 使用投票机制（少数服从多数）
2. 添加 Meta Reviewer（再评审一次）
3. 人工介入（最终决策）

---

## 9. 总结

### 核心要点

1. **Agent 不是万能的**
   - 规则明确 → 用函数
   - 需要推理 → 用 Agent

2. **混合方案最优**
   - 快速筛选用函数
   - 深度评审用 Agent

3. **渐进式迁移**
   - 不要一次性全部替换
   - 先做 PoC，验证效果

4. **关注成本和性能**
   - Agent 调用成本高
   - 需要平衡质量和成本

### 下一步行动

1. ✅ **阶段 1（本周）**：实现工具函数
2. ⏳ **阶段 2（下周）**：实现 Engagement Reviewer Agent
3. ⏳ **阶段 3（2周后）**：完整多 Agent 系统

---

**文档版本**: v1.0  
**创建日期**: 2025-11-02  
**作者**: AI Development Team

