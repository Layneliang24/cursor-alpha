"""
基本模型单元测试
"""
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.ai.config_models import (
    AIProvider, APIKey, AIModel, ModelConfig, 
    TokenUsage, UsageQuota, FailoverStrategy
)

User = get_user_model()


class AIProviderModelTest(TestCase):
    """AI提供商模型测试"""
    
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_provider(self):
        """测试创建提供商"""
        provider = AIProvider.objects.create(
            name='test_provider',
            provider_type='openai',
            display_name='Test Provider',
            base_url='https://api.openai.com',
            created_by=self.user
        )
        
        self.assertEqual(provider.name, 'test_provider')
        self.assertEqual(provider.provider_type, 'openai')
        self.assertEqual(provider.display_name, 'Test Provider')
        self.assertTrue(provider.is_active)
        self.assertFalse(provider.is_healthy)
    
    def test_provider_str_representation(self):
        """测试提供商字符串表示"""
        provider = AIProvider.objects.create(
            name='test_provider',
            provider_type='anthropic',
            display_name='Test Provider',
            base_url='https://api.anthropic.com',
            created_by=self.user
        )
        
        self.assertEqual(str(provider), 'Test Provider (anthropic)')
    
    def test_provider_health_update(self):
        """测试提供商健康状态更新"""
        provider = AIProvider.objects.create(
            name='test_provider',
            provider_type='openai',
            display_name='Test Provider',
            base_url='https://api.openai.com',
            created_by=self.user
        )
        
        # 更新健康状态
        provider.update_health_status(True, 0.5)
        provider.refresh_from_db()
        
        self.assertTrue(provider.is_healthy)
        self.assertEqual(provider.avg_response_time, 0.5)


class APIKeyModelTest(TestCase):
    """API密钥模型测试"""
    
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.provider = AIProvider.objects.create(
            name='test_provider',
            provider_type='openai',
            display_name='Test Provider',
            base_url='https://api.openai.com',
            created_by=self.user
        )
    
    def test_create_api_key(self):
        """测试创建API密钥"""
        api_key = APIKey.objects.create(
            provider=self.provider,
            user=self.user,
            name='Test Key',
            encrypted_key='encrypted_key_value'
        )
        
        self.assertEqual(api_key.name, 'Test Key')
        self.assertEqual(api_key.provider, self.provider)
        self.assertEqual(api_key.user, self.user)
        self.assertTrue(api_key.is_active)
        self.assertFalse(api_key.is_default)
    
    def test_api_key_str_representation(self):
        """测试API密钥字符串表示"""
        api_key = APIKey.objects.create(
            provider=self.provider,
            user=self.user,
            name='Test Key',
            encrypted_key='encrypted_key_value'
        )
        
        self.assertEqual(str(api_key), 'Test Key (test_provider)')


class AIModelModelTest(TestCase):
    """AI模型模型测试"""
    
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.provider = AIProvider.objects.create(
            name='test_provider',
            provider_type='openai',
            display_name='Test Provider',
            base_url='https://api.openai.com',
            created_by=self.user
        )
    
    def test_create_model(self):
        """测试创建AI模型"""
        model = AIModel.objects.create(
            name='GPT-4',
            provider=self.provider,
            model_id='gpt-4',
            max_tokens=4096,
            temperature=0.7,
            created_by=self.user
        )
        
        self.assertEqual(model.name, 'GPT-4')
        self.assertEqual(model.model_id, 'gpt-4')
        self.assertEqual(model.provider, self.provider)
        self.assertEqual(model.max_tokens, 4096)
        self.assertEqual(model.temperature, 0.7)
    
    def test_model_str_representation(self):
        """测试AI模型字符串表示"""
        model = AIModel.objects.create(
            name='GPT-4',
            provider=self.provider,
            model_id='gpt-4',
            max_tokens=4096,
            created_by=self.user
        )
        
        self.assertEqual(str(model), 'GPT-4 (gpt-4)')


class ModelConfigModelTest(TestCase):
    """模型配置模型测试"""
    
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.provider = AIProvider.objects.create(
            name='test_provider',
            provider_type='openai',
            display_name='Test Provider',
            base_url='https://api.openai.com',
            created_by=self.user
        )
        
        self.model = AIModel.objects.create(
            name='GPT-4',
            provider=self.provider,
            model_id='gpt-4',
            max_tokens=4096,
            created_by=self.user
        )
    
    def test_create_model_config(self):
        """测试创建模型配置"""
        config = ModelConfig.objects.create(
            name='Default Config',
            model=self.model,
            temperature=0.7,
            max_tokens=4096,
            top_p=0.9,
            created_by=self.user
        )
        
        self.assertEqual(config.name, 'Default Config')
        self.assertEqual(config.model, self.model)
        self.assertEqual(config.temperature, 0.7)
        self.assertEqual(config.max_tokens, 4096)
        self.assertEqual(config.top_p, 0.9)
    
    def test_config_str_representation(self):
        """测试模型配置字符串表示"""
        config = ModelConfig.objects.create(
            name='Default Config',
            model=self.model,
            temperature=0.7,
            max_tokens=4096,
            created_by=self.user
        )
        
        self.assertEqual(str(config), 'Default Config (GPT-4)')


