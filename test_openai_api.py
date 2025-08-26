#!/usr/bin/env python3
"""
OpenAI API测试脚本
"""

import os
from openai import OpenAI

def test_openai_api():
    """测试OpenAI API连接"""
    try:
        # 获取API密钥
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("❌ 未找到OPENAI_API_KEY环境变量")
            return False
        
        print(f"🔑 API密钥: {api_key[:20]}...")
        
        # 创建客户端
        client = OpenAI(api_key=api_key)
        
        # 发送测试请求
        print("📡 发送测试请求...")
        response = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[
                {'role': 'user', 'content': 'Hello, 这是一个测试消息。请回复"API连接成功!"'}
            ],
            max_tokens=50
        )
        
        # 显示结果
        print("✅ API连接成功!")
        print(f"📝 响应: {response.choices[0].message.content}")
        print(f"🔢 使用tokens: {response.usage.total_tokens}")
        
        return True
        
    except Exception as e:
        print(f"❌ API连接失败: {e}")
        return False

if __name__ == "__main__":
    print("🧪 开始测试OpenAI API...")
    success = test_openai_api()
    
    if success:
        print("\n🎉 测试完成！API可以正常使用。")
    else:
        print("\n💥 测试失败！请检查API密钥和网络连接。") 