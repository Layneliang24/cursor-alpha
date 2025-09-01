"""
自动降级与恢复检测逻辑测试
"""

import pytest
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta

from ..models import (
    AIProvider, AIModel, FailoverStrategy, FailoverRule, ProviderHealthStatus
)
from ..services.failover_service import FailoverService

User = get_user_model()


@pytest.mark.django_db
class TestFailoverAutoSwitch(TestCase):
    """测试自动降级与恢复检测逻辑"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
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
        
        # 确保备用提供商被标记为健康
        self.fallback_provider1.is_healthy = True
        self.fallback_provider1.save()
        self.fallback_provider2.is_healthy = True
        self.fallback_provider2.save()
        
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
            cooldown=60,  # 1分钟冷却期
            jitter_window=10,  # 10秒抖动窗口
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
        
        # 创建故障转移服务
        self.failover_service = FailoverService(self.strategy)
    
    def test_initial_health_status_creation(self):
        """测试初始健康状态创建"""
        # 记录一次成功请求
        self.failover_service.record_request_result(
            self.primary_provider, 
            success=True, 
            response_time=1.5
        )
        
        # 验证健康状态记录已创建
        health_status = ProviderHealthStatus.objects.get(
            strategy=self.strategy,
            provider=self.primary_provider
        )
        
        self.assertEqual(health_status.success_count, 1)
        self.assertEqual(health_status.failure_count, 0)
        self.assertEqual(health_status.consecutive_successes, 1)
        self.assertEqual(health_status.consecutive_failures, 0)
        self.assertTrue(health_status.is_healthy)
        self.assertIsNotNone(health_status.last_success_at)
    
    def test_consecutive_failures_trigger_failover(self):
        """测试连续失败触发故障转移"""
        # 记录连续失败，达到阈值
        for i in range(self.strategy.fail_threshold):
            self.failover_service.record_request_result(
                self.primary_provider,
                success=False,
                response_time=5.0,
                error_type='timeout'
            )
        
        # 验证已切换到备用提供商
        self.strategy.refresh_from_db()
        self.assertEqual(self.strategy.active_provider, self.fallback_provider1)
        self.assertIsNotNone(self.strategy.last_switch_at)
    
    def test_cooldown_period_prevents_rapid_switching(self):
        """测试冷却期防止快速切换"""
        # 先触发一次故障转移
        for i in range(self.strategy.fail_threshold):
            self.failover_service.record_request_result(
                self.primary_provider,
                success=False,
                response_time=5.0
            )
        
        # 验证已切换到备用提供商
        self.strategy.refresh_from_db()
        self.assertEqual(self.strategy.active_provider, self.fallback_provider1)
        
        # 在冷却期内尝试再次切换
        self.failover_service.record_request_result(
            self.fallback_provider1,
            success=False,
            response_time=5.0
        )
        
        # 验证没有再次切换
        self.strategy.refresh_from_db()
        self.assertEqual(self.strategy.active_provider, self.fallback_provider1)
    
    def test_recovery_after_consecutive_successes(self):
        """测试连续成功后恢复主提供商"""
        # 先切换到备用提供商
        for i in range(self.strategy.fail_threshold):
            self.failover_service.record_request_result(
                self.primary_provider,
                success=False,
                response_time=5.0
            )
        
        self.strategy.refresh_from_db()
        self.assertEqual(self.strategy.active_provider, self.fallback_provider1)
        
        # 等待冷却期结束
        self.strategy.last_switch_at = timezone.now() - timedelta(seconds=self.strategy.cooldown + 10)
        self.strategy.save()
        
        # 确保主提供商被标记为健康
        self.primary_provider.is_healthy = True
        self.primary_provider.save()
        
        # 记录主提供商连续成功
        for i in range(self.strategy.recovery_threshold):
            self.failover_service.record_request_result(
                self.primary_provider,
                success=True,
                response_time=1.0
            )
        
        # 验证已恢复到主提供商
        self.strategy.refresh_from_db()
        self.assertEqual(self.strategy.active_provider, self.primary_provider)
    
    def test_jitter_window_prevents_thrashing(self):
        """测试抖动窗口防止抖动"""
        # 先切换到备用提供商
        for i in range(self.strategy.fail_threshold):
            self.failover_service.record_request_result(
                self.primary_provider,
                success=False,
                response_time=5.0
            )
        
        self.strategy.refresh_from_db()
        self.assertEqual(self.strategy.active_provider, self.fallback_provider1)
        
        # 等待冷却期结束但仍在抖动窗口内
        # 抖动窗口现在是冷却期(60秒) + 抖动窗口(10秒) = 70秒，我们等待65秒，这样冷却期结束但仍在抖动窗口内
        self.strategy.last_switch_at = timezone.now() - timedelta(seconds=65)
        self.strategy.save()
        
        # 记录主提供商连续成功
        for i in range(self.strategy.recovery_threshold):
            self.failover_service.record_request_result(
                self.primary_provider,
                success=True,
                response_time=1.0
            )
        
        # 验证仍在备用提供商（抖动窗口内）
        self.strategy.refresh_from_db()
        self.assertEqual(self.strategy.active_provider, self.fallback_provider1)
    
    def test_priority_mode_selection(self):
        """测试优先级模式选择"""
        # 设置主提供商不健康
        self.primary_provider.is_healthy = False
        self.primary_provider.save()
        
        # 获取活跃提供商
        active_provider = self.failover_service.get_active_provider()
        
        # 应该选择优先级最高的备用提供商
        self.assertEqual(active_provider, self.fallback_provider1)
    
    def test_round_robin_mode_selection(self):
        """测试轮询模式选择"""
        # 切换到轮询模式
        self.strategy.strategy_mode = 'round_robin'
        self.strategy.save()
        
        # 多次获取活跃提供商，应该轮询
        providers = []
        for i in range(5):
            provider = self.failover_service._select_next_provider()
            providers.append(provider)
        
        # 验证轮询逻辑
        self.assertIn(self.primary_provider, providers)
        self.assertIn(self.fallback_provider1, providers)
        self.assertIn(self.fallback_provider2, providers)
    
    def test_health_summary(self):
        """测试健康状态摘要"""
        # 记录一些请求结果
        self.failover_service.record_request_result(
            self.primary_provider, success=True, response_time=1.0
        )
        self.failover_service.record_request_result(
            self.primary_provider, success=False, response_time=5.0
        )
        self.failover_service.record_request_result(
            self.fallback_provider1, success=True, response_time=2.0
        )
        
        # 获取健康摘要
        summary = self.failover_service.get_health_summary()
        
        # 验证摘要内容
        self.assertEqual(summary['strategy_id'], self.strategy.id)
        self.assertEqual(summary['strategy_name'], self.strategy.name)
        self.assertIsNotNone(summary['active_provider'])
        self.assertGreater(len(summary['providers']), 0)
        
        # 验证提供商信息
        for provider_info in summary['providers']:
            self.assertIn('provider_name', provider_info)
            self.assertIn('is_healthy', provider_info)
            self.assertIn('success_rate', provider_info)
            self.assertIn('consecutive_failures', provider_info)
            self.assertIn('consecutive_successes', provider_info)
    
    def test_provider_health_status_methods(self):
        """测试提供商健康状态方法"""
        # 创建健康状态记录
        health_status = ProviderHealthStatus.objects.create(
            strategy=self.strategy,
            provider=self.primary_provider,
            success_count=5,
            failure_count=2,
            consecutive_successes=3,
            consecutive_failures=0,
            is_healthy=True,
            is_available=True
        )
        
        # 测试成功率计算
        success_rate = health_status.get_success_rate()
        self.assertAlmostEqual(success_rate, 5/7, places=2)
        
        # 测试总请求数
        total_requests = health_status.get_total_requests()
        self.assertEqual(total_requests, 7)
        
        # 测试故障转移判断
        self.assertFalse(health_status.should_failover())
        
        # 测试恢复判断
        self.assertFalse(health_status.should_recover())
        
        # 设置连续失败达到阈值
        health_status.consecutive_failures = self.strategy.fail_threshold
        health_status.save()
        
        # 现在应该触发故障转移
        self.assertTrue(health_status.should_failover())
        
        # 设置连续成功达到阈值
        health_status.consecutive_successes = self.strategy.recovery_threshold
        health_status.consecutive_failures = 0
        health_status.save()
        
        # 现在应该触发恢复
        self.assertTrue(health_status.should_recover())
    
    def test_response_time_tracking(self):
        """测试响应时间跟踪"""
        health_status = ProviderHealthStatus.objects.create(
            strategy=self.strategy,
            provider=self.primary_provider
        )
        
        # 记录多次请求的响应时间
        response_times = [1.0, 2.0, 0.5, 3.0, 1.5]
        for rt in response_times:
            health_status.record_success(rt)
        
        # 验证响应时间统计
        self.assertIsNotNone(health_status.avg_response_time)
        self.assertIsNotNone(health_status.min_response_time)
        self.assertIsNotNone(health_status.max_response_time)
        
        # 验证最小和最大响应时间
        self.assertEqual(health_status.min_response_time, 0.5)
        self.assertEqual(health_status.max_response_time, 3.0)
        
        # 验证平均响应时间（近似）
        expected_avg = sum(response_times) / len(response_times)
        self.assertAlmostEqual(health_status.avg_response_time, expected_avg, places=1)
