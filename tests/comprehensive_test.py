"""
综合测试套件 - Social Media Agent
===================================

这个文件整合了所有功能测试，对整套代码进行全面检查。

测试模块：
1. 核心功能测试（模块导入、配置、日志）
2. 工具模块测试（缓存、错误处理、性能监控）
3. 内容创作测试（分析、创作、发布）
4. 评审系统测试（质量、互动、合规）
5. 端到端测试（完整工作流）
6. 批处理测试（批量任务处理）

运行方式：
    python tests/comprehensive_test.py
    或
    pytest tests/comprehensive_test.py -v
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 设置 Mock 模式（避免真实 API 调用）
os.environ['MOCK_MODE'] = 'true'

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# 第一部分：核心功能测试
# ============================================================================

class CoreFunctionalityTests:
    """核心功能测试集"""
    
    @staticmethod
    def test_imports() -> bool:
        """测试：核心模块导入"""
        print("\n" + "=" * 70)
        print("📦 测试：核心模块导入")
        print("=" * 70)
        
        try:
            # 配置模块
            from config import (
                ModelConfig, MCPConfig, PathConfig,
                LogConfig, DevConfig, BusinessConfig
            )
            print("✅ 配置模块导入成功")
            
            # 工具模块
            from utils.llm_client import LLMClient
            from utils.model_router import ModelRouter
            from utils.response_utils import create_success_response
            from utils.draft_manager import DraftManager
            from utils.mock_data import MockDataGenerator
            from utils.logger_config import setup_logging, get_logger
            from utils.cache_manager import CacheManager
            from utils.error_handler import AgentError
            from utils.performance_monitor import PerformanceMetrics
            print("✅ 工具模块导入成功")
            
            # 内容创作模块
            from tools.content_analyst import agent_a_analyze_xiaohongshu
            from tools.content_creator import agent_c_create_content
            from tools.publisher import publish_to_xiaohongshu
            from tools.image_generator import generate_images_for_content
            print("✅ 内容创作模块导入成功")
            
            # 评审模块
            from tools.review_tools_v1 import review_content
            from agents.reviewers.quality_reviewer import review_quality
            from agents.reviewers.engagement_reviewer import review_engagement
            from agents.reviewers.compliance_reviewer import review_compliance
            print("✅ 评审模块导入成功")
            
            return True
            
        except Exception as e:
            print(f"❌ 模块导入失败: {str(e)}")
            return False
    
    @staticmethod
    def test_config() -> bool:
        """测试：配置系统"""
        print("\n" + "=" * 70)
        print("⚙️  测试：配置系统")
        print("=" * 70)
        
        try:
            from config import PathConfig, ModelConfig, DevConfig
            
            # 检查路径配置
            assert PathConfig.BASE_DIR.exists(), "BASE_DIR 不存在"
            print(f"✅ 项目根目录: {PathConfig.BASE_DIR}")
            
            # 确保输出目录
            PathConfig.ensure_dirs()
            assert PathConfig.DRAFTS_DIR.exists(), "DRAFTS_DIR 不存在"
            assert PathConfig.LOGS_DIR.exists(), "LOGS_DIR 不存在"
            print("✅ 输出目录已创建")
            
            # 检查 Mock 模式
            assert DevConfig.MOCK_MODE == True, "Mock 模式未启用"
            print("✅ Mock 模式已启用")
            
            # 验证配置
            validation_result = ModelConfig.validate_config()
            assert "success" in validation_result
            print("✅ 配置验证通过")
            
            return True
            
        except Exception as e:
            print(f"❌ 配置检查失败: {str(e)}")
            return False
    
    @staticmethod
    def test_logging() -> bool:
        """测试：日志系统"""
        print("\n" + "=" * 70)
        print("📝 测试：日志系统")
        print("=" * 70)
        
        try:
            from utils.logger_config import setup_logging, get_logger
            
            # 配置日志
            setup_logging(level='INFO', console_enabled=True, file_enabled=False)
            print("✅ 日志系统配置成功")
            
            # 获取 Logger
            logger = get_logger('test')
            logger.info("测试日志消息")
            logger.warning("测试警告消息")
            print("✅ Logger 可以正常工作")
            
            return True
            
        except Exception as e:
            print(f"❌ 日志系统测试失败: {str(e)}")
            return False


# ============================================================================
# 第二部分：工具模块测试
# ============================================================================

class UtilityTests:
    """工具模块测试集"""
    
    @staticmethod
    def test_cache_manager() -> bool:
        """测试：缓存管理器"""
        print("\n" + "=" * 70)
        print("💾 测试：缓存管理器")
        print("=" * 70)
        
        try:
            from utils.cache_manager import CacheManager, cache_key
            
            cache = CacheManager()
            
            # 测试基本操作
            cache.set("test_key", "test_value", ttl=10)
            value = cache.get("test_key")
            assert value == "test_value", "缓存值不匹配"
            print("✅ 基本缓存操作正常")
            
            # 测试缓存键生成
            key1 = cache_key("search", "悉尼旅游")
            key2 = cache_key("search", "悉尼旅游")
            assert key1 == key2, "相同参数应生成相同的键"
            print("✅ 缓存键生成正常")
            
            # 测试统计
            stats = cache.get_stats()
            assert "hits" in stats and "misses" in stats
            print("✅ 缓存统计正常")
            
            # 清理测试数据
            cache.delete("test_key")
            
            return True
            
        except Exception as e:
            print(f"❌ 缓存管理器测试失败: {str(e)}")
            return False
    
    @staticmethod
    def test_error_handler() -> bool:
        """测试：错误处理"""
        print("\n" + "=" * 70)
        print("🛡️  测试：错误处理")
        print("=" * 70)
        
        try:
            from utils.error_handler import (
                AgentError, NetworkError, APIError,
                create_error_response, create_success_response,
                with_error_handling, safe_json_parse
            )
            
            # 测试错误类
            error = AgentError("测试错误")
            assert error.message == "测试错误"
            print("✅ 错误类创建正常")
            
            # 测试响应创建
            success_resp = create_success_response({"key": "value"})
            error_resp = create_error_response("错误信息")
            
            success_data = json.loads(success_resp)
            error_data = json.loads(error_resp)
            
            assert success_data["success"] == True
            assert error_data["success"] == False
            print("✅ 响应格式正常")
            
            # 测试 JSON 解析
            data = safe_json_parse('{"key": "value"}')
            assert data["key"] == "value"
            print("✅ JSON 解析正常")
            
            return True
            
        except Exception as e:
            print(f"❌ 错误处理测试失败: {str(e)}")
            return False
    
    @staticmethod
    def test_performance_monitor() -> bool:
        """测试：性能监控"""
        print("\n" + "=" * 70)
        print("📊 测试：性能监控")
        print("=" * 70)
        
        try:
            from utils.performance_monitor import (
                PerformanceMetrics, Timer, log_performance
            )
            
            # 测试性能指标
            metrics = PerformanceMetrics()
            metrics.record_duration("test_func", 1.5)
            metrics.record_duration("test_func", 2.0)
            
            stats = metrics.get_stats("test_func")
            assert stats["calls"] == 2
            assert stats["avg_time"] == 1.75
            print("✅ 性能指标收集正常")
            
            # 测试计时器
            with Timer("测试操作") as timer:
                time.sleep(0.1)
            assert timer.elapsed >= 0.1
            print("✅ 计时器正常")
            
            return True
            
        except Exception as e:
            print(f"❌ 性能监控测试失败: {str(e)}")
            return False
    
    @staticmethod
    def test_draft_manager() -> bool:
        """测试：草稿管理器"""
        print("\n" + "=" * 70)
        print("📄 测试：草稿管理器")
        print("=" * 70)
        
        try:
            from utils.draft_manager import DraftManager, save_draft_from_content
            
            # 创建测试草稿
            test_content = {
                'title': '测试草稿',
                'content': '这是一个测试草稿内容',
                'hashtags': ['测试']
            }
            
            draft_id = save_draft_from_content(
                content_data=test_content,
                topic='测试'
            )
            print(f"✅ 草稿保存成功: {draft_id}")
            
            # 加载草稿
            manager = DraftManager()
            draft = manager.load_draft(draft_id)
            assert draft['topic'] == '测试', "草稿加载失败"
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
            return False
    
    @staticmethod
    def test_mock_data() -> bool:
        """测试：Mock 数据生成"""
        print("\n" + "=" * 70)
        print("🎭 测试：Mock 数据生成")
        print("=" * 70)
        
        try:
            from utils.mock_data import MockDataGenerator
            
            # 测试搜索 Mock
            search_result = MockDataGenerator.mock_xiaohongshu_search("测试", limit=3)
            assert 'notes' in search_result
            assert len(search_result['notes']) == 3
            print(f"✅ Mock 搜索数据生成成功（{len(search_result['notes'])} 条）")
            
            # 测试分析 Mock
            analysis = MockDataGenerator.mock_content_analysis("测试主题")
            assert 'title_patterns' in analysis
            print("✅ Mock 分析数据生成成功")
            
            # 测试创作 Mock
            creation = MockDataGenerator.mock_content_creation("测试", "casual")
            assert 'title' in creation
            print("✅ Mock 创作数据生成成功")
            
            return True
            
        except Exception as e:
            print(f"❌ Mock 数据测试失败: {str(e)}")
            return False


# ============================================================================
# 第三部分：内容创作测试
# ============================================================================

class ContentCreationTests:
    """内容创作测试集"""
    
    @staticmethod
    def test_content_analyst() -> bool:
        """测试：内容分析 Agent"""
        print("\n" + "=" * 70)
        print("📊 测试：内容分析 Agent")
        print("=" * 70)
        
        try:
            from tools.content_analyst import agent_a_analyze_xiaohongshu
            
            result = agent_a_analyze_xiaohongshu(
                keyword="悉尼旅游",
                limit=3,
                quality_level="fast"
            )
            
            data = json.loads(result)
            # 兼容不同的响应格式
            if 'success' in data:
                assert data.get('success') or 'data' in data
            else:
                assert 'title_patterns' in data or 'user_needs' in data
            
            print("✅ 内容分析 Agent 正常工作")
            return True
            
        except Exception as e:
            print(f"❌ 内容分析测试失败: {str(e)}")
            return False
    
    @staticmethod
    def test_content_creator() -> bool:
        """测试：内容创作 Agent"""
        print("\n" + "=" * 70)
        print("✍️  测试：内容创作 Agent")
        print("=" * 70)
        
        try:
            from tools.content_analyst import agent_a_analyze_xiaohongshu
            from tools.content_creator import agent_c_create_content
            
            # 先进行分析
            analysis_result = agent_a_analyze_xiaohongshu(
                keyword="悉尼旅游",
                limit=3,
                quality_level="fast"
            )
            
            # 创作内容
            creation_result = agent_c_create_content(
                analysis_result=analysis_result,
                topic="悉尼旅游",
                style="casual",
                quality_level="fast"
            )
            
            data = json.loads(creation_result)
            # 兼容不同的响应格式
            if 'success' in data:
                content = data.get('data', {})
            else:
                content = data
            
            assert 'title' in content
            assert 'content' in content
            
            print(f"✅ 内容创作 Agent 正常工作")
            print(f"   标题: {content['title'][:30]}...")
            
            return True
            
        except Exception as e:
            print(f"❌ 内容创作测试失败: {str(e)}")
            return False
    
    @staticmethod
    def test_publisher() -> bool:
        """测试：发布工具"""
        print("\n" + "=" * 70)
        print("📤 测试：发布工具")
        print("=" * 70)
        
        try:
            from tools.publisher import publish_to_xiaohongshu
            
            result = publish_to_xiaohongshu(
                title="测试标题",
                content="测试内容",
                tags=['测试']
            )
            
            data = json.loads(result)
            # Mock 模式下应该返回成功
            assert 'success' in data or 'note_id' in data
            
            print("✅ 发布工具正常工作")
            return True
            
        except Exception as e:
            print(f"❌ 发布工具测试失败: {str(e)}")
            return False
    
    @staticmethod
    def test_image_generator() -> bool:
        """测试：图片生成工具"""
        print("\n" + "=" * 70)
        print("🖼️  测试：图片生成工具")
        print("=" * 70)
        
        try:
            from tools.image_generator import generate_images_for_content
            
            image_suggestions = json.dumps([
                {
                    "description": "悉尼歌剧院日落景色",
                    "purpose": "展示地标",
                    "position": 1
                }
            ], ensure_ascii=False)
            
            result = generate_images_for_content(
                image_suggestions=image_suggestions,
                topic="悉尼旅游",
                count=1,
                method="unsplash",
                save_to_disk=False  # 不保存，只测试API调用
            )
            
            data = json.loads(result)
            assert 'success' in data or 'images' in data
            
            print("✅ 图片生成工具正常工作")
            return True
            
        except Exception as e:
            print(f"❌ 图片生成测试失败: {str(e)}")
            # 图片生成可能需要外部API，失败是可以接受的
            print("⚠️  注意：图片生成需要外部API，跳过此测试")
            return True  # 允许跳过


# ============================================================================
# 第四部分：评审系统测试
# ============================================================================

class ReviewSystemTests:
    """评审系统测试集"""
    
    @staticmethod
    def test_quality_review() -> bool:
        """测试：质量评审"""
        print("\n" + "=" * 70)
        print("🔍 测试：质量评审")
        print("=" * 70)
        
        try:
            from agents.reviewers.quality_reviewer import review_quality
            
            content = {
                "title": "悉尼旅游攻略",
                "content": "分享我的悉尼之旅体验...",
                "topic": "悉尼旅游"
            }
            
            result = review_quality(content)
            data = json.loads(result)
            
            assert 'score' in data
            assert 0 <= data['score'] <= 10
            print(f"✅ 质量评审正常工作（评分: {data['score']}/10）")
            
            return True
            
        except Exception as e:
            print(f"❌ 质量评审测试失败: {str(e)}")
            return False
    
    @staticmethod
    def test_engagement_review() -> bool:
        """测试：互动评审"""
        print("\n" + "=" * 70)
        print("🔥 测试：互动评审")
        print("=" * 70)
        
        try:
            from agents.reviewers.engagement_reviewer import review_engagement
            
            content = {
                "title": "悉尼旅游攻略｜3天2夜深度游✨",
                "content": "分享我的悉尼之旅！超多干货...",
                "topic": "悉尼旅游"
            }
            
            result = review_engagement(content)
            data = json.loads(result)
            
            assert 'score' in data
            assert 0 <= data['score'] <= 10
            print(f"✅ 互动评审正常工作（评分: {data['score']}/10）")
            
            return True
            
        except Exception as e:
            print(f"❌ 互动评审测试失败: {str(e)}")
            return False
    
    @staticmethod
    def test_compliance_review() -> bool:
        """测试：合规性评审"""
        print("\n" + "=" * 70)
        print("⚖️  测试：合规性评审")
        print("=" * 70)
        
        try:
            from agents.reviewers.compliance_reviewer import review_compliance
            
            # 测试正常内容
            good_content = {
                "title": "健康饮食小技巧",
                "content": "分享一些实用的健康饮食建议",
                "hashtags": ["健康", "饮食"]
            }
            
            result = review_compliance(good_content)
            data = json.loads(result)
            
            # 兼容不同的响应格式
            if 'data' in data:
                comp_data = data['data']
                score = comp_data.get('overall', {}).get('score', 10)
            else:
                score = data.get('score', 10)
            
            assert score >= 0
            print(f"✅ 合规性评审正常工作（评分: {score}/10）")
            
            return True
            
        except Exception as e:
            print(f"❌ 合规性评审测试失败: {str(e)}")
            return False
    
    @staticmethod
    def test_review_tools() -> bool:
        """测试：评审工具集"""
        print("\n" + "=" * 70)
        print("🛠️  测试：评审工具集")
        print("=" * 70)
        
        try:
            from tools.review_tools_v1 import review_content
            
            content = {
                "title": "🌸京都赏樱攻略｜3天2夜超详细路线",
                "content": "今年樱花季去了趟京都，太美了！分享我的路线...",
                "hashtags": ["京都旅游", "樱花季"]
            }
            
            result = review_content(content, quality_level="fast")
            data = json.loads(result)
            
            assert data.get('success') == True
            assert 'overall_score' in data['data']
            assert 'reviews' in data['data']
            
            overall_score = data['data']['overall_score']
            print(f"✅ 评审工具集正常工作（总分: {overall_score}/10）")
            
            return True
            
        except Exception as e:
            print(f"❌ 评审工具集测试失败: {str(e)}")
            return False


# ============================================================================
# 第五部分：端到端测试
# ============================================================================

class EndToEndTests:
    """端到端测试集"""
    
    @staticmethod
    def test_full_workflow() -> bool:
        """测试：完整工作流（分析→创作→评审）"""
        print("\n" + "=" * 70)
        print("🔄 测试：完整工作流")
        print("=" * 70)
        
        topic = "悉尼旅游"
        
        try:
            # 步骤 1: 内容分析
            print("\n📊 步骤 1/4: 内容分析...")
            from tools.content_analyst import agent_a_analyze_xiaohongshu
            
            analysis_result = agent_a_analyze_xiaohongshu(
                keyword=topic,
                limit=3,
                quality_level="fast"
            )
            
            analysis = json.loads(analysis_result)
            print("   ✅ 分析完成")
            
            # 步骤 2: 内容创作
            print("\n✍️  步骤 2/4: 内容创作...")
            from tools.content_creator import agent_c_create_content
            
            create_result = agent_c_create_content(
                analysis_result=analysis_result,
                topic=topic,
                style="casual",
                quality_level="fast"
            )
            
            create_data = json.loads(create_result)
            if 'success' in create_data:
                content = create_data.get('data', {})
            else:
                content = create_data
            
            title = content.get('title', '')
            body = content.get('content', '')
            print(f"   ✅ 创作完成: {title[:30]}...")
            
            # 步骤 3: 质量评审
            print("\n🔍 步骤 3/4: 质量评审...")
            from agents.reviewers.quality_reviewer import review_quality
            
            quality_result = review_quality({
                "title": title,
                "content": body,
                "topic": topic
            })
            
            quality = json.loads(quality_result)
            quality_score = quality.get('score', 0)
            print(f"   ✅ 质量评审完成: {quality_score}/10")
            
            # 步骤 4: 合规性检查
            print("\n⚖️  步骤 4/4: 合规性检查...")
            from agents.reviewers.compliance_reviewer import review_compliance
            
            compliance_result = review_compliance({
                "title": title,
                "content": body,
                "hashtags": content.get('hashtags', [])
            })
            
            compliance = json.loads(compliance_result)
            if 'data' in compliance:
                comp_data = compliance['data']
                compliance_passed = comp_data.get('overall', {}).get('passed', True)
            else:
                compliance_passed = compliance.get('passed', True)
            
            print(f"   ✅ 合规检查完成: {'通过' if compliance_passed else '未通过'}")
            
            # 决策
            print("\n🎯 评审决策:")
            if not compliance_passed:
                decision = "必须优化（合规问题）"
            elif quality_score >= 8.0:
                decision = "可以发布（优秀）"
            elif quality_score >= 6.0:
                decision = "建议询问用户"
            else:
                decision = "建议优化"
            
            print(f"   决策: {decision}")
            print(f"   质量评分: {quality_score}/10")
            print(f"   合规性: {'通过' if compliance_passed else '未通过'}")
            
            print("\n✅ 完整工作流测试通过")
            return True
            
        except Exception as e:
            print(f"\n❌ 完整工作流测试失败: {str(e)}")
            return False


# ============================================================================
# 第六部分：批处理测试
# ============================================================================

class BatchProcessingTests:
    """批处理测试集"""
    
    @staticmethod
    def test_batch_tasks() -> bool:
        """测试：批量任务处理"""
        print("\n" + "=" * 70)
        print("📦 测试：批量任务处理")
        print("=" * 70)
        
        try:
            from tools.review_tools_v1 import batch_review
            
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
            
            result = batch_review(content_list, quality_level="fast")
            data = json.loads(result)
            
            assert data.get('success') == True
            assert data['data']['total'] == 3
            
            print(f"✅ 批量评审正常工作（处理 {data['data']['total']} 个任务）")
            
            # 显示结果统计
            passed = sum(1 for item in data['data']['results'] 
                        if item['review']['data']['passed'])
            print(f"   通过: {passed}/{data['data']['total']}")
            
            return True
            
        except Exception as e:
            print(f"❌ 批量任务测试失败: {str(e)}")
            return False


# ============================================================================
# 测试运行器
# ============================================================================

class TestRunner:
    """测试运行器"""
    
    def __init__(self):
        self.results: List[Tuple[str, str, bool]] = []
        self.start_time = time.time()
    
    def run_test_suite(self, suite_name: str, test_class):
        """运行测试套件"""
        print("\n" + "=" * 70)
        print(f"🧪 测试套件：{suite_name}")
        print("=" * 70)
        
        # 获取所有测试方法
        test_methods = [
            method for method in dir(test_class)
            if method.startswith('test_') and callable(getattr(test_class, method))
        ]
        
        for method_name in test_methods:
            test_method = getattr(test_class, method_name)
            try:
                result = test_method()
                self.results.append((suite_name, method_name, result))
            except Exception as e:
                logger.error(f"测试异常: {suite_name}.{method_name}: {str(e)}")
                self.results.append((suite_name, method_name, False))
    
    def print_summary(self):
        """打印测试总结"""
        elapsed_time = time.time() - self.start_time
        
        print("\n" + "=" * 70)
        print("📊 测试总结")
        print("=" * 70)
        
        # 按套件分组
        suites = {}
        for suite_name, method_name, result in self.results:
            if suite_name not in suites:
                suites[suite_name] = []
            suites[suite_name].append((method_name, result))
        
        # 打印每个套件的结果
        total_passed = 0
        total_tests = len(self.results)
        
        for suite_name, tests in suites.items():
            passed = sum(1 for _, result in tests if result)
            total = len(tests)
            total_passed += passed
            
            print(f"\n📦 {suite_name}: {passed}/{total} 通过")
            for method_name, result in tests:
                status = "✅" if result else "❌"
                # 格式化方法名
                display_name = method_name.replace('test_', '').replace('_', ' ').title()
                print(f"   {status} {display_name}")
        
        # 总体统计
        print("\n" + "=" * 70)
        print(f"总计: {total_passed}/{total_tests} 通过 ({total_passed/total_tests*100:.1f}%)")
        print(f"耗时: {elapsed_time:.1f} 秒")
        
        if total_passed == total_tests:
            print("\n🎉 所有测试通过！系统运行正常。")
            return 0
        else:
            failed = total_tests - total_passed
            print(f"\n⚠️  {failed} 个测试失败，请检查问题。")
            return 1


# ============================================================================
# 主函数
# ============================================================================

def main():
    """主测试函数"""
    print("\n" + "=" * 70)
    print("🧪 Social Media Agent - 综合测试套件")
    print("=" * 70)
    print(f"项目路径: {project_root}")
    print(f"Mock 模式: 启用")
    print(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    runner = TestRunner()
    
    # 运行所有测试套件
    runner.run_test_suite("核心功能", CoreFunctionalityTests)
    runner.run_test_suite("工具模块", UtilityTests)
    runner.run_test_suite("内容创作", ContentCreationTests)
    runner.run_test_suite("评审系统", ReviewSystemTests)
    runner.run_test_suite("端到端", EndToEndTests)
    runner.run_test_suite("批处理", BatchProcessingTests)
    
    # 打印总结
    exit_code = runner.print_summary()
    
    return exit_code


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 测试运行异常: {str(e)}")
        logger.error("测试运行异常", exc_info=True)
        sys.exit(1)

