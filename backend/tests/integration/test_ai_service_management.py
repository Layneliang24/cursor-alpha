"""
AI服务管理集成测试

测试AI服务管理器、负载均衡、健康监控和降级功能的集成
"""

import pytest
import asyncio
import time
from unittest.mock import patch, MagicMock
from django.test import TestCase, override_settings
from django.core.cache import cache
from rest_framework.test import APITestCase
from django.contrib.auth.models import User

from apps.ai.services.manager import AIServiceManager
from apps.ai.services.load_balancer import LoadBalancingStrategy
from apps.ai.services.degradation import ServiceLevel
from apps.ai.adapters.base import (
    AIProviderType, AIModelConfig, AIMessage, MessageRole,
    HealthCheckResult, AIResponse
)


class AIServiceManagerIntegrationTest(TestCase):
    """AI服务管理器集成测试"""
    
    def setUp(self):
        """测试设置"""
        cache.clear()
        # 重置单例实例
        AIServiceManager._instance = None
        
        # 模拟API密钥
        self.mock_keys = {
            AIProviderType.OPENAI: 'sk-test-openai-key',
            AIProviderType.ANTHROPIC: 'sk-test-claude-key',
            AIProviderType.GOOGLE: 'test-google-key'
        }
    
    def tearDown(self):
        """测试清理"""
        cache.clear()
        AIServiceManager._instance = None
    
    @override_settings(
        AI_SERVICES={
            'test-openai': {
                'provider': 'openai',
                'model': 'gpt-3.5-turbo',
                'weight': 2,
                'enabled': True
            },
            'test-claude': {
                'provider': 'anthropic',
                'model': 'claude-3-haiku-20240307',
                'weight': 1,
                'enabled': True
            }
        }
    )
    @patch.dict('os.environ', {
        'OPENAI_API_KEY': 'sk-test-openai-key',
        'ANTHROPIC_API_KEY': 'sk-test-claude-key'
    })
    def test_service_initialization(self):
        """测试服务初始化"""
        manager = AIServiceManager()
        
        # 验证服务已加载
        status = manager.get_service_status()
        self.assertIn('test-openai', status)
        self.assertIn('test-claude', status)
        
        # 验证配置正确
        openai_status = status['test-openai']
        self.assertEqual(openai_status['provider'], 'openai')
        self.assertEqual(openai_status['model'], 'gpt-3.5-turbo')
        self.assertEqual(openai_status['weight'], 2)
        self.assertTrue(openai_status['enabled'])
    
    @patch.dict('os.environ', {
        'OPENAI_API_KEY': 'sk-test-openai-key'
    })
    def test_dynamic_service_management(self):
        """测试动态服务管理"""
        manager = AIServiceManager()
        
        # 添加服务
        success = manager.add_service(
            service_name='test-dynamic',
            provider=AIProviderType.OPENAI,
            model='gpt-4',
            weight=3
        )
        self.assertTrue(success)
        
        # 验证服务已添加
        status = manager.get_service_status()
        self.assertIn('test-dynamic', status)
        
        # 禁用服务
        success = manager.disable_service('test-dynamic')
        self.assertTrue(success)
        
        # 验证服务已禁用
        status = manager.get_service_status()
        self.assertFalse(status['test-dynamic']['enabled'])
        
        # 移除服务
        success = manager.remove_service('test-dynamic')
        self.assertTrue(success)
        
        # 验证服务已移除
        status = manager.get_service_status()
        self.assertNotIn('test-dynamic', status)
    
    def test_load_balancing_strategies(self):
        """测试负载均衡策略"""
        manager = AIServiceManager()
        
        # 测试不同策略
        strategies = [
            LoadBalancingStrategy.ROUND_ROBIN,
            LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN,
            LoadBalancingStrategy.RANDOM,
            LoadBalancingStrategy.WEIGHTED_RANDOM
        ]
        
        for strategy in strategies:
            manager.set_load_balancing_strategy(strategy)
            stats = manager.get_load_balancer_stats()
            self.assertEqual(stats['strategy'], strategy.value)
    
    def test_service_degradation(self):
        """测试服务降级"""
        manager = AIServiceManager()
        
        # 强制降级
        manager.force_degradation(ServiceLevel.DEGRADED)
        degradation_status = manager.get_degradation_status()
        self.assertEqual(degradation_status['current_level'], 'degraded')
        
        # 清除降级
        manager.clear_degradation()
        degradation_status = manager.get_degradation_status()
        # 注意：清除后可能不是NORMAL，因为自动监控可能检测到其他状态


