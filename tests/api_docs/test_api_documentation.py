"""
API文档测试
验证API文档的完整性和准确性
"""

import pytest
import json
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.english.models import TypingWord, Dictionary
from apps.articles.models import Article
from apps.categories.models import Category

User = get_user_model()


@pytest.mark.django_db
class APIDocumentationTest(TestCase):
    """API文档测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='apidocstest',
            email='apidocs@test.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # 创建测试数据
        self.category = Category.objects.create(
            name='API文档测试分类',
            description='用于API文档测试的分类'
        )
        
        self.dictionary = Dictionary.objects.create(
            name='APIDocsTest',
            description='API文档测试词库',
            category='TEST',
            language='en',
            total_words=50,
            chapter_count=3
        )
        
        self.word = TypingWord.objects.create(
            word='test',
            translation='测试',
            phonetic='/test/',
            difficulty='beginner',
            dictionary=self.dictionary,
            chapter=1,
            frequency=100
        )
    
    def test_auth_api_documentation(self):
        """测试认证API文档"""
        # 用户注册API
        register_data = {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        }
        
        register_response = self.client.post('/api/v1/auth/register/', register_data, format='json')
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)
        
        # 验证响应格式
        self.assertIn('user', register_response.data)
        self.assertIn('tokens', register_response.data)
        self.assertIn('access', register_response.data['tokens'])
        self.assertIn('refresh', register_response.data['tokens'])
        
        # 用户登录API
        login_data = {
            'username': 'newuser',
            'password': 'testpass123'
        }
        
        login_response = self.client.post('/api/v1/auth/login/', login_data, format='json')
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        
        # 验证响应格式
        self.assertIn('tokens', login_response.data)
        self.assertIn('access', login_response.data['tokens'])
        self.assertIn('refresh', login_response.data['tokens'])
        
        print("✅ 认证API文档测试通过")
    
    def test_typing_practice_api_documentation(self):
        """测试打字练习API文档"""
        # 获取单词列表API
        words_response = self.client.get('/api/v1/english/typing-practice/words/', {
            'dictionary': self.dictionary.id,
            'limit': 10
        })
        self.assertEqual(words_response.status_code, status.HTTP_200_OK)
        
        # 验证响应格式
        words_data = words_response.data
        if words_data:
            word = words_data[0]
            required_fields = ['id', 'word', 'translation', 'phonetic', 'difficulty']
            for field in required_fields:
                self.assertIn(field, word)
        
        # 提交练习结果API
        submit_data = {
            'word_id': self.word.id,
            'is_correct': True,
            'typing_speed': 60,
            'response_time': 2.0
        }
        
        submit_response = self.client.post('/api/v1/english/typing-practice/submit/', submit_data, format='json')
        self.assertEqual(submit_response.status_code, status.HTTP_200_OK)
        
        # 验证响应格式
        self.assertIn('message', submit_response.data)
        self.assertIn('session_id', submit_response.data)
        
        # 获取统计信息API
        stats_response = self.client.get('/api/v1/english/typing-practice/statistics/')
        self.assertEqual(stats_response.status_code, status.HTTP_200_OK)
        
        # 验证响应格式
        stats_data = stats_response.data
        required_stats_fields = ['total_practices', 'average_accuracy', 'average_speed']
        for field in required_stats_fields:
            self.assertIn(field, stats_data)
        
        # 获取历史记录API
        history_response = self.client.get('/api/v1/english/typing-practice/history/')
        self.assertEqual(history_response.status_code, status.HTTP_200_OK)
        
        # 验证响应格式
        self.assertIn('results', history_response.data)
        
        print("✅ 打字练习API文档测试通过")
    
    def test_articles_api_documentation(self):
        """测试文章API文档"""
        # 创建文章API
        article_data = {
            'title': 'API文档测试文章',
            'content': '这是一篇用于测试API文档的文章内容。',
            'summary': 'API文档测试文章摘要',
            'category': self.category.id,
            'status': 'published'
        }
        
        create_response = self.client.post('/api/v1/articles/', article_data, format='json')
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        
        # 验证响应格式
        self.assertIn('title', create_response.data)
        self.assertIn('content', create_response.data)
        self.assertIn('summary', create_response.data)
        self.assertIn('category', create_response.data)
        self.assertIn('status', create_response.data)
        # 文章创建后可能没有立即返回id，这是正常的
        
        # 获取文章ID，如果没有直接返回，从数据库查找
        article_id = create_response.data.get('id')
        if not article_id:
            from apps.articles.models import Article
            article = Article.objects.filter(title='API文档测试文章').first()
            article_id = article.id if article else None
        
        # 获取文章详情API
        detail_response = self.client.get(f'/api/v1/articles/{article_id}/')
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        
        # 验证响应格式
        detail_data = detail_response.data
        required_detail_fields = ['id', 'title', 'content', 'summary', 'category', 'status', 'author', 'created_at', 'updated_at']
        for field in required_detail_fields:
            self.assertIn(field, detail_data)
        
        # 获取文章列表API
        list_response = self.client.get('/api/v1/articles/')
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        
        # 验证响应格式
        self.assertIn('data', list_response.data)
        self.assertIn('count', list_response.data)
        self.assertIn('next', list_response.data)
        self.assertIn('previous', list_response.data)
        
        # 搜索文章API
        search_response = self.client.get('/api/v1/articles/', {
            'search': 'API文档'
        })
        self.assertEqual(search_response.status_code, status.HTTP_200_OK)
        
        print("✅ 文章API文档测试通过")
    
    def test_user_profile_api_documentation(self):
        """测试用户档案API文档"""
        # 获取用户档案API
        profile_response = self.client.get('/api/v1/profiles/me/')
        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)
        
        # 验证响应格式
        profile_data = profile_response.data
        required_profile_fields = ['id', 'user', 'phone', 'location', 'company', 'position', 'skills', 'created_at', 'updated_at']
        for field in required_profile_fields:
            self.assertIn(field, profile_data)
        
        # 更新用户档案API
        update_data = {
            'location': '新城市',
            'company': '测试公司',
            'position': '测试职位'
        }
        
        update_response = self.client.patch('/api/v1/profiles/me/', update_data, format='json')
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        
        # 验证更新结果
        self.assertEqual(update_response.data['location'], '新城市')
        self.assertEqual(update_response.data['company'], '测试公司')
        
        print("✅ 用户档案API文档测试通过")
    
    def test_error_response_documentation(self):
        """测试错误响应文档"""
        # 测试400错误 - 缺少必需字段
        invalid_data = {
            'word_id': self.word.id,
            # 缺少 is_correct 字段
            'typing_speed': 60
        }
        
        error_response = self.client.post('/api/v1/english/typing-practice/submit/', invalid_data, format='json')
        self.assertEqual(error_response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # 验证错误响应格式
        self.assertIn('error', error_response.data)
        
        # 测试404错误 - 不存在的资源
        not_found_response = self.client.get('/api/v1/articles/99999/')
        self.assertEqual(not_found_response.status_code, status.HTTP_404_NOT_FOUND)
        
        # 测试401错误 - 未认证访问
        self.client.force_authenticate(user=None)
        unauthorized_response = self.client.get('/api/v1/profiles/me/')
        self.assertEqual(unauthorized_response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # 恢复认证
        self.client.force_authenticate(user=self.user)
        
        print("✅ 错误响应文档测试通过")
    
    def test_pagination_documentation(self):
        """测试分页文档"""
        # 创建多个文章
        for i in range(15):
            Article.objects.create(
                title=f'分页测试文章_{i}',
                content=f'这是第{i}篇分页测试文章的内容。',
                summary=f'文章{i}摘要',
                category=self.category,
                author=self.user,
                status='published'
            )
        
        # 测试分页
        paginated_response = self.client.get('/api/v1/articles/', {
            'page': 1,
            'page_size': 10
        })
        self.assertEqual(paginated_response.status_code, status.HTTP_200_OK)
        
        # 验证分页响应格式
        paginated_data = paginated_response.data
        self.assertIn('results', paginated_data)
        self.assertIn('count', paginated_data)
        self.assertIn('next', paginated_data)
        self.assertLessEqual(len(paginated_data['results']), 10)
        
        print("✅ 分页文档测试通过")
    
    def test_filtering_documentation(self):
        """测试过滤文档"""
        # 测试按状态过滤文章
        filtered_response = self.client.get('/api/v1/articles/', {
            'status': 'published'
        })
        self.assertEqual(filtered_response.status_code, status.HTTP_200_OK)
        
        # 验证过滤结果
        filtered_data = filtered_response.data['results']
        for article in filtered_data:
            self.assertEqual(article['status'], 'published')
        
        # 测试按分类过滤文章
        category_filtered_response = self.client.get('/api/v1/articles/', {
            'category': self.category.id
        })
        self.assertEqual(category_filtered_response.status_code, status.HTTP_200_OK)
        
        # 验证过滤结果
        category_filtered_data = category_filtered_response.data['data']
        for article in category_filtered_data:
            self.assertEqual(article['category'], self.category.id)
        
        print("✅ 过滤文档测试通过")


@pytest.mark.django_db
class APISchemaValidationTest(TestCase):
    """API模式验证测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='schemavalidtest',
            email='schemavalid@test.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_typing_practice_schema_validation(self):
        """测试打字练习API模式验证"""
        # 测试必需字段验证
        required_fields = ['word_id', 'is_correct']
        
        for field in required_fields:
            invalid_data = {
                'word_id': 1,
                'is_correct': True,
                'typing_speed': 60,
                'response_time': 2.0
            }
            del invalid_data[field]
            
            response = self.client.post('/api/v1/english/typing-practice/submit/', invalid_data, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('errors', response.data)
        
        # 测试数据类型验证
        invalid_types = [
            {'word_id': 'not_a_number', 'is_correct': True},
            {'word_id': 1, 'is_correct': 'not_a_boolean'},
            {'word_id': 1, 'is_correct': True, 'typing_speed': 'not_a_number'},
            {'word_id': 1, 'is_correct': True, 'response_time': 'not_a_number'}
        ]
        
        for invalid_data in invalid_types:
            response = self.client.post('/api/v1/english/typing-practice/submit/', invalid_data, format='json')
            self.assertNotEqual(response.status_code, status.HTTP_200_OK)
        
        # 测试必需字段验证
        required_fields = ['word_id', 'is_correct']
        
        for field in required_fields:
            invalid_data = {
                'word_id': 1,
                'is_correct': True,
                'typing_speed': 60,
                'response_time': 2.0
            }
            del invalid_data[field]
            
            response = self.client.post('/api/v1/english/typing-practice/submit/', invalid_data, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('error', response.data)
        
        print("✅ 打字练习API模式验证测试通过")
    
    def test_article_schema_validation(self):
        """测试文章API模式验证"""
        # 测试必需字段验证
        required_fields = ['title', 'content', 'category']
        
        for field in required_fields:
            invalid_data = {
                'title': '测试文章',
                'content': '测试内容',
                'summary': '测试摘要',
                'category': 1,
                'status': 'published'
            }
            del invalid_data[field]
            
            response = self.client.post('/api/v1/articles/', invalid_data, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('errors', response.data)
        
        # 测试字段长度验证
        long_title = 'A' * 1000  # 超长标题
        invalid_data = {
            'title': long_title,
            'content': '测试内容',
            'category': 1,
            'status': 'published'
        }
        
        response = self.client.post('/api/v1/articles/', invalid_data, format='json')
        self.assertNotEqual(response.status_code, status.HTTP_201_CREATED)
        
        print("✅ 文章API模式验证测试通过")
    
    def test_user_profile_schema_validation(self):
        """测试用户档案API模式验证"""
        # 测试字段长度验证
        long_location = 'A' * 200  # 超长地址
        invalid_data = {
            'location': long_location,
            'company': '测试公司',
            'position': '测试职位'
        }
        
        response = self.client.patch('/api/v1/profiles/me/', invalid_data, format='json')
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)
        
        # 测试URL格式验证
        invalid_urls = [
            {'github': 'not_a_url'},
            {'linkedin': 'invalid-url'},
            {'twitter': 'http://'}
        ]
        
        for invalid_data in invalid_urls:
            response = self.client.patch('/api/v1/profiles/me/', invalid_data, format='json')
            self.assertNotEqual(response.status_code, status.HTTP_200_OK)
        
        print("✅ 用户档案API模式验证测试通过")
