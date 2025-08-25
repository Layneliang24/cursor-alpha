#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
示例flaky测试用例

这些测试用例故意设计为不稳定，用于演示flaky测试检测机制
注意：这些测试仅用于演示目的，在实际项目中应该避免这样的测试
"""

import random
import time
from unittest.mock import patch

import pytest
from django.test import TestCase


class FlakyTestExamples(TestCase):
    """Flaky测试示例"""
    
    @pytest.mark.flaky
    def test_random_failure(self):
        """随机失败的测试 - 50%成功率"""
        if random.random() < 0.5:
            self.fail("Random failure occurred")
        self.assertTrue(True)
    
    @pytest.mark.flaky
    def test_timing_sensitive(self):
        """时间敏感的测试 - 可能因为时间而失败"""
        start_time = time.time()
        time.sleep(0.1)  # 模拟一些处理时间
        end_time = time.time()
        
        # 这个断言可能因为系统负载而失败
        duration = end_time - start_time
        self.assertLess(duration, 0.15, f"Test took too long: {duration}s")
    
    @pytest.mark.flaky
    def test_external_dependency(self):
        """依赖外部服务的测试 - 可能因为网络问题失败"""
        # 模拟外部API调用
        success_rate = 0.7  # 70%成功率
        if random.random() > success_rate:
            raise ConnectionError("Failed to connect to external service")
        
        self.assertTrue(True)
    
    def test_stable_test(self):
        """稳定的测试 - 应该总是通过"""
        self.assertEqual(2 + 2, 4)
        self.assertTrue(True)
    
    @pytest.mark.flaky
    def test_race_condition(self):
        """竞态条件测试 - 可能因为并发问题失败"""
        # 模拟竞态条件
        shared_resource = []
        
        def worker():
            for i in range(10):
                shared_resource.append(i)
                time.sleep(0.001)  # 模拟处理时间
        
        import threading
        threads = [threading.Thread(target=worker) for _ in range(2)]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # 这个断言可能因为竞态条件而失败
        expected_length = 20
        actual_length = len(shared_resource)
        
        # 添加一些随机性来模拟真实的竞态条件
        if random.random() < 0.3:  # 30%的失败率
            self.assertEqual(actual_length, expected_length - 1)  # 故意错误的断言
        else:
            self.assertEqual(actual_length, expected_length)
    
    @pytest.mark.flaky
    def test_memory_dependent(self):
        """内存依赖的测试 - 可能因为内存不足失败"""
        # 模拟内存使用
        large_list = []
        
        try:
            # 随机决定是否创建大量数据
            if random.random() < 0.2:  # 20%的概率
                # 创建大量数据来模拟内存压力
                for i in range(100000):
                    large_list.append(f"data_{i}" * 10)
            
            # 模拟内存不足的情况
            if len(large_list) > 50000:
                raise MemoryError("Insufficient memory")
            
            self.assertTrue(True)
        
        finally:
            # 清理内存
            large_list.clear()
    
    @pytest.mark.flaky
    def test_environment_dependent(self):
        """环境依赖的测试 - 可能因为环境变量失败"""
        import os
        
        # 模拟环境变量检查
        test_env = os.environ.get('TEST_ENV', 'development')
        
        # 随机模拟环境问题
        if random.random() < 0.25:  # 25%失败率
            # 模拟环境配置错误
            with patch.dict(os.environ, {'TEST_ENV': 'invalid'}):
                test_env = os.environ.get('TEST_ENV')
                if test_env == 'invalid':
                    self.fail("Invalid environment configuration")
        
        self.assertIn(test_env, ['development', 'testing', 'production'])
    
    def test_another_stable_test(self):
        """另一个稳定的测试"""
        self.assertEqual("hello".upper(), "HELLO")
        self.assertIsInstance([], list)
    
    @pytest.mark.flaky
    @pytest.mark.slow
    def test_slow_and_flaky(self):
        """既慢又不稳定的测试"""
        # 模拟长时间运行的测试
        time.sleep(0.5)
        
        # 添加随机失败
        if random.random() < 0.4:  # 40%失败率
            self.fail("Slow test failed randomly")
        
        self.assertTrue(True)
    
    def test_database_dependent(self):
        """数据库依赖的测试 - 通常比较稳定"""
        from django.contrib.auth.models import User
        
        # 创建测试用户
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(user.check_password('testpass123'))
        
        # 清理
        user.delete()


class FlakyTestUtilities:
    """Flaky测试工具类"""
    
    @staticmethod
    def simulate_network_delay():
        """模拟网络延迟"""
        delay = random.uniform(0.01, 0.1)
        time.sleep(delay)
        return delay
    
    @staticmethod
    def simulate_random_error(error_rate=0.3):
        """模拟随机错误"""
        if random.random() < error_rate:
            raise RuntimeError("Simulated random error")
        return True
    
    @staticmethod
    def create_flaky_condition(success_rate=0.7):
        """创建flaky条件"""
        return random.random() < success_rate


# 独立的测试函数（非类方法）
@pytest.mark.flaky
def test_function_level_flaky():
    """函数级别的flaky测试"""
    utilities = FlakyTestUtilities()
    
    # 模拟网络延迟
    delay = utilities.simulate_network_delay()
    
    # 如果延迟太长，测试失败
    if delay > 0.08:
        pytest.fail(f"Network delay too high: {delay}s")
    
    assert True


@pytest.mark.flaky
def test_mock_failure():
    """使用mock的flaky测试"""
    with patch('random.random') as mock_random:
        # 30%的时间返回高值（导致失败）
        mock_random.return_value = 0.9 if random.random() < 0.3 else 0.1
        
        if mock_random.return_value > 0.5:
            pytest.fail("Mock returned high value")
        
        assert mock_random.return_value <= 0.5


def test_stable_function():
    """稳定的函数测试"""
    assert 1 + 1 == 2
    assert "test".startswith("te")
    assert len([1, 2, 3]) == 3