"""
AI配置管理API视图
"""

import logging
import sys
from datetime import datetime, timedelta
from decimal import Decimal
from django.conf import settings

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.utils import timezone
from django.http import HttpResponse
import json
import yaml
from django.utils.decorators import method_decorator
from django.db.models import Count, Sum, Avg, Q
from django.db import transaction
from apps.rbac.permissions import RBACPermission, CanManageAIConfig
from apps.rbac.services import AuditService
from apps.common.ratelimit import ai_config_limit, ai_test_limit, sensitive_limit
from apps.common.security import DatabaseSecurityMixin
from apps.common.ssl_config import APIKeySecurityManager

from .config_models import (
    AIProvider, APIKey, AIModel, PromptTemplate, ModelConfig, TokenUsage,
    FailoverStrategy, FailoverRule, UsageQuota, ConfigTemplate, ConfigVersion,
    UserSettings, SystemConfig, LoginHistory, DeviceSession
)
from .serializers import (
    AIProviderSerializer, APIKeySerializer, APIKeyCreateSerializer,
    AIModelSerializer, PromptTemplateSerializer, ModelConfigSerializer, TokenUsageSerializer,
    FailoverStrategySerializer, FailoverRuleSerializer, UsageQuotaSerializer,
    ConfigExportSerializer, ConfigImportSerializer, ConfigTemplateSerializer, ConfigVersionSerializer,
    UserSettingsSerializer, SystemConfigSerializer, LoginHistorySerializer, DeviceSessionSerializer,
    UserProfileSerializer, PasswordChangeSerializer
)
from .adapters.factory import AIAdapterFactory

logger = logging.getLogger(__name__)


class AIProviderViewSet(DatabaseSecurityMixin, viewsets.ModelViewSet):
    """AI提供商管理ViewSet"""
    
    queryset = AIProvider.objects.all()
    serializer_class = AIProviderSerializer
    permission_classes = [IsAuthenticated]
    
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
                'base_url': provider.base_url
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
            
            # 创建适配器配置
            from apps.ai.adapters.base import AIModelConfig
            
            config = AIModelConfig(
                provider=provider.provider_type,
                model_name='test-model',  # 用于测试的模型名称
                api_key=api_key.get_key(),
                base_url=provider.base_url
            )
            
            # 创建适配器并测试连接
            adapter = AIAdapterFactory.create_adapter(config)
            
            # 执行健康检查（异步调用）
            import asyncio
            
            # 在同步环境中调用异步方法
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                health_result = loop.run_until_complete(adapter.health_check())
            finally:
                loop.close()
            
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
                
                # 创建适配器配置
                from apps.ai.adapters.base import AIModelConfig
                
                config = AIModelConfig(
                    provider=provider.provider_type,
                    model_name='test-model',  # 用于测试的模型名称
                    api_key=api_key.get_key(),
                    base_url=provider.base_url
                )
                
                # 创建适配器并测试连接
                adapter = AIAdapterFactory.create_adapter(config)
                
                # 执行健康检查（异步调用）
                import asyncio
                
                # 在同步环境中调用异步方法
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    health_result = loop.run_until_complete(adapter.health_check())
                finally:
                    loop.close()
                
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


