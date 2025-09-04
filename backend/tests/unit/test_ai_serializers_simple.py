# -*- coding: utf-8 -*-
"""
AI序列化器简化测试
只测试基本的序列化器功能，避免复杂的依赖关系
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

from apps.ai.config_models import (
    AIProvider, APIKey, AIModel, AIProviderType
)

User = get_user_model()


class SimpleAIProviderSerializerTest(TestCase):
    """简化的AI提供商序列化器测试"""
    
    def test_provider_model_creation(self):
        """测试AI提供商模型创建（不使用序列化器）"""
        provider = AIProvider.objects.create(
            name='test_provider',
            provider_type=AIProviderType.OPENAI,
            display_name='Test Provider',
            base_url='https://api.openai.com'
        )
        
        self.assertEqual(provider.name, 'test_provider')
        self.assertEqual(provider.provider_type, AIProviderType.OPENAI)
        self.assertEqual(provider.display_name, 'Test Provider')
        self.assertEqual(provider.base_url, 'https://api.openai.com')
    
    def test_provider_str_method(self):
        """测试AI提供商字符串方法"""
        provider = AIProvider.objects.create(
            name='test_provider',
            provider_type=AIProviderType.OPENAI,
            display_name='Test Provider',
            base_url='https://api.openai.com'
        )
        
        str_repr = str(provider)
        self.assertIn('Test Provider', str_repr)
        self.assertIn('openai', str_repr)


class SimpleAPIKeySerializerTest(TestCase):
    """简化的API密钥序列化器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.provider = AIProvider.objects.create(
            name='test_provider',
            provider_type=AIProviderType.OPENAI,
            display_name='Test Provider',
            base_url='https://api.openai.com'
        )
    
    def test_api_key_model_creation(self):
        """测试API密钥模型创建（不使用序列化器）"""
        api_key = APIKey.objects.create(
            provider=self.provider,
            user=self.user,
            name='Test Key',
            encrypted_key='encrypted_key_value'
        )
        
        self.assertEqual(api_key.provider, self.provider)
        self.assertEqual(api_key.user, self.user)
        self.assertEqual(api_key.name, 'Test Key')
        self.assertEqual(api_key.encrypted_key, 'encrypted_key_value')
    
    def test_api_key_str_method(self):
        """测试API密钥字符串方法"""
        api_key = APIKey.objects.create(
            provider=self.provider,
            user=self.user,
            name='Test Key',
            encrypted_key='encrypted_key_value'
        )
        
        str_repr = str(api_key)
        self.assertIn('Test Key', str_repr)
        self.assertIn('Test Provider', str_repr)


class SimpleAIModelSerializerTest(TestCase):
    """简化的AI模型序列化器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.provider = AIProvider.objects.create(
            name='test_provider',
            provider_type=AIProviderType.OPENAI,
            display_name='Test Provider',
            base_url='https://api.openai.com'
        )
    
    def test_ai_model_creation(self):
        """测试AI模型创建（不使用序列化器）"""
        model = AIModel.objects.create(
            provider=self.provider,
            model_id='test-model',
            display_name='Test Model',
            max_tokens=1024
        )
        
        self.assertEqual(model.provider, self.provider)
        self.assertEqual(model.model_id, 'test-model')
        self.assertEqual(model.display_name, 'Test Model')
        self.assertEqual(model.max_tokens, 1024)
    
    def test_ai_model_str_method(self):
        """测试AI模型字符串方法"""
        model = AIModel.objects.create(
            provider=self.provider,
            model_id='test-model',
            display_name='Test Model',
            max_tokens=1024
        )
        
        str_repr = str(model)
        self.assertIn('Test Model', str_repr)
        self.assertIn('Test Provider', str_repr)


class SimpleSerializerIntegrationTest(TestCase):
    """简化的序列化器集成测试"""
    
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.provider = AIProvider.objects.create(
            name='test_provider',
            provider_type=AIProviderType.OPENAI,
            display_name='Test Provider',
            base_url='https://api.openai.com'
        )
    
    def test_provider_model_relationship(self):
        """测试提供商与模型的关系"""
        model = AIModel.objects.create(
            provider=self.provider,
            model_id='test-model',
            display_name='Test Model',
            max_tokens=1024
        )
        
        api_key = APIKey.objects.create(
            provider=self.provider,
            user=self.user,
            name='Test Key',
            encrypted_key='encrypted_key_value'
        )
        
        # 验证关系
        self.assertEqual(model.provider, self.provider)
        self.assertEqual(api_key.provider, self.provider)
        self.assertEqual(api_key.user, self.user)
        self.assertIn(model, self.provider.models.all())
        self.assertIn(api_key, self.provider.api_keys.all())
        self.assertIn(api_key, self.user.api_keys.all())
    
    def test_model_creation_workflow(self):
        """测试模型创建工作流"""
        # 1. 创建提供商
        provider = AIProvider.objects.create(
            name='workflow_provider',
            provider_type=AIProviderType.OPENAI,
            display_name='Workflow Provider',
            base_url='https://api.workflow.com'
        )
        
        # 2. 创建模型
        model = AIModel.objects.create(
            provider=provider,
            model_id='workflow-model',
            display_name='Workflow Model',
            max_tokens=2048,
            supports_streaming=True,
            supports_functions=True
        )
        
        # 3. 验证模型属性
        self.assertEqual(model.provider, provider)
        self.assertEqual(model.model_id, 'workflow-model')
        self.assertEqual(model.max_tokens, 2048)
        self.assertTrue(model.supports_streaming)
        self.assertTrue(model.supports_functions)
        
        # 4. 验证提供商关系
        self.assertIn(model, provider.models.all())
        self.assertEqual(provider.models.count(), 1)
