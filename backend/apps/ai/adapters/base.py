# -*- coding: utf-8 -*-
"""
AI适配器基础类
定义统一的AI服务接口规范
"""
import asyncio
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union, AsyncIterator, Any
from enum import Enum
import logging

from .exceptions import (
    AIServiceException, RateLimitException, AuthenticationException,
    ModelNotFoundException, ServiceUnavailableException
)

logger = logging.getLogger(__name__)


class AIProviderType(Enum):
    """AI提供商类型"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    AZURE = "azure"
    LOCAL = "local"
    CUSTOM = "custom"


class MessageRole(Enum):
    """消息角色"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    FUNCTION = "function"


@dataclass
class AIMessage:
    """AI消息数据结构"""
    role: MessageRole
    content: str
    timestamp: Optional[float] = field(default_factory=time.time)
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)


@dataclass
class AIModelConfig:
    """AI模型配置"""
    provider: AIProviderType
    model_name: str
    api_key: str
    base_url: Optional[str] = None
    max_tokens: int = 4000
    temperature: float = 0.7
    top_p: float = 0.9
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    stream_chunk_size: int = 1024
    
    # 高级配置
    context_window: int = 8192
    supports_streaming: bool = True
    supports_function_calling: bool = False
    supports_vision: bool = False
    
    # 成本控制
    cost_per_input_token: float = 0.0
    cost_per_output_token: float = 0.0
    daily_quota_limit: Optional[int] = None
    
    def __post_init__(self):
        """配置验证"""
        if self.max_tokens > self.context_window:
            self.max_tokens = self.context_window - 1000  # 留出系统提示空间
        
        if self.temperature < 0 or self.temperature > 2:
            raise ValueError("temperature必须在0-2之间")
        
        if not self.api_key:
            raise ValueError("api_key不能为空")


@dataclass
class AIResponse:
    """AI响应数据结构"""
    content: str
    model: str
    provider: str
    usage: Optional[Dict[str, int]] = None
    finish_reason: Optional[str] = None
    response_time: Optional[float] = None
    cost: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)
    
    def calculate_cost(self, config: AIModelConfig) -> float:
        """计算API调用成本"""
        if not self.usage or not config.cost_per_input_token:
            return 0.0
        
        input_cost = self.usage.get('prompt_tokens', 0) * config.cost_per_input_token
        output_cost = self.usage.get('completion_tokens', 0) * config.cost_per_output_token
        
        return input_cost + output_cost


@dataclass
class HealthCheckResult:
    """健康检查结果"""
    is_healthy: bool
    response_time: float
    error_message: Optional[str] = None
    model_available: bool = True
    quota_remaining: Optional[int] = None
    last_check: float = field(default_factory=time.time)


