"""
AI序列化器单元测试
"""
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from apps.ai.config_models import (
    AIProvider, APIKey, AIModel, ModelConfig, 
    TokenUsage, UsageQuota, FailoverStrategy,
    ConfigTemplate, ConfigVersion, UserSettings, SystemConfig
)
from apps.ai.serializers import (
    AIProviderSerializer, APIKeySerializer, AIModelSerializer,
    ModelConfigSerializer, TokenUsageSerializer, UsageQuotaSerializer,
    FailoverStrategySerializer, ConfigTemplateSerializer, ConfigVersionSerializer,
    UserSettingsSerializer, SystemConfigSerializer, LoginHistorySerializer,
    DeviceSessionSerializer, UserProfileSerializer, PasswordChangeSerializer
)

User = get_user_model()


class AIProviderSerializerTest(TestCase):
    """AI提供商序列化器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.provider_data = {
            'name': 'Test Provider',
            'type': 'openai',
            'base_url': 'https://api.openai.com',
            'api_version': 'v1',
            'status': 'active',
            'description': 'Test provider description'
        }
    
    def test_valid_provider_data(self):
        """测试有效数据序列化"""
        serializer = AIProviderSerializer(data=self.provider_data)
        self.assertTrue(serializer.is_valid())
    
    def test_invalid_provider_data(self):
        """测试无效数据序列化"""
        invalid_data = self.provider_data.copy()
        invalid_data['type'] = 'invalid_type'
        
        serializer = AIProviderSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('type', serializer.errors)
    
    def test_provider_creation(self):
        """测试提供商创建"""
        serializer = AIProviderSerializer(data=self.provider_data)
        self.assertTrue(serializer.is_valid())
        
        provider = serializer.save()
        self.assertEqual(provider.name, 'Test Provider')
        self.assertEqual(provider.type, 'openai')
    
    def test_provider_update(self):
        """测试提供商更新"""
        provider = AIProvider.objects.create(**self.provider_data)
        
        update_data = {'name': 'Updated Provider'}
        serializer = AIProviderSerializer(provider, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid())
        
        updated_provider = serializer.save()
        self.assertEqual(updated_provider.name, 'Updated Provider')


class APIKeySerializerTest(TestCase):
    """API密钥序列化器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.provider = AIProvider.objects.create(
            name='Test Provider',
            type='openai',
            base_url='https://api.openai.com'
        )
        
        self.key_data = {
            'name': 'Test Key',
            'provider': self.provider.id,
            'key_value': 'sk-test-key',
            'is_active': True,
            'description': 'Test API key'
        }
    
    def test_valid_key_data(self):
        """测试有效数据序列化"""
        serializer = APIKeySerializer(data=self.key_data)
        self.assertTrue(serializer.is_valid())
    
    def test_key_creation(self):
        """测试密钥创建"""
        serializer = APIKeySerializer(data=self.key_data)
        self.assertTrue(serializer.is_valid())
        
        key = serializer.save()
        self.assertEqual(key.name, 'Test Key')
        self.assertEqual(key.provider, self.provider)
    
    def test_key_validation(self):
        """测试密钥验证"""
        invalid_data = self.key_data.copy()
        invalid_data['key_value'] = 'invalid-key'
        
        serializer = APIKeySerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())


