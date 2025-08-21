#!/usr/bin/env python3
"""
BBC新闻保存功能单元测试
"""

import os
import sys
import django
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alpha.settings')
django.setup()

from django.test import TestCase
from django.utils import timezone
from apps.english.models import News
from apps.english.news_crawler import BBCNewsCrawler, EnhancedNewsCrawlerService, NewsItem

class TestBBCNewsSave(TestCase):
    """测试BBC新闻保存功能"""
    
    def setUp(self):
        """测试前准备"""
        # 清理测试数据
        News.objects.filter(source_url__startswith="http://test-bbc-").delete()
    
    def tearDown(self):
        """测试后清理"""
        # 清理测试数据
        News.objects.filter(source_url__startswith="http://test-bbc-").delete()
    
    def test_news_save_with_sufficient_content(self):
        """测试内容足够的新闻保存"""
        # 创建测试新闻项
        test_item = NewsItem(
            title="Test BBC Article with Sufficient Content",
            content="This is a test article with sufficient content length to pass the minimum word count requirement. It should have at least fifty words to be considered valid for saving to the database. The content is substantial enough to be considered a proper news article.",
            url="http://test-bbc-sufficient.com/article1",
            source="BBC",
            published_at=timezone.now(),
            summary="Test summary for sufficient content",
            difficulty_level="intermediate",
            tags=["test", "bbc", "sufficient"],
            image_url="",
            image_alt=""
        )
        
        # 测试保存
        real_service = EnhancedNewsCrawlerService()
        saved_count = real_service.save_news_to_db([test_item])
        
        # 验证结果
        self.assertEqual(saved_count, 1, "应该成功保存1条新闻")
        
        # 检查数据库中是否真的保存了
        saved_news = News.objects.filter(source_url="http://test-bbc-sufficient.com/article1")
        self.assertEqual(saved_news.count(), 1, "数据库中应该有1条新闻")
        
        news = saved_news.first()
        self.assertEqual(news.title, test_item.title)
        self.assertEqual(news.source, "BBC")
        self.assertGreaterEqual(news.word_count, 30, "词数应该大于等于30")
    
    def test_news_save_with_short_content(self):
        """测试短内容新闻也能保存（无字数限制）"""
        # 创建短内容的测试新闻项
        test_item = NewsItem(
            title="Test BBC Article with Short Content",
            content="Short content.",
            url="http://test-bbc-short.com/article1",
            source="BBC",
            published_at=timezone.now(),
            summary="Short summary",
            difficulty_level="beginner",
            tags=["test", "bbc"],
            image_url="",
            image_alt=""
        )

        # 测试保存
        real_service = EnhancedNewsCrawlerService()
        saved_count = real_service.save_news_to_db([test_item])

        # 验证结果
        self.assertEqual(saved_count, 1, "短内容新闻也应该被保存（无字数限制）")
        
        # 检查数据库中确实保存了
        saved_news = News.objects.filter(source_url="http://test-bbc-short.com/article1")
        self.assertEqual(saved_news.count(), 1, "数据库中应该有短内容新闻")
    
    def test_duplicate_url_detection(self):
        """测试重复URL检测"""
        # 清理之前的测试数据
        News.objects.filter(source_url="http://test-bbc-duplicate.com/article1").delete()
        
        # 创建第一条新闻
        test_item1 = NewsItem(
            title="Test BBC Article 1",
            content="This is the first test article with sufficient content length to pass the minimum word count requirement.",
            url="http://test-bbc-duplicate.com/article1",
            source="BBC",
            published_at=timezone.now(),
            summary="First article summary",
            difficulty_level="intermediate",
            tags=["test", "bbc"],
            image_url="",
            image_alt=""
        )
        
        # 创建第二条相同URL的新闻
        test_item2 = NewsItem(
            title="Test BBC Article 2 - Duplicate",
            content="This is the second test article with the same URL but different content.",
            url="http://test-bbc-duplicate.com/article1",  # 相同URL
            source="BBC",
            published_at=timezone.now(),
            summary="Second article summary",
            difficulty_level="intermediate",
            tags=["test", "bbc"],
            image_url="",
            image_alt=""
        )
        
        # 测试保存
        real_service = EnhancedNewsCrawlerService()
        
        # 保存第一条新闻
        saved_count1 = real_service.save_news_to_db([test_item1])
        self.assertEqual(saved_count1, 1, "第一条新闻应该成功保存")
        
        # 尝试保存第二条新闻（重复URL），禁用备用新闻生成
        saved_count2 = real_service.save_news_to_db([test_item2], generate_fallback=False)
        self.assertEqual(saved_count2, 0, "重复URL的新闻应该被跳过")
        
        # 检查数据库中只有一条新闻
        saved_news = News.objects.filter(source_url="http://test-bbc-duplicate.com/article1")
        self.assertEqual(saved_news.count(), 1, "数据库中应该只有1条新闻")
        
        # 验证保存的是第一条新闻
        news = saved_news.first()
        self.assertEqual(news.title, test_item1.title, "应该保存第一条新闻")
    
    def test_content_length_validation(self):
        """测试内容长度验证"""
        test_cases = [
            {
                'title': 'Very Short Content',
                'content': 'Short.',
                'expected_saved': 1,
                'description': '短内容也应该被保存（无字数限制）'
            },
            {
                'title': 'Medium Content',
                'content': 'This is a medium length content with more words.',
                'expected_saved': 1,
                'description': '中等长度内容应该被保存'
            },
            {
                'title': 'Sufficient Content',
                'content': 'This is a longer content that should meet the minimum word count requirement. It contains enough words to pass the validation and should be saved to the database successfully.',
                'expected_saved': 1,
                'description': '长内容应该被保存'
            }
        ]
        
        real_service = EnhancedNewsCrawlerService()
        
        for i, test_case in enumerate(test_cases):
            with self.subTest(test_case=test_case):
                # 创建测试新闻项
                test_item = NewsItem(
                    title=test_case['title'],
                    content=test_case['content'],
                    url=f"http://test-bbc-length-{i}.com/article1",
                    source="BBC",
                    published_at=timezone.now(),
                    summary=f"Test summary for {test_case['title']}",
                    difficulty_level="intermediate",
                    tags=["test", "bbc"],
                    image_url="",
                    image_alt=""
                )
                
                # 清理之前的测试数据
                News.objects.filter(source_url=f"http://test-bbc-length-{i}.com/article1").delete()
                
                # 测试保存
                saved_count = real_service.save_news_to_db([test_item])
                
                # 验证结果
                self.assertEqual(
                    saved_count, 
                    test_case['expected_saved'], 
                    f"{test_case['description']}: 期望保存{test_case['expected_saved']}条，实际保存{saved_count}条"
                )
    
    @patch('apps.english.news_crawler.BBCNewsCrawler.get_article_content')
    def test_bbc_crawler_content_extraction(self, mock_get_content):
        """测试BBC爬虫内容提取"""
        # 模拟内容提取结果
        mock_get_content.return_value = {
            'content': 'This is a test article content with sufficient length to pass the minimum word count requirement. It contains enough words to be considered valid for saving to the database.',
            'image_url': 'http://test.com/image.jpg',
            'image_alt': 'Test image'
        }
        
        # 创建BBC爬虫
        crawler = BBCNewsCrawler()
        
        # 模拟RSS内容
        mock_rss_item = MagicMock()
        mock_rss_item.find.side_effect = lambda tag: {
            'title': MagicMock(get_text=lambda: 'Test BBC Article'),
            'link': MagicMock(get_text=lambda: 'http://test-bbc-crawler.com/article1'),
            'description': MagicMock(get_text=lambda: 'Test description'),
            'pubDate': MagicMock(get_text=lambda: 'Mon, 16 Aug 2025 10:00:00 GMT')
        }.get(tag, None)
        
        # 测试解析RSS条目
        news_item = crawler._parse_rss_item(mock_rss_item)
        
        # 验证结果
        self.assertIsNotNone(news_item, "应该成功解析RSS条目")
        self.assertEqual(news_item.title, 'Test BBC Article')
        self.assertEqual(news_item.url, 'http://test-bbc-crawler.com/article1')
        self.assertEqual(news_item.source, 'BBC')
        
        # 验证内容不为空
        word_count = len(news_item.content.split())
        self.assertGreater(word_count, 0, "内容应该不为空")
    
    def test_news_model_fields(self):
        """测试News模型字段"""
        # 创建测试新闻
        test_news = News.objects.create(
            title="Test BBC Model Article",
            content="This is a test article to verify the News model fields are working correctly.",
            source_url="http://test-bbc-model.com/article1",
            source="BBC",
            publish_date=timezone.now().date(),
            summary="Test summary for model fields",
            difficulty_level="intermediate",
            word_count=15,
            reading_time_minutes=1,
            key_vocabulary="test, bbc, model",
            comprehension_questions=["What is this article about?", "Is this a test?"],
            image_url="",
            image_alt=""
        )
        
        # 验证字段
        self.assertEqual(test_news.title, "Test BBC Model Article")
        self.assertEqual(test_news.source, "BBC")
        self.assertEqual(test_news.word_count, 15)
        self.assertEqual(test_news.difficulty_level, "intermediate")
        self.assertEqual(test_news.key_vocabulary, "test, bbc, model")
        self.assertIsInstance(test_news.comprehension_questions, list)
        self.assertEqual(len(test_news.comprehension_questions), 2)

