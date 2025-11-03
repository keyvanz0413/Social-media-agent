"""
测试 Coordinator Agent 模型配置

验证新配置的模型是否可用
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import AgentConfig


def test_model_config():
    """测试模型配置"""
    print("\n" + "=" * 70)
    print("🧪 测试 Coordinator Agent 模型配置")
    print("=" * 70 + "\n")
    
    # 显示当前配置
    model_name = AgentConfig.COORDINATOR["model"]
    print(f"📋 当前配置:")
    print(f"   模型: {model_name}")
    print(f"   最大迭代: {AgentConfig.COORDINATOR['max_iterations']}")
    print(f"   温度: {AgentConfig.COORDINATOR['temperature']}")
    print()
    
    return model_name


def test_agent_creation():
    """测试 Agent 创建"""
    print("🤖 测试 Agent 创建...")
    
    try:
        from agent import create_coordinator_agent
        
        agent = create_coordinator_agent()
        print(f"   ✅ Agent 创建成功")
        print()
        
        return agent
    except Exception as e:
        print(f"   ❌ Agent 创建失败: {str(e)}")
        import traceback
        traceback.print_exc()
        print()
        return None


def test_simple_input():
    """测试简单输入"""
    print("💬 测试简单对话...")
    
    try:
        from agent import create_coordinator_agent
        
        agent = create_coordinator_agent()
        
        # 简单测试：只让它回复，不调用工具
        print("   发送测试消息: '你好，请介绍一下你自己'")
        result = agent.input("你好，请介绍一下你自己")
        
        print(f"   ✅ 模型响应成功")
        print(f"   响应长度: {len(result)} 字符")
        print(f"   响应预览: {result[:100]}...")
        print()
        
        return True
    except Exception as e:
        print(f"   ❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        print()
        return False


def main():
    """运行所有测试"""
    print("\n" + "=" * 70)
    print("🔍 Coordinator 模型验证测试")
    print("=" * 70)
    
    # 测试 1: 配置检查
    model_name = test_model_config()
    
    # 测试 2: Agent 创建
    agent = test_agent_creation()
    
    if not agent:
        print("=" * 70)
        print("❌ Agent 创建失败，停止后续测试")
        print("=" * 70)
        print("\n💡 可能的问题:")
        print("   1. 检查 .env 中的 OPENAI_API_KEY 是否配置")
        print("   2. 检查 .env 中的 OPENAI_BASE_URL 是否配置（第三方平台需要）")
        print("   3. 确认第三方平台支持模型: gpt-5-mini-2025-08-07")
        print()
        return
    
    # 测试 3: 简单对话
    print("💬 测试简单对话...")
    try:
        print("   发送测试消息: '你好，请简单介绍一下你的功能'")
        result = agent.input("你好，请简单介绍一下你的功能")
        
        print(f"   ✅ 模型响应成功")
        print(f"   响应长度: {len(result)} 字符")
        print(f"   响应预览: {result[:150]}...")
        print()
        dialogue_ok = True
    except Exception as e:
        print(f"   ❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        print()
        dialogue_ok = False
    
    # 总结
    print("=" * 70)
    print("📊 测试总结")
    print("=" * 70)
    print()
    
    if agent and dialogue_ok:
        print("✅ 所有测试通过！")
        print(f"\n🎉 模型 '{model_name}' 配置正确，可以正常使用！")
        print()
        print("💡 下一步:")
        print("   - 可以开始使用完整功能")
        print("   - 运行: python main.py --mode single --task '测试任务'")
    else:
        print("⚠️ 部分测试失败")
        print("\n请检查:")
        print("   1. API Key 是否正确")
        print("   2. Base URL 是否配置")
        print("   3. 模型名称是否正确")
        print("   4. 第三方平台是否支持该模型")
    
    print()


if __name__ == "__main__":
    main()

