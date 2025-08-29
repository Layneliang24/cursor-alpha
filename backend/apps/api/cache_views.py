# -*- coding: utf-8 -*-
"""
缓存管理API视图
提供缓存监控、管理和调试功能
"""
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .cache_strategy import (
    CacheStrategy, CacheMonitor, CacheWarmup, 
    ExpressionCacheManager, cache_strategy, cache_monitor
)


@extend_schema_view(
    list=extend_schema(
        summary="获取缓存统计信息",
        description="获取Redis缓存的详细统计信息，包括内存使用、命中率、操作统计等",
        tags=['Cache', 'Monitoring']
    )
)
class CacheViewSet(viewsets.ViewSet):
    """缓存管理API"""
    
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        """管理操作需要管理员权限"""
        if self.action in ['clear_all', 'warmup']:
            return [IsAdminUser()]
        return [IsAuthenticated()]
    
    @extend_schema(
        summary="获取缓存统计",
        description="获取Redis缓存的详细统计信息",
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'redis_info': {'type': 'object', 'description': 'Redis基础信息'},
                    'cache_operations': {'type': 'object', 'description': '缓存操作统计'},
                    'cache_layers': {'type': 'object', 'description': '缓存层级配置'},
                    'timestamp': {'type': 'string', 'format': 'date-time'}
                }
            }
        }
    )
    def list(self, request):
        """获取缓存统计信息"""
        stats = cache_monitor.get_cache_stats()
        return Response(stats)
    
    @extend_schema(
        summary="清空所有缓存",
        description="清空Redis中的所有缓存数据（管理员操作，谨慎使用）",
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean'},
                    'before_stats': {'type': 'object'},
                    'cleared_at': {'type': 'string', 'format': 'date-time'}
                }
            }
        }
    )
    @action(detail=False, methods=['post'], permission_classes=[IsAdminUser])
    def clear_all(self, request):
        """清空所有缓存"""
        result = cache_monitor.clear_all_cache()
        return Response(result)
    
    @extend_schema(
        summary="缓存预热",
        description="预热热点数据到缓存中，提升系统响应性能",
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean'},
                    'message': {'type': 'string'},
                    'warmed_at': {'type': 'string', 'format': 'date-time'}
                }
            }
        }
    )
    @action(detail=False, methods=['post'], permission_classes=[IsAdminUser])
    def warmup(self, request):
        """缓存预热"""
        success = CacheWarmup.warmup_hot_data()
        
        return Response({
            'success': success,
            'message': '缓存预热完成' if success else '缓存预热失败',
            'warmed_at': timezone.now().isoformat()
        })
    
    @extend_schema(
        summary="失效指定模式的缓存",
        description="根据模式批量失效缓存键",
        parameters=[
            OpenApiParameter(
                'pattern', 
                OpenApiTypes.STR, 
                description='缓存键模式，支持通配符',
                required=True
            ),
            OpenApiParameter(
                'prefix', 
                OpenApiTypes.STR, 
                description='缓存前缀类型',
                enum=['api', 'expression', 'user', 'stats', 'search', 'ai'],
                default='api'
            ),
        ],
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'invalidated_count': {'type': 'integer'},
                    'pattern': {'type': 'string'},
                    'prefix': {'type': 'string'}
                }
            }
        }
    )
    @action(detail=False, methods=['post'], permission_classes=[IsAdminUser])
    def invalidate(self, request):
        """按模式失效缓存"""
        pattern = request.data.get('pattern')
        prefix = request.data.get('prefix', 'api')
        
        if not pattern:
            return Response(
                {'error': 'pattern参数是必需的'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        count = CacheStrategy.invalidate_pattern(pattern, prefix)
        
        return Response({
            'invalidated_count': count,
            'pattern': pattern,
            'prefix': prefix
        })
    
    @extend_schema(
        summary="获取热门表达缓存",
        description="获取缓存的热门地道表达列表",
        parameters=[
            OpenApiParameter(
                'limit', 
                OpenApiTypes.INT, 
                description='返回数量限制',
                default=50
            ),
            OpenApiParameter(
                'force_refresh', 
                OpenApiTypes.BOOL, 
                description='强制刷新缓存',
                default=False
            ),
        ],
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'expressions': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'id': {'type': 'integer'},
                                'text': {'type': 'string'},
                                'meaning': {'type': 'string'},
                                'difficulty_level': {'type': 'string'},
                                'usage_count': {'type': 'integer'}
                            }
                        }
                    },
                    'cached': {'type': 'boolean'},
                    'timestamp': {'type': 'string', 'format': 'date-time'}
                }
            }
        }
    )
    @action(detail=False, methods=['get'])
    def hot_expressions(self, request):
        """获取热门表达（缓存版本）"""
        limit = int(request.query_params.get('limit', 50))
        force_refresh = request.query_params.get('force_refresh', 'false').lower() == 'true'
        
        if force_refresh:
            # 强制刷新：先失效缓存
            CacheStrategy.invalidate_pattern(f'hot_expressions:{limit}', 'expression')
        
        expressions = ExpressionCacheManager.cache_hot_expressions(limit)
        
        return Response({
            'expressions': expressions,
            'cached': not force_refresh,
            'timestamp': timezone.now().isoformat()
        })
