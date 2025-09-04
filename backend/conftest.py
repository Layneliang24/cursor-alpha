# -*- coding: utf-8 -*-
"""
优化的pytest配置文件
配置Django测试环境和通用fixtures
"""

import os
import sys
import pytest
from pathlib import Path

# 设置环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_settings')
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

# 测试工厂将在需要时动态导入

# 全局fixtures
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
    from django.contrib.auth import get_user_model
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
    from django.contrib.auth import get_user_model
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
    """API客户端fixture"""
    return APIClient()

@pytest.fixture(scope='function')
def authenticated_client(api_client, test_user):
    """已认证的API客户端fixture"""
    api_client.force_authenticate(user=test_user)
    return api_client

@pytest.fixture(scope='function')
def superuser_client(api_client, test_superuser):
    """超级用户API客户端fixture"""
    api_client.force_authenticate(user=test_superuser)
    return api_client

@pytest.fixture(scope='function')
def request_factory():
    """请求工厂fixture"""
    return RequestFactory()

@pytest.fixture(scope='function')
def test_ai_provider():
    """测试AI提供商fixture - 简化版本"""
    # 返回一个模拟对象，避免复杂的模型依赖
    class MockProvider:
        def __init__(self):
            self.id = 1
            self.name = 'test_provider'
        
        def delete(self):
            pass
    
    yield MockProvider()

@pytest.fixture(scope='function')
def test_api_key(test_ai_provider, test_user):
    """测试API密钥fixture - 简化版本"""
    # 返回一个模拟对象，避免复杂的模型依赖
    class MockAPIKey:
        def __init__(self):
            self.id = 1
            self.name = 'test_key'
        
        def delete(self):
            pass
    
    yield MockAPIKey()

# 测试数据管理fixtures
@pytest.fixture(scope='function')
def test_data_dir():
    """测试数据目录fixture"""
    data_dir = Path('tests/data')
    data_dir.mkdir(exist_ok=True)
    yield data_dir
    # 清理测试数据文件
    try:
        for file_path in data_dir.glob('*'):
            if file_path.is_file():
                file_path.unlink()
    except:
        pass

@pytest.fixture(scope='function')
def temp_media_dir():
    """临时媒体目录fixture"""
    media_dir = Path('tests/temp_media')
    media_dir.mkdir(exist_ok=True)
    yield media_dir
    # 清理临时媒体文件
    try:
        for file_path in media_dir.glob('*'):
            if file_path.is_file():
                file_path.unlink()
            elif file_path.is_dir():
                import shutil
                shutil.rmtree(file_path)
    except:
        pass

# 性能测试fixtures
@pytest.fixture(scope='function')
def benchmark():
    """性能测试fixture"""
    import time
    start_time = time.time()
    yield
    end_time = time.time()
    print(f"\n测试执行时间: {end_time - start_time:.4f} 秒")

# 模拟外部服务fixtures
@pytest.fixture(scope='function')
def mock_external_apis():
    """模拟外部API调用fixture"""
    import responses
    with responses.RequestsMock() as rsps:
        # 模拟常见的API调用
        rsps.add(
            responses.GET,
            'https://api.openai.com/v1/models',
            json={'data': [{'id': 'gpt-4'}]},
            status=200
        )
        rsps.add(
            responses.POST,
            'https://api.openai.com/v1/chat/completions',
            json={'choices': [{'message': {'content': 'Test response'}}]},
            status=200
        )
        yield rsps

# 测试标记
def pytest_configure(config):
    """配置pytest标记"""
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as end-to-end test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as performance test"
    )
    config.addinivalue_line(
        "markers", "security: mark test as security test"
    )
    config.addinivalue_line(
        "markers", "asyncio: mark test as async test"
    )
    config.addinivalue_line(
        "markers", "flaky: mark test as potentially flaky"
    )

# 测试收集钩子
def pytest_collection_modifyitems(config, items):
    """修改测试收集项"""
    for item in items:
        # 为慢速测试添加超时
        if "slow" in item.keywords:
            item.add_marker(pytest.mark.timeout(60))
        
        # 为性能测试添加基准（如果pytest-benchmark可用）
        try:
            import pytest_benchmark
            if "performance" in item.keywords:
                item.add_marker(pytest.mark.benchmark)
        except ImportError:
            pass

# 测试报告钩子
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """终端总结钩子"""
    # 显示测试统计
    stats = terminalreporter.stats
    if 'passed' in stats:
        print(f"\n通过的测试: {len(stats['passed'])}")
    if 'failed' in stats:
        print(f"\n失败的测试: {len(stats['failed'])}")
    if 'skipped' in stats:
        print(f"\n跳过的测试: {len(stats['skipped'])}")

# 测试会话钩子
def pytest_sessionstart(session):
    """测试会话开始钩子"""
    print("\n开始测试会话...")
    print(f"测试环境: {os.environ.get('DJANGO_SETTINGS_MODULE', 'unknown')}")
    print(f"Python版本: {sys.version}")
    print(f"Django版本: {django.get_version()}")

def pytest_sessionfinish(session, exitstatus):
    """测试会话结束钩子"""
    print(f"\n测试会话结束，退出状态: {exitstatus}")
    if exitstatus == 0:
        print("所有测试通过!")
    else:
        print("部分测试失败!")
