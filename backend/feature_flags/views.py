from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import FeatureFlag, FeatureFlagHistory, FeatureFlagUsage
from .serializers import (
    FeatureFlagSerializer,
    FeatureFlagCreateSerializer,
    FeatureFlagUpdateSerializer,
    FeatureFlagHistorySerializer,
    FeatureFlagUsageSerializer,
    FeatureFlagStatsSerializer
)
from .services import feature_flag_service


class FeatureFlagViewSet(viewsets.ModelViewSet):
    """特性开关管理API"""
    
    queryset = FeatureFlag.objects.all()
    serializer_class = FeatureFlagSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'key'
    
    def get_serializer_class(self):
        if self.action == 'create':
            return FeatureFlagCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return FeatureFlagUpdateSerializer
        return FeatureFlagSerializer
    
    def get_permissions(self):
        """管理操作需要管理员权限"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]
    
    @extend_schema(
        summary="获取特性开关列表",
        description="获取所有特性开关的列表，支持按状态、环境等条件过滤",
        parameters=[
            OpenApiParameter('status', OpenApiTypes.STR, description='按状态过滤'),
            OpenApiParameter('environment', OpenApiTypes.STR, description='按环境过滤'),
            OpenApiParameter('search', OpenApiTypes.STR, description='搜索关键词'),
        ]
    )
    def list(self, request):
        queryset = self.get_queryset()
        
        # 过滤条件
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        environment_filter = request.query_params.get('environment')
        if environment_filter:
            queryset = queryset.filter(environments__contains=[environment_filter])
        
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(key__icontains=search) | 
                Q(description__icontains=search)
            )
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="创建特性开关",
        description="创建新的特性开关"
    )
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            flag = feature_flag_service.create_flag(
                serializer.validated_data,
                request.user
            )
            if flag:
                response_serializer = FeatureFlagSerializer(flag)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {'error': '创建特性开关失败'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        summary="更新特性开关",
        description="更新指定的特性开关"
    )
    def update(self, request, key=None):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            reason = request.data.get('reason', '手动更新')
            success = feature_flag_service.update_flag(
                key,
                serializer.validated_data,
                request.user,
                reason
            )
            if success:
                flag = FeatureFlag.objects.get(key=key)
                response_serializer = FeatureFlagSerializer(flag)
                return Response(response_serializer.data)
            else:
                return Response(
                    {'error': '更新特性开关失败'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        summary="删除特性开关",
        description="删除指定的特性开关"
    )
    def destroy(self, request, key=None):
        reason = request.data.get('reason', '手动删除')
        success = feature_flag_service.delete_flag(key, request.user, reason)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {'error': '删除特性开关失败'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @extend_schema(
        summary="检查特性开关状态",
        description="检查指定特性开关对当前用户是否启用",
        parameters=[
            OpenApiParameter('context', OpenApiTypes.OBJECT, description='额外上下文信息'),
        ]
    )
    @action(detail=True, methods=['get', 'post'])
    def check(self, request, key=None):
        """检查特性开关状态"""
        context = request.data.get('context', {}) if request.method == 'POST' else {}
        
        is_enabled = feature_flag_service.is_enabled(
            key,
            request.user,
            context
        )
        
        value = feature_flag_service.get_value(
            key,
            request.user,
            context
        )
        
        return Response({
            'key': key,
            'enabled': is_enabled,
            'value': value,
            'user_id': request.user.id,
            'timestamp': timezone.now().isoformat()
        })
    
    @extend_schema(
        summary="获取所有特性开关状态",
        description="获取所有特性开关对当前用户的状态",
        parameters=[
            OpenApiParameter('context', OpenApiTypes.OBJECT, description='额外上下文信息'),
        ]
    )
    @action(detail=False, methods=['get', 'post'])
    def check_all(self, request):
        """获取所有特性开关状态"""
        context = request.data.get('context', {}) if request.method == 'POST' else {}
        
        flags = feature_flag_service.get_all_flags(
            request.user,
            context
        )
        
        return Response({
            'flags': flags,
            'user_id': request.user.id,
            'timestamp': timezone.now().isoformat()
        })
    
    @extend_schema(
        summary="快速启用/禁用特性开关",
        description="快速切换特性开关的启用状态"
    )
    @action(detail=True, methods=['post'])
    def toggle(self, request, key=None):
        """快速启用/禁用特性开关"""
        try:
            flag = FeatureFlag.objects.get(key=key)
            new_status = (
                FeatureFlag.Status.ENABLED 
                if flag.status == FeatureFlag.Status.DISABLED 
                else FeatureFlag.Status.DISABLED
            )
            
            reason = request.data.get('reason', f'快速切换为{new_status}')
            success = feature_flag_service.update_flag(
                key,
                {'status': new_status},
                request.user,
                reason
            )
            
            if success:
                flag.refresh_from_db()
                serializer = FeatureFlagSerializer(flag)
                return Response(serializer.data)
            else:
                return Response(
                    {'error': '切换状态失败'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except FeatureFlag.DoesNotExist:
            return Response(
                {'error': '特性开关不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @extend_schema(
        summary="灰度发布控制",
        description="调整特性开关的灰度发布百分比"
    )
    @action(detail=True, methods=['post'])
    def rollout(self, request, key=None):
        """灰度发布控制"""
        percentage = request.data.get('percentage')
        if percentage is None or not (0 <= percentage <= 100):
            return Response(
                {'error': '百分比必须在0-100之间'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reason = request.data.get('reason', f'调整灰度百分比为{percentage}%')
        success = feature_flag_service.update_flag(
            key,
            {
                'status': FeatureFlag.Status.ROLLOUT,
                'target_type': FeatureFlag.TargetType.PERCENTAGE,
                'rollout_percentage': percentage
            },
            request.user,
            reason
        )
        
        if success:
            flag = FeatureFlag.objects.get(key=key)
            serializer = FeatureFlagSerializer(flag)
            return Response(serializer.data)
        else:
            return Response(
                {'error': '调整灰度百分比失败'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @extend_schema(
        summary="获取特性开关统计信息",
        description="获取特性开关的使用统计信息",
        parameters=[
            OpenApiParameter('days', OpenApiTypes.INT, description='统计天数，默认7天'),
        ]
    )
    @action(detail=True, methods=['get'])
    def stats(self, request, key=None):
        """获取特性开关统计信息"""
        days = int(request.query_params.get('days', 7))
        stats = feature_flag_service.get_usage_stats(key, days)
        
        if not stats:
            return Response(
                {'error': '特性开关不存在或无统计数据'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = FeatureFlagStatsSerializer(stats)
        return Response(serializer.data)
    
    @extend_schema(
        summary="获取特性开关变更历史",
        description="获取特性开关的变更历史记录"
    )
    @action(detail=True, methods=['get'])
    def history(self, request, key=None):
        """获取特性开关变更历史"""
        try:
            flag = FeatureFlag.objects.get(key=key)
            history = FeatureFlagHistory.objects.filter(
                feature_flag=flag
            ).order_by('-changed_at')[:50]  # 最近50条记录
            
            serializer = FeatureFlagHistorySerializer(history, many=True)
            return Response(serializer.data)
            
        except FeatureFlag.DoesNotExist:
            return Response(
                {'error': '特性开关不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @extend_schema(
        summary="获取特性开关使用记录",
        description="获取特性开关的使用记录",
        parameters=[
            OpenApiParameter('limit', OpenApiTypes.INT, description='记录数量限制，默认100'),
            OpenApiParameter('user_id', OpenApiTypes.INT, description='按用户ID过滤'),
        ]
    )
    @action(detail=True, methods=['get'])
    def usage(self, request, key=None):
        """获取特性开关使用记录"""
        try:
            flag = FeatureFlag.objects.get(key=key)
            limit = int(request.query_params.get('limit', 100))
            user_id = request.query_params.get('user_id')
            
            usage_records = FeatureFlagUsage.objects.filter(
                feature_flag=flag
            ).order_by('-accessed_at')
            
            if user_id:
                usage_records = usage_records.filter(user_id=user_id)
            
            usage_records = usage_records[:limit]
            
            serializer = FeatureFlagUsageSerializer(usage_records, many=True)
            return Response(serializer.data)
            
        except FeatureFlag.DoesNotExist:
            return Response(
                {'error': '特性开关不存在'},
                status=status.HTTP_404_NOT_FOUND
            )


class FeatureFlagPublicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    特性开关公共API - 只读，用于前端检查特性开关状态
    """
    queryset = FeatureFlag.objects.filter(
        status__in=[FeatureFlag.Status.ENABLED, FeatureFlag.Status.ROLLOUT]
    )
    serializer_class = FeatureFlagSerializer
    permission_classes = []  # 允许匿名访问
    lookup_field = 'key'
    
    @extend_schema(
        summary="检查单个特性开关",
        description="检查指定特性开关对当前用户是否启用（公共接口）"
    )
    @action(detail=True, methods=['get'])
    def enabled(self, request, key=None):
        """检查特性开关是否启用（简化版）"""
        is_enabled = feature_flag_service.is_enabled(key, request.user)
        
        return Response({
            'enabled': is_enabled
        })
    
    @extend_schema(
        summary="批量检查特性开关",
        description="批量检查多个特性开关的状态"
    )
    @action(detail=False, methods=['post'])
    def batch_check(self, request):
        """批量检查特性开关"""
        flag_keys = request.data.get('flags', [])
        context = request.data.get('context', {})
        
        if not isinstance(flag_keys, list):
            return Response(
                {'error': 'flags字段必须是数组'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        results = {}
        for key in flag_keys:
            results[key] = feature_flag_service.is_enabled(
                key,
                request.user,
                context
            )
        
        return Response({
            'flags': results,
            'user_id': request.user.id
        })