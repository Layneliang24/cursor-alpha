# -*- coding: utf-8 -*-
"""
AI应用核心模型简化测试
只测试基本的模型创建功能，避免复杂的依赖关系
"""

import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from decimal import Decimal
from datetime import datetime, timedelta

from apps.ai.config_models import (
    AIProvider, APIKey, AIModel, AIProviderType
)

User = get_user_model()


class SimpleAIProviderTest(TestCase):
    """简化的AI提供商测试"""
    
    def test_create_ai_provider_basic(self):
        """测试创建AI提供商（基础功能）"""
        provider = AIProvider.objects.create(
            name='openai_test',
            provider_type=AIProviderType.OPENAI,
            display_name='OpenAI Test',
            base_url='https://api.openai.com'
        )
        
        self.assertEqual(provider.name, 'openai_test')
        self.assertEqual(provider.provider_type, AIProviderType.OPENAI)
        self.assertEqual(provider.display_name, 'OpenAI Test')
        self.assertEqual(provider.base_url, 'https://api.openai.com')
        self.assertTrue(provider.is_active)
        self.assertFalse(provider.is_healthy)
        self.assertEqual(str(provider), 'OpenAI Test (openai)')
    
    def test_ai_provider_unique_name(self):
        """测试AI提供商名称唯一性"""
        AIProvider.objects.create(
            name='test_provider',
            provider_type=AIProviderType.OPENAI,
            display_name='Test Provider',
            base_url='https://api.test.com'
        )
        
        with self.assertRaises(IntegrityError):
            AIProvider.objects.create(
                name='test_provider',
                provider_type=AIProviderType.ANTHROPIC,
                display_name='Another Test Provider',
                base_url='https://api.another.com'
            )
    
    def test_ai_provider_different_types(self):
        """测试不同AI提供商类型"""
        # OpenAI
        openai_provider = AIProvider.objects.create(
            name='openai',
            provider_type=AIProviderType.OPENAI,
            display_name='OpenAI',
            base_url='https://api.openai.com'
        )
        
        # Anthropic
        anthropic_provider = AIProvider.objects.create(
            name='anthropic',
            provider_type=AIProviderType.ANTHROPIC,
            display_name='Anthropic',
            base_url='https://api.anthropic.com'
        )
        
        # Google
        google_provider = AIProvider.objects.create(
            name='google',
            provider_type=AIProviderType.GOOGLE,
            display_name='Google',
            base_url='https://generativelanguage.googleapis.com'
        )
        
        self.assertEqual(openai_provider.provider_type, AIProviderType.OPENAI)
        self.assertEqual(anthropic_provider.provider_type, AIProviderType.ANTHROPIC)
        self.assertEqual(google_provider.provider_type, AIProviderType.GOOGLE)


class SimpleAIModelTest(TestCase):
    """简化的AI模型测试"""
    
    def setUp(self):
        """测试前准备"""
        self.provider = AIProvider.objects.create(
            name='test_provider',
            provider_type=AIProviderType.OPENAI,
            display_name='Test Provider',
            base_url='https://api.test.com'
        )
    
    def test_create_ai_model_basic(self):
        """测试创建AI模型（基础功能）"""
        model = AIModel.objects.create(
            provider=self.provider,
            model_id='gpt-4',
            display_name='GPT-4',
            max_tokens=8192
        )
        
        self.assertEqual(model.provider, self.provider)
        self.assertEqual(model.model_id, 'gpt-4')
        self.assertEqual(model.display_name, 'GPT-4')
        self.assertEqual(model.max_tokens, 8192)
        self.assertTrue(model.supports_streaming)
        self.assertFalse(model.supports_functions)
        self.assertFalse(model.supports_vision)
        self.assertTrue(model.is_active)
        self.assertFalse(model.is_recommended)
        self.assertEqual(str(model), 'GPT-4 (Test Provider)')
    
    def test_ai_model_provider_relationship(self):
        """测试AI模型与提供商的关系"""
        model = AIModel.objects.create(
            provider=self.provider,
            model_id='test-model',
            display_name='Test Model',
            max_tokens=1024
        )
        
        self.assertEqual(model.provider, self.provider)
        self.assertIn(model, self.provider.models.all())
    
    def test_ai_model_unique_constraint(self):
        """测试AI模型唯一性约束"""
        AIModel.objects.create(
            provider=self.provider,
            model_id='test-model',
            display_name='Test Model',
            max_tokens=1024
        )
        
        with self.assertRaises(IntegrityError):
            AIModel.objects.create(
                provider=self.provider,
                model_id='test-model',
                display_name='Another Test Model',
                max_tokens=2048
            )
    
    def test_ai_model_different_providers(self):
        """测试不同提供商的模型"""
        provider2 = AIProvider.objects.create(
            name='test_provider2',
            provider_type=AIProviderType.ANTHROPIC,
            display_name='Test Provider 2',
            base_url='https://api.test2.com'
        )
        
        # 同一模型ID在不同提供商下应该可以存在
        model1 = AIModel.objects.create(
            provider=self.provider,
            model_id='test-model',
            display_name='Test Model 1',
            max_tokens=1024
        )
        
        model2 = AIModel.objects.create(
            provider=provider2,
            model_id='test-model',
            display_name='Test Model 2',
            max_tokens=2048
        )
        
        self.assertEqual(model1.provider, self.provider)
        self.assertEqual(model2.provider, provider2)
        self.assertEqual(model1.model_id, 'test-model')
        self.assertEqual(model2.model_id, 'test-model')


