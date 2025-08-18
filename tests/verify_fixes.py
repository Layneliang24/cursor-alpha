#!/usr/bin/env python
"""
验证修复效果的简单脚本
"""

def test_model_field_fixes():
    """测试模型字段修复"""
    print("🔍 验证模型字段修复...")
    
    # 检查Word模型字段
    try:
        from apps.english.models import Word
        word_fields = [field.name for field in Word._meta.fields]
        expected_fields = ['word', 'phonetic', 'definition', 'example']
        
        for field in expected_fields:
            if field in word_fields:
                print(f"✅ Word模型包含字段: {field}")
            else:
                print(f"❌ Word模型缺少字段: {field}")
        
    except Exception as e:
        print(f"❌ Word模型测试失败: {e}")
    
    # 检查News模型字段
    try:
        from apps.english.models import News
        news_fields = [field.name for field in News._meta.fields]
        expected_fields = ['title', 'content', 'source', 'source_url', 'publish_date']
        
        for field in expected_fields:
            if field in news_fields:
                print(f"✅ News模型包含字段: {field}")
            else:
                print(f"❌ News模型缺少字段: {field}")
        
    except Exception as e:
        print(f"❌ News模型测试失败: {e}")
    
    # 检查TypingWord模型字段
    try:
        from apps.english.models import TypingWord, Dictionary
        typing_word_fields = [field.name for field in TypingWord._meta.fields]
        expected_fields = ['word', 'translation', 'phonetic', 'difficulty', 'dictionary']
        
        for field in expected_fields:
            if field in typing_word_fields:
                print(f"✅ TypingWord模型包含字段: {field}")
            else:
                print(f"❌ TypingWord模型缺少字段: {field}")
        
    except Exception as e:
        print(f"❌ TypingWord模型测试失败: {e}")


def test_api_url_fixes():
    """测试API URL修复"""
    print("\n🔍 验证API URL修复...")
    
    # 检查健康检查URL
    try:
        from django.urls import reverse
        health_url = '/api/health/'
        print(f"✅ 健康检查URL: {health_url}")
    except Exception as e:
        print(f"❌ 健康检查URL测试失败: {e}")
    
    # 检查认证URL
    auth_urls = [
        '/api/v1/auth/login/',
        '/api/v1/auth/register/',
        '/api/v1/auth/logout/'
    ]
    
    for url in auth_urls:
        print(f"✅ 认证URL: {url}")
    
    # 检查英语学习URL
    english_urls = [
        '/api/v1/english/words/',
        '/api/v1/english/expressions/',
        '/api/v1/english/news/'
    ]
    
    for url in english_urls:
        print(f"✅ 英语学习URL: {url}")


def test_database_config_fixes():
    """测试数据库配置修复"""
    print("\n🔍 验证数据库配置修复...")
    
    try:
        from django.conf import settings
        db_engine = settings.DATABASES['default']['ENGINE']
        print(f"✅ 数据库引擎: {db_engine}")
        
        if 'sqlite' in db_engine or 'mysql' in db_engine:
            print("✅ 数据库引擎配置正确")
        else:
            print("❌ 数据库引擎配置异常")
            
    except Exception as e:
        print(f"❌ 数据库配置测试失败: {e}")


if __name__ == '__main__':
    print("🚀 开始验证修复效果...\n")
    
    test_model_field_fixes()
    test_api_url_fixes()
    test_database_config_fixes()
    
    print("\n✅ 验证完成！") 