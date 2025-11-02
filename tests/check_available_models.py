#!/usr/bin/env python3
"""
检查第三方平台支持的模型
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# 初始化客户端
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)

print("=" * 60)
print("检查第三方平台支持的模型")
print(f"平台: {os.getenv('OPENAI_BASE_URL')}")
print("=" * 60)

# 尝试列出模型
try:
    models = client.models.list()
    print(f"\n✅ 找到 {len(models.data)} 个可用模型：\n")
    
    # 按类别分组
    claude_models = []
    gpt_models = []
    other_models = []
    
    for model in models.data:
        model_id = model.id
        if 'claude' in model_id.lower():
            claude_models.append(model_id)
        elif 'gpt' in model_id.lower():
            gpt_models.append(model_id)
        else:
            other_models.append(model_id)
    
    if claude_models:
        print("🎭 Claude 模型:")
        for m in sorted(claude_models):
            print(f"  - {m}")
    else:
        print("⚠️  没有找到 Claude 模型")
    
    print(f"\n🤖 GPT 模型:")
    for m in sorted(gpt_models)[:10]:  # 只显示前10个
        print(f"  - {m}")
    if len(gpt_models) > 10:
        print(f"  ... 还有 {len(gpt_models) - 10} 个")
    
    if other_models:
        print(f"\n🌟 其他模型:")
        for m in sorted(other_models)[:5]:
            print(f"  - {m}")
        if len(other_models) > 5:
            print(f"  ... 还有 {len(other_models) - 5} 个")

except Exception as e:
    print(f"❌ 无法列出模型: {str(e)}")
    print("\n💡 尝试测试常见的 Claude 模型名称变体：")
    
    # 测试各种可能的 Claude 模型名称
    test_models = [
        "claude-3.5-sonnet",
        "claude-3-5-sonnet-20241022",
        "anthropic/claude-3.5-sonnet",
        "claude-3-sonnet",
        "claude-3.5-sonnet-20240620",
        "claude-sonnet-3.5",
        "gpt-4o",  # 测试 GPT 作为对比
    ]
    
    print("\n测试各种模型名称：")
    for model_name in test_models:
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=5
            )
            print(f"✅ {model_name:40} - 可用")
        except Exception as e:
            error_msg = str(e)
            if "model_not_found" in error_msg or "无可用渠道" in error_msg:
                print(f"❌ {model_name:40} - 不支持")
            elif "503" in error_msg:
                print(f"⚠️  {model_name:40} - 服务不可用")
            else:
                print(f"❓ {model_name:40} - {error_msg[:50]}")

print("\n" + "=" * 60)

