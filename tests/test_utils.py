"""
单元测试：工具模块
测试各种工具函数和类
"""

import os
import json
import pytest
from pathlib import Path

# 设置 Mock 模式
os.environ['MOCK_MODE'] = 'true'


class TestDraftManager:
    """草稿管理器测试"""
    
    @pytest.fixture
    def draft_manager(self):
        """创建草稿管理器实例"""
        from utils.draft_manager import DraftManager
        return DraftManager()
    
    @pytest.fixture
    def sample_content(self):
        """示例内容"""
        return {
            'title': '测试标题',
            'content': '测试内容' * 100,
            'hashtags': ['测试', '单元测试']
        }
    
    def test_save_and_load_draft(self, draft_manager, sample_content):
        """测试保存和加载草稿"""
        from utils.draft_manager import save_draft_from_content
        
        # 保存草稿
        draft_id = save_draft_from_content(
            content_data=sample_content,
            topic='测试主题'
        )
        
        assert draft_id is not None
        assert len(draft_id) > 0
        
        # 加载草稿
        loaded = draft_manager.load_draft(draft_id)
        assert loaded['topic'] == '测试主题'
        assert loaded['content']['title'] == sample_content['title']
        
        # 清理
        draft_manager.delete_draft(draft_id)
    
    def test_list_drafts(self, draft_manager, sample_content):
        """测试列出草稿"""
        from utils.draft_manager import save_draft_from_content
        
        # 保存几个草稿
        draft_ids = []
        for i in range(3):
            draft_id = save_draft_from_content(
                content_data=sample_content,
                topic=f'测试主题{i}'
            )
            draft_ids.append(draft_id)
        
        # 列出草稿
        drafts = draft_manager.list_drafts(limit=5)
        assert len(drafts) >= 3
        
        # 清理
        for draft_id in draft_ids:
            draft_manager.delete_draft(draft_id)
    
    def test_delete_draft(self, draft_manager, sample_content):
        """测试删除草稿"""
        from utils.draft_manager import save_draft_from_content
        
        # 保存草稿
        draft_id = save_draft_from_content(
            content_data=sample_content,
            topic='测试删除'
        )
        
        # 删除草稿
        result = draft_manager.delete_draft(draft_id)
        assert result == True
        
        # 验证已删除
        with pytest.raises(FileNotFoundError):
            draft_manager.load_draft(draft_id)


class TestResponseUtils:
    """响应工具测试"""
    
    def test_create_success_response(self):
        """测试创建成功响应"""
        from utils.response_utils import create_success_response
        
        response = create_success_response(
            data={'key': 'value'},
            message='测试成功'
        )
        
        data = json.loads(response)
        assert data['success'] == True
        assert data['message'] == '测试成功'
        assert data['data']['key'] == 'value'
    
    def test_create_error_response(self):
        """测试创建错误响应"""
        from utils.response_utils import create_error_response
        
        response = create_error_response(
            error='测试错误',
            message='操作失败'
        )
        
        data = json.loads(response)
        assert data['success'] == False
        assert data['message'] == '操作失败'
        assert 'error' in data
    
    def test_parse_tool_response(self):
        """测试解析工具响应"""
        from utils.response_utils import (
            create_success_response,
            parse_tool_response
        )
        
        response = create_success_response(data={'test': 'data'})
        parsed = parse_tool_response(response)
        
        assert parsed.success == True
        assert parsed.data['test'] == 'data'
    
    def test_is_success(self):
        """测试判断响应是否成功"""
        from utils.response_utils import (
            create_success_response,
            create_error_response,
            is_success
        )
        
        success_resp = create_success_response(data={})
        error_resp = create_error_response(error='错误')
        
        assert is_success(success_resp) == True
        assert is_success(error_resp) == False


