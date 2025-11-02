# 多Agent评审系统实施指南

## 📖 快速理解

### 核心问题

**Q: Agent 和函数有什么区别？**

```python
# ❌ 函数：只能执行固定逻辑
def review_engagement(content):
    score = 5.0
    if has_number_in_title(content):
        score += 1.0
    return score

# ✅ Agent：可以思考、使用工具、做决策
engagement_agent = Agent(
    tools=[
        search_similar_posts,    # 搜索爆款
        analyze_title_patterns,  # 分析规律
        check_emotional_triggers # 检查情感
    ]
)
# Agent 会自主决定：
# "我先搜索同类爆款，再分析标题规律，然后对比..."
```

### 什么时候用 Agent？

| 场景 | 推荐 | 原因 |
|------|------|------|
| 固定规则检查（如敏感词）| 函数 | 快速、稳定、低成本 |
| 需要对比历史数据 | Agent | Agent 可以搜索和分析 |
| 需要推理判断 | Agent | Agent 可以思考决策 |
| 简单评分 | 函数 | 函数足够 |

---

## 🏗️ 系统架构

### 当前架构（函数式）
```
Coordinator Agent
    ↓
review_content() [函数]
    ├── review_engagement() [函数]
    ├── review_quality() [函数]
    └── review_compliance() [函数]
```

### 升级架构（多Agent）
```
Coordinator Agent
    ↓
review_content_with_agents() [工具]
    ↓
    ├── Engagement Reviewer Agent
    │   └── Tools: search_posts, analyze_titles
    │
    ├── Quality Reviewer Agent
    │   └── Tools: check_grammar, analyze_structure
    │
    └── Compliance Reviewer Agent
        └── Tools: check_sensitive, query_rules
```

---

## 🚀 实施步骤

### 阶段 1：创建工具函数（已完成 ✅）

**文件**: `tools/review_tools.py`

创建了 8 个工具函数：
- `search_similar_posts` - 搜索爆款帖子
- `analyze_title_patterns` - 分析标题规律
- `check_emotional_triggers` - 检查情感触发点
- `get_engagement_stats` - 获取互动统计
- `check_grammar` - 语法检查
- `analyze_content_structure` - 分析结构
- `check_sensitive_words_detailed` - 敏感词检测
- `query_platform_rules` - 查询平台规则

**状态**: ✅ 已创建，可以单独测试

### 阶段 2：创建 Engagement Reviewer Agent（已完成 ✅）

**文件**: `agents/reviewers/engagement_reviewer.py`

实现了第一个真正的 Reviewer Agent：
- 使用 ConnectOnion 框架
- 配置了 4 个专属工具
- 详细的系统提示词
- 可以独立运行

**测试**:
```bash
python tests/test_engagement_reviewer_agent.py
```

**状态**: ✅ 已实现，可测试

### 阶段 3：创建其他 Reviewer Agents（待实施）

#### 3.1 Quality Reviewer Agent

**文件**: `agents/reviewers/quality_reviewer.py`（待更新）

**需要**:
1. 复制 `engagement_reviewer.py` 的结构
2. 修改工具列表：
   ```python
   tools = [
       check_grammar,
       analyze_content_structure
   ]
   ```
3. 修改系统提示词（专注于质量评审）
4. 实现 `review_quality()` 函数

**工作量**: 2-3 小时

#### 3.2 Compliance Reviewer Agent

**文件**: `agents/reviewers/compliance_reviewer.py`（待更新）

**需要**:
1. 工具列表：
   ```python
   tools = [
       check_sensitive_words_detailed,
       query_platform_rules
   ]
   ```
2. 系统提示词（专注于合规性）
3. 实现 `review_compliance()` 函数

**特殊考虑**:
- 合规检查可能不需要 Agent（规则明确）
- 可以保留函数式，只在需要时升级
- **建议**: 先保留函数式

**工作量**: 2-3 小时（如果升级为 Agent）

### 阶段 4：集成到 Coordinator（待实施）

**方案 A：简单方案（推荐）**

