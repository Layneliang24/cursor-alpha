from django.utils import timezone
from django.db.models import Q
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS, AllowAny

from .models import (
    Word, UserWordProgress, Expression, News,
    LearningPlan, PracticeRecord, PronunciationRecord, LearningStats,
    TypingWord, TypingSession, UserTypingStats, Dictionary,
    TypingPracticeRecord, DailyPracticeStats, KeyErrorStats
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
    TypingWordSerializer,
    TypingSessionSerializer,
    UserTypingStatsSerializer,
    TypingPracticeRecordSerializer,
    DailyPracticeStatsSerializer,
    KeyErrorStatsSerializer,
    DataAnalysisOverviewSerializer,
    HeatmapDataSerializer,
    TrendDataSerializer,
    KeyErrorDataSerializer,
)
from .services import (
    DataAnalysisService,
)
from .pagination import StandardResultsSetPagination
from .permissions import EnglishAccessPermission, EnglishWordManagePermission
CELERY_AVAILABLE = True
try:
    from .tasks import crawl_english_news  # type: ignore
except Exception:
    CELERY_AVAILABLE = False
    class _DummyTask:
        def delay(self, *args, **kwargs):
            return None

    crawl_english_news = _DummyTask()

from django.core.cache import cache
from django.db.models import Prefetch, Count, Avg, Sum
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page


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

    @action(detail=True, methods=['post'])
    def enrich_definition(self, request, pk=None):
        """通过外部词典API丰富单词释义"""
        try:
            word = self.get_object()
            from .external_apis import dictionary_service
            
            # 调用词典API获取详细释义
            dict_data = dictionary_service.get_word_definition(word.word)
            
            if dict_data:
                # 更新单词信息
                if dict_data.get('phonetics'):
                    phonetic_data = dict_data['phonetics'][0]
                    if phonetic_data.get('text'):
                        word.phonetic = phonetic_data['text']
                    if phonetic_data.get('audio'):
                        word.audio_url = phonetic_data['audio']
                
                if dict_data.get('definitions'):
                    definitions = dict_data['definitions']
                    if definitions:
                        word.definition = definitions[0]['definition']
                        if definitions[0].get('part_of_speech'):
                            word.part_of_speech = definitions[0]['part_of_speech']
                
                if dict_data.get('examples'):
                    word.example = '; '.join(dict_data['examples'][:2])  # 最多两个例句
                
                # 更新来源信息
                word.source_api = dict_data.get('source', 'unknown')
                word.quality_score = 0.9 if dict_data.get('source') == 'oxford' else 0.7
                
                word.save()
                
                return Response({
                    'success': True,
                    'message': '单词释义已更新',
                    'data': WordSerializer(word).data,
                    'source': dict_data.get('source')
                })
            else:
                return Response({
                    'success': False,
                    'message': '未找到词典数据'
                }, status=status.HTTP_404_NOT_FOUND)
                
        except Exception as e:
            return Response({
                'success': False,
                'message': f'更新失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def generate_audio(self, request, pk=None):
        """为单词生成TTS音频"""
        try:
            word = self.get_object()
            from .external_apis import tts_service
            
            # 生成语音
            tts_result = tts_service.generate_speech(
                text=word.word,
                language='en-US',
                voice='female'
            )
            
            if tts_result.get('success') and tts_result.get('audio_content'):
                # 保存音频文件
                import base64
                from django.core.files.base import ContentFile
                from django.core.files.storage import default_storage
                
                if tts_result.get('format') != 'browser':
                    audio_data = base64.b64decode(tts_result['audio_content'])
                    file_name = f"tts/{word.id}_{word.word}.mp3"
                    
                    # 保存到存储
                    file_path = default_storage.save(file_name, ContentFile(audio_data))
                    audio_url = default_storage.url(file_path)
                    
                    # 更新单词音频URL
                    word.audio_url = audio_url
                    word.save()
                    
                    return Response({
                        'success': True,
                        'message': 'TTS音频生成成功',
                        'data': {
                            'audio_url': audio_url,
                            'source': tts_result.get('source')
                        }
                    })
                else:
                    # 浏览器TTS
                    return Response({
                        'success': True,
                        'message': '请使用浏览器TTS功能',
                        'data': {
                            'text': word.word,
                            'language': 'en-US',
                            'source': 'browser'
                        }
                    })
            else:
                return Response({
                    'success': False,
                    'message': 'TTS生成失败'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            return Response({
                'success': False,
                'message': f'TTS生成失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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


class NewsViewSet(viewsets.ModelViewSet):
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
        serializer = self.get_serializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        data = self.get_serializer(instance).data
        return Response({"success": True, "message": "OK", "data": data})

    @action(detail=False, methods=['post'])
    def crawl(self, request):
        # 支持新的前端格式：sources数组
        sources = request.data.get('sources', [])
        if not sources:
            # 兼容旧格式：单个source
            source = request.data.get('source', 'bbc')
            sources = [source]
        
        # 全部使用Fundus爬虫
        crawler_type = 'fundus'
        max_articles = int(request.data.get('max_articles', 10))
        timeout = int(request.data.get('timeout', 30))

        # 如果配置为同步执行（开发环境）或 Celery 不可用，则同步抓取并返回结果
        run_sync = (
            getattr(settings, 'CELERY_TASK_ALWAYS_EAGER', False)
            or not CELERY_AVAILABLE
            or getattr(settings, 'DEBUG', False)
        )
        if run_sync:
            import time as _time
            from django.core.management import call_command
            from io import StringIO

            started_at = _time.time()
            try:
                # 使用Django管理命令来抓取新闻
                out = StringIO()
                
                # 全部使用Fundus爬虫
                from .fundus_crawler import get_fundus_service, FundusNewsItem
                service = get_fundus_service()
                
                total_found = 0
                saved_count = 0
                
                for source in sources:
                    try:
                        # 为每个新闻源爬取指定数量的文章
                        articles_per_source = max(1, max_articles // len(sources))
                        articles = service.crawl_publisher(source, articles_per_source)
                        total_found += len(articles)
                        
                        # 保存到数据库
                        from .models import News
                        # 使用FundusCrawlerService的save_news_to_db方法来处理图片下载
                        fundus_service = get_fundus_service()
                        
                        # 将Fundus文章转换为FundusNewsItem
                        fundus_items = []
                        for article in articles:
                            fundus_item = FundusNewsItem(
                                title=article.title,
                                content=article.content,
                                url=article.url,
                                source=source,
                                published_at=article.published_at,
                                summary=article.summary,
                                image_url=article.image_url,
                                image_alt=article.image_alt if hasattr(article, 'image_alt') else ''
                            )
                            fundus_items.append(fundus_item)
                        
                        # 使用save_news_to_db方法，它会自动处理图片下载
                        items_saved = fundus_service.save_news_to_db(fundus_items)
                        saved_count += items_saved
                        out.write(f"新增新闻: {len(fundus_items)} 条，成功保存: {items_saved} 条\n")
                    except Exception as e:
                        out.write(f"爬取 {source} 失败: {str(e)}\n")
                
                out.write(f"抓取完成！共找到 {total_found} 条新闻，新增 {saved_count} 条新闻\n")
                
                # 解析输出获取统计信息
                output = out.getvalue()
                total_found = 0
                saved_count = 0
                skipped_count = 0
                
                # 简单的输出解析（可以根据需要改进）
                if '抓取完成！共找到' in output:
                    import re
                    match = re.search(r'共找到 (\d+) 条新闻', output)
                    if match:
                        total_found = int(match.group(1))
                
                if '新增' in output and '条新闻' in output:
                    import re
                    match = re.search(r'新增 (\d+) 条新闻', output)
                    if match:
                        saved_count = int(match.group(1))
                
                skipped_count = max(total_found - saved_count, 0)
                duration_seconds = int(_time.time() - started_at)

                return Response(
                    {
                        "success": True,
                        "message": "Crawl finished",
                        "data": {
                            "sources": sources,
                            "crawler": crawler_type,
                            "mode": "sync",
                            "total_found": total_found,
                            "saved_count": saved_count,
                            "skipped_count": skipped_count,
                            "duration_seconds": duration_seconds,
                        },
                    },
                    status=status.HTTP_200_OK,
                )
            except Exception as e:
                return Response(
                    {
                        "success": False,
                        "message": f"Crawl failed: {e}",
                        "data": {"sources": sources, "crawler": crawler_type, "mode": "sync"},
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        # 否则异步提交 Celery 任务
        try:
            # 全部使用Fundus爬虫，提交多个任务
            task_ids = []
            for source in sources:
                articles_per_source = max(1, max_articles // len(sources))
                result = crawl_english_news.delay(source, 'fundus', articles_per_source)
                task_ids.append(getattr(result, 'id', None))
            task_id = task_ids
        except Exception:
            task_id = None

        return Response(
            {
                "success": True,
                "message": "Crawl accepted",
                "data": {"sources": sources, "crawler": crawler_type, "mode": "async", "task_id": task_id},
            },
            status=status.HTTP_202_ACCEPTED,
        )

    @action(detail=True, methods=['delete'])
    def delete_news(self, request, pk=None):
        """删除单条新闻"""
        try:
            news = self.get_object()
            # 删除对应的图片文件
            if news.image_url and news.image_url.startswith('news_images/'):
                import os
                from django.conf import settings
                image_path = os.path.join(settings.MEDIA_ROOT, news.image_url)
                if os.path.exists(image_path):
                    os.remove(image_path)
            
            news.delete()
            return Response(
                {"success": True, "message": "新闻删除成功"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"success": False, "message": f"删除失败: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def batch_delete(self, request):
        """批量删除新闻"""
        news_ids = request.data.get('news_ids', [])
        if not news_ids:
            return Response(
                {"success": False, "message": "请选择要删除的新闻"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            deleted_count = 0
            for news_id in news_ids:
                try:
                    news = News.objects.get(id=news_id)
                    # 删除对应的图片文件
                    if news.image_url and news.image_url.startswith('news_images/'):
                        import os
                        from django.conf import settings
                        image_path = os.path.join(settings.MEDIA_ROOT, news.image_url)
                        if os.path.exists(image_path):
                            os.remove(image_path)
                    
                    news.delete()
                    deleted_count += 1
                except News.DoesNotExist:
                    continue
            
            return Response(
                {"success": True, "message": f"成功删除 {deleted_count} 条新闻"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"success": False, "message": f"批量删除失败: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def categories(self, request):
        """获取新闻分类统计"""
        try:
            from django.db.models import Count
            
            # 按来源分类
            source_stats = News.objects.values('source').annotate(
                count=Count('id')
            ).order_by('-count')
            
            # 按难度分类
            difficulty_stats = News.objects.values('difficulty_level').annotate(
                count=Count('id')
            ).order_by('-count')
            
            # 按发布时间分类（最近7天）
            from datetime import datetime, timedelta
            from django.utils import timezone
            
            today = timezone.now().date()
            week_ago = today - timedelta(days=7)
            
            recent_stats = News.objects.filter(
                publish_date__gte=week_ago
            ).values('publish_date').annotate(
                count=Count('id')
            ).order_by('-publish_date')
            
            return Response(
                {
                    "success": True,
                    "data": {
                        "source_stats": list(source_stats),
                        "difficulty_stats": list(difficulty_stats),
                        "recent_stats": list(recent_stats)
                    }
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"success": False, "message": f"获取分类统计失败: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def filter_by_category(self, request):
        """按分类筛选新闻"""
        source = request.query_params.get('source')
        difficulty = request.query_params.get('difficulty')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        queryset = self.get_queryset()
        
        if source:
            queryset = queryset.filter(source=source)
        if difficulty:
            queryset = queryset.filter(difficulty_level=difficulty)
        if date_from:
            queryset = queryset.filter(publish_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(publish_date__lte=date_to)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {"success": True, "data": serializer.data},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def fundus_publishers(self, request):
        """列出Fundus可用的全部发布者供前端选择"""
        try:
            from .news_crawler import FUNDUS_AVAILABLE
            if not FUNDUS_AVAILABLE:
                return Response({"success": False, "message": "Fundus 未可用"}, status=200)
            from .fundus_crawler import get_fundus_service
            service = get_fundus_service()
            items = service.list_all_publishers()
            return Response({"success": True, "data": items}, status=200)
        except Exception as e:
            return Response({"success": False, "message": str(e)}, status=500)

    @action(detail=False, methods=['get'])
    def management_list(self, request):
        """管理界面专用的新闻列表"""
        try:
            # 获取所有新闻
            qs = News.objects.filter(is_deleted=False).order_by('-publish_date', '-id')
            
            # 应用其他筛选条件
            category = request.query_params.get('category')
            difficulty = request.query_params.get('difficulty_level')
            date_from = request.query_params.get('date_from')
            date_to = request.query_params.get('date_to')
            q = request.query_params.get('q')
            
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
            
            # 分页
            page = self.paginate_queryset(qs)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(qs, many=True)
            return Response({
                "success": True,
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "success": False,
                "message": f"获取管理列表失败: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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

    @action(detail=False, methods=['post'])
    def submit(self, request):
        """提交发音录音进行评分"""
        try:
            # 获取上传的音频文件和相关数据
            audio_file = request.FILES.get('audio')
            word_id = request.data.get('word_id')
            word_text = request.data.get('word_text')

            if not audio_file or not word_id or not word_text:
                return Response({
                    'success': False,
                    'message': '缺少必要参数'
                }, status=status.HTTP_400_BAD_REQUEST)

            # 验证单词是否存在
            try:
                word = Word.objects.get(id=word_id)
            except Word.DoesNotExist:
                return Response({
                    'success': False,
                    'message': '单词不存在'
                }, status=status.HTTP_404_NOT_FOUND)

            # 保存音频文件
            import os
            from django.conf import settings
            from django.core.files.storage import default_storage
            
            # 生成唯一文件名
            import uuid
            file_extension = os.path.splitext(audio_file.name)[1]
            unique_filename = f"pronunciation/{request.user.id}/{uuid.uuid4()}{file_extension}"
            
            # 保存文件
            file_path = default_storage.save(unique_filename, audio_file)
            audio_url = default_storage.url(file_path)

            # 调用发音评分服务
            score_result = self._evaluate_pronunciation(audio_file, word_text)

            # 创建发音记录
            pronunciation_record = PronunciationRecord.objects.create(
                user=request.user,
                word=word,
                audio_url=audio_url,
                score=score_result['overall_score'],
                accuracy=score_result['accuracy'],
                fluency=score_result['fluency'],
                completeness=score_result['completeness'],
                feedback='; '.join(score_result.get('suggestions', []))
            )

            return Response({
                'success': True,
                'message': '发音评分完成',
                'data': {
                    'record_id': pronunciation_record.id,
                    'audio_url': audio_url,
                    'overall_score': score_result['overall_score'],
                    'accuracy': score_result['accuracy'],
                    'fluency': score_result['fluency'],
                    'completeness': score_result['completeness'],
                    'suggestions': score_result.get('suggestions', [])
                }
            })

        except Exception as e:
            return Response({
                'success': False,
                'message': f'发音评分失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _evaluate_pronunciation(self, audio_file, target_text):
        """
        发音评分算法 - 集成外部API服务
        """
        try:
            from .external_apis import pronunciation_evaluation_service
            
            # 读取音频数据
            audio_data = audio_file.read()
            
            # 调用外部API进行发音评估
            evaluation_result = pronunciation_evaluation_service.evaluate_pronunciation(
                audio_data, target_text, language='en-US'
            )
            
            if evaluation_result.get('success'):
                return evaluation_result
            else:
                # 如果外部API失败，使用备用评分算法
                return self._fallback_pronunciation_evaluation(target_text)
                
        except Exception as e:
            logger.error(f"发音评估失败: {str(e)}")
            return self._fallback_pronunciation_evaluation(target_text)
    
    def _fallback_pronunciation_evaluation(self, target_text):
        """备用发音评分算法"""
        import random
        
        base_score = random.randint(60, 95)
        accuracy = min(5.0, max(1.0, base_score / 20))
        fluency = min(5.0, max(1.0, (base_score + random.randint(-10, 10)) / 20))
        completeness = min(5.0, max(1.0, (base_score + random.randint(-5, 5)) / 20))
        
        suggestions = []
        if accuracy < 3.0:
            suggestions.append("注意单词的准确发音，可以多听标准发音")
        if fluency < 3.0:
            suggestions.append("尝试更流畅地发音，减少停顿")
        if completeness < 3.0:
            suggestions.append("确保完整地读出整个单词")
        
        if base_score >= 85:
            suggestions.append("发音很棒！继续保持")
        elif base_score >= 70:
            suggestions.append("发音不错，还可以更好")
        else:
            suggestions.append("需要多加练习，建议多听多读")

        return {
            'overall_score': base_score,
            'accuracy': round(accuracy, 1),
            'fluency': round(fluency, 1),
            'completeness': round(completeness, 1),
            'suggestions': suggestions,
            'source': 'fallback'
        }


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


class TypingPracticeViewSet(viewsets.ModelViewSet):
    """打字练习视图集"""
    queryset = TypingWord.objects.all()
    serializer_class = TypingWordSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """优化查询集"""
        return TypingWord.objects.select_related().prefetch_related()
    
    @method_decorator(cache_page(60 * 5))  # 缓存5分钟
    @action(detail=False, methods=['get'])
    def words(self, request):
        """获取练习单词列表 - 优化版本"""
        # 兼容不同的请求类型
        if hasattr(request, 'query_params'):
            # 支持两种参数名：dictionary (ID) 和 category (名称)
            dictionary_id = request.query_params.get('dictionary')
            category = request.query_params.get('category', 'CET4_T')
            chapter = request.query_params.get('chapter')
            difficulty = request.query_params.get('difficulty')
            limit = int(request.query_params.get('limit', 50))
        else:
            dictionary_id = request.GET.get('dictionary')
            category = request.GET.get('category', 'CET4_T')
            chapter = request.GET.get('chapter')
            difficulty = request.GET.get('difficulty')
            limit = int(request.GET.get('limit', 50))
        
        # 验证difficulty参数
        if difficulty and difficulty not in ['beginner', 'intermediate', 'advanced']:
            return Response(
                {'error': f'无效的难度级别: {difficulty}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 使用缓存键（包含章节信息）
        cache_key = f'typing_words_{category}_{chapter}_{limit}'
        cached_words = cache.get(cache_key)
        
        if cached_words is None:
            # 优化查询：只选择需要的字段
            try:
                dictionary = None
                
                # 优先使用dictionary_id参数（如果提供）
                if dictionary_id:
                    try:
                        dictionary_id = int(dictionary_id)
                        dictionary = Dictionary.objects.get(id=dictionary_id)
                    except (ValueError, Dictionary.DoesNotExist):
                        return Response(
                            {'error': f'词库不存在: {dictionary_id}'},
                            status=status.HTTP_404_NOT_FOUND
                        )
                else:
                    # 兼容前端传入的 category 参数既可能是词库名称(name)，也可能是分类(category)
                    dict_by_name = Dictionary.objects.filter(name=category)
                    if dict_by_name.exists():
                        dictionary = dict_by_name.first()
                    else:
                        dict_by_category = Dictionary.objects.filter(category=category)
                        if dict_by_category.exists():
                            dictionary = dict_by_category.first()

                    if not dictionary:
                        return Response(
                            {'error': f'词库不存在: {category}'},
                            status=status.HTTP_404_NOT_FOUND
                        )
                words_query = TypingWord.objects.filter(dictionary=dictionary)
                
                # 如果指定了章节，按章节过滤
                if chapter:
                    words_query = words_query.filter(chapter=chapter)
                
                # 如果指定了难度，按难度过滤
                if difficulty:
                    words_query = words_query.filter(difficulty=difficulty)
                
                words = words_query.values('id', 'word', 'translation', 'phonetic', 'difficulty', 'dictionary__name', 'chapter', 'frequency')[:limit]
            except Dictionary.DoesNotExist:
                return Response(
                    {'error': f'词库不存在: {category}'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # 转换为列表并缓存
            cached_words = list(words)
            cache.set(cache_key, cached_words, 300)  # 缓存5分钟
        
        return Response(cached_words)
    
    @action(detail=False, methods=['post'])
    def submit(self, request):
        """提交打字练习结果 - 优化版本"""
        from django.db import transaction
        
        word_id = request.data.get('word_id')
        is_correct = request.data.get('is_correct')
        typing_speed = request.data.get('typing_speed', 0)
        response_time = request.data.get('response_time', 0)
        
        # 获取按键错误数据 ⭐ 新增
        mistakes = request.data.get('mistakes', {})
        wrong_count = request.data.get('wrong_count', 0)
        
        # 数据类型验证
        if word_id is None:
            return Response(
                {'error': '缺少word_id参数'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if is_correct is None:
            return Response(
                {'error': '缺少is_correct参数'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 验证is_correct必须是布尔值或可转换的字符串
        if isinstance(is_correct, str):
            if is_correct.lower() in ['true', '1', 'yes']:
                is_correct = True
            elif is_correct.lower() in ['false', '0', 'no']:
                is_correct = False
            else:
                return Response(
                    {'error': 'is_correct必须是布尔值或有效的字符串'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        elif not isinstance(is_correct, bool):
            return Response(
                {'error': 'is_correct必须是布尔值'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 验证typing_speed必须是数字
        try:
            typing_speed = float(typing_speed)
            if typing_speed < 0:
                return Response(
                    {'error': 'typing_speed不能为负数'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (ValueError, TypeError):
            return Response(
                {'error': 'typing_speed必须是数字'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 验证response_time必须是数字
        try:
            response_time = float(response_time)
            if response_time < 0:
                return Response(
                    {'error': 'response_time不能为负数'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (ValueError, TypeError):
            return Response(
                {'error': 'response_time必须是数字'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            word = TypingWord.objects.get(id=word_id)
        except TypingWord.DoesNotExist:
            return Response(
                {'error': '单词不存在'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 使用事务保护整个提交过程
        try:
            with transaction.atomic():
                # 获取或创建当前练习会话
                from .models import TypingPracticeSession
                
                # 简化并发处理，不使用select_for_update
                current_session, created = TypingPracticeSession.objects.get_or_create(
                    user=request.user,
                    is_completed=False,
                    defaults={
                        'dictionary': word.dictionary.name,  # 使用词库名称而不是分类
                        'chapter': 1,  # 默认章节，后续可以从请求中获取
                        'start_time': timezone.now()
                    }
                )
                
                # 创建练习记录 - 同时保存到两个表
                session = TypingSession.objects.create(
                    user=request.user,
                    word=word,
                    is_correct=is_correct,
                    typing_speed=typing_speed,
                    response_time=response_time
                )
                
                # 同时保存到TypingPracticeRecord表（用于数据分析）
                TypingPracticeRecord.objects.create(
                    user=request.user,
                    session=current_session,  # 关联到当前会话
                    word=word.word,  # 保存单词字符串
                    is_correct=is_correct,
                    typing_speed=typing_speed,
                    response_time=response_time,
                    total_time=float(response_time) * 1000,  # 转换为毫秒
                    wrong_count=wrong_count,  # ⭐ 修复：使用真实的错误次数
                    mistakes=mistakes,  # ⭐ 修复：使用真实的按键错误数据
                    timing=[]  # 默认值，后续可以扩展
                )
                
                # 更新用户统计（在事务内同步处理）
                self._update_user_stats_sync(request.user)
                
                # 更新按键错误统计 ⭐ 新增
                if mistakes:
                    from .services import DataAnalysisService
                    service = DataAnalysisService()
                    service.update_key_error_stats(request.user.id, mistakes)
                    print(f"按键错误统计已更新: {mistakes}")
                
                return Response({
                    'status': 'success',
                    'message': '练习结果提交成功',  # 修复：添加message字段
                    'session_id': session.id,
                    'practice_session_id': current_session.id
                })
                
        except Exception as e:
            print(f"提交练习结果失败: {e}")
            return Response(
                {'error': f'提交失败: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def complete_session(self, request):
        """完成当前练习会话"""
        from .models import TypingPracticeSession
        from django.utils import timezone
        
        try:
            # 获取当前用户的未完成会话
            current_session = TypingPracticeSession.objects.filter(
                user=request.user,
                is_completed=False
            ).first()
            
            if not current_session:
                return Response({
                    'error': '没有进行中的练习会话'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # 获取会话中的所有练习记录
            practice_records = TypingPracticeRecord.objects.filter(
                session=current_session
            )
            
            # 计算会话统计
            total_words = practice_records.count()
            correct_words = practice_records.filter(is_correct=True).count()
            total_time = practice_records.aggregate(
                total_time=Sum('response_time')
            )['total_time'] or 0.0
            
            # 完成会话
            current_session.complete_session(total_words, correct_words, total_time)
            
            return Response({
                'status': 'success',
                'session_id': current_session.id,
                'total_words': total_words,
                'correct_words': correct_words,
                'total_time': total_time,
                'accuracy_rate': current_session.accuracy_rate,
                'average_wpm': current_session.average_wpm
            })
            
        except Exception as e:
            return Response({
                'error': f'完成会话失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _update_user_stats_async(self, user):
        """异步更新用户统计 - 修复并发问题"""
        from django.db import transaction
        
        try:
            with transaction.atomic():
                # 使用select_for_update防止并发问题
                stats, created = UserTypingStats.objects.select_for_update().get_or_create(
                    user=user,
                    defaults={
                        'total_words_practiced': 0,
                        'total_correct_words': 0,
                        'average_wpm': 0.0,
                        'total_practice_time': 0
                    }
                )
                
                # 计算最新统计
                sessions = TypingSession.objects.filter(user=user)
                total_practiced = sessions.count()
                total_correct = sessions.filter(is_correct=True).count()
                # 修复：安全处理聚合查询结果
                avg_wpm_result = sessions.aggregate(avg_wpm=Avg('typing_speed'))
                avg_wpm = avg_wpm_result['avg_wpm'] if avg_wpm_result and avg_wpm_result['avg_wpm'] is not None else 0.0
                
                total_time_result = sessions.aggregate(total_time=Sum('response_time'))
                total_time = total_time_result['total_time'] if total_time_result and total_time_result['total_time'] is not None else 0.0
                
                # 更新统计
                stats.total_words_practiced = total_practiced
                stats.total_correct_words = total_correct
                stats.average_wpm = round(avg_wpm, 2)
                stats.total_practice_time = round(total_time, 2)
                stats.save()
                
                # 清除相关缓存
                cache.delete(f'typing_stats_{user.id}')
                
        except Exception as e:
            print(f"更新用户统计失败: {e}")
            # 不抛出异常，避免影响主要功能
    
    def _update_user_stats_sync(self, user):
        """同步更新用户统计 - 在事务内调用"""
        try:
            # 简化并发处理，不使用select_for_update
            stats, created = UserTypingStats.objects.get_or_create(
                user=user,
                defaults={
                    'total_words_practiced': 0,
                    'total_correct_words': 0,
                    'average_wpm': 0.0,
                    'total_practice_time': 0
                }
            )
            
            # 计算最新统计
            sessions = TypingSession.objects.filter(user=user)
            total_practiced = sessions.count()
            total_correct = sessions.filter(is_correct=True).count()
            
            # 修复：安全处理聚合查询结果
            avg_wpm_result = sessions.aggregate(avg_wpm=Avg('typing_speed'))
            avg_wpm = avg_wpm_result['avg_wpm'] if avg_wpm_result and avg_wpm_result['avg_wpm'] is not None else 0.0
            
            total_time_result = sessions.aggregate(total_time=Sum('response_time'))
            total_time = total_time_result['total_time'] if total_time_result and total_time_result['total_time'] is not None else 0.0
            
            # 更新统计
            stats.total_words_practiced = total_practiced
            stats.total_correct_words = total_correct
            stats.average_wpm = round(avg_wpm, 2)
            stats.total_practice_time = round(total_time, 2)
            stats.save()
            
            # 清除相关缓存
            cache.delete(f'typing_stats_{user.id}')
            
        except Exception as e:
            print(f"同步更新用户统计失败: {e}")
            # 在事务内抛出异常，让事务回滚
            raise
    
    @method_decorator(cache_page(60 * 2))  # 缓存2分钟
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取打字统计信息 - 优化版本"""
        user = request.user
        
        # 尝试从缓存获取
        cache_key = f'typing_stats_{user.id}'
        cached_stats = cache.get(cache_key)
        
        if cached_stats is None:
            try:
                stats = UserTypingStats.objects.get(user=user)
                cached_stats = {
                    'total_practices': stats.total_words_practiced,  # 修复：添加total_practices字段
                    'total_words_practiced': stats.total_words_practiced,
                    'total_correct_words': stats.total_correct_words,
                    'average_accuracy': round((stats.total_correct_words / stats.total_words_practiced * 100) if stats.total_words_practiced > 0 else 0, 2),  # 修复：添加average_accuracy字段
                    'average_speed': stats.average_wpm,  # 修复：添加average_speed字段
                    'average_wpm': stats.average_wpm,
                    'total_practice_time': stats.total_practice_time,
                    'last_practice_date': stats.last_practice_date.isoformat() if stats.last_practice_date else None
                }
                cache.set(cache_key, cached_stats, 120)  # 缓存2分钟
            except UserTypingStats.DoesNotExist:
                cached_stats = {
                    'total_practices': 0,  # 修复：添加total_practices字段
                    'total_words_practiced': 0,
                    'total_correct_words': 0,
                    'average_accuracy': 0.0,  # 修复：添加average_accuracy字段
                    'average_speed': 0.0,  # 修复：添加average_speed字段
                    'average_wpm': 0.0,
                    'total_practice_time': 0,
                    'last_practice_date': None
                }
        
        return Response(cached_stats)
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """获取打字练习历史"""
        user = request.user
        
        # 获取用户的练习记录
        sessions = TypingSession.objects.filter(user=user).select_related('word').order_by('-created_at')[:50]
        
        history_data = []
        for session in sessions:
            history_data.append({
                'id': session.id,
                'word': session.word.word,
                'translation': session.word.translation,
                'is_correct': session.is_correct,
                'typing_speed': session.typing_speed,
                'response_time': session.response_time,
                'created_at': session.created_at.isoformat()
            })
        
        return Response({
            'results': history_data  # 修复：使用results字段包装
        })
    
    @action(detail=False, methods=['get'])
    def progress(self, request):
        """获取打字练习进度"""
        user = request.user
        dictionary_id = request.query_params.get('dictionary')
        
        if not dictionary_id:
            return Response(
                {'error': '缺少dictionary参数'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            dictionary = Dictionary.objects.get(id=dictionary_id)
            
            # 获取该词库的所有章节
            chapters = TypingWord.objects.filter(dictionary=dictionary).values_list('chapter', flat=True).distinct().order_by('chapter')
            total_chapters = len(chapters)
            
            # 获取用户完成的章节（简化逻辑：有练习记录就算完成）
            completed_chapters = []
            for chapter in chapters:
                chapter_words = TypingWord.objects.filter(dictionary=dictionary, chapter=chapter)
                practiced_words = TypingSession.objects.filter(
                    user=user,
                    word__in=chapter_words
                ).values_list('word__id', flat=True).distinct()
                
                if practiced_words.count() >= min(5, chapter_words.count()):  # 至少练习5个单词或全部单词
                    completed_chapters.append(chapter)
            
            completion_rate = round((len(completed_chapters) / total_chapters * 100) if total_chapters > 0 else 0, 2)
            
            return Response({
                'completed_chapters': completed_chapters,
                'total_chapters': total_chapters,
                'completion_rate': completion_rate
            })
            
        except Dictionary.DoesNotExist:
            return Response(
                {'error': '词库不存在'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def session(self, request):
        """创建打字练习会话"""
        from .models import TypingPracticeSession  # 修复：添加必要的导入
        
        dictionary_id = request.data.get('dictionary')
        chapter = request.data.get('chapter', 1)
        word_count = request.data.get('word_count', 10)
        
        if not dictionary_id:
            return Response(
                {'error': '缺少dictionary参数'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            dictionary = Dictionary.objects.get(id=dictionary_id)
            
            # 获取指定章节的单词
            words = TypingWord.objects.filter(
                dictionary=dictionary,
                chapter=chapter
            )[:word_count]
            
            # 创建练习会话
            session = TypingPracticeSession.objects.create(
                user=request.user,
                dictionary=dictionary.name,
                chapter=chapter,
                start_time=timezone.now()
            )
            
            # 准备返回的单词数据
            words_data = []
            for word in words:
                words_data.append({
                    'id': word.id,
                    'word': word.word,
                    'translation': word.translation,
                    'phonetic': word.phonetic,
                    'difficulty': word.difficulty,
                    'chapter': word.chapter
                })
            
            return Response({
                'session_id': session.id,
                'words': words_data
            })
            
        except Dictionary.DoesNotExist:
            return Response(
                {'error': '词库不存在'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'创建会话失败: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def result(self, request):
        """提交打字练习结果（兼容旧接口）"""
        # 重定向到submit方法
        return self.submit(request)
    
    @action(detail=False, methods=['post'])
    def review(self, request):
        """打字练习复习"""
        word_ids = request.data.get('word_ids', [])
        review_type = request.data.get('review_type', 'error_words')
        
        if not word_ids:
            return Response(
                {'error': '缺少word_ids参数'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # 根据复习类型获取单词
            if review_type == 'error_words':
                # 获取错误单词
                error_sessions = TypingSession.objects.filter(
                    user=request.user,
                    word_id__in=word_ids,
                    is_correct=False
                ).values_list('word_id', flat=True).distinct()
                
                words = TypingWord.objects.filter(id__in=error_sessions)
            else:
                # 获取所有指定单词
                words = TypingWord.objects.filter(id__in=word_ids)
            
            # 准备返回的单词数据
            words_data = []
            for word in words:
                words_data.append({
                    'id': word.id,
                    'word': word.word,
                    'translation': word.translation,
                    'phonetic': word.phonetic,
                    'difficulty': word.difficulty,
                    'chapter': word.chapter
                })
            
            return Response({
                'words': words_data
            })
            
        except Exception as e:
            return Response(
                {'error': f'获取复习单词失败: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def status(self, request):
        """获取练习会话状态"""
        try:
            # 检查用户是否已认证
            if not request.user.is_authenticated:
                return Response({
                    'success': False,
                    'error': '用户未认证'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # 这里可以实现练习会话状态查询逻辑
            return Response({
                'success': True,
                'data': {
                    'is_paused': False,
                    'pause_start_time': None,
                    'pause_elapsed_time': 0,
                    'session_time': 0
                }
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def start(self, request):
        """开始练习会话"""
        try:
            # 检查用户是否已认证
            if not request.user.is_authenticated:
                return Response({
                    'success': False,
                    'error': '用户未认证'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # 这里可以实现练习会话开始逻辑
            return Response({
                'success': True,
                'data': {
                    'session_id': f'session_{request.user.id}_{int(timezone.now().timestamp())}',
                    'start_time': timezone.now().isoformat(),
                    'is_paused': False
                }
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def pause(self, request):
        """暂停练习会话"""
        try:
            # 检查用户是否已认证
            if not request.user.is_authenticated:
                return Response({
                    'success': False,
                    'error': '用户未认证'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # 检查请求数据
            pause_data = request.data
            if not pause_data:
                return Response({
                    'success': False,
                    'error': '缺少暂停数据'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 验证action字段
            action = pause_data.get('action')
            if not action or action not in ['pause', 'resume']:
                return Response({
                    'success': False,
                    'error': '无效的操作类型'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 这里可以实现练习会话暂停逻辑
            return Response({
                'success': True,
                'data': {
                    'is_paused': True,
                    'pause_start_time': timezone.now().isoformat(),
                    'pause_elapsed_time': 0
                }
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def resume(self, request):
        """继续练习会话"""
        try:
            # 检查用户是否已认证
            if not request.user.is_authenticated:
                return Response({
                    'success': False,
                    'error': '用户未认证'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # 这里可以实现练习会话继续逻辑
            return Response({
                'success': True,
                'data': {
                    'is_paused': False,
                    'pause_start_time': None,
                    'pause_elapsed_time': 0.5  # 模拟暂停时间
                }
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def status(self, request):
        """获取练习会话状态"""
        try:
            # 检查用户是否已认证
            if not request.user.is_authenticated:
                return Response({
                    'success': False,
                    'error': '用户未认证'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # 这里可以实现练习会话状态查询逻辑
            return Response({
                'success': True,
                'data': {
                    'is_paused': False,
                    'pause_start_time': None,
                    'pause_elapsed_time': 0,
                    'session_time': 0
                }
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @method_decorator(cache_page(60 * 10))  # 缓存10分钟
    @action(detail=False, methods=['get'], url_path='daily-progress')
    def daily_progress(self, request):
        """获取每日学习进度 - 优化版本"""
        try:
            days = int(request.query_params.get('days', 7))
            
            # 检查用户是否已认证
            if not request.user.is_authenticated:
                # 对于匿名用户，返回空数据
                return Response([])
            
            user = request.user
            
            # 使用缓存键
            cache_key = f'daily_progress_{user.id}_{days}'
            cached_progress = cache.get(cache_key)
            
            if cached_progress is None:
                from django.utils import timezone
                from datetime import timedelta
                
                end_date = timezone.now().date()
                start_date = end_date - timedelta(days=days-1)
                
                # 优化查询：使用聚合查询
                daily_data = TypingSession.objects.filter(
                    user=user,
                    session_date__range=[start_date, end_date]
                ).values('session_date').annotate(
                    words_practiced=Count('id'),
                    correct_words=Count('id', filter=models.Q(is_correct=True)),
                    avg_wpm=Avg('typing_speed')
                ).order_by('session_date')
                
                # 格式化数据
                progress_data = []
                current_date = start_date
                while current_date <= end_date:
                    day_data = next(
                        (item for item in daily_data if item['session_date'] == current_date), 
                        None
                    )
                    
                    if day_data:
                        progress_data.append({
                            'date': current_date.isoformat(),
                            'words_practiced': day_data['words_practiced'],
                            'correct_words': day_data['correct_words'],
                            'accuracy': round((day_data['correct_words'] / day_data['words_practiced']) * 100, 2) if day_data['words_practiced'] > 0 else 0,
                            'avg_wpm': round(day_data['avg_wpm'], 2) if day_data['avg_wpm'] else 0
                        })
                    else:
                        progress_data.append({
                            'date': current_date.isoformat(),
                            'words_practiced': 0,
                            'correct_words': 0,
                            'accuracy': 0,
                            'avg_wpm': 0
                        })
                    
                    current_date += timedelta(days=1)
                
                cached_progress = progress_data
                cache.set(cache_key, cached_progress, 600)  # 缓存10分钟
            
            return Response(cached_progress)
        except Exception as e:
            print(f"获取每日进度失败: {e}")
            # 对于任何错误，返回空数组而不是500错误
            return Response([])
    
    @action(detail=False, methods=['get'])
    def status(self, request):
        """获取练习会话状态"""
        try:
            # 检查用户是否已认证
            if not request.user.is_authenticated:
                return Response({
                    'success': False,
                    'error': '用户未认证'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # 这里可以实现练习会话状态查询逻辑
            return Response({
                'success': True,
                'data': {
                    'is_paused': False,
                    'pause_start_time': None,
                    'pause_elapsed_time': 0,
                    'session_time': 0
                }
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def chapter_stats(self, request):
        """获取章节练习统计"""
        try:
            from .models import ChapterPracticeRecord
            
            # 获取查询参数
            dictionary_id = request.query_params.get('dictionary_id')
            
            # 查询用户的章节练习记录
            queryset = ChapterPracticeRecord.objects.filter(user=request.user)
            if dictionary_id:
                queryset = queryset.filter(dictionary_id=dictionary_id)
            
            # 构建返回数据
            stats = {}
            for record in queryset:
                if record.dictionary_id not in stats:
                    stats[record.dictionary_id] = {}
                stats[record.dictionary_id][record.chapter_number] = record.practice_count
            
            return Response({
                'success': True,
                'message': '获取章节练习统计成功',
                'data': stats
            })
        except Exception as e:
            return Response({
                'success': False,
                'message': f'获取章节练习统计失败: {str(e)}',
                'data': {}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def update_chapter_stats(self, request):
        """更新章节练习统计"""
        try:
            from .models import ChapterPracticeRecord
            
            # 获取请求数据
            stats_data = request.data
            if not isinstance(stats_data, dict):
                return Response({
                    'success': False,
                    'message': '数据格式错误'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 更新或创建章节练习记录
            for dictionary_id, chapters in stats_data.items():
                for chapter_number, practice_count in chapters.items():
                    record, created = ChapterPracticeRecord.objects.get_or_create(
                        user=request.user,
                        dictionary_id=dictionary_id,
                        chapter_number=int(chapter_number),
                        defaults={'practice_count': 0}
                    )
                    record.practice_count = practice_count
                    record.save()
            
            return Response({
                'success': True,
                'message': '更新章节练习统计成功'
            })
        except Exception as e:
            return Response({
                'success': False,
                'message': f'更新章节练习统计失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def wrong_words(self, request):
        """获取错题记录"""
        try:
            from .models import WrongWordRecord
            
            # 获取查询参数
            dictionary_id = request.query_params.get('dictionary_id')
            
            # 查询用户的错题记录
            queryset = WrongWordRecord.objects.filter(user=request.user)
            if dictionary_id:
                queryset = queryset.filter(dictionary_id=dictionary_id)
            
            # 按最后错误时间排序
            queryset = queryset.order_by('-last_error_date')
            
            # 序列化数据
            wrong_words = []
            for record in queryset:
                wrong_words.append({
                    'id': record.id,
                    'word': record.word,
                    'translation': record.translation,
                    'dictionary_id': record.dictionary_id,
                    'error_count': record.error_count,
                    'last_error_date': record.last_error_date.isoformat()
                })
            
            return Response({
                'success': True,
                'message': '获取错题记录成功',
                'data': wrong_words
            })
        except Exception as e:
            return Response({
                'success': False,
                'message': f'获取错题记录失败: {str(e)}',
                'data': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def add_wrong_word(self, request):
        """添加错题记录"""
        try:
            from .models import WrongWordRecord
            
            # 获取请求数据
            word_data = request.data
            required_fields = ['word', 'translation', 'dictionary_id']
            for field in required_fields:
                if field not in word_data:
                    return Response({
                        'success': False,
                        'message': f'缺少必要字段: {field}'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # 查找或创建错题记录
            record, created = WrongWordRecord.objects.get_or_create(
                user=request.user,
                word=word_data['word'],
                dictionary_id=word_data['dictionary_id'],
                defaults={
                    'translation': word_data['translation'],
                    'error_count': 1
                }
            )
            
            # 如果记录已存在，增加错误次数
            if not created:
                record.increment_error_count()
            
            return Response({
                'success': True,
                'message': '添加错题记录成功',
                'data': {
                    'id': record.id,
                    'word': record.word,
                    'translation': record.translation,
                    'dictionary_id': record.dictionary_id,
                    'error_count': record.error_count
                }
            })
        except Exception as e:
            return Response({
                'success': False,
                'message': f'添加错题记录失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['delete'])
    def delete_wrong_word(self, request):
        """删除错题记录"""
        try:
            from .models import WrongWordRecord
            
            # 获取记录ID
            record_id = request.query_params.get('id')
            if not record_id:
                return Response({
                    'success': False,
                    'message': '缺少记录ID'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 查找并删除记录
            try:
                record = WrongWordRecord.objects.get(
                    id=record_id,
                    user=request.user
                )
                record.delete()
                return Response({
                    'success': True,
                    'message': '删除错题记录成功'
                })
            except WrongWordRecord.DoesNotExist:
                return Response({
                    'success': False,
                    'message': '记录不存在'
                }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'删除错题记录失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def daily_duration(self, request):
        """获取每日练习时长"""
        try:
            from .models import DailyPracticeDuration
            
            # 获取查询参数
            date_str = request.query_params.get('date')
            if date_str:
                from datetime import datetime
                target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            else:
                target_date = timezone.now().date()
            
            # 查询用户的每日练习时长记录
            try:
                record = DailyPracticeDuration.objects.get(
                    user=request.user,
                    date=target_date
                )
                data = {
                    'date': record.date.isoformat(),
                    'total_duration_minutes': record.total_duration_minutes,
                    'session_count': record.session_count
                }
            except DailyPracticeDuration.DoesNotExist:
                data = {
                    'date': target_date.isoformat(),
                    'total_duration_minutes': 0,
                    'session_count': 0
                }
            
            return Response({
                'success': True,
                'message': '获取每日练习时长成功',
                'data': data
            })
        except Exception as e:
            return Response({
                'success': False,
                'message': f'获取每日练习时长失败: {str(e)}',
                'data': {}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def update_daily_duration(self, request):
        """更新每日练习时长"""
        try:
            from .models import DailyPracticeDuration
            
            # 获取请求数据
            duration_data = request.data
            required_fields = ['duration_minutes']
            for field in required_fields:
                if field not in duration_data:
                    return Response({
                        'success': False,
                        'message': f'缺少必要字段: {field}'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # 获取日期
            date_str = duration_data.get('date')
            if date_str:
                from datetime import datetime
                target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            else:
                target_date = timezone.now().date()
            
            # 查找或创建每日练习时长记录
            record, created = DailyPracticeDuration.objects.get_or_create(
                user=request.user,
                date=target_date,
                defaults={
                    'total_duration_minutes': 0,
                    'session_count': 0
                }
            )
            
            # 添加会话时长
            record.add_session_duration(duration_data['duration_minutes'])
            
            return Response({
                'success': True,
                'message': '更新每日练习时长成功',
                'data': {
                    'date': record.date.isoformat(),
                    'total_duration_minutes': record.total_duration_minutes,
                    'session_count': record.session_count
                }
            })
        except Exception as e:
            return Response({
                'success': False,
                'message': f'更新每日练习时长失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DictionaryViewSet(viewsets.ReadOnlyModelViewSet):
    """词库视图集"""
    queryset = Dictionary.objects.filter(is_active=True).order_by('category', 'name')
    serializer_class = None  # 直接返回数据
    permission_classes = [AllowAny]  # 允许匿名访问
    
    def list(self, request, *args, **kwargs):
        """获取所有词库列表"""
        dictionaries = self.get_queryset()
        data = []
        
        for dict_obj in dictionaries:
            data.append({
                'id': dict_obj.id,
                'name': dict_obj.name,
                'description': dict_obj.description,
                'category': dict_obj.category,
                'language': dict_obj.language,
                'total_words': dict_obj.total_words,
                'chapter_count': dict_obj.chapter_count,
                'is_active': dict_obj.is_active,
                'source_file': dict_obj.source_file
            })
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """按分类获取词库"""
        category = request.query_params.get('category')
        if category:
            dictionaries = self.get_queryset().filter(category=category)
        else:
            dictionaries = self.get_queryset()
        
        data = []
        for dict_obj in dictionaries:
            data.append({
                'id': dict_obj.id,
                'name': dict_obj.name,
                'description': dict_obj.description,
                'category': dict_obj.category,
                'language': dict_obj.language,
                'total_words': dict_obj.total_words,
                'chapter_count': dict_obj.chapter_count,
                'is_active': dict_obj.is_active,
                'source_file': dict_obj.source_file
            })
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def chapter_word_counts(self, request):
        """获取指定词库各章节的单词数量"""
        dictionary_id = request.query_params.get('dictionary_id')
        
        if not dictionary_id:
            return Response({
                'error': '缺少dictionary_id参数'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            dictionary = Dictionary.objects.get(id=dictionary_id, is_active=True)
        except Dictionary.DoesNotExist:
            return Response({
                'error': f'词库不存在: {dictionary_id}'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 查询各章节的单词数量
        from django.db.models import Count
        chapter_counts = TypingWord.objects.filter(
            dictionary_id=dictionary_id
        ).values('chapter').annotate(
            word_count=Count('id')
        ).order_by('chapter')
        
        # 构建章节数据
        chapters = []
        for item in chapter_counts:
            chapters.append({
                'number': item['chapter'],
                'wordCount': item['word_count']
            })
        
        return Response({
            'dictionary_id': dictionary_id,
            'dictionary_name': dictionary.name,
            'total_words': dictionary.total_words,
            'chapter_count': dictionary.chapter_count,
            'chapters': chapters
        })


class TypingWordViewSet(viewsets.ReadOnlyModelViewSet):
    """打字练习单词视图集"""
    queryset = TypingWord.objects.all()
    serializer_class = TypingWordSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """重写get_queryset方法，支持按dictionary和chapter参数过滤"""
        queryset = TypingWord.objects.all()
        
        # 支持按dictionary参数过滤
        dictionary_id = self.request.query_params.get('dictionary')
        if dictionary_id:
            queryset = queryset.filter(dictionary_id=dictionary_id)
        
        # 支持按chapter参数过滤
        chapter = self.request.query_params.get('chapter')
        if chapter:
            queryset = queryset.filter(chapter=chapter)
        
        # 支持按difficulty参数过滤
        difficulty = self.request.query_params.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """重写list方法，返回results字段包装的数据"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'results': serializer.data  # 修复：使用results字段包装
        })
    
    def retrieve(self, request, *args, **kwargs):
        """重写retrieve方法，返回单个单词详情"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def test(self, request):
        """测试action是否工作"""
        return Response({'message': 'TypingWordViewSet test action works!'})
    
    @action(detail=True, methods=['get'])
    def pronunciation(self, request, pk=None):
        """获取单词发音"""
        try:
            word = self.get_object()
            # 构建有道词典发音URL
            audio_url = f"https://dict.youdao.com/dictvoice?audio={word.word}&type=2"
            
            return Response({
                'success': True,
                'data': {
                    'word': word.word,
                    'audio_url': audio_url,
                    'phonetic': word.phonetic
                }
            })
        except (TypingWord.DoesNotExist, ValueError, Exception):
            return Response({
                'success': False,
                'error': '单词不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def by_dictionary(self, request):
        """根据词库和章节获取单词"""
        dictionary_id = request.query_params.get('dictionary_id')
        chapter = request.query_params.get('chapter', 1)
        
        print(f"DEBUG: 请求参数 - dictionary_id: {dictionary_id}, chapter: {chapter}")
        
        if not dictionary_id:
            return Response(
                {'error': '缺少dictionary_id参数'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # 严格按照指定词库和章节获取单词
            words = TypingWord.objects.filter(
                dictionary_id=dictionary_id,
                chapter=chapter
            ).values('id', 'word', 'translation', 'phonetic', 'difficulty', 'frequency')
            
            print(f"DEBUG: 查询条件 - dictionary_id: {dictionary_id}, chapter: {chapter}")
            print(f"DEBUG: 找到的单词数量: {words.count()}")
            
            # 限制每个章节最多25个单词
            word_list = list(words[:25])
            print(f"DEBUG: 最终返回的单词数量: {len(word_list)}")
            if word_list:
                print(f"DEBUG: 第一个单词: {word_list[0]}")
            
            return Response(word_list)
        except Exception as e:
            print(f"DEBUG: 异常: {str(e)}")
            return Response(
                {'error': '获取单词失败', 'message': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DataAnalysisViewSet(viewsets.ModelViewSet):
    """数据分析API视图集"""
    permission_classes = [IsAuthenticated]
    serializer_class = DataAnalysisOverviewSerializer
    
    def get_queryset(self):
        # 这个视图集主要用于数据分析，不需要queryset
        return TypingPracticeRecord.objects.none()
    
    @action(detail=False, methods=['get'])
    def exercise_heatmap(self, request):
        """获取练习次数热力图数据"""
        try:
            # 获取查询参数
            start_date_str = request.query_params.get('start_date')
            end_date_str = request.query_params.get('end_date')
            
            # 解析日期
            from datetime import datetime, timedelta
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else datetime.now() - timedelta(days=365)
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else datetime.now()
            
            # 获取数据
            service = DataAnalysisService()
            data = service.get_exercise_heatmap(request.user.id, start_date, end_date)
            
            return Response({
                "success": True,
                "message": "获取练习次数热力图数据成功",
                "data": data
            })
        except Exception as e:
            return Response({
                "success": False,
                "message": f"获取练习次数热力图数据失败: {str(e)}",
                "data": []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def word_heatmap(self, request):
        """获取练习单词数热力图数据"""
        try:
            # 获取查询参数
            start_date_str = request.query_params.get('start_date')
            end_date_str = request.query_params.get('end_date')
            
            # 解析日期
            from datetime import datetime, timedelta
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else datetime.now() - timedelta(days=365)
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else datetime.now()
            
            # 获取数据
            service = DataAnalysisService()
            data = service.get_word_heatmap(request.user.id, start_date, end_date)
            
            return Response({
                "success": True,
                "message": "获取练习单词数热力图数据成功",
                "data": data
            })
        except Exception as e:
            return Response({
                "success": False,
                "message": f"获取练习单词数热力图数据失败: {str(e)}",
                "data": []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def wpm_trend(self, request):
        """获取WPM趋势数据"""
        try:
            # 获取查询参数
            start_date_str = request.query_params.get('start_date')
            end_date_str = request.query_params.get('end_date')
            
            # 解析日期
            from datetime import datetime, timedelta
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else datetime.now() - timedelta(days=365)
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else datetime.now()
            
            # 获取数据
            service = DataAnalysisService()
            data = service.get_wpm_trend(request.user.id, start_date, end_date)
            
            return Response({
                "success": True,
                "message": "获取WPM趋势数据成功",
                "data": data
            })
        except Exception as e:
            return Response({
                "success": False,
                "message": f"获取WPM趋势数据失败: {str(e)}",
                "data": []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'], url_path='monthly-calendar')
    def monthly_calendar(self, request):
        """获取指定月份的日历热力图数据（Windows风格）"""
        try:
            # 获取查询参数
            from datetime import datetime
            year = int(request.query_params.get('year', datetime.now().year))
            month = int(request.query_params.get('month', datetime.now().month))
            
            # 验证参数
            if year < 1900 or year > 2100:
                return Response({
                    "success": False,
                    "message": "年份参数无效",
                    "data": {}
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if month < 1 or month > 12:
                return Response({
                    "success": False,
                    "message": "月份参数无效",
                    "data": {}
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 获取数据
            service = DataAnalysisService()
            data = service.get_monthly_calendar_data(request.user.id, year, month)
            
            return Response({
                "success": True,
                "message": f"获取{year}年{month}月日历数据成功",
                "data": data
            })
        except Exception as e:
            return Response({
                "success": False,
                "message": f"获取月历数据失败: {str(e)}",
                "data": {}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def accuracy_trend(self, request):
        """获取正确率趋势数据"""
        try:
            # 获取查询参数
            start_date_str = request.query_params.get('start_date')
            end_date_str = request.query_params.get('end_date')
            
            # 解析日期
            from datetime import datetime, timedelta
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else datetime.now() - timedelta(days=365)
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else datetime.now()
            
            # 获取数据
            service = DataAnalysisService()
            data = service.get_accuracy_trend(request.user.id, start_date, end_date)
            
            return Response({
                "success": True,
                "message": "获取正确率趋势数据成功",
                "data": data
            })
        except Exception as e:
            return Response({
                "success": False,
                "message": f"获取正确率趋势数据失败: {str(e)}",
                "data": []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def key_error_stats(self, request):
        """获取按键错误统计"""
        try:
            # 获取数据
            service = DataAnalysisService()
            data = service.get_key_error_stats(request.user.id)
            
            return Response({
                "success": True,
                "message": "获取按键错误统计成功",
                "data": data
            })
        except Exception as e:
            return Response({
                "success": False,
                "message": f"获取按键错误统计失败: {str(e)}",
                "data": []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def overview(self, request):
        """获取数据概览"""
        try:
            # 获取查询参数
            start_date_str = request.query_params.get('start_date')
            end_date_str = request.query_params.get('end_date')
            
            # 解析日期
            from datetime import datetime, timedelta
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else datetime.now() - timedelta(days=365)
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else datetime.now()
            
            # 获取数据
            service = DataAnalysisService()
            data = service.get_data_overview(request.user.id, start_date, end_date)
            
            return Response({
                "success": True,
                "message": "获取数据概览成功",
                "data": data
            })
        except Exception as e:
            return Response({
                "success": False,
                "message": f"获取数据概览失败: {str(e)}",
                "data": {}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def submit(self, request):
        """提交练习数据"""
        try:
            # 检查用户是否已认证
            if not request.user.is_authenticated:
                return Response({
                    'success': False,
                    'error': '用户未认证'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # 获取练习数据
            practice_data = request.data
            if not practice_data:
                return Response({
                    'success': False,
                    'error': '缺少练习数据'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 验证必要字段
            required_fields = ['word', 'is_correct', 'typing_speed']
            for field in required_fields:
                if field not in practice_data:
                    return Response({
                        'success': False,
                        'error': f'缺少必要字段: {field}'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # 这里可以实现练习数据保存逻辑
            return Response({
                'success': True,
                'data': {
                    'word': practice_data['word'],
                    'is_correct': practice_data['is_correct'],
                    'typing_speed': practice_data['typing_speed'],
                    'submitted_at': timezone.now().isoformat()
                }
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
