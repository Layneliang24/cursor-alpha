"""
同步版本的模型发现服务
用于Django管理命令和其他同步上下文
"""

import logging
from typing import Dict, List
from django.core.cache import cache

from .model_discovery import ModelDiscoveryService, ModelInfo
from ..config_models import AIProvider, AIModel
from ..adapters.base import AIProviderType

logger = logging.getLogger(__name__)


class SyncModelDiscoveryService:
    """同步版本的模型发现服务"""
    
    def __init__(self):
        self.async_service = ModelDiscoveryService()
    
    def get_all_models_sync(self, force_refresh: bool = False) -> Dict[str, List[ModelInfo]]:
        """
        获取所有提供商的模型列表（同步版本）
        
        Args:
            force_refresh: 是否强制刷新缓存
            
        Returns:
            按提供商分组的模型列表
        """
        cache_key = f"{self.async_service.CACHE_KEY_PREFIX}:all_models"
        
        if not force_refresh:
            cached_data = cache.get(cache_key)
            if cached_data:
                logger.info("从缓存获取模型列表")
                return self.async_service._deserialize_models(cached_data)
        
        logger.info("开始获取所有提供商的模型列表（同步模式）")
        all_models = {}
        
        # 获取活跃的提供商
        active_providers = AIProvider.objects.filter(is_active=True)
        
        for provider in active_providers:
            try:
                # 检查提供商类型是否有效
                try:
                    provider_type = AIProviderType(provider.provider_type)
                except ValueError:
                    logger.warning(f"跳过不支持的提供商类型: {provider.provider_type}")
                    all_models[provider.provider_type] = []
                    continue
                
                models = self.get_provider_models_sync(provider_type, provider)
                all_models[provider.provider_type] = models
                logger.info(f"获取到 {provider.display_name} 的 {len(models)} 个模型")
            except Exception as e:
                logger.error(f"获取提供商 {provider.display_name} 模型失败: {e}")
                all_models[provider.provider_type] = []
        
        # 缓存结果
        serializable_data = self.async_service._serialize_models(all_models)
        cache.set(cache_key, serializable_data, self.async_service.CACHE_TIMEOUT)
        
        logger.info(f"模型发现完成，共获取 {sum(len(models) for models in all_models.values())} 个模型")
        return all_models
    
    def get_provider_models_sync(
        self, 
        provider_type: AIProviderType, 
        provider: AIProvider
    ) -> List[ModelInfo]:
        """
        获取特定提供商的模型列表（同步版本）
        
        Args:
            provider_type: 提供商类型
            provider: 提供商实例
            
        Returns:
            模型信息列表
        """
        # 对于同步版本，我们主要使用预定义模型
        # 如果需要API调用，可以在后续版本中添加同步HTTP请求
        
        models = self.async_service.PREDEFINED_MODELS.get(provider_type, [])
        
        # 更新模型中的提供商信息
        updated_models = []
        for model in models:
            # 创建新的模型实例，更新提供商信息
            updated_model = ModelInfo(
                id=model.id,
                name=model.name,
                display_name=model.display_name,
                provider=provider.display_name,  # 使用数据库中的显示名称
                provider_type=provider.provider_type,
                description=model.description,
                max_tokens=model.max_tokens,
                supports_streaming=model.supports_streaming,
                supports_functions=model.supports_functions,
                supports_vision=model.supports_vision,
                cost_per_1k_input=model.cost_per_1k_input,
                cost_per_1k_output=model.cost_per_1k_output,
                is_recommended=model.is_recommended,
                context_window=model.context_window,
                release_date=model.release_date,
                capabilities=model.capabilities.copy() if model.capabilities else []
            )
            updated_models.append(updated_model)
        
        return updated_models
    
    def sync_models_to_database_sync(self, force_refresh: bool = False) -> Dict[str, int]:
        """
        同步模型到数据库（同步版本）
        
        Args:
            force_refresh: 是否强制刷新
            
        Returns:
            同步统计信息
        """
        logger.info("开始同步模型到数据库（同步模式）")
        
        # 获取所有模型
        all_models = self.get_all_models_sync(force_refresh)
        
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
    
    def clear_cache_sync(self, provider_type: str = None):
        """清除缓存（同步版本）"""
        if provider_type:
            cache_key = f"{self.async_service.CACHE_KEY_PREFIX}:provider:{provider_type}"
            cache.delete(cache_key)
            logger.info(f"清除提供商 {provider_type} 的缓存")
        else:
            # 清除所有相关缓存
            cache_keys = [
                f"{self.async_service.CACHE_KEY_PREFIX}:all_models",
            ]
            
            # 清除所有提供商缓存
            for provider_type_enum in AIProviderType:
                cache_keys.append(f"{self.async_service.CACHE_KEY_PREFIX}:provider:{provider_type_enum.value}")
            
            cache.delete_many(cache_keys)
            logger.info("清除所有模型发现缓存")


# 全局实例
sync_model_discovery_service = SyncModelDiscoveryService()
