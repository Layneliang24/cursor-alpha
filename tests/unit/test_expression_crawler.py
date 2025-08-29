"""
地道表达爬虫单元测试
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from django.utils import timezone
from bs4 import BeautifulSoup
from datetime import datetime

from apps.english.expression_crawler import (
    ExpressionItem,
    BaseExpressionCrawler,
    DictionaryCrawler,
    ExpressionCrawlerService
)


class ExpressionItemTest(TestCase):
    """表达式数据项测试"""
    
    def test_expression_item_creation(self):
        """测试表达式项目创建"""
        item = ExpressionItem(
            expression="break the ice",
            meaning="开始对话，打破僵局",
            source_url="https://example.com/test",
            source_name="TestDict",
            expression_type="idiom",
            formality_level="neutral",
            frequency_score=7
        )
        
        self.assertEqual(item.expression, "break the ice")
        self.assertEqual(item.meaning, "开始对话，打破僵局")
        self.assertEqual(item.source_name, "TestDict")
        self.assertEqual(item.expression_type, "idiom")
        self.assertEqual(item.formality_level, "neutral")
        self.assertEqual(item.frequency_score, 7)
        self.assertIsInstance(item.created_at, datetime)
    
    def test_expression_item_defaults(self):
        """测试表达式项目默认值"""
        item = ExpressionItem(
            expression="test phrase",
            meaning="test meaning",
            source_url="https://test.com",
            source_name="Test"
        )
        
        self.assertEqual(item.expression_type, "phrase")
        self.assertEqual(item.formality_level, "neutral")
        self.assertEqual(item.frequency_score, 5)
        self.assertEqual(item.usage_examples, [])
        self.assertEqual(item.scenarios, [])
        self.assertEqual(item.metadata, {})


class MockExpressionCrawler(BaseExpressionCrawler):
    """测试用的模拟爬虫"""
    
    def crawl_expressions(self, limit: int = 50):
        return [
            ExpressionItem(
                expression="test expression",
                meaning="test meaning",
                source_url="https://mock.com/test",
                source_name=self.source_name
            )
        ]


class BaseExpressionCrawlerTest(TestCase):
    """基础表达式爬虫测试"""
    
    def setUp(self):
        self.crawler = MockExpressionCrawler("TestCrawler")
    
    def test_crawler_initialization(self):
        """测试爬虫初始化"""
        self.assertEqual(self.crawler.source_name, "TestCrawler")
        self.assertIsNotNone(self.crawler.session)
        self.assertFalse(self.crawler.use_js_rendering)
    
    @patch('apps.english.expression_crawler.requests.Session.get')
    def test_get_dynamic_content(self, mock_get):
        """测试获取动态内容"""
        # 模拟HTTP响应
        mock_response = Mock()
        mock_response.content = b'<html><body>Test Content</body></html>'
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        soup = self.crawler.get_dynamic_content("https://test.com")
        
        self.assertIsInstance(soup, BeautifulSoup)
        self.assertIn("Test Content", str(soup))
        mock_get.assert_called_once()
    
    def test_determine_expression_type(self):
        """测试表达式类型判断"""
        # 测试习语
        self.assertEqual(
            self.crawler.determine_expression_type("break the ice"),
            "idiom"
        )
        
        # 测试俚语
        self.assertEqual(
            self.crawler.determine_expression_type("cool", "slang for good"),
            "slang"
        )
        
        # 测试固定搭配
        self.assertEqual(
            self.crawler.determine_expression_type("listen to"),
            "collocation"
        )
        
        # 测试默认短语
        self.assertEqual(
            self.crawler.determine_expression_type("hello world"),
            "phrase"
        )
    
    def test_determine_formality_level(self):
        """测试正式程度判断"""
        # 测试正式
        self.assertEqual(
            self.crawler.determine_formality_level("", "formal business term"),
            "formal"
        )
        
        # 测试非正式
        self.assertEqual(
            self.crawler.determine_formality_level("", "informal slang"),
            "informal"
        )
        
        # 测试中性
        self.assertEqual(
            self.crawler.determine_formality_level("test phrase", "neutral meaning"),
            "neutral"
        )
    
    def test_calculate_frequency_score(self):
        """测试频率评分计算"""
        # 短表达式应该有较高评分
        score1 = self.crawler.calculate_frequency_score("get up")
        self.assertGreaterEqual(score1, 6)
        
        # 长表达式应该有较低评分
        score2 = self.crawler.calculate_frequency_score("a very long and complex expression")
        self.assertLessEqual(score2, 6)
        
        # 评分应该在1-10范围内
        self.assertGreaterEqual(score1, 1)
        self.assertLessEqual(score1, 10)
        self.assertGreaterEqual(score2, 1)
        self.assertLessEqual(score2, 10)
    
    def test_extract_scenarios(self):
        """测试场景提取"""
        examples = ["We use this at work", "Great for business meetings"]
        meaning = "A professional expression"
        
        scenarios = self.crawler.extract_scenarios(examples, meaning)
        
        self.assertIn("business", scenarios)
        self.assertIn("workplace", scenarios)
        self.assertLessEqual(len(scenarios), 3)
    
    def test_clean_expression_text(self):
        """测试表达式文本清理"""
        # 测试去除编号
        self.assertEqual(
            self.crawler.clean_expression_text("1. break the ice"),
            "break the ice"
        )
        
        # 测试去除项目符号
        self.assertEqual(
            self.crawler.clean_expression_text("• test phrase"),
            "test phrase"
        )
        
        # 测试去除末尾括号
        self.assertEqual(
            self.crawler.clean_expression_text("test phrase (informal)"),
            "test phrase"
        )
        
        # 测试去除多余标点
        self.assertEqual(
            self.crawler.clean_expression_text("，，test phrase；；"),
            "test phrase"
        )
    
    def test_extract_expression_data(self):
        """测试表达式数据提取"""
        html_content = """
        <div>
            <h1 class="expression">break the ice</h1>
            <p class="meaning">to start a conversation</p>
            <div class="example">Let me break the ice with a joke.</div>
        </div>
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        expressions = self.crawler.extract_expression_data(soup, "https://test.com")
        
        self.assertGreater(len(expressions), 0)
        if expressions:
            expr = expressions[0]
            self.assertEqual(expr['expression'], 'break the ice')
            self.assertEqual(expr['meaning'], 'to start a conversation')
            self.assertIn('Let me break the ice with a joke.', expr['examples'])


