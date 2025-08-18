"""
带认证的API功能测试脚本
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
from rest_framework_simplejwt.tokens import RefreshToken
from apps.english.models import TypingWord, Dictionary, TypingSession, UserTypingStats

User = get_user_model()


def create_test_user_and_get_token():
    """创建测试用户并获取认证token"""
    try:
        # 创建测试用户
        user, created = User.objects.get_or_create(
            username='testuser_api',
            defaults={
                'email': 'test_api@example.com',
                'password': 'testpass123'
            }
        )
        
        if created:
            user.set_password('testpass123')
            user.save()
            print(f"创建了新用户: {user.username}")
        else:
            print(f"使用现有用户: {user.username}")
        
        # 生成JWT token
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        print(f"获取到认证token: {access_token[:20]}...")
        return access_token
        
    except Exception as e:
        print(f"创建用户或获取token失败: {e}")
        return None


def test_api_with_auth():
    """使用认证测试API功能"""
    print("=== 开始带认证的API功能测试 ===\n")
    
    # 1. 获取认证token
    print("1. 获取认证token:")
    token = create_test_user_and_get_token()
    if not token:
        print("   无法获取认证token，测试终止")
        return
    
    print()
    
    # 2. 设置请求头
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    base_url = "http://localhost:8000"
    
    # 3. 测试词库API
    print("2. 测试词库API:")
    try:
        response = requests.get(f"{base_url}/api/v1/english/dictionaries/", headers=headers)
        print(f"   词库API状态码: {response.status_code}")
        
        if response.status_code == 200:
            dictionaries = response.json()
            print(f"   返回 {len(dictionaries)} 个词库")
            
            # 显示前几个词库
            for i, dict_obj in enumerate(dictionaries[:3]):
                print(f"   - {dict_obj['name']} (类别: {dict_obj['category']}, 单词数: {dict_obj['total_words']})")
            
            if len(dictionaries) > 3:
                print(f"   ... 还有 {len(dictionaries) - 3} 个词库")
        else:
            print(f"   错误: {response.text}")
            return
            
    except Exception as e:
        print(f"   词库API错误: {e}")
        return
    
    print()
    
    # 4. 测试打字练习单词API
    print("3. 测试打字练习单词API:")
    try:
        # 使用第一个词库进行测试
        test_dict = dictionaries[0]
        print(f"   使用词库 '{test_dict['name']}' 进行测试")
        
        # 测试不同的参数组合
        test_cases = [
            {
                'name': '基本查询（无章节过滤）',
                'params': {
                    'category': test_dict['name'],
                    'difficulty': 'beginner',
                    'limit': 5
                }
            },
            {
                'name': '带章节过滤',
                'params': {
                    'category': test_dict['name'],
                    'difficulty': 'beginner',
                    'chapter': 1,
                    'limit': 5
                }
            },
            {
                'name': '不同难度级别',
                'params': {
                    'category': test_dict['name'],
                    'difficulty': 'intermediate',
                    'chapter': 1,
                    'limit': 5
                }
            }
        ]
        
        for test_case in test_cases:
            print(f"   测试: {test_case['name']}")
            response = requests.get(f"{base_url}/api/v1/english/typing-practice/words/", 
                                 params=test_case['params'], headers=headers)
            
            print(f"   状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   返回 {len(data)} 个单词")
                if data:
                    first_word = data[0]
                    print(f"   第一个单词: {first_word['word']} (翻译: {first_word['translation']}, 章节: {first_word['chapter']})")
            else:
                print(f"   错误: {response.text}")
            
            print()
            
    except Exception as e:
        print(f"   打字练习API错误: {e}")
    
    # 5. 测试错误情况
    print("4. 测试错误情况:")
    try:
        # 测试不存在的词库
        print("   测试不存在的词库:")
        response = requests.get(f"{base_url}/api/v1/english/typing-practice/words/", 
                             params={'category': 'NONEXISTENT_DICT', 'difficulty': 'beginner'}, 
                             headers=headers)
        print(f"   状态码: {response.status_code}")
        if response.status_code == 404:
            print("   ✓ 正确返回404错误")
        else:
            print(f"   意外状态码: {response.status_code}")
        
        # 测试无效的难度级别
        print("   测试无效的难度级别:")
        response = requests.get(f"{base_url}/api/v1/english/typing-practice/words/", 
                             params={'category': test_dict['name'], 'difficulty': 'invalid'}, 
                             headers=headers)
        print(f"   状态码: {response.status_code}")
        if response.status_code == 400:
            print("   ✓ 正确返回400错误")
        else:
            print(f"   意外状态码: {response.status_code}")
            
    except Exception as e:
        print(f"   错误情况测试失败: {e}")
    
    print("\n=== 带认证的API功能测试完成 ===")


if __name__ == '__main__':
    test_api_with_auth()

带认证的API功能测试脚本
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
from rest_framework_simplejwt.tokens import RefreshToken
from apps.english.models import TypingWord, Dictionary, TypingSession, UserTypingStats

User = get_user_model()


def create_test_user_and_get_token():
    """创建测试用户并获取认证token"""
    try:
        # 创建测试用户
        user, created = User.objects.get_or_create(
            username='testuser_api',
            defaults={
                'email': 'test_api@example.com',
                'password': 'testpass123'
            }
        )
        
        if created:
            user.set_password('testpass123')
            user.save()
            print(f"创建了新用户: {user.username}")
        else:
            print(f"使用现有用户: {user.username}")
        
        # 生成JWT token
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        print(f"获取到认证token: {access_token[:20]}...")
        return access_token
        
    except Exception as e:
        print(f"创建用户或获取token失败: {e}")
        return None


def test_api_with_auth():
    """使用认证测试API功能"""
    print("=== 开始带认证的API功能测试 ===\n")
    
    # 1. 获取认证token
    print("1. 获取认证token:")
    token = create_test_user_and_get_token()
    if not token:
        print("   无法获取认证token，测试终止")
        return
    
    print()
    
    # 2. 设置请求头
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    base_url = "http://localhost:8000"
    
    # 3. 测试词库API
    print("2. 测试词库API:")
    try:
        response = requests.get(f"{base_url}/api/v1/english/dictionaries/", headers=headers)
        print(f"   词库API状态码: {response.status_code}")
        
        if response.status_code == 200:
            dictionaries = response.json()
            print(f"   返回 {len(dictionaries)} 个词库")
            
            # 显示前几个词库
            for i, dict_obj in enumerate(dictionaries[:3]):
                print(f"   - {dict_obj['name']} (类别: {dict_obj['category']}, 单词数: {dict_obj['total_words']})")
            
            if len(dictionaries) > 3:
                print(f"   ... 还有 {len(dictionaries) - 3} 个词库")
        else:
            print(f"   错误: {response.text}")
            return
            
    except Exception as e:
        print(f"   词库API错误: {e}")
        return
    
    print()
    
    # 4. 测试打字练习单词API
    print("3. 测试打字练习单词API:")
    try:
        # 使用第一个词库进行测试
        test_dict = dictionaries[0]
        print(f"   使用词库 '{test_dict['name']}' 进行测试")
        
        # 测试不同的参数组合
        test_cases = [
            {
                'name': '基本查询（无章节过滤）',
                'params': {
                    'category': test_dict['name'],
                    'difficulty': 'beginner',
                    'limit': 5
                }
            },
            {
                'name': '带章节过滤',
                'params': {
                    'category': test_dict['name'],
                    'difficulty': 'beginner',
                    'chapter': 1,
                    'limit': 5
                }
            },
            {
                'name': '不同难度级别',
                'params': {
                    'category': test_dict['name'],
                    'difficulty': 'intermediate',
                    'chapter': 1,
                    'limit': 5
                }
            }
        ]
        
        for test_case in test_cases:
            print(f"   测试: {test_case['name']}")
            response = requests.get(f"{base_url}/api/v1/english/typing-practice/words/", 
                                 params=test_case['params'], headers=headers)
            
            print(f"   状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   返回 {len(data)} 个单词")
                if data:
                    first_word = data[0]
                    print(f"   第一个单词: {first_word['word']} (翻译: {first_word['translation']}, 章节: {first_word['chapter']})")
            else:
                print(f"   错误: {response.text}")
            
            print()
            
    except Exception as e:
        print(f"   打字练习API错误: {e}")
    
    # 5. 测试错误情况
    print("4. 测试错误情况:")
    try:
        # 测试不存在的词库
        print("   测试不存在的词库:")
        response = requests.get(f"{base_url}/api/v1/english/typing-practice/words/", 
                             params={'category': 'NONEXISTENT_DICT', 'difficulty': 'beginner'}, 
                             headers=headers)
        print(f"   状态码: {response.status_code}")
        if response.status_code == 404:
            print("   ✓ 正确返回404错误")
        else:
            print(f"   意外状态码: {response.status_code}")
        
        # 测试无效的难度级别
        print("   测试无效的难度级别:")
        response = requests.get(f"{base_url}/api/v1/english/typing-practice/words/", 
                             params={'category': test_dict['name'], 'difficulty': 'invalid'}, 
                             headers=headers)
        print(f"   状态码: {response.status_code}")
        if response.status_code == 400:
            print("   ✓ 正确返回400错误")
        else:
            print(f"   意外状态码: {response.status_code}")
            
    except Exception as e:
        print(f"   错误情况测试失败: {e}")
    
    print("\n=== 带认证的API功能测试完成 ===")


if __name__ == '__main__':
    test_api_with_auth()

