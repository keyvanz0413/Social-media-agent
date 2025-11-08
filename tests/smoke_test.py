"""
烟雾测试（Smoke Test）
快速验证系统核心功能是否正常工作
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 设置 Mock 模式（避免真实 API 调用）
os.environ['MOCK_MODE'] = 'true'

import json
from typing import Dict, Any


def test_imports():
    """测试 1: 检查核心模块是否可以导入"""
    print("\n" + "=" * 60)
    print("测试 1: 核心模块导入")
    print("=" * 60)
    
    try:
        # 配置模块
        from config import (
            ModelConfig, MCPConfig, PathConfig,
            LogConfig, DevConfig, BusinessConfig
        )
        print("✅ 配置模块导入成功")
        
        # 工具模块
        from utils.llm_client import LLMClient
        from utils.mcp_client import XiaohongshuMCPClient
        from utils.model_router import ModelRouter
        from utils.response_utils import create_success_response
        from utils.draft_manager import DraftManager
        from utils.mock_data import MockDataGenerator
        from utils.logger_config import setup_logging, get_logger
        print("✅ 工具模块导入成功")
        
        # 子 Agent 模块
        from tools.content_analyst import agent_a_analyze_xiaohongshu
        from tools.content_creator import agent_c_create_content
        from tools.publisher import publish_to_xiaohongshu
        print("✅ 子 Agent 模块导入成功")
        
        # 主协调 Agent
        try:
            from agent import create_coordinator_agent
            print("✅ 主协调 Agent 模块导入成功")
        except ImportError as e:
            print(f"⚠️  主协调 Agent 导入失败（可能缺少 connectonion）: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 模块导入失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_config():
    """测试 2: 检查配置是否正确"""
    print("\n" + "=" * 60)
    print("测试 2: 配置系统")
    print("=" * 60)
    
    try:
        from config import PathConfig, ModelConfig, DevConfig
        
        # 检查路径配置
        assert PathConfig.BASE_DIR.exists(), "BASE_DIR 不存在"
        print(f"✅ 项目根目录: {PathConfig.BASE_DIR}")
        
        # 检查输出目录
        PathConfig.ensure_dirs()
        assert PathConfig.DRAFTS_DIR.exists(), "DRAFTS_DIR 不存在"
        assert PathConfig.LOGS_DIR.exists(), "LOGS_DIR 不存在"
        print(f"✅ 输出目录已创建")
        
        # 检查 Mock 模式
        assert DevConfig.MOCK_MODE == True, "Mock 模式未启用"
        print(f"✅ Mock 模式已启用")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置检查失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_logging():
    """测试 3: 检查日志系统"""
    print("\n" + "=" * 60)
    print("测试 3: 日志系统")
    print("=" * 60)
    
    try:
        from utils.logger_config import setup_logging, get_logger
        
        # 配置日志
        setup_logging(level='INFO', console_enabled=True, file_enabled=False)
        print("✅ 日志系统配置成功")
        
        # 获取 Logger
        logger = get_logger('smoke_test')
        logger.info("这是一条测试日志")
        logger.warning("这是一条警告日志")
        print("✅ Logger 可以正常工作")
        
        return True
        
    except Exception as e:
        print(f"❌ 日志系统测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_mock_data():
    """测试 4: 检查 Mock 数据生成"""
    print("\n" + "=" * 60)
    print("测试 4: Mock 数据生成")
    print("=" * 60)
    
    try:
        from utils.mock_data import MockDataGenerator, get_mock_llm_response
        
        # 测试小红书搜索 Mock
        search_result = MockDataGenerator.mock_xiaohongshu_search("测试", limit=3)
        assert 'notes' in search_result, "Mock 搜索结果格式错误"
        assert len(search_result['notes']) == 3, "Mock 搜索结果数量错误"
        print(f"✅ Mock 搜索数据生成成功（{len(search_result['notes'])} 条）")
        
        # 测试内容分析 Mock
        analysis = MockDataGenerator.mock_content_analysis("测试主题")
        assert 'title_patterns' in analysis, "Mock 分析结果格式错误"
        print("✅ Mock 分析数据生成成功")
        
        # 测试内容创作 Mock
        creation = MockDataGenerator.mock_content_creation("测试", "casual")
        assert 'title' in creation, "Mock 创作结果格式错误"
        print(f"✅ Mock 创作数据生成成功（标题: {creation['title'][:20]}...）")
        
        # 测试 LLM 响应 Mock
        llm_response = get_mock_llm_response("分析这段文本", "analysis")
        assert len(llm_response) > 0, "Mock LLM 响应为空"
        print("✅ Mock LLM 响应生成成功")
        
        return True
        
    except Exception as e:
        print(f"❌ Mock 数据测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_draft_manager():
    """测试 5: 检查草稿管理器"""
    print("\n" + "=" * 60)
    print("测试 5: 草稿管理器")
    print("=" * 60)
    
    try:
        from utils.draft_manager import DraftManager, save_draft_from_content
        
        # 创建测试草稿
        test_content = {
            'title': '烟雾测试草稿',
            'content': '这是一个测试草稿内容',
            'hashtags': ['测试', '烟雾测试']
        }
        
        draft_id = save_draft_from_content(
            content_data=test_content,
            topic='烟雾测试'
        )
        print(f"✅ 草稿保存成功: {draft_id}")
        
        # 加载草稿
        manager = DraftManager()
        draft = manager.load_draft(draft_id)
        assert draft['topic'] == '烟雾测试', "草稿加载失败"
        print("✅ 草稿加载成功")
        
        # 列出草稿
        drafts = manager.list_drafts(limit=5)
        assert len(drafts) > 0, "草稿列表为空"
        print(f"✅ 草稿列表获取成功（共 {len(drafts)} 个）")
        
        # 删除测试草稿
        manager.delete_draft(draft_id)
        print("✅ 测试草稿已清理")
        
        return True
        
    except Exception as e:
        print(f"❌ 草稿管理器测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_sub_agents():
    """测试 6: 检查子 Agent 功能（Mock 模式）"""
    print("\n" + "=" * 60)
    print("测试 6: 子 Agent 功能（Mock 模式）")
    print("=" * 60)
    
    try:
        from tools.content_analyst import agent_a_analyze_xiaohongshu
        from tools.content_creator import agent_c_create_content
        from tools.publisher import publish_to_xiaohongshu
        
        # 测试分析 Agent
        print("📊 测试内容分析 Agent...")
        analysis_result = agent_a_analyze_xiaohongshu(
            keyword="测试关键词",
            limit=3,
            quality_level="fast"
        )
        analysis_data = json.loads(analysis_result)
        print(f"✅ 分析 Agent 正常工作")
        
        # 测试创作 Agent
        print("✍️  测试内容创作 Agent...")
        creation_result = agent_c_create_content(
            analysis_result=analysis_result,
            topic="测试主题",
            style="casual",
            quality_level="fast"
        )
        creation_data = json.loads(creation_result)
        assert 'title' in creation_data, "创作结果缺少标题"
        print(f"✅ 创作 Agent 正常工作（标题: {creation_data['title'][:20]}...）")
        
        # 测试发布工具
        print("📤 测试发布工具...")
        publish_result = publish_to_xiaohongshu(
            title=creation_data['title'][:20],
            content=creation_data['content'][:100],
            tags=['测试']
        )
        publish_data = json.loads(publish_result)
        print("✅ 发布工具正常工作")
        
        return True
        
    except Exception as e:
        print(f"❌ 子 Agent 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_response_format():
    """测试 7: 检查统一响应格式"""
    print("\n" + "=" * 60)
    print("测试 7: 统一响应格式")
    print("=" * 60)
    
    try:
        from utils.response_utils import (
            create_success_response,
            create_error_response,
            parse_tool_response,
            is_success
        )
        
        # 测试成功响应
        success_resp = create_success_response(
            data={'key': 'value'},
            message='测试成功'
        )
        assert is_success(success_resp), "成功响应格式错误"
        print("✅ 成功响应格式正确")
        
        # 测试失败响应
        error_resp = create_error_response(
            error='测试错误',
            message='测试失败'
        )
        assert not is_success(error_resp), "失败响应格式错误"
        print("✅ 失败响应格式正确")
        
        # 测试解析
        parsed = parse_tool_response(success_resp)
        assert parsed.success == True, "响应解析错误"
        print("✅ 响应解析正常")
        
        return True
        
    except Exception as e:
        print(f"❌ 响应格式测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """运行所有烟雾测试"""
    print("\n" + "=" * 60)
    print("🧪 开始烟雾测试（Smoke Test）")
    print("=" * 60)
    print(f"Mock 模式: 启用")
    print(f"测试环境: {project_root}")
    
    tests = [
        ("核心模块导入", test_imports),
        ("配置系统", test_config),
        ("日志系统", test_logging),
        ("Mock 数据生成", test_mock_data),
        ("草稿管理器", test_draft_manager),
        ("子 Agent 功能", test_sub_agents),
        ("统一响应格式", test_response_format),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ 测试 '{test_name}' 发生异常: {str(e)}")
            results.append((test_name, False))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    failed = len(results) - passed
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status}: {test_name}")
    
    print("\n" + "=" * 60)
    print(f"总计: {len(results)} 个测试")
    print(f"通过: {passed} 个 ✅")
    print(f"失败: {failed} 个 ❌")
    print(f"成功率: {passed/len(results)*100:.1f}%")
    print("=" * 60)
    
    if failed == 0:
        print("\n🎉 所有烟雾测试通过！系统核心功能正常。")
        return 0
    else:
        print(f"\n⚠️  有 {failed} 个测试失败，请检查问题。")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)

