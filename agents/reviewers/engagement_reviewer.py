"""
Engagement Reviewer Agent
互动潜力评审 Agent

职责：
- 评估内容的点赞、收藏、评论潜力
- 分析标题吸引力和情感触发点
- 对比类似爆款帖子
- 提供具体的优化建议

工具：
- search_similar_posts: 搜索类似爆款帖子
- analyze_title_patterns: 分析标题规律
- check_emotional_triggers: 检查情感触发点
- get_engagement_stats: 获取同类内容互动数据

输出：
- score: 互动潜力评分 (0-10)
- strengths: 优势列表
- weaknesses: 不足列表
- suggestions: 优化建议列表
- confidence: 评分置信度
"""

import logging
import json
from pathlib import Path

try:
    from connectonion import Agent
except ImportError:
    Agent = None
    logging.warning("ConnectOnion 未安装，无法使用 Engagement Reviewer Agent")

# 导入工具函数
from tools.review_tools import (
    search_similar_posts,
    analyze_title_patterns,
    check_emotional_triggers,
    get_engagement_stats
)

from config import AgentConfig, ModelConfig

logger = logging.getLogger(__name__)


def create_engagement_reviewer_agent():
    """
    创建互动潜力评审 Agent
    
    Returns:
        配置好的 Engagement Reviewer Agent 实例
        
    Example:
        >>> agent = create_engagement_reviewer_agent()
        >>> result = agent.input('''请评审这篇帖子的互动潜力：
        ... 标题：澳洲旅游攻略｜3天2夜悉尼深度游
        ... 正文：分享我的悉尼之旅...
        ... 话题：澳洲旅游
        ... ''')
        >>> review = json.loads(result)
        >>> print(f"评分: {review['score']}/10")
    """
    if Agent is None:
        raise ImportError(
            "ConnectOnion 框架未安装。请运行: pip install connectonion"
        )
    
    # 1. 加载系统提示词
    system_prompt = _load_system_prompt()
    
    # 2. 注册工具函数
    tools = [
        search_similar_posts,
        analyze_title_patterns,
        check_emotional_triggers,
        get_engagement_stats
    ]
    
    # 3. 获取配置
    agent_config = AgentConfig.SUB_AGENTS.get("reviewer_engagement", {})
    model_name = agent_config.get("model", "gpt-4o-mini")
    # 注意：ConnectOnion Agent 不支持 temperature 参数
    # temperature 由模型本身控制
    
    # 4. 创建 Agent
    logger.info(f"创建 Engagement Reviewer Agent，模型: {model_name}")
    
    agent = Agent(
        name="engagement_reviewer",
        system_prompt=system_prompt,
        tools=tools,
        model=model_name,
        max_iterations=10  # 评审通常不需要太多迭代
    )
    
    logger.info("Engagement Reviewer Agent 创建成功")
    return agent


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
    便捷函数：使用 Agent 评审互动潜力
    
    这是一个封装函数，方便其他模块调用。
    
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
        # 创建 Agent
        agent = create_engagement_reviewer_agent()
        
        # 构建输入
        user_input = f"""请评审这篇小红书内容的互动潜力：

标题：{content_data.get('title', '')}

正文：
{content_data.get('content', '')[:500]}{"..." if len(content_data.get('content', '')) > 500 else ""}

话题：{content_data.get('topic', '未指定')}

请使用你的工具进行深度分析，给出详细的评审结果。"""
        
        # 调用 Agent
        result = agent.input(user_input)
        
        # Agent 应该返回 JSON，但为了保险起见，验证一下
        try:
            json.loads(result)
            return result
        except json.JSONDecodeError:
            # 如果 Agent 返回的不是 JSON，尝试提取
            logger.warning("Agent 返回的不是纯JSON，尝试提取")
            # 简单提取逻辑（实际应该更复杂）
            import re
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                return json_match.group(0)
            else:
                # 返回错误
                return json.dumps({
                    "success": False,
                    "error": "Agent 返回格式错误",
                    "raw_output": result
                })
        
    except Exception as e:
        logger.error(f"Engagement 评审失败: {str(e)}", exc_info=True)
        return json.dumps({
            "success": False,
            "error": str(e)
        })


# 导出
__all__ = [
    "create_engagement_reviewer_agent",
    "review_engagement"
]

