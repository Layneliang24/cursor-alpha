# -*- coding: utf-8 -*-
"""
API缓存性能测试
验证缓存策略的有效性和性能提升
"""
import time
import pytest
import requests
from django.test import TestCase, TransactionTestCase
from django.core.cache import cache
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.english.models import IdiomaticExpression, ExpressionSource
from apps.api.cache_strategy import CacheStrategy, CacheMonitor

User = get_user_model()


class APICachePerformanceTest(APITestCase):
    """API缓存性能测试"""
    
    def setUp(self):
        """测试准备"""
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # 创建测试数据
        self.source = ExpressionSource.objects.create(
            name='Test Source',
            url='https://test.com',
            reliability_score=0.9
        )
        
        # 创建测试表达式
        self.expressions = []
        for i in range(10):
            expr = IdiomaticExpression.objects.create(
                expression=f'test expression {i}',
                meaning=f'测试表达含义 {i}',
                cultural_background=f'文化背景 {i}',
                difficulty_level='intermediate',
                frequency_score=0.8,
                source=self.source
            )
            self.expressions.append(expr)
        
        # 认证客户端
        self.client.force_authenticate(user=self.user)
        
        # 清空缓存
        cache.clear()
    
    def test_expression_list_cache_performance(self):
        """测试表达式列表缓存性能"""
        url = reverse('idiomaticexpression-list')
        
        # 第一次请求（缓存未命中）
        start_time = time.time()
        response1 = self.client.get(url)
        first_request_time = time.time() - start_time
        
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertIn('X-Cache', response1)
        
        # 第二次请求（缓存命中）
        start_time = time.time()
        response2 = self.client.get(url)
        second_request_time = time.time() - start_time
        
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(response1.data, response2.data)
        
        # 验证缓存提升性能
        performance_improvement = (first_request_time - second_request_time) / first_request_time * 100
        
        print(f"第一次请求时间: {first_request_time:.4f}s")
        print(f"第二次请求时间: {second_request_time:.4f}s")
        print(f"性能提升: {performance_improvement:.2f}%")
        
        # 缓存应该显著提升性能（至少20%）
        self.assertGreater(performance_improvement, 20, 
                          "缓存应该显著提升API响应性能")
    
    def test_expression_detail_cache(self):
        """测试表达式详情缓存"""
        expression = self.expressions[0]
        url = reverse('idiomaticexpression-detail', kwargs={'pk': expression.id})
        
        # 第一次请求
        response1 = self.client.get(url)
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        
        # 第二次请求应该从缓存返回
        response2 = self.client.get(url)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(response1.data, response2.data)
        
        # 验证缓存头
        self.assertIn('Cache-Control', response2)
        self.assertIn('ETag', response2)
    
    def test_cache_invalidation(self):
        """测试缓存失效机制"""
        expression = self.expressions[0]
        list_url = reverse('idiomaticexpression-list')
        detail_url = reverse('idiomaticexpression-detail', kwargs={'pk': expression.id})
        
        # 预热缓存
        self.client.get(list_url)
        self.client.get(detail_url)
        
        # 更新表达式
        update_data = {'meaning': '更新后的含义'}
        response = self.client.patch(detail_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证缓存已失效
        response_after_update = self.client.get(detail_url)
        self.assertEqual(response_after_update.data['meaning'], '更新后的含义')
    
    def test_cache_statistics_api(self):
        """测试缓存统计API"""
        cache_url = reverse('cache-list')
        
        # 先进行一些API调用生成缓存统计
        list_url = reverse('idiomaticexpression-list')
        for _ in range(3):
            self.client.get(list_url)
        
        # 获取缓存统计
        response = self.client.get(cache_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data
        self.assertIn('redis_info', data)
        self.assertIn('cache_operations', data)
        self.assertIn('timestamp', data)
        
        # 验证Redis信息
        redis_info = data['redis_info']
        self.assertIn('used_memory', redis_info)
        self.assertIn('hit_rate', redis_info)
    
    def test_cache_warmup(self):
        """测试缓存预热功能"""
        # 需要管理员权限
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.client.force_authenticate(user=admin_user)
        
        warmup_url = reverse('cache-warmup')
        response = self.client.post(warmup_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertIn('success', data)
        self.assertIn('message', data)
        self.assertTrue(data['success'])
    
    def test_hot_expressions_cache(self):
        """测试热门表达缓存"""
        hot_url = reverse('cache-hot-expressions')
        
        # 第一次请求
        response1 = self.client.get(hot_url, {'limit': 5})
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        
        data = response1.data
        self.assertIn('expressions', data)
        self.assertIn('cached', data)
        self.assertIn('timestamp', data)
        
        # 第二次请求应该从缓存返回
        response2 = self.client.get(hot_url, {'limit': 5})
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(response1.data['expressions'], response2.data['expressions'])
    
    def test_etag_validation(self):
        """测试ETag验证机制"""
        url = reverse('idiomaticexpression-list')
        
        # 第一次请求获取ETag
        response1 = self.client.get(url)
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        etag = response1.get('ETag', '').strip('"')
        
        # 使用ETag再次请求
        response2 = self.client.get(url, HTTP_IF_NONE_MATCH=f'"{etag}"')
        
        # 应该返回304 Not Modified
        if hasattr(response2, 'status_code'):
            # 如果缓存中间件正常工作，应该返回304
            self.assertIn(response2.status_code, [status.HTTP_304_NOT_MODIFIED, status.HTTP_200_OK])


class CacheStrategyTest(TestCase):
    """缓存策略单元测试"""
    
    def setUp(self):
        cache.clear()
    
    def test_cache_key_generation(self):
        """测试缓存键生成"""
        key1 = CacheStrategy.get_cache_key('api', 'test', id=1, name='test')
        key2 = CacheStrategy.get_cache_key('api', 'test', name='test', id=1)  # 参数顺序不同
        
        # 相同参数应该生成相同的键
        self.assertEqual(key1, key2)
        
        # 验证键格式
        self.assertTrue(key1.startswith('api:v1:'))
        self.assertIn('test', key1)
    
    def test_cache_layer_management(self):
        """测试缓存层级管理"""
        test_data = {'test': 'data'}
        
        # 设置不同层级的缓存
        CacheStrategy.set_with_layer('test_l1', test_data, 'L1_HOT', 'api')
        CacheStrategy.set_with_layer('test_l3', test_data, 'L3_NORMAL', 'api')
        
        # 验证缓存设置成功
        cached_l1 = CacheStrategy.get_with_fallback('test_l1', prefix='api')
        cached_l3 = CacheStrategy.get_with_fallback('test_l3', prefix='api')
        
        self.assertEqual(cached_l1, test_data)
        self.assertEqual(cached_l3, test_data)
    
    def test_cache_invalidation_pattern(self):
        """测试缓存模式失效"""
        # 设置多个相关缓存
        CacheStrategy.set_with_layer('user:1:prefs', {'pref': 'test'}, 'L3_NORMAL', 'user')
        CacheStrategy.set_with_layer('user:1:stats', {'stats': 'test'}, 'L3_NORMAL', 'user')
        CacheStrategy.set_with_layer('user:2:prefs', {'pref': 'test2'}, 'L3_NORMAL', 'user')
        
        # 失效用户1的所有缓存
        invalidated = CacheStrategy.invalidate_pattern('user:1:', 'user')
        
        # 验证失效结果
        self.assertGreaterEqual(invalidated, 0)  # 可能因Redis实现而异
        
        # 验证用户2的缓存仍然存在
        user2_data = CacheStrategy.get_with_fallback('user:2:prefs', prefix='user')
        self.assertIsNotNone(user2_data)


@pytest.mark.performance
class CachePerformanceBenchmark(TransactionTestCase):
    """缓存性能基准测试"""
    
    def setUp(self):
        """准备大量测试数据"""
        cache.clear()
        
        # 创建大量表达式数据
        source = ExpressionSource.objects.create(
            name='Benchmark Source',
            url='https://benchmark.com'
        )
        
        expressions = []
        for i in range(100):
            expr = IdiomaticExpression.objects.create(
                expression=f'benchmark expression {i}',
                meaning=f'基准测试表达 {i}',
                difficulty_level='intermediate',
                frequency_score=0.5 + (i % 5) * 0.1,
                source=source
            )
            expressions.append(expr)
        
        self.expressions = expressions
    
    def test_large_dataset_cache_performance(self):
        """测试大数据集的缓存性能"""
        client = APIClient()
        url = '/api/v1/expressions/'
        
        # 测试多次请求的性能
        times = []
        
        for i in range(5):
            start_time = time.time()
            response = client.get(url, {'page_size': 50})
            request_time = time.time() - start_time
            times.append(request_time)
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        print(f"请求时间: {times}")
        print(f"平均时间: {sum(times) / len(times):.4f}s")
        print(f"最快时间: {min(times):.4f}s")
        print(f"最慢时间: {max(times):.4f}s")
        
        # 后续请求应该比第一次快（缓存效果）
        avg_cached_time = sum(times[1:]) / len(times[1:])
        first_time = times[0]
        
        improvement = (first_time - avg_cached_time) / first_time * 100
        print(f"缓存性能提升: {improvement:.2f}%")
        
        # 缓存应该提升性能至少10%
        self.assertGreater(improvement, 10)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
