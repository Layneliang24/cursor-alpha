# -*- coding: utf-8 -*-
"""
AI适配器工厂
根据配置自动创建合适的适配器实例
"""
from typing import Dict, List, Type, Optional
import logging

from .base import BaseAIAdapter, AIModelConfig, AIProviderType
from .openai_adapter import OpenAIAdapter
from .claude_adapter import ClaudeAdapter
from .google_adapter import GoogleAdapter
from .chenmoai_adapter import ChenmoAIAdapter
from .openrouter_adapter import OpenRouterAdapter
from .exceptions import ModelNotFoundException, AIServiceException

logger = logging.getLogger(__name__)


class AIAdapterFactory:
    """AI适配器工厂类"""
    
    # 注册的适配器类型
    _adapters: Dict[AIProviderType, Type[BaseAIAdapter]] = {
        AIProviderType.OPENAI: OpenAIAdapter,
        AIProviderType.ANTHROPIC: ClaudeAdapter,
        AIProviderType.GOOGLE: GoogleAdapter,
        AIProviderType.CHENMOAI: ChenmoAIAdapter,
        AIProviderType.OPENROUTER: OpenRouterAdapter,
    }
    
    # 模型到提供商的映射
    _model_provider_mapping = {
        # OpenAI模型
        'gpt-3.5-turbo': AIProviderType.OPENAI,
        'gpt-4': AIProviderType.OPENAI,
        'gpt-4-turbo': AIProviderType.OPENAI,
        'gpt-4o': AIProviderType.OPENAI,
        'gpt-4o-mini': AIProviderType.OPENAI,
        'gpt-5': AIProviderType.OPENAI,
        
        # Claude模型
        'claude-3-opus-20240229': AIProviderType.ANTHROPIC,
        'claude-3-sonnet-20240229': AIProviderType.ANTHROPIC,
        'claude-3-haiku-20240307': AIProviderType.ANTHROPIC,
        'claude-3-5-sonnet-20241022': AIProviderType.ANTHROPIC,
        'claude-3-5-haiku-20241022': AIProviderType.ANTHROPIC,
        'claude-3-7-sonnet-20250219': AIProviderType.ANTHROPIC,
        
        # Google模型
        'gemini-1.0-pro': AIProviderType.GOOGLE,
        'gemini-1.5-pro': AIProviderType.GOOGLE,
        'gemini-1.5-flash': AIProviderType.GOOGLE,
        'gemini-2.0-flash-exp': AIProviderType.GOOGLE,
        'gemini-2.5-pro-exp-03-25': AIProviderType.GOOGLE,
        
        # ChenmoAI模型（支持多种模型通过中转访问）
        'chenmoai-gpt-4': AIProviderType.CHENMOAI,
        'chenmoai-gpt-3.5-turbo': AIProviderType.CHENMOAI,
        'chenmoai-claude-3-sonnet': AIProviderType.CHENMOAI,
        'chenmoai-claude-3-haiku': AIProviderType.CHENMOAI,
        'chenmoai-gemini-pro': AIProviderType.CHENMOAI,
        
        # OpenRouter模型（免费和付费模型）
        'google/gemma-2-9b-it:free': AIProviderType.OPENROUTER,
        'microsoft/phi-3-mini-128k-instruct:free': AIProviderType.OPENROUTER,
        'huggingfaceh4/zephyr-7b-beta:free': AIProviderType.OPENROUTER,
        'openchat/openchat-7b:free': AIProviderType.OPENROUTER,
        'openai/gpt-4o': AIProviderType.OPENROUTER,
        'openai/gpt-4o-mini': AIProviderType.OPENROUTER,
        'anthropic/claude-3-5-sonnet': AIProviderType.OPENROUTER,
        'anthropic/claude-3-haiku': AIProviderType.OPENROUTER,
    }
    
    @classmethod
    def create_adapter(cls, config: AIModelConfig) -> BaseAIAdapter:
        """
        根据配置创建适配器实例
        
        Args:
            config: AI模型配置
            
        Returns:
            对应的适配器实例
            
        Raises:
            ModelNotFoundException: 不支持的模型或提供商
            AIServiceException: 适配器创建失败
        """
        try:
            # 获取适配器类
            adapter_class = cls._get_adapter_class(config)
            
            # 创建适配器实例
            adapter = adapter_class(config)
            
            logger.info(f"成功创建AI适配器: {adapter}")
            return adapter
            
        except Exception as e:
            logger.error(f"创建AI适配器失败: {e}")
            # 安全地获取提供商名称
            provider_name = config.provider.value if config.provider and hasattr(config.provider, 'value') else str(config.provider)
            raise AIServiceException(
                f"无法创建AI适配器: {str(e)}",
                provider=provider_name
            )
    
    @classmethod
    def _get_adapter_class(cls, config: AIModelConfig) -> Type[BaseAIAdapter]:
        """获取适配器类"""
        provider = config.provider
        
        # 如果没有指定提供商，尝试从模型名称推断
        if provider == AIProviderType.CUSTOM:
            inferred_provider = cls._infer_provider_from_model(config.model_name)
            if inferred_provider:
                provider = inferred_provider
                logger.info(f"从模型名称 {config.model_name} 推断提供商: {provider.value}")
        
        adapter_class = cls._adapters.get(provider)
        if not adapter_class:
            # 安全地获取提供商名称
            provider_name = provider.value if provider and hasattr(provider, 'value') else str(provider)
            raise ModelNotFoundException(
                f"不支持的AI提供商: {provider_name}",
                provider=provider_name
            )
        
        return adapter_class
    
    @classmethod
    def _infer_provider_from_model(cls, model_name: str) -> Optional[AIProviderType]:
        """从模型名称推断提供商"""
        return cls._model_provider_mapping.get(model_name)
    
    @classmethod
    def register_adapter(
        cls, 
        provider: AIProviderType, 
        adapter_class: Type[BaseAIAdapter]
    ) -> None:
        """
        注册新的适配器类
        
        Args:
            provider: AI提供商类型
            adapter_class: 适配器类
        """
        if not issubclass(adapter_class, BaseAIAdapter):
            raise ValueError(f"适配器类必须继承自BaseAIAdapter")
        
        cls._adapters[provider] = adapter_class
        logger.info(f"注册AI适配器: {provider.value} -> {adapter_class.__name__}")
    
    @classmethod
    def register_model_mapping(cls, model_name: str, provider: AIProviderType) -> None:
        """
        注册模型到提供商的映射
        
        Args:
            model_name: 模型名称
            provider: 提供商类型
        """
        cls._model_provider_mapping[model_name] = provider
        logger.info(f"注册模型映射: {model_name} -> {provider.value}")
    
    @classmethod
    def get_supported_models(cls) -> Dict[AIProviderType, List[str]]:
        """获取所有支持的模型列表"""
        supported = {}
        
        for provider, adapter_class in cls._adapters.items():
            if hasattr(adapter_class, 'SUPPORTED_MODELS'):
                supported[provider] = list(adapter_class.SUPPORTED_MODELS.keys())
        
        return supported
    
    @classmethod
    def get_supported_providers(cls) -> List[AIProviderType]:
        """获取所有支持的提供商"""
        return list(cls._adapters.keys())
    
    @classmethod
    def is_model_supported(cls, model_name: str, provider: AIProviderType = None) -> bool:
        """
        检查模型是否支持
        
        Args:
            model_name: 模型名称
            provider: 可选的提供商类型
            
        Returns:
            是否支持该模型
        """
        if provider:
            adapter_class = cls._adapters.get(provider)
            if adapter_class and hasattr(adapter_class, 'SUPPORTED_MODELS'):
                return model_name in adapter_class.SUPPORTED_MODELS
        else:
            # 在所有提供商中查找
            for adapter_class in cls._adapters.values():
                if hasattr(adapter_class, 'SUPPORTED_MODELS'):
                    if model_name in adapter_class.SUPPORTED_MODELS:
                        return True
        
        return False
    
    @classmethod
    def get_model_info(cls, model_name: str, provider: AIProviderType = None) -> Optional[Dict]:
        """
        获取模型信息
        
        Args:
            model_name: 模型名称
            provider: 可选的提供商类型
            
        Returns:
            模型信息字典或None
        """
        if provider:
            adapter_class = cls._adapters.get(provider)
            if adapter_class and hasattr(adapter_class, 'SUPPORTED_MODELS'):
                return adapter_class.SUPPORTED_MODELS.get(model_name)
        else:
            # 在所有提供商中查找
            for prov, adapter_class in cls._adapters.items():
                if hasattr(adapter_class, 'SUPPORTED_MODELS'):
                    model_info = adapter_class.SUPPORTED_MODELS.get(model_name)
                    if model_info:
                        return {**model_info, 'provider': prov}
        
        return None


