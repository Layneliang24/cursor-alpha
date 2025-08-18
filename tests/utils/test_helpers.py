# -*- coding: utf-8 -*-
"""
测试辅助函数模块
提供常用的测试工具函数，简化测试用例编写
"""

import json
import os
import random
import string
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from unittest.mock import Mock, patch

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from rest_framework.test import APIClient

User = get_user_model()


class TestDataFactory:
    """测试数据工厂类"""
    
    @staticmethod
    def create_user_data(**kwargs) -> Dict[str, Any]:
        """创建用户测试数据"""
        default_data = {
            'username': f'test_user_{random.randint(1000, 9999)}',
            'email': f'test{random.randint(1000, 9999)}@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
        }
        default_data.update(kwargs)
        return default_data
    
    @staticmethod
    def create_article_data(**kwargs) -> Dict[str, Any]:
        """创建文章测试数据"""
        default_data = {
            'title': f'Test Article {random.randint(1000, 9999)}',
            'content': f'This is test content {random.randint(1000, 9999)}',
            'summary': f'Test summary {random.randint(1000, 9999)}',
            'category': 'test',
        }
        default_data.update(kwargs)
        return default_data
    
    @staticmethod
    def create_news_data(**kwargs) -> Dict[str, Any]:
        """创建新闻测试数据"""
        default_data = {
            'title': f'Test News {random.randint(1000, 9999)}',
            'content': f'This is test news content {random.randint(1000, 9999)}',
            'summary': f'Test news summary {random.randint(1000, 9999)}',
            'source': 'test_source',
            'category': 'test',
            'word_count': random.randint(100, 500),
        }
        default_data.update(kwargs)
        return default_data
    
    @staticmethod
    def create_typing_word_data(**kwargs) -> Dict[str, Any]:
        """创建打字练习单词测试数据"""
        default_data = {
            'word': f'test{random.randint(1000, 9999)}',
            'translation': f'测试{random.randint(1000, 9999)}',
            'difficulty': random.choice(['easy', 'medium', 'hard']),
            'category': 'test',
        }
        default_data.update(kwargs)
        return default_data


class TestUserManager:
    """测试用户管理类"""
    
    @staticmethod
    def create_test_user(**kwargs) -> User:
        """创建测试用户"""
        user_data = TestDataFactory.create_user_data(**kwargs)
        user = User.objects.create_user(**user_data)
        return user
    
    @staticmethod
    def create_test_superuser(**kwargs) -> User:
        """创建测试超级用户"""
        user_data = TestDataFactory.create_user_data(**kwargs)
        user_data['is_staff'] = True
        user_data['is_superuser'] = True
        user = User.objects.create_superuser(**user_data)
        return user
    
    @staticmethod
    def login_user(client: Client, user: User) -> bool:
        """用户登录"""
        return client.login(username=user.username, password='testpass123')
    
    @staticmethod
    def login_api_user(api_client: APIClient, user: User) -> bool:
        """API用户登录"""
        # 这里需要根据实际的认证方式调整
        # 假设使用JWT token认证
        try:
            response = api_client.post('/api/auth/login/', {
                'username': user.username,
                'password': 'testpass123'
            })
            if response.status_code == 200:
                token = response.data.get('token')
                if token:
                    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
                    return True
        except Exception:
            pass
        return False


class TestDatabaseManager:
    """测试数据库管理类"""
    
    @staticmethod
    def clean_test_data():
        """清理测试数据"""
        # 清理用户数据
        User.objects.filter(username__startswith='test_user_').delete()
        User.objects.filter(email__startswith='test').delete()
        
        # 清理其他测试数据
        # 这里需要根据实际的数据模型调整
        
    @staticmethod
    def create_test_fixtures():
        """创建测试数据夹具"""
        fixtures = {}
        
        # 创建测试用户
        test_user = TestUserManager.create_test_user()
        fixtures['test_user'] = test_user
        
        # 创建测试超级用户
        test_superuser = TestUserManager.create_test_superuser()
        fixtures['test_superuser'] = test_superuser
        
        return fixtures


