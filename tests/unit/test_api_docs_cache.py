# -*- coding: utf-8 -*-
"""
API文档和缓存策略测试
"""
import pytest
from django.test import TestCase, override_settings
from django.core.cache import cache
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from unittest.mock import patch, Mock
import json

from apps.english.models import IdiomaticExpression, UserExpressionProgress
from apps.english.cache_strategy import EnglishCacheManager, CachePreheater, CacheMonitor
from apps.english.cache_strategy import ResponseCacheMiddleware

User = get_user_model()


class APIDocumentationTest(TestCase):
    """API文档测试"""
    
    def setUp(self):
        self.client = APIClient()
    
    def test_openapi_schema_accessible(self):
        """测试OpenAPI schema可以访问"""
        response = self.client.get('/api/schema/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/vnd.oai.openapi')
    
    def test_swagger_ui_accessible(self):
        """测试Swagger UI可以访问"""
        response = self.client.get('/api/swagger/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/html', response['content-type'])
    
    def test_redoc_accessible(self):
        """测试ReDoc可以访问"""
        response = self.client.get('/api/redoc/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/html', response['content-type'])
    
    def test_schema_includes_english_endpoints(self):
        """测试schema包含地道表达相关端点"""
        response = self.client.get('/api/schema/')
        self.assertEqual(response.status_code, 200)
        
        # 解析schema - drf-spectacular返回YAML格式
        import yaml
        schema = yaml.safe_load(response.content.decode('utf-8'))
        paths = schema.get('paths', {})
        
        # 检查关键端点是否存在
        expected_paths = [
            '/api/v1/expressions/',
            '/api/v1/user-progress/',
            '/api/v1/statistics/overview/',
        ]
        
        for path in expected_paths:
            self.assertIn(path, paths, f"端点 {path} 未在schema中找到")
    
    def test_schema_includes_security_schemes(self):
        """测试schema包含安全方案"""
        response = self.client.get('/api/schema/')
        
        # 解析schema - drf-spectacular返回YAML格式
        import yaml
        schema = yaml.safe_load(response.content.decode('utf-8'))
        
        security_schemes = schema.get('components', {}).get('securitySchemes', {})
        
        expected_schemes = ['BearerAuth', 'ApiKeyAuth', 'SessionAuth']
        for scheme in expected_schemes:
            self.assertIn(scheme, security_schemes, f"安全方案 {scheme} 未找到")
    
    def test_schema_includes_tags(self):
        """测试schema包含正确的标签"""
        response = self.client.get('/api/schema/')
        
        # 解析schema - drf-spectacular返回YAML格式
        import yaml
        schema = yaml.safe_load(response.content.decode('utf-8'))
        
        tags = [tag['name'] for tag in schema.get('tags', [])]
        expected_tags = ['Authentication', 'Expressions', 'Learning', 'Statistics']
        
        for tag in expected_tags:
            self.assertIn(tag, tags, f"标签 {tag} 未找到")


