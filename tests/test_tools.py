"""
单元测试：工具函数
测试内容分析、创作、发布等工具
"""

import os
import json
import pytest

# 设置 Mock 模式
os.environ['MOCK_MODE'] = 'true'


@pytest.mark.unit
class TestContentAnalyst:
    """内容分析工具测试"""
    
    def test_analyze_xiaohongshu(self):
        """测试小红书内容分析"""
        from tools.content_analyst import agent_a_analyze_xiaohongshu
        
        result = agent_a_analyze_xiaohongshu(
            keyword="测试关键词",
            limit=3,
            quality_level="fast"
        )
        
        assert result is not None
        data = json.loads(result)
        
        # 兼容不同的响应格式
        if 'success' in data:
            assert data.get('success') or 'data' in data
        else:
            assert 'title_patterns' in data or 'user_needs' in data
    
    def test_analyze_with_different_limits(self):
        """测试不同数量限制的分析"""
        from tools.content_analyst import agent_a_analyze_xiaohongshu
        
        for limit in [3, 5, 10]:
            result = agent_a_analyze_xiaohongshu(
                keyword="测试",
                limit=limit,
                quality_level="fast"
            )
            
            assert result is not None
            data = json.loads(result)
            assert data is not None


@pytest.mark.unit
class TestContentCreator:
    """内容创作工具测试"""
    
    @pytest.fixture
    def analysis_result(self):
        """获取分析结果作为输入"""
        from tools.content_analyst import agent_a_analyze_xiaohongshu
        return agent_a_analyze_xiaohongshu("测试", limit=3, quality_level="fast")
    
    def test_create_content(self, analysis_result):
        """测试内容创作"""
        from tools.content_creator import agent_c_create_content
        
        result = agent_c_create_content(
            analysis_result=analysis_result,
            topic="测试主题",
            style="casual",
            quality_level="fast"
        )
        
        assert result is not None
        data = json.loads(result)
        
        # 兼容不同的响应格式
        if 'success' in data:
            content = data.get('data', {})
        else:
            content = data
        
        assert 'title' in content
        assert 'content' in content
    
    def test_different_styles(self, analysis_result):
        """测试不同风格的创作"""
        from tools.content_creator import agent_c_create_content
        
        styles = ['casual', 'professional', 'humorous']
        
        for style in styles:
            result = agent_c_create_content(
                analysis_result=analysis_result,
                topic="测试",
                style=style,
                quality_level="fast"
            )
            
            assert result is not None
            data = json.loads(result)
            assert data is not None


@pytest.mark.unit
class TestPublisher:
    """发布工具测试"""
    
    def test_publish_to_xiaohongshu(self):
        """测试发布到小红书"""
        from tools.publisher import publish_to_xiaohongshu
        
        result = publish_to_xiaohongshu(
            title="测试标题",
            content="测试内容",
            tags=['测试']
        )
        
        assert result is not None
        data = json.loads(result)
        
        # Mock 模式下应该成功
        assert 'success' in data or 'note_id' in data


@pytest.mark.unit
class TestImageGenerator:
    """图片生成工具测试"""
    
    def test_generate_images(self):
        """测试图片生成"""
        from tools.image_generator import generate_images_for_content
        
        suggestions = json.dumps([
            {
                "description": "测试图片描述",
                "purpose": "测试目的",
                "position": 1
            }
        ])
        
        result = generate_images_for_content(
            image_suggestions=suggestions,
            topic="测试",
            count=1,
            method="unsplash",
            save_to_disk=False
        )
        
        assert result is not None
        # 图片生成可能需要外部 API，允许跳过


@pytest.mark.unit
class TestReviewTools:
    """评审工具测试"""
    
    @pytest.fixture
    def sample_content(self):
        """示例内容"""
        return {
            "title": "测试标题｜测试内容",
            "content": "这是一段测试内容" * 20,
            "hashtags": ["测试", "单元测试"]
        }
    
    def test_quality_review(self, sample_content):
        """测试质量评审"""
        from agents.reviewers.quality_reviewer import review_quality
        
        result = review_quality(sample_content)
        data = json.loads(result)
        
        assert 'score' in data
        assert 0 <= data['score'] <= 10
    
    def test_engagement_review(self, sample_content):
        """测试互动评审"""
        from agents.reviewers.engagement_reviewer import review_engagement
        
        result = review_engagement(sample_content)
        data = json.loads(result)
        
        assert 'score' in data
        assert 0 <= data['score'] <= 10
    
    def test_compliance_review(self, sample_content):
        """测试合规性评审"""
        from agents.reviewers.compliance_reviewer import review_compliance
        
        result = review_compliance(sample_content)
        data = json.loads(result)
        
        assert data is not None
    
    def test_review_content(self, sample_content):
        """测试综合评审"""
        from tools.review_tools_v1 import review_content
        
        result = review_content(sample_content, quality_level="fast")
        data = json.loads(result)
        
        assert data.get('success') == True
        assert 'overall_score' in data['data']


@pytest.mark.integration
class TestEndToEndWorkflow:
    """端到端工作流测试"""
    
    def test_full_content_creation_workflow(self):
        """测试完整的内容创作流程"""
        topic = "单元测试"
        
        # 步骤 1: 分析
        from tools.content_analyst import agent_a_analyze_xiaohongshu
        analysis = agent_a_analyze_xiaohongshu(
            keyword=topic,
            limit=3,
            quality_level="fast"
        )
        assert analysis is not None
        
        # 步骤 2: 创作
        from tools.content_creator import agent_c_create_content
        creation = agent_c_create_content(
            analysis_result=analysis,
            topic=topic,
            style="casual",
            quality_level="fast"
        )
        assert creation is not None
        
        # 步骤 3: 评审
        from tools.review_tools_v1 import review_content
        
        creation_data = json.loads(creation)
        if 'success' in creation_data:
            content = creation_data.get('data', {})
        else:
            content = creation_data
        
        review = review_content(content, quality_level="fast")
        assert review is not None
        
        # 步骤 4: 发布（Mock）
        from tools.publisher import publish_to_xiaohongshu
        publish = publish_to_xiaohongshu(
            title=content.get('title', '测试')[:20],
            content=content.get('content', '测试')[:100],
            tags=['测试']
        )
        assert publish is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "unit"])

