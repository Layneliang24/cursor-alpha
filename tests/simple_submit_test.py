#!/usr/bin/env python
"""
Submit API简单测试

验证submit API基本功能是否正常工作
"""

import os
import sys
import django

# 设置Django环境
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alpha.settings')
django.setup()

import requests
import json
from apps.users.models import User
from apps.english.models import TypingWord, Dictionary
from rest_framework_simplejwt.tokens import RefreshToken

def test_submit_api():
    """测试submit API基本功能"""
    
    print("🧪 开始Submit API测试")
    print("=" * 50)
    
    try:
        # 1. 创建或获取测试用户
        print("1. 创建测试用户...")
        user, created = User.objects.get_or_create(
            email='submit_test@example.com',
            defaults={
                'username': 'submit_test_user',
                'first_name': 'Submit',
                'last_name': 'Test'
            }
        )
        print(f"   用户: {user.username} ({'新建' if created else '已存在'})")
        
        # 2. 生成JWT token
        print("2. 生成认证token...")
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        print(f"   Token: {access_token[:20]}...")
        
        # 3. 获取测试单词
        print("3. 获取测试单词...")
        word = TypingWord.objects.first()
        if not word:
            print("   ❌ 没有找到测试单词，请确保数据库中有单词数据")
            return False
        print(f"   单词: {word.word} (ID: {word.id})")
        
        # 4. 测试submit API
        print("4. 测试submit API...")
        url = 'http://127.0.0.1:8000/api/v1/english/typing-practice/submit/'
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        test_data = {
            'word_id': word.id,
            'is_correct': True,
            'typing_speed': 60,
            'response_time': 2.5
        }
        
        print(f"   URL: {url}")
        print(f"   数据: {test_data}")
        
        response = requests.post(url, json=test_data, headers=headers)
        
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.text}")
        
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get('status') == 'success':
                print("   ✅ Submit API测试成功！")
                print(f"   Session ID: {response_data.get('session_id')}")
                return True
            else:
                print("   ❌ Submit API响应格式错误")
                return False
        else:
            print(f"   ❌ Submit API测试失败，状态码: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ 测试过程中出现异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_consistency():
    """测试数据一致性"""
    
    print("\n🔍 检查数据一致性")
    print("=" * 50)
    
    try:
        from apps.english.models import TypingSession, TypingPracticeRecord
        
        # 获取最近的记录
        latest_session = TypingSession.objects.last()
        latest_practice = TypingPracticeRecord.objects.last()
        
        if latest_session and latest_practice:
            print(f"最新TypingSession记录:")
            print(f"   用户: {latest_session.user.username}")
            print(f"   单词: {latest_session.word.word}")
            print(f"   正确: {latest_session.is_correct}")
            print(f"   速度: {latest_session.typing_speed}")
            print(f"   时间: {latest_session.response_time}")
            
            print(f"\n最新TypingPracticeRecord记录:")
            print(f"   用户: {latest_practice.user.username}")
            print(f"   单词: {latest_practice.word}")
            print(f"   正确: {latest_practice.is_correct}")
            print(f"   速度: {latest_practice.typing_speed}")
            print(f"   时间: {latest_practice.response_time}")
            
            # 检查一致性
            if (latest_session.is_correct == latest_practice.is_correct and
                latest_session.typing_speed == latest_practice.typing_speed and
                latest_session.response_time == latest_practice.response_time):
                print("\n   ✅ 数据一致性检查通过")
                return True
            else:
                print("\n   ❌ 数据一致性检查失败")
                return False
        else:
            print("   ⚠️  没有找到练习记录")
            return True
            
    except Exception as e:
        print(f"   ❌ 数据一致性检查异常: {e}")
        return False

def main():
    """主测试函数"""
    
    print("🚀 Submit API 简单测试套件")
    print("=" * 60)
    
    # 基本功能测试
    api_test_passed = test_submit_api()
    
    # 数据一致性测试
    data_test_passed = test_data_consistency()
    
    # 结果汇总
    print("\n📊 测试结果汇总")
    print("=" * 60)
    print(f"Submit API功能测试: {'✅ 通过' if api_test_passed else '❌ 失败'}")
    print(f"数据一致性测试: {'✅ 通过' if data_test_passed else '❌ 失败'}")
    
    overall_success = api_test_passed and data_test_passed
    print(f"\n总体结果: {'🎉 全部通过' if overall_success else '💥 部分失败'}")
    
    return overall_success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
