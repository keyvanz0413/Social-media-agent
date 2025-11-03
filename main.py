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
    
    # 1. 检查必要的目录（静默）
    try:
        PathConfig.ensure_dirs()
    except Exception as e:
        results['issues'].append(f"创建目录失败: {str(e)}")
        results['success'] = False
        return results
    
    # 2. 检查 LLM API 配置（静默）
    llm_configured = False
    
    if ModelConfig.OPENAI_API_KEY:
        llm_configured = True
    else:
        results['warnings'].append("OpenAI API Key 未配置")
    
    if ModelConfig.ANTHROPIC_API_KEY:
        llm_configured = True
    else:
        results['warnings'].append("Anthropic API Key 未配置")
    
    # 检查 Ollama
    if ModelConfig.OLLAMA_BASE_URL:
        llm_configured = True
    
    if not llm_configured:
        results['issues'].append(
            "至少需要配置一个 LLM API（OpenAI、Anthropic 或 Ollama）"
        )
        results['success'] = False
    
    # 3. 检查 MCP 配置（静默）
    
    # 4. 显示配置摘要（仅在有问题时显示）
    if DevConfig.MOCK_MODE:
        results['warnings'].append("Mock 模式已启用")
    
    # 5. 总结（仅在失败时显示详细信息）
    if not results['success']:
        print("❌ 环境初始化失败\n")
        for issue in results['issues']:
            print(f"  ❌ {issue}")
        print()
    
    if results['warnings'] and (DevConfig.DEBUG or not results['success']):
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
    try:
        client = XiaohongshuMCPClient()
        
        # 检查服务健康
        if client.check_health():
            # 检查登录状态（静默）
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
    提供完整的交互体验，包括草稿管理、历史记录等
    """
    from agent import create_coordinator_agent
    from utils.draft_manager import get_draft_manager
    
    # 创建 Agent
    try:
        # 临时禁用警告（避免显示大量提示词内容）
        import warnings
        warnings.filterwarnings('ignore', category=UserWarning, module='connectonion')
        
        coordinator = create_coordinator_agent()
        
        # 恢复警告
        warnings.filterwarnings('default')
    except ImportError as e:
        print(f"❌ ConnectOnion 未安装: pip install connectonion")
        return
    except Exception as e:
        print(f"❌ 初始化失败: {str(e)}")
        logger.error(f"创建 Agent 失败: {str(e)}", exc_info=True)
        return
    
    # 显示简洁的启动信息
    print_help()
    
    # 获取草稿管理器
    draft_manager = get_draft_manager()
    
    # 交互循环
    while True:
        try:
            # 读取用户输入
            user_input = input("\n👤 你: ").strip()
            
            # 处理退出命令
            if user_input.lower() in ['exit', 'quit', '退出', 'q']:
                print("\n👋 再见！")
                break
            
            # 处理空输入
            if not user_input:
                continue
            
            # 处理特殊命令
            if user_input.lower() in ['help', '帮助', 'h']:
                print_help()
                continue
            
            if user_input.lower() in ['drafts', '草稿', 'd']:
                show_drafts(draft_manager)
                continue
            
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


def show_drafts(draft_manager, limit: int = 5):
    """显示最近的草稿"""
    print("\n" + "=" * 70)
    print(f"📝 最近的草稿（最多显示 {limit} 个）")
    print("=" * 70 + "\n")
    
    try:
        drafts = draft_manager.list_drafts(limit=limit)
        
        if not drafts:
            print("暂无草稿")
            return
        
        for i, draft in enumerate(drafts, 1):
            content = draft.get('content', {})
            title = content.get('title', '无标题')
            topic = draft.get('topic', '未知主题')
            draft_id = draft.get('draft_id', '未知ID')
            created_at = draft.get('created_at', '')
            
            # 格式化时间
            if created_at:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(created_at)
                    created_at = dt.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    pass
            
            print(f"{i}. [{topic}] {title}")
            print(f"   ID: {draft_id}")
            print(f"   时间: {created_at}")
            print()
        
        print(f"💾 草稿目录: {PathConfig.DRAFTS_DIR}")
        print("-" * 70)
        
    except Exception as e:
        print(f"❌ 加载草稿失败: {str(e)}")
        logger.error(f"显示草稿列表失败: {str(e)}", exc_info=True)


def run_batch_mode(task_file: str):
    """
    批处理模式 - 从文件读取任务列表
    
    支持的文件格式：
    - JSON: [{"task": "...", "priority": 1}, ...]
    - TXT: 每行一个任务
    
    Args:
        task_file: 任务文件路径
    """
    from agent import create_coordinator_agent
    from utils.draft_manager import get_draft_manager
    from datetime import datetime
    import json
    from pathlib import Path
    
    print(f"\n📋 批处理模式")
    print(f"任务文件: {task_file}\n")
    
    # 1. 读取任务列表
    try:
        tasks = _load_tasks_from_file(task_file)
        print(f"✅ 成功加载 {len(tasks)} 个任务\n")
    except Exception as e:
        print(f"❌ 加载任务文件失败: {str(e)}")
        return False
    
    if not tasks:
        print("❌ 任务列表为空")
        return False
    
    # 2. 创建 Coordinator Agent
    try:
        import warnings
        warnings.filterwarnings('ignore', category=UserWarning, module='connectonion')
        coordinator = create_coordinator_agent()
        warnings.filterwarnings('default')
    except Exception as e:
        print(f"❌ 初始化 Agent 失败: {str(e)}")
        return False
    
    # 3. 执行批处理
    print("=" * 70)
    print("开始批处理执行...")
    print("=" * 70 + "\n")
    
    results = []
    success_count = 0
    failed_count = 0
    
    # 使用进度条
    try:
        from tqdm import tqdm
        use_tqdm = True
    except ImportError:
        use_tqdm = False
        print("💡 安装 tqdm 可显示进度条: pip install tqdm\n")
    
    task_iterator = tqdm(tasks, desc="处理进度") if use_tqdm else tasks
    
    for i, task_info in enumerate(task_iterator, 1):
        task = task_info.get('task') if isinstance(task_info, dict) else task_info
        
        if not use_tqdm:
            print(f"\n[{i}/{len(tasks)}] 任务: {task[:50]}...")
        
        try:
            # 执行任务
            result = coordinator.input(task)
            
            # 记录结果
            results.append({
                "index": i,
                "task": task,
                "status": "success",
                "result": result,
                "timestamp": datetime.now().isoformat()
            })
            
            success_count += 1
            
            if not use_tqdm:
                print(f"  ✅ 成功")
        
        except KeyboardInterrupt:
            print("\n\n⚠️  用户中断批处理")
            break
        
        except Exception as e:
            # 记录错误
            results.append({
                "index": i,
                "task": task,
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            
            failed_count += 1
            
            if not use_tqdm:
                print(f"  ❌ 失败: {str(e)}")
            
            logger.error(f"任务 {i} 执行失败: {str(e)}", exc_info=True)
    
    # 4. 生成报告
    print("\n" + "=" * 70)
    print("批处理完成")
    print("=" * 70)
    print(f"\n📊 执行统计:")
    print(f"  总任务数: {len(tasks)}")
    print(f"  ✅ 成功: {success_count}")
    print(f"  ❌ 失败: {failed_count}")
    print(f"  成功率: {success_count/len(tasks)*100:.1f}%\n")
    
    # 5. 保存报告
    try:
        report_path = _save_batch_report(results, task_file)
        print(f"📄 详细报告已保存: {report_path}\n")
    except Exception as e:
        print(f"⚠️  保存报告失败: {str(e)}\n")
    
    return success_count > 0


def _load_tasks_from_file(task_file: str) -> list:
    """
    从文件加载任务列表
    
    Args:
        task_file: 任务文件路径
    
    Returns:
        任务列表
    """
    import json
    from pathlib import Path
    
    file_path = Path(task_file)
    
    if not file_path.exists():
        raise FileNotFoundError(f"任务文件不存在: {task_file}")
    
    # 根据文件扩展名判断格式
    if file_path.suffix.lower() == '.json':
        # JSON格式
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 支持两种格式
        # 1. [{"task": "..."}, ...]
        # 2. ["task1", "task2", ...]
        if isinstance(data, list):
            return data
        else:
            raise ValueError("JSON文件必须包含任务列表数组")
    
    elif file_path.suffix.lower() in ['.txt', '.md']:
        # 文本格式，每行一个任务
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 过滤空行和注释
        tasks = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                tasks.append(line)
        
        return tasks
    
    else:
        raise ValueError(f"不支持的文件格式: {file_path.suffix}")


def _save_batch_report(results: list, task_file: str) -> str:
    """
    保存批处理报告
    
    Args:
        results: 结果列表
        task_file: 原始任务文件路径
    
    Returns:
        报告文件路径
    """
    import json
    from pathlib import Path
    from datetime import datetime
    
    # 生成报告文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    task_file_name = Path(task_file).stem
    report_file = PathConfig.OUTPUTS_DIR / "logs" / f"batch_report_{task_file_name}_{timestamp}.json"
    
    # 确保目录存在
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    # 生成报告
    report = {
        "task_file": str(task_file),
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total": len(results),
            "success": sum(1 for r in results if r.get("status") == "success"),
            "failed": sum(1 for r in results if r.get("status") == "failed")
        },
        "results": results
    }
    
    # 保存报告
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    return str(report_file)


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
    
    print(f"\n📋 任务: {task}\n")
    
    try:
        # 创建 Coordinator Agent（静默）
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
                            print(f"💾 草稿已保存: {draft_id}\n")
            except Exception as e:
                logger.debug(f"保存草稿失败（非关键错误）: {str(e)}")
        
        print("✅ 完成\n")
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
    
    # 初始化环境（静默）
    env_result = setup_environment()
    
    if not env_result['success']:
        print("\n❌ 环境初始化失败，无法继续")
        sys.exit(1)
    
    # 检查 MCP 连接（可选）
    if not args.skip_mcp_check:
        mcp_ok = validate_mcp_connection()
        if not mcp_ok:
            print("⚠️  MCP 服务未连接（可添加 --skip-mcp-check 跳过）")
            
            # 询问是否继续
            if args.mode == "interactive":
                user_input = input("是否继续（不能发布到小红书）？[y/N]: ").strip().lower()
                if user_input not in ['y', 'yes']:
                    print("👋 再见！")
                    sys.exit(0)
            else:
                print("❌ 在非交互模式下，MCP 服务是必需的")
                sys.exit(1)
    
    # 仅检查模式
    if args.check:
        print("\n" + "=" * 70)
        print("🔍 系统配置检查")
        print("=" * 70 + "\n")
        
        # 配置验证
        from config import ModelConfig
        validation_result = ModelConfig.validate_config()
        
        if validation_result["success"]:
            print("✅ 配置验证通过\n")
        else:
            print("❌ 配置验证失败\n")
            for error in validation_result["errors"]:
                print(f"  ❌ {error}")
            print()
        
        if validation_result["warnings"]:
            print("⚠️  警告:")
            for warning in validation_result["warnings"]:
                print(f"  ⚠️  {warning}")
            print()
        
        # 打印配置摘要
        ModelConfig.print_config_summary()
        
        # MCP连接检查
        if not args.skip_mcp_check:
            print("🔌 MCP服务检查:")
            if validate_mcp_connection():
                print("  ✅ MCP服务正常\n")
            else:
                print("  ❌ MCP服务未连接\n")
        
        print("=" * 70)
        
        if validation_result["success"]:
            print("\n✅ 所有检查通过，系统可以正常运行\n")
        else:
            print("\n❌ 存在配置问题，请修复后再运行\n")
            sys.exit(1)
        
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

