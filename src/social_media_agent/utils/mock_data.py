"""
Mock 数据生成器
用于开发和测试环境，提供模拟的 API 响应
"""

import json
from typing import Dict, Any, List
from datetime import datetime


class MockDataGenerator:
    """Mock 数据生成器"""
    
    @staticmethod
    def mock_xiaohongshu_search(keyword: str, limit: int = 5) -> Dict[str, Any]:
        """
        模拟小红书搜索结果
        
        Args:
            keyword: 搜索关键词
            limit: 结果数量
            
        Returns:
            模拟的搜索结果
        """
        mock_notes = []
        
        for i in range(min(limit, 5)):
            note = {
                'note_id': f'mock_note_{i+1}',
                'title': f'🔥{keyword}攻略第{i+1}篇！必看',
                'desc': f'这是关于{keyword}的详细攻略内容...',
                'content': f'这是关于{keyword}的详细攻略内容...',
                'author': {
                    'user_id': f'mock_user_{i+1}',
                    'nickname': f'小红书用户{i+1}'
                },
                'interact_info': {
                    'liked_count': 5000 + i * 1000,
                    'comment_count': 500 + i * 100,
                    'collected_count': 1000 + i * 200
                },
                'stats': {
                    'likes': 5000 + i * 1000,
                    'comments': 500 + i * 100,
                    'collects': 1000 + i * 200
                },
                'tags': [keyword, '攻略', '实用'],
                'published_at': '2025-11-01T10:00:00'
            }
            mock_notes.append(note)

        return {
            # 新契约：与 MCP Client 对齐
            'feeds': mock_notes,
            # 兼容旧测试
            'notes': mock_notes,
            'count': len(mock_notes),
            'total': limit,
            'keyword': keyword
        }
    
    @staticmethod
    def mock_content_analysis(keyword: str) -> Dict[str, Any]:
        """
        模拟内容分析结果
        
        Args:
            keyword: 分析的关键词
            
        Returns:
            模拟的分析结果
        """
        content_structure = {
            'common_sections': ['开篇吸引', '正文攻略', '注意事项', '总结建议'],
            'avg_paragraphs': 6,
            'emoji_usage': '高频使用（平均每段2-3个）'
        }

        return {
            'keyword': keyword,
            'title_patterns': [
                '数字型标题（如"7天攻略"）',
                '疑问式标题（如"你知道吗？"）',
                '感叹式标题（如"太美了！"）'
            ],
            'content_structure': content_structure,
            # 向后兼容旧测试字段
            'content_features': content_structure,
            'user_needs': [
                '实用攻略和省钱技巧',
                '真实体验分享',
                '避坑指南',
                '行程规划建议'
            ],
            'hot_topics': [
                f'{keyword}必去景点',
                f'{keyword}美食推荐',
                f'{keyword}住宿攻略',
                f'{keyword}交通指南'
            ],
            'engagement_triggers': [
                '使用数字增加可信度',
                '提供实用省钱技巧',
                '分享独特体验',
                '引发情感共鸣'
            ],
            'creation_suggestions': {
                'title_style': '使用数字+关键词+价格/时间',
                'content_tone': '轻松casual，略带亲切感',
                'structure': '开篇引入 → 分点展开 → 注意事项 → 结尾总结',
                'visual_elements': '建议配图6-9张，突出重点场景'
            },
            'metadata': {
                'analyzed_notes': 5,
                'avg_likes': 7500,
                'avg_comments': 750,
                'analysis_time': datetime.now().isoformat()
            }
        }
    
    @staticmethod
    def mock_content_creation(topic: str, style: str = 'casual') -> Dict[str, Any]:
        """
        模拟内容创作结果
        
        Args:
            topic: 主题
            style: 风格
            
        Returns:
            模拟的创作内容
        """
        return {
            'title': f'🦘{topic}3天2夜攻略！人均不到3k',
            'alternative_titles': [
                f'{topic}超全攻略！省钱必看',
                f'去{topic}前必读！避坑指南',
                f'{topic}自由行攻略｜实用干货'
            ],
            'content': f"""哈喽姐妹们！今天来分享我的{topic}之旅～

🌟 行程规划
Day1: 抵达 → 市区游览 → 夜景
Day2: 核心景点打卡 → 特色美食
Day3: 购物 → 返程

💰 费用明细
· 机票：往返约1500元
· 住宿：民宿300元/晚 x 2
· 餐饮：约500元
· 门票：约400元
· 交通：约200元
总计：约2900元！

📸 拍照打卡点
1. XX景点 - 最佳时间：日落
2. YY街道 - 文艺小清新
3. ZZ海滩 - ins风大片

⚠️ 注意事项
✓ 提前预订可以省钱
✓ 避开节假日高峰
✓ 防晒霜必备
✓ 提前下载地图

💡 实用Tips
记得带转换插头、提前换些现金、学几句当地语言会加分哦～

有问题评论区问我！祝大家玩得开心🎉""",
            'hashtags': [
                f'{topic}旅游',
                f'{topic}攻略',
                '自由行',
                '省钱攻略',
                '旅行vlog'
            ],
            'image_suggestions': [
                {'description': '封面图：标志性建筑全景', 'scene': '地标建筑'},
                {'description': '行程规划图：清晰的路线图', 'scene': '地图'},
                {'description': '美食特写：当地特色美食', 'scene': '美食'},
                {'description': '住宿环境：民宿内景', 'scene': '住宿'},
                {'description': '风景大片：最美景点', 'scene': '风景'},
                {'description': '人物照片：旅行氛围感', 'scene': '人物'}
            ],
            'metadata': {
                'word_count': 456,
                'style': style,
                'tone': 'casual',
                'target_audience': '年轻女性旅行者',
                'estimated_reading_time': '2分钟',
                'draft_id': 'mock_draft_' + datetime.now().strftime('%Y%m%d_%H%M%S')
            }
        }
    
    @staticmethod
    def mock_publish_result(success: bool = True) -> Dict[str, Any]:
        """
        模拟发布结果
        
        Args:
            success: 是否成功
            
        Returns:
            模拟的发布结果
        """
        if success:
            return {
                'success': True,
                'note_id': 'mock_note_123456',
                'url': 'https://www.xiaohongshu.com/explore/mock_note_123456',
                'note_url': 'https://www.xiaohongshu.com/explore/mock_note_123456',
                'published_at': datetime.now().isoformat(),
                'message': '笔记发布成功（模拟）'
            }
        else:
            return {
                'success': False,
                'error': '发布失败（模拟）',
                'error_code': 'MOCK_ERROR',
                'message': '这是一个模拟的发布失败'
            }
    
    @staticmethod
    def mock_mcp_health() -> Dict[str, Any]:
        """模拟 MCP 健康检查"""
        return {
            'status': 'healthy',
            'service': 'xiaohongshu-mcp',
            'version': '1.0.0-mock',
            'timestamp': datetime.now().isoformat()
        }
    
    @staticmethod
    def mock_login_status(logged_in: bool = True) -> Dict[str, Any]:
        """模拟登录状态"""
        if logged_in:
            return {
                'is_logged_in': True,
                'logged_in': True,
                'username': 'mock_user',
                'user_id': 'mock_user_123',
                'nickname': '测试用户（Mock）'
            }
        else:
            return {
                'is_logged_in': False,
                'logged_in': False,
                'message': '未登录（模拟）'
            }


