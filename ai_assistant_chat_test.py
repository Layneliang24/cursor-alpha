#!/usr/bin/env python3
"""
AI助教聊天组件功能测试
"""
import asyncio
from playwright.async_api import async_playwright
import json
import time

class AIAssistantChatTester:
    def __init__(self):
        self.test_results = {
            "component_loading": {},
            "ui_interaction": {},
            "api_communication": {},
            "error_handling": {},
            "summary": {}
        }
    
    async def test_component_loading(self, page):
        """测试AI助教聊天组件加载"""
        print("🔍 测试AI助教聊天组件加载...")
        
        try:
            # 导航到地道表达学习页面
            response = await page.goto("http://localhost:3000/english/idiomatic-learning", 
                                     wait_until="domcontentloaded", timeout=15000)
            
            if response.status != 200:
                print(f"❌ 页面加载失败，状态码: {response.status}")
                return {"success": False, "error": f"页面状态码: {response.status}"}
            
            # 等待页面加载
            await page.wait_for_timeout(3000)
            
            # 检查是否有AI助教相关的元素
            ai_elements_checks = {
                "ai_chat_button": {
                    "selectors": [
                        "button[data-testid='ai-chat-button']",
                        ".ai-chat-button",
                        "button:has-text('AI助教')",
                        "button:has-text('智能助教')",
                        "[class*='ai']:has-text('助教')",
                        "button[title*='AI']",
                        "button[title*='助教']"
                    ],
                    "found": False,
                    "element": None
                },
                "chat_dialog": {
                    "selectors": [
                        ".ai-chat-dialog",
                        "[data-testid='ai-chat-dialog']",
                        ".el-dialog:has-text('AI助教')",
                        ".chat-container",
                        "[class*='chat'][class*='dialog']"
                    ],
                    "found": False,
                    "element": None
                }
            }
            
            # 检查AI聊天按钮
            for selector in ai_elements_checks["ai_chat_button"]["selectors"]:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        ai_elements_checks["ai_chat_button"]["found"] = True
                        ai_elements_checks["ai_chat_button"]["element"] = element
                        print(f"  ✅ 找到AI聊天按钮: {selector}")
                        break
                except:
                    continue
            
            if not ai_elements_checks["ai_chat_button"]["found"]:
                print("  ❌ 未找到AI聊天按钮")
            
            # 尝试点击AI聊天按钮（如果找到）
            chat_dialog_opened = False
            if ai_elements_checks["ai_chat_button"]["found"]:
                try:
                    await ai_elements_checks["ai_chat_button"]["element"].click()
                    await page.wait_for_timeout(2000)
                    
                    # 检查聊天对话框是否打开
                    for selector in ai_elements_checks["chat_dialog"]["selectors"]:
                        try:
                            element = await page.query_selector(selector)
                            if element:
                                is_visible = await element.is_visible()
                                if is_visible:
                                    ai_elements_checks["chat_dialog"]["found"] = True
                                    ai_elements_checks["chat_dialog"]["element"] = element
                                    chat_dialog_opened = True
                                    print(f"  ✅ AI聊天对话框已打开: {selector}")
                                    break
                        except:
                            continue
                    
                    if not chat_dialog_opened:
                        print("  ⚠️ AI聊天按钮可点击，但对话框未打开")
                
                except Exception as e:
                    print(f"  ❌ 点击AI聊天按钮失败: {e}")
            
            # 检查页面内容，看是否有AI助教相关的文字
            page_content = await page.content()
            ai_text_indicators = [
                "AI助教" in page_content,
                "智能助教" in page_content,
                "AI聊天" in page_content,
                "ChatDotSquare" in page_content,  # 我们修复的图标
            ]
            
            has_ai_text = any(ai_text_indicators)
            
            result = {
                "page_loaded": response.status == 200,
                "ai_button_found": ai_elements_checks["ai_chat_button"]["found"],
                "chat_dialog_accessible": chat_dialog_opened,
                "has_ai_text_content": has_ai_text,
                "ai_text_indicators": ai_text_indicators,
                "success": (
                    response.status == 200 and
                    (ai_elements_checks["ai_chat_button"]["found"] or has_ai_text)
                )
            }
            
            self.test_results["component_loading"] = result
            return result
            
        except Exception as e:
            error_result = {"success": False, "error": str(e)}
            self.test_results["component_loading"] = error_result
            print(f"❌ 组件加载测试失败: {e}")
            return error_result
    
    async def test_ui_interaction(self, page):
        """测试UI交互功能"""
        print("\n🖱️ 测试UI交互功能...")
        
        try:
            # 尝试找到并测试各种UI元素
            ui_tests = {
                "input_field": {
                    "selectors": [
                        "input[placeholder*='消息']",
                        "input[placeholder*='输入']",
                        "textarea[placeholder*='消息']",
                        ".chat-input input",
                        "[data-testid='chat-input']"
                    ],
                    "test_passed": False
                },
                "send_button": {
                    "selectors": [
                        "button:has-text('发送')",
                        "button[title='发送']",
                        ".send-button",
                        "[data-testid='send-button']"
                    ],
                    "test_passed": False
                },
                "message_area": {
                    "selectors": [
                        ".chat-messages",
                        ".message-list",
                        "[data-testid='messages']",
                        ".conversation"
                    ],
                    "test_passed": False
                }
            }
            
            for element_type, config in ui_tests.items():
                for selector in config["selectors"]:
                    try:
                        element = await page.query_selector(selector)
                        if element:
                            is_visible = await element.is_visible()
                            if is_visible:
                                config["test_passed"] = True
                                print(f"  ✅ {element_type} 元素可见: {selector}")
                                break
                    except:
                        continue
                
                if not config["test_passed"]:
                    print(f"  ❌ {element_type} 元素未找到")
            
            # 检查页面是否有基本的聊天界面结构
            basic_chat_structure = (
                ui_tests["input_field"]["test_passed"] or
                ui_tests["send_button"]["test_passed"] or
                ui_tests["message_area"]["test_passed"]
            )
            
            result = {
                "ui_elements": ui_tests,
                "has_basic_chat_structure": basic_chat_structure,
                "success": basic_chat_structure
            }
            
            self.test_results["ui_interaction"] = result
            return result
            
        except Exception as e:
            error_result = {"success": False, "error": str(e)}
            self.test_results["ui_interaction"] = error_result
            print(f"❌ UI交互测试失败: {e}")
            return error_result
    
    async def test_api_communication(self, page):
        """测试API通信功能"""
        print("\n🌐 测试API通信功能...")
        
        try:
            # 监听网络请求
            api_requests = []
            websocket_connections = []
            
            page.on("request", lambda request: 
                api_requests.append({
                    "url": request.url,
                    "method": request.method,
                    "headers": dict(request.headers)
                }) if "/api/" in request.url else None)
            
            page.on("websocket", lambda ws:
                websocket_connections.append({
                    "url": ws.url
                }))
            
            # 等待一段时间收集网络活动
            await page.wait_for_timeout(5000)
            
            # 检查是否有AI相关的API调用
            ai_api_calls = [
                req for req in api_requests 
                if any(keyword in req["url"].lower() for keyword in ["ai", "chat", "conversation", "assistant"])
            ]
            
            # 检查是否有WebSocket连接
            has_websocket = len(websocket_connections) > 0
            
            result = {
                "total_api_requests": len(api_requests),
                "ai_related_requests": len(ai_api_calls),
                "websocket_connections": len(websocket_connections),
                "has_websocket": has_websocket,
                "api_requests_sample": api_requests[:5],  # 前5个请求作为样本
                "ai_api_calls": ai_api_calls,
                "success": len(api_requests) > 0  # 至少有一些API活动
            }
            
            self.test_results["api_communication"] = result
            
            if len(ai_api_calls) > 0:
                print(f"  ✅ 发现 {len(ai_api_calls)} 个AI相关API调用")
            else:
                print("  ⚠️ 未发现AI相关API调用")
            
            if has_websocket:
                print(f"  ✅ 发现 {len(websocket_connections)} 个WebSocket连接")
            else:
                print("  ⚠️ 未发现WebSocket连接")
            
            return result
            
        except Exception as e:
            error_result = {"success": False, "error": str(e)}
            self.test_results["api_communication"] = error_result
            print(f"❌ API通信测试失败: {e}")
            return error_result
    
    async def test_error_handling(self, page):
        """测试错误处理"""
        print("\n🚨 测试错误处理...")
        
        try:
            console_errors = []
            js_errors = []
            
            # 监听控制台错误
            page.on("console", lambda msg: 
                console_errors.append({
                    "type": msg.type,
                    "text": msg.text,
                    "location": msg.location
                }) if msg.type in ["error", "warning"] else None)
            
            page.on("pageerror", lambda error: js_errors.append(str(error)))
            
            # 等待收集错误
            await page.wait_for_timeout(3000)
            
            # 分析错误类型
            ai_related_errors = []
            for error in console_errors + [{"text": err} for err in js_errors]:
                error_text = error.get("text", "").lower()
                if any(keyword in error_text for keyword in ["ai", "chat", "assistant", "conversation"]):
                    ai_related_errors.append(error_text)
            
            result = {
                "console_errors": len(console_errors),
                "js_errors": len(js_errors),
                "ai_related_errors": len(ai_related_errors),
                "error_details": {
                    "console": console_errors[:3],  # 前3个控制台错误
                    "js": js_errors[:3],  # 前3个JS错误
                    "ai_related": ai_related_errors
                },
                "success": len(console_errors) == 0 and len(js_errors) == 0
            }
            
            self.test_results["error_handling"] = result
            
            if result["success"]:
                print("  ✅ 无错误发现")
            else:
                print(f"  ⚠️ 发现 {len(console_errors)} 个控制台错误，{len(js_errors)} 个JS错误")
                if ai_related_errors:
                    print(f"  ❌ 发现 {len(ai_related_errors)} 个AI相关错误")
            
            return result
            
        except Exception as e:
            error_result = {"success": False, "error": str(e)}
            self.test_results["error_handling"] = error_result
            print(f"❌ 错误处理测试失败: {e}")
            return error_result
    
    def generate_summary(self):
        """生成测试汇总"""
        component_loading = self.test_results.get("component_loading", {})
        ui_interaction = self.test_results.get("ui_interaction", {})
        api_communication = self.test_results.get("api_communication", {})
        error_handling = self.test_results.get("error_handling", {})
        
        # 计算各项成功率
        tests = [component_loading, ui_interaction, api_communication, error_handling]
        successful_tests = sum(1 for test in tests if test.get("success", False))
        total_tests = len(tests)
        
        # 详细分析
        component_ready = component_loading.get("success", False)
        ui_functional = ui_interaction.get("success", False)
        api_working = api_communication.get("success", False)
        no_errors = error_handling.get("success", False)
        
        overall_success = (
            component_ready and
            ui_functional and
            api_working and
            no_errors
        )
        
        self.test_results["summary"] = {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "success_rate": successful_tests / total_tests if total_tests > 0 else 0,
            "component_ready": component_ready,
            "ui_functional": ui_functional,
            "api_working": api_working,
            "no_errors": no_errors,
            "overall_success": overall_success,
            "recommendations": []
        }
        
        # 生成建议
        if not component_ready:
            self.test_results["summary"]["recommendations"].append("检查AI助教组件是否正确加载和渲染")
        if not ui_functional:
            self.test_results["summary"]["recommendations"].append("完善AI助教聊天界面的UI元素")
        if not api_working:
            self.test_results["summary"]["recommendations"].append("确保AI助教的后端API通信正常")
        if not no_errors:
            self.test_results["summary"]["recommendations"].append("修复JavaScript和控制台错误")
        
        print(f"\n{'='*50}")
        print("📊 AI助教聊天组件测试汇总")
        print(f"{'='*50}")
        
        print(f"🧩 组件加载: {'✅' if component_ready else '❌'}")
        print(f"🖱️ UI交互: {'✅' if ui_functional else '❌'}")
        print(f"🌐 API通信: {'✅' if api_working else '❌'}")
        print(f"🚨 错误处理: {'✅' if no_errors else '❌'}")
        
        print(f"\n📈 成功率: {self.test_results['summary']['success_rate']:.1%} ({successful_tests}/{total_tests})")
        
        overall_status = "✅ 功能正常" if overall_success else "⚠️ 需要修复"
        print(f"🏆 整体状态: {overall_status}")
        
        if self.test_results["summary"]["recommendations"]:
            print(f"\n💡 建议:")
            for i, rec in enumerate(self.test_results["summary"]["recommendations"], 1):
                print(f"  {i}. {rec}")
        
        return self.test_results["summary"]
    
    async def run_full_test(self):
        """运行完整的AI助教聊天测试"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                print("🎯 AI助教聊天组件功能测试")
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
                
                # 依次运行各项测试
                await self.test_component_loading(page)
                await self.test_ui_interaction(page)
                await self.test_api_communication(page)
                await self.test_error_handling(page)
                
                # 生成汇总
                summary = self.generate_summary()
                
                return summary["overall_success"]
                
            finally:
                await browser.close()

async def main():
    tester = AIAssistantChatTester()
    success = await tester.run_full_test()
    
    # 保存详细结果
    with open("ai_assistant_chat_test_results.json", "w", encoding="utf-8") as f:
        json.dump(tester.test_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 详细结果已保存到: ai_assistant_chat_test_results.json")
    
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
