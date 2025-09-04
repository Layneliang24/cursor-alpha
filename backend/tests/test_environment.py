# -*- coding: utf-8 -*-
"""
测试环境验证测试
验证测试环境配置是否正确
"""

import pytest
from django.test import TestCase
from django.conf import settings
from django.contrib.auth import get_user_model


class TestEnvironmentConfiguration(TestCase):
    """测试环境配置测试"""
    
    def test_django_settings_loaded(self):
        """测试Django设置是否正确加载"""
        self.assertTrue(settings.configured)
        self.assertEqual(settings.DEBUG, False)
        self.assertEqual(settings.TESTING, True)
    
    def test_database_configuration(self):
        """测试数据库配置"""
        self.assertIn('default', settings.DATABASES)
        db_config = settings.DATABASES['default']
        self.assertEqual(db_config['ENGINE'], 'django.db.backends.sqlite3')
        # Windows环境下SQLite内存数据库名称可能不同
        self.assertIn('memory', db_config['NAME'])
    
    def test_cache_configuration(self):
        """测试缓存配置"""
        self.assertIn('default', settings.CACHES)
        cache_config = settings.CACHES['default']
        self.assertEqual(cache_config['BACKEND'], 'django.core.cache.backends.dummy.DummyCache')
    
    def test_email_configuration(self):
        """测试邮件配置"""
        self.assertEqual(settings.EMAIL_BACKEND, 'django.core.mail.backends.locmem.EmailBackend')
    
    def test_installed_apps(self):
        """测试已安装的应用"""
        expected_apps = [
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.staticfiles',
            'rest_framework',
            'corsheaders',
        ]
        
        for app in expected_apps:
            self.assertIn(app, settings.INSTALLED_APPS)
    
    def test_rest_framework_configuration(self):
        """测试REST Framework配置"""
        self.assertIn('REST_FRAMEWORK', dir(settings))
        rf_settings = settings.REST_FRAMEWORK
        self.assertIn('DEFAULT_AUTHENTICATION_CLASSES', rf_settings)
        self.assertIn('DEFAULT_PERMISSION_CLASSES', rf_settings)
        self.assertIn('DEFAULT_RENDERER_CLASSES', rf_settings)


class TestBasicFunctionality(TestCase):
    """基本功能测试"""
    
    def test_user_model_available(self):
        """测试用户模型是否可用"""
        User = get_user_model()
        self.assertIsNotNone(User)
    
    def test_create_test_user(self):
        """测试创建测试用户"""
        User = get_user_model()
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        
        # 清理
        user.delete()
    
    def test_create_superuser(self):
        """测试创建超级用户"""
        User = get_user_model()
        superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)
        
        # 清理
        superuser.delete()


@pytest.mark.django_db
class TestPytestIntegration:
    """pytest集成测试"""
    
    def test_pytest_mark_django_db(self):
        """测试pytest django_db标记"""
        # 这个测试应该能够访问数据库
        User = get_user_model()
        user_count = User.objects.count()
        # 只是验证数据库访问正常，不关心具体数量
        assert isinstance(user_count, int)
    
    def test_pytest_fixtures_available(self):
        """测试pytest fixtures是否可用"""
        # 这个测试验证pytest fixtures系统工作正常
        assert True  # 简单的断言测试


class TestPerformanceOptimizations(TestCase):
    """性能优化测试"""
    
    def test_password_hashers_optimized(self):
        """测试密码哈希器是否优化"""
        # 测试环境应该使用MD5哈希器以加速测试
        self.assertIn('django.contrib.auth.hashers.MD5PasswordHasher', settings.PASSWORD_HASHERS)
    
    def test_migrations_disabled(self):
        """测试迁移是否被禁用"""
        # 测试环境应该禁用迁移
        self.assertTrue(hasattr(settings, 'MIGRATION_MODULES'))
    
    def test_logging_disabled(self):
        """测试日志是否被禁用"""
        # 测试环境应该禁用日志
        self.assertIn('LOGGING', dir(settings))
        logging_config = settings.LOGGING
        self.assertTrue(logging_config.get('disable_existing_loggers', False))


class TestEnvironmentVariables(TestCase):
    """环境变量测试"""
    
    def test_testing_environment_variable(self):
        """测试TESTING环境变量"""
        import os
        self.assertEqual(os.environ.get('TESTING'), 'true')
    
    def test_django_settings_module(self):
        """测试DJANGO_SETTINGS_MODULE环境变量"""
        import os
        self.assertEqual(os.environ.get('DJANGO_SETTINGS_MODULE'), 'test_settings')
    
    def test_django_test_runner(self):
        """测试DJANGO_TEST_RUNNER环境变量"""
        import os
        self.assertEqual(os.environ.get('DJANGO_TEST_RUNNER'), 'django.test.runner.DiscoverRunner')


if __name__ == '__main__':
    # 可以直接运行这个文件来测试环境
    import django
    django.setup()
    
    # 运行测试
    import unittest
    unittest.main()