在 `agent.py` 中添加三个工具：

```python
# 导入 Reviewer Agents
from agents.reviewers.engagement_reviewer import review_engagement
from agents.reviewers.quality_reviewer import review_quality
from agents.reviewers.compliance_reviewer import review_compliance

# 在 create_coordinator_agent() 中添加工具
tools = [
    agent_a_analyze_xiaohongshu,
    agent_c_create_content,
    generate_images_from_draft,
    
    # 新增：评审工具
    review_engagement,      # Agent 评审
    review_quality,         # Agent 评审
    review_compliance,      # 函数评审（或 Agent）
    
    publish_to_xiaohongshu
]
```

**方案 B：复杂方案（可选）**

创建统一的评审工具：

**文件**: `tools/review_orchestrator.py`

```python
def review_content_with_agents(content_data: dict) -> str:
    """统一的评审工具，协调多个 Reviewer Agents"""
    
    # 1. 创建 Agents
    engagement_agent = create_engagement_reviewer_agent()
    quality_agent = create_quality_reviewer_agent()
    # compliance 保留函数
    
    # 2. 并行调用
    with ThreadPoolExecutor() as executor:
        eng_future = executor.submit(...)
        qual_future = executor.submit(...)
    
    # 3. 汇总结果
    return aggregate_results(...)
```

然后在 Coordinator 中只添加一个工具：
```python
tools = [
    ...,
    review_content_with_agents,  # 统一入口
    ...
]
```

**推荐**: 先用方案 A（简单），效果好再考虑方案 B

### 阶段 5：优化和监控（持续）

**性能优化**:
- 并行化评审（3 个 Agent 同时运行）
- 缓存工具结果（相似内容复用）
- 使用快速模型（gpt-4o-mini）

**成本优化**:
- 只在需要时使用 Agent
- 先用函数快速筛选
- 监控 API 调用次数

**质量监控**:
- 记录评审结果
- 对比 Agent vs 函数的差异
- 收集用户反馈

---

## 📝 实施清单

### 本周（已完成 ✅）
- [x] 设计整体架构
- [x] 创建工具函数文件 `tools/review_tools.py`
- [x] 实现 Engagement Reviewer Agent
- [x] 创建测试文件
- [x] 编写文档

### 下周（待实施）
- [ ] 测试 Engagement Reviewer Agent
- [ ] 修复工具函数中的 bug
- [ ] 实现 Quality Reviewer Agent
- [ ] 决定 Compliance 是否需要 Agent
- [ ] 创建评审对比测试

### 2 周后（待实施）
- [ ] 集成所有 Reviewer Agents 到 Coordinator
- [ ] 实现并行评审
- [ ] 添加降级策略（Agent 失败时用函数）
- [ ] 性能和成本优化
- [ ] 完整流程测试

---

## 🧪 测试方法

### 测试 1：单独测试 Engagement Agent

```bash
cd Social-media-agent
python tests/test_engagement_reviewer_agent.py
```

**预期**:
- Agent 会调用 4 个工具
- 搜索爆款帖子
- 分析标题规律
- 给出详细评审结果

### 测试 2：对比 Agent vs 函数

运行测试文件的对比部分，查看两种方案的差异。

### 测试 3：工具函数单独测试

```python
from tools.review_tools import search_similar_posts

result = search_similar_posts("澳洲旅游", limit=5)
print(result)
```

---

## 💡 关键决策

### 决策 1：Compliance 是否需要 Agent？

**分析**:
- 合规检查规则明确（敏感词库、广告法）
- 不需要复杂推理
- 函数式评审已经足够

**建议**: 
- ✅ **保留函数式**（`review_tools_v1.py` 中的 `review_compliance`）
- 只在需要"智能理解上下文"时才升级为 Agent

### 决策 2：是否需要 Review Orchestrator？

**分析**:
- MVP 阶段：Coordinator 直接调用 3 个 Agents 即可
- 未来如果逻辑复杂（如多轮评审、自适应策略），再添加 Orchestrator

