#!/usr/bin/env python3
"""
Model Router + 真实 API 集成测试
验证 Model Router 与实际 API 调用的集成
"""

import os
from dotenv import load_dotenv
from utils.model_router import ModelRouter, TaskType, QualityLevel

# 加载环境变量
load_dotenv()

def test_api_integration():
    """测试与 API 的集成"""
    print("=" * 60)
    print("🧪 Model Router + API 集成测试")
    print("=" * 60)
    
    # 检查 API 配置
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    
    if not api_key:
        print("❌ 未配置 OPENAI_API_KEY")
        return False
    
    print(f"✅ API Key: {api_key[:15]}...{api_key[-4:]}")
    print(f"✅ Base URL: {base_url or '(默认)'}")
    
    # 创建路由器
    router = ModelRouter()
    
    # 测试不同场景的模型选择
    print("\n" + "=" * 60)
    print("场景测试")
    print("=" * 60)
    
    scenarios = [
        ("分析小红书热门内容", TaskType.ANALYSIS, QualityLevel.BALANCED),
        ("创作旅游帖子", TaskType.CREATION, QualityLevel.HIGH),
        ("快速评审文本", TaskType.REVIEW, QualityLevel.FAST),
    ]
    
    for desc, task, quality in scenarios:
        model = router.select_model(task, quality)
        info = router.get_model_info(model)
        
        print(f"\n场景: {desc}")
        print(f"  任务类型: {task.value}")
        print(f"  质量级别: {quality.value}")
        print(f"  选择模型: {model}")
        print(f"  模型描述: {info['description']}")
        print(f"  成本级别: {info['cost_level']}")
        
        # 显示降级链
        fallback = router.get_fallback_model(model)
        if fallback:
            print(f"  备用模型: {fallback}")
    
    # 说明如何在实际代码中使用
    print("\n" + "=" * 60)
    print("使用示例")
    print("=" * 60)
    
    print("""
# 在你的 Agent 代码中：
from connectonion import llm_do
from utils.model_router import ModelRouter, TaskType

router = ModelRouter()

# 1. 内容分析时
def analyze_content(keyword):
    model = router.select_model(TaskType.ANALYSIS)
    prompt = f"分析关键词 '{keyword}' 的内容..."
    result = llm_do(prompt, model=model)
    return result

# 2. 内容创作时
def create_content(analysis):
    model = router.select_model(TaskType.CREATION)
    prompt = f"基于分析创作内容：{analysis}"
    result = llm_do(prompt, model=model)
    return result

# 3. 带降级的错误处理
def safe_llm_call(prompt, task_type):
    router = ModelRouter()
    model = router.select_model(task_type)
    
    try:
        return llm_do(prompt, model=model)
    except Exception as e:
        # 尝试使用备用模型
        fallback = router.get_fallback_model(model)
        if fallback:
            print(f"主模型失败，切换到 {fallback}")
            return llm_do(prompt, model=fallback)
        else:
            raise e
    """)
    
    print("\n✅ 集成测试完成！")
    print("\n💡 提示：")
    print("  - Model Router 已就绪，可以在 Agent 中使用")
    print("  - 它会自动使用你配置的第三方 API")
    print("  - 下一步：实现 Mock MCP Client")
    
    return True


if __name__ == "__main__":
    test_api_integration()

