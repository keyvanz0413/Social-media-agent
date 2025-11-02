"""
LLM Client - 统一的 LLM 调用封装
支持 OpenAI、Anthropic、Ollama 等多种提供商
"""

import logging
import os
from typing import Optional, List, Dict, Any
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

# 尝试导入所需的库
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None

from config import ModelConfig

# 配置日志
logger = logging.getLogger(__name__)


class LLMError(Exception):
    """LLM 调用异常"""
    pass


class LLMClient:
    """
    统一的 LLM 客户端封装
    
    支持多个提供商：
    - OpenAI (gpt-4o, gpt-4o-mini, gpt-4o-vision)
    - Anthropic (claude-3.5-sonnet)
    - Ollama (llama3.2, 及其他本地模型)
    - 第三方 OpenAI 兼容平台
    """
    
    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        openai_base_url: Optional[str] = None,
        anthropic_api_key: Optional[str] = None,
        ollama_base_url: Optional[str] = None
    ):
        """
        初始化 LLM 客户端
        
        Args:
            openai_api_key: OpenAI API Key（如果使用 OpenAI 或第三方平台）
            openai_base_url: OpenAI Base URL（可选，用于第三方平台）
            anthropic_api_key: Anthropic API Key（如果使用 Claude）
            ollama_base_url: Ollama Base URL（默认：http://localhost:11434/v1）
        """
        # 从配置或参数获取 API Keys
        self.openai_api_key = openai_api_key or ModelConfig.OPENAI_API_KEY
        self.openai_base_url = openai_base_url or ModelConfig.OPENAI_BASE_URL
        self.anthropic_api_key = anthropic_api_key or ModelConfig.ANTHROPIC_API_KEY
        self.ollama_base_url = ollama_base_url or ModelConfig.OLLAMA_BASE_URL
        
        # 初始化客户端（延迟初始化）
        self._openai_client = None
        self._anthropic_client = None
        
        # 检查必要的库是否已安装
        if OpenAI is None:
            logger.warning("openai 库未安装，无法使用 OpenAI 模型")
        if Anthropic is None:
            logger.warning("anthropic 库未安装，无法使用 Claude 模型")
    
    def _get_openai_client(self) -> Optional[OpenAI]:
        """获取 OpenAI 客户端（延迟初始化）"""
        if OpenAI is None:
            return None
        
        if self._openai_client is None:
            if not self.openai_api_key:
                return None
            
            kwargs = {"api_key": self.openai_api_key}
            if self.openai_base_url:
                kwargs["base_url"] = self.openai_base_url
            
            self._openai_client = OpenAI(**kwargs)
            logger.debug(f"初始化 OpenAI 客户端，Base URL: {self.openai_base_url or '默认'}")
        
        return self._openai_client
    
    def _get_anthropic_client(self) -> Optional[Anthropic]:
        """获取 Anthropic 客户端（延迟初始化）"""
        if Anthropic is None:
            return None
        
        if self._anthropic_client is None:
            if not self.anthropic_api_key:
                return None
            
            self._anthropic_client = Anthropic(api_key=self.anthropic_api_key)
            logger.debug("初始化 Anthropic 客户端")
        
        return self._anthropic_client
    
    def _detect_provider(self, model_name: str) -> str:
        """
        检测模型所属的提供商
        
        Args:
            model_name: 模型名称（如 "gpt-4o", "claude-3.5-sonnet", "llama3.2"）
            
        Returns:
            提供商名称：openai, anthropic, ollama
            
        Raises:
            LLMError: 如果无法识别提供商
        """
        model_lower = model_name.lower()
        
        # Anthropic 模型
        if "claude" in model_lower:
            return "anthropic"
        
        # Ollama 模型（通常不包含 "gpt" 或 "claude"）
        if model_lower.startswith(("llama", "qwen", "mistral", "phi", "gemma")):
            return "ollama"
        
        # OpenAI 模型或第三方平台（默认）
        if any(keyword in model_lower for keyword in ["gpt", "o1", "text-"]):
            return "openai"
        
        # 如果配置了自定义 base_url，可能是第三方平台
        if self.openai_base_url and "openai.com" not in self.openai_base_url.lower():
            return "openai"  # 使用 OpenAI 兼容接口
        
        # 默认尝试 OpenAI（包括第三方平台）
        return "openai"
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((LLMError, Exception))
    )
    def call_llm(
        self,
        prompt: str,
        model_name: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """
        统一的 LLM 调用接口
        
        Args:
            prompt: 用户提示词
            model_name: 模型名称（如 "gpt-4o", "claude-3.5-sonnet", "llama3.2"）
            system_prompt: 系统提示词（可选）
            temperature: 温度参数（0.0-2.0），默认 0.7
            max_tokens: 最大生成 token 数，默认 2000
            **kwargs: 其他模型特定参数
            
        Returns:
            生成的文本内容
            
        Raises:
            LLMError: 调用失败时抛出
            
        Example:
            >>> client = LLMClient()
            >>> result = client.call_llm(
            ...     prompt="分析这段文本的情感倾向",
            ...     model_name="gpt-4o",
            ...     system_prompt="你是一位专业的情感分析专家"
            ... )
        """
        # Mock 模式检查
        from config import DevConfig
        if DevConfig.MOCK_MODE:
            logger.info(f"🎭 Mock 模式：模拟 LLM 调用 ({model_name})")
            from utils.mock_data import get_mock_llm_response
            
            # 根据提示词推断任务类型
            task_type = 'general'
            if 'analyze' in prompt.lower() or '分析' in prompt:
                task_type = 'analysis'
            elif 'create' in prompt.lower() or '创作' in prompt or '生成' in prompt:
                task_type = 'creation'
            
            return get_mock_llm_response(prompt, task_type)
        
        try:
            provider = self._detect_provider(model_name)
            logger.info(f"调用 {provider} 模型: {model_name}")
            
            if provider == "openai":
                return self._call_openai(
                    prompt=prompt,
                    model_name=model_name,
                    system_prompt=system_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )
            elif provider == "anthropic":
                return self._call_anthropic(
                    prompt=prompt,
                    model_name=model_name,
                    system_prompt=system_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )
            elif provider == "ollama":
                return self._call_ollama(
                    prompt=prompt,
                    model_name=model_name,
                    system_prompt=system_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )
            else:
                raise LLMError(f"不支持的提供商: {provider}")
                
        except Exception as e:
            if isinstance(e, LLMError):
                raise
            error_msg = f"调用 LLM 失败 ({model_name}): {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise LLMError(error_msg) from e
    
    def _call_openai(
        self,
        prompt: str,
        model_name: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> str:
        """调用 OpenAI API"""
        client = self._get_openai_client()
        if client is None:
            raise LLMError("OpenAI 客户端未初始化，请检查 OPENAI_API_KEY 配置")
        
        # 构建消息列表
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            content = response.choices[0].message.content
            if not content:
                raise LLMError("OpenAI 返回空内容")
            
            logger.debug(f"OpenAI 调用成功，生成 {len(content)} 字符")
            return content
            
        except Exception as e:
            raise LLMError(f"OpenAI API 调用失败: {str(e)}")
    
    def _call_anthropic(
        self,
        prompt: str,
        model_name: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> str:
        """调用 Anthropic API"""
        client = self._get_anthropic_client()
        if client is None:
            raise LLMError("Anthropic 客户端未初始化，请检查 ANTHROPIC_API_KEY 配置")
        
        try:
            # Anthropic API 的消息格式
            messages = [{"role": "user", "content": prompt}]
            
            api_kwargs = {
                "model": model_name,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            
            # Anthropic 的系统提示词通过 system 参数传递
            if system_prompt:
                api_kwargs["system"] = system_prompt
            
            # 添加其他参数
            api_kwargs.update(kwargs)
            
            response = client.messages.create(**api_kwargs)
            
            if not response.content or len(response.content) == 0:
                raise LLMError("Anthropic 返回空内容")
            
            # Anthropic 返回的内容是列表格式
            content = ""
            for block in response.content:
                if hasattr(block, 'text'):
                    content += block.text
                elif isinstance(block, str):
                    content += block
            
            if not content:
                raise LLMError("Anthropic 返回内容为空")
            
            logger.debug(f"Anthropic 调用成功，生成 {len(content)} 字符")
            return content
            
        except Exception as e:
            raise LLMError(f"Anthropic API 调用失败: {str(e)}")
    
    def _call_ollama(
        self,
        prompt: str,
        model_name: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> str:
        """调用 Ollama API（通过 OpenAI 兼容接口）"""
        # Ollama 使用 OpenAI 兼容接口
        if not self.ollama_base_url:
            raise LLMError("OLLAMA_BASE_URL 未配置")
        
        # 临时创建 OpenAI 客户端指向 Ollama
        try:
            if OpenAI is None:
                raise LLMError("openai 库未安装，无法使用 Ollama")
            
            ollama_client = OpenAI(
                api_key="ollama",  # Ollama 不需要真实的 API Key
                base_url=self.ollama_base_url
            )
            
            # 构建消息
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = ollama_client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            content = response.choices[0].message.content
            if not content:
                raise LLMError("Ollama 返回空内容")
            
            logger.debug(f"Ollama 调用成功，生成 {len(content)} 字符")
            return content
            
        except Exception as e:
            raise LLMError(f"Ollama API 调用失败: {str(e)}")


# 便捷函数：快速创建客户端并调用
def call_llm(
    prompt: str,
    model_name: str,
    system_prompt: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 2000,
    **kwargs
) -> str:
    """
    便捷函数：快速调用 LLM
    
    Args:
        prompt: 用户提示词
        model_name: 模型名称
        system_prompt: 系统提示词（可选）
        temperature: 温度参数，默认 0.7
        max_tokens: 最大 token 数，默认 2000
        **kwargs: 其他参数
        
    Returns:
        生成的文本内容
        
    Example:
        >>> result = call_llm("写一首诗", "gpt-4o-mini")
        >>> print(result)
    """
    client = LLMClient()
    return client.call_llm(
        prompt=prompt,
        model_name=model_name,
        system_prompt=system_prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        **kwargs
    )


# 模块级别的单例实例（可选）
_client_instance = None


def get_client() -> LLMClient:
    """
    获取全局单例 LLM 客户端实例
    
    如果客户端尚未创建，则创建一个新实例
    后续调用将返回同一个实例
    """
    global _client_instance
    if _client_instance is None:
        _client_instance = LLMClient()
    return _client_instance


if __name__ == "__main__":
    # 测试代码
    print("🧪 LLM Client 测试\n")
    
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    
    # 测试 1: 检测提供商
    print("=" * 60)
    print("测试 1: 提供商检测")
    print("=" * 60)
    
    client = LLMClient()
    test_models = [
        "gpt-4o",
        "claude-3.5-sonnet",
        "llama3.2",
        "gpt-4o-mini"
    ]
    
    for model in test_models:
        provider = client._detect_provider(model)
        print(f"模型: {model:25} → 提供商: {provider}")
    
    # 测试 2: 实际调用（需要配置 API Key）
    print("\n" + "=" * 60)
    print("测试 2: LLM 调用（需要配置 API Key）")
    print("=" * 60)
    
    test_prompt = "用一句话介绍人工智能"
    
    # 测试 OpenAI（如果有配置）
    if ModelConfig.OPENAI_API_KEY:
        try:
            print(f"\n测试 OpenAI (gpt-4o-mini)...")
            result = call_llm(
                prompt=test_prompt,
                model_name="gpt-4o-mini",
                max_tokens=100
            )
            print(f"结果: {result[:100]}...")
        except Exception as e:
            print(f"❌ OpenAI 调用失败: {e}")
    else:
        print("⚠️  OPENAI_API_KEY 未配置，跳过 OpenAI 测试")
    
    # 测试 Anthropic（如果有配置）
    if ModelConfig.ANTHROPIC_API_KEY:
        try:
            print(f"\n测试 Anthropic (claude-3.5-sonnet)...")
            result = call_llm(
                prompt=test_prompt,
                model_name="claude-3.5-sonnet",
                max_tokens=100
            )
            print(f"结果: {result[:100]}...")
        except Exception as e:
            print(f"❌ Anthropic 调用失败: {e}")
    else:
        print("⚠️  ANTHROPIC_API_KEY 未配置，跳过 Anthropic 测试")
    
    print("\n✅ 测试完成！")

