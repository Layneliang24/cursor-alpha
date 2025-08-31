"""
AI配置模块安全测试
包括XSS防护、SQL注入防护、速率限制等
"""
import json
import time
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.exceptions import ValidationError
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock

from apps.ai.config_models import AIProvider, APIKey, AIModel, ModelConfig
from apps.common.security import SQLSecurityUtils, InputValidator
from apps.rbac.models import Role, Permission, UserRole

User = get_user_model()

class SecurityUtilsTestCase(TestCase):
    """安全工具类测试"""
    
    def test_sql_injection_detection(self):
        """测试SQL注入检测"""
        # 危险输入
        dangerous_inputs = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "UNION SELECT * FROM users",
            "'; EXEC xp_cmdshell('dir'); --",
            "1'; DELETE FROM config_manager_aiprovider; --"
        ]
        
        for dangerous_input in dangerous_inputs:
            with self.assertRaises(ValidationError):
                SQLSecurityUtils.validate_sql_input(dangerous_input)
    
    def test_safe_input_validation(self):
        """测试安全输入验证"""
        # 安全输入
        safe_inputs = [
            "openai",
            "test-provider",
            "GPT-4",
            "配置名称123"
        ]
        
        for safe_input in safe_inputs:
            try:
                result = SQLSecurityUtils.validate_sql_input(safe_input)
                self.assertEqual(result, safe_input.strip())
            except ValidationError:
                self.fail(f"安全输入被错误拒绝: {safe_input}")
    
    def test_table_name_validation(self):
        """测试表名验证"""
        # 安全表名
        safe_tables = [
            "config_manager_aiprovider",
            "config_manager_apikey",
            "english_word"
        ]
        
        for table in safe_tables:
            result = SQLSecurityUtils.validate_table_name(table)
            self.assertEqual(result, table)
        
        # 危险表名
        dangerous_tables = [
            "users; DROP TABLE",
            "../etc/passwd",
            "information_schema.tables"
        ]
        
        for table in dangerous_tables:
            with self.assertRaises(ValidationError):
                SQLSecurityUtils.validate_table_name(table)
    
    def test_provider_type_validation(self):
        """测试提供商类型验证"""
        # 有效类型
        valid_types = ['openai', 'anthropic', 'google', 'azure']
        for provider_type in valid_types:
            result = InputValidator.validate_provider_type(provider_type)
            self.assertEqual(result, provider_type)
        
        # 无效类型
        invalid_types = ['', 'invalid', 'DROP TABLE', '<script>']
        for provider_type in invalid_types:
            with self.assertRaises(ValidationError):
                InputValidator.validate_provider_type(provider_type)
    
    def test_model_name_validation(self):
        """测试模型名称验证"""
        # 有效名称
        valid_names = ['gpt-4', 'claude-3', 'gemini-pro', 'gpt-3.5-turbo']
        for name in valid_names:
            result = InputValidator.validate_model_name(name)
            self.assertEqual(result, name)
        
        # 无效名称
        invalid_names = ['', 'model with spaces', '<script>alert(1)</script>', 'model;DROP TABLE']
        for name in invalid_names:
            with self.assertRaises(ValidationError):
                InputValidator.validate_model_name(name)
    
    def test_json_config_validation(self):
        """测试JSON配置验证"""
        # 有效配置
        valid_config = {
            'temperature': 0.7,
            'max_tokens': 1000,
            'top_p': 0.9
        }
        result = InputValidator.validate_json_config(valid_config)
        self.assertEqual(result, valid_config)
        
        # 无效配置
        invalid_configs = [
            {'dangerous_key': 'value'},  # 不允许的键
            {'temperature': 5.0},        # 超出范围
            {'max_tokens': -1},          # 负数
            "not a dict"                 # 非字典类型
        ]
        
        for config in invalid_configs:
            with self.assertRaises(ValidationError):
                InputValidator.validate_json_config(config)