class BaseAIAdapter(ABC):
    """AI适配器抽象基类"""
    
    def __init__(self, config: AIModelConfig):
        self.config = config
        self.provider_type = config.provider
        self._session = None
        self._last_health_check: Optional[HealthCheckResult] = None
        
        # 验证配置
        self.validate_config()
    
    @abstractmethod
    def validate_config(self) -> None:
        """验证配置有效性"""
        pass
    
    @abstractmethod
    async def generate_response(
        self,
        messages: List[AIMessage],
        **kwargs
    ) -> AIResponse:
        """生成AI响应"""
        pass
    
    @abstractmethod
    async def stream_response(
        self,
        messages: List[AIMessage],
        **kwargs
    ) -> AsyncIterator[str]:
        """流式生成AI响应"""
        pass
    
    @abstractmethod
    async def health_check(self) -> HealthCheckResult:
        """健康检查"""
        pass
    
    async def estimate_tokens(self, text: str) -> int:
        """估算文本token数量"""
        # 简单估算：1个token约等于4个字符
        return len(text) // 4 + 1
    
    async def validate_context_length(self, messages: List[AIMessage]) -> bool:
        """验证上下文长度是否超限"""
        total_tokens = 0
        for message in messages:
            total_tokens += await self.estimate_tokens(message.content)
        
        return total_tokens <= (self.config.context_window - self.config.max_tokens)
    
    def format_messages(self, messages: List[AIMessage]) -> List[Dict[str, str]]:
        """格式化消息为API所需格式"""
        return [
            {
                "role": msg.role.value,
                "content": msg.content
            }
            for msg in messages
        ]
    
    def create_system_message(self, content: str) -> AIMessage:
        """创建系统消息"""
        return AIMessage(role=MessageRole.SYSTEM, content=content)
    
    def create_user_message(self, content: str) -> AIMessage:
        """创建用户消息"""
        return AIMessage(role=MessageRole.USER, content=content)
    
    def create_assistant_message(self, content: str) -> AIMessage:
        """创建助手消息"""
        return AIMessage(role=MessageRole.ASSISTANT, content=content)
    
    async def retry_on_failure(self, func, *args, **kwargs):
        """重试机制"""
        last_exception = None
        
        for attempt in range(self.config.max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except (RateLimitException, ServiceUnavailableException) as e:
                last_exception = e
                if attempt < self.config.max_retries:
                    # 指数退避
                    delay = self.config.retry_delay * (2 ** attempt)
                    logger.warning(f"重试第{attempt + 1}次，延迟{delay}秒: {e}")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"重试{self.config.max_retries}次后仍然失败: {e}")
                    break
            except Exception as e:
                # 对于其他异常，不重试
                logger.error(f"AI服务调用失败: {e}")
                raise e
        
        raise last_exception
    
    def get_provider_name(self) -> str:
        """获取提供商名称"""
        return self.provider_type.value
    
    def get_model_name(self) -> str:
        """获取模型名称"""
        return self.config.model_name
    
    def is_healthy(self) -> bool:
        """检查服务是否健康"""
        if not self._last_health_check:
            return False
        
        # 健康检查结果5分钟内有效
        age = time.time() - self._last_health_check.last_check
        return age < 300 and self._last_health_check.is_healthy
    
    def get_health_status(self) -> Optional[HealthCheckResult]:
        """获取健康状态"""
        return self._last_health_check
    
    async def refresh_health_check(self) -> HealthCheckResult:
        """刷新健康检查"""
        try:
            self._last_health_check = await self.health_check()
            return self._last_health_check
        except Exception as e:
            logger.error(f"健康检查失败: {e}")
            self._last_health_check = HealthCheckResult(
                is_healthy=False,
                response_time=0.0,
                error_message=str(e),
                model_available=False
            )
            return self._last_health_check
    
    def __str__(self):
        return f"{self.__class__.__name__}({self.config.provider.value}:{self.config.model_name})"
    
    def __repr__(self):
        return self.__str__()


class MockAIAdapter(BaseAIAdapter):
    """Mock AI适配器，用于测试"""
    
    def __init__(self, config: AIModelConfig):
        super().__init__(config)
        self.response_delay = 0.1
    
    def validate_config(self) -> None:
        """Mock适配器总是有效"""
        pass
    
    async def generate_response(
        self,
        messages: List[AIMessage],
        **kwargs
    ) -> AIResponse:
        """生成模拟响应"""
        await asyncio.sleep(self.response_delay)
        
        last_message = messages[-1] if messages else None
        mock_content = f"这是一个模拟的AI响应，针对消息: {last_message.content if last_message else 'None'}"
        
        return AIResponse(
            content=mock_content,
            model=self.config.model_name,
            provider=self.config.provider.value,
            usage={
                'prompt_tokens': 50,
                'completion_tokens': 20,
                'total_tokens': 70
            },
            finish_reason='stop',
            response_time=self.response_delay,
            cost=0.001
        )
    
    async def stream_response(
        self,
        messages: List[AIMessage],
        **kwargs
    ) -> AsyncIterator[str]:
        """流式模拟响应"""
        response = await self.generate_response(messages, **kwargs)
        
        # 将响应分块发送
        words = response.content.split()
        for i, word in enumerate(words):
            await asyncio.sleep(0.05)  # 模拟流式延迟
            if i == len(words) - 1:
                yield word
            else:
                yield word + " "
    
    async def health_check(self) -> HealthCheckResult:
        """模拟健康检查"""
        start_time = time.time()
        await asyncio.sleep(0.01)  # 模拟网络延迟
        
        return HealthCheckResult(
            is_healthy=True,
            response_time=time.time() - start_time,
            model_available=True,
            quota_remaining=1000
        )

