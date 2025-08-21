"""
测试数据工厂测试
验证测试数据工厂的功能
"""

import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from tests.factories import (
    UserFactory, UserProfileFactory, CategoryFactory, DictionaryFactory,
    TypingWordFactory, ArticleFactory, TypingSessionFactory, UserTypingStatsFactory,
    BatchDataFactory
)

User = get_user_model()


@pytest.mark.django_db
class TestDataFactoryTest(TestCase):
    """测试数据工厂测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
    
    def test_user_factory(self):
        """测试用户工厂"""
        # 创建单个用户
        user = UserFactory()
        
        # 验证用户字段
        self.assertIsNotNone(user.username)
        self.assertIsNotNone(user.email)
        self.assertTrue(user.check_password('testpass123'))
        self.assertIsNotNone(user.first_name)
        self.assertIsNotNone(user.last_name)
        self.assertIsNotNone(user.bio)
        self.assertIsNotNone(user.website)
        
        # 创建多个用户
        users = UserFactory.create_batch(5)
        self.assertEqual(len(users), 5)
        
        # 验证用户名唯一性
        usernames = [user.username for user in users]
        self.assertEqual(len(usernames), len(set(usernames)))
        
        print("✅ 用户工厂测试通过")
    
    def test_user_profile_factory(self):
        """测试用户档案工厂"""
        # 创建用户档案
        profile = UserProfileFactory()
        
        # 验证档案字段
        self.assertIsNotNone(profile.user)
        self.assertIsNotNone(profile.phone)
        self.assertIsNotNone(profile.location)
        self.assertIsNotNone(profile.company)
        self.assertIsNotNone(profile.position)
        self.assertIsNotNone(profile.skills)
        self.assertIsNotNone(profile.github)
        self.assertIsNotNone(profile.linkedin)
        self.assertIsNotNone(profile.twitter)
        
        print("✅ 用户档案工厂测试通过")
    
    def test_category_factory(self):
        """测试分类工厂"""
        # 创建分类
        category = CategoryFactory()
        
        # 验证分类字段
        self.assertIsNotNone(category.name)
        self.assertIsNotNone(category.description)
        
        # 创建多个分类
        categories = CategoryFactory.create_batch(3)
        self.assertEqual(len(categories), 3)
        
        print("✅ 分类工厂测试通过")
    
    def test_dictionary_factory(self):
        """测试词典工厂"""
        # 创建词典
        dictionary = DictionaryFactory()
        
        # 验证词典字段
        self.assertIsNotNone(dictionary.name)
        self.assertIsNotNone(dictionary.description)
        self.assertIsNotNone(dictionary.category)
        self.assertIn(dictionary.language, ['en', 'zh', 'es', 'fr'])
        self.assertGreater(dictionary.total_words, 0)
        self.assertGreater(dictionary.chapter_count, 0)
        
        print("✅ 词典工厂测试通过")
    
    def test_typing_word_factory(self):
        """测试打字单词工厂"""
        # 创建单词
        word = TypingWordFactory()
        
        # 验证单词字段
        self.assertIsNotNone(word.word)
        self.assertIsNotNone(word.translation)
        self.assertIsNotNone(word.phonetic)
        self.assertIn(word.difficulty, ['beginner', 'intermediate', 'advanced'])
        self.assertIsNotNone(word.dictionary)
        self.assertGreater(word.chapter, 0)
        self.assertGreater(word.frequency, 0)
        
        print("✅ 打字单词工厂测试通过")
    
    def test_article_factory(self):
        """测试文章工厂"""
        # 创建文章
        article = ArticleFactory()
        
        # 验证文章字段
        self.assertIsNotNone(article.title)
        self.assertIsNotNone(article.content)
        self.assertIsNotNone(article.summary)
        self.assertIsNotNone(article.category)
        self.assertIsNotNone(article.author)
        self.assertIn(article.status, ['draft', 'published', 'archived'])
        
        print("✅ 文章工厂测试通过")
    
    def test_typing_session_factory(self):
        """测试打字练习会话工厂"""
        # 创建练习会话
        session = TypingSessionFactory()
        
        # 验证会话字段
        self.assertIsNotNone(session.user)
        self.assertIsNotNone(session.word)
        self.assertIsInstance(session.is_correct, bool)
        self.assertGreaterEqual(session.typing_speed, 10)
        self.assertLessEqual(session.typing_speed, 200)
        self.assertGreater(session.response_time, 0)
        
        print("✅ 打字练习会话工厂测试通过")
    
    def test_user_typing_stats_factory(self):
        """测试用户打字统计工厂"""
        # 创建统计
        stats = UserTypingStatsFactory()
        
        # 验证统计字段
        self.assertIsNotNone(stats.user)
        self.assertGreaterEqual(stats.total_words_practiced, 0)
        self.assertGreaterEqual(stats.total_correct_words, 0)
        self.assertGreaterEqual(stats.total_practice_time, 0)
        self.assertGreaterEqual(stats.average_typing_speed, 10)
        self.assertLessEqual(stats.average_typing_speed, 200)
        self.assertIsNotNone(stats.last_practice_date)
        
        print("✅ 用户打字统计工厂测试通过")
    
    def test_batch_data_factory(self):
        """测试批量数据工厂"""
        # 批量创建用户
        users = BatchDataFactory.create_users(10)
        self.assertEqual(len(users), 10)
        
        # 批量创建单词
        dictionary = DictionaryFactory()
        words = BatchDataFactory.create_typing_words(20, dictionary)
        self.assertEqual(len(words), 20)
        for word in words:
            self.assertEqual(word.dictionary, dictionary)
        
        # 批量创建文章
        author = UserFactory()
        articles = BatchDataFactory.create_articles(5, author)
        self.assertEqual(len(articles), 5)
        for article in articles:
            self.assertEqual(article.author, author)
        
        # 批量创建练习会话
        user = UserFactory()
        word = TypingWordFactory()
        sessions = BatchDataFactory.create_typing_sessions(10, user, word)
        self.assertEqual(len(sessions), 10)
        for session in sessions:
            self.assertEqual(session.user, user)
            self.assertEqual(session.word, word)
        
        print("✅ 批量数据工厂测试通过")
    
    def test_complete_test_data(self):
        """测试完整测试数据创建"""
        # 创建完整测试数据
        test_data = BatchDataFactory.create_complete_test_data()
        
        # 验证数据完整性
        self.assertEqual(len(test_data['users']), 5)
        self.assertEqual(len(test_data['categories']), 3)
        self.assertEqual(len(test_data['dictionaries']), 2)
        self.assertEqual(len(test_data['words']), 50)  # 2个词典 * 25个单词
        self.assertEqual(len(test_data['articles']), 18)  # 3个分类 * 2个用户 * 3篇文章
        self.assertEqual(len(test_data['sessions']), 100)  # 5个用户 * 10个单词 * 2次练习
        
        print("✅ 完整测试数据创建测试通过")


@pytest.mark.django_db
class TestDataFactoryIntegrationTest(TestCase):
    """测试数据工厂集成测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
    
    def test_factory_data_with_api(self):
        """测试工厂数据与API的集成"""
        # 使用工厂创建测试数据
        user = UserFactory()
        self.client.force_authenticate(user=user)
        
        category = CategoryFactory()
        dictionary = DictionaryFactory()
        word = TypingWordFactory(dictionary=dictionary)
        
        # 测试API调用
        # 1. 获取单词列表
        words_response = self.client.get('/api/v1/english/typing-practice/words/', {
            'dictionary': dictionary.id,
            'limit': 10
        })
        self.assertEqual(words_response.status_code, status.HTTP_200_OK)
        
        # 2. 提交练习结果
        submit_data = {
            'word_id': word.id,
            'is_correct': True,
            'typing_speed': 60,
            'response_time': 2.0
        }
        
        submit_response = self.client.post('/api/v1/english/typing-practice/submit/', submit_data, format='json')
        self.assertEqual(submit_response.status_code, status.HTTP_200_OK)
        
        # 3. 创建文章
        article_data = {
            'title': '工厂测试文章',
            'content': '这是使用工厂创建的测试文章。',
            'summary': '工厂测试文章摘要',
            'category': category.id,
            'status': 'published'
        }
        
        article_response = self.client.post('/api/v1/articles/', article_data, format='json')
        self.assertEqual(article_response.status_code, status.HTTP_201_CREATED)
        
        print("✅ 工厂数据与API集成测试通过")
    
    def test_bulk_data_performance(self):
        """测试批量数据性能"""
        import time
        
        # 测试批量创建性能
        start_time = time.time()
        
        # 创建大量测试数据
        users = UserFactory.create_batch(50)
        dictionaries = DictionaryFactory.create_batch(5)
        
        words = []
        for dictionary in dictionaries:
            words.extend(TypingWordFactory.create_batch(100, dictionary=dictionary))
        
        end_time = time.time()
        creation_time = end_time - start_time
        
        # 验证性能（500个单词应该在合理时间内创建）
        self.assertLess(creation_time, 10.0, f"批量创建500个单词耗时 {creation_time:.2f}秒，超过10秒限制")
        
        # 验证数据完整性
        self.assertEqual(len(users), 50)
        self.assertEqual(len(dictionaries), 5)
        self.assertEqual(len(words), 500)
        
        print(f"✅ 批量数据性能测试通过，创建500个单词耗时: {creation_time:.2f}秒")
    
    def test_factory_data_consistency(self):
        """测试工厂数据一致性"""
        # 创建相同配置的数据
        dictionary1 = DictionaryFactory(name='TestDict1')
        dictionary2 = DictionaryFactory(name='TestDict2')
        
        # 创建相同配置的单词
        words1 = TypingWordFactory.create_batch(10, dictionary=dictionary1, difficulty='beginner')
        words2 = TypingWordFactory.create_batch(10, dictionary=dictionary2, difficulty='beginner')
        
        # 验证数据一致性
        for word in words1:
            self.assertEqual(word.dictionary, dictionary1)
            self.assertEqual(word.difficulty, 'beginner')
        
        for word in words2:
            self.assertEqual(word.dictionary, dictionary2)
            self.assertEqual(word.difficulty, 'beginner')
        
        # 验证数据唯一性
        word_ids1 = [word.id for word in words1]
        word_ids2 = [word.id for word in words2]
        
        self.assertEqual(len(word_ids1), len(set(word_ids1)))
        self.assertEqual(len(word_ids2), len(set(word_ids2)))
        
        print("✅ 工厂数据一致性测试通过")
    
    def test_factory_data_relationships(self):
        """测试工厂数据关系"""
        # 创建有关系的测试数据
        user = UserFactory()
        profile = UserProfileFactory(user=user)
        category = CategoryFactory()
        dictionary = DictionaryFactory()
        word = TypingWordFactory(dictionary=dictionary)
        article = ArticleFactory(author=user, category=category)
        session = TypingSessionFactory(user=user, word=word)
        
        # 验证关系正确性
        self.assertEqual(profile.user, user)
        self.assertEqual(word.dictionary, dictionary)
        self.assertEqual(article.author, user)
        self.assertEqual(article.category, category)
        self.assertEqual(session.user, user)
        self.assertEqual(session.word, word)
        
        # 验证反向关系
        self.assertEqual(user.profile, profile)
        self.assertIn(word, dictionary.typingword_set.all())
        self.assertIn(article, user.article_set.all())
        self.assertIn(article, category.article_set.all())
        self.assertIn(session, user.typingsession_set.all())
        self.assertIn(session, word.typingsession_set.all())
        
        print("✅ 工厂数据关系测试通过")