@override_settings(CACHES={
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'test-api-docs-cache',
    }
})
class CacheStrategyTest(TestCase):
    """缓存策略测试"""
    
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.expression = IdiomaticExpression.objects.create(
            expression='break the ice',
            meaning='打破沉默',
            difficulty_level='intermediate',
            metadata={'tags': ['social', 'business']}
        )
    
    def tearDown(self):
        cache.clear()
    
    def test_expression_list_cache(self):
        """测试表达列表缓存"""
        # 设置缓存
        test_data = {'results': [{'id': 1, 'expression': 'test'}]}
        filters = {'difficulty_level': 'intermediate'}
        
        EnglishCacheManager.set_expression_list(test_data, filters, 1, 20)
        
        # 获取缓存
        cached_data = EnglishCacheManager.get_expression_list(filters, 1, 20)
        self.assertEqual(cached_data, test_data)
    
    def test_expression_detail_cache(self):
        """测试表达详情缓存"""
        test_data = {'id': 1, 'expression': 'break the ice', 'meaning': '打破沉默'}
        
        # 设置缓存
        EnglishCacheManager.set_expression_detail(1, test_data)
        
        # 获取缓存
        cached_data = EnglishCacheManager.get_expression_detail(1)
        self.assertEqual(cached_data, test_data)
    
    def test_user_progress_cache(self):
        """测试用户进度缓存"""
        test_data = {'user_id': 1, 'expression_id': 1, 'mastery_level': 3}
        
        # 设置缓存
        EnglishCacheManager.set_user_progress(1, test_data, 1)
        
        # 获取缓存
        cached_data = EnglishCacheManager.get_user_progress(1, 1)
        self.assertEqual(cached_data, test_data)
    
    def test_statistics_cache(self):
        """测试统计数据缓存"""
        test_data = {'total_expressions': 100, 'learned': 50}
        
        # 设置缓存
        EnglishCacheManager.set_statistics(1, 'overview', test_data)
        
        # 获取缓存
        cached_data = EnglishCacheManager.get_statistics(1, 'overview')
        self.assertEqual(cached_data, test_data)
    
    def test_hot_expressions_cache(self):
        """测试热门表达缓存"""
        test_data = [{'id': 1, 'expression': 'popular'}, {'id': 2, 'expression': 'trending'}]
        
        # 设置缓存
        EnglishCacheManager.set_hot_expressions(test_data, 10)
        
        # 获取缓存
        cached_data = EnglishCacheManager.get_hot_expressions(10)
        self.assertEqual(cached_data, test_data)
    
    def test_search_results_cache(self):
        """测试搜索结果缓存"""
        test_data = {'results': [{'id': 1, 'expression': 'found'}]}
        query = 'test query'
        filters = {'difficulty_level': 'intermediate'}
        
        # 设置缓存
        EnglishCacheManager.set_search_results(query, test_data, filters)
        
        # 获取缓存
        cached_data = EnglishCacheManager.get_search_results(query, filters)
        self.assertEqual(cached_data, test_data)
    
    def test_cache_invalidation_on_expression_save(self):
        """测试表达保存时的缓存失效"""
        # 先设置缓存
        EnglishCacheManager.set_expression_detail(self.expression.id, {'test': 'data'})
        
        # 确认缓存存在
        cached_data = EnglishCacheManager.get_expression_detail(self.expression.id)
        self.assertIsNotNone(cached_data)
        
        # 保存表达（触发信号）
        self.expression.meaning = '新的含义'
        self.expression.save()
        
        # 验证缓存已失效
        cached_data = EnglishCacheManager.get_expression_detail(self.expression.id)
        self.assertIsNone(cached_data)
    
    def test_cache_invalidation_on_progress_save(self):
        """测试用户进度保存时的缓存失效"""
        progress = UserExpressionProgress.objects.create(
            user=self.user,
            expression=self.expression,
            mastery_level=3
        )
        
        # 先设置缓存
        EnglishCacheManager.set_user_progress(self.user.id, {'test': 'data'}, self.expression.id)
        
        # 确认缓存存在
        cached_data = EnglishCacheManager.get_user_progress(self.user.id, self.expression.id)
        self.assertIsNotNone(cached_data)
        
        # 保存进度（触发信号）
        progress.mastery_level = 4
        progress.save()
        
        # 验证缓存已失效
        cached_data = EnglishCacheManager.get_user_progress(self.user.id, self.expression.id)
        self.assertIsNone(cached_data)


