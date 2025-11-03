"""
Quality Reviewer Agent
内容质量评审 Agent

职责：
- 评估内容的可读性和专业性
- 检查语法、结构、逻辑
- 分析内容深度和价值
- 提供质量优化建议

工具：
- check_grammar: 检查语法问题
- analyze_content_structure: 分析内容结构
- check_readability: 检查可读性
- analyze_content_depth: 分析内容深度
- check_information_accuracy: 检查信息准确性

输出：
- score: 质量评分 (0-10)
- strengths: 优势列表
- weaknesses: 不足列表
- suggestions: 优化建议列表
- confidence: 评分置信度
"""

import logging
import json
import warnings
from pathlib import Path

try:
    from connectonion import Agent
except ImportError:
    Agent = None
    logging.warning("ConnectOnion 未安装，无法使用 Quality Reviewer Agent")

# 导入工具函数
from tools.review_tools import (
    check_grammar,
    analyze_content_structure,
    check_readability,
    analyze_content_depth,
    check_information_accuracy
)

from config import AgentConfig, ModelConfig

logger = logging.getLogger(__name__)


def create_quality_reviewer_agent():
    """
    创建内容质量评审 Agent
    
    Returns:
        配置好的 Quality Reviewer Agent 实例
        
    Example:
        >>> agent = create_quality_reviewer_agent()
        >>> result = agent.input('''请评审这篇帖子的内容质量：
        ... 标题：澳洲旅游攻略｜3天2夜悉尼深度游
        ... 正文：分享我的悉尼之旅...
        ... ''')
        >>> review = json.loads(result)
        >>> print(f"质量评分: {review['score']}/10")
    """
    if Agent is None:
        raise ImportError(
            "ConnectOnion 框架未安装。请运行: pip install connectonion"
        )
    
    # 1. 加载系统提示词
    system_prompt = _load_system_prompt()
    
    # 2. 注册工具函数
    tools = [
        check_grammar,
        analyze_content_structure,
        check_readability,
        analyze_content_depth,
        check_information_accuracy
    ]
    
    # 3. 获取配置
    agent_config = AgentConfig.SUB_AGENTS.get("reviewer_quality", {})
    model_name = agent_config.get("model", "gpt-4o-mini")
    
    # 4. 创建 Agent
    logger.info(f"创建 Quality Reviewer Agent，模型: {model_name}")
    
    # 抑制 connectonion 的 system_prompt 警告输出
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning, module="connectonion")
        agent = Agent(
            name="quality_reviewer",
            system_prompt=system_prompt,
            tools=tools,
            model=model_name,
            max_iterations=10
        )
    
    logger.info("Quality Reviewer Agent 创建成功")
    return agent


