"""
协调Agent - 负责整体流程的协调和管理
"""

import logging
from typing import Any, Dict

from langchain.agents import create_agent
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI

from social_media_agent.config import Config
from social_media_agent.tools.langchain_tools import get_structured_tools

logger = logging.getLogger(__name__)


def create_coordinator_agent():
    """
    创建主协调 Agent。
    """
    system_prompt = _load_system_prompt()
    
    # 获取配置
    config = Config.AGENT_CONFIGS["coordinator"]
    model_name = config["model"]
    
    logger.info(f"创建 LangChain Coordinator Agent，模型: {model_name}")
    
    # 根据模型选择对应的LLM
    model = _create_model(model_name, config)
    
    # 组装可调用工具列表
    tools = _wrap_tools()
    
    # 创建协调 Agent
    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt=system_prompt
    )
    
    logger.info("✅ LangChain Coordinator Agent 创建成功")
    return agent


def _wrap_tools():
    """
    获取工具列表（含显式参数 schema）。
    """
    tools = get_structured_tools()
    logger.info(f"✅ 已包装 {len(tools)} 个工具")
    return tools


def _create_model(model_name: str, config: Dict[str, Any]):
    """
    创建LangChain模型实例
    
    支持:
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
    return """你是社交媒体内容协调Agent，负责按需调用工具完成分析、创作、评审、排期、记忆与发布。

可用工具（名称必须精确）：
- analyze_xiaohongshu(keyword, limit=5, quality_level="balanced")
- create_content(analysis_result, topic, style="casual", quality_level="balanced")
- generate_images_from_draft(draft_id, method="dalle", count=None)
- generate_images_for_content(image_suggestions, topic, count=None, method="dalle")
- review_engagement(content_data)
- review_quality(content_data)
- review_compliance(content_data)
- publish_to_xiaohongshu(title, content, images=None, video_path=None, tags=None)
- save_memory(item_type, content, metadata=None, source="agent")
- search_memory(query, top_k=5, item_type=None)
- list_recent_memories(limit=20, item_type=None)
- create_schedule(topic, days=7, frequency="daily", start_date=None, preferred_time="20:00", platform="xiaohongshu")
- list_schedule(date_from=None, date_to=None, status=None, limit=50)
- reschedule(item_id, new_time)

执行原则：
1) 用户要“排期/日历/计划发布”时，优先用排期工具。
2) 用户要内容创作时，按 分析 -> 创作 -> 评审 ->（可选）发布。
3) 关键偏好与复盘结论写入记忆；新任务可先检索记忆再创作。
4) 工具返回为结构化结果（dict）；失败时读取 success/error 字段并重试或降级。
5) 全程中文输出，简洁说明进展、结果和失败原因。"""


def main():
    """
    主函数 - 用于本地测试
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
                
                # invoke 接受 messages 格式输入
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
