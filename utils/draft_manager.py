"""
草稿管理工具
负责内容草稿的保存、读取和管理
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from config import PathConfig

logger = logging.getLogger(__name__)


class DraftManager:
    """草稿管理器"""
    
    def __init__(self, drafts_dir: Optional[Path] = None):
        """
        初始化草稿管理器
        
        Args:
            drafts_dir: 草稿保存目录，默认使用配置中的目录
        """
        self.drafts_dir = drafts_dir or PathConfig.DRAFTS_DIR
        self.drafts_dir.mkdir(parents=True, exist_ok=True)
    
    def save_draft(
        self,
        content_data: Dict[str, Any],
        topic: str,
        draft_id: Optional[str] = None,
        analysis_data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        保存草稿
        
        Args:
            content_data: 内容数据（标题、正文、标签等）
            topic: 主题
            draft_id: 草稿ID，如果不提供则自动生成
            analysis_data: 分析数据（可选）
            metadata: 额外的元数据（可选）
            
        Returns:
            草稿ID
            
        Example:
            >>> manager = DraftManager()
            >>> draft_id = manager.save_draft(
            ...     content_data={'title': '标题', 'content': '内容'},
            ...     topic='澳洲旅游'
            ... )
            >>> print(draft_id)
            '20251102_143052_澳洲旅游'
        """
        # 生成草稿 ID
        if draft_id is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # 清理主题名称，移除特殊字符
            safe_topic = self._sanitize_filename(topic)
            draft_id = f"{timestamp}_{safe_topic}"
        
        # 构造草稿数据
        draft = {
            'draft_id': draft_id,
            'topic': topic,
            'content': content_data,
            'analysis': analysis_data,
            'metadata': metadata or {},
            'created_at': datetime.now().isoformat(),
            'version': '1.0'
        }
        
        # 保存草稿
        draft_path = self.drafts_dir / f"{draft_id}.json"
        try:
            with open(draft_path, 'w', encoding='utf-8') as f:
                json.dump(draft, f, ensure_ascii=False, indent=2)
            
            logger.info(f"草稿已保存: {draft_path}")
            return draft_id
            
        except Exception as e:
            logger.error(f"保存草稿失败: {str(e)}")
            raise
    
    def load_draft(self, draft_id: str) -> Dict[str, Any]:
        """
        加载草稿
        
        Args:
            draft_id: 草稿ID
            
        Returns:
            草稿数据
            
        Raises:
            FileNotFoundError: 草稿不存在
        """
        draft_path = self.drafts_dir / f"{draft_id}.json"
        
        if not draft_path.exists():
            raise FileNotFoundError(f"草稿不存在: {draft_id}")
        
        try:
            with open(draft_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载草稿失败: {str(e)}")
            raise
    
    def list_drafts(
        self,
        topic: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        列出所有草稿
        
        Args:
            topic: 按主题过滤（可选）
            limit: 限制返回数量（可选）
            
        Returns:
            草稿列表，按创建时间倒序排列
        """
        drafts = []
        
        for draft_path in self.drafts_dir.glob("*.json"):
            try:
                with open(draft_path, 'r', encoding='utf-8') as f:
                    draft = json.load(f)
                
                # 主题过滤
                if topic and draft.get('topic') != topic:
                    continue
                
                drafts.append(draft)
                
            except Exception as e:
                logger.warning(f"跳过无效草稿 {draft_path}: {str(e)}")
        
        # 按创建时间倒序排列
        drafts.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        # 限制数量
        if limit:
            drafts = drafts[:limit]
        
        return drafts
    
    def delete_draft(self, draft_id: str) -> bool:
        """
        删除草稿
        
        Args:
            draft_id: 草稿ID
            
        Returns:
            是否删除成功
        """
        draft_path = self.drafts_dir / f"{draft_id}.json"
        
        try:
            if draft_path.exists():
                draft_path.unlink()
                logger.info(f"草稿已删除: {draft_id}")
                return True
            else:
                logger.warning(f"草稿不存在: {draft_id}")
                return False
        except Exception as e:
            logger.error(f"删除草稿失败: {str(e)}")
            return False
    
    def get_draft_summary(self, draft_id: str) -> Dict[str, Any]:
        """
        获取草稿摘要信息
        
        Args:
            draft_id: 草稿ID
            
        Returns:
            草稿摘要（ID、主题、标题、创建时间等）
        """
        draft = self.load_draft(draft_id)
        content = draft.get('content', {})
        
        return {
            'draft_id': draft.get('draft_id'),
            'topic': draft.get('topic'),
            'title': content.get('title', '无标题'),
            'created_at': draft.get('created_at'),
            'word_count': content.get('metadata', {}).get('word_count', 0)
        }
    
    def cleanup_old_drafts(self, days: int = 30) -> int:
        """
        清理旧草稿
        
        Args:
            days: 保留最近 N 天的草稿
            
        Returns:
            删除的草稿数量
        """
        from datetime import timedelta
        
        cutoff_time = datetime.now() - timedelta(days=days)
        deleted_count = 0
        
        for draft_path in self.drafts_dir.glob("*.json"):
            try:
                with open(draft_path, 'r', encoding='utf-8') as f:
                    draft = json.load(f)
                
                created_at_str = draft.get('created_at')
                if created_at_str:
                    created_at = datetime.fromisoformat(created_at_str)
                    if created_at < cutoff_time:
                        draft_path.unlink()
                        deleted_count += 1
                        logger.info(f"已删除旧草稿: {draft_path.name}")
                        
            except Exception as e:
                logger.warning(f"处理草稿 {draft_path} 时出错: {str(e)}")
        
        logger.info(f"清理完成，共删除 {deleted_count} 个旧草稿")
        return deleted_count
    
    @staticmethod
    def _sanitize_filename(filename: str, max_length: int = 50) -> str:
        """
        清理文件名，移除特殊字符
        
        Args:
            filename: 原始文件名
            max_length: 最大长度
            
        Returns:
            清理后的文件名
        """
        # 移除或替换特殊字符
        import re
        cleaned = re.sub(r'[<>:"/\\|?*]', '_', filename)
        cleaned = cleaned.strip()
        
        # 限制长度
        if len(cleaned) > max_length:
            cleaned = cleaned[:max_length]
        
        return cleaned or 'draft'


# 全局实例（单例）
_default_manager = None


def get_draft_manager() -> DraftManager:
    """
    获取默认的草稿管理器实例（单例）
    
    Returns:
        DraftManager 实例
    """
    global _default_manager
    if _default_manager is None:
        _default_manager = DraftManager()
    return _default_manager


def save_draft_from_content(
    content_data: Dict[str, Any],
    topic: str,
    analysis_data: Optional[Dict[str, Any]] = None
) -> str:
    """
    便捷函数：保存内容草稿
    
    Args:
        content_data: 内容数据
        topic: 主题
        analysis_data: 分析数据（可选）
        
    Returns:
        草稿ID
    """
    manager = get_draft_manager()
    return manager.save_draft(
        content_data=content_data,
        topic=topic,
        analysis_data=analysis_data
    )


def load_latest_draft(topic: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    加载最新的草稿
    
    Args:
        topic: 按主题过滤（可选）
        
    Returns:
        草稿数据，如果没有草稿则返回 None
    """
    manager = get_draft_manager()
    drafts = manager.list_drafts(topic=topic, limit=1)
    
    return drafts[0] if drafts else None


__all__ = [
    'DraftManager',
    'get_draft_manager',
    'save_draft_from_content',
    'load_latest_draft'
]

