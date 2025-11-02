"""
Model Router - 智能模型路由器
根据任务类型自动选择最优的 LLM 模型
"""

from enum import Enum
from typing import Dict, Optional, Any
import os
from config import ModelConfig


class TaskType(Enum):
    """
    任务类型枚举
    定义了系统支持的所有任务类型
    """
    ANALYSIS = "analysis"         # 内容分析（需要推理能力）
    CREATION = "creation"         # 内容创作（需要创意能力）
    REVIEW = "review"             # 内容评审（快速判断）
    REASONING = "reasoning"       # 复杂推理（策略制定）
    VISION = "vision"             # 视觉理解（多模态）


class QualityLevel(Enum):
    """
    质量级别枚举
    用于在性能和成本之间进行权衡
    """
    FAST = "fast"           # 快速模式：优先考虑成本，使用轻量模型
    BALANCED = "balanced"   # 平衡模式：性能和成本的最佳平衡（默认）
    HIGH = "high"           # 高质量模式：优先考虑性能，使用最强模型


class ModelRouter:
    """
    模型路由器
    
    职责：
    1. 根据任务类型和质量要求选择最优模型
    2. 提供模型降级策略
    3. 提供模型信息查询
    
    使用示例：
        router = ModelRouter()
        model = router.select_model(TaskType.ANALYSIS)
        result = llm_do(prompt, model=model)
    """
    
    def __init__(self):
        """初始化模型路由器，加载配置"""
        self.task_mapping = ModelConfig.TASK_MODEL_MAPPING
        self.fallback_models = ModelConfig.FALLBACK_MODELS
        self.model_info = ModelConfig.MODEL_INFO
        
    def select_model(
        self, 
        task_type: TaskType,
        quality_level: QualityLevel = QualityLevel.BALANCED
    ) -> str:
        """
        根据任务类型和质量要求选择模型
        
        Args:
            task_type: 任务类型（ANALYSIS, CREATION, REVIEW等）
            quality_level: 质量级别（FAST, BALANCED, HIGH），默认 BALANCED
            
        Returns:
            str: 模型名称，如 "gpt-4o", "claude-3.5-sonnet"
            
        Raises:
            ValueError: 如果任务类型不支持
            
        Example:
            >>> router = ModelRouter()
            >>> model = router.select_model(TaskType.ANALYSIS)
            >>> print(model)
            'gpt-4o'
            
            >>> model = router.select_model(TaskType.CREATION, QualityLevel.FAST)
            >>> print(model)
            'gpt-4o-mini'
        """
        task_key = task_type.value
        quality_key = quality_level.value
        
        # 检查任务类型是否支持
        if task_key not in self.task_mapping:
            raise ValueError(
                f"不支持的任务类型: {task_key}。"
                f"支持的类型: {list(self.task_mapping.keys())}"
            )
        
        # 获取该任务类型的模型配置
        task_models = self.task_mapping[task_key]
        
        # 检查质量级别是否存在
        if quality_key not in task_models:
            # 如果指定的质量级别不存在，降级到 balanced
            quality_key = "balanced"
        
        model = task_models[quality_key]
        
        return model
    
    def get_fallback_model(self, primary_model: str) -> Optional[str]:
        """
        获取备用模型（降级策略）
        
        当主模型调用失败时，可以尝试使用备用模型
        
        Args:
            primary_model: 主模型名称
            
        Returns:
            Optional[str]: 备用模型名称，如果没有备用模型则返回 None
            
        Example:
            >>> router = ModelRouter()
            >>> fallback = router.get_fallback_model("gpt-4o")
            >>> print(fallback)
            'gpt-4o-mini'
            
            >>> fallback = router.get_fallback_model("gpt-4o-mini")
            >>> print(fallback)
            None  # 已经是最便宜的模型，无法继续降级
        """
        return self.fallback_models.get(primary_model)
    
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """
        获取模型的详细信息
        
        Args:
            model_name: 模型名称
            
        Returns:
            Dict: 包含模型详细信息的字典
                - provider: 提供商（openai, anthropic等）
                - description: 模型描述
                - strengths: 优势列表
                - cost_level: 成本级别（low, medium, high）
                - context_window: 上下文窗口大小
                
        Example:
            >>> router = ModelRouter()
            >>> info = router.get_model_info("gpt-4o")
            >>> print(info['description'])
            'OpenAI 最新旗舰模型'
            >>> print(info['strengths'])
            ['深度推理', '复杂问题求解', '策略制定']
        """
        if model_name not in self.model_info:
            return {
                "provider": "unknown",
                "description": f"未知模型: {model_name}",
                "strengths": [],
                "cost_level": "unknown",
                "context_window": 0
            }
        
        return self.model_info[model_name]
    
    def get_all_models(self) -> list[str]:
        """
        获取所有可用的模型列表
        
        Returns:
            list: 所有模型名称的列表
        """
        return list(self.model_info.keys())
    
    def get_models_by_task(self, task_type: TaskType) -> Dict[str, str]:
        """
        获取指定任务类型的所有质量级别对应的模型
        
        Args:
            task_type: 任务类型
            
        Returns:
            Dict: 质量级别到模型名称的映射
            
        Example:
            >>> router = ModelRouter()
            >>> models = router.get_models_by_task(TaskType.CREATION)
            >>> print(models)
            {'fast': 'gpt-4o-mini', 'balanced': 'claude-3.5-sonnet', 'high': 'claude-3.5-sonnet'}
        """
        task_key = task_type.value
        return self.task_mapping.get(task_key, {})
    
    def suggest_model(
        self, 
        task_description: str,
        prefer_fast: bool = False
    ) -> str:
        """
        根据任务描述智能推荐模型（简单的启发式规则）
        
        Args:
            task_description: 任务描述文本
            prefer_fast: 是否优先考虑速度
            
        Returns:
            str: 推荐的模型名称
            
        Note:
            这是一个简化的实现，未来可以使用更复杂的启发式或机器学习方法
        """
        desc_lower = task_description.lower()
        
        # 关键词匹配（简单的启发式规则）
        if any(word in desc_lower for word in ['分析', 'analyze', '研究', 'study']):
            task_type = TaskType.ANALYSIS
        elif any(word in desc_lower for word in ['创作', 'create', '写作', 'write', '生成', 'generate']):
            task_type = TaskType.CREATION
        elif any(word in desc_lower for word in ['评审', 'review', '检查', 'check', '评分', 'score']):
            task_type = TaskType.REVIEW
        elif any(word in desc_lower for word in ['图片', 'image', '视觉', 'visual', '图像']):
            task_type = TaskType.VISION
        else:
            # 默认使用推理任务
            task_type = TaskType.REASONING
        
        # 根据速度偏好选择质量级别
        quality = QualityLevel.FAST if prefer_fast else QualityLevel.BALANCED
        
        return self.select_model(task_type, quality)
    
    def print_info(self):
        """
        打印路由器配置信息（用于调试）
        """
        print("=" * 60)
        print("Model Router 配置信息")
        print("=" * 60)
        
        print("\n📋 支持的任务类型:")
        for task in TaskType:
            print(f"  - {task.value}")
        
        print("\n📊 质量级别:")
        for level in QualityLevel:
            print(f"  - {level.value}")
        
        print("\n🤖 可用模型:")
        for model_name in self.get_all_models():
            info = self.get_model_info(model_name)
            print(f"  - {model_name}")
            print(f"    提供商: {info['provider']}")
            print(f"    描述: {info['description']}")
            print(f"    成本: {info['cost_level']}")
        
        print("\n🔄 降级链:")
        for primary, fallback in self.fallback_models.items():
            if fallback:
                print(f"  {primary} → {fallback}")
            else:
                print(f"  {primary} → (无备用)")
        
        print("=" * 60)


