"""
地道表达API视图集
"""

from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound
from django.db.models import Q, Count, Avg, Prefetch, Sum, Max, Min
from django.utils import timezone
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from django.core.cache import cache
from django.http import StreamingHttpResponse
import json
from datetime import datetime, timedelta

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


class StatisticsViewSet(viewsets.GenericViewSet):
    """学习数据统计ViewSet"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def overview(self, request):
        """获取学习数据总览"""
        cache_key = f'stats_overview_{request.user.id}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        user = request.user
        
        # 用户学习进度统计
        progress_queryset = UserExpressionProgress.objects.filter(user=user)
        
        # 基础统计
        total_learned = progress_queryset.count()
        total_expressions = IdiomaticExpression.objects.count()
        favorites_count = progress_queryset.filter(is_favorite=True).count()
        
        # 掌握度分布
        mastery_stats = progress_queryset.values('mastery_level').annotate(
            count=Count('id')
        ).order_by('mastery_level')
        
        # 平均掌握度
        avg_mastery = progress_queryset.aggregate(avg=Avg('mastery_level'))['avg'] or 0
        
        # 复习统计
        total_reviews = progress_queryset.aggregate(total=Sum('review_count'))['total'] or 0
        
        # 最近7天的学习活动
        week_ago = timezone.now() - timedelta(days=7)
        recent_activity = progress_queryset.filter(
            last_reviewed__gte=week_ago
        ).count()
        
        # 需要复习的表达式数量
        review_threshold = timezone.now() - timedelta(days=7)
        review_due_count = progress_queryset.filter(
            Q(last_reviewed__lt=review_threshold) |
            Q(mastery_level__lt=3)
        ).count()
        
        # 学习进度百分比
        learning_progress = (total_learned / total_expressions * 100) if total_expressions > 0 else 0
        
        data = {
            'total_learned': total_learned,
            'total_expressions': total_expressions,
            'learning_progress': round(learning_progress, 2),
            'favorites_count': favorites_count,
            'avg_mastery_level': round(avg_mastery, 2),
            'total_reviews': total_reviews,
            'recent_activity_count': recent_activity,
            'review_due_count': review_due_count,
            'mastery_distribution': list(mastery_stats)
        }
        
        # 缓存5分钟
        cache.set(cache_key, data, 300)
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def learning_trend(self, request):
        """获取学习趋势数据"""
        cache_key = f'stats_trend_{request.user.id}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        user = request.user
        days = min(int(request.query_params.get('days', 30)), 90)  # 最多90天
        
        # 计算日期范围
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        # 按天统计学习活动
        daily_stats = []
        current_date = start_date
        
        while current_date <= end_date:
            next_date = current_date + timedelta(days=1)
            
            # 当天的学习活动
            day_progress = UserExpressionProgress.objects.filter(
                user=user,
                last_reviewed__date=current_date
            )
            
            daily_stats.append({
                'date': current_date.isoformat(),
                'expressions_reviewed': day_progress.count(),
                'avg_mastery_improvement': day_progress.aggregate(
                    avg=Avg('mastery_level')
                )['avg'] or 0
            })
            
            current_date = next_date
        
        data = {
            'period_days': days,
            'daily_stats': daily_stats,
            'total_active_days': len([d for d in daily_stats if d['expressions_reviewed'] > 0])
        }
        
        # 缓存10分钟
        cache.set(cache_key, data, 600)
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def mastery_analysis(self, request):
        """获取掌握度分析"""
        cache_key = f'stats_mastery_{request.user.id}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        user = request.user
        progress_queryset = UserExpressionProgress.objects.filter(user=user)
        
        # 按表达式类型分析掌握度
        type_mastery = progress_queryset.select_related('expression').values(
            'expression__expression_type'
        ).annotate(
            count=Count('id'),
            avg_mastery=Avg('mastery_level'),
            max_mastery=Max('mastery_level'),
            min_mastery=Min('mastery_level')
        ).order_by('-avg_mastery')
        
        # 按正式程度分析掌握度
        formality_mastery = progress_queryset.select_related('expression').values(
            'expression__formality_level'
        ).annotate(
            count=Count('id'),
            avg_mastery=Avg('mastery_level'),
            max_mastery=Max('mastery_level'),
            min_mastery=Min('mastery_level')
        ).order_by('-avg_mastery')
        
        # 按场景分析掌握度
        scenario_mastery = progress_queryset.select_related(
            'expression'
        ).prefetch_related(
            'expression__scenario_links__scenario'
        ).values(
            'expression__scenario_links__scenario__scenario_name'
        ).annotate(
            count=Count('id'),
            avg_mastery=Avg('mastery_level')
        ).order_by('-avg_mastery')[:10]  # 前10个场景
        
        # 掌握度改进趋势（最近30天）
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_improvements = progress_queryset.filter(
            last_reviewed__gte=thirty_days_ago,
            review_count__gt=1
        ).count()
        
        data = {
            'by_expression_type': list(type_mastery),
            'by_formality_level': list(formality_mastery),
            'by_scenario': list(scenario_mastery),
            'recent_improvements': recent_improvements,
            'total_analyzed': progress_queryset.count()
        }
        
        # 缓存15分钟
        cache.set(cache_key, data, 900)
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def weak_areas(self, request):
        """获取薄弱环节分析"""
        user = request.user
        
        # 掌握度低的表达式
        weak_expressions = UserExpressionProgress.objects.filter(
            user=user,
            mastery_level__lt=3
        ).select_related('expression').order_by('mastery_level')[:20]
        
        # 需要复习的表达式
        review_threshold = timezone.now() - timedelta(days=7)
        need_review = UserExpressionProgress.objects.filter(
            user=user
        ).filter(
            Q(last_reviewed__lt=review_threshold) |
            Q(mastery_level__lt=3)
        ).select_related('expression').order_by('last_reviewed')[:20]
        
        # 复习次数多但掌握度仍然低的表达式（困难表达式）
        difficult_expressions = UserExpressionProgress.objects.filter(
            user=user,
            review_count__gte=3,
            mastery_level__lt=3
        ).select_related('expression').order_by('mastery_level', '-review_count')[:10]
        
        from .english_serializers import UserExpressionProgressSerializer
        
        data = {
            'weak_expressions': UserExpressionProgressSerializer(weak_expressions, many=True).data,
            'need_review': UserExpressionProgressSerializer(need_review, many=True).data,
            'difficult_expressions': UserExpressionProgressSerializer(difficult_expressions, many=True).data
        }
        
        return Response(data)


class AIAssistantViewSet(viewsets.GenericViewSet):
    """AI助教ViewSet"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def chat(self, request):
        """AI对话接口"""
        message = request.data.get('message', '').strip()
        context_type = request.data.get('context_type', 'general')  # general, expression, learning
        context_id = request.data.get('context_id')  # 相关表达式或学习内容的ID
        stream = request.data.get('stream', False)  # 是否流式响应
        
        if not message:
            raise ValidationError("消息内容不能为空")
        
        # 获取AI配置
        try:
            ai_config = AIAssistantConfig.objects.get(is_active=True)
        except AIAssistantConfig.DoesNotExist:
            return Response(
                {'error': 'AI助教服务暂时不可用'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        # 构建上下文
        context = self._build_context(request.user, context_type, context_id)
        
        # 构建完整的提示
        full_prompt = self._build_prompt(message, context, ai_config)
        
        try:
            if stream:
                return self._stream_response(full_prompt, ai_config)
            else:
                response = self._get_ai_response(full_prompt, ai_config)
                return Response({
                    'response': response,
                    'context_type': context_type,
                    'timestamp': timezone.now().isoformat()
                })
        except Exception as e:
            logger.error(f"AI助教服务错误: {str(e)}")
            return Response(
                {'error': 'AI助教服务出现错误，请稍后重试'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def explain_expression(self, request):
        """解释表达式"""
        expression_id = request.data.get('expression_id')
        question = request.data.get('question', '').strip()
        
        if not expression_id:
            raise ValidationError("表达式ID不能为空")
        
        try:
            expression = IdiomaticExpression.objects.get(id=expression_id)
        except IdiomaticExpression.DoesNotExist:
            raise NotFound("表达式不存在")
        
        # 获取AI配置
        try:
            ai_config = AIAssistantConfig.objects.get(is_active=True)
        except AIAssistantConfig.DoesNotExist:
            return Response(
                {'error': 'AI助教服务暂时不可用'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        # 构建解释提示
        explain_prompt = self._build_explanation_prompt(expression, question, ai_config)
        
        try:
            response = self._get_ai_response(explain_prompt, ai_config)
            return Response({
                'expression': expression.expression,
                'explanation': response,
                'question': question,
                'timestamp': timezone.now().isoformat()
            })
        except Exception as e:
            logger.error(f"表达式解释服务错误: {str(e)}")
            return Response(
                {'error': '表达式解释服务出现错误，请稍后重试'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def practice_dialogue(self, request):
        """练习对话"""
        expression_id = request.data.get('expression_id')
        scenario = request.data.get('scenario', 'casual')  # casual, business, academic
        difficulty = request.data.get('difficulty', 'medium')  # easy, medium, hard
        
        if not expression_id:
            raise ValidationError("表达式ID不能为空")
        
        try:
            expression = IdiomaticExpression.objects.get(id=expression_id)
        except IdiomaticExpression.DoesNotExist:
            raise NotFound("表达式不存在")
        
        # 获取AI配置
        try:
            ai_config = AIAssistantConfig.objects.get(is_active=True)
        except AIAssistantConfig.DoesNotExist:
            return Response(
                {'error': 'AI助教服务暂时不可用'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        # 构建对话练习提示
        dialogue_prompt = self._build_dialogue_prompt(expression, scenario, difficulty, ai_config)
        
        try:
            response = self._get_ai_response(dialogue_prompt, ai_config)
            return Response({
                'expression': expression.expression,
                'scenario': scenario,
                'difficulty': difficulty,
                'dialogue': response,
                'timestamp': timezone.now().isoformat()
            })
        except Exception as e:
            logger.error(f"对话练习服务错误: {str(e)}")
            return Response(
                {'error': '对话练习服务出现错误，请稍后重试'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _build_context(self, user, context_type, context_id):
        """构建上下文信息"""
        context = {
            'user_stats': self._get_user_stats(user),
            'context_type': context_type
        }
        
        if context_type == 'expression' and context_id:
            try:
                expression = IdiomaticExpression.objects.get(id=context_id)
                context['expression'] = {
                    'text': expression.expression,
                    'meaning': expression.meaning,
                    'type': expression.expression_type,
                    'formality': expression.formality_level,
                    'examples': expression.usage_examples
                }
            except IdiomaticExpression.DoesNotExist:
                pass
        
        return context
    
    def _get_user_stats(self, user):
        """获取用户学习统计"""
        progress_queryset = UserExpressionProgress.objects.filter(user=user)
        
        return {
            'total_learned': progress_queryset.count(),
            'avg_mastery': progress_queryset.aggregate(avg=Avg('mastery_level'))['avg'] or 0,
            'favorites_count': progress_queryset.filter(is_favorite=True).count()
        }
    
    def _build_prompt(self, message, context, ai_config):
        """构建AI提示"""
        system_prompt = ai_config.system_prompt or """
        你是一位专业的英语学习助教，专门帮助用户学习地道的英语表达。
        请用中文回答用户的问题，提供准确、有用的英语学习建议。
        """
        
        context_info = f"""
        用户学习情况：
        - 已学习表达式：{context['user_stats']['total_learned']}个
        - 平均掌握度：{context['user_stats']['avg_mastery']:.1f}/5
        - 收藏表达式：{context['user_stats']['favorites_count']}个
        """
        
        if context.get('expression'):
            expr = context['expression']
            context_info += f"""
        
        当前讨论的表达式：
        - 表达式：{expr['text']}
        - 含义：{expr['meaning']}
        - 类型：{expr['type']}
        - 正式程度：{expr['formality']}
        """
        
        return f"{system_prompt}\n\n{context_info}\n\n用户问题：{message}"
    
    def _build_explanation_prompt(self, expression, question, ai_config):
        """构建解释提示"""
        base_prompt = f"""
        请详细解释这个英语表达式："{expression.expression}"
        
        表达式信息：
        - 含义：{expression.meaning}
        - 类型：{expression.expression_type}
        - 正式程度：{expression.formality_level}
        - 使用示例：{', '.join(expression.usage_examples) if expression.usage_examples else '无'}
        - 文化背景：{expression.cultural_background or '无'}
        """
        
        if question:
            base_prompt += f"\n\n用户特别想了解：{question}"
        
        base_prompt += """
        
        请从以下几个方面进行解释：
        1. 字面意思和实际含义
        2. 使用场合和语境
        3. 语法结构分析
        4. 相似表达式对比
        5. 实用的记忆技巧
        """
        
        return base_prompt
    
    def _build_dialogue_prompt(self, expression, scenario, difficulty, ai_config):
        """构建对话练习提示"""
        scenario_desc = {
            'casual': '日常休闲对话',
            'business': '商务场合对话',
            'academic': '学术讨论对话'
        }
        
        difficulty_desc = {
            'easy': '简单（基础词汇，简短句子）',
            'medium': '中等（常用词汇，中等长度句子）',
            'hard': '困难（高级词汇，复杂句子结构）'
        }
        
        return f"""
        请创建一个包含表达式 "{expression.expression}" 的{scenario_desc.get(scenario, '对话')}练习。
        
        要求：
        - 难度级别：{difficulty_desc.get(difficulty, '中等')}
        - 对话应该自然地使用这个表达式
        - 提供2-3轮对话
        - 每轮对话后提供使用要点说明
        - 场景设定要真实可信
        
        表达式含义：{expression.meaning}
        使用示例：{', '.join(expression.usage_examples) if expression.usage_examples else '无'}
        
        请按以下格式输出：
        【场景设定】
        【对话内容】
        【使用要点】
        【练习建议】
        """
    
    def _get_ai_response(self, prompt, ai_config):
        """获取AI响应（模拟实现）"""
        # 这里应该调用实际的AI服务，比如OpenAI、Claude等
        # 现在返回模拟响应
        return f"这是AI助教的回复。收到提示：{prompt[:100]}..."
    
    def _stream_response(self, prompt, ai_config):
        """流式响应（模拟实现）"""
        def generate():
            # 模拟流式响应
            response_parts = [
                "这是", "AI助教", "的流式", "回复。", "正在", "处理您的", "问题..."
            ]
            
            for part in response_parts:
                yield f"data: {json.dumps({'content': part, 'done': False})}\n\n"
                # 实际实现中这里会有真实的AI响应流
            
            yield f"data: {json.dumps({'content': '', 'done': True})}\n\n"
        
        response = StreamingHttpResponse(
            generate(),
            content_type='text/event-stream'
        )
        response['Cache-Control'] = 'no-cache'
        response['Connection'] = 'keep-alive'
        return response
