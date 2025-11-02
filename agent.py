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

# 导入子 Agent
from sub_agents.content_analyst import agent_a_analyze_xiaohongshu
from sub_agents.content_creator import agent_c_create_content
from sub_agents.publisher import publish_to_xiaohongshu

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
        publish_to_xiaohongshu
    ]
    
    # 3. 获取配置
    coordinator_config = AgentConfig.COORDINATOR
    model_name = coordinator_config.get("model", "gpt-4o")
    max_iterations = coordinator_config.get("max_iterations", 30)
    temperature = coordinator_config.get("temperature", 0.7)
    
    # 4. 创建 Agent 实例
    logger.info(f"创建 Coordinator Agent，模型: {model_name}")
    
    agent = Agent(
        name=coordinator_config.get("name", "social_media_coordinator"),
        system_prompt=system_prompt,
        tools=tools,
        max_iterations=max_iterations,
        model=model_name,
        temperature=temperature
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
- `agent_a_analyze_xiaohongshu(keyword: str, limit: int = 5)`: 分析小红书热门内容
  - 返回 JSON 字符串，包含标题模式、用户需求、创作建议等
  
- `agent_c_create_content(analysis_result: str, topic: str, style: str = "casual")`: 创作小红书帖子
  - 参数：analysis_result（JSON字符串）、topic（主题）、style（风格：casual/professional/storytelling）
  - 返回 JSON 字符串，包含标题、正文、标签等
  
- `publish_to_xiaohongshu(title: str, content: str, images: List[str] = None, video_path: str = None, tags: List[str] = None)`: 发布内容到小红书
  - 参数：title（标题）、content（正文）、images（图片路径列表）、video_path（视频路径）、tags（标签列表）
  - 返回 JSON 字符串，包含发布结果

## 工作流程（MVP 版本）

### 标准流程
```
用户需求 → 内容分析 → 内容创作 → 发布
```

### 执行步骤
1. 使用 `agent_a_analyze_xiaohongshu` 分析相关话题的热门内容
2. 解析分析结果 JSON，提取有用信息
3. 使用 `agent_c_create_content` 基于分析结果创作内容
   - 将分析结果的 JSON 字符串直接传递给 `analysis_result` 参数
4. 解析创作结果 JSON，提取标题、正文、标签、图片建议等
5. 使用 `publish_to_xiaohongshu` 发布最终内容
   - 从创作结果中提取标题、正文、标签
   - 如果有图片建议，可以提示用户准备图片

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
4. 解析结果，告诉用户创作的内容标题和摘要
5. 调用 `publish_to_xiaohongshu(标题, 正文, 图片列表, 标签列表)`
6. 告知用户发布结果"""


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

