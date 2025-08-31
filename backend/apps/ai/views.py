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
from django.db.models import Count, Sum, Avg
from django.db import transaction

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


class AIProviderViewSet(viewsets.ModelViewSet):
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
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
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


class APIKeyViewSet(viewsets.ModelViewSet):
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
        serializer.save(user=self.request.user)
    
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