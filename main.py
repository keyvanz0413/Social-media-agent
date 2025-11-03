"""
Social Media Agent - Main Entry Point
社交媒体 Agent 系统的主入口

核心功能：
- 交互式对话模式
- 单任务执行模式
"""

import sys
import argparse
import logging
from typing import Dict, Any

# 导入配置
from config import ModelConfig, PathConfig, LogConfig, DevConfig

# 导入工具
from utils.mcp_client import XiaohongshuMCPClient

# 配置日志
logger = logging.getLogger(__name__)


def validate_mcp_connection() -> bool:
    """
    验证 MCP 服务连接
    
    Returns:
        bool: 连接是否正常
    """
    try:
        client = XiaohongshuMCPClient()
        
        if client.check_health():
            login_status = client.check_login_status()
            if not login_status.get('logged_in', False):
                print("⚠️  未登录小红书账号（运行 'python xiaohongshu_manager.py login'）")
            return True
        else:
            print("❌ MCP 服务无响应")
            return False
            
    except Exception as e:
        print(f"❌ MCP 连接失败: {str(e)}")
        print("💡 启动 MCP: python xiaohongshu_manager.py start")
        return False


def run_interactive_mode():
    """
    交互式模式 - 与用户对话式交互
    """
    from agent import create_coordinator_agent
    
    # 创建 Agent
    try:
        import warnings
        warnings.filterwarnings('ignore', category=UserWarning, module='connectonion')
        coordinator = create_coordinator_agent()
        warnings.filterwarnings('default')
    except ImportError:
        print("❌ ConnectOnion 未安装: pip install connectonion")
        return
    except Exception as e:
        print(f"❌ 初始化失败: {str(e)}")
        logger.error(f"创建 Agent 失败: {str(e)}", exc_info=True)
        return
    
    # 显示帮助信息
    print_help()
    
    # 交互循环
    while True:
        try:
            user_input = input("\n👤 你: ").strip()
            
            # 处理退出命令
            if user_input.lower() in ['exit', 'quit', '退出', 'q']:
                print("\n👋 再见！")
                break
            
            # 处理空输入
            if not user_input:
                continue
            
            # 处理帮助命令
            if user_input.lower() in ['help', '帮助', 'h']:
                print_help()
                continue
            
            # 清屏命令
            if user_input.lower() in ['clear', '清屏', 'cls']:
                import os
                os.system('clear' if os.name != 'nt' else 'cls')
                continue
            
            # 调用 Agent 处理请求
            print("\n🤖 Coordinator: 正在处理...\n")
            result = coordinator.input(user_input)
            
            # 显示结果
            print(f"\n🤖 Coordinator: {result}\n")
            print("-" * 70)
            
        except KeyboardInterrupt:
            print("\n\n👋 再见！")
            break
        except Exception as e:
            print(f"\n❌ 错误: {str(e)}\n")
            logger.error(f"处理用户输入时出错: {str(e)}", exc_info=True)
            print("💡 提示: 你可以继续输入其他请求，或输入 'help' 查看帮助")


def print_help():
    """显示帮助信息"""
    print("""
============================================================
💡 使用示例：
   • 发表一篇关于澳洲旅游的帖子
   • 写一篇北海道攻略，参考10篇爆款帖子
   • 创作美食内容，只看3篇就好

📌 可自定义参考帖子数量（默认5篇，建议3-10篇）

💡 输入 'exit' 或 'quit' 退出
============================================================
    """)


def run_single_task(task: str):
    """
    单任务模式 - 执行单个任务
    
    Args:
        task: 任务描述
    """
    from agent import create_coordinator_agent
    
    print(f"\n📋 任务: {task}\n")
    
    try:
        # 创建 Agent
        import warnings
        warnings.filterwarnings('ignore', category=UserWarning, module='connectonion')
        coordinator = create_coordinator_agent()
        warnings.filterwarnings('default')
        
        # 执行任务
        print("🤖 正在处理...\n")
        result = coordinator.input(task)
        
        # 显示结果
        print("\n📝 结果:")
        print(result)
        print()
        print("✅ 完成\n")
        return True
        
    except ImportError:
        print("❌ ConnectOnion 未安装: pip install connectonion")
        return False
        
    except Exception as e:
        print(f"❌ 任务执行失败: {str(e)}")
        logger.error(f"单任务执行失败: {str(e)}", exc_info=True)
        return False


