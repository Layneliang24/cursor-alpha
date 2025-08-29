"""
专业爬虫单元测试
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from django.utils import timezone
from bs4 import BeautifulSoup
import json

from apps.english.specialized_crawlers import (
    CambridgeCrawler,
    CollinsCrawler,
    RedditCrawler,
    UrbanDictionaryCrawler,
    YouGlishCrawler,
    register_specialized_crawlers
)
from apps.english.expression_crawler import ExpressionItem


class CambridgeCrawlerTest(TestCase):
    """剑桥词典爬虫测试"""
    
    def setUp(self):
        self.crawler = CambridgeCrawler()
    
    def test_cambridge_crawler_initialization(self):
        """测试剑桥爬虫初始化"""
        self.assertEqual(self.crawler.source_name, "Cambridge Dictionary")
        self.assertEqual(self.crawler.base_url, "https://dictionary.cambridge.org")
        self.assertEqual(len(self.crawler.search_patterns), 2)
        self.assertIn('Referer', self.crawler.session.headers)
    
    def test_get_selector_combinations(self):
        """测试剑桥词典选择器组合"""
        combinations = self.crawler._get_selector_combinations()
        
        self.assertIsInstance(combinations, list)
        self.assertGreater(len(combinations), 0)
        
        for combo in combinations:
            self.assertIn('expression', combo)
            self.assertIn('meaning', combo)
            self.assertIn('example', combo)
    
    def test_extract_phonetic_transcription(self):
        """测试音标提取"""
        html_content = '''
        <div class="pron">
            <span class="ipa">/break the ice/</span>
        </div>
        '''
        soup = BeautifulSoup(html_content, 'html.parser')
        
        phonetic = self.crawler.extract_phonetic_transcription(soup, "break the ice")
        self.assertEqual(phonetic, "/break the ice/")
    
    def test_extract_additional_metadata(self):
        """测试额外元数据提取"""
        html_content = '''
        <div>
            <span class="pos">noun</span>
            <span class="freq">common</span>
            <span class="register">informal</span>
        </div>
        '''
        soup = BeautifulSoup(html_content, 'html.parser')
        
        metadata = self.crawler._extract_additional_metadata(soup, "test")
        
        self.assertEqual(metadata['part_of_speech'], 'noun')
        self.assertEqual(metadata['frequency_info'], 'common')
        self.assertEqual(metadata['register'], 'informal')
    
    def test_calculate_cambridge_frequency(self):
        """测试剑桥频率计算"""
        # 测试常见词汇
        metadata1 = {'frequency_info': 'common word'}
        score1 = self.crawler._calculate_cambridge_frequency(metadata1)
        self.assertEqual(score1, 8)
        
        # 测试罕见词汇
        metadata2 = {'frequency_info': 'rare usage'}
        score2 = self.crawler._calculate_cambridge_frequency(metadata2)
        self.assertEqual(score2, 3)
        
        # 测试默认情况
        metadata3 = {}
        score3 = self.crawler._calculate_cambridge_frequency(metadata3)
        self.assertEqual(score3, 6)
    
    def test_create_expression_item(self):
        """测试创建剑桥表达式项目"""
        data = {
            'expression': 'break the ice',
            'meaning': 'to make people feel more relaxed',
            'examples': ['Let me break the ice with a joke.'],
            'metadata': {
                'register': 'informal',
                'frequency_info': 'common'
            },
            'phonetic': '/breɪk ðə aɪs/'
        }
        
        item = self.crawler._create_expression_item(data, "https://test.com")
        
        self.assertIsNotNone(item)
        self.assertEqual(item.expression, "break the ice")
        self.assertEqual(item.meaning, "to make people feel more relaxed")
        self.assertEqual(item.formality_level, "informal")
        self.assertEqual(item.frequency_score, 8)
        self.assertEqual(item.phonetic_transcription, "/breɪk ðə aɪs/")
        self.assertIn("cambridge_dictionary", item.metadata['extraction_method'])


class CollinsCrawlerTest(TestCase):
    """柯林斯词典爬虫测试"""
    
    def setUp(self):
        self.crawler = CollinsCrawler()
    
    def test_collins_crawler_initialization(self):
        """测试柯林斯爬虫初始化"""
        self.assertEqual(self.crawler.source_name, "Collins Dictionary")
        self.assertEqual(self.crawler.base_url, "https://www.collinsdictionary.com")
        self.assertIn('Referer', self.crawler.session.headers)
    
    def test_get_selector_combinations(self):
        """测试柯林斯选择器组合"""
        combinations = self.crawler._get_selector_combinations()
        
        self.assertIsInstance(combinations, list)
        self.assertEqual(len(combinations), 3)  # 主要结构、短语、搜索结果
    
    def test_extract_collins_rating(self):
        """测试柯林斯星级评分提取"""
        # 测试星级符号
        html_content1 = '<div class="stars">★★★</div>'
        soup1 = BeautifulSoup(html_content1, 'html.parser')
        rating1 = self.crawler._extract_collins_rating(soup1)
        self.assertEqual(rating1, 6)  # 3星 * 2 = 6分
        
        # 测试没有星级
        html_content2 = '<div>no stars</div>'
        soup2 = BeautifulSoup(html_content2, 'html.parser')
        rating2 = self.crawler._extract_collins_rating(soup2)
        self.assertEqual(rating2, 5)  # 默认值


class RedditCrawlerTest(TestCase):
    """Reddit爬虫测试"""
    
    def setUp(self):
        self.crawler = RedditCrawler()
    
    def test_reddit_crawler_initialization(self):
        """测试Reddit爬虫初始化"""
        self.assertEqual(self.crawler.source_name, "Reddit English Learning")
        self.assertEqual(len(self.crawler.subreddits), 5)
        self.assertIn('EnglishLearning', self.crawler.subreddits)
    
    def test_is_expression_related(self):
        """测试表达式相关性判断"""
        # 相关的标题和内容
        self.assertTrue(
            self.crawler._is_expression_related(
                "What does 'break the ice' mean?",
                "I heard this idiom but don't understand it"
            )
        )
        
        # 不相关的内容
        self.assertFalse(
            self.crawler._is_expression_related(
                "Random discussion about weather",
                "It's sunny today"
            )
        )
    
    def test_extract_meaning_from_context(self):
        """测试从上下文提取含义"""
        title = "What does 'break the ice' mean?"
        content = "Break the ice means to start a conversation or make people feel comfortable."
        
        meaning = self.crawler._extract_meaning_from_context("break the ice", title, content)
        
        self.assertIn("start a conversation", meaning)
    
    def test_create_usage_example(self):
        """测试创建使用示例"""
        title = "How to use 'break the ice' in conversation?"
        content = "You can break the ice by asking about their hobbies."
        
        example = self.crawler._create_usage_example("break the ice", title, content)
        
        self.assertIn("break the ice", example.lower())
    
    def test_calculate_reddit_frequency(self):
        """测试Reddit频率计算"""
        # 高人气帖子
        post1 = {'score': 150, 'num_comments': 30}
        score1 = self.crawler._calculate_reddit_frequency(post1)
        self.assertEqual(score1, 8)
        
        # 低人气帖子
        post2 = {'score': 2, 'num_comments': 1}
        score2 = self.crawler._calculate_reddit_frequency(post2)
        self.assertEqual(score2, 4)
    
    @patch('apps.english.specialized_crawlers.requests.Session.get')
    def test_crawl_subreddit(self, mock_get):
        """测试子版块抓取"""
        # 模拟Reddit API响应
        mock_response = Mock()
        mock_response.json.return_value = {
            'data': {
                'children': [
                    {
                        'data': {
                            'title': 'What does "break the ice" mean?',
                            'selftext': 'Break the ice means to start conversation.',
                            'permalink': '/r/test/comments/123/',
                            'score': 50,
                            'num_comments': 10,
                            'subreddit': 'EnglishLearning'
                        }
                    }
                ]
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        expressions = self.crawler._crawl_subreddit('EnglishLearning', 5)
        
        self.assertGreaterEqual(len(expressions), 0)
        mock_get.assert_called_once()
    
    def test_extract_expressions_from_post(self):
        """测试从帖子提取表达式"""
        post = {
            'title': 'What does "break the ice" mean?',
            'selftext': 'I think "break the ice" means to start a conversation.',
            'permalink': '/r/test/comments/123/',
            'score': 25,
            'num_comments': 5,
            'subreddit': 'EnglishLearning'
        }
        
        expressions = self.crawler._extract_expressions_from_post(post)
        
        self.assertGreater(len(expressions), 0)
        if expressions:
            expr = expressions[0]
            self.assertEqual(expr.expression, "break the ice")
            self.assertEqual(expr.formality_level, "informal")
            self.assertIn("casual", expr.scenarios)


class UrbanDictionaryCrawlerTest(TestCase):
    """Urban Dictionary爬虫测试"""
    
    def setUp(self):
        self.crawler = UrbanDictionaryCrawler()
    
    def test_urban_crawler_initialization(self):
        """测试Urban Dictionary爬虫初始化"""
        self.assertEqual(self.crawler.source_name, "Urban Dictionary")
        self.assertEqual(self.crawler.base_url, "https://www.urbandictionary.com")
    
    def test_extract_vote_count(self):
        """测试投票数提取"""
        html_content = '<div class="up">👍 25</div>'
        elem = BeautifulSoup(html_content, 'html.parser')
        
        count = self.crawler._extract_vote_count(elem, '.up')
        self.assertEqual(count, 25)
    
    def test_calculate_urban_frequency(self):
        """测试Urban Dictionary频率计算"""
        # 高赞同率，高投票数
        score1 = self.crawler._calculate_urban_frequency(80, 20)  # 80%赞同率，100总票数
        self.assertEqual(score1, 8)
        
        # 低赞同率
        score2 = self.crawler._calculate_urban_frequency(20, 80)  # 20%赞同率
        self.assertEqual(score2, 3)
        
        # 无投票
        score3 = self.crawler._calculate_urban_frequency(0, 0)
        self.assertEqual(score3, 3)
    
    def test_parse_urban_definition(self):
        """测试Urban Dictionary定义解析"""
        html_content = '''
        <div class="definition">
            <div class="word">lit</div>
            <div class="meaning">Something that is amazing or exciting</div>
            <div class="example">That party was lit!</div>
            <div class="up">👍 150</div>
            <div class="down">👎 20</div>
        </div>
        '''
        def_elem = BeautifulSoup(html_content, 'html.parser').select_one('.definition')
        
        item = self.crawler._parse_urban_definition(def_elem, "https://test.com")
        
        self.assertIsNotNone(item)
        self.assertEqual(item.expression, "lit")
        self.assertEqual(item.expression_type, "slang")
        self.assertEqual(item.formality_level, "informal")
        self.assertIn("That party was lit!", item.usage_examples)
        self.assertEqual(item.metadata['thumbs_up'], 150)
        self.assertEqual(item.metadata['thumbs_down'], 20)


class YouGlishCrawlerTest(TestCase):
    """YouGlish爬虫测试"""
    
    def setUp(self):
        self.crawler = YouGlishCrawler()
    
    def test_youglish_crawler_initialization(self):
        """测试YouGlish爬虫初始化"""
        self.assertEqual(self.crawler.source_name, "YouGlish")
        self.assertEqual(self.crawler.base_url, "https://youglish.com")
    
    def test_extract_result_count(self):
        """测试结果数量提取"""
        html_content = '<div class="result-count">Found 1,234 results</div>'
        soup = BeautifulSoup(html_content, 'html.parser')
        
        count = self.crawler._extract_result_count(soup)
        self.assertEqual(count, 1234)
    
    @patch.object(YouGlishCrawler, 'get_dynamic_content')
    def test_search_youglish_term(self, mock_get_content):
        """测试YouGlish术语搜索"""
        # 模拟页面内容
        html_content = '<div class="result-count">Found 500 videos</div>'
        mock_soup = BeautifulSoup(html_content, 'html.parser')
        mock_get_content.return_value = mock_soup
        
        item = self.crawler._search_youglish_term("break the ice")
        
        self.assertIsNotNone(item)
        self.assertEqual(item.expression, "break the ice")
        self.assertEqual(item.metadata['video_count'], 500)
        self.assertIn("spoken", item.scenarios)
        mock_get_content.assert_called_once()


class CrawlerIntegrationTest(TestCase):
    """爬虫集成测试"""
    
    def test_register_specialized_crawlers(self):
        """测试专业爬虫注册"""
        # 重新导入以确保注册过程
        from apps.english.expression_crawler import expression_crawler_service
        
        # 检查是否注册了所有爬虫
        expected_crawlers = ['cambridge', 'collins', 'reddit', 'urban_dictionary', 'youglish']
        
        for crawler_name in expected_crawlers:
            self.assertIn(crawler_name, expression_crawler_service.crawlers)
    
    def test_all_crawlers_inherit_correctly(self):
        """测试所有爬虫正确继承"""
        from apps.english.expression_crawler import expression_crawler_service
        
        for name, crawler in expression_crawler_service.crawlers.items():
            # 检查是否有必要的方法
            self.assertTrue(hasattr(crawler, 'crawl_expressions'))
            self.assertTrue(hasattr(crawler, 'source_name'))
            
            # 检查是否是正确的类型
            from apps.english.expression_crawler import BaseExpressionCrawler
            self.assertIsInstance(crawler, BaseExpressionCrawler)
    
    @patch('apps.english.specialized_crawlers.time.sleep')
    def test_crawling_with_rate_limiting(self, mock_sleep):
        """测试爬虫的频率限制"""
        crawler = RedditCrawler()
        
        # 模拟抓取过程（不实际发送请求）
        with patch.object(crawler, '_crawl_subreddit', return_value=[]):
            crawler.crawl_expressions(limit=10)
            
        # 验证是否调用了sleep（频率限制）
        self.assertTrue(mock_sleep.called)
    
    def test_error_handling_in_crawlers(self):
        """测试爬虫的错误处理"""
        crawler = CambridgeCrawler()
        
        # 测试无效数据的处理
        invalid_data = {'expression': '', 'meaning': ''}
        item = crawler._create_expression_item(invalid_data, "https://test.com")
        
        self.assertIsNone(item)  # 应该返回None而不是抛出异常
    
    def test_metadata_consistency(self):
        """测试元数据一致性"""
        crawlers = [
            CambridgeCrawler(),
            CollinsCrawler(),
            RedditCrawler(),
            UrbanDictionaryCrawler(),
            YouGlishCrawler()
        ]
        
        for crawler in crawlers:
            # 每个爬虫都应该有source_name
            self.assertIsNotNone(crawler.source_name)
            self.assertIsInstance(crawler.source_name, str)
            self.assertGreater(len(crawler.source_name), 0)


class ExpressionQualityTest(TestCase):
    """表达式质量测试"""
    
    def test_expression_type_classification(self):
        """测试表达式类型分类"""
        crawler = CambridgeCrawler()
        
        # 测试习语识别
        idiom_type = crawler.determine_expression_type("break the ice", "start conversation")
        self.assertEqual(idiom_type, "idiom")
        
        # 测试俚语识别
        slang_type = crawler.determine_expression_type("cool", "slang for good")
        self.assertEqual(slang_type, "slang")
    
    def test_formality_level_detection(self):
        """测试正式程度检测"""
        crawler = CambridgeCrawler()
        
        # 测试正式表达
        formal_level = crawler.determine_formality_level("", "formal business term")
        self.assertEqual(formal_level, "formal")
        
        # 测试非正式表达
        informal_level = crawler.determine_formality_level("", "informal casual expression")
        self.assertEqual(informal_level, "informal")
    
    def test_scenario_extraction_accuracy(self):
        """测试场景提取准确性"""
        crawler = CambridgeCrawler()
        
        examples = ["We use this in business meetings", "Great for workplace communication"]
        scenarios = crawler.extract_scenarios(examples, "professional expression")
        
        self.assertIn("business", scenarios)
        self.assertIn("workplace", scenarios)
    
    def test_frequency_score_calculation(self):
        """测试频率评分计算"""
        crawler = CambridgeCrawler()
        
        # 短表达式应该有较高评分
        short_score = crawler.calculate_frequency_score("get up")
        self.assertGreaterEqual(short_score, 6)
        
        # 长表达式应该有较低评分
        long_score = crawler.calculate_frequency_score("a very long and unusual expression")
        self.assertLessEqual(long_score, 6)
        
        # 评分应该在合理范围内
        self.assertGreaterEqual(short_score, 1)
        self.assertLessEqual(short_score, 10)
        self.assertGreaterEqual(long_score, 1)
        self.assertLessEqual(long_score, 10)
