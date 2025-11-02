#!/usr/bin/env python3
"""
小红书MCP服务管理脚本
用于管理MCP服务的启动、停止、登录等操作
"""

import os
import sys
import signal
import subprocess
import time
import requests
import psutil
from pathlib import Path

# 配置路径
MCP_DIR = Path("/Users/keyvanzhuo/Documents/CodeProjects/ConnetOnion/xiaohongshu-mcp")
MCP_BIN = MCP_DIR / "xiaohongshu-mcp"
LOGIN_BIN = MCP_DIR / "xiaohongshu-login"
PID_FILE = MCP_DIR / "xiaohongshu-mcp.pid"
LOG_FILE = MCP_DIR / "xiaohongshu-mcp.log"

# 服务配置
MCP_URL = "http://localhost:18060"
API_URL = f"{MCP_URL}/api/v1"


class Colors:
    """终端颜色"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(text):
    """打印标题"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}  {text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")


def print_success(text):
    """打印成功信息"""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")


def print_error(text):
    """打印错误信息"""
    print(f"{Colors.RED}❌ {text}{Colors.END}")


def print_warning(text):
    """打印警告信息"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")


def print_info(text):
    """打印普通信息"""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")


def check_binaries():
    """检查二进制文件是否存在"""
    if not MCP_BIN.exists():
        print_error(f"MCP服务程序不存在: {MCP_BIN}")
        print_info("请先编译或下载 xiaohongshu-mcp")
        return False
    
    if not LOGIN_BIN.exists():
        print_error(f"登录工具不存在: {LOGIN_BIN}")
        print_info("请先编译登录工具: go build -o xiaohongshu-login cmd/login/main.go")
        return False
    
    return True


def is_service_running():
    """检查服务是否正在运行"""
    # 方法1: 检查PID文件
    if PID_FILE.exists():
        try:
            with open(PID_FILE, 'r') as f:
                pid = int(f.read().strip())
            
            # 检查进程是否存在
            if psutil.pid_exists(pid):
                try:
                    proc = psutil.Process(pid)
                    if 'xiaohongshu-mcp' in proc.name():
                        return pid
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except (ValueError, FileNotFoundError):
            pass
    
    # 方法2: 通过进程名查找
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info.get('cmdline', [])
            if cmdline and 'xiaohongshu-mcp' in ' '.join(cmdline):
                return proc.info['pid']
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    return None


def check_service_health():
    """检查服务健康状态"""
    try:
        response = requests.get(f"{MCP_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def check_login_status():
    """检查登录状态"""
    try:
        response = requests.get(f"{API_URL}/login/status", timeout=5)
        if response.status_code == 200:
            result = response.json()
            return result.get('data', {}).get('is_logged_in', False)
    except:
        pass
    return False


def start_service(headless=True):
    """启动MCP服务"""
    print_header("启动小红书MCP服务")
    
    # 检查二进制文件
    if not check_binaries():
        return False
    
    # 检查是否已经运行
    pid = is_service_running()
    if pid:
        print_warning(f"服务已经在运行 (PID: {pid})")
        return True
    
    # 启动服务
    print_info("正在启动服务...")
    
    try:
        # 打开日志文件
        log_file = open(LOG_FILE, 'a')
        
        # 构建命令
        cmd = [str(MCP_BIN)]
        if headless:
            cmd.extend(['-headless=true'])
        else:
            cmd.extend(['-headless=false'])
        
        # 启动进程
        process = subprocess.Popen(
            cmd,
            cwd=str(MCP_DIR),
            stdout=log_file,
            stderr=subprocess.STDOUT,
            start_new_session=True
        )
        
        # 保存PID
        with open(PID_FILE, 'w') as f:
            f.write(str(process.pid))
        
        # 等待服务启动
        print_info("等待服务启动...")
        for i in range(10):
            time.sleep(1)
            if check_service_health():
                print_success(f"服务启动成功 (PID: {process.pid})")
                print_info(f"服务地址: {MCP_URL}")
                print_info(f"日志文件: {LOG_FILE}")
                
                # 检查登录状态
                if check_login_status():
                    print_success("已登录小红书")
                else:
                    print_warning("未登录小红书，请运行: python xiaohongshu_manager.py login")
                
                return True
        
        print_error("服务启动超时，请检查日志")
        return False
        
    except Exception as e:
        print_error(f"启动服务失败: {str(e)}")
        return False


def stop_service():
    """停止MCP服务"""
    print_header("停止小红书MCP服务")
    
    pid = is_service_running()
    if not pid:
        print_warning("服务未运行")
        return True
    
    print_info(f"正在停止服务 (PID: {pid})...")
    
    try:
        # 发送SIGTERM信号
        os.kill(pid, signal.SIGTERM)
        
        # 等待进程结束
        for i in range(10):
            time.sleep(1)
            if not psutil.pid_exists(pid):
                print_success("服务已停止")
                
                # 删除PID文件
                if PID_FILE.exists():
                    PID_FILE.unlink()
                
                return True
        
        # 如果还没结束，强制杀死
        print_warning("正在强制停止服务...")
        os.kill(pid, signal.SIGKILL)
        time.sleep(1)
        
        if not psutil.pid_exists(pid):
            print_success("服务已停止")
            if PID_FILE.exists():
                PID_FILE.unlink()
            return True
        else:
            print_error("无法停止服务")
            return False
            
    except Exception as e:
        print_error(f"停止服务失败: {str(e)}")
        return False


def restart_service(headless=True):
    """重启MCP服务"""
    print_header("重启小红书MCP服务")
    
    if is_service_running():
        if not stop_service():
            return False
        time.sleep(2)
    
    return start_service(headless)


def login():
    """运行登录工具"""
    print_header("小红书登录")
    
    # 检查二进制文件
    if not LOGIN_BIN.exists():
        print_error(f"登录工具不存在: {LOGIN_BIN}")
        print_info("请先编译: go build -o xiaohongshu-login cmd/login/main.go")
        return False
    
    print_info("正在启动登录工具...")
    print_info("请在打开的浏览器中完成登录...")
    
    try:
        result = subprocess.run(
            [str(LOGIN_BIN)],
            cwd=str(MCP_DIR)
        )
        
        if result.returncode == 0:
            print_success("登录完成")
            return True
        else:
            print_error("登录失败")
            return False
            
    except Exception as e:
        print_error(f"运行登录工具失败: {str(e)}")
        return False


def show_status():
    """显示服务状态"""
    print_header("小红书MCP服务状态")
    
    # 检查服务运行状态
    pid = is_service_running()
    if pid:
        print_success(f"服务正在运行 (PID: {pid})")
        
        # 检查健康状态
        if check_service_health():
            print_success(f"健康检查通过")
        else:
            print_warning("健康检查失败")
        
        # 检查登录状态
        if check_login_status():
            print_success("已登录小红书")
        else:
            print_warning("未登录小红书")
        
        # 显示进程信息
        try:
            proc = psutil.Process(pid)
            print_info(f"运行时间: {int(time.time() - proc.create_time())} 秒")
            print_info(f"CPU使用: {proc.cpu_percent()}%")
            print_info(f"内存使用: {proc.memory_info().rss / 1024 / 1024:.1f} MB")
        except:
            pass
            
    else:
        print_warning("服务未运行")
    
    print_info(f"\n服务地址: {MCP_URL}")
    print_info(f"日志文件: {LOG_FILE}")


def show_logs(lines=50):
    """显示日志"""
    print_header(f"最近 {lines} 行日志")
    
    if not LOG_FILE.exists():
        print_warning("日志文件不存在")
        return
    
    try:
        # 使用tail命令显示最后N行
        result = subprocess.run(
            ['tail', '-n', str(lines), str(LOG_FILE)],
            capture_output=True,
            text=True
        )
        print(result.stdout)
    except Exception as e:
        print_error(f"读取日志失败: {str(e)}")


def show_help():
    """显示帮助信息"""
    help_text = f"""
{Colors.BOLD}小红书MCP服务管理工具{Colors.END}

