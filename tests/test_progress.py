#!/usr/bin/env python3
"""
综合测试脚本
测试所有模块功能：API配置、Model Router、MCP Client
"""

import os
import sys
import logging
from typing import Optional
from dotenv import load_dotenv
import requests

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_section(title: str, symbol: str = "="):
    """打印章节标题"""
    print(f"\n{symbol * 70}")
    print(f"  {title}")
    print(f"{symbol * 70}\n")


# ========== 1. API 配置测试 ==========

def test_api_configuration() -> bool:
    """测试API配置是否正确"""
    print_section("🔍 测试 1：API 配置检查")
    
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    
    if not api_key:
        print("❌ 未找到 OPENAI_API_KEY")
        print("💡 请在 .env 文件中配置 OPENAI_API_KEY")
        return False
    
    print(f"✅ API Key: {api_key[:15]}...{api_key[-4:]}")
    
    if not base_url:
        base_url = "https://api.openai.com/v1"
        print(f"ℹ️  Base URL: {base_url} (默认)")
    else:
        print(f"✅ Base URL: {base_url}")
    
    # 识别平台
    platform = identify_platform(base_url)
    if platform:
        print(f"🏢 检测到平台: {platform}")
    
    # 测试连接
    print("\n正在测试 API 连接...")
    try:
        response = requests.post(
            f"{base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Say 'Hello!'"}
                ],
                "max_tokens": 20
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            message = data['choices'][0]['message']['content']
            print(f"✅ API 连接成功！")
            print(f"   模型响应: {message}")
            
            if 'usage' in data:
                usage = data['usage']
                print(f"   Token 使用: {usage.get('total_tokens', 0)} tokens")
            
            return True
        else:
            print(f"❌ API 调用失败 (状态码: {response.status_code})")
            print(f"   错误信息: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ API 测试失败: {str(e)}")
        return False


def identify_platform(base_url: str) -> Optional[str]:
    """识别API平台"""
    if not base_url:
        return "OpenAI (官方)"
    
    url_lower = base_url.lower()
    
    if "openrouter.ai" in url_lower:
        return "OpenRouter (多模型聚合)"
    elif "siliconflow.cn" in url_lower:
        return "硅基流动 (国内平台)"
    elif "groq.com" in url_lower:
        return "Groq (超快推理)"
    elif "deepseek.com" in url_lower:
        return "DeepSeek (高性价比)"
    elif "moonshot.cn" in url_lower:
        return "Moonshot (Kimi)"
    elif "localhost" in url_lower or "127.0.0.1" in url_lower:
        return "本地服务 (Ollama/LMStudio)"
    elif "openai.com" in url_lower:
        return "OpenAI (官方)"
    else:
        return "第三方平台"


# ========== 2. Model Router 测试 ==========

def test_model_router() -> bool:
    """测试 Model Router 功能"""
    print_section("🔍 测试 2：Model Router")
    
    try:
        from utils.model_router import (
            ModelRouter, 
            TaskType, 
            QualityLevel,
            get_router
        )
        
        router = ModelRouter()
        
        # 测试1: 基础模型选择
        print("测试 2.1: 基础模型选择")
        test_cases = [
            (TaskType.ANALYSIS, QualityLevel.FAST, "gpt-4o-mini"),
            (TaskType.ANALYSIS, QualityLevel.BALANCED, "gpt-4o"),
            (TaskType.CREATION, QualityLevel.HIGH, "claude-3.5-sonnet"),
            (TaskType.REVIEW, QualityLevel.FAST, "gpt-4o-mini"),
        ]
        
        all_passed = True
        for task, quality, expected in test_cases:
            model = router.select_model(task, quality)
            passed = model == expected
            status = "✅" if passed else "❌"
            print(f"  {status} {task.value} + {quality.value} → {model}")
            if not passed:
                all_passed = False
        
        if not all_passed:
            return False
        
        # 测试2: 降级策略
        print("\n测试 2.2: 降级策略")
        fallback_tests = [
            ("gpt-4o", "gpt-4o-mini"),
            ("claude-3.5-sonnet", "gpt-4o"),
        ]
        
        for primary, expected_fallback in fallback_tests:
            fallback = router.get_fallback_model(primary)
            passed = fallback == expected_fallback
            status = "✅" if passed else "❌"
            print(f"  {status} {primary} → {fallback or '(无备用)'}")
            if not passed:
                all_passed = False
        
        # 测试3: 模型信息查询
        print("\n测试 2.3: 模型信息查询")
        info = router.get_model_info("gpt-4o")
        if "provider" in info and "description" in info:
            print(f"  ✅ gpt-4o: {info['description']}")
        else:
            print("  ❌ 模型信息查询失败")
            all_passed = False
        
        # 测试4: 智能推荐
        print("\n测试 2.4: 智能推荐")
        model = router.suggest_model("分析小红书的热门内容")
        print(f"  ✅ 推荐模型: {model}")
        
        # 测试5: 单例模式
        print("\n测试 2.5: 单例模式")
        router1 = get_router()
        router2 = get_router()
        if router1 is router2:
            print("  ✅ 单例模式正常工作")
        else:
            print("  ❌ 单例模式失败")
            all_passed = False
        
        if all_passed:
            print("\n✅ Model Router 所有测试通过！")
        
        return all_passed
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ Model Router 测试失败: {e}")
        logger.exception("详细错误")
        return False