class AIModelSerializerTest(TestCase):
    """AI模型序列化器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.provider = AIProvider.objects.create(
            name='Test Provider',
            type='openai',
            base_url='https://api.openai.com'
        )
        
        self.model_data = {
            'name': 'GPT-4',
            'provider': self.provider.id,
            'model_id': 'gpt-4',
            'max_tokens': 4096,
            'temperature': 0.7,
            'description': 'GPT-4 model'
        }
    
    def test_valid_model_data(self):
        """测试有效数据序列化"""
        serializer = AIModelSerializer(data=self.model_data)
        self.assertTrue(serializer.is_valid())
    
    def test_model_creation(self):
        """测试模型创建"""
        serializer = AIModelSerializer(data=self.model_data)
        self.assertTrue(serializer.is_valid())
        
        model = serializer.save()
        self.assertEqual(model.name, 'GPT-4')
        self.assertEqual(model.model_id, 'gpt-4')
    
    def test_model_validation(self):
        """测试模型验证"""
        invalid_data = self.model_data.copy()
        invalid_data['max_tokens'] = -1
        
        serializer = AIModelSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())


class ModelConfigSerializerTest(TestCase):
    """模型配置序列化器测试"""
    
    def setUp(self):
        """测试前准备"""
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
        
        self.config_data = {
            'name': 'Default Config',
            'model': self.model.id,
            'temperature': 0.7,
            'max_tokens': 4096,
            'top_p': 0.9,
            'frequency_penalty': 0.0,
            'presence_penalty': 0.0
        }
    
    def test_valid_config_data(self):
        """测试有效数据序列化"""
        serializer = ModelConfigSerializer(data=self.config_data)
        self.assertTrue(serializer.is_valid())
    
    def test_config_creation(self):
        """测试配置创建"""
        serializer = ModelConfigSerializer(data=self.config_data)
        self.assertTrue(serializer.is_valid())
        
        config = serializer.save()
        self.assertEqual(config.name, 'Default Config')
        self.assertEqual(config.temperature, 0.7)


class TokenUsageSerializerTest(TestCase):
    """Token使用量序列化器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.provider = AIProvider.objects.create(
            name='Test Provider',
            type='openai',
            base_url='https://api.openai.com'
        )
        
        self.usage_data = {
            'user': self.user.id,
            'provider': self.provider.id,
            'model_name': 'gpt-4',
            'prompt_tokens': 100,
            'completion_tokens': 50,
            'total_tokens': 150,
            'cost': 0.003
        }
    
    def test_valid_usage_data(self):
        """测试有效数据序列化"""
        serializer = TokenUsageSerializer(data=self.usage_data)
        self.assertTrue(serializer.is_valid())
    
    def test_usage_creation(self):
        """测试使用量记录创建"""
        serializer = TokenUsageSerializer(data=self.usage_data)
        self.assertTrue(serializer.is_valid())
        
        usage = serializer.save()
        self.assertEqual(usage.model_name, 'gpt-4')
        self.assertEqual(usage.total_tokens, 150)


class FailoverStrategySerializerTest(TestCase):
    """故障转移策略序列化器测试"""
    
    def setUp(self):
        """测试前准备"""
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
        
        self.strategy_data = {
            'name': 'Test Strategy',
            'priority': 1,
            'providers': [self.provider1.id, self.provider2.id],
            'description': 'Test failover strategy'
        }
    
    def test_valid_strategy_data(self):
        """测试有效数据序列化"""
        serializer = FailoverStrategySerializer(data=self.strategy_data)
        self.assertTrue(serializer.is_valid())
    
    def test_strategy_creation(self):
        """测试策略创建"""
        serializer = FailoverStrategySerializer(data=self.strategy_data)
        self.assertTrue(serializer.is_valid())
        
        strategy = serializer.save()
        self.assertEqual(strategy.name, 'Test Strategy')
        self.assertEqual(len(strategy.providers), 2)


class ConfigTemplateSerializerTest(TestCase):
    """配置模板序列化器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.template_data = {
            'name': 'Test Template',
            'description': 'Test template description',
            'config_data': {
                'providers': [],
                'api_keys': [],
                'models': []
            }
        }
    
    def test_valid_template_data(self):
        """测试有效数据序列化"""
        serializer = ConfigTemplateSerializer(data=self.template_data)
        self.assertTrue(serializer.is_valid())
    
    def test_template_creation(self):
        """测试模板创建"""
        serializer = ConfigTemplateSerializer(data=self.template_data)
        self.assertTrue(serializer.is_valid())
        
        template = serializer.save()
        self.assertEqual(template.name, 'Test Template')
        self.assertIsInstance(template.config_data, dict)


class ConfigVersionSerializerTest(TestCase):
    """配置版本序列化器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.version_data = {
            'version_number': '1.0.0',
            'description': 'Initial version',
            'config_data': {
                'providers': [],
                'api_keys': [],
                'models': []
            },
            'created_by': self.user.id
        }
    
    def test_valid_version_data(self):
        """测试有效数据序列化"""
        serializer = ConfigVersionSerializer(data=self.version_data)
        self.assertTrue(serializer.is_valid())
    
    def test_version_creation(self):
        """测试版本创建"""
        serializer = ConfigVersionSerializer(data=self.version_data)
        self.assertTrue(serializer.is_valid())
        
        version = serializer.save()
        self.assertEqual(version.version_number, '1.0.0')
        self.assertEqual(version.created_by, self.user)


