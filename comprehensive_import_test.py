#!/usr/bin/env python3
"""
全面的前端导入检查测试
使用Playwright检查所有组件的导入和加载情况
"""
import asyncio
from playwright.async_api import async_playwright
import json
import re
from pathlib import Path

class ImportChecker:
    def __init__(self):
        self.test_results = {
            "pages": {},
            "components": {},
            "errors": [],
            "summary": {}
        }
    
    async def check_page_imports(self, page, url, page_name):
        """检查特定页面的导入和错误"""
        console_errors = []
        js_errors = []
        network_failures = []
        
        # 监听错误
        page.on("console", lambda msg: 
            console_errors.append({
                "type": msg.type,
                "text": msg.text,
                "location": msg.location
            }) if msg.type in ["error", "warning"] else None)
        
        page.on("pageerror", lambda error: js_errors.append(str(error)))
        
        page.on("response", lambda response:
            network_failures.append({
                "url": response.url,
                "status": response.status,
                "status_text": response.status_text
            }) if response.status >= 400 else None)
        
        try:
            print(f"🔍 检查页面: {page_name} ({url})")
            
            # 导航到页面
            response = await page.goto(url, wait_until="domcontentloaded", timeout=15000)
            
            # 等待Vue应用加载
            await page.wait_for_timeout(3000)
            
            # 检查页面是否正确渲染
            app_element = await page.query_selector("#app")
            has_vue_app = app_element is not None
            
            # 检查是否有Vue错误
            vue_error_elements = await page.query_selector_all(".vue-error, .error-boundary")
            has_vue_errors = len(vue_error_elements) > 0
            
            # 检查特定的组件是否加载
            component_checks = {}
            if "idiomatic-learning" in url:
                # 检查学习页面的关键组件
                component_selectors = {
                    "expression_card": ".expression-card, [data-testid='expression-card']",
                    "learning_modes": ".learning-modes, [data-testid='learning-modes']",
                    "ai_assistant": ".ai-assistant, [data-testid='ai-assistant']",
                    "dashboard": ".learning-dashboard, [data-testid='dashboard']"
                }
                
                for component, selector in component_selectors.items():
                    try:
                        element = await page.query_selector(selector)
                        component_checks[component] = element is not None
                    except:
                        component_checks[component] = False
            
            # 分析错误类型
            import_errors = []
            icon_errors = []
            module_errors = []
            
            for error in console_errors + js_errors:
                error_text = error if isinstance(error, str) else error.get("text", "")
                
                if "import" in error_text.lower() or "module" in error_text.lower():
                    if "icons-vue" in error_text:
                        icon_errors.append(error_text)
                    elif "does not provide an export" in error_text:
                        import_errors.append(error_text)
                    else:
                        module_errors.append(error_text)
            
            result = {
                "url": url,
                "status_code": response.status,
                "has_vue_app": has_vue_app,
                "has_vue_errors": has_vue_errors,
                "console_errors": len(console_errors),
                "js_errors": len(js_errors),
                "network_failures": len(network_failures),
                "import_errors": import_errors,
                "icon_errors": icon_errors,
                "module_errors": module_errors,
                "component_checks": component_checks,
                "success": (
                    response.status == 200 and
                    has_vue_app and
                    not has_vue_errors and
                    len(import_errors) == 0 and
                    len(icon_errors) == 0
                )
            }
            
            self.test_results["pages"][page_name] = result
            
            status = "✅" if result["success"] else "❌"
            print(f"  {status} 状态码: {response.status}")
            print(f"  {status} Vue应用: {'已挂载' if has_vue_app else '未挂载'}")
            print(f"  {'✅' if len(import_errors) == 0 else '❌'} 导入错误: {len(import_errors)}个")
            print(f"  {'✅' if len(icon_errors) == 0 else '❌'} 图标错误: {len(icon_errors)}个")
            
            if component_checks:
                print("  🧩 组件检查:")
                for component, loaded in component_checks.items():
                    status = "✅" if loaded else "❌"
                    print(f"    {status} {component}")
            
            return result
            
        except Exception as e:
            error_result = {
                "url": url,
                "error": str(e),
                "success": False
            }
            self.test_results["pages"][page_name] = error_result
            print(f"  ❌ 页面检查失败: {e}")
            return error_result

    async def run_comprehensive_test(self):
        """运行全面的导入测试"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                print("🎯 全面的前端导入检查测试")
                print("=" * 50)
                
                # 检查前端服务
                try:
                    response = await page.goto("http://localhost:3000/", timeout=5000)
                    if response.status != 200:
                        print(f"❌ 前端服务异常，状态码: {response.status}")
                        return False
                    print("✅ 前端服务运行正常")
                except Exception as e:
                    print(f"❌ 前端服务无法访问: {e}")
                    return False
                
                # 测试页面列表
                test_pages = [
                    ("首页", "http://localhost:3000/"),
                    ("地道表达列表", "http://localhost:3000/english/expressions"),
                    ("地道表达学习", "http://localhost:3000/english/idiomatic-learning"),
                    ("学习分析", "http://localhost:3000/english/learning-analytics")
                ]
                
                # 依次测试每个页面
                for page_name, url in test_pages:
                    await self.check_page_imports(page, url, page_name)
                    await page.wait_for_timeout(1000)  # 页面间间隔
                
                # 生成汇总报告
                self.generate_summary()
                
                return self.test_results["summary"]["overall_success"]
                
            finally:
                await browser.close()
    
    def generate_summary(self):
        """生成测试汇总"""
        total_pages = len(self.test_results["pages"])
        successful_pages = sum(1 for result in self.test_results["pages"].values() 
                              if result.get("success", False))
        
        total_import_errors = sum(len(result.get("import_errors", [])) 
                                 for result in self.test_results["pages"].values())
        total_icon_errors = sum(len(result.get("icon_errors", [])) 
                               for result in self.test_results["pages"].values())
        total_module_errors = sum(len(result.get("module_errors", [])) 
                                 for result in self.test_results["pages"].values())
        
        self.test_results["summary"] = {
            "total_pages": total_pages,
            "successful_pages": successful_pages,
            "success_rate": successful_pages / total_pages if total_pages > 0 else 0,
            "total_import_errors": total_import_errors,
            "total_icon_errors": total_icon_errors,
            "total_module_errors": total_module_errors,
            "overall_success": (
                successful_pages == total_pages and
                total_import_errors == 0 and
                total_icon_errors == 0
            )
        }
        
        print(f"\n{'='*50}")
        print("📊 测试汇总报告")
        print(f"{'='*50}")
        print(f"📄 测试页面: {total_pages}个")
        print(f"✅ 成功页面: {successful_pages}个")
        print(f"📈 成功率: {self.test_results['summary']['success_rate']:.1%}")
        print(f"🚫 导入错误: {total_import_errors}个")
        print(f"🎨 图标错误: {total_icon_errors}个")
        print(f"📦 模块错误: {total_module_errors}个")
        
        overall_status = "✅ 全部通过" if self.test_results["summary"]["overall_success"] else "❌ 存在问题"
        print(f"\n🏆 整体结果: {overall_status}")
        
        # 详细错误报告
        if total_import_errors + total_icon_errors + total_module_errors > 0:
            print(f"\n🔍 错误详情:")
            for page_name, result in self.test_results["pages"].items():
                if not result.get("success", False):
                    print(f"\n📄 {page_name}:")
                    for error in result.get("import_errors", []):
                        print(f"  🚫 导入错误: {error}")
                    for error in result.get("icon_errors", []):
                        print(f"  🎨 图标错误: {error}")
                    for error in result.get("module_errors", []):
                        print(f"  📦 模块错误: {error}")

async def main():
    checker = ImportChecker()
    success = await checker.run_comprehensive_test()
    
    # 保存详细结果
    with open("comprehensive_import_test_results.json", "w", encoding="utf-8") as f:
        json.dump(checker.test_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 详细结果已保存到: comprehensive_import_test_results.json")
    
    return success

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
