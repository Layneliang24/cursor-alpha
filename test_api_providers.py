#!/usr/bin/env python3
"""
测试不同API提供商的脚本
"""

import os
import requests
from openai import OpenAI

def test_openai_api():
    """测试OpenAI API"""
    print("🧪 测试OpenAI API...")
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ 未找到OPENAI_API_KEY")
        return False
    
    print(f"🔑 API密钥: {api_key[:20]}...")
    
    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[{'role': 'user', 'content': 'Hello, 这是一个测试消息。请回复"API连接成功!"'}],
            max_tokens=50
        )
        print("✅ OpenAI API连接成功!")
        print(f"📝 响应: {response.choices[0].message.content}")
        return True
    except Exception as e:
        print(f"❌ OpenAI API连接失败: {e}")
        return False

def test_siliconflow_api():
    """测试硅基流动API"""
    print("\n🧪 测试硅基流动API...")
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ 未找到API密钥")
        return False
    
    try:
        print(f"🔑 API密钥: {api_key[:20]}...")
        response = requests.post(
            "https://api.siliconflow.cn/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "Qwen/QwQ-32B",
                "thinking_budget": 4096,
                "top_p": 0.7,
                "messages": [{"role": "user", "content": "Hello, 这是一个测试消息。请回复API连接成功!"}],
                "max_tokens": 50
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 硅基流动API连接成功!")
            print(f"📝 响应: {result['choices'][0]['message']['content'][:100]}...")
            print(f"🔢 Token使用: {result['usage']['total_tokens']}")
            return True
        else:
            print(f"❌ 硅基流动API失败: {response.status_code}")
            print(f"错误信息: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ 硅基流动API连接失败: {e}")
        return False

def test_custom_api_endpoint():
    """测试其他自定义API端点"""
    print("\n🧪 测试其他API端点...")
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ 未找到API密钥")
        return False
    
    # 尝试不同的API端点
    endpoints = [
        "https://api.openai.com/v1/chat/completions",
        "https://api.deepseek.com/v1/chat/completions",    # DeepSeek API
    ]
    
    for endpoint in endpoints:
        try:
            print(f"🔗 测试端点: {endpoint}")
            response = requests.post(
                endpoint,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": "Hello"}],
                    "max_tokens": 10
                },
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ 端点 {endpoint} 连接成功!")
                return True
            else:
                print(f"❌ 端点 {endpoint} 失败: {response.status_code}")
                print(f"错误信息: {response.text[:200]}")
        except Exception as e:
            print(f"❌ 端点 {endpoint} 连接失败: {e}")
    
    return False

def test_anthropic_api():
    """测试Anthropic API"""
    print("\n🧪 测试Anthropic API...")
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ 未找到ANTHROPIC_API_KEY")
        return False
    
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=50,
            messages=[{"role": "user", "content": "Hello, 这是一个测试消息。"}]
        )
        print("✅ Anthropic API连接成功!")
        print(f"📝 响应: {response.content[0].text}")
        return True
    except Exception as e:
        print(f"❌ Anthropic API连接失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("🔧 API提供商测试工具")
    print("=" * 60)
    
    # 测试OpenAI API
    openai_success = test_openai_api()
    
    # 测试硅基流动API
    siliconflow_success = test_siliconflow_api()
    
    # 测试其他自定义端点
    custom_success = test_custom_api_endpoint()
    
    # 测试Anthropic API
    anthropic_success = test_anthropic_api()
    
    print("\n" + "=" * 60)
    print("📊 测试结果总结:")
    print(f"OpenAI API: {'✅ 成功' if openai_success else '❌ 失败'}")
    print(f"硅基流动API: {'✅ 成功' if siliconflow_success else '❌ 失败'}")
    print(f"其他端点: {'✅ 成功' if custom_success else '❌ 失败'}")
    print(f"Anthropic API: {'✅ 成功' if anthropic_success else '❌ 失败'}")
    
    if any([openai_success, siliconflow_success, custom_success, anthropic_success]):
        print("\n🎉 至少有一个API提供商可用!")
        if siliconflow_success:
            print("💡 硅基流动API可用，您可以使用AI增强流水线进行开发")
        print("💡 您可以使用AI增强流水线进行开发")
    else:
        print("\n⚠️ 所有API提供商都不可用")
        print("💡 建议使用备用方案继续开发")
    
    print("=" * 60)

if __name__ == "__main__":
    main() 