class TestResponseValidator:
    """测试响应验证类"""
    
    @staticmethod
    def validate_success_response(response, expected_status_code: int = 200):
        """验证成功响应"""
        assert response.status_code == expected_status_code
        if hasattr(response, 'data'):
            assert 'success' in response.data or 'data' in response.data
    
    @staticmethod
    def validate_error_response(response, expected_status_code: int = 400):
        """验证错误响应"""
        assert response.status_code == expected_status_code
        if hasattr(response, 'data'):
            assert 'error' in response.data or 'message' in response.data
    
    @staticmethod
    def validate_pagination_response(response):
        """验证分页响应"""
        assert response.status_code == 200
        if hasattr(response, 'data'):
            data = response.data
            assert 'count' in data or 'total' in data
            assert 'results' in data or 'items' in data


class TestMockHelper:
    """测试模拟辅助类"""
    
    @staticmethod
    def mock_external_api(api_name: str, return_value: Any = None):
        """模拟外部API调用"""
        if return_value is None:
            return_value = {'success': True, 'data': 'mocked_data'}
        
        return patch(f'alpha.apps.english.services.{api_name}', return_value=return_value)
    
    @staticmethod
    def mock_file_upload(file_path: str = None):
        """模拟文件上传"""
        if file_path is None:
            file_path = 'tests/resources/fixtures/test_file.txt'
        
        mock_file = Mock()
        mock_file.name = 'test_file.txt'
        mock_file.size = 1024
        mock_file.content_type = 'text/plain'
        
        return mock_file


class TestPerformanceHelper:
    """测试性能辅助类"""
    
    @staticmethod
    def measure_execution_time(func, *args, **kwargs):
        """测量函数执行时间"""
        start_time = datetime.now()
        result = func(*args, **kwargs)
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        return result, execution_time
    
    @staticmethod
    def assert_performance_threshold(execution_time: float, threshold: float = 1.0):
        """断言性能阈值"""
        assert execution_time <= threshold, f"执行时间 {execution_time}s 超过阈值 {threshold}s"


class TestDataGenerator:
    """测试数据生成器"""
    
    @staticmethod
    def generate_random_string(length: int = 10) -> str:
        """生成随机字符串"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    @staticmethod
    def generate_random_email() -> str:
        """生成随机邮箱"""
        username = ''.join(random.choices(string.ascii_lowercase, k=8))
        domain = ''.join(random.choices(string.ascii_lowercase, k=6))
        return f"{username}@{domain}.com"
    
    @staticmethod
    def generate_random_date(start_date: datetime = None, end_date: datetime = None) -> datetime:
        """生成随机日期"""
        if start_date is None:
            start_date = datetime.now() - timedelta(days=365)
        if end_date is None:
            end_date = datetime.now()
        
        time_between_dates = end_date - start_date
        days_between_dates = time_between_dates.days
        random_number_of_days = random.randrange(days_between_dates)
        random_date = start_date + timedelta(days=random_number_of_days)
        return random_date


# 常用测试装饰器
def skip_if_no_database(func):
    """如果没有数据库则跳过测试"""
    return pytest.mark.skipif(
        os.getenv('SKIP_DATABASE_TESTS') == 'true',
        reason="数据库测试被跳过"
    )(func)


def skip_if_no_external_api(func):
    """如果没有外部API则跳过测试"""
    return pytest.mark.skipif(
        os.getenv('SKIP_EXTERNAL_API_TESTS') == 'true',
        reason="外部API测试被跳过"
    )(func)


def slow_test(func):
    """标记为慢速测试"""
    return pytest.mark.slow(func)


def integration_test(func):
    """标记为集成测试"""
    return pytest.mark.integration(func)


def api_test(func):
    """标记为API测试"""
    return pytest.mark.api(func)


def frontend_test(func):
    """标记为前端测试"""
    return pytest.mark.frontend(func)


# 导出常用类和函数
__all__ = [
    'TestDataFactory',
    'TestUserManager', 
    'TestDatabaseManager',
    'TestResponseValidator',
    'TestMockHelper',
    'TestPerformanceHelper',
    'TestDataGenerator',
    'skip_if_no_database',
    'skip_if_no_external_api',
    'slow_test',
    'integration_test',
    'api_test',
    'frontend_test',
]
"""
测试辅助函数模块
提供常用的测试工具函数，简化测试用例编写
"""

import json
import os
import random
import string
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from unittest.mock import Mock, patch

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from rest_framework.test import APIClient

User = get_user_model()


class TestDataFactory:
    """测试数据工厂类"""
    
    @staticmethod
    def create_user_data(**kwargs) -> Dict[str, Any]:
        """创建用户测试数据"""
        default_data = {
            'username': f'test_user_{random.randint(1000, 9999)}',
            'email': f'test{random.randint(1000, 9999)}@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
        }
        default_data.update(kwargs)
        return default_data
    
    @staticmethod
    def create_article_data(**kwargs) -> Dict[str, Any]:
        """创建文章测试数据"""
        default_data = {
            'title': f'Test Article {random.randint(1000, 9999)}',
            'content': f'This is test content {random.randint(1000, 9999)}',
            'summary': f'Test summary {random.randint(1000, 9999)}',
            'category': 'test',
        }
        default_data.update(kwargs)
        return default_data
    
    @staticmethod
    def create_news_data(**kwargs) -> Dict[str, Any]:
        """创建新闻测试数据"""
        default_data = {
            'title': f'Test News {random.randint(1000, 9999)}',
            'content': f'This is test news content {random.randint(1000, 9999)}',
            'summary': f'Test news summary {random.randint(1000, 9999)}',
            'source': 'test_source',
            'category': 'test',
            'word_count': random.randint(100, 500),
        }
        default_data.update(kwargs)
        return default_data
    
    @staticmethod
    def create_typing_word_data(**kwargs) -> Dict[str, Any]:
        """创建打字练习单词测试数据"""
        default_data = {
            'word': f'test{random.randint(1000, 9999)}',
            'translation': f'测试{random.randint(1000, 9999)}',
            'difficulty': random.choice(['easy', 'medium', 'hard']),
            'category': 'test',
        }
        default_data.update(kwargs)
        return default_data


class TestUserManager:
    """测试用户管理类"""
    
    @staticmethod
    def create_test_user(**kwargs) -> User:
        """创建测试用户"""
        user_data = TestDataFactory.create_user_data(**kwargs)
        user = User.objects.create_user(**user_data)
        return user
    
    @staticmethod
    def create_test_superuser(**kwargs) -> User:
        """创建测试超级用户"""
        user_data = TestDataFactory.create_user_data(**kwargs)
        user_data['is_staff'] = True
        user_data['is_superuser'] = True
        user = User.objects.create_superuser(**user_data)
        return user
    
    @staticmethod
    def login_user(client: Client, user: User) -> bool:
        """用户登录"""
        return client.login(username=user.username, password='testpass123')
    
    @staticmethod
    def login_api_user(api_client: APIClient, user: User) -> bool:
        """API用户登录"""
        # 这里需要根据实际的认证方式调整
        # 假设使用JWT token认证
        try:
            response = api_client.post('/api/auth/login/', {
                'username': user.username,
                'password': 'testpass123'
            })
            if response.status_code == 200:
                token = response.data.get('token')
                if token:
                    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
                    return True
        except Exception:
            pass
        return False


class TestDatabaseManager:
    """测试数据库管理类"""
    
    @staticmethod
    def clean_test_data():
        """清理测试数据"""
        # 清理用户数据
        User.objects.filter(username__startswith='test_user_').delete()
        User.objects.filter(email__startswith='test').delete()
        
        # 清理其他测试数据
        # 这里需要根据实际的数据模型调整
        
    @staticmethod
    def create_test_fixtures():
        """创建测试数据夹具"""
        fixtures = {}
        
        # 创建测试用户
        test_user = TestUserManager.create_test_user()
        fixtures['test_user'] = test_user
        
        # 创建测试超级用户
        test_superuser = TestUserManager.create_test_superuser()
        fixtures['test_superuser'] = test_superuser
        
        return fixtures


class TestResponseValidator:
    """测试响应验证类"""
    
    @staticmethod
    def validate_success_response(response, expected_status_code: int = 200):
        """验证成功响应"""
        assert response.status_code == expected_status_code
        if hasattr(response, 'data'):
            assert 'success' in response.data or 'data' in response.data
    
    @staticmethod
    def validate_error_response(response, expected_status_code: int = 400):
        """验证错误响应"""
        assert response.status_code == expected_status_code
        if hasattr(response, 'data'):
            assert 'error' in response.data or 'message' in response.data
    
    @staticmethod
    def validate_pagination_response(response):
        """验证分页响应"""
        assert response.status_code == 200
        if hasattr(response, 'data'):
            data = response.data
            assert 'count' in data or 'total' in data
            assert 'results' in data or 'items' in data


class TestMockHelper:
    """测试模拟辅助类"""
    
    @staticmethod
    def mock_external_api(api_name: str, return_value: Any = None):
        """模拟外部API调用"""
        if return_value is None:
            return_value = {'success': True, 'data': 'mocked_data'}
        
        return patch(f'alpha.apps.english.services.{api_name}', return_value=return_value)
    
    @staticmethod
    def mock_file_upload(file_path: str = None):
        """模拟文件上传"""
        if file_path is None:
            file_path = 'tests/resources/fixtures/test_file.txt'
        
        mock_file = Mock()
        mock_file.name = 'test_file.txt'
        mock_file.size = 1024
        mock_file.content_type = 'text/plain'
        
        return mock_file


class TestPerformanceHelper:
    """测试性能辅助类"""
    
    @staticmethod
    def measure_execution_time(func, *args, **kwargs):
        """测量函数执行时间"""
        start_time = datetime.now()
        result = func(*args, **kwargs)
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        return result, execution_time
    
    @staticmethod
    def assert_performance_threshold(execution_time: float, threshold: float = 1.0):
        """断言性能阈值"""
        assert execution_time <= threshold, f"执行时间 {execution_time}s 超过阈值 {threshold}s"


class TestDataGenerator:
    """测试数据生成器"""
    
    @staticmethod
    def generate_random_string(length: int = 10) -> str:
        """生成随机字符串"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    @staticmethod
    def generate_random_email() -> str:
        """生成随机邮箱"""
        username = ''.join(random.choices(string.ascii_lowercase, k=8))
        domain = ''.join(random.choices(string.ascii_lowercase, k=6))
        return f"{username}@{domain}.com"
    
    @staticmethod
    def generate_random_date(start_date: datetime = None, end_date: datetime = None) -> datetime:
        """生成随机日期"""
        if start_date is None:
            start_date = datetime.now() - timedelta(days=365)
        if end_date is None:
            end_date = datetime.now()
        
        time_between_dates = end_date - start_date
        days_between_dates = time_between_dates.days
        random_number_of_days = random.randrange(days_between_dates)
        random_date = start_date + timedelta(days=random_number_of_days)
        return random_date


