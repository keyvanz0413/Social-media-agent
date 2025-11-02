"""
测试 Engagement Reviewer Agent
演示如何使用真正的 Agent 进行评审
"""

import json
import logging
from pathlib import Path
import sys

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_engagement_reviewer_agent():
    """
    测试 Engagement Reviewer Agent
    
    这个测试展示了 Agent 与普通函数的区别：
    - Agent 会主动使用工具
    - Agent 会进行推理和决策
    - Agent 会给出更深入的分析
    """
    try:
        from agents.reviewers.engagement_reviewer import create_engagement_reviewer_agent
        
        print("=" * 60)
        print("🧪 测试 Engagement Reviewer Agent")
        print("=" * 60)
        print()
        
        # 1. 创建 Agent
        print("📌 步骤 1: 创建 Engagement Reviewer Agent...")
        agent = create_engagement_reviewer_agent()
        print("✅ Agent 创建成功！")
        print()
        
        # 2. 准备测试内容
        test_content = {
            "title": "澳洲旅游攻略",
            "content": """
分享我的澳洲之旅经验！

去了悉尼、墨尔本和黄金海岸。悉尼歌剧院真的很美，邦迪海滩人很多。墨尔本的咖啡文化很有意思。

建议大家提前订票，旺季很贵。带好防晒霜！
""",
            "topic": "澳洲旅游"
        }
        
        print("📌 步骤 2: 准备测试内容")
        print(f"   标题: {test_content['title']}")
        print(f"   话题: {test_content['topic']}")
        print()
        
        # 3. 构建输入
        user_input = f"""请评审这篇小红书内容的互动潜力：

标题：{test_content['title']}

正文：
{test_content['content']}

话题：{test_content['topic']}

请使用你的工具进行深度分析，给出详细的评审结果。"""
        
        # 4. 调用 Agent
        print("📌 步骤 3: 调用 Agent 进行评审...")
        print("💡 Agent 会自动：")
        print("   1. 搜索同话题的爆款帖子")
        print("   2. 分析标题规律")
        print("   3. 检查情感触发点")
        print("   4. 获取互动数据统计")
        print("   5. 给出综合评审结果")
        print()
        print("⏳ 评审中...(这可能需要30-60秒)")
        print("-" * 60)
        
        result = agent.input(user_input)
        
        print()
        print("-" * 60)
        print("✅ 评审完成！")
        print()
        
        # 5. 解析结果
        print("📌 步骤 4: 解析评审结果")
        try:
            review_data = json.loads(result)
            
            print()
            print("=" * 60)
            print("📊 评审结果")
            print("=" * 60)
            print()
            
            print(f"🎯 互动潜力评分: {review_data.get('score', 'N/A')}/10")
            print(f"📈 置信度: {review_data.get('confidence', 'N/A')}")
            print(f"📊 与平均水平对比: {review_data.get('compared_to_average', 'N/A')}")
            print(f"💭 预期互动: {review_data.get('expected_engagement', 'N/A')}")
            print()
            
            print("✨ 优势：")
            for strength in review_data.get('strengths', []):
                print(f"   • {strength}")
            print()
            
            print("⚠️  不足：")
            for weakness in review_data.get('weaknesses', []):
                print(f"   • {weakness}")
            print()
            
            print("💡 优化建议：")
            for suggestion in review_data.get('suggestions', []):
                print(f"   • {suggestion}")
            print()
            
            print("=" * 60)
            
            # 判断是否通过
            passed = review_data.get('score', 0) >= 8.0
            if passed:
                print("✅ 评审通过！内容具有良好的互动潜力")
            else:
                print("⚠️  评审未通过，建议优化后再发布")
            
            return True
            
        except json.JSONDecodeError as e:
            print(f"❌ 解析JSON失败: {str(e)}")
            print(f"原始输出: {result}")
            return False
        
    except ImportError as e:
        print(f"❌ 导入失败: {str(e)}")
        print("💡 请确保已安装 ConnectOnion: pip install connectonion")
        return False
        
    except Exception as e:
        logger.error(f"测试失败: {str(e)}", exc_info=True)
        print(f"❌ 测试失败: {str(e)}")
        return False


def test_comparison_with_function():
    """
    对比 Agent 和函数的评审差异
    
    展示两种方案的区别
    """
    print()
    print("=" * 60)
    print("🔬 对比测试：Agent vs 函数")
    print("=" * 60)
    print()
    
    test_content = {
        "title": "澳洲旅游攻略",
        "content": "分享我的澳洲之旅...",
        "hashtags": ["澳洲旅游", "旅行攻略"]
    }
    
    print("📌 使用相同的测试内容")
    print()
    
    # 测试 1: 函数式评审
    try:
        from tools.review_tools_v1 import review_engagement as review_engagement_function
        
        print("1️⃣  函数式评审 (review_tools_v1.py)")
        print("-" * 60)
        
        result_func = review_engagement_function(test_content, quality_level="balanced")
        result_func_data = json.loads(result_func)
        
        if result_func_data.get('success'):
            func_score = result_func_data['data']['score']
            print(f"   评分: {func_score}/10")
            print(f"   用时: ~5秒")
            print(f"   成本: ~$0.01")
            print(f"   特点: 快速、规则明确、稳定")
        
        print()
        
    except Exception as e:
        print(f"   ❌ 函数式评审测试失败: {str(e)}")
        print()
    
    # 测试 2: Agent 评审
    try:
        from agents.reviewers.engagement_reviewer import review_engagement
        
        print("2️⃣  Agent 评审 (engagement_reviewer.py)")
        print("-" * 60)
        
        result_agent = review_engagement(test_content)
        result_agent_data = json.loads(result_agent)
        
        if result_agent_data.get('success', True) and 'score' in result_agent_data:
            agent_score = result_agent_data['score']
            print(f"   评分: {agent_score}/10")
            print(f"   用时: ~30-60秒")
            print(f"   成本: ~$0.03-0.05")
            print(f"   特点: 深度分析、数据驱动、可推理")
            print(f"   工具调用: 搜索爆款、分析标题、检查情感")
        
        print()
        
    except Exception as e:
        print(f"   ❌ Agent 评审测试失败: {str(e)}")
        print()
    
    print("=" * 60)
    print("📊 总结")
    print("=" * 60)
    print()
    print("函数式评审：")
    print("  ✅ 快速、低成本、稳定")
    print("  ❌ 无法使用工具、无法深度推理")
    print()
    print("Agent 评审：")
    print("  ✅ 深度分析、数据驱动、可使用工具")
    print("  ❌ 较慢、成本较高")
    print()
    print("💡 建议：")
    print("  - MVP 阶段使用函数式评审")
    print("  - 需要深度分析时使用 Agent 评审")
    print("  - 或采用混合方案：先用函数快速筛选，再用 Agent 深度评审")
    print()


def main():
    """主函数"""
    print()
    print("🚀 Engagement Reviewer Agent 测试")
    print()
    
    # 测试 1: 基本功能测试
    success = test_engagement_reviewer_agent()
    
    if success:
        print()
        input("按 Enter 继续对比测试...")
        
        # 测试 2: 对比测试
        test_comparison_with_function()
    
    print()
    print("✅ 测试完成！")
    print()


if __name__ == "__main__":
    main()