class TestMockData:
    """Mock 数据生成器测试"""
    
    def test_mock_search_result(self):
        """测试 Mock 搜索结果"""
        from utils.mock_data import MockDataGenerator
        
        result = MockDataGenerator.mock_xiaohongshu_search("测试", limit=5)
        
        assert 'notes' in result
        assert len(result['notes']) == 5
        assert all('title' in note for note in result['notes'])
    
    def test_mock_content_analysis(self):
        """测试 Mock 内容分析"""
        from utils.mock_data import MockDataGenerator
        
        analysis = MockDataGenerator.mock_content_analysis("测试主题")
        
        assert 'title_patterns' in analysis
        assert 'content_features' in analysis
        assert 'user_needs' in analysis
    
    def test_mock_content_creation(self):
        """测试 Mock 内容创作"""
        from utils.mock_data import MockDataGenerator
        
        creation = MockDataGenerator.mock_content_creation("测试", "casual")
        
        assert 'title' in creation
        assert 'content' in creation
        assert 'hashtags' in creation
        assert len(creation['hashtags']) > 0
    
    def test_mock_llm_response(self):
        """测试 Mock LLM 响应"""
        from utils.mock_data import get_mock_llm_response
        
        response = get_mock_llm_response("测试提示", "analysis")
        
        assert response is not None
        assert len(response) > 0


class TestLogger:
    """日志系统测试"""
    
    def test_setup_logging(self):
        """测试日志设置"""
        from utils.logger_config import setup_logging, get_logger
        
        setup_logging(level='INFO', console_enabled=True, file_enabled=False)
        logger = get_logger('test')
        
        assert logger is not None
        
        # 测试日志记录
        logger.info("测试信息日志")
        logger.warning("测试警告日志")
        logger.error("测试错误日志")
    
    def test_get_logger(self):
        """测试获取 Logger"""
        from utils.logger_config import get_logger
        
        logger1 = get_logger('test1')
        logger2 = get_logger('test2')
        logger3 = get_logger('test1')  # 相同名称
        
        assert logger1 is not None
        assert logger2 is not None
        assert logger1.name != logger2.name
        # Logger 应该被缓存
        assert logger1 is logger3 or logger1.name == logger3.name


class TestErrorHandler:
    """错误处理测试"""
    
    def test_agent_error(self):
        """测试 AgentError"""
        from utils.error_handler import AgentError
        
        error = AgentError("测试错误", error_code="TEST_001")
        
        assert str(error) == "测试错误"
        assert error.error_code == "TEST_001"
    
    def test_create_error_response(self):
        """测试创建错误响应"""
        from utils.error_handler import create_error_response
        
        response = create_error_response("错误信息")
        data = json.loads(response)
        
        assert data['success'] == False
        assert 'error' in data
    
    def test_safe_json_parse(self):
        """测试安全 JSON 解析"""
        from utils.error_handler import safe_json_parse
        
        # 有效 JSON
        valid = safe_json_parse('{"key": "value"}')
        assert valid['key'] == 'value'
        
        # 无效 JSON
        invalid = safe_json_parse('invalid json')
        assert invalid == {}
        
        # 带默认值
        with_default = safe_json_parse('invalid', default={'default': True})
        assert with_default['default'] == True


@pytest.mark.slow
class TestPerformanceMonitor:
    """性能监控测试（较慢）"""
    
    def test_timer(self):
        """测试计时器"""
        from utils.performance_monitor import Timer
        import time
        
        with Timer("测试操作") as timer:
            time.sleep(0.1)
        
        assert timer.elapsed >= 0.1
    
    def test_performance_metrics(self):
        """测试性能指标"""
        from utils.performance_monitor import PerformanceMetrics
        
        metrics = PerformanceMetrics()
        
        # 记录一些数据
        metrics.record_duration("test_func", 1.5)
        metrics.record_duration("test_func", 2.0)
        metrics.record_duration("test_func", 1.0)
        
        # 获取统计
        stats = metrics.get_stats("test_func")
        
        assert stats['calls'] == 3
        assert stats['total_time'] == 4.5
        assert stats['avg_time'] == 1.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

