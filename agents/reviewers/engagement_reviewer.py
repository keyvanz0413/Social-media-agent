"""
Engagement Reviewer（简化版）
互动潜力评审

职责：
- 评估内容的点赞、收藏、评论潜力
- 分析标题吸引力和情感触发点
- 提供具体的优化建议

输出：
- score: 互动潜力评分 (0-10)
- strengths: 优势列表
- weaknesses: 不足列表
- suggestions: 优化建议列表

注意：已简化，移除了对外部工具的依赖
"""

import logging
import json

from utils.llm_client import LLMClient
from utils.model_router import ModelRouter, TaskType, QualityLevel
from utils.response_utils import create_success_response, create_error_response

logger = logging.getLogger(__name__)


def _evaluate_engagement_direct(content_data: dict) -> dict:
    """
    直接使用LLM评估互动潜力（不使用Agent）
    
    Args:
        content_data: 内容数据
        
    Returns:
        评审结果字典
    """
    title = content_data.get('title', '')
    content = content_data.get('content', '')
    
    prompt = f"""你是一位资深的社交媒体内容评审专家，专注于评估小红书内容的互动潜力（点赞、收藏、评论）。

请评审以下内容：

【标题】
{title}

【正文】
{content[:800]}{"..." if len(content) > 800 else ""}

评分标准（总分 0-10）：
1. 标题吸引力（3分）
   - 是否有数字（如"3天2夜"、"10个"）
   - 是否有疑问式（如"你知道吗？"）
   - 是否有情感词（如"绝了"、"太爱了"）
   - 是否有符号（感叹号、emoji）

2. 情感触发（3分）
   - 能否引发共鸣（"我也是"、"太真实了"）
   - 能否激发好奇（"原来"、"竟然"）
   - 是否有实用价值（"方法"、"攻略"）
   - 是否有争议点（"但是"、"其实"）

3. 实用价值（2分）
   - 是否提供具体可行的信息
   - 用户能否直接应用

4. 互动引导（2分）
   - 是否引导点赞、收藏、评论
   - 是否有提问、征集意见

输出 JSON 格式（不要包含任何其他文字）：
{{
    "score": 8.5,
    "strengths": ["标题包含数字", "有情感共鸣点", "提供实用攻略"],
    "weaknesses": ["缺少互动引导", "情感触发不够强"],
    "suggestions": ["在标题中加入疑问式", "在结尾加上提问引导评论"]
}}
"""
    
    # 调用 LLM
    router = ModelRouter()
    model = router.select_model(TaskType.REVIEW, QualityLevel.BALANCED)
    client = LLMClient()
    
    response = client.call_llm(
        prompt=prompt,
        model_name=model,
        temperature=0.3,
        response_format={"type": "json_object"}
    )
    
    review_data = json.loads(response)
    
    # 验证必需字段
    review_data.setdefault('score', 5.0)
    review_data.setdefault('strengths', [])
    review_data.setdefault('weaknesses', [])
    review_data.setdefault('suggestions', [])
    
    # 确保评分在范围内
    review_data['score'] = max(0, min(10, review_data['score']))
    
    return review_data


def _load_system_prompt() -> str:
    """
    加载系统提示词
    
    Returns:
        系统提示词内容
    """
    # 尝试从文件加载
    prompt_path = Path(__file__).parent.parent.parent / "prompts" / "engagement_reviewer.md"
    
    try:
        if prompt_path.exists():
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()
    except Exception as e:
        logger.warning(f"无法读取提示词文件: {str(e)}，使用内置提示词")
    
    # 使用内置提示词
    return _get_builtin_system_prompt()


