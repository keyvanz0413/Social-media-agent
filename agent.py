"""
Main Coordinator Agent
主协调 Agent - 负责整体流程的协调和管理
"""

import logging
from pathlib import Path

try:
    from connectonion import Agent
except ImportError:
    Agent = None
    logging.warning("ConnectOnion 未安装，无法使用 Coordinator Agent")

# 导入工具函数
from tools.content_analyst import agent_a_analyze_xiaohongshu
from tools.content_creator import agent_c_create_content
from tools.image_generator import generate_images_for_content, generate_images_from_draft
from tools.publisher import publish_to_xiaohongshu

# 导入配置
from config import AgentConfig, PathConfig, ModelConfig

# 配置日志
logger = logging.getLogger(__name__)


def create_coordinator_agent():
    """
    创建主协调 Agent
    
    Returns:
        配置好的 Agent 实例
        
    Example:
        >>> agent = create_coordinator_agent()
        >>> result = agent.input("发表一篇关于澳洲旅游的帖子")
        >>> print(result)
    """
    if Agent is None:
        raise ImportError(
            "ConnectOnion 框架未安装。请运行: pip install connectonion"
        )
    
    # 1. 加载系统提示词
    system_prompt = _load_system_prompt()
    
    # 2. 注册所有工具函数
    tools = [
        agent_a_analyze_xiaohongshu,
        agent_c_create_content,
        generate_images_for_content,
        generate_images_from_draft,
        publish_to_xiaohongshu
    ]
    
    # 3. 获取配置
    coordinator_config = AgentConfig.COORDINATOR
    model_name = coordinator_config.get("model", "gpt-4o")
    max_iterations = coordinator_config.get("max_iterations", 30)
    
    # 4. 创建 Agent 实例
    logger.info(f"创建 Coordinator Agent，模型: {model_name}")
    
    agent = Agent(
        name=coordinator_config.get("name", "social_media_coordinator"),
        system_prompt=system_prompt,
        tools=tools,
        max_iterations=max_iterations,
        model=model_name
    )
    
    logger.info("Coordinator Agent 创建成功")
    return agent


def _load_system_prompt() -> str:
    """
    加载系统提示词
    
    Returns:
        系统提示词内容
    """
    prompt_path = PathConfig.PROMPTS_DIR / "coordinator.md"
    
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logger.warning(f"提示词文件不存在: {prompt_path}，使用默认提示词")
        return _get_default_system_prompt()
    except Exception as e:
        logger.error(f"读取提示词文件失败: {str(e)}，使用默认提示词")
        return _get_default_system_prompt()


