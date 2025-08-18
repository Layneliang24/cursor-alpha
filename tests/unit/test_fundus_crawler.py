#!/usr/bin/env python3
"""
简单的Fundus测试脚本
"""

import os
import sys
import django

# 设置Django环境
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alpha.settings')
django.setup()

from apps.english.fundus_crawler import get_fundus_service

def test_fundus_crawling():
    """测试Fundus爬虫"""
    print("=" * 50)
    print("Fundus爬虫测试")
    print("=" * 50)
    
    try:
        # 初始化服务
        service = get_fundus_service()
        print("✅ Fundus服务初始化成功")
        
        # 测试爬取BBC新闻
        print("\n🔄 测试爬取BBC新闻...")
        articles = service.crawl_publisher('uk.BBC', 2)
        print(f"✅ 爬取到 {len(articles)} 篇文章")
        
        # 检查文章内容和图片
        for i, article in enumerate(articles[:2], 1):
            print(f"\n文章 {i}:")
            print(f"  标题: {article.title[:80]}...")
            print(f"  内容长度: {len(article.content)} 字符")
            print(f"  图片URL: {article.image_url[:100] if article.image_url else '无图片'}")
            print(f"  来源: {article.source}")
            print(f"  发布时间: {article.published_at}")
        
        # 测试图片下载功能
        if articles and articles[0].image_url:
            print(f"\n🔄 测试图片下载功能...")
            local_image_path = service._download_and_save_image(articles[0].image_url, articles[0].title)
            if local_image_path:
                print(f"✅ 图片下载成功: {local_image_path}")
            else:
                print("❌ 图片下载失败")
        
        print("\n🎉 Fundus爬虫测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_fundus_crawling()
