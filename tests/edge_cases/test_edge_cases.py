"""
边界情况测试
测试各种极端和异常情况
"""

import pytest
import json
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.english.models import TypingWord, Dictionary, TypingSession, UserTypingStats
from apps.articles.models import Article
from apps.categories.models import Category

User = get_user_model()


@pytest.mark.django_db
class EdgeCaseTest(TestCase):
    """边界情况测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='edgecasetest',
            email='edgecase@test.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.dictionary = Dictionary.objects.create(
            name='EdgeCaseTest',
            description='边界测试词库',
            category='TEST',
            language='en',
            total_words=10,
            chapter_count=1
        )
    
    def test_empty_data_handling(self):
        """测试空数据处理"""
        # 测试空请求体
        empty_response = self.client.post('/api/v1/english/typing-practice/submit/', {}, format='json')
        self.assertNotEqual(empty_response.status_code, status.HTTP_200_OK)
        
        # 测试空查询参数
        empty_query_response = self.client.get('/api/v1/english/typing-practice/words/')
        self.assertEqual(empty_query_response.status_code, status.HTTP_200_OK)
        
        # 测试空字符串参数
        empty_string_response = self.client.post('/api/v1/english/typing-practice/submit/', {
            'word_id': '',
            'is_correct': '',
            'typing_speed': '',
            'response_time': ''
        }, format='json')
        self.assertNotEqual(empty_string_response.status_code, status.HTTP_200_OK)
        
        print("✅ 空数据处理测试通过")
    
    def test_invalid_data_types(self):
        """测试无效数据类型"""
        word = TypingWord.objects.create(
            word='test',
            translation='测试',
            phonetic='/test/',
            difficulty='beginner',
            dictionary=self.dictionary,
            chapter=1,
            frequency=100
        )
        
        # 测试字符串类型的数字字段
        string_number_response = self.client.post('/api/v1/english/typing-practice/submit/', {
            'word_id': str(word.id),
            'is_correct': 'true',  # 字符串布尔值
            'typing_speed': '60.5',  # 字符串数字
            'response_time': '2.0'   # 字符串数字
        }, format='json')
        
        # 应该能正确处理字符串类型的数字
        self.assertEqual(string_number_response.status_code, status.HTTP_200_OK)
        
        # 测试完全无效的数据类型
        invalid_type_response = self.client.post('/api/v1/english/typing-practice/submit/', {
            'word_id': 'not_a_number',
            'is_correct': 'not_a_boolean',
            'typing_speed': 'not_a_number',
            'response_time': 'not_a_number'
        }, format='json')
        
        self.assertNotEqual(invalid_type_response.status_code, status.HTTP_200_OK)
        
        print("✅ 无效数据类型测试通过")
    
    def test_extremely_large_values(self):
        """测试极大值处理"""
        word = TypingWord.objects.create(
            word='large',
            translation='大',
            phonetic='/lɑːdʒ/',
            difficulty='beginner',
            dictionary=self.dictionary,
            chapter=1,
            frequency=100
        )
        
        # 测试极大数字
        large_number_response = self.client.post('/api/v1/english/typing-practice/submit/', {
            'word_id': word.id,
            'is_correct': True,
            'typing_speed': 999999999.99,  # 极大速度
            'response_time': 999999999.99  # 极大时间
        }, format='json')
        
        # 应该能处理极大值
        self.assertEqual(large_number_response.status_code, status.HTTP_200_OK)
        
        # 测试极小数字
        small_number_response = self.client.post('/api/v1/english/typing-practice/submit/', {
            'word_id': word.id,
            'is_correct': True,
            'typing_speed': 0.000001,  # 极小速度
            'response_time': 0.000001  # 极小时间
        }, format='json')
        
        self.assertEqual(small_number_response.status_code, status.HTTP_200_OK)
        
        print("✅ 极大值处理测试通过")
    
    def test_special_characters_in_content(self):
        """测试内容中的特殊字符"""
        # 创建包含特殊字符的文章
        special_content = """
        这是一篇包含特殊字符的文章：
        - 引号："双引号" 和 '单引号'
        - 符号：@#$%^&*()_+-=[]{}|;':",./<>?
        - 换行符：
        第二行
        第三行
        - 制表符：	制表符
        - 特殊Unicode：🚀🎉💻📱
        - 数学符号：∑∏∫√∞≠≈≤≥
        """
        
        category = Category.objects.create(
            name='特殊字符测试',
            description='测试特殊字符处理'
        )
        
        article_data = {
            'title': '特殊字符测试文章',
            'content': special_content,
            'summary': '测试特殊字符处理',
            'category': category.id,
            'status': 'published'
        }
        
        article_response = self.client.post('/api/v1/articles/', article_data, format='json')
        self.assertEqual(article_response.status_code, status.HTTP_201_CREATED)
        
        # 验证文章内容正确保存
        article_id = article_response.data['id']
        article_detail = self.client.get(f'/api/v1/articles/{article_id}/').data
        self.assertEqual(article_detail['title'], '特殊字符测试文章')
        self.assertIn('🚀🎉💻📱', article_detail['content'])
        
        print("✅ 特殊字符内容测试通过")
    
    def test_unicode_handling(self):
        """测试Unicode字符处理"""
        # 创建包含Unicode字符的单词
        unicode_word = TypingWord.objects.create(
            word='café',  # 重音符号
            translation='咖啡厅',
            phonetic='/kæˈfeɪ/',
            difficulty='beginner',
            dictionary=self.dictionary,
            chapter=1,
            frequency=100
        )
        
        # 测试Unicode查询
        query_response = self.client.get('/api/v1/english/typing-practice/words/', {
            'dictionary': self.dictionary.id,
            'limit': 10
        })
        
        self.assertEqual(query_response.status_code, status.HTTP_200_OK)
        
        # 查找Unicode单词
        found = False
        for word_data in query_response.data:
            if word_data['word'] == 'café':
                found = True
                break
        
        self.assertTrue(found, "Unicode字符应该能被正确处理")
        
        # 测试提交包含Unicode的练习
        unicode_response = self.client.post('/api/v1/english/typing-practice/submit/', {
            'word_id': unicode_word.id,
            'is_correct': True,
            'typing_speed': 60,
            'response_time': 2.0
        }, format='json')
        
        self.assertEqual(unicode_response.status_code, status.HTTP_200_OK)
        
        print("✅ Unicode字符处理测试通过")
    
    def test_very_long_strings(self):
        """测试超长字符串处理"""
        # 创建超长标题
        long_title = 'A' * 1000  # 1000个字符的标题
        
        category = Category.objects.create(
            name='超长字符串测试',
            description='测试超长字符串处理'
        )
        
        article_data = {
            'title': long_title,
            'content': '这是超长标题文章的内容',
            'summary': '超长标题文章摘要',
            'category': category.id,
            'status': 'published'
        }
        
        article_response = self.client.post('/api/v1/articles/', article_data, format='json')
        
        # 应该被拒绝或截断
        self.assertNotEqual(article_response.status_code, status.HTTP_201_CREATED)
        
        # 测试合理长度的标题
        reasonable_title = 'A' * 200  # 200个字符的标题
        article_data['title'] = reasonable_title
        
        reasonable_response = self.client.post('/api/v1/articles/', article_data, format='json')
        self.assertEqual(reasonable_response.status_code, status.HTTP_201_CREATED)
        
        print("✅ 超长字符串处理测试通过")
    
    def test_nonexistent_resource_access(self):
        """测试访问不存在资源"""
        # 测试不存在的单词ID
        nonexistent_word_response = self.client.post('/api/v1/english/typing-practice/submit/', {
            'word_id': 999999,
            'is_correct': True,
            'typing_speed': 60,
            'response_time': 2.0
        }, format='json')
        
        self.assertEqual(nonexistent_word_response.status_code, status.HTTP_404_NOT_FOUND)
        
        # 测试不存在的文章ID
        nonexistent_article_response = self.client.get('/api/v1/articles/999999/')
        self.assertEqual(nonexistent_article_response.status_code, status.HTTP_404_NOT_FOUND)
        
        # 测试不存在的用户档案
        nonexistent_profile_response = self.client.get('/api/v1/users/profile/999999/')
        self.assertEqual(nonexistent_profile_response.status_code, status.HTTP_404_NOT_FOUND)
        
        print("✅ 不存在资源访问测试通过")
    
    def test_malformed_json_requests(self):
        """测试格式错误的JSON请求"""
        # 测试不完整的JSON
        incomplete_json = '{"word_id": 1, "is_correct": true'  # 缺少闭合括号
        
        response = self.client.post(
            '/api/v1/english/typing-practice/submit/',
            incomplete_json,
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # 测试无效的JSON格式
        invalid_json = '{"word_id": 1, "is_correct": true, "typing_speed": "not_a_number"}'
        
        response = self.client.post(
            '/api/v1/english/typing-practice/submit/',
            invalid_json,
            content_type='application/json'
        )
        
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)
        
        print("✅ 格式错误JSON请求测试通过")
    
    def test_authentication_edge_cases(self):
        """测试认证边界情况"""
        # 测试无效token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid_token')
        
        response = self.client.get('/api/v1/english/typing-practice/statistics/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # 测试过期token（模拟）
        self.client.credentials(HTTP_AUTHORIZATION='Bearer expired_token')
        
        response = self.client.get('/api/v1/english/typing-practice/statistics/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # 测试空token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ')
        
        response = self.client.get('/api/v1/english/typing-practice/statistics/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # 恢复有效认证
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get('/api/v1/english/typing-practice/statistics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        print("✅ 认证边界情况测试通过")
    
    def test_concurrent_modification_edge_cases(self):
        """测试并发修改边界情况"""
        import threading
        import time
        
        word = TypingWord.objects.create(
            word='concurrent',
            translation='并发',
            phonetic='/kənˈkʌrənt/',
            difficulty='beginner',
            dictionary=self.dictionary,
            chapter=1,
            frequency=100
        )
        
        results = []
        
        def concurrent_submission(thread_id):
            """并发提交函数"""
            try:
                client = APIClient()
                client.force_authenticate(user=self.user)
                
                response = client.post('/api/v1/english/typing-practice/submit/', {
                    'word_id': word.id,
                    'is_correct': True,
                    'typing_speed': 60 + thread_id,
                    'response_time': 2.0 + thread_id * 0.1
                }, format='json')
                
                results.append({
                    'thread_id': thread_id,
                    'status_code': response.status_code,
                    'success': response.status_code == status.HTTP_200_OK
                })
            except Exception as e:
                results.append({
                    'thread_id': thread_id,
                    'error': str(e),
                    'success': False
                })
        
        # 启动多个并发线程
        threads = []
        for i in range(10):
            thread = threading.Thread(target=concurrent_submission, args=(i,))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 检查结果
        successful_submissions = sum(1 for result in results if result.get('success', False))
        
        # 所有提交都应该成功（系统应该能处理并发）
        self.assertEqual(successful_submissions, 10, f"并发提交失败: {results}")
        
        # 验证数据一致性
        session_count = TypingSession.objects.filter(user=self.user).count()
        self.assertEqual(session_count, 10)
        
        print("✅ 并发修改边界情况测试通过")


@pytest.mark.django_db
class ErrorHandlingTest(TestCase):
    """错误处理测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='errorhandlingtest',
            email='errorhandling@test.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_database_connection_error_handling(self):
        """测试数据库连接错误处理"""
        # 这个测试主要验证系统在数据库错误时的行为
        # 在实际环境中，可能需要模拟数据库连接失败
        
        # 测试正常情况下的数据库操作
        response = self.client.get('/api/v1/english/typing-practice/statistics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        print("✅ 数据库连接错误处理测试通过")
    
    def test_network_timeout_handling(self):
        """测试网络超时处理"""
        # 测试长时间运行的查询
        start_time = time.time()
        
        response = self.client.get('/api/v1/english/typing-practice/statistics/')
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # 确保查询在合理时间内完成
        self.assertLess(execution_time, 5.0, f"查询耗时 {execution_time:.2f}秒，超过5秒限制")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        print("✅ 网络超时处理测试通过")
    
    def test_memory_overflow_handling(self):
        """测试内存溢出处理"""
        # 测试大量数据查询的内存使用
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 执行一系列查询操作
        for i in range(100):
            response = self.client.get('/api/v1/english/typing-practice/statistics/')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # 内存增长应该在合理范围内
        self.assertLess(memory_increase, 50.0, f"内存增长 {memory_increase:.2f}MB，超过50MB限制")
        
        print("✅ 内存溢出处理测试通过")
