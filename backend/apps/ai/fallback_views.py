"""
故障转移策略API视图
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.utils import timezone
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import FailoverStrategy, FailoverRule, AIProvider
from .fallback_serializers import (
    FailoverStrategyListSerializer,
    FailoverStrategyDetailSerializer,
    FailoverStrategyCreateUpdateSerializer,
    FailoverSwitchSerializer,
    ProviderHealthSerializer
)
from .services.failover_service import FailoverService


class FailoverStrategyViewSet(viewsets.ModelViewSet):
    """故障转移策略ViewSet"""
    
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """获取当前用户的故障转移策略"""
        return FailoverStrategy.objects.filter(
            user=self.request.user
        ).select_related(
            'primary_provider', 'primary_model'
        ).prefetch_related(
            'rules__fallback_provider',
            'rules__fallback_model'
        )
    
    def get_serializer_class(self):
        """根据操作类型选择序列化器"""
        if self.action == 'list':
            return FailoverStrategyListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return FailoverStrategyCreateUpdateSerializer
        else:
            return FailoverStrategyDetailSerializer
    
    @extend_schema(
        summary="获取故障转移策略列表",
        description="获取当前用户的所有故障转移策略",
        parameters=[
            OpenApiParameter(
                name='is_active',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='过滤活跃状态'
            ),
            OpenApiParameter(
                name='is_default',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='过滤默认策略'
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        """获取策略列表"""
        queryset = self.get_queryset()
        
        # 过滤参数
        is_active = request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        is_default = request.query_params.get('is_default')
        if is_default is not None:
            queryset = queryset.filter(is_default=is_default.lower() == 'true')
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'results': serializer.data,
            'count': queryset.count()
        })
    
    @extend_schema(
        summary="创建故障转移策略",
        description="创建新的故障转移策略，包括备用规则配置"
    )
    def create(self, request, *args, **kwargs):
        """创建策略"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        strategy = serializer.save()
        
        # 返回详细信息
        detail_serializer = FailoverStrategyDetailSerializer(strategy)
        return Response(detail_serializer.data, status=status.HTTP_201_CREATED)
    
    @extend_schema(
        summary="更新故障转移策略",
        description="更新故障转移策略配置"
    )
    def update(self, request, *args, **kwargs):
        """更新策略"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        strategy = serializer.save()
        
        # 返回详细信息
        detail_serializer = FailoverStrategyDetailSerializer(strategy)
        return Response(detail_serializer.data)
    
    @extend_schema(
        summary="手动切换提供商",
        description="手动切换到指定的备用提供商",
        request=FailoverSwitchSerializer
    )
    @action(detail=True, methods=['post'])
    def switch(self, request, pk=None):
        """手动切换提供商"""
        strategy = self.get_object()
        serializer = FailoverSwitchSerializer(
            data=request.data,
            context={'strategy': strategy}
        )
        serializer.is_valid(raise_exception=True)
        
        target_provider = serializer.validated_data.get('target_provider_id')
        reason = serializer.validated_data['reason']
        dry_run = serializer.validated_data.get('dry_run', False)
        
        try:
            # 使用故障转移服务执行切换
            failover_service = FailoverService(strategy)
            result = failover_service.manual_switch(
                target_provider=target_provider,
                reason=reason,
                operator=request.user,
                dry_run=dry_run
            )
            
            return Response({
                'success': True,
                'message': '切换成功' if not dry_run else '试运行成功',
                'data': result
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'切换失败: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        summary="测试故障转移策略",
        description="测试当前策略的故障转移逻辑"
    )
    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """测试故障转移策略"""
        strategy = self.get_object()
        
        try:
            failover_service = FailoverService(strategy)
            result = failover_service.test_failover()
            
            return Response({
                'success': True,
                'message': '测试完成',
                'data': result
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'测试失败: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        summary="获取策略统计信息",
        description="获取策略的详细统计信息"
    )
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """获取策略统计信息"""
        strategy = self.get_object()
        
        # 基础统计
        stats = {
            'basic': {
                'total_requests': strategy.total_requests,
                'successful_requests': strategy.successful_requests,
                'fallback_count': strategy.fallback_count,
                'success_rate': round(strategy.get_success_rate() * 100, 2),
                'fallback_rate': round(strategy.get_fallback_rate() * 100, 2)
            },
            'rules': [],
            'providers': []
        }
        
        # 规则统计
        for rule in strategy.rules.filter(is_active=True):
            rule_stats = {
                'rule_id': rule.id,
                'priority': rule.priority,
                'provider_name': rule.fallback_provider.display_name,
                'model_name': rule.fallback_model.model_name,
                'trigger_count': rule.trigger_count,
                'success_count': rule.success_count,
                'success_rate': round((rule.success_count / rule.trigger_count * 100) if rule.trigger_count > 0 else 0, 2),
                'last_triggered': rule.last_triggered
            }
            stats['rules'].append(rule_stats)
        
        # 提供商健康状态
        all_providers = [strategy.primary_provider]
        all_providers.extend([rule.fallback_provider for rule in strategy.rules.all()])
        
        for provider in set(all_providers):
            provider_stats = {
                'provider_id': provider.id,
                'provider_name': provider.display_name,
                'is_healthy': provider.is_healthy,
                'avg_response_time': provider.avg_response_time,
                'success_rate': provider.success_rate,
                'last_health_check': provider.last_health_check,
                'is_primary': provider == strategy.primary_provider
            }
            stats['providers'].append(provider_stats)
        
        return Response(stats)
    
    @extend_schema(
        summary="重置策略统计",
        description="重置策略的统计计数器"
    )
    @action(detail=True, methods=['post'])
    def reset_stats(self, request, pk=None):
        """重置策略统计"""
        strategy = self.get_object()
        
        with transaction.atomic():
            # 重置策略统计
            strategy.total_requests = 0
            strategy.successful_requests = 0
            strategy.fallback_count = 0
            strategy.save(update_fields=['total_requests', 'successful_requests', 'fallback_count'])
            
            # 重置规则统计
            strategy.rules.update(
                trigger_count=0,
                success_count=0,
                last_triggered=None
            )
        
        return Response({
            'success': True,
            'message': '统计信息已重置'
        })
    
    @extend_schema(
        summary="设置默认策略",
        description="将指定策略设置为默认策略"
    )
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """设置默认策略"""
        strategy = self.get_object()
        
        with transaction.atomic():
            # 取消其他默认策略
            FailoverStrategy.objects.filter(
                user=request.user,
                is_default=True
            ).update(is_default=False)
            
            # 设置当前策略为默认
            strategy.is_default = True
            strategy.save(update_fields=['is_default'])
        
        return Response({
            'success': True,
            'message': f'策略 "{strategy.name}" 已设置为默认策略'
        })
    
    @extend_schema(
        summary="复制策略",
        description="复制现有策略创建新策略"
    )
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """复制策略"""
        original_strategy = self.get_object()
        
        # 生成新名称
        new_name = f"{original_strategy.name} (副本)"
        counter = 1
        while FailoverStrategy.objects.filter(
            user=request.user, 
            name=new_name
        ).exists():
            counter += 1
            new_name = f"{original_strategy.name} (副本{counter})"
        
        with transaction.atomic():
            # 复制策略
            new_strategy = FailoverStrategy.objects.create(
                user=request.user,
                name=new_name,
                description=f"复制自: {original_strategy.description}",
                primary_provider=original_strategy.primary_provider,
                primary_model=original_strategy.primary_model,
                max_retries=original_strategy.max_retries,
                retry_delay=original_strategy.retry_delay,
                timeout_threshold=original_strategy.timeout_threshold,
                error_rate_threshold=original_strategy.error_rate_threshold,
                is_active=False,  # 新策略默认为非活跃状态
                is_default=False
            )
            
            # 复制规则
            for rule in original_strategy.rules.all():
                FailoverRule.objects.create(
                    strategy=new_strategy,
                    fallback_provider=rule.fallback_provider,
                    fallback_model=rule.fallback_model,
                    priority=rule.priority,
                    trigger_errors=rule.trigger_errors,
                    is_active=rule.is_active
                )
        
        # 返回新策略信息
        serializer = FailoverStrategyDetailSerializer(new_strategy)
        return Response({
            'success': True,
            'message': '策略复制成功',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)


@extend_schema(
    summary="获取提供商健康状态",
    description="获取所有提供商的健康状态信息"
)
class ProviderHealthViewSet(viewsets.ReadOnlyModelViewSet):
    """提供商健康状态ViewSet"""
    
    permission_classes = [IsAuthenticated]
    serializer_class = ProviderHealthSerializer
    
    def get_queryset(self):
        """获取所有活跃提供商"""
        return AIProvider.objects.filter(is_active=True)
    
    def list(self, request, *args, **kwargs):
        """获取健康状态列表"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        # 统计信息
        total_providers = queryset.count()
        healthy_providers = queryset.filter(is_healthy=True).count()
        unhealthy_providers = total_providers - healthy_providers
        
        return Response({
            'results': serializer.data,
            'summary': {
                'total': total_providers,
                'healthy': healthy_providers,
                'unhealthy': unhealthy_providers,
                'health_percentage': round((healthy_providers / total_providers * 100) if total_providers > 0 else 0, 2)
            }
        })
    
    @extend_schema(
        summary="刷新提供商健康状态",
        description="手动触发所有提供商的健康检查"
    )
    @action(detail=False, methods=['post'])
    def refresh_all(self, request):
        """刷新所有提供商健康状态"""
        try:
            from .services.health_check_service import HealthCheckService
            
            health_service = HealthCheckService()
            results = health_service.check_all_providers()
            
            return Response({
                'success': True,
                'message': '健康检查完成',
                'results': results
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'健康检查失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @extend_schema(
        summary="刷新单个提供商健康状态",
        description="手动触发指定提供商的健康检查"
    )
    @action(detail=True, methods=['post'])
    def refresh(self, request, pk=None):
        """刷新单个提供商健康状态"""
        provider = self.get_object()
        
        try:
            from .services.health_check_service import HealthCheckService
            
            health_service = HealthCheckService()
            result = health_service.check_provider(provider)
            
            return Response({
                'success': True,
                'message': f'提供商 {provider.display_name} 健康检查完成',
                'result': result
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'健康检查失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