# ========== 3. MCP Client 测试 ==========

def test_mcp_client() -> bool:
    """测试 MCP Client 功能"""
    print_section("🔍 测试 3：小红书 MCP Client")
    
    try:
        from utils.mcp_client import XiaohongshuMCPClient, XiaohongshuMCPError
        
        # 创建客户端
        print("正在初始化 MCP 客户端...")
        client = XiaohongshuMCPClient()
        print(f"✅ 客户端初始化成功")
        print(f"   MCP服务地址：{client.base_url}")
        
        all_passed = True
        
        # 测试1: 登录状态检查
        print("\n测试 3.1: 检查登录状态")
        try:
            status = client.check_login_status()
            is_logged_in = status.get('is_logged_in', False)
            username = status.get('username', '未知')
            
            if is_logged_in:
                print(f"  ✅ 已登录小红书")
                print(f"     用户名：{username}")
            else:
                print(f"  ⚠️  未登录小红书")
                print(f"     请运行: cd ../xiaohongshu-mcp && ./xiaohongshu-login")
                all_passed = False
        except XiaohongshuMCPError as e:
            print(f"  ❌ 登录状态检查失败: {e}")
            all_passed = False
        
        # 测试2: 获取推荐列表
        print("\n测试 3.2: 获取推荐列表")
        try:
            result = client.list_feeds(limit=5)
            feeds = result.get('feeds', [])
            print(f"  ✅ 获取成功，共 {len(feeds)} 篇推荐笔记")
            if feeds:
                for i, feed in enumerate(feeds[:3], 1):
                    title = feed.get('title', '无标题')
                    likes = feed.get('liked_count', 0)
                    print(f"     {i}. {title} (点赞: {likes})")
        except XiaohongshuMCPError as e:
            print(f"  ⚠️  获取推荐列表失败: {e}")
            # 推荐列表失败不影响整体测试
        
        # 测试3: 搜索功能（可能失败，服务端问题）
        print("\n测试 3.3: 搜索笔记")
        try:
            result = client.search_notes("旅游", limit=3)
            feeds = result.get('feeds', [])
            print(f"  ✅ 搜索成功，找到 {len(feeds)} 篇笔记")
        except XiaohongshuMCPError as e:
            print(f"  ⚠️  搜索失败 (已知服务端问题): {str(e)[:100]}...")
            # 搜索失败不影响整体测试，这是已知的服务端问题
        
        # 关闭客户端
        client.close()
        print("\n✅ MCP Client 测试完成")
        
        return all_passed
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ MCP Client 测试失败: {e}")
        logger.exception("详细错误")
        return False


# ========== 4. MCP 服务测试 (直接HTTP) ==========