@override_settings(CACHES={
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'test-cache-preheater',
    }
})
class CachePreheaterTest(TestCase):
    """缓存预热器测试"""
    
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # 创建测试表达
        self.expressions = []
        for i in range(5):
            expr = IdiomaticExpression.objects.create(
                expression=f'expression_{i}',
                meaning=f'meaning_{i}',
                difficulty_level='intermediate',
                metadata={'tags': ['test']}
            )
            self.expressions.append(expr)
            
            # 为部分表达创建用户进度（模拟热门度）
            if i < 3:
                UserExpressionProgress.objects.create(
                    user=self.user,
                    expression=expr,
                    mastery_level=i + 1
                )
    
    def tearDown(self):
        cache.clear()
    
    def test_preheat_hot_expressions(self):
        """测试预热热门表达"""
        # 执行预热
        CachePreheater.preheat_hot_expressions()
        
        # 验证缓存是否存在
        hot_data = EnglishCacheManager.get_hot_expressions()
        self.assertIsNotNone(hot_data)
        self.assertIsInstance(hot_data, list)
        self.assertGreater(len(hot_data), 0)
    
    def test_preheat_random_pools(self):
        """测试预热随机表达池"""
        # 执行预热
        CachePreheater.preheat_random_pools()
        
        # 验证不同级别的随机池
        levels = ['beginner', 'intermediate', 'advanced']
        for level in levels:
            pool_data = EnglishCacheManager.get_random_pool(level)
            # 由于测试数据只有intermediate级别，只验证该级别
            if level == 'intermediate':
                self.assertIsNotNone(pool_data)
                self.assertIsInstance(pool_data, list)
        
        # 验证全部级别的随机池
        all_pool = EnglishCacheManager.get_random_pool()
        self.assertIsNotNone(all_pool)
        self.assertIsInstance(all_pool, list)


class CacheMonitorTest(TestCase):
    """缓存监控器测试"""
    
    def test_get_cache_metrics(self):
        """测试获取缓存指标"""
        metrics = CacheMonitor.get_cache_metrics()
        self.assertIsInstance(metrics, dict)
        # 由于使用的是LocMemCache，可能没有Redis相关指标
        # 但应该有基本的结构
    
    @patch('apps.english.cache_strategy.logger')
    def test_log_cache_performance(self, mock_logger):
        """测试记录缓存性能日志"""
        metrics = CacheMonitor.log_cache_performance()
        
        # 验证返回了指标
        self.assertIsInstance(metrics, dict)
        
        # 验证调用了logger
        mock_logger.info.assert_called_once()


@override_settings(CACHES={
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'test-response-cache',
    }
})
class ResponseCacheMiddlewareTest(TestCase):
    """响应缓存中间件测试"""
    
    def setUp(self):
        cache.clear()
        
        # 创建mock response
        self.mock_get_response = Mock()
        self.mock_response = Mock()
        self.mock_response.status_code = 200
        self.mock_get_response.return_value = self.mock_response
        
        self.middleware = ResponseCacheMiddleware(self.mock_get_response)
    
    def tearDown(self):
        cache.clear()
    
    def test_middleware_initialization(self):
        """测试中间件初始化"""
        self.assertIsNotNone(self.middleware.get_response)
        self.assertIsInstance(self.middleware.cacheable_paths, list)
        self.assertGreater(self.middleware.cache_timeout, 0)
    
    def test_make_response_cache_key(self):
        """测试响应缓存键生成"""
        # 创建mock request
        mock_request = Mock()
        mock_request.path = '/api/v1/expressions/'
        mock_request.META = {'QUERY_STRING': 'page=1&limit=10'}
        mock_request.user.id = 123
        
        cache_key = self.middleware._make_response_cache_key(mock_request)
        
        self.assertIsInstance(cache_key, str)
        self.assertTrue(cache_key.startswith('response_cache:'))
    
    def test_cacheable_path_detection(self):
        """测试可缓存路径检测"""
        from django.http import HttpResponse
        
        # 创建真实的HttpResponse而不是Mock
        real_response = HttpResponse('{"test": "data"}', content_type='application/json')
        real_response.status_code = 200
        self.mock_get_response.return_value = real_response
        
        # 创建mock request
        mock_request = Mock()
        mock_request.method = 'GET'
        mock_request.path = '/api/v1/expressions/'
        mock_request.META = {'QUERY_STRING': ''}
        mock_request.user.id = 123
        
        # 调用中间件
        response = self.middleware(mock_request)
        
        # 验证调用了get_response
        self.mock_get_response.assert_called_once_with(mock_request)
        self.assertEqual(response, real_response)


