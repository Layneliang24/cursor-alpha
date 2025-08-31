#!/usr/bin/env python3
"""
Vue Router配置验证测试
"""
import asyncio
from playwright.async_api import async_playwright
import json
from pathlib import Path

class RouterValidator:
    def __init__(self):
        self.validation_results = {
            "routes": {},
            "navigation_tests": {},
            "summary": {}
        }
        
        # 关键路由配置（从router/index.js中提取）
        self.key_routes = [
            {"path": "/", "name": "Home", "component": "@/views/Home.vue"},
            {"path": "/english/expressions", "name": "EnglishExpressions", "component": "@/views/english/Expressions.vue"},
            {"path": "/english/idiomatic-learning", "name": "IdiomaticLearning", "component": "@/views/idiomatic-expressions/ExpressionLearning.vue"},
            {"path": "/english/learning-analytics", "name": "LearningAnalytics", "component": "@/views/english/LearningAnalytics.vue"},
            {"path": "/login", "name": "Login", "component": "@/views/auth/Login.vue"},
        ]
    
    def check_component_files(self):
        """检查路由对应的组件文件是否存在"""
        print("🔍 检查路由组件文件是否存在...")
        
        component_checks = {}
        
        for route in self.key_routes:
            component_path = route["component"].replace("@/", "frontend/src/")
            file_path = Path(component_path)
            
            exists = file_path.exists()
            component_checks[route["name"]] = {
                "path": route["path"],
                "component": route["component"],
                "file_path": str(file_path),
                "exists": exists
            }
            
            status = "✅" if exists else "❌"
            print(f"  {status} {route['name']}: {component_path}")
        
        self.validation_results["component_files"] = component_checks
        return component_checks
    
    async def test_route_navigation(self):
        """测试路由导航功能"""
        print("\n🧭 测试路由导航功能...")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            navigation_results = {}
            
            try:
                # 检查前端服务
                response = await page.goto("http://localhost:3000/", timeout=5000)
                if response.status != 200:
                    print(f"❌ 前端服务异常，状态码: {response.status}")
                    return {}
                
                for route in self.key_routes:
                    route_name = route["name"]
                    route_path = route["path"]
                    
                    try:
                        print(f"  🔍 测试路由: {route_name} ({route_path})")
                        
                        # 导航到路由
                        response = await page.goto(f"http://localhost:3000{route_path}", 
                                                 wait_until="domcontentloaded", timeout=10000)
                        
                        # 等待Vue应用加载
                        await page.wait_for_timeout(2000)
                        
                        # 检查页面状态
                        current_url = page.url
                        page_title = await page.title()
                        
                        # 检查是否有Vue错误
                        console_errors = []
                        page.on("console", lambda msg: 
                            console_errors.append(msg.text) if msg.type == "error" else None)
                        
                        # 检查页面内容
                        app_element = await page.query_selector("#app")
                        has_vue_app = app_element is not None
                        
                        # 检查是否正确路由
                        is_correct_route = route_path in current_url or current_url.endswith(route_path)
                        
                        # 特殊处理登录重定向
                        if route_path != "/login" and "login" in current_url.lower():
                            # 可能是因为需要认证而重定向到登录页面
                            is_auth_redirect = True
                        else:
                            is_auth_redirect = False
                        
                        navigation_results[route_name] = {
                            "path": route_path,
                            "status_code": response.status,
                            "current_url": current_url,
                            "page_title": page_title,
                            "has_vue_app": has_vue_app,
                            "is_correct_route": is_correct_route,
                            "is_auth_redirect": is_auth_redirect,
                            "console_errors": len(console_errors),
                            "success": (
                                response.status == 200 and
                                has_vue_app and
                                (is_correct_route or is_auth_redirect)
                            )
                        }
                        
                        status = "✅" if navigation_results[route_name]["success"] else "❌"
                        print(f"    {status} 状态码: {response.status}, URL: {current_url}")
                        
                        if is_auth_redirect:
                            print(f"    ℹ️ 认证重定向: 需要登录访问")
                        
                    except Exception as e:
                        navigation_results[route_name] = {
                            "path": route_path,
                            "error": str(e),
                            "success": False
                        }
                        print(f"    ❌ 导航失败: {e}")
                
            finally:
                await browser.close()
            
            self.validation_results["navigation_tests"] = navigation_results
            return navigation_results
    
    async def test_router_guards(self):
        """测试路由守卫功能"""
        print("\n🛡️ 测试路由守卫功能...")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            guard_results = {}
            
            try:
                # 测试未认证访问需要认证的路由
                protected_routes = [
                    "/english/expressions",
                    "/english/idiomatic-learning",
                    "/english/learning-analytics"
                ]
                
                for route_path in protected_routes:
                    try:
                        print(f"  🔍 测试受保护路由: {route_path}")
                        
                        response = await page.goto(f"http://localhost:3000{route_path}", 
                                                 wait_until="domcontentloaded", timeout=10000)
                        
                        await page.wait_for_timeout(2000)
                        
                        current_url = page.url
                        
                        # 检查是否重定向到登录页面
                        is_redirected_to_login = "login" in current_url.lower()
                        
                        guard_results[route_path] = {
                            "original_path": route_path,
                            "current_url": current_url,
                            "redirected_to_login": is_redirected_to_login,
                            "guard_working": is_redirected_to_login,
                            "success": is_redirected_to_login
                        }
                        
                        status = "✅" if is_redirected_to_login else "❌"
                        print(f"    {status} 路由守卫: {'正常重定向到登录' if is_redirected_to_login else '未重定向'}")
                        
                    except Exception as e:
                        guard_results[route_path] = {
                            "original_path": route_path,
                            "error": str(e),
                            "success": False
                        }
                        print(f"    ❌ 测试失败: {e}")
                
            finally:
                await browser.close()
            
            self.validation_results["router_guards"] = guard_results
            return guard_results
    
    def generate_summary(self):
        """生成验证汇总"""
        component_files = self.validation_results.get("component_files", {})
        navigation_tests = self.validation_results.get("navigation_tests", {})
        router_guards = self.validation_results.get("router_guards", {})
        
        # 统计组件文件
        total_components = len(component_files)
        existing_components = sum(1 for check in component_files.values() if check["exists"])
        
        # 统计导航测试
        total_navigation = len(navigation_tests)
        successful_navigation = sum(1 for result in navigation_tests.values() if result.get("success", False))
        
        # 统计路由守卫
        total_guards = len(router_guards)
        working_guards = sum(1 for result in router_guards.values() if result.get("success", False))
        
        self.validation_results["summary"] = {
            "component_files": {
                "total": total_components,
                "existing": existing_components,
                "missing": total_components - existing_components
            },
            "navigation": {
                "total": total_navigation,
                "successful": successful_navigation,
                "failed": total_navigation - successful_navigation
            },
            "router_guards": {
                "total": total_guards,
                "working": working_guards,
                "not_working": total_guards - working_guards
            },
            "overall_success": (
                existing_components == total_components and
                successful_navigation >= total_navigation * 0.8 and  # 允许80%成功率（考虑认证重定向）
                working_guards == total_guards
            )
        }
        
        print(f"\n{'='*50}")
        print("📊 Vue Router验证汇总")
        print(f"{'='*50}")
        
        print(f"📁 组件文件检查:")
        print(f"  ✅ 存在: {existing_components}/{total_components}")
        print(f"  ❌ 缺失: {total_components - existing_components}")
        
        print(f"🧭 路由导航测试:")
        print(f"  ✅ 成功: {successful_navigation}/{total_navigation}")
        print(f"  ❌ 失败: {total_navigation - successful_navigation}")
        
        print(f"🛡️ 路由守卫测试:")
        print(f"  ✅ 正常: {working_guards}/{total_guards}")
        print(f"  ❌ 异常: {total_guards - working_guards}")
        
        overall_status = "✅ 全部通过" if self.validation_results["summary"]["overall_success"] else "⚠️ 存在问题"
        print(f"\n🏆 整体结果: {overall_status}")
        
        return self.validation_results["summary"]
    
    async def run_full_validation(self):
        """运行完整的路由验证"""
        print("🎯 Vue Router配置验证测试")
        print("=" * 50)
        
        # 1. 检查组件文件
        self.check_component_files()
        
        # 2. 测试路由导航
        await self.test_route_navigation()
        
        # 3. 测试路由守卫
        await self.test_router_guards()
        
        # 4. 生成汇总
        summary = self.generate_summary()
        
        return summary

async def main():
    validator = RouterValidator()
    summary = await validator.run_full_validation()
    
    # 保存详细结果
    with open("router_validation_results.json", "w", encoding="utf-8") as f:
        json.dump(validator.validation_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 详细结果已保存到: router_validation_results.json")
    
    return summary["overall_success"]

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ 测试被用户中断")
        exit(1)
    except Exception as e:
        print(f"❌ 测试执行异常: {e}")
        exit(1)
