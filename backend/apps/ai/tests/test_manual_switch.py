"""
手动切换端点与权限审计测试
"""

import pytest
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from datetime import timedelta

from ..models import (
    AIProvider, AIModel, FailoverStrategy, FailoverRule, ProviderHealthStatus, FallbackAuditLog
)
from ..services.failover_service import FailoverService

User = get_user_model()


@pytest.mark.django_db
class TestManualSwitchAPI(TestCase):
    """测试手动切换API端点"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        # 创建测试提供商
        self.primary_provider = AIProvider.objects.create(
            name='primary_openai',
            provider_type='openai',
            display_name='Primary OpenAI',
            base_url='https://api.openai.com/v1',
            is_active=True,
            is_healthy=True
        )
        
        self.fallback_provider1 = AIProvider.objects.create(
            name='fallback_anthropic',
            provider_type='anthropic',
            display_name='Fallback Anthropic',
            base_url='https://api.anthropic.com',
            is_active=True,
            is_healthy=True
        )
        
        self.fallback_provider2 = AIProvider.objects.create(
            name='fallback_google',
            provider_type='google',
            display_name='Fallback Google',
            base_url='https://generativelanguage.googleapis.com',
            is_active=True,
            is_healthy=True
        )
        
        # 创建测试模型
        self.primary_model = AIModel.objects.create(
            provider=self.primary_provider,
            model_id='gpt-4',
            display_name='GPT-4',
            max_tokens=8192,
            is_active=True
        )
        
        self.fallback_model1 = AIModel.objects.create(
            provider=self.fallback_provider1,
            model_id='claude-3-sonnet',
            display_name='Claude 3 Sonnet',
            max_tokens=4096,
            is_active=True
        )
        
        self.fallback_model2 = AIModel.objects.create(
            provider=self.fallback_provider2,
            model_id='gemini-pro',
            display_name='Gemini Pro',
            max_tokens=30720,
            is_active=True
        )
        
        # 创建故障转移策略
        self.strategy = FailoverStrategy.objects.create(
            user=self.user,
            name='Test Strategy',
            description='Test failover strategy',
            primary_provider=self.primary_provider,
            primary_model=self.primary_model,
            active_provider=self.primary_provider,
            strategy_mode='priority',
            fail_threshold=3,
            recovery_threshold=5,
            cooldown=60,
            jitter_window=10,
            is_active=True
        )
        
        # 创建故障转移规则
        self.rule1 = FailoverRule.objects.create(
            strategy=self.strategy,
            fallback_provider=self.fallback_provider1,
            fallback_model=self.fallback_model1,
            priority=1,
            trigger_errors=['timeout', 'rate_limit']
        )
        
        self.rule2 = FailoverRule.objects.create(
            strategy=self.strategy,
            fallback_provider=self.fallback_provider2,
            fallback_model=self.fallback_model2,
            priority=2,
            trigger_errors=['quota_exceeded']
        )
        
        # 创建API客户端
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_manual_switch_with_target_provider(self):
        """测试指定目标提供商的手动切换"""
        url = reverse('ai:failoverstrategy-switch', kwargs={'pk': self.strategy.id})
        data = {
            'target_provider_id': self.fallback_provider1.id,
            'reason': '性能优化测试',
            'dry_run': False
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['target_provider'], 'Fallback Anthropic')
        self.assertEqual(response.data['data']['reason'], '性能优化测试')
        self.assertTrue(response.data['data']['switched'])
        
        # 验证策略已更新
        self.strategy.refresh_from_db()
        self.assertEqual(self.strategy.active_provider, self.fallback_provider1)
    
    def test_manual_switch_auto_select(self):
        """测试自动选择下一个可用提供商"""
        url = reverse('ai:failoverstrategy-switch', kwargs={'pk': self.strategy.id})
        data = {
            'reason': '自动选择测试',
            'dry_run': False
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIsNotNone(response.data['data']['target_provider'])
        self.assertTrue(response.data['data']['switched'])
    
    def test_manual_switch_dry_run(self):
        """测试试运行模式"""
        url = reverse('ai:failoverstrategy-switch', kwargs={'pk': self.strategy.id})
        data = {
            'target_provider_id': self.fallback_provider1.id,
            'reason': '试运行测试',
            'dry_run': True
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertTrue(response.data['data']['dry_run'])
        self.assertFalse(response.data['data']['switched'])
        
        # 验证策略未实际更新
        self.strategy.refresh_from_db()
        self.assertEqual(self.strategy.active_provider, self.primary_provider)
    
    def test_manual_switch_permission_denied(self):
        """测试权限不足的情况"""
        # 使用其他用户尝试切换
        self.client.force_authenticate(user=self.other_user)
        
        url = reverse('ai:failoverstrategy-switch', kwargs={'pk': self.strategy.id})
        data = {
            'target_provider_id': self.fallback_provider1.id,
            'reason': '权限测试',
            'dry_run': False
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['error_code'], 'PERMISSION_DENIED')
    
    def test_manual_switch_invalid_provider(self):
        """测试无效提供商的情况"""
        url = reverse('ai:failoverstrategy-switch', kwargs={'pk': self.strategy.id})
        data = {
            'target_provider_id': 99999,  # 不存在的提供商ID
            'reason': '无效提供商测试',
            'dry_run': False
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['error_code'], 'VALIDATION_ERROR')
    
    def test_manual_switch_provider_not_in_strategy(self):
        """测试提供商不在策略中的情况"""
        # 创建一个不在策略中的提供商
        external_provider = AIProvider.objects.create(
            name='external_provider',
            provider_type='custom',
            display_name='External Provider',
            base_url='https://external.com',
            is_active=True,
            is_healthy=True
        )
        
        url = reverse('ai:failoverstrategy-switch', kwargs={'pk': self.strategy.id})
        data = {
            'target_provider_id': external_provider.id,
            'reason': '外部提供商测试',
            'dry_run': False
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['error_code'], 'VALIDATION_ERROR')
    
    def test_manual_switch_unhealthy_provider(self):
        """测试不健康提供商的情况"""
        # 设置备用提供商为不健康
        self.fallback_provider1.is_healthy = False
        self.fallback_provider1.save()
        
        url = reverse('ai:failoverstrategy-switch', kwargs={'pk': self.strategy.id})
        data = {
            'target_provider_id': self.fallback_provider1.id,
            'reason': '不健康提供商测试',
            'dry_run': False
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['error_code'], 'VALIDATION_ERROR')
    
    def test_manual_switch_inactive_strategy(self):
        """测试非活跃策略的情况"""
        # 设置策略为非活跃
        self.strategy.is_active = False
        self.strategy.save()
        
        url = reverse('ai:failoverstrategy-switch', kwargs={'pk': self.strategy.id})
        data = {
            'target_provider_id': self.fallback_provider1.id,
            'reason': '非活跃策略测试',
            'dry_run': False
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('策略未激活', response.data['message'])
    
    def test_manual_switch_already_target_provider(self):
        """测试已经是目标提供商的情况"""
        url = reverse('ai:failoverstrategy-switch', kwargs={'pk': self.strategy.id})
        data = {
            'target_provider_id': self.primary_provider.id,  # 当前已经是主提供商
            'reason': '已经是目标提供商测试',
            'dry_run': False
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertFalse(response.data['data']['switched'])
        self.assertIn('当前已经是目标提供商', response.data['data']['message'])


@pytest.mark.django_db
class TestAuditLogsAPI(TestCase):
    """测试审计日志API端点"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # 创建测试提供商和策略
        self.primary_provider = AIProvider.objects.create(
            name='primary_openai',
            provider_type='openai',
            display_name='Primary OpenAI',
            base_url='https://api.openai.com/v1',
            is_active=True,
            is_healthy=True
        )
        
        self.fallback_provider = AIProvider.objects.create(
            name='fallback_anthropic',
            provider_type='anthropic',
            display_name='Fallback Anthropic',
            base_url='https://api.anthropic.com',
            is_active=True,
            is_healthy=True
        )
        
        self.primary_model = AIModel.objects.create(
            provider=self.primary_provider,
            model_id='gpt-4',
            display_name='GPT-4',
            max_tokens=8192,
            is_active=True
        )
        
        self.strategy = FailoverStrategy.objects.create(
            user=self.user,
            name='Test Strategy',
            description='Test failover strategy',
            primary_provider=self.primary_provider,
            primary_model=self.primary_model,
            active_provider=self.primary_provider,
            is_active=True
        )
        
        # 创建一些审计日志
        self.audit_log1 = FallbackAuditLog.objects.create(
            strategy=self.strategy,
            action_type='manual_switch',
            from_provider='Primary OpenAI',
            to_provider='Fallback Anthropic',
            reason='测试切换',
            operator=self.user
        )
        
        self.audit_log2 = FallbackAuditLog.objects.create(
            strategy=self.strategy,
            action_type='auto_switch',
            from_provider='Fallback Anthropic',
            to_provider='Primary OpenAI',
            reason='自动恢复',
            operator=None
        )
        
        # 创建API客户端
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_get_audit_logs(self):
        """测试获取审计日志"""
        url = reverse('ai:failoverstrategy-audit-logs', kwargs={'pk': self.strategy.id})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['summary']['total_logs'], 2)
        self.assertEqual(response.data['summary']['action_type_stats']['manual_switch'], 1)
        self.assertEqual(response.data['summary']['action_type_stats']['auto_switch'], 1)
    
    def test_get_audit_logs_with_filter(self):
        """测试带过滤条件的审计日志查询"""
        url = reverse('ai:failoverstrategy-audit-logs', kwargs={'pk': self.strategy.id})
        
        # 过滤手动切换
        response = self.client.get(url, {'action_type': 'manual_switch'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['action_type'], 'manual_switch')
    
    def test_get_audit_logs_with_limit(self):
        """测试限制返回数量的审计日志查询"""
        # 创建更多日志
        for i in range(5):
            FallbackAuditLog.objects.create(
                strategy=self.strategy,
                action_type='health_check',
                from_provider='Provider A',
                to_provider='Provider B',
                reason=f'健康检查 {i}',
                operator=self.user
            )
        
        url = reverse('ai:failoverstrategy-audit-logs', kwargs={'pk': self.strategy.id})
        response = self.client.get(url, {'limit': 3})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
    
    def test_get_audit_logs_permission_denied(self):
        """测试权限不足的情况"""
        # 使用其他用户尝试访问
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=other_user)
        
        url = reverse('ai:failoverstrategy-audit-logs', kwargs={'pk': self.strategy.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


@pytest.mark.django_db
class TestManualSwitchService(TestCase):
    """测试手动切换服务逻辑"""
    
    def setUp(self):
        """设置测试环境"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.primary_provider = AIProvider.objects.create(
            name='primary_openai',
            provider_type='openai',
            display_name='Primary OpenAI',
            base_url='https://api.openai.com/v1',
            is_active=True,
            is_healthy=True
        )
        
        self.fallback_provider = AIProvider.objects.create(
            name='fallback_anthropic',
            provider_type='anthropic',
            display_name='Fallback Anthropic',
            base_url='https://api.anthropic.com',
            is_active=True,
            is_healthy=True
        )
        
        self.primary_model = AIModel.objects.create(
            provider=self.primary_provider,
            model_id='gpt-4',
            display_name='GPT-4',
            max_tokens=8192,
            is_active=True
        )
        
        self.fallback_model1 = AIModel.objects.create(
            provider=self.fallback_provider,
            model_id='claude-3-sonnet',
            display_name='Claude 3 Sonnet',
            max_tokens=4096,
            is_active=True
        )
        
        self.strategy = FailoverStrategy.objects.create(
            user=self.user,
            name='Test Strategy',
            description='Test failover strategy',
            primary_provider=self.primary_provider,
            primary_model=self.primary_model,
            active_provider=self.primary_provider,
            is_active=True
        )
        
        # 创建故障转移规则
        self.rule = FailoverRule.objects.create(
            strategy=self.strategy,
            fallback_provider=self.fallback_provider,
            fallback_model=self.fallback_model1,
            priority=1,
            trigger_errors=['timeout', 'rate_limit']
        )
        
        self.failover_service = FailoverService(self.strategy)
    
    def test_manual_switch_success(self):
        """测试手动切换成功"""
        result = self.failover_service.manual_switch(
            target_provider=self.fallback_provider,
            reason='测试切换',
            operator=self.user,
            dry_run=False
        )
        
        self.assertTrue(result['success'])
        self.assertTrue(result['switched'])
        self.assertEqual(result['target_provider'], 'Fallback Anthropic')
        self.assertEqual(result['operator'], 'testuser')
        
        # 验证策略已更新
        self.strategy.refresh_from_db()
        self.assertEqual(self.strategy.active_provider, self.fallback_provider)
    
    def test_manual_switch_dry_run(self):
        """测试试运行模式"""
        result = self.failover_service.manual_switch(
            target_provider=self.fallback_provider,
            reason='试运行测试',
            operator=self.user,
            dry_run=True
        )
        
        self.assertTrue(result['success'])
        self.assertTrue(result['dry_run'])
        self.assertFalse(result['switched'])
        
        # 验证策略未实际更新
        self.strategy.refresh_from_db()
        self.assertEqual(self.strategy.active_provider, self.primary_provider)
    
    def test_manual_switch_permission_denied(self):
        """测试权限不足"""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        with self.assertRaises(PermissionError):
            self.failover_service.manual_switch(
                target_provider=self.fallback_provider,
                reason='权限测试',
                operator=other_user,
                dry_run=False
            )
    
    def test_manual_switch_provider_not_in_strategy(self):
        """测试提供商不在策略中"""
        external_provider = AIProvider.objects.create(
            name='external_provider',
            provider_type='custom',
            display_name='External Provider',
            base_url='https://external.com',
            is_active=True,
            is_healthy=True
        )
        
        with self.assertRaises(ValueError):
            self.failover_service.manual_switch(
                target_provider=external_provider,
                reason='外部提供商测试',
                operator=self.user,
                dry_run=False
            )
    
    def test_manual_switch_unhealthy_provider(self):
        """测试不健康提供商"""
        self.fallback_provider.is_healthy = False
        self.fallback_provider.save()
        
        with self.assertRaises(ValueError):
            self.failover_service.manual_switch(
                target_provider=self.fallback_provider,
                reason='不健康提供商测试',
                operator=self.user,
                dry_run=False
            )
    
    def test_manual_switch_audit_log_creation(self):
        """测试审计日志创建"""
        initial_count = FallbackAuditLog.objects.count()
        
        self.failover_service.manual_switch(
            target_provider=self.fallback_provider,
            reason='审计日志测试',
            operator=self.user,
            dry_run=False
        )
        
        # 验证审计日志已创建
        final_count = FallbackAuditLog.objects.count()
        self.assertEqual(final_count, initial_count + 1)
        
        # 验证日志内容
        latest_log = FallbackAuditLog.objects.latest('created_at')
        self.assertEqual(latest_log.action_type, 'manual_switch')
        self.assertEqual(latest_log.from_provider, 'Primary OpenAI')
        self.assertEqual(latest_log.to_provider, 'Fallback Anthropic')
        self.assertEqual(latest_log.reason, '审计日志测试')
        self.assertEqual(latest_log.operator, self.user)
