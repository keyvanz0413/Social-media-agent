"""
缓存功能测试

测试缓存管理器的各项功能
"""

import sys
import os
import time
import json

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.cache_manager import CacheManager, get_cache_manager, cache_key


def test_basic_cache():
    """测试基本缓存功能"""
    print("\n" + "=" * 70)
    print("🧪 测试 1: 基本缓存功能")
    print("=" * 70 + "\n")
    
    cache = CacheManager()
    
    # 测试 set 和 get
    print("1️⃣ 测试 set/get...")
    cache.set("test_key", "test_value", ttl=10)
    value = cache.get("test_key")
    assert value == "test_value", "缓存值不匹配"
    print("   ✅ set/get 正常")
    
    # 测试不存在的键
    print("2️⃣ 测试不存在的键...")
    value = cache.get("non_existent_key")
    assert value is None, "不存在的键应返回None"
    print("   ✅ 返回 None 正常")
    
    # 测试删除
    print("3️⃣ 测试 delete...")
    cache.delete("test_key")
    value = cache.get("test_key")
    assert value is None, "删除后应返回None"
    print("   ✅ delete 正常")
    
    print("\n✅ 基本缓存功能测试通过\n")
    return True


def test_cache_expiration():
    """测试缓存过期"""
    print("\n" + "=" * 70)
    print("🧪 测试 2: 缓存过期（TTL）")
    print("=" * 70 + "\n")
    
    cache = CacheManager()
    
    # 设置2秒过期的缓存
    print("1️⃣ 设置2秒过期的缓存...")
    cache.set("expiring_key", "will_expire", ttl=2)
    
    # 立即获取
    print("2️⃣ 立即获取...")
    value = cache.get("expiring_key")
    assert value == "will_expire", "应该能获取到值"
    print(f"   ✅ 获取成功: {value}")
    
    # 等待3秒
    print("3️⃣ 等待3秒后再获取...")
    time.sleep(3)
    value = cache.get("expiring_key")
    assert value is None, "过期后应返回None"
    print(f"   ✅ 返回 None（已过期）")
    
    # 测试永久缓存
    print("4️⃣ 测试永久缓存（TTL=0）...")
    cache.set("permanent_key", "永久数据", ttl=0)
    time.sleep(2)
    value = cache.get("permanent_key")
    assert value == "永久数据", "永久缓存不应过期"
    print(f"   ✅ 永久缓存正常: {value}")
    
    print("\n✅ 缓存过期测试通过\n")
    return True


def test_cache_statistics():
    """测试缓存统计"""
    print("\n" + "=" * 70)
    print("🧪 测试 3: 缓存统计")
    print("=" * 70 + "\n")
    
    cache = CacheManager()
    cache.clear()  # 清空以获得准确统计
    
    # 重置统计
    cache.stats = {"hits": 0, "misses": 0, "sets": 0}
    
    print("1️⃣ 执行一系列操作...")
    # 设置3个缓存
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    cache.set("key3", "value3")
    
    # 命中2次
    cache.get("key1")
    cache.get("key2")
    
    # 未命中2次
    cache.get("non_existent_1")
    cache.get("non_existent_2")
    
    # 再次命中
    cache.get("key1")
    
    print("2️⃣ 查看统计...")
    stats = cache.get_stats()
    
    print(f"   设置次数: {stats['sets']}")
    print(f"   命中次数: {stats['hits']}")
    print(f"   未命中次数: {stats['misses']}")
    print(f"   命中率: {stats['hit_rate']}")
    print(f"   内存缓存项: {stats['memory_items']}")
    
    # 验证
    assert stats['sets'] == 3, f"设置次数应该是3，实际{stats['sets']}"
    assert stats['hits'] == 3, f"命中次数应该是3，实际{stats['hits']}"
    assert stats['misses'] == 2, f"未命中次数应该是2，实际{stats['misses']}"
    assert stats['hit_rate'] == "60.0%", f"命中率应该是60.0%，实际{stats['hit_rate']}"
    
    print("\n✅ 缓存统计测试通过\n")
    return True