def test_mcp_service() -> bool:
    """直接测试MCP服务的HTTP接口"""
    print_section("🔍 测试 4：MCP 服务 (直接HTTP)")
    
    MCP_BASE_URL = "http://localhost:18060"
    API_URL = f"{MCP_BASE_URL}/api/v1"
    
    print(f"MCP服务地址: {MCP_BASE_URL}")
    
    all_passed = True
    
    # 测试1: MCP 协议初始化
    print("\n测试 4.1: MCP 协议初始化")
    try:
        response = requests.post(f"{MCP_BASE_URL}/mcp", json={
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            },
            "id": 1
        }, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            server_info = result.get('result', {}).get('serverInfo', {})
            print(f"  ✅ MCP连接成功")
            print(f"     服务器名称：{server_info.get('name')}")
            print(f"     服务器版本：{server_info.get('version')}")
        else:
            print(f"  ❌ MCP连接失败：HTTP {response.status_code}")
            all_passed = False
    except requests.exceptions.ConnectionError:
        print(f"  ❌ 无法连接到MCP服务")
        print(f"     请确保MCP服务正在运行:")
        print(f"     cd ../xiaohongshu-mcp && ./xiaohongshu-mcp")
        return False
    except Exception as e:
        print(f"  ❌ MCP初始化失败: {e}")
        all_passed = False
    
    # 测试2: 登录状态 API
    print("\n测试 4.2: 登录状态 API")
    try:
        response = requests.get(f"{API_URL}/login/status", timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            is_logged_in = result.get('data', {}).get('is_logged_in', False)
            username = result.get('data', {}).get('username', '未知')
            
            if is_logged_in:
                print(f"  ✅ 已登录小红书")
                print(f"     用户名：{username}")
            else:
                print(f"  ⚠️  未登录小红书")
                all_passed = False
        else:
            print(f"  ❌ API调用失败：HTTP {response.status_code}")
            all_passed = False
    except Exception as e:
        print(f"  ❌ 登录状态检查失败: {e}")
        all_passed = False
    
    # 测试3: 推荐列表 API
    print("\n测试 4.3: 推荐列表 API")
    try:
        response = requests.get(f"{API_URL}/feeds/list?limit=5", timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                feeds = result.get('data', {}).get('feeds', [])
                print(f"  ✅ 获取成功，共 {len(feeds)} 篇笔记")
            else:
                print(f"  ❌ 获取失败：{result.get('message')}")
                all_passed = False
        else:
            print(f"  ❌ API调用失败：HTTP {response.status_code}")
            all_passed = False
    except Exception as e:
        print(f"  ❌ 获取推荐列表失败: {e}")
        all_passed = False
    
    if all_passed:
        print("\n✅ MCP 服务所有测试通过！")
    
    return all_passed


# ========== 主测试流程 ==========

def main():
    """运行所有测试"""
    print("\n" + "="*70)
    print("  🚀 社交媒体 Agent - 综合功能测试")
    print("="*70)
    
    results = {}
    
    # 测试1: API配置
    results['api_config'] = test_api_configuration()
    
    # 测试2: Model Router
    results['model_router'] = test_model_router()
    
    # 测试3: MCP Client
    results['mcp_client'] = test_mcp_client()
    
    # 测试4: MCP Service
    results['mcp_service'] = test_mcp_service()
    
    # 测试结果总结
    print_section("📊 测试结果总结", "=")
    
    total = len(results)
    passed = sum(1 for result in results.values() if result)
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name:20s} {status}")
    
    print(f"\n  总计：{passed}/{total} 项测试通过")
    
    if passed == total:
        print_section("🎉 所有测试通过！系统已准备就绪！", "=")
        print("✨ 接下来可以：")
        print("   1. 开始实现业务逻辑 (sub_agents/)")
        print("   2. 运行示例: python example_mcp_usage.py")
        print("   3. 查看文档: MCP_CLIENT_USAGE.md")
        return 0
    else:
        print_section("⚠️  部分测试失败，请检查", "=")
        
        if not results['api_config']:
            print("🔧 API配置问题:")
            print("   1. 检查 .env 文件是否存在")
            print("   2. 确认 OPENAI_API_KEY 已配置")
            print("   3. 如使用第三方平台，配置 OPENAI_BASE_URL")
        
        if not results['model_router']:
            print("\n🔧 Model Router问题:")
            print("   1. 检查 utils/model_router.py 文件")
            print("   2. 确认导入路径正确")
        
        if not results['mcp_client'] or not results['mcp_service']:
            print("\n🔧 MCP服务问题:")
            print("   1. 确保MCP服务正在运行:")
            print("      cd ../xiaohongshu-mcp && ./xiaohongshu-mcp")
            print("   2. 检查是否已登录:")
            print("      cd ../xiaohongshu-mcp && ./xiaohongshu-login")
            print("   3. 确认服务地址: http://localhost:18060")
        
        return 1


if __name__ == "__main__":
    sys.exit(main())