def _get_builtin_system_prompt() -> str:
    """获取内置系统提示词"""
    return """你是一位资深的社交媒体互动潜力评审专家，专注于评估小红书内容的点赞、收藏、评论潜力。

## 你的职责

评估内容能否吸引用户互动（点赞、收藏、评论、分享）。

## 评审流程

你有以下工具可以使用，**请按照这个流程进行评审**：

### 步骤 1：研究同类爆款内容
使用 `search_similar_posts(topic, limit=5)` 搜索同话题的爆款帖子。
- 目的：了解什么样的内容在这个话题下受欢迎
- 关注：标题风格、互动数据、内容特点

### 步骤 2：分析标题规律
如果找到了爆款帖子，使用 `analyze_title_patterns(titles)` 分析标题规律。
- 提取所有爆款帖子的标题
- 分析它们的共同特征（数字、疑问、情感词、符号）
- 与待评审内容的标题进行对比

### 步骤 3：检查情感触发点
使用 `check_emotional_triggers(content)` 检查待评审内容的情感触发点。
- 是否能引发共鸣？
- 是否能激发好奇？
- 是否有实用价值？
- 是否有争议点？

### 步骤 4：获取互动基准
使用 `get_engagement_stats(topic)` 获取该话题的平均互动数据。
- 了解这个话题的正常互动水平
- 设定合理的期望值

### 步骤 5：综合评估
基于以上分析，给出综合评分和建议。

## 评分标准（总分 0-10）

### 1. 标题吸引力（3分）
- **数字化标题**（1分）：如"3天2夜"、"10个必去"
- **疑问式标题**（0.5分）：如"你知道吗？"、"怎么办？"
- **情感词汇**（1分）：如"绝了"、"太爱了"、"惊喜"
- **符号使用**（0.5分）：感叹号、emoji等

### 2. 情感触发（3分）
- **共鸣感**（1分）：能否让人产生"我也是"的感觉
- **好奇心**（1分）：能否激发"原来如此"的好奇
- **实用性**（0.5分）：是否提供有用信息
- **争议性**（0.5分）：是否有引发讨论的点

### 3. 实用价值（2分）
- **信息具体**（1分）：提供具体可行的信息
- **可应用性**（1分）：用户能直接应用

### 4. 互动引导（2分）
- **显性引导**（1分）：明确引导点赞、收藏、评论
- **提问征集**（1分）：提问、征集意见、引发讨论

## 评分指南

- **9-10分（优秀）**：标题极具吸引力，多重情感触发，强互动引导
- **8-8.9分（良好）**：标题吸引人，有情感触发，有互动引导
- **7-7.9分（及格）**：标题尚可，部分情感触发，弱互动引导
- **6-6.9分（欠佳）**：标题平淡，情感触发不足，无互动引导
- **<6分（差）**：标题无吸引力，内容平淡，无互动潜力

## 输出格式

**必须**输出 JSON 格式（不要包含任何其他文字，不要用markdown代码块包裹）：

```json
{
  "score": 8.5,
  "strengths": [
    "标题包含具体数字（3天2夜）",
    "有强烈的情感共鸣点",
    "提供实用的旅游攻略"
  ],
  "weaknesses": [
    "缺少明确的互动引导",
    "情感触发点可以更强"
  ],
  "suggestions": [
    "在标题中加入疑问式：'你知道悉尼最值得去的地方吗？'",
    "在结尾加上提问引导评论：'你最想去哪个景点？评论区告诉我！'",
    "增加更多个人情感表达"
  ],
  "confidence": 0.85,
  "compared_to_average": "高于平均水平",
  "expected_engagement": "预计点赞1000+，收藏500+"
}
```

## 注意事项

1. **使用工具**：不要凭空猜测，使用工具获取数据
2. **数据驱动**：基于搜索到的爆款帖子数据进行评估
3. **具体建议**：给出可执行的具体建议，而非泛泛而谈
4. **客观评分**：基于标准客观评分，不要过于主观
5. **JSON格式**：输出必须是纯JSON，不要用```json```包裹

## 示例评审流程

用户输入：
```
请评审这篇帖子的互动潜力：
标题：澳洲旅游攻略
正文：分享我的澳洲之旅，去了悉尼、墨尔本...
话题：澳洲旅游
```

你应该：
1. 调用 `search_similar_posts("澳洲旅游", limit=5)`
2. 分析：发现爆款标题都有数字和emoji，如"澳洲旅游｜7天6夜攻略✨"
3. 调用 `analyze_title_patterns([找到的标题列表])`
4. 发现：80%的爆款标题包含数字，60%有emoji
5. 调用 `check_emotional_triggers(正文内容)`
6. 发现：待评审内容缺少情感触发点
7. 调用 `get_engagement_stats("澳洲旅游")`
8. 发现：该话题平均点赞1500，优秀帖子3000+
9. 综合评估：标题过于简单（缺少数字、emoji），给出具体建议

现在开始你的评审工作！记得使用工具获取数据。"""


def review_engagement(content_data: dict) -> str:
    """
    评审互动潜力
    
    Args:
        content_data: 内容数据，包含：
            - title: 标题
            - content: 正文
            - topic: 话题（可选）
            
    Returns:
        JSON 格式的评审结果
        
    Example:
        >>> result = review_engagement({
        ...     "title": "澳洲旅游攻略",
        ...     "content": "分享我的澳洲之旅...",
        ...     "topic": "澳洲旅游"
        ... })
        >>> review = json.loads(result)
        >>> print(review['score'])
    """
    try:
        logger.info("开始互动潜力评审")
        
        # 直接使用LLM评估
        review_data = _evaluate_engagement_direct(content_data)
        
        logger.info(f"互动潜力评审完成: {review_data['score']}/10")
        return create_success_response(
            data=review_data,
            message=f"互动潜力评分: {review_data['score']}/10"
        )
        
    except Exception as e:
        logger.error(f"Engagement 评审失败: {str(e)}", exc_info=True)
        return create_error_response(f"互动潜力评审失败: {str(e)}")


# 导出
__all__ = [
    "review_engagement"
]