@override_settings(CACHES={
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'test-integration-cache',
    }
})
class CacheIntegrationTest(APITestCase):
    """缓存集成测试"""
    
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # 创建测试数据
        self.expression = IdiomaticExpression.objects.create(
            expression='break the ice',
            meaning='打破沉默',
            difficulty_level='intermediate',
            metadata={'tags': ['social']}
        )
    
    def tearDown(self):
        cache.clear()
    
    def test_expression_list_caching_integration(self):
        """测试表达列表缓存集成"""
        url = '/api/v1/expressions/'
        
        # 第一次请求（应该从数据库获取并缓存）
        with patch.object(EnglishCacheManager, 'set_expression_list') as mock_set:
            response1 = self.client.get(url)
            self.assertEqual(response1.status_code, 200)
            # 验证设置了缓存
            mock_set.assert_called_once()
        
        # 第二次请求（应该从缓存获取）
        with patch.object(EnglishCacheManager, 'get_expression_list', 
                         return_value={'cached': True}) as mock_get:
            response2 = self.client.get(url)
            self.assertEqual(response2.status_code, 200)
            self.assertEqual(response2.data, {'cached': True})
            # 验证获取了缓存
            mock_get.assert_called_once()
    
    def test_expression_detail_caching_integration(self):
        """测试表达详情缓存集成"""
        url = f'/api/v1/expressions/{self.expression.id}/'
        
        # 第一次请求（应该从数据库获取并缓存）
        with patch.object(EnglishCacheManager, 'set_expression_detail') as mock_set:
            response1 = self.client.get(url)
            self.assertEqual(response1.status_code, 200)
            # 验证设置了缓存
            mock_set.assert_called_once_with(str(self.expression.id), response1.data)
        
        # 第二次请求（应该从缓存获取）
        with patch.object(EnglishCacheManager, 'get_expression_detail', 
                         return_value={'cached': True}) as mock_get:
            response2 = self.client.get(url)
            self.assertEqual(response2.status_code, 200)
            self.assertEqual(response2.data, {'cached': True})
            # 验证获取了缓存
            mock_get.assert_called_once_with(str(self.expression.id))
    
    def test_statistics_caching_integration(self):
        """测试统计数据缓存集成"""
        url = '/api/v1/statistics/overview/'
        
        # 第一次请求（应该从数据库获取并缓存）
        with patch.object(EnglishCacheManager, 'set_statistics') as mock_set:
            response1 = self.client.get(url)
            self.assertEqual(response1.status_code, 200)
            # 验证设置了缓存
            mock_set.assert_called_once()
        
        # 第二次请求（应该从缓存获取）
        with patch.object(EnglishCacheManager, 'get_statistics', 
                         return_value={'cached_stats': True}) as mock_get:
            response2 = self.client.get(url)
            self.assertEqual(response2.status_code, 200)
            self.assertEqual(response2.data, {'cached_stats': True})
            # 验证获取了缓存
            mock_get.assert_called_once()


class CacheKeyGenerationTest(TestCase):
    """缓存键生成测试"""
    
    def test_make_key_basic(self):
        """测试基本缓存键生成"""
        key = EnglishCacheManager._make_key('test', 'category', 123, 'param')
        expected = 'english:test:category:123:param'
        self.assertEqual(key, expected)
    
    def test_make_hash_key(self):
        """测试哈希缓存键生成"""
        data = {'filters': {'level': 'intermediate'}, 'page': 1}
        key = EnglishCacheManager._make_hash_key('search', data)
        
        self.assertTrue(key.startswith('english:search:'))
        self.assertEqual(len(key.split(':')), 3)  # prefix:category:hash
    
    def test_hash_key_consistency(self):
        """测试哈希键的一致性"""
        data = {'filters': {'level': 'intermediate'}, 'page': 1}
        
        key1 = EnglishCacheManager._make_hash_key('search', data)
        key2 = EnglishCacheManager._make_hash_key('search', data)
        
        # 相同数据应该生成相同的键
        self.assertEqual(key1, key2)
        
        # 不同数据应该生成不同的键
        data2 = {'filters': {'level': 'advanced'}, 'page': 1}
        key3 = EnglishCacheManager._make_hash_key('search', data2)
        self.assertNotEqual(key1, key3)
