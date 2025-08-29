# -*- coding: utf-8 -*-
"""
API缓存策略模块
实现分层缓存、智能失效和性能监控
"""
import hashlib
import json
import logging
import time
from typing import Any, Dict, List, Optional, Union, Callable
from functools import wraps
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from django.db.models import QuerySet
from rest_framework.response import Response


logger = logging.getLogger(__name__)


class CacheStrategy:
    """缓存策略管理器"""
    
    # 缓存层级定义
    CACHE_LAYERS = {
        'L1_HOT': 60,           # 1分钟 - 热点数据
        'L2_FREQUENT': 300,     # 5分钟 - 频繁访问
        'L3_NORMAL': 1800,      # 30分钟 - 普通数据
        'L4_COLD': 3600,        # 1小时 - 冷数据
        'L5_STATIC': 86400,     # 24小时 - 静态数据
    }
    
    # 缓存键前缀
    CACHE_PREFIXES = {
        'api': 'api:v1:',
        'expression': 'expr:',
        'user': 'user:',
        'stats': 'stats:',
        'search': 'search:',
        'ai': 'ai:',
    }
    
    @classmethod
    def get_cache_key(cls, prefix: str, *args, **kwargs) -> str:
        """生成标准化缓存键"""
        base_prefix = cls.CACHE_PREFIXES.get(prefix, f"{prefix}:")
        
        # 构建键组件
        key_parts = [base_prefix]
        key_parts.extend(str(arg) for arg in args)
        
        # 添加关键字参数
        if kwargs:
            sorted_kwargs = sorted(kwargs.items())
            kwargs_str = '&'.join(f"{k}={v}" for k, v in sorted_kwargs)
            key_parts.append(kwargs_str)
        
        # 生成最终键
        cache_key = ''.join(key_parts)
        
        # 如果键太长，使用哈希
        if len(cache_key) > 200:
            hash_suffix = hashlib.md5(cache_key.encode()).hexdigest()[:8]
            cache_key = f"{base_prefix}hash:{hash_suffix}"
        
        return cache_key
    
    @classmethod
    def set_with_layer(cls, key: str, value: Any, layer: str = 'L3_NORMAL', 
                      prefix: str = 'api') -> bool:
        """按层级设置缓存"""
        try:
            full_key = cls.get_cache_key(prefix, key)
            timeout = cls.CACHE_LAYERS.get(layer, cls.CACHE_LAYERS['L3_NORMAL'])
            
            # 记录缓存操作
            logger.debug(f"Setting cache: {full_key} (layer: {layer}, timeout: {timeout}s)")
            
            cache.set(full_key, value, timeout)
            
            # 记录缓存统计
            cls._record_cache_operation('set', prefix, layer)
            return True
            
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    @classmethod
    def get_with_fallback(cls, key: str, fallback_func: Callable = None, 
                         prefix: str = 'api', layer: str = 'L3_NORMAL') -> Any:
        """获取缓存，支持回退函数"""
        try:
            full_key = cls.get_cache_key(prefix, key)
            value = cache.get(full_key)
            
            if value is not None:
                # 记录缓存命中
                cls._record_cache_operation('hit', prefix, layer)
                logger.debug(f"Cache hit: {full_key}")
                return value
            
            # 缓存未命中，执行回退函数
            cls._record_cache_operation('miss', prefix, layer)
            logger.debug(f"Cache miss: {full_key}")
            
            if fallback_func:
                value = fallback_func()
                if value is not None:
                    cls.set_with_layer(key, value, layer, prefix)
                return value
            
            return None
            
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return fallback_func() if fallback_func else None
    
    @classmethod
    def invalidate_pattern(cls, pattern: str, prefix: str = 'api') -> int:
        """按模式批量失效缓存"""
        try:
            # 构建完整模式
            full_pattern = cls.get_cache_key(prefix, pattern)
            
            # 获取所有匹配的键（这里简化实现，实际需要Redis SCAN）
            # 注意：django_redis支持delete_pattern
            from django_redis import get_redis_connection
            
            redis_conn = get_redis_connection("default")
            keys = redis_conn.keys(f"{full_pattern}*")
            
            if keys:
                count = redis_conn.delete(*keys)
                logger.info(f"Invalidated {count} cache keys matching pattern: {full_pattern}")
                return count
            
            return 0
            
        except Exception as e:
            logger.error(f"Cache invalidation error: {e}")
            return 0
    
    @classmethod
    def _record_cache_operation(cls, operation: str, prefix: str, layer: str):
        """记录缓存操作统计"""
        try:
            stats_key = f"cache_stats:{operation}:{prefix}:{layer}"
            current_count = cache.get(stats_key, 0)
            cache.set(stats_key, current_count + 1, 3600)  # 1小时统计窗口
        except Exception:
            pass  # 统计失败不影响主流程


