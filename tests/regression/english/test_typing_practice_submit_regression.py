#!/usr/bin/env python
"""
打字练习Submit API回归测试

确保submit API的关键功能在代码变更后仍然正常工作：
1. 防止字段名回归（word vs word_id）
2. 防止双表保存回归
3. 防止认证问题回归
4. 防止数据一致性问题回归
"""

import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from apps.english.models import (
    TypingWord, Dictionary, TypingSession, 
    TypingPracticeRecord, UserTypingStats
)

User = get_user_model()


class SubmitAPIRegressionTest(APITestCase):
    """Submit API关键回归测试"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        print("\n" + "="*60)
        print("开始Submit API回归测试")
        print("="*60)
    
    def setUp(self):
        """测试数据准备"""
        # 创建测试用户
        self.user = User.objects.create_user(
            username='regression_test_user',
            email='regression@test.com',
            password='testpass123'
        )
        
        # 创建测试词库
        self.dictionary = Dictionary.objects.create(
            name='回归测试词库',
            category='REGRESSION_TEST',
            description='回归测试专用词库',
            language='en',
            total_words=10,
            chapter_count=1
        )
        
        # 创建测试单词
        self.word = TypingWord.objects.create(
            word='regression',
            translation='回归',
            phonetic='/rɪˈɡreʃən/',
            difficulty='intermediate',
            dictionary=self.dictionary,
            chapter=1,
            frequency=100
        )
        
        # JWT认证
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)
        self.client = APIClient()
        self.submit_url = '/api/v1/english/typing-practice/submit/'
    
    def test_regression_field_name_word_id(self):
        """回归测试：确保API使用word_id而不是word字段"""
        print("\n测试字段名回归：word_id vs word")
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        # 正确的字段名应该工作
        correct_data = {
            'word_id': self.word.id,
            'is_correct': True,
            'typing_speed': 60,
            'response_time': 2.5
        }
        
        response = self.client.post(self.submit_url, correct_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        print("✓ word_id字段正常工作")
        
        # 错误的字段名应该失败
        wrong_data = {
            'word': self.word.word,  # 错误：应该是word_id
            'is_correct': True,
            'typing_speed': 60,
            'response_time': 2.5
        }
        
        response = self.client.post(self.submit_url, wrong_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('缺少word_id参数', response.data['error'])
        print("✓ word字段正确拒绝")
        
        # 同时使用两个字段的情况
        mixed_data = {
            'word_id': self.word.id,
            'word': self.word.word,  # 多余的字段
            'is_correct': True,
            'typing_speed': 60,
            'response_time': 2.5
        }
        
        response = self.client.post(self.submit_url, mixed_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # 应该忽略多余字段
        print("✓ 混合字段情况正常处理")
    
    def test_regression_dual_table_saving(self):
        """回归测试：确保数据同时保存到两个表"""
        print("\n测试双表保存回归")
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        # 清除可能存在的旧数据
        TypingSession.objects.filter(user=self.user).delete()
        TypingPracticeRecord.objects.filter(user=self.user).delete()
        
        data = {
            'word_id': self.word.id,
            'is_correct': True,
            'typing_speed': 75,
            'response_time': 1.8
        }
        
        response = self.client.post(self.submit_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证TypingSession表
        session = TypingSession.objects.filter(user=self.user).first()
        self.assertIsNotNone(session, "TypingSession记录未创建")
        self.assertEqual(session.word.id, self.word.id)
        self.assertEqual(session.is_correct, True)
        self.assertEqual(session.typing_speed, 75)
        self.assertEqual(session.response_time, 1.8)
        print("✓ TypingSession表数据正确")
        
        # 验证TypingPracticeRecord表
        practice_record = TypingPracticeRecord.objects.filter(user=self.user).first()
        self.assertIsNotNone(practice_record, "TypingPracticeRecord记录未创建")
        self.assertEqual(practice_record.word, self.word.word)  # 注意：这里保存的是字符串
        self.assertEqual(practice_record.is_correct, True)
        self.assertEqual(practice_record.typing_speed, 75)
        self.assertEqual(practice_record.response_time, 1.8)
        print("✓ TypingPracticeRecord表数据正确")
        
        # 验证数据一致性
        self.assertEqual(session.is_correct, practice_record.is_correct)
        self.assertEqual(session.typing_speed, practice_record.typing_speed)
        self.assertEqual(session.response_time, practice_record.response_time)
        print("✓ 两表数据一致")
    
    def test_regression_authentication_requirements(self):
        """回归测试：确保认证要求正确"""
        print("\n测试认证要求回归")
        
        data = {
            'word_id': self.word.id,
            'is_correct': True,
            'typing_speed': 60,
            'response_time': 2.5
        }
        
        # 未认证请求应该失败
        response = self.client.post(self.submit_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        print("✓ 未认证请求正确拒绝")
        
        # 无效token应该失败
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid_token')
        response = self.client.post(self.submit_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        print("✓ 无效token正确拒绝")
        
        # 有效token应该成功
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.post(self.submit_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("✓ 有效token正常工作")
    
    def test_regression_required_fields(self):
        """回归测试：确保必填字段验证正确"""
        print("\n测试必填字段回归")
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        # 缺少word_id
        data_no_word_id = {
            'is_correct': True,
            'typing_speed': 60,
            'response_time': 2.5
        }
        response = self.client.post(self.submit_url, data_no_word_id, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('缺少word_id参数', response.data['error'])
        print("✓ 缺少word_id正确拒绝")
        
        # 缺少is_correct
        data_no_is_correct = {
            'word_id': self.word.id,
            'typing_speed': 60,
            'response_time': 2.5
        }
        response = self.client.post(self.submit_url, data_no_is_correct, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('缺少is_correct参数', response.data['error'])
        print("✓ 缺少is_correct正确拒绝")
        
        # typing_speed和response_time应该有默认值
        data_minimal = {
            'word_id': self.word.id,
            'is_correct': True
        }
        response = self.client.post(self.submit_url, data_minimal, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("✓ 可选字段默认值正常工作")
    
    def test_regression_data_types(self):
        """回归测试：确保数据类型验证正确"""
        print("\n测试数据类型回归")
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        # 测试各种数据类型
        test_cases = [
            {
                'name': '字符串word_id',
                'data': {'word_id': str(self.word.id), 'is_correct': True},
                'should_succeed': True
            },
            {
                'name': '字符串is_correct',
                'data': {'word_id': self.word.id, 'is_correct': 'true'},
                'should_succeed': True  # Django REST framework会转换
            },
            {
                'name': '字符串typing_speed',
                'data': {'word_id': self.word.id, 'is_correct': True, 'typing_speed': '60'},
                'should_succeed': True
            },
            {
                'name': '负数typing_speed',
                'data': {'word_id': self.word.id, 'is_correct': True, 'typing_speed': -10},
                'should_succeed': True  # API应该接受，业务逻辑可能处理
            }
        ]
        
        for case in test_cases:
            response = self.client.post(self.submit_url, case['data'], format='json')
            if case['should_succeed']:
                self.assertEqual(response.status_code, status.HTTP_200_OK, 
                               f"{case['name']} 应该成功但失败了")
                print(f"✓ {case['name']} 正常处理")
            else:
                self.assertNotEqual(response.status_code, status.HTTP_200_OK,
                                   f"{case['name']} 应该失败但成功了")
                print(f"✓ {case['name']} 正确拒绝")
    
    def test_regression_response_format(self):
        """回归测试：确保响应格式一致"""
        print("\n测试响应格式回归")
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        data = {
            'word_id': self.word.id,
            'is_correct': True,
            'typing_speed': 60,
            'response_time': 2.5
        }
        
        response = self.client.post(self.submit_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证响应格式
        self.assertIn('status', response.data)
        self.assertIn('session_id', response.data)
        self.assertEqual(response.data['status'], 'success')
        self.assertIsInstance(response.data['session_id'], int)
        print("✓ 成功响应格式正确")
        
        # 测试错误响应格式
        error_data = {'word_id': 99999, 'is_correct': True}
        response = self.client.post(self.submit_url, error_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
        print("✓ 错误响应格式正确")
    
    def test_regression_multiple_submissions_same_word(self):
        """回归测试：确保同一单词多次提交正常工作"""
        print("\n测试同一单词多次提交回归")
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        # 提交同一单词3次
        submissions = [
            {'is_correct': True, 'typing_speed': 50, 'response_time': 3.0},
            {'is_correct': False, 'typing_speed': 45, 'response_time': 3.5},
            {'is_correct': True, 'typing_speed': 60, 'response_time': 2.5},
        ]
        
        session_ids = []
        for i, submission in enumerate(submissions):
            data = {
                'word_id': self.word.id,
                **submission
            }
            
            response = self.client.post(self.submit_url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            session_ids.append(response.data['session_id'])
            print(f"✓ 第{i+1}次提交成功，session_id: {response.data['session_id']}")
        
        # 验证所有session_id都不同
        self.assertEqual(len(set(session_ids)), len(session_ids), "session_id应该唯一")
        print("✓ 所有session_id唯一")
        
        # 验证数据库记录
        sessions = TypingSession.objects.filter(user=self.user, word=self.word)
        practice_records = TypingPracticeRecord.objects.filter(user=self.user, word=self.word.word)
        
        self.assertEqual(sessions.count(), len(submissions))
        self.assertEqual(practice_records.count(), len(submissions))
        print(f"✓ 数据库记录正确：{sessions.count()}条TypingSession，{practice_records.count()}条TypingPracticeRecord")
    
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        print("\n" + "="*60)
        print("Submit API回归测试完成")
        print("="*60)


class SubmitAPIRegressionPerformanceTest(APITestCase):
    """Submit API性能回归测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='perf_user',
            email='perf@test.com',
            password='testpass123'
        )
        
        self.dictionary = Dictionary.objects.create(
            name='性能测试词库',
            category='PERFORMANCE_TEST',
            description='性能测试专用',
            language='en',
            total_words=100,
            chapter_count=1
        )
        
        # 创建100个测试单词
        self.words = []
        for i in range(100):
            word = TypingWord.objects.create(
                word=f'perf_word_{i:03d}',
                translation=f'性能单词{i}',
                phonetic=f'/perf{i}/',
                difficulty='easy',
                dictionary=self.dictionary,
                chapter=1,
                frequency=100 - i
            )
            self.words.append(word)
        
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        self.submit_url = '/api/v1/english/typing-practice/submit/'
    
    def test_regression_bulk_submission_performance(self):
        """回归测试：批量提交性能"""
        print("\n测试批量提交性能回归")
        
        import time
        
        start_time = time.time()
        
        # 提交50个单词
        for i in range(50):
            data = {
                'word_id': self.words[i].id,
                'is_correct': i % 3 != 0,  # 2/3正确率
                'typing_speed': 50 + i,
                'response_time': 2.0 + i * 0.01
            }
            
            response = self.client.post(self.submit_url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"✓ 50次提交总耗时: {total_time:.2f}秒")
        print(f"✓ 平均每次提交: {total_time/50:.3f}秒")
        
        # 性能断言（根据实际情况调整）
        self.assertLess(total_time, 30.0, "批量提交性能回归：耗时超过30秒")
        self.assertLess(total_time/50, 1.0, "单次提交性能回归：平均耗时超过1秒")
        
        # 验证数据完整性
        sessions = TypingSession.objects.filter(user=self.user)
        practice_records = TypingPracticeRecord.objects.filter(user=self.user)
        
        self.assertEqual(sessions.count(), 50)
        self.assertEqual(practice_records.count(), 50)
        print("✓ 数据完整性验证通过")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
