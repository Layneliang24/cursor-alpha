"""
地道表达API视图集
"""

from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound
from django.db.models import Q, Count, Avg, Prefetch
from django.utils import timezone
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend

from apps.english.models import (
    IdiomaticExpression, ExpressionSource, ExpressionScenario,
    ExpressionScenarioLink, UserExpressionProgress, AIAssistantConfig
)
from .english_serializers import (
    IdiomaticExpressionListSerializer, IdiomaticExpressionDetailSerializer,
    IdiomaticExpressionCreateSerializer, IdiomaticExpressionUpdateSerializer,
    UserExpressionProgressSerializer, LearningSessionSerializer,
    AIAssistantConfigSerializer, ExpressionSearchSerializer,
    ExpressionSourceSerializer, ExpressionScenarioSerializer
)
from .pagination import CustomPageNumberPagination
from .permissions import IsAuthorOrAdminOrReadOnly

import random
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class IdiomaticExpressionViewSet(viewsets.ModelViewSet):
    """地道表达ViewSet"""
    
    queryset = IdiomaticExpression.objects.prefetch_related(
        'scenario_links__scenario'
    ).all()
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['expression', 'meaning', 'cultural_background']
    ordering_fields = ['created_at', 'frequency_score', 'expression']
    ordering = ['-created_at']
    
    # 权限控制
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        """根据动作选择序列化器"""
        if self.action == 'list':
            return IdiomaticExpressionListSerializer
        elif self.action == 'create':
            return IdiomaticExpressionCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return IdiomaticExpressionUpdateSerializer
        else:
            return IdiomaticExpressionDetailSerializer
    
    def get_queryset(self):
        """获取查询集"""
        queryset = super().get_queryset()
        
        # 基础筛选
        expression_type = self.request.query_params.get('expression_type')
        if expression_type:
            queryset = queryset.filter(expression_type=expression_type)
        
        formality_level = self.request.query_params.get('formality_level')
        if formality_level:
            queryset = queryset.filter(formality_level=formality_level)
        
        # 频率分数筛选
        freq_min = self.request.query_params.get('frequency_score_min')
        freq_max = self.request.query_params.get('frequency_score_max')
        if freq_min:
            queryset = queryset.filter(frequency_score__gte=freq_min)
        if freq_max:
            queryset = queryset.filter(frequency_score__lte=freq_max)
        
        # 场景筛选
        scenario_ids = self.request.query_params.getlist('scenario_ids')
        if scenario_ids:
            queryset = queryset.filter(scenario_links__scenario_id__in=scenario_ids).distinct()
        
        # 数据源筛选
        source_ids = self.request.query_params.getlist('source_ids')
        if source_ids:
            queryset = queryset.filter(source_id__in=source_ids)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """高级搜索接口"""
        serializer = ExpressionSearchSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        
        params = serializer.validated_data
        queryset = self.get_queryset()
        
        # 文本搜索
        q = params.get('q')
        if q:
            queryset = queryset.filter(
                Q(expression__icontains=q) |
                Q(meaning__icontains=q) |
                Q(cultural_background__icontains=q)
            )
        
        # 应用其他筛选条件
        for field in ['expression_type', 'formality_level']:
            value = params.get(field)
            if value:
                queryset = queryset.filter(**{field: value})
        
        # 频率分数范围
        freq_min = params.get('frequency_score_min')
        freq_max = params.get('frequency_score_max')
        if freq_min:
            queryset = queryset.filter(frequency_score__gte=freq_min)
        if freq_max:
            queryset = queryset.filter(frequency_score__lte=freq_max)
        
        # 场景和数据源筛选
        scenario_ids = params.get('scenario_ids', [])
        if scenario_ids:
            queryset = queryset.filter(scenario_links__scenario_id__in=scenario_ids).distinct()
        
        source_ids = params.get('source_ids', [])
        if source_ids:
            queryset = queryset.filter(source_id__in=source_ids)
        
        # 排序
        ordering = params.get('ordering', '-created_at')
        queryset = queryset.order_by(ordering)
        
        # 分页返回
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = IdiomaticExpressionListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = IdiomaticExpressionListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def random(self, request):
        """随机获取表达式"""
        limit = min(int(request.query_params.get('limit', 10)), 50)
        
        # 获取总数
        total_count = self.get_queryset().count()
        if total_count == 0:
            return Response([])
        
        # 随机选择
        if total_count <= limit:
            queryset = self.get_queryset()
        else:
            # 随机选择ID
            random_ids = random.sample(
                list(self.get_queryset().values_list('id', flat=True)),
                min(limit, total_count)
            )
            queryset = self.get_queryset().filter(id__in=random_ids)
        
        serializer = IdiomaticExpressionListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """获取热门表达式"""
        limit = min(int(request.query_params.get('limit', 10)), 50)
        
        queryset = self.get_queryset().filter(
            frequency_score__gte=7
        ).order_by('-frequency_score', '-created_at')[:limit]
        
        serializer = IdiomaticExpressionListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """获取最新表达式"""
        limit = min(int(request.query_params.get('limit', 10)), 50)
        
        queryset = self.get_queryset().order_by('-created_at')[:limit]
        
        serializer = IdiomaticExpressionListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """获取统计信息"""
        queryset = self.get_queryset()
        
        stats = {
            'total_count': queryset.count(),
            'by_type': queryset.values('expression_type').annotate(
                count=Count('id')
            ).order_by('-count'),
            'by_formality': queryset.values('formality_level').annotate(
                count=Count('id')
            ).order_by('-count'),
            'avg_frequency_score': queryset.aggregate(
                avg=Avg('frequency_score')
            )['avg'] or 0,
            'by_source': queryset.select_related('source').values(
                'source__source_name'
            ).annotate(
                count=Count('id')
            ).order_by('-count')[:10]
        }
        
        return Response(stats)
    
    def perform_create(self, serializer):
        """创建时的额外处理"""
        # 可以在这里添加创建日志等逻辑
        instance = serializer.save()
        logger.info(f"创建新表达式: {instance.expression} (ID: {instance.id})")
    
    def perform_update(self, serializer):
        """更新时的额外处理"""
        instance = serializer.save()
        logger.info(f"更新表达式: {instance.expression} (ID: {instance.id})")
    
    def perform_destroy(self, instance):
        """删除时的额外处理"""
        logger.info(f"删除表达式: {instance.expression} (ID: {instance.id})")
        instance.delete()


