"""
AI模型发现服务

提供从各AI提供商获取可用模型列表的功能
支持缓存机制和手动刷新
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

import aiohttp
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone

from ..adapters.factory import AIAdapterFactory
from ..adapters.base import AIProviderType, AIModelConfig
from ..config_models import AIProvider, APIKey, AIModel

logger = logging.getLogger(__name__)


@dataclass
class ModelInfo:
    """模型信息数据结构"""
    id: str
    name: str
    display_name: str
    provider: str
    provider_type: str
    description: str = ""
    max_tokens: int = 4096
    supports_streaming: bool = True
    supports_functions: bool = False
    supports_vision: bool = False
    cost_per_1k_input: float = 0.0
    cost_per_1k_output: float = 0.0
    is_recommended: bool = False
    context_window: int = 4096
    release_date: Optional[str] = None
    capabilities: List[str] = None
    
    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = []


class ModelDiscoveryService:
    """模型发现服务"""
    
    # 缓存配置
    CACHE_KEY_PREFIX = "ai_models_discovery"
    CACHE_TIMEOUT = 3600  # 1小时
    PROVIDER_CACHE_TIMEOUT = 1800  # 30分钟
    
    # 各提供商的模型获取端点
    PROVIDER_ENDPOINTS = {
        AIProviderType.OPENAI: "https://api.openai.com/v1/models",
        AIProviderType.ANTHROPIC: None,  # Claude没有公开的模型列表API
        AIProviderType.GOOGLE: None,  # Gemini需要特殊处理
        AIProviderType.OPENROUTER: "https://openrouter.ai/api/v1/models",
        AIProviderType.CHENMOAI: None,  # 中转服务，使用预定义列表
    }
    
    # 预定义模型信息（用于没有API的提供商）
    PREDEFINED_MODELS = {
        AIProviderType.ANTHROPIC: [
            ModelInfo(
                id="claude-3-5-sonnet-20241022",
                name="claude-3-5-sonnet-20241022",
                display_name="Claude 3.5 Sonnet",
                provider="Anthropic",
                provider_type="anthropic",
                description="最新的Claude 3.5 Sonnet模型，在编程、写作和分析方面表现卓越",
                max_tokens=8192,
                context_window=200000,
                supports_streaming=True,
                supports_functions=True,
                supports_vision=True,
                cost_per_1k_input=3.0,
                cost_per_1k_output=15.0,
                is_recommended=True,
                capabilities=["text", "vision", "function_calling", "analysis"]
            ),
            ModelInfo(
                id="claude-3-5-haiku-20241022",
                name="claude-3-5-haiku-20241022",
                display_name="Claude 3.5 Haiku",
                provider="Anthropic",
                provider_type="anthropic",
                description="快速且经济的Claude 3.5 Haiku模型，适合日常任务",
                max_tokens=8192,
                context_window=200000,
                supports_streaming=True,
                supports_functions=True,
                supports_vision=True,
                cost_per_1k_input=1.0,
                cost_per_1k_output=5.0,
                is_recommended=True,
                capabilities=["text", "vision", "function_calling"]
            ),
            ModelInfo(
                id="claude-3-opus-20240229",
                name="claude-3-opus-20240229",
                display_name="Claude 3 Opus",
                provider="Anthropic",
                provider_type="anthropic",
                description="Claude 3系列中最强大的模型，适合复杂任务",
                max_tokens=4096,
                context_window=200000,
                supports_streaming=True,
                supports_functions=False,
                supports_vision=True,
                cost_per_1k_input=15.0,
                cost_per_1k_output=75.0,
                capabilities=["text", "vision", "analysis"]
            ),
        ],
        
        AIProviderType.GOOGLE: [
            ModelInfo(
                id="gemini-2.0-flash-exp",
                name="gemini-2.0-flash-exp",
                display_name="Gemini 2.0 Flash (Experimental)",
                provider="Google",
                provider_type="google",
                description="Google最新的Gemini 2.0 Flash实验版本",
                max_tokens=8192,
                context_window=1000000,
                supports_streaming=True,
                supports_functions=True,
                supports_vision=True,
                cost_per_1k_input=0.075,
                cost_per_1k_output=0.30,
                is_recommended=True,
                capabilities=["text", "vision", "function_calling", "multimodal"]
            ),
            ModelInfo(
                id="gemini-1.5-pro",
                name="gemini-1.5-pro",
                display_name="Gemini 1.5 Pro",
                provider="Google",
                provider_type="google",
                description="Google Gemini 1.5 Pro模型，支持超长上下文",
                max_tokens=8192,
                context_window=2000000,
                supports_streaming=True,
                supports_functions=True,
                supports_vision=True,
                cost_per_1k_input=1.25,
                cost_per_1k_output=5.0,
                is_recommended=True,
                capabilities=["text", "vision", "function_calling", "long_context"]
            ),
            ModelInfo(
                id="gemini-1.5-flash",
                name="gemini-1.5-flash",
                display_name="Gemini 1.5 Flash",
                provider="Google",
                provider_type="google",
                description="快速且经济的Gemini 1.5 Flash模型",
                max_tokens=8192,
                context_window=1000000,
                supports_streaming=True,
                supports_functions=True,
                supports_vision=True,
                cost_per_1k_input=0.075,
                cost_per_1k_output=0.30,
                is_recommended=True,
                capabilities=["text", "vision", "function_calling"]
            ),
        ],
        
        AIProviderType.CHENMOAI: [
            ModelInfo(
                id="gpt-4o",
                name="gpt-4o",
                display_name="GPT-4o (ChenmoAI)",
                provider="ChenmoAI",
                provider_type="chenmoai",
                description="通过ChenmoAI中转的GPT-4o模型",
                max_tokens=4096,
                context_window=128000,
                supports_streaming=True,
                supports_functions=True,
                supports_vision=True,
                cost_per_1k_input=2.5,
                cost_per_1k_output=10.0,
                capabilities=["text", "vision", "function_calling"]
            ),
            ModelInfo(
                id="claude-3-5-sonnet-20241022",
                name="claude-3-5-sonnet-20241022",
                display_name="Claude 3.5 Sonnet (ChenmoAI)",
                provider="ChenmoAI",
                provider_type="chenmoai",
                description="通过ChenmoAI中转的Claude 3.5 Sonnet模型",
                max_tokens=8192,
                context_window=200000,
                supports_streaming=True,
                supports_functions=True,
                supports_vision=True,
                cost_per_1k_input=3.0,
                cost_per_1k_output=15.0,
                capabilities=["text", "vision", "function_calling"]
            ),
        ],
    }
    
    def __init__(self):
        self.session = None
    
    async def get_all_models(self, force_refresh: bool = False) -> Dict[str, List[ModelInfo]]:
        """
        获取所有提供商的模型列表
        
        Args:
            force_refresh: 是否强制刷新缓存
            
        Returns:
            按提供商分组的模型列表
        """
        cache_key = f"{self.CACHE_KEY_PREFIX}:all_models"
        
        if not force_refresh:
            cached_data = cache.get(cache_key)
            if cached_data:
                logger.info("从缓存获取模型列表")
                return self._deserialize_models(cached_data)
        
        logger.info("开始获取所有提供商的模型列表")
        all_models = {}
        
        # 获取活跃的提供商
        active_providers = AIProvider.objects.filter(is_active=True)
        
        for provider in active_providers:
            try:
                provider_type = AIProviderType(provider.provider_type)
                models = await self.get_provider_models(provider_type, provider, force_refresh)
                all_models[provider.provider_type] = models
                logger.info(f"获取到 {provider.display_name} 的 {len(models)} 个模型")
            except Exception as e:
                logger.error(f"获取提供商 {provider.display_name} 模型失败: {e}")
                all_models[provider.provider_type] = []
        
        # 缓存结果
        serializable_data = self._serialize_models(all_models)
        cache.set(cache_key, serializable_data, self.CACHE_TIMEOUT)
        
        logger.info(f"模型发现完成，共获取 {sum(len(models) for models in all_models.values())} 个模型")
        return all_models
    
    async def get_provider_models(
        self, 
        provider_type: AIProviderType, 
        provider: AIProvider,
        force_refresh: bool = False
    ) -> List[ModelInfo]:
        """
        获取特定提供商的模型列表
        
        Args:
            provider_type: 提供商类型
            provider: 提供商实例
            force_refresh: 是否强制刷新
            
        Returns:
            模型信息列表
        """
        cache_key = f"{self.CACHE_KEY_PREFIX}:provider:{provider_type.value}"
        
        if not force_refresh:
            cached_models = cache.get(cache_key)
            if cached_models:
                return [ModelInfo(**model_data) for model_data in cached_models]
        
        models = []
        
        try:
            if provider_type in self.PROVIDER_ENDPOINTS and self.PROVIDER_ENDPOINTS[provider_type]:
                # 通过API获取模型列表
                models = await self._fetch_models_from_api(provider_type, provider)
            else:
                # 使用预定义模型列表
                models = self.PREDEFINED_MODELS.get(provider_type, [])
            
            # 缓存结果
            serializable_models = [asdict(model) for model in models]
            cache.set(cache_key, serializable_models, self.PROVIDER_CACHE_TIMEOUT)
            
        except Exception as e:
            logger.error(f"获取 {provider_type.value} 模型列表失败: {e}")
            # 返回预定义模型作为备选
            models = self.PREDEFINED_MODELS.get(provider_type, [])
        
        return models
    
    async def _fetch_models_from_api(
        self, 
        provider_type: AIProviderType, 
        provider: AIProvider
    ) -> List[ModelInfo]:
        """从API获取模型列表"""
        endpoint = self.PROVIDER_ENDPOINTS[provider_type]
        if not endpoint:
            return []
        
        # 获取API密钥
        api_key = await self._get_provider_api_key(provider)
        if not api_key:
            logger.warning(f"未找到 {provider.display_name} 的有效API密钥")
            return self.PREDEFINED_MODELS.get(provider_type, [])
        
        headers = self._build_headers(provider_type, api_key)
        
        try:
            if not self.session:
                self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))
            
            async with self.session.get(endpoint, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_api_response(provider_type, provider, data)
                else:
                    logger.error(f"API请求失败: {response.status} - {await response.text()}")
                    return self.PREDEFINED_MODELS.get(provider_type, [])
                    
        except Exception as e:
            logger.error(f"API请求异常: {e}")
            return self.PREDEFINED_MODELS.get(provider_type, [])
    
    def _build_headers(self, provider_type: AIProviderType, api_key: str) -> Dict[str, str]:
        """构建API请求头"""
        if provider_type == AIProviderType.OPENAI:
            return {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
        elif provider_type == AIProviderType.OPENROUTER:
            return {
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": "https://alpha-ai-assistant.com",
                "X-Title": "Alpha AI Assistant"
            }
        else:
            return {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
    
    def _parse_api_response(
        self, 
        provider_type: AIProviderType, 
        provider: AIProvider, 
        data: Dict[str, Any]
    ) -> List[ModelInfo]:
        """解析API响应"""
        models = []
        
        if provider_type == AIProviderType.OPENAI:
            models = self._parse_openai_response(provider, data)
        elif provider_type == AIProviderType.OPENROUTER:
            models = self._parse_openrouter_response(provider, data)
        
        return models
    
    def _parse_openai_response(self, provider: AIProvider, data: Dict[str, Any]) -> List[ModelInfo]:
        """解析OpenAI API响应"""
        models = []
        
        for model_data in data.get('data', []):
            model_id = model_data.get('id', '')
            
            # 只处理GPT模型
            if not model_id.startswith(('gpt-', 'o1-')):
                continue
            
            # 获取模型详细信息
            model_info = self._get_openai_model_details(model_id)
            
            models.append(ModelInfo(
                id=model_id,
                name=model_id,
                display_name=model_info.get('display_name', model_id),
                provider=provider.display_name,
                provider_type=provider.provider_type,
                description=model_info.get('description', f"OpenAI {model_id} 模型"),
                max_tokens=model_info.get('max_tokens', 4096),
                context_window=model_info.get('context_window', 4096),
                supports_streaming=model_info.get('supports_streaming', True),
                supports_functions=model_info.get('supports_functions', True),
                supports_vision=model_info.get('supports_vision', False),
                cost_per_1k_input=model_info.get('cost_per_1k_input', 0.0),
                cost_per_1k_output=model_info.get('cost_per_1k_output', 0.0),
                is_recommended=model_info.get('is_recommended', False),
                capabilities=model_info.get('capabilities', ['text'])
            ))
        
        return models
    
    def _parse_openrouter_response(self, provider: AIProvider, data: Dict[str, Any]) -> List[ModelInfo]:
        """解析OpenRouter API响应"""
        models = []
        
        for model_data in data.get('data', []):
            model_id = model_data.get('id', '')
            pricing = model_data.get('pricing', {})
            
            models.append(ModelInfo(
                id=model_id,
                name=model_id,
                display_name=model_data.get('name', model_id),
                provider=provider.display_name,
                provider_type=provider.provider_type,
                description=model_data.get('description', ''),
                max_tokens=model_data.get('top_provider', {}).get('max_completion_tokens', 4096),
                context_window=model_data.get('context_length', 4096),
                supports_streaming=True,  # OpenRouter大多数模型支持流式
                supports_functions=model_data.get('architecture', {}).get('instruct_type') == 'function',
                supports_vision='vision' in model_data.get('architecture', {}).get('modality', ''),
                cost_per_1k_input=float(pricing.get('prompt', '0')) * 1000,
                cost_per_1k_output=float(pricing.get('completion', '0')) * 1000,
                is_recommended=model_id.endswith(':free'),  # 免费模型标记为推荐
                capabilities=self._extract_capabilities(model_data)
            ))
        
        return models
    
    def _get_openai_model_details(self, model_id: str) -> Dict[str, Any]:
        """获取OpenAI模型详细信息"""
        model_details = {
            'gpt-4o': {
                'display_name': 'GPT-4o',
                'description': 'OpenAI最新的GPT-4o模型，支持文本和视觉',
                'max_tokens': 4096,
                'context_window': 128000,
                'supports_vision': True,
                'supports_functions': True,
                'cost_per_1k_input': 2.5,
                'cost_per_1k_output': 10.0,
                'is_recommended': True,
                'capabilities': ['text', 'vision', 'function_calling']
            },
            'gpt-4o-mini': {
                'display_name': 'GPT-4o Mini',
                'description': '经济实惠的GPT-4o精简版',
                'max_tokens': 16384,
                'context_window': 128000,
                'supports_vision': True,
                'supports_functions': True,
                'cost_per_1k_input': 0.15,
                'cost_per_1k_output': 0.6,
                'is_recommended': True,
                'capabilities': ['text', 'vision', 'function_calling']
            },
            'gpt-4-turbo': {
                'display_name': 'GPT-4 Turbo',
                'description': 'GPT-4 Turbo模型，支持更大上下文窗口',
                'max_tokens': 4096,
                'context_window': 128000,
                'supports_vision': True,
                'supports_functions': True,
                'cost_per_1k_input': 10.0,
                'cost_per_1k_output': 30.0,
                'capabilities': ['text', 'vision', 'function_calling']
            },
            'gpt-3.5-turbo': {
                'display_name': 'GPT-3.5 Turbo',
                'description': '经典的GPT-3.5 Turbo模型',
                'max_tokens': 4096,
                'context_window': 16385,
                'supports_vision': False,
                'supports_functions': True,
                'cost_per_1k_input': 0.5,
                'cost_per_1k_output': 1.5,
                'capabilities': ['text', 'function_calling']
            },
        }
        
        return model_details.get(model_id, {
            'display_name': model_id,
            'description': f'OpenAI {model_id} 模型',
            'max_tokens': 4096,
            'context_window': 4096,
            'supports_vision': False,
            'supports_functions': False,
            'cost_per_1k_input': 0.0,
            'cost_per_1k_output': 0.0,
            'capabilities': ['text']
        })
    
    def _extract_capabilities(self, model_data: Dict[str, Any]) -> List[str]:
        """从模型数据中提取功能列表"""
        capabilities = ['text']  # 所有模型都支持文本
        
        architecture = model_data.get('architecture', {})
        modality = architecture.get('modality', '')
        
        if 'vision' in modality:
            capabilities.append('vision')
        if 'audio' in modality:
            capabilities.append('audio')
        if architecture.get('instruct_type') == 'function':
            capabilities.append('function_calling')
        
        return capabilities
    
    async def _get_provider_api_key(self, provider: AIProvider) -> Optional[str]:
        """获取提供商的API密钥"""
        try:
            api_key = APIKey.objects.filter(
                provider=provider,
                is_active=True,
                is_default=True
            ).first()
            
            if api_key and not api_key.is_expired():
                return api_key.get_key()
        except Exception as e:
            logger.error(f"获取API密钥失败: {e}")
        
        return None
    
    def _serialize_models(self, models_dict: Dict[str, List[ModelInfo]]) -> Dict[str, List[Dict]]:
        """序列化模型数据用于缓存"""
        serialized = {}
        for provider_type, models in models_dict.items():
            serialized[provider_type] = [asdict(model) for model in models]
        return serialized
    
    def _deserialize_models(self, serialized_data: Dict[str, List[Dict]]) -> Dict[str, List[ModelInfo]]:
        """反序列化缓存的模型数据"""
        deserialized = {}
        for provider_type, models_data in serialized_data.items():
            deserialized[provider_type] = [ModelInfo(**model_data) for model_data in models_data]
        return deserialized
    
    async def sync_models_to_database(self, force_refresh: bool = False) -> Dict[str, int]:
        """
        同步模型到数据库
        
        Args:
            force_refresh: 是否强制刷新
            
        Returns:
            同步统计信息
        """
        logger.info("开始同步模型到数据库")
        
        # 获取所有模型
        all_models = await self.get_all_models(force_refresh)
        
        stats = {
            'created': 0,
            'updated': 0,
            'skipped': 0,
            'errors': 0
        }
        
        for provider_type, models in all_models.items():
            try:
                provider = AIProvider.objects.filter(
                    provider_type=provider_type,
                    is_active=True
                ).first()
                
                if not provider:
                    logger.warning(f"未找到活跃的提供商: {provider_type}")
                    continue
                
                for model_info in models:
                    try:
                        model, created = AIModel.objects.update_or_create(
                            provider=provider,
                            model_id=model_info.id,
                            defaults={
                                'display_name': model_info.display_name,
                                'description': model_info.description,
                                'max_tokens': model_info.max_tokens,
                                'supports_streaming': model_info.supports_streaming,
                                'supports_functions': model_info.supports_functions,
                                'supports_vision': model_info.supports_vision,
                                'cost_per_1k_input_tokens': model_info.cost_per_1k_input,
                                'cost_per_1k_output_tokens': model_info.cost_per_1k_output,
                                'is_recommended': model_info.is_recommended,
                            }
                        )
                        
                        if created:
                            stats['created'] += 1
                            logger.debug(f"创建模型: {model_info.display_name}")
                        else:
                            stats['updated'] += 1
                            logger.debug(f"更新模型: {model_info.display_name}")
                            
                    except Exception as e:
                        logger.error(f"同步模型 {model_info.id} 失败: {e}")
                        stats['errors'] += 1
                        
            except Exception as e:
                logger.error(f"处理提供商 {provider_type} 模型失败: {e}")
                stats['errors'] += 1
        
        logger.info(f"模型同步完成: 创建 {stats['created']}, 更新 {stats['updated']}, 错误 {stats['errors']}")
        return stats
    
    async def clear_cache(self, provider_type: Optional[str] = None):
        """清除缓存"""
        if provider_type:
            cache_key = f"{self.CACHE_KEY_PREFIX}:provider:{provider_type}"
            cache.delete(cache_key)
            logger.info(f"清除提供商 {provider_type} 的缓存")
        else:
            # 清除所有相关缓存
            cache_keys = [
                f"{self.CACHE_KEY_PREFIX}:all_models",
            ]
            
            # 清除所有提供商缓存
            for provider_type in AIProviderType:
                cache_keys.append(f"{self.CACHE_KEY_PREFIX}:provider:{provider_type.value}")
            
            cache.delete_many(cache_keys)
            logger.info("清除所有模型发现缓存")
    
    async def close(self):
        """关闭HTTP会话"""
        if self.session:
            await self.session.close()
            self.session = None


# 全局实例
model_discovery_service = ModelDiscoveryService()

