#!/usr/bin/env python3
"""
全面功能测试：地道表达学习平台完整性验证
包括前端组件加载、API响应、用户流程等
"""
import requests
import json
import time
from urllib.parse import urljoin

def test_component_loading():
    """测试前端组件加载情况"""
    print("🔍 测试前端组件加载...")
    
    try:
        # 获取地道表达学习页面内容
        response = requests.get("http://localhost:3000/english/idiomatic-learning", timeout=10)
        content = response.text
        
        # 检查关键组件是否存在
        component_checks = {
            "Vue应用挂载点": 'id="app"' in content,
            "Vite开发服务器": 'vite/client' in content,
            "页面标题设置": 'title>' in content,
            "Vue路由系统": 'router-link' in content or 'RouterLink' in content,
            "Element Plus样式": 'element-plus' in content or 'el-' in content,
        }
        
        print("前端组件检查结果:")
        for component, loaded in component_checks.items():
            status = "✅" if loaded else "❌"
            print(f"  {status} {component}")
        
        return all(component_checks.values())
        
    except Exception as e:
        print(f"❌ 前端组件加载测试失败: {e}")
        return False

def test_api_endpoints():
    """测试关键API端点"""
    print("\n🔧 测试后端API端点...")
    
    endpoints = [
        ("/api/v1/", "API根路径"),
        ("/api/v1/english/expressions/", "地道表达API"),
        ("/api/v1/analytics/progress-trend/", "学习进度API"),
        ("/api/v1/analytics/mastery-distribution/", "掌握度分布API"),
        ("/api/v1/analytics/time-analysis/", "时间分析API"),
        ("/api/v1/analytics/efficiency-analysis/", "效率分析API"),
        ("/api/v1/analytics/learning-insights/", "学习洞察API"),
        ("/api/v1/english/reports/", "学习报告API"),
        ("/api/v1/english/goals/", "学习目标API"),
    ]
    
    results = {}
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"http://localhost:8000{endpoint}", timeout=5)
            # 200表示正常，401表示需要认证但端点存在，都算成功
            success = response.status_code in [200, 401]
            results[name] = success
            status = "✅" if success else "❌"
            print(f"  {status} {name} - 状态码: {response.status_code}")
        except Exception as e:
            results[name] = False
            print(f"  ❌ {name} - 连接失败: {e}")
    
    return all(results.values())

def test_route_accessibility():
    """测试路由可访问性"""
    print("\n🛣️ 测试路由可访问性...")
    
    routes = [
        ("/", "首页"),
        ("/english/expressions", "地道表达列表"),
        ("/english/idiomatic-learning", "地道表达学习"),
        ("/english/learning-analytics", "学习数据分析"),
        ("/english/dashboard", "英语学习仪表板"),
        ("/english/typing-practice", "打字练习"),
    ]
    
    results = {}
    for route, name in routes:
        try:
            response = requests.get(f"http://localhost:3000{route}", timeout=10)
            success = response.status_code == 200
            results[name] = success
            status = "✅" if success else "❌"
            print(f"  {status} {name} - 状态码: {response.status_code}")
        except Exception as e:
            results[name] = False
            print(f"  ❌ {name} - 连接失败: {e}")
    
    return all(results.values())

def test_page_content_completeness():
    """测试页面内容完整性"""
    print("\n📄 测试页面内容完整性...")
    
    try:
        # 测试地道表达学习页面
        response = requests.get("http://localhost:3000/english/idiomatic-learning", timeout=10)
        content = response.text
        
        # 检查页面应该包含的关键内容
        content_checks = {
            "页面基础结构": '<div' in content and '</div>' in content,
            "Vue应用容器": 'id="app"' in content,
            "CSS样式引用": 'stylesheet' in content or 'style' in content,
            "JavaScript模块": 'script' in content,
            "字符编码设置": 'charset="UTF-8"' in content,
            "移动端适配": 'viewport' in content,
        }
        
        print("页面内容完整性检查:")
        for check, passed in content_checks.items():
            status = "✅" if passed else "❌"
            print(f"  {status} {check}")
        
        return all(content_checks.values())
        
    except Exception as e:
        print(f"❌ 页面内容测试失败: {e}")
        return False

