"""
Quality Reviewer Agent 使用示例

展示如何使用 Quality Reviewer Agent 评审内容质量
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.reviewers.quality_reviewer import review_quality
import json


def example_1_basic_usage():
    """
    示例 1: 基本使用
    
    评审一篇质量较差的内容
    """
    print("\n" + "=" * 70)
    print("示例 1: 基本使用 - 评审质量较差的内容")
    print("=" * 70 + "\n")
    
    content = {
        "title": "旅游攻略",
        "content": "我去了悉尼玩了几天觉得挺好的推荐大家去玩悉尼很美墨尔本也不错海港大桥歌剧院都很漂亮天气也不错吃的也很多建议大家都去看看真的很值得去",
        "topic": "悉尼旅游"
    }
    
    print("📋 待评审内容:")
    print(f"   标题: {content['title']}")
    print(f"   正文: {content['content'][:50]}...")
    print(f"   话题: {content['topic']}")
    print()
    
    # 调用评审
    result = review_quality(content)
    review = json.loads(result)
    
    # 显示结果
    print(f"📈 质量评分: {review['score']}/10")
    print(f"\n💡 优化建议:")
    for i, suggestion in enumerate(review.get('suggestions', []), 1):
        print(f"   {i}. {suggestion}")


def example_2_good_content():
    """
    示例 2: 高质量内容
    
    评审一篇质量较好的内容
    """
    print("\n" + "=" * 70)
    print("示例 2: 评审高质量内容")
    print("=" * 70 + "\n")
    
    content = {
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
        "topic": "悉尼旅游"
    }
    
    print("📋 待评审内容: 质量较好的旅游攻略")
    print()
    
    # 调用评审
    result = review_quality(content)
    review = json.loads(result)
    
    # 显示结果
    print(f"📈 质量评分: {review['score']}/10")
    print(f"\n✅ 优势:")
    for i, strength in enumerate(review.get('strengths', []), 1):
        print(f"   {i}. {strength}")
    
    if review.get('quality_breakdown'):
        print(f"\n📊 质量细分:")
        breakdown = review['quality_breakdown']
        print(f"   语法规范: {breakdown.get('grammar', 'N/A')}/10")
        print(f"   结构清晰: {breakdown.get('structure', 'N/A')}/10")
        print(f"   可读性: {breakdown.get('readability', 'N/A')}/10")
        print(f"   内容深度: {breakdown.get('depth', 'N/A')}/10")
        print(f"   信息准确: {breakdown.get('accuracy', 'N/A')}/10")


def example_3_detailed_analysis():
    """
    示例 3: 详细分析
    
    展示所有评审维度
    """
    print("\n" + "=" * 70)
    print("示例 3: 详细质量分析")
    print("=" * 70 + "\n")
    
    content = {
        "title": "最好的旅游攻略",
        "content": """我觉得悉尼是澳洲最好的城市一定要去看看歌剧院绝对是最美的建筑保证你会爱上这里完美的旅游体验百分之百满意""",
        "topic": "悉尼旅游"
    }
    
    print("📋 待评审内容: 包含多个问题的内容")
    print()
    
    # 调用评审
    result = review_quality(content)
    review = json.loads(result)
    
    # 显示完整结果
    print(f"📈 总体评分: {review['score']}/10")
    print(f"🎯 置信度: {review.get('confidence', 'N/A')}")
    print(f"📖 阅读级别: {review.get('reading_level', 'N/A')}")
    
    print(f"\n✅ 优势:")
    for i, strength in enumerate(review.get('strengths', []), 1):
        print(f"   {i}. {strength}")
    
    print(f"\n⚠️  不足:")
    for i, weakness in enumerate(review.get('weaknesses', []), 1):
        print(f"   {i}. {weakness}")
    
    print(f"\n💡 优化建议:")
    for i, suggestion in enumerate(review.get('suggestions', []), 1):
        print(f"   {i}. {suggestion}")


def example_4_batch_review():
    """
    示例 4: 批量评审
    
    评审多篇内容
    """
    print("\n" + "=" * 70)
    print("示例 4: 批量评审多篇内容")
    print("=" * 70 + "\n")
    
    contents = [
        {
            "title": "悉尼一日游",
            "content": "今天去了悉尼。",
            "topic": "悉尼旅游"
        },
        {
            "title": "悉尼旅游攻略｜详细版",
            "content": """第一次来悉尼，给大家分享一些实用建议！

✨ 必去景点
1. 悉尼歌剧院（门票42澳元，建议提前预约）
2. 海港大桥（攀爬268澳元，体验超棒）
3. 邦迪海滩（免费，记得带防晒霜）

💰 预算参考
住宿：100-200澳元/晚
餐饮：30-80澳元/餐
交通：Opal卡，日票18澳元

⏰ 最佳季节
9-11月春季，天气舒适，游客较少

有问题欢迎评论区交流！🎉""",
            "topic": "悉尼旅游"
        }
    ]
    
    for i, content in enumerate(contents, 1):
        print(f"\n📋 内容 {i}: {content['title']}")
        
        result = review_quality(content)
        review = json.loads(result)
        
        score = review['score']
        print(f"   评分: {score}/10")
        
        if score >= 8:
            print(f"   状态: ✅ 高质量，可以发布")
        elif score >= 6:
            print(f"   状态: ⚠️  需要优化")
        else:
            print(f"   状态: ❌ 质量较差，需要重写")


def main():
    """运行所有示例"""
    print("\n" + "=" * 70)
    print("🎯 Quality Reviewer Agent 使用示例")
    print("=" * 70)
    
    # 运行各个示例
    example_1_basic_usage()
    
    # 如果要运行所有示例，取消下面的注释
    # example_2_good_content()
    # example_3_detailed_analysis()
    # example_4_batch_review()
    
    print("\n" + "=" * 70)
    print("✅ 示例运行完成！")
    print("=" * 70 + "\n")
    
    print("💡 更多用法:")
    print("   - 取消注释 main() 中的其他示例来查看更多用法")
    print("   - 查看 agents/reviewers/quality_reviewer.py 了解实现细节")
    print("   - 查看 tests/test_quality_reviewer_agent.py 了解测试用例")
    print()


if __name__ == "__main__":
    main()

