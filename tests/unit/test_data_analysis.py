"""
数据分析功能测试
测试数据分析相关的API和服务功能
"""

import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from datetime import datetime, timedelta
from apps.english.models import (
    TypingPracticeRecord, 
    DailyPracticeStats, 
    KeyErrorStats,
    TypingWord,
    Dictionary
)
from apps.english.services import DataAnalysisService

User = get_user_model()


@pytest.mark.django_db
class DataAnalysisServiceTest(TestCase):
    """数据分析服务测试"""
    
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # 创建测试词库和单词
        self.dictionary = Dictionary.objects.create(
            name='测试词典',
            description='测试用词典',
            category='test'
        )
        
        self.typing_word = TypingWord.objects.create(
            word='test',
            translation='测试',
            phonetic='test',
            difficulty='beginner',
            dictionary=self.dictionary,
            chapter=1,
            frequency=100
        )
        
        # 创建测试数据
        self.create_test_data()
        
        # 创建服务实例
        self.service = DataAnalysisService()
    
    def create_test_data(self):
        """创建测试数据"""
        # 创建最近7天的练习记录
        for i in range(7):
            date = timezone.now().date() - timedelta(days=i)
            
            # 每天创建不同数量的练习记录
            for j in range(i + 1):  # 第1天1条，第2天2条，以此类推
                TypingPracticeRecord.objects.create(
                    user=self.user,
                    word=f'word{j}',
                    is_correct=j % 2 == 0,  # 交替正确和错误
                    typing_speed=50 + j * 5,  # 递增的速度
                    response_time=2.0 + j * 0.1,
                    total_time=3000 + j * 100,
                    wrong_count=j % 3,
                    mistakes={'a': 1, 'b': 2} if j % 2 == 0 else {},
                    timing=[100, 200, 300],
                    session_date=date
                )
        
        # 创建按键错误统计
        KeyErrorStats.objects.create(
            user=self.user,
            key='a',
            error_count=10
        )
        KeyErrorStats.objects.create(
            user=self.user,
            key='b',
            error_count=8
        )
        KeyErrorStats.objects.create(
            user=self.user,
            key='c',
            error_count=5
        )
    
    def test_get_exercise_heatmap(self):
        """测试获取练习次数热力图数据"""
        start_date = timezone.now() - timedelta(days=7)
        end_date = timezone.now()
        
        data = self.service.get_exercise_heatmap(self.user.id, start_date, end_date)
        
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        
        # 验证数据结构
        for item in data:
            self.assertIn('date', item)
            self.assertIn('count', item)
            self.assertIn('level', item)
            self.assertIsInstance(item['count'], int)
            self.assertIsInstance(item['level'], int)
            self.assertGreaterEqual(item['level'], 0)
            self.assertLessEqual(item['level'], 4)
    
    def test_get_word_heatmap(self):
        """测试获取练习单词数热力图数据"""
        start_date = timezone.now() - timedelta(days=7)
        end_date = timezone.now()
        
        data = self.service.get_word_heatmap(self.user.id, start_date, end_date)
        
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        
        # 验证数据结构
        for item in data:
            self.assertIn('date', item)
            self.assertIn('count', item)
            self.assertIn('level', item)
            self.assertIsInstance(item['count'], int)
            self.assertIsInstance(item['level'], int)
    
    def test_get_wpm_trend(self):
        """测试获取WPM趋势数据"""
        start_date = timezone.now() - timedelta(days=7)
        end_date = timezone.now()
        
        data = self.service.get_wpm_trend(self.user.id, start_date, end_date)
        
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        
        # 验证数据结构
        for item in data:
            self.assertIsInstance(item, list)
            self.assertEqual(len(item), 2)
            self.assertIsInstance(item[0], str)  # 日期
            self.assertIsInstance(item[1], float)  # WPM值
    
    def test_get_accuracy_trend(self):
        """测试获取正确率趋势数据"""
        start_date = timezone.now() - timedelta(days=7)
        end_date = timezone.now()
        
        data = self.service.get_accuracy_trend(self.user.id, start_date, end_date)
        
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        
        # 验证数据结构
        for item in data:
            self.assertIsInstance(item, list)
            self.assertEqual(len(item), 2)
            self.assertIsInstance(item[0], str)  # 日期
            self.assertIsInstance(item[1], float)  # 正确率
            self.assertGreaterEqual(item[1], 0)
            self.assertLessEqual(item[1], 100)
    
    def test_get_key_error_stats(self):
        """测试获取按键错误统计"""
        data = self.service.get_key_error_stats(self.user.id)
        
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        
        # 验证数据结构
        for item in data:
            self.assertIn('name', item)
            self.assertIn('value', item)
            self.assertIsInstance(item['name'], str)
            self.assertIsInstance(item['value'], int)
            self.assertGreater(item['value'], 0)
    
    def test_get_data_overview(self):
        """测试获取数据概览"""
        start_date = timezone.now() - timedelta(days=7)
        end_date = timezone.now()
        
        data = self.service.get_data_overview(self.user.id, start_date, end_date)
        
        self.assertIsInstance(data, dict)
        self.assertIn('total_exercises', data)
        self.assertIn('total_words', data)
        self.assertIn('avg_wpm', data)
        self.assertIn('avg_accuracy', data)
        self.assertIn('date_range', data)
        
        # 验证数据类型
        self.assertIsInstance(data['total_exercises'], int)
        self.assertIsInstance(data['total_words'], int)
        self.assertIsInstance(data['avg_wpm'], float)
        self.assertIsInstance(data['avg_accuracy'], float)
        self.assertIsInstance(data['date_range'], list)
    
    def test_get_heatmap_level(self):
        """测试热力图等级计算"""
        # 测试不同数量的等级
        self.assertEqual(self.service._get_heatmap_level(0), 0)
        self.assertEqual(self.service._get_heatmap_level(1), 1)
        self.assertEqual(self.service._get_heatmap_level(3), 1)
        self.assertEqual(self.service._get_heatmap_level(4), 2)
        self.assertEqual(self.service._get_heatmap_level(7), 2)
        self.assertEqual(self.service._get_heatmap_level(8), 3)
        self.assertEqual(self.service._get_heatmap_level(11), 3)
        self.assertEqual(self.service._get_heatmap_level(12), 4)
    
    def test_aggregate_daily_stats(self):
        """测试每日统计数据聚合"""
        date = timezone.now().date()
        
        # 执行聚合
        self.service.aggregate_daily_stats(self.user.id, date)
        
        # 验证是否创建了统计记录
        stats = DailyPracticeStats.objects.filter(user=self.user, date=date)
        self.assertTrue(stats.exists())
        
        stat = stats.first()
        self.assertIsInstance(stat.exercise_count, int)
        self.assertIsInstance(stat.word_count, int)
        self.assertIsInstance(stat.total_time, float)
        self.assertIsInstance(stat.wrong_count, int)
        self.assertIsInstance(stat.avg_wpm, float)
        self.assertIsInstance(stat.accuracy_rate, float)


