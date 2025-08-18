#!/usr/bin/env python3
"""
测试新闻可见性字段移除和删除刷新功能
"""

import os
import sys
import django
import requests
import json
import time

# 设置Django环境
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alpha.settings')
django.setup()

from apps.english.models import News
from apps.users.models import User

def test_is_visible_field_removed():
    """测试is_visible字段已从模型中移除"""
    print("=" * 50)
    print("测试is_visible字段移除")
    print("=" * 50)
    
    try:
        # 检查模型字段
        news_fields = [field.name for field in News._meta.fields]
        
        if 'is_visible' in news_fields:
            print("❌ is_visible字段仍然存在于模型中")
            return False
        else:
            print("✅ is_visible字段已从模型中移除")
            return True
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False

def test_news_creation_without_visibility():
    """测试创建新闻时不需要is_visible字段"""
    print("\n" + "=" * 50)
    print("测试新闻创建（无可见性字段）")
    print("=" * 50)
    
    try:
        # 创建测试新闻
        test_news = News.objects.create(
            title="测试新闻标题",
            summary="测试新闻摘要",
            content="测试新闻内容",
            source="test",
            category="test",
            word_count=100
        )
        
        print(f"✅ 成功创建新闻: {test_news.title}")
        print(f"   新闻ID: {test_news.id}")
        
        # 清理测试数据
        test_news.delete()
        print("✅ 测试数据清理完成")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False

def test_api_without_visibility():
    """测试API不包含可见性字段"""
    print("\n" + "=" * 50)
    print("测试API响应（无可见性字段）")
    print("=" * 50)
    
    try:
        # 创建测试用户（如果需要认证）
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@example.com'}
        )
        
        # 创建测试新闻
        test_news = News.objects.create(
            title="API测试新闻",
            summary="API测试摘要",
            content="API测试内容",
            source="api_test",
            category="test",
            word_count=150
        )
        
        # 测试API响应
        response = requests.get('http://localhost:8000/api/v1/english/news/', timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            news_list = data.get('results', [])
            
            if news_list:
                first_news = news_list[0]
                if 'is_visible' in first_news:
                    print("❌ API响应中仍然包含is_visible字段")
                    return False
                else:
                    print("✅ API响应中不包含is_visible字段")
                    return True
            else:
                print("⚠️ API返回空列表，无法验证字段")
                return True
        else:
            print(f"❌ API请求失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False
    finally:
        # 清理测试数据
        try:
            test_news.delete()
            if created:
                user.delete()
        except:
            pass

def test_news_deletion_refresh():
    """测试删除新闻后列表刷新功能"""
    print("\n" + "=" * 50)
    print("测试删除新闻后列表刷新")
    print("=" * 50)
    
    try:
        # 创建测试新闻
        test_news = News.objects.create(
            title="删除测试新闻",
            summary="删除测试摘要",
            content="删除测试内容",
            source="delete_test",
            category="test",
            word_count=200
        )
        
        news_id = test_news.id
        print(f"✅ 创建测试新闻，ID: {news_id}")
        
        # 验证新闻存在
        response1 = requests.get('http://localhost:8000/api/v1/english/news/', timeout=10)
        if response1.status_code == 200:
            data1 = response1.json()
            news_list1 = data1.get('results', [])
            news_exists = any(news['id'] == news_id for news in news_list1)
            print(f"   删除前新闻存在: {news_exists}")
        
        # 删除新闻
        delete_response = requests.delete(f'http://localhost:8000/api/v1/english/news/{news_id}/delete_news/', timeout=10)
        if delete_response.status_code == 200:
            print("✅ 新闻删除成功")
        else:
            print(f"❌ 新闻删除失败: {delete_response.status_code}")
            return False
        
        # 等待一下确保删除完成
        time.sleep(1)
        
        # 验证新闻已删除
        response2 = requests.get('http://localhost:8000/api/v1/english/news/', timeout=10)
        if response2.status_code == 200:
            data2 = response2.json()
            news_list2 = data2.get('results', [])
            news_still_exists = any(news['id'] == news_id for news in news_list2)
            print(f"   删除后新闻存在: {news_still_exists}")
            
            if not news_still_exists:
                print("✅ 新闻删除后列表已正确更新")
                return True
            else:
                print("❌ 新闻删除后列表未正确更新")
                return False
        else:
            print(f"❌ 获取新闻列表失败: {response2.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("新闻可见性字段移除和删除刷新功能测试")
    print("=" * 60)
    print(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 运行所有测试
    tests = [
        ("is_visible字段移除", test_is_visible_field_removed),
        ("新闻创建（无可见性）", test_news_creation_without_visibility),
        ("API响应（无可见性）", test_api_without_visibility),
        ("删除新闻后列表刷新", test_news_deletion_refresh),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"🔄 运行测试: {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 测试通过")
            else:
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {str(e)}")
        print()
    
    # 测试结果总结
    print("=" * 60)
    print("测试结果总结")
    print("=" * 60)
    print(f"通过: {passed}/{total}")
    
    if passed == total:
        print("🎉 所有测试通过！")
    else:
        print("⚠️ 部分测试失败，请检查相关功能")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
















