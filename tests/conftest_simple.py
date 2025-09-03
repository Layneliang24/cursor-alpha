# -*- coding: utf-8 -*-
"""
简化的conftest.py文件
避免在导入时进行Django设置，只在需要时配置
"""

import pytest
import os
import sys
from pathlib import Path

# 基本pytest配置
pytest_plugins = []

# 延迟导入Django相关模块
def get_django_components():
    """延迟获取Django组件"""
    try:
        # 设置Django环境
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.test_settings_simple')
        
        import django
        if not django.conf.settings.configured:
            django.setup()
        
        from django.test import TestCase, RequestFactory
        from django.contrib.auth import get_user_model
        from rest_framework.test import APIClient
        
        return {
            'TestCase': TestCase,
            'RequestFactory': RequestFactory,
            'get_user_model': get_user_model,
            'APIClient': APIClient,
            'django_available': True
        }
    except Exception as e:
        return {
            'django_available': False,
            'error': str(e)
        }

# 全局变量，延迟初始化
_django_components = None

def get_django_component(name):
    """获取Django组件"""
    global _django_components
    if _django_components is None:
        _django_components = get_django_components()
    
    if not _django_components.get('django_available', False):
        pytest.skip(f"Django不可用: {_django_components.get('error', 'Unknown error')}")
    
    return _django_components.get(name)

# 基本fixtures，不依赖Django
@pytest.fixture(scope='session')
def test_environment():
    """测试环境信息"""
    return {
        'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        'working_directory': str(Path.cwd()),
        'django_available': get_django_component('django_available') if _django_components else False
    }

# Django相关fixtures，延迟加载
@pytest.fixture(scope='function')
def test_user():
    """测试用户fixture"""
    get_user_model = get_django_component('get_user_model')
    User = get_user_model()
    
    user = User.objects.create_user(
        username='test_user',
        email='test@example.com',
        password='testpass123'
    )
    yield user
    # 清理测试用户
    try:
        user.delete()
    except:
        pass

@pytest.fixture(scope='function')
def test_superuser():
    """测试超级用户fixture"""
    get_user_model = get_django_component('get_user_model')
    User = get_user_model()
    
    user = User.objects.create_superuser(
        username='test_superuser',
        email='super@example.com',
        password='testpass123'
    )
    yield user
    # 清理测试超级用户
    try:
        user.delete()
    except:
        pass

@pytest.fixture(scope='function')
def api_client():
    """API测试客户端fixture"""
    APIClient = get_django_component('APIClient')
    return APIClient()

@pytest.fixture(scope='function')
def request_factory():
    """请求工厂fixture"""
    RequestFactory = get_django_component('RequestFactory')
    return RequestFactory()

# 测试数据fixtures
@pytest.fixture(scope='function')
def test_article_data():
    """测试文章数据fixture"""
    return {
        'title': 'Test Article',
        'content': 'This is a test article content.',
        'summary': 'Test summary',
        'author': 'Test Author'
    }

@pytest.fixture(scope='function')
def test_user_data():
    """测试用户数据fixture"""
    return {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass123',
        'first_name': 'Test',
        'last_name': 'User'
    }