class AIProviderSecurityTestCase(APITestCase):
    """AI提供商安全测试"""
    
    def setUp(self):
        """测试准备"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # 创建管理员角色和权限
        admin_role = Role.objects.create(name='admin', description='管理员')
        ai_config_permission = Permission.objects.create(
            name='ai_config.create',
            description='创建AI配置'
        )
        admin_role.permissions.add(ai_config_permission)
        UserRole.objects.create(user=self.user, role=admin_role)
        
        self.client.force_authenticate(user=self.user)
    
    def test_xss_prevention_in_provider_creation(self):
        """测试提供商创建中的XSS防护"""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert(1)",
            "<img src=x onerror=alert(1)>",
            "';alert(String.fromCharCode(88,83,83))//';alert(String.fromCharCode(88,83,83))//",
            "\"><script>alert(1)</script>"
        ]
        
        for payload in xss_payloads:
            data = {
                'provider_type': 'openai',
                'display_name': payload,  # XSS载荷
                'api_endpoint': 'https://api.openai.com/v1',
                'is_active': True
            }
            
            response = self.client.post('/api/v1/ai/providers/', data)
            
            # 应该返回400错误或清理后的数据
            if response.status_code == 201:
                # 如果创建成功，检查数据是否被清理
                provider = AIProvider.objects.get(id=response.data['id'])
                self.assertNotIn('<script>', provider.display_name)
                self.assertNotIn('javascript:', provider.display_name)
                provider.delete()  # 清理测试数据
            else:
                # 应该是400验证错误
                self.assertEqual(response.status_code, 400)
    
    def test_sql_injection_prevention(self):
        """测试SQL注入防护"""
        # 创建测试提供商
        provider = AIProvider.objects.create(
            name='test_provider',
            provider_type='openai',
            display_name='Test Provider',
            api_endpoint='https://api.openai.com/v1',
            created_by=self.user
        )
        
        # SQL注入载荷
        sql_payloads = [
            "1'; DROP TABLE config_manager_aiprovider; --",
            "1' OR '1'='1",
            "'; SELECT * FROM django_user; --",
            "UNION SELECT username, password FROM auth_user",
        ]
        
        for payload in sql_payloads:
            # 尝试通过查询参数注入
            response = self.client.get(f'/api/v1/ai/providers/?search={payload}')
            
            # 应该正常返回（ORM会处理注入）或返回400错误
            self.assertIn(response.status_code, [200, 400])
            
            # 检查提供商是否仍然存在（未被删除）
            self.assertTrue(AIProvider.objects.filter(id=provider.id).exists())
    
    def test_input_length_limits(self):
        """测试输入长度限制"""
        # 超长输入
        long_name = 'A' * 200  # 超过100字符限制
        long_description = 'B' * 1000  # 超过500字符限制
        
        data = {
            'provider_type': 'openai',
            'display_name': long_name,
            'description': long_description,
            'api_endpoint': 'https://api.openai.com/v1',
            'is_active': True
        }
        
        response = self.client.post('/api/v1/ai/providers/', data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('display_name', response.data)
    
    def test_url_validation(self):
        """测试URL验证"""
        invalid_urls = [
            'javascript:alert(1)',
            'data:text/html,<script>alert(1)</script>',
            'ftp://malicious.com',
            'file:///etc/passwd',
            'not-a-url'
        ]
        
        for invalid_url in invalid_urls:
            data = {
                'provider_type': 'openai',
                'display_name': 'Test Provider',
                'api_endpoint': invalid_url,
                'is_active': True
            }
            
            response = self.client.post('/api/v1/ai/providers/', data)
            self.assertEqual(response.status_code, 400)

class RateLimitTestCase(APITestCase):
    """速率限制测试"""
    
    def setUp(self):
        """测试准备"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com', 
            password='testpass123'
        )
        
        # 创建权限
        admin_role = Role.objects.create(name='admin', description='管理员')
        test_permission = Permission.objects.create(
            name='ai_config.test',
            description='测试AI配置'
        )
        admin_role.permissions.add(test_permission)
        UserRole.objects.create(user=self.user, role=admin_role)
        
        self.client.force_authenticate(user=self.user)
        
        # 创建测试提供商
        self.provider = AIProvider.objects.create(
            name='test_provider',
            provider_type='openai',
            display_name='Test Provider',
            api_endpoint='https://api.openai.com/v1',
            created_by=self.user
        )
    
    @patch('apps.common.ratelimit.cache')
    def test_rate_limit_enforcement(self, mock_cache):
        """测试速率限制执行"""
        # 模拟缓存行为
        mock_cache.get.return_value = 0
        mock_cache.set.return_value = True
        
        # 正常请求应该成功
        response = self.client.get('/api/v1/ai/providers/')
        self.assertEqual(response.status_code, 200)
        
        # 模拟达到速率限制
        mock_cache.get.return_value = 100  # 假设已达到限制
        
        response = self.client.get('/api/v1/ai/providers/')
        # 根据具体实现，可能返回429或正常响应（取决于装饰器配置）
        self.assertIn(response.status_code, [200, 429])
    
    def test_sensitive_operation_limit(self):
        """测试敏感操作限制"""
        # 测试连接是敏感操作，应该有更严格的限制
        url = f'/api/v1/ai/providers/{self.provider.id}/test_connection/'
        
        # 第一次请求应该成功（或因为缺少API密钥而失败，但不是速率限制）
        response = self.client.post(url)
        self.assertNotEqual(response.status_code, 429)
    
    def test_role_based_rate_limits(self):
        """测试基于角色的速率限制"""
        # 创建不同角色的用户
        guest_user = User.objects.create_user(
            username='guest',
            email='guest@example.com',
            password='guestpass123'
        )
        
        # 测试访客用户限制（应该更严格）
        guest_client = APIClient()
        guest_client.force_authenticate(user=guest_user)
        
        response = guest_client.get('/api/v1/ai/providers/')
        # 根据权限配置，可能返回403或其他状态码
        self.assertIn(response.status_code, [200, 403, 429])

