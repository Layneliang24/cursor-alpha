# -*- coding: utf-8 -*-
"""
pytest配置文件
配置Django测试环境和通用fixtures
"""

import os
import sys
import pytest
from pathlib import Path

# 添加backend目录到Python路径
project_root = Path(__file__).parent.parent
backend_dir = project_root / 'backend'
sys.path.insert(0, str(backend_dir))

# 设置环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.test_settings')
os.environ.setdefault('TESTING', 'true')

# 导入Django设置
import django
from django.conf import settings

# 配置Django
if not settings.configured:
    django.setup()

# 导入Django测试工具
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    """数据库设置fixture"""
    with django_db_blocker.unblock():
        # 确保使用测试数据库设置
        pass


@pytest.fixture(scope='function')
def db_access_without_rollback_and_truncate(django_db_setup, django_db_blocker):
    """数据库访问fixture，不进行回滚和截断"""
    django_db_blocker.unblock()
    yield
    django_db_blocker.restore()


@pytest.fixture(scope='function')
def test_user():
    """测试用户fixture"""
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
def authenticated_user(test_user):
    """已认证用户fixture"""
    return test_user


@pytest.fixture(scope='function')
def authenticated_superuser(test_superuser):
    """已认证超级用户fixture"""
    return test_superuser


@pytest.fixture(scope='function')
def api_client():
    """API测试客户端fixture"""
    return APIClient()


@pytest.fixture(scope='function')
def authenticated_api_client(api_client, authenticated_user):
    """已认证的API测试客户端fixture"""
    api_client.force_authenticate(user=authenticated_user)
    return api_client


@pytest.fixture(scope='function')
def superuser_api_client(api_client, authenticated_superuser):
    """超级用户API测试客户端fixture"""
    api_client.force_authenticate(user=authenticated_superuser)
    return api_client


@pytest.fixture(scope='function')
def request_factory():
    """请求工厂fixture"""
    return RequestFactory()


@pytest.fixture(scope='function')
def test_article_data():
    """测试文章数据fixture"""
    return {
        'title': 'Test Article',
        'content': 'This is a test article content.',
        'summary': 'Test summary',
        'category': 'test',
        'tags': ['test', 'article']
    }


@pytest.fixture(scope='function')
def test_news_data():
    """测试新闻数据fixture"""
    return {
        'title': 'Test News',
        'content': 'This is test news content.',
        'summary': 'Test news summary',
        'source': 'test_source',
        'category': 'test',
        'publish_date': '2024-01-01'
    }


@pytest.fixture(scope='function')
def test_typing_word_data():
    """测试打字单词数据fixture"""
    return {
        'word': 'test',
        'translation': '测试',
        'pronunciation': '/test/',
        'difficulty': 'easy',
        'category': 'test'
    }


@pytest.fixture(scope='function')
def test_settings():
    """测试设置fixture"""
    return {
        'TESTING': True,
        'DEBUG': False,
        'DATABASES': {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        }
    }


@pytest.fixture(scope='function')
def setup_test_environment():
    """测试环境设置fixture"""
    # 设置测试环境变量
    os.environ['TESTING'] = 'true'
    os.environ['DEBUG'] = 'false'
    
    yield
    
    # 清理测试环境
    if 'TESTING' in os.environ:
        del os.environ['TESTING']
    if 'DEBUG' in os.environ:
        del os.environ['DEBUG']


def pytest_configure(config):
    """pytest配置钩子"""
    # 定义自定义标记
    config.addinivalue_line(
        "markers", "slow: 慢速测试"
    )
    config.addinivalue_line(
        "markers", "integration: 集成测试"
    )
    config.addinivalue_line(
        "markers", "api: API测试"
    )
    config.addinivalue_line(
        "markers", "frontend: 前端测试"
    )
    config.addinivalue_line(
        "markers", "regression: 回归测试"
    )
    config.addinivalue_line(
        "markers", "new_feature: 新功能测试"
    )
    config.addinivalue_line(
        "markers", "skip_if_no_database: 如果没有数据库则跳过"
    )
    config.addinivalue_line(
        "markers", "skip_if_no_external_api: 如果没有外部API则跳过"
    )


def pytest_collection_modifyitems(config, items):
    """测试收集修改钩子"""
    # 根据文件路径自动标记测试
    for item in items:
        # 根据文件路径标记
        if 'regression' in str(item.fspath):
            item.add_marker(pytest.mark.regression)
        if 'new_features' in str(item.fspath):
            item.add_marker(pytest.mark.new_feature)
        
        # 根据函数名标记
        if 'test_api' in item.name:
            item.add_marker(pytest.mark.api)
        if 'test_frontend' in item.name:
            item.add_marker(pytest.mark.frontend)
        if 'test_integration' in item.name:
            item.add_marker(pytest.mark.integration)
