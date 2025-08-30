# -*- coding: utf-8 -*-
"""
Google Gemini API适配器
支持Gemini系列模型和流式响应
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


class GoogleAdapter(BaseAIAdapter):
    """Google Gemini API适配器"""
    
    # 支持的模型列表
    SUPPORTED_MODELS = {
        'gemini-1.5-pro': {'context_window': 2097152, 'supports_streaming': True},
        'gemini-1.5-flash': {'context_window': 1048576, 'supports_streaming': True},
        'gemini-1.0-pro': {'context_window': 32768, 'supports_streaming': True},
        'gemini-2.0-flash-exp': {'context_window': 1048576, 'supports_streaming': True},
        'gemini-2.5-pro-exp-03-25': {'context_window': 2097152, 'supports_streaming': True},  # 最新实验版
    }
    
    def __init__(self, config: AIModelConfig):
        super().__init__(config)
        self.base_url = config.base_url or "https://generativelanguage.googleapis.com/v1beta"
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "Alpha-AI-Assistant/1.0"
        }
        # Google API使用查询参数传递API密钥
        self.api_key_param = f"key={config.api_key}"
    
    def validate_config(self) -> None:
        """验证Google配置"""
        if len(self.config.api_key) < 30:
            logger.warning("Google API密钥格式可能不正确")
        
        # 检查模型是否支持
        model_info = self.SUPPORTED_MODELS.get(self.config.model_name)
        if model_info:
            self.config.context_window = model_info['context_window']
            self.config.supports_streaming = model_info['supports_streaming']
    
    def format_messages(self, messages: List[AIMessage]) -> Dict[str, Any]:
        """格式化消息为Google API格式"""
        # Google Gemini API使用不同的消息格式
        formatted_contents = []
        
        for msg in messages:
            if msg.role.value == "system":
                # 系统消息转换为用户消息的前缀
                formatted_contents.append({
                    "role": "user",
                    "parts": [{"text": f"[System]: {msg.content}"}]
                })
            elif msg.role.value == "user":
                formatted_contents.append({
                    "role": "user",
                    "parts": [{"text": msg.content}]
                })
            elif msg.role.value == "assistant":
                formatted_contents.append({
                    "role": "model",  # Google使用"model"而不是"assistant"
                    "parts": [{"text": msg.content}]
                })
        
        return {"contents": formatted_contents}
    
    async def generate_response(
        self,
        messages: List[AIMessage],
        **kwargs
    ) -> AIResponse:
        """生成Google响应"""
        start_time = time.time()
        
        # 构建请求数据
        formatted_messages = self.format_messages(messages)
        request_data = {
            "generationConfig": {
                "maxOutputTokens": kwargs.get('max_tokens', self.config.max_tokens),
                "temperature": kwargs.get('temperature', self.config.temperature),
                "topP": kwargs.get('top_p', self.config.top_p),
            },
            **formatted_messages
        }
        
        # 使用重试机制
        return await self.retry_on_failure(self._make_request, request_data, start_time)
    
    async def stream_response(
        self,
        messages: List[AIMessage],
        **kwargs
    ) -> AsyncIterator[str]:
        """流式生成Google响应"""
        if not self.config.supports_streaming:
            response = await self.generate_response(messages, **kwargs)
            yield response.content
            return
        
        formatted_messages = self.format_messages(messages)
        request_data = {
            "generationConfig": {
                "maxOutputTokens": kwargs.get('max_tokens', self.config.max_tokens),
                "temperature": kwargs.get('temperature', self.config.temperature),
            },
            **formatted_messages
        }
        
        url = f"{self.base_url}/models/{self.config.model_name}:streamGenerateContent?{self.api_key_param}"
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
            async with session.post(url, headers=self.headers, json=request_data) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    raise await self._handle_error_response(response.status, error_text)
                
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    
                    if line.startswith('data: '):
                        data = line[6:]
                        
                        try:
                            chunk = json.loads(data)
                            
                            # Google Gemini流式响应格式
                            candidates = chunk.get('candidates', [])
                            if candidates:
                                content = candidates[0].get('content', {})
                                parts = content.get('parts', [])
                                for part in parts:
                                    text = part.get('text', '')
                                    if text:
                                        yield text
                                        
                        except json.JSONDecodeError:
                            continue
    
    async def _make_request(self, request_data: Dict[str, Any], start_time: float) -> AIResponse:
        """执行Google API请求"""
        url = f"{self.base_url}/models/{self.config.model_name}:generateContent?{self.api_key_param}"
        
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.timeout)
        ) as session:
            try:
                async with session.post(
                    url,
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
                    f"Google API请求超时（{self.config.timeout}秒）",
                    provider="google"
                )
            except aiohttp.ClientError as e:
                raise ServiceUnavailableException(
                    f"网络连接错误: {str(e)}",
                    provider="google"
                )
    
    def _parse_response(self, data: Dict[str, Any], response_time: float) -> AIResponse:
        """解析Google响应"""
        try:
            candidates = data.get('candidates', [])
            if not candidates:
                raise ResponseParseException(
                    "Google响应中没有候选内容",
                    raw_response=json.dumps(data),
                    provider="google"
                )
            
            candidate = candidates[0]
            content = candidate.get('content', {})
            parts = content.get('parts', [])
            
            # 合并所有text部分
            full_content = ""
            for part in parts:
                if part.get('text'):
                    full_content += part['text']
            
            # 提取使用量信息
            usage_metadata = data.get('usageMetadata', {})
            usage = {
                'prompt_tokens': usage_metadata.get('promptTokenCount', 0),
                'completion_tokens': usage_metadata.get('candidatesTokenCount', 0),
                'total_tokens': usage_metadata.get('totalTokenCount', 0)
            }
            
            finish_reason = candidate.get('finishReason', 'STOP')
            
            # 计算成本
            cost = 0.0
            if usage and self.config.cost_per_input_token > 0:
                input_cost = usage['prompt_tokens'] * self.config.cost_per_input_token
                output_cost = usage['completion_tokens'] * self.config.cost_per_output_token
                cost = input_cost + output_cost
            
            return AIResponse(
                content=full_content,
                model=self.config.model_name,
                provider="google",
                usage=usage,
                finish_reason=finish_reason,
                response_time=response_time,
                cost=cost,
                metadata={
                    'safety_ratings': candidate.get('safetyRatings', []),
                    'citation_metadata': candidate.get('citationMetadata', {}),
                    'model_version': data.get('modelVersion')
                }
            )
            
        except (KeyError, IndexError, TypeError) as e:
            raise ResponseParseException(
                f"Google响应格式错误: {str(e)}",
                raw_response=json.dumps(data),
                provider="google"
            )
    
    async def _handle_error_response(self, status_code: int, error_text: str) -> AIServiceException:
        """处理Google错误响应"""
        try:
            error_data = json.loads(error_text)
            error_message = error_data.get('error', {}).get('message', error_text)
            error_code = error_data.get('error', {}).get('code', str(status_code))
        except json.JSONDecodeError:
            error_message = error_text
            error_code = str(status_code)
        
        if status_code == 400:
            return InvalidRequestException(
                f"Google API请求无效: {error_message}",
                error_code=error_code,
                provider="google"
            )
        elif status_code == 401 or status_code == 403:
            return AuthenticationException(
                f"Google API认证失败: {error_message}",
                error_code=error_code,
                provider="google"
            )
        elif status_code == 429:
            return RateLimitException(
                f"Google API调用频率超限: {error_message}",
                error_code=error_code,
                provider="google"
            )
        elif status_code == 404:
            return ModelNotFoundException(
                self.config.model_name,
                error_code=error_code,
                provider="google"
            )
        elif status_code >= 500:
            return ServiceUnavailableException(
                f"Google服务不可用: {error_message}",
                error_code=error_code,
                provider="google"
            )
        else:
            return AIServiceException(
                f"Google API错误: {error_message}",
                error_code=error_code,
                provider="google"
            )
    
    async def health_check(self) -> HealthCheckResult:
        """Google健康检查"""
        start_time = time.time()
        
        try:
            test_messages = [
                self.create_user_message("Hello")
            ]
            
            formatted_messages = self.format_messages(test_messages)
            request_data = {
                "generationConfig": {
                    "maxOutputTokens": 10,
                    "temperature": 0
                },
                **formatted_messages
            }
            
            url = f"{self.base_url}/models/{self.config.model_name}:generateContent?{self.api_key_param}"
            
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10)
            ) as session:
                async with session.post(
                    url,
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
        """Google token估算"""
        # Gemini使用类似的估算规则
        # 英文约4个字符/token，中文约2个字符/token
        english_chars = sum(1 for c in text if ord(c) < 128)
        chinese_chars = len(text) - english_chars
        
        estimated_tokens = (english_chars // 4) + (chinese_chars // 2)
        return int(estimated_tokens) + 5  # 加上buffer