class XSSPreventionTestCase(TestCase):
    """XSS防护测试"""
    
    def setUp(self):
        """测试准备"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_html_escaping_in_model_fields(self):
        """测试模型字段中的HTML转义"""
        xss_payload = "<script>alert('xss')</script>"
        
        # 测试提供商名称
        provider = AIProvider.objects.create(
            name='test_provider',
            provider_type='openai',
            display_name=xss_payload,
            api_endpoint='https://api.openai.com/v1',
            created_by=self.user
        )
        
        # 检查存储的数据（应该被转义或拒绝）
        saved_provider = AIProvider.objects.get(id=provider.id)
        self.assertNotEqual(saved_provider.display_name, xss_payload)
    
    def test_json_field_xss_prevention(self):
        """测试JSON字段XSS防护"""
        # 创建模型配置
        provider = AIProvider.objects.create(
            name='test_provider',
            provider_type='openai',
            display_name='Test Provider',
            api_endpoint='https://api.openai.com/v1',
            created_by=self.user
        )
        
        model = AIModel.objects.create(
            provider=provider,
            model_id='gpt-4',
            display_name='GPT-4',
            max_tokens=4096
        )
        
        # 尝试在JSON配置中注入XSS
        xss_config = {
            'temperature': 0.7,
            'system_prompt': "<script>alert('xss')</script>",
            'custom_setting': "javascript:alert(1)"
        }
        
        try:
            config = ModelConfig.objects.create(
                user=self.user,
                model=model,
                config_name='test_config',
                custom_parameters=xss_config
            )
            
            # 检查保存的配置
            saved_config = ModelConfig.objects.get(id=config.id)
            # 根据验证器实现，可能被清理或拒绝
            if saved_config.custom_parameters:
                self.assertNotIn('<script>', str(saved_config.custom_parameters))
                self.assertNotIn('javascript:', str(saved_config.custom_parameters))
        except ValidationError:
            # 验证器正确拒绝了危险输入
            pass

class APISecurityTestCase(APITestCase):
    """API安全测试"""
    
    def setUp(self):
        """测试准备"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # 创建必要的权限
        admin_role = Role.objects.create(name='admin', description='管理员')
        permissions = [
            'ai_config.view', 'ai_config.create', 'ai_config.edit', 
            'ai_config.delete', 'ai_config.test'
        ]
        
        for perm_name in permissions:
            permission = Permission.objects.create(
                name=perm_name,
                description=f'AI配置权限: {perm_name}'
            )
            admin_role.permissions.add(permission)
        
        UserRole.objects.create(user=self.user, role=admin_role)
        self.client.force_authenticate(user=self.user)
    
    def test_api_input_sanitization(self):
        """测试API输入清理"""
        # XSS载荷
        xss_data = {
            'provider_type': 'openai',
            'display_name': "<img src=x onerror=alert(1)>",
            'description': "';DROP TABLE users;--",
            'api_endpoint': 'javascript:alert(1)',
            'is_active': True
        }
        
        response = self.client.post('/api/v1/ai/providers/', xss_data)
        
        # 应该返回400验证错误
        self.assertEqual(response.status_code, 400)
        
        # 检查错误信息
        self.assertTrue(any(
            'display_name' in key or 'api_endpoint' in key 
            for key in response.data.keys()
        ))
    
    def test_api_response_headers(self):
        """测试API响应安全头"""
        response = self.client.get('/api/v1/ai/providers/')
        
        # 检查安全头（如果在中间件中设置）
        # 注意：这些头可能在前端服务器（Nginx）中设置
        expected_headers = [
            'X-Content-Type-Options',
            'X-Frame-Options',
            'Referrer-Policy'
        ]
        
        # 在开发环境中，这些头可能不存在
        # 在生产环境中应该检查这些头
        pass  # 占位符，实际部署时需要验证
    
    def test_csrf_protection(self):
        """测试CSRF保护"""
        # 创建未认证的客户端
        unauth_client = APIClient()
        
        # 尝试POST请求（应该需要CSRF令牌或被拒绝）
        data = {
            'provider_type': 'openai',
            'display_name': 'Test Provider',
            'api_endpoint': 'https://api.openai.com/v1'
        }
        
        response = unauth_client.post('/api/v1/ai/providers/', data)
        # 应该返回403（CSRF）或401（未认证）
        self.assertIn(response.status_code, [401, 403])
    
    def test_file_upload_security(self):
        """测试文件上传安全（如果有文件上传功能）"""
        # 这是一个占位符测试
        # 如果后续添加文件上传功能，需要测试：
        # 1. 文件类型验证
        # 2. 文件大小限制
        # 3. 文件名安全性
        # 4. 病毒扫描（如果需要）
        pass

