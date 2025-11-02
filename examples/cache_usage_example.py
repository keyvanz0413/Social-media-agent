"""
缓存使用示例

展示如何使用缓存功能提升性能
"""

import sys
import os
import time

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.cache_manager import get_cache_manager, cache_key, CacheManager
from utils.cached_mcp_client import get_cached_mcp_client
from tools.review_optimized import review_content_optimized, clear_review_cache, get_review_cache_stats
import json


def example_1_basic_cache():
    """
    示例 1: 基本缓存使用
    
    展示如何使用缓存管理器
    """
    print("\n" + "=" * 70)
    print("示例 1: 基本缓存使用")
    print("=" * 70 + "\n")
    
    # 获取缓存管理器
    cache = get_cache_manager()
    
    # 设置缓存
    print("1️⃣ 设置缓存...")
    cache.set("user_name", "小红书用户", ttl=3600)
    cache.set("user_age", 25, ttl=3600)
    print("   ✅ 缓存已设置")
    
    # 获取缓存
    print("\n2️⃣ 获取缓存...")
    name = cache.get("user_name")
    age = cache.get("user_age")
    print(f"   姓名: {name}")
    print(f"   年龄: {age}")
    
    # 删除缓存
    print("\n3️⃣ 删除缓存...")
    cache.delete("user_age")
    age = cache.get("user_age")
    print(f"   年龄（已删除）: {age}")
    
    # 查看统计
    print("\n4️⃣ 缓存统计...")
    stats = cache.get_stats()
    print(f"   命中次数: {stats['hits']}")
    print(f"   未命中次数: {stats['misses']}")
    print(f"   命中率: {stats['hit_rate']}")


def example_2_mcp_search_cache():
    """
    示例 2: MCP 搜索缓存
    
    展示如何缓存搜索结果
    """
    print("\n" + "=" * 70)
    print("示例 2: MCP 搜索缓存")
    print("=" * 70 + "\n")
    
    # 获取带缓存的 MCP 客户端
    client = get_cached_mcp_client(cache_ttl=1800)  # 30分钟缓存
    
    keyword = "悉尼旅游"
    
    # 第一次搜索（会调用 MCP API）
    print(f"1️⃣ 第一次搜索 '{keyword}'...")
    start = time.time()
    result1 = client.search_notes(keyword, limit=5)
    time1 = time.time() - start
    count1 = len(result1.get('feeds', []))
    print(f"   找到 {count1} 篇笔记")
    print(f"   耗时: {time1:.2f}秒")
    
    # 第二次搜索（使用缓存）
    print(f"\n2️⃣ 第二次搜索 '{keyword}'（应该使用缓存）...")
    start = time.time()
    result2 = client.search_notes(keyword, limit=5)
    time2 = time.time() - start
    count2 = len(result2.get('feeds', []))
    print(f"   找到 {count2} 篇笔记")
    print(f"   耗时: {time2:.2f}秒")
    
    # 对比
    speedup = time1 / time2 if time2 > 0 else float('inf')
    print(f"\n⚡ 性能提升:")
    print(f"   第一次: {time1:.2f}秒")
    print(f"   第二次: {time2:.2f}秒")
    print(f"   加速比: {speedup:.1f}x")
    
    # 缓存统计
    stats = client.get_cache_stats()
    print(f"\n📊 缓存统计:")
    print(f"   命中率: {stats.get('hit_rate', 'N/A')}")
    
    client.close()


