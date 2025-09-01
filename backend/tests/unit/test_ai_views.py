"""
AI视图单元测试
"""
import pytest
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
            name='Test Provider',
            type='openai',
            base_url='https://api.openai.com',
            api_version='v1',
            status='active'
        )
    
    def test_list_providers(self):
        """测试获取提供商列表"""
        url = reverse('ai-providers-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Provider')
    
    def test_create_provider(self):
        """测试创建提供商"""
        url = reverse('ai-providers-list')
        data = {
            'name': 'New Provider',
            'type': 'anthropic',
            'base_url': 'https://api.anthropic.com',
            'api_version': 'v1',
            'status': 'active'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(AIProvider.objects.count(), 2)
        self.assertEqual(response.data['name'], 'New Provider')
    
    def test_update_provider(self):
        """测试更新提供商"""
        url = reverse('ai-providers-detail', args=[self.provider.id])
        data = {'name': 'Updated Provider'}
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.provider.refresh_from_db()
        self.assertEqual(self.provider.name, 'Updated Provider')
    
    def test_delete_provider(self):
        """测试删除提供商"""
        url = reverse('ai-providers-detail', args=[self.provider.id])
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
            name='Test Provider',
            type='openai',
            base_url='https://api.openai.com'
        )
        
        self.api_key = APIKey.objects.create(
            name='Test Key',
            provider=self.provider,
            key_value='sk-test-key',
            is_active=True
        )
    
    def test_list_api_keys(self):
        """测试获取API密钥列表"""
        url = reverse('ai-api-keys-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Key')
    
    def test_create_api_key(self):
        """测试创建API密钥"""
        url = reverse('ai-api-keys-list')
        data = {
            'name': 'New Key',
            'provider': self.provider.id,
            'key_value': 'sk-new-key',
            'is_active': True
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(APIKey.objects.count(), 2)
    
    def test_update_api_key(self):
        """测试更新API密钥"""
        url = reverse('ai-api-keys-detail', args=[self.api_key.id])
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
            name='Test Provider',
            type='openai',
            base_url='https://api.openai.com'
        )
        
        self.model = AIModel.objects.create(
            name='GPT-4',
            provider=self.provider,
            model_id='gpt-4',
            max_tokens=4096,
            temperature=0.7
        )
    
    def test_list_models(self):
        """测试获取模型列表"""
        url = reverse('ai-models-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'GPT-4')
    
    def test_create_model(self):
        """测试创建模型"""
        url = reverse('ai-models-list')
        data = {
            'name': 'Claude-3',
            'provider': self.provider.id,
            'model_id': 'claude-3',
            'max_tokens': 8192,
            'temperature': 0.5
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
            name='Test Provider',
            type='openai',
            base_url='https://api.openai.com'
        )
        
        self.model = AIModel.objects.create(
            name='GPT-4',
            provider=self.provider,
            model_id='gpt-4'
        )
        
        self.config = ModelConfig.objects.create(
            name='Default Config',
            model=self.model,
            temperature=0.7,
            max_tokens=4096,
            top_p=0.9
        )
    
    def test_list_configs(self):
        """测试获取配置列表"""
        url = reverse('ai-model-configs-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Default Config')
    
    def test_create_config(self):
        """测试创建配置"""
        url = reverse('ai-model-configs-list')
        data = {
            'name': 'Custom Config',
            'model': self.model.id,
            'temperature': 0.5,
            'max_tokens': 2048,
            'top_p': 0.8
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
            name='Test Provider',
            type='openai',
            base_url='https://api.openai.com'
        )
        
        self.usage = TokenUsage.objects.create(
            user=self.user,
            provider=self.provider,
            model_name='gpt-4',
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            cost=0.003
        )
    
    def test_list_usage(self):
        """测试获取使用量列表"""
        url = reverse('ai-token-usage-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['model_name'], 'gpt-4')
    
    def test_create_usage(self):
        """测试创建使用量记录"""
        url = reverse('ai-token-usage-list')
        data = {
            'provider': self.provider.id,
            'model_name': 'claude-3',
            'prompt_tokens': 200,
            'completion_tokens': 100,
            'total_tokens': 300,
            'cost': 0.006
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TokenUsage.objects.count(), 2)


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
            name='Test Provider',
            type='openai',
            base_url='https://api.openai.com'
        )
        
        self.api_key = APIKey.objects.create(
            name='Test Key',
            provider=self.provider,
            key_value='sk-test-key'
        )
    
    def test_export_config(self):
        """测试导出配置"""
        url = reverse('config-export')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('providers', response.data)
        self.assertIn('api_keys', response.data)
    
    def test_import_config(self):
        """测试导入配置"""
        url = reverse('config-import')
        data = {
            'providers': [
                {
                    'name': 'Imported Provider',
                    'type': 'anthropic',
                    'base_url': 'https://api.anthropic.com',
                    'api_version': 'v1'
                }
            ],
            'api_keys': [
                {
                    'name': 'Imported Key',
                    'provider_type': 'anthropic',
                    'key_value': 'sk-imported-key'
                }
            ]
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('imported', response.data)


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
        url = reverse('user-settings-my-settings')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('theme', response.data)
        self.assertIn('language', response.data)
    
    def test_update_my_settings(self):
        """测试更新用户设置"""
        url = reverse('user-settings-my-settings')
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
            description='Test configuration'
        )
    
    def test_list_system_configs(self):
        """测试获取系统配置列表"""
        url = reverse('system-configs-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['key'], 'test_key')
    
    def test_create_system_config(self):
        """测试创建系统配置"""
        url = reverse('system-configs-list')
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
            name='Primary Provider',
            type='openai',
            base_url='https://api.openai.com'
        )
        
        self.provider2 = AIProvider.objects.create(
            name='Backup Provider',
            type='anthropic',
            base_url='https://api.anthropic.com'
        )
        
        self.strategy = FailoverStrategy.objects.create(
            name='Test Strategy',
            priority=1,
            providers=[self.provider1.id, self.provider2.id]
        )
    
    def test_list_strategies(self):
        """测试获取策略列表"""
        url = reverse('ai-failover-strategies-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Strategy')
    
    def test_create_strategy(self):
        """测试创建策略"""
        url = reverse('ai-failover-strategies-list')
        data = {
            'name': 'New Strategy',
            'priority': 2,
            'providers': [self.provider1.id]
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
            config_data={
                'providers': [],
                'api_keys': [],
                'models': []
            }
        )
    
    def test_list_templates(self):
        """测试获取模板列表"""
        url = reverse('ai-config-templates-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Template')
    
    def test_create_template(self):
        """测试创建模板"""
        url = reverse('ai-config-templates-list')
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
            version_number='1.0.0',
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
        url = reverse('ai-config-versions-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['version_number'], '1.0.0')
    
    def test_create_version(self):
        """测试创建版本"""
        url = reverse('ai-config-versions-list')
        data = {
            'version_number': '1.1.0',
            'description': 'Updated version',
            'config_data': {
                'providers': [],
                'api_keys': [],
                'models': []
            }
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ConfigVersion.objects.count(), 2)
