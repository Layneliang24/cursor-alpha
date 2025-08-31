#!/usr/bin/env python3
"""
Playwright测试：验证Element Plus图标修复效果
"""
import asyncio
from playwright.async_api import async_playwright
import json

async def test_idiomatic_learning_page():
    """测试地道表达学习页面的真实浏览器加载情况"""
    
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        # 收集控制台错误
        console_errors = []
        page.on("console", lambda msg: 
            console_errors.append(msg.text) if msg.type == "error" else None)
        
        # 收集JavaScript错误
        js_errors = []
        page.on("pageerror", lambda error: js_errors.append(str(error)))
        
        try:
            print("🚀 开始测试地道表达学习页面...")
            
            # 导航到页面
            print("📍 导航到页面...")
            response = await page.goto("http://localhost:3000/english/idiomatic-learning", 
                                     wait_until="domcontentloaded", timeout=30000)
            
            print(f"✅ 页面响应状态: {response.status}")
            
            # 等待Vue应用加载
            print("⏳ 等待Vue应用加载...")
            await page.wait_for_timeout(3000)
            
            # 检查页面标题
            title = await page.title()
            print(f"📄 页面标题: {title}")
            
            # 检查是否有Vue应用挂载点
            app_element = await page.query_selector("#app")
            if app_element:
                print("✅ Vue应用挂载点存在")
            else:
                print("❌ Vue应用挂载点不存在")
            
            # 检查页面内容是否加载
            print("🔍 检查页面内容加载...")
            
            # 等待可能的动态内容加载
            try:
                await page.wait_for_selector("body", timeout=5000)
                print("✅ 页面body元素已加载")
            except:
                print("⚠️ 页面加载可能有问题")
            
            # 获取页面HTML内容
            content = await page.content()
            
            # 检查是否包含Vue相关内容
            vue_indicators = {
                "Vue挂载点": 'id="app"' in content,
                "Vite客户端": 'vite/client' in content,
                "Vue模块": '/src/main.js' in content,
            }
            
            print("📊 Vue应用检查结果:")
            for indicator, present in vue_indicators.items():
                status = "✅" if present else "❌"
                print(f"  {status} {indicator}")
            
            # 检查控制台错误
            print(f"\n🔍 控制台错误检查:")
            if console_errors:
                print(f"❌ 发现 {len(console_errors)} 个控制台错误:")
                for error in console_errors[:5]:  # 只显示前5个
                    print(f"  - {error}")
                if len(console_errors) > 5:
                    print(f"  ... 还有 {len(console_errors) - 5} 个错误")
            else:
                print("✅ 无控制台错误")
            
            # 检查JavaScript错误
            print(f"\n🔍 JavaScript错误检查:")
            if js_errors:
                print(f"❌ 发现 {len(js_errors)} 个JavaScript错误:")
                for error in js_errors[:3]:  # 只显示前3个
                    print(f"  - {error}")
                if len(js_errors) > 3:
                    print(f"  ... 还有 {len(js_errors) - 3} 个错误")
            else:
                print("✅ 无JavaScript错误")
            
            # 尝试检测特定的Element Plus图标错误
            robot_error_found = any("Robot" in error for error in console_errors + js_errors)
            if robot_error_found:
                print("❌ 仍然存在Robot图标相关错误")
            else:
                print("✅ 未发现Robot图标相关错误")
            
            # 检查网络请求
            print(f"\n🌐 检查关键资源加载...")
            
            # 检查主要的JavaScript模块是否加载成功
            try:
                main_js_response = await page.goto("http://localhost:3000/src/main.js", 
                                                  wait_until="domcontentloaded")
                if main_js_response.status == 200:
                    print("✅ main.js 加载成功")
                else:
                    print(f"❌ main.js 加载失败: {main_js_response.status}")
            except Exception as e:
                print(f"❌ main.js 加载异常: {e}")
            
            # 生成测试报告
            test_result = {
                "page_status": response.status,
                "page_title": title,
                "vue_app_mounted": app_element is not None,
                "console_errors": len(console_errors),
                "js_errors": len(js_errors),
                "robot_error_fixed": not robot_error_found,
                "vue_indicators": vue_indicators
            }
            
            return test_result
            
        except Exception as e:
            print(f"❌ 测试执行失败: {e}")
            return {
                "error": str(e),
                "console_errors": len(console_errors),
                "js_errors": len(js_errors)
            }
        
        finally:
            await browser.close()

async def test_navigation_flow():
    """测试导航流程"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            print("\n🧭 测试导航流程...")
            
            # 从首页开始
            await page.goto("http://localhost:3000/", wait_until="domcontentloaded")
            print("✅ 首页加载成功")
            
            # 尝试导航到地道表达学习页面
            await page.goto("http://localhost:3000/english/idiomatic-learning", 
                          wait_until="domcontentloaded")
            print("✅ 地道表达学习页面导航成功")
            
            # 检查URL是否正确
            current_url = page.url
            if "idiomatic-learning" in current_url:
                print("✅ URL路径正确")
            else:
                print(f"❌ URL路径异常: {current_url}")
            
            return {"navigation_success": True, "final_url": current_url}
            
        except Exception as e:
            print(f"❌ 导航测试失败: {e}")
            return {"navigation_success": False, "error": str(e)}
        
        finally:
            await browser.close()

async def main():
    print("🎯 Playwright真实浏览器测试 - 验证Element Plus图标修复")
    print("=" * 60)
    
    # 检查前端服务是否运行
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            response = await page.goto("http://localhost:3000/", timeout=5000)
            if response.status != 200:
                print(f"❌ 前端服务异常，状态码: {response.status}")
                return False
        except Exception as e:
            print(f"❌ 前端服务无法访问: {e}")
            print("请确保运行 'cd frontend && npm run dev'")
            return False
        finally:
            await browser.close()
    
    # 执行测试
    results = {}
    
    # 测试1: 页面加载和错误检查
    page_result = await test_idiomatic_learning_page()
    results["page_test"] = page_result
    
    # 测试2: 导航流程
    nav_result = await test_navigation_flow()
    results["navigation_test"] = nav_result
    
    # 汇总结果
    print(f"\n{'='*60}")
    print("🎯 测试结果汇总")
    print(f"{'='*60}")
    
    if "error" not in page_result:
        print(f"📊 页面测试结果:")
        print(f"  - 页面状态码: {page_result.get('page_status', 'N/A')}")
        print(f"  - Vue应用挂载: {'✅' if page_result.get('vue_app_mounted') else '❌'}")
        print(f"  - 控制台错误: {page_result.get('console_errors', 0)}个")
        print(f"  - JavaScript错误: {page_result.get('js_errors', 0)}个")
        print(f"  - Robot图标修复: {'✅' if page_result.get('robot_error_fixed') else '❌'}")
    else:
        print(f"❌ 页面测试失败: {page_result.get('error')}")
    
    if nav_result.get("navigation_success"):
        print(f"🧭 导航测试: ✅ 成功")
    else:
        print(f"🧭 导航测试: ❌ 失败 - {nav_result.get('error', '未知错误')}")
    
    # 判断整体成功
    overall_success = (
        page_result.get("page_status") == 200 and
        page_result.get("robot_error_fixed", False) and
        page_result.get("console_errors", 1) == 0 and
        page_result.get("js_errors", 1) == 0 and
        nav_result.get("navigation_success", False)
    )
    
    print(f"\n🏆 整体测试结果: {'✅ 成功' if overall_success else '❌ 需要进一步修复'}")
    
    # 保存详细结果到文件
    with open("playwright_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"📄 详细结果已保存到: playwright_test_results.json")
    
    return overall_success

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
