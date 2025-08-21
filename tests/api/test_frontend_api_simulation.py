#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试前端API调用模拟
模拟TypingPractice.vue中的API调用，验证进度条数据来源

作者: Claude-4-sonnet
创建时间: 2025-08-21
"""

import requests
import json
import time
from datetime import datetime


class FrontendAPISimulator:
    """前端API调用模拟器"""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1/english"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'FrontendAPISimulator/1.0'
        })
    
    def log(self, message, level="INFO"):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
    
    def simulate_getTypingWordsByDictionary(self, dictionary_name, chapter):
        """模拟前端调用 getTypingWordsByDictionary"""
        self.log(f"=== 模拟前端API调用: getTypingWordsByDictionary ===")
        self.log(f"参数: dictionary_name='{dictionary_name}', chapter={chapter}")
        
        try:
            # 步骤1: 获取词典列表，找到对应的dictionary_id
            self.log("步骤1: 获取词典列表")
            dict_response = self.session.get(f"{self.api_base}/dictionaries/")
            
            if dict_response.status_code != 200:
                self.log(f"获取词典列表失败: {dict_response.status_code}", "ERROR")
                return None
            
            dictionaries = dict_response.json()
            target_dict = None
            
            for dict_info in dictionaries:
                if dict_info.get('name') == dictionary_name:
                    target_dict = dict_info
                    break
            
            if not target_dict:
                self.log(f"未找到词典: {dictionary_name}", "ERROR")
                return None
            
            dictionary_id = target_dict.get('id')
            self.log(f"找到词典: {dictionary_name} (ID: {dictionary_id})")
            
            # 步骤2: 调用 getTypingWordsByDictionary API
            self.log("步骤2: 调用 getTypingWordsByDictionary API")
            self.log(f"注意: 前端传递的是 dictionary_name='{dictionary_name}'，但API需要 dictionary_id={dictionary_id}")
            
            # 模拟前端可能的问题：传递了错误的参数
            wrong_params = {
                'category': dictionary_name,  # ❌ 前端错误地传递了词典名称
                'chapter': chapter
            }
            
            self.log(f"前端错误参数: {wrong_params}")
            
            # 正确的API调用
            correct_params = {
                'dictionary_id': dictionary_id,
                'chapter': chapter
            }
            
            self.log(f"正确参数: {correct_params}")
            
            # 测试正确的API调用
            response = self.session.get(
                f"{self.api_base}/typing-words/by_dictionary/",
                params=correct_params
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ API调用成功，返回 {len(data)} 个单词")
                
                if data:
                    self.log("单词列表:")
                    for i, word in enumerate(data[:3], 1):  # 只显示前3个
                        self.log(f"  {i}. {word.get('word')} - {word.get('translation')}")
                    
                    if len(data) > 3:
                        self.log(f"  ... 还有 {len(data) - 3} 个单词")
                    
                    # 验证进度条所需的数据结构
                    self.log("\n=== 进度条数据验证 ===")
                    self.log(f"words.length: {len(data)}")
                    self.log(f"currentWordIndex: 0 (初始值)")
                    self.log(f"进度条宽度: {((0 + 1) / len(data) * 100):.1f}%")
                    self.log(f"进度条文本: 1/{len(data)}")
                    
                    return data
                else:
                    self.log("⚠️  API返回空数组", "WARNING")
                    return []
            else:
                self.log(f"❌ API调用失败: {response.status_code}", "ERROR")
                self.log(f"响应内容: {response.text}")
                return None
                
        except Exception as e:
            self.log(f"模拟API调用失败: {str(e)}", "ERROR")
            return None
    
    def test_progress_bar_data_flow(self):
        """测试进度条数据流"""
        self.log("=== 测试进度条数据流 ===")
        
        # 测试测试词典章节1
        self.log("\n--- 测试测试词典章节1 ---")
        words_chapter1 = self.simulate_getTypingWordsByDictionary("测试词典", 1)
        
        if words_chapter1 and len(words_chapter1) > 0:
            self.log("✅ 章节1数据获取成功，进度条应该显示")
            self.log(f"进度条条件: words && words.length > 0")
            self.log(f"words: {words_chapter1 is not None}")
            self.log(f"words.length: {len(words_chapter1)}")
            self.log(f"条件结果: {words_chapter1 is not None and len(words_chapter1) > 0}")
        else:
            self.log("❌ 章节1数据获取失败，进度条不会显示")
        
        # 测试测试词典章节2
        self.log("\n--- 测试测试词典章节2 ---")
        words_chapter2 = self.simulate_getTypingWordsByDictionary("测试词典", 2)
        
        if words_chapter2 and len(words_chapter2) > 0:
            self.log("✅ 章节2数据获取成功，进度条应该显示")
        else:
            self.log("❌ 章节2数据获取失败，进度条不会显示")
        
        # 测试CET-6词典（对比）
        self.log("\n--- 测试CET-6词典章节1 ---")
        words_cet6 = self.simulate_getTypingWordsByDictionary("CET-6", 1)
        
        if words_cet6 and len(words_cet6) > 0:
            self.log("✅ CET-6词典数据获取成功，进度条应该显示")
        else:
            self.log("❌ CET-6词典数据获取失败，进度条不会显示")
    
    def run_diagnosis(self):
        """运行诊断"""
        self.log("🚀 开始诊断进度条不显示问题")
        self.log("=" * 60)
        
        self.test_progress_bar_data_flow()
        
        self.log("\n" + "=" * 60)
        self.log("💡 诊断建议:")
        self.log("1. 检查前端是否正确调用了 getTypingWordsByDictionary")
        self.log("2. 检查API返回的数据是否正确")
        self.log("3. 检查 typingStore 中的 words 数组是否正确设置")
        self.log("4. 检查进度条的显示条件是否满足")


def main():
    """主函数"""
    print("前端API调用模拟诊断脚本")
    print("=" * 60)
    
    # 创建模拟器
    simulator = FrontendAPISimulator()
    
    # 运行诊断
    simulator.run_diagnosis()
    
    print("\n✅ 诊断完成！")


if __name__ == "__main__":
    main()