class CacheDecorators:
    """缓存装饰器集合"""
    
    @staticmethod
    def api_cache(layer: str = 'L3_NORMAL', prefix: str = 'api', 
                  key_func: Optional[Callable] = None):
        """API响应缓存装饰器"""
        def decorator(view_func):
            @wraps(view_func)
            def wrapper(*args, **kwargs):
                # 生成缓存键
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    # 默认键生成策略
                    request = args[1] if len(args) > 1 else kwargs.get('request')
                    cache_key = f"{view_func.__name__}:{request.path}:{hash(str(request.GET))}"
                
                # 尝试从缓存获取
                cached_response = CacheStrategy.get_with_fallback(
                    cache_key, 
                    prefix=prefix, 
                    layer=layer
                )
                
                if cached_response:
                    return Response(cached_response)
                
                # 执行视图函数
                response = view_func(*args, **kwargs)
                
                # 缓存成功响应
                if hasattr(response, 'data') and response.status_code == 200:
                    CacheStrategy.set_with_layer(
                        cache_key, 
                        response.data, 
                        layer=layer, 
                        prefix=prefix
                    )
                
                return response
            return wrapper
        return decorator
    
    @staticmethod
    def model_cache(model_name: str, layer: str = 'L3_NORMAL'):
        """模型数据缓存装饰器"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # 生成基于参数的缓存键
                cache_key = f"{model_name}:{func.__name__}:{hash(str(args) + str(kwargs))}"
                
                return CacheStrategy.get_with_fallback(
                    cache_key,
                    lambda: func(*args, **kwargs),
                    prefix='api',
                    layer=layer
                )
            return wrapper
        return decorator


class ExpressionCacheManager:
    """地道表达专用缓存管理器"""
    
    @staticmethod
    def cache_hot_expressions(limit: int = 100) -> List[Dict]:
        """缓存热门表达"""
        def get_hot_expressions():
            from apps.english.models import Expression
            return list(Expression.objects.filter(
                is_active=True
            ).order_by('-usage_count')[:limit].values(
                'id', 'text', 'meaning', 'difficulty_level', 'usage_count'
            ))
        
        return CacheStrategy.get_with_fallback(
            f'hot_expressions:{limit}',
            get_hot_expressions,
            prefix='expression',
            layer='L2_FREQUENT'
        )
    
    @staticmethod
    def cache_user_preferences(user_id: int) -> Dict:
        """缓存用户偏好设置"""
        def get_user_prefs():
            from apps.users.models import UserProfile
            try:
                profile = UserProfile.objects.get(user_id=user_id)
                return {
                    'difficulty_preference': getattr(profile, 'difficulty_preference', 'intermediate'),
                    'learning_goals': getattr(profile, 'learning_goals', []),
                    'daily_target': getattr(profile, 'daily_target', 10),
                }
            except UserProfile.DoesNotExist:
                return {'difficulty_preference': 'intermediate', 'learning_goals': [], 'daily_target': 10}
        
        return CacheStrategy.get_with_fallback(
            f'user_prefs:{user_id}',
            get_user_prefs,
            prefix='user',
            layer='L3_NORMAL'
        )
    
    @staticmethod
    def invalidate_user_cache(user_id: int):
        """失效用户相关缓存"""
        patterns = [
            f'user:user_prefs:{user_id}',
            f'stats:user:{user_id}',
            f'api:user:{user_id}',
        ]
        
        total_invalidated = 0
        for pattern in patterns:
            total_invalidated += CacheStrategy.invalidate_pattern(pattern)
        
        logger.info(f"Invalidated {total_invalidated} cache entries for user {user_id}")
        return total_invalidated


class CacheMonitor:
    """缓存性能监控"""
    
    @staticmethod
    def get_cache_stats() -> Dict[str, Any]:
        """获取缓存统计信息"""
        try:
            from django_redis import get_redis_connection
            redis_conn = get_redis_connection("default")
            
            # Redis基础信息
            info = redis_conn.info()
            
            # 缓存操作统计
            cache_operations = {}
            for operation in ['set', 'hit', 'miss']:
                for prefix in CacheStrategy.CACHE_PREFIXES.keys():
                    for layer in CacheStrategy.CACHE_LAYERS.keys():
                        stats_key = f"cache_stats:{operation}:{prefix}:{layer}"
                        count = cache.get(stats_key, 0)
                        if count > 0:
                            cache_operations[f"{operation}_{prefix}_{layer}"] = count
            
            return {
                'redis_info': {
                    'used_memory': info.get('used_memory_human', 'N/A'),
                    'connected_clients': info.get('connected_clients', 0),
                    'total_commands_processed': info.get('total_commands_processed', 0),
                    'keyspace_hits': info.get('keyspace_hits', 0),
                    'keyspace_misses': info.get('keyspace_misses', 0),
                    'hit_rate': round(
                        info.get('keyspace_hits', 0) / 
                        max(info.get('keyspace_hits', 0) + info.get('keyspace_misses', 0), 1) * 100, 
                        2
                    )
                },
                'cache_operations': cache_operations,
                'cache_layers': CacheStrategy.CACHE_LAYERS,
                'timestamp': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {'error': str(e), 'timestamp': timezone.now().isoformat()}
    
    @staticmethod
    def clear_all_cache() -> Dict[str, Any]:
        """清空所有缓存（谨慎使用）"""
        try:
            from django_redis import get_redis_connection
            redis_conn = get_redis_connection("default")
            
            # 获取清理前的统计
            before_stats = CacheMonitor.get_cache_stats()
            
            # 清空缓存
            redis_conn.flushdb()
            
            logger.warning("All cache cleared")
            
            return {
                'success': True,
                'before_stats': before_stats,
                'cleared_at': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return {'success': False, 'error': str(e)}


# 缓存预热策略
class CacheWarmup:
    """缓存预热管理"""
    
    @staticmethod
    def warmup_hot_data():
        """预热热点数据"""
        try:
            logger.info("Starting cache warmup...")
            
            # 预热热门表达
            ExpressionCacheManager.cache_hot_expressions(50)
            
            # 预热常用统计数据
            from apps.english.models import Expression
            total_expressions = Expression.objects.filter(is_active=True).count()
            CacheStrategy.set_with_layer(
                'total_active_expressions', 
                total_expressions, 
                layer='L4_COLD',
                prefix='stats'
            )
            
            logger.info("Cache warmup completed")
            return True
            
        except Exception as e:
            logger.error(f"Cache warmup failed: {e}")
            return False


# 实例化全局服务
cache_strategy = CacheStrategy()
expression_cache = ExpressionCacheManager()
cache_monitor = CacheMonitor()
cache_warmup = CacheWarmup()
