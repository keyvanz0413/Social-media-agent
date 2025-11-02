"""
MVP v0.2 功能测试脚本
测试新实现的 P0 功能
"""

import json
from pathlib import Path

# 导入新功能
from utils.response_utils import (
    create_success_response,
    create_error_response,
    parse_tool_response,
    is_success,
    get_response_data
)
from utils.draft_manager import (
    DraftManager,
    get_draft_manager,
    save_draft_from_content,
    load_latest_draft
)
from config import PathConfig


def test_response_utils():
    """测试统一响应格式工具"""
    print("=" * 60)
    print("测试 1: 统一响应格式工具")
    print("=" * 60 + "\n")
    
    # 测试成功响应
    success_response = create_success_response(
        data={'title': '澳洲旅游攻略', 'content': '这是一篇关于澳洲的文章'},
        message='内容创作成功',
        word_count=100,
        quality_score=8.5
    )
    
    print("✅ 成功响应示例:")
    print(success_response)
    print()
    
    # 测试失败响应
    error_response = create_error_response(
        error='API 调用超时',
        message='分析失败',
        retry_after=60
    )
    
    print("❌ 失败响应示例:")
    print(error_response)
    print()
    
    # 测试解析响应
    parsed = parse_tool_response(success_response)
    print(f"✅ 解析成功: {parsed.success}")
    print(f"📊 数据: {parsed.data}")
    print(f"💬 消息: {parsed.message}")
    print()


def test_draft_manager():
    """测试草稿管理器"""
    print("=" * 60)
    print("测试 2: 草稿管理器")
    print("=" * 60 + "\n")
    
    # 创建草稿管理器
    manager = get_draft_manager()
    
    # 测试保存草稿
    print("📝 保存测试草稿...")
    draft_id = save_draft_from_content(
        content_data={
            'title': '🦘澳洲大洋路3天2夜攻略！人均不到3k',
            'content': '澳洲大洋路真的太美了！这次3天2夜的自驾之旅...',
            'hashtags': ['澳洲旅游', '大洋路', '自驾游'],
            'metadata': {
                'word_count': 856,
                'style': 'casual'
            }
        },
        topic='澳洲旅游',
        analysis_data={
            'title_patterns': ['数字型', '疑问式'],
            'user_needs': ['实用攻略', '省钱技巧']
        }
    )
    
    print(f"✅ 草稿已保存: {draft_id}")
    print(f"📁 保存路径: {PathConfig.DRAFTS_DIR / f'{draft_id}.json'}")
    print()
    
    # 测试加载草稿
    print("📖 加载草稿...")
    draft = manager.load_draft(draft_id)
    print(f"✅ 草稿加载成功")
    print(f"📋 主题: {draft['topic']}")
    print(f"📝 标题: {draft['content']['title']}")
    print(f"⏰ 创建时间: {draft['created_at']}")
    print()
    
    # 测试列出草稿
    print("📋 列出所有草稿...")
    drafts = manager.list_drafts(limit=5)
    print(f"✅ 找到 {len(drafts)} 个草稿")
    for i, d in enumerate(drafts[:3], 1):
        summary = manager.get_draft_summary(d['draft_id'])
        print(f"  {i}. {summary['title']} ({summary['word_count']}字)")
    print()
    
    return draft_id


def test_environment_setup():
    """测试环境初始化"""
    print("=" * 60)
    print("测试 3: 环境初始化")
    print("=" * 60 + "\n")
    
    from main import setup_environment
    
    result = setup_environment()
    
    if result['success']:
        print("✅ 环境初始化成功！")
    else:
        print("❌ 环境初始化失败")
        for issue in result['issues']:
            print(f"  ❌ {issue}")
    
    if result['warnings']:
        print("\n⚠️  警告:")
        for warning in result['warnings']:
            print(f"  ⚠️  {warning}")
    
    print()


def test_mcp_validation():
    """测试 MCP 连接验证"""
    print("=" * 60)
    print("测试 4: MCP 连接验证")
    print("=" * 60 + "\n")
    
    from main import validate_mcp_connection
    
    result = validate_mcp_connection()
    
    if result:
        print("✅ MCP 连接验证通过")
    else:
        print("⚠️  MCP 连接验证失败（这是正常的，如果 MCP 服务未启动）")
    
    print()


def cleanup_test_draft(draft_id):
    """清理测试草稿"""
    print("🧹 清理测试数据...")
    manager = get_draft_manager()
    if manager.delete_draft(draft_id):
        print(f"✅ 测试草稿已删除: {draft_id}")
    print()


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("🧪 MVP v0.2 功能测试")
    print("=" * 60 + "\n")
    
    draft_id = None
    
    try:
        # 测试 1: 响应格式工具
        test_response_utils()
        
        # 测试 2: 草稿管理器
        draft_id = test_draft_manager()
        
        # 测试 3: 环境初始化
        test_environment_setup()
        
        # 测试 4: MCP 连接验证
        test_mcp_validation()
        
        print("=" * 60)
        print("✅ 所有测试完成！")
        print("=" * 60 + "\n")
        
        print("💡 提示:")
        print("  - 统一响应格式工具: utils/response_utils.py")
        print("  - 草稿管理器: utils/draft_manager.py")
        print("  - 主入口: main.py")
        print()
        
        print("📚 使用示例:")
        print("  # 检查环境")
        print("  python main.py --check")
        print()
        print("  # 单任务模式")
        print("  python main.py --mode single --task '发表一篇关于澳洲旅游的帖子'")
        print()
        print("  # 跳过 MCP 检查（仅测试分析和创作）")
        print("  python main.py --skip-mcp-check")
        print()
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理测试数据
        if draft_id:
            cleanup_test_draft(draft_id)


if __name__ == "__main__":
    main()