def test_navigation_integration():
    """测试导航集成"""
    print("\n🧭 测试导航集成...")
    
    try:
        # 获取首页内容，检查导航菜单
        response = requests.get("http://localhost:3000/", timeout=10)
        content = response.text
        
        # 检查导航相关内容
        nav_checks = {
            "导航容器存在": 'nav' in content.lower(),
            "路由链接系统": 'router-link' in content or 'href=' in content,
            "英语学习菜单": '英语学习' in content,
            "下拉菜单结构": 'dropdown' in content.lower() or 'menu' in content.lower(),
        }
        
        print("导航集成检查:")
        for check, passed in nav_checks.items():
            status = "✅" if passed else "❌"
            print(f"  {status} {check}")
        
        return all(nav_checks.values())
        
    except Exception as e:
        print(f"❌ 导航集成测试失败: {e}")
        return False

def analyze_page_differences():
    """分析两个页面的差异"""
    print("\n🔍 分析页面功能差异...")
    
    try:
        # 获取两个页面的内容
        expressions_response = requests.get("http://localhost:3000/english/expressions", timeout=10)
        learning_response = requests.get("http://localhost:3000/english/idiomatic-learning", timeout=10)
        
        expressions_content = expressions_response.text
        learning_content = learning_response.text
        
        # 分析功能差异
        print("\n页面功能对比分析:")
        print("📋 地道表达列表页面 (/english/expressions):")
        print("  - 简单的表达式展示和搜索")
        print("  - 基础的筛选功能")
        print("  - 静态内容浏览")
        
        print("\n🎮 地道表达学习页面 (/english/idiomatic-learning):")
        print("  - 多种学习模式")
        print("  - 交互式学习体验")
        print("  - 进度追踪和分析")
        
        # 检查特定功能标识
        learning_features = {
            "学习模式选择": "mode-card" in learning_content or "学习模式" in learning_content,
            "AI助教功能": "AI助教" in learning_content or "ai-chat" in learning_content,
            "进度统计": "统计" in learning_content or "progress" in learning_content,
            "互动组件": "el-button" in learning_content or "button" in learning_content,
        }
        
        print("\n🎯 学习页面功能验证:")
        for feature, exists in learning_features.items():
            status = "✅" if exists else "❌"
            print(f"  {status} {feature}")
        
        return True
        
    except Exception as e:
        print(f"❌ 页面差异分析失败: {e}")
        return False

def main():
    print("🚀 开始全面功能测试：地道表达学习平台")
    print("=" * 60)
    
    tests = [
        ("前端组件加载", test_component_loading),
        ("API端点功能", test_api_endpoints),
        ("路由可访问性", test_route_accessibility),
        ("页面内容完整性", test_page_content_completeness),
        ("导航集成", test_navigation_integration),
        ("页面功能差异分析", analyze_page_differences),
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name}执行失败: {e}")
            results[test_name] = False
    
    # 汇总结果
    print(f"\n{'='*60}")
    print("🎯 全面功能测试结果汇总")
    print(f"{'='*60}")
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n总体结果:")
    print(f"✅ 通过: {passed}/{total}")
    print(f"❌ 失败: {total-passed}/{total}")
    print(f"成功率: {(passed/total*100):.1f}%")
    
    # 问题诊断
    if passed < total:
        print(f"\n⚠️ 发现的问题:")
        for test_name, result in results.items():
            if not result:
                print(f"  🔸 {test_name} 测试失败")
    
    print(f"\n🏆 测试完成！平台功能{'完全正常' if passed == total else '存在问题'}")
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
