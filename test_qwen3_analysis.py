"""
测试 Qwen3 模型分析功能
验证配置是否正确，模型是否可用
"""

import json
from tools.content_analyst import agent_a_analyze_xiaohongshu
from utils.model_router import ModelRouter, TaskType, QualityLevel

def test_model_selection():
    """测试模型选择是否正确"""
    print("=" * 60)
    print("🧪 测试模型选择配置")
    print("=" * 60)
    
    router = ModelRouter()
    
    # 测试不同质量级别的模型选择
    levels = [QualityLevel.FAST, QualityLevel.BALANCED, QualityLevel.HIGH]
    
    for level in levels:
        model = router.select_model(TaskType.ANALYSIS, level)
        print(f"\n✓ {level.value:>8} 级别 → {model}")
        
        # 显示模型信息
        info = router.get_model_info(model)
        if info:
            print(f"  描述: {info.get('description', 'N/A')}")
            print(f"  优势: {', '.join(info.get('strengths', []))}")
            print(f"  成本: {info.get('cost_level', 'N/A')}")
    
    print("\n" + "=" * 60)

def test_qwen3_analysis():
    """测试 Qwen3 实际分析能力"""
    print("\n" + "=" * 60)
    print("🚀 测试 Qwen3 分析功能（使用少量数据）")
    print("=" * 60)
    
    # 使用少量数据快速测试
    keyword = "北京旅游"
    limit = 3  # 只取3篇，快速测试
    quality_level = "balanced"  # 使用 qwen-plus
    
    print(f"\n📊 测试参数:")
    print(f"  关键词: {keyword}")
    print(f"  数量: {limit} 篇")
    print(f"  质量级别: {quality_level} (qwen-plus)")
    print(f"\n⏳ 正在分析...\n")
    
    try:
        result_json = agent_a_analyze_xiaohongshu(
            keyword=keyword,
            limit=limit,
            quality_level=quality_level
        )
        
        result = json.loads(result_json)
        
        if result.get("success"):
            print("✅ 分析成功！\n")
            
            data = result.get("data", {})
            
            # 显示关键结果
            print(f"📈 分析结果:")
            print(f"  实际分析: {data.get('total_analyzed', 0)} 篇笔记")
            
            title_patterns = data.get("title_patterns", [])
            print(f"  标题模式: {len(title_patterns)} 个")
            if title_patterns:
                print(f"    示例: {title_patterns[0]}")
            
            hot_topics = data.get("hot_topics", [])
            print(f"  热门话题: {len(hot_topics)} 个")
            if hot_topics:
                print(f"    示例: {hot_topics[0]}")
            
            suggestions = data.get("creation_suggestions", [])
            print(f"  创作建议: {len(suggestions)} 条")
            if suggestions:
                print(f"    示例: {suggestions[0][:50]}...")
            
            print("\n✨ Qwen3 模型工作正常！")
            
        else:
            print(f"❌ 分析失败: {result.get('error', '未知错误')}")
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)

def main():
    """主测试函数"""
    print("\n🧪 Qwen3 模型配置测试\n")
    
    # 测试1：模型选择配置
    test_model_selection()
    
    # 测试2：实际分析功能（可选，需要MCP服务）
    user_input = input("\n是否测试实际分析功能？需要MCP服务运行 (y/n): ")
    if user_input.lower() in ['y', 'yes']:
        test_qwen3_analysis()
    else:
        print("\n跳过实际分析测试")
    
    print("\n✅ 测试完成！\n")

if __name__ == "__main__":
    main()

