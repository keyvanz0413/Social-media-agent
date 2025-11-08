# API 文档 - 工具函数参考

本文档详细介绍 Social Media Agent 系统中所有可用的工具函数。

---

## 📋 目录

1. [内容分析工具](#1-内容分析工具)
2. [内容创作工具](#2-内容创作工具)
3. [图片生成工具](#3-图片生成工具)
4. [评审工具](#4-评审工具)
5. [发布工具](#5-发布工具)
6. [模型路由工具](#6-模型路由工具)

---

## 1. 内容分析工具

### `agent_a_analyze_xiaohongshu()`

分析小红书平台上指定关键词的热门内容，提取创作灵感和数据洞察。

**位置**: `tools/content_analyst.py`

#### 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `keyword` | str | 必需 | 搜索关键词 |
| `limit` | int | 5 | 返回笔记数量 |
| `quality_level` | str | "balanced" | 质量级别：fast/balanced/high |

#### 返回值

返回 JSON 字符串，包含以下字段：

```python
{
    "success": bool,              # 是否成功
    "keyword": str,               # 搜索关键词
    "total_analyzed": int,        # 分析的笔记数量
    "title_patterns": [           # 标题模式
        {
            "pattern": str,       # 模式名称（如"数字型"、"疑问式"）
            "example": str,       # 示例标题
            "usage_rate": float   # 使用频率
        }
    ],
    "content_structure": {        # 内容结构
        "opening": str,           # 开头方式
        "body": str,              # 正文结构
        "closing": str            # 结尾方式
    },
    "user_needs": [str],          # 用户需求列表
    "hot_topics": [str],          # 热门话题列表
    "interaction_stats": {        # 互动数据统计
        "avg_likes": float,       # 平均点赞数
        "avg_collects": float,    # 平均收藏数
        "avg_comments": float,    # 平均评论数
        "engagement_rate": float  # 互动率
    },
    "creation_suggestions": [str] # 创作建议
}
```

#### 示例

```python
from tools.content_analyst import agent_a_analyze_xiaohongshu
import json

# 基础用法
result = agent_a_analyze_xiaohongshu("澳洲旅游", limit=5)
data = json.loads(result)

print(f"标题模式: {data['title_patterns']}")
print(f"用户需求: {data['user_needs']}")
print(f"创作建议: {data['creation_suggestions']}")

# 高质量分析
result = agent_a_analyze_xiaohongshu(
    keyword="悉尼旅游",
    limit=10,
    quality_level="high"
)
```

#### 错误处理

函数会捕获异常并返回错误信息：

```python
{
    "success": false,
    "error": "错误详情",
    "message": "用户友好的错误消息"
}
```

---

## 2. 内容创作工具

### `agent_c_create_content()`

基于分析结果创作高质量小红书帖子。

**位置**: `tools/content_creator.py`

#### 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `analysis_result` | str | 必需 | Agent A 的分析结果（JSON字符串） |
| `topic` | str | 必需 | 创作主题 |
| `style` | str | "casual" | 风格：casual/professional/storytelling |
| `quality_level` | str | "balanced" | 质量级别：fast/balanced/high |

#### 返回值

返回 JSON 字符串，包含以下字段：

```python
{
    "success": bool,              # 是否成功
    "title": str,                 # 主标题
    "alternative_titles": [str],  # 备选标题（3-5个）
    "content": str,               # 正文内容
    "hashtags": [str],            # 话题标签（5-8个）
    "image_suggestions": [        # 图片建议
        {
            "description": str,   # 图片描述
            "scene": str,         # 场景说明
            "keywords": [str]     # 关键词
        }
    ],
    "metadata": {                 # 元数据
        "word_count": int,        # 字数
        "paragraph_count": int,   # 段落数
        "emoji_count": int,       # emoji 数量
        "style": str,             # 风格
        "target_audience": str,   # 目标受众
        "estimated_reading_time": int,  # 预计阅读时间（秒）
        "draft_id": str           # 草稿ID（自动保存）
    }
}
```

#### 示例

```python
from tools.content_creator import agent_c_create_content
from tools.content_analyst import agent_a_analyze_xiaohongshu
import json

# 完整流程：分析 → 创作
# 1. 分析
analysis = agent_a_analyze_xiaohongshu("澳洲旅游", limit=5)

# 2. 创作（轻松风格）
result = agent_c_create_content(
    analysis_result=analysis,
    topic="澳洲旅游攻略",
    style="casual",
    quality_level="balanced"
)

data = json.loads(result)
print(f"标题: {data['title']}")
print(f"正文: {data['content'][:100]}...")
print(f"标签: {', '.join(data['hashtags'])}")
print(f"图片建议: {len(data['image_suggestions'])} 张")

# 专业风格
result = agent_c_create_content(
    analysis_result=analysis,
    topic="澳洲留学申请指南",
    style="professional",
    quality_level="high"
)

# 故事风格
result = agent_c_create_content(
    analysis_result=analysis,
    topic="我的澳洲旅行日记",
    style="storytelling"
)
```

---

## 3. 图片生成工具

### `generate_images_for_content()`

基于内容建议使用 AI 生成图片。

**位置**: `tools/image_generator.py`

#### 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `image_suggestions` | str | 必需 | 图片建议（JSON字符串） |
| `topic` | str | 必需 | 主题 |
| `count` | int | None | 生成数量（None=使用建议数量） |
| `method` | str | "dalle" | 生成方法：dalle/local |

#### 返回值

```python
{
    "success": bool,
    "images": [
        {
            "path": str,          # 图片路径
            "description": str,   # 描述
            "method": str,        # 生成方法
            "url": str            # 原始URL（如适用）
        }
    ],
    "metadata": {
        "count": int,
        "method": str,
        "topic": str
    }
}
```

#### 示例

```python
from tools.image_generator import generate_images_for_content
import json

# 从创作结果中提取图片建议
content_result = agent_c_create_content(...)
content_data = json.loads(content_result)
image_suggestions = json.dumps(content_data['image_suggestions'])

# 使用 DALL-E 3 生成（推荐）
result = generate_images_for_content(
    image_suggestions=image_suggestions,
    topic="澳洲旅游",
    method="dalle",
    count=3
)

data = json.loads(result)
for img in data['images']:
    print(f"图片: {img['path']}")
    print(f"描述: {img['description']}")
```

### `generate_images_from_draft()`

从已保存的草稿生成图片。

#### 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `draft_id` | str | 必需 | 草稿ID |
| `method` | str | "dalle" | 生成方法：dalle/local |
| `count` | int | None | 生成数量 |

#### 示例

```python
# 创作内容后会自动生成 draft_id
content_result = json.loads(agent_c_create_content(...))
draft_id = content_result['metadata']['draft_id']

# 从草稿生成图片
result = generate_images_from_draft(
    draft_id=draft_id,
    method="dalle"
)
```

---

## 4. 评审工具

### `review_quality()`

质量评审 Agent，进行5维度质量评估。

**位置**: `agents/reviewers/quality_reviewer.py`

#### 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `title` | str | 必需 | 标题 |
| `content` | str | 必需 | 正文 |
| `topic` | str | 必需 | 主题 |

#### 返回值

```python
{
    "success": bool,
    "score": float,               # 总分（0-10）
    "dimensions": {               # 各维度评分
        "grammar": float,         # 语法准确性
        "structure": float,       # 结构清晰度
        "readability": float,     # 可读性
        "depth": float,           # 内容深度
        "accuracy": float         # 准确性
    },
    "suggestions": [str],         # 优化建议
    "decision": str,              # 决策：approve/revise/reject
    "metadata": {
        "reviewer": "quality",
        "timestamp": str
    }
}
```

### `review_engagement()`

互动评审 Agent，评估互动潜力。

**位置**: `agents/reviewers/engagement_reviewer.py`

#### 返回值结构同上

### `review_compliance()`

合规性检查（函数式评审）。

**位置**: `tools/review_tools_v1.py`

#### 返回值

```python
{
    "success": bool,
    "score": float,               # 合规分数（0-10）
    "risk_level": str,            # 风险等级：low/medium/high
    "issues": [                   # 问题列表
        {
            "type": str,          # 问题类型
            "description": str,   # 描述
            "severity": str       # 严重程度
        }
    ],
    "decision": str               # 决策
}
```

### `review_content_optimized()`

优化的综合评审（并行 + 缓存）。

**位置**: `tools/review_optimized.py`

#### 参数

```python
def review_content_optimized(
    content_data: Dict[str, Any],
    enable_quality: bool = True,
    enable_engagement: bool = True,
    enable_compliance: bool = True,
    use_cache: bool = True
) -> Dict[str, Any]
```

#### 返回值

```python
{
    "final_score": float,         # 综合得分
    "decision": str,              # 最终决策
    "reviews": {
        "quality": {...},
        "engagement": {...},
        "compliance": {...}
    },
    "performance": {
        "total_time": float,
        "cache_hits": int,
        "parallel_execution": bool
    }
}
```

#### 示例

```python
from tools.review_optimized import review_content_optimized

content = {
    "title": "澳洲旅游必去的10个景点",
    "content": "...",
    "topic": "澳洲旅游"
}

# 完整评审（并行 + 缓存）
result = review_content_optimized(
    content_data=content,
    enable_quality=True,
    enable_engagement=True,
    enable_compliance=True
)

print(f"综合得分: {result['final_score']}/10")
print(f"决策: {result['decision']}")
print(f"耗时: {result['performance']['total_time']:.2f}秒")
```

---

## 5. 发布工具

### `publish_to_xiaohongshu()`

发布内容到小红书平台。

**位置**: `tools/publisher.py`

#### 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `title` | str | 必需 | 标题 |
| `content` | str | 必需 | 正文 |
| `images` | List[str] | None | 图片路径列表 |
| `video_path` | str | None | 视频路径 |
| `tags` | List[str] | None | 标签列表 |

#### 返回值

```python
{
    "success": bool,
    "note_id": str,               # 笔记ID
    "url": str,                   # 笔记链接
    "message": str                # 结果消息
}
```

#### 示例

```python
from tools.publisher import publish_to_xiaohongshu

result = publish_to_xiaohongshu(
    title="澳洲旅游攻略",
    content="详细正文内容...",
    images=[
        "/path/to/image1.jpg",
        "/path/to/image2.jpg"
    ],
    tags=["澳洲旅游", "旅行攻略", "悉尼"]
)

data = json.loads(result)
if data['success']:
    print(f"发布成功！笔记ID: {data['note_id']}")
    print(f"链接: {data['url']}")
```

---

## 6. 模型路由工具

### `ModelRouter`

智能模型路由器，支持自动降级策略。

**位置**: `utils/model_router.py`

#### 核心方法

##### `select_model(task_type, quality_level)`

根据任务类型和质量要求选择最优模型。

```python
from utils.model_router import ModelRouter, TaskType, QualityLevel

router = ModelRouter()

# 选择分析任务的模型
model = router.select_model(
    TaskType.ANALYSIS,
    QualityLevel.BALANCED
)
print(f"使用模型: {model}")  # 输出: gpt-4o
```

##### `call_with_fallback(model_name, call_function, **kwargs)`

**自动降级调用**：当主模型失败时，自动尝试备用模型。

```python
def my_llm_call(model, prompt):
    # 你的 LLM 调用逻辑
    return llm.chat(model=model, messages=[...])

router = ModelRouter()

# 自动降级调用
result, used_model = router.call_with_fallback(
    model_name="gpt-4o",
    call_function=my_llm_call,
    max_retries=3,
    retry_delay=1.0,
    prompt="分析这段文本"
)

print(f"成功使用模型: {used_model}")
# 如果 gpt-4o 失败，会自动尝试 gpt-4o-mini
```

##### `check_model_availability(model_name, test_function)`

检查模型是否可用。

```python
# 检查配置
is_available = router.check_model_availability("gpt-4o")

# 实际测试调用
def test_call(model):
    return llm.chat(model=model, messages=[{"role": "user", "content": "test"}])

is_available = router.check_model_availability("gpt-4o", test_call)
print(f"GPT-4o 可用: {is_available}")
```

##### `get_fallback_chain(model_name)`

获取完整的降级链。

```python
chain = router.get_fallback_chain("gpt-4o")
print(chain)  # ['gpt-4o', 'gpt-4o-mini']
```

#### 装饰器模式

使用 `@with_fallback` 装饰器自动添加降级功能：

```python
from utils.model_router import with_fallback

@with_fallback("gpt-4o", max_retries=3)
def analyze_content(model: str, prompt: str):
    return llm.chat(model=model, messages=[{"role": "user", "content": prompt}])

# 直接调用，自动处理降级
result = analyze_content(prompt="分析这段文本")
```

#### 辅助函数

##### `select_best_available_model(task_type, quality_level)`

选择最佳可用模型（自动检查可用性）。

```python
from utils.model_router import select_best_available_model, TaskType, QualityLevel

# 自动选择第一个可用的模型
model = select_best_available_model(
    TaskType.ANALYSIS,
    QualityLevel.HIGH
)
# 如果首选模型不可用，会自动使用降级链中的第一个可用模型
```

---

## 📊 使用示例：完整工作流

```python
from tools.content_analyst import agent_a_analyze_xiaohongshu
from tools.content_creator import agent_c_create_content
from tools.image_generator import generate_images_from_draft
from tools.review_optimized import review_content_optimized
from tools.publisher import publish_to_xiaohongshu
import json

# 1. 分析热门内容
print("📊 步骤 1: 分析热门内容")
analysis = agent_a_analyze_xiaohongshu("澳洲旅游", limit=5)
print("✅ 分析完成")

# 2. 创作内容
print("\n✍️ 步骤 2: 创作内容")
content_result = agent_c_create_content(
    analysis_result=analysis,
    topic="澳洲旅游攻略",
    style="casual"
)
content_data = json.loads(content_result)
print(f"✅ 创作完成，标题: {content_data['title']}")

# 3. 生成图片
print("\n🎨 步骤 3: 生成图片")
draft_id = content_data['metadata']['draft_id']
images_result = generate_images_from_draft(draft_id, method="dalle")
images_data = json.loads(images_result)
image_paths = [img['path'] for img in images_data['images']]
print(f"✅ 生成 {len(image_paths)} 张图片")

# 4. 评审内容
print("\n🔍 步骤 4: 评审内容")
review_result = review_content_optimized({
    "title": content_data['title'],
    "content": content_data['content'],
    "topic": "澳洲旅游"
})
print(f"✅ 评审完成，得分: {review_result['final_score']}/10")
print(f"决策: {review_result['decision']}")

# 5. 发布（如果通过评审）
if review_result['decision'] == 'approve':
    print("\n📤 步骤 5: 发布内容")
    publish_result = publish_to_xiaohongshu(
        title=content_data['title'],
        content=content_data['content'],
        images=image_paths,
        tags=content_data['hashtags']
    )
    publish_data = json.loads(publish_result)
    if publish_data['success']:
        print(f"✅ 发布成功！笔记ID: {publish_data['note_id']}")
else:
    print("\n⚠️ 内容未通过评审，建议优化")
```

---

## 🔧 错误处理

所有工具函数都遵循统一的错误处理模式：

```python
{
    "success": false,
    "error": "技术错误详情",
    "message": "用户友好的错误消息"
}
```

**建议的错误处理方式**：

```python
import json

result = agent_a_analyze_xiaohongshu("keyword")
data = json.loads(result)

if not data.get('success', True):
    print(f"错误: {data['message']}")
    # 处理错误
else:
    # 处理成功结果
    pass
```

---

## 📝 最佳实践

1. **使用质量级别控制成本**
   - `fast`: 快速任务，低成本
   - `balanced`: 平衡模式（推荐）
   - `high`: 高质量任务

2. **利用缓存机制**
   - 相同的分析请求会自动缓存（30分钟）
   - 评审结果也会缓存（24小时）

3. **使用自动降级**
   - 通过 `ModelRouter` 的 `call_with_fallback()` 或 `@with_fallback` 装饰器
   - 确保服务稳定性

4. **批量处理**
   - 使用并行评审 (`review_content_optimized`)
   - 提升处理速度

5. **草稿管理**
   - 内容创作后会自动保存草稿
   - 可以通过 `draft_id` 重新生成图片

---

## 📚 相关文档

- [Agent 使用指南](./API-Agents.md)
- [配置参考](./API-Config.md)
- [架构设计](./Architecture.md)

---

**更新时间**: 2025-11-03  
**版本**: v0.7

