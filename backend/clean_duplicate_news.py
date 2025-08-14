#!/usr/bin/env python
"""
清理重复的新闻数据
"""

import os
import sys
import django
from datetime import datetime, timedelta

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alpha.settings')
django.setup()

from apps.english.models import News
from django.db.models import Q
from django.utils import timezone
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def clean_duplicate_news():
    """清理重复的新闻"""
    logger.info("开始清理重复新闻...")
    
    # 1. 删除使用哈希URL的新闻（这些可能是重复的）
    hash_url_news = News.objects.filter(source_url__startswith='fundus_')
    hash_count = hash_url_news.count()
    logger.info(f"找到 {hash_count} 条使用哈希URL的新闻")
    
    if hash_count > 0:
        hash_url_news.delete()
        logger.info(f"已删除 {hash_count} 条哈希URL新闻")
    
    # 2. 删除重复的URL
    from django.db.models import Count
    duplicate_urls = News.objects.values('source_url').annotate(
        count=Count('id')
    ).filter(count__gt=1, source_url__isnull=False).exclude(source_url='')
    
    for dup in duplicate_urls:
        url = dup['source_url']
        news_list = News.objects.filter(source_url=url).order_by('id')
        # 保留第一条，删除其他
        to_delete = news_list[1:]
        deleted_count = to_delete.count()
        to_delete.delete()
        logger.info(f"删除URL重复新闻: {url[:50]}... (删除 {deleted_count} 条)")
    
    # 3. 删除标题相似的新闻
    all_news = News.objects.all().order_by('id')
    deleted_titles = set()
    
    for news in all_news:
        if news.id in deleted_titles:
            continue
            
        # 查找标题相似的新闻
        similar_news = News.objects.filter(
            Q(title__icontains=news.title[:30]) | Q(title__icontains=news.title[-30:]),
            source=news.source
        ).exclude(id=news.id)
        
        if similar_news.exists():
            similar_ids = list(similar_news.values_list('id', flat=True))
            similar_news.delete()
            deleted_titles.update(similar_ids)
            logger.info(f"删除标题相似新闻: {news.title[:50]}... (删除 {len(similar_ids)} 条)")
    
    # 4. 删除最近7天内同一来源过多的新闻
    recent_date = timezone.now().date() - timedelta(days=7)
    for source in News.objects.values_list('source', flat=True).distinct():
        recent_news = News.objects.filter(
            source=source,
            publish_date__gte=recent_date
        ).order_by('-publish_date')
        
        if recent_news.count() > 50:
            to_delete = recent_news[50:]  # 保留最新的50条
            deleted_count = to_delete.count()
            to_delete.delete()
            logger.info(f"删除来源 {source} 的旧新闻: 删除 {deleted_count} 条")
    
    # 统计结果
    final_count = News.objects.count()
    logger.info(f"清理完成，剩余新闻数量: {final_count}")

if __name__ == '__main__':
    clean_duplicate_news()

