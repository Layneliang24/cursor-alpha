#!/usr/bin/env python3
"""
简单的HTTP API测试脚本
"""

import requests
import json
import time

def test_backend_server():
    """测试后端服务器"""
    try:
        response = requests.get('http://localhost:8000/api/v1/english/news/', timeout=5)
        if response.status_code == 200:
            print("✅ 后端服务器运行正常")
            return True
        else:
            print(f"❌ 后端服务器响应异常: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 后端服务器连接失败: {e}")
        return False

def test_news_crawling():
    """测试新闻爬取API"""
    try:
        test_data = {
            "sources": ["uk.BBC", "us.TechCrunch"],
            "max_articles": 2,
            "timeout": 60
        }
        
        print("🔄 开始测试新闻爬取API...")
        print(f"   测试数据: {test_data}")
        
        response = requests.post(
            'http://localhost:8000/api/v1/english/news/crawl/',
            json=test_data,
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 新闻爬取API成功!")
            print(f"   响应数据: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"❌ 新闻爬取API失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 新闻爬取API请求失败: {e}")
        return False

def test_news_list():
    """测试新闻列表API"""
    try:
        response = requests.get('http://localhost:8000/api/v1/english/news/', timeout=10)
        if response.status_code == 200:
            data = response.json()
            news_count = len(data.get('results', []))
            print(f"✅ 获取新闻列表成功，共 {news_count} 条新闻")
            
            # 检查是否有图片
            news_with_images = 0
            for news in data.get('results', []):
                if news.get('image_url'):
                    news_with_images += 1
            
            print(f"   其中 {news_with_images} 条新闻包含图片")
            return True
        else:
            print(f"❌ 获取新闻列表失败: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 获取新闻列表请求失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("新闻爬取功能API测试")
    print("=" * 60)
    print(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 测试服务器状态
    print("1. 测试后端服务器状态")
    print("-" * 30)
    backend_ok = test_backend_server()
    print()
    
    if not backend_ok:
        print("❌ 后端服务器未运行，无法继续测试")
        return
    
    # 测试新闻爬取
    print("2. 测试新闻爬取API")
    print("-" * 30)
    crawling_ok = test_news_crawling()
    print()
    
    # 测试新闻列表
    print("3. 测试新闻列表API")
    print("-" * 30)
    list_ok = test_news_list()
    print()
    
    # 测试结果总结
    print("4. 测试结果总结")
    print("-" * 30)
    if backend_ok and crawling_ok and list_ok:
        print("🎉 所有API测试通过！新闻爬取功能正常工作")
    else:
        print("⚠️  部分API测试失败，请检查相关功能")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