@pytest.mark.django_db
class DataAnalysisAPITest(TestCase):
    """数据分析API测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # 创建测试数据
        self.create_test_data()
        
        # 认证用户
        self.client.force_authenticate(user=self.user)
    
    def create_test_data(self):
        """创建测试数据"""
        # 创建最近3天的练习记录
        for i in range(3):
            date = timezone.now().date() - timedelta(days=i)
            for j in range(5):
                TypingPracticeRecord.objects.create(
                    user=self.user,
                    word=f'word{j}',
                    is_correct=j % 2 == 0,
                    typing_speed=50 + j * 5,
                    response_time=2.0,
                    total_time=3000,
                    wrong_count=j % 3,
                    mistakes={'a': 1} if j % 2 == 0 else {},
                    timing=[100, 200, 300],
                    session_date=date
                )
        
        # 创建按键错误统计
        KeyErrorStats.objects.create(
            user=self.user,
            key='a',
            error_count=10
        )
    
    def test_exercise_heatmap_api(self):
        """测试练习次数热力图API"""
        start_date = (timezone.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        end_date = timezone.now().strftime('%Y-%m-%d')
        
        response = self.client.get('/api/v1/english/data-analysis/exercise_heatmap/', {
            'start_date': start_date,
            'end_date': end_date
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('success', response.data)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
        self.assertIsInstance(response.data['data'], list)
    
    def test_word_heatmap_api(self):
        """测试练习单词数热力图API"""
        start_date = (timezone.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        end_date = timezone.now().strftime('%Y-%m-%d')
        
        response = self.client.get('/api/v1/english/data-analysis/word_heatmap/', {
            'start_date': start_date,
            'end_date': end_date
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('success', response.data)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
        self.assertIsInstance(response.data['data'], list)
    
    def test_wpm_trend_api(self):
        """测试WPM趋势API"""
        start_date = (timezone.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        end_date = timezone.now().strftime('%Y-%m-%d')
        
        response = self.client.get('/api/v1/english/data-analysis/wpm_trend/', {
            'start_date': start_date,
            'end_date': end_date
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('success', response.data)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
        self.assertIsInstance(response.data['data'], list)
    
    def test_accuracy_trend_api(self):
        """测试正确率趋势API"""
        start_date = (timezone.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        end_date = timezone.now().strftime('%Y-%m-%d')
        
        response = self.client.get('/api/v1/english/data-analysis/accuracy_trend/', {
            'start_date': start_date,
            'end_date': end_date
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('success', response.data)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
        self.assertIsInstance(response.data['data'], list)
    
    def test_key_error_stats_api(self):
        """测试按键错误统计API"""
        response = self.client.get('/api/v1/english/data-analysis/key_error_stats/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('success', response.data)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
        self.assertIsInstance(response.data['data'], list)
    
    def test_overview_api(self):
        """测试数据概览API"""
        start_date = (timezone.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        end_date = timezone.now().strftime('%Y-%m-%d')
        
        response = self.client.get('/api/v1/english/data-analysis/overview/', {
            'start_date': start_date,
            'end_date': end_date
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('success', response.data)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
        self.assertIsInstance(response.data['data'], dict)
        
        # 验证概览数据字段
        overview = response.data['data']
        self.assertIn('total_exercises', overview)
        self.assertIn('total_words', overview)
        self.assertIn('avg_wpm', overview)
        self.assertIn('avg_accuracy', overview)
    
    def test_api_requires_authentication(self):
        """测试API需要认证"""
        self.client.force_authenticate(user=None)
        
        response = self.client.get('/api/v1/english/data-analysis/overview/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_api_with_invalid_date_format(self):
        """测试API使用无效日期格式"""
        response = self.client.get('/api/v1/english/data-analysis/overview/', {
            'start_date': 'invalid-date',
            'end_date': 'invalid-date'
        })
        
        # 应该返回500错误或处理异常
        self.assertIn(response.status_code, [400, 500])
    
    def test_api_without_date_parameters(self):
        """测试API不使用日期参数"""
        response = self.client.get('/api/v1/english/data-analysis/overview/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('success', response.data)
        self.assertTrue(response.data['success'])


@pytest.mark.django_db
class DataAnalysisEdgeCaseTest(TestCase):
    """数据分析边界情况测试"""
    
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.service = DataAnalysisService()
    
    def test_empty_data_analysis(self):
        """测试空数据分析"""
        start_date = timezone.now() - timedelta(days=7)
        end_date = timezone.now()
        
        # 测试各种空数据情况
        heatmap_data = self.service.get_exercise_heatmap(self.user.id, start_date, end_date)
        self.assertEqual(heatmap_data, [])
        
        word_heatmap_data = self.service.get_word_heatmap(self.user.id, start_date, end_date)
        self.assertEqual(word_heatmap_data, [])
        
        wpm_trend_data = self.service.get_wpm_trend(self.user.id, start_date, end_date)
        self.assertEqual(wpm_trend_data, [])
        
        accuracy_trend_data = self.service.get_accuracy_trend(self.user.id, start_date, end_date)
        self.assertEqual(accuracy_trend_data, [])
        
        key_error_data = self.service.get_key_error_stats(self.user.id)
        self.assertEqual(key_error_data, [])
        
        overview_data = self.service.get_data_overview(self.user.id, start_date, end_date)
        self.assertEqual(overview_data['total_exercises'], 0)
        self.assertEqual(overview_data['total_words'], 0)
        self.assertEqual(overview_data['avg_wpm'], 0)
        self.assertEqual(overview_data['avg_accuracy'], 0)
    
    def test_large_date_range(self):
        """测试大日期范围"""
        start_date = timezone.now() - timedelta(days=365)
        end_date = timezone.now()
        
        # 应该能处理大日期范围而不出错
        try:
            data = self.service.get_data_overview(self.user.id, start_date, end_date)
            self.assertIsInstance(data, dict)
        except Exception as e:
            self.fail(f"大日期范围处理失败: {e}")
    
    def test_invalid_user_id(self):
        """测试无效用户ID"""
        start_date = timezone.now() - timedelta(days=7)
        end_date = timezone.now()
        
        # 使用不存在的用户ID
        data = self.service.get_data_overview(99999, start_date, end_date)
        self.assertEqual(data['total_exercises'], 0)
    
    def test_date_range_validation(self):
        """测试日期范围验证"""
        start_date = timezone.now()
        end_date = timezone.now() - timedelta(days=7)  # 结束日期早于开始日期
        
        # 应该能处理反向日期范围
        try:
            data = self.service.get_data_overview(self.user.id, start_date, end_date)
            self.assertIsInstance(data, dict)
        except Exception as e:
            self.fail(f"反向日期范围处理失败: {e}")


@pytest.mark.django_db
class DataAnalysisPerformanceTest(TestCase):
    """数据分析性能测试"""
    
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.service = DataAnalysisService()
        
        # 创建大量测试数据
        self.create_large_test_data()
    
    def create_large_test_data(self):
        """创建大量测试数据"""
        # 创建100天的数据，每天100条记录
        for i in range(100):
            date = timezone.now().date() - timedelta(days=i)
            for j in range(100):
                TypingPracticeRecord.objects.create(
                    user=self.user,
                    word=f'word{j}',
                    is_correct=j % 2 == 0,
                    typing_speed=50 + j % 50,
                    response_time=2.0,
                    total_time=3000,
                    wrong_count=j % 5,
                    mistakes={'a': 1} if j % 2 == 0 else {},
                    timing=[100, 200, 300],
                    session_date=date
                )
    
    def test_large_data_performance(self):
        """测试大数据量性能"""
        import time
        
        start_date = timezone.now() - timedelta(days=30)
        end_date = timezone.now()
        
        # 测试各种分析功能的性能
        start_time = time.time()
        self.service.get_exercise_heatmap(self.user.id, start_date, end_date)
        heatmap_time = time.time() - start_time
        
        start_time = time.time()
        self.service.get_data_overview(self.user.id, start_date, end_date)
        overview_time = time.time() - start_time
        
        # 性能应该在合理范围内（比如小于5秒）
        self.assertLess(heatmap_time, 5.0, f"热力图生成时间过长: {heatmap_time:.2f}秒")
        self.assertLess(overview_time, 5.0, f"概览生成时间过长: {overview_time:.2f}秒") 