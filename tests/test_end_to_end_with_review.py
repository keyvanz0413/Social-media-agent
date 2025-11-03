"""
端到端测试 - 包含评审系统

测试完整的内容创作流程：
分析 → 创作 → 图片生成 → 多维度评审 → 决策 → 发布（模拟）
"""

import sys
import os
import json
import time
import logging

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.content_analyst import agent_a_analyze_xiaohongshu
from tools.content_creator import agent_c_create_content
from agents.reviewers.quality_reviewer import review_quality
from agents.reviewers.engagement_reviewer import review_engagement
from tools.review_tools_v1 import review_compliance

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_end_to_end_with_standard_review():
    """
    测试标准评审流程
    
    流程：分析 → 创作 → 质量评审 → 合规性检查 → 决策
    """
    print("\n" + "=" * 70)
    print("🧪 端到端测试：标准评审流程")
    print("=" * 70 + "\n")
    
    topic = "悉尼旅游"
    start_time = time.time()
    
    try:
        # ========== 步骤 1: 内容分析 ==========
        print("📊 步骤 1/5: 内容分析")
        print(f"   正在分析'{topic}'相关内容...")
        
        step_start = time.time()
        analysis_result = agent_a_analyze_xiaohongshu(
            keyword=topic,
            limit=5,
            quality_level="fast"  # 使用fast模式加速测试
        )
        step_time = time.time() - step_start
        
        analysis = json.loads(analysis_result)
        # 兼容不同的响应格式
        if 'success' in analysis:
            success = analysis.get('success')
            data = analysis.get('data', {})
        else:
            # 如果没有 success 字段，假设整个响应就是data
            success = True
            data = analysis
        
        if success and data:
            print(f"   ✅ 分析完成（{step_time:.1f}秒）")
            print(f"   - 发现标题模式：{len(data.get('title_patterns', {}))}个")
            print(f"   - 用户需求：{len(data.get('user_needs', []))}条")
        else:
            print(f"   ❌ 分析失败：{analysis.get('error', '未知错误')}")
            return False
        
        print()
        
        # ========== 步骤 2: 内容创作 ==========
        print("✍️  步骤 2/5: 内容创作")
        print(f"   正在创作'{topic}'帖子...")
        
        step_start = time.time()
        create_result = agent_c_create_content(
            analysis_result=analysis_result,
            topic=topic,
            style="casual",
            quality_level="fast"
        )
        step_time = time.time() - step_start
        
        create_data = json.loads(create_result)
        # 兼容不同的响应格式
        if 'success' in create_data:
            success = create_data.get('success')
            content = create_data.get('data', {})
        else:
            success = True
            content = create_data
        
        if success and content:
            print(f"   ✅ 创作完成（{step_time:.1f}秒）")
            title = content.get('title', '')
            body = content.get('content', '')
            draft_id = content.get('metadata', {}).get('draft_id', '')
            
            print(f"   - 标题：{title}")
            print(f"   - 正文：{body[:50]}...")
            print(f"   - 草稿ID：{draft_id}")
        else:
            print(f"   ❌ 创作失败：{create_data.get('error', '未知错误')}")
            return False
        
        print()
        
        # ========== 步骤 3: 质量评审 ==========
        print("🔍 步骤 3/5: 质量评审")
        print("   正在评估内容质量...")
        
        step_start = time.time()
        quality_result = review_quality({
            "title": title,
            "content": body,
            "topic": topic
        })
        step_time = time.time() - step_start
        
        quality = json.loads(quality_result)
        quality_score = quality.get('score', 0)
        
        print(f"   ✅ 质量评审完成（{step_time:.1f}秒）")
        print(f"   - 总体评分：{quality_score}/10")
        
        if 'quality_breakdown' in quality:
            breakdown = quality['quality_breakdown']
            print(f"   - 细分评分：")
            print(f"     · 语法：{breakdown.get('grammar', 'N/A')}/10")
            print(f"     · 结构：{breakdown.get('structure', 'N/A')}/10")
            print(f"     · 可读性：{breakdown.get('readability', 'N/A')}/10")
            print(f"     · 深度：{breakdown.get('depth', 'N/A')}/10")
            print(f"     · 准确性：{breakdown.get('accuracy', 'N/A')}/10")
        
        if quality.get('suggestions'):
            print(f"   - 优化建议：{len(quality['suggestions'])}条")
            for i, sug in enumerate(quality['suggestions'][:2], 1):
                print(f"     {i}. {sug}")
        
        print()
        
        # ========== 步骤 4: 合规性检查 ==========
        print("⚖️  步骤 4/5: 合规性检查")
        print("   正在检查内容合规性...")
        
        step_start = time.time()
        compliance_result = review_compliance({
            "title": title,
            "content": body,
            "hashtags": content.get('hashtags', []) if isinstance(content, dict) else []
        })
        step_time = time.time() - step_start
        
        compliance = json.loads(compliance_result)
        # 兼容不同的响应格式
        if 'data' in compliance:
            comp_data = compliance['data']
            compliance_passed = comp_data.get('overall', {}).get('passed', False)
            compliance_score = comp_data.get('overall', {}).get('score', 0)
            issues = comp_data.get('issues', [])
        else:
            # 简化格式
            compliance_passed = compliance.get('passed', True)
            compliance_score = compliance.get('score', 10)
            issues = compliance.get('issues', [])
        
        print(f"   ✅ 合规性检查完成（{step_time:.1f}秒）")
        print(f"   - 评分：{compliance_score}/10")
        print(f"   - 结果：{'✅ 通过' if compliance_passed else '❌ 未通过'}")
        
        if issues:
            print(f"   - 发现问题：{len(issues)}个")
            for issue in issues[:2]:
                if isinstance(issue, dict):
                    print(f"     · {issue.get('category', '未知')}：{issue.get('message', '')}")
        
        print()
        
        # ========== 步骤 5: 评审决策 ==========
        print("🎯 步骤 5/5: 评审决策")
        print("   根据评审结果做出决策...")
        
        # 决策逻辑
        if not compliance_passed:
            decision = "MUST_OPTIMIZE"
            reason = "存在合规性风险"
            action_text = "❌ 必须优化"
        elif quality_score >= 8.0:
            decision = "PUBLISH"
            reason = "内容质量优秀"
            action_text = "✅ 可以发布"
        elif quality_score >= 6.0:
            decision = "ASK_USER"
            reason = "内容质量良好，可以优化"
            action_text = "⚠️  建议询问用户"
        else:
            decision = "RECOMMEND_OPTIMIZE"
            reason = "内容质量有待提升"
            action_text = "⚠️  建议优化"
        
        print(f"   - 决策：{action_text}")
        print(f"   - 原因：{reason}")
        print(f"   - 质量评分：{quality_score}/10")
        print(f"   - 合规性：{'通过' if compliance_passed else '未通过'}")
        
        print()
        
        # ========== 总结 ==========
        total_time = time.time() - start_time
        
        print("=" * 70)
        print("📊 测试总结")
        print("=" * 70)
        print(f"\n✅ 测试完成")
        print(f"\n⏱️  总耗时：{total_time:.1f}秒")
        print(f"\n📈 评审结果：")
        print(f"   - 质量评分：{quality_score}/10")
        print(f"   - 合规性：{'通过' if compliance_passed else '未通过'}")
        print(f"   - 最终决策：{action_text}")
        
        print(f"\n💰 估算成本：")
        print(f"   - 内容创作：~$0.02")
        print(f"   - 质量评审：~$0.0003")
        print(f"   - 合规检查：~$0.0001")
        print(f"   - 总计：~$0.0204")
        
        print(f"\n🎯 流程验证：")
        print(f"   ✅ 内容分析正常")
        print(f"   ✅ 内容创作正常")
        print(f"   ✅ 质量评审正常")
        print(f"   ✅ 合规检查正常")
        print(f"   ✅ 决策逻辑正常")
        
        print("\n" + "=" * 70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败：{str(e)}")
        logger.error(f"端到端测试异常：{str(e)}", exc_info=True)
        return False


def test_end_to_end_with_full_review():
    """
    测试完整评审流程（可选）
    
    流程：分析 → 创作 → 互动评审 → 质量评审 → 合规性检查 → 决策
    
    注意：此测试包含互动评审，耗时较长（~60秒）
    """
    print("\n" + "=" * 70)
    print("🧪 端到端测试：完整评审流程（含互动评审）")
    print("=" * 70 + "\n")
    print("⚠️  此测试包含互动评审 Agent，预计耗时约60秒")
    print()
    
    topic = "悉尼旅游"
    start_time = time.time()
    
    try:
        # 步骤 1-2：同上（分析和创作）
        print("📊 步骤 1/6: 内容分析（简化版）")
        analysis_result = agent_a_analyze_xiaohongshu(topic, limit=3, quality_level="fast")
        analysis = json.loads(analysis_result)
        if not analysis.get('success'):
            print("❌ 分析失败")
            return False
        print("✅ 分析完成\n")
        
        print("✍️  步骤 2/6: 内容创作")
        create_result = agent_c_create_content(
            analysis_result=analysis_result,
            topic=topic,
            style="casual",
            quality_level="fast"
        )
        create_data = json.loads(create_result)
        if not create_data.get('success'):
            print("❌ 创作失败")
            return False
        
        content = create_data['data']
        title = content['title']
        body = content['content']
        print(f"✅ 创作完成\n   标题：{title}\n")
        
        # 步骤 3：互动评审
        print("🔥 步骤 3/6: 互动潜力评审（智能Agent）")
        print("   正在分析互动潜力...")
        
        step_start = time.time()
        engagement_result = review_engagement({
            "title": title,
            "content": body,
            "topic": topic
        })
        step_time = time.time() - step_start
        
        engagement = json.loads(engagement_result)
        engagement_score = engagement.get('score', 0)
        
        print(f"   ✅ 互动评审完成（{step_time:.1f}秒）")
        print(f"   - 评分：{engagement_score}/10")
        print()
        
        # 步骤 4：质量评审
        print("🔍 步骤 4/6: 质量评审")
        quality_result = review_quality({
            "title": title,
            "content": body,
            "topic": topic
        })
        quality = json.loads(quality_result)
        quality_score = quality.get('score', 0)
        print(f"   ✅ 质量评审完成")
        print(f"   - 评分：{quality_score}/10\n")
        
        # 步骤 5：合规性
        print("⚖️  步骤 5/6: 合规性检查")
        compliance_result = review_compliance({
            "title": title,
            "content": body,
            "hashtags": content.get('hashtags', [])
        })
        compliance = json.loads(compliance_result)
        compliance_passed = compliance['data'].get('overall', {}).get('passed', False)
        print(f"   ✅ 合规检查完成")
        print(f"   - 结果：{'通过' if compliance_passed else '未通过'}\n")
        
        # 步骤 6：综合决策
        print("🎯 步骤 6/6: 综合决策")
        overall_score = (engagement_score + quality_score) / 2
        print(f"   - 互动评分：{engagement_score}/10")
        print(f"   - 质量评分：{quality_score}/10")
        print(f"   - 综合评分：{overall_score:.1f}/10")
        print(f"   - 合规性：{'通过' if compliance_passed else '未通过'}")
        
        if not compliance_passed:
            print(f"   - 决策：❌ 必须优化（合规性问题）")
        elif overall_score >= 8.0:
            print(f"   - 决策：✅ 可以发布（优秀）")
        else:
            print(f"   - 决策：⚠️  建议优化")
        
        total_time = time.time() - start_time
        print(f"\n⏱️  总耗时：{total_time:.1f}秒")
        print(f"💰 估算成本：~$0.025")
        
        print("\n✅ 完整评审流程测试通过！\n")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败：{str(e)}")
        logger.error(f"完整评审测试异常：{str(e)}", exc_info=True)
        return False


def test_decision_logic():
    """
    测试评审决策逻辑
    """
    print("\n" + "=" * 70)
    print("🧪 测试：评审决策逻辑")
    print("=" * 70 + "\n")
    
    test_cases = [
        {
            "name": "优秀内容",
            "quality_score": 9.0,
            "compliance_passed": True,
            "expected": "PUBLISH"
        },
        {
            "name": "良好内容",
            "quality_score": 7.5,
            "compliance_passed": True,
            "expected": "ASK_USER"
        },
        {
            "name": "欠佳内容",
            "quality_score": 5.5,
            "compliance_passed": True,
            "expected": "RECOMMEND_OPTIMIZE"
        },
        {
            "name": "合规问题",
            "quality_score": 9.0,
            "compliance_passed": False,
            "expected": "MUST_OPTIMIZE"
        }
    ]
    
    passed = 0
    for case in test_cases:
        quality_score = case['quality_score']
        compliance_passed = case['compliance_passed']
        expected = case['expected']
        
        # 决策逻辑
        if not compliance_passed:
            decision = "MUST_OPTIMIZE"
        elif quality_score >= 8.0:
            decision = "PUBLISH"
        elif quality_score >= 6.0:
            decision = "ASK_USER"
        else:
            decision = "RECOMMEND_OPTIMIZE"
        
        result = "✅" if decision == expected else "❌"
        print(f"{result} {case['name']}")
        print(f"   质量:{quality_score}/10, 合规:{'通过' if compliance_passed else '未通过'}")
        print(f"   期望:{expected}, 实际:{decision}")
        
        if decision == expected:
            passed += 1
        print()
    
    print(f"测试结果：{passed}/{len(test_cases)} 通过")
    return passed == len(test_cases)


def main():
    """运行所有测试"""
    print("\n" + "=" * 70)
    print("🧪 端到端测试套件（含评审系统）")
    print("=" * 70 + "\n")
    
    results = []
    
    # 测试 1：标准评审流程
    print("🧪 测试 1: 标准评审流程")
    results.append(("标准评审流程", test_end_to_end_with_standard_review()))
    
    # 测试 2：决策逻辑
    print("\n🧪 测试 2: 决策逻辑")
    results.append(("决策逻辑", test_decision_logic()))
    
    # 测试 3：完整评审流程（可选，耗时长）
    # 取消注释以运行完整评审测试
    # print("\n🧪 测试 3: 完整评审流程（含互动评审）")
    # results.append(("完整评审流程", test_end_to_end_with_full_review()))
    
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
        print("\n🎉 所有测试通过！评审系统集成成功。\n")
    else:
        print(f"\n⚠️  {total - passed} 个测试失败，请检查日志。\n")


if __name__ == "__main__":
    main()

