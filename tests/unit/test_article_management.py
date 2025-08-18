"""
文章管理功能测试
测试文章创建、编辑、删除和搜索功能
"""

import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.articles.models import Article
from apps.categories.models import Category, Tag
from apps.users.models import UserProfile

User = get_user_model()


@pytest.mark.django_db
class ArticleCreationTest(TestCase):
    """文章创建测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='测试分类',
            description='测试用分类'
        )
        self.tag = Tag.objects.create(
            name='测试标签',
            description='测试用标签'
        )
        
        # 登录用户
        login_response = self.client.post('/api/v1/auth/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        }, format='json')
        token = login_response.data['tokens']['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    
    def test_create_article_success(self):
        """测试文章创建成功"""
        article_data = {
            'title': '测试文章',
            'content': '这是一篇测试文章的内容。',
            'summary': '测试文章摘要',
            'category': self.category.id,
            'tags': [self.tag.id],
            'status': 'published'
        }
        
        response = self.client.post('/api/v1/articles/', article_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], '测试文章')
        self.assertEqual(response.data['content'], '这是一篇测试文章的内容。')
        self.assertEqual(response.data['author'], self.user.id)
        self.assertEqual(response.data['status'], 'published')
    
    def test_create_article_without_authentication(self):
        """测试未认证用户创建文章"""
        self.client.credentials()  # 清除认证信息
        
        article_data = {
            'title': '测试文章',
            'content': '这是一篇测试文章的内容。',
            'category': self.category.id
        }
        
        response = self.client.post('/api/v1/articles/', article_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_create_article_missing_required_fields(self):
        """测试缺少必填字段的文章创建"""
        article_data = {
            'content': '这是一篇测试文章的内容。',
            'category': self.category.id
            # 缺少title
        }
        
        response = self.client.post('/api/v1/articles/', article_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)
    
    def test_create_article_with_invalid_category(self):
        """测试使用无效分类创建文章"""
        article_data = {
            'title': '测试文章',
            'content': '这是一篇测试文章的内容。',
            'category': 99999  # 不存在的分类ID
        }
        
        response = self.client.post('/api/v1/articles/', article_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('category', response.data)
    
    def test_create_article_with_draft_status(self):
        """测试创建草稿状态的文章"""
        article_data = {
            'title': '草稿文章',
            'content': '这是一篇草稿文章的内容。',
            'category': self.category.id,
            'status': 'draft'
        }
        
        response = self.client.post('/api/v1/articles/', article_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'draft')


@pytest.mark.django_db
class ArticleEditTest(TestCase):
    """文章编辑测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='测试分类',
            description='测试用分类'
        )
        self.tag = Tag.objects.create(
            name='测试标签',
            description='测试用标签'
        )
        self.article = Article.objects.create(
            title='原始文章',
            content='原始内容',
            summary='原始摘要',
            author=self.user,
            category=self.category,
            status='published'
        )
        
        # 登录用户
        login_response = self.client.post('/api/v1/auth/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        }, format='json')
        token = login_response.data['tokens']['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    
    def test_edit_article_success(self):
        """测试文章编辑成功"""
        update_data = {
            'title': '更新后的文章',
            'content': '更新后的内容',
            'summary': '更新后的摘要'
        }
        
        response = self.client.patch(f'/api/v1/articles/{self.article.id}/', update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], '更新后的文章')
        self.assertEqual(response.data['content'], '更新后的内容')
        self.assertEqual(response.data['summary'], '更新后的摘要')
    
    def test_edit_article_by_non_author(self):
        """测试非作者编辑文章"""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        
        # 使用其他用户登录
        login_response = self.client.post('/api/v1/auth/login/', {
            'username': 'otheruser',
            'password': 'otherpass123'
        }, format='json')
        token = login_response.data['tokens']['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        update_data = {
            'title': '尝试编辑的文章'
        }
        
        response = self.client.patch(f'/api/v1/articles/{self.article.id}/', update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_edit_article_without_authentication(self):
        """测试未认证用户编辑文章"""
        self.client.credentials()  # 清除认证信息
        
        update_data = {
            'title': '尝试编辑的文章'
        }
        
        response = self.client.patch(f'/api/v1/articles/{self.article.id}/', update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_edit_article_change_category(self):
        """测试编辑文章时更改分类"""
        new_category = Category.objects.create(
            name='新分类',
            description='新的测试分类'
        )
        
        update_data = {
            'category': new_category.id
        }
        
        response = self.client.patch(f'/api/v1/articles/{self.article.id}/', update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['category'], new_category.id)
    
    def test_edit_article_change_status(self):
        """测试编辑文章时更改状态"""
        update_data = {
            'status': 'draft'
        }
        
        response = self.client.patch(f'/api/v1/articles/{self.article.id}/', update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'draft')
    
    def test_edit_nonexistent_article(self):
        """测试编辑不存在的文章"""
        update_data = {
            'title': '尝试编辑的文章'
        }
        
        response = self.client.patch('/api/v1/articles/99999/', update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


@pytest.mark.django_db
class ArticleDeleteTest(TestCase):
    """文章删除测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='测试分类',
            description='测试用分类'
        )
        self.article = Article.objects.create(
            title='要删除的文章',
            content='要删除的内容',
            author=self.user,
            category=self.category,
            status='published'
        )
        
        # 登录用户
        login_response = self.client.post('/api/v1/auth/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        }, format='json')
        token = login_response.data['tokens']['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    
    def test_delete_article_success(self):
        """测试文章删除成功"""
        response = self.client.delete(f'/api/v1/articles/{self.article.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # 验证文章已被删除
        self.assertFalse(Article.objects.filter(id=self.article.id).exists())
    
    def test_delete_article_by_non_author(self):
        """测试非作者删除文章"""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        
        # 使用其他用户登录
        login_response = self.client.post('/api/v1/auth/login/', {
            'username': 'otheruser',
            'password': 'otherpass123'
        }, format='json')
        token = login_response.data['tokens']['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        response = self.client.delete(f'/api/v1/articles/{self.article.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # 验证文章仍然存在
        self.assertTrue(Article.objects.filter(id=self.article.id).exists())
    
    def test_delete_article_without_authentication(self):
        """测试未认证用户删除文章"""
        self.client.credentials()  # 清除认证信息
        
        response = self.client.delete(f'/api/v1/articles/{self.article.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # 验证文章仍然存在
        self.assertTrue(Article.objects.filter(id=self.article.id).exists())
    
    def test_delete_nonexistent_article(self):
        """测试删除不存在的文章"""
        response = self.client.delete('/api/v1/articles/99999/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


@pytest.mark.django_db
class ArticleSearchTest(TestCase):
    """文章搜索测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='测试分类',
            description='测试用分类'
        )
        
        # 创建多篇文章用于搜索测试
        self.article1 = Article.objects.create(
            title='Python编程指南',
            content='这是一篇关于Python编程的文章。',
            summary='Python编程入门指南',
            author=self.user,
            category=self.category,
            status='published'
        )
        self.article2 = Article.objects.create(
            title='Django框架教程',
            content='这是一篇关于Django框架的文章。',
            summary='Django框架学习教程',
            author=self.user,
            category=self.category,
            status='published'
        )
        self.article3 = Article.objects.create(
            title='JavaScript基础',
            content='这是一篇关于JavaScript的文章。',
            summary='JavaScript基础知识',
            author=self.user,
            category=self.category,
            status='draft'
        )
    
    def test_search_articles_by_title(self):
        """测试按标题搜索文章"""
        response = self.client.get('/api/v1/articles/?search=Python')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Python编程指南')
    
    def test_search_articles_by_content(self):
        """测试按内容搜索文章"""
        response = self.client.get('/api/v1/articles/?search=Django')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Django框架教程')
    
    def test_search_articles_by_summary(self):
        """测试按摘要搜索文章"""
        response = self.client.get('/api/v1/articles/?search=教程')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Django框架教程')
    
    def test_search_articles_no_results(self):
        """测试搜索无结果"""
        response = self.client.get('/api/v1/articles/?search=不存在的关键词')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)
    
    def test_filter_articles_by_category(self):
        """测试按分类筛选文章"""
        response = self.client.get(f'/api/v1/articles/?category={self.category.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # 只返回已发布的文章
        for article in response.data['results']:
            self.assertEqual(article['category'], self.category.id)
    
    def test_filter_articles_by_status(self):
        """测试按状态筛选文章"""
        response = self.client.get('/api/v1/articles/?status=published')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        for article in response.data['results']:
            self.assertEqual(article['status'], 'published')
    
    def test_filter_articles_by_author(self):
        """测试按作者筛选文章"""
        response = self.client.get(f'/api/v1/articles/?author={self.user.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # 只返回已发布的文章
        for article in response.data['results']:
            self.assertEqual(article['author'], self.user.id)
    
    def test_articles_pagination(self):
        """测试文章分页"""
        # 创建更多文章以测试分页
        for i in range(15):
            Article.objects.create(
                title=f'文章{i}',
                content=f'文章{i}的内容',
                author=self.user,
                category=self.category,
                status='published'
            )
        
        response = self.client.get('/api/v1/articles/?page=1&page_size=10')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
    
    def test_articles_ordering(self):
        """测试文章排序"""
        response = self.client.get('/api/v1/articles/?ordering=-created_at')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        
        # 验证按创建时间倒序排列
        first_article = response.data['results'][0]
        second_article = response.data['results'][1]
        self.assertGreater(first_article['created_at'], second_article['created_at'])


@pytest.mark.django_db
class ArticleDetailTest(TestCase):
    """文章详情测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='测试分类',
            description='测试用分类'
        )
        self.article = Article.objects.create(
            title='测试文章',
            content='这是一篇测试文章的内容。',
            summary='测试文章摘要',
            author=self.user,
            category=self.category,
            status='published'
        )
    
    def test_get_article_detail(self):
        """测试获取文章详情"""
        response = self.client.get(f'/api/v1/articles/{self.article.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], '测试文章')
        self.assertEqual(response.data['content'], '这是一篇测试文章的内容。')
        self.assertEqual(response.data['summary'], '测试文章摘要')
        self.assertEqual(response.data['author'], self.user.id)
        self.assertEqual(response.data['category'], self.category.id)
        self.assertEqual(response.data['status'], 'published')
    
    def test_get_nonexistent_article(self):
        """测试获取不存在的文章"""
        response = self.client.get('/api/v1/articles/99999/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_get_draft_article_by_author(self):
        """测试作者获取草稿文章"""
        draft_article = Article.objects.create(
            title='草稿文章',
            content='草稿内容',
            author=self.user,
            category=self.category,
            status='draft'
        )
        
        # 登录作者
        login_response = self.client.post('/api/v1/auth/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        }, format='json')
        token = login_response.data['tokens']['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        response = self.client.get(f'/api/v1/articles/{draft_article.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], '草稿文章')
    
    def test_get_draft_article_by_non_author(self):
        """测试非作者获取草稿文章"""
        draft_article = Article.objects.create(
            title='草稿文章',
            content='草稿内容',
            author=self.user,
            category=self.category,
            status='draft'
        )
        
        response = self.client.get(f'/api/v1/articles/{draft_article.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND) 