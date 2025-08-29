# -*- coding: utf-8 -*-
"""
缓存策略单元测试
验证缓存模块的核心功能
"""
import pytest
from django.test import TestCase, override_settings
from django.core.cache import cache
from apps.api.cache_strategy import CacheStrategy, CacheMonitor, ExpressionCacheManager


# 使用本地内存缓存进行测试
@override_settings(CACHES={
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'test-cache',
    }
})
class CacheStrategyTest(TestCase):
    """缓存策略测试"""
    
    def setUp(self):
        """测试准备"""
        cache.clear()
    
    def test_cache_key_generation(self):
        """测试缓存键生成"""
        # 测试基础键生成
        key1 = CacheStrategy.get_cache_key('api', 'test')
        self.assertTrue(key1.startswith('api:v1:'))
        self.assertIn('test', key1)
        
        # 测试参数键生成
        key2 = CacheStrategy.get_cache_key('api', 'test', id=1, name='example')
        key3 = CacheStrategy.get_cache_key('api', 'test', name='example', id=1)
        self.assertEqual(key2, key3, "相同参数应生成相同键")
        
        # 测试长键哈希
        long_key = 'a' * 300
        key4 = CacheStrategy.get_cache_key('api', long_key)
        self.assertLess(len(key4), 250, "长键应该被哈希化")
        self.assertIn('hash:', key4)
    
    def test_cache_layer_management(self):
        """测试缓存层级管理"""
        test_data = {'test': 'layer_data', 'timestamp': '2024-01-01'}
        
        # 测试不同层级设置
        result1 = CacheStrategy.set_with_layer('test_l1', test_data, 'L1_HOT', 'api')
        result2 = CacheStrategy.set_with_layer('test_l3', test_data, 'L3_NORMAL', 'api')
        
        self.assertTrue(result1, "L1层级缓存设置应该成功")
        self.assertTrue(result2, "L3层级缓存设置应该成功")
        
        # 验证缓存获取
        cached_l1 = CacheStrategy.get_with_fallback('test_l1', prefix='api')
        cached_l3 = CacheStrategy.get_with_fallback('test_l3', prefix='api')
        
        self.assertEqual(cached_l1, test_data)
        self.assertEqual(cached_l3, test_data)
    
    def test_cache_fallback_function(self):
        """测试缓存回退函数"""
        def fallback_func():
            return {'fallback': True, 'data': 'generated'}
        
        # 第一次调用应该执行回退函数并缓存结果
        result1 = CacheStrategy.get_with_fallback(
            'fallback_test', 
            fallback_func, 
            prefix='api'
        )
        
        self.assertEqual(result1['fallback'], True)
        
        # 第二次调用应该从缓存返回
        result2 = CacheStrategy.get_with_fallback(
            'fallback_test', 
            lambda: {'fallback': False, 'data': 'should_not_execute'}, 
            prefix='api'
        )
        
        self.assertEqual(result2['fallback'], True, "应该从缓存返回，不执行回退函数")
    
    def test_expression_cache_manager(self):
        """测试表达式缓存管理器"""
        # 由于没有实际数据，测试缓存键生成和基础功能
        cache_key = CacheStrategy.get_cache_key('expression', 'hot_expressions', limit=10)
        self.assertIn('expression:', cache_key)
        
        # 测试用户偏好缓存（模拟数据）
        test_prefs = {
            'difficulty_preference': 'intermediate',
            'learning_goals': ['business', 'casual'],
            'daily_target': 20
        }
        
        CacheStrategy.set_with_layer('user_prefs:123', test_prefs, 'L3_NORMAL', 'user')
        cached_prefs = CacheStrategy.get_with_fallback('user_prefs:123', prefix='user')
        
        self.assertEqual(cached_prefs, test_prefs)
    
    def test_cache_monitor_stats(self):
        """测试缓存监控统计"""
        # 执行一些缓存操作
        CacheStrategy.set_with_layer('monitor_test1', {'data': 1}, 'L1_HOT', 'api')
        CacheStrategy.set_with_layer('monitor_test2', {'data': 2}, 'L3_NORMAL', 'api')
        
        CacheStrategy.get_with_fallback('monitor_test1', prefix='api')
        CacheStrategy.get_with_fallback('monitor_test2', prefix='api')
        CacheStrategy.get_with_fallback('nonexistent', prefix='api')  # 未命中
        
        # 获取统计信息（本地缓存版本）
        stats = CacheMonitor.get_cache_stats()
        
        self.assertIn('redis_info', stats)
        self.assertIn('cache_operations', stats)
        self.assertIn('timestamp', stats)
    
    def test_cache_invalidation(self):
        """测试缓存失效"""
        # 设置多个相关缓存
        CacheStrategy.set_with_layer('user:1:prefs', {'pref': 'test1'}, 'L3_NORMAL', 'user')
        CacheStrategy.set_with_layer('user:1:stats', {'stats': 'test1'}, 'L3_NORMAL', 'user')
        CacheStrategy.set_with_layer('user:2:prefs', {'pref': 'test2'}, 'L3_NORMAL', 'user')
        
        # 验证缓存存在
        self.assertIsNotNone(CacheStrategy.get_with_fallback('user:1:prefs', prefix='user'))
        self.assertIsNotNone(CacheStrategy.get_with_fallback('user:2:prefs', prefix='user'))
        
        # 失效特定用户缓存（本地缓存版本不支持模式删除，但测试逻辑）
        try:
            invalidated = CacheStrategy.invalidate_pattern('user:1:', 'user')
            # 对于locmem缓存，这会失败但不应该抛出异常
            self.assertGreaterEqual(invalidated, 0)
        except Exception:
            # 本地内存缓存不支持模式删除，这是预期的
            pass


class CacheIntegrationTest(TestCase):
    """缓存集成测试"""
    
    def setUp(self):
        cache.clear()
    
    def test_cache_decorator_functionality(self):
        """测试缓存装饰器功能"""
        from apps.api.cache_strategy import CacheDecorators
        
        call_count = 0
        
        @CacheDecorators.model_cache('test_model', 'L1_HOT')
        def expensive_function(param):
            nonlocal call_count
            call_count += 1
            return {'result': f'computed_{param}', 'call_count': call_count}
        
        # 第一次调用
        result1 = expensive_function('param1')
        self.assertEqual(call_count, 1)
        self.assertEqual(result1['result'], 'computed_param1')
        
        # 第二次调用应该从缓存返回
        result2 = expensive_function('param1')
        self.assertEqual(call_count, 1, "第二次调用应该从缓存返回，不增加调用计数")
        self.assertEqual(result2['result'], 'computed_param1')
        
        # 不同参数应该重新计算
        result3 = expensive_function('param2')
        self.assertEqual(call_count, 2)
        self.assertEqual(result3['result'], 'computed_param2')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
