# -*- coding: utf-8 -*-
"""
地道表达模块缓存策略
"""
from django.core.cache import cache
from django.conf import settings
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Count
from datetime import datetime, timedelta
import json
import logging
import hashlib

from .models import IdiomaticExpression, UserExpressionProgress, ExpressionSource, ExpressionScenario

logger = logging.getLogger(__name__)


class EnglishCacheManager:
    """地道表达缓存管理器"""
    
    # 缓存键前缀
    PREFIX = 'english'
    
    # 缓存超时时间 (秒)
    TIMEOUTS = {
        'expression_list': 3600,      # 1小时
        'expression_detail': 7200,    # 2小时
        'user_progress': 1800,        # 30分钟
        'statistics': 900,            # 15分钟
        'hot_expressions': 14400,     # 4小时
        'search_results': 1800,       # 30分钟
        'random_pool': 3600,          # 1小时
    }
    
    @classmethod
    def _make_key(cls, category, *args):
        """生成缓存键"""
        key_parts = [cls.PREFIX, category] + [str(arg) for arg in args]
        return ':'.join(key_parts)
    
    @classmethod
    def _make_hash_key(cls, category, data):
        """为复杂数据生成哈希键"""
        data_str = json.dumps(data, sort_keys=True)
        hash_obj = hashlib.md5(data_str.encode())
        return cls._make_key(category, hash_obj.hexdigest())
    
    # 表达列表缓存
    @classmethod
    def get_expression_list(cls, filters=None, page=1, page_size=20):
        """获取表达列表缓存"""
        cache_key = cls._make_hash_key('expression_list', {
            'filters': filters or {},
            'page': page,
            'page_size': page_size
        })
        return cache.get(cache_key)
    
    @classmethod
    def set_expression_list(cls, data, filters=None, page=1, page_size=20):
        """设置表达列表缓存"""
        cache_key = cls._make_hash_key('expression_list', {
            'filters': filters or {},
            'page': page,
            'page_size': page_size
        })
        timeout = cls.TIMEOUTS['expression_list']
        cache.set(cache_key, data, timeout)
        logger.debug(f"缓存表达列表: {cache_key}, 超时: {timeout}秒")
    
    # 表达详情缓存
    @classmethod
    def get_expression_detail(cls, expression_id):
        """获取表达详情缓存"""
        cache_key = cls._make_key('expression_detail', expression_id)
        return cache.get(cache_key)
    
    @classmethod
    def set_expression_detail(cls, expression_id, data):
        """设置表达详情缓存"""
        cache_key = cls._make_key('expression_detail', expression_id)
        timeout = cls.TIMEOUTS['expression_detail']
        cache.set(cache_key, data, timeout)
        logger.debug(f"缓存表达详情: {cache_key}, 超时: {timeout}秒")
    
    @classmethod
    def invalidate_expression(cls, expression_id):
        """失效特定表达的所有缓存"""
        # 删除详情缓存
        detail_key = cls._make_key('expression_detail', expression_id)
        cache.delete(detail_key)
        
        # 删除相关的列表缓存（通过模式匹配）
        cls._invalidate_pattern('expression_list')
        cls._invalidate_pattern('hot_expressions')
        cls._invalidate_pattern('random_pool')
        
        logger.info(f"失效表达缓存: ID {expression_id}")
    
    # 用户进度缓存
    @classmethod
    def get_user_progress(cls, user_id, expression_id=None):
        """获取用户进度缓存"""
        if expression_id:
            cache_key = cls._make_key('user_progress', user_id, expression_id)
        else:
            cache_key = cls._make_key('user_progress_list', user_id)
        return cache.get(cache_key)
    
    @classmethod
    def set_user_progress(cls, user_id, data, expression_id=None):
        """设置用户进度缓存"""
        if expression_id:
            cache_key = cls._make_key('user_progress', user_id, expression_id)
        else:
            cache_key = cls._make_key('user_progress_list', user_id)
        timeout = cls.TIMEOUTS['user_progress']
        cache.set(cache_key, data, timeout)
        logger.debug(f"缓存用户进度: {cache_key}")
    
    @classmethod
    def invalidate_user_progress(cls, user_id, expression_id=None):
        """失效用户进度缓存"""
        if expression_id:
            cache_key = cls._make_key('user_progress', user_id, expression_id)
            cache.delete(cache_key)
        
        # 失效用户的统计缓存
        cls._invalidate_pattern(f'user_progress_list:{user_id}')
        cls._invalidate_pattern(f'statistics:{user_id}')
        
        logger.info(f"失效用户进度缓存: 用户 {user_id}, 表达 {expression_id}")
    
    # 统计数据缓存
    @classmethod
    def get_statistics(cls, user_id, stat_type='overview'):
        """获取统计数据缓存"""
        cache_key = cls._make_key('statistics', user_id, stat_type)
        return cache.get(cache_key)
    
    @classmethod
    def set_statistics(cls, user_id, stat_type, data):
        """设置统计数据缓存"""
        cache_key = cls._make_key('statistics', user_id, stat_type)
        timeout = cls.TIMEOUTS['statistics']
        cache.set(cache_key, data, timeout)
        logger.debug(f"缓存统计数据: {cache_key}")
    
    # 热门表达缓存
    @classmethod
    def get_hot_expressions(cls, limit=10):
        """获取热门表达缓存"""
        cache_key = cls._make_key('hot_expressions', limit)
        return cache.get(cache_key)
    
    @classmethod
    def set_hot_expressions(cls, data, limit=10):
        """设置热门表达缓存"""
        cache_key = cls._make_key('hot_expressions', limit)
        timeout = cls.TIMEOUTS['hot_expressions']
        cache.set(cache_key, data, timeout)
        logger.debug(f"缓存热门表达: {cache_key}")
    
    # 搜索结果缓存
    @classmethod
    def get_search_results(cls, query, filters=None):
        """获取搜索结果缓存"""
        cache_key = cls._make_hash_key('search_results', {
            'query': query,
            'filters': filters or {}
        })
        return cache.get(cache_key)
    
    @classmethod
    def set_search_results(cls, query, data, filters=None):
        """设置搜索结果缓存"""
        cache_key = cls._make_hash_key('search_results', {
            'query': query,
            'filters': filters or {}
        })
        timeout = cls.TIMEOUTS['search_results']
        cache.set(cache_key, data, timeout)
        logger.debug(f"缓存搜索结果: {cache_key}")
    
    # 随机表达池缓存
    @classmethod
    def get_random_pool(cls, difficulty_level=None):
        """获取随机表达池缓存"""
        cache_key = cls._make_key('random_pool', difficulty_level or 'all')
        return cache.get(cache_key)
    
    @classmethod
    def set_random_pool(cls, data, difficulty_level=None):
        """设置随机表达池缓存"""
        cache_key = cls._make_key('random_pool', difficulty_level or 'all')
        timeout = cls.TIMEOUTS['random_pool']
        cache.set(cache_key, data, timeout)
        logger.debug(f"缓存随机池: {cache_key}")
    
    # 缓存失效辅助方法
    @classmethod
    def _invalidate_pattern(cls, pattern):
        """根据模式失效缓存（简化版本）"""
        # 注意：这是一个简化版本，实际生产环境可能需要Redis的SCAN命令
        # 这里我们只是记录日志，实际的模式匹配删除需要Redis支持
        logger.debug(f"请求失效缓存模式: {pattern}")
        
        # 如果使用Redis，可以实现真正的模式匹配删除
        try:
            from django_redis import get_redis_connection
            redis_conn = get_redis_connection("default")
            keys = redis_conn.keys(f"{cls.PREFIX}:{pattern}*")
            if keys:
                redis_conn.delete(*keys)
                logger.info(f"删除了 {len(keys)} 个匹配的缓存键")
        except Exception as e:
            logger.warning(f"模式删除缓存失败: {e}")
    
    @classmethod
    def clear_all(cls):
        """清除所有地道表达相关缓存"""
        cls._invalidate_pattern('')
        logger.info("清除所有地道表达缓存")
    
    @classmethod
    def get_cache_stats(cls):
        """获取缓存统计信息"""
        try:
            from django_redis import get_redis_connection
            redis_conn = get_redis_connection("default")
            info = redis_conn.info()
            
            return {
                'redis_version': info.get('redis_version'),
                'used_memory_human': info.get('used_memory_human'),
                'connected_clients': info.get('connected_clients'),
                'total_commands_processed': info.get('total_commands_processed'),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'hit_rate': round(
                    info.get('keyspace_hits', 0) / 
                    max(info.get('keyspace_hits', 0) + info.get('keyspace_misses', 0), 1) * 100, 2
                )
            }
        except Exception as e:
            logger.error(f"获取缓存统计失败: {e}")
            return {'error': str(e)}


