#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试打字练习单词API接口
模拟前端请求，测试测试词典的单词获取功能

作者: Claude-4-sonnet
创建时间: 2025-08-21
"""

import requests
import json
import time
from datetime import datetime


class TypingWordsAPITester:
    """打字练习单词API测试器"""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1/english"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'TypingWordsAPITester/1.0'
        })
    
    def log(self, message, level="INFO"):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
    
    def test_dictionary_list(self):
        """测试获取词典列表"""
        self.log("=== 测试获取词典列表 ===")
        
        try:
            url = f"{self.api_base}/dictionaries/"
            self.log(f"请求URL: {url}")
            
            start_time = time.time()
            response = self.session.get(url)
            end_time = time.time()
            
            self.log(f"响应状态码: {response.status_code}")
            self.log(f"请求耗时: {(end_time - start_time) * 1000:.2f}ms")
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"返回词典数量: {len(data)}")
                
                for dict_info in data:
                    self.log(f"  词典: {dict_info.get('name')} (ID: {dict_info.get('id')})")
                    self.log(f"    描述: {dict_info.get('description')}")
                    self.log(f"    分类: {dict_info.get('category')}")
                    self.log(f"    总词数: {dict_info.get('total_words')}")
                    self.log(f"    章节数: {dict_info.get('chapter_count')}")
                    self.log(f"    状态: {'启用' if dict_info.get('is_active') else '禁用'}")
                    self.log("")
                
                return data
            else:
                self.log(f"请求失败: {response.status_code}", "ERROR")
                self.log(f"响应内容: {response.text}", "ERROR")
                return None
                
        except Exception as e:
            self.log(f"测试词典列表失败: {str(e)}", "ERROR")
            return None
    
    def test_typing_words_by_dictionary(self, dictionary_id, chapter):
        """测试根据词典和章节获取单词"""
        self.log(f"=== 测试获取词典 {dictionary_id} 章节 {chapter} 的单词 ===")
        
        try:
            url = f"{self.api_base}/typing-words/by_dictionary/"
            params = {
                'dictionary_id': dictionary_id,
                'chapter': chapter
            }
            
            self.log(f"请求URL: {url}")
            self.log(f"请求参数: {params}")
            
            start_time = time.time()
            response = self.session.get(url, params=params)
            end_time = time.time()
            
            self.log(f"响应状态码: {response.status_code}")
            self.log(f"请求耗时: {(end_time - start_time) * 1000:.2f}ms")
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"返回单词数量: {len(data)}")
                
                if data:
                    self.log("单词列表:")
                    for i, word in enumerate(data, 1):
                        self.log(f"  {i}. {word.get('word')} - {word.get('translation')}")
                        self.log(f"     音标: {word.get('phonetic')}")
                        self.log(f"     难度: {word.get('difficulty')}")
                        self.log(f"     频率: {word.get('frequency')}")
                        self.log("")
                else:
                    self.log("⚠️  没有找到符合条件的单词", "WARNING")
                
                return data
            else:
                self.log(f"请求失败: {response.status_code}", "ERROR")
                self.log(f"响应内容: {response.text}", "ERROR")
                return None
                
        except Exception as e:
            self.log(f"测试单词获取失败: {str(e)}", "ERROR")
            return None
    
    def test_specific_test_dictionary(self):
        """专门测试测试词典"""
        self.log("=== 专门测试测试词典 ===")
        
        # 先获取词典列表，找到测试词典
        dictionaries = self.test_dictionary_list()
        if not dictionaries:
            return False
        
        # 查找测试词典
        test_dict = None
        for dict_info in dictionaries:
            if dict_info.get('name') == '测试词典':
                test_dict = dict_info
                break
        
        if not test_dict:
            self.log("❌ 未找到测试词典", "ERROR")
            return False
        
        self.log(f"✅ 找到测试词典: {test_dict.get('name')} (ID: {test_dict.get('id')})")
        
        # 测试测试词典的章节1
        dictionary_id = test_dict.get('id')
        chapter = 1
        
        words = self.test_typing_words_by_dictionary(dictionary_id, chapter)
        
        if words and len(words) > 0:
            self.log(f"✅ 测试词典章节1成功获取到 {len(words)} 个单词", "SUCCESS")
            return True
        else:
            self.log("❌ 测试词典章节1没有单词", "ERROR")
            return False
    
    def run_full_test(self):
        """运行完整测试"""
        self.log("🚀 开始运行打字练习单词API完整测试")
        self.log("=" * 50)
        
        # 测试1: 获取词典列表
        dictionaries = self.test_dictionary_list()
        
        if not dictionaries:
            self.log("❌ 无法获取词典列表，测试终止", "ERROR")
            return False
        
        # 测试2: 专门测试测试词典
        test_result = self.test_specific_test_dictionary()
        
        # 测试3: 测试CET-6词典（作为对比）
        self.log("=== 对比测试: CET-6词典 ===")
        cet6_dict = None
        for dict_info in dictionaries:
            if dict_info.get('name') == 'CET-6':
                cet6_dict = dict_info
                break
        
        if cet6_dict:
            self.log(f"测试CET-6词典 (ID: {cet6_dict.get('id')}) 章节1")
            cet6_words = self.test_typing_words_by_dictionary(cet6_dict.get('id'), 1)
            if cet6_words:
                self.log(f"CET-6词典章节1有 {len(cet6_words)} 个单词")
        
        self.log("=" * 50)
        
        if test_result:
            self.log("🎉 测试词典API测试成功！", "SUCCESS")
        else:
            self.log("💥 测试词典API测试失败！", "ERROR")
        
        return test_result


def main():
    """主函数"""
    print("打字练习单词API测试脚本")
    print("=" * 50)
    
    # 创建测试器
    tester = TypingWordsAPITester()
    
    # 运行测试
    success = tester.run_full_test()
    
    # 返回结果
    if success:
        print("\n✅ 所有测试通过！测试词典可以正常使用。")
        return 0
    else:
        print("\n❌ 测试失败！需要检查API或数据库配置。")
        return 1


if __name__ == "__main__":
    exit(main())
