# -*- coding: utf-8 -*-
"""
数据分析功能测试
测试英语学习模块的数据分析相关功能
"""

import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from datetime import datetime, timedelta
import json

from tests.utils.test_helpers import TestDataFactory, TestUserManager
from apps.english.models import TypingPracticeRecord, DailyPracticeStats, KeyErrorStats

User = get_user_model()


class TestDataAnalysisAPI(TestCase):
    """数据分析API测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.user = TestUserManager.create_test_user()
        self.client.force_authenticate(user=self.user)
        
        # 创建测试数据
        self._create_test_practice_data()
    
    def _create_test_practice_data(self):
        """创建测试练习数据"""
        # 创建练习记录
        for i in range(10):
            TypingPracticeRecord.objects.create(
                user=self.user,
                word=f"test_word_{i}",
                is_correct=True,
                typing_speed=50.0 + i,
                response_time=1.0,
                total_time=1000 + i * 100,
                wrong_count=0,
                mistakes={},
                timing=[100, 200, 300],
                session_date=datetime.now().date() - timedelta(days=i)
            )
        
        # 创建每日统计
        DailyPracticeStats.objects.create(
            user=self.user,
            date=datetime.now().date(),
            exercise_count=10,
            word_count=10,
            avg_wpm=55.0,
            accuracy_rate=95.0
        )
        
        # 创建按键错误统计
        KeyErrorStats.objects.create(
            user=self.user,
            key='a',
            error_count=5,
            last_error_date=datetime.now().date()
        )
    
    def test_exercise_heatmap_api(self):
        """测试练习次数热力图API"""
        response = self.client.get('/api/v1/english/data-analysis/exercise_heatmap/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
        
        # 验证数据结构
        data = response.data['data']
        self.assertIsInstance(data, list)
        if data:
            self.assertIn('date', data[0])
            self.assertIn('count', data[0])
            self.assertIn('level', data[0])
    
    def test_word_heatmap_api(self):
        """测试练习单词数热力图API"""
        response = self.client.get('/api/v1/english/data-analysis/word_heatmap/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
    
    def test_wpm_trend_api(self):
        """测试WPM趋势图API"""
        response = self.client.get('/api/v1/english/data-analysis/wpm_trend/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
    
    def test_accuracy_trend_api(self):
        """测试正确率趋势图API"""
        response = self.client.get('/api/v1/english/data-analysis/accuracy_trend/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
    
    def test_key_error_stats_api(self):
        """测试按键错误统计API"""
        response = self.client.get('/api/v1/english/data-analysis/key_error_stats/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
    
    def test_data_overview_api(self):
        """测试数据概览API"""
        response = self.client.get('/api/v1/english/data-analysis/overview/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
        
        # 验证概览数据
        overview = response.data['data']
        self.assertIn('total_exercises', overview)
        self.assertIn('total_words', overview)
        self.assertIn('avg_wpm', overview)
        self.assertIn('avg_accuracy', overview)
    
    def test_date_range_filtering(self):
        """测试日期范围过滤"""
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        response = self.client.get(f'/api/v1/english/data-analysis/exercise_heatmap/?start_date={start_date}&end_date={end_date}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
    
    def test_unauthorized_access(self):
        """测试未授权访问"""
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/v1/english/data-analysis/exercise_heatmap/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestDataAnalysisService(TestCase):
    """数据分析服务测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.user = TestUserManager.create_test_user()
        self._create_test_data()
    
    def _create_test_data(self):
        """创建测试数据"""
        # 创建多天的练习数据
        for i in range(30):
            date = datetime.now().date() - timedelta(days=i)
            TypingPracticeRecord.objects.create(
                user=self.user,
                word=f"word_{i}",
                is_correct=i % 3 != 0,  # 部分错误
                typing_speed=40.0 + (i % 20),
                response_time=1.0 + (i % 5) * 0.1,
                total_time=1000 + i * 50,
                wrong_count=i % 3,
                mistakes={'a': 1} if i % 3 == 0 else {},
                timing=[100, 200, 300],
                session_date=date
            )
    
    def test_exercise_heatmap_data_generation(self):
        """测试练习次数热力图数据生成"""
        from apps.english.services import DataAnalysisService
        
        service = DataAnalysisService()
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()
        
        data = service.get_exercise_heatmap(self.user.id, start_date, end_date)
        
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        
        # 验证数据格式
        for item in data:
            self.assertIn('date', item)
            self.assertIn('count', item)
            self.assertIn('level', item)
    
    def test_word_heatmap_data_generation(self):
        """测试练习单词数热力图数据生成"""
        from apps.english.services import DataAnalysisService
        
        service = DataAnalysisService()
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()
        
        data = service.get_word_heatmap(self.user.id, start_date, end_date)
        
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
    
    def test_wpm_trend_data_generation(self):
        """测试WPM趋势图数据生成"""
        from apps.english.services import DataAnalysisService
        
        service = DataAnalysisService()
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()
        
        data = service.get_wpm_trend(self.user.id, start_date, end_date)
        
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
    
    def test_accuracy_trend_data_generation(self):
        """测试正确率趋势图数据生成"""
        from apps.english.services import DataAnalysisService
        
        service = DataAnalysisService()
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()
        
        data = service.get_accuracy_trend(self.user.id, start_date, end_date)
        
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
    
    def test_key_error_stats_data_generation(self):
        """测试按键错误统计数据生成"""
        from apps.english.services import DataAnalysisService
        
        service = DataAnalysisService()
        data = service.get_key_error_stats(self.user.id)
        
        self.assertIsInstance(data, list)
    
    def test_data_overview_generation(self):
        """测试数据概览生成"""
        from apps.english.services import DataAnalysisService
        
        service = DataAnalysisService()
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()
        overview = service.get_data_overview(self.user.id, start_date, end_date)
        
        self.assertIsInstance(overview, dict)
        self.assertIn('total_exercises', overview)
        self.assertIn('total_words', overview)
        self.assertIn('avg_wpm', overview)
        self.assertIn('avg_accuracy', overview)