class UserSettingsSerializerTest(TestCase):
    """用户设置序列化器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.settings_data = {
            'user': self.user.id,
            'display_name': 'Test User',
            'theme': 'dark',
            'language': 'en-US',
            'timezone': 'UTC',
            'email_notifications': True,
            'push_notifications': False
        }
    
    def test_valid_settings_data(self):
        """测试有效数据序列化"""
        serializer = UserSettingsSerializer(data=self.settings_data)
        self.assertTrue(serializer.is_valid())
    
    def test_settings_creation(self):
        """测试设置创建"""
        serializer = UserSettingsSerializer(data=self.settings_data)
        self.assertTrue(serializer.is_valid())
        
        settings = serializer.save()
        self.assertEqual(settings.display_name, 'Test User')
        self.assertEqual(settings.theme, 'dark')
    
    def test_settings_update(self):
        """测试设置更新"""
        settings = UserSettings.objects.create(
            user=self.user,
            theme='light',
            language='zh-CN'
        )
        
        update_data = {'theme': 'dark'}
        serializer = UserSettingsSerializer(settings, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid())
        
        updated_settings = serializer.save()
        self.assertEqual(updated_settings.theme, 'dark')


class SystemConfigSerializerTest(TestCase):
    """系统配置序列化器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.config_data = {
            'key': 'test_key',
            'value': 'test_value',
            'description': 'Test configuration',
            'is_public': False
        }
    
    def test_valid_config_data(self):
        """测试有效数据序列化"""
        serializer = SystemConfigSerializer(data=self.config_data)
        self.assertTrue(serializer.is_valid())
    
    def test_config_creation(self):
        """测试配置创建"""
        serializer = SystemConfigSerializer(data=self.config_data)
        self.assertTrue(serializer.is_valid())
        
        config = serializer.save()
        self.assertEqual(config.key, 'test_key')
        self.assertEqual(config.value, 'test_value')
    
    def test_config_validation(self):
        """测试配置验证"""
        invalid_data = self.config_data.copy()
        invalid_data['key'] = ''  # 空键名
        
        serializer = SystemConfigSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())


class LoginHistorySerializerTest(TestCase):
    """登录历史序列化器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.history_data = {
            'user': self.user.id,
            'ip_address': '192.168.1.1',
            'user_agent': 'Mozilla/5.0',
            'location': 'Beijing, China',
            'device_type': 'desktop',
            'browser': 'Chrome',
            'os': 'Windows',
            'status': 'success'
        }
    
    def test_valid_history_data(self):
        """测试有效数据序列化"""
        serializer = LoginHistorySerializer(data=self.history_data)
        self.assertTrue(serializer.is_valid())
    
    def test_history_creation(self):
        """测试历史记录创建"""
        serializer = LoginHistorySerializer(data=self.history_data)
        self.assertTrue(serializer.is_valid())
        
        history = serializer.save()
        self.assertEqual(history.ip_address, '192.168.1.1')
        self.assertEqual(history.status, 'success')


class DeviceSessionSerializerTest(TestCase):
    """设备会话序列化器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.session_data = {
            'user': self.user.id,
            'device_name': 'Test Device',
            'device_type': 'desktop',
            'ip_address': '192.168.1.1',
            'browser': 'Chrome',
            'os': 'Windows',
            'is_active': True
        }
    
    def test_valid_session_data(self):
        """测试有效数据序列化"""
        serializer = DeviceSessionSerializer(data=self.session_data)
        self.assertTrue(serializer.is_valid())
    
    def test_session_creation(self):
        """测试会话创建"""
        serializer = DeviceSessionSerializer(data=self.session_data)
        self.assertTrue(serializer.is_valid())
        
        session = serializer.save()
        self.assertEqual(session.device_name, 'Test Device')
        self.assertTrue(session.is_active)


class UserProfileSerializerTest(TestCase):
    """用户资料序列化器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.profile_data = {
            'user': self.user.id,
            'display_name': 'Test User',
            'avatar_url': 'https://example.com/avatar.jpg',
            'bio': 'Test user bio'
        }
    
    def test_valid_profile_data(self):
        """测试有效数据序列化"""
        serializer = UserProfileSerializer(data=self.profile_data)
        self.assertTrue(serializer.is_valid())
    
    def test_profile_creation(self):
        """测试资料创建"""
        serializer = UserProfileSerializer(data=self.profile_data)
        self.assertTrue(serializer.is_valid())
        
        profile = serializer.save()
        self.assertEqual(profile.display_name, 'Test User')
        self.assertEqual(profile.bio, 'Test user bio')


class PasswordChangeSerializerTest(TestCase):
    """密码修改序列化器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.password_data = {
            'old_password': 'testpass123',
            'new_password': 'newpass123',
            'confirm_password': 'newpass123'
        }
    
    def test_valid_password_data(self):
        """测试有效数据序列化"""
        serializer = PasswordChangeSerializer(data=self.password_data)
        self.assertTrue(serializer.is_valid())
    
    def test_password_validation(self):
        """测试密码验证"""
        invalid_data = self.password_data.copy()
        invalid_data['confirm_password'] = 'wrongpass'
        
        serializer = PasswordChangeSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('confirm_password', serializer.errors)
    
    def test_old_password_validation(self):
        """测试旧密码验证"""
        invalid_data = self.password_data.copy()
        invalid_data['old_password'] = 'wrongpass'
        
        serializer = PasswordChangeSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('old_password', serializer.errors)