# 便利函数
def create_adapter_from_django_model(ai_config_model) -> BaseAIAdapter:
    """
    从Django模型创建适配器
    
    Args:
        ai_config_model: AIAssistantConfig Django模型实例
        
    Returns:
        适配器实例
    """
    from apps.english.models import AIAssistantConfig
    
    if not isinstance(ai_config_model, AIAssistantConfig):
        raise ValueError("必须传入AIAssistantConfig模型实例")
    
    # 将Django模型转换为适配器配置
    provider_mapping = {
        'openai': AIProviderType.OPENAI,
        'anthropic': AIProviderType.ANTHROPIC,
        'google': AIProviderType.GOOGLE,
        'azure': AIProviderType.AZURE,
        'local': AIProviderType.LOCAL,
        'custom': AIProviderType.CUSTOM,
    }
    
    provider = provider_mapping.get(
        ai_config_model.ai_provider, 
        AIProviderType.CUSTOM
    )
    
    config = AIModelConfig(
        provider=provider,
        model_name=ai_config_model.model_name,
        api_key=ai_config_model.api_key,
        base_url=ai_config_model.api_base_url,
        max_tokens=ai_config_model.max_tokens,
        temperature=ai_config_model.temperature,
        timeout=ai_config_model.timeout,
        max_retries=ai_config_model.max_retries,
        cost_per_input_token=float(ai_config_model.cost_per_input_token or 0),
        cost_per_output_token=float(ai_config_model.cost_per_output_token or 0),
        daily_quota_limit=ai_config_model.daily_quota_limit
    )
    
    return AIAdapterFactory.create_adapter(config)
