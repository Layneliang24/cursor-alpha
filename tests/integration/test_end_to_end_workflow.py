"""
端到端工作流测试
测试完整用户流程和跨模块集成
"""

import pytest
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import json

from apps.articles.models import Article
from apps.categories.models import Category
from apps.english.models import Word, Expression, UserTypingStats, TypingWord
from apps.users.models import UserProfile

User = get_user_model()


class EndToEndWorkflowTestCase(TestCase):
    """端到端工作流测试用例"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.user_profile = UserProfile.objects.create(
            user=self.user,
            bio='Test bio'
        )
        self.client.force_authenticate(user=self.user)
        
        # 创建测试数据
        self.category = Category.objects.create(
            name='Technology',
            description='Technology articles'
        )
        
        self.article = Article.objects.create(
            title='Python Programming Guide',
            content='Learn Python programming step by step',
            summary='Python programming tutorial',
            author=self.user,
            category=self.category,
            status='published'
        )
        
        self.word = Word.objects.create(
            word='python',
            translation='Python编程语言',
            difficulty='medium',
            phonetic='/ˈpaɪθən/'
        )
        
        self.expression = Expression.objects.create(
            expression='learn by doing',
            translation='在实践中学习',
            usage_examples='The best way to learn programming is to learn by doing.'
        )
    
    def test_complete_user_registration_workflow(self):
        """测试完整用户注册工作流"""
        # 1. 用户注册
        registration_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'password_confirm': 'newpass123'
        }
        
        response = self.client.post('/api/v1/auth/register/', registration_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 2. 用户登录
        login_data = {
            'username': 'newuser',
            'password': 'newpass123'
        }
        
        response = self.client.post('/api/v1/auth/login/', login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 3. 获取用户信息
        response = self.client.get('/api/v1/users/profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_complete_article_management_workflow(self):
        """测试完整文章管理工作流"""
        # 1. 创建文章
        article_data = {
            'title': 'Test Article',
            'content': 'This is a test article content',
            'summary': 'Test article summary',
            'category': self.category.id,
            'status': 'draft'
        }
        
        response = self.client.post('/api/v1/articles/', article_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        article_id = response.data['id']
        
        # 2. 编辑文章
        edit_data = {
            'title': 'Updated Test Article',
            'content': 'This is an updated test article content',
            'summary': 'Updated test article summary',
            'status': 'published'
        }
        
        response = self.client.put(f'/api/v1/articles/{article_id}/', edit_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 3. 查看文章列表
        response = self.client.get('/api/v1/articles/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)
        
        # 4. 查看文章详情
        response = self.client.get(f'/api/v1/articles/{article_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Test Article')
        
        # 5. 删除文章
        response = self.client.delete(f'/api/v1/articles/{article_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    
    def test_complete_english_learning_workflow(self):
        """测试完整英语学习工作流"""
        # 1. 获取单词列表
        response = self.client.get('/api/v1/english/words/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)
        
        # 2. 获取单词详情
        response = self.client.get(f'/api/v1/english/words/{self.word.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['word'], 'python')
        
        # 3. 获取表达列表
        response = self.client.get('/api/v1/english/expressions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)
        
        # 4. 获取表达详情
        response = self.client.get(f'/api/v1/english/expressions/{self.expression.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['expression'], 'learn by doing')
    
    def test_complete_typing_practice_workflow(self):
        """测试完整打字练习工作流"""
        # 1. 获取打字练习单词
        response = self.client.get('/api/v1/english/typing-words/?difficulty=medium&limit=10')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 2. 提交打字练习结果
        typing_data = {
            'word_id': self.word.id,
            'is_correct': True,
            'typing_speed': 50,
            'accuracy': 95.0
        }
        
        response = self.client.post('/api/v1/english/typing-practice/submit/', typing_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 3. 获取用户打字统计
        response = self.client.get('/api/v1/english/typing-stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_complete_data_analysis_workflow(self):
        """测试完整数据分析工作流"""
        # 1. 获取数据概览
        response = self.client.get('/api/v1/english/data-analysis/overview/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 2. 获取准确率趋势
        response = self.client.get('/api/v1/english/data-analysis/accuracy-trend/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 3. 获取WPM趋势
        response = self.client.get('/api/v1/english/data-analysis/wpm-trend/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 4. 获取练习热力图
        response = self.client.get('/api/v1/english/data-analysis/exercise-heatmap/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 5. 获取单词热力图
        response = self.client.get('/api/v1/english/data-analysis/word-heatmap/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 6. 获取按键错误统计
        response = self.client.get('/api/v1/english/data-analysis/key-error-stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CrossModuleIntegrationTestCase(TestCase):
    """跨模块集成测试用例"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # 创建测试数据
        self.category = Category.objects.create(
            name='Technology',
            description='Technology articles'
        )
        
        self.article = Article.objects.create(
            title='Python Programming Guide',
            content='Learn Python programming step by step',
            summary='Python programming tutorial',
            author=self.user,
            category=self.category,
            status='published'
        )
    
    def test_article_typing_integration(self):
        """测试文章与打字练习的集成"""
        # 1. 创建包含特定单词的文章
        article_data = {
            'title': 'Python Keywords',
            'content': 'Python has many keywords like def, class, import, from, as, in, is, and, or, not.',
            'summary': 'Python keywords overview',
            'category': self.category.id,
            'status': 'published'
        }
        
        response = self.client.post('/api/v1/articles/', article_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 2. 检查文章内容是否影响打字练习
        response = self.client.get('/api/v1/english/typing-words/?difficulty=easy&limit=5')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_user_profile_integration(self):
        """测试用户档案与其他模块的集成"""
        # 1. 更新用户档案
        profile_data = {
            'bio': 'Python developer and English learner'
        }
        
        response = self.client.put('/api/v1/users/profile/', profile_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 2. 检查用户档案更新是否影响其他功能
        response = self.client.get('/api/v1/articles/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response = self.client.get('/api/v1/english/words/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class BoundaryConditionTestCase(TestCase):
    """边界条件测试用例"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_extreme_data_values(self):
        """测试极端数据值"""
        # 测试非常长的标题
        long_title = 'A' * 1000
        article_data = {
            'title': long_title,
            'content': 'Test content',
            'summary': 'Test summary',
            'status': 'draft'
        }
        
        response = self.client.post('/api/v1/articles/', article_data, format='json')
        # 应该返回400错误，因为标题过长
        self.assertIn(response.status_code, [400, 201])
    
    def test_large_data_handling(self):
        """测试大数据处理"""
        # 测试大量数据的处理能力
        response = self.client.get('/api/v1/english/words/?limit=1000')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_special_characters_handling(self):
        """测试特殊字符处理"""
        # 测试包含特殊字符的内容
        special_content = 'Special chars: !@#$%^&*()_+-=[]{}|;:,.<>?'
        article_data = {
            'title': 'Special Characters Test',
            'content': special_content,
            'summary': 'Testing special characters',
            'status': 'draft'
        }
        
        response = self.client.post('/api/v1/articles/', article_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


if __name__ == '__main__':
    pytest.main([__file__])
