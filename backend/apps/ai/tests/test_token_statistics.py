"""
Token统计功能测试
"""
import json
from decimal import Decimal
from datetime import datetime, timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from unittest.mock import patch, MagicMock

from apps.ai.models import (
    AIProvider, AIModel, APIKey, TokenUsage, 
    PerformanceMetric, SystemAlert
)
from apps.ai.services.token_statistics import (
    TokenStatisticsService, TokenStatistics, BudgetAlert
)

User = get_user_model()


class TokenStatisticsServiceTest(TestCase):
    """Token统计服务测试"""
    
    def setUp(self):
        """设置测试数据"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.provider = AIProvider.objects.create(
            name='openai-test',
            provider_type='openai',
            display_name='OpenAI',
            base_url='https://api.openai.com/v1',
            is_active=True
        )
        
        self.model = AIModel.objects.create(
            provider=self.provider,
            model_id='gpt-3.5-turbo',
            display_name='GPT-3.5 Turbo',
            max_tokens=4096,
            is_active=True
        )
        
        self.api_key = APIKey.objects.create(
            user=self.user,
            provider=self.provider,
            name='test-key',
            encrypted_key='test-encrypted-key'
        )
        
        # 创建Token统计服务实例
        self.service = TokenStatisticsService()
    
    def test_realtime_statistics_empty(self):
        """测试空数据的实时统计"""
        stats = self.service.get_realtime_statistics(user=self.user)
        
        self.assertIsInstance(stats, TokenStatistics)
        self.assertEqual(stats.total_requests, 0)
        self.assertEqual(stats.input_tokens, 0)
        self.assertEqual(stats.output_tokens, 0)
        self.assertEqual(stats.total_cost, Decimal('0.00'))
        # 检查基本属性存在
        self.assertTrue(hasattr(stats, 'period'))
        self.assertTrue(hasattr(stats, 'start_time'))
        self.assertTrue(hasattr(stats, 'end_time'))
    
    def test_realtime_statistics_with_data(self):
        """测试有数据的实时统计"""
        # 创建今日Token使用记录
        today = timezone.now().date()
        TokenUsage.objects.create(
            user=self.user,
            provider=self.provider,
            model=self.model,
            api_key=self.api_key,
            input_tokens=100,
            output_tokens=50,
            total_tokens=150,
            input_cost=Decimal('0.0005'),
            output_cost=Decimal('0.0005'),
            total_cost=Decimal('0.001'),
            response_time=0.5
        )
        
        TokenUsage.objects.create(
            user=self.user,
            provider=self.provider,
            model=self.model,
            api_key=self.api_key,
            input_tokens=200,
            output_tokens=100,
            total_tokens=300,
            input_cost=Decimal('0.001'),
            output_cost=Decimal('0.001'),
            total_cost=Decimal('0.002'),
            response_time=0.5
        )
        
        stats = self.service.get_realtime_statistics(user=self.user)
        
        self.assertIsInstance(stats, TokenStatistics)
        self.assertEqual(stats.total_requests, 2)
        self.assertEqual(stats.input_tokens, 300)
        self.assertEqual(stats.output_tokens, 150)
        self.assertEqual(stats.total_tokens, 450)
        self.assertEqual(stats.total_cost, Decimal('0.003'))
    
    def test_historical_statistics(self):
        """测试历史统计"""
        # 创建一些当前数据用于测试
        TokenUsage.objects.create(
            user=self.user,
            provider=self.provider,
            model=self.model,
            api_key=self.api_key,
            input_tokens=100,
            output_tokens=50,
            total_tokens=150,
            input_cost=Decimal('0.0005'),
            output_cost=Decimal('0.0005'),
            total_cost=Decimal('0.001'),
            response_time=0.5
        )
        
        TokenUsage.objects.create(
            user=self.user,
            provider=self.provider,
            model=self.model,
            api_key=self.api_key,
            input_tokens=200,
            output_tokens=100,
            total_tokens=300,
            input_cost=Decimal('0.001'),
            output_cost=Decimal('0.001'),
            total_cost=Decimal('0.002'),
            response_time=0.5
        )
        
        # 测试历史统计功能（所有数据都在范围内）
        stats = self.service.get_historical_statistics(
            user=self.user, 
            days=7
        )
        
        # 验证统计结果（返回的是列表）
        self.assertIsInstance(stats, list)
        if stats:
            # 如果有统计数据，验证第一个元素
            first_stat = stats[0]
            self.assertIsInstance(first_stat, TokenStatistics)
    
    def test_provider_statistics(self):
        """测试按提供商统计"""
        # 创建另一个提供商
        provider2 = AIProvider.objects.create(
            name='anthropic-test',
            provider_type='anthropic',
            display_name='Anthropic',
            base_url='https://api.anthropic.com/v1',
            is_active=True
        )
        
        model2 = AIModel.objects.create(
            provider=provider2,
            model_id='claude-3-sonnet',
            display_name='Claude 3 Sonnet',
            max_tokens=4096,
            is_active=True
        )
        
        api_key2 = APIKey.objects.create(
            user=self.user,
            provider=provider2,
            name='claude-key',
            encrypted_key='claude-encrypted-key'
        )
        
        today = timezone.now().date()
        
        # OpenAI数据
        TokenUsage.objects.create(
            user=self.user,
            provider=self.provider,
            model=self.model,
            api_key=self.api_key,
            input_tokens=100,
            output_tokens=50,
            total_tokens=150,
            input_cost=Decimal('0.0005'),
            output_cost=Decimal('0.0005'),
            total_cost=Decimal('0.001'),
            response_time=0.5
        )
        
        # Anthropic数据
        TokenUsage.objects.create(
            user=self.user,
            provider=provider2,
            model=model2,
            api_key=api_key2,
            input_tokens=200,
            output_tokens=100,
            total_tokens=300,
            input_cost=Decimal('0.001'),
            output_cost=Decimal('0.001'),
            total_cost=Decimal('0.002'),
            response_time=0.5
        )
        
        stats = self.service.get_provider_statistics(
            user=self.user
        )
        
        # stats是列表，需要检查第一个元素
        self.assertIsInstance(stats, list)
        if stats:
            first_stat = stats[0]
            self.assertIsInstance(first_stat, ProviderStatistics)
        
        stats_all = self.service.get_realtime_statistics(user=self.user)
        # 检查实时统计对象
        self.assertIsInstance(stats_all, TokenStatistics)
    
    def test_model_statistics(self):
        """测试按模型统计"""
        # 创建另一个模型
        model2 = AIModel.objects.create(
            provider=self.provider,
            model_id='gpt-4',
            display_name='GPT-4',
            max_tokens=8192,
            is_active=True
        )
        
        today = timezone.now().date()
        
        # GPT-3.5数据
        TokenUsage.objects.create(
            user=self.user,
            provider=self.provider,
            model=self.model,
            api_key=self.api_key,
            input_tokens=100,
            output_tokens=50,
            total_tokens=150,
            input_cost=Decimal('0.0005'),
            output_cost=Decimal('0.0005'),
            total_cost=Decimal('0.001'),
            response_time=0.5
        )
        
        # GPT-4数据
        TokenUsage.objects.create(
            user=self.user,
            provider=self.provider,
            model=model2,
            api_key=self.api_key,
            input_tokens=200,
            output_tokens=100,
            total_tokens=300,
            input_cost=Decimal('0.0015'),
            output_cost=Decimal('0.0015'),
            total_cost=Decimal('0.003'),
            response_time=0.5
        )
        
        stats = self.service.get_model_statistics(
            user=self.user
        )
        
        self.assertEqual(stats.total_requests, 1)
        self.assertEqual(stats.input_tokens, 100)
        self.assertEqual(stats.output_tokens, 50)
        self.assertEqual(stats.total_cost, Decimal('0.001'))
        
        stats_all = self.service.get_realtime_statistics(user=self.user)
        self.assertEqual(len(stats_all.model_breakdown), 2)
    
    def test_user_summary(self):
        """测试用户总结"""
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        
        # 今日数据
        TokenUsage.objects.create(
            user=self.user,
            provider=self.provider,
            model=self.model,
            api_key=self.api_key,
            input_tokens=100,
            output_tokens=50,
            total_tokens=150,
            input_cost=Decimal('0.0005'),
            output_cost=Decimal('0.0005'),
            total_cost=Decimal('0.001'),
            response_time=0.5
        )
        
        # 昨日数据
        TokenUsage.objects.create(
            user=self.user,
            provider=self.provider,
            model=self.model,
            api_key=self.api_key,
            input_tokens=200,
            output_tokens=100,
            total_tokens=300,
            input_cost=Decimal('0.001'),
            output_cost=Decimal('0.001'),
            total_cost=Decimal('0.002'),
            response_time=1.0
        )
        
        summary = self.service.get_user_summary(user=self.user)
        
        self.assertIn('today', summary)
        self.assertIn('yesterday', summary)
        self.assertIn('last_7_days', summary)
        self.assertIn('last_30_days', summary)
        self.assertIn('total', summary)
        
        # 验证今日数据
        self.assertEqual(summary['today']['total_requests'], 1)
        self.assertEqual(summary['today']['total_cost'], Decimal('0.001'))
        
        # 验证昨日数据
        self.assertEqual(summary['yesterday']['total_requests'], 1)
        self.assertEqual(summary['yesterday']['total_cost'], Decimal('0.002'))
        
        # 验证7天数据
        self.assertEqual(summary['last_7_days']['total_requests'], 2)
        self.assertEqual(summary['last_7_days']['total_cost'], Decimal('0.003'))
    
    @patch('apps.ai.models.UsageQuota.objects.filter')
    def test_check_budget_alerts(self, mock_quota_filter):
        """测试预算告警检查"""
        # 模拟配额数据
        mock_quota = MagicMock()
        mock_quota.user = self.user
        mock_quota.monthly_limit = Decimal('10.00')
        mock_quota.daily_limit = Decimal('1.00')
        mock_quota_filter.return_value = [mock_quota]
        
        # 创建使用数据，超过每日限额的80%
        today = timezone.now().date()
        TokenUsage.objects.create(
            user=self.user,
            provider=self.provider,
            model=self.model,
            api_key=self.api_key,
            input_tokens=1000,
            output_tokens=500,
            total_tokens=1500,
            input_cost=Decimal('0.425'),
            output_cost=Decimal('0.425'),
            total_cost=Decimal('0.85'),  # 超过每日限额的80%
            response_time=1.5
        )
        
        alerts = self.service.check_budget_alerts()
        
        self.assertGreater(len(alerts), 0)
        alert = alerts[0]
        self.assertIsInstance(alert, BudgetAlert)
        self.assertEqual(alert.user_id, self.user.id)
        self.assertEqual(alert.username, self.user.username)
        self.assertGreater(alert.usage_percentage, 80)
    
    def test_token_statistics_to_dict(self):
        """测试TokenStatistics转字典"""
        from datetime import datetime
        now = datetime.now()
        stats = TokenStatistics(
            period='day',
            start_time=now,
            end_time=now,
            total_requests=10,
            input_tokens=1000,
            output_tokens=500,
            total_tokens=1500,
            total_cost=Decimal('0.01'),
            avg_tokens_per_request=150.0
        )
        
        result = stats.to_dict()
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['total_requests'], 10)
        self.assertEqual(result['input_tokens'], 1000)
        self.assertEqual(result['output_tokens'], 500)
        self.assertEqual(result['total_tokens'], 1500)
        self.assertEqual(result['total_cost'], 0.01)  # Decimal转为float
        self.assertEqual(result['avg_tokens_per_request'], 150.0)
        self.assertIn('period', result)
        self.assertIn('start_time', result)
        self.assertIn('end_time', result)


from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken


class TokenStatisticsAPITest(APITestCase):
    """Token统计API测试"""
    
    def setUp(self):
        """设置测试数据"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.provider = AIProvider.objects.create(
            name='openai-test',
            provider_type='openai',
            display_name='OpenAI',
            base_url='https://api.openai.com/v1',
            is_active=True
        )
        
        self.model = AIModel.objects.create(
            provider=self.provider,
            model_id='gpt-3.5-turbo',
            display_name='GPT-3.5 Turbo',
            max_tokens=4096,
            is_active=True
        )
        
        self.api_key = APIKey.objects.create(
            user=self.user,
            provider=self.provider,
            name='test-key',
            encrypted_key='test-encrypted-key'
        )
        
        # 创建JWT token
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        
        # 设置认证头
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
    
    def test_realtime_statistics_api(self):
        """测试实时统计API"""
        url = reverse('ai:tokenstatistics-realtime')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertIn('success', data)
        self.assertIn('data', data)
        self.assertIn('timestamp', data)
        self.assertTrue(data['success'])
        
        stats_data = data['data']
        self.assertIn('total_requests', stats_data)
        self.assertIn('input_tokens', stats_data)
        self.assertIn('output_tokens', stats_data)
        self.assertIn('total_cost', stats_data)
    
    def test_historical_statistics_api(self):
        """测试历史统计API"""
        url = reverse('ai:tokenstatistics-historical')
        response = self.client.get(url, {'days': 7})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertIn('success', data)
        self.assertIn('data', data)
        self.assertTrue(data['success'])
    
    def test_user_summary_api(self):
        """测试用户总结API"""
        url = reverse('ai:tokenstatistics-summary')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertIn('success', data)
        self.assertIn('data', data)
        self.assertTrue(data['success'])
        
        summary_data = data['data']
        self.assertIn('user_id', summary_data)
        self.assertIn('username', summary_data)
        self.assertIn('period_days', summary_data)
        self.assertIn('total_requests', summary_data)
        self.assertIn('total_cost', summary_data)
        self.assertIn('today_requests', summary_data)
        self.assertIn('today_tokens', summary_data)
        self.assertIn('today_cost', summary_data)
    
    def test_unauthorized_access(self):
        """测试未授权访问"""
        self.client.credentials()  # 清除认证头
        
        url = reverse('ai:tokenstatistics-realtime')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)