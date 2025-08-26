#!/usr/bin/env python3
"""
OpenAI配额问题快速解决方案
"""

import os
import webbrowser

def print_solution():
    """打印解决方案"""
    print("=" * 60)
    print("🔧 OpenAI配额问题快速解决方案")
    print("=" * 60)
    
    print("\n🎯 当前问题:")
    print("❌ OpenAI API配额不足 (429错误)")
    print("❌ 无法使用云AI服务")
    
    print("\n💡 立即解决方案:")
    print("1. 使用备用方案继续开发 (推荐)")
    print("2. 解决OpenAI配额问题")
    print("3. 使用其他AI服务")
    
    print("\n🥇 方案1: 使用备用方案 (立即可用)")
    print("命令: python scripts/local_ai_pipeline.py --input your_requirement.md")
    print("优势: 无需配置，立即可用，生成完整代码")
    
    print("\n🥈 方案2: 解决OpenAI配额")
    print("步骤:")
    print("  1. 检查账户余额")
    print("  2. 设置支付方式")
    print("  3. 重新生成API密钥")
    
    print("\n🥉 方案3: 使用Claude API")
    print("步骤:")
    print("  1. 注册Claude账户")
    print("  2. 获得免费额度")
    print("  3. 设置API密钥")

def open_help_pages():
    """打开帮助页面"""
    print("\n🌐 打开帮助页面...")
    
    pages = [
        ("OpenAI账户账单", "https://platform.openai.com/account/billing"),
        ("OpenAI API密钥", "https://platform.openai.com/api-keys"),
        ("Claude控制台", "https://console.anthropic.com/"),
        ("OpenAI支持", "https://help.openai.com/")
    ]
    
    for name, url in pages:
        print(f"📖 打开 {name}: {url}")
        try:
            webbrowser.open(url)
        except Exception as e:
            print(f"⚠️ 无法打开 {name}: {e}")

def test_current_status():
    """测试当前状态"""
    print("\n🧪 测试当前状态...")
    
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print(f"✅ 找到OpenAI API密钥: {api_key[:20]}...")
        print("❌ 但配额不足，需要充值或设置支付方式")
    else:
        print("❌ 未找到OpenAI API密钥")
    
    print("\n💡 建议:")
    print("1. 立即使用备用方案继续开发")
    print("2. 同时解决API配额问题")
    print("3. 考虑使用Claude API作为替代")

def main():
    """主函数"""
    print_solution()
    open_help_pages()
    test_current_status()
    
    print("\n" + "=" * 60)
    print("🎯 推荐操作:")
    print("1. 立即运行: python scripts/local_ai_pipeline.py --input docs/spec/requirements/idiomatic_expressions_enhancement.md")
    print("2. 检查OpenAI账户状态")
    print("3. 考虑使用Claude API")
    print("=" * 60)

if __name__ == "__main__":
    main() 