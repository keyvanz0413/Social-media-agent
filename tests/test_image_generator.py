"""
测试图片生成工具
"""

import json
import logging
from pathlib import Path
import sys

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.image_generator import (
    generate_images_for_content,
    generate_images_from_draft,
    _extract_search_keywords
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_basic_image_generation():
    """测试基本的图片生成功能"""
    print("\n" + "=" * 80)
    print("测试 1: 基本图片生成（Unsplash）")
    print("=" * 80)
    
    # 测试数据
    image_suggestions = json.dumps([
        {
            "description": "悉尼歌剧院日落景色",
            "purpose": "展示地标",
            "position": 1
        },
        {
            "description": "清澈的海滩和蓝天",
            "purpose": "展示自然风光",
            "position": 2
        }
    ], ensure_ascii=False)
    
    # 生成图片
    result_str = generate_images_for_content(
        image_suggestions=image_suggestions,
        topic="悉尼旅游",
        count=2,
        method="unsplash",
        save_to_disk=True
    )
    
    # 解析结果
    result = json.loads(result_str)
    
    print(f"\n✅ 生成结果: {result.get('success')}")
    print(f"📊 生成方法: {result.get('method')}")
    print(f"🖼️  图片数量: {result.get('count')}")
    
    if result.get("success"):
        images = result.get("images", [])
        for idx, img in enumerate(images):
            print(f"\n图片 {idx + 1}:")
            print(f"  - 描述: {img.get('description')}")
            print(f"  - 路径: {img.get('path')}")
            print(f"  - URL: {img.get('url')}")
            print(f"  - 来源: {img.get('source')}")
            
            # 检查文件是否存在
            if img.get('path'):
                path = Path(img['path'])
                if path.exists():
                    print(f"  - ✅ 文件已保存 (大小: {path.stat().st_size / 1024:.2f} KB)")
                else:
                    print(f"  - ❌ 文件不存在")
    else:
        print(f"❌ 生成失败: {result.get('error')}")
    
    return result.get("success", False)


def test_from_draft():
    """测试从草稿生成图片"""
    print("\n" + "=" * 80)
    print("测试 2: 从草稿生成图片")
    print("=" * 80)
    
    # 使用实际的草稿ID（从之前的测试）
    draft_id = "20251102_234551_悉尼旅游"
    
    print(f"使用草稿: {draft_id}")
    
    result_str = generate_images_from_draft(
        draft_id=draft_id,
        method="unsplash",
        count=3
    )
    
    result = json.loads(result_str)
    
    print(f"\n✅ 生成结果: {result.get('success')}")
    
    if result.get("success"):
        images = result.get("images", [])
        print(f"🖼️  生成了 {len(images)} 张图片")
        
        for idx, img in enumerate(images):
            print(f"\n图片 {idx + 1}:")
            print(f"  - 描述: {img.get('description')}")
            print(f"  - 路径: {img.get('path')}")
            
        # 显示可用于发布的图片路径列表
        image_paths = [img.get('path') for img in images if img.get('path')]
        print(f"\n📋 可用于发布的图片路径列表:")
        print(json.dumps(image_paths, ensure_ascii=False, indent=2))
    else:
        print(f"❌ 生成失败: {result.get('error')}")
        print(f"💡 提示: 确保草稿文件存在: {draft_id}.json")
    
    return result.get("success", False)


def test_keyword_extraction():
    """测试关键词提取功能"""
    print("\n" + "=" * 80)
    print("测试 3: 关键词提取")
    print("=" * 80)
    
    test_cases = [
        ("悉尼歌剧院日落景色", "悉尼旅游"),
        ("Wattamolla Beach清澈海水与沙滩全景", "海滩旅游"),
        ("中国友谊花园的廊桥与湖水倒影", "园林景观")
    ]
    
    for description, topic in test_cases:
        print(f"\n描述: {description}")
        print(f"主题: {topic}")
        
        # 注意：这个功能需要 LLM API，可能会失败
        try:
            keywords = _extract_search_keywords(description, topic)
            print(f"关键词: {keywords}")
        except Exception as e:
            print(f"❌ 提取失败: {str(e)}")


def test_different_methods():
    """测试不同的图片生成方法"""
    print("\n" + "=" * 80)
    print("测试 4: 不同的图片生成方法")
    print("=" * 80)
    
    image_suggestions = json.dumps([
        {
            "description": "beautiful beach sunset",
            "purpose": "测试",
            "position": 1
        }
    ], ensure_ascii=False)
    
    methods = ["unsplash"]  # 只测试 unsplash，其他方法需要配置
    
    for method in methods:
        print(f"\n测试方法: {method}")
        
        result_str = generate_images_for_content(
            image_suggestions=image_suggestions,
            topic="测试",
            count=1,
            method=method,
            save_to_disk=False  # 不保存，只测试API调用
        )
        
        result = json.loads(result_str)
        
        if result.get("success"):
            print(f"  ✅ {method} 测试通过")
        else:
            print(f"  ❌ {method} 测试失败: {result.get('error')}")


def main():
    """运行所有测试"""
    print("\n🧪 图片生成工具测试套件")
    print("=" * 80)
    
    results = []
    
    # 测试 1: 基本图片生成
    try:
        success = test_basic_image_generation()
        results.append(("基本图片生成", success))
    except Exception as e:
        logger.error(f"测试 1 失败: {str(e)}", exc_info=True)
        results.append(("基本图片生成", False))
    
    # 测试 2: 从草稿生成（可选，需要已有草稿）
    try:
        success = test_from_draft()
        results.append(("从草稿生成图片", success))
    except Exception as e:
        logger.error(f"测试 2 失败: {str(e)}", exc_info=True)
        results.append(("从草稿生成图片", False))
    
    # 测试 3: 关键词提取（可选，需要 LLM API）
    # test_keyword_extraction()
    
    # 测试 4: 不同方法（可选）
    # test_different_methods()
    
    # 汇总结果
    print("\n" + "=" * 80)
    print("📊 测试汇总")
    print("=" * 80)
    
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{test_name}: {status}")
    
    # 总体结果
    all_passed = all(success for _, success in results)
    
    print("\n" + "=" * 80)
    if all_passed:
        print("🎉 所有测试通过！")
    else:
        print("⚠️  部分测试失败，请检查日志")
    print("=" * 80)
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

