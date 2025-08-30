# -*- coding: utf-8 -*-
"""
Anthropic Claude API适配器
支持Claude系列模型和流式响应
"""
import asyncio
import time
import json
import aiohttp
from typing import List, AsyncIterator, Dict, Any
import logging

from .base import BaseAIAdapter, AIModelConfig, AIMessage, AIResponse, HealthCheckResult
from .exceptions import (
    AIServiceException, RateLimitException, AuthenticationException,
    ModelNotFoundException, QuotaExceededException, ServiceUnavailableException,
    InvalidRequestException, ResponseParseException
)

logger = logging.getLogger(__name__)


class ClaudeAdapter(BaseAIAdapter):
    """Anthropic Claude API适配器"""
    
    # 支持的模型列表
    SUPPORTED_MODELS = {
        'claude-3-5-sonnet-20241022': {'context_window': 200000, 'supports_streaming': True},
        'claude-3-5-haiku-20241022': {'context_window': 200000, 'supports_streaming': True},
        'claude-3-opus-20240229': {'context_window': 200000, 'supports_streaming': True},
        'claude-3-sonnet-20240229': {'context_window': 200000, 'supports_streaming': True},
        'claude-3-haiku-20240307': {'context_window': 200000, 'supports_streaming': True},
        'claude-3-7-sonnet-20250219': {'context_window': 200000, 'supports_streaming': True},  # 最新Claude
    }
    
    def __init__(self, config: AIModelConfig):
        super().__init__(config)
        self.base_url = config.base_url or "https://api.anthropic.com/v1"
        self.headers = {
            "x-api-key": config.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
            "User-Agent": "Alpha-AI-Assistant/1.0"
        }
    
    def validate_config(self) -> None:
        """验证Claude配置"""
        if not self.config.api_key.startswith('sk-ant-'):
            logger.warning("Claude API密钥格式可能不正确")
        
        # 检查模型是否支持
        model_info = self.SUPPORTED_MODELS.get(self.config.model_name)
        if model_info:
            self.config.context_window = model_info['context_window']
            self.config.supports_streaming = model_info['supports_streaming']
    
    def format_messages(self, messages: List[AIMessage]) -> Dict[str, Any]:
        """格式化消息为Claude API格式"""
        # Claude API要求system消息单独传递
        system_message = ""
        conversation_messages = []
        
        for msg in messages:
            if msg.role.value == "system":
                system_message = msg.content
            else:
                conversation_messages.append({
                    "role": msg.role.value,
                    "content": msg.content
                })
        
        return {
            "system": system_message,
            "messages": conversation_messages
        }
    
    async def generate_response(
        self,
        messages: List[AIMessage],
        **kwargs
    ) -> AIResponse:
        """生成Claude响应"""
        start_time = time.time()
        
        # 构建请求数据
        formatted_messages = self.format_messages(messages)
        request_data = {
            "model": self.config.model_name,
            "max_tokens": kwargs.get('max_tokens', self.config.max_tokens),
            "temperature": kwargs.get('temperature', self.config.temperature),
            "top_p": kwargs.get('top_p', self.config.top_p),
            "stream": False,
            **formatted_messages
        }
        
        # 使用重试机制
        return await self.retry_on_failure(self._make_request, request_data, start_time)
    
    async def stream_response(
        self,
        messages: List[AIMessage],
        **kwargs
    ) -> AsyncIterator[str]:
        """流式生成Claude响应"""
        if not self.config.supports_streaming:
            response = await self.generate_response(messages, **kwargs)
            yield response.content
            return
        
        formatted_messages = self.format_messages(messages)
        request_data = {
            "model": self.config.model_name,
            "max_tokens": kwargs.get('max_tokens', self.config.max_tokens),
            "temperature": kwargs.get('temperature', self.config.temperature),
            "stream": True,
            **formatted_messages
        }
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
            async with session.post(
                f"{self.base_url}/messages",
                headers=self.headers,
                json=request_data
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    raise await self._handle_error_response(response.status, error_text)
                
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    
                    if line.startswith('data: '):
                        data = line[6:]
                        
                        if data == '[DONE]':
                            break
                        
                        try:
                            chunk = json.loads(data)
                            
                            if chunk.get('type') == 'content_block_delta':
                                delta = chunk.get('delta', {})
                                content = delta.get('text', '')
                                
                                if content:
                                    yield content
                                    
                        except json.JSONDecodeError:
                            continue
    
    async def _make_request(self, request_data: Dict[str, Any], start_time: float) -> AIResponse:
        """执行Claude API请求"""
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.timeout)
        ) as session:
            try:
                async with session.post(
                    f"{self.base_url}/messages",
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
                    f"Claude API请求超时（{self.config.timeout}秒）",
                    provider="anthropic"
                )
            except aiohttp.ClientError as e:
                raise ServiceUnavailableException(
                    f"网络连接错误: {str(e)}",
                    provider="anthropic"
                )
    
    def _parse_response(self, data: Dict[str, Any], response_time: float) -> AIResponse:
        """解析Claude响应"""
        try:
            content = ""
            
            # Claude API返回的内容在content数组中
            for content_block in data.get('content', []):
                if content_block.get('type') == 'text':
                    content += content_block.get('text', '')
            
            usage = data.get('usage', {})
            stop_reason = data.get('stop_reason')
            
            # 计算成本
            cost = 0.0
            if usage and self.config.cost_per_input_token > 0:
                input_cost = usage.get('input_tokens', 0) * self.config.cost_per_input_token
                output_cost = usage.get('output_tokens', 0) * self.config.cost_per_output_token
                cost = input_cost + output_cost
            
            return AIResponse(
                content=content,
                model=data.get('model', self.config.model_name),
                provider="anthropic",
                usage={
                    'prompt_tokens': usage.get('input_tokens', 0),
                    'completion_tokens': usage.get('output_tokens', 0),
                    'total_tokens': usage.get('input_tokens', 0) + usage.get('output_tokens', 0)
                },
                finish_reason=stop_reason,
                response_time=response_time,
                cost=cost,
                metadata={
                    'id': data.get('id'),
                    'type': data.get('type'),
                    'role': data.get('role')
                }
            )
            
        except (KeyError, TypeError) as e:
            raise ResponseParseException(
                f"Claude响应格式错误: {str(e)}",
                raw_response=json.dumps(data),
                provider="anthropic"
            )
    
    async def _handle_error_response(self, status_code: int, error_text: str) -> AIServiceException:
        """处理Claude错误响应"""
        try:
            error_data = json.loads(error_text)
            error_message = error_data.get('error', {}).get('message', error_text)
            error_type = error_data.get('error', {}).get('type', str(status_code))
        except json.JSONDecodeError:
            error_message = error_text
            error_type = str(status_code)
        
        if status_code == 401:
            return AuthenticationException(
                f"Claude API认证失败: {error_message}",
                error_code=error_type,
                provider="anthropic"
            )
        elif status_code == 429:
            return RateLimitException(
                f"Claude API调用频率超限: {error_message}",
                error_code=error_type,
                provider="anthropic"
            )
        elif status_code == 404:
            return ModelNotFoundException(
                self.config.model_name,
                error_code=error_type,
                provider="anthropic"
            )
        elif status_code == 402:
            return QuotaExceededException(
                f"Claude API配额已用完: {error_message}",
                error_code=error_type,
                provider="anthropic"
            )
        elif status_code >= 500:
            return ServiceUnavailableException(
                f"Claude服务不可用: {error_message}",
                error_code=error_type,
                provider="anthropic"
            )
        else:
            return AIServiceException(
                f"Claude API错误: {error_message}",
                error_code=error_type,
                provider="anthropic"
            )
    
    async def health_check(self) -> HealthCheckResult:
        """Claude健康检查"""
        start_time = time.time()
        
        try:
            test_messages = [
                self.create_user_message("Hello")
            ]
            
            formatted_messages = self.format_messages(test_messages)
            request_data = {
                "model": self.config.model_name,
                "max_tokens": 10,
                "temperature": 0,
                **formatted_messages
            }
            
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10)
            ) as session:
                async with session.post(
                    f"{self.base_url}/messages",
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
