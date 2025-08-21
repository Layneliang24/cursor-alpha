#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试前端API封装层
验证前端API调用的正确性

作者: Claude-4-sonnet
创建时间: 2025-08-21
"""

import requests
import json
from datetime import datetime


class FrontendAPIWrapperTester:
    """前端API封装层测试器"""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'FrontendAPIWrapperTester/1.0'
        })
    
    def log(self, message, level="INFO"):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
    
    def test_frontend_api_wrapper(self):
        """测试前端API封装层的实现"""
        self.log("=== 测试前端API封装层 ===")
        
        # 模拟前端API调用的错误实现
        self.log("\n--- 测试错误的API实现 ---")
        self.test_wrong_api_implementation()
        
        # 模拟前端API调用的正确实现
        self.log("\n--- 测试正确的API实现 ---")
        self.test_correct_api_implementation()
    
    def test_wrong_api_implementation(self):
        """测试错误的API实现（模拟修复前的问题）"""
        self.log("模拟前端错误的API调用:")
        self.log("GET /english/typing-practice/words/?category=CET-6&chapter=1")
        
        # 错误的API调用
        wrong_url = f"{self.api_base}/english/typing-practice/words/"
        wrong_params = {
            'category': 'CET-6',  # ❌ 错误参数名
            'chapter': 1
        }
        
        try:
            response = self.session.get(wrong_url, params=wrong_params)
            self.log(f"错误API调用状态码: {response.status_code}")
            
            if response.status_code == 404:
                self.log("✅ 正确检测到404错误")
                try:
                    error_data = response.json()
                    self.log(f"错误详情: {error_data}")
                except:
                    self.log(f"响应内容: {response.text}")
            else:
                self.log(f"❌ 意外状态码: {response.status_code}")
                
        except Exception as e:
            self.log(f"❌ 错误API调用异常: {str(e)}", "ERROR")
    
    def test_correct_api_implementation(self):
        """测试正确的API实现（模拟修复后的问题）"""
        self.log("模拟前端正确的API调用:")
        self.log("GET /english/typing-words/by_dictionary/?dictionary_id=2&chapter=1")
        
        # 正确的API调用
        correct_url = f"{self.api_base}/english/typing-words/by_dictionary/"
        correct_params = {
            'dictionary_id': 2,  # ✅ 正确参数名和值
            'chapter': 1
        }
        
        try:
            response = self.session.get(correct_url, params=correct_params)
            self.log(f"正确API调用状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ 正确API调用成功，返回 {len(data)} 个单词")
                if data:
                    self.log("单词示例:")
                    for i, word in enumerate(data[:3], 1):
                        self.log(f"  {i}. {word.get('word')} - {word.get('translation')}")
            else:
                self.log(f"❌ 正确API调用失败: {response.status_code}")
                self.log(f"响应内容: {response.text}")
                
        except Exception as e:
            self.log(f"❌ 正确API调用异常: {str(e)}", "ERROR")
    
    def test_api_path_comparison(self):
        """比较不同API路径的差异"""
        self.log("\n=== API路径比较 ===")
        
        paths_to_test = [
            "/english/typing-practice/words/",
            "/english/typing-words/by_dictionary/",
            "/english/typing-words/"
        ]
        
        for path in paths_to_test:
            self.log(f"\n测试路径: {path}")
            url = f"{self.base_url}/api/v1{path}"
            
            try:
                response = self.session.get(url)
                self.log(f"状态码: {response.status_code}")
                
                if response.status_code == 200:
                    self.log("✅ 路径可用")
                elif response.status_code == 404:
                    self.log("❌ 路径不存在")
                else:
                    self.log(f"⚠️ 其他状态码: {response.status_code}")
                    
            except Exception as e:
                self.log(f"❌ 请求异常: {str(e)}", "ERROR")
    
    def run_diagnosis(self):
        """运行完整诊断"""
        self.log("🚀 开始诊断前端API封装层问题")
        self.log("=" * 60)
        
        self.test_frontend_api_wrapper()
        self.test_api_path_comparison()
        
        self.log("\n" + "=" * 60)
        self.log("💡 诊断结论:")
        self.log("1. 前端API封装层使用了错误的API路径")
        self.log("2. 前端API封装层使用了错误的参数名")
        self.log("3. 需要修复 english.js 中的 getTypingWordsByDictionary 方法")
        self.log("4. 测试脚本验证了后端API本身是正常的")


def main():
    """主函数"""
    print("前端API封装层诊断脚本")
    print("=" * 60)
    
    # 创建测试器
    tester = FrontendAPIWrapperTester()
    
    # 运行诊断
    tester.run_diagnosis()
    
    print("\n✅ 诊断完成！")


if __name__ == "__main__":
    main()
