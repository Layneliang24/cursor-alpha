from django.utils import timezone
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS

from .models import (
    Word, UserWordProgress, Expression, News,
    LearningPlan, PracticeRecord, PronunciationRecord, LearningStats
)
from .serializers import (
    WordSerializer,
    UserWordProgressSerializer,
    ExpressionSerializer,
    NewsSerializer,
    LearningPlanSerializer,
    PracticeRecordSerializer,
    PronunciationRecordSerializer,
    LearningStatsSerializer,
    WordProgressReviewSerializer,
    LearningOverviewSerializer,
    PracticeQuestionSerializer,
    PracticeSubmissionSerializer,
)
from .services import (
    SM2Algorithm,
    LearningPlanService,
    LearningStatsService,
    PracticeService,
    NewsService,
)
from .pagination import StandardResultsSetPagination
from .permissions import EnglishAccessPermission, EnglishWordManagePermission
try:
    from .tasks import crawl_english_news  # type: ignore
except Exception:
    class _DummyTask:
        def delay(self, *args, **kwargs):
            return None

    crawl_english_news = _DummyTask()


class WordViewSet(viewsets.ModelViewSet):
    queryset = Word.objects.filter(is_deleted=False).order_by('id')
    serializer_class = WordSerializer
    permission_classes = [IsAuthenticated, EnglishAccessPermission, EnglishWordManagePermission]
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        # Read: auth + english access; Write: need manage
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated(), EnglishAccessPermission()]
        return [IsAuthenticated(), EnglishAccessPermission(), EnglishWordManagePermission()]

    def get_queryset(self):
        qs = super().get_queryset()
        difficulty = self.request.query_params.get('difficulty_level')
        category = self.request.query_params.get('category')
        q = self.request.query_params.get('q')
        if difficulty:
            qs = qs.filter(difficulty_level=difficulty)
        if category:
            qs = qs.filter(category_hint=category)
        if q:
            qs = qs.filter(Q(word__icontains=q) | Q(definition__icontains=q))
        return qs

    def list(self, request, *args, **kwargs):
        page = self.paginate_queryset(self.get_queryset())
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        data = self.get_serializer(instance).data
        return Response({"success": True, "message": "OK", "data": data})

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": True, "message": "Created", "data": serializer.data}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": True, "message": "OK", "data": serializer.data})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.save(update_fields=['is_deleted', 'deleted_at'])
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserWordProgressViewSet(viewsets.ModelViewSet):
    queryset = UserWordProgress.objects.filter(is_deleted=False).select_related('word').order_by('id')
    serializer_class = UserWordProgressSerializer
    permission_classes = [IsAuthenticated, EnglishAccessPermission]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        page = self.paginate_queryset(self.get_queryset())
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        data = self.get_serializer(instance).data
        return Response({"success": True, "message": "OK", "data": data})

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, last_review_date=timezone.now())

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({"success": True, "message": "OK", "data": serializer.data})

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": True, "message": "OK", "data": serializer.data})

    @action(detail=False, methods=['get'])
    def review(self, request):
        qs = self.get_queryset().filter(next_review_date__lte=timezone.now())
        page = self.paginate_queryset(qs)
        ser = self.get_serializer(page, many=True)
        return self.get_paginated_response(ser.data)

    @action(detail=True, methods=['post'])
    def review(self, request, pk=None):
        instance = self.get_object()
        # quality: 0..5, 默认3
        try:
            quality = int(request.data.get('quality', 3))
        except Exception:
            quality = 3
        quality = max(0, min(5, quality))

        # 更新 mastery 与间隔（简化 SRS 规则）
        mastery = instance.mastery_level or 0.0
        if quality <= 2:
            mastery = max(0.0, mastery - 0.1)
        else:
            mastery = min(1.0, mastery + (quality - 2) * 0.08)

        instance.review_count = (instance.review_count or 0) + 1
        instance.last_review_date = timezone.now()

        if quality <= 2:
            interval_days = 1
        else:
            schedule = [1, 2, 4, 7, 15, 30]
            idx = min(instance.review_count - 1, len(schedule) - 1)
            interval_days = schedule[idx]

        instance.next_review_date = instance.last_review_date + timezone.timedelta(days=interval_days)
        instance.mastery_level = mastery

        if mastery >= 0.8:
            instance.status = 'mastered'
        elif quality <= 2:
            instance.status = 'learning'
        else:
            instance.status = instance.status or 'learning'

        instance.save()
        data = self.get_serializer(instance).data
        return Response({"success": True, "message": "Reviewed", "data": data})

    @action(detail=False, methods=['post'])
    def batch_review(self, request):
        """批量提交复习结果"""
        serializer = WordProgressReviewSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        
        results = []
        for item in serializer.validated_data:
            try:
                word = Word.objects.get(id=item['word_id'])
                progress = SM2Algorithm.update_word_progress(
                    request.user, 
                    word, 
                    item['quality']
                )
                results.append({
                    'word_id': word.id,
                    'success': True,
                    'next_review_date': progress.next_review_date,
                    'mastery_level': progress.mastery_level
                })
            except Word.DoesNotExist:
                results.append({
                    'word_id': item['word_id'],
                    'success': False,
                    'error': '单词不存在'
                })
        
        # 更新每日统计
        LearningStatsService.update_daily_stats(request.user)
        
        return Response({
            'success': True,
            'message': '复习提交成功',
            'data': results
        })

    @action(detail=False, methods=['get'])
    def learning_overview(self, request):
        """获取学习概览"""
        days = int(request.query_params.get('days', 7))
        overview = LearningStatsService.get_learning_overview(request.user, days)
        serializer = LearningOverviewSerializer(overview)
        return Response({
            'success': True,
            'message': 'OK',
            'data': serializer.data
        })


class ExpressionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Expression.objects.filter(is_deleted=False).order_by('id')
    serializer_class = ExpressionSerializer
    permission_classes = [IsAuthenticated, EnglishAccessPermission]
    pagination_class = StandardResultsSetPagination

    def list(self, request, *args, **kwargs):
        page = self.paginate_queryset(self.get_queryset())
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        data = self.get_serializer(instance).data
        return Response({"success": True, "message": "OK", "data": data})


class NewsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = News.objects.filter(is_deleted=False).order_by('-publish_date', '-id')
    serializer_class = NewsSerializer
    permission_classes = [IsAuthenticated, EnglishAccessPermission]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        qs = super().get_queryset()
        category = self.request.query_params.get('category')
        difficulty = self.request.query_params.get('difficulty_level')
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        q = self.request.query_params.get('q')
        if category:
            qs = qs.filter(category=category)
        if difficulty:
            qs = qs.filter(difficulty_level=difficulty)
        if date_from:
            qs = qs.filter(publish_date__gte=date_from)
        if date_to:
            qs = qs.filter(publish_date__lte=date_to)
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(content__icontains=q) | Q(summary__icontains=q))
        return qs

    def list(self, request, *args, **kwargs):
        page = self.paginate_queryset(self.get_queryset())
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        data = self.get_serializer(instance).data
        return Response({"success": True, "message": "OK", "data": data})

    @action(detail=False, methods=['post'])
    def crawl(self, request):
        source = request.data.get('source', 'bbc')
        # 调度celery异步任务
        try:
            crawl_english_news.delay(source)
        except Exception:
            # Celery 未配置时，仍返回接受状态
            pass
        return Response({"success": True, "message": "Crawl accepted", "data": {"source": source}}, status=status.HTTP_202_ACCEPTED)


class LearningPlanViewSet(viewsets.ModelViewSet):
    """学习计划ViewSet"""
    queryset = LearningPlan.objects.filter(is_deleted=False).order_by('-created_at')
    serializer_class = LearningPlanSerializer
    permission_classes = [IsAuthenticated, EnglishAccessPermission]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['get'])
    def daily_words(self, request, pk=None):
        """获取今日学习单词"""
        plan = self.get_object()
        words = LearningPlanService.get_daily_words(request.user, plan)
        serializer = WordSerializer(words, many=True)
        return Response({
            'success': True,
            'message': 'OK',
            'data': serializer.data
        })

    @action(detail=True, methods=['get'])
    def daily_expressions(self, request, pk=None):
        """获取今日学习表达"""
        plan = self.get_object()
        expressions = LearningPlanService.get_daily_expressions(request.user, plan)
        serializer = ExpressionSerializer(expressions, many=True)
        return Response({
            'success': True,
            'message': 'OK',
            'data': serializer.data
        })


class PracticeRecordViewSet(viewsets.ModelViewSet):
    """练习记录ViewSet"""
    queryset = PracticeRecord.objects.all().order_by('-created_at')
    serializer_class = PracticeRecordSerializer
    permission_classes = [IsAuthenticated, EnglishAccessPermission]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def submit_practice(self, request):
        """提交练习答案"""
        serializer = PracticeSubmissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        record = PracticeService.record_practice(
            user=request.user,
            practice_type=data['practice_type'],
            content_id=data['content_id'],
            content_type=data['content_type'],
            question=data['question'],
            user_answer=data['user_answer'],
            correct_answer=data['correct_answer'],
            time_spent=data['time_spent']
        )
        
        result_serializer = PracticeRecordSerializer(record)
        return Response({
            'success': True,
            'message': '练习提交成功',
            'data': result_serializer.data
        })

    @action(detail=False, methods=['get'])
    def generate_questions(self, request):
        """生成练习题目"""
        practice_type = request.query_params.get('type', 'word_spelling')
        count = int(request.query_params.get('count', 5))
        
        questions = []
        if practice_type == 'word_spelling':
            words = Word.objects.filter(is_deleted=False).order_by('?')[:count]
            for word in words:
                question = PracticeService.generate_word_spelling_question(word)
                questions.append(question)
        elif practice_type == 'word_meaning':
            words = Word.objects.filter(is_deleted=False).order_by('?')[:count]
            for word in words:
                question = PracticeService.generate_word_meaning_question(word)
                questions.append(question)
        
        serializer = PracticeQuestionSerializer(questions, many=True)
        return Response({
            'success': True,
            'message': 'OK',
            'data': serializer.data
        })


class PronunciationRecordViewSet(viewsets.ModelViewSet):
    """发音记录ViewSet"""
    queryset = PronunciationRecord.objects.all().order_by('-created_at')
    serializer_class = PronunciationRecordSerializer
    permission_classes = [IsAuthenticated, EnglishAccessPermission]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class LearningStatsViewSet(viewsets.ReadOnlyModelViewSet):
    """学习统计ViewSet"""
    queryset = LearningStats.objects.all().order_by('-date')
    serializer_class = LearningStatsSerializer
    permission_classes = [IsAuthenticated, EnglishAccessPermission]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def update_today(self, request):
        """更新今日统计"""
        stats = LearningStatsService.update_daily_stats(request.user)
        serializer = self.get_serializer(stats)
        return Response({
            'success': True,
            'message': '统计更新成功',
            'data': serializer.data
        })
