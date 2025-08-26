#!/usr/bin/env python3
"""
OpenAI配额问题快速修复脚本
"""

import os
import sys
import subprocess
import webbrowser
from pathlib import Path

def print_banner():
    """打印横幅"""
    print("=" * 60)
    print("🔧 OpenAI配额问题快速修复工具")
    print("=" * 60)

def check_current_status():
    """检查当前状态"""
    print("🔍 检查当前状态...")
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ 未找到OPENAI_API_KEY环境变量")
        return False
    
    print(f"✅ 找到API密钥: {api_key[:20]}...")
    
    # 运行测试
    try:
        result = subprocess.run([sys.executable, "test_openai_api.py"], 
                              capture_output=True, text=True)
        if "配额不足" in result.stdout or "insufficient_quota" in result.stdout or "429" in result.stdout or "测试失败" in result.stdout:
            print("❌ 确认配额不足问题")
            return False
        elif "测试完成" in result.stdout or "API连接成功" in result.stdout:
            print("✅ API密钥工作正常")
            return True
        else:
            print("⚠️ 无法确定状态")
            return False
    except Exception as e:
        print(f"⚠️ 测试失败: {e}")
        return False

def open_web_pages():
    """打开相关网页"""
    print("\n🌐 打开相关网页...")
    
    pages = [
        ("OpenAI账户账单", "https://platform.openai.com/account/billing"),
        ("OpenAI API密钥", "https://platform.openai.com/api-keys"),
        ("OpenAI使用情况", "https://platform.openai.com/account/usage"),
        ("Ollama下载", "https://ollama.ai/"),
        ("Claude控制台", "https://console.anthropic.com/")
    ]
    
    for name, url in pages:
        print(f"📖 打开 {name}: {url}")
        try:
            webbrowser.open(url)
        except Exception as e:
            print(f"⚠️ 无法打开 {name}: {e}")

def suggest_solutions():
    """建议解决方案"""
    print("\n💡 解决方案建议:")
    
    print("\n🥇 立即解决方案 (推荐):")
    print("1. 使用本地AI流水线 (无需API密钥)")
    print("   python scripts/local_ai_pipeline.py --input your_requirement.md")
    
    print("\n🥈 账户修复方案:")
    print("1. 检查账户余额和支付方式")
    print("2. 重新生成API密钥")
    print("3. 设置支出限制")
    
    print("\n🥉 替代方案:")
    print("1. 安装Ollama获得完全免费的AI体验")
    print("2. 使用Claude API (有免费额度)")
    print("3. 申请新的OpenAI账户")

def test_local_ai():
    """测试本地AI流水线"""
    print("\n🧪 测试本地AI流水线...")
    
    try:
        result = subprocess.run([
            sys.executable, "scripts/local_ai_pipeline.py",
            "--input", "docs/spec/requirements/idiomatic_expressions_enhancement.md",
            "--dry-run"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 本地AI流水线工作正常")
            print("💡 您可以使用本地AI流水线继续开发")
        else:
            print("❌ 本地AI流水线测试失败")
            print(result.stderr)
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def install_ollama_guide():
    """Ollama安装指南"""
    print("\n📦 Ollama安装指南:")
    
    print("\n1. 下载Ollama:")
    print("   访问: https://ollama.ai/")
    print("   选择Windows版本下载")
    
    print("\n2. 安装后启动:")
    print("   ollama serve")
    
    print("\n3. 下载模型:")
    print("   ollama pull llama2")
    print("   ollama pull codellama")
    
    print("\n4. 测试:")
    print("   ollama run llama2 'Hello, world!'")

def main():
    """主函数"""
    print_banner()
    
    # 检查当前状态
    is_working = check_current_status()
    
    if is_working:
        print("\n🎉 您的OpenAI API工作正常！")
        return
    
    # 打开相关网页
    open_web_pages()
    
    # 建议解决方案
    suggest_solutions()
    
    # 测试本地AI
    test_local_ai()
    
    # Ollama安装指南
    install_ollama_guide()
    
    print("\n" + "=" * 60)
    print("🎯 推荐操作顺序:")
    print("1. 立即使用本地AI流水线继续开发")
    print("2. 检查OpenAI账户状态")
    print("3. 考虑安装Ollama获得更好的体验")
    print("=" * 60)

if __name__ == "__main__":
    main() 