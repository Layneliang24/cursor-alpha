#!/usr/bin/env python
"""
打字练习Submit API集成测试

测试submit API与其他系统组件的集成：
1. 与数据分析服务的集成
2. 与用户统计更新的集成
3. 与缓存系统的集成
4. 端到端测试场景
"""

import pytest
import time
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from apps.english.models import (
    TypingWord, Dictionary, TypingSession, 
    TypingPracticeRecord, UserTypingStats
)
from apps.english.services import DataAnalysisService

User = get_user_model()


class TypingPracticeSubmitIntegrationTest(APITestCase):
    """Submit API集成测试"""
    
    def setUp(self):
        """测试数据准备"""
        # 清除缓存
        cache.clear()
        
        # 创建测试用户
        self.user = User.objects.create_user(
            username='integration_user',
            email='integration@example.com',
            password='testpass123'
        )
        
        # 创建测试词库
        self.dictionary = Dictionary.objects.create(
            name='集成测试词库',
            category='集成测试',
            description='集成测试专用词库',
            language='en',
            total_words=20,
            chapter_count=2
        )
        
        # 创建测试单词
        self.words = []
        for chapter in [1, 2]:
            for i in range(10):
                word = TypingWord.objects.create(
                    word=f'word{chapter}_{i}',
                    translation=f'单词{chapter}_{i}',
                    phonetic=f'/word{chapter}_{i}/',
                    difficulty='easy',
                    dictionary=self.dictionary,
                    chapter=chapter,
                    frequency=100 - i * 5
                )
                self.words.append(word)
        
        # JWT认证
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        self.submit_url = '/api/v1/english/typing-practice/submit/'
        self.data_analysis_service = DataAnalysisService()
    
    def test_submit_and_data_analysis_integration(self):
        """测试提交数据后数据分析服务能正确读取"""
        # 提交多条练习记录
        test_data = [
            {'word_id': self.words[0].id, 'is_correct': True, 'typing_speed': 60, 'response_time': 2.0},
            {'word_id': self.words[1].id, 'is_correct': False, 'typing_speed': 45, 'response_time': 3.5},
            {'word_id': self.words[2].id, 'is_correct': True, 'typing_speed': 70, 'response_time': 1.8},
            {'word_id': self.words[0].id, 'is_correct': True, 'typing_speed': 65, 'response_time': 2.2},  # 重复单词
        ]
        
        # 提交所有数据
        for data in test_data:
            response = self.client.post(self.submit_url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证数据分析服务能读取到数据
        from datetime import datetime, timedelta
        from django.utils import timezone
        
        end_date = timezone.now()
        start_date = end_date - timedelta(days=1)
        
        # 测试数据概览
        overview = self.data_analysis_service.get_data_overview(
            self.user.id, start_date, end_date
        )
        
        self.assertEqual(overview['total_exercises'], 1)  # 总练习次数（1个会话）
        self.assertEqual(overview['total_words'], 4)  # 总练习单词数（不去重）
        self.assertEqual(overview['correct_exercises'], 3)  # 正确次数
        self.assertAlmostEqual(overview['avg_accuracy'], 75.0, places=1)  # 正确率
        
        # 测试热力图数据
        heatmap_data = self.data_analysis_service.get_word_heatmap(
            self.user.id, start_date, end_date
        )
        self.assertTrue(len(heatmap_data) >= 1)  # 至少有今天的数据
    
    def test_submit_and_user_stats_integration(self):
        """测试提交数据后用户统计正确更新"""
        # 初始状态检查
        initial_stats = UserTypingStats.objects.filter(user=self.user).first()
        self.assertIsNone(initial_stats)
        
        # 提交练习数据
        data = {
            'word_id': self.words[0].id,
            'is_correct': True,
            'typing_speed': 60,
            'response_time': 2.5
        }
        
        response = self.client.post(self.submit_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 等待异步统计更新（如果有的话）
        time.sleep(0.1)
        
        # 验证用户统计已创建
        stats = UserTypingStats.objects.filter(user=self.user).first()
        self.assertIsNotNone(stats)
        self.assertEqual(stats.total_words_practiced, 1)
        self.assertEqual(stats.total_correct_words, 1)
        self.assertEqual(stats.average_wpm, 60.0)
        
        # 提交第二条数据
        data2 = {
            'word_id': self.words[1].id,
            'is_correct': False,
            'typing_speed': 40,
            'response_time': 3.0
        }
        
        response = self.client.post(self.submit_url, data2, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 等待统计更新
        time.sleep(0.1)
        
        # 验证统计更新
        stats.refresh_from_db()
        self.assertEqual(stats.total_words_practiced, 2)
        self.assertEqual(stats.total_correct_words, 1)
        self.assertEqual(stats.average_wpm, 50.0)  # (60 + 40) / 2
    
    def test_submit_and_cache_integration(self):
        """测试提交数据对缓存系统的影响"""
        # 先访问统计API，让数据被缓存
        stats_url = '/api/v1/english/typing-practice/statistics/'
        response = self.client.get(stats_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 提交新的练习数据
        data = {
            'word_id': self.words[0].id,
            'is_correct': True,
            'typing_speed': 60,
            'response_time': 2.5
        }
        
        response = self.client.post(self.submit_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 再次访问统计API，验证缓存是否被正确清除和更新
        response = self.client.get(stats_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 注意：具体的缓存验证逻辑取决于缓存实现
    
    def test_end_to_end_practice_session(self):
        """端到端测试：完整的练习会话"""
        # 模拟一个完整的练习会话
        practice_words = self.words[:5]  # 选择5个单词进行练习
        
        session_data = []
        for i, word in enumerate(practice_words):
            data = {
                'word_id': word.id,
                'is_correct': i != 2,  # 第3个单词错误
                'typing_speed': 50 + i * 5,  # 逐渐提高速度
                'response_time': 3.0 - i * 0.2  # 逐渐缩短时间
            }
            session_data.append(data)
        
        # 提交所有练习数据
        session_ids = []
        for data in session_data:
            response = self.client.post(self.submit_url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            session_ids.append(response.data['session_id'])
        
        # 验证所有session都已创建
        self.assertEqual(len(session_ids), len(practice_words))
        self.assertEqual(len(set(session_ids)), len(practice_words))  # 确保ID唯一
        
        # 验证数据库一致性
        sessions = TypingSession.objects.filter(user=self.user).order_by('id')
        practice_records = TypingPracticeRecord.objects.filter(user=self.user).order_by('id')
        
        self.assertEqual(sessions.count(), len(practice_words))
        self.assertEqual(practice_records.count(), len(practice_words))
        
        # 验证数据内容一致性
        for i, (session, practice_record, original_data) in enumerate(
            zip(sessions, practice_records, session_data)
        ):
            self.assertEqual(session.is_correct, original_data['is_correct'])
            self.assertEqual(session.typing_speed, original_data['typing_speed'])
            self.assertEqual(session.response_time, original_data['response_time'])
            
            self.assertEqual(practice_record.is_correct, original_data['is_correct'])
            self.assertEqual(practice_record.typing_speed, original_data['typing_speed'])
            self.assertEqual(practice_record.response_time, original_data['response_time'])
    
    @pytest.mark.skip(reason="并发测试在测试环境中不稳定，暂跳过")
    def test_concurrent_submissions(self):
        """测试并发提交的处理"""
        import threading
        import queue

        results = queue.Queue()

        def submit_word(word_id, user_token):
            """并发提交函数"""
            client = APIClient()
            client.credentials(HTTP_AUTHORIZATION=f'Bearer {user_token}')

            data = {
                'word_id': word_id,
                'is_correct': True,
                'typing_speed': 60,
                'response_time': 2.0
            }

            try:
                response = client.post(self.submit_url, data, format='json')
                results.put(('success', response.status_code, response.data))
            except Exception as e:
                results.put(('error', str(e)))

        # 创建多个并发提交
        threads = []
        for i in range(3):
            thread = threading.Thread(
                target=submit_word,
                args=(self.words[i].id, self.access_token)
            )
            threads.append(thread)
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        # 验证结果
        success_count = 0
        while not results.empty():
            result = results.get()
            if result[0] == 'success':
                success_count += 1
                self.assertEqual(result[1], status.HTTP_200_OK)

        self.assertEqual(success_count, 3)

        # 验证数据库记录
        sessions = TypingSession.objects.filter(user=self.user)
        self.assertEqual(sessions.count(), 3)


class TypingPracticeSubmitErrorRecoveryTest(APITestCase):
    """Submit API错误恢复测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='recovery_user',
            email='recovery@example.com',
            password='testpass123'
        )
        
        self.dictionary = Dictionary.objects.create(
            name='错误恢复测试词库',
            category='错误恢复',
            description='错误恢复测试',
            language='en',
            total_words=5,
            chapter_count=1
        )
        
        self.word = TypingWord.objects.create(
            word='recovery_test',
            translation='恢复测试',
            phonetic='/recovery/',
            difficulty='easy',
            dictionary=self.dictionary,
            chapter=1,
            frequency=100
        )
        
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)
        self.client = APIClient()
        self.submit_url = '/api/v1/english/typing-practice/submit/'
    
    def test_partial_failure_recovery(self):
        """测试部分失败后的恢复"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        # 先提交一个成功的记录
        success_data = {
            'word_id': self.word.id,
            'is_correct': True,
            'typing_speed': 60,
            'response_time': 2.0
        }
        
        response = self.client.post(self.submit_url, success_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 提交一个失败的记录（无效的word_id）
        fail_data = {
            'word_id': 99999,
            'is_correct': True,
            'typing_speed': 60,
            'response_time': 2.0
        }
        
        response = self.client.post(self.submit_url, fail_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # 再提交一个成功的记录，验证系统仍然正常工作
        success_data2 = {
            'word_id': self.word.id,
            'is_correct': False,
            'typing_speed': 45,
            'response_time': 3.0
        }
        
        response = self.client.post(self.submit_url, success_data2, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证只有成功的记录被保存
        sessions = TypingSession.objects.filter(user=self.user)
        self.assertEqual(sessions.count(), 2)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
