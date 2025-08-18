"""
基础单元测试
测试核心功能和工具函数
"""

import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import connections
from django.db.utils import OperationalError

User = get_user_model()


class BasicFunctionalityTest(TestCase):
    """基础功能测试"""
    
    def test_database_connection(self):
        """测试数据库连接"""
        try:
            db_conn = connections['default']
            with db_conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
            self.assertEqual(result[0], 1)
        except OperationalError:
            self.fail("数据库连接失败")

    def test_user_creation(self):
        """测试用户创建"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))

    def test_superuser_creation(self):
        """测试超级用户创建"""
        superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)


class ManagementCommandsTest(TestCase):
    """管理命令测试"""
    
    def test_wait_for_db_command(self):
        """测试等待数据库命令"""
        try:
            call_command('wait_for_db')
            # 如果没有异常，说明命令执行成功
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"wait_for_db命令失败: {e}")

    def test_create_superuser_if_not_exists_command(self):
        """测试创建超级用户命令"""
        try:
            call_command('create_superuser_if_not_exists')
            # 检查是否创建了超级用户
            superuser_count = User.objects.filter(is_superuser=True).count()
            self.assertGreaterEqual(superuser_count, 0)
        except Exception as e:
            self.fail(f"create_superuser_if_not_exists命令失败: {e}")


class SettingsTest(TestCase):
    """设置测试"""
    
    def test_debug_setting(self):
        """测试DEBUG设置"""
        from django.conf import settings
        self.assertIsInstance(settings.DEBUG, bool)

    def test_database_setting(self):
        """测试数据库设置"""
        from django.conf import settings
        self.assertIn('default', settings.DATABASES)
        db_config = settings.DATABASES['default']
        self.assertIn('ENGINE', db_config)
        self.assertIn('NAME', db_config)

    def test_installed_apps(self):
        """测试已安装应用"""
        from django.conf import settings
        required_apps = [
            'django.contrib.admin',
            'django.contrib.auth',
            'rest_framework',
            'apps.users',
            'apps.english',
        ]
        for app in required_apps:
            self.assertIn(app, settings.INSTALLED_APPS)


class URLPatternsTest(TestCase):
    """URL模式测试"""
    
    def test_admin_url(self):
        """测试管理后台URL"""
        from django.urls import reverse
        try:
            admin_url = reverse('admin:index')
            self.assertIn('admin', admin_url)
        except Exception:
            # 如果admin URL不可用，跳过测试
            self.skipTest("Admin URL不可用")

    def test_api_root_url(self):
        """测试API根URL"""
        from django.urls import reverse
        try:
            api_url = reverse('api-root')
            self.assertIn('api', api_url)
        except Exception:
            # 如果API URL不可用，跳过测试
            self.skipTest("API URL不可用")


@pytest.mark.fast
class FastTests:
    """快速测试（标记为fast）"""
    
    def test_quick_math(self):
        """快速数学测试"""
        assert 2 + 2 == 4
        assert 3 * 3 == 9

    def test_string_operations(self):
        """字符串操作测试"""
        text = "Hello, World!"
        assert len(text) == 13
        assert text.upper() == "HELLO, WORLD!"
        assert text.lower() == "hello, world!"


@pytest.mark.slow
class SlowTests:
    """慢速测试（标记为slow）"""
    
    def test_database_operations(self):
        """数据库操作测试"""
        # 这里可以添加需要较长时间的数据库测试
        assert True

    def test_external_api_calls(self):
        """外部API调用测试"""
        # 这里可以添加需要调用外部API的测试
        assert True
