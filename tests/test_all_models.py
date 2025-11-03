"""
测试所有配置的模型是否可用
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openai import OpenAI
from dotenv import load_dotenv
from config import AgentConfig

load_dotenv()

# 初始化客户端
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)

print("\n" + "=" * 70)
print("🧪 测试所有配置的模型")
print("=" * 70 + "\n")

# 收集所有配置的模型
models_to_test = {
    "Coordinator": AgentConfig.COORDINATOR["model"],
    "Content Analyst": AgentConfig.SUB_AGENTS["content_analyst"]["model"],
    "Content Creator": AgentConfig.SUB_AGENTS["content_creator"]["model"],
    "Image Generator": AgentConfig.SUB_AGENTS["image_generator"]["model"],
    "Engagement Reviewer": AgentConfig.SUB_AGENTS["reviewer_engagement"]["model"],
    "Quality Reviewer": AgentConfig.SUB_AGENTS["reviewer_quality"]["model"],
    "Compliance Checker": AgentConfig.SUB_AGENTS["reviewer_compliance"]["model"],
}

results = []

for task_name, model_name in models_to_test.items():
    print(f"📝 {task_name:25} → {model_name}")
    
    try:
        # 发送简单测试消息
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": "测试"}],
            max_tokens=10
        )
        print(f"   ✅ 模型可用\n")
        results.append((task_name, True))
    except Exception as e:
        error_msg = str(e)
        if "model_not_found" in error_msg or "无可用渠道" in error_msg:
            print(f"   ❌ 模型不支持\n")
        else:
            print(f"   ❌ 错误: {error_msg[:50]}...\n")
        results.append((task_name, False))

# 总结
print("=" * 70)
print("📊 测试总结")
print("=" * 70)
print()

passed = sum(1 for _, ok in results if ok)
total = len(results)

for task_name, ok in results:
    status = "✅ 可用" if ok else "❌ 不可用"
    print(f"   {status} - {task_name}")

print(f"\n   总计: {passed}/{total} 可用")

if passed == total:
    print("\n🎉 所有模型配置正确，可以正常使用！\n")
else:
    print(f"\n⚠️ {total - passed} 个模型不可用，请检查配置。\n")

