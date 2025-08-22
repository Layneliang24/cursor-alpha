"""
AI模块单元测试
测试AI相关功能的正确性
"""

import pytest
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


class AIModuleTestCase(TestCase):
    """AI模块基础测试用例"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_ai_conversations_endpoint_exists(self):
        """测试AI对话端点存在"""
        response = self.client.get('/api/v1/ai/ai/conversations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], 'ai placeholder')
        self.assertEqual(data['data'], [])
    
    def test_ai_conversations_requires_authentication(self):
        """测试AI对话端点需要认证"""
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/v1/ai/ai/conversations/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_ai_conversations_viewset_structure(self):
        """测试AI对话视图集结构"""
        from apps.ai.views import ConversationViewSet
        # 检查视图集类是否存在
        self.assertTrue(hasattr(ConversationViewSet, 'list'))
        self.assertTrue(hasattr(ConversationViewSet, 'permission_classes'))
    
    def test_ai_conversations_permission_classes(self):
        """测试AI对话权限类"""
        from apps.ai.views import ConversationViewSet
        from rest_framework.permissions import IsAuthenticated
        
        # 检查权限类设置
        self.assertIn(IsAuthenticated, ConversationViewSet.permission_classes)


class AIAPITestCase(TestCase):
    """AI API测试用例"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_ai_conversations_list_method(self):
        """测试AI对话列表方法"""
        response = self.client.get('/api/v1/ai/ai/conversations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证响应格式
        data = response.json()
        self.assertIn('success', data)
        self.assertIn('message', data)
        self.assertIn('data', data)
        self.assertTrue(data['success'])
    
    def test_ai_module_initialization(self):
        """测试AI模块初始化"""
        from apps.ai.apps import AiConfig
        # 检查AI应用配置
        self.assertEqual(AiConfig.name, 'ai')
        self.assertEqual(AiConfig.default_auto_field, 'django.db.models.BigAutoField')


class AIIntegrationTestCase(TestCase):
    """AI模块集成测试用例"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_ai_module_with_other_modules(self):
        """测试AI模块与其他模块的集成"""
        # 测试AI模块是否影响其他模块
        response = self.client.get('/api/v1/english/words/')
        self.assertIn(response.status_code, [200, 401, 403, 404])
    
    def test_ai_conversations_error_handling(self):
        """测试AI对话错误处理"""
        # 测试无效请求的处理
        response = self.client.post('/api/v1/ai/ai/conversations/', {'invalid': 'data'})
        # 应该返回405，因为视图集没有实现create方法
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


if __name__ == '__main__':
    pytest.main([__file__])