{Colors.BOLD}用法:{Colors.END}
    python xiaohongshu_manager.py <command> [options]

{Colors.BOLD}命令:{Colors.END}
    start           启动MCP服务（默认无头模式）
    start --headed  启动MCP服务（有界面模式）
    stop            停止MCP服务
    restart         重启MCP服务
    login           运行登录工具
    status          显示服务状态
    logs [N]        显示最近N行日志（默认50行）
    help            显示此帮助信息

{Colors.BOLD}示例:{Colors.END}
    python xiaohongshu_manager.py start          # 启动服务
    python xiaohongshu_manager.py login          # 登录小红书
    python xiaohongshu_manager.py status         # 查看状态
    python xiaohongshu_manager.py logs 100       # 查看最近100行日志
    python xiaohongshu_manager.py restart        # 重启服务
    python xiaohongshu_manager.py stop           # 停止服务

{Colors.BOLD}配置:{Colors.END}
    MCP目录: {MCP_DIR}
    服务地址: {MCP_URL}
    日志文件: {LOG_FILE}
"""
    print(help_text)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == 'start':
        headless = '--headed' not in sys.argv
        start_service(headless)
    
    elif command == 'stop':
        stop_service()
    
    elif command == 'restart':
        headless = '--headed' not in sys.argv
        restart_service(headless)
    
    elif command == 'login':
        login()
    
    elif command == 'status':
        show_status()
    
    elif command == 'logs':
        lines = 50
        if len(sys.argv) > 2:
            try:
                lines = int(sys.argv[2])
            except ValueError:
                pass
        show_logs(lines)
    
    elif command in ['help', '-h', '--help']:
        show_help()
    
    else:
        print_error(f"未知命令: {command}")
        print_info("使用 'help' 查看可用命令")


if __name__ == "__main__":
    main()

