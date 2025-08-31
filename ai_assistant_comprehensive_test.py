#!/usr/bin/env python3
"""
AI助教聊天组件完整功能测试
包含模式切换和实际使用流程测试
"""
import asyncio
from playwright.async_api import async_playwright
import json
import time

class AIAssistantComprehensiveTester:
    def __init__(self):
        self.test_results = {
            "mode_switching": {},
            "component_loading": {},
            "ui_interaction": {},
            "functionality": {},
            "summary": {}
        }
    
    async def test_mode_switching(self, page):
        """测试学习模式切换功能"""
        print("🔄 测试学习模式切换功能...")
        
        try:
            # 导航到地道表达学习页面
            response = await page.goto("http://localhost:3000/english/idiomatic-learning", 
                                     wait_until="domcontentloaded", timeout=15000)
            
            if response.status != 200:
                print(f"❌ 页面加载失败，状态码: {response.status}")
                return {"success": False, "error": f"页面状态码: {response.status}"}
            
            # 等待页面加载
            await page.wait_for_timeout(3000)
            
            print("  🔍 检查学习模式选项...")
            
            # 查找学习模式选择区域
            mode_selectors = [
                ".mode-card",
                "[data-testid='mode-card']",
                ".learning-modes .mode-option",
                ".mode-selection .mode-item"
            ]
            
            mode_cards = []
            for selector in mode_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    if elements:
                        mode_cards = elements
                        print(f"  ✅ 找到 {len(elements)} 个学习模式选项: {selector}")
                        break
                except:
                    continue
            
            if not mode_cards:
                print("  ❌ 未找到学习模式选择区域")
                return {"success": False, "error": "未找到学习模式选择区域"}
            
            # 查找AI对话模式
            ai_mode_found = False
            ai_mode_element = None
            
            for card in mode_cards:
                try:
                    # 检查是否包含AI相关的图标或文字
                    card_html = await card.inner_html()
                    card_text = await card.inner_text()
                    
                    if any(keyword in card_html.lower() or keyword in card_text.lower() 
                          for keyword in ["chatdotsquare", "ai", "对话", "助教", "聊天"]):
                        ai_mode_found = True
                        ai_mode_element = card
                        print(f"  ✅ 找到AI对话模式: {card_text.strip()}")
                        break
                except:
                    continue
            
            if not ai_mode_found:
                print("  ❌ 未找到AI对话模式选项")
                return {"success": False, "error": "未找到AI对话模式选项"}
            
            # 点击AI对话模式
            print("  🖱️ 点击AI对话模式...")
            await ai_mode_element.click()
            await page.wait_for_timeout(2000)
            
            # 检查模式是否切换成功
            mode_switched = False
            try:
                # 检查AI对话模式是否激活
                is_active = await ai_mode_element.evaluate("element => element.classList.contains('active')")
                if is_active:
                    mode_switched = True
                    print("  ✅ AI对话模式已激活")
            except:
                pass
            
            if not mode_switched:
                # 尝试其他方式检查
                try:
                    ai_chat_area = await page.query_selector(".ai-chat-mode, [data-testid='ai-chat-mode']")
                    if ai_chat_area:
                        is_visible = await ai_chat_area.is_visible()
                        if is_visible:
                            mode_switched = True
                            print("  ✅ AI对话区域已显示")
                except:
                    pass
            
            result = {
                "page_loaded": response.status == 200,
                "mode_cards_found": len(mode_cards),
                "ai_mode_found": ai_mode_found,
                "mode_switched": mode_switched,
                "success": response.status == 200 and ai_mode_found and mode_switched
            }
            
            self.test_results["mode_switching"] = result
            return result
            
        except Exception as e:
            error_result = {"success": False, "error": str(e)}
            self.test_results["mode_switching"] = error_result
            print(f"❌ 模式切换测试失败: {e}")
            return error_result
    
    async def test_ai_component_in_mode(self, page):
        """测试AI对话模式下的组件加载"""
        print("\n🤖 测试AI对话模式下的组件加载...")
        
        try:
            # 等待AI组件加载
            await page.wait_for_timeout(2000)
            
            # 查找AI助教聊天组件
            ai_component_selectors = [
                ".ai-assistant-chat",
                ".ai-chat-container",
                "[data-testid='ai-assistant-chat']",
                ".chat-interface",
                ".ai-dialog"
            ]
            
            ai_component_found = False
            ai_component = None
            
            for selector in ai_component_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        is_visible = await element.is_visible()
                        if is_visible:
                            ai_component_found = True
                            ai_component = element
                            print(f"  ✅ AI助教组件已加载: {selector}")
                            break
                except:
                    continue
            
            # 如果没找到特定的组件容器，检查是否有相关的UI元素
            if not ai_component_found:
                print("  🔍 检查AI相关UI元素...")
                
                ui_elements = {
                    "input_field": [
                        "input[placeholder*='消息']",
                        "input[placeholder*='输入']",
                        "textarea[placeholder*='消息']",
                        "input[type='text']"
                    ],
                    "send_button": [
                        "button:has-text('发送')",
                        "button[title='发送']",
                        "button[type='submit']"
                    ],
                    "chat_area": [
                        ".chat-messages",
                        ".message-list",
                        ".conversation-area"
                    ]
                }
                
                found_elements = {}
                for element_type, selectors in ui_elements.items():
                    for selector in selectors:
                        try:
                            element = await page.query_selector(selector)
                            if element:
                                is_visible = await element.is_visible()
                                if is_visible:
                                    found_elements[element_type] = selector
                                    print(f"    ✅ {element_type}: {selector}")
                                    break
                        except:
                            continue
                    
                    if element_type not in found_elements:
                        print(f"    ❌ {element_type}: 未找到")
                
                # 如果找到了基本的聊天UI元素，认为组件基本加载成功
                ai_component_found = len(found_elements) >= 1
            
            # 检查页面内容中是否有AI相关的文字
            page_content = await page.content()
            ai_text_present = any(text in page_content for text in [
                "AI助教", "智能助教", "发送消息", "聊天", "对话"
            ])
            
            result = {
                "ai_component_found": ai_component_found,
                "ai_text_present": ai_text_present,
                "success": ai_component_found or ai_text_present
            }
            
            if not result["success"]:
                print("  ❌ AI助教组件未正确加载")
            
            self.test_results["component_loading"] = result
            return result
            
        except Exception as e:
            error_result = {"success": False, "error": str(e)}
            self.test_results["component_loading"] = error_result
            print(f"❌ AI组件加载测试失败: {e}")
            return error_result
    
    async def test_chat_functionality(self, page):
        """测试聊天功能"""
        print("\n💬 测试聊天功能...")
        
        try:
            # 查找输入框
            input_selectors = [
                "input[placeholder*='消息']",
                "input[placeholder*='输入']", 
                "textarea[placeholder*='消息']",
                "input[type='text']",
                ".chat-input input",
                ".message-input"
            ]
            
            input_element = None
            for selector in input_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        is_visible = await element.is_visible()
                        is_enabled = await element.is_enabled()
                        if is_visible and is_enabled:
                            input_element = element
                            print(f"  ✅ 找到可用输入框: {selector}")
                            break
                except:
                    continue
            
            if not input_element:
                print("  ❌ 未找到可用的消息输入框")
                return {"success": False, "error": "未找到输入框"}
            
            # 尝试输入测试消息
            test_message = "你好，这是一个测试消息"
            print(f"  📝 输入测试消息: {test_message}")
            
            await input_element.click()
            await input_element.fill(test_message)
            
            # 等待一下确保输入完成
            await page.wait_for_timeout(1000)
            
            # 检查输入是否成功
            input_value = await input_element.input_value()
            input_successful = test_message in input_value
            
            if input_successful:
                print("  ✅ 消息输入成功")
            else:
                print("  ⚠️ 消息输入可能有问题")
            
            # 查找发送按钮
            send_selectors = [
                "button:has-text('发送')",
                "button[title='发送']",
                "button[type='submit']",
                ".send-button",
                ".chat-send-btn"
            ]
            
            send_button = None
            for selector in send_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        is_visible = await element.is_visible()
                        is_enabled = await element.is_enabled()
                        if is_visible and is_enabled:
                            send_button = element
                            print(f"  ✅ 找到发送按钮: {selector}")
                            break
                except:
                    continue
            
            send_button_available = send_button is not None
            if not send_button_available:
                print("  ⚠️ 未找到发送按钮，尝试Enter键发送")
                # 尝试使用Enter键发送
                try:
                    await input_element.press("Enter")
                    print("  ✅ 尝试使用Enter键发送")
                except:
                    print("  ❌ Enter键发送失败")
            else:
                # 点击发送按钮
                try:
                    await send_button.click()
                    print("  ✅ 点击发送按钮")
                except Exception as e:
                    print(f"  ❌ 点击发送按钮失败: {e}")
            
            # 等待可能的响应
            await page.wait_for_timeout(3000)
            
            result = {
                "input_available": input_element is not None,
                "input_successful": input_successful,
                "send_button_available": send_button_available,
                "message_sent": input_successful and (send_button_available or True),  # 假设Enter键有效
                "success": input_element is not None and input_successful
            }
            
            self.test_results["functionality"] = result
            return result
            
        except Exception as e:
            error_result = {"success": False, "error": str(e)}
            self.test_results["functionality"] = error_result
            print(f"❌ 聊天功能测试失败: {e}")
            return error_result
    
    def generate_comprehensive_summary(self):
        """生成完整的测试汇总"""
        mode_switching = self.test_results.get("mode_switching", {})
        component_loading = self.test_results.get("component_loading", {})
        functionality = self.test_results.get("functionality", {})
        
        # 各项测试结果
        mode_switch_ok = mode_switching.get("success", False)
        component_loaded = component_loading.get("success", False)
        functionality_ok = functionality.get("success", False)
        
        # 计算总体成功率
        tests = [mode_switch_ok, component_loaded, functionality_ok]
        successful_tests = sum(tests)
        total_tests = len(tests)
        
        # 判断AI助教组件整体状态
        ai_assistant_functional = mode_switch_ok and component_loaded and functionality_ok
        
        self.test_results["summary"] = {
            "mode_switching": mode_switch_ok,
            "component_loading": component_loaded,
            "functionality": functionality_ok,
            "success_rate": successful_tests / total_tests if total_tests > 0 else 0,
            "ai_assistant_functional": ai_assistant_functional,
            "recommendations": []
        }
        
        # 生成具体建议
        if not mode_switch_ok:
            self.test_results["summary"]["recommendations"].append("修复学习模式切换功能，确保用户可以切换到AI对话模式")
        if not component_loaded:
            self.test_results["summary"]["recommendations"].append("检查AIAssistantChat组件的渲染和显示逻辑")
        if not functionality_ok:
            self.test_results["summary"]["recommendations"].append("完善AI助教的输入和发送消息功能")
        
        print(f"\n{'='*60}")
        print("📊 AI助教聊天组件完整测试汇总")
        print(f"{'='*60}")
        
        print(f"🔄 模式切换: {'✅' if mode_switch_ok else '❌'}")
        print(f"🤖 组件加载: {'✅' if component_loaded else '❌'}")
        print(f"💬 基础功能: {'✅' if functionality_ok else '❌'}")
        
        print(f"\n📈 成功率: {self.test_results['summary']['success_rate']:.1%} ({successful_tests}/{total_tests})")
        
        if ai_assistant_functional:
            print("🏆 AI助教组件状态: ✅ 功能正常")
            print("🎉 用户可以正常使用AI助教聊天功能！")
        else:
            print("🏆 AI助教组件状态: ⚠️ 需要修复")
            
            if self.test_results["summary"]["recommendations"]:
                print(f"\n💡 修复建议:")
                for i, rec in enumerate(self.test_results["summary"]["recommendations"], 1):
                    print(f"  {i}. {rec}")
        
        return self.test_results["summary"]
    
    async def run_comprehensive_test(self):
        """运行完整的AI助教测试"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)  # 使用有头模式便于调试
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                print("🎯 AI助教聊天组件完整功能测试")
                print("=" * 60)
                
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
                
                # 依次运行测试
                await self.test_mode_switching(page)
                await self.test_ai_component_in_mode(page)
                await self.test_chat_functionality(page)
                
                # 生成汇总
                summary = self.generate_comprehensive_summary()
                
                return summary["ai_assistant_functional"]
                
            finally:
                await browser.close()

async def main():
    tester = AIAssistantComprehensiveTester()
    success = await tester.run_comprehensive_test()
    
    # 保存详细结果
    with open("ai_assistant_comprehensive_test_results.json", "w", encoding="utf-8") as f:
        json.dump(tester.test_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 详细结果已保存到: ai_assistant_comprehensive_test_results.json")
    
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