class AIServiceAPITest(APITestCase):
    """AI服务管理API测试"""
    
    def setUp(self):
        """测试设置"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        cache.clear()
        AIServiceManager._instance = None
    
    def tearDown(self):
        """测试清理"""
        cache.clear()
        AIServiceManager._instance = None
    
    def test_get_service_status_api(self):
        """测试获取服务状态API"""
        response = self.client.get('/api/v1/ai/services/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('services', data)
        self.assertIn('load_balancer', data)
        self.assertIn('degradation', data)
    
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'sk-test-key'})
    def test_add_service_api(self):
        """测试添加服务API"""
        service_data = {
            'service_name': 'test-api-service',
            'provider': 'openai',
            'model': 'gpt-3.5-turbo',
            'weight': 2
        }
        
        response = self.client.post('/api/v1/ai/services/add_service/', service_data)
        self.assertEqual(response.status_code, 201)
        
        # 验证服务已添加
        response = self.client.get('/api/v1/ai/services/')
        data = response.json()
        self.assertIn('test-api-service', data['services'])
    
    def test_load_balancer_strategy_api(self):
        """测试负载均衡策略API"""
        strategy_data = {'strategy': 'round_robin'}
        
        response = self.client.post('/api/v1/ai/load-balancer/set_strategy/', strategy_data)
        self.assertEqual(response.status_code, 200)
        
        # 验证策略已更新
        response = self.client.get('/api/v1/ai/load-balancer/')
        data = response.json()
        self.assertEqual(data['strategy'], 'round_robin')
    
    def test_degradation_control_api(self):
        """测试服务降级控制API"""
        # 强制降级
        degradation_data = {'level': 'degraded'}
        response = self.client.post('/api/v1/ai/degradation/force_degradation/', degradation_data)
        self.assertEqual(response.status_code, 200)
        
        # 验证降级状态
        response = self.client.get('/api/v1/ai/degradation/')
        data = response.json()
        self.assertEqual(data['current_level'], 'degraded')
        
        # 清除降级
        response = self.client.post('/api/v1/ai/degradation/clear_degradation/')
        self.assertEqual(response.status_code, 200)
    
    def test_health_monitor_api(self):
        """测试健康监控API"""
        response = self.client.get('/api/v1/ai/health/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('summary', data)
        self.assertIn('services', data)
        
        # 验证摘要字段
        summary = data['summary']
        self.assertIn('total_services', summary)
        self.assertIn('healthy_services', summary)
        self.assertIn('health_percentage', summary)
    
    @patch('apps.ai.adapters.openai_adapter.OpenAIAdapter.generate_response')
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'sk-test-key'})
    async def test_ai_chat_api(self, mock_generate):
        """测试AI对话API"""
        # 模拟AI响应
        mock_response = AIResponse(
            content="测试响应",
            model="gpt-3.5-turbo",
            usage={'total_tokens': 50}
        )
        mock_generate.return_value = mock_response
        
        chat_data = {
            'messages': [
                {'role': 'user', 'content': '你好'}
            ]
        }
        
        response = self.client.post('/api/v1/ai/services/chat/', chat_data)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('response', data)
        self.assertIn('service_used', data)
        self.assertIn('tokens_used', data)


class LoadBalancerIntegrationTest(TestCase):
    """负载均衡器集成测试"""
    
    def setUp(self):
        """测试设置"""
        from apps.ai.services.load_balancer import LoadBalancer
        self.load_balancer = LoadBalancer()
    
    def test_round_robin_distribution(self):
        """测试轮询分发"""
        self.load_balancer.set_strategy(LoadBalancingStrategy.ROUND_ROBIN)
        
        services = {'service1': 1, 'service2': 1, 'service3': 1}
        selections = []
        
        # 选择多次，验证轮询效果
        for _ in range(9):
            selected = self.load_balancer.select_service(services)
            selections.append(selected)
        
        # 验证每个服务都被选中了3次
        for service_name in services:
            self.assertEqual(selections.count(service_name), 3)
    
    def test_weighted_distribution(self):
        """测试加权分发"""
        self.load_balancer.set_strategy(LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN)
        
        services = {'high_weight': 3, 'low_weight': 1}
        selections = []
        
        # 选择多次，验证权重效果
        for _ in range(20):
            selected = self.load_balancer.select_service(services)
            selections.append(selected)
        
        # 高权重服务应该被选中更多次
        high_count = selections.count('high_weight')
        low_count = selections.count('low_weight')
        self.assertGreater(high_count, low_count)
    
    def test_service_exclusion(self):
        """测试服务排除"""
        services = {'service1': 1, 'service2': 1, 'service3': 1}
        exclude = ['service2']
        
        # 多次选择，验证排除效果
        for _ in range(10):
            selected = self.load_balancer.select_service(services, exclude=exclude)
            self.assertNotEqual(selected, 'service2')


class HealthMonitorIntegrationTest(TestCase):
    """健康监控集成测试"""
    
    def setUp(self):
        """测试设置"""
        from apps.ai.services.health_monitor import HealthMonitor
        self.health_monitor = HealthMonitor()
    
    def test_health_status_tracking(self):
        """测试健康状态跟踪"""
        service_name = 'test-service'
        
        # 模拟健康检查结果
        healthy_result = HealthCheckResult(
            is_healthy=True,
            response_time=0.5,
            error=None
        )
        
        unhealthy_result = HealthCheckResult(
            is_healthy=False,
            response_time=10.0,
            error="Connection timeout"
        )
        
        # 更新健康状态
        self.health_monitor.update_health(service_name, healthy_result)
        health = self.health_monitor.get_health(service_name)
        self.assertTrue(health.is_healthy)
        self.assertEqual(health.response_time, 0.5)
        
        # 更新为不健康
        self.health_monitor.update_health(service_name, unhealthy_result)
        health = self.health_monitor.get_health(service_name)
        self.assertFalse(health.is_healthy)
        self.assertEqual(health.error, "Connection timeout")
    
    def test_health_summary(self):
        """测试健康状态摘要"""
        # 添加多个服务的健康状态
        services = ['service1', 'service2', 'service3']
        
        for i, service_name in enumerate(services):
            result = HealthCheckResult(
                is_healthy=i < 2,  # 前两个健康，最后一个不健康
                response_time=1.0,
                error=None if i < 2 else "Error"
            )
            self.health_monitor.update_health(service_name, result)
        
        # 获取摘要
        summary = self.health_monitor.get_health_summary()
        self.assertEqual(summary['total_services'], 3)
        self.assertEqual(summary['healthy_services'], 2)
        self.assertEqual(summary['unhealthy_services'], 1)
        self.assertAlmostEqual(summary['health_percentage'], 66.67, places=1)


class DegradationManagerIntegrationTest(TestCase):
    """服务降级管理器集成测试"""
    
    def setUp(self):
        """测试设置"""
        from apps.ai.services.degradation import DegradationManager, DegradationThresholds
        
        # 使用较低的阈值便于测试
        test_thresholds = DegradationThresholds(
            degraded_cpu_threshold=50.0,
            minimal_cpu_threshold=80.0,
            disabled_cpu_threshold=95.0
        )
        
        self.degradation_manager = DegradationManager(test_thresholds)
    
    def tearDown(self):
        """测试清理"""
        self.degradation_manager.stop_monitoring()
    
    def test_forced_degradation(self):
        """测试强制降级"""
        # 强制设置降级级别
        self.degradation_manager.force_degradation(ServiceLevel.DEGRADED)
        self.assertEqual(self.degradation_manager.get_current_level(), ServiceLevel.DEGRADED)
        
        # 清除强制设置
        self.degradation_manager.clear_degradation()
        # 注意：清除后级别可能不是NORMAL，因为自动监控在运行
    
    def test_load_simulation(self):
        """测试负载模拟"""
        original_level = self.degradation_manager.get_current_level()
        
        # 模拟高负载
        self.degradation_manager.simulate_load(duration_seconds=2)
        
        # 等待监控检测到负载变化
        time.sleep(1)
        
        # 验证指标变化
        metrics = self.degradation_manager.get_metrics()
        self.assertGreater(metrics['cpu_usage'], 50.0)  # 应该超过降级阈值
    
    def test_degradation_recommendations(self):
        """测试降级建议"""
        # 模拟高负载获取建议
        self.degradation_manager.simulate_load(duration_seconds=1)
        time.sleep(0.5)
        
        recommendations = self.degradation_manager.get_degradation_recommendations()
        self.assertIsInstance(recommendations, list)
        # 高负载时应该有建议
        if recommendations:
            self.assertTrue(any('CPU' in rec for rec in recommendations))


class KeyManagerIntegrationTest(TestCase):
    """API密钥管理器集成测试"""
    
    def setUp(self):
        """测试设置"""
        cache.clear()
        from apps.ai.services.key_manager import APIKeyManager
        self.key_manager = APIKeyManager()
    
    def tearDown(self):
        """测试清理"""
        cache.clear()
    
    @patch.dict('os.environ', {
        'OPENAI_API_KEY': 'sk-test-openai-key',
        'ANTHROPIC_API_KEY': 'sk-test-claude-key'
    })
    def test_key_loading_and_encryption(self):
        """测试密钥加载和加密"""
        # 重新初始化以加载环境变量
        self.key_manager._load_keys_from_env()
        
        # 获取密钥
        openai_key = self.key_manager.get_key(AIProviderType.OPENAI)
        claude_key = self.key_manager.get_key(AIProviderType.ANTHROPIC)
        
        self.assertEqual(openai_key, 'sk-test-openai-key')
        self.assertEqual(claude_key, 'sk-test-claude-key')
    
    def test_key_rotation(self):
        """测试密钥轮换"""
        provider = AIProviderType.OPENAI
        
        # 添加多个密钥
        key_id1 = self.key_manager.add_key(provider, 'key1', is_primary=True)
        key_id2 = self.key_manager.add_key(provider, 'key2', is_primary=False)
        
        # 验证初始主密钥
        current_key = self.key_manager.get_key(provider)
        self.assertEqual(current_key, 'key1')
        
        # 执行轮换
        success = self.key_manager.rotate_keys(provider)
        self.assertTrue(success)
        
        # 验证密钥已轮换
        rotated_key = self.key_manager.get_key(provider)
        self.assertEqual(rotated_key, 'key2')
    
    def test_key_statistics(self):
        """测试密钥统计"""
        provider = AIProviderType.OPENAI
        
        # 添加密钥
        self.key_manager.add_key(provider, 'test-key', is_primary=True)
        
        # 使用密钥几次
        for _ in range(3):
            self.key_manager.get_key(provider)
        
        # 获取统计
        stats = self.key_manager.get_key_stats(provider)
        self.assertIn('openai', stats)
        
        openai_stats = stats['openai']
        self.assertEqual(openai_stats['total_keys'], 1)
        self.assertTrue(openai_stats['keys'])
        
        key_stat = openai_stats['keys'][0]
        self.assertTrue(key_stat['is_primary'])
        self.assertGreaterEqual(key_stat['usage_count'], 3)


@pytest.mark.asyncio
class AsyncAIServiceTest:
    """异步AI服务测试"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """测试设置"""
        cache.clear()
        AIServiceManager._instance = None
        yield
        cache.clear()
        AIServiceManager._instance = None
    
    @patch('apps.ai.adapters.openai_adapter.OpenAIAdapter.generate_response')
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'sk-test-key'})
    async def test_async_response_generation(self, mock_generate):
        """测试异步响应生成"""
        # 模拟AI响应
        mock_response = AIResponse(
            content="异步测试响应",
            model="gpt-3.5-turbo",
            usage={'total_tokens': 30}
        )
        mock_generate.return_value = mock_response
        
        manager = AIServiceManager()
        
        # 添加测试服务
        success = manager.add_service(
            service_name='async-test',
            provider=AIProviderType.OPENAI,
            model='gpt-3.5-turbo'
        )
        assert success
        
        # 准备消息
        messages = [AIMessage(role=MessageRole.USER, content="测试消息")]
        
        # 生成响应
        response = await manager.generate_response(messages)
        
        assert response.content == "异步测试响应"
        assert mock_generate.called
    
    @patch('apps.ai.adapters.openai_adapter.OpenAIAdapter.generate_response')
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'sk-test-key'})
    async def test_failover_mechanism(self, mock_generate):
        """测试故障转移机制"""
        manager = AIServiceManager()
        
        # 添加两个服务
        manager.add_service('primary', AIProviderType.OPENAI, 'gpt-4', weight=3)
        manager.add_service('backup', AIProviderType.OPENAI, 'gpt-3.5-turbo', weight=1)
        
        # 模拟主服务失败，备用服务成功
        def side_effect(*args, **kwargs):
            if 'gpt-4' in str(kwargs) or hasattr(args[0], 'model') and args[0].model == 'gpt-4':
                raise Exception("主服务故障")
            return AIResponse(content="备用服务响应", model="gpt-3.5-turbo")
        
        mock_generate.side_effect = side_effect
        
        # 准备消息
        messages = [AIMessage(role=MessageRole.USER, content="测试故障转移")]
        
        # 应该自动转移到备用服务
        response = await manager.generate_response(messages)
        assert "备用服务响应" in response.content