def test_cache_key_generation():
    """测试缓存键生成"""
    print("\n" + "=" * 70)
    print("🧪 测试 4: 缓存键生成")
    print("=" * 70 + "\n")
    
    # 测试各种参数组合
    print("1️⃣ 测试不同参数组合...")
    
    key1 = cache_key("search", "悉尼旅游")
    print(f"   key1: {key1}")
    
    key2 = cache_key("search", "悉尼旅游", limit=5)
    print(f"   key2: {key2}")
    
    key3 = cache_key("search", "悉尼旅游", limit=5, sort="hot")
    print(f"   key3: {key3}")
    
    # 验证相同参数生成相同的键
    print("\n2️⃣ 测试相同参数...")
    key4 = cache_key("search", "悉尼旅游", limit=5)
    assert key2 == key4, "相同参数应生成相同的键"
    print(f"   ✅ 相同参数生成相同键")
    
    # 验证不同参数生成不同的键
    print("\n3️⃣ 测试不同参数...")
    assert key1 != key2, "不同参数应生成不同的键"
    assert key2 != key3, "不同参数应生成不同的键"
    print(f"   ✅ 不同参数生成不同键")
    
    print("\n✅ 缓存键生成测试通过\n")
    return True


def test_memory_eviction():
    """测试内存淘汰机制"""
    print("\n" + "=" * 70)
    print("🧪 测试 5: 内存淘汰机制")
    print("=" * 70 + "\n")
    
    # 创建小容量缓存
    cache = CacheManager(max_memory_items=5)
    
    print("1️⃣ 添加10个缓存项（容量限制5个）...")
    for i in range(10):
        cache.set(f"item_{i}", f"value_{i}")
    
    stats = cache.get_stats()
    print(f"   内存缓存项: {stats['memory_items']}")
    
    # 验证淘汰
    assert stats['memory_items'] <= 5, f"内存缓存项应 ≤ 5，实际{stats['memory_items']}"
    print(f"   ✅ 淘汰机制正常（保留 ≤ 5项）")
    
    # 访问一些项增加命中次数
    print("\n2️⃣ 访问部分项增加命中次数...")
    for i in range(5, 10):
        cache.get(f"item_{i}")
    
    # 再添加新项，应该淘汰命中次数少的
    print("3️⃣ 添加新项...")
    cache.set("new_item", "new_value")
    
    stats = cache.get_stats()
    assert stats['memory_items'] <= 5, "淘汰后应保持限制"
    print(f"   ✅ 淘汰机制持续工作")
    
    print("\n✅ 内存淘汰测试通过\n")
    return True


def test_disk_persistence():
    """测试磁盘持久化"""
    print("\n" + "=" * 70)
    print("🧪 测试 6: 磁盘持久化")
    print("=" * 70 + "\n")
    
    # 创建第一个缓存实例
    print("1️⃣ 创建第一个缓存实例并保存数据...")
    cache1 = CacheManager()
    cache1.set("persistent_key", "persistent_value", ttl=3600)
    
    # 从内存中删除
    del cache1._memory_cache["persistent_key"]
    print("   已从内存中删除")
    
    # 获取应该从磁盘加载
    print("\n2️⃣ 从磁盘重新加载...")
    value = cache1.get("persistent_key")
    assert value == "persistent_value", "应该能从磁盘加载"
    print(f"   ✅ 从磁盘加载成功: {value}")
    
    # 创建第二个缓存实例
    print("\n3️⃣ 创建新的缓存实例...")
    cache2 = CacheManager()
    value = cache2.get("persistent_key")
    print(f"   ✅ 新实例能读取: {value}")
    
    # 清理
    cache2.delete("persistent_key")
    
    print("\n✅ 磁盘持久化测试通过\n")
    return True


def main():
    """运行所有测试"""
    print("\n" + "=" * 70)
    print("🧪 缓存功能测试套件")
    print("=" * 70 + "\n")
    
    results = []
    
    # 运行所有测试
    tests = [
        ("基本缓存功能", test_basic_cache),
        ("缓存过期", test_cache_expiration),
        ("缓存统计", test_cache_statistics),
        ("缓存键生成", test_cache_key_generation),
        ("内存淘汰", test_memory_eviction),
        ("磁盘持久化", test_disk_persistence)
    ]
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"   ❌ 测试失败: {str(e)}\n")
            results.append((name, False))
    
    # 总结
    print("\n" + "=" * 70)
    print("📊 测试总结")
    print("=" * 70 + "\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {status} - {name}")
    
    print(f"\n   总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有缓存测试通过！缓存系统运行正常。\n")
    else:
        print(f"\n⚠️  {total - passed} 个测试失败。\n")


if __name__ == "__main__":
    main()