class DictionaryCrawlerTest(TestCase):
    """词典爬虫测试"""
    
    def setUp(self):
        self.crawler = DictionaryCrawler(
            source_name="TestDict",
            base_url="https://testdict.com",
            search_patterns=["https://testdict.com/search?q={term}"]
        )
    
    def test_dictionary_crawler_initialization(self):
        """测试词典爬虫初始化"""
        self.assertEqual(self.crawler.source_name, "TestDict")
        self.assertEqual(self.crawler.base_url, "https://testdict.com")
        self.assertEqual(len(self.crawler.search_patterns), 1)
    
    @patch.object(DictionaryCrawler, 'get_dynamic_content')
    @patch.object(DictionaryCrawler, 'extract_expression_data')
    def test_search_expression(self, mock_extract, mock_get_content):
        """测试表达式搜索"""
        # 模拟返回的页面内容
        mock_soup = BeautifulSoup('<html></html>', 'html.parser')
        mock_get_content.return_value = mock_soup
        
        # 模拟提取的数据
        mock_extract.return_value = [{
            'expression': 'break the ice',
            'meaning': 'to start conversation',
            'examples': ['Let me break the ice.'],
            'source_url': 'https://testdict.com/search?q=break+the+ice'
        }]
        
        expressions = self.crawler._search_expression("break the ice")
        
        self.assertEqual(len(expressions), 1)
        self.assertEqual(expressions[0].expression, "break the ice")
        self.assertEqual(expressions[0].meaning, "to start conversation")
        self.assertEqual(expressions[0].source_name, "TestDict")
        
        mock_get_content.assert_called_once()
        mock_extract.assert_called_once()
    
    def test_create_expression_item(self):
        """测试创建表达式项目"""
        data = {
            'expression': 'piece of cake',
            'meaning': 'very easy',
            'examples': ['This test is a piece of cake.'],
            'search_term': 'piece of cake'
        }
        
        item = self.crawler._create_expression_item(data, "https://test.com")
        
        self.assertIsNotNone(item)
        self.assertEqual(item.expression, "piece of cake")
        self.assertEqual(item.meaning, "very easy")
        self.assertEqual(item.source_name, "TestDict")
        self.assertIn("This test is a piece of cake.", item.usage_examples)
        self.assertIn("extraction_method", item.metadata)
    
    def test_create_expression_item_invalid_data(self):
        """测试无效数据的表达式项目创建"""
        # 缺少表达式
        data1 = {'meaning': 'test meaning'}
        item1 = self.crawler._create_expression_item(data1, "https://test.com")
        self.assertIsNone(item1)
        
        # 缺少含义
        data2 = {'expression': 'test expression'}
        item2 = self.crawler._create_expression_item(data2, "https://test.com")
        self.assertIsNone(item2)


