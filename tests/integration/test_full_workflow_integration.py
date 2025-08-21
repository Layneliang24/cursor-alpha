"""
完整工作流集成测试
测试跨模块的完整业务流程
"""

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
class FullLearningWorkflowTest(TestCase):
    """完整学习工作流测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='workflowtest',
            email='workflow@test.com',
            password='testpass123'
        )
        
        # 创建测试数据
        self.category = Category.objects.create(
            name='工作流测试分类',
            description='用于工作流测试的分类'
        )
        
        self.dictionary = Dictionary.objects.create(
            name='WorkflowTest',
            description='工作流测试词库',
            category='TEST',
            language='en',
            total_words=100,
            chapter_count=5
        )
        
        # 创建测试单词
        self.words = []
        for i in range(20):
            word = TypingWord.objects.create(
                word=f'workflow_word_{i}',
                translation=f'工作流测试单词_{i}',
                phonetic=f'/workflow{i}/',
                difficulty='beginner',
                dictionary=self.dictionary,
                chapter=1,
                frequency=i
            )
            self.words.append(word)
    
    def test_complete_user_learning_workflow(self):
        """测试完整的用户学习工作流"""
        # 1. 用户注册和登录
        register_data = {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        }
        
        register_response = self.client.post('/api/v1/auth/register/', register_data, format='json')
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)
        
        # 登录
        login_data = {
            'username': 'newuser',
            'password': 'testpass123'
        }
        
        login_response = self.client.post('/api/v1/auth/login/', login_data, format='json')
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        
        token = login_response.data['tokens']['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # 2. 获取学习内容
        words_response = self.client.get('/api/v1/english/typing-practice/words/', {
            'dictionary': self.dictionary.id,
            'limit': 10
        })
        self.assertEqual(words_response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(words_response.data), 0)
        
        # 3. 完成练习
        practice_results = []
        for i, word_data in enumerate(words_response.data[:5]):
            result = self.client.post('/api/v1/english/typing-practice/submit/', {
                'word_id': word_data['id'],
                'is_correct': i % 2 == 0,  # 交替正确和错误
                'typing_speed': 50 + i * 5,
                'response_time': 2.0 + i * 0.5
            }, format='json')
            self.assertEqual(result.status_code, status.HTTP_200_OK)
            practice_results.append(result.data)
        
        # 4. 查看学习统计
        stats_response = self.client.get('/api/v1/english/typing-practice/statistics/')
        self.assertEqual(stats_response.status_code, status.HTTP_200_OK)
        
        stats = stats_response.data
        self.assertIn('total_practices', stats)
        self.assertIn('average_accuracy', stats)
        self.assertIn('average_speed', stats)
        
        # 验证统计数据正确性
        self.assertEqual(stats['total_practices'], 5)
        expected_accuracy = (3 / 5) * 100  # 3个正确，5个总数
        self.assertAlmostEqual(stats['average_accuracy'], expected_accuracy, delta=1.0)
        
        # 5. 查看练习历史
        history_response = self.client.get('/api/v1/english/typing-practice/history/')
        self.assertEqual(history_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(history_response.data['results']), 5)
        
        # 6. 查看文章内容（跨模块功能）
        article_data = {
            'title': '学习工作流测试文章',
            'content': '这是一篇用于测试学习工作流的文章内容。',
            'summary': '工作流测试文章摘要',
            'category': self.category.id,
            'status': 'published'
        }
        
        article_response = self.client.post('/api/v1/articles/', article_data, format='json')
        self.assertEqual(article_response.status_code, status.HTTP_201_CREATED)
        
        # 7. 搜索文章
        search_response = self.client.get('/api/v1/articles/', {
            'search': '工作流'
        })
        self.assertEqual(search_response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(search_response.data.get('data', [])), 0)
        
        print("✅ 完整学习工作流测试通过")
    
    def test_data_consistency_across_modules(self):
        """测试跨模块数据一致性"""
        # 设置认证
        self.client.force_authenticate(user=self.user)
        
        # 1. 创建练习记录
        for i in range(10):
            word = self.words[i % len(self.words)]
            response = self.client.post('/api/v1/english/typing-practice/submit/', {
                'word_id': word.id,
                'is_correct': True,
                'typing_speed': 60,
                'response_time': 2.0
            }, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 2. 验证数据一致性
        # 检查TypingSession记录
        session_count = TypingSession.objects.filter(user=self.user).count()
        self.assertEqual(session_count, 10)
        
        # 检查UserTypingStats统计
        stats = UserTypingStats.objects.get(user=self.user)
        self.assertEqual(stats.total_words_practiced, 10)
        self.assertEqual(stats.total_correct_words, 10)
        
        # 3. 验证API返回的数据一致性
        api_stats = self.client.get('/api/v1/english/typing-practice/statistics/').data
        self.assertEqual(api_stats['total_practices'], 10)
        self.assertEqual(api_stats['total_words_practiced'], 10)
        self.assertEqual(api_stats['total_correct_words'], 10)
        
        # 4. 验证历史记录一致性
        history = self.client.get('/api/v1/english/typing-practice/history/').data
        self.assertEqual(len(history['results']), 10)
        
        print("✅ 跨模块数据一致性测试通过")
    
    def test_error_recovery_and_rollback(self):
        """测试错误恢复和回滚机制"""
        self.client.force_authenticate(user=self.user)
        
        # 1. 记录初始状态
        initial_session_count = TypingSession.objects.filter(user=self.user).count()
        
        # 确保UserTypingStats存在
        stats, created = UserTypingStats.objects.get_or_create(user=self.user)
        initial_total_practiced = stats.total_words_practiced
        
        # 2. 执行一系列操作，其中包含错误
        successful_submissions = 0
        for i in range(5):
            word = self.words[i % len(self.words)]
            
            # 正常提交
            response = self.client.post('/api/v1/english/typing-practice/submit/', {
                'word_id': word.id,
                'is_correct': True,
                'typing_speed': 60,
                'response_time': 2.0
            }, format='json')
            
            if response.status_code == status.HTTP_200_OK:
                successful_submissions += 1
            
            # 故意提交错误数据（应该被拒绝）
            error_response = self.client.post('/api/v1/english/typing-practice/submit/', {
                'word_id': 99999,  # 不存在的单词ID
                'is_correct': True,
                'typing_speed': 60,
                'response_time': 2.0
            }, format='json')
            
            # 错误提交应该被拒绝
            self.assertNotEqual(error_response.status_code, status.HTTP_200_OK)
        
        # 3. 验证系统状态一致性
        final_session_count = TypingSession.objects.filter(user=self.user).count()
        final_stats = UserTypingStats.objects.get(user=self.user)
        
        # 只有成功的提交应该被记录
        expected_new_sessions = successful_submissions
        self.assertEqual(final_session_count, initial_session_count + expected_new_sessions)
        self.assertEqual(final_stats.total_words_practiced, initial_total_practiced + expected_new_sessions)
        
        print("✅ 错误恢复和回滚机制测试通过")


@pytest.mark.django_db
class CrossModuleIntegrationTest(TestCase):
    """跨模块集成测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='crossmoduletest',
            email='crossmodule@test.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # 创建测试数据
        self.category = Category.objects.create(
            name='跨模块测试分类',
            description='用于跨模块测试的分类'
        )
        
        self.dictionary = Dictionary.objects.create(
            name='CrossModuleTest',
            description='跨模块测试词库',
            category='TEST',
            language='en',
            total_words=50,
            chapter_count=3
        )
    
    def test_user_profile_integration(self):
        """测试用户档案集成"""
        # 1. 创建用户档案
        profile_data = {
            'bio': '测试用户简介',
            'location': '测试城市',
            'website': 'https://test.com'
        }
        
        profile_response = self.client.get('/api/v1/profiles/me/')
        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)
        
        # 2. 验证档案创建
        profile = UserProfile.objects.get(user=self.user)
        
        # 3. 更新档案
        update_data = {
            'bio': '更新后的用户简介',
            'location': '新城市'
        }
        
        update_response = self.client.patch('/api/v1/profiles/me/', update_data, format='json')
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        
        # 4. 验证更新
        profile.refresh_from_db()
        self.assertEqual(profile.bio, '更新后的用户简介')
        
        print("✅ 用户档案集成测试通过")
    
    def test_article_typing_integration(self):
        """测试文章和打字练习的集成"""
        # 1. 创建文章
        article_data = {
            'title': '打字练习相关文章',
            'content': '这篇文章包含一些需要练习的单词：test, example, practice',
            'summary': '打字练习文章摘要',
            'category': self.category.id,
            'status': 'published'
        }
        
        article_response = self.client.post('/api/v1/articles/', article_data, format='json')
        self.assertEqual(article_response.status_code, status.HTTP_201_CREATED)
        
        # 从响应中获取文章ID
        article_id = article_response.data.get('id')
        if not article_id:
            # 如果响应中没有id，尝试从数据库中找到刚创建的文章
            article = Article.objects.filter(title='打字练习相关文章').first()
            article_id = article.id if article else None
        
        # 2. 创建相关单词
        words = ['test', 'example', 'practice']
        created_words = []
        
        for word_text in words:
            word = TypingWord.objects.create(
                word=word_text,
                translation=f'{word_text}的翻译',
                phonetic=f'/{word_text}/',
                difficulty='beginner',
                dictionary=self.dictionary,
                chapter=1,
                frequency=100
            )
            created_words.append(word)
        
        # 3. 练习文章中的单词
        for word in created_words:
            response = self.client.post('/api/v1/english/typing-practice/submit/', {
                'word_id': word.id,
                'is_correct': True,
                'typing_speed': 60,
                'response_time': 2.0
            }, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 4. 验证学习进度
        stats = self.client.get('/api/v1/english/typing-practice/statistics/').data
        self.assertEqual(stats['total_practices'], 3)
        
        # 5. 查看文章详情
        article_detail = self.client.get(f'/api/v1/articles/{article_id}/').data
        self.assertEqual(article_detail['title'], '打字练习相关文章')
        
        print("✅ 文章打字练习集成测试通过")
    
    def test_concurrent_user_operations(self):
        """测试并发用户操作"""
        import threading
        import queue
        
        results = queue.Queue()
        
        def user_operation(user_id):
            """用户操作函数"""
            try:
                # 创建新用户
                user = User.objects.create_user(
                    username=f'concurrent_user_{user_id}',
                    email=f'concurrent{user_id}@test.com',
                    password='testpass123'
                )
                
                # 创建客户端并认证
                client = APIClient()
                client.force_authenticate(user=user)
                
                # 执行一系列操作
                for i in range(5):
                    # 获取单词
                    words_response = client.get('/api/v1/english/typing-practice/words/', {
                        'dictionary': self.dictionary.id,
                        'limit': 5
                    })
                    
                    if words_response.status_code != status.HTTP_200_OK:
                        results.put(f"User {user_id} failed to get words")
                        return
                    
                    # 提交练习
                    if words_response.data:
                        word = words_response.data[0]
                        submit_response = client.post('/api/v1/english/typing-practice/submit/', {
                            'word_id': word['id'],
                            'is_correct': True,
                            'typing_speed': 60,
                            'response_time': 2.0
                        }, format='json')
                        
                        if submit_response.status_code != status.HTTP_200_OK:
                            results.put(f"User {user_id} failed to submit practice")
                            return
                
                results.put(f"User {user_id} completed successfully")
                
            except Exception as e:
                results.put(f"User {user_id} failed with exception: {e}")
        
        # 启动5个并发用户
        threads = []
        for i in range(5):
            thread = threading.Thread(target=user_operation, args=(i,))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 检查结果
        failures = []
        while not results.empty():
            result = results.get()
            if "failed" in result:
                failures.append(result)
        
        self.assertEqual(len(failures), 0, f"并发用户操作失败: {failures}")
        
        print("✅ 并发用户操作测试通过")


@pytest.mark.django_db
class BoundaryConditionTest(TestCase):
    """边界条件测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='boundarytest',
            email='boundary@test.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.dictionary = Dictionary.objects.create(
            name='BoundaryTest',
            description='边界测试词库',
            category='TEST',
            language='en',
            total_words=10,
            chapter_count=1
        )
    
    def test_extreme_data_values(self):
        """测试极端数据值"""
        # 创建测试单词
        word = TypingWord.objects.create(
            word='extreme',
            translation='极端',
            phonetic='/ɪkˈstriːm/',
            difficulty='beginner',
            dictionary=self.dictionary,
            chapter=1,
            frequency=999999
        )
        
        # 测试极端打字速度
        extreme_speed_response = self.client.post('/api/v1/english/typing-practice/submit/', {
            'word_id': word.id,
            'is_correct': True,
            'typing_speed': 999.99,  # 极高速度
            'response_time': 0.001   # 极短时间
        }, format='json')
        
        self.assertEqual(extreme_speed_response.status_code, status.HTTP_200_OK)
        
        # 测试零值和负值
        zero_response = self.client.post('/api/v1/english/typing-practice/submit/', {
            'word_id': word.id,
            'is_correct': True,
            'typing_speed': 0,
            'response_time': 0
        }, format='json')
        
        self.assertEqual(zero_response.status_code, status.HTTP_200_OK)
        
        # 测试负值（应该被拒绝）
        negative_response = self.client.post('/api/v1/english/typing-practice/submit/', {
            'word_id': word.id,
            'is_correct': True,
            'typing_speed': -10,
            'response_time': -5
        }, format='json')
        
        self.assertNotEqual(negative_response.status_code, status.HTTP_200_OK)
        
        print("✅ 极端数据值测试通过")
    
    def test_large_data_handling(self):
        """测试大数据量处理"""
        # 创建大量单词
        words = []
        for i in range(1000):
            word = TypingWord.objects.create(
                word=f'large_word_{i}',
                translation=f'大数据单词_{i}',
                phonetic=f'/large{i}/',
                difficulty='beginner',
                dictionary=self.dictionary,
                chapter=1,
                frequency=i
            )
            words.append(word)
        
        # 测试大量数据查询
        large_query_response = self.client.get('/api/v1/english/typing-practice/words/', {
            'dictionary': self.dictionary.id,
            'limit': 1000
        })
        
        self.assertEqual(large_query_response.status_code, status.HTTP_200_OK)
        
        # 验证返回数据量
        returned_words = large_query_response.data
        self.assertLessEqual(len(returned_words), 1000)  # 应该有限制
        
        print("✅ 大数据量处理测试通过")
    
    def test_special_characters_handling(self):
        """测试特殊字符处理"""
        # 创建包含特殊字符的单词
        special_word = TypingWord.objects.create(
            word='café',  # 包含重音符号
            translation='咖啡厅',
            phonetic='/kæˈfeɪ/',
            difficulty='beginner',
            dictionary=self.dictionary,
            chapter=1,
            frequency=100
        )
        
        # 测试特殊字符查询
        query_response = self.client.get('/api/v1/english/typing-practice/words/', {
            'dictionary': self.dictionary.id,
            'limit': 10
        })
        
        self.assertEqual(query_response.status_code, status.HTTP_200_OK)
        
        # 查找包含特殊字符的单词
        found = False
        for word_data in query_response.data:
            if word_data['word'] == 'café':
                found = True
                break
        
        self.assertTrue(found, "包含特殊字符的单词应该能被正确处理")
        
        print("✅ 特殊字符处理测试通过")
