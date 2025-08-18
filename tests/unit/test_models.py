"""
模型单元测试
测试所有数据模型的功能
"""

import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

from apps.articles.models import Article
from apps.categories.models import Category
from apps.english.models import Word, Expression, News, UserWordProgress
from apps.users.models import UserProfile

User = get_user_model()


class UserModelTest(TestCase):
    """用户模型测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_creation(self):
        """测试用户创建"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertFalse(self.user.is_superuser)
        self.assertFalse(self.user.is_staff)
    
    def test_user_str_representation(self):
        """测试用户字符串表示"""
        self.assertEqual(str(self.user), 'testuser')
    
    def test_user_profile_creation(self):
        """测试用户资料自动创建"""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsInstance(self.user.profile, UserProfile)


class UserProfileModelTest(TestCase):
    """用户资料模型测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = self.user.profile
    
    def test_profile_creation(self):
        """测试资料创建"""
        self.assertEqual(self.profile.user, self.user)
        self.assertEqual(self.profile.avatar_url, '')  # 默认为空字符串
    
    def test_profile_str_representation(self):
        """测试资料字符串表示"""
        self.assertEqual(str(self.profile), f'{self.user.username}的资料')


class ArticleModelTest(TestCase):
    """文章模型测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='测试分类',
            description='测试分类描述'
        )
        self.article = Article.objects.create(
            title='测试文章',
            content='测试文章内容',
            author=self.user,
            category=self.category
        )
    
    def test_article_creation(self):
        """测试文章创建"""
        self.assertEqual(self.article.title, '测试文章')
        self.assertEqual(self.article.content, '测试文章内容')
        self.assertEqual(self.article.author, self.user)
        self.assertEqual(self.article.category, self.category)
        self.assertFalse(self.article.is_published)
    
    def test_article_str_representation(self):
        """测试文章字符串表示"""
        self.assertEqual(str(self.article), '测试文章')
    
    def test_article_timestamps(self):
        """测试文章时间戳"""
        self.assertIsNotNone(self.article.created_at)
        self.assertIsNotNone(self.article.updated_at)
        self.assertEqual(self.article.created_at, self.article.updated_at)


class CategoryModelTest(TestCase):
    """分类模型测试"""
    
    def setUp(self):
        self.category = Category.objects.create(
            name='测试分类',
            description='测试分类描述'
        )
    
    def test_category_creation(self):
        """测试分类创建"""
        self.assertEqual(self.category.name, '测试分类')
        self.assertEqual(self.category.description, '测试分类描述')
    
    def test_category_str_representation(self):
        """测试分类字符串表示"""
        self.assertEqual(str(self.category), '测试分类')


class WordModelTest(TestCase):
    """单词模型测试"""
    
    def setUp(self):
        self.word = Word.objects.create(
            word='test',
            phonetic='/test/',
            definition='A procedure intended to establish the quality or performance of something.',
            example='This is a test sentence.',
            difficulty_level='intermediate'
        )
    
    def test_word_creation(self):
        """测试单词创建"""
        self.assertEqual(self.word.word, 'test')
        self.assertEqual(self.word.phonetic, '/test/')
        self.assertEqual(self.word.definition, 'A procedure intended to establish the quality or performance of something.')
        self.assertEqual(self.word.example, 'This is a test sentence.')
        self.assertEqual(self.word.difficulty_level, 'intermediate')
    
    def test_word_str_representation(self):
        """测试单词字符串表示"""
        self.assertEqual(str(self.word), 'test')
    
    def test_word_difficulty_choices(self):
        """测试单词难度级别选择"""
        valid_levels = ['beginner', 'intermediate', 'advanced']
        self.assertIn(self.word.difficulty_level, valid_levels)


class ExpressionModelTest(TestCase):
    """表达模型测试"""
    
    def setUp(self):
        self.expression = Expression.objects.create(
            expression='break the ice',
            meaning='To initiate conversation in a social setting',
            usage_examples='Let me break the ice by introducing myself.',
            difficulty_level='intermediate'
        )
    
    def test_expression_creation(self):
        """测试表达创建"""
        self.assertEqual(self.expression.expression, 'break the ice')
        self.assertEqual(self.expression.meaning, 'To initiate conversation in a social setting')
        self.assertEqual(self.expression.usage_examples, 'Let me break the ice by introducing myself.')
        self.assertEqual(self.expression.difficulty_level, 'intermediate')
    
    def test_expression_str_representation(self):
        """测试表达字符串表示"""
        self.assertEqual(str(self.expression), 'break the ice')


class NewsModelTest(TestCase):
    """新闻模型测试"""
    
    def setUp(self):
        self.news = News.objects.create(
            title='Test News Title',
            content='This is a test news content.',
            source='test_source',
            source_url='https://example.com/test-news',
            publish_date=timezone.now().date(),
            difficulty_level='intermediate'
        )
    
    def test_news_creation(self):
        """测试新闻创建"""
        self.assertEqual(self.news.title, 'Test News Title')
        self.assertEqual(self.news.content, 'This is a test news content.')
        self.assertEqual(self.news.source, 'test_source')
        self.assertEqual(self.news.source_url, 'https://example.com/test-news')
        self.assertEqual(self.news.difficulty_level, 'intermediate')
    
    def test_news_str_representation(self):
        """测试新闻字符串表示"""
        self.assertEqual(str(self.news), 'Test News Title')
    
    def test_news_published_date(self):
        """测试新闻发布日期"""
        self.assertIsNotNone(self.news.publish_date)
        self.assertLessEqual(self.news.publish_date, timezone.now().date())


class UserWordProgressModelTest(TestCase):
    """用户单词进度模型测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.word = Word.objects.create(
            word='test',
            phonetic='/test/',
            definition='A test definition.',
            difficulty_level='intermediate'
        )
        self.progress = UserWordProgress.objects.create(
            user=self.user,
            word=self.word,
            review_count=0,
            next_review_date=timezone.now(),
            mastery_level=0
        )
    
    def test_progress_creation(self):
        """测试进度创建"""
        self.assertEqual(self.progress.user, self.user)
        self.assertEqual(self.progress.word, self.word)
        self.assertEqual(self.progress.review_count, 0)
        self.assertEqual(self.progress.mastery_level, 0)
    
    def test_progress_str_representation(self):
        """测试进度字符串表示"""
        # UserWordProgress模型没有自定义__str__方法，使用默认的Django表示
        expected = f'UserWordProgress object ({self.progress.id})'
        self.assertEqual(str(self.progress), expected)
    
    def test_progress_mastery_level_validation(self):
        """测试掌握级别验证"""
        # 测试有效值
        self.progress.mastery_level = 5
        self.progress.full_clean()
        
        # 测试无效值
        with self.assertRaises(ValidationError):
            self.progress.mastery_level = 11
            self.progress.full_clean()


@pytest.mark.fast
class FastModelTests:
    """快速模型测试"""
    
    def test_model_imports(self):
        """测试模型导入"""
        from apps.articles.models import Article, Category
        from apps.english.models import Word, Expression, News, UserWordProgress
        from apps.users.models import UserProfile
        assert True  # 如果导入成功，测试通过


@pytest.mark.slow
class SlowModelTests:
    """慢速模型测试"""
    
    def test_bulk_operations(self):
        """测试批量操作"""
        # 这里可以添加需要较长时间的批量操作测试
        assert True
