"""
AI配置管理API测试
"""

import json
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import patch, MagicMock

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from ..config_models import AIProvider, APIKey, AIModel, TokenUsage, UsageQuota, AIProviderType
from ..adapters.base import HealthCheckResult

User = get_user_model()


class AIProviderViewSetTestCase(APITestCase):
    """AI提供商ViewSet测试"""
    
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # 生成JWT token
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        
        # 设置认证头
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        # 创建测试提供商
        self.provider = AIProvider.objects.create(
            name='test_provider',
            provider_type=AIProviderType.OPENAI,
            display_name='Test Provider',
            base_url='https://api.test.com/v1',
            is_active=True,
            created_by=self.user
        )
        
        # 创建测试API密钥
        self.api_key = APIKey.objects.create(
            provider=self.provider,
            user=self.user,
            name='Test Key',
            is_active=True,
            is_default=True
        )
        self.api_key.set_key('sk-test123456789')
        self.api_key.save()
    
    def test_list_providers(self):
        """测试获取提供商列表"""
        url = reverse('ai:aiprovider-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # API返回的是列表，不是分页对象
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'test_provider')
    
    def test_create_provider(self):
        """测试创建提供商"""
        url = reverse('ai:aiprovider-list')
        data = {
            'name': 'new_provider',
            'provider_type': 'anthropic',
            'display_name': 'New Provider',
            'base_url': 'https://api.anthropic.com/v1',
            'description': 'Test provider'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'new_provider')
        self.assertEqual(response.data['created_by'], self.user.id)
    
    def test_update_provider(self):
        """测试更新提供商"""
        url = reverse('ai:aiprovider-detail', kwargs={'pk': self.provider.pk})
        data = {
            'display_name': 'Updated Provider',
            'description': 'Updated description'
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['display_name'], 'Updated Provider')
    
    def test_delete_provider(self):
        """测试删除提供商"""
        url = reverse('ai:aiprovider-detail', kwargs={'pk': self.provider.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(AIProvider.objects.filter(pk=self.provider.pk).exists())
    
    @patch('apps.ai.adapters.factory.AIAdapterFactory.create_adapter')
    def test_test_connection_success(self, mock_create_adapter):
        """测试连接测试成功"""
        # 模拟健康检查成功
        mock_adapter = MagicMock()
        mock_health_result = HealthCheckResult(
            is_healthy=True,
            response_time=0.15
        )
        
        # 创建异步模拟
        async def mock_health_check():
            return mock_health_result
        
        mock_adapter.health_check = mock_health_check
        mock_create_adapter.return_value = mock_adapter
        
        url = reverse('ai:aiprovider-test-connection', kwargs={'pk': self.provider.pk})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('连接测试成功', response.data['message'])
        
        # 验证提供商状态已更新
        self.provider.refresh_from_db()
        self.assertTrue(self.provider.is_healthy)
    
    @patch('apps.ai.adapters.factory.AIAdapterFactory.create_adapter')
    def test_test_connection_failure(self, mock_create_adapter):
        """测试连接测试失败"""
        # 模拟健康检查失败
        mock_adapter = MagicMock()
        mock_health_result = HealthCheckResult(
            is_healthy=False,
            response_time=0.0
        )
        
        # 创建异步模拟
        async def mock_health_check():
            return mock_health_result
        
        mock_adapter.health_check = mock_health_check
        mock_create_adapter.return_value = mock_adapter
        
        url = reverse('ai:aiprovider-test-connection', kwargs={'pk': self.provider.pk})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['success'])
        self.assertIn('连接测试失败', response.data['message'])
        
        # 验证提供商状态已更新
        self.provider.refresh_from_db()
        self.assertFalse(self.provider.is_healthy)
    
    def test_test_connection_no_api_key(self):
        """测试连接测试时没有API密钥"""
        # 删除API密钥
        self.api_key.delete()
        
        url = reverse('ai:aiprovider-test-connection', kwargs={'pk': self.provider.pk})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('未找到可用的API密钥', response.data['message'])
    
    @patch('apps.ai.adapters.factory.AIAdapterFactory.create_adapter')
    def test_bulk_test(self, mock_create_adapter):
        """测试批量连接测试"""
        # 创建第二个提供商
        provider2 = AIProvider.objects.create(
            name='test_provider2',
            provider_type=AIProviderType.ANTHROPIC,
            display_name='Test Provider 2',
            base_url='https://api.anthropic.com/v1',
            is_active=True,
            created_by=self.user
        )
        
        api_key2 = APIKey.objects.create(
            provider=provider2,
            user=self.user,
            name='Test Key 2',
            is_active=True,
            is_default=True
        )
        api_key2.set_key('sk-ant-test123456789')
        api_key2.save()
        
        # 模拟健康检查结果
        mock_adapter = MagicMock()
        mock_health_result = HealthCheckResult(
            is_healthy=True,
            response_time=0.12
        )
        
        # 创建异步模拟
        async def mock_health_check():
            return mock_health_result
        
        mock_adapter.health_check = mock_health_check
        mock_create_adapter.return_value = mock_adapter
        
        url = reverse('ai:aiprovider-bulk-test')
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_tested'], 2)
        self.assertEqual(response.data['success_count'], 2)
        self.assertEqual(response.data['failure_count'], 0)
        # 检查响应数据结构
        self.assertIn('total_tested', response.data)
        self.assertIn('success_count', response.data)
        self.assertIn('failure_count', response.data)
    
    def test_system_health(self):
        """测试系统健康状态"""
        url = reverse('ai:aiprovider-system-health')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_providers'], 1)
        self.assertEqual(response.data['active_providers'], 1)
        self.assertIn('health_percentage', response.data)
    
    def test_filter_by_active_status(self):
        """测试按活跃状态过滤"""
        # 创建非活跃提供商
        AIProvider.objects.create(
            name='inactive_provider',
            provider_type=AIProviderType.GOOGLE,
            display_name='Inactive Provider',
            base_url='https://api.google.com/v1',
            is_active=False,
            created_by=self.user
        )
        
        # 测试只获取活跃提供商
        url = reverse('ai:aiprovider-list') + '?is_active=true'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'test_provider')
    
    def test_unauthorized_access(self):
        """测试未认证访问"""
        self.client.credentials()  # 清除认证头
        
        url = reverse('ai:aiprovider-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class APIKeyViewSetTestCase(APITestCase):
    """API密钥ViewSet测试"""
    
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # 生成JWT token
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        
        # 设置认证头
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        # 创建测试提供商
        self.provider = AIProvider.objects.create(
            name='test_provider',
            provider_type=AIProviderType.OPENAI,
            display_name='Test Provider',
            base_url='https://api.test.com/v1',
            is_active=True
        )
        
        # 创建测试API密钥
        self.api_key = APIKey.objects.create(
            provider=self.provider,
            user=self.user,
            name='Test Key',
            is_active=True,
            is_default=True
        )
        self.api_key.set_key('sk-test123456789')
        self.api_key.save()
    
    def test_list_api_keys(self):
        """测试获取API密钥列表"""
        url = reverse('ai:apikey-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Key')
        self.assertIn('masked_key', response.data[0])
        self.assertNotIn('encrypted_key', response.data[0])
    
    def test_create_api_key(self):
        """测试创建API密钥"""
        url = reverse('ai:apikey-list')
        data = {
            'name': 'New Test Key',
            'provider': self.provider.id,
            'raw_key': 'sk-new123456789',
            'is_default': False
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Test Key')
        self.assertEqual(response.data['user'], self.user.id)
        
        # 验证密钥已加密存储
        created_key = APIKey.objects.get(id=response.data['id'])
        self.assertEqual(created_key.get_key(), 'sk-new123456789')
    
    def test_update_api_key(self):
        """测试更新API密钥"""
        url = reverse('ai:apikey-detail', kwargs={'pk': self.api_key.pk})
        data = {
            'name': 'Updated Test Key',
            'is_active': False
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Test Key')
        self.assertFalse(response.data['is_active'])
    
    def test_delete_api_key(self):
        """测试删除API密钥"""
        url = reverse('ai:apikey-detail', kwargs={'pk': self.api_key.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(APIKey.objects.filter(pk=self.api_key.pk).exists())
    
    @patch('apps.ai.adapters.factory.AIAdapterFactory.create_adapter')
    def test_test_api_key_success(self, mock_create_adapter):
        """测试API密钥测试成功"""
        # 模拟健康检查成功
        mock_adapter = MagicMock()
        mock_health_result = HealthCheckResult(
            is_healthy=True,
            response_time=0.18
        )
        mock_adapter.health_check.return_value = mock_health_result
        mock_create_adapter.return_value = mock_adapter
        
        url = reverse('ai:apikey-test', kwargs={'pk': self.api_key.pk})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('密钥测试成功', response.data['message'])
        
        # 验证最后使用时间已更新
        self.api_key.refresh_from_db()
        self.assertIsNotNone(self.api_key.last_used)
    
    def test_set_default_api_key(self):
        """测试设置默认API密钥"""
        # 创建第二个密钥
        api_key2 = APIKey.objects.create(
            provider=self.provider,
            user=self.user,
            name='Test Key 2',
            is_active=True,
            is_default=False
        )
        api_key2.set_key('sk-test987654321')
        api_key2.save()
        
        url = reverse('ai:apikey-set-default', kwargs={'pk': api_key2.pk})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # 验证默认状态已更新
        self.api_key.refresh_from_db()
        api_key2.refresh_from_db()
        
        self.assertFalse(self.api_key.is_default)
        self.assertTrue(api_key2.is_default)
    
    def test_expiring_soon_api_keys(self):
        """测试获取即将过期的API密钥"""
        # 设置密钥为3天后过期
        self.api_key.expires_at = timezone.now() + timedelta(days=3)
        self.api_key.save()
        
        url = reverse('ai:apikey-expiring-soon') + '?days=7'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['days_ahead'], 7)
        self.assertEqual(len(response.data['keys']), 1)
    
    def test_filter_by_provider(self):
        """测试按提供商过滤"""
        # 创建另一个提供商和密钥
        provider2 = AIProvider.objects.create(
            name='provider2',
            provider_type=AIProviderType.ANTHROPIC,
            display_name='Provider 2',
            base_url='https://api.anthropic.com/v1',
            is_active=True
        )
        
        APIKey.objects.create(
            provider=provider2,
            user=self.user,
            name='Key for Provider 2',
            is_active=True
        )
        
        # 测试按提供商过滤
        url = reverse('ai:apikey-list') + f'?provider={self.provider.id}'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['provider'], self.provider.id)
    
    def test_user_isolation(self):
        """测试用户隔离（只能看到自己的密钥）"""
        # 创建另一个用户和密钥
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        
        APIKey.objects.create(
            provider=self.provider,
            user=other_user,
            name='Other User Key',
            is_active=True
        )
        
        url = reverse('ai:apikey-list')
        response = self.client.get(url)
        
        # 应该只能看到当前用户的密钥
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['user'], self.user.id)


class TokenUsageViewSetTestCase(APITestCase):
    """Token使用统计ViewSet测试"""
    
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # 生成JWT token
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        
        # 设置认证头
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        # 创建测试数据
        self.provider = AIProvider.objects.create(
            name='test_provider',
            provider_type=AIProviderType.OPENAI,
            display_name='Test Provider',
            base_url='https://api.test.com/v1',
            is_active=True
        )
        
        self.model = AIModel.objects.create(
            provider=self.provider,
            model_id='gpt-3.5-turbo',
            display_name='GPT-3.5 Turbo',
            max_tokens=4096,
            cost_per_1k_input_tokens=0.001,
            cost_per_1k_output_tokens=0.002
        )
        
        # 创建API密钥
        self.api_key = APIKey.objects.create(
            user=self.user,
            provider=self.provider,
            name='Test API Key',
            is_active=True
        )
        self.api_key.set_key('test-key-123')
        self.api_key.save()
        
        # 创建使用记录
        self.usage = TokenUsage.objects.create(
            user=self.user,
            provider=self.provider,
            model=self.model,
            api_key=self.api_key,
            request_id='test-request-123',
            input_tokens=100,
            output_tokens=50,
            total_tokens=150,
            input_cost=Decimal('0.10'),
            output_cost=Decimal('0.15'),
            total_cost=Decimal('0.25'),
            response_time=1.5
        )
    
    def test_list_token_usage(self):
        """测试获取Token使用记录"""
        url = reverse('ai:tokenusage-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['total_tokens'], 150)
    
    def test_usage_summary(self):
        """测试使用统计摘要"""
        url = reverse('ai:tokenusage-summary')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['summary']['total_tokens'], 150)
        self.assertEqual(response.data['summary']['total_cost'], 0.25)
        self.assertEqual(response.data['summary']['total_requests'], 1)
    
    def test_usage_trends(self):
        """测试使用趋势数据"""
        url = reverse('ai:tokenusage-trends')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('daily_trends', response.data)
    
    def test_time_range_filter(self):
        """测试时间范围过滤"""
        # 创建旧的使用记录（8天前）
        from datetime import timedelta
        old_date = timezone.now() - timedelta(days=8)
        
        # 先创建记录，然后更新created_at
        old_usage = TokenUsage.objects.create(
            user=self.user,
            provider=self.provider,
            model=self.model,
            api_key=self.api_key,
            request_id='old-request-123',
            input_tokens=50,
            output_tokens=25,
            total_tokens=75,
            input_cost=Decimal('0.05'),
            output_cost=Decimal('0.075'),
            total_cost=Decimal('0.125'),
            response_time=1.0
        )
        
        # 直接更新数据库中的created_at字段
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE ai_token_usage SET created_at = %s WHERE id = %s",
                [old_date, old_usage.id]
            )
        
        # 测试今日范围
        url = reverse('ai:tokenusage-list') + '?time_range=today'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 应该只有今天的记录（setUp中创建的1条）
        self.assertEqual(len(response.data), 1)


class UsageQuotaViewSetTestCase(APITestCase):
    """使用配额ViewSet测试"""
    
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # 生成JWT token
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        
        # 设置认证头
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        # 创建测试提供商
        self.provider = AIProvider.objects.create(
            name='test_provider',
            provider_type='openai',
            display_name='Test Provider',
            base_url='https://api.openai.com/v1',
            is_active=True
        )
        
        # 创建测试配额
        self.quota = UsageQuota.objects.create(
            user=self.user,
            provider=self.provider,
            quota_type='monthly',
            token_limit=100000,
            token_used=25000,
            cost_limit=Decimal('100.00'),
            cost_used=Decimal('25.00'),
            request_limit=1000,
            request_used=250,
            period_start=timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0),
            period_end=timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0) + timedelta(days=30),
            is_active=True
        )
    
    def test_list_quotas(self):
        """测试获取配额列表"""
        url = reverse('ai:usagequota-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['quota_type'], 'monthly')
    
    def test_create_quota(self):
        """测试创建配额"""
        url = reverse('ai:usagequota-list')
        data = {
            'provider': self.provider.id,
            'quota_type': 'daily',
            'token_limit': 10000,
            'cost_limit': 10.0,
            'request_limit': 100,
            'period_start': timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat(),
            'period_end': (timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)).isoformat(),
            'is_active': True
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['quota_type'], 'daily')
        self.assertEqual(response.data['user'], self.user.id)
    
    def test_reset_quota(self):
        """测试重置配额"""
        url = reverse('ai:usagequota-reset', kwargs={'pk': self.quota.pk})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # 验证配额已重置
        self.quota.refresh_from_db()
        self.assertEqual(self.quota.token_used, 0)
        self.assertEqual(self.quota.cost_used, Decimal('0.00'))
        self.assertEqual(self.quota.request_used, 0)
    
    def test_quota_status(self):
        """测试配额状态"""
        url = reverse('ai:usagequota-status')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_quotas'], 1)
        self.assertEqual(response.data['exceeded_quotas'], 0)
        
        quota_data = response.data['quotas'][0]
        self.assertEqual(quota_data['usage_percentage'], 25.0)  # 25000/100000 * 100
        self.assertFalse(quota_data['is_exceeded'])
        self.assertEqual(quota_data['token_used'], 25000)
        self.assertEqual(quota_data['token_limit'], 100000)
