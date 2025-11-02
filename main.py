"""
Social Media Agent - Main Entry Point
社交媒体 Agent 系统的主入口

MVP 功能：
- 分析小红书热门内容
- 创作高质量帖子
- 发布到小红书平台
"""

import os
import sys
import argparse
import logging
from typing import Optional, Dict, Any
from pathlib import Path

# 导入配置
from config import (
    ModelConfig, MCPConfig, PathConfig, 
    LogConfig, DevConfig
)

# 导入工具
from utils.mcp_client import XiaohongshuMCPClient
from utils.response_utils import parse_tool_response, is_success, get_response_error

# 配置日志
logger = logging.getLogger(__name__)


def setup_environment() -> Dict[str, Any]:
    """
    初始化环境
    - 加载环境变量
    - 检查必要的配置
    - 初始化输出目录
    
    Returns:
        包含环境检查结果的字典
    """
    results = {
        'success': True,
        'issues': [],
        'warnings': []
    }
    
    print("🔧 正在初始化环境...")
    
    # 1. 检查必要的目录
    try:
        PathConfig.ensure_dirs()
        print("✅ 输出目录已创建")
    except Exception as e:
        results['issues'].append(f"创建目录失败: {str(e)}")
        results['success'] = False
        return results
    
    # 2. 检查 LLM API 配置
    llm_configured = False
    
    if ModelConfig.OPENAI_API_KEY:
        print("✅ OpenAI API Key 已配置")
        llm_configured = True
    else:
        results['warnings'].append("OpenAI API Key 未配置")
    
    if ModelConfig.ANTHROPIC_API_KEY:
        print("✅ Anthropic API Key 已配置")
        llm_configured = True
    else:
        results['warnings'].append("Anthropic API Key 未配置")
    
    # 检查 Ollama
    if ModelConfig.OLLAMA_BASE_URL:
        print(f"✅ Ollama 配置: {ModelConfig.OLLAMA_BASE_URL}")
        llm_configured = True
    
    if not llm_configured:
        results['issues'].append(
            "至少需要配置一个 LLM API（OpenAI、Anthropic 或 Ollama）"
        )
        results['success'] = False
    
    # 3. 检查 MCP 配置
    mcp_url = MCPConfig.SERVERS['xiaohongshu']['url']
    print(f"ℹ️  小红书 MCP 地址: {mcp_url}")
    
    # 4. 显示配置摘要
    if DevConfig.DEBUG:
        print(f"ℹ️  调试模式: 已启用")
    
    if DevConfig.MOCK_MODE:
        print(f"⚠️  Mock 模式: 已启用（不会调用真实 API）")
        results['warnings'].append("Mock 模式已启用")
    
    # 5. 总结
    if results['success']:
        print("✅ 环境初始化完成\n")
    else:
        print("❌ 环境初始化失败\n")
        for issue in results['issues']:
            print(f"  ❌ {issue}")
    
    if results['warnings']:
        print("⚠️  警告:")
        for warning in results['warnings']:
            print(f"  ⚠️  {warning}")
        print()
    
    return results


def validate_mcp_connection() -> bool:
    """
    验证 MCP 服务连接
    
    Returns:
        bool: 连接是否正常
    """
    print("🔌 正在检查小红书 MCP 服务...")
    
    try:
        client = XiaohongshuMCPClient()
        
        # 检查服务健康
        if client.check_health():
            print("✅ MCP 服务连接正常")
            
            # 检查登录状态
            login_status = client.check_login_status()
            if login_status.get('logged_in', False):
                username = login_status.get('username', '未知用户')
                print(f"✅ 已登录小红书账号: {username}")
            else:
                print("⚠️  未登录小红书账号")
                print("💡 提示: 运行 'python xiaohongshu_manager.py login' 进行登录")
            
            return True
        else:
            print("❌ MCP 服务无响应")
            return False
            
    except Exception as e:
        print(f"❌ MCP 连接失败: {str(e)}")
        print("\n💡 解决方案:")
        print("  1. 启动 MCP 服务: python xiaohongshu_manager.py start")
        print(f"  2. 确认服务地址: {MCPConfig.SERVERS['xiaohongshu']['url']}")
        print("  3. 检查防火墙设置")
        return False


def run_interactive_mode():
    """
    交互式模式 - 与用户对话式交互
    """
    # TODO: 实现交互式对话
    print("🤖 社交媒体 Agent 已启动（交互模式）")
    print("请输入你的需求，例如：发表一篇关于澳洲旅游的帖子")
    print("输入 'quit' 退出\n")
    
    # while True:
    #     user_input = input("用户: ")
    #     if user_input.lower() == 'quit':
    #         break
    #     # 调用 coordinator agent
    #     # response = coordinator.input(user_input)
    #     # print(f"Agent: {response}")
    pass


def run_batch_mode(task_file: str):
    """
    批处理模式 - 从文件读取任务列表
    
    Args:
        task_file: 任务文件路径
    """
    # TODO: 实现批处理逻辑
    pass