class UserExpressionProgressViewSet(viewsets.ModelViewSet):
    """用户表达式学习进度ViewSet"""
    
    serializer_class = UserExpressionProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPageNumberPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['last_reviewed', 'created_at', 'mastery_level']
    ordering = ['-last_reviewed']
    
    def get_queryset(self):
        """获取当前用户的学习进度"""
        return UserExpressionProgress.objects.filter(
            user=self.request.user
        ).select_related('expression').prefetch_related(
            'expression__scenario_links__scenario'
        )
    
    @action(detail=False, methods=['get'])
    def favorites(self, request):
        """获取收藏的表达式"""
        queryset = self.get_queryset().filter(is_favorite=True)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def review_due(self, request):
        """获取需要复习的表达式"""
        # 简单的复习算法：7天未复习或掌握度低于3
        from datetime import timedelta
        
        review_threshold = timezone.now() - timedelta(days=7)
        
        queryset = self.get_queryset().filter(
            Q(last_reviewed__lt=review_threshold) |
            Q(mastery_level__lt=3)
        ).order_by('last_reviewed', 'mastery_level')
        
        limit = min(int(request.query_params.get('limit', 20)), 50)
        queryset = queryset[:limit]
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """获取学习统计"""
        queryset = self.get_queryset()
        
        stats = {
            'total_learned': queryset.count(),
            'favorites_count': queryset.filter(is_favorite=True).count(),
            'mastery_distribution': queryset.values('mastery_level').annotate(
                count=Count('id')
            ).order_by('mastery_level'),
            'avg_mastery_level': queryset.aggregate(
                avg=Avg('mastery_level')
            )['avg'] or 0,
            'review_count_total': queryset.aggregate(
                total=Count('review_count')
            )['total'] or 0
        }
        
        return Response(stats)
    
    @action(detail=True, methods=['post'])
    def mark_favorite(self, request, pk=None):
        """标记/取消收藏"""
        progress = self.get_object()
        is_favorite = request.data.get('is_favorite', not progress.is_favorite)
        
        progress.is_favorite = is_favorite
        progress.save(update_fields=['is_favorite'])
        
        return Response({
            'is_favorite': progress.is_favorite,
            'message': '已收藏' if is_favorite else '已取消收藏'
        })
    
    @action(detail=True, methods=['post'])
    def update_mastery(self, request, pk=None):
        """更新掌握程度"""
        progress = self.get_object()
        mastery_level = request.data.get('mastery_level')
        
        if mastery_level is None or not (0 <= mastery_level <= 5):
            raise ValidationError("掌握程度必须在0-5之间")
        
        progress.mastery_level = mastery_level
        progress.last_reviewed = timezone.now()
        progress.review_count += 1
        progress.save(update_fields=['mastery_level', 'last_reviewed', 'review_count'])
        
        return Response({
            'mastery_level': progress.mastery_level,
            'last_reviewed': progress.last_reviewed,
            'review_count': progress.review_count,
            'message': '掌握程度已更新'
        })