class TestBBCNewsCrawlerIntegration(TestCase):
    """测试BBC新闻爬虫集成"""
    
    def setUp(self):
        """测试前准备"""
        self.crawler = BBCNewsCrawler()
    
    @patch('apps.english.news_crawler.BBCNewsCrawler.get_rss_content')
    @patch('apps.english.news_crawler.BBCNewsCrawler.get_article_content')
    def test_full_crawl_process(self, mock_get_content, mock_get_rss):
        """测试完整的爬取过程"""
        # 模拟RSS内容
        mock_rss_soup = MagicMock()
        mock_rss_item = MagicMock()
        mock_rss_item.find.side_effect = lambda tag: {
            'title': MagicMock(get_text=lambda: 'Test BBC Article'),
            'link': MagicMock(get_text=lambda: 'http://test-bbc-integration.com/article1'),
            'description': MagicMock(get_text=lambda: 'Test description'),
            'pubDate': MagicMock(get_text=lambda: 'Mon, 16 Aug 2025 10:00:00 GMT')
        }.get(tag, None)
        
        mock_rss_soup.find_all.return_value = [mock_rss_item]
        mock_get_rss.return_value = mock_rss_soup
        
        # 模拟文章内容
        mock_get_content.return_value = {
            'content': 'This is a test article content with sufficient length to pass the minimum word count requirement. It contains enough words to be considered valid for saving to the database.',
            'image_url': 'http://test.com/image.jpg',
            'image_alt': 'Test image'
        }
        
        # 测试爬取
        news_items = self.crawler.crawl_news_list()
        
        # 验证结果
        self.assertGreater(len(news_items), 0, "应该爬取到新闻")
        
        news_item = news_items[0]
        self.assertEqual(news_item.title, 'Test BBC Article')
        self.assertEqual(news_item.source, 'BBC')
        
        # 验证内容不为空
        word_count = len(news_item.content.split())
        self.assertGreater(word_count, 0, "内容应该不为空")
    
    def test_crawler_initialization(self):
        """测试爬虫初始化"""
        self.assertEqual(self.crawler.source_name, 'BBC')
        self.assertIsInstance(self.crawler.rss_feeds, list)
        self.assertGreater(len(self.crawler.rss_feeds), 0, "应该有RSS源配置")
        
        # 验证RSS源都是BBC的
        for rss_url in self.crawler.rss_feeds:
            self.assertIn('bbci.co.uk', rss_url, "RSS源应该是BBC的")

if __name__ == '__main__':
    # 运行测试
    import unittest
    unittest.main()




