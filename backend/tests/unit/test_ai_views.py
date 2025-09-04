# 测试环境配置
import os
os.environ['TESTING'] = 'True'
os.environ['DJANGO_SETTINGS_MODULE'] = 'backend.settings'

"""
AI视图单元测试
"""
from unittest.mock import Mock, patch, MagicMock, call, ANY, sentinel
import pytest
import json
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from apps.ai.config_models import (
    AIProvider, APIKey, AIModel, ModelConfig, 
    TokenUsage, UsageQuota, FailoverStrategy,
    ConfigTemplate, ConfigVersion, UserSettings, SystemConfig
)

User = get_user_model()


class AIProviderViewSetTest(APITestCase):
    """AI提供商视图集测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # 创建测试数据
        self.provider = AIProvider.objects.create(
            name='test_provider',
            display_name='Test Provider',
            provider_type='openai',
            base_url='https://api.openai.com',
            api_version='v1'
        )
    
    def test_list_providers(self):
        """测试获取提供商列表"""
        url = reverse('ai:aiprovider-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['display_name'], 'Test Provider')
    
    def test_create_provider(self):
        """测试创建提供商"""
        url = reverse('ai:aiprovider-list')
        data = {
            'name': 'new_provider',
            'display_name': 'New Provider',
            'provider_type': 'anthropic',
            'base_url': 'https://api.anthropic.com',
            'api_version': 'v1'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(AIProvider.objects.count(), 2)
        self.assertEqual(response.data['display_name'], 'New Provider')
    
    def test_update_provider(self):
        """测试更新提供商"""
        url = reverse('ai:aiprovider-detail', args=[self.provider.id])
        data = {'display_name': 'Updated Provider'}
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.provider.refresh_from_db()
        self.assertEqual(self.provider.display_name, 'Updated Provider')
    
    def test_delete_provider(self):
        """测试删除提供商"""
        url = reverse('ai:aiprovider-detail', args=[self.provider.id])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(AIProvider.objects.count(), 0)


class APIKeyViewSetTest(APITestCase):
    """API密钥视图集测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.provider = AIProvider.objects.create(
            name='test_provider',
            display_name='Test Provider',
            provider_type='openai',
            base_url='https://api.openai.com'
        )
        
        self.api_key = APIKey.objects.create(
            name='Test Key',
            provider=self.provider,
            user=self.user
        )
        self.api_key.set_key('sk-test-key')
        self.api_key.save()
    
    def test_list_api_keys(self):
        """测试获取API密钥列表"""
        url = reverse('ai:apikey-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Key')
    
    def test_create_api_key(self):
        """测试创建API密钥"""
        url = reverse('ai:apikey-list')
        data = {
            'name': 'New Key',
            'provider': self.provider.id,
            'raw_key': 'sk-new-key',
            'is_default': False
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(APIKey.objects.count(), 2)
    
    def test_update_api_key(self):
        """测试更新API密钥"""
        url = reverse('ai:apikey-detail', args=[self.api_key.id])
        data = {'name': 'Updated Key'}
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.api_key.refresh_from_db()
        self.assertEqual(self.api_key.name, 'Updated Key')


class AIModelViewSetTest(APITestCase):
    """AI模型视图集测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.provider = AIProvider.objects.create(
            name='test_provider',
            display_name='Test Provider',
            provider_type='openai',
            base_url='https://api.openai.com'
        )
        
        self.model = AIModel.objects.create(
            display_name='GPT-4',
            provider=self.provider,
            model_id='gpt-4',
            max_tokens=4096
        )
    
    def test_list_models(self):
        """测试获取模型列表"""
        url = reverse('ai:aimodel-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['display_name'], 'GPT-4')
    
    def test_create_model(self):
        """测试创建模型"""
        url = reverse('ai:aimodel-list')
        data = {
            'display_name': 'Claude-3',
            'provider': self.provider.id,
            'model_id': 'claude-3',
            'max_tokens': 8192
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(AIModel.objects.count(), 2)


class ModelConfigViewSetTest(APITestCase):
    """模型配置视图集测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.provider = AIProvider.objects.create(
            name='test_provider',
            display_name='Test Provider',
            provider_type='openai',
            base_url='https://api.openai.com'
        )
        
        self.model = AIModel.objects.create(
            display_name='GPT-4',
            provider=self.provider,
            model_id='gpt-4',
            max_tokens=4096
        )
        
        self.config = ModelConfig.objects.create(
            config_name='Default Config',
            user=self.user,
            provider=self.provider,
            model=self.model.display_name,
            max_tokens=4096
        )
    
    def test_list_configs(self):
        """测试获取配置列表"""
        url = reverse('ai:modelconfig-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['config_name'], 'Default Config')
    
    def test_create_config(self):
        """测试创建配置"""
        url = reverse('ai:modelconfig-list')
        data = {
            'config_name': 'Custom Config',
            'provider': self.provider.id,
            'model': self.model.display_name,
            'max_tokens': 2048
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ModelConfig.objects.count(), 2)


class TokenUsageViewSetTest(APITestCase):
    """Token使用量视图集测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.provider = AIProvider.objects.create(
            name='test_provider',
            display_name='Test Provider',
            provider_type='openai',
            base_url='https://api.openai.com'
        )
        
        # 创建AIModel和APIKey用于TokenUsage
        self.model = AIModel.objects.create(
            display_name='GPT-4',
            provider=self.provider,
            model_id='gpt-4',
            max_tokens=4096
        )
        
        self.api_key = APIKey.objects.create(
            name='Test Key',
            provider=self.provider,
            user=self.user
        )
        self.api_key.set_key('sk-test-key')
        self.api_key.save()
        
        self.usage = TokenUsage.objects.create(
            user=self.user,
            provider=self.provider,
            model=self.model,
            api_key=self.api_key,
            input_tokens=100,
            output_tokens=50,
            input_cost=0.002,
            output_cost=0.001,
            response_time=1.5,
            status='success'
        )
    
    def test_list_usage(self):
        """测试获取使用量列表"""
        url = reverse('ai:tokenusage-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['model_display_name'], 'GPT-4')
    
    def test_create_usage_not_allowed(self):
        """测试创建使用量记录不被允许（只读视图集）"""
        url = reverse('ai:tokenusage-list')
        data = {
            'provider': self.provider.id,
            'model': self.model.id,
            'api_key': self.api_key.id,
            'input_tokens': 200,
            'output_tokens': 100,
            'input_cost': 0.004,
            'output_cost': 0.002,
            'response_time': 2.0,
            'status': 'success'
        }
        response = self.client.post(url, data)
        
        # TokenUsageViewSet是只读的，不支持POST
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class ConfigExportImportTest(APITestCase):
    """配置导入导出测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.provider = AIProvider.objects.create(
            name='test_provider',
            display_name='Test Provider',
            provider_type='openai',
            base_url='https://api.openai.com'
        )
        
        self.api_key = APIKey.objects.create(
            name='Test Key',
            provider=self.provider,
            user=self.user
        )
        self.api_key.set_key('sk-test-key')
        self.api_key.save()
    
    def test_export_config(self):
        """测试导出配置"""
        url = reverse('ai:config-export')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 由于返回的是HttpResponse，需要解析JSON内容
        content = json.loads(response.content.decode('utf-8'))
        self.assertIn('providers', content)
        self.assertIn('strategies', content)
    
    def test_import_config_requires_file(self):
        """测试导入配置需要文件上传"""
        url = reverse('ai:config-import')
        # 由于ConfigImportSerializer期望文件上传，直接POST数据会失败
        data = {}
        response = self.client.post(url, data)
        
        # 应该返回400，因为缺少必需的文件字段
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('file', response.data)


class UserSettingsViewSetTest(APITestCase):
    """用户设置视图集测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_get_my_settings(self):
        """测试获取用户设置"""
        url = reverse('ai:user-settings-my-settings')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('theme', response.data)
        self.assertIn('language', response.data)
    
    def test_update_my_settings(self):
        """测试更新用户设置"""
        url = reverse('ai:user-settings-my-settings')
        data = {
            'theme': 'dark',
            'language': 'en-US',
            'timezone': 'UTC'
        }
        response = self.client.put(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['theme'], 'dark')
        self.assertEqual(response.data['language'], 'en-US')


class SystemConfigViewSetTest(APITestCase):
    """系统配置视图集测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.config = SystemConfig.objects.create(
            key='test_key',
            value='test_value',
            description='Test configuration',
            is_public=True
        )
    
    def test_list_system_configs(self):
        """测试获取系统配置列表"""
        url = reverse('ai:system-configs-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['key'], 'test_key')
    
    def test_create_system_config(self):
        """测试创建系统配置"""
        url = reverse('ai:system-configs-list')
        data = {
            'key': 'new_key',
            'value': 'new_value',
            'description': 'New configuration'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SystemConfig.objects.count(), 2)


class FailoverStrategyViewSetTest(APITestCase):
    """故障转移策略视图集测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.provider1 = AIProvider.objects.create(
            name='primary_provider',
            display_name='Primary Provider',
            provider_type='openai',
            base_url='https://api.openai.com',
            api_version='v1'
        )
        
        self.provider2 = AIProvider.objects.create(
            name='backup_provider',
            display_name='Backup Provider',
            provider_type='anthropic',
            base_url='https://api.anthropic.com',
            api_version='v1'
        )
        
        # 创建AIModel用于FailoverStrategy
        self.model = AIModel.objects.create(
            display_name='GPT-4',
            provider=self.provider1,
            model_id='gpt-4',
            max_tokens=4096
        )
        
        # 为备用提供商创建模型
        self.fallback_model = AIModel.objects.create(
            display_name='Claude-3',
            provider=self.provider2,
            model_id='claude-3',
            max_tokens=4096
        )
        
        self.strategy = FailoverStrategy.objects.create(
            name='Test Strategy',
            user=self.user,
            primary_provider=self.provider1,
            primary_model=self.model,
            strategy_mode='priority',
            is_active=True
        )
        
        # 创建FailoverRule来连接备用提供商和模型
        from apps.ai.config_models import FailoverRule
        FailoverRule.objects.create(
            strategy=self.strategy,
            fallback_provider=self.provider2,
            fallback_model=self.fallback_model,
            priority=1,
            trigger_errors=['timeout', 'rate_limit']
        )
    
    def test_list_strategies(self):
        """测试获取故障转移策略列表"""
        url = reverse('ai:fallbackstrategy-list')
        response = self.client.get(url)
        
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.data}")
        
        # 检查数据库状态
        from apps.ai.config_models import FailoverStrategy
        total_strategies = FailoverStrategy.objects.count()
        print(f"数据库中总共有 {total_strategies} 个FailoverStrategy")
        print(f"当前用户创建的策略: {FailoverStrategy.objects.filter(user=self.user).count()}")
        
        # 检查每个策略的详细信息
        for strategy in FailoverStrategy.objects.all():
            print(f"策略 {strategy.id}: user={strategy.user.id}, name={strategy.name}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 由于FailoverStrategyViewSet.list返回{'results': [...], 'count': 1}格式
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['name'], 'Test Strategy')
    
    def test_create_strategy(self):
        """测试创建策略"""
        url = reverse('ai:fallbackstrategy-list')
        data = {
            'name': 'New Strategy',
            'user': self.user.id,
            'primary_provider': self.provider1.id,
            'primary_model': self.model.id,
            'strategy_mode': 'priority',
            'is_active': True
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FailoverStrategy.objects.count(), 2)


class ConfigTemplateViewSetTest(APITestCase):
    """配置模板视图集测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.template = ConfigTemplate.objects.create(
            name='Test Template',
            description='Test template description',
            created_by=self.user,
            config_data={
                'providers': [],
                'api_keys': [],
                'models': []
            }
        )
    
    def test_list_templates(self):
        """测试获取模板列表"""
        url = reverse('ai:config-template-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Template')
    
    def test_create_template(self):
        """测试创建模板"""
        url = reverse('ai:config-template-list')
        data = {
            'name': 'New Template',
            'description': 'New template description',
            'config_data': {
                'providers': [],
                'api_keys': [],
                'models': []
            }
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ConfigTemplate.objects.count(), 2)


class ConfigVersionViewSetTest(APITestCase):
    """配置版本视图集测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.version = ConfigVersion.objects.create(
            version_name='1.0.0',
            description='Initial version',
            config_data={
                'providers': [],
                'api_keys': [],
                'models': []
            },
            created_by=self.user
        )
    
    def test_list_versions(self):
        """测试获取版本列表"""
        url = reverse('ai:config-version-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['version_name'], '1.0.0')
    
    def test_create_version_not_allowed(self):
        """测试创建版本不被允许（只读视图集）"""
        url = reverse('ai:config-version-list')
        data = {
            'version_name': '1.1.0',
            'description': 'Updated version',
            'config_data': {
                'providers': [],
                'api_keys': [],
                'models': []
            }
        }
        response = self.client.post(url, data, format='json')
        
        # ConfigVersionViewSet是只读的，不支持POST
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

# TODO: 考虑使用测试数据工厂来创建测试数据
# from tests.data_management.test_data_factory import TestDataFactory