def _get_default_system_prompt() -> str:
    """获取默认系统提示词"""
    return """你是一个智能社交媒体内容创作协调者，负责管理和调度多个专业 Agent 来完成小红书内容的创作和发布任务。

## 核心职责
1. **理解用户意图**：准确理解用户的创作需求和目标
2. **制定执行计划**：决定调用哪些工具、按什么顺序调用
3. **协调 Agent 工作**：管理内容分析、创作、发布等环节
4. **质量控制**：确保最终内容符合小红书平台规范和用户预期

## 可用工具
- `agent_a_analyze_xiaohongshu(keyword: str, limit: int = 5, quality_level: str = "balanced")`: 分析小红书热门内容
  - 返回 JSON 字符串，包含标题模式、用户需求、创作建议等
  
- `agent_c_create_content(analysis_result: str, topic: str, style: str = "casual", quality_level: str = "balanced")`: 创作小红书帖子
  - 参数：analysis_result（JSON字符串）、topic（主题）、style（风格：casual/professional/storytelling）
  - 返回 JSON 字符串，包含标题、正文、标签、**image_suggestions**（图片建议列表）等
  
- `generate_images_for_content(image_suggestions: str, topic: str, count: int = None, method: str = "dalle")`: 使用 AI 生成图片
  - 参数：image_suggestions（图片建议JSON字符串）、topic（主题）、count（数量）、method（方法：dalle/local）
  - 返回 JSON 字符串，包含生成的图片路径列表
  - **重要**：method="dalle" 是推荐方法，使用 DALL-E 3 AI 生成高质量图片
  - **注意**：需要配置 OPENAI_API_KEY
  
- `generate_images_from_draft(draft_id: str, method: str = "dalle", count: int = None)`: 从草稿使用 AI 生成图片
  - 参数：draft_id（草稿ID，从创作结果的metadata中获取）、method（生成方法：dalle/local）
  - 返回 JSON 字符串，包含生成的图片路径列表
  
- `publish_to_xiaohongshu(title: str, content: str, images: List[str] = None, video_path: str = None, tags: List[str] = None)`: 发布内容到小红书
  - 参数：title（标题）、content（正文）、**images（图片路径列表，必需）**、video_path（视频路径）、tags（标签列表）
  - 返回 JSON 字符串，包含发布结果
  - **注意**：必须提供 images 或 video_path，至少一个

## 工作流程（完整版本）

### 标准流程
```
用户需求 → 内容分析 → 内容创作 → 图片生成 → 发布
```

### 执行步骤
1. 使用 `agent_a_analyze_xiaohongshu` 分析相关话题的热门内容
2. 解析分析结果 JSON，提取有用信息
3. 使用 `agent_c_create_content` 基于分析结果创作内容
   - 将分析结果的 JSON 字符串直接传递给 `analysis_result` 参数
   - 返回结果包含 **image_suggestions**（图片建议列表）和 **draft_id**
4. 使用 `generate_images_from_draft` 或 `generate_images_for_content` 使用 AI 生成图片
   - 推荐使用 draft_id 调用 `generate_images_from_draft`，这样会自动读取图片建议
   - 或者从创作结果中提取 image_suggestions，调用 `generate_images_for_content`
   - 推荐使用 method="dalle"（DALL-E 3 AI 生成，高质量且完全可控）
   - 需要确保 OPENAI_API_KEY 已配置
5. 解析图片生成结果，提取图片路径列表
6. 使用 `publish_to_xiaohongshu` 发布最终内容
   - 从创作结果中提取标题、正文、标签
   - 从图片生成结果中提取图片路径列表
   - **必须提供图片路径**，否则发布会失败

## 注意事项
- **工具函数返回的都是 JSON 格式字符串**，需要解析后使用
- **数据传递**：将上一个工具的 JSON 结果直接作为下一个工具的字符串参数传递
- **错误处理**：如果某个步骤失败，向用户说明情况并询问如何处理
- **发布确认**：发布前务必确认内容质量符合要求（可选，MVP 可以自动发布）
- **保持沟通**：及时反馈进度，告知用户当前执行到哪个步骤

## 输出格式
- 使用清晰的中文与用户交流
- 展示关键步骤的结果（如分析发现的标题模式、创作的内容摘要）
- 最终给出发布结果（成功时显示笔记ID或链接，失败时说明原因）

## 示例对话

用户："发表一篇关于澳洲旅游的帖子"

你应该：
1. 调用 `agent_a_analyze_xiaohongshu("澳洲旅游", limit=5)`
2. 解析结果，告诉用户发现了哪些标题模式和用户需求
3. 调用 `agent_c_create_content(分析结果JSON, "澳洲旅游", "casual")`
4. 解析创作结果，提取 draft_id、标题、正文等
5. 调用 `generate_images_from_draft(draft_id, method="dalle")` 使用 AI 生成图片
   - 或者提取 image_suggestions，调用 `generate_images_for_content(image_suggestions, "澳洲旅游", method="dalle")`
6. 解析图片生成结果，提取图片路径列表（images字段中每个元素的path字段）
7. 调用 `publish_to_xiaohongshu(标题, 正文, images=图片路径列表, tags=标签列表)`
8. 告知用户发布结果（成功或失败原因）

## 图片生成方法选择
- **dalle**（推荐）：DALL-E 3 AI 生成，高质量、完全可控、创意无限
  - 需要 OPENAI_API_KEY
  - 费用：约 $0.04/张（standard）或 $0.08/张（hd）
  - 适合所有场景，特别是需要创意或特定场景的图片
- **local**：本地 Stable Diffusion，完全免费但需要本地部署
  - 需要本地部署 SD WebUI
  - 需要较强的 GPU
  - 适合高频使用、预算有限的场景

**注意**：Unsplash 和 Pexels 已经集成在 MCP 中，如需搜索图库，请使用 MCP 的相关工具。

默认使用 DALL-E 3 生成，提供最佳质量和灵活性。"""


def main():
    """
    主函数 - 用于测试
    """
    try:
        # 创建 Agent
        print("🚀 正在初始化 Coordinator Agent...")
        coordinator = create_coordinator_agent()
        print("✅ Coordinator Agent 已就绪！\n")
        
        # 交互循环
        print("=" * 60)
        print("💡 提示：输入你的需求，例如 '发表一篇关于澳洲旅游的帖子'")
        print("💡 输入 'exit' 或 'quit' 退出\n")
        print("=" * 60 + "\n")
        
        while True:
            try:
                user_input = input("👤 你: ").strip()
                
                if user_input.lower() in ['exit', 'quit', '退出', 'q']:
                    print("\n👋 再见！")
                    break
                
                if not user_input:
                    continue
                
                # 调用 Agent
                print("\n🤖 Coordinator: 正在处理...\n")
                result = coordinator.input(user_input)
                print(f"\n🤖 Coordinator: {result}\n")
                print("-" * 60 + "\n")
                
            except KeyboardInterrupt:
                print("\n\n👋 再见！")
                break
            except Exception as e:
                print(f"\n❌ 错误: {str(e)}\n")
                logger.error(f"处理用户输入时出错: {str(e)}", exc_info=True)
                
    except ImportError as e:
        print(f"❌ {str(e)}")
        print("\n💡 安装命令: pip install connectonion")
    except Exception as e:
        print(f"❌ 初始化失败: {str(e)}")
        logger.error(f"初始化 Coordinator Agent 失败: {str(e)}", exc_info=True)


if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    main()

