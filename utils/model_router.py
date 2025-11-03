"""
Model Router - 智能模型路由器
根据任务类型自动选择最优的 LLM 模型

Features:
- 自动模型选择（基于任务类型和质量要求）
- 自动降级策略（主模型失败时自动切换备用模型）
- 模型健康检查和可用性检测
- 重试机制和错误恢复
"""

from enum import Enum
from typing import Dict, Optional, Any, Callable, Tuple
import os
import logging
import time
from functools import wraps
from config import ModelConfig

logger = logging.getLogger(__name__)


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
    
    def get_fallback_chain(self, primary_model: str, max_depth: int = 5) -> list[str]:
        """
        获取完整的降级链
        
        Args:
            primary_model: 主模型名称
            max_depth: 最大降级深度，防止循环引用
            
        Returns:
            list: 降级链列表，从主模型到最终备用模型
            
        Example:
            >>> router = ModelRouter()
            >>> chain = router.get_fallback_chain("gpt-4o")
            >>> print(chain)
            ['gpt-4o', 'gpt-4o-mini']
        """
        chain = [primary_model]
        current = primary_model
        depth = 0
        
        while depth < max_depth:
            fallback = self.get_fallback_model(current)
            if fallback is None or fallback in chain:
                break
            chain.append(fallback)
            current = fallback
            depth += 1
        
        return chain
    
    def call_with_fallback(
        self,
        model_name: str,
        call_function: Callable,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        **kwargs
    ) -> Tuple[Any, str]:
        """
        使用自动降级策略调用 LLM
        
        当主模型调用失败时，自动尝试降级链中的备用模型，
        并支持每个模型的重试机制。
        
        Args:
            model_name: 主模型名称
            call_function: 调用函数，签名应为 func(model=..., **kwargs)
            max_retries: 每个模型的最大重试次数
            retry_delay: 重试延迟（秒）
            **kwargs: 传递给 call_function 的额外参数
            
        Returns:
            Tuple[Any, str]: (调用结果, 成功使用的模型名称)
            
        Raises:
            Exception: 如果所有模型都失败，抛出最后一个异常
            
        Example:
            >>> def my_llm_call(model, prompt):
            ...     # 你的 LLM 调用逻辑
            ...     return llm.chat(model=model, messages=[{"role": "user", "content": prompt}])
            >>> 
            >>> router = ModelRouter()
            >>> result, used_model = router.call_with_fallback(
            ...     "gpt-4o",
            ...     my_llm_call,
            ...     prompt="分析这段文本"
            ... )
            >>> print(f"使用模型: {used_model}")
            >>> print(f"结果: {result}")
        """
        fallback_chain = self.get_fallback_chain(model_name)
        last_exception = None
        
        for model in fallback_chain:
            logger.info(f"尝试使用模型: {model}")
            
            # 对每个模型进行重试
            for attempt in range(max_retries):
                try:
                    result = call_function(model=model, **kwargs)
                    
                    # 成功！记录并返回
                    if model != model_name:
                        logger.warning(
                            f"主模型 {model_name} 不可用，已降级至 {model}"
                        )
                    else:
                        logger.info(f"成功使用模型: {model}")
                    
                    return result, model
                    
                except Exception as e:
                    last_exception = e
                    logger.warning(
                        f"模型 {model} 调用失败 (尝试 {attempt + 1}/{max_retries}): {str(e)}"
                    )
                    
                    # 如果不是最后一次重试，等待后再试
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
            
            # 这个模型的所有重试都失败了，尝试下一个备用模型
            logger.error(f"模型 {model} 在 {max_retries} 次重试后仍然失败，尝试降级")
        
        # 所有模型都失败了
        logger.error(f"所有模型都失败了！降级链: {fallback_chain}")
        raise Exception(
            f"所有模型调用失败。最后错误: {str(last_exception)}"
        )
    
    def check_model_availability(
        self,
        model_name: str,
        test_function: Optional[Callable] = None,
        timeout: float = 10.0
    ) -> bool:
        """
        检查模型是否可用
        
        Args:
            model_name: 要检查的模型名称
            test_function: 测试函数，用于实际调用模型
                         如果为 None，只检查配置是否存在
            timeout: 超时时间（秒）
            
        Returns:
            bool: 模型是否可用
            
        Example:
            >>> def test_call(model):
            ...     return llm.chat(model=model, messages=[{"role": "user", "content": "test"}])
            >>> 
            >>> router = ModelRouter()
            >>> is_available = router.check_model_availability("gpt-4o", test_call)
            >>> print(f"GPT-4o 可用: {is_available}")
        """
        # 1. 检查模型是否在配置中
        if model_name not in self.model_info:
            logger.warning(f"模型 {model_name} 不在配置中")
            return False
        
        # 2. 检查 API key 是否配置
        model_info = self.get_model_info(model_name)
        provider = model_info.get('provider', 'unknown')
        
        if provider == 'openai' and not ModelConfig.OPENAI_API_KEY:
            logger.warning(f"模型 {model_name} 需要 OPENAI_API_KEY")
            return False
        elif provider == 'anthropic' and not ModelConfig.ANTHROPIC_API_KEY:
            logger.warning(f"模型 {model_name} 需要 ANTHROPIC_API_KEY")
            return False
        
        # 3. 如果提供了测试函数，实际调用测试
        if test_function:
            try:
                import signal
                
                # 设置超时
                def timeout_handler(signum, frame):
                    raise TimeoutError("模型测试超时")
                
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(int(timeout))
                
                try:
                    test_function(model=model_name)
                    signal.alarm(0)  # 取消超时
                    logger.info(f"模型 {model_name} 可用")
                    return True
                except Exception as e:
                    signal.alarm(0)  # 取消超时
                    logger.warning(f"模型 {model_name} 测试失败: {str(e)}")
                    return False
                    
            except Exception as e:
                logger.warning(f"模型可用性检查失败: {str(e)}")
                return False
        
        # 如果没有测试函数，只检查配置
        return True
    
    def get_available_models(
        self,
        test_function: Optional[Callable] = None
    ) -> Dict[str, bool]:
        """
        获取所有模型的可用性状态
        
        Args:
            test_function: 可选的测试函数
            
        Returns:
            Dict: 模型名称到可用性的映射
            
        Example:
            >>> router = ModelRouter()
            >>> availability = router.get_available_models()
            >>> for model, is_available in availability.items():
            ...     status = "✅" if is_available else "❌"
            ...     print(f"{status} {model}")
        """
        availability = {}
        
        for model_name in self.get_all_models():
            availability[model_name] = self.check_model_availability(
                model_name,
                test_function
            )
        
        return availability
    
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
                fallback_chain = self.get_fallback_chain(primary)
                chain_str = " → ".join(fallback_chain)
                print(f"  {chain_str}")
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


