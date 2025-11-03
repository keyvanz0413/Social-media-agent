"""
性能优化测试

对比优化前后的性能差异：
1. 串行 vs 并行评审
2. 无缓存 vs 有缓存
3. 完整测试和基准测试
"""

import sys
import os
import json
import time
import logging

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.review_optimized import review_content_optimized, clear_review_cache, get_review_cache_stats
from agents.reviewers.quality_reviewer import review_quality
from tools.review_tools_v1 import review_compliance

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


# 测试内容
TEST_CONTENT = {
    "title": "悉尼旅游攻略｜3天2夜深度游✨",
    "content": """分享我的悉尼之旅！

📍 第一天：市区经典
上午去了悉尼歌剧院，建议提前预约参观，门票42澳元。中午在环形码头吃了海鲜，景色超美！下午爬上海港大桥，费用268澳元，有专业教练带领。

📍 第二天：海滩休闲
去了邦迪海滩，冲浪体验超棒！记得带防晒霜，澳洲的阳光很强。晚上在达令港吃晚餐，推荐海鲜拼盘。

📍 第三天：文化体验
参观了澳大利亚博物馆，了解了当地历史。下午在岩石区逛街，买了很多纪念品。

💰 费用总结：约3000澳元/人
⏰ 最佳季节：9-11月（春季）

你们还想了解哪些景点？评论区告诉我！✨""",
    "topic": "悉尼旅游",
    "hashtags": ["悉尼旅游", "澳洲攻略"]
}


def test_serial_review():
    """测试串行评审（原始方式）"""
    print("\n" + "=" * 70)
    print("🧪 测试 1: 串行评审（原始方式）")
    print("=" * 70 + "\n")
    
    start_time = time.time()
    
    # 1. 质量评审
    print("1️⃣ 质量评审...")
    q_start = time.time()
    quality_result = review_quality(TEST_CONTENT)
    q_time = time.time() - q_start
    print(f"   完成（{q_time:.1f}秒）")
    
    # 2. 合规检查
    print("2️⃣ 合规检查...")
    c_start = time.time()
    compliance_result = review_compliance(TEST_CONTENT)
    c_time = time.time() - c_start
    print(f"   完成（{c_time:.1f}秒）")
    
    total_time = time.time() - start_time
    
    # 解析结果
    quality = json.loads(quality_result)
    quality_score = quality.get('score', 0)
    
    print(f"\n📊 结果：")
    print(f"   质量评分: {quality_score}/10")
    print(f"   质量评审耗时: {q_time:.1f}秒")
    print(f"   合规检查耗时: {c_time:.1f}秒")
    print(f"   ⏱️  总耗时: {total_time:.1f}秒")
    
    return {
        "quality_score": quality_score,
        "total_time": total_time,
        "quality_time": q_time,
        "compliance_time": c_time
    }


def test_parallel_review():
    """测试并行评审（优化后）"""
    print("\n" + "=" * 70)
    print("🧪 测试 2: 并行评审（优化后）")
    print("=" * 70 + "\n")
    
    # 清除缓存确保公平比较
    clear_review_cache()
    
    start_time = time.time()
    
    print("🚀 并行执行质量评审和合规检查...")
    result = review_content_optimized(
        TEST_CONTENT,
        enable_engagement=False,
        use_cache=False  # 第一次不使用缓存
    )
    
    total_time = time.time() - start_time
    
    print(f"\n📊 结果：")
    print(f"   综合评分: {result['overall']['score']}/10")
    print(f"   质量评分: {result['overall']['quality_score']}/10")
    print(f"   合规性: {'✅ 通过' if result['overall']['compliance_passed'] else '❌ 未通过'}")
    print(f"   决策: {result['overall']['action_text']}")
    print(f"   ⏱️  总耗时: {result['performance']['elapsed_time']}秒")
    
    return {
        "overall_score": result['overall']['score'],
        "total_time": result['performance']['elapsed_time'],
        "from_cache": result['performance']['from_cache']
    }


