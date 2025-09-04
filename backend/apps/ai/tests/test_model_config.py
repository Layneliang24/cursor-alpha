"""
ModelConfig API 测试
"""

import json
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

from apps.ai.models import AIProvider, AIModel, PromptTemplate, ModelConfig

User = get_user_model()


class ModelConfigAPITestCase(TestCase):
    """模型配置API测试用例"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # 创建API客户端
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # 创建测试提供商
        self.provider = AIProvider.objects.create(
            name='openai',
            provider_type='openai',
            display_name='OpenAI',
            base_url='https://api.openai.com/v1',
            is_active=True
        )
        
        # 创建测试模型
        self.model = AIModel.objects.create(
            provider=self.provider,
            model_id='gpt-3.5-turbo',
            display_name='GPT-3.5 Turbo',
            max_tokens=4096,
            is_active=True
        )
        
        # 创建测试模板
        self.template = PromptTemplate.objects.create(
            name='测试模板',
            content='你是一个有用的AI助手',
            category='general',
            is_active=True,
            created_by=self.user
        )
        
    def test_create_model_config(self):
        """测试创建模型配置"""
        url = reverse('ai:modelconfig-list')
        data = {
            'provider': self.provider.id,
            'model': 'gpt-3.5-turbo',
            'config_name': '测试配置',
            'temperature': 0.8,
            'max_tokens': 1000,
            'top_p': 0.9,
            'frequency_penalty': 0.1,
            'presence_penalty': 0.1,
            'prompt_template': self.template.id,
            'system_prompt_template': '自定义系统提示',
            'advanced_params': {
                'seed': 42,
                'reserved_tokens': 256
            }
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 验证返回数据
        response_data = response.json()
        self.assertEqual(response_data['config_name'], '测试配置')
        self.assertEqual(response_data['temperature'], 0.8)
        self.assertEqual(response_data['max_tokens'], 1000)
        self.assertEqual(response_data['provider'], self.provider.id)
        self.assertEqual(response_data['model'], 'gpt-3.5-turbo')
        
        # 验证数据库中的记录
        config = ModelConfig.objects.get(id=response_data['id'])
        self.assertEqual(config.user, self.user)
        self.assertEqual(config.config_name, '测试配置')
        
    def test_list_model_configs(self):
        """测试获取模型配置列表"""
        # 创建测试配置
        config = ModelConfig.objects.create(
            user=self.user,
            provider=self.provider,
            model='gpt-3.5-turbo',
            config_name='测试配置1',
            temperature=0.7
        )
        
        url = reverse('ai:modelconfig-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(len(response_data), 1)
        self.assertEqual(response_data[0]['id'], config.id)
        
    def test_get_model_config_detail(self):
        """测试获取模型配置详情"""
        config = ModelConfig.objects.create(
            user=self.user,
            provider=self.provider,
            model='gpt-3.5-turbo',
            config_name='测试配置',
            temperature=0.7,
            prompt_template=self.template
        )
        
        url = reverse('ai:modelconfig-detail', kwargs={'pk': config.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(response_data['id'], config.id)
        self.assertEqual(response_data['config_name'], '测试配置')
        self.assertEqual(response_data['template_name'], self.template.name)
        
    def test_update_model_config(self):
        """测试更新模型配置"""
        config = ModelConfig.objects.create(
            user=self.user,
            provider=self.provider,
            model='gpt-3.5-turbo',
            config_name='原始配置',
            temperature=0.7
        )
        
        url = reverse('ai:modelconfig-detail', kwargs={'pk': config.id})
        data = {
            'config_name': '更新后配置',
            'temperature': 0.9,
            'max_tokens': 2000
        }
        
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证更新
        config.refresh_from_db()
        self.assertEqual(config.config_name, '更新后配置')
        self.assertEqual(config.temperature, 0.9)
        self.assertEqual(config.max_tokens, 2000)
        
    def test_delete_model_config(self):
        """测试删除模型配置（软删除）"""
        config = ModelConfig.objects.create(
            user=self.user,
            provider=self.provider,
            model='gpt-3.5-turbo',
            config_name='待删除配置',
            temperature=0.7
        )
        
        url = reverse('ai:modelconfig-detail', kwargs={'pk': config.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # 验证软删除
        config.refresh_from_db()
        self.assertFalse(config.is_active)
        
    def test_set_default_config(self):
        """测试设置默认配置"""
        config = ModelConfig.objects.create(
            user=self.user,
            provider=self.provider,
            model='gpt-3.5-turbo',
            config_name='测试配置',
            temperature=0.7
        )
        
        url = reverse('ai:modelconfig-set-default', kwargs={'pk': config.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证设置为默认
        config.refresh_from_db()
        self.assertTrue(config.is_default)
        
    def test_duplicate_config(self):
        """测试复制配置"""
        original_config = ModelConfig.objects.create(
            user=self.user,
            provider=self.provider,
            model='gpt-3.5-turbo',
            config_name='原始配置',
            temperature=0.8,
            max_tokens=1500,
            prompt_template=self.template
        )
        
        url = reverse('ai:modelconfig-duplicate', kwargs={'pk': original_config.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_data = response.json()
        
        # 验证复制的配置
        self.assertEqual(response_data['data']['config_name'], '原始配置 (副本)')
        self.assertEqual(response_data['data']['temperature'], 0.8)
        self.assertEqual(response_data['data']['max_tokens'], 1500)
        self.assertFalse(response_data['data']['is_default'])  # 副本不应该是默认的
        
    def test_models_metadata_endpoint(self):
        """测试模型元数据端点"""
        url = reverse('ai:modelconfig-models-metadata')
        response = self.client.get(url, {'provider_id': self.provider.id})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        
        self.assertTrue(response_data['success'])
        self.assertEqual(len(response_data['data']), 1)
        self.assertEqual(response_data['data'][0]['name'], 'gpt-3.5-turbo')
        self.assertEqual(response_data['data'][0]['context_window'], 4096)
        
    def test_validation_temperature_range(self):
        """测试温度参数范围验证"""
        url = reverse('ai:modelconfig-list')
        data = {
            'provider': self.provider.id,
            'model': 'gpt-3.5-turbo',
            'config_name': '测试配置',
            'temperature': 2.5  # 超出范围
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('temperature', response.json())
        
    def test_validation_max_tokens_limit(self):
        """测试最大Token限制验证"""
        url = reverse('ai:modelconfig-list')
        data = {
            'provider': self.provider.id,
            'model': 'gpt-3.5-turbo',
            'config_name': '测试配置',
            'max_tokens': 5000,  # 超出模型上下文窗口
            'advanced_params': {'reserved_tokens': 256}
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('max_tokens', response.json())
        
    def test_validation_advanced_params(self):
        """测试高级参数验证"""
        url = reverse('ai:modelconfig-list')
        data = {
            'provider': self.provider.id,
            'model': 'gpt-3.5-turbo',
            'config_name': '测试配置',
            'advanced_params': {
                'seed': -1,  # 无效的种子值
                'stop_words': ['a', 'b'] * 10,  # 过多停止词
                'reserved_tokens': -1  # 无效的保留Token数
            }
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('advanced_params', response.json())


class PromptTemplateAPITestCase(TestCase):
    """系统提示模板API测试用例"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
    def test_create_prompt_template(self):
        """测试创建提示模板"""
        url = reverse('ai:prompttemplate-list')
        data = {
            'name': '测试模板',
            'description': '这是一个测试模板',
            'content': '你是一个专业的测试助手',
            'category': 'general'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        response_data = response.json()
        self.assertEqual(response_data['name'], '测试模板')
        self.assertEqual(response_data['category'], 'general')
        self.assertEqual(response_data['created_by'], self.user.id)
        
    def test_list_prompt_templates(self):
        """测试获取模板列表"""
        # 创建用户模板
        user_template = PromptTemplate.objects.create(
            name='用户模板',
            content='用户创建的模板',
            category='custom',
            created_by=self.user
        )
        
        # 创建系统模板
        system_template = PromptTemplate.objects.create(
            name='系统模板',
            content='系统内置模板',
            category='general',
            is_system=True,
            is_public=True,
            created_by=self.user
        )
        
        url = reverse('ai:prompttemplate-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        
        # 用户应该能看到自己的模板和系统模板
        template_names = [t['name'] for t in response_data]
        self.assertIn('用户模板', template_names)
        self.assertIn('系统模板', template_names)
        
    def test_get_template_categories(self):
        """测试获取模板分类"""
        url = reverse('ai:prompttemplate-categories')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        
        self.assertTrue(response_data['success'])
        categories = response_data['data']
        
        # 验证包含预期的分类
        category_values = [c['value'] for c in categories]
        self.assertIn('general', category_values)
        self.assertIn('coding', category_values)
        self.assertIn('writing', category_values)
        
    def test_template_validation(self):
        """测试模板验证"""
        url = reverse('ai:prompttemplate-list')
        
        # 测试名称过短
        data = {
            'name': 'a',  # 过短
            'content': '有效的内容',
            'category': 'general'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # 测试内容过短
        data = {
            'name': '有效名称',
            'content': 'abc',  # 过短
            'category': 'general'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
