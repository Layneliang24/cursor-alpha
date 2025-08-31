"""
API密钥加密存储功能测试
"""

import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.ai.config_models import AIProvider, APIKey, AIProviderType

User = get_user_model()


class APIKeyEncryptionTest(TestCase):
    """API密钥加密存储测试"""
    
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
            base_url='https://api.test.com/v1',
            is_active=True
        )
    
    def test_api_key_encryption_storage(self):
        """测试API密钥加密存储"""
        # 创建API密钥
        api_key = APIKey.objects.create(
            provider=self.provider,
            user=self.user,
            name='Test Key'
        )
        
        # 设置原始密钥
        raw_key = 'sk-test1234567890abcdef'
        api_key.set_key(raw_key)
        api_key.save()
        
        # 验证加密存储
        # 重新从数据库获取以确保数据已持久化
        saved_key = APIKey.objects.get(id=api_key.id)
        
        # 验证解密功能
        self.assertEqual(saved_key.get_key(), raw_key)
        
        # 验证掩码显示
        expected_masked = 'sk-t...cdef'
        self.assertEqual(saved_key.masked_key, expected_masked)
        
        # 验证前缀生成
        self.assertEqual(saved_key.key_prefix, expected_masked)
    
    def test_api_key_masking(self):
        """测试API密钥掩码显示"""
        api_key = APIKey.objects.create(
            provider=self.provider,
            user=self.user,
            name='Test Key 2'
        )
        
        # 测试短密钥
        short_key = 'sk-123'
        api_key.set_key(short_key)
        self.assertEqual(api_key.masked_key, 'sk-1***')
        
        # 测试长密钥
        long_key = 'sk-very-long-api-key-1234567890'
        api_key.set_key(long_key)
        self.assertEqual(api_key.masked_key, 'sk-v...7890')
    
    def test_encrypted_field_not_readable(self):
        """测试加密字段在数据库中不可读"""
        api_key = APIKey.objects.create(
            provider=self.provider,
            user=self.user,
            name='Test Key 3'
        )
        
        raw_key = 'sk-secret123456789'
        api_key.set_key(raw_key)
        api_key.save()
        
        # 验证数据库中存储的不是原始密钥
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT encrypted_key FROM ai_api_keys WHERE id = %s", [api_key.id])
        stored_value = cursor.fetchone()[0]
        
        # 加密后的数据不应该等于原始密钥
        self.assertNotEqual(stored_value, raw_key)
        
        # 但解密后应该等于原始密钥
        self.assertEqual(api_key.get_key(), raw_key)
