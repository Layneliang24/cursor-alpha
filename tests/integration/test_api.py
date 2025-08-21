"""
API集成测试
测试API端点的完整功能
"""

import pytest
import json
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from apps.articles.models import Article
from apps.categories.models import Category
from apps.english.models import Word, Expression, News

User = get_user_model()


class HealthCheckAPITest(TestCase):
    """健康检查API测试"""
    
    def setUp(self):
        self.client = APIClient()
    
    def test_health_check_endpoint(self):
        """测试健康检查端点"""
        url = '/api/health/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('ok', data)
        self.assertIn('details', data)
        self.assertIn('app', data['details'])
        self.assertIn('db', data['details'])


class AuthenticationAPITest(TestCase):
    """认证API测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_registration(self):
        """测试用户注册"""
        url = '/api/v1/auth/register/'
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'password_confirm': 'newpass123'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 验证用户是否创建
        user = User.objects.get(username='newuser')
        self.assertEqual(user.email, 'newuser@example.com')
    
    def test_user_login(self):
        """测试用户登录"""
        url = '/api/v1/auth/login/'
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        # API返回格式：{'message': '登录成功', 'user': {...}, 'tokens': {'access': '...', 'refresh': '...'}}
        self.assertIn('tokens', data)
        self.assertIn('access', data['tokens'])
        self.assertIn('refresh', data['tokens'])
    
    def test_user_logout(self):
        """测试用户登出"""
        # 先登录获取token
        login_url = '/api/v1/auth/login/'
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        login_response = self.client.post(login_url, login_data, format='json')
        # 修复token获取路径
        token = login_response.json()['tokens']['access']
        
        # 测试登出
        logout_url = '/api/v1/auth/logout/'
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post(logout_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ArticleAPITest(TestCase):
    """文章API测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Test Category',
            description='Test category description'
        )
        self.article = Article.objects.create(
            title='Test Article',
            content='Test article content.',
            author=self.user,
            category=self.category,
            status='published'  # 修复：设置为已发布状态，否则API不会返回
        )
        # 设置认证
        self.client.force_authenticate(user=self.user)
    
    def test_article_list(self):
        """测试文章列表API"""
        url = '/api/v1/articles/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        # API可能返回不同的格式，适配两种情况
        if 'results' in data:
            self.assertGreater(len(data['results']), 0)
        elif 'data' in data:
            self.assertGreater(len(data['data']), 0)
        else:
            # 如果都没有，检查数据库中是否有已发布的文章
            published_articles = Article.objects.filter(status='published').count()
            if published_articles > 0:
                self.fail(f"数据库中有{published_articles}篇已发布文章，但API返回空列表")
            # 如果数据库中没有已发布文章，测试通过
    
    def test_article_detail(self):
        """测试文章详情API"""
        url = f'/api/v1/articles/{self.article.pk}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['title'], 'Test Article')
        self.assertEqual(data['content'], 'Test article content.')
    
    def test_article_creation(self):
        """测试文章创建API"""
        url = '/api/v1/articles/'
        data = {
            'title': 'New Article',
            'content': 'New article content.',
            'category': self.category.pk
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 验证文章是否创建
        article = Article.objects.get(title='New Article')
        self.assertEqual(article.author, self.user)


class EnglishAPITest(TestCase):
    """英语API测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.word = Word.objects.create(
            word='test',
            phonetic='/test/',
            definition='A test word.',
            difficulty_level='beginner'
        )
        self.expression = Expression.objects.create(
            expression='break the ice',
            meaning='To initiate conversation.',
            difficulty_level='intermediate'
        )
        # 设置认证
        self.client.force_authenticate(user=self.user)
    
    def test_word_list(self):
        """测试单词列表API"""
        url = '/api/v1/english/words/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        # API返回格式：{'success': True, 'message': 'OK', 'data': [...], 'pagination': {...}}
        self.assertIn('data', data)
        self.assertGreater(len(data['data']), 0)
    
    def test_word_detail(self):
        """测试单词详情API"""
        url = f'/api/v1/english/words/{self.word.pk}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        # 如果API返回嵌套格式，需要适配
        if 'data' in data:
            word_data = data['data']
        else:
            word_data = data
        self.assertEqual(word_data['word'], 'test')
        self.assertEqual(word_data['phonetic'], '/test/')
    
    def test_expression_list(self):
        """测试表达列表API"""
        url = '/api/v1/english/expressions/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        # API返回格式：{'success': True, 'message': 'OK', 'data': [...], 'pagination': {...}}
        self.assertIn('data', data)
        self.assertGreater(len(data['data']), 0)
    
    def test_expression_detail(self):
        """测试表达详情API"""
        url = f'/api/v1/english/expressions/{self.expression.pk}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        # 如果API返回嵌套格式，需要适配
        if 'data' in data:
            expression_data = data['data']
        else:
            expression_data = data
        self.assertEqual(expression_data['expression'], 'break the ice')
        self.assertEqual(expression_data['meaning'], 'To initiate conversation.')


class NewsAPITest(TestCase):
    """新闻API测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.news = News.objects.create(
            title='Test News',
            content='Test news content.',
            source='test_source',
            source_url='https://example.com/test',
            difficulty_level='intermediate'
        )
        # 设置认证
        self.client.force_authenticate(user=self.user)
    
    def test_news_list(self):
        """测试新闻列表API"""
        url = '/api/v1/english/news/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        # API返回格式：{'success': True, 'message': 'OK', 'data': [...], 'pagination': {...}}
        self.assertIn('data', data)
        self.assertGreater(len(data['data']), 0)
    
    def test_news_detail(self):
        """测试新闻详情API"""
        url = f'/api/v1/english/news/{self.news.pk}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        # 如果API返回嵌套格式，需要适配
        if 'data' in data:
            news_data = data['data']
        else:
            news_data = data
        self.assertEqual(news_data['title'], 'Test News')
        self.assertEqual(news_data['content'], 'Test news content.')


class PermissionAPITest(TestCase):
    """权限API测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
    
    def test_unauthorized_access(self):
        """测试未授权访问"""
        url = '/api/v1/articles/'
        data = {'title': 'Test', 'content': 'Test content'}
        
        # 未认证用户不能创建文章
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_authorized_access(self):
        """测试授权访问"""
        # 创建测试分类
        category = Category.objects.create(
            name='Test Category',
            description='Test category description'
        )
        
        url = '/api/v1/articles/'
        data = {
            'title': 'Test Article',
            'content': 'Test content',
            'category': category.id  # 修复：添加必需的category字段
        }
        
        # 认证用户可以创建文章
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


@pytest.mark.integration
class IntegrationTests:
    """集成测试标记"""
    
    def test_full_user_workflow(self):
        """测试完整用户工作流程"""
        # 这里可以添加完整的用户工作流程测试
        assert True
    
    def test_api_endpoint_integration(self):
        """测试API端点集成"""
        # 这里可以添加API端点集成测试
        assert True


@pytest.mark.slow
class SlowAPITests:
    """慢速API测试"""
    
    def test_bulk_operations(self):
        """测试批量操作"""
        # 这里可以添加需要较长时间的批量操作测试
        assert True
