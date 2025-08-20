#!/usr/bin/env python
"""
打字练习Submit API测试用例

测试范围：
1. 单元测试：submit API的基本功能
2. 集成测试：submit API与数据库的交互
3. 认证测试：用户认证相关的测试
4. 边界测试：各种边界条件的测试
"""

import pytest
import json
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from apps.english.models import (
    TypingWord, Dictionary, TypingSession, 
    TypingPracticeRecord, UserTypingStats
)

User = get_user_model()


class TypingPracticeSubmitAPITest(APITestCase):
    """打字练习Submit API测试"""
    
    def setUp(self):
        """测试数据准备"""
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # 创建测试词库
        self.dictionary = Dictionary.objects.create(
            name='测试词库',
            category='测试',
            description='用于测试的词库',
            language='en',
            total_words=10,
            chapter_count=1
        )
        
        # 创建测试单词
        self.word = TypingWord.objects.create(
            word='test',
            translation='测试',
            phonetic='/test/',
            difficulty='easy',
            dictionary=self.dictionary,
            chapter=1,
            frequency=100
        )
        
        # 生成JWT token
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)
        
        # 设置API客户端
        self.client = APIClient()
        self.submit_url = '/api/v1/english/typing-practice/submit/'
    
    def test_submit_success(self):
        """测试成功提交练习数据"""
        # 设置认证
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        # 准备测试数据
        data = {
            'word_id': self.word.id,
            'is_correct': True,
            'typing_speed': 60,
            'response_time': 2.5
        }
        
        # 发送请求
        response = self.client.post(self.submit_url, data, format='json')
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertIn('session_id', response.data)
        
        # 验证数据库记录
        # 检查TypingSession记录
        session = TypingSession.objects.get(id=response.data['session_id'])
        self.assertEqual(session.user, self.user)
        self.assertEqual(session.word, self.word)
        self.assertEqual(session.is_correct, True)
        self.assertEqual(session.typing_speed, 60)
        self.assertEqual(session.response_time, 2.5)
        
        # 检查TypingPracticeRecord记录
        practice_record = TypingPracticeRecord.objects.filter(
            user=self.user, 
            word=self.word.word
        ).first()
        self.assertIsNotNone(practice_record)
        self.assertEqual(practice_record.is_correct, True)
        self.assertEqual(practice_record.typing_speed, 60)
        self.assertEqual(practice_record.response_time, 2.5)
    
    def test_submit_without_authentication(self):
        """测试未认证用户提交数据"""
        data = {
            'word_id': self.word.id,
            'is_correct': True,
            'typing_speed': 60,
            'response_time': 2.5
        }
        
        response = self.client.post(self.submit_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_submit_missing_word_id(self):
        """测试缺少word_id参数"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        data = {
            'is_correct': True,
            'typing_speed': 60,
            'response_time': 2.5
        }
        
        response = self.client.post(self.submit_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('缺少word_id参数', response.data['error'])
    
    def test_submit_missing_is_correct(self):
        """测试缺少is_correct参数"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        data = {
            'word_id': self.word.id,
            'typing_speed': 60,
            'response_time': 2.5
        }
        
        response = self.client.post(self.submit_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('缺少is_correct参数', response.data['error'])
    
    def test_submit_invalid_word_id(self):
        """测试无效的word_id"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        data = {
            'word_id': 99999,  # 不存在的单词ID
            'is_correct': True,
            'typing_speed': 60,
            'response_time': 2.5
        }
        
        response = self.client.post(self.submit_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('单词不存在', response.data['error'])
    
    def test_submit_with_default_values(self):
        """测试使用默认值的提交"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        data = {
            'word_id': self.word.id,
            'is_correct': False
            # typing_speed和response_time使用默认值
        }
        
        response = self.client.post(self.submit_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证默认值
        session = TypingSession.objects.get(id=response.data['session_id'])
        self.assertEqual(session.typing_speed, 0)
        self.assertEqual(session.response_time, 0)
    
    def test_submit_multiple_records(self):
        """测试提交多条记录"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        # 提交第一条记录
        data1 = {
            'word_id': self.word.id,
            'is_correct': True,
            'typing_speed': 60,
            'response_time': 2.5
        }
        response1 = self.client.post(self.submit_url, data1, format='json')
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        
        # 提交第二条记录
        data2 = {
            'word_id': self.word.id,
            'is_correct': False,
            'typing_speed': 45,
            'response_time': 3.0
        }
        response2 = self.client.post(self.submit_url, data2, format='json')
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        
        # 验证两条记录都存在
        sessions = TypingSession.objects.filter(user=self.user)
        self.assertEqual(sessions.count(), 2)
        
        practice_records = TypingPracticeRecord.objects.filter(user=self.user)
        self.assertEqual(practice_records.count(), 2)
    
    def test_user_stats_update(self):
        """测试用户统计更新"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        # 提交练习数据
        data = {
            'word_id': self.word.id,
            'is_correct': True,
            'typing_speed': 60,
            'response_time': 2.5
        }
        
        response = self.client.post(self.submit_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证用户统计是否创建/更新
        stats = UserTypingStats.objects.filter(user=self.user).first()
        self.assertIsNotNone(stats)
    
    def test_submit_with_extreme_values(self):
        """测试极值情况"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        # 测试极大值
        data = {
            'word_id': self.word.id,
            'is_correct': True,
            'typing_speed': 999999,
            'response_time': 999999.99
        }
        
        response = self.client.post(self.submit_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 测试极小值
        data = {
            'word_id': self.word.id,
            'is_correct': False,
            'typing_speed': 0,
            'response_time': 0.01
        }
        
        response = self.client.post(self.submit_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TypingPracticeSubmitRegressionTest(APITestCase):
    """Submit API回归测试"""
    
    def setUp(self):
        """测试数据准备"""
        self.user = User.objects.create_user(
            username='regressionuser',
            email='regression@example.com',
            password='testpass123'
        )
        
        self.dictionary = Dictionary.objects.create(
            name='回归测试词库',
            category='回归测试',
            description='回归测试专用词库',
            language='en',
            total_words=5,
            chapter_count=1
        )
        
        # 创建多个测试单词
        self.words = []
        for i in range(5):
            word = TypingWord.objects.create(
                word=f'word{i}',
                translation=f'单词{i}',
                phonetic=f'/word{i}/',
                difficulty='easy',
                dictionary=self.dictionary,
                chapter=1,
                frequency=100 - i * 10
            )
            self.words.append(word)
        
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)
        self.client = APIClient()
        self.submit_url = '/api/v1/english/typing-practice/submit/'
    
    def test_submit_api_field_consistency(self):
        """回归测试：确保API字段一致性"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        # 确保API接受word_id而不是word字段
        correct_data = {
            'word_id': self.words[0].id,
            'is_correct': True,
            'typing_speed': 60,
            'response_time': 2.5
        }
        
        response = self.client.post(self.submit_url, correct_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 确保使用错误的字段名会失败
        wrong_data = {
            'word': self.words[0].word,  # 错误的字段名
            'is_correct': True,
            'typing_speed': 60,
            'response_time': 2.5
        }
        
        response = self.client.post(self.submit_url, wrong_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_dual_table_saving(self):
        """回归测试：确保数据同时保存到两个表"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        data = {
            'word_id': self.words[0].id,
            'is_correct': True,
            'typing_speed': 60,
            'response_time': 2.5
        }
        
        response = self.client.post(self.submit_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 确保TypingSession记录存在
        session_exists = TypingSession.objects.filter(
            user=self.user,
            word=self.words[0]
        ).exists()
        self.assertTrue(session_exists)
        
        # 确保TypingPracticeRecord记录存在
        practice_exists = TypingPracticeRecord.objects.filter(
            user=self.user,
            word=self.words[0].word
        ).exists()
        self.assertTrue(practice_exists)
    
    def test_batch_submission_performance(self):
        """回归测试：批量提交性能测试"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        # 批量提交多个单词
        for i, word in enumerate(self.words):
            data = {
                'word_id': word.id,
                'is_correct': i % 2 == 0,  # 交替正确/错误
                'typing_speed': 50 + i * 10,
                'response_time': 2.0 + i * 0.5
            }
            
            response = self.client.post(self.submit_url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证所有记录都已保存
        session_count = TypingSession.objects.filter(user=self.user).count()
        practice_count = TypingPracticeRecord.objects.filter(user=self.user).count()
        
        self.assertEqual(session_count, len(self.words))
        self.assertEqual(practice_count, len(self.words))


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