@pytest.mark.unit
class TestDataAnalysisUnit(TestCase):
    """数据分析单元测试类"""
    
    def test_heatmap_level_calculation(self):
        """测试热力图级别计算"""
        from apps.english.services import DataAnalysisService
        
        service = DataAnalysisService()
        
        # 测试不同数量的级别计算
        self.assertEqual(service._get_heatmap_level(0), 0)
        self.assertEqual(service._get_heatmap_level(1), 1)
        self.assertEqual(service._get_heatmap_level(5), 2)
        self.assertEqual(service._get_heatmap_level(10), 3)
        self.assertEqual(service._get_heatmap_level(20), 4)
    
    def test_date_range_validation(self):
        """测试日期范围验证"""
        from apps.english.services import DataAnalysisService
        
        service = DataAnalysisService()
        
        # 测试有效日期范围
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()
        
        # 这里应该能正常处理，不会抛出异常
        try:
            service.get_exercise_heatmap(1, start_date, end_date)
            self.assertTrue(True)  # 如果没有异常，测试通过
        except Exception as e:
            self.fail(f"不应该抛出异常: {e}")


@pytest.mark.integration
class TestDataAnalysisIntegration(TestCase):
    """数据分析集成测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.user = TestUserManager.create_test_user()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_full_data_analysis_workflow(self):
        """测试完整的数据分析工作流"""
        # 1. 创建练习数据
        self._create_practice_session()
        
        # 2. 获取各种分析数据
        responses = {}
        
        # 练习次数热力图
        responses['exercise_heatmap'] = self.client.get('/api/v1/english/data-analysis/exercise_heatmap/')
        
        # 练习单词数热力图
        responses['word_heatmap'] = self.client.get('/api/v1/english/data-analysis/word_heatmap/')
        
        # WPM趋势图
        responses['wpm_trend'] = self.client.get('/api/v1/english/data-analysis/wpm_trend/')
        
        # 正确率趋势图
        responses['accuracy_trend'] = self.client.get('/api/v1/english/data-analysis/accuracy_trend/')
        
        # 按键错误统计
        responses['key_error_stats'] = self.client.get('/api/v1/english/data-analysis/key_error_stats/')
        
        # 数据概览
        responses['overview'] = self.client.get('/api/v1/english/data-analysis/overview/')
        
        # 验证所有API都返回成功
        for name, response in responses.items():
            with self.subTest(api_name=name):
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertTrue(response.data['success'])
    
    def _create_practice_session(self):
        """创建练习会话数据"""
        # 创建今天的练习记录
        TypingPracticeRecord.objects.create(
            user=self.user,
            word="hello",
            is_correct=True,
            typing_speed=60.0,
            response_time=1.2,
            total_time=1200,
            wrong_count=0,
            mistakes={},
            timing=[200, 300, 400, 300],
            session_date=datetime.now().date()
        )
        
        # 创建昨天的练习记录
        TypingPracticeRecord.objects.create(
            user=self.user,
            word="world",
            is_correct=False,
            typing_speed=45.0,
            response_time=1.8,
            total_time=1800,
            wrong_count=2,
            mistakes={'w': 1, 'o': 1},
            timing=[400, 500, 600, 300],
            session_date=datetime.now().date() - timedelta(days=1)
        )
"""
数据分析功能测试
测试英语学习模块的数据分析相关功能
"""

import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from datetime import datetime, timedelta
import json

from tests.utils.test_helpers import TestDataFactory, TestUserManager
from apps.english.models import TypingPracticeRecord, DailyPracticeStats, KeyErrorStats

User = get_user_model()


class TestDataAnalysisAPI(TestCase):
    """数据分析API测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.user = TestUserManager.create_test_user()
        self.client.force_authenticate(user=self.user)
        
        # 创建测试数据
        self._create_test_practice_data()
    
    def _create_test_practice_data(self):
        """创建测试练习数据"""
        # 创建练习记录
        for i in range(10):
            TypingPracticeRecord.objects.create(
                user=self.user,
                word=f"test_word_{i}",
                is_correct=True,
                typing_speed=50.0 + i,
                response_time=1.0,
                total_time=1000 + i * 100,
                wrong_count=0,
                mistakes={},
                timing=[100, 200, 300],
                session_date=datetime.now().date() - timedelta(days=i)
            )
        
        # 创建每日统计
        DailyPracticeStats.objects.create(
            user=self.user,
            date=datetime.now().date(),
            exercise_count=10,
            word_count=10,
            avg_wpm=55.0,
            accuracy_rate=95.0
        )
        
        # 创建按键错误统计
        KeyErrorStats.objects.create(
            user=self.user,
            key='a',
            error_count=5,
            last_error_date=datetime.now().date()
        )
    
    def test_exercise_heatmap_api(self):
        """测试练习次数热力图API"""
        response = self.client.get('/api/v1/english/data-analysis/exercise_heatmap/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
        
        # 验证数据结构
        data = response.data['data']
        self.assertIsInstance(data, list)
        if data:
            self.assertIn('date', data[0])
            self.assertIn('count', data[0])
            self.assertIn('level', data[0])
    
    def test_word_heatmap_api(self):
        """测试练习单词数热力图API"""
        response = self.client.get('/api/v1/english/data-analysis/word_heatmap/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
    
    def test_wpm_trend_api(self):
        """测试WPM趋势图API"""
        response = self.client.get('/api/v1/english/data-analysis/wpm_trend/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
    
    def test_accuracy_trend_api(self):
        """测试正确率趋势图API"""
        response = self.client.get('/api/v1/english/data-analysis/accuracy_trend/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
    
    def test_key_error_stats_api(self):
        """测试按键错误统计API"""
        response = self.client.get('/api/v1/english/data-analysis/key_error_stats/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
    
    def test_data_overview_api(self):
        """测试数据概览API"""
        response = self.client.get('/api/v1/english/data-analysis/overview/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
        
        # 验证概览数据
        overview = response.data['data']
        self.assertIn('total_exercises', overview)
        self.assertIn('total_words', overview)
        self.assertIn('avg_wpm', overview)
        self.assertIn('avg_accuracy', overview)
    
    def test_date_range_filtering(self):
        """测试日期范围过滤"""
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        response = self.client.get(f'/api/v1/english/data-analysis/exercise_heatmap/?start_date={start_date}&end_date={end_date}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
    
    def test_unauthorized_access(self):
        """测试未授权访问"""
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/v1/english/data-analysis/exercise_heatmap/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestDataAnalysisService(TestCase):
    """数据分析服务测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.user = TestUserManager.create_test_user()
        self._create_test_data()
    
    def _create_test_data(self):
        """创建测试数据"""
        # 创建多天的练习数据
        for i in range(30):
            date = datetime.now().date() - timedelta(days=i)
            TypingPracticeRecord.objects.create(
                user=self.user,
                word=f"word_{i}",
                is_correct=i % 3 != 0,  # 部分错误
                typing_speed=40.0 + (i % 20),
                response_time=1.0 + (i % 5) * 0.1,
                total_time=1000 + i * 50,
                wrong_count=i % 3,
                mistakes={'a': 1} if i % 3 == 0 else {},
                timing=[100, 200, 300],
                session_date=date
            )
    
    def test_exercise_heatmap_data_generation(self):
        """测试练习次数热力图数据生成"""
        from apps.english.services import DataAnalysisService
        
        service = DataAnalysisService()
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()
        
        data = service.get_exercise_heatmap(self.user.id, start_date, end_date)
        
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        
        # 验证数据格式
        for item in data:
            self.assertIn('date', item)
            self.assertIn('count', item)
            self.assertIn('level', item)
    
    def test_word_heatmap_data_generation(self):
        """测试练习单词数热力图数据生成"""
        from apps.english.services import DataAnalysisService
        
        service = DataAnalysisService()
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()
        
        data = service.get_word_heatmap(self.user.id, start_date, end_date)
        
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
    
    def test_wpm_trend_data_generation(self):
        """测试WPM趋势图数据生成"""
        from apps.english.services import DataAnalysisService
        
        service = DataAnalysisService()
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()
        
        data = service.get_wpm_trend(self.user.id, start_date, end_date)
        
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
    
    def test_accuracy_trend_data_generation(self):
        """测试正确率趋势图数据生成"""
        from apps.english.services import DataAnalysisService
        
        service = DataAnalysisService()
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()
        
        data = service.get_accuracy_trend(self.user.id, start_date, end_date)
        
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
    
    def test_key_error_stats_data_generation(self):
        """测试按键错误统计数据生成"""
        from apps.english.services import DataAnalysisService
        
        service = DataAnalysisService()
        data = service.get_key_error_stats(self.user.id)
        
        self.assertIsInstance(data, list)
    
    def test_data_overview_generation(self):
        """测试数据概览生成"""
        from apps.english.services import DataAnalysisService
        
        service = DataAnalysisService()
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()
        overview = service.get_data_overview(self.user.id, start_date, end_date)
        
        self.assertIsInstance(overview, dict)
        self.assertIn('total_exercises', overview)
        self.assertIn('total_words', overview)
        self.assertIn('avg_wpm', overview)
        self.assertIn('avg_accuracy', overview)


@pytest.mark.unit
class TestDataAnalysisUnit(TestCase):
    """数据分析单元测试类"""
    
    def test_heatmap_level_calculation(self):
        """测试热力图级别计算"""
        from apps.english.services import DataAnalysisService
        
        service = DataAnalysisService()
        
        # 测试不同数量的级别计算
        self.assertEqual(service._get_heatmap_level(0), 0)
        self.assertEqual(service._get_heatmap_level(1), 1)
        self.assertEqual(service._get_heatmap_level(5), 2)
        self.assertEqual(service._get_heatmap_level(10), 3)
        self.assertEqual(service._get_heatmap_level(20), 4)
    
    def test_date_range_validation(self):
        """测试日期范围验证"""
        from apps.english.services import DataAnalysisService
        
        service = DataAnalysisService()
        
        # 测试有效日期范围
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()
        
        # 这里应该能正常处理，不会抛出异常
        try:
            service.get_exercise_heatmap(1, start_date, end_date)
            self.assertTrue(True)  # 如果没有异常，测试通过
        except Exception as e:
            self.fail(f"不应该抛出异常: {e}")


@pytest.mark.integration
class TestDataAnalysisIntegration(TestCase):
    """数据分析集成测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.user = TestUserManager.create_test_user()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_full_data_analysis_workflow(self):
        """测试完整的数据分析工作流"""
        # 1. 创建练习数据
        self._create_practice_session()
        
        # 2. 获取各种分析数据
        responses = {}
        
        # 练习次数热力图
        responses['exercise_heatmap'] = self.client.get('/api/v1/english/data-analysis/exercise_heatmap/')
        
        # 练习单词数热力图
        responses['word_heatmap'] = self.client.get('/api/v1/english/data-analysis/word_heatmap/')
        
        # WPM趋势图
        responses['wpm_trend'] = self.client.get('/api/v1/english/data-analysis/wpm_trend/')
        
        # 正确率趋势图
        responses['accuracy_trend'] = self.client.get('/api/v1/english/data-analysis/accuracy_trend/')
        
        # 按键错误统计
        responses['key_error_stats'] = self.client.get('/api/v1/english/data-analysis/key_error_stats/')
        
        # 数据概览
        responses['overview'] = self.client.get('/api/v1/english/data-analysis/overview/')
        
        # 验证所有API都返回成功
        for name, response in responses.items():
            with self.subTest(api_name=name):
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertTrue(response.data['success'])
    
    def _create_practice_session(self):
        """创建练习会话数据"""
        # 创建今天的练习记录
        TypingPracticeRecord.objects.create(
            user=self.user,
            word="hello",
            is_correct=True,
            typing_speed=60.0,
            response_time=1.2,
            total_time=1200,
            wrong_count=0,
            mistakes={},
            timing=[200, 300, 400, 300],
            session_date=datetime.now().date()
        )
        
        # 创建昨天的练习记录
        TypingPracticeRecord.objects.create(
            user=self.user,
            word="world",
            is_correct=False,
            typing_speed=45.0,
            response_time=1.8,
            total_time=1800,
            wrong_count=2,
            mistakes={'w': 1, 'o': 1},
            timing=[400, 500, 600, 300],
            session_date=datetime.now().date() - timedelta(days=1)
        )