def run_single_task(task: str, save_draft: bool = True):
    """
    单任务模式 - 执行单个任务
    
    Args:
        task: 任务描述
        save_draft: 是否自动保存草稿
    """
    from agent import create_coordinator_agent
    from utils.draft_manager import get_draft_manager
    import json
    
    print("\n" + "=" * 60)
    print(f"📋 任务: {task}")
    print("=" * 60 + "\n")
    
    try:
        # 创建 Coordinator Agent
        print("🚀 正在初始化 Coordinator Agent...")
        coordinator = create_coordinator_agent()
        print("✅ Agent 已就绪\n")
        
        # 执行任务
        print("🤖 Coordinator: 正在处理任务...\n")
        result = coordinator.input(task)
        
        # 显示结果
        print("\n" + "=" * 60)
        print("📝 执行结果")
        print("=" * 60)
        print(result)
        print("=" * 60 + "\n")
        
        # 尝试解析和保存草稿（如果结果包含内容数据）
        if save_draft:
            try:
                # 尝试从结果中提取内容数据
                # 注意：这里假设 result 可能包含 JSON 数据
                if '{' in result and '}' in result:
                    # 提取 JSON 部分
                    import re
                    json_match = re.search(r'\{.*\}', result, re.DOTALL)
                    if json_match:
                        content_data = json.loads(json_match.group())
                        
                        # 如果包含内容字段，保存草稿
                        if 'title' in content_data or 'content' in content_data:
                            manager = get_draft_manager()
                            draft_id = manager.save_draft(
                                content_data=content_data,
                                topic=task,
                                metadata={'mode': 'single_task'}
                            )
                            print(f"✅ 草稿已保存: {draft_id}")
                            print(f"📁 保存路径: {PathConfig.DRAFTS_DIR / f'{draft_id}.json'}\n")
            except Exception as e:
                logger.debug(f"保存草稿失败（非关键错误）: {str(e)}")
        
        print("✅ 任务完成！\n")
        return True
        
    except ImportError as e:
        print(f"❌ 导入错误: {str(e)}")
        print("💡 请确保已安装 ConnectOnion: pip install connectonion")
        return False
        
    except Exception as e:
        print(f"❌ 任务执行失败: {str(e)}")
        logger.error(f"单任务执行失败: {str(e)}", exc_info=True)
        return False


def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(
        description="社交媒体 Multi-Agent 系统 - MVP v0.2",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 检查环境配置
  python main.py --check
  
  # 单任务模式
  python main.py --mode single --task "发表一篇关于澳洲旅游的帖子"
  
  # 交互式模式（默认）
  python main.py
  
  # 跳过 MCP 连接检查（仅测试分析和创作）
  python main.py --skip-mcp-check
        """
    )
    
    parser.add_argument(
        "--mode",
        choices=["interactive", "single", "batch"],
        default="interactive",
        help="运行模式：interactive（交互）/ single（单任务）/ batch（批处理）"
    )
    
    parser.add_argument(
        "--task",
        type=str,
        help="单任务模式下的任务描述"
    )
    
    parser.add_argument(
        "--task-file",
        type=str,
        help="批处理模式下的任务文件路径"
    )
    
    parser.add_argument(
        "--check",
        action="store_true",
        help="仅检查环境和配置，不执行任务"
    )
    
    parser.add_argument(
        "--skip-mcp-check",
        action="store_true",
        help="跳过 MCP 连接检查（用于测试分析和创作功能）"
    )
    
    parser.add_argument(
        "--no-save-draft",
        action="store_true",
        help="不自动保存草稿"
    )
    
    args = parser.parse_args()
    
    # 配置日志系统（使用新的日志管理器）
    from utils.logger_config import setup_logging
    log_level = 'DEBUG' if DevConfig.DEBUG else LogConfig.LEVEL
    setup_logging(
        level=log_level,
        console_enabled=LogConfig.CONSOLE_ENABLED,
        file_enabled=LogConfig.FILE_ENABLED,
        colorize=LogConfig.CONSOLE_COLORIZE
    )
    
    print("\n" + "=" * 60)
    print("🤖 社交媒体 Multi-Agent 系统 - MVP v0.2")
    print("=" * 60 + "\n")
    
    # 初始化环境
    env_result = setup_environment()
    
    if not env_result['success']:
        print("\n❌ 环境初始化失败，无法继续")
        sys.exit(1)
    
    # 检查 MCP 连接（可选）
    if not args.skip_mcp_check:
        mcp_ok = validate_mcp_connection()
        if not mcp_ok:
            print("\n⚠️  MCP 服务未连接")
            print("💡 提示: 如果只想测试分析和创作功能，可以添加 --skip-mcp-check 参数")
            
            # 询问是否继续
            if args.mode == "interactive":
                user_input = input("\n是否继续（不能发布到小红书）？[y/N]: ").strip().lower()
                if user_input not in ['y', 'yes']:
                    print("👋 再见！")
                    sys.exit(0)
            else:
                print("❌ 在非交互模式下，MCP 服务是必需的")
                sys.exit(1)
    else:
        print("⏭️  已跳过 MCP 连接检查\n")
    
    print("✅ 初始化完成\n")
    
    # 仅检查模式
    if args.check:
        print("✅ 所有检查通过，系统可以正常运行")
        return
    
    # 根据模式运行
    try:
    if args.mode == "interactive":
        run_interactive_mode()
    elif args.mode == "single":
        if not args.task:
            print("❌ 单任务模式需要提供 --task 参数")
                print("💡 示例: python main.py --mode single --task '发表一篇关于澳洲旅游的帖子'")
            sys.exit(1)
            
            save_draft = not args.no_save_draft
            success = run_single_task(args.task, save_draft=save_draft)
            sys.exit(0 if success else 1)
            
    elif args.mode == "batch":
        if not args.task_file:
            print("❌ 批处理模式需要提供 --task-file 参数")
            sys.exit(1)
        run_batch_mode(args.task_file)
            
    except KeyboardInterrupt:
        print("\n\n👋 用户中断，再见！")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        logger.error(f"主程序错误: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

