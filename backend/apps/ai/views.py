"""
AI配置管理API视图
"""

import logging
from datetime import datetime, timedelta

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.db.models import Count, Sum, Avg
from django.db import transaction
from apps.rbac.permissions import RBACPermission, CanManageAIConfig
from apps.rbac.services import AuditService
from apps.common.ratelimit import ai_config_limit, ai_test_limit, sensitive_limit
from apps.common.security import DatabaseSecurityMixin
from apps.common.ssl_config import APIKeySecurityManager

from .config_models import (
    AIProvider, APIKey, AIModel, ModelConfig, TokenUsage,
    FailoverStrategy, FailoverRule, UsageQuota
)
from .serializers import (
    AIProviderSerializer, APIKeySerializer, APIKeyCreateSerializer,
    AIModelSerializer, ModelConfigSerializer, TokenUsageSerializer,
    FailoverStrategySerializer, FailoverRuleSerializer, UsageQuotaSerializer
)
from .adapters.factory import AIAdapterFactory

logger = logging.getLogger(__name__)


@method_decorator(ai_config_limit, name='dispatch')
class AIProviderViewSet(DatabaseSecurityMixin, viewsets.ModelViewSet):
    """AI提供商管理ViewSet"""
    
    queryset = AIProvider.objects.all()
    serializer_class = AIProviderSerializer
    permission_classes = [RBACPermission]
    
    # RBAC权限配置
    resource_type = 'ai_config'
    
    def get_permissions(self):
        """根据操作类型返回不同权限"""
        if self.action in ['list', 'retrieve']:
            return [RBACPermission('ai_config.view')]
        elif self.action == 'create':
            return [RBACPermission('ai_config.create')]
        elif self.action in ['update', 'partial_update']:
            return [RBACPermission('ai_config.edit')]
        elif self.action == 'destroy':
            return [RBACPermission('ai_config.delete')]
        elif self.action in ['test_connection', 'bulk_test']:
            return [RBACPermission('ai_config.test')]
        else:
            return [CanManageAIConfig()]
    
    def get_queryset(self):
        """获取查询集"""
        queryset = super().get_queryset()
        
        # 按状态过滤
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # 按健康状态过滤
        is_healthy = self.request.query_params.get('is_healthy')
        if is_healthy is not None:
            queryset = queryset.filter(is_healthy=is_healthy.lower() == 'true')
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """创建提供商时设置创建者"""
        provider = serializer.save(created_by=self.request.user)
        
        # 记录审计日志
        AuditService.log_user_action(
            user=self.request.user,
            action='create_ai_provider',
            resource_type='ai_provider',
            description=f"创建AI提供商: {provider.display_name}",
            request=self.request,
            resource_id=str(provider.id),
            resource_name=provider.display_name,
            new_value={
                'provider_type': provider.provider_type,
                'display_name': provider.display_name,
                'api_endpoint': provider.api_endpoint
            }
        )
    
    @action(detail=True, methods=['post'])
    @method_decorator(ai_test_limit)
    def test_connection(self, request, pk=None):
        """测试单个提供商连接"""
        provider = self.get_object()
        
        try:
            # 获取该提供商的默认API密钥
            api_key = APIKey.objects.filter(
                provider=provider,
                is_active=True,
                is_default=True
            ).first()
            
            if not api_key:
                return Response({
                    'success': False,
                    'message': '未找到可用的API密钥',
                    'provider_id': provider.id,
                    'provider_name': provider.display_name
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 创建适配器并测试连接
            adapter = AIAdapterFactory.create_adapter(
                provider_type=provider.provider_type,
                api_key=api_key.get_key(),
                base_url=provider.base_url
            )
            
            # 执行健康检查
            health_result = adapter.health_check()
            
            # 更新提供商状态
            provider.is_healthy = health_result.is_healthy
            provider.last_health_check = timezone.now()
            if health_result.response_time:
                provider.avg_response_time = health_result.response_time
            provider.save()
            
            return Response({
                'success': health_result.is_healthy,
                'message': '连接测试成功' if health_result.is_healthy else '连接测试失败',
                'provider_id': provider.id,
                'provider_name': provider.display_name,
                'response_time': health_result.response_time,
                'details': health_result.details if hasattr(health_result, 'details') else None
            })
            
        except Exception as e:
            logger.error(f'提供商连接测试失败 {provider.name}: {e}')
            
            # 更新提供商状态为不健康
            provider.is_healthy = False
            provider.last_health_check = timezone.now()
            provider.save()
            
            return Response({
                'success': False,
                'message': f'连接测试失败: {str(e)}',
                'provider_id': provider.id,
                'provider_name': provider.display_name
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    @method_decorator(sensitive_limit)
    def bulk_test(self, request):
        """批量测试所有提供商连接"""
        providers = self.get_queryset().filter(is_active=True)
        results = []
        
        for provider in providers:
            try:
                # 获取该提供商的默认API密钥
                api_key = APIKey.objects.filter(
                    provider=provider,
                    is_active=True,
                    is_default=True
                ).first()
                
                if not api_key:
                    results.append({
                        'provider_id': provider.id,
                        'provider_name': provider.display_name,
                        'success': False,
                        'message': '未找到可用的API密钥'
                    })
                    continue
                
                # 创建适配器并测试连接
                adapter = AIAdapterFactory.create_adapter(
                    provider_type=provider.provider_type,
                    api_key=api_key.get_key(),
                    base_url=provider.base_url
                )
                
                # 执行健康检查
                health_result = adapter.health_check()
                
                # 更新提供商状态
                provider.is_healthy = health_result.is_healthy
                provider.last_health_check = timezone.now()
                if health_result.response_time:
                    provider.avg_response_time = health_result.response_time
                provider.save()
                
                results.append({
                    'provider_id': provider.id,
                    'provider_name': provider.display_name,
                    'success': health_result.is_healthy,
                    'message': '连接正常' if health_result.is_healthy else '连接异常',
                    'response_time': health_result.response_time
                })
                
            except Exception as e:
                logger.error(f'提供商批量测试失败 {provider.name}: {e}')
                
                # 更新提供商状态为不健康
                provider.is_healthy = False
                provider.last_health_check = timezone.now()
                provider.save()
                
                results.append({
                    'provider_id': provider.id,
                    'provider_name': provider.display_name,
                    'success': False,
                    'message': f'测试失败: {str(e)}'
                })
        
        # 统计结果
        total_count = len(results)
        success_count = sum(1 for r in results if r['success'])
        
        return Response({
            'total_tested': total_count,
            'success_count': success_count,
            'failure_count': total_count - success_count,
            'results': results
        })
    
    @action(detail=True, methods=['get'])
    def status_history(self, request, pk=None):
        """获取提供商状态历史"""
        provider = self.get_object()
        
        # 这里可以扩展为从专门的状态历史表获取数据
        # 目前返回基本的状态信息
        return Response({
            'provider_id': provider.id,
            'provider_name': provider.display_name,
            'current_status': {
                'is_healthy': provider.is_healthy,
                'is_active': provider.is_active,
                'last_health_check': provider.last_health_check,
                'avg_response_time': provider.avg_response_time,
                'success_rate': provider.success_rate
            },
            'history': [
                # 可以在这里添加历史状态数据
            ]
        })
    
    @action(detail=False, methods=['get'])
    def system_health(self, request):
        """获取系统整体健康状态"""
        providers = self.get_queryset()
        
        total_count = providers.count()
        healthy_count = providers.filter(is_healthy=True).count()
        active_count = providers.filter(is_active=True).count()
        
        # 计算平均响应时间
        avg_response_time = providers.filter(
            avg_response_time__isnull=False
        ).aggregate(avg_time=Avg('avg_response_time'))['avg_time']
        
        return Response({
            'total_providers': total_count,
            'healthy_providers': healthy_count,
            'active_providers': active_count,
            'health_percentage': (healthy_count / total_count * 100) if total_count > 0 else 0,
            'average_response_time': avg_response_time,
            'last_updated': timezone.now()
        })


@method_decorator(sensitive_limit, name='dispatch')
class APIKeyViewSet(DatabaseSecurityMixin, viewsets.ModelViewSet):
    """API密钥管理ViewSet"""
    
    queryset = APIKey.objects.all()
    permission_classes = [RBACPermission]
    resource_type = 'ai_config'
    
    def get_permissions(self):
        """根据操作类型返回不同权限"""
        if self.action in ['list', 'retrieve']:
            return [RBACPermission('ai_config.view')]
        elif self.action == 'create':
            return [RBACPermission('ai_config.create')]
        elif self.action in ['update', 'partial_update']:
            return [RBACPermission('ai_config.edit')]
        elif self.action == 'destroy':
            return [RBACPermission('ai_config.delete')]
        else:
            return [CanManageAIConfig()]
    
    def get_serializer_class(self):
        """根据动作选择序列化器"""
        if self.action == 'create':
            return APIKeyCreateSerializer
        return APIKeySerializer
    
    def get_queryset(self):
        """获取当前用户的API密钥"""
        queryset = APIKey.objects.filter(user=self.request.user)
        
        # 按提供商过滤
        provider_id = self.request.query_params.get('provider')
        if provider_id:
            queryset = queryset.filter(provider_id=provider_id)
        
        # 按状态过滤
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.select_related('provider').order_by('-created_at')
    
    def perform_create(self, serializer):
        """创建API密钥时设置用户"""
        # 验证API密钥传输安全性
        if not APIKeySecurityManager.validate_key_transmission(self.request):
            from rest_framework.exceptions import ValidationError
            raise ValidationError('请使用HTTPS连接创建API密钥')
        
        api_key = serializer.save(user=self.request.user)
        
        # 记录密钥创建日志
        APIKeySecurityManager.log_key_access(
            user=self.request.user,
            action='create',
            key_id=str(api_key.id)
        )
    
    def list(self, request, *args, **kwargs):
        """获取API密钥列表（安全版本）"""
        queryset = self.filter_queryset(self.get_queryset())
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            # 确保返回安全的响应数据
            safe_data = [
                APIKeySecurityManager.create_secure_api_key_response(item)
                for item in serializer.data
            ]
            return self.get_paginated_response(safe_data)
        
        serializer = self.get_serializer(queryset, many=True)
        safe_data = [
            APIKeySecurityManager.create_secure_api_key_response(item)
            for item in serializer.data
        ]
        return Response(safe_data)
    
    def retrieve(self, request, *args, **kwargs):
        """获取单个API密钥详情（安全版本）"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        # 记录密钥访问日志
        APIKeySecurityManager.log_key_access(
            user=request.user,
            action='view',
            key_id=str(instance.id)
        )
        
        # 返回安全响应
        safe_data = APIKeySecurityManager.create_secure_api_key_response(serializer.data)
        return Response(safe_data)
    
    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """测试API密钥有效性"""
        api_key = self.get_object()
        
        try:
            # 创建适配器并测试
            adapter = AIAdapterFactory.create_adapter(
                provider_type=api_key.provider.provider_type,
                api_key=api_key.get_key(),
                base_url=api_key.provider.base_url
            )
            
            # 执行健康检查
            health_result = adapter.health_check()
            
            # 更新最后使用时间
            if health_result.is_healthy:
                api_key.last_used = timezone.now()
                api_key.save()
            
            return Response({
                'success': health_result.is_healthy,
                'message': '密钥测试成功' if health_result.is_healthy else '密钥测试失败',
                'key_id': api_key.key_id,
                'key_name': api_key.name,
                'response_time': health_result.response_time
            })
            
        except Exception as e:
            logger.error(f'API密钥测试失败 {api_key.name}: {e}')
            return Response({
                'success': False,
                'message': f'密钥测试失败: {str(e)}',
                'key_id': api_key.key_id,
                'key_name': api_key.name
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """设置为默认密钥"""
        api_key = self.get_object()
        
        with transaction.atomic():
            # 取消同一提供商下的其他默认密钥
            APIKey.objects.filter(
                provider=api_key.provider,
                user=self.request.user,
                is_default=True
            ).update(is_default=False)
            
            # 设置当前密钥为默认
            api_key.is_default = True
            api_key.save()
        
        return Response({
            'success': True,
            'message': f'{api_key.name} 已设置为默认密钥',
            'key_id': api_key.key_id
        })
    
    @action(detail=False, methods=['get'])
    def expiring_soon(self, request):
        """获取即将过期的密钥"""
        days_ahead = int(request.query_params.get('days', 7))
        warning_date = timezone.now() + timedelta(days=days_ahead)
        
        expiring_keys = self.get_queryset().filter(
            expires_at__lte=warning_date,
            expires_at__gt=timezone.now(),
            is_active=True
        )
        
        serializer = self.get_serializer(expiring_keys, many=True)
        return Response({
            'count': expiring_keys.count(),
            'days_ahead': days_ahead,
            'keys': serializer.data
        })


class AIModelViewSet(viewsets.ModelViewSet):
    """AI模型管理ViewSet"""
    
    queryset = AIModel.objects.all()
    serializer_class = AIModelSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """获取查询集"""
        queryset = super().get_queryset()
        
        # 按提供商过滤
        provider_id = self.request.query_params.get('provider')
        if provider_id:
            queryset = queryset.filter(provider_id=provider_id)
        
        # 按推荐状态过滤
        is_recommended = self.request.query_params.get('is_recommended')
        if is_recommended is not None:
            queryset = queryset.filter(is_recommended=is_recommended.lower() == 'true')
        
        return queryset.select_related('provider').order_by('-is_recommended', 'provider__name', 'display_name')
    
    @action(detail=False, methods=['get'])
    def recommended(self, request):
        """获取推荐模型"""
        recommended_models = self.get_queryset().filter(
            is_recommended=True,
            is_active=True
        )
        
        serializer = self.get_serializer(recommended_models, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def pricing(self, request, pk=None):
        """获取模型定价信息"""
        model = self.get_object()
        
        return Response({
            'model_id': model.id,
            'model_name': model.display_name,
            'input_cost': model.cost_per_1k_input_tokens,
            'output_cost': model.cost_per_1k_output_tokens,
            'currency': 'USD',
            'unit': 'per 1K tokens',
            'max_tokens': model.max_tokens
        })


class TokenUsageViewSet(viewsets.ReadOnlyModelViewSet):
    """Token使用统计ViewSet（只读）"""
    
    queryset = TokenUsage.objects.all()
    serializer_class = TokenUsageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """获取当前用户的使用记录"""
        queryset = TokenUsage.objects.filter(user=self.request.user)
        
        # 时间范围过滤
        time_range = self.request.query_params.get('time_range', 'week')
        now = timezone.now()
        
        if time_range == 'today':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif time_range == 'week':
            start_date = now - timedelta(days=7)
        elif time_range == 'month':
            start_date = now - timedelta(days=30)
        elif time_range == 'quarter':
            start_date = now - timedelta(days=90)
        else:
            start_date = now - timedelta(days=7)  # 默认一周
        
        queryset = queryset.filter(created_at__gte=start_date)
        
        # 按模型过滤
        model_id = self.request.query_params.get('model')
        if model_id:
            queryset = queryset.filter(model_id=model_id)
        
        return queryset.select_related('model').order_by('-created_at')
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """获取使用统计摘要"""
        queryset = self.get_queryset()
        
        # 聚合统计
        stats = queryset.aggregate(
            total_tokens=Sum('total_tokens'),
            total_cost=Sum('cost'),
            total_requests=Count('id'),
            avg_tokens_per_request=Avg('total_tokens')
        )
        
        # 按模型分组统计
        model_stats = queryset.values(
            'model__display_name',
            'model__provider__display_name'
        ).annotate(
            tokens=Sum('total_tokens'),
            cost=Sum('cost'),
            requests=Count('id')
        ).order_by('-cost')
        
        return Response({
            'summary': {
                'total_tokens': stats['total_tokens'] or 0,
                'total_cost': float(stats['total_cost'] or 0),
                'total_requests': stats['total_requests'] or 0,
                'avg_tokens_per_request': float(stats['avg_tokens_per_request'] or 0)
            },
            'by_model': list(model_stats)
        })
    
    @action(detail=False, methods=['get'])
    def trends(self, request):
        """获取使用趋势数据"""
        queryset = self.get_queryset()
        
        # 按日期分组统计
        daily_stats = queryset.extra(
            select={'date': 'DATE(created_at)'}
        ).values('date').annotate(
            tokens=Sum('total_tokens'),
            cost=Sum('cost'),
            requests=Count('id')
        ).order_by('date')
        
        return Response({
            'daily_trends': list(daily_stats)
        })


class UsageQuotaViewSet(viewsets.ModelViewSet):
    """使用配额管理ViewSet"""
    
    queryset = UsageQuota.objects.all()
    serializer_class = UsageQuotaSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """获取当前用户的配额"""
        return UsageQuota.objects.filter(user=self.request.user).order_by('-created_at')
    
    def perform_create(self, serializer):
        """创建配额时设置用户"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def reset(self, request, pk=None):
        """重置配额使用量"""
        quota = self.get_object()
        
        quota.used_amount = 0
        quota.last_reset = timezone.now()
        quota.save()
        
        return Response({
            'success': True,
            'message': f'配额 {quota.quota_name} 已重置',
            'quota_id': quota.id,
            'reset_time': quota.last_reset
        })
    
    @action(detail=False, methods=['get'])
    def status(self, request):
        """获取所有配额状态"""
        quotas = self.get_queryset().filter(is_active=True)
        
        status_data = []
        for quota in quotas:
            usage_percentage = (quota.used_amount / quota.limit_amount * 100) if quota.limit_amount > 0 else 0
            
            status_data.append({
                'quota_id': quota.id,
                'quota_name': quota.quota_name,
                'quota_type': quota.quota_type,
                'used_amount': quota.used_amount,
                'limit_amount': quota.limit_amount,
                'usage_percentage': usage_percentage,
                'is_exceeded': quota.used_amount >= quota.limit_amount,
                'last_reset': quota.last_reset
            })
        
        return Response({
            'quotas': status_data,
            'total_quotas': len(status_data),
            'exceeded_quotas': sum(1 for q in status_data if q['is_exceeded'])
        })


class ModelDiscoveryViewSet(viewsets.ViewSet):
    """模型发现ViewSet"""
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def discover(self, request):
        """发现所有提供商的可用模型"""
        from .services.model_discovery import model_discovery_service
        
        force_refresh = request.query_params.get('force_refresh', 'false').lower() == 'true'
        provider_filter = request.query_params.get('provider')
        
        try:
            # 获取所有模型
            import asyncio
            all_models = asyncio.run(model_discovery_service.get_all_models(force_refresh=force_refresh))
            
            # 过滤特定提供商
            if provider_filter:
                filtered_models = {
                    k: v for k, v in all_models.items() 
                    if k == provider_filter
                }
                all_models = filtered_models
            
            # 转换为API响应格式
            response_data = {}
            total_models = 0
            
            for provider_type, models in all_models.items():
                model_list = []
                for model in models:
                    model_list.append({
                        'id': model.id,
                        'name': model.name,
                        'display_name': model.display_name,
                        'provider': model.provider,
                        'provider_type': model.provider_type,
                        'description': model.description,
                        'max_tokens': model.max_tokens,
                        'context_window': model.context_window,
                        'supports_streaming': model.supports_streaming,
                        'supports_functions': model.supports_functions,
                        'supports_vision': model.supports_vision,
                        'cost_per_1k_input': model.cost_per_1k_input,
                        'cost_per_1k_output': model.cost_per_1k_output,
                        'is_recommended': model.is_recommended,
                        'capabilities': model.capabilities,
                        'release_date': model.release_date
                    })
                
                response_data[provider_type] = {
                    'models': model_list,
                    'count': len(model_list)
                }
                total_models += len(model_list)
            
            return Response({
                'success': True,
                'data': response_data,
                'summary': {
                    'total_models': total_models,
                    'providers_count': len(response_data),
                    'force_refreshed': force_refresh,
                    'timestamp': timezone.now().isoformat()
                }
            })
            
        except Exception as e:
            logger.error(f'模型发现失败: {e}')
            return Response({
                'success': False,
                'error': str(e),
                'message': '模型发现过程中出现错误'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def provider_models(self, request):
        """获取特定提供商的模型列表"""
        from .services.model_discovery import model_discovery_service
        
        provider_type = request.query_params.get('provider_type')
        if not provider_type:
            return Response({
                'success': False,
                'error': 'provider_type参数是必需的'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 获取提供商实例
            provider = AIProvider.objects.filter(
                provider_type=provider_type,
                is_active=True
            ).first()
            
            if not provider:
                return Response({
                    'success': False,
                    'error': f'未找到活跃的提供商: {provider_type}'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # 获取模型列表
            from ..adapters.base import AIProviderType
            provider_enum = AIProviderType(provider_type)
            force_refresh = request.query_params.get('force_refresh', 'false').lower() == 'true'
            
            import asyncio
            models = asyncio.run(model_discovery_service.get_provider_models(
                provider_enum, provider, force_refresh
            ))
            
            # 转换为响应格式
            model_list = []
            for model in models:
                model_list.append({
                    'id': model.id,
                    'name': model.name,
                    'display_name': model.display_name,
                    'provider': model.provider,
                    'provider_type': model.provider_type,
                    'description': model.description,
                    'max_tokens': model.max_tokens,
                    'context_window': model.context_window,
                    'supports_streaming': model.supports_streaming,
                    'supports_functions': model.supports_functions,
                    'supports_vision': model.supports_vision,
                    'cost_per_1k_input': model.cost_per_1k_input,
                    'cost_per_1k_output': model.cost_per_1k_output,
                    'is_recommended': model.is_recommended,
                    'capabilities': model.capabilities
                })
            
            return Response({
                'success': True,
                'provider_type': provider_type,
                'provider_name': provider.display_name,
                'models': model_list,
                'count': len(model_list),
                'force_refreshed': force_refresh,
                'timestamp': timezone.now().isoformat()
            })
            
        except ValueError as e:
            return Response({
                'success': False,
                'error': f'不支持的提供商类型: {provider_type}'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f'获取提供商模型失败: {e}')
            return Response({
                'success': False,
                'error': str(e),
                'message': '获取模型列表时出现错误'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def sync_to_database(self, request):
        """同步模型到数据库"""
        from .services.model_discovery import model_discovery_service
        
        # 检查权限
        if not request.user.is_staff:
            return Response({
                'success': False,
                'error': '需要管理员权限'
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            force_refresh = request.data.get('force_refresh', False)
            import asyncio
            stats = asyncio.run(model_discovery_service.sync_models_to_database(force_refresh))
            
            return Response({
                'success': True,
                'message': '模型同步完成',
                'stats': stats,
                'timestamp': timezone.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f'模型同步失败: {e}')
            return Response({
                'success': False,
                'error': str(e),
                'message': '模型同步过程中出现错误'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def clear_cache(self, request):
        """清除模型发现缓存"""
        from .services.model_discovery import model_discovery_service
        
        try:
            provider_type = request.data.get('provider_type')
            import asyncio
            asyncio.run(model_discovery_service.clear_cache(provider_type))
            
            message = f'已清除{"所有" if not provider_type else provider_type}模型缓存'
            
            return Response({
                'success': True,
                'message': message,
                'timestamp': timezone.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f'清除缓存失败: {e}')
            return Response({
                'success': False,
                'error': str(e),
                'message': '清除缓存时出现错误'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def supported_providers(self, request):
        """获取支持的提供商列表"""
        from ..adapters.base import AIProviderType
        
        providers = []
        for provider_type in AIProviderType:
            # 获取数据库中的提供商信息
            provider = AIProvider.objects.filter(
                provider_type=provider_type.value,
                is_active=True
            ).first()
            
            providers.append({
                'type': provider_type.value,
                'name': provider_type.name,
                'display_name': provider.display_name if provider else provider_type.value.title(),
                'is_active': bool(provider),
                'has_api_endpoint': provider_type in [
                    AIProviderType.OPENAI, 
                    AIProviderType.OPENROUTER
                ],
                'description': provider.description if provider else f'{provider_type.value.title()} AI提供商'
            })
        
        return Response({
            'success': True,
            'providers': providers,
            'count': len(providers),
            'active_count': sum(1 for p in providers if p['is_active'])
        })
    
    @action(detail=False, methods=['get'])
    def model_stats(self, request):
        """获取模型统计信息"""
        try:
            # 从数据库获取统计
            total_models = AIModel.objects.filter(is_active=True).count()
            recommended_models = AIModel.objects.filter(is_active=True, is_recommended=True).count()
            
            # 按提供商分组统计
            provider_stats = AIModel.objects.filter(is_active=True).values(
                'provider__provider_type',
                'provider__display_name'
            ).annotate(
                model_count=Count('id'),
                recommended_count=Count('id', filter=models.Q(is_recommended=True))
            ).order_by('-model_count')
            
            # 按功能统计
            streaming_models = AIModel.objects.filter(is_active=True, supports_streaming=True).count()
            function_models = AIModel.objects.filter(is_active=True, supports_functions=True).count()
            vision_models = AIModel.objects.filter(is_active=True, supports_vision=True).count()
            
            return Response({
                'success': True,
                'stats': {
                    'total_models': total_models,
                    'recommended_models': recommended_models,
                    'streaming_models': streaming_models,
                    'function_models': function_models,
                    'vision_models': vision_models
                },
                'provider_stats': list(provider_stats),
                'timestamp': timezone.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f'获取模型统计失败: {e}')
            return Response({
                'success': False,
                'error': str(e),
                'message': '获取统计信息时出现错误'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MonitoringViewSet(viewsets.ViewSet):
    """监控ViewSet"""
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def overview(self, request):
        """获取系统监控概览"""
        from .services.monitoring_service import monitoring_service
        
        try:
            overview = monitoring_service.get_system_overview()
            return Response(overview)
            
        except Exception as e:
            logger.error(f"获取监控概览失败: {e}")
            return Response(
                {'error': f'获取监控概览失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def services(self, request):
        """获取所有服务状态"""
        from .services.monitoring_service import monitoring_service
        
        try:
            services = monitoring_service.get_all_services_status()
            return Response({
                'services': [service.to_dict() for service in services],
                'total_services': len(services),
                'timestamp': timezone.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"获取服务状态失败: {e}")
            return Response(
                {'error': f'获取服务状态失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def service_status(self, request, pk=None):
        """获取特定服务状态"""
        from .services.monitoring_service import monitoring_service
        
        service_name = pk
        if not service_name:
            return Response(
                {'error': '服务名称不能为空'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            service_status = monitoring_service.get_service_status(service_name)
            if not service_status:
                return Response(
                    {'error': f'服务 {service_name} 未找到'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response(service_status.to_dict())
            
        except Exception as e:
            logger.error(f"获取服务 {service_name} 状态失败: {e}")
            return Response(
                {'error': f'获取服务状态失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def service_history(self, request, pk=None):
        """获取服务指标历史"""
        from .services.monitoring_service import monitoring_service
        
        service_name = pk
        if not service_name:
            return Response(
                {'error': '服务名称不能为空'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 获取时间范围参数
        hours = int(request.query_params.get('hours', 24))
        if hours <= 0 or hours > 168:  # 最多7天
            hours = 24
        
        try:
            history = monitoring_service.get_service_metrics_history(service_name, hours)
            return Response({
                'service_name': service_name,
                'hours': hours,
                'history': history,
                'count': len(history)
            })
            
        except Exception as e:
            logger.error(f"获取服务 {service_name} 历史失败: {e}")
            return Response(
                {'error': f'获取服务历史失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def alerts(self, request):
        """获取活跃告警"""
        from .services.monitoring_service import monitoring_service
        
        try:
            alerts = monitoring_service.get_active_alerts()
            return Response({
                'alerts': alerts,
                'total_alerts': len(alerts),
                'timestamp': timezone.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"获取告警失败: {e}")
            return Response(
                {'error': f'获取告警失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def health_check(self, request):
        """强制健康检查"""
        from .services.monitoring_service import monitoring_service
        
        service_name = request.data.get('service_name')
        
        try:
            result = monitoring_service.force_health_check(service_name)
            return Response({
                'message': '健康检查完成',
                'result': result,
                'timestamp': timezone.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"强制健康检查失败: {e}")
            return Response(
                {'error': f'健康检查失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def cleanup_data(self, request):
        """清理旧监控数据"""
        from .services.monitoring_service import monitoring_service
        
        # 检查管理员权限
        if not request.user.is_staff:
            return Response(
                {'error': '需要管理员权限'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        days = int(request.data.get('days', 7))
        if days <= 0 or days > 30:
            days = 7
        
        try:
            result = monitoring_service.cleanup_old_data(days)
            return Response({
                'message': f'数据清理完成，清理 {days} 天前的数据',
                'result': result,
                'timestamp': timezone.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"数据清理失败: {e}")
            return Response(
                {'error': f'数据清理失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def metrics_summary(self, request):
        """获取指标摘要"""
        from .services.monitoring_service import monitoring_service
        from ..monitoring_models import ServiceHealthRecord, SystemAlert
        
        # 获取时间范围参数
        hours = int(request.query_params.get('hours', 24))
        if hours <= 0 or hours > 168:  # 最多7天
            hours = 24
        
        try:
            cutoff_time = timezone.now() - timedelta(hours=hours)
            
            # 基础统计
            total_checks = ServiceHealthRecord.objects.filter(
                check_timestamp__gte=cutoff_time
            ).count()
            
            healthy_checks = ServiceHealthRecord.objects.filter(
                check_timestamp__gte=cutoff_time,
                is_healthy=True
            ).count()
            
            # 活跃告警
            active_alerts = SystemAlert.get_active_alerts().count()
            critical_alerts = SystemAlert.get_active_alerts().filter(
                level=SystemAlert.AlertLevel.CRITICAL
            ).count()
            
            # 服务状态分布
            services = monitoring_service.get_all_services_status()
            healthy_services = sum(1 for s in services if s.is_healthy)
            
            summary = {
                'period_hours': hours,
                'timestamp': timezone.now().isoformat(),
                'health_checks': {
                    'total': total_checks,
                    'healthy': healthy_checks,
                    'unhealthy': total_checks - healthy_checks,
                    'health_rate': round((healthy_checks / total_checks * 100) if total_checks > 0 else 0, 2)
                },
                'services': {
                    'total': len(services),
                    'healthy': healthy_services,
                    'unhealthy': len(services) - healthy_services
                },
                'alerts': {
                    'active': active_alerts,
                    'critical': critical_alerts
                }
            }
            
            return Response(summary)
            
        except Exception as e:
            logger.error(f"获取指标摘要失败: {e}")
            return Response(
                {'error': f'获取指标摘要失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TokenStatisticsViewSet(viewsets.ViewSet):
    """Token统计ViewSet"""
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def realtime(self, request):
        """获取实时Token统计（当日）"""
        from .services.token_statistics import token_statistics_service
        
        try:
            # 获取查询参数
            provider_id = request.query_params.get('provider')
            model_id = request.query_params.get('model')
            
            # 获取过滤对象
            provider = None
            model = None
            
            if provider_id:
                try:
                    provider = AIProvider.objects.get(id=provider_id, is_active=True)
                except AIProvider.DoesNotExist:
                    return Response(
                        {'error': f'提供商 {provider_id} 不存在或未激活'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            if model_id:
                try:
                    model = AIModel.objects.get(id=model_id, is_active=True)
                except AIModel.DoesNotExist:
                    return Response(
                        {'error': f'模型 {model_id} 不存在或未激活'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # 获取实时统计
            stats = token_statistics_service.get_realtime_statistics(
                user=request.user,
                provider=provider,
                model=model
            )
            
            return Response({
                'success': True,
                'data': stats.to_dict(),
                'timestamp': timezone.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"获取实时Token统计失败: {e}")
            return Response(
                {'error': f'获取实时统计失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def historical(self, request):
        """获取历史Token统计"""
        from .services.token_statistics import token_statistics_service
        
        try:
            # 获取查询参数
            period = request.query_params.get('period', 'day')
            days = int(request.query_params.get('days', 30))
            provider_id = request.query_params.get('provider')
            model_id = request.query_params.get('model')
            
            # 参数验证
            if period not in ['hour', 'day', 'week', 'month']:
                period = 'day'
            
            if days <= 0 or days > 365:
                days = 30
            
            # 获取过滤对象
            provider = None
            model = None
            
            if provider_id:
                try:
                    provider = AIProvider.objects.get(id=provider_id, is_active=True)
                except AIProvider.DoesNotExist:
                    return Response(
                        {'error': f'提供商 {provider_id} 不存在或未激活'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            if model_id:
                try:
                    model = AIModel.objects.get(id=model_id, is_active=True)
                except AIModel.DoesNotExist:
                    return Response(
                        {'error': f'模型 {model_id} 不存在或未激活'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # 获取历史统计
            stats = token_statistics_service.get_historical_statistics(
                period=period,
                days=days,
                user=request.user,
                provider=provider,
                model=model
            )
            
            return Response({
                'success': True,
                'data': [stat.to_dict() for stat in stats],
                'period': period,
                'days': days,
                'count': len(stats),
                'timestamp': timezone.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"获取历史Token统计失败: {e}")
            return Response(
                {'error': f'获取历史统计失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def providers(self, request):
        """获取按提供商分组的统计"""
        from .services.token_statistics import token_statistics_service
        
        try:
            days = int(request.query_params.get('days', 30))
            if days <= 0 or days > 365:
                days = 30
            
            # 获取提供商统计
            stats = token_statistics_service.get_provider_statistics(
                user=request.user,
                days=days
            )
            
            return Response({
                'success': True,
                'data': [stat.to_dict() for stat in stats],
                'days': days,
                'count': len(stats),
                'timestamp': timezone.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"获取提供商统计失败: {e}")
            return Response(
                {'error': f'获取提供商统计失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def models(self, request):
        """获取按模型分组的统计"""
        from .services.token_statistics import token_statistics_service
        
        try:
            days = int(request.query_params.get('days', 30))
            provider_id = request.query_params.get('provider')
            
            if days <= 0 or days > 365:
                days = 30
            
            # 获取过滤对象
            provider = None
            if provider_id:
                try:
                    provider = AIProvider.objects.get(id=provider_id, is_active=True)
                except AIProvider.DoesNotExist:
                    return Response(
                        {'error': f'提供商 {provider_id} 不存在或未激活'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # 获取模型统计
            stats = token_statistics_service.get_model_statistics(
                user=request.user,
                provider=provider,
                days=days
            )
            
            return Response({
                'success': True,
                'data': [stat.to_dict() for stat in stats],
                'days': days,
                'provider_filter': provider.display_name if provider else None,
                'count': len(stats),
                'timestamp': timezone.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"获取模型统计失败: {e}")
            return Response(
                {'error': f'获取模型统计失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """获取用户使用摘要"""
        from .services.token_statistics import token_statistics_service
        
        try:
            days = int(request.query_params.get('days', 30))
            if days <= 0 or days > 365:
                days = 30
            
            # 获取用户摘要
            summary = token_statistics_service.get_user_summary(
                user=request.user,
                days=days
            )
            
            return Response({
                'success': True,
                'data': summary,
                'timestamp': timezone.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"获取用户摘要失败: {e}")
            return Response(
                {'error': f'获取用户摘要失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def budget_status(self, request):
        """获取预算使用状态"""
        from .services.token_statistics import token_statistics_service
        
        try:
            # 检查用户的预算告警
            alerts = token_statistics_service.check_budget_alerts()
            user_alerts = [alert for alert in alerts if alert.user_id == request.user.id]
            
            # 获取用户配额设置
            from .config_models import UsageQuota
            user_quotas = UsageQuota.objects.filter(
                user=request.user,
                is_active=True
            ).values(
                'period_type', 'cost_limit', 'token_limit'
            )
            
            # 获取当前使用情况
            today_stats = token_statistics_service.get_realtime_statistics(user=request.user)
            
            return Response({
                'success': True,
                'data': {
                    'user_id': request.user.id,
                    'username': request.user.username,
                    'quotas': list(user_quotas),
                    'alerts': [alert.to_dict() for alert in user_alerts],
                    'today_usage': {
                        'requests': today_stats.total_requests,
                        'tokens': today_stats.total_tokens,
                        'cost': float(today_stats.total_cost)
                    }
                },
                'timestamp': timezone.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"获取预算状态失败: {e}")
            return Response(
                {'error': f'获取预算状态失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def record_usage(self, request):
        """记录Token使用（内部API）"""
        # 检查权限（仅限系统内部调用）
        if not request.user.is_staff:
            return Response(
                {'error': '仅限内部使用'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            data = request.data
            required_fields = [
                'provider_id', 'model_id', 'api_key_id',
                'input_tokens', 'output_tokens', 'input_cost', 'output_cost'
            ]
            
            # 验证必需字段
            for field in required_fields:
                if field not in data:
                    return Response(
                        {'error': f'缺少必需字段: {field}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # 创建Token使用记录
            usage = TokenUsage.objects.create(
                user=request.user,
                provider_id=data['provider_id'],
                model_id=data['model_id'],
                api_key_id=data['api_key_id'],
                request_id=data.get('request_id', ''),
                conversation_id=data.get('conversation_id', ''),
                input_tokens=int(data['input_tokens']),
                output_tokens=int(data['output_tokens']),
                input_cost=Decimal(str(data['input_cost'])),
                output_cost=Decimal(str(data['output_cost'])),
                response_time=float(data.get('response_time', 0.0)),
                is_streaming=data.get('is_streaming', False),
                status=data.get('status', 'success'),
                error_message=data.get('error_message', '')
            )
            
            return Response({
                'success': True,
                'data': {
                    'usage_id': usage.id,
                    'total_tokens': usage.total_tokens,
                    'total_cost': float(usage.total_cost)
                },
                'timestamp': timezone.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"记录Token使用失败: {e}")
            return Response(
                {'error': f'记录使用失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def export(self, request):
        """导出Token使用数据"""
        try:
            # 获取查询参数
            days = int(request.query_params.get('days', 30))
            format_type = request.query_params.get('format', 'json')
            
            if days <= 0 or days > 365:
                days = 30
            
            # 时间范围
            end_time = timezone.now()
            start_time = end_time - timedelta(days=days)
            
            # 获取用户的使用记录
            usage_records = TokenUsage.objects.filter(
                user=request.user,
                created_at__gte=start_time,
                created_at__lte=end_time
            ).select_related('provider', 'model', 'api_key').order_by('-created_at')
            
            # 构建导出数据
            export_data = []
            for record in usage_records:
                export_data.append({
                    'timestamp': record.created_at.isoformat(),
                    'provider': record.provider.display_name,
                    'model': record.model.display_name,
                    'request_id': record.request_id,
                    'conversation_id': record.conversation_id,
                    'input_tokens': record.input_tokens,
                    'output_tokens': record.output_tokens,
                    'total_tokens': record.total_tokens,
                    'input_cost': float(record.input_cost),
                    'output_cost': float(record.output_cost),
                    'total_cost': float(record.total_cost),
                    'response_time': record.response_time,
                    'status': record.status,
                    'error_message': record.error_message
                })
            
            if format_type == 'csv':
                # 返回CSV格式
                import csv
                import io
                
                output = io.StringIO()
                writer = csv.DictWriter(output, fieldnames=export_data[0].keys() if export_data else [])
                writer.writeheader()
                writer.writerows(export_data)
                
                response = Response(
                    output.getvalue(),
                    content_type='text/csv',
                    status=status.HTTP_200_OK
                )
                response['Content-Disposition'] = f'attachment; filename="token_usage_{request.user.username}_{days}days.csv"'
                return response
            else:
                # 返回JSON格式
                return Response({
                    'success': True,
                    'data': export_data,
                    'count': len(export_data),
                    'period_days': days,
                    'period_start': start_time.isoformat(),
                    'period_end': end_time.isoformat(),
                    'timestamp': timezone.now().isoformat()
                })
            
        except Exception as e:
            logger.error(f"导出Token使用数据失败: {e}")
            return Response(
                {'error': f'导出数据失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )