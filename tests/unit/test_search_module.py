"""
搜索模块单元测试
测试搜索功能的正确性和完整性
"""

import pytest
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.articles.models import Article
from apps.categories.models import Category
from apps.english.models import Word, Expression
from apps.users.models import UserProfile

User = get_user_model()


class SearchModuleTestCase(TestCase):
    """搜索模块基础测试用例"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        # UserProfile没有bio字段，bio字段在User模型中
        self.user_profile = UserProfile.objects.create(
            user=self.user
        )
        
        # 创建测试数据
        self.category = Category.objects.create(
            name='Test Category',
            description='Test category description'
        )
        
        self.article = Article.objects.create(
            title='Test Article',
            content='This is a test article content',
            summary='Test article summary',
            author=self.user,
            category=self.category,
            status='published'
        )
        
        self.word = Word.objects.create(
            word='test',
            translation='测试',
            difficulty='easy',
            phonetic='/test/'
        )
        
        self.expression = Expression.objects.create(
            expression='test expression',
            translation='测试表达',
            usage_examples='This is a test expression usage example.'
        )
    
    def test_search_endpoint_exists(self):
        """测试搜索端点存在"""
        response = self.client.get('/api/v1/search/?q=test')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], 'search placeholder')
        self.assertIn('query', data['data'])
        self.assertIn('results', data['data'])
    
    def test_search_function_view_structure(self):
        """测试搜索函数视图结构"""
        from apps.search.views import search_view
        # 检查搜索视图函数是否存在
        self.assertTrue(callable(search_view))
    
    def test_search_allows_anonymous_access(self):
        """测试搜索允许匿名访问"""
        # 搜索模块允许匿名访问，这是正确的
        response = self.client.get('/api/v1/search/?q=test')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class SearchAPITestCase(TestCase):
    """搜索API测试用例"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # 创建测试数据
        self.category = Category.objects.create(
            name='Test Category',
            description='Test category description'
        )
        
        self.article = Article.objects.create(
            title='Test Article',
            content='This is a test article content about Python programming',
            summary='Test article summary',
            author=self.user,
            category=self.category,
            status='published'
        )
        
        self.word = Word.objects.create(
            word='python',
            definition='Python编程语言',
            difficulty_level='intermediate',
            phonetic='/ˈpaɪθən/'
        )
    
    def test_search_with_query_parameter(self):
        """测试带查询参数的搜索"""
        response = self.client.get('/api/v1/search/?q=python')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertEqual(data['data']['query'], 'python')
        self.assertEqual(data['data']['results'], [])
    
    def test_search_without_query_parameter(self):
        """测试不带查询参数的搜索"""
        response = self.client.get('/api/v1/search/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertEqual(data['data']['query'], '')
        self.assertEqual(data['data']['results'], [])
    
    def test_search_module_initialization(self):
        """测试搜索模块初始化"""
        from apps.search.apps import SearchConfig
        # 检查搜索应用配置
        self.assertEqual(SearchConfig.name, 'apps.search')
        self.assertEqual(SearchConfig.default_auto_field, 'django.db.models.BigAutoField')


class SearchIntegrationTestCase(TestCase):
    """搜索模块集成测试用例"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # 创建测试数据
        self.category = Category.objects.create(
            name='Programming',
            description='Programming related articles'
        )
        
        self.article1 = Article.objects.create(
            title='Python Programming Guide',
            content='Learn Python programming step by step',
            summary='Python programming tutorial',
            author=self.user,
            category=self.category,
            status='published'
        )
        
        self.article2 = Article.objects.create(
            title='Django Web Development',
            content='Build web applications with Django framework',
            summary='Django web development guide',
            author=self.user,
            category=self.category,
            status='published'
        )
    
    def test_search_module_with_other_modules(self):
        """测试搜索模块与其他模块的集成"""
        # 测试搜索模块是否影响其他模块
        response = self.client.get('/api/v1/articles/')
        self.assertIn(response.status_code, [200, 401, 403, 404])
    
    def test_search_response_format_consistency(self):
        """测试搜索响应格式一致性"""
        response = self.client.get('/api/v1/search/?q=test')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        # 验证响应格式的一致性
        self.assertIn('success', data)
        self.assertIn('message', data)
        self.assertIn('data', data)
        self.assertIn('query', data['data'])
        self.assertIn('results', data['data'])


class SearchFunctionalityTestCase(TestCase):
    """搜索功能测试用例"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # 创建测试数据
        self.category = Category.objects.create(
            name='Technology',
            description='Technology articles'
        )
        
        self.article = Article.objects.create(
            title='Machine Learning Basics',
            content='Introduction to machine learning algorithms and concepts',
            summary='ML fundamentals',
            author=self.user,
            category=self.category,
            status='published'
        )
    
    def test_search_placeholder_functionality(self):
        """测试搜索占位符功能"""
        # 当前搜索功能是占位符，应该返回空结果
        response = self.client.get('/api/v1/search/?q=machine+learning')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertEqual(data['data']['query'], 'machine learning')
        self.assertEqual(data['data']['results'], [])
    
    def test_search_http_methods(self):
        """测试搜索HTTP方法支持"""
        # 搜索视图只支持GET方法
        response = self.client.post('/api/v1/search/', {'q': 'test'})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        
        response = self.client.put('/api/v1/search/', {'q': 'test'})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        
        response = self.client.delete('/api/v1/search/')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


if __name__ == '__main__':
    pytest.main([__file__])