**建议**:
- ✅ **暂不添加**
- 直接在 Coordinator 中调用 Reviewer Agents

### 决策 3：评审是否并行？

**分析**:
- 串行：简单但慢（90秒）
- 并行：快但复杂（30秒）

**建议**:
- MVP: 串行（先保证能用）
- v1.0: 并行（优化性能）

---

## 📊 成本估算

### 函数式评审
- LLM 调用：2-3 次
- 成本：~$0.01/次
- 时间：5-10 秒

### Agent 评审（单个）
- LLM 调用：5-8 次（Agent 自己 + 工具）
- 成本：~$0.03-0.05/次
- 时间：20-40 秒

### 多Agent 评审（3个）
- LLM 调用：15-25 次
- 成本：~$0.10-0.15/次
- 时间：
  - 串行：60-120 秒
  - 并行：30-60 秒

### 混合方案（推荐）
- Compliance: 函数（$0.005）
- Engagement: Agent（$0.04）
- Quality: 函数（$0.005）
- **总计**：~$0.05/次，20-30 秒

---

## 🎯 下一步行动

### 立即可做
1. **测试现有实现**
   ```bash
   python tests/test_engagement_reviewer_agent.py
   ```

2. **修复可能的 bug**
   - 工具函数的 MCP 调用
   - Agent 返回格式
   - 错误处理

### 本周内
3. **实现 Quality Reviewer Agent**
   - 复制 engagement_reviewer.py
   - 修改工具和提示词
   - 测试

4. **决定 Compliance 方案**
   - 保持函数 or 升级 Agent？

### 下周
5. **集成到 Coordinator**
   - 添加评审工具到 agent.py
   - 更新 Coordinator 提示词
   - 完整流程测试

---

## 📚 相关文件

### 核心文件
- `docs/MULTI_AGENT_REVIEW_DESIGN.md` - 详细设计文档
- `tools/review_tools.py` - 工具函数集
- `agents/reviewers/engagement_reviewer.py` - Engagement Agent
- `tests/test_engagement_reviewer_agent.py` - 测试文件

### 待更新文件
- `agents/reviewers/quality_reviewer.py` - 需要实现
- `agents/reviewers/compliance_reviewer.py` - 需要决策
- `agent.py` - 需要添加评审工具
- `prompts/coordinator.md` - 需要更新提示词

---

## 🤔 常见问题

### Q1: 为什么不全部用 Agent？

**A**: Agent 不是万能的
- 规则明确的任务（如敏感词检测）→ 函数更快更稳定
- 需要推理的任务（如评估创新性）→ Agent 更智能

### Q2: Agent 调用成本会不会太高？

**A**: 可以优化
1. 使用快速模型（gpt-4o-mini）
2. 只在需要时使用 Agent
3. 缓存工具结果
4. 并行调用减少时间

**对比**:
- 图片生成：$0.16（4 张 DALL-E）
- Agent 评审：$0.05-0.10
- 总成本占比：~30%，可接受

### Q3: 如何保证 Agent 稳定性？

**A**: 多重保障
1. 详细的系统提示词
2. 降级策略（Agent 失败 → 函数）
3. 结果验证和修复
4. 错误处理和重试

### Q4: 现在就要全部实现吗？

**A**: 不需要，渐进式
1. **本周**: 测试 Engagement Agent
2. **下周**: 实现 Quality Agent
3. **2周后**: 集成到 Coordinator
4. **持续**: 优化和监控

---

## 📞 需要帮助？

### 实施问题
- Agent 创建报错 → 检查 ConnectOnion 安装
- 工具函数报错 → 检查 MCP 服务是否运行
- 成本过高 → 优化模型选择和并行策略

### 设计问题
- 不确定是否用 Agent → 参考决策矩阵
- 不知道如何优化 → 参考成本分析
- 遇到特殊场景 → 查看设计文档

---

**文档版本**: v1.0  
**创建日期**: 2025-11-02  
**最后更新**: 2025-11-02  
**状态**: ✅ Engagement Agent 已实现，其他待实施

