"""
Model Router
根据任务类型和质量要求选择合适的 LLM 模型
"""

from enum import Enum
from typing import Dict
import logging
from config import Config

logger = logging.getLogger(__name__)


class TaskType(Enum):
    """任务类型"""
    ANALYSIS = "analysis"
    CREATION = "creation"
    REVIEW = "review"
    REASONING = "reasoning"


class QualityLevel(Enum):
    """质量级别"""
    FAST = "fast"
    BALANCED = "balanced"
    HIGH = "high"


class ModelRouter:
    """
    简化的模型路由器
    
    职责：根据任务类型和质量级别选择合适的模型
    
    Example:
        >>> router = ModelRouter()
        >>> model = router.select_model(TaskType.ANALYSIS, QualityLevel.BALANCED)
        >>> print(model)
        'qwen-plus'
    """
    
    def __init__(self):
        """初始化路由器"""
        self.task_mapping = Config.TASK_MODEL_MAPPING
    
    def select_model(
        self,
        task_type: TaskType,
        quality_level: QualityLevel = QualityLevel.BALANCED
    ) -> str:
        """
        选择适合的模型
        
        Args:
            task_type: 任务类型
            quality_level: 质量级别（默认 BALANCED）
            
        Returns:
            模型名称
            
        Raises:
            ValueError: 任务类型不支持
        """
        task_key = task_type.value
        quality_key = quality_level.value
        
        if task_key not in self.task_mapping:
            raise ValueError(
                f"不支持的任务类型: {task_key}. "
                f"支持的类型: {list(self.task_mapping.keys())}"
            )
        
        task_models = self.task_mapping[task_key]
        
        # 如果指定的质量级别不存在，降级到 balanced
        if quality_key not in task_models:
            logger.warning(
                f"质量级别 {quality_key} 不存在，使用 balanced"
            )
            quality_key = "balanced"
        
        model = task_models[quality_key]
        logger.debug(
            f"选择模型: {model} (任务={task_key}, 质量={quality_key})"
        )
        
        return model


# 导出
__all__ = ['ModelRouter', 'TaskType', 'QualityLevel']