# 便捷函数：快速创建路由器实例
def create_router() -> ModelRouter:
    """
    创建并返回一个 ModelRouter 实例
    
    这是一个便捷函数，用于快速获取路由器实例
    """
    return ModelRouter()


# 模块级别的单例实例（可选）
_router_instance = None

def get_router() -> ModelRouter:
    """
    获取全局单例路由器实例
    
    如果路由器尚未创建，则创建一个新实例
    后续调用将返回同一个实例
    """
    global _router_instance
    if _router_instance is None:
        _router_instance = ModelRouter()
    return _router_instance


if __name__ == "__main__":
    # 测试代码
    print("🧪 Model Router 测试\n")
    
    router = ModelRouter()
    
    # 测试 1: 基础模型选择
    print("=" * 60)
    print("测试 1: 基础模型选择")
    print("=" * 60)
    
    test_cases = [
        (TaskType.ANALYSIS, QualityLevel.BALANCED),
        (TaskType.CREATION, QualityLevel.HIGH),
        (TaskType.REVIEW, QualityLevel.FAST),
    ]
    
    for task, quality in test_cases:
        model = router.select_model(task, quality)
        print(f"任务: {task.value:12} | 质量: {quality.value:10} → 模型: {model}")
    
    # 测试 2: 降级策略
    print("\n" + "=" * 60)
    print("测试 2: 降级策略")
    print("=" * 60)
    
    models_to_test = ["gpt-4o", "claude-3.5-sonnet", "gpt-4o-mini"]
    for model in models_to_test:
        fallback = router.get_fallback_model(model)
        print(f"{model:25} → {fallback or '(无备用)'}")
    
    # 测试 3: 模型信息
    print("\n" + "=" * 60)
    print("测试 3: 模型信息查询")
    print("=" * 60)
    
    info = router.get_model_info("gpt-4o")
    print(f"模型: gpt-4o")
    print(f"  描述: {info['description']}")
    print(f"  优势: {', '.join(info['strengths'])}")
    print(f"  成本: {info['cost_level']}")
    
    # 测试 4: 智能推荐
    print("\n" + "=" * 60)
    print("测试 4: 智能推荐")
    print("=" * 60)
    
    tasks = [
        "分析这篇文章的主要观点",
        "创作一篇小红书帖子",
        "评审这段代码的质量"
    ]
    
    for task_desc in tasks:
        recommended = router.suggest_model(task_desc)
        print(f"任务: {task_desc:30} → 推荐: {recommended}")
    
    print("\n✅ 测试完成！")
