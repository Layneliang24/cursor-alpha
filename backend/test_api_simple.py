"""
简单的API功能测试脚本
用于验证打字练习相关API是否正常工作
"""

import os
import sys
import django
import requests
import json

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alpha.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.english.models import TypingWord, Dictionary, TypingSession, UserTypingStats

User = get_user_model()


def test_api_directly():
    """直接测试API功能"""
    print("=== 开始API功能测试 ===\n")
    
    # 1. 检查数据库中的词库数据
    print("1. 检查数据库中的词库数据:")
    try:
        dictionaries = Dictionary.objects.all()
        print(f"   找到 {dictionaries.count()} 个词库:")
        for dict_obj in dictionaries:
            print(f"   - {dict_obj.name} (类别: {dict_obj.category}, 单词数: {dict_obj.total_words}, 章节数: {dict_obj.chapter_count})")
    except Exception as e:
        print(f"   错误: {e}")
    
    print()
    
    # 2. 检查数据库中的单词数据
    print("2. 检查数据库中的单词数据:")
    try:
        words = TypingWord.objects.all()
        print(f"   找到 {words.count()} 个单词:")
        for word in words[:5]:  # 只显示前5个
            print(f"   - {word.word} (翻译: {word.translation}, 词库: {word.dictionary.name if word.dictionary else 'None'}, 章节: {word.chapter})")
        if words.count() > 5:
            print(f"   ... 还有 {words.count() - 5} 个单词")
    except Exception as e:
        print(f"   错误: {e}")
    
    print()
    
    # 3. 检查API端点是否可访问
    print("3. 检查API端点:")
    base_url = "http://localhost:8000"
    
    # 检查词库API
    try:
        response = requests.get(f"{base_url}/api/v1/english/dictionaries/")
        print(f"   词库API: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   返回 {len(data)} 个词库")
        else:
            print(f"   错误: {response.text}")
    except Exception as e:
        print(f"   词库API错误: {e}")
    
    # 检查打字练习单词API
    try:
        # 先尝试获取词库列表
        dict_response = requests.get(f"{base_url}/api/v1/english/dictionaries/")
        if dict_response.status_code == 200:
            dictionaries = dict_response.json()
            if dictionaries:
                # 使用第一个词库进行测试
                test_dict = dictionaries[0]
                print(f"   使用词库 '{test_dict['name']}' 测试打字练习API")
                
                params = {
                    'category': test_dict['name'],
                    'difficulty': 'beginner',
                    'chapter': 1,
                    'limit': 5
                }
                
                response = requests.get(f"{base_url}/api/v1/english/typing-practice/words/", params=params)
                print(f"   打字练习API: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"   返回 {len(data)} 个单词")
                    if data:
                        print(f"   第一个单词: {data[0]}")
                else:
                    print(f"   错误: {response.text}")
            else:
                print("   没有可用的词库进行测试")
        else:
            print(f"   无法获取词库列表: {dict_response.status_code}")
    except Exception as e:
        print(f"   打字练习API错误: {e}")
    
    print()
    
    # 4. 检查模型关系
    print("4. 检查模型关系:")
    try:
        # 检查TypingWord和Dictionary的关系
        words_with_dict = TypingWord.objects.select_related('dictionary').all()
        print(f"   有词库关联的单词: {words_with_dict.count()}")
        
        # 检查章节分布
        chapter_counts = {}
        for word in words_with_dict:
            chapter = word.chapter
            chapter_counts[chapter] = chapter_counts.get(chapter, 0) + 1
        
        print(f"   章节分布: {dict(sorted(chapter_counts.items()))}")
        
    except Exception as e:
        print(f"   模型关系检查错误: {e}")
    
    print("\n=== API功能测试完成 ===")


if __name__ == '__main__':
    test_api_directly()

简单的API功能测试脚本
用于验证打字练习相关API是否正常工作
"""

import os
import sys
import django
import requests
import json

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alpha.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.english.models import TypingWord, Dictionary, TypingSession, UserTypingStats

User = get_user_model()


def test_api_directly():
    """直接测试API功能"""
    print("=== 开始API功能测试 ===\n")
    
    # 1. 检查数据库中的词库数据
    print("1. 检查数据库中的词库数据:")
    try:
        dictionaries = Dictionary.objects.all()
        print(f"   找到 {dictionaries.count()} 个词库:")
        for dict_obj in dictionaries:
            print(f"   - {dict_obj.name} (类别: {dict_obj.category}, 单词数: {dict_obj.total_words}, 章节数: {dict_obj.chapter_count})")
    except Exception as e:
        print(f"   错误: {e}")
    
    print()
    
    # 2. 检查数据库中的单词数据
    print("2. 检查数据库中的单词数据:")
    try:
        words = TypingWord.objects.all()
        print(f"   找到 {words.count()} 个单词:")
        for word in words[:5]:  # 只显示前5个
            print(f"   - {word.word} (翻译: {word.translation}, 词库: {word.dictionary.name if word.dictionary else 'None'}, 章节: {word.chapter})")
        if words.count() > 5:
            print(f"   ... 还有 {words.count() - 5} 个单词")
    except Exception as e:
        print(f"   错误: {e}")
    
    print()
    
    # 3. 检查API端点是否可访问
    print("3. 检查API端点:")
    base_url = "http://localhost:8000"
    
    # 检查词库API
    try:
        response = requests.get(f"{base_url}/api/v1/english/dictionaries/")
        print(f"   词库API: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   返回 {len(data)} 个词库")
        else:
            print(f"   错误: {response.text}")
    except Exception as e:
        print(f"   词库API错误: {e}")
    
    # 检查打字练习单词API
    try:
        # 先尝试获取词库列表
        dict_response = requests.get(f"{base_url}/api/v1/english/dictionaries/")
        if dict_response.status_code == 200:
            dictionaries = dict_response.json()
            if dictionaries:
                # 使用第一个词库进行测试
                test_dict = dictionaries[0]
                print(f"   使用词库 '{test_dict['name']}' 测试打字练习API")
                
                params = {
                    'category': test_dict['name'],
                    'difficulty': 'beginner',
                    'chapter': 1,
                    'limit': 5
                }
                
                response = requests.get(f"{base_url}/api/v1/english/typing-practice/words/", params=params)
                print(f"   打字练习API: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"   返回 {len(data)} 个单词")
                    if data:
                        print(f"   第一个单词: {data[0]}")
                else:
                    print(f"   错误: {response.text}")
            else:
                print("   没有可用的词库进行测试")
        else:
            print(f"   无法获取词库列表: {dict_response.status_code}")
    except Exception as e:
        print(f"   打字练习API错误: {e}")
    
    print()
    
    # 4. 检查模型关系
    print("4. 检查模型关系:")
    try:
        # 检查TypingWord和Dictionary的关系
        words_with_dict = TypingWord.objects.select_related('dictionary').all()
        print(f"   有词库关联的单词: {words_with_dict.count()}")
        
        # 检查章节分布
        chapter_counts = {}
        for word in words_with_dict:
            chapter = word.chapter
            chapter_counts[chapter] = chapter_counts.get(chapter, 0) + 1
        
        print(f"   章节分布: {dict(sorted(chapter_counts.items()))}")
        
    except Exception as e:
        print(f"   模型关系检查错误: {e}")
    
    print("\n=== API功能测试完成 ===")


if __name__ == '__main__':
    test_api_directly()

