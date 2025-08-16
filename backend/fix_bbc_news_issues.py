#!/usr/bin/env python3
"""
修复BBC新闻被跳过的问题
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alpha.settings')
django.setup()

from django.utils import timezone
from apps.english.models import News
from apps.english.news_crawler import BBCNewsCrawler, RealNewsCrawlerService

def analyze_bbc_issues():
    """分析BBC新闻问题"""
    print("=== 分析BBC新闻问题 ===")
    
    # 1. 检查现有BBC新闻
    bbc_count = News.objects.filter(source='BBC').count()
    print(f"现有BBC新闻数量: {bbc_count}")
    
    if bbc_count > 0:
        recent_bbc = News.objects.filter(source='BBC').order_by('-created_at')[:5]
        print("最近5条BBC新闻:")
        for news in recent_bbc:
            print(f"  - {news.title[:50]}... (词数: {news.word_count}, URL: {news.source_url[:50]}...)")
    
    # 2. 测试BBC爬虫
    print("\n=== 测试BBC爬虫 ===")
    crawler = BBCNewsCrawler()
    
    try:
        # 测试RSS源访问
        print("测试RSS源访问:")
        for rss_url in crawler.rss_feeds:
            try:
                soup = crawler.get_rss_content(rss_url)
                if soup:
                    items = soup.find_all('item')
                    print(f"  ✓ {rss_url}: 找到 {len(items)} 个条目")
                else:
                    print(f"  ✗ {rss_url}: 无法获取内容")
            except Exception as e:
                print(f"  ✗ {rss_url}: 错误 - {e}")
        
        # 测试新闻抓取
        print("\n测试新闻抓取:")
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
                print(f"     是否满足内容获取要求(100): {word_count >= 100}")
                print()
        else:
            print("没有抓取到任何BBC新闻")
            
    except Exception as e:
        print(f"BBC爬虫测试失败: {e}")
        import traceback
        traceback.print_exc()

def fix_content_length_validation():
    """修复内容长度验证问题"""
    print("\n=== 修复内容长度验证问题 ===")
    
    # 修改get_article_content方法中的最小词数要求
    print("当前问题：get_article_content要求100词，save_news_to_db只要求50词")
    print("建议：统一为50词，或者降低get_article_content的要求")
    
    # 检查是否有因为内容长度被跳过的新闻
    short_news = News.objects.filter(source='BBC', word_count__lt=100).count()
    print(f"词数少于100的BBC新闻: {short_news} 条")

def fix_duplicate_detection():
    """修复重复检测问题"""
    print("\n=== 修复重复检测问题 ===")
    
    # 检查重复URL
    from django.db.models import Count
    duplicate_urls = News.objects.filter(source='BBC').values('source_url').annotate(
        count=Count('id')
    ).filter(count__gt=1)
    
    if duplicate_urls:
        print(f"发现 {len(duplicate_urls)} 个重复URL:")
        for dup in duplicate_urls:
            print(f"  - {dup['source_url'][:60]}... (重复 {dup['count']} 次)")
    else:
        print("没有发现重复URL")

def test_improved_bbc_crawler():
    """测试改进的BBC爬虫"""
    print("\n=== 测试改进的BBC爬虫 ===")
    
    # 创建一个改进的BBC爬虫类
    class ImprovedBBCNewsCrawler(BBCNewsCrawler):
        def get_article_content(self, url: str) -> dict:
            """改进的文章内容获取方法"""
            try:
                import requests
                from bs4 import BeautifulSoup
                import urllib.parse
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'lxml')
                
                # 提取图片
                image_url, image_alt = self.extract_featured_image(soup, url)
                
                # BBC特定的内容选择器
                content_selectors = [
                    '[data-component="text-block"]',
                    '.zn-body__paragraph',
                    '.article-body p',
                    '.story-body p',
                    '.article__content p',
                    '.story__content p',
                    '.article-text p',
                    '.post-body p',
                    'article p',
                    '.content p'
                ]
                
                content_parts = []
                for selector in content_selectors:
                    elements = soup.select(selector)
                    if elements:
                        for elem in elements:
                            text = self.clean_text(elem.get_text())
                            if text and len(text) > 10:  # 降低最小长度要求
                                content_parts.append(text)
                        
                        if content_parts:
                            break
                
                if content_parts:
                    full_content = ' '.join(content_parts)
                    
                    # 降低最小词数要求到50
                    word_count = len(full_content.split())
                    if word_count >= 50:  # 从100降低到50
                        print(f"成功提取BBC文章内容，共 {word_count} 个单词")
                        return {
                            'content': full_content,
                            'image_url': image_url,
                            'image_alt': image_alt
                        }
                    else:
                        print(f"BBC文章内容太短，只有 {word_count} 个单词，跳过")
                        return None
                
                print(f"无法提取BBC文章内容: {url}")
                return None
                
            except Exception as e:
                print(f"获取BBC文章内容失败 {url}: {str(e)}")
                return None
    
    # 测试改进的爬虫
    improved_crawler = ImprovedBBCNewsCrawler()
    
    try:
        news_items = improved_crawler.crawl_news_list()
        print(f"改进爬虫成功抓取 {len(news_items)} 条BBC新闻")
        
        if news_items:
            print("前3条新闻详情:")
            for i, item in enumerate(news_items[:3]):
                word_count = len(item.content.split()) if item.content else 0
                print(f"  {i+1}. {item.title[:50]}...")
                print(f"     词数: {word_count}")
                print(f"     URL: {item.url[:60]}...")
                print()
    except Exception as e:
        print(f"改进爬虫测试失败: {e}")

def create_test_news():
    """创建测试新闻"""
    print("\n=== 创建测试新闻 ===")
    
    # 清理测试数据
    News.objects.filter(source_url__startswith="http://test-bbc-fix-").delete()
    
    # 创建测试新闻
    test_news = News.objects.create(
        title="Test BBC Article - Fix Test",
        content="This is a test article to verify that the BBC news saving functionality is working correctly. It contains enough words to pass the minimum word count requirement and should be saved successfully to the database.",
        source_url="http://test-bbc-fix-1.com/article1",
        source="BBC",
        publish_date=timezone.now().date(),
        summary="Test summary for BBC fix",
        difficulty_level="intermediate",
        word_count=25,
        reading_time_minutes=1,
        key_vocabulary="test, bbc, fix",
        comprehension_questions=["What is this article about?", "Is this a test article?"],
        image_url="",
        image_alt=""
    )
    
    print(f"创建测试新闻成功: {test_news.id}")
    
    # 验证创建
    saved_news = News.objects.filter(source_url="http://test-bbc-fix-1.com/article1")
    print(f"数据库中实际保存: {saved_news.count()} 条")
    
    # 清理测试数据
    News.objects.filter(source_url__startswith="http://test-bbc-fix-").delete()

def main():
    """主函数"""
    print("BBC新闻问题修复脚本")
    print("=" * 50)
    
    try:
        # 1. 分析问题
        analyze_bbc_issues()
        
        # 2. 修复内容长度验证
        fix_content_length_validation()
        
        # 3. 修复重复检测
        fix_duplicate_detection()
        
        # 4. 测试改进的爬虫
        test_improved_bbc_crawler()
        
        # 5. 创建测试新闻
        create_test_news()
        
        print("\n" + "=" * 50)
        print("修复脚本执行完成！")
        print("\n建议修复措施:")
        print("1. 将get_article_content的最小词数要求从100降低到50")
        print("2. 改进BBC特定的内容选择器")
        print("3. 添加更好的错误处理和重试机制")
        print("4. 考虑使用备用内容源")
        
    except Exception as e:
        print(f"修复脚本执行出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
