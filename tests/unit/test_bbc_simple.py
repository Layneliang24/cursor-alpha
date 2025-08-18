#!/usr/bin/env python3
"""
简化的BBC新闻跳过问题诊断
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alpha.settings')
django.setup()

from django.utils import timezone
from apps.english.models import News
from apps.english.news_crawler import BBCNewsCrawler, EnhancedNewsCrawlerService

def main():
    print("=== BBC新闻跳过问题诊断 ===")
    
    # 1. 检查现有BBC新闻
    bbc_count = News.objects.filter(source='BBC').count()
    print(f"现有BBC新闻数量: {bbc_count}")
    
    if bbc_count > 0:
        recent_bbc = News.objects.filter(source='BBC').order_by('-created_at')[:3]
        print("最近3条BBC新闻:")
        for news in recent_bbc:
            print(f"  - {news.title[:50]}... (词数: {news.word_count})")
    
    # 2. 测试BBC爬虫
    print("\n=== 测试BBC爬虫 ===")
    crawler = BBCNewsCrawler()
    
    try:
        news_items = crawler.crawl_news_list()
        print(f"成功抓取 {len(news_items)} 条BBC新闻")
        
        if news_items:
            print("前3条新闻详情:")
            for i, item in enumerate(news_items[:3]):
                word_count = len(item.content.split()) if item.content else 0
                print(f"  {i+1}. {item.title[:50]}...")
                print(f"     词数: {word_count}")
                print(f"     URL: {item.url[:60]}...")
                print(f"     是否满足最小词数要求(50): {word_count >= 50}")
                print()
    except Exception as e:
        print(f"BBC爬虫测试失败: {e}")
    
    # 3. 测试保存逻辑
    print("=== 测试保存逻辑 ===")
    
    # 创建测试新闻项
    from apps.english.news_crawler import NewsItem
    
    test_item = NewsItem(
        title="Test BBC Article",
        content="This is a test article with sufficient content length to pass the minimum word count requirement. It should have at least fifty words to be considered valid for saving to the database.",
        url="http://test-bbc-save.com/article1",
        source="BBC",
        published_at=timezone.now(),
        summary="Test summary",
        difficulty_level="intermediate",
        tags=["test", "bbc"],
        image_url="",
        image_alt=""
    )
    
    # 清理测试数据
    News.objects.filter(source_url="http://test-bbc-save.com/article1").delete()
    
    # 测试保存
    real_service = EnhancedNewsCrawlerService()
    saved_count = real_service.save_news_to_db([test_item])
    print(f"测试新闻保存结果: {saved_count} 条成功保存")
    
    # 检查是否真的保存了
    saved_news = News.objects.filter(source_url="http://test-bbc-save.com/article1")
    print(f"数据库中实际保存: {saved_news.count()} 条")
    
    # 4. 检查重复检测
    print("\n=== 检查重复检测 ===")
    
    # 再次尝试保存相同URL的新闻
    duplicate_item = NewsItem(
        title="Test BBC Article - Duplicate",
        content="This is a duplicate article with the same URL.",
        url="http://test-bbc-save.com/article1",  # 相同URL
        source="BBC",
        published_at=timezone.now(),
        summary="Duplicate test",
        difficulty_level="intermediate",
        tags=["test", "bbc"],
        image_url="",
        image_alt=""
    )
    
    duplicate_saved = real_service.save_news_to_db([duplicate_item])
    print(f"重复URL新闻保存结果: {duplicate_saved} 条成功保存")
    
    # 清理测试数据
    News.objects.filter(source_url="http://test-bbc-save.com/article1").delete()
    
    print("\n=== 诊断完成 ===")

if __name__ == "__main__":
    main()
