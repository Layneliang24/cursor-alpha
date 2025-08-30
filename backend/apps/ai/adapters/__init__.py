# -*- coding: utf-8 -*-
"""
AI适配器模块
提供统一的AI服务接口和多种模型适配器
"""

from .base import BaseAIAdapter, AIModelConfig, AIResponse, AIMessage, MessageRole, AIProviderType
from .openai_adapter import OpenAIAdapter
from .claude_adapter import ClaudeAdapter
from .google_adapter import GoogleAdapter
from .factory import AIAdapterFactory, create_adapter_from_django_model
from .exceptions import (
    AIServiceException, RateLimitException, 
    AuthenticationException, ModelNotFoundException,
    QuotaExceededException, ServiceUnavailableException,
    InvalidRequestException, ResponseParseException
)

__all__ = [
    # 基础类
    'BaseAIAdapter',
    'AIModelConfig', 
    'AIResponse',
    'AIMessage',
    'MessageRole',
    'AIProviderType',
    
    # 适配器实现
    'OpenAIAdapter',
    'ClaudeAdapter',
    'GoogleAdapter',
    
    # 工厂和便利函数
    'AIAdapterFactory',
    'create_adapter_from_django_model',
    
    # 异常
    'AIServiceException',
    'RateLimitException',
    'AuthenticationException', 
    'ModelNotFoundException',
    'QuotaExceededException',
    'ServiceUnavailableException',
    'InvalidRequestException',
    'ResponseParseException'
]