def get_mock_llm_response(prompt: str, task_type: str = 'general') -> str:
    """
    生成模拟的 LLM 响应
    
    Args:
        prompt: 提示词
        task_type: 任务类型（analysis/creation/review）
        
    Returns:
        模拟的 LLM 响应文本
    """
    if task_type == 'analysis':
        return json.dumps(
            MockDataGenerator.mock_content_analysis('模拟关键词'),
            ensure_ascii=False,
            indent=2
        )
    elif task_type == 'creation':
        return json.dumps(
            MockDataGenerator.mock_content_creation('模拟主题'),
            ensure_ascii=False,
            indent=2
        )
    elif task_type == 'review':
        # 模拟评审响应
        return json.dumps({
            "score": 8.0,
            "strengths": [
                "内容结构清晰",
                "表达流畅自然",
                "有一定的实用价值"
            ],
            "weaknesses": [
                "部分细节可以更充实",
                "互动引导略显不足"
            ],
            "suggestions": [
                "可以添加更多具体的细节和案例",
                "在结尾增加互动引导，如提问或征集意见",
                "标题可以更加吸引眼球"
            ]
        }, ensure_ascii=False, indent=2)
    else:
        return "这是一个模拟的 LLM 响应。"


__all__ = [
    'MockDataGenerator',
    'get_mock_llm_response'
]
