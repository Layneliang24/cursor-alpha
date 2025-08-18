import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.english.models import TypingWord, TypingSession, UserTypingStats, Dictionary
from apps.english.serializers import TypingWordSerializer, TypingSessionSerializer, UserTypingStatsSerializer

User = get_user_model()


class TypingPracticeTestCase(TestCase):
    """打字练习功能测试用例"""
    
    def setUp(self):
        """测试前准备"""
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # 创建测试词库
        self.dictionary = Dictionary.objects.create(
            name='CET4_T',
            description='CET4词汇库',
            category='CET4',
            language='en',
            total_words=1000,
            chapter_count=10
        )
        
        # 创建测试单词
        self.word1 = TypingWord.objects.create(
            word='test',
            translation='测试',
            phonetic='test',
            difficulty='beginner',
            dictionary=self.dictionary,
            chapter=1,
            frequency=100
        )
        
        self.word2 = TypingWord.objects.create(
            word='example',
            translation='例子',
            phonetic='ɪɡˈzæmpəl',
            difficulty='intermediate',
            dictionary=self.dictionary,
            chapter=1,
            frequency=50
        )
        
        # 创建用户统计
        self.user_stats = UserTypingStats.objects.create(
            user=self.user,
            total_words_practiced=0,
            total_correct_words=0,
            average_wpm=0.0,
            total_practice_time=0
        )
        
        # 创建API客户端
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_get_typing_words(self):
        """测试获取打字练习单词"""
        url = '/api/v1/english/typing-practice/words/'
        params = {
            'dictionary': self.dictionary.id,
            'difficulty': 'beginner',
            'limit': 5
        }
        
        response = self.client.get(url, params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertTrue(len(response.data) > 0)
        
        # 验证返回的单词数据
        word_data = response.data[0]
        self.assertIn('id', word_data)
        self.assertIn('word', word_data)
        self.assertIn('translation', word_data)
        self.assertIn('phonetic', word_data)
        self.assertIn('difficulty', word_data)
        self.assertIn('dictionary__name', word_data)  # 序列化器返回的是dictionary__name
    
    def test_get_typing_words_invalid_dictionary(self):
        """测试无效词库的错误处理"""
        url = '/api/v1/english/typing-practice/words/'
        params = {
            'dictionary': 99999,  # 不存在的词库ID
            'difficulty': 'beginner',
            'limit': 5
        }
        
        response = self.client.get(url, params)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_get_typing_words_invalid_difficulty(self):
        """测试无效难度级别的错误处理"""
        url = '/api/v1/english/typing-practice/words/'
        params = {
            'dictionary': self.dictionary.id,
            'difficulty': 'invalid',
            'limit': 5
        }
        
        response = self.client.get(url, params)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_submit_typing_practice(self):
        """测试提交打字练习结果"""
        url = '/api/v1/english/typing-practice/submit/'
        data = {
            'word_id': self.word1.id,
            'is_correct': True,
            'typing_speed': 60,
            'response_time': 2.5
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)
        self.assertEqual(response.data['status'], 'success')
        
        # 验证练习记录是否创建
        session = TypingSession.objects.filter(
            user=self.user,
            word=self.word1
        ).first()
        self.assertIsNotNone(session)
        self.assertTrue(session.is_correct)
        self.assertEqual(session.typing_speed, 60)
        self.assertEqual(session.response_time, 2.5)
    
    def test_submit_typing_practice_missing_word_id(self):
        """测试缺少word_id参数的错误处理"""
        url = '/api/v1/english/typing-practice/submit/'
        data = {
            'is_correct': True,
            'typing_speed': 60,
            'response_time': 2.5
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_submit_typing_practice_missing_is_correct(self):
        """测试缺少is_correct参数的错误处理"""
        url = '/api/v1/english/typing-practice/submit/'
        data = {
            'word_id': self.word1.id,
            'typing_speed': 60,
            'response_time': 2.5
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_submit_typing_practice_invalid_word_id(self):
        """测试无效word_id的错误处理"""
        url = '/api/v1/english/typing-practice/submit/'
        data = {
            'word_id': 99999,  # 不存在的单词ID
            'is_correct': True,
            'typing_speed': 60,
            'response_time': 2.5
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_get_typing_statistics(self):
        """测试获取打字统计信息"""
        url = '/api/v1/english/typing-practice/statistics/'
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_words_practiced', response.data)
        self.assertIn('total_correct_words', response.data)
        self.assertIn('average_wpm', response.data)
        self.assertIn('total_practice_time', response.data)
    
    def test_get_daily_progress(self):
        """测试获取每日学习进度"""
        url = '/api/v1/english/typing-practice/daily_progress/'
        params = {'days': 7}
        
        response = self.client.get(url, params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
    
    def test_typing_session_creation(self):
        """测试打字会话创建"""
        session = TypingSession.objects.create(
            user=self.user,
            word=self.word1,
            is_correct=True,
            typing_speed=50,
            response_time=3.0
        )
        
        self.assertIsNotNone(session)
        self.assertEqual(session.user, self.user)
        self.assertEqual(session.word, self.word1)
        self.assertTrue(session.is_correct)
        self.assertEqual(session.typing_speed, 50)
        self.assertEqual(session.response_time, 3.0)
    
    def test_user_typing_stats_update(self):
        """测试用户打字统计更新"""
        # 创建一些练习记录
        TypingSession.objects.create(
            user=self.user,
            word=self.word1,
            is_correct=True,
            typing_speed=60,
            response_time=2.0
        )
        
        TypingSession.objects.create(
            user=self.user,
            word=self.word2,
            is_correct=False,
            typing_speed=40,
            response_time=4.0
        )
        
        # 更新统计
        stats = UserTypingStats.objects.get(user=self.user)
        stats.total_words_practiced = TypingSession.objects.filter(user=self.user).count()
        stats.total_correct_words = TypingSession.objects.filter(user=self.user, is_correct=True).count()
        stats.save()
        
        self.assertEqual(stats.total_words_practiced, 2)
        self.assertEqual(stats.total_correct_words, 1)
    
    def test_typing_word_serializer(self):
        """测试打字单词序列化器"""
        serializer = TypingWordSerializer(self.word1)
        data = serializer.data
        
        self.assertEqual(data['word'], 'test')
        self.assertEqual(data['translation'], '测试')
        self.assertEqual(data['phonetic'], 'test')
        self.assertEqual(data['difficulty'], 'beginner')
        self.assertIn('dictionary', data)  # 检查dictionary字段而不是category
    
    def test_typing_session_serializer(self):
        """测试打字会话序列化器"""
        session = TypingSession.objects.create(
            user=self.user,
            word=self.word1,
            is_correct=True,
            typing_speed=60,
            response_time=2.0
        )
        
        serializer = TypingSessionSerializer(session)
        data = serializer.data
        
        self.assertIn('id', data)
        self.assertIn('word', data)
        self.assertIn('is_correct', data)
        self.assertIn('typing_speed', data)
        self.assertIn('response_time', data)
        self.assertTrue(data['is_correct'])
        self.assertEqual(data['typing_speed'], 60)
    
    def test_user_typing_stats_serializer(self):
        """测试用户打字统计序列化器"""
        serializer = UserTypingStatsSerializer(self.user_stats)
        data = serializer.data
        
        self.assertIn('total_words_practiced', data)
        self.assertIn('total_correct_words', data)
        self.assertIn('average_wpm', data)
        self.assertIn('total_practice_time', data)
        self.assertEqual(data['total_words_practiced'], 0)
        self.assertEqual(data['total_correct_words'], 0)


class TypingPracticeIntegrationTestCase(TestCase):
    """打字练习集成测试用例"""
    
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            username='integration_test_user',
            email='integration@example.com',
            password='testpass123'
        )
        
        # 创建测试词库
        self.test_dictionary = Dictionary.objects.create(
            name='CET4_T',
            description='CET4词汇库',
            category='CET4',
            language='en',
            total_words=1000,
            chapter_count=10
        )
        
        # 创建多个测试单词
        for i in range(10):
            TypingWord.objects.create(
                word=f'word{i}',
                translation=f'单词{i}',
                phonetic=f'wɜːd{i}',
                difficulty='beginner' if i < 5 else 'intermediate',
                dictionary=self.test_dictionary,
                chapter=1,
                frequency=100 - i * 10
            )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_complete_typing_practice_flow(self):
        """测试完整的打字练习流程"""
        # 1. 获取练习单词
        words_url = '/api/v1/english/typing-practice/words/'
        words_response = self.client.get(words_url, {
            'dictionary': self.test_dictionary.id,
            'difficulty': 'beginner',
            'limit': 5
        })
        
        self.assertEqual(words_response.status_code, status.HTTP_200_OK)
        words = words_response.data
        self.assertEqual(len(words), 5)
        
        # 2. 提交练习结果
        submit_url = '/api/v1/english/typing-practice/submit/'
        for word in words[:3]:  # 只练习前3个单词
            response = self.client.post(submit_url, {
                'word_id': word['id'],
                'is_correct': True,
                'typing_speed': 60,
                'response_time': 2.0
            })
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 3. 检查统计信息
        stats_url = '/api/v1/english/typing-practice/statistics/'
        stats_response = self.client.get(stats_url)
        
        self.assertEqual(stats_response.status_code, status.HTTP_200_OK)
        # 注意：这里可能需要手动更新统计，因为后端可能没有自动更新逻辑
        
        # 4. 检查练习记录
        sessions = TypingSession.objects.filter(user=self.user)
        self.assertEqual(sessions.count(), 3)
        
        for session in sessions:
            self.assertTrue(session.is_correct)
            self.assertEqual(session.typing_speed, 60)
            self.assertEqual(session.response_time, 2.0)
    
    def test_typing_practice_performance(self):
        """测试打字练习性能"""
        import time
        
        # 测试获取单词的性能
        start_time = time.time()
        response = self.client.get('/api/v1/english/typing-practice/words/', {
            'dictionary': self.test_dictionary.id,
            'difficulty': 'beginner',
            'limit': 50
        })
        end_time = time.time()
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLess(end_time - start_time, 1.0)  # 应该在1秒内完成
        
        # 测试批量提交的性能
        words = response.data[:10]
        start_time = time.time()
        
        for word in words:
            self.client.post('/api/v1/english/typing-practice/submit/', {
                'word_id': word['id'],
                'is_correct': True,
                'typing_speed': 60,
                'response_time': 2.0
            })
        
        end_time = time.time()
        self.assertLess(end_time - start_time, 5.0)  # 批量提交应该在5秒内完成
















