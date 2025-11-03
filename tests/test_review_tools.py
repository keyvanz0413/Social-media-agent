"""
测试评审工具 (review_tools_v1.py)

运行方式：
    python tests/test_review_tools.py
    或
    pytest tests/test_review_tools.py -v
"""

import json
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 启用 Mock 模式（避免消耗真实 API）
import os
os.environ['MOCK_MODE'] = 'true'

from tools.review_tools_v1 import (
    review_content,
    review_engagement,
    review_quality,
    review_compliance,
    batch_review
)


def test_review_engagement():
    """测试互动潜力评审"""
    print("\n" + "=" * 60)
    print("测试：互动潜力评审")
    print("=" * 60)
    
    content_data = {
        "title": "🦘澳洲大洋路3天2夜攻略！人均不到3k",
        "content": """
        这次澳洲之旅真的太惊喜了！和大家分享一下我的3天2夜自驾攻略。
        
        第一天：墨尔本出发 → 大洋路起点
        - 早上8点出发，沿途风景绝美
        - 中午在小镇吃海鲜，新鲜又便宜
        
        第二天：十二门徒 → 返回墨尔本
        - 必看日落，太震撼了！
        - 记得提前预定酒店
        
        💰 费用：
        - 租车: $150/3天
        - 住宿: $200/2晚
        - 餐饮: $100
        - 门票: $50
        
        你们想知道更多细节吗？评论区告诉我！
        """
    }
    
    result_json = review_engagement(content_data, quality_level="balanced")
    result = json.loads(result_json)
    
    print(f"✅ 评审成功: {result['success']}")
    print(f"📊 评分: {result['data']['score']}/10")
    print(f"💪 优势: {result['data']['strengths']}")
    print(f"⚠️  不足: {result['data']['weaknesses']}")
    print(f"💡 建议: {result['data']['suggestions']}")
    
    assert result['success'] == True
    assert 0 <= result['data']['score'] <= 10
    print("\n✅ 互动潜力评审测试通过！")


def test_review_quality():
    """测试内容质量评审"""
    print("\n" + "=" * 60)
    print("测试：内容质量评审")
    print("=" * 60)
    
    content_data = {
        "title": "咖啡入门指南",
        "content": """
        咖啡是世界上最受欢迎的饮料之一。本文将介绍咖啡的基础知识。
        
        1. 咖啡豆种类
        - 阿拉比卡：口感细腻，酸度高
        - 罗布斯塔：苦味重，咖啡因高
        
        2. 冲泡方法
        - 手冲：保留原味
        - 意式：浓郁醇厚
        - 法压：方便快捷
        
        3. 品鉴技巧
        - 观察颜色
        - 闻取香气
        - 品尝味道
        
        希望这篇指南能帮助你更好地享受咖啡！
        """
    }
    
    result_json = review_quality(content_data, quality_level="balanced")
    result = json.loads(result_json)
    
    print(f"✅ 评审成功: {result['success']}")
    print(f"📊 评分: {result['data']['score']}/10")
    print(f"💪 优势: {result['data']['strengths']}")
    print(f"⚠️  不足: {result['data']['weaknesses']}")
    print(f"💡 建议: {result['data']['suggestions']}")
    
    assert result['success'] == True
    assert 0 <= result['data']['score'] <= 10
    print("\n✅ 内容质量评审测试通过！")


def test_review_compliance():
    """测试合规性评审"""
    print("\n" + "=" * 60)
    print("测试：合规性评审")
    print("=" * 60)
    
    # 测试正常内容
    good_content = {
        "title": "健康饮食小技巧",
        "content": "分享一些实用的健康饮食建议，帮助大家养成良好习惯。"
    }
    
    result_json = review_compliance(good_content, quality_level="balanced")
    result = json.loads(result_json)
    
    print("--- 正常内容评审 ---")
    print(f"✅ 评审成功: {result['success']}")
    print(f"📊 评分: {result['data']['score']}/10")
    print(f"🛡️  风险等级: {result['data']['risk_level']}")
    print(f"⚠️  问题: {result['data']['issues']}")
    
    assert result['success'] == True
    assert result['data']['score'] >= 8
    assert result['data']['risk_level'] == 'low'
    
    # 测试有问题的内容
    bad_content = {
        "title": "最好的减肥产品，绝对有效！",
        "content": "这是市场上最强的减肥药，100%见效！加我微信购买！"
    }
    
    result_json = review_compliance(bad_content, quality_level="balanced")
    result = json.loads(result_json)
    
    print("\n--- 问题内容评审 ---")
    print(f"✅ 评审成功: {result['success']}")
    print(f"📊 评分: {result['data']['score']}/10")
    print(f"🛡️  风险等级: {result['data']['risk_level']}")
    print(f"⚠️  问题: {result['data']['issues']}")
    
    assert result['success'] == True
    assert result['data']['score'] < 8
    assert len(result['data']['issues']) > 0
    
    print("\n✅ 合规性评审测试通过！")


