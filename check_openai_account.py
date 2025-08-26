#!/usr/bin/env python3
"""
OpenAI账户状态检查脚本
"""

import os
import requests
from openai import OpenAI

def check_openai_account():
    """检查OpenAI账户状态"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ 未找到OPENAI_API_KEY环境变量")
        return
    
    print("🔍 检查OpenAI账户状态...")
    print(f"🔑 API密钥: {api_key[:20]}...")
    
    # 创建客户端
    client = OpenAI(api_key=api_key)
    
    try:
        # 尝试获取账户信息
        print("📊 获取账户信息...")
        
        # 测试不同的模型
        models_to_test = [
            "gpt-3.5-turbo",
            "gpt-4",
            "gpt-4-turbo-preview"
        ]
        
        for model in models_to_test:
            try:
                print(f"🧪 测试模型: {model}")
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": "Hello"}],
                    max_tokens=10
                )
                print(f"✅ {model} 可用")
                break
            except Exception as e:
                print(f"❌ {model} 不可用: {str(e)[:100]}...")
        
        # 尝试获取使用情况（如果API支持）
        try:
            print("\n📈 获取使用情况...")
            # 注意：这个端点可能需要特定的权限
            usage_response = requests.get(
                "https://api.openai.com/v1/usage",
                headers={"Authorization": f"Bearer {api_key}"}
            )
            if usage_response.status_code == 200:
                print("✅ 可以获取使用情况")
                print(usage_response.json())
            else:
                print(f"⚠️ 无法获取使用情况: {usage_response.status_code}")
        except Exception as e:
            print(f"⚠️ 获取使用情况失败: {e}")
            
    except Exception as e:
        print(f"❌ 账户检查失败: {e}")
    
    print("\n💡 建议:")
    print("1. 访问 https://platform.openai.com/account/billing 检查余额")
    print("2. 访问 https://platform.openai.com/account/usage 查看使用情况")
    print("3. 访问 https://platform.openai.com/api-keys 重新生成密钥")
    print("4. 确保账户已设置支付方式")

if __name__ == "__main__":
    check_openai_account() 