class TokenUsageModelTest(TestCase):
    """Token使用量模型测试"""
    
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.provider = AIProvider.objects.create(
            name='test_provider',
            provider_type='openai',
            display_name='Test Provider',
            base_url='https://api.openai.com',
            created_by=self.user
        )
    
    def test_create_token_usage(self):
        """测试创建Token使用量记录"""
        usage = TokenUsage.objects.create(
            user=self.user,
            provider=self.provider,
            model_name='gpt-4',
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            cost=0.003
        )
        
        self.assertEqual(usage.user, self.user)
        self.assertEqual(usage.provider, self.provider)
        self.assertEqual(usage.model_name, 'gpt-4')
        self.assertEqual(usage.prompt_tokens, 100)
        self.assertEqual(usage.completion_tokens, 50)
        self.assertEqual(usage.total_tokens, 150)
        self.assertEqual(usage.cost, 0.003)
    
    def test_usage_str_representation(self):
        """测试Token使用量字符串表示"""
        usage = TokenUsage.objects.create(
            user=self.user,
            provider=self.provider,
            model_name='gpt-4',
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            cost=0.003
        )
        
        self.assertEqual(str(usage), 'testuser - gpt-4 (150 tokens)')


class UsageQuotaModelTest(TestCase):
    """使用配额模型测试"""
    
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.provider = AIProvider.objects.create(
            name='test_provider',
            provider_type='openai',
            display_name='Test Provider',
            base_url='https://api.openai.com',
            created_by=self.user
        )
    
    def test_create_usage_quota(self):
        """测试创建使用配额"""
        quota = UsageQuota.objects.create(
            user=self.user,
            provider=self.provider,
            quota_type='daily',
            limit=1000000,
            used=500000,
            reset_date='2024-01-15'
        )
        
        self.assertEqual(quota.user, self.user)
        self.assertEqual(quota.provider, self.provider)
        self.assertEqual(quota.quota_type, 'daily')
        self.assertEqual(quota.limit, 1000000)
        self.assertEqual(quota.used, 500000)
        self.assertEqual(quota.reset_date, '2024-01-15')
    
    def test_quota_str_representation(self):
        """测试使用配额字符串表示"""
        quota = UsageQuota.objects.create(
            user=self.user,
            provider=self.provider,
            quota_type='daily',
            limit=1000000,
            used=500000,
            reset_date='2024-01-15'
        )
        
        self.assertEqual(str(quota), 'testuser - daily quota (500000/1000000)')


class FailoverStrategyModelTest(TestCase):
    """故障转移策略模型测试"""
    
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.provider1 = AIProvider.objects.create(
            name='primary_provider',
            provider_type='openai',
            display_name='Primary Provider',
            base_url='https://api.openai.com',
            created_by=self.user
        )
        
        self.provider2 = AIProvider.objects.create(
            name='backup_provider',
            provider_type='anthropic',
            display_name='Backup Provider',
            base_url='https://api.anthropic.com',
            created_by=self.user
        )
    
    def test_create_failover_strategy(self):
        """测试创建故障转移策略"""
        strategy = FailoverStrategy.objects.create(
            name='Test Strategy',
            priority=1,
            providers=[self.provider1.id, self.provider2.id],
            created_by=self.user
        )
        
        self.assertEqual(strategy.name, 'Test Strategy')
        self.assertEqual(strategy.priority, 1)
        self.assertEqual(len(strategy.providers), 2)
        self.assertIn(self.provider1.id, strategy.providers)
        self.assertIn(self.provider2.id, strategy.providers)
    
    def test_strategy_str_representation(self):
        """测试故障转移策略字符串表示"""
        strategy = FailoverStrategy.objects.create(
            name='Test Strategy',
            priority=1,
            providers=[self.provider1.id, self.provider2.id],
            created_by=self.user
        )
        
        self.assertEqual(str(strategy), 'Test Strategy (Priority: 1)')


class ModelRelationshipsTest(TestCase):
    """模型关系测试"""
    
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.provider = AIProvider.objects.create(
            name='test_provider',
            provider_type='openai',
            display_name='Test Provider',
            base_url='https://api.openai.com',
            created_by=self.user
        )
        
        self.api_key = APIKey.objects.create(
            provider=self.provider,
            user=self.user,
            name='Test Key',
            encrypted_key='encrypted_key_value'
        )
        
        self.model = AIModel.objects.create(
            name='GPT-4',
            provider=self.provider,
            model_id='gpt-4',
            max_tokens=4096,
            created_by=self.user
        )
        
        self.config = ModelConfig.objects.create(
            name='Default Config',
            model=self.model,
            temperature=0.7,
            max_tokens=4096,
            created_by=self.user
        )
    
    def test_provider_api_keys_relationship(self):
        """测试提供商与API密钥的关系"""
        self.assertEqual(self.provider.api_keys.count(), 1)
        self.assertEqual(self.provider.api_keys.first(), self.api_key)
    
    def test_provider_models_relationship(self):
        """测试提供商与模型的关系"""
        self.assertEqual(self.provider.ai_models.count(), 1)
        self.assertEqual(self.provider.ai_models.first(), self.model)
    
    def test_model_configs_relationship(self):
        """测试模型与配置的关系"""
        self.assertEqual(self.model.model_configs.count(), 1)
        self.assertEqual(self.model.model_configs.first(), self.config)
    
    def test_user_api_keys_relationship(self):
        """测试用户与API密钥的关系"""
        self.assertEqual(self.user.api_keys.count(), 1)
        self.assertEqual(self.user.api_keys.first(), self.api_key)