def example_3_review_cache():
    """
    示例 3: 评审结果缓存
    
    展示如何缓存评审结果
    """
    print("\n" + "=" * 70)
    print("示例 3: 评审结果缓存")
    print("=" * 70 + "\n")
    
    # 清除旧缓存
    clear_review_cache()
    
    content = {
        "title": "悉尼旅游攻略｜3天2夜深度游✨",
        "content": "分享我的悉尼之旅！去了歌剧院、海港大桥...",
        "topic": "悉尼旅游"
    }
    
    # 第一次评审（会调用 Agent）
    print("1️⃣ 第一次评审...")
    start = time.time()
    result1 = review_content_optimized(content, use_cache=True)
    time1 = time.time() - start
    print(f"   综合评分: {result1['overall']['score']}/10")
    print(f"   耗时: {time1:.1f}秒")
    print(f"   来自缓存: {result1['performance']['from_cache']}")
    
    # 第二次评审（使用缓存）
    print("\n2️⃣ 第二次评审（相同内容）...")
    start = time.time()
    result2 = review_content_optimized(content, use_cache=True)
    time2 = time.time() - start
    print(f"   综合评分: {result2['overall']['score']}/10")
    print(f"   耗时: {time2:.2f}秒")
    print(f"   来自缓存: {result2['performance']['from_cache']}")
    
    # 对比
    speedup = time1 / time2 if time2 > 0 else float('inf')
    print(f"\n⚡ 性能提升:")
    print(f"   第一次: {time1:.1f}秒（执行评审）")
    print(f"   第二次: {time2:.2f}秒（读取缓存）")
    print(f"   加速比: {speedup:.0f}x")
    
    # 缓存统计
    stats = get_review_cache_stats()
    print(f"\n📊 缓存统计:")
    print(f"   命中率: {stats['hit_rate']}")
    print(f"   命中次数: {stats['hits']}")


def example_4_cache_ttl():
    """
    示例 4: 缓存过期
    
    展示缓存TTL（生存时间）的使用
    """
    print("\n" + "=" * 70)
    print("示例 4: 缓存过期（TTL）")
    print("=" * 70 + "\n")
    
    cache = get_cache_manager()
    
    # 设置短期缓存（2秒）
    print("1️⃣ 设置2秒过期的缓存...")
    cache.set("temp_data", "这是临时数据", ttl=2)
    
    # 立即获取
    print("2️⃣ 立即获取...")
    data = cache.get("temp_data")
    print(f"   结果: {data}")
    
    # 等待3秒
    print("\n3️⃣ 等待3秒后再获取...")
    time.sleep(3)
    data = cache.get("temp_data")
    print(f"   结果: {data} （应该是None，因为已过期）")
    
    # 设置永久缓存（TTL=0）
    print("\n4️⃣ 设置永久缓存（TTL=0）...")
    cache.set("permanent_data", "永久数据", ttl=0)
    
    time.sleep(2)
    data = cache.get("permanent_data")
    print(f"   2秒后获取: {data} （永不过期）")


def example_5_cache_management():
    """
    示例 5: 缓存管理
    
    展示缓存清理和统计
    """
    print("\n" + "=" * 70)
    print("示例 5: 缓存管理")
    print("=" * 70 + "\n")
    
    cache = get_cache_manager()
    
    # 添加一些缓存
    print("1️⃣ 添加多个缓存项...")
    for i in range(5):
        cache.set(f"item_{i}", f"value_{i}", ttl=3600)
    print(f"   已添加 5 个缓存项")
    
    # 查看统计
    print("\n2️⃣ 查看缓存统计...")
    stats = cache.get_stats()
    print(f"   内存缓存项: {stats['memory_items']}")
    print(f"   总请求数: {stats['total_requests']}")
    print(f"   命中率: {stats['hit_rate']}")
    
    # 清理过期缓存
    print("\n3️⃣ 清理过期缓存...")
    count = cache.cleanup_expired()
    print(f"   清理了 {count} 个过期缓存")
    
    # 清空所有缓存
    print("\n4️⃣ 清空所有缓存...")
    cache.clear()
    stats = cache.get_stats()
    print(f"   内存缓存项: {stats['memory_items']} （应该是0）")


def main():
    """运行所有示例"""
    print("\n" + "=" * 70)
    print("🎯 缓存使用示例")
    print("=" * 70)
    
    # 运行各个示例
    example_1_basic_cache()
    
    # 如果要运行所有示例，取消下面的注释
    # example_2_mcp_search_cache()  # 需要 MCP 服务运行
    # example_3_review_cache()      # 需要 API keys
    # example_4_cache_ttl()
    # example_5_cache_management()
    
    print("\n" + "=" * 70)
    print("✅ 示例运行完成！")
    print("=" * 70 + "\n")
    
    print("💡 更多用法:")
    print("   - 取消注释 main() 中的其他示例来查看更多用法")
    print("   - 查看 utils/cache_manager.py 了解实现细节")
    print("   - 查看 utils/cached_mcp_client.py 了解 MCP 缓存")
    print("   - 查看 tools/review_optimized.py 了解评审缓存")
    print()


if __name__ == "__main__":
    main()

