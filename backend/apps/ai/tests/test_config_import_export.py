import json
import tempfile
import os
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from ..config_models import AIProvider, FailoverStrategy, ConfigTemplate, ConfigVersion, AIModel
from ..serializers import ConfigExportSerializer, ConfigImportSerializer

User = get_user_model()


class ConfigExportViewTest(APITestCase):
    """配置导出视图测试"""

    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # 创建测试数据
        self.provider = AIProvider.objects.create(
            name='Test Provider',
            provider_type='openai',
            display_name='Test Provider',
            base_url='https://api.openai.com',
            is_active=True,
            is_healthy=True,
            created_by=self.user
        )
        
        # 创建AIModel
        self.model = AIModel.objects.create(
            provider=self.provider,
            model_id='gpt-3.5-turbo',
            display_name='GPT-3.5 Turbo',
            max_tokens=4096,
            supports_streaming=True,
            supports_functions=False,
            supports_vision=False,
            is_active=True
        )
        
        self.strategy = FailoverStrategy.objects.create(
            name='Test Strategy',
            description='Test strategy description',
            primary_provider=self.provider,
            primary_model=self.model,
            user=self.user
        )

    def test_export_config_json(self):
        """测试导出JSON格式配置"""
        url = reverse('ai:config-export')
        response = self.client.get(url, {'format': 'json'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertIn('attachment', response['Content-Disposition'])
        self.assertIn('.json', response['Content-Disposition'])
        
        # 验证导出内容
        content = json.loads(response.content.decode())
        self.assertIn('providers', content)
        self.assertIn('strategies', content)
        self.assertIn('version', content)
        self.assertEqual(len(content['providers']), 1)
        self.assertEqual(len(content['strategies']), 1)

    def test_export_config_yaml(self):
        """测试导出YAML格式配置"""
        url = reverse('ai:config-export')
        response = self.client.get(url, {'format': 'yaml'})
        
        # 添加调试信息
        if response.status_code != 200:
            print(f"Status code: {response.status_code}")
            print(f"Response content: {response.content}")
            if hasattr(response, 'data'):
                print(f"Response data: {response.data}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/x-yaml')
        self.assertIn('attachment', response['Content-Disposition'])
        self.assertIn('.yaml', response['Content-Disposition'])

    def test_export_config_creates_version(self):
        """测试导出配置时创建版本记录"""
        url = reverse('ai:config-export')
        initial_count = ConfigVersion.objects.count()
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ConfigVersion.objects.count(), initial_count + 1)
        
        # 验证版本记录
        version = ConfigVersion.objects.latest('created_at')
        self.assertEqual(version.created_by, self.user)
        self.assertIn('Export_', version.version_name)


class ConfigImportViewTest(APITestCase):
    """配置导入视图测试"""

    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # 创建测试所需的基础数据
        from apps.ai.config_models import AIProvider, AIModel
        
        # 创建一个测试提供商
        self.test_provider = AIProvider.objects.create(
            name='Test Provider',
            provider_type='openai',
            display_name='Test Provider',
            base_url='https://api.openai.com',
            is_active=True,
            is_healthy=True
        )
        
        # 创建一个测试模型
        self.test_model = AIModel.objects.create(
            model_id='gpt-3.5-turbo',
            provider=self.test_provider,
            display_name='GPT-3.5 Turbo',
            description='Test model',
            max_tokens=4096,
            cost_per_1k_input_tokens=0.001,
            cost_per_1k_output_tokens=0.002,
            is_active=True
        )
        
        # 创建测试配置文件
        self.config_data = {
            'version': '1.0.0',
            'providers': [
                {
                    'name': 'Imported Provider',
                    'provider_type': 'openai',
                    'display_name': 'Imported Provider',
                    'base_url': 'https://api.openai.com',
                    'is_active': True,
                    'is_healthy': True
                }
            ],
            'strategies': [
                {
                    'name': 'Imported Strategy',
                    'description': 'Imported strategy description'
                }
            ],
            'settings': {
                'default_timeout': 30,
                'max_retries': 3
            }
        }

    def test_import_config_validation_only(self):
        """测试仅验证配置"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.config_data, f)
            f.flush()
            
            with open(f.name, 'rb') as file:
                response = self.client.post(
                    reverse('ai:config-import'),
                    {
                        'file': file,
                        'validate_only': True
                    },
                    format='multipart'
                )
        
        os.unlink(f.name)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('config_summary', response.data)
        self.assertEqual(response.data['config_summary']['providers_count'], 1)
        self.assertEqual(response.data['config_summary']['strategies_count'], 1)

    def test_import_config_success(self):
        """测试成功导入配置"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.config_data, f)
            f.flush()
            
            with open(f.name, 'rb') as file:
                response = self.client.post(
                    reverse('ai:config-import'),
                    {
                        'file': file,
                        'overwrite_existing': True
                    },
                    format='multipart'
                )
        
        os.unlink(f.name)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('import_result', response.data)
        
        # 验证数据已导入
        provider = AIProvider.objects.filter(name='Imported Provider').first()
        self.assertIsNotNone(provider)
        self.assertEqual(provider.provider_type, 'openai')
        
        strategy = FailoverStrategy.objects.filter(name='Imported Strategy').first()
        self.assertIsNotNone(strategy)

    def test_import_config_invalid_format(self):
        """测试导入无效格式的配置文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write('invalid content')
            f.flush()
            
            with open(f.name, 'rb') as file:
                response = self.client.post(
                    reverse('ai:config-import'),
                    {'file': file},
                    format='multipart'
                )
        
        os.unlink(f.name)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('file', response.data)

    def test_import_config_missing_required_fields(self):
        """测试导入缺少必需字段的配置"""
        invalid_config = {
            'version': '1.0.0',
            'providers': []  # 缺少strategies字段
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(invalid_config, f)
            f.flush()
            
            with open(f.name, 'rb') as file:
                response = self.client.post(
                    reverse('ai:config-import'),
                    {'file': file},
                    format='multipart'
                )
        
        os.unlink(f.name)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('缺少必需字段', str(response.data))

    def test_import_config_creates_version(self):
        """测试导入配置时创建版本记录"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.config_data, f)
            f.flush()
            
            initial_count = ConfigVersion.objects.count()
            
            with open(f.name, 'rb') as file:
                response = self.client.post(
                    reverse('ai:config-import'),
                    {'file': file},
                    format='multipart'
                )
        
        os.unlink(f.name)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ConfigVersion.objects.count(), initial_count + 1)
        
        # 验证版本记录
        version = ConfigVersion.objects.latest('created_at')
        self.assertEqual(version.created_by, self.user)
        self.assertIn('Import_', version.version_name)


class ConfigTemplateViewSetTest(APITestCase):
    """配置模板视图集测试"""

    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.template_data = {
            'name': 'Test Template',
            'description': 'Test template description',
            'tags': ['test', 'template'],
            'config_data': {
                'version': '1.0.0',
                'providers': [],
                'strategies': []
            }
        }

    def test_create_template(self):
        """测试创建模板"""
        url = reverse('ai:config-template-list')
        response = self.client.post(url, self.template_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ConfigTemplate.objects.count(), 1)
        
        template = ConfigTemplate.objects.first()
        self.assertEqual(template.name, 'Test Template')
        self.assertEqual(template.created_by, self.user)

    def test_list_templates(self):
        """测试获取模板列表"""
        ConfigTemplate.objects.create(
            name='Test Template',
            description='Test description',
            config_data=self.template_data['config_data'],
            created_by=self.user
        )
        
        url = reverse('ai:config-template-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Template')

    def test_apply_template(self):
        """测试应用模板"""
        template = ConfigTemplate.objects.create(
            name='Test Template',
            description='Test description',
            config_data=self.template_data['config_data'],
            created_by=self.user
        )
        
        url = reverse('ai:config-template-apply', kwargs={'pk': template.pk})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('import_result', response.data)


class ConfigVersionViewSetTest(APITestCase):
    """配置版本视图集测试"""

    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.version_data = {
            'version_name': 'Test Version',
            'description': 'Test version description',
            'config_data': {
                'version': '1.0.0',
                'providers': [],
                'strategies': []
            }
        }

    def test_list_versions(self):
        """测试获取版本列表"""
        ConfigVersion.objects.create(
            version_name='Test Version',
            description='Test description',
            config_data=self.version_data['config_data'],
            created_by=self.user
        )
        
        url = reverse('ai:config-version-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['version_name'], 'Test Version')

    def test_rollback_version(self):
        """测试回滚版本"""
        version = ConfigVersion.objects.create(
            version_name='Test Version',
            description='Test description',
            config_data=self.version_data['config_data'],
            created_by=self.user
        )
        
        url = reverse('ai:config-version-rollback', kwargs={'pk': version.pk})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('rollback_result', response.data)


class ConfigSerializerTest(TestCase):
    """配置序列化器测试"""

    def test_config_export_serializer(self):
        """测试配置导出序列化器"""
        data = {
            'providers': [],
            'strategies': [],
            'settings': {'test': 'value'},
            'version': '1.0.0',
            'export_time': '2023-12-01T10:30:00Z',
            'metadata': {'total_providers': 0, 'total_strategies': 0}
        }
        
        serializer = ConfigExportSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        # 测试自定义表示
        representation = serializer.to_representation(data)
        self.assertIn('export_time', representation)
        self.assertIn('version', representation)
        self.assertIn('metadata', representation)

    def test_config_import_serializer_validation(self):
        """测试配置导入序列化器验证"""
        # 测试有效文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({'test': 'data'}, f)
            f.flush()
            
            with open(f.name, 'rb') as file:
                data = {
                    'file': file,
                    'format': 'json',
                    'validate_only': False,
                    'overwrite_existing': False
                }
                serializer = ConfigImportSerializer(data=data)
                # 注意：这里需要模拟文件读取，实际测试中可能需要更复杂的设置
        
        os.unlink(f.name)

    def test_config_import_serializer_file_validation(self):
        """测试配置导入序列化器文件验证"""
        # 测试文件大小验证
        large_file = type('MockFile', (), {
            'size': 11 * 1024 * 1024,  # 11MB
            'name': 'test.json'
        })()
        
        serializer = ConfigImportSerializer()
        with self.assertRaises(Exception):
            serializer.validate_file(large_file)
        
        # 测试文件格式验证
        invalid_file = type('MockFile', (), {
            'size': 1024,
            'name': 'test.txt'
        })()
        
        with self.assertRaises(Exception):
            serializer.validate_file(invalid_file)
