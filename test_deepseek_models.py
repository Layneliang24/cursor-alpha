#!/usr/bin/env python3
"""
测试DeepSeek强大模型的脚本
"""

import os
import requests
import json

def test_deepseek_model(model_name, api_key):
    """测试DeepSeek模型"""
    print(f"\n🧪 测试模型: {model_name}")
    
    # 使用更合理的参数设置
    data = {
        "model": model_name,
        "messages": [{"role": "user", "content": "请分析以下需求并生成高质量的代码：英语学习-地道表达模块，需要包含数据采集、存储、展示功能。请生成Django模型代码。"}],
        "max_tokens": 2000,  # 增加输出长度
        "temperature": 0.1,  # 降低随机性，提高代码质量
        "top_p": 0.9,       # 提高创造性
        "stream": False
    }
    
    try:
        response = requests.post(
            "https://api.siliconflow.cn/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json=data,
            timeout=120  # 增加超时时间
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {model_name} 连接成功!")
            print(f"📝 响应长度: {len(result['choices'][0]['message']['content'])} 字符")
            print(f"🔢 Token使用: {result['usage']['total_tokens']}")
            print(f"📄 响应预览: {result['choices'][0]['message']['content'][:200]}...")
            return True, result['choices'][0]['message']['content']
        else:
            print(f"❌ {model_name} 失败: {response.status_code}")
            print(f"错误信息: {response.text[:200]}")
            return False, None
            
    except Exception as e:
        print(f"❌ {model_name} 连接失败: {e}")
        return False, None

def main():
    """主函数"""
    print("=" * 60)
    print("🔧 DeepSeek强大模型测试工具")
    print("=" * 60)
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ 未找到API密钥")
        return
    
    print(f"🔑 API密钥: {api_key[:20]}...")
    
    # 测试不同的DeepSeek模型（使用正确的名称）
    models_to_test = [
        "deepseek-ai/DeepSeek-R1",           # DeepSeek R1 - 最强大的模型
        "deepseek-ai/DeepSeek-V3.1",         # DeepSeek V3.1 - 最新版本
        "deepseek-ai/DeepSeek-V3",           # DeepSeek V3
        "deepseek-ai/DeepSeek-V2.5",         # DeepSeek V2.5
        "Qwen/Qwen3-235B-A22B-Instruct-2507", # Qwen3 235B - 超大模型
        "Qwen/Qwen3-Coder-480B-A35B-Instruct", # Qwen3 Coder 480B - 代码专用
        "Qwen/QwQ-32B"                       # 当前可用的模型
    ]
    
    best_model = None
    best_response = None
    
    for model in models_to_test:
        success, response = test_deepseek_model(model, api_key)
        if success and response:
            if not best_model or len(response) > len(best_response):
                best_model = model
                best_response = response
    
    print("\n" + "=" * 60)
    print("📊 测试结果总结:")
    
    if best_model:
        print(f"🏆 最佳模型: {best_model}")
        print(f"📝 最佳响应长度: {len(best_response)} 字符")
        print("\n💡 建议使用最佳模型进行AI增强流水线开发")
        
        # 保存最佳响应
        with open(f"best_response_{best_model.replace('/', '_')}.txt", "w", encoding="utf-8") as f:
            f.write(best_response)
        print(f"💾 最佳响应已保存到: best_response_{best_model.replace('/', '_')}.txt")
    else:
        print("❌ 所有模型都测试失败")
    
    print("=" * 60)

if __name__ == "__main__":
    main() 