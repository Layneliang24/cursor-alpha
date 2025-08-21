"""
性能回归测试
用于检测业务逻辑修改是否导致性能退化
"""

import time
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.english.models import TypingWord, Dictionary, TypingSession, UserTypingStats
from apps.articles.models import Article
from apps.categories.models import Category
from apps.users.models import UserProfile

User = get_user_model()


@pytest.mark.django_db
class PerformanceRegressionTest(TestCase):
    """性能回归测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # 创建测试数据
        self.dictionary = Dictionary.objects.create(
            name='PerformanceTest',
            description='性能测试词库',
            category='TEST',
            language='en',
            total_words=1000,
            chapter_count=10
        )
        
        # 创建大量测试单词
        self.words = []
        for i in range(100):
            word = TypingWord.objects.create(
                word=f'test_word_{i}',
                translation=f'测试单词_{i}',
                phonetic=f'/test{i}/',
                difficulty='beginner',
                dictionary=self.dictionary,
                chapter=1,
                frequency=i
            )
            self.words.append(word)
        
        # 创建分类
        self.category = Category.objects.create(
            name='性能测试分类',
            description='用于性能测试的分类'
        )
    
    def test_typing_practice_bulk_submission_performance(self):
        """测试大量打字练习提交的性能"""
        # 性能基准：100次提交应该在5秒内完成
        start_time = time.time()
        
        for i in range(100):
            word = self.words[i % len(self.words)]
            response = self.client.post('/api/v1/english/typing-practice/submit/', {
                'word_id': word.id,
                'is_correct': True,
                'typing_speed': 60 + i,
                'response_time': 2.0 + (i * 0.01)
            }, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # 性能断言：100次提交应该在5秒内完成
        self.assertLess(execution_time, 5.0, 
                       f"100次打字练习提交耗时 {execution_time:.2f}秒，超过5秒限制")
        
        print(f"✅ 100次打字练习提交耗时: {execution_time:.2f}秒")
    
    def test_typing_words_query_performance(self):
        """测试打字单词查询的性能"""
        # 性能基准：查询100个单词应该在1秒内完成
        start_time = time.time()
        
        response = self.client.get('/api/v1/english/typing-practice/words/', {
            'dictionary': self.dictionary.id,
            'limit': 100
        })
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLess(execution_time, 1.0, 
                       f"查询100个单词耗时 {execution_time:.2f}秒，超过1秒限制")
        
        print(f"✅ 查询100个单词耗时: {execution_time:.2f}秒")
    
    def test_article_search_performance(self):
        """测试文章搜索的性能"""
        # 创建大量测试文章
        articles = []
        for i in range(50):
            article = Article.objects.create(
                title=f'性能测试文章_{i}',
                content=f'这是第{i}篇性能测试文章的内容。' * 10,  # 增加内容长度
                summary=f'文章{i}摘要',
                category=self.category,
                author=self.user,
                status='published'
            )
            articles.append(article)
        
        # 性能基准：搜索50篇文章应该在2秒内完成
        start_time = time.time()
        
        response = self.client.get('/api/v1/articles/', {
            'search': '性能测试',
            'page_size': 50
        })
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLess(execution_time, 2.0, 
                       f"搜索50篇文章耗时 {execution_time:.2f}秒，超过2秒限制")
        
        print(f"✅ 搜索50篇文章耗时: {execution_time:.2f}秒")
    
    def test_statistics_calculation_performance(self):
        """测试统计计算的性能"""
        # 创建大量练习记录
        for i in range(200):
            word = self.words[i % len(self.words)]
            TypingSession.objects.create(
                user=self.user,
                word=word,
                is_correct=i % 2 == 0,  # 交替正确和错误
                typing_speed=50 + (i % 30),
                response_time=1.0 + (i % 5) * 0.5
            )
        
        # 性能基准：统计计算应该在1秒内完成
        start_time = time.time()
        
        response = self.client.get('/api/v1/english/typing-practice/statistics/')
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLess(execution_time, 1.0, 
                       f"统计计算耗时 {execution_time:.2f}秒，超过1秒限制")
        
        print(f"✅ 统计计算耗时: {execution_time:.2f}秒")
    
    def test_concurrent_access_performance(self):
        """测试并发访问的性能"""
        import threading
        import queue
        
        results = queue.Queue()
        
        def worker(worker_id):
            """工作线程函数"""
            try:
                # 每个线程执行10次查询
                for i in range(10):
                    response = self.client.get('/api/v1/english/typing-practice/words/', {
                        'dictionary': self.dictionary.id,
                        'limit': 10
                    })
                    if response.status_code != status.HTTP_200_OK:
                        results.put(f"Worker {worker_id} failed at iteration {i}")
                        return
                results.put(f"Worker {worker_id} completed successfully")
            except Exception as e:
                results.put(f"Worker {worker_id} failed with exception: {e}")
        
        # 启动10个并发线程
        threads = []
        start_time = time.time()
        
        for i in range(10):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # 检查所有线程是否成功完成
        failures = []
        while not results.empty():
            result = results.get()
            if "failed" in result:
                failures.append(result)
        
        self.assertEqual(len(failures), 0, f"并发测试失败: {failures}")
        self.assertLess(execution_time, 10.0, 
                       f"10个并发线程执行100次查询耗时 {execution_time:.2f}秒，超过10秒限制")
        
        print(f"✅ 10个并发线程执行100次查询耗时: {execution_time:.2f}秒")


@pytest.mark.django_db
class MemoryUsageTest(TestCase):
    """内存使用测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='memorytest',
            email='memory@test.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_memory_usage_with_large_data(self):
        """测试大数据量下的内存使用"""
        import psutil
        import os
        
        # 获取初始内存使用
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 创建大量数据
        dictionary = Dictionary.objects.create(
            name='MemoryTest',
            description='内存测试词库',
            category='TEST',
            language='en',
            total_words=1000,
            chapter_count=10
        )
        
        # 创建1000个单词
        words = []
        for i in range(1000):
            word = TypingWord.objects.create(
                word=f'memory_word_{i}',
                translation=f'内存测试单词_{i}',
                phonetic=f'/memory{i}/',
                difficulty='beginner',
                dictionary=dictionary,
                chapter=1,
                frequency=i
            )
            words.append(word)
        
        # 执行查询操作
        response = self.client.get('/api/v1/english/typing-practice/words/', {
            'dictionary': dictionary.id,
            'limit': 1000
        })
        
        # 获取最终内存使用
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 内存增长应该在合理范围内（小于100MB）
        self.assertLess(memory_increase, 100.0, 
                       f"内存使用增长 {memory_increase:.2f}MB，超过100MB限制")
        
        print(f"✅ 内存使用增长: {memory_increase:.2f}MB")


