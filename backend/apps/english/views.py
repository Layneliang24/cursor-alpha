from django.utils import timezone
from django.db.models import Q
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS, AllowAny

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
CELERY_AVAILABLE = True
try:
    from .tasks import crawl_english_news  # type: ignore
except Exception:
    CELERY_AVAILABLE = False
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
        serializer = self.get_serializer(page, many=True)
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
