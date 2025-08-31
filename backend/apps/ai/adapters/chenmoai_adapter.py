# -*- coding: utf-8 -*-
"""
ChenmoAI API适配器
支持通过chenmoai中转站访问各种AI模型
"""
import asyncio
import time
import json
import aiohttp
from typing import List, AsyncIterator, Dict, Any
import logging

from .base import BaseAIAdapter, AIModelConfig, AIMessage, AIResponse, HealthCheckResult, AIProviderType
from .exceptions import (
    AIServiceException, RateLimitException, AuthenticationException,
    ModelNotFoundException, QuotaExceededException, ServiceUnavailableException,
    InvalidRequestException, ResponseParseException
)

logger = logging.getLogger(__name__)


class ChenmoAIAdapter(BaseAIAdapter):
    """ChenmoAI API适配器"""
    
    # 支持的模型列表（通过chenmoai中转访问）
    SUPPORTED_MODELS = {
        # GPT系列
        'gpt-4': {'context_window': 8192, 'supports_streaming': True},
        'gpt-4-turbo': {'context_window': 128000, 'supports_streaming': True},
        'gpt-4o': {'context_window': 128000, 'supports_streaming': True},
        'gpt-4o-mini': {'context_window': 128000, 'supports_streaming': True},
        'gpt-3.5-turbo': {'context_window': 16385, 'supports_streaming': True},
        
        # Claude系列
        'claude-3-opus-20240229': {'context_window': 200000, 'supports_streaming': True},
        'claude-3-sonnet-20240229': {'context_window': 200000, 'supports_streaming': True},
        'claude-3-haiku-20240307': {'context_window': 200000, 'supports_streaming': True},
        'claude-3-5-sonnet-20241022': {'context_window': 200000, 'supports_streaming': True},
        'claude-3-5-haiku-20241022': {'context_window': 200000, 'supports_streaming': True},
        
        # Gemini系列
        'gemini-1.5-pro': {'context_window': 1000000, 'supports_streaming': True},
        'gemini-1.5-flash': {'context_window': 1000000, 'supports_streaming': True},
        'gemini-2.0-flash-exp': {'context_window': 1000000, 'supports_streaming': True},
        
        # 其他模型
        'deepseek-chat': {'context_window': 32000, 'supports_streaming': True},
        'qwen-turbo': {'context_window': 8000, 'supports_streaming': True},
        'glm-4': {'context_window': 128000, 'supports_streaming': True},
    }
    
    def __init__(self, config: AIModelConfig):
        super().__init__(config)
        # 使用香港节点，连接更稳定
        self.base_url = config.base_url or "https://hk.chenmoai.cn/v1"
        self.headers = {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Alpha-AI-Assistant/1.0"
        }
    
    def validate_config(self) -> None:
        """验证ChenmoAI配置"""
        if not self.config.api_key.startswith('sk-'):
            logger.warning("ChenmoAI API密钥格式可能不正确")
        
        # 检查模型是否支持
        model_info = self.SUPPORTED_MODELS.get(self.config.model_name)
        if model_info:
            # 更新配置中的上下文窗口大小
            self.config.context_window = model_info['context_window']
            self.config.supports_streaming = model_info['supports_streaming']
    
    async def generate_response(
        self,
        messages: List[AIMessage],
        **kwargs
    ) -> AIResponse:
        """生成ChenmoAI响应"""
        start_time = time.time()
        
        # 构建请求数据
        request_data = {
            "model": self.config.model_name,
            "messages": self.format_messages(messages),
            "max_tokens": kwargs.get('max_tokens', self.config.max_tokens),
            "temperature": kwargs.get('temperature', self.config.temperature),
            "top_p": kwargs.get('top_p', self.config.top_p),
            "frequency_penalty": kwargs.get('frequency_penalty', self.config.frequency_penalty),
            "presence_penalty": kwargs.get('presence_penalty', self.config.presence_penalty),
            "stream": False
        }
        
        # 使用重试机制
        return await self.retry_on_failure(self._make_request, request_data, start_time)
    
    async def stream_response(
        self,
        messages: List[AIMessage],
        **kwargs
    ) -> AsyncIterator[str]:
        """流式生成ChenmoAI响应"""
        if not self.config.supports_streaming:
            # 如果模型不支持流式，回退到普通响应
            response = await self.generate_response(messages, **kwargs)
            yield response.content
            return
        
        request_data = {
            "model": self.config.model_name,
            "messages": self.format_messages(messages),
            "max_tokens": kwargs.get('max_tokens', self.config.max_tokens),
            "temperature": kwargs.get('temperature', self.config.temperature),
            "stream": True
        }
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
            async with session.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=request_data
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    raise await self._handle_error_response(response.status, error_text)
                
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    
                    if line.startswith('data: '):
                        data = line[6:]  # 去掉 'data: ' 前缀
                        
                        if data == '[DONE]':
                            break
                        
                        try:
                            chunk = json.loads(data)
                            delta = chunk.get('choices', [{}])[0].get('delta', {})
                            content = delta.get('content', '')
                            
                            if content:
                                yield content
                                
                        except json.JSONDecodeError:
                            continue  # 跳过无效的JSON
    
    async def _make_request(self, request_data: Dict[str, Any], start_time: float) -> AIResponse:
        """执行API请求"""
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.timeout)
        ) as session:
            try:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=request_data
                ) as response:
                    
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_response(data, response_time)
                    else:
                        error_text = await response.text()
                        raise await self._handle_error_response(response.status, error_text)
                        
            except asyncio.TimeoutError:
                raise ServiceUnavailableException(
                    f"ChenmoAI API请求超时（{self.config.timeout}秒）",
                    provider="chenmoai"
                )
            except aiohttp.ClientError as e:
                raise ServiceUnavailableException(
                    f"网络连接错误: {str(e)}",
                    provider="chenmoai"
                )
    
    def _parse_response(self, data: Dict[str, Any], response_time: float) -> AIResponse:
        """解析ChenmoAI响应"""
        try:
            choice = data['choices'][0]
            content = choice['message']['content']
            usage = data.get('usage', {})
            finish_reason = choice.get('finish_reason')
            
            # 计算成本（chenmoai通常比官方便宜）
            cost = 0.0
            if usage and self.config.cost_per_input_token > 0:
                input_cost = usage.get('prompt_tokens', 0) * self.config.cost_per_input_token
                output_cost = usage.get('completion_tokens', 0) * self.config.cost_per_output_token
                cost = input_cost + output_cost
            
            return AIResponse(
                content=content,
                model=data.get('model', self.config.model_name),
                provider="chenmoai",
                usage=usage,
                finish_reason=finish_reason,
                response_time=response_time,
                cost=cost,
                metadata={
                    'created': data.get('created'),
                    'id': data.get('id'),
                    'proxy_provider': 'chenmoai'
                }
            )
            
        except (KeyError, IndexError) as e:
            raise ResponseParseException(
                f"ChenmoAI响应格式错误: {str(e)}",
                raw_response=json.dumps(data),
                provider="chenmoai"
            )
    
    async def _handle_error_response(self, status_code: int, error_text: str) -> AIServiceException:
        """处理错误响应"""
        try:
            error_data = json.loads(error_text)
            error_message = error_data.get('error', {}).get('message', error_text)
            error_code = error_data.get('error', {}).get('code', str(status_code))
        except json.JSONDecodeError:
            error_message = error_text
            error_code = str(status_code)
        
        if status_code == 401:
            return AuthenticationException(
                f"ChenmoAI API认证失败: {error_message}",
                error_code=error_code,
                provider="chenmoai"
            )
        elif status_code == 429:
            return RateLimitException(
                f"ChenmoAI API调用频率超限: {error_message}",
                error_code=error_code,
                provider="chenmoai"
            )
        elif status_code == 404:
            return ModelNotFoundException(
                self.config.model_name,
                error_code=error_code,
                provider="chenmoai"
            )
        elif status_code == 402:
            return QuotaExceededException(
                f"ChenmoAI API配额已用完: {error_message}",
                error_code=error_code,
                provider="chenmoai"
            )
        elif status_code >= 500:
            return ServiceUnavailableException(
                f"ChenmoAI服务不可用: {error_message}",
                error_code=error_code,
                provider="chenmoai"
            )
        else:
            return AIServiceException(
                f"ChenmoAI API错误: {error_message}",
                error_code=error_code,
                provider="chenmoai"
            )
    
    async def health_check(self) -> HealthCheckResult:
        """ChenmoAI健康检查"""
        start_time = time.time()
        
        try:
            # 发送简单的健康检查请求
            test_messages = [
                self.create_system_message("You are a helpful assistant."),
                self.create_user_message("Hello")
            ]
            
            request_data = {
                "model": self.config.model_name,
                "messages": self.format_messages(test_messages),
                "max_tokens": 10,
                "temperature": 0
            }
            
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10)
            ) as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=request_data
                ) as response:
                    
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        return HealthCheckResult(
                            is_healthy=True,
                            response_time=response_time,
                            model_available=True
                        )
                    else:
                        error_text = await response.text()
                        return HealthCheckResult(
                            is_healthy=False,
                            response_time=response_time,
                            error_message=f"HTTP {response.status}: {error_text}",
                            model_available=False
                        )
                        
        except Exception as e:
            return HealthCheckResult(
                is_healthy=False,
                response_time=time.time() - start_time,
                error_message=str(e),
                model_available=False
            )
    
    async def estimate_tokens(self, text: str) -> int:
        """Token估算（与OpenAI兼容）"""
        # 基于通用估算规则：1个token约等于4个字符（英文）或1.5个字符（中文）
        english_chars = sum(1 for c in text if ord(c) < 128)
        chinese_chars = len(text) - english_chars
        
        estimated_tokens = (english_chars // 4) + (chinese_chars // 1.5)
        return int(estimated_tokens) + 10  # 加上一些buffer