# 装饰器：自动降级
def with_fallback(
    model_name: str,
    max_retries: int = 3,
    retry_delay: float = 1.0
):
    """
    装饰器：为函数添加自动降级功能
    
    Args:
        model_name: 主模型名称
        max_retries: 每个模型的最大重试次数
        retry_delay: 重试延迟（秒）
        
    Example:
        >>> @with_fallback("gpt-4o", max_retries=3)
        ... def analyze_content(model: str, prompt: str):
        ...     return llm.chat(model=model, messages=[{"role": "user", "content": prompt}])
        >>> 
        >>> result = analyze_content(prompt="分析这段文本")
        >>> # 如果 gpt-4o 失败，会自动尝试 gpt-4o-mini
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            router = get_router()
            
            # 创建调用函数
            def call_func(model: str, **kw):
                return func(*args, model=model, **{**kwargs, **kw})
            
            result, used_model = router.call_with_fallback(
                model_name,
                call_func,
                max_retries=max_retries,
                retry_delay=retry_delay
            )
            
            return result
        
        return wrapper
    return decorator


def select_best_available_model(
    task_type: TaskType,
    quality_level: QualityLevel = QualityLevel.BALANCED,
    test_function: Optional[Callable] = None
) -> str:
    """
    选择最佳可用模型
    
    如果首选模型不可用，自动选择降级链中的第一个可用模型
    
    Args:
        task_type: 任务类型
        quality_level: 质量级别
        test_function: 可选的测试函数
        
    Returns:
        str: 第一个可用的模型名称
        
    Example:
        >>> model = select_best_available_model(TaskType.ANALYSIS, QualityLevel.HIGH)
        >>> print(f"将使用模型: {model}")
    """
    router = get_router()
    
    # 选择首选模型
    preferred_model = router.select_model(task_type, quality_level)
    
    # 获取降级链
    fallback_chain = router.get_fallback_chain(preferred_model)
    
    # 检查每个模型的可用性
    for model in fallback_chain:
        if router.check_model_availability(model, test_function):
            if model != preferred_model:
                logger.info(
                    f"首选模型 {preferred_model} 不可用，使用 {model}"
                )
            return model
    
    # 如果所有模型都不可用，返回首选模型（让后续调用处理错误）
    logger.warning(
        f"降级链中所有模型都不可用: {fallback_chain}，返回首选模型"
    )
    return preferred_model


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
    
    # 测试 2: 降级链（增强版）
    print("\n" + "=" * 60)
    print("测试 2: 降级链（完整路径）")
    print("=" * 60)
    
    models_to_test = ["gpt-4o", "claude-3-5-sonnet-20241022", "gpt-4o-mini"]
    for model in models_to_test:
        chain = router.get_fallback_chain(model)
        chain_str = " → ".join(chain)
        print(f"{model:30} → {chain_str}")
    
    # 测试 3: 模型可用性检查
    print("\n" + "=" * 60)
    print("测试 3: 模型可用性检查（仅配置检查）")
    print("=" * 60)
    
    availability = router.get_available_models()
    for model_name, is_available in availability.items():
        status = "✅" if is_available else "❌"
        print(f"{status} {model_name}")
    
    # 测试 4: 模型信息
    print("\n" + "=" * 60)
    print("测试 4: 模型信息查询")
    print("=" * 60)
    
    info = router.get_model_info("gpt-4o")
    print(f"模型: gpt-4o")
    print(f"  描述: {info['description']}")
    print(f"  优势: {', '.join(info['strengths'])}")
    print(f"  成本: {info['cost_level']}")
    print(f"  上下文窗口: {info['context_window']:,} tokens")
    
    # 测试 5: 智能推荐
    print("\n" + "=" * 60)
    print("测试 5: 智能推荐")
    print("=" * 60)
    
    tasks = [
        "分析这篇文章的主要观点",
        "创作一篇小红书帖子",
        "评审这段代码的质量"
    ]
    
    for task_desc in tasks:
        recommended = router.suggest_model(task_desc)
        print(f"任务: {task_desc:30} → 推荐: {recommended}")
    
    # 测试 6: 选择最佳可用模型
    print("\n" + "=" * 60)
    print("测试 6: 选择最佳可用模型")
    print("=" * 60)
    
    test_tasks = [
        (TaskType.ANALYSIS, QualityLevel.HIGH),
        (TaskType.CREATION, QualityLevel.BALANCED),
        (TaskType.REVIEW, QualityLevel.FAST),
    ]
    
    for task, quality in test_tasks:
        best_model = select_best_available_model(task, quality)
        preferred = router.select_model(task, quality)
        if best_model != preferred:
            print(f"任务: {task.value:12} | 首选: {preferred:30} → 实际: {best_model}")
        else:
            print(f"任务: {task.value:12} | 模型: {best_model}")
    
    print("\n✅ 测试完成！")
    print("\n💡 使用提示:")
    print("  1. call_with_fallback() - 自动降级调用")
    print("  2. @with_fallback() - 装饰器模式")
    print("  3. select_best_available_model() - 智能选择")