class SimpleAPIKeyTest(TestCase):
    """简化的API密钥测试"""
    
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
            base_url='https://api.test.com'
        )
    
    def test_create_api_key_basic(self):
        """测试创建API密钥（基础功能）"""
        api_key = APIKey.objects.create(
            provider=self.provider,
            user=self.user,
            name='My OpenAI Key',
            encrypted_key='encrypted_key_value'
        )
        
        self.assertEqual(api_key.provider, self.provider)
        self.assertEqual(api_key.user, self.user)
        self.assertEqual(api_key.name, 'My OpenAI Key')
        self.assertEqual(api_key.encrypted_key, 'encrypted_key_value')
        self.assertTrue(api_key.is_active)
        self.assertFalse(api_key.is_default)
        self.assertEqual(str(api_key), 'My OpenAI Key - Test Provider')
    
    def test_api_key_unique_constraint(self):
        """测试API密钥唯一性约束（is_default=True时）"""
        # 创建第一个默认密钥
        APIKey.objects.create(
            provider=self.provider,
            user=self.user,
            name='Default Key',
            encrypted_key='encrypted_key_value',
            is_default=True
        )
        
        # 尝试创建第二个默认密钥，应该抛出IntegrityError
        with self.assertRaises(IntegrityError):
            APIKey.objects.create(
                provider=self.provider,
                user=self.user,
                name='Another Default Key',
                encrypted_key='another_encrypted_key_value',
                is_default=True
            )
    
    def test_api_key_non_default_creation(self):
        """测试创建非默认API密钥"""
        # 创建第一个默认密钥
        APIKey.objects.create(
            provider=self.provider,
            user=self.user,
            name='Default Key',
            encrypted_key='encrypted_key_value',
            is_default=True
        )
        
        # 创建非默认密钥应该成功
        non_default_key = APIKey.objects.create(
            provider=self.provider,
            user=self.user,
            name='Non-Default Key',
            encrypted_key='non_default_encrypted_key_value',
            is_default=False
        )
        self.assertFalse(non_default_key.is_default)
        
        # 验证可以创建多个非默认密钥
        another_non_default = APIKey.objects.create(
            provider=self.provider,
            user=self.user,
            name='Another Non-Default Key',
            encrypted_key='another_non_default_encrypted_key_value',
            is_default=False
        )
        self.assertFalse(another_non_default.is_default)
    
    def test_api_key_user_relationship(self):
        """测试API密钥与用户的关系"""
        api_key = APIKey.objects.create(
            provider=self.provider,
            user=self.user,
            name='Test Key',
            encrypted_key='encrypted_key_value'
        )
        
        self.assertEqual(api_key.user, self.user)
        self.assertIn(api_key, self.user.api_keys.all())
    
    def test_api_key_provider_relationship(self):
        """测试API密钥与提供商的关系"""
        api_key = APIKey.objects.create(
            provider=self.provider,
            user=self.user,
            name='Test Key',
            encrypted_key='encrypted_key_value'
        )
        
        self.assertEqual(api_key.provider, self.provider)
        self.assertIn(api_key, self.provider.api_keys.all())


class TestAIModelIntegrationSimple(TestCase):
    """AI模型集成测试（简化版）"""
    
    def test_provider_model_relationship(self):
        """测试提供商与模型的关系"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        provider = AIProvider.objects.create(
            name='test_provider',
            provider_type=AIProviderType.OPENAI,
            display_name='Test Provider',
            base_url='https://api.test.com'
        )
        
        model = AIModel.objects.create(
            provider=provider,
            model_id='test-model',
            display_name='Test Model',
            max_tokens=1024
        )
        
        api_key = APIKey.objects.create(
            provider=provider,
            user=user,
            name='Test Key',
            encrypted_key='encrypted_key_value'
        )
        
        # 验证关系
        self.assertEqual(model.provider, provider)
        self.assertEqual(api_key.provider, provider)
        self.assertEqual(api_key.user, user)
        self.assertIn(model, provider.models.all())
        self.assertIn(api_key, provider.api_keys.all())
        self.assertIn(api_key, user.api_keys.all())
    
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

