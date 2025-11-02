#!/usr/bin/env python3
"""
测试第三方 API 配置
用于验证 API Key 和 Base URL 是否配置正确
"""

import os
import sys
from dotenv import load_dotenv
import requests
from typing import Optional

# 加载环境变量
load_dotenv()


def test_api_connection() -> bool:
    """
    测试 API 连接是否正常
    
    Returns:
        bool: 连接是否成功
    """
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    
    # 检查配置
    print("=" * 60)
    print("🔍 检查 API 配置")
    print("=" * 60)
    
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
    
    print("\n" + "=" * 60)
    print("🧪 测试 API 连接")
    print("=" * 60)
    
    # 测试连接
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
                "max_tokens": 20,
                "temperature": 0.7
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            message = data['choices'][0]['message']['content']
            
            print(f"✅ API 连接成功！")
            print(f"\n📝 测试响应:")
            print(f"   模型: gpt-4o-mini")
            print(f"   响应: {message}")
            
            # 显示使用信息
            if 'usage' in data:
                usage = data['usage']
                print(f"\n📊 Token 使用:")
                print(f"   输入: {usage.get('prompt_tokens', 0)} tokens")
                print(f"   输出: {usage.get('completion_tokens', 0)} tokens")
                print(f"   总计: {usage.get('total_tokens', 0)} tokens")
            
            print("\n" + "=" * 60)
            print("🎉 配置正确！可以开始使用了")
            print("=" * 60)
            return True
        else:
            print(f"❌ API 调用失败")
            print(f"   状态码: {response.status_code}")
            print(f"   错误信息: {response.text}")
            
            # 提供建议
            if response.status_code == 401:
                print("\n💡 建议:")
                print("   - 检查 API Key 是否正确")
                print("   - 确认 API Key 是否有效")
            elif response.status_code == 404:
                print("\n💡 建议:")
                print("   - 检查 Base URL 是否正确")
                print("   - 确认模型名称是否支持")
            
            return False
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
        print("💡 建议: 检查网络连接或尝试其他 API 服务器")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ 连接错误")
        print("💡 建议: 检查 Base URL 是否正确，或检查网络连接")
        return False
    except Exception as e:
        print(f"❌ 未知错误: {str(e)}")
        return False


def identify_platform(base_url: str) -> Optional[str]:
    """
    识别 API 平台
    
    Args:
        base_url: API Base URL
        
    Returns:
        平台名称
    """
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
    elif "bigmodel.cn" in url_lower:
        return "智谱 AI (GLM)"
    elif "together.xyz" in url_lower:
        return "TogetherAI"
    elif "localhost" in url_lower or "127.0.0.1" in url_lower:
        return "本地服务 (Ollama/LMStudio)"
    elif "openai.com" in url_lower:
        return "OpenAI (官方)"
    else:
        return "未知平台"


def show_config_guide():
    """显示配置指南"""
    print("\n" + "=" * 60)
    print("📖 配置指南")
    print("=" * 60)
    print("""
1. 创建 .env 文件:
   cp env.example .env

2. 编辑 .env 文件，配置以下变量:

   # OpenRouter (推荐)
   OPENAI_API_KEY=sk-or-v1-your-key-here
   OPENAI_BASE_URL=https://openrouter.ai/api/v1

   # 或者硅基流动 (国内推荐)
   OPENAI_API_KEY=sk-your-key
   OPENAI_BASE_URL=https://api.siliconflow.cn/v1

3. 重新运行此脚本进行测试

更多详情请查看: docs/THIRD_PARTY_API_GUIDE.md
    """)


def main():
    """主函数"""
    print("\n🤖 第三方 API 配置测试工具\n")
    
    # 检查 .env 文件
    if not os.path.exists(".env"):
        print("⚠️  未找到 .env 文件")
        show_config_guide()
        sys.exit(1)
    
    # 测试 API
    success = test_api_connection()
    
    if not success:
        show_config_guide()
        sys.exit(1)
    else:
        print("\n💻 你现在可以运行:")
        print("   python agent.py")
        print("   python main.py")
        sys.exit(0)


if __name__ == "__main__":
    main()