@pytest.mark.django_db
class DatabaseQueryOptimizationTest(TestCase):
    """数据库查询优化测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='querytest',
            email='query@test.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_database_query_count(self):
        """测试数据库查询次数"""
        from django.db import connection, reset_queries
        from django.test.utils import override_settings
        
        # 创建测试数据
        dictionary = Dictionary.objects.create(
            name='QueryTest',
            description='查询测试词库',
            category='TEST',
            language='en',
            total_words=100,
            chapter_count=5
        )
        
        for i in range(50):
            TypingWord.objects.create(
                word=f'query_word_{i}',
                translation=f'查询测试单词_{i}',
                phonetic=f'/query{i}/',
                difficulty='beginner',
                dictionary=dictionary,
                chapter=1,
                frequency=i
            )
        
        # 重置查询计数
        reset_queries()
        
        # 执行查询
        response = self.client.get('/api/v1/english/typing-practice/words/', {
            'dictionary': dictionary.id,
            'limit': 50
        })
        
        # 获取查询次数
        query_count = len(connection.queries)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 查询次数应该在合理范围内（小于10次）
        self.assertLess(query_count, 10, 
                       f"数据库查询次数 {query_count}，超过10次限制")
        
        print(f"✅ 数据库查询次数: {query_count}")
        
        # 打印查询详情（调试用）
        for i, query in enumerate(connection.queries):
            print(f"Query {i+1}: {query['sql'][:100]}...")
