#!/usr/bin/env python3
"""
E2E测试：地道表达学习功能完整性测试
"""
import requests
import json
import time
from urllib.parse import urljoin

# 测试配置
BASE_URL = "http://localhost:3000"
API_BASE_URL = "http://localhost:8000/api/v1"

class E2ETestResults:
    def __init__(self):
        self.tests = []
        self.passed = 0
        self.failed = 0
    
    def add_test(self, name, passed, message=""):
        self.tests.append({
            'name': name,
            'passed': passed,
            'message': message
        })
        if passed:
            self.passed += 1
        else:
            self.failed += 1
    
    def print_results(self):
        print(f"\n{'='*60}")
        print(f"E2E测试结果汇总")
        print(f"{'='*60}")
        print(f"总测试数: {len(self.tests)}")
        print(f"✅ 通过: {self.passed}")
        print(f"❌ 失败: {self.failed}")
        print(f"成功率: {(self.passed/len(self.tests)*100):.1f}%")
        print(f"{'='*60}")
        
        for test in self.tests:
            status = "✅ PASS" if test['passed'] else "❌ FAIL"
            print(f"{status} - {test['name']}")
            if test['message']:
                print(f"     {test['message']}")
        
        return self.failed == 0

def test_frontend_accessibility():
    """测试前端页面可访问性"""
    results = E2ETestResults()
    
    # 测试1: 首页可访问
    try:
        response = requests.get(BASE_URL, timeout=10)
        results.add_test(
            "首页可访问性", 
            response.status_code == 200,
            f"状态码: {response.status_code}"
        )
    except Exception as e:
        results.add_test("首页可访问性", False, f"连接失败: {str(e)}")
    
    # 测试2: 地道表达列表页面可访问
    try:
        response = requests.get(f"{BASE_URL}/english/expressions", timeout=10)
        results.add_test(
            "地道表达列表页面可访问性", 
            response.status_code == 200,
            f"状态码: {response.status_code}"
        )
    except Exception as e:
        results.add_test("地道表达列表页面可访问性", False, f"连接失败: {str(e)}")
    
    # 测试3: 地道表达学习页面可访问
    try:
        response = requests.get(f"{BASE_URL}/english/idiomatic-learning", timeout=10)
        results.add_test(
            "地道表达学习页面可访问性", 
            response.status_code == 200,
            f"状态码: {response.status_code}"
        )
    except Exception as e:
        results.add_test("地道表达学习页面可访问性", False, f"连接失败: {str(e)}")
    
    return results

def test_backend_api():
    """测试后端API功能"""
    results = E2ETestResults()
    
    # 测试1: API健康检查
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=10)
        results.add_test(
            "后端API基础可访问性", 
            response.status_code == 200,
            f"状态码: {response.status_code}"
        )
    except Exception as e:
        results.add_test("后端API基础可访问性", False, f"连接失败: {str(e)}")
    
    # 测试2: 地道表达API
    try:
        response = requests.get(f"{API_BASE_URL}/english/expressions/", timeout=10)
        results.add_test(
            "地道表达API可访问性", 
            response.status_code in [200, 401],  # 401表示需要认证，但API存在
            f"状态码: {response.status_code}"
        )
    except Exception as e:
        results.add_test("地道表达API可访问性", False, f"连接失败: {str(e)}")
    
    # 测试3: 学习分析API
    try:
        response = requests.get(f"{API_BASE_URL}/analytics/progress-trend/", timeout=10)
        results.add_test(
            "学习分析API可访问性", 
            response.status_code in [200, 401],  # 401表示需要认证，但API存在
            f"状态码: {response.status_code}"
        )
    except Exception as e:
        results.add_test("学习分析API可访问性", False, f"连接失败: {str(e)}")
    
    return results

def test_route_conflicts():
    """测试路由冲突问题"""
    results = E2ETestResults()
    
    routes_to_test = [
        ("/english/expressions", "地道表达列表页面"),
        ("/english/idiomatic-learning", "地道表达学习页面"),
        ("/english/learning-analytics", "学习数据分析页面")
    ]
    
    for route, name in routes_to_test:
        try:
            response = requests.get(f"{BASE_URL}{route}", timeout=10)
            # 检查返回的内容是否为HTML而不是错误页面
            is_html = 'text/html' in response.headers.get('content-type', '')
            content = response.text
            is_not_error = '404' not in content and 'Not Found' not in content
            
            results.add_test(
                f"{name}路由正常", 
                response.status_code == 200 and is_html and is_not_error,
                f"状态码: {response.status_code}, HTML: {is_html}, 无错误: {is_not_error}"
            )
        except Exception as e:
            results.add_test(f"{name}路由正常", False, f"连接失败: {str(e)}")
    
    return results

def main():
    print("🚀 开始E2E测试：地道表达学习功能完整性测试")
    print("=" * 60)
    
    all_results = []
    
    # 前端可访问性测试
    print("\n📱 测试前端页面可访问性...")
    frontend_results = test_frontend_accessibility()
    all_results.append(frontend_results)
    
    # 后端API测试
    print("\n🔧 测试后端API功能...")
    backend_results = test_backend_api()
    all_results.append(backend_results)
    
    # 路由冲突测试
    print("\n🛣️ 测试路由配置...")
    route_results = test_route_conflicts()
    all_results.append(route_results)
    
    # 汇总结果
    total_passed = sum(r.passed for r in all_results)
    total_failed = sum(r.failed for r in all_results)
    total_tests = sum(len(r.tests) for r in all_results)
    
    print(f"\n🎯 E2E测试完整性分析")
    print(f"{'='*60}")
    print(f"总测试覆盖范围:")
    print(f"  - 前端页面可访问性: {len(frontend_results.tests)}项测试")
    print(f"  - 后端API功能性: {len(backend_results.tests)}项测试")
    print(f"  - 路由配置正确性: {len(route_results.tests)}项测试")
    print(f"")
    print(f"整体测试结果:")
    print(f"  总测试数: {total_tests}")
    print(f"  ✅ 通过: {total_passed}")
    print(f"  ❌ 失败: {total_failed}")
    print(f"  成功率: {(total_passed/total_tests*100):.1f}%")
    
    # 详细结果
    for i, results in enumerate(all_results, 1):
        print(f"\n📊 测试组 {i} 详细结果:")
        results.print_results()
    
    # 问题分析和建议
    if total_failed > 0:
        print(f"\n⚠️ 发现的问题和建议:")
        print(f"{'='*60}")
        
        if frontend_results.failed > 0:
            print("🔸 前端问题:")
            print("  - 检查前端开发服务器是否正常运行")
            print("  - 确认Vue路由配置是否正确")
            print("  - 检查组件文件是否存在且无语法错误")
        
        if backend_results.failed > 0:
            print("🔸 后端问题:")
            print("  - 检查Django服务器是否正常运行")
            print("  - 确认API端点配置是否正确")
            print("  - 检查数据库连接和迁移状态")
        
        if route_results.failed > 0:
            print("🔸 路由问题:")
            print("  - 检查是否存在路由冲突")
            print("  - 确认所有路由对应的组件都存在")
            print("  - 检查路由权限配置是否正确")
    
    print(f"\n🎉 E2E测试完成！")
    return total_failed == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
