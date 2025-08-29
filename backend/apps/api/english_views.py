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
from apps.english.permissions import (
    EnglishLearnerPermission, EnglishContentManagerPermission,
    EnglishAdminPermission, UserProgressOwnerPermission
)
from apps.english.security import (
    EnglishExpressionsThrottle, EnglishLearningThrottle,
    EnglishManagementThrottle, EnglishAnonymousThrottle,
    SecurityAuditLogger, ContentSecurityValidator
)
from apps.english.cache_strategy import EnglishCacheManager, CacheMonitor
from .cache_strategy import CacheDecorators, CacheStrategy
from .english_serializers import (
    IdiomaticExpressionListSerializer, IdiomaticExpressionDetailSerializer,
    IdiomaticExpressionCreateSerializer, IdiomaticExpressionUpdateSerializer,
    UserExpressionProgressSerializer, LearningSessionSerializer,
    AIAssistantConfigSerializer, ExpressionSearchSerializer,
    ExpressionSourceSerializer, ExpressionScenarioSerializer,
    IdiomaticExpressionBatchSerializer, UserProgressBatchSerializer,
    DynamicFieldExpressionSerializer
)
from .pagination import CustomPageNumberPagination
from .permissions import IsAuthorOrAdminOrReadOnly
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

import random
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