# 常用测试装饰器
def skip_if_no_database(func):
    """如果没有数据库则跳过测试"""
    return pytest.mark.skipif(
        os.getenv('SKIP_DATABASE_TESTS') == 'true',
        reason="数据库测试被跳过"
    )(func)


def skip_if_no_external_api(func):
    """如果没有外部API则跳过测试"""
    return pytest.mark.skipif(
        os.getenv('SKIP_EXTERNAL_API_TESTS') == 'true',
        reason="外部API测试被跳过"
    )(func)


def slow_test(func):
    """标记为慢速测试"""
    return pytest.mark.slow(func)


def integration_test(func):
    """标记为集成测试"""
    return pytest.mark.integration(func)


def api_test(func):
    """标记为API测试"""
    return pytest.mark.api(func)


def frontend_test(func):
    """标记为前端测试"""
    return pytest.mark.frontend(func)


# 导出常用类和函数
__all__ = [
    'TestDataFactory',
    'TestUserManager', 
    'TestDatabaseManager',
    'TestResponseValidator',
    'TestMockHelper',
    'TestPerformanceHelper',
    'TestDataGenerator',
    'skip_if_no_database',
    'skip_if_no_external_api',
    'slow_test',
    'integration_test',
    'api_test',
    'frontend_test',
]
