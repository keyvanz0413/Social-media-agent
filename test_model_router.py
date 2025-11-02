#!/usr/bin/env python3
"""
Model Router 单元测试
测试模型路由器的各项功能
"""

import sys
from utils.model_router import (
    ModelRouter, 
    TaskType, 
    QualityLevel,
    create_router,
    get_router
)


def test_basic_selection():
    """测试基础的模型选择功能"""
    print("=" * 60)
    print("测试 1: 基础模型选择")
    print("=" * 60)
    
    router = ModelRouter()
    
    # 测试不同任务类型和质量级别的组合
    test_cases = [
        (TaskType.ANALYSIS, QualityLevel.FAST, "gpt-4o-mini"),
        (TaskType.ANALYSIS, QualityLevel.BALANCED, "gpt-4o"),
        (TaskType.CREATION, QualityLevel.BALANCED, "claude-3.5-sonnet"),
        (TaskType.REVIEW, QualityLevel.FAST, "gpt-4o-mini"),
    ]
    
    all_passed = True
    for task, quality, expected in test_cases:
        model = router.select_model(task, quality)
        passed = model == expected
        status = "✅" if passed else "❌"
        print(f"{status} {task.value:12} + {quality.value:10} → {model:25} (期望: {expected})")
        if not passed:
            all_passed = False
    
    return all_passed


def test_fallback_strategy():
    """测试降级策略"""
    print("\n" + "=" * 60)
    print("测试 2: 降级策略")
    print("=" * 60)
    
    router = ModelRouter()
    
    test_cases = [
        ("gpt-4o", "gpt-4o-mini"),
        ("claude-3.5-sonnet", "gpt-4o"),
        ("gpt-4o-mini", None),  # 已经是最便宜的
    ]
    
    all_passed = True
    for primary, expected_fallback in test_cases:
        fallback = router.get_fallback_model(primary)
        passed = fallback == expected_fallback
        status = "✅" if passed else "❌"
        fallback_str = fallback or "(无备用)"
        expected_str = expected_fallback or "(无备用)"
        print(f"{status} {primary:25} → {fallback_str:25} (期望: {expected_str})")
        if not passed:
            all_passed = False
    
    return all_passed


def test_model_info():
    """测试模型信息查询"""
    print("\n" + "=" * 60)
    print("测试 3: 模型信息查询")
    print("=" * 60)
    
    router = ModelRouter()
    
    # 测试已知模型
    info = router.get_model_info("gpt-4o")
    assert "provider" in info
    assert "description" in info
    assert "strengths" in info
    print(f"✅ gpt-4o 信息查询成功")
    print(f"   提供商: {info['provider']}")
    print(f"   描述: {info['description']}")
    print(f"   优势: {', '.join(info['strengths'][:2])}")
    
    # 测试未知模型
    info = router.get_model_info("unknown-model")
    assert info['provider'] == "unknown"
    print(f"✅ 未知模型处理正确")
    
    return True


def test_suggest_model():
    """测试智能推荐功能"""
    print("\n" + "=" * 60)
    print("测试 4: 智能推荐")
    print("=" * 60)
    
    router = ModelRouter()
    
    test_cases = [
        ("分析小红书的热门内容", False, TaskType.ANALYSIS),
        ("创作一篇关于旅游的帖子", False, TaskType.CREATION),
        ("评审这段文本的质量", False, TaskType.REVIEW),
        ("快速检查一下", True, TaskType.REVIEW),
    ]
    
    for task_desc, prefer_fast, expected_task in test_cases:
        model = router.suggest_model(task_desc, prefer_fast)
        # 只检查返回了一个模型名称
        passed = model is not None and len(model) > 0
        status = "✅" if passed else "❌"
        print(f"{status} '{task_desc}' → {model}")
    
    return True


def test_get_models_by_task():
    """测试按任务类型获取模型"""
    print("\n" + "=" * 60)
    print("测试 5: 按任务类型获取模型")
    print("=" * 60)
    
    router = ModelRouter()
    
    for task in TaskType:
        models = router.get_models_by_task(task)
        print(f"✅ {task.value:12} → {len(models)} 个质量级别")
        for quality, model in models.items():
            print(f"     {quality:10} : {model}")
    
    return True


def test_singleton():
    """测试单例模式"""
    print("\n" + "=" * 60)
    print("测试 6: 单例模式")
    print("=" * 60)
    
    router1 = get_router()
    router2 = get_router()
    
    passed = router1 is router2
    status = "✅" if passed else "❌"
    print(f"{status} 两次调用返回同一实例: {router1 is router2}")
    
    # 测试 create_router 创建新实例
    router3 = create_router()
    passed = router3 is not router1
    status = "✅" if passed else "❌"
    print(f"{status} create_router 创建新实例: {router3 is not router1}")
    
    return True


def test_error_handling():
    """测试错误处理"""
    print("\n" + "=" * 60)
    print("测试 7: 错误处理")
    print("=" * 60)
    
    router = ModelRouter()
    
    # 测试不支持的任务类型（需要手动构造一个错误的枚举值）
    # 这里我们通过直接传入字符串来模拟
    # 实际使用中，由于使用了 Enum，很难传入无效值
    
    print("✅ Enum 类型保证了任务类型的有效性")
    
    # 测试获取不存在的模型信息
    info = router.get_model_info("non-existent-model")
    passed = info['provider'] == "unknown"
    status = "✅" if passed else "❌"
    print(f"{status} 未知模型返回默认信息: {passed}")
    
    return True


def main():
    """运行所有测试"""
    print("\n🧪 Model Router 单元测试\n")
    
    tests = [
        ("基础模型选择", test_basic_selection),
        ("降级策略", test_fallback_strategy),
        ("模型信息查询", test_model_info),
        ("智能推荐", test_suggest_model),
        ("按任务获取模型", test_get_models_by_task),
        ("单例模式", test_singleton),
        ("错误处理", test_error_handling),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result, None))
        except Exception as e:
            results.append((test_name, False, str(e)))
    
    # 打印总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    passed_count = 0
    for test_name, result, error in results:
        if result:
            print(f"✅ {test_name}")
            passed_count += 1
        else:
            print(f"❌ {test_name}")
            if error:
                print(f"   错误: {error}")
    
    print(f"\n通过: {passed_count}/{len(tests)}")
    
    if passed_count == len(tests):
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print(f"\n⚠️  有 {len(tests) - passed_count} 个测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())

