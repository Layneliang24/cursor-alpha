# -*- coding: utf-8 -*-
"""
API缓存中间件
自动处理HTTP缓存头和响应缓存
"""
import hashlib
import json
import time
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse, JsonResponse
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class APICacheMiddleware(MiddlewareMixin):
    """API响应缓存中间件"""
    
    # 缓存配置
    CACHEABLE_METHODS = ['GET', 'HEAD']
    CACHE_TIMEOUT = 300  # 5分钟默认缓存
    
    # 缓存策略配置
    CACHE_STRATEGIES = {
        '/api/v1/expressions/': {'timeout': 600, 'vary': ['Accept', 'Authorization']},  # 10分钟
        '/api/v1/statistics/': {'timeout': 1800, 'vary': ['Accept', 'Authorization']},  # 30分钟
        '/api/v1/cache/': {'timeout': 60, 'vary': ['Accept']},  # 1分钟
        '/api/v1/ai-assistant/': {'timeout': 0, 'vary': []},  # 不缓存AI响应
    }
    
    def process_request(self, request):
        """处理请求 - 检查缓存"""
        # 只处理API请求
        if not request.path.startswith('/api/v1/'):
            return None
        
        # 只缓存安全方法
        if request.method not in self.CACHEABLE_METHODS:
            return None
        
        # 生成缓存键
        cache_key = self._generate_cache_key(request)
        
        # 尝试从缓存获取
        cached_response = cache.get(cache_key)
        if cached_response:
            logger.debug(f"Cache hit for: {request.path}")
            
            # 返回缓存的响应
            response = JsonResponse(cached_response['data'])
            
            # 添加缓存头
            response['X-Cache'] = 'HIT'
            response['X-Cache-Key'] = cache_key[:50] + '...' if len(cache_key) > 50 else cache_key
            response['Cache-Control'] = f"public, max-age={cached_response.get('max_age', 300)}"
            response['ETag'] = cached_response.get('etag', '')
            
            # 添加Vary头
            strategy = self._get_cache_strategy(request.path)
            if strategy.get('vary'):
                response['Vary'] = ', '.join(strategy['vary'])
            
            return response
        
        return None
    
    def process_response(self, request, response):
        """处理响应 - 设置缓存"""
        # 只处理API请求
        if not request.path.startswith('/api/v1/'):
            return response
        
        # 只缓存成功的GET请求
        if (request.method not in self.CACHEABLE_METHODS or 
            response.status_code != 200 or
            not hasattr(response, 'data')):
            return response
        
        # 获取缓存策略
        strategy = self._get_cache_strategy(request.path)
        timeout = strategy.get('timeout', self.CACHE_TIMEOUT)
        
        # 不缓存超时为0的路径
        if timeout == 0:
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            return response
        
        # 生成缓存键和ETag
        cache_key = self._generate_cache_key(request)
        
        try:
            # 获取响应数据
            if hasattr(response, 'data'):
                response_data = response.data
            elif hasattr(response, 'content'):
                response_data = json.loads(response.content.decode())
            else:
                return response
            
            # 生成ETag
            etag = hashlib.md5(
                json.dumps(response_data, sort_keys=True, default=str).encode()
            ).hexdigest()
            
            # 检查If-None-Match头
            client_etag = request.META.get('HTTP_IF_NONE_MATCH', '').strip('"')
            if client_etag == etag:
                # 返回304 Not Modified
                from django.http import HttpResponseNotModified
                not_modified = HttpResponseNotModified()
                not_modified['ETag'] = f'"{etag}"'
                not_modified['X-Cache'] = 'VALIDATED'
                return not_modified
            
            # 缓存响应数据
            cache_data = {
                'data': response_data,
                'etag': etag,
                'max_age': timeout,
                'cached_at': timezone.now().isoformat()
            }
            
            cache.set(cache_key, cache_data, timeout)
            logger.debug(f"Cached response for: {request.path} (timeout: {timeout}s)")
            
            # 添加缓存头
            response['X-Cache'] = 'MISS'
            response['X-Cache-Key'] = cache_key[:50] + '...' if len(cache_key) > 50 else cache_key
            response['Cache-Control'] = f"public, max-age={timeout}"
            response['ETag'] = f'"{etag}"'
            
            # 添加Vary头
            if strategy.get('vary'):
                response['Vary'] = ', '.join(strategy['vary'])
            
        except Exception as e:
            logger.error(f"Error caching response: {e}")
        
        return response
    
    def _generate_cache_key(self, request):
        """生成缓存键"""
        # 基础键组件
        key_parts = [
            'api_cache',
            request.path,
            request.method,
        ]
        
        # 添加查询参数（排序后）
        if request.GET:
            query_params = '&'.join(
                f"{k}={v}" for k, v in sorted(request.GET.items())
            )
            key_parts.append(query_params)
        
        # 添加用户ID（如果已认证）
        if hasattr(request, 'user') and request.user.is_authenticated:
            key_parts.append(f"user:{request.user.id}")
        
        # 生成最终键
        cache_key = ':'.join(key_parts)
        
        # 如果键太长，使用哈希
        if len(cache_key) > 200:
            cache_key = f"api_cache:hash:{hashlib.md5(cache_key.encode()).hexdigest()}"
        
        return cache_key
    
    def _get_cache_strategy(self, path):
        """获取路径的缓存策略"""
        # 精确匹配
        if path in self.CACHE_STRATEGIES:
            return self.CACHE_STRATEGIES[path]
        
        # 前缀匹配
        for pattern, strategy in self.CACHE_STRATEGIES.items():
            if path.startswith(pattern):
                return strategy
        
        # 默认策略
        return {'timeout': self.CACHE_TIMEOUT, 'vary': ['Accept', 'Authorization']}


class CacheHeadersMiddleware(MiddlewareMixin):
    """缓存头中间件 - 为静态资源和API添加合适的缓存头"""
    
    def process_response(self, request, response):
        """添加缓存头"""
        
        # 静态文件缓存（1天）
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            response['Cache-Control'] = 'public, max-age=86400'  # 1天
            response['Expires'] = (timezone.now() + timezone.timedelta(days=1)).strftime('%a, %d %b %Y %H:%M:%S GMT')
        
        # API文档缓存（1小时）
        elif request.path in ['/api/schema/', '/api/swagger/', '/api/redoc/']:
            response['Cache-Control'] = 'public, max-age=3600'  # 1小时
        
        # 健康检查不缓存
        elif request.path == '/api/health/':
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        
        # API根路径短期缓存（5分钟）
        elif request.path == '/api/':
            response['Cache-Control'] = 'public, max-age=300'  # 5分钟
        
        return response
