"""
协调Agent - 负责整体流程的协调和管理
使用 LangChain 1.0 框架重构
"""

import logging
from typing import Any, Dict

from langchain.agents import create_agent
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI

from tools.content_analyst import analyze_xiaohongshu
from tools.content_creator import create_content
from tools.image_generator import generate_images_for_content, generate_images_from_draft
from tools.publisher import publish_to_xiaohongshu
from agents.reviewers.engagement_reviewer import review_engagement
from agents.reviewers.quality_reviewer import review_quality
from tools.review_tools_v1 import review_compliance
from config import Config

logger = logging.getLogger(__name__)


def create_coordinator_agent():
    """
    创建主协调Agent (LangChain 1.0版本)
    
    使用LangChain 1.0的create_agent()函数，提供:
    - 更简洁的API
    - 基于LangGraph的持久化执行
    - 流式输出支持
    - Human-in-the-loop功能
    """
    system_prompt = _load_system_prompt()
    
    # 获取配置
    config = Config.AGENT_CONFIGS["coordinator"]
    model_name = config["model"]
    
    logger.info(f"创建 LangChain Coordinator Agent，模型: {model_name}")
    
    # 根据模型选择对应的LLM
    model = _create_model(model_name, config)
    
    # 包装工具函数为 LangChain 工具
    # LangChain 需要显式的工具声明才能让 Agent 调用
    tools = _wrap_tools()
    
    # 使用LangChain 1.0的create_agent创建Agent
    # 这比ConnectOnion更简洁，并且内置了LangGraph的持久化功能
    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt=system_prompt
    )
    
    logger.info("✅ LangChain Coordinator Agent 创建成功")
    return agent


def _wrap_tools():
    """
    将普通 Python 函数包装为 LangChain 工具
    
    关键: LangChain 1.0 需要使用 @tool 装饰器或显式声明工具
    才能让 Agent 识别并调用
    """
    from langchain_core.tools import StructuredTool
    
    # 包装所有工具函数
    tools = [
        StructuredTool.from_function(
            func=analyze_xiaohongshu,
            name="analyze_xiaohongshu",
            description="分析小红书平台上指定关键词的热门内容，提取标题模式、用户需求等"
        ),
        StructuredTool.from_function(
            func=create_content,
            name="create_content",
            description="基于分析结果创作小红书帖子，包含标题、正文、标签和图片建议"
        ),
        StructuredTool.from_function(
            func=generate_images_for_content,
            name="generate_images_for_content",
            description="使用 AI 生成图片（DALL-E 3 或本地模型）"
        ),
        StructuredTool.from_function(
            func=generate_images_from_draft,
            name="generate_images_from_draft",
            description="从草稿使用 AI 生成图片"
        ),
        StructuredTool.from_function(
            func=review_engagement,
            name="review_engagement",
            description="评审内容的吸引力和互动潜力"
        ),
        StructuredTool.from_function(
            func=review_quality,
            name="review_quality",
            description="评审内容的质量（语法、结构、可读性等）"
        ),
        StructuredTool.from_function(
            func=review_compliance,
            name="review_compliance",
            description="检查内容是否符合小红书平台规范"
        ),
        StructuredTool.from_function(
            func=publish_to_xiaohongshu,
            name="publish_to_xiaohongshu",
            description="发布内容到小红书平台"
        )
    ]
    
    logger.info(f"✅ 已包装 {len(tools)} 个工具")
    return tools


def _create_model(model_name: str, config: Dict[str, Any]):
    """
    创建LangChain模型实例
    
    LangChain 1.0提供统一的模型接口，支持:
    - OpenAI (GPT-4, GPT-4o, etc.)
    - Anthropic (Claude系列)
    - 其他第三方兼容平台
    """
    temperature = config.get("temperature", 0.7)
    
    # 检测模型类型并创建相应的ChatModel
    if "claude" in model_name.lower():
        # 使用Anthropic模型
        if Config.ANTHROPIC_API_KEY:
            logger.info(f"使用 Anthropic API: {model_name}")
            return ChatAnthropic(
                model=model_name,
                temperature=temperature,
                anthropic_api_key=Config.ANTHROPIC_API_KEY,
                streaming=config.get("streaming", True)
            )
        elif Config.OPENAI_BASE_URL:
            # 通过第三方平台调用Claude
            logger.info(f"通过第三方平台调用: {model_name}")
            return ChatOpenAI(
                model=model_name,
                temperature=temperature,
                openai_api_key=Config.OPENAI_API_KEY,
                openai_api_base=Config.OPENAI_BASE_URL,
                streaming=config.get("streaming", True)
            )
        else:
            raise ValueError("未配置 ANTHROPIC_API_KEY 或 OPENAI_BASE_URL")
    else:
        # 使用OpenAI或兼容API
        if not Config.OPENAI_API_KEY:
            raise ValueError("未配置 OPENAI_API_KEY")
        
        kwargs = {
            "model": model_name,
            "temperature": temperature,
            "openai_api_key": Config.OPENAI_API_KEY,
            "streaming": config.get("streaming", True)
        }
        
        # 如果配置了自定义base_url，使用它
        if Config.OPENAI_BASE_URL:
            kwargs["openai_api_base"] = Config.OPENAI_BASE_URL
            logger.info(f"使用第三方平台: {Config.OPENAI_BASE_URL}")
        
        return ChatOpenAI(**kwargs)


def _load_system_prompt() -> str:
    """加载系统提示词"""
    prompt_path = Config.PROMPTS_DIR / "coordinator.md"
    
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logger.warning(f"提示词文件不存在: {prompt_path}")
        return _get_default_system_prompt()
    except Exception as e:
        logger.error(f"读取提示词失败: {str(e)}")
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
    主函数 - 用于测试 (LangChain 1.0版本)
    """
    try:
        # 创建 Agent
        print("🚀 正在初始化 LangChain Coordinator Agent...")
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
                
                # 使用LangChain 1.0的invoke方法调用Agent
                # invoke接受messages格式的输入
                print("\n🤖 Coordinator: 正在处理...\n")
                response = coordinator.invoke(
                    {"messages": [{"role": "user", "content": user_input}]}
                )
                
                # 从响应中提取结果
                result = response.get("messages", [])[-1].content if response.get("messages") else str(response)
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
        print("\n💡 安装命令: pip install langchain langchain-openai langchain-anthropic")
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