def _load_system_prompt() -> str:
    """
    加载系统提示词
    
    Returns:
        系统提示词内容
    """
    # 尝试从文件加载
    prompt_path = Path(__file__).parent.parent.parent / "prompts" / "quality_reviewer.md"
    
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
    return """你是一位资深的内容质量评审专家，专注于评估小红书内容的专业性、可读性和价值。

## 你的职责

评估内容的整体质量，包括语法、结构、逻辑、深度和准确性。

## 评审流程

你有以下工具可以使用，**请按照这个流程进行评审**：

### 步骤 1：检查语法问题
使用 `check_grammar(text)` 检查基础语法问题。
- 标点符号使用
- 错别字和拼写
- 重复词汇
- 基本语法错误

### 步骤 2：分析内容结构
使用 `analyze_content_structure(content)` 分析内容组织。
- 是否有清晰的开头？
- 正文是否有逻辑？
- 是否有总结或行动号召？
- 段落划分是否合理？

### 步骤 3：评估可读性
使用 `check_readability(content)` 评估阅读体验。
- 句子长度是否适中？
- 是否有过多专业术语？
- 排版是否清晰？
- 是否易于快速浏览？

### 步骤 4：分析内容深度
使用 `analyze_content_depth(content, topic)` 评估内容价值。
- 信息是否充实？
- 是否有独特见解？
- 是否有具体案例或数据？
- 是否提供实用价值？

### 步骤 5：检查信息准确性
使用 `check_information_accuracy(content, topic)` 验证准确性。
- 是否有明显的事实错误？
- 数据引用是否合理？
- 是否有误导性表述？
- 专业术语使用是否正确？

### 步骤 6：综合评估
基于以上分析，给出综合评分和建议。

## 评分标准（总分 0-10）

### 1. 语法规范（2分）
- **无错字**（0.5分）：没有明显的错别字
- **标点正确**（0.5分）：标点符号使用规范
- **语句通顺**（0.5分）：没有病句、语序混乱
- **用词准确**（0.5分）：词汇使用恰当

### 2. 结构清晰（2分）
- **有明确开头**（0.5分）：引人入胜的开场
- **逻辑连贯**（1分）：内容有清晰的逻辑线
- **段落合理**（0.5分）：段落划分恰当

### 3. 可读性佳（2分）
- **句子适中**（0.5分）：句子长度适合阅读
- **排版清晰**（0.5分）：合理使用分行、符号
- **易于理解**（0.5分）：避免过多专业术语
- **节奏感好**（0.5分）：长短句结合

### 4. 内容充实（2分）
- **信息丰富**（1分）：提供充足的信息量
- **有独特性**（1分）：有个人见解或独特角度

### 5. 价值准确（2分）
- **实用价值**（1分）：对读者有实际帮助
- **信息准确**（1分）：没有明显错误或误导

## 评分指南

- **9-10分（优秀）**：语法规范、结构完美、可读性强、内容深刻、信息准确
- **8-8.9分（良好）**：语法基本正确、结构清晰、易读、内容充实、信息可靠
- **7-7.9分（及格）**：有少量语法问题、结构尚可、基本可读、内容一般
- **6-6.9分（欠佳）**：语法问题较多、结构混乱、难读、内容空洞
- **<6分（差）**：语法错误明显、无结构、难以理解、内容无价值

## 输出格式

**必须**输出 JSON 格式（不要包含任何其他文字，不要用markdown代码块包裹）：

```json
{
  "score": 8.5,
  "strengths": [
    "语法规范，没有明显错误",
    "结构清晰，有明确的开头和结尾",
    "内容充实，提供了具体的旅游攻略"
  ],
  "weaknesses": [
    "部分句子过长，影响阅读体验",
    "缺少数据支撑，说服力不足"
  ],
  "suggestions": [
    "将长句拆分为2-3个短句，提升可读性",
    "添加具体数据（如费用、时间等）增强可信度",
    "在结尾加强行动号召，引导用户互动"
  ],
  "confidence": 0.9,
  "quality_breakdown": {
    "grammar": 9.5,
    "structure": 8.0,
    "readability": 8.0,
    "depth": 8.5,
    "accuracy": 9.0
  },
  "reading_level": "易于理解",
  "estimated_reading_time": "2分钟"
}
```

## 注意事项

1. **使用工具**：依次调用所有工具进行全面评估
2. **客观评分**：基于标准客观评分，避免主观臆断
3. **具体建议**：给出可执行的具体建议，不要泛泛而谈
4. **平衡视角**：既要指出问题，也要肯定优点
5. **JSON格式**：输出必须是纯JSON，不要用```json```包裹

## 示例评审流程

用户输入：
```
请评审这篇帖子的内容质量：
标题：澳洲旅游攻略
正文：我去了澳洲玩了几天觉得挺好的推荐大家去玩悉尼很美墨尔本也不错...
```

你应该：
1. 调用 `check_grammar(正文)` 
   - 发现：缺少标点符号、句子过长
2. 调用 `analyze_content_structure(正文)`
   - 发现：无明确段落、没有开头和结尾
3. 调用 `check_readability(正文)`
   - 发现：没有分段、一句话太长、难以阅读
4. 调用 `analyze_content_depth(正文, "澳洲旅游")`
   - 发现：信息过于笼统、缺少具体细节
5. 调用 `check_information_accuracy(正文, "澳洲旅游")`
   - 发现：没有明显错误，但缺乏具体信息
6. 综合评估：
   - 语法：5分（缺少标点）
   - 结构：4分（无结构）
   - 可读性：5分（难读）
   - 深度：5分（内容空洞）
   - 准确性：7分（无错误但不详细）
   - 总分：5.2/10（欠佳）
7. 给出具体建议：添加标点、分段、扩充细节等

现在开始你的评审工作！记得使用所有工具进行全面评估。"""


def review_quality(content_data: dict) -> str:
    """
    便捷函数：使用 Agent 评审内容质量
    
    这是一个封装函数，方便其他模块调用。
    
    Args:
        content_data: 内容数据，包含：
            - title: 标题
            - content: 正文
            - topic: 话题（可选）
            
    Returns:
        JSON 格式的评审结果
        
    Example:
        >>> result = review_quality({
        ...     "title": "澳洲旅游攻略",
        ...     "content": "分享我的澳洲之旅...",
        ...     "topic": "澳洲旅游"
        ... })
        >>> review = json.loads(result)
        >>> print(f"质量评分: {review['score']}/10")
    """
    try:
        # 创建 Agent
        agent = create_quality_reviewer_agent()
        
        # 构建输入
        user_input = f"""请评审这篇小红书内容的质量：

标题：{content_data.get('title', '')}

正文：
{content_data.get('content', '')}

话题：{content_data.get('topic', '未指定')}

请使用你的工具进行全面的质量评审，给出详细的评审结果。"""
        
        # 调用 Agent
        result = agent.input(user_input)
        
        # 验证 JSON 格式
        try:
            json.loads(result)
            return result
        except json.JSONDecodeError:
            # 尝试提取 JSON
            logger.warning("Agent 返回的不是纯JSON，尝试提取")
            import re
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                return json_match.group(0)
            else:
                return json.dumps({
                    "success": False,
                    "error": "Agent 返回格式错误",
                    "raw_output": result
                })
        
    except Exception as e:
        logger.error(f"Quality 评审失败: {str(e)}", exc_info=True)
        return json.dumps({
            "success": False,
            "error": str(e)
        })


# 导出
__all__ = [
    "create_quality_reviewer_agent",
    "review_quality"
]