class ExpressionCrawlerServiceTest(TestCase):
    """表达式爬虫服务测试"""
    
    def setUp(self):
        self.service = ExpressionCrawlerService()
    
    def test_service_initialization(self):
        """测试服务初始化"""
        self.assertIsInstance(self.service.crawlers, dict)
    
    def test_add_crawler(self):
        """测试添加爬虫"""
        crawler = MockExpressionCrawler("TestCrawler")
        self.service.add_crawler("test", crawler)
        
        self.assertIn("test", self.service.crawlers)
        self.assertEqual(self.service.crawlers["test"], crawler)
    
    def test_crawl_expressions_single_source(self):
        """测试单一源抓取"""
        crawler = MockExpressionCrawler("TestCrawler")
        self.service.add_crawler("test", crawler)
        
        expressions = self.service.crawl_expressions("test", limit=10)
        
        self.assertEqual(len(expressions), 1)
        self.assertEqual(expressions[0].expression, "test expression")
        self.assertEqual(expressions[0].source_name, "TestCrawler")
    
    def test_crawl_expressions_all_sources(self):
        """测试所有源抓取"""
        crawler1 = MockExpressionCrawler("Crawler1")
        crawler2 = MockExpressionCrawler("Crawler2")
        
        self.service.add_crawler("test1", crawler1)
        self.service.add_crawler("test2", crawler2)
        
        expressions = self.service.crawl_expressions(limit=20)
        
        self.assertEqual(len(expressions), 2)
        source_names = [expr.source_name for expr in expressions]
        self.assertIn("Crawler1", source_names)
        self.assertIn("Crawler2", source_names)
    
    @patch('apps.english.models.IdiomaticExpression')
    @patch('apps.english.models.ExpressionSource')
    def test_save_expressions_to_db(self, mock_source_model, mock_expression_model):
        """测试保存表达式到数据库"""
        # 模拟数据库操作
        mock_expression_model.objects.filter.return_value.exists.return_value = False
        mock_source_instance = Mock()
        mock_source_model.objects.get_or_create.return_value = (mock_source_instance, True)
        mock_expression_instance = Mock()
        mock_expression_model.objects.create.return_value = mock_expression_instance
        
        expressions = [
            ExpressionItem(
                expression="test expression",
                meaning="test meaning",
                source_url="https://test.com",
                source_name="TestSource"
            )
        ]
        
        saved_count = self.service.save_expressions_to_db(expressions)
        
        self.assertEqual(saved_count, 1)
        mock_expression_model.objects.create.assert_called_once()
        mock_source_instance.expressions.add.assert_called_once()


class CrawlerIntegrationTest(TestCase):
    """爬虫集成测试"""
    
    def test_full_crawling_workflow(self):
        """测试完整的爬虫工作流程"""
        # 创建服务
        service = ExpressionCrawlerService()
        
        # 添加模拟爬虫
        crawler = MockExpressionCrawler("IntegrationTest")
        service.add_crawler("integration", crawler)
        
        # 抓取表达式
        expressions = service.crawl_expressions("integration", limit=5)
        
        # 验证结果
        self.assertGreater(len(expressions), 0)
        for expr in expressions:
            self.assertIsInstance(expr, ExpressionItem)
            self.assertIsNotNone(expr.expression)
            self.assertIsNotNone(expr.meaning)
            self.assertIsNotNone(expr.source_url)
            self.assertIsNotNone(expr.source_name)