class CachePreheater:
    """缓存预热器"""
    
    @classmethod
    def preheat_hot_expressions(cls):
        """预热热门表达数据"""
        try:
            from .models import IdiomaticExpression
            
            # 获取最受欢迎的表达（基于用户进度数量）
            hot_expressions = IdiomaticExpression.objects.annotate(
                progress_count=Count('userexpressionprogress')
            ).order_by('-progress_count')[:20]
            
            # 缓存热门表达
            hot_data = []
            for expr in hot_expressions:
                data = {
                    'id': expr.id,
                    'expression': expr.expression,
                    'meaning': expr.meaning,
                    'difficulty_level': expr.difficulty_level,
                    'progress_count': expr.progress_count
                }
                hot_data.append(data)
                
                # 同时缓存详情
                EnglishCacheManager.set_expression_detail(expr.id, data)
            
            EnglishCacheManager.set_hot_expressions(hot_data)
            logger.info(f"预热了 {len(hot_data)} 个热门表达")
            
        except Exception as e:
            logger.error(f"预热热门表达失败: {e}")
    
    @classmethod
    def preheat_random_pools(cls):
        """预热随机表达池"""
        try:
            from .models import IdiomaticExpression
            
            difficulty_levels = ['beginner', 'intermediate', 'advanced']
            
            for level in difficulty_levels:
                expressions = list(IdiomaticExpression.objects.filter(
                    difficulty_level=level
                ).values('id', 'expression', 'meaning', 'difficulty_level')[:100])
                
                EnglishCacheManager.set_random_pool(expressions, level)
                logger.info(f"预热了 {level} 级别的随机池，{len(expressions)} 个表达")
            
            # 预热全部级别的随机池
            all_expressions = list(IdiomaticExpression.objects.values(
                'id', 'expression', 'meaning', 'difficulty_level'
            )[:200])
            EnglishCacheManager.set_random_pool(all_expressions)
            logger.info(f"预热了全部级别的随机池，{len(all_expressions)} 个表达")
            
        except Exception as e:
            logger.error(f"预热随机池失败: {e}")
    
    @classmethod
    def preheat_all(cls):
        """预热所有缓存"""
        logger.info("开始预热地道表达缓存...")
        cls.preheat_hot_expressions()
        cls.preheat_random_pools()
        logger.info("缓存预热完成")


