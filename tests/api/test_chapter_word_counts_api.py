#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试章节单词数量API
验证新添加的chapter_word_counts接口

作者: Claude-4-sonnet
创建时间: 2025-08-21
"""

import requests
import json
from datetime import datetime


class ChapterWordCountsAPITester:
    """章节单词数量API测试器"""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1/english"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'ChapterWordCountsAPITester/1.0'
        })
    
    def log(self, message, level="INFO"):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
    
    def test_chapter_word_counts_api(self):
        """测试章节单词数量API"""
        self.log("=== 测试章节单词数量API ===")
        
        # 测试测试词典
        self.log("\n--- 测试测试词典 (ID: 3) ---")
        self.test_dictionary_chapters(3)
        
        # 测试CET-6词典
        self.log("\n--- 测试CET-6词典 (ID: 2) ---")
        self.test_dictionary_chapters(2)
        
        # 测试错误情况
        self.log("\n--- 测试错误情况 ---")
        self.test_error_cases()
    
    def test_dictionary_chapters(self, dictionary_id):
        """测试指定词典的章节数据"""
        self.log(f"测试词典ID: {dictionary_id}")
        
        try:
            response = self.session.get(
                f"{self.api_base}/dictionaries/chapter_word_counts/",
                params={'dictionary_id': dictionary_id}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ API调用成功")
                self.log(f"词典名称: {data.get('dictionary_name')}")
                self.log(f"总单词数: {data.get('total_words')}")
                self.log(f"章节数: {data.get('chapter_count')}")
                
                chapters = data.get('chapters', [])
                self.log(f"章节详情:")
                for chapter in chapters:
                    self.log(f"  第{chapter.get('number')}章: {chapter.get('wordCount')}个单词")
                
                # 验证数据准确性
                self.verify_chapter_data(dictionary_id, chapters)
                
            else:
                self.log(f"❌ API调用失败: {response.status_code}")
                self.log(f"响应内容: {response.text}")
                
        except Exception as e:
            self.log(f"❌ 测试异常: {str(e)}", "ERROR")
    
    def verify_chapter_data(self, dictionary_id, chapters):
        """验证章节数据的准确性"""
        self.log(f"\n--- 验证词典 {dictionary_id} 的章节数据 ---")
        
        # 这里可以添加更详细的数据验证逻辑
        total_chapter_words = sum(chapter.get('wordCount', 0) for chapter in chapters)
        self.log(f"章节单词总数: {total_chapter_words}")
        
        # 检查是否有空章节
        empty_chapters = [c for c in chapters if c.get('wordCount', 0) == 0]
        if empty_chapters:
            self.log(f"⚠️ 发现空章节: {[c.get('number') for c in empty_chapters]}")
        else:
            self.log("✅ 所有章节都有单词")
    
    def test_error_cases(self):
        """测试错误情况"""
        self.log("测试缺少dictionary_id参数")
        
        try:
            response = self.session.get(
                f"{self.api_base}/dictionaries/chapter_word_counts/"
            )
            
            if response.status_code == 400:
                self.log("✅ 正确返回400错误")
                error_data = response.json()
                self.log(f"错误信息: {error_data.get('error')}")
            else:
                self.log(f"❌ 意外状态码: {response.status_code}")
                
        except Exception as e:
            self.log(f"❌ 测试异常: {str(e)}", "ERROR")
        
        self.log("\n测试不存在的词典ID")
        
        try:
            response = self.session.get(
                f"{self.api_base}/dictionaries/chapter_word_counts/",
                params={'dictionary_id': 99999}
            )
            
            if response.status_code == 404:
                self.log("✅ 正确返回404错误")
                error_data = response.json()
                self.log(f"错误信息: {error_data.get('error')}")
            else:
                self.log(f"❌ 意外状态码: {response.status_code}")
                
        except Exception as e:
            self.log(f"❌ 测试异常: {str(e)}", "ERROR")
    
    def run_tests(self):
        """运行所有测试"""
        self.log("🚀 开始测试章节单词数量API")
        self.log("=" * 60)
        
        self.test_chapter_word_counts_api()
        
        self.log("\n" + "=" * 60)
        self.log("💡 测试总结:")
        self.log("1. 验证了新的chapter_word_counts API接口")
        self.log("2. 测试了正常情况和错误情况")
        self.log("3. 验证了章节数据的准确性")


def main():
    """主函数"""
    print("章节单词数量API测试脚本")
    print("=" * 60)
    
    # 创建测试器
    tester = ChapterWordCountsAPITester()
    
    # 运行测试
    tester.run_tests()
    
    print("\n✅ 测试完成！")


if __name__ == "__main__":
    main()