def test_review_content_full():
    """测试完整的内容评审"""
    print("\n" + "=" * 60)
    print("测试：完整内容评审")
    print("=" * 60)
    
    content_data = {
        "title": "🌸京都赏樱攻略｜3天2夜超详细路线",
        "content": """
        今年樱花季去了趟京都，太美了！分享我的3天2夜路线~
        
        📅 Day 1：清水寺 → 二年坂 → 祇园
        - 早上7点到清水寺，人少景美
        - 二年坂有很多特色小店
        - 晚上在祇园遇见艺伎！
        
        📅 Day 2：岚山 → 金阁寺
        - 竹林真的太仙了！
        - 金阁寺日落超美
        
        📅 Day 3：伏见稻荷 → 奈良
        - 千本鸟居必打卡
        - 喂小鹿太治愈了
        
        💰 花费明细：
        - 机票: ¥2000
        - 住宿: ¥800/晚 × 2 = ¥1600
        - 交通: ¥500
        - 餐饮: ¥800
        - 门票: ¥200
        总计: ¥5100
        
        🎁 实用Tips：
        1. 提前买JR Pass
        2. 早起避开人群
        3. 下载Google Maps
        
        有问题欢迎评论区问我呀~💕
        """,
        "hashtags": ["京都旅游", "樱花季", "日本旅游"]
    }
    
    result_json = review_content(content_data, quality_level="balanced")
    result = json.loads(result_json)
    
    print(f"✅ 评审成功: {result['success']}")
    print(f"\n📊 总分: {result['data']['overall_score']}/10")
    print(f"🎯 是否通过: {'✅ 通过' if result['data']['passed'] else '❌ 不通过'}")
    print(f"🚦 通过阈值: {result['data']['pass_threshold']}")
    
    print(f"\n--- 各维度评分 ---")
    reviews = result['data']['reviews']
    print(f"💬 互动潜力: {reviews['engagement']['score']}/10")
    print(f"   优势: {reviews['engagement']['strengths'][:2]}")
    
    print(f"\n📝 内容质量: {reviews['quality']['score']}/10")
    print(f"   优势: {reviews['quality']['strengths'][:2]}")
    
    print(f"\n🛡️  合规性: {reviews['compliance']['score']}/10")
    print(f"   风险等级: {reviews['compliance']['risk_level']}")
    
    print(f"\n💡 优化建议:")
    for idx, suggestion in enumerate(result['data']['suggestions'][:5], 1):
        print(f"   {idx}. {suggestion}")
    
    assert result['success'] == True
    assert 'overall_score' in result['data']
    assert 'reviews' in result['data']
    assert all(k in result['data']['reviews'] for k in ['engagement', 'quality', 'compliance'])
    
    print("\n✅ 完整内容评审测试通过！")


def test_batch_review():
    """测试批量评审"""
    print("\n" + "=" * 60)
    print("测试：批量评审")
    print("=" * 60)
    
    content_list = [
        {
            "title": "早餐推荐｜快手营养早餐",
            "content": "分享几款10分钟就能做好的营养早餐..."
        },
        {
            "title": "健身小白入门指南",
            "content": "新手健身需要注意什么？这篇文章告诉你..."
        },
        {
            "title": "读书笔记｜《原则》",
            "content": "最近读了《原则》这本书，收获很大..."
        }
    ]
    
    result_json = batch_review(content_list, quality_level="fast")
    result = json.loads(result_json)
    
    print(f"✅ 批量评审成功: {result['success']}")
    print(f"📊 评审数量: {result['data']['total']}")
    
    for item in result['data']['results']:
        print(f"\n--- 内容 {item['index'] + 1} ---")
        print(f"标题: {item['title']}")
        print(f"总分: {item['review']['data']['overall_score']}/10")
        print(f"通过: {'✅' if item['review']['data']['passed'] else '❌'}")
    
    assert result['success'] == True
    assert result['data']['total'] == 3
    
    print("\n✅ 批量评审测试通过！")


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("🧪 开始测试评审工具")
    print("=" * 60)
    
    try:
        test_review_engagement()
        test_review_quality()
        test_review_compliance()
        test_review_content_full()
        test_batch_review()
        
        print("\n" + "=" * 60)
        print("🎉 所有测试通过！")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ 测试失败: {str(e)}")
        raise
    except Exception as e:
        print(f"\n❌ 测试出错: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()

