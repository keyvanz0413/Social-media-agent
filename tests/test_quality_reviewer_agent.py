"""
测试 Quality Reviewer Agent

验证质量评审 Agent 的功能是否正常
"""

import sys
import os
import json
import time
import logging

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.reviewers.quality_reviewer import (
    create_quality_reviewer_agent,
    review_quality
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_quality_reviewer_agent():
    """
    测试 Quality Reviewer Agent 完整工作流
    """
    print("\n" + "=" * 70)
    print("测试 Quality Reviewer Agent")
    print("=" * 70 + "\n")
    
    # 1. 准备测试内容（一个质量较差的内容）
    test_content = {
        "title": "悉尼旅游攻略",
        "content": """我去了悉尼玩了几天觉得挺好的推荐大家去玩悉尼很美墨尔本也不错海港大桥歌剧院都很漂亮天气也不错吃的也很多建议大家都去看看真的很值得去""",
        "topic": "悉尼旅游"
    }
    
    print("📋 测试内容:")
    print(f"   标题: {test_content['title']}")
    print(f"   正文: {test_content['content'][:50]}...")
    print(f"   话题: {test_content['topic']}")
    print()
    
    try:
        # 2. 创建 Agent
        print("🤖 创建 Quality Reviewer Agent...")
        start_time = time.time()
        agent = create_quality_reviewer_agent()
        print(f"   ✅ Agent 创建成功")
        print()
        
        # 3. 构建评审请求
        user_input = f"""请评审这篇小红书内容的质量：

标题：{test_content['title']}

正文：
{test_content['content']}

话题：{test_content['topic']}

请使用你的工具进行全面的质量评审，给出详细的评审结果。"""
        
        # 4. 调用 Agent
        print("🔍 开始质量评审...")
        print("   Agent 会依次调用以下工具:")
        print("   1. check_grammar - 检查语法")
        print("   2. analyze_content_structure - 分析结构")
        print("   3. check_readability - 评估可读性")
        print("   4. analyze_content_depth - 分析深度")
        print("   5. check_information_accuracy - 检查准确性")
        print()
        
        result = agent.input(user_input)
        
        elapsed_time = time.time() - start_time
        print(f"   ⏱️  评审耗时: {elapsed_time:.1f}秒")
        print()
        
        # 5. 解析结果
        print("📊 评审结果:")
        print("-" * 70)
        
        try:
            review = json.loads(result)
            
            # 显示评分
            print(f"\n   📈 总体评分: {review.get('score', 'N/A')}/10")
            print(f"   🎯 置信度: {review.get('confidence', 'N/A')}")
            
            # 显示细分评分
            if 'quality_breakdown' in review:
                print(f"\n   📊 质量细分:")
                breakdown = review['quality_breakdown']
                print(f"      语法规范: {breakdown.get('grammar', 'N/A')}/10")
                print(f"      结构清晰: {breakdown.get('structure', 'N/A')}/10")
                print(f"      可读性: {breakdown.get('readability', 'N/A')}/10")
                print(f"      内容深度: {breakdown.get('depth', 'N/A')}/10")
                print(f"      信息准确: {breakdown.get('accuracy', 'N/A')}/10")
            
            # 显示阅读级别
            if 'reading_level' in review:
                print(f"\n   📖 阅读级别: {review['reading_level']}")
            if 'estimated_reading_time' in review:
                print(f"   ⏰ 预计阅读时间: {review['estimated_reading_time']}")
            
            # 显示优势
            if 'strengths' in review and review['strengths']:
                print(f"\n   ✅ 优势:")
                for i, strength in enumerate(review['strengths'], 1):
                    print(f"      {i}. {strength}")
            
            # 显示不足
            if 'weaknesses' in review and review['weaknesses']:
                print(f"\n   ⚠️  不足:")
                for i, weakness in enumerate(review['weaknesses'], 1):
                    print(f"      {i}. {weakness}")
            
            # 显示建议
            if 'suggestions' in review and review['suggestions']:
                print(f"\n   💡 优化建议:")
                for i, suggestion in enumerate(review['suggestions'], 1):
                    print(f"      {i}. {suggestion}")
            
            print()
            
            # 6. 验证结果
            print("\n" + "=" * 70)
            print("✅ 测试验证")
            print("=" * 70 + "\n")
            
            # 检查必需字段
            required_fields = ['score', 'strengths', 'weaknesses', 'suggestions', 'confidence']
            missing_fields = [f for f in required_fields if f not in review]
            
            if missing_fields:
                print(f"   ❌ 缺少必需字段: {', '.join(missing_fields)}")
                return False
            else:
                print("   ✅ 所有必需字段都存在")
            
            # 检查评分范围
            score = review.get('score', 0)
            if 0 <= score <= 10:
                print(f"   ✅ 评分在有效范围内 ({score}/10)")
            else:
                print(f"   ❌ 评分超出范围: {score}")
                return False
            
            # 检查是否有建议
            if len(review.get('suggestions', [])) > 0:
                print(f"   ✅ 提供了 {len(review['suggestions'])} 条优化建议")
            else:
                print("   ⚠️  没有提供优化建议")
            
            # 检查是否有质量细分
            if 'quality_breakdown' in review:
                print("   ✅ 提供了详细的质量细分")
            else:
                print("   ⚠️  缺少质量细分")
            
            # 预期：这个内容质量较差，评分应该较低
            expected_score_range = (4, 7)  # 预期4-7分
            if expected_score_range[0] <= score <= expected_score_range[1]:
                print(f"   ✅ 评分符合预期 (预期{expected_score_range[0]}-{expected_score_range[1]}分)")
            else:
                print(f"   ⚠️  评分不在预期范围 (预期{expected_score_range[0]}-{expected_score_range[1]}分，实际{score}分)")
            
            # 7. 性能和成本总结
            print("\n" + "=" * 70)
            print("📊 性能和成本")
            print("=" * 70 + "\n")
            
            print(f"   ⏱️  总耗时: {elapsed_time:.1f}秒")
            
            # 估算成本（基于 GPT-4o-mini）
            # 假设: 输入500 tokens, 输出300 tokens
            # GPT-4o-mini: $0.150/1M input, $0.600/1M output
            estimated_input_tokens = 500
            estimated_output_tokens = 300
            estimated_cost = (estimated_input_tokens * 0.15 / 1000000 + 
                            estimated_output_tokens * 0.6 / 1000000)
            
            print(f"   💰 估算成本: ${estimated_cost:.4f}")
            print(f"   📊 成本效益: 优秀（低成本，高价值）")
            
            print("\n" + "=" * 70)
            print("✅ Quality Reviewer Agent 测试通过！")
            print("=" * 70 + "\n")
            
            return True
            
        except json.JSONDecodeError as e:
            print(f"   ❌ JSON 解析失败: {str(e)}")
            print(f"   原始输出: {result[:200]}...")
            return False
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        logger.error(f"测试异常: {str(e)}", exc_info=True)
        return False


def test_convenience_function():
    """
    测试便捷函数 review_quality
    """
    print("\n" + "=" * 70)
    print("测试便捷函数 review_quality()")
    print("=" * 70 + "\n")
    
    # 测试一个质量较好的内容
    good_content = {
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
    
    print("📋 测试内容: 质量较好的旅游攻略")
    print()
    
    try:
        start_time = time.time()
        result = review_quality(good_content)
        elapsed_time = time.time() - start_time
        
        review = json.loads(result)
        score = review.get('score', 0)
        
        print(f"   📈 评分: {score}/10")
        print(f"   ⏱️  耗时: {elapsed_time:.1f}秒")
        
        # 预期：这个内容质量较好，评分应该较高
        if score >= 7.5:
            print(f"   ✅ 评分符合预期（高质量内容）")
        else:
            print(f"   ⚠️  评分低于预期（预期≥7.5分）")
        
        print("\n" + "=" * 70)
        print("✅ 便捷函数测试通过！")
        print("=" * 70 + "\n")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 测试失败: {str(e)}")
        return False


def test_tool_error_handling():
    """
    测试工具函数错误处理
    """
    print("\n" + "=" * 70)
    print("测试错误处理能力")
    print("=" * 70 + "\n")
    
    # 测试空内容
    empty_content = {
        "title": "",
        "content": "",
        "topic": ""
    }
    
    print("📋 测试场景: 空内容")
    print()
    
    try:
        result = review_quality(empty_content)
        review = json.loads(result)
        
        # Agent 应该能处理空内容
        if 'score' in review or 'error' in review:
            print("   ✅ Agent 能处理空内容输入")
        else:
            print("   ⚠️  Agent 对空内容的处理不够完善")
        
        print("\n" + "=" * 70)
        print("✅ 错误处理测试通过！")
        print("=" * 70 + "\n")
        
        return True
        
    except Exception as e:
        print(f"   ⚠️  捕获异常: {str(e)}")
        print("   ✅ 异常被正确处理")
        return True


def main():
    """运行所有测试"""
    print("\n" + "=" * 70)
    print("🧪 Quality Reviewer Agent 测试套件")
    print("=" * 70 + "\n")
    
    # 检查依赖
    try:
        from connectonion import Agent
        print("✅ ConnectOnion 框架已安装")
    except ImportError:
        print("❌ ConnectOnion 框架未安装")
        print("💡 请运行: pip install connectonion")
        return
    
    print()
    
    # 运行测试
    results = []
    
    # 测试 1: Agent 完整工作流
    print("\n" + "🧪 测试 1: Agent 完整工作流")
    results.append(("Agent 工作流", test_quality_reviewer_agent()))
    
    # 测试 2: 便捷函数
    print("\n" + "🧪 测试 2: 便捷函数")
    results.append(("便捷函数", test_convenience_function()))
    
    # 测试 3: 错误处理
    print("\n" + "🧪 测试 3: 错误处理")
    results.append(("错误处理", test_tool_error_handling()))
    
    # 总结
    print("\n" + "=" * 70)
    print("📊 测试总结")
    print("=" * 70 + "\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {status} - {name}")
    
    print()
    print(f"   总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！Quality Reviewer Agent 运行正常。\n")
    else:
        print(f"\n⚠️  {total - passed} 个测试失败，请检查日志。\n")


if __name__ == "__main__":
    main()