def check_environment() -> Dict[str, Any]:
    """
    简化的环境检查
    
    Returns:
        检查结果字典
    """
    issues = []
    
    # 检查必要的目录
    try:
        PathConfig.ensure_dirs()
    except Exception as e:
        issues.append(f"创建目录失败: {str(e)}")
    
    # 检查 API 配置
    if not ModelConfig.OPENAI_API_KEY and not ModelConfig.ANTHROPIC_API_KEY:
        issues.append("未配置 API Key（需要 OPENAI_API_KEY 或 ANTHROPIC_API_KEY）")
    
    return {
        'success': len(issues) == 0,
        'issues': issues
    }


def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(
        description="社交媒体 Multi-Agent 系统 v1.1",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 交互式模式（默认）
  python main.py
  
  # 单任务模式
  python main.py --task "发表一篇关于澳洲旅游的帖子"
  
  # 检查系统配置
  python main.py --check
  
  # 跳过 MCP 连接检查
  python main.py --skip-mcp-check
        """
    )
    
    parser.add_argument(
        "--task",
        type=str,
        help="单任务模式：执行单个任务"
    )
    
    parser.add_argument(
        "--check",
        action="store_true",
        help="检查环境和配置"
    )
    
    parser.add_argument(
        "--skip-mcp-check",
        action="store_true",
        help="跳过 MCP 连接检查"
    )
    
    args = parser.parse_args()
    
    # 配置日志系统
    from utils.logger_config import setup_logging
    log_level = 'DEBUG' if DevConfig.DEBUG else LogConfig.LOG_LEVEL
    setup_logging(
        level=log_level,
        console_enabled=LogConfig.LOG_CONSOLE_ENABLED,
        file_enabled=LogConfig.LOG_FILE_ENABLED,
        colorize=LogConfig.LOG_CONSOLE_COLORIZE
    )
    
    # 环境检查
    env_result = check_environment()
    if not env_result['success']:
        print("\n❌ 环境初始化失败:")
        for issue in env_result['issues']:
            print(f"  • {issue}")
        print()
        sys.exit(1)
    
    # 仅检查模式
    if args.check:
        print("\n" + "=" * 70)
        print("🔍 系统配置检查")
        print("=" * 70 + "\n")
        
        print("📋 配置信息:")
        print(f"  - OpenAI API: {'✅ 已配置' if ModelConfig.OPENAI_API_KEY else '❌ 未配置'}")
        print(f"  - Anthropic API: {'✅ 已配置' if ModelConfig.ANTHROPIC_API_KEY else '❌ 未配置'}")
        print(f"  - 日志级别: {ModelConfig.LOG_LEVEL}")
        print(f"  - 调试模式: {'开启' if ModelConfig.DEBUG else '关闭'}")
        print()
        
        if not args.skip_mcp_check:
            print("🔌 MCP服务检查:")
            if validate_mcp_connection():
                print("  ✅ MCP服务正常\n")
            else:
                print("  ❌ MCP服务未连接\n")
        
        print("=" * 70)
        print("\n✅ 系统检查完成\n")
        return
    
    # MCP 连接检查（可选）
    if not args.skip_mcp_check:
        mcp_ok = validate_mcp_connection()
        if not mcp_ok:
            print("\n⚠️  MCP 服务未连接（可添加 --skip-mcp-check 跳过）")
            if args.task:
                # 单任务模式，MCP 必需
                print("❌ 单任务模式需要 MCP 服务")
                sys.exit(1)
            else:
                # 交互模式，询问用户
                try:
                    user_input = input("是否继续（不能发布到小红书）？[y/N]: ").strip().lower()
                    if user_input not in ['y', 'yes']:
                        print("👋 再见！")
                        sys.exit(0)
                except (EOFError, KeyboardInterrupt):
                    print("\n👋 再见！")
                    sys.exit(0)
    
    # 运行模式
    try:
        if args.task:
            # 单任务模式
            success = run_single_task(args.task)
            sys.exit(0 if success else 1)
        else:
            # 交互式模式（默认）
            run_interactive_mode()
            
    except KeyboardInterrupt:
        print("\n\n👋 用户中断，再见！")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        logger.error(f"主程序错误: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
