"""
并行执行器
用于并行执行多个独立的任务，提升整体性能
"""

import logging
import time
from typing import List, Callable, Any, Dict, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Task:
    """任务定义"""
    name: str
    func: Callable
    args: tuple = ()
    kwargs: dict = None
    
    def __post_init__(self):
        if self.kwargs is None:
            self.kwargs = {}


@dataclass
class TaskResult:
    """任务结果"""
    name: str
    success: bool
    result: Any = None
    error: Exception = None
    elapsed_time: float = 0.0


class ParallelExecutor:
    """
    并行执行器
    
    用于并行执行多个独立的任务，如评审、图片生成等
    """
    
    def __init__(self, max_workers: int = 3):
        """
        初始化执行器
        
        Args:
            max_workers: 最大并行工作线程数
        """
        self.max_workers = max_workers
        logger.info(f"初始化并行执行器，最大工作线程: {max_workers}")
    
    def execute_tasks(
        self,
        tasks: List[Task],
        timeout: float = None
    ) -> Dict[str, TaskResult]:
        """
        并行执行多个任务
        
        Args:
            tasks: 任务列表
            timeout: 超时时间（秒），None表示不限制
            
        Returns:
            任务名称到结果的映射
            
        Example:
            >>> executor = ParallelExecutor(max_workers=2)
            >>> tasks = [
            ...     Task("task1", func1, args=(arg1,)),
            ...     Task("task2", func2, kwargs={'key': 'value'})
            ... ]
            >>> results = executor.execute_tasks(tasks)
            >>> print(results["task1"].result)
        """
        if not tasks:
            logger.warning("任务列表为空")
            return {}
        
        logger.info(f"开始并行执行 {len(tasks)} 个任务")
        start_time = time.time()
        
        results = {}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_task = {}
            for task in tasks:
                future = executor.submit(self._execute_single_task, task)
                future_to_task[future] = task
            
            # 收集结果
            for future in as_completed(future_to_task, timeout=timeout):
                task = future_to_task[future]
                try:
                    result = future.result()
                    results[task.name] = result
                    
                    status = "✅" if result.success else "❌"
                    logger.info(
                        f"{status} {task.name} 完成 "
                        f"({result.elapsed_time:.2f}秒)"
                    )
                except Exception as e:
                    logger.error(f"任务 {task.name} 异常: {str(e)}")
                    results[task.name] = TaskResult(
                        name=task.name,
                        success=False,
                        error=e
                    )
        
        total_time = time.time() - start_time
        success_count = sum(1 for r in results.values() if r.success)
        
        logger.info(
            f"并行执行完成: {success_count}/{len(tasks)} 成功, "
            f"总耗时 {total_time:.2f}秒"
        )
        
        return results
    
    def _execute_single_task(self, task: Task) -> TaskResult:
        """
        执行单个任务
        
        Args:
            task: 任务定义
            
        Returns:
            任务结果
        """
        start_time = time.time()
        
        try:
            logger.debug(f"开始执行任务: {task.name}")
            result = task.func(*task.args, **task.kwargs)
            elapsed_time = time.time() - start_time
            
            return TaskResult(
                name=task.name,
                success=True,
                result=result,
                elapsed_time=elapsed_time
            )
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(
                f"任务 {task.name} 失败: {str(e)}",
                exc_info=True
            )
            
            return TaskResult(
                name=task.name,
                success=False,
                error=e,
                elapsed_time=elapsed_time
            )


def parallel_review(
    content_data: dict,
    enable_engagement: bool = False
) -> Dict[str, Any]:
    """
    并行执行多个评审
    
    这是一个便捷函数，用于并行执行质量评审和合规性检查
    
    Args:
        content_data: 内容数据
        enable_engagement: 是否启用互动评审（较慢）
        
    Returns:
        评审结果字典
        
    Example:
        >>> results = parallel_review({
        ...     "title": "标题",
        ...     "content": "正文",
        ...     "topic": "话题"
        ... })
        >>> print(results['quality']['score'])
        >>> print(results['compliance']['passed'])
    """
    from agents.reviewers.quality_reviewer import review_quality
    from tools.review_tools_v1 import review_compliance
    
    tasks = [
        Task(
            name="quality",
            func=review_quality,
            kwargs={"content_data": content_data}
        ),
        Task(
            name="compliance",
            func=review_compliance,
            kwargs={"content_data": content_data}
        )
    ]
    
    # 可选：添加互动评审
    if enable_engagement:
        from agents.reviewers.engagement_reviewer import review_engagement
        tasks.append(Task(
            name="engagement",
            func=review_engagement,
            kwargs={"content_data": content_data}
        ))
    
    # 并行执行
    executor = ParallelExecutor(max_workers=len(tasks))
    task_results = executor.execute_tasks(tasks)
    
    # 解析结果
    import json
    results = {}
    
    for name, task_result in task_results.items():
        if task_result.success:
            try:
                results[name] = json.loads(task_result.result)
            except json.JSONDecodeError:
                logger.warning(f"无法解析 {name} 的JSON结果")
                results[name] = {"error": "JSON解析失败"}
        else:
            results[name] = {
                "error": str(task_result.error) if task_result.error else "执行失败"
            }
    
    return results


__all__ = [
    'ParallelExecutor',
    'Task',
    'TaskResult',
    'parallel_review'
]