@extend_schema_view(
    list=extend_schema(
        tags=['Expressions'],
        summary='获取地道表达列表',
        description='分页获取地道表达列表，支持搜索、过滤和排序',
        parameters=[
            OpenApiParameter('search', OpenApiTypes.STR, description='搜索关键词'),
            OpenApiParameter('difficulty_level', OpenApiTypes.STR, description='难度级别'),
            OpenApiParameter('tags', OpenApiTypes.STR, description='标签过滤'),
            OpenApiParameter('ordering', OpenApiTypes.STR, description='排序字段'),
        ],
        examples=[
            OpenApiExample(
                'Basic Request',
                summary='基本请求示例',
                description='获取前10个表达',
                value={'page': 1, 'page_size': 10}
            ),
        ]
    ),
    create=extend_schema(
        tags=['Expressions'],
        summary='创建地道表达',
        description='创建新的地道表达，需要内容管理权限'
    ),
    retrieve=extend_schema(
        tags=['Expressions'],
        summary='获取地道表达详情',
        description='根据ID获取地道表达的详细信息'
    ),
    update=extend_schema(
        tags=['Expressions'],
        summary='更新地道表达',
        description='更新指定的地道表达，需要内容管理权限'
    ),
    destroy=extend_schema(
        tags=['Expressions'],
        summary='删除地道表达',
        description='删除指定的地道表达，需要内容管理权限'
    ),
)
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
    permission_classes = [EnglishLearnerPermission]
    throttle_classes = [EnglishExpressionsThrottle]
    
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
    
    def list(self, request, *args, **kwargs):
        """获取表达式列表（带缓存）"""
        # 检查是否有搜索参数
        search_query = request.query_params.get('search', '').strip()
        if search_query:
            # 如果有搜索，使用搜索逻辑
            return self.search(request)
        
        # 尝试从缓存获取
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        filters = {
            'difficulty_level': request.query_params.get('difficulty_level'),
            'tags': request.query_params.get('tags'),
            'ordering': request.query_params.get('ordering'),
            'source': request.query_params.getlist('source'),
            'expression_type': request.query_params.get('expression_type'),
            'formality_level': request.query_params.get('formality_level'),
        }
        # 移除None值和空列表
        filters = {k: v for k, v in filters.items() if v}
        
        cached_data = EnglishCacheManager.get_expression_list(filters, page, page_size)
        if cached_data:
            logger.debug("返回缓存的表达列表")
            return Response(cached_data)
        
        # 否则返回标准分页列表并缓存结果
        response = super().list(request, *args, **kwargs)
        if response.status_code == 200:
            EnglishCacheManager.set_expression_list(response.data, filters, page, page_size)
            logger.debug("缓存新的表达列表")
        
        return response
    
    def retrieve(self, request, *args, **kwargs):
        """获取表达详情（带缓存）"""
        expression_id = kwargs.get('pk')
        
        # 尝试从缓存获取
        cached_data = EnglishCacheManager.get_expression_detail(expression_id)
        if cached_data:
            logger.debug(f"返回缓存的表达详情: {expression_id}")
            return Response(cached_data)
        
        # 否则从数据库获取并缓存
        response = super().retrieve(request, *args, **kwargs)
        if response.status_code == 200:
            EnglishCacheManager.set_expression_detail(expression_id, response.data)
            logger.debug(f"缓存新的表达详情: {expression_id}")
        
        return response
    
    @extend_schema(
        tags=['Expressions'],
        summary='搜索地道表达',
        description='根据关键词搜索地道表达，支持模糊匹配',
        parameters=[
            OpenApiParameter('q', OpenApiTypes.STR, description='搜索关键词', required=True),
            OpenApiParameter('limit', OpenApiTypes.INT, description='返回数量限制，最大50'),
        ]
    )
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
    
    @extend_schema(
        tags=['Expressions'],
        summary='获取随机地道表达',
        description='随机返回一个地道表达，支持按难度级别过滤',
        parameters=[
            OpenApiParameter('difficulty_level', OpenApiTypes.STR, description='难度级别过滤')
        ],
        examples=[
            OpenApiExample(
                'Random Expression',
                summary='随机表达示例',
                description='随机获取一个中级难度表达',
                request_only=False,
                response_only=True,
                value={
                    'id': 1,
                    'expression': 'break the ice',
                    'meaning': '打破沉默，缓解尴尬气氛',
                    'difficulty_level': 'intermediate'
                }
            )
        ]
    )
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
    
    @extend_schema(
        tags=['Management'],
        summary='批量创建地道表达',
        description='批量创建多个地道表达，需要内容管理权限',
        request=IdiomaticExpressionBatchSerializer,
        examples=[
            OpenApiExample(
                'Batch Create',
                summary='批量创建示例',
                description='批量创建两个表达',
                value={
                    'expressions': [
                        {
                            'expression': 'break the ice',
                            'meaning': '打破沉默',
                            'difficulty_level': 'intermediate'
                        },
                        {
                            'expression': 'piece of cake',
                            'meaning': '小菜一碟',
                            'difficulty_level': 'beginner'
                        }
                    ]
                }
            )
        ]
    )
    @action(detail=False, methods=['post'], 
            permission_classes=[EnglishContentManagerPermission],
            throttle_classes=[EnglishManagementThrottle])
    def batch_create(self, request):
        """批量创建表达式"""
        if not isinstance(request.data, list):
            return Response(
                {'error': '批量创建需要提供列表数据'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(request.data) > 100:
            return Response(
                {'error': '批量操作最多支持100条记录'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            serializer = IdiomaticExpressionBatchSerializer()
            expressions = serializer.create_batch(request.data)
            
            # 返回创建的表达式
            result_serializer = IdiomaticExpressionListSerializer(expressions, many=True)
            return Response({
                'created_count': len(expressions),
                'expressions': result_serializer.data
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            logger.error(f"批量创建表达式失败: {str(e)}")
            return Response(
                {'error': '批量创建失败，请检查数据格式'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['put'], 
            permission_classes=[EnglishContentManagerPermission],
            throttle_classes=[EnglishManagementThrottle])
    def batch_update(self, request):
        """批量更新表达式"""
        if not isinstance(request.data, list):
            return Response(
                {'error': '批量更新需要提供列表数据'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 提取ID列表
        ids = [item.get('id') for item in request.data if item.get('id')]
        if not ids:
            return Response(
                {'error': '批量更新需要提供表达式ID'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 获取要更新的实例
        instances = list(IdiomaticExpression.objects.filter(id__in=ids))
        if len(instances) != len(ids):
            return Response(
                {'error': '部分表达式不存在'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 排序实例以匹配输入数据顺序
        instance_dict = {inst.id: inst for inst in instances}
        ordered_instances = [instance_dict[item['id']] for item in request.data]
        
        try:
            serializer = IdiomaticExpressionBatchSerializer()
            updated_expressions = serializer.update_batch(ordered_instances, request.data)
            
            # 返回更新的表达式
            result_serializer = IdiomaticExpressionListSerializer(updated_expressions, many=True)
            return Response({
                'updated_count': len(updated_expressions),
                'expressions': result_serializer.data
            })
        
        except Exception as e:
            logger.error(f"批量更新表达式失败: {str(e)}")
            return Response(
                {'error': '批量更新失败，请检查数据格式'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def dynamic_fields(self, request):
        """动态字段接口"""
        fields_param = request.query_params.get('fields', '')
        exclude_param = request.query_params.get('exclude', '')
        
        # 清理字段列表
        fields = [f.strip() for f in fields_param.split(',') if f.strip()] if fields_param else None
        exclude = [f.strip() for f in exclude_param.split(',') if f.strip()] if exclude_param else None
        
        queryset = self.get_queryset().order_by('id')  # 添加排序避免分页警告
        
        # 分页
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = IdiomaticExpressionListSerializer(
                page, 
                many=True,
                fields=fields,
                exclude=exclude,
                context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        
        serializer = IdiomaticExpressionListSerializer(
            queryset,
            many=True,
            fields=fields,
            exclude=exclude,
            context={'request': request}
        )
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        tags=['Learning'],
        summary='获取用户学习进度',
        description='获取当前用户的表达学习进度列表'
    ),
    create=extend_schema(
        tags=['Learning'],
        summary='记录学习进度',
        description='记录用户对特定表达的学习进度'
    ),
    retrieve=extend_schema(
        tags=['Learning'],
        summary='获取单个学习进度',
        description='获取用户对特定表达的详细学习进度'
    ),
    update=extend_schema(
        tags=['Learning'],
        summary='更新学习进度',
        description='更新用户的学习进度和掌握程度'
    ),
)
class UserExpressionProgressViewSet(viewsets.ModelViewSet):
    """用户表达式学习进度ViewSet"""
    
    serializer_class = UserExpressionProgressSerializer
    permission_classes = [UserProgressOwnerPermission]
    throttle_classes = [EnglishLearningThrottle]
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
    
    @action(detail=False, methods=['put'])
    def batch_update_progress(self, request):
        """批量更新学习进度"""
        if not isinstance(request.data, list):
            return Response(
                {'error': '批量更新需要提供列表数据'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            serializer = UserProgressBatchSerializer()
            updated_progress = serializer.update_batch(request.user, request.data)
            
            # 返回更新结果
            result_serializer = UserExpressionProgressSerializer(updated_progress, many=True)
            return Response({
                'updated_count': len(updated_progress),
                'progress': result_serializer.data
            })
        
        except Exception as e:
            logger.error(f"批量更新学习进度失败: {str(e)}")
            return Response(
                {'error': '批量更新失败，请检查数据格式'},
                status=status.HTTP_400_BAD_REQUEST
            )


class LearningSessionViewSet(viewsets.GenericViewSet):
    """学习会话ViewSet"""
    
    permission_classes = [EnglishLearnerPermission]
    throttle_classes = [EnglishLearningThrottle]
    
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
    permission_classes = [EnglishLearnerPermission]
    throttle_classes = [EnglishExpressionsThrottle]
    pagination_class = CustomPageNumberPagination
    ordering = ['source_name']


class ExpressionScenarioViewSet(viewsets.ReadOnlyModelViewSet):
    """表达式场景ViewSet（只读）"""
    
    queryset = ExpressionScenario.objects.all()
    serializer_class = ExpressionScenarioSerializer
    permission_classes = [EnglishLearnerPermission]
    throttle_classes = [EnglishExpressionsThrottle]
    pagination_class = CustomPageNumberPagination
    ordering = ['scenario_name']


@extend_schema_view(
    list=extend_schema(exclude=True),  # 不显示list方法
)
class StatisticsViewSet(viewsets.GenericViewSet):
    """学习数据统计ViewSet"""
    
    permission_classes = [EnglishLearnerPermission]
    throttle_classes = [EnglishLearningThrottle]
    
    @extend_schema(
        tags=['Statistics'],
        summary='获取学习统计概览',
        description='获取用户的学习统计数据概览',
        examples=[
            OpenApiExample(
                'Statistics Overview',
                summary='统计概览示例',
                description='用户学习数据统计',
                response_only=True,
                value={
                    'total_expressions': 150,
                    'learned_expressions': 45,
                    'mastery_distribution': {
                        'beginner': 20,
                        'intermediate': 15,
                        'advanced': 10
                    },
                    'learning_streak': 7,
                    'avg_mastery_level': 3.2
                }
            )
        ]
    )
    @action(detail=False, methods=['get'])
    def overview(self, request):
        """获取学习数据总览"""
        # 使用缓存管理器
        cached_data = EnglishCacheManager.get_statistics(request.user.id, 'overview')
        
        if cached_data:
            logger.debug(f"返回缓存的统计数据: 用户 {request.user.id}")
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
        
        # 缓存结果
        EnglishCacheManager.set_statistics(request.user.id, 'overview', data)
        
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
    
    permission_classes = [EnglishLearnerPermission]
    throttle_classes = [EnglishLearningThrottle]
    
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
