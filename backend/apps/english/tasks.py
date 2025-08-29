"""
Celery异步任务
包含爬虫任务、数据处理任务和维护任务
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from celery import shared_task, current_task
from celery.exceptions import Retry
from django.utils import timezone
from django.db import transaction
from django.core.cache import cache

from .expression_crawler import ExpressionCrawlerService
from .specialized_crawlers import register_specialized_crawlers
from .data_quality import data_processor
from .news_crawler import real_news_crawler_service
from .models import IdiomaticExpression, ExpressionSource, NewsItem

logger = logging.getLogger(__name__)


class TaskStatus:
    """任务状态常量"""
    PENDING = 'PENDING'
    STARTED = 'STARTED' 
    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'
    RETRY = 'RETRY'
    REVOKED = 'REVOKED'


class TaskPriority:
    """任务优先级常量"""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


def update_task_progress(current: int, total: int, description: str = ""):
    """更新任务进度"""
    if current_task:
        current_task.update_state(
            state='PROGRESS',
            meta={
                'current': current,
                'total': total,
                'description': description,
                'percentage': int((current / total) * 100) if total > 0 else 0
            }
        )


def get_task_lock_key(task_name: str, params: str = "") -> str:
    """生成任务锁的缓存键"""
    return f"task_lock:{task_name}:{params}"


def acquire_task_lock(task_name: str, params: str = "", timeout: int = 3600) -> bool:
    """获取任务锁，防止重复执行"""
    lock_key = get_task_lock_key(task_name, params)
    return cache.add(lock_key, timezone.now().isoformat(), timeout)


def release_task_lock(task_name: str, params: str = ""):
    """释放任务锁"""
    lock_key = get_task_lock_key(task_name, params)
    cache.delete(lock_key)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def crawl_expressions_task(self, sources: List[str] = None, max_items_per_source: int = 50, quality_threshold: float = 0.6):
    """
    异步爬取地道表达任务
    
    Args:
        sources: 数据源列表，如['cambridge', 'collins']
        max_items_per_source: 每个源的最大抓取数量
        quality_threshold: 质量阈值
    """
    task_id = self.request.id
    lock_key = f"crawl_expressions:{'-'.join(sources or ['all'])}"
    
    # 检查任务锁
    if not acquire_task_lock('crawl_expressions', lock_key):
        logger.warning(f"爬取表达式任务已在运行: {lock_key}")
        return {
            'status': 'skipped',
            'message': '任务已在运行中',
            'task_id': task_id
        }
    
    try:
        logger.info(f"开始爬取地道表达任务 [{task_id}]")
        
        # 初始化爬虫服务
        crawler_service = ExpressionCrawlerService()
        register_specialized_crawlers(crawler_service)
        
        # 获取可用的爬虫
        available_crawlers = list(crawler_service.crawlers.keys())
        target_sources = sources or available_crawlers
        
        # 过滤不存在的源
        valid_sources = [s for s in target_sources if s in available_crawlers]
        if not valid_sources:
            raise ValueError(f"没有找到有效的数据源: {target_sources}")
        
        logger.info(f"目标数据源: {valid_sources}")
        
        total_sources = len(valid_sources)
        all_items = []
        source_results = {}
        
        for i, source in enumerate(valid_sources):
            try:
                update_task_progress(i, total_sources, f"正在爬取 {source}")
                
                logger.info(f"开始爬取 {source}")
                crawler = crawler_service.crawlers[source]
                
                # 爬取数据
                items = crawler.crawl_expressions(max_items=max_items_per_source)
                
                # 数据质量处理
                processing_results = data_processor.process_expression_items(items, quality_threshold)
                
                accepted_items = processing_results['accepted']
                all_items.extend(accepted_items)
                
                source_results[source] = {
                    'total_crawled': len(items),
                    'accepted': len(accepted_items),
                    'rejected_quality': len(processing_results['rejected_quality']),
                    'rejected_duplicate': len(processing_results['rejected_duplicate']),
                    'rejected_invalid': len(processing_results['rejected_invalid'])
                }
                
                logger.info(f"{source} 爬取完成: {len(accepted_items)}/{len(items)} 通过质量检查")
                
            except Exception as e:
                logger.error(f"爬取 {source} 失败: {str(e)}")
                source_results[source] = {
                    'error': str(e),
                    'total_crawled': 0,
                    'accepted': 0
                }
        
        # 保存到数据库
        update_task_progress(total_sources, total_sources, "正在保存到数据库")
        
        saved_count = 0
        if all_items:
            saved_count = crawler_service.save_expressions_to_db(all_items)
        
        # 生成质量报告
        quality_report = data_processor.generate_quality_report({
            'accepted': all_items,
            'rejected_quality': [],
            'rejected_duplicate': [],
            'rejected_invalid': []
        })
        
        result = {
            'status': 'success',
            'task_id': task_id,
            'total_crawled': sum(r.get('total_crawled', 0) for r in source_results.values()),
            'total_accepted': len(all_items),
            'total_saved': saved_count,
            'sources': source_results,
            'quality_report': quality_report,
            'execution_time': timezone.now().isoformat()
        }
        
        logger.info(f"爬取表达式任务完成 [{task_id}]: {saved_count} 条新数据")
        return result
        
    except Exception as exc:
        logger.error(f"爬取表达式任务失败 [{task_id}]: {str(exc)}")
        
        # 重试机制
        if self.request.retries < self.max_retries:
            logger.info(f"任务将在 {self.default_retry_delay} 秒后重试 (第 {self.request.retries + 1} 次)")
            raise self.retry(exc=exc, countdown=self.default_retry_delay)
        
        return {
            'status': 'failed',
            'task_id': task_id,
            'error': str(exc),
            'retries': self.request.retries
        }
    
    finally:
        release_task_lock('crawl_expressions', lock_key)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def crawl_news_task(self, source: str = 'bbc', crawler_type: str = 'traditional', max_articles: int = 20):
    """
    异步爬取新闻任务
    
    Args:
        source: 新闻源
        crawler_type: 爬虫类型 ('traditional', 'fundus', 'both')
        max_articles: 最大文章数量
    """
    task_id = self.request.id
    lock_key = f"{source}:{crawler_type}"
    
    # 检查任务锁
    if not acquire_task_lock('crawl_news', lock_key):
        logger.warning(f"爬取新闻任务已在运行: {lock_key}")
        return {
            'status': 'skipped',
            'message': '任务已在运行中',
            'task_id': task_id
        }
    
    try:
        logger.info(f"开始爬取新闻任务 [{task_id}]: {source} ({crawler_type})")
        
        update_task_progress(0, 1, f"正在爬取 {source} 新闻")
        
        all_news_items = []
        
        # 传统爬虫
        if crawler_type in ['traditional', 'both']:
            if source == 'all':
                traditional_items = real_news_crawler_service.crawl_all_sources()
            else:
                traditional_items = real_news_crawler_service.crawl_news(source)
                if max_articles and isinstance(max_articles, int):
                    traditional_items = traditional_items[:max_articles]
            all_news_items.extend(traditional_items)
        
        # Fundus爬虫 (如果可用)
        if crawler_type in ['fundus', 'both']:
            try:
                from .fundus_crawler import get_fundus_service, FUNDUS_AVAILABLE
                if FUNDUS_AVAILABLE:
                    fundus_service = get_fundus_service()
                    if source == 'all':
                        fundus_items = fundus_service.crawl_all_supported(max_articles_per_publisher=max_articles)
                    else:
                        fundus_items = fundus_service.crawl_publisher(source, max_articles)
                    all_news_items.extend(fundus_items)
                else:
                    logger.warning("Fundus不可用，跳过Fundus爬虫")
            except ImportError:
                logger.warning("Fundus模块不可用")
        
        if not all_news_items:
            logger.warning(f"未抓取到任何 {source} 新闻")
            return {
                'status': 'success',
                'task_id': task_id,
                'total_crawled': 0,
                'total_saved': 0,
                'message': f'未抓取到任何 {source} 新闻'
            }
        
        # 保存到数据库
        update_task_progress(1, 1, "正在保存到数据库")
        
        saved_count = 0
        
        # 分别保存传统爬虫和Fundus爬虫的结果
        traditional_sources = ['BBC', 'CNN', 'Reuters', 'TechCrunch', 'China Daily', 'Xinhua', 'Generated']
        
        if crawler_type in ['traditional', 'both']:
            traditional_items = [item for item in all_news_items if hasattr(item, 'source') and item.source in traditional_sources]
            if traditional_items:
                saved_count += real_news_crawler_service.save_news_to_db(traditional_items)
        
        if crawler_type in ['fundus', 'both']:
            fundus_items = [item for item in all_news_items if hasattr(item, 'source') and item.source not in traditional_sources]
            if fundus_items:
                try:
                    from .fundus_crawler import get_fundus_service
                    fundus_service = get_fundus_service()
                    saved_count += fundus_service.save_news_to_db(fundus_items)
                except ImportError:
                    logger.warning("无法保存Fundus新闻：模块不可用")
        
        result = {
            'status': 'success',
            'task_id': task_id,
            'source': source,
            'crawler_type': crawler_type,
            'total_crawled': len(all_news_items),
            'total_saved': saved_count,
            'skipped': len(all_news_items) - saved_count,
            'execution_time': timezone.now().isoformat()
        }
        
        logger.info(f"爬取新闻任务完成 [{task_id}]: {saved_count}/{len(all_news_items)} 条新数据")
        return result
        
    except Exception as exc:
        logger.error(f"爬取新闻任务失败 [{task_id}]: {str(exc)}")
        
        # 重试机制
        if self.request.retries < self.max_retries:
            logger.info(f"任务将在 {self.default_retry_delay} 秒后重试 (第 {self.request.retries + 1} 次)")
            raise self.retry(exc=exc, countdown=self.default_retry_delay)
        
        return {
            'status': 'failed',
            'task_id': task_id,
            'error': str(exc),
            'retries': self.request.retries
        }
    
    finally:
        release_task_lock('crawl_news', lock_key)


@shared_task(bind=True)
def process_data_quality_task(self, expression_ids: List[int] = None, quality_threshold: float = 0.6):
    """
    异步数据质量处理任务
    
    Args:
        expression_ids: 要处理的表达式ID列表，None表示处理所有
        quality_threshold: 质量阈值
    """
    task_id = self.request.id
    
    try:
        logger.info(f"开始数据质量处理任务 [{task_id}]")
        
        # 获取要处理的表达式
        if expression_ids:
            expressions = IdiomaticExpression.objects.filter(id__in=expression_ids)
        else:
            expressions = IdiomaticExpression.objects.all()
        
        total_count = expressions.count()
        if total_count == 0:
            return {
                'status': 'success',
                'task_id': task_id,
                'message': '没有找到需要处理的表达式'
            }
        
        processed_count = 0
        updated_count = 0
        
        for i, expression in enumerate(expressions.iterator()):
            update_task_progress(i, total_count, f"处理表达式: {expression.expression}")
            
            try:
                # 转换为ExpressionItem进行质量评估
                from .expression_crawler import ExpressionItem
                
                item = ExpressionItem(
                    expression=expression.expression,
                    meaning=expression.meaning,
                    source_url=expression.source.source_url if expression.source else '',
                    source_name=expression.source.source_name if expression.source else '',
                    usage_examples=expression.usage_examples or [],
                    scenarios=[link.scenario.scenario_name for link in expression.scenario_links.all()],
                    phonetic_transcription=expression.phonetic_transcription or '',
                    expression_type=expression.expression_type,
                    formality_level=expression.formality_level,
                    frequency_score=expression.frequency_score,
                    cultural_background=expression.cultural_background or '',
                    metadata=expression.metadata or {}
                )
                
                # 质量评估
                quality_scores = data_processor.quality_assessor.assess_expression_quality(item)
                is_high_quality = quality_scores['overall'] >= quality_threshold
                
                # 更新数据库记录
                if expression.metadata != quality_scores or not hasattr(expression, 'quality_checked'):
                    expression.metadata = {
                        **(expression.metadata or {}),
                        'quality_scores': quality_scores,
                        'is_high_quality': is_high_quality,
                        'quality_checked_at': timezone.now().isoformat()
                    }
                    expression.save(update_fields=['metadata'])
                    updated_count += 1
                
                processed_count += 1
                
            except Exception as e:
                logger.error(f"处理表达式 {expression.id} 失败: {str(e)}")
        
        result = {
            'status': 'success',
            'task_id': task_id,
            'total_expressions': total_count,
            'processed_count': processed_count,
            'updated_count': updated_count,
            'quality_threshold': quality_threshold,
            'execution_time': timezone.now().isoformat()
        }
        
        logger.info(f"数据质量处理任务完成 [{task_id}]: {updated_count}/{processed_count} 条数据更新")
        return result
        
    except Exception as exc:
        logger.error(f"数据质量处理任务失败 [{task_id}]: {str(exc)}")
        return {
            'status': 'failed',
            'task_id': task_id,
            'error': str(exc)
        }


@shared_task
def cleanup_old_data():
    """清理过期数据任务"""
    try:
        logger.info("开始清理过期数据")
        
        # 清理30天前的新闻
        cutoff_date = timezone.now() - timedelta(days=30)
        old_news_count = NewsItem.objects.filter(created_at__lt=cutoff_date).count()
        
        if old_news_count > 0:
            NewsItem.objects.filter(created_at__lt=cutoff_date).delete()
            logger.info(f"清理了 {old_news_count} 条过期新闻")
        
        # 清理缓存中的任务锁
        cache_keys = cache.keys("task_lock:*")
        if cache_keys:
            cache.delete_many(cache_keys)
            logger.info(f"清理了 {len(cache_keys)} 个任务锁")
        
        return {
            'status': 'success',
            'cleaned_news': old_news_count,
            'cleaned_locks': len(cache_keys) if cache_keys else 0
        }
        
    except Exception as e:
        logger.error(f"清理过期数据失败: {str(e)}")
        return {
            'status': 'failed',
            'error': str(e)
        }


# 定时任务
@shared_task
def scheduled_crawl_expressions():
    """定时爬取地道表达"""
    return crawl_expressions_task.delay(
        sources=['cambridge', 'collins'],
        max_items_per_source=20,
        quality_threshold=0.7
    )


@shared_task  
def scheduled_crawl_news():
    """定时爬取新闻"""
    return crawl_news_task.delay(
        source='bbc',
        crawler_type='traditional',
        max_articles=10
    )