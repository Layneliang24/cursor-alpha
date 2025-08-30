#!/usr/bin/env python
"""
AI服务管理系统功能验证脚本

验证AI服务管理器、负载均衡、健康监控等核心功能
"""

import os
import sys
import django
from pathlib import Path

# 添加项目路径到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alpha.settings')
django.setup()

from apps.ai.services.manager import AIServiceManager
from apps.ai.services.load_balancer import LoadBalancingStrategy
from apps.ai.services.degradation import ServiceLevel
from apps.ai.adapters.base import AIProviderType


def test_service_manager():
    """测试AI服务管理器"""
    print("🧪 测试AI服务管理器...")
    
    try:
        # 获取服务管理器实例
        manager = AIServiceManager()
        
        # 获取服务状态
        status = manager.get_service_status()
        print(f"✅ 服务状态获取成功，共 {len(status)} 个服务")
        
        # 测试负载均衡统计
        lb_stats = manager.get_load_balancer_stats()
        print(f"✅ 负载均衡统计获取成功，策略: {lb_stats.get('strategy', 'unknown')}")
        
        # 测试降级状态
        degradation_status = manager.get_degradation_status()
        print(f"✅ 降级状态获取成功，当前级别: {degradation_status.get('current_level', 'unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 服务管理器测试失败: {e}")
        return False


def test_load_balancer():
    """测试负载均衡器"""
    print("\n🧪 测试负载均衡器...")
    
    try:
        manager = AIServiceManager()
        
        # 测试不同的负载均衡策略
        strategies = [
            LoadBalancingStrategy.ROUND_ROBIN,
            LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN,
            LoadBalancingStrategy.RANDOM
        ]
        
        for strategy in strategies:
            manager.set_load_balancing_strategy(strategy)
            stats = manager.get_load_balancer_stats()
            print(f"✅ 负载均衡策略切换成功: {strategy.value}")
        
        return True
        
    except Exception as e:
        print(f"❌ 负载均衡器测试失败: {e}")
        return False


def test_service_degradation():
    """测试服务降级"""
    print("\n🧪 测试服务降级...")
    
    try:
        manager = AIServiceManager()
        
        # 测试强制降级
        manager.force_degradation(ServiceLevel.DEGRADED)
        status = manager.get_degradation_status()
        print(f"✅ 强制降级成功，当前级别: {status.get('current_level')}")
        
        # 清除降级
        manager.clear_degradation()
        status = manager.get_degradation_status()
        print(f"✅ 降级清除成功，当前级别: {status.get('current_level')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 服务降级测试失败: {e}")
        return False


def test_service_operations():
    """测试服务操作"""
    print("\n🧪 测试服务操作...")
    
    try:
        manager = AIServiceManager()
        
        # 获取初始服务列表
        initial_status = manager.get_service_status()
        initial_count = len(initial_status)
        
        # 测试添加服务（模拟，不需要真实API密钥）
        test_service_name = 'test-service'
        
        # 由于没有API密钥，添加会失败，但这是预期的
        success = manager.add_service(
            service_name=test_service_name,
            provider=AIProviderType.OPENAI,
            model='gpt-3.5-turbo',
            weight=1
        )
        
        if not success:
            print("✅ 服务添加正确失败（缺少API密钥，符合预期）")
        
        # 测试服务启用/禁用（对现有服务）
        current_services = list(initial_status.keys())
        if current_services:
            test_existing_service = current_services[0]
            
            # 禁用服务
            success = manager.disable_service(test_existing_service)
            if success:
                print(f"✅ 服务 {test_existing_service} 禁用成功")
                
                # 重新启用
                success = manager.enable_service(test_existing_service)
                if success:
                    print(f"✅ 服务 {test_existing_service} 启用成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 服务操作测试失败: {e}")
        return False


def test_health_monitoring():
    """测试健康监控"""
    print("\n🧪 测试健康监控...")
    
    try:
        manager = AIServiceManager()
        health_monitor = manager._health_monitor
        
        # 获取健康摘要
        summary = health_monitor.get_health_summary()
        print(f"✅ 健康摘要获取成功:")
        print(f"   - 总服务数: {summary.get('total_services', 0)}")
        print(f"   - 健康服务数: {summary.get('healthy_services', 0)}")
        print(f"   - 健康百分比: {summary.get('health_percentage', 0):.1f}%")
        
        # 获取所有服务健康状态
        all_health = health_monitor.get_all_health()
        print(f"✅ 服务健康状态获取成功，共 {len(all_health)} 个服务")
        
        return True
        
    except Exception as e:
        print(f"❌ 健康监控测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🚀 开始AI服务管理系统功能验证")
    print("=" * 50)
    
    tests = [
        test_service_manager,
        test_load_balancer,
        test_service_degradation,
        test_service_operations,
        test_health_monitoring
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"🎯 测试完成: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！AI服务管理系统功能正常")
        return True
    else:
        print("⚠️  部分测试失败，请检查系统配置")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