class APIKeyViewSet(DatabaseSecurityMixin, viewsets.ModelViewSet):
    """API密钥管理ViewSet"""
    
    queryset = APIKey.objects.all()
    permission_classes = [IsAuthenticated]
    
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
        # 验证API密钥传输安全性（在测试环境中跳过）
        # 检查是否在测试环境中
        is_testing = (
            getattr(settings, 'TESTING', False) or 
            getattr(settings, 'DEBUG', False) or
            'test' in sys.argv or
            'pytest' in sys.argv[0] if sys.argv else False
        )
        
        if not is_testing:
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
        
        return queryset.select_related('model', 'provider').order_by('-created_at')
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """获取使用统计摘要"""
        queryset = self.get_queryset()
        
        # 聚合统计
        stats = queryset.aggregate(
            total_tokens=Sum('total_tokens'),
            total_cost=Sum('total_cost'),
            total_requests=Count('id')
        )
        
        # 计算平均Token数
        if stats['total_requests'] > 0:
            avg_tokens = stats['total_tokens'] / stats['total_requests']
        else:
            avg_tokens = 0
        
        # 按模型分组统计
        model_stats = queryset.values(
            'model__display_name',
            'provider__display_name'
        ).annotate(
            tokens=Sum('total_tokens'),
            cost=Sum('total_cost'),
            requests=Count('id')
        ).order_by('-cost')
        
        return Response({
            'summary': {
                'total_tokens': stats['total_tokens'] or 0,
                'total_cost': float(stats['total_cost'] or 0),
                'total_requests': stats['total_requests'] or 0,
                'avg_tokens_per_request': float(avg_tokens)
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
            cost=Sum('total_cost'),
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
                recommended_count=Count('id', filter=Q(is_recommended=True))
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


@method_decorator(ai_config_limit, name='dispatch')
class PromptTemplateViewSet(DatabaseSecurityMixin, viewsets.ModelViewSet):
    """系统提示模板管理ViewSet"""
    
    serializer_class = PromptTemplateSerializer
    permission_classes = [RBACPermission]
    
    # RBAC权限配置
    resource_type = 'ai_config'
    
    def get_permissions(self):
        """根据操作类型返回不同权限"""
        if self.action in ['list', 'retrieve']:
            return [RBACPermission('ai_config.view')]
        elif self.action in ['create']:
            return [RBACPermission('ai_config.create')]
        elif self.action in ['update', 'partial_update']:
            return [RBACPermission('ai_config.edit')]
        elif self.action in ['destroy']:
            return [RBACPermission('ai_config.delete')]
        else:
            return [RBACPermission('ai_config.manage')]
    
    def get_queryset(self):
        """获取用户可访问的模板"""
        user = self.request.user
        
        # 用户可以看到：自己创建的模板、公共模板、系统模板
        from django.db import models as django_models
        return PromptTemplate.objects.filter(
            django_models.Q(created_by=user) | 
            django_models.Q(is_public=True) | 
            django_models.Q(is_system=True)
        ).filter(is_active=True).order_by('-is_system', '-usage_count', 'name')
    
    def perform_create(self, serializer):
        """创建模板时记录审计日志"""
        template = serializer.save(created_by=self.request.user)
        
        AuditService.log_user_action(
            user=self.request.user,
            action='create_prompt_template',
            resource_type='prompt_template',
            resource_id=str(template.id),
            details=f"创建提示模板: {template.name}"
        )
    
    def perform_update(self, serializer):
        """更新模板时记录审计日志"""
        template = serializer.save()
        
        AuditService.log_user_action(
            user=self.request.user,
            action='update_prompt_template',
            resource_type='prompt_template',
            resource_id=str(template.id),
            details=f"更新提示模板: {template.name}"
        )
    
    def perform_destroy(self, instance):
        """删除模板时记录审计日志"""
        AuditService.log_user_action(
            user=self.request.user,
            action='delete_prompt_template',
            resource_type='prompt_template',
            resource_id=str(instance.id),
            details=f"删除提示模板: {instance.name}"
        )
        
        # 软删除：设置为非活跃状态
        instance.is_active = False
        instance.save()
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """获取模板分类列表"""
        try:
            categories = []
            for choice in PromptTemplate._meta.get_field('category').choices:
                categories.append({
                    'value': choice[0],
                    'label': choice[1]
                })
            
            return Response({
                'success': True,
                'data': categories
            })
            
        except Exception as e:
            logger.error(f"获取模板分类失败: {e}")
            return Response(
                {'error': f'获取分类失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(ai_config_limit, name='dispatch')
class ModelConfigViewSet(DatabaseSecurityMixin, viewsets.ModelViewSet):
    """模型配置管理ViewSet"""
    
    serializer_class = ModelConfigSerializer
    permission_classes = [RBACPermission]
    
    # RBAC权限配置
    resource_type = 'ai_config'
    
    def get_permissions(self):
        """根据操作类型返回不同权限"""
        if self.action in ['list', 'retrieve']:
            return [RBACPermission('ai_config.view')]
        elif self.action in ['create']:
            return [RBACPermission('ai_config.create')]
        elif self.action in ['update', 'partial_update']:
            return [RBACPermission('ai_config.edit')]
        elif self.action in ['destroy']:
            return [RBACPermission('ai_config.delete')]
        else:
            return [RBACPermission('ai_config.manage')]
    
    def get_queryset(self):
        """获取用户的模型配置"""
        return ModelConfig.objects.filter(
            user=self.request.user,
            is_active=True
        ).select_related(
            'provider', 'prompt_template'
        ).order_by('-is_default', '-last_used', '-created_at')
    
    def perform_create(self, serializer):
        """创建配置时记录审计日志"""
        config = serializer.save(user=self.request.user)
        
        AuditService.log_user_action(
            user=self.request.user,
            action='create_model_config',
            resource_type='model_config',
            resource_id=str(config.id),
            details=f"创建模型配置: {config.config_name}"
        )
    
    def perform_update(self, serializer):
        """更新配置时记录审计日志和使用时间"""
        config = serializer.save(last_used=timezone.now())
        
        AuditService.log_user_action(
            user=self.request.user,
            action='update_model_config',
            resource_type='model_config',
            resource_id=str(config.id),
            details=f"更新模型配置: {config.config_name}"
        )
    
    def perform_destroy(self, instance):
        """删除配置时记录审计日志"""
        AuditService.log_user_action(
            user=self.request.user,
            action='delete_model_config',
            resource_type='model_config',
            resource_id=str(instance.id),
            details=f"删除模型配置: {instance.config_name}"
        )
        
        # 软删除：设置为非活跃状态
        instance.is_active = False
        instance.save()
    
    @action(detail=False, methods=['get'])
    def models_metadata(self, request):
        """获取模型元数据（用于前端限制最大Token）"""
        try:
            provider_id = request.query_params.get('provider_id')
            if not provider_id:
                return Response(
                    {'error': 'provider_id参数是必需的'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 获取指定提供商的模型列表
            models = AIModel.objects.filter(
                provider_id=provider_id,
                is_active=True
            ).values('model_id', 'display_name', 'max_tokens')
            
            models_data = []
            for model in models:
                models_data.append({
                    'name': model['model_id'],
                    'display_name': model['display_name'],
                    'context_window': model['max_tokens'] or 4096
                })
            
            return Response({
                'success': True,
                'data': models_data
            })
            
        except Exception as e:
            logger.error(f"获取模型元数据失败: {e}")
            return Response(
                {'error': f'获取模型元数据失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """设置为默认配置"""
        try:
            config = self.get_object()
            
            # 取消用户的其他默认配置
            ModelConfig.objects.filter(
                user=request.user,
                provider=config.provider,
                model=config.model,
                is_default=True
            ).update(is_default=False)
            
            # 设置当前配置为默认
            config.is_default = True
            config.save()
            
            AuditService.log_user_action(
                user=request.user,
                action='set_default_model_config',
                resource_type='model_config',
                resource_id=str(config.id),
                details=f"设置默认配置: {config.config_name}"
            )
            
            return Response({
                'success': True,
                'message': '已设置为默认配置'
            })
            
        except Exception as e:
            logger.error(f"设置默认配置失败: {e}")
            return Response(
                {'error': f'设置默认配置失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """复制配置"""
        try:
            original_config = self.get_object()
            
            # 创建副本
            new_config = ModelConfig.objects.create(
                user=request.user,
                provider=original_config.provider,
                model=original_config.model,
                config_name=f"{original_config.config_name} (副本)",
                temperature=original_config.temperature,
                max_tokens=original_config.max_tokens,
                top_p=original_config.top_p,
                frequency_penalty=original_config.frequency_penalty,
                presence_penalty=original_config.presence_penalty,
                prompt_template=original_config.prompt_template,
                system_prompt_template=original_config.system_prompt_template,
                advanced_params=original_config.advanced_params,
                is_default=False,
                is_active=True
            )
            
            AuditService.log_user_action(
                user=request.user,
                action='duplicate_model_config',
                resource_type='model_config',
                resource_id=str(new_config.id),
                details=f"复制配置: {original_config.config_name} -> {new_config.config_name}"
            )
            
            serializer = self.get_serializer(new_config)
            return Response({
                'success': True,
                'data': serializer.data,
                'message': '配置复制成功'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"复制配置失败: {e}")
            return Response(
                {'error': f'复制配置失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ConfigExportView(APIView):
    """配置导出视图"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """导出配置"""
        try:
            format_type = request.GET.get('format', 'json')
            
            # 获取所有配置数据
            providers = AIProvider.objects.all()
            strategies = FailoverStrategy.objects.all()
            
            # 构建导出数据
            export_data = {
                'providers': AIProviderSerializer(providers, many=True).data,
                'strategies': FailoverStrategySerializer(strategies, many=True).data,
                'settings': self._get_system_settings(),
                'version': '1.0.0',
                'export_time': datetime.now().isoformat(),
                'metadata': {
                    'total_providers': providers.count(),
                    'total_strategies': strategies.count(),
                    'export_format': format_type
                }
            }
            
            # 创建版本记录
            ConfigVersion.objects.create(
                config_data=export_data,
                version_name=f"Export_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                description=f"配置导出 - {format_type.upper()}格式",
                created_by=request.user
            )
            
            # 根据格式返回响应
            if format_type == 'yaml':
                yaml_content = yaml.dump(export_data, default_flow_style=False, allow_unicode=True)
                response = HttpResponse(yaml_content, content_type='application/x-yaml')
                response['Content-Disposition'] = f'attachment; filename="ai_config_{datetime.now().strftime("%Y%m%d_%H%M%S")}.yaml"'
            else:
                json_content = json.dumps(export_data, ensure_ascii=False, indent=2)
                response = HttpResponse(json_content, content_type='application/json')
                response['Content-Disposition'] = f'attachment; filename="ai_config_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"'
            
            return response
            
        except Exception as e:
            return Response(
                {'error': f'导出失败：{str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _get_system_settings(self):
        """获取系统设置"""
        return {
            'default_timeout': 30,
            'max_retries': 3,
            'health_check_interval': 60,
            'log_level': 'INFO'
        }


class ConfigImportView(APIView):
    """配置导入视图"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """导入配置"""
        try:
            serializer = ConfigImportSerializer(data=request.data, context={'request': request})
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            config_data = serializer.validated_data['parsed_config']
            validate_only = serializer.validated_data.get('validate_only', False)
            overwrite_existing = serializer.validated_data.get('overwrite_existing', False)
            
            if validate_only:
                # 仅验证，不导入
                return Response({
                    'message': '配置验证通过',
                    'config_summary': {
                        'providers_count': len(config_data.get('providers', [])),
                        'strategies_count': len(config_data.get('strategies', [])),
                        'version': config_data.get('version', 'unknown')
                    }
                })
            
            # 执行导入
            import_result = self._import_config(config_data, overwrite_existing, request.user)
            
            return Response({
                'message': '配置导入成功',
                'import_result': import_result
            })
            
        except Exception as e:
            return Response(
                {'error': f'导入失败：{str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _import_config(self, config_data, overwrite_existing, user):
        """执行配置导入"""
        result = {
            'providers_imported': 0,
            'strategies_imported': 0,
            'providers_updated': 0,
            'strategies_updated': 0,
            'errors': []
        }
        
        # 导入提供商配置
        if 'providers' in config_data:
            for provider_data in config_data['providers']:
                try:
                    provider_name = provider_data.get('name')
                    existing_provider = AIProvider.objects.filter(name=provider_name).first()
                    
                    if existing_provider and not overwrite_existing:
                        result['errors'].append(f"提供商 {provider_name} 已存在，跳过导入")
                        continue
                    
                    if existing_provider:
                        # 更新现有提供商
                        for field, value in provider_data.items():
                            if hasattr(existing_provider, field):
                                setattr(existing_provider, field, value)
                        existing_provider.save()
                        result['providers_updated'] += 1
                    else:
                        # 创建新提供商
                        AIProvider.objects.create(**provider_data)
                        result['providers_imported'] += 1
                        
                except Exception as e:
                    result['errors'].append(f"导入提供商 {provider_name} 失败：{str(e)}")
        
        # 导入策略配置
        if 'strategies' in config_data:
            for strategy_data in config_data['strategies']:
                try:
                    strategy_name = strategy_data.get('name')
                    existing_strategy = FailoverStrategy.objects.filter(name=strategy_name).first()
                    
                    if existing_strategy and not overwrite_existing:
                        result['errors'].append(f"策略 {strategy_name} 已存在，跳过导入")
                        continue
                    
                    if existing_strategy:
                        # 更新现有策略
                        for field, value in strategy_data.items():
                            if hasattr(existing_strategy, field):
                                setattr(existing_strategy, field, value)
                        existing_strategy.save()
                        result['strategies_updated'] += 1
                    else:
                        # 创建新策略
                        FailoverStrategy.objects.create(**strategy_data)
                        result['strategies_imported'] += 1
                        
                except Exception as e:
                    result['errors'].append(f"导入策略 {strategy_name} 失败：{str(e)}")
        
        # 创建导入版本记录
        ConfigVersion.objects.create(
            config_data=config_data,
            version_name=f"Import_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            description=f"配置导入 - 提供商:{result['providers_imported']} 策略:{result['strategies_imported']}",
            created_by=user
        )
        
        return result


class ConfigTemplateViewSet(viewsets.ModelViewSet):
    """配置模板视图集"""
    queryset = ConfigTemplate.objects.all()
    serializer_class = ConfigTemplateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """过滤查询集"""
        queryset = super().get_queryset()
        
        # 按创建者过滤
        if not self.request.user.is_superuser:
            queryset = queryset.filter(created_by=self.request.user)
        
        # 按标签过滤
        tag = self.request.query_params.get('tag')
        if tag:
            queryset = queryset.filter(tags__contains=tag)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """创建模板"""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def apply(self, request, pk=None):
        """应用模板"""
        try:
            template = self.get_object()
            config_data = template.config_data
            
            # 执行导入
            import_result = ConfigImportView()._import_config(
                config_data,
                overwrite_existing=True,
                user=request.user
            )
            
            return Response({
                'message': f'模板 {template.name} 应用成功',
                'import_result': import_result
            })
            
        except Exception as e:
            return Response(
                {'error': f'应用模板失败：{str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ConfigVersionViewSet(viewsets.ReadOnlyModelViewSet):
    """配置版本视图集"""
    queryset = ConfigVersion.objects.all()
    serializer_class = ConfigVersionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """过滤查询集"""
        queryset = super().get_queryset()
        
        # 按创建者过滤
        if not self.request.user.is_superuser:
            queryset = queryset.filter(created_by=self.request.user)
        
        return queryset.order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def rollback(self, request, pk=None):
        """回滚到指定版本"""
        try:
            version = self.get_object()
            config_data = version.config_data
            
            # 执行回滚
            rollback_result = ConfigImportView()._import_config(
                config_data,
                overwrite_existing=True,
                user=request.user
            )
            
            # 创建回滚记录
            ConfigVersion.objects.create(
                config_data=config_data,
                version_name=f"Rollback_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                description=f"回滚到版本 {version.version_name}",
                created_by=request.user
            )
            
            return Response({
                'message': f'回滚到版本 {version.version_name} 成功',
                'rollback_result': rollback_result
            })
            
        except Exception as e:
            return Response(
                {'error': f'回滚失败：{str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserSettingsViewSet(viewsets.ModelViewSet):
    """用户设置视图集"""
    serializer_class = UserSettingsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """获取当前用户的设置"""
        return UserSettings.objects.filter(user=self.request.user)
    
    def get_object(self):
        """获取或创建用户设置"""
        settings, created = UserSettings.objects.get_or_create(user=self.request.user)
        return settings
    
    @action(detail=False, methods=['get', 'put', 'patch'])
    def my_settings(self, request):
        """获取或更新当前用户的设置"""
        settings, created = UserSettings.objects.get_or_create(user=request.user)
        
        if request.method == 'GET':
            serializer = self.get_serializer(settings)
            return Response(serializer.data)
        
        elif request.method in ['PUT', 'PATCH']:
            serializer = self.get_serializer(settings, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SystemConfigViewSet(viewsets.ModelViewSet):
    """系统配置视图集"""
    queryset = SystemConfig.objects.all()
    serializer_class = SystemConfigSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """根据权限过滤配置"""
        if self.request.user.is_staff:
            return SystemConfig.objects.all()
        return SystemConfig.objects.filter(is_public=True)
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """按分类获取配置"""
        category = request.GET.get('category', 'general')
        configs = self.get_queryset().filter(category=category)
        serializer = self.get_serializer(configs, many=True)
        return Response(serializer.data)


class LoginHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """登录历史视图集"""
    serializer_class = LoginHistorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """获取当前用户的登录历史"""
        return LoginHistory.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """获取最近的登录记录"""
        limit = int(request.GET.get('limit', 10))
        history = self.get_queryset()[:limit]
        serializer = self.get_serializer(history, many=True)
        return Response(serializer.data)


class DeviceSessionViewSet(viewsets.ModelViewSet):
    """设备会话视图集"""
    serializer_class = DeviceSessionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """获取当前用户的设备会话"""
        return DeviceSession.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def terminate(self, request, pk=None):
        """终止设备会话"""
        session = self.get_object()
        session.is_active = False
        session.save()
        return Response({'message': '会话已终止'})
    
    @action(detail=False, methods=['post'])
    def terminate_all(self, request):
        """终止所有设备会话"""
        self.get_queryset().update(is_active=False)
        return Response({'message': '所有会话已终止'})


class UserProfileViewSet(viewsets.ModelViewSet):
    """用户资料视图集"""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """获取当前用户"""
        return User.objects.filter(id=self.request.user.id)
    
    def get_object(self):
        """获取当前用户"""
        return self.request.user
    
    @action(detail=False, methods=['get', 'put', 'patch'])
    def my_profile(self, request):
        """获取或更新当前用户资料"""
        user = request.user
        
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        
        elif request.method in ['PUT', 'PATCH']:
            serializer = self.get_serializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordChangeView(APIView):
    """密码修改视图"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """修改密码"""
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            # 记录密码修改历史
            LoginHistory.objects.create(
                user=user,
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                device_type=self._get_device_type(request),
                browser=self._get_browser(request),
                os=self._get_os(request),
                success=True
            )
            
            return Response({'message': '密码修改成功'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _get_client_ip(self, request):
        """获取客户端IP"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _get_device_type(self, request):
        """获取设备类型"""
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        if 'mobile' in user_agent:
            return 'mobile'
        elif 'tablet' in user_agent:
            return 'tablet'
        else:
            return 'desktop'
    
    def _get_browser(self, request):
        """获取浏览器信息"""
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        if 'chrome' in user_agent.lower():
            return 'Chrome'
        elif 'firefox' in user_agent.lower():
            return 'Firefox'
        elif 'safari' in user_agent.lower():
            return 'Safari'
        elif 'edge' in user_agent.lower():
            return 'Edge'
        else:
            return 'Unknown'
    
    def _get_os(self, request):
        """获取操作系统信息"""
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        if 'windows' in user_agent.lower():
            return 'Windows'
        elif 'mac' in user_agent.lower():
            return 'macOS'
        elif 'linux' in user_agent.lower():
            return 'Linux'
        elif 'android' in user_agent.lower():
            return 'Android'
        elif 'ios' in user_agent.lower():
            return 'iOS'
        else:
            return 'Unknown'

# 重新导出ConversationViewSet以保持向后兼容性
from .conversation.views import ConversationViewSet

__all__ = [
    'AIProviderViewSet', 'APIKeyViewSet', 'AIModelViewSet', 'PromptTemplateViewSet',
    'ModelConfigViewSet', 'TokenUsageViewSet', 'FailoverStrategyViewSet',
    'FailoverRuleViewSet', 'UsageQuotaViewSet', 'ConfigExportView', 'ConfigImportView',
    'ConfigTemplateViewSet', 'ConfigVersionViewSet', 'UserSettingsViewSet',
    'SystemConfigViewSet', 'LoginHistoryViewSet', 'DeviceSessionViewSet',
    'UserProfileViewSet', 'PasswordChangeView', 'ConversationViewSet'
]