class LearningSessionViewSet(viewsets.GenericViewSet):
    """学习会话ViewSet"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def create_session(self, request):
        """创建学习会话"""
        serializer = LearningSessionSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        params = serializer.validated_data
        session_type = params['session_type']
        limit = params['limit']
        
        # 根据会话类型获取表达式
        if session_type == 'review':
            expressions = self._get_review_expressions(request.user, params, limit)
        elif session_type == 'new':
            expressions = self._get_new_expressions(request.user, params, limit)
        elif session_type == 'favorite':
            expressions = self._get_favorite_expressions(request.user, limit)
        else:  # random
            expressions = self._get_random_expressions(params, limit)
        
        # 序列化返回
        from .english_serializers import IdiomaticExpressionDetailSerializer
        serializer = IdiomaticExpressionDetailSerializer(
            expressions, 
            many=True,
            context={'request': request}
        )
        
        return Response({
            'session_type': session_type,
            'expressions': serializer.data,
            'count': len(expressions)
        })
    
    def _get_review_expressions(self, user, params, limit):
        """获取复习表达式"""
        from datetime import timedelta
        
        review_threshold = timezone.now() - timedelta(days=7)
        
        progress_queryset = UserExpressionProgress.objects.filter(
            user=user
        ).filter(
            Q(last_reviewed__lt=review_threshold) |
            Q(mastery_level__lt=3)
        ).select_related('expression__source').prefetch_related(
            'expression__scenario_links__scenario'
        )
        
        # 应用筛选条件
        progress_queryset = self._apply_filters(progress_queryset, params, 'expression__')
        
        # 按优先级排序：掌握度低的优先，然后是复习时间久的
        progress_queryset = progress_queryset.order_by('mastery_level', 'last_reviewed')
        
        return [p.expression for p in progress_queryset[:limit]]
    
    def _get_new_expressions(self, user, params, limit):
        """获取新表达式（用户未学过的）"""
        learned_ids = UserExpressionProgress.objects.filter(
            user=user
        ).values_list('expression_id', flat=True)
        
        queryset = IdiomaticExpression.objects.exclude(
            id__in=learned_ids
        ).select_related('source').prefetch_related(
            'scenario_links__scenario'
        )
        
        # 应用筛选条件
        queryset = self._apply_filters(queryset, params)
        
        # 随机排序
        return list(queryset.order_by('?')[:limit])
    
    def _get_favorite_expressions(self, user, limit):
        """获取收藏的表达式"""
        progress_queryset = UserExpressionProgress.objects.filter(
            user=user,
            is_favorite=True
        ).select_related('expression__source').prefetch_related(
            'expression__scenario_links__scenario'
        ).order_by('-last_reviewed')
        
        return [p.expression for p in progress_queryset[:limit]]
    
    def _get_random_expressions(self, params, limit):
        """获取随机表达式"""
        queryset = IdiomaticExpression.objects.select_related('source').prefetch_related(
            'scenario_links__scenario'
        )
        
        # 应用筛选条件
        queryset = self._apply_filters(queryset, params)
        
        # 随机选择
        return list(queryset.order_by('?')[:limit])
    
    def _apply_filters(self, queryset, params, prefix=''):
        """应用筛选条件"""
        expression_types = params.get('expression_types', [])
        if expression_types:
            queryset = queryset.filter(**{f'{prefix}expression_type__in': expression_types})
        
        scenario_ids = params.get('scenario_ids', [])
        if scenario_ids:
            queryset = queryset.filter(**{f'{prefix}scenario_links__scenario_id__in': scenario_ids}).distinct()
        
        return queryset


class ExpressionSourceViewSet(viewsets.ReadOnlyModelViewSet):
    """表达式数据源ViewSet（只读）"""
    
    queryset = ExpressionSource.objects.all()
    serializer_class = ExpressionSourceSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = CustomPageNumberPagination
    ordering = ['source_name']


class ExpressionScenarioViewSet(viewsets.ReadOnlyModelViewSet):
    """表达式场景ViewSet（只读）"""
    
    queryset = ExpressionScenario.objects.all()
    serializer_class = ExpressionScenarioSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = CustomPageNumberPagination
    ordering = ['scenario_name']
