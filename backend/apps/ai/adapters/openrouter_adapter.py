# -*- coding: utf-8 -*-
"""
OpenRouter API适配器
通过OpenRouter访问多种AI模型的统一接口
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


class OpenRouterAdapter(BaseAIAdapter):
    """OpenRouter API适配器"""
    
    # 支持的模型列表（通过OpenRouter访问）
    SUPPORTED_MODELS = {
        # 免费模型
        'google/gemma-2-9b-it:free': {'context_window': 8192, 'supports_streaming': True},
        'microsoft/phi-3-mini-128k-instruct:free': {'context_window': 128000, 'supports_streaming': True},
        'huggingfaceh4/zephyr-7b-beta:free': {'context_window': 4096, 'supports_streaming': True},
        'openchat/openchat-7b:free': {'context_window': 8192, 'supports_streaming': True},
        
        # GPT系列
        'openai/gpt-4o': {'context_window': 128000, 'supports_streaming': True},
        'openai/gpt-4o-mini': {'context_window': 128000, 'supports_streaming': True},
        'openai/gpt-4-turbo': {'context_window': 128000, 'supports_streaming': True},
        'openai/gpt-3.5-turbo': {'context_window': 16385, 'supports_streaming': True},
        
        # Claude系列
        'anthropic/claude-3-5-sonnet': {'context_window': 200000, 'supports_streaming': True},
        'anthropic/claude-3-haiku': {'context_window': 200000, 'supports_streaming': True},
        'anthropic/claude-3-opus': {'context_window': 200000, 'supports_streaming': True},
        
        # 其他热门模型
        'meta-llama/llama-3.1-8b-instruct:free': {'context_window': 131072, 'supports_streaming': True},
        'qwen/qwen-2-7b-instruct:free': {'context_window': 32768, 'supports_streaming': True},
    }
    
    def __init__(self, api_key: str, model_name: str = 'google/gemma-2-9b-it:free', **kwargs):
        """初始化OpenRouter适配器
        
        Args:
            api_key: OpenRouter API密钥
            model_name: 模型名称，默认使用免费的Gemma模型
            **kwargs: 其他配置参数
        """
        self.api_key = api_key
        self.model_name = model_name
        self.base_url = kwargs.get('base_url', 'https://openrouter.ai/api/v1')
        self.timeout = kwargs.get('timeout', 30)
        self.max_retries = kwargs.get('max_retries', 3)
        
        # 验证模型是否支持
        if model_name not in self.SUPPORTED_MODELS:
            logger.warning(f"模型 {model_name} 不在预定义列表中，但仍会尝试使用")
        
        # 设置模型配置
        model_info = self.SUPPORTED_MODELS.get(model_name, {
            'context_window': 8192, 
            'supports_streaming': True
        })
        
        self.config = AIModelConfig(
            provider=AIProviderType.CUSTOM,
            model_name=model_name,
            api_key=api_key,
            base_url=self.base_url,
            max_tokens=kwargs.get('max_tokens', 2048),
            temperature=kwargs.get('temperature', 0.7),
            context_window=model_info['context_window'],
            supports_streaming=model_info['supports_streaming']
        )
        
        logger.info(f"初始化OpenRouter适配器: {model_name}")
    
    async def generate_response(self, messages: List[AIMessage], **kwargs) -> AIResponse:
        """生成AI响应"""
        try:
            # 准备请求数据
            request_data = {
                "model": self.model_name,
                "messages": [{"role": msg.role, "content": msg.content} for msg in messages],
                "max_tokens": kwargs.get('max_tokens', self.config.max_tokens),
                "temperature": kwargs.get('temperature', self.config.temperature),
                "stream": False
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://alpha-platform.local",  # OpenRouter要求
                "X-Title": "Alpha AI Assistant"  # OpenRouter要求
            }
            
            # 发送请求
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=request_data
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        if 'choices' in data and len(data['choices']) > 0:
                            choice = data['choices'][0]
                            content = choice.get('message', {}).get('content', '')
                            
                            # 统计使用量
                            usage = data.get('usage', {})
                            
                            return AIResponse(
                                content=content,
                                model=self.model_name,
                                provider=AIProviderType.CUSTOM.value,
                                usage={
                                    'prompt_tokens': usage.get('prompt_tokens', 0),
                                    'completion_tokens': usage.get('completion_tokens', 0),
                                    'total_tokens': usage.get('total_tokens', 0)
                                },
                                metadata={
                                    'finish_reason': choice.get('finish_reason'),
                                    'response_time': time.time()
                                }
                            )
                        else:
                            raise ResponseParseException("响应中没有找到有效的选择项")
                    
                    else:
                        error_text = await response.text()
                        await self._handle_error(response.status, error_text)
        
        except asyncio.TimeoutError:
            raise ServiceUnavailableException("请求超时")
        except aiohttp.ClientError as e:
            raise ServiceUnavailableException(f"网络错误: {str(e)}")
        except Exception as e:
            logger.error(f"OpenRouter请求失败: {str(e)}")
            raise AIServiceException(f"生成响应失败: {str(e)}")
    
    async def generate_stream(self, messages: List[AIMessage], **kwargs) -> AsyncIterator[str]:
        """生成流式响应"""
        try:
            # 准备请求数据
            request_data = {
                "model": self.model_name,
                "messages": [{"role": msg.role, "content": msg.content} for msg in messages],
                "max_tokens": kwargs.get('max_tokens', self.config.max_tokens),
                "temperature": kwargs.get('temperature', self.config.temperature),
                "stream": True
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://alpha-platform.local",
                "X-Title": "Alpha AI Assistant"
            }
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=request_data
                ) as response:
                    
                    if response.status == 200:
                        async for line in response.content:
                            line = line.decode('utf-8').strip()
                            
                            if line.startswith('data: '):
                                data_str = line[6:]  # 移除 'data: ' 前缀
                                
                                if data_str == '[DONE]':
                                    break
                                
                                try:
                                    data = json.loads(data_str)
                                    if 'choices' in data and len(data['choices']) > 0:
                                        delta = data['choices'][0].get('delta', {})
                                        content = delta.get('content', '')
                                        if content:
                                            yield content
                                except json.JSONDecodeError:
                                    continue
                    else:
                        error_text = await response.text()
                        await self._handle_error(response.status, error_text)
        
        except asyncio.TimeoutError:
            raise ServiceUnavailableException("流式请求超时")
        except aiohttp.ClientError as e:
            raise ServiceUnavailableException(f"网络错误: {str(e)}")
        except Exception as e:
            logger.error(f"OpenRouter流式请求失败: {str(e)}")
            raise AIServiceException(f"生成流式响应失败: {str(e)}")
    
    async def health_check(self) -> HealthCheckResult:
        """健康检查"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # 使用简单的模型列表请求进行健康检查
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(
                    f"{self.base_url}/models",
                    headers=headers
                ) as response:
                    
                    if response.status == 200:
                        return HealthCheckResult(
                            is_healthy=True,
                            response_time=0.1  # 估算值
                        )
                    else:
                        return HealthCheckResult(
                            is_healthy=False,
                            response_time=0.1
                        )
        
        except Exception as e:
            return HealthCheckResult(
                is_healthy=False,
                response_time=10.0
            )
    
    async def _handle_error(self, status_code: int, error_text: str):
        """处理API错误响应"""
        try:
            error_data = json.loads(error_text)
            error_message = error_data.get('error', {}).get('message', error_text)
        except (json.JSONDecodeError, KeyError):
            error_message = error_text
        
        if status_code == 401:
            raise AuthenticationException(f"认证失败: {error_message}")
        elif status_code == 402:
            raise QuotaExceededException(f"配额不足: {error_message}")
        elif status_code == 429:
            raise RateLimitException(f"请求频率限制: {error_message}")
        elif status_code == 404:
            raise ModelNotFoundException(f"模型不存在: {error_message}")
        elif status_code >= 500:
            raise ServiceUnavailableException(f"服务不可用: {error_message}")
        else:
            raise InvalidRequestException(f"请求无效 ({status_code}): {error_message}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        model_info = self.SUPPORTED_MODELS.get(self.model_name, {})
        return {
            "name": self.model_name,
            "provider": "OpenRouter",
            "context_window": model_info.get('context_window', 8192),
            "supports_streaming": model_info.get('supports_streaming', True),
            "is_free": ':free' in self.model_name,
            "description": f"通过OpenRouter访问的{self.model_name}模型"
        }
    
    async def stream_response(self, messages: List[AIMessage], **kwargs) -> AsyncIterator[str]:
        """流式响应（与generate_stream相同）"""
        async for chunk in self.generate_stream(messages, **kwargs):
            yield chunk
    
    def validate_config(self) -> bool:
        """验证配置是否有效"""
        try:
            # 检查必要的配置项
            if not self.api_key:
                logger.error("OpenRouter API密钥未设置")
                return False
            
            if not self.model_name:
                logger.error("模型名称未设置")
                return False
            
            if not self.base_url:
                logger.error("基础URL未设置")
                return False
            
            return True
        
        except Exception as e:
            logger.error(f"配置验证失败: {e}")
            return False