# 信号处理器 - 自动缓存失效
@receiver(post_save, sender=IdiomaticExpression)
def invalidate_expression_cache_on_save(sender, instance, **kwargs):
    """表达保存时失效相关缓存"""
    EnglishCacheManager.invalidate_expression(instance.id)
    logger.debug(f"表达保存触发缓存失效: {instance.expression}")


@receiver(post_delete, sender=IdiomaticExpression)
def invalidate_expression_cache_on_delete(sender, instance, **kwargs):
    """表达删除时失效相关缓存"""
    EnglishCacheManager.invalidate_expression(instance.id)
    logger.debug(f"表达删除触发缓存失效: {instance.expression}")


@receiver(post_save, sender=UserExpressionProgress)
def invalidate_progress_cache_on_save(sender, instance, **kwargs):
    """用户进度保存时失效相关缓存"""
    EnglishCacheManager.invalidate_user_progress(
        instance.user_id, instance.expression_id
    )
    logger.debug(f"用户进度保存触发缓存失效: 用户 {instance.user_id}, 表达 {instance.expression_id}")


@receiver(post_delete, sender=UserExpressionProgress)
def invalidate_progress_cache_on_delete(sender, instance, **kwargs):
    """用户进度删除时失效相关缓存"""
    EnglishCacheManager.invalidate_user_progress(
        instance.user_id, instance.expression_id
    )
    logger.debug(f"用户进度删除触发缓存失效: 用户 {instance.user_id}, 表达 {instance.expression_id}")


class CacheMonitor:
    """缓存监控器"""
    
    @classmethod
    def get_cache_metrics(cls):
        """获取缓存性能指标"""
        metrics = EnglishCacheManager.get_cache_stats()
        
        # 添加应用级别的指标
        try:
            # 统计地道表达相关的缓存键数量
            from django_redis import get_redis_connection
            redis_conn = get_redis_connection("default")
            
            english_keys = redis_conn.keys(f"{EnglishCacheManager.PREFIX}:*")
            metrics.update({
                'english_cache_keys': len(english_keys),
                'cache_categories': {
                    'expressions': len([k for k in english_keys if b'expression' in k]),
                    'progress': len([k for k in english_keys if b'progress' in k]),
                    'statistics': len([k for k in english_keys if b'statistics' in k]),
                    'search': len([k for k in english_keys if b'search' in k]),
                }
            })
            
        except Exception as e:
            logger.error(f"获取缓存指标失败: {e}")
            metrics['app_metrics_error'] = str(e)
        
        return metrics
    
    @classmethod
    def log_cache_performance(cls):
        """记录缓存性能日志"""
        metrics = cls.get_cache_metrics()
        logger.info(f"缓存性能指标: {json.dumps(metrics, indent=2)}")
        return metrics


class ResponseCacheMiddleware:
    """API响应缓存中间件"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.cacheable_paths = [
            '/api/v1/expressions/',
            '/api/v1/expression-sources/',
            '/api/v1/expression-scenarios/',
        ]
        self.cache_timeout = 300  # 5分钟
    
    def __call__(self, request):
        # 检查是否为可缓存的GET请求
        if (request.method == 'GET' and 
            any(request.path.startswith(path) for path in self.cacheable_paths)):
            
            cache_key = self._make_response_cache_key(request)
            cached_response = cache.get(cache_key)
            
            if cached_response:
                logger.debug(f"返回缓存响应: {cache_key}")
                return cached_response
        
        response = self.get_response(request)
        
        # 缓存成功的GET响应
        if (request.method == 'GET' and 
            response.status_code == 200 and
            any(request.path.startswith(path) for path in self.cacheable_paths)):
            
            cache_key = self._make_response_cache_key(request)
            cache.set(cache_key, response, self.cache_timeout)
            logger.debug(f"缓存响应: {cache_key}")
        
        return response
    
    def _make_response_cache_key(self, request):
        """生成响应缓存键"""
        path = request.path
        query_string = request.META.get('QUERY_STRING', '')
        user_id = getattr(request.user, 'id', 'anon')
        
        key_data = f"{path}?{query_string}:user_{user_id}"
        hash_obj = hashlib.md5(key_data.encode())
        return f"response_cache:{hash_obj.hexdigest()}"