def test_cached_review():
    """测试缓存效果"""
    print("\n" + "=" * 70)
    print("🧪 测试 3: 缓存效果")
    print("=" * 70 + "\n")
    
    # 第一次调用（会缓存）
    print("1️⃣ 第一次调用（写入缓存）...")
    start_time = time.time()
    result1 = review_content_optimized(
        TEST_CONTENT,
        enable_engagement=False,
        use_cache=True
    )
    time1 = time.time() - start_time
    from_cache1 = result1['performance']['from_cache']
    print(f"   耗时: {time1:.1f}秒, 来自缓存: {from_cache1}")
    
    # 第二次调用（使用缓存）
    print("\n2️⃣ 第二次调用（读取缓存）...")
    start_time = time.time()
    result2 = review_content_optimized(
        TEST_CONTENT,
        enable_engagement=False,
        use_cache=True
    )
    time2 = time.time() - start_time
    from_cache2 = result2['performance']['from_cache']
    print(f"   耗时: {time2:.1f}秒, 来自缓存: {from_cache2}")
    
    # 缓存统计
    stats = get_review_cache_stats()
    
    print(f"\n📊 缓存统计：")
    print(f"   命中率: {stats['hit_rate']}")
    print(f"   命中次数: {stats['hits']}")
    print(f"   未命中次数: {stats['misses']}")
    print(f"   总请求: {stats['total_requests']}")
    
    speedup = time1 / time2 if time2 > 0 else 0
    print(f"\n⚡ 性能提升：")
    print(f"   第一次: {time1:.2f}秒")
    print(f"   第二次: {time2:.2f}秒")
    print(f"   加速比: {speedup:.1f}x")
    
    return {
        "first_time": time1,
        "second_time": time2,
        "speedup": speedup,
        "stats": stats
    }


def test_comparison():
    """对比测试：串行 vs 并行"""
    print("\n" + "=" * 70)
    print("🧪 测试 4: 性能对比（串行 vs 并行）")
    print("=" * 70 + "\n")
    
    # 清除缓存
    clear_review_cache()
    
    print("📊 运行多次测试取平均值...\n")
    
    runs = 2  # 测试次数
    serial_times = []
    parallel_times = []
    
    for i in range(runs):
        print(f"第 {i+1}/{runs} 轮测试：")
        
        # 串行
        print("  ⏱️  串行测试...", end=" ")
        s_start = time.time()
        review_quality(TEST_CONTENT)
        review_compliance(TEST_CONTENT)
        s_time = time.time() - s_start
        serial_times.append(s_time)
        print(f"{s_time:.1f}秒")
        
        # 并行（不使用缓存）
        print("  ⚡ 并行测试...", end=" ")
        clear_review_cache()  # 每次清除缓存
        result = review_content_optimized(TEST_CONTENT, use_cache=False)
        p_time = result['performance']['elapsed_time']
        parallel_times.append(p_time)
        print(f"{p_time:.1f}秒")
        
        print()
    
    avg_serial = sum(serial_times) / len(serial_times)
    avg_parallel = sum(parallel_times) / len(parallel_times)
    improvement = ((avg_serial - avg_parallel) / avg_serial) * 100
    speedup = avg_serial / avg_parallel
    
    print("=" * 70)
    print("📊 性能对比结果")
    print("=" * 70)
    print(f"\n串行评审（原始）:")
    print(f"   平均耗时: {avg_serial:.2f}秒")
    print(f"\n并行评审（优化）:")
    print(f"   平均耗时: {avg_parallel:.2f}秒")
    print(f"\n⚡ 性能提升:")
    print(f"   时间减少: {improvement:.1f}%")
    print(f"   加速比: {speedup:.2f}x")
    print(f"   节省时间: {avg_serial - avg_parallel:.2f}秒")
    
    return {
        "serial_avg": avg_serial,
        "parallel_avg": avg_parallel,
        "improvement": improvement,
        "speedup": speedup
    }


def main():
    """运行所有测试"""
    print("\n" + "=" * 70)
    print("🚀 性能优化测试套件")
    print("=" * 70)
    
    results = {}
    
    # 测试 1: 串行评审
    results['serial'] = test_serial_review()
    
    # 测试 2: 并行评审
    results['parallel'] = test_parallel_review()
    
    # 测试 3: 缓存效果
    results['cache'] = test_cached_review()
    
    # 测试 4: 性能对比
    results['comparison'] = test_comparison()
    
    # 最终总结
    print("\n" + "=" * 70)
    print("📊 测试总结")
    print("=" * 70 + "\n")
    
    comp = results['comparison']
    cache = results['cache']
    
    print("✅ 所有测试完成！\n")
    
    print("🎯 关键发现：")
    print(f"   1. 并行评审比串行快 {comp['improvement']:.1f}%")
    print(f"   2. 缓存命中可加速 {cache['speedup']:.1f}x")
    print(f"   3. 综合优化可节省 {comp['serial_avg'] - comp['parallel_avg']:.1f}秒/次")
    
    print(f"\n💰 成本节省：")
    print(f"   串行评审: {comp['serial_avg']:.1f}秒 → 并行评审: {comp['parallel_avg']:.1f}秒")
    print(f"   首次评审: {cache['first_time']:.1f}秒 → 缓存命中: {cache['second_time']:.2f}秒")
    
    print(f"\n🎉 性能优化成功！")
    print(f"   ⚡ 速度提升: {comp['speedup']:.2f}x")
    print(f"   💾 缓存效果: {cache['speedup']:.1f}x")
    print(f"   ⏱️  总体改善: 显著")
    
    print()


if __name__ == "__main__":
    main()