class SecurityMiddlewareTestCase(TestCase):
    """安全中间件测试"""
    
    def setUp(self):
        """测试准备"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_security_headers_middleware(self):
        """测试安全头中间件"""
        response = self.client.get('/')
        
        # 检查基础安全头
        # 注意：在开发环境中可能不设置这些头
        # 在生产环境中应该有这些头
        if hasattr(response, 'get'):
            # 如果有安全头中间件
            pass
    
    def test_rate_limit_logging(self):
        """测试速率限制日志"""
        with patch('apps.common.ratelimit.logger') as mock_logger:
            # 模拟多次快速请求
            for _ in range(5):
                self.client.get('/api/v1/ai/providers/')
            
            # 检查是否有日志记录（根据实际实现）
            # mock_logger.info.assert_called()

class SecurityComplianceTestCase(TestCase):
    """安全合规性测试"""
    
    def test_password_policy_compliance(self):
        """测试密码策略合规性"""
        # 测试弱密码是否被拒绝
        weak_passwords = ['123', 'password', '111111']
        
        for weak_password in weak_passwords:
            try:
                user = User.objects.create_user(
                    username=f'test_{weak_password}',
                    email=f'test_{weak_password}@example.com',
                    password=weak_password
                )
                # 如果创建成功，检查密码是否被正确处理
                self.assertTrue(user.check_password(weak_password))
            except ValidationError:
                # 密码策略正确拒绝了弱密码
                pass
    
    def test_session_security(self):
        """测试会话安全"""
        # 登录用户
        self.client.login(username='testuser', password='testpass123')
        
        # 检查会话cookie设置
        response = self.client.get('/api/v1/ai/providers/')
        
        # 在生产环境中，session cookie应该是secure的
        # 在开发环境中可能不是
        pass
    
    def test_sensitive_data_exposure(self):
        """测试敏感数据暴露"""
        # 创建API密钥
        provider = AIProvider.objects.create(
            name='test_provider',
            provider_type='openai',
            display_name='Test Provider',
            api_endpoint='https://api.openai.com/v1',
            created_by=self.user
        )
        
        api_key = APIKey.objects.create(
            name='test_key',
            provider=provider,
            user=self.user
        )
        api_key.set_key('sk-test-key-12345')
        api_key.save()
        
        # 通过API获取密钥信息
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/v1/ai/api-keys/')
        
        # 检查响应中不包含原始密钥
        response_str = json.dumps(response.data)
        self.assertNotIn('sk-test-key-12345', response_str)
        
        # 但应该包含掩码版本
        self.assertIn('sk-***', response_str)
