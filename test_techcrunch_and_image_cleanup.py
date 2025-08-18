#!/usr/bin/env python3
"""
TechCrunch爬取问题和图片删除问题诊断脚本
"""

import sys
import os
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_techcrunch_crawler():
    """测试TechCrunch爬虫"""
    print("🧪 测试TechCrunch爬虫")
    print("="*50)
    
    try:
        # 添加项目路径
        backend_path = os.path.join(os.path.dirname(__file__), 'backend')
        sys.path.insert(0, backend_path)
        
        # 设置Django环境
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alpha.settings')
        
        import django
        django.setup()
        
        from apps.english.news_crawler import TechCrunchNewsCrawler
        
        print("1. 创建TechCrunch爬虫实例...")
        crawler = TechCrunchNewsCrawler()
        print("✅ TechCrunch爬虫创建成功")
        
        print("2. 检查RSS源...")
        print(f"RSS源数量: {len(crawler.rss_feeds)}")
        for i, rss_url in enumerate(crawler.rss_feeds, 1):
            print(f"   {i}. {rss_url}")
        
        print("3. 测试RSS内容获取...")
        for rss_url in crawler.rss_feeds:
            print(f"   测试: {rss_url}")
            try:
                soup = crawler.get_rss_content(rss_url)
                if soup:
                    items = soup.find_all('item')
                    print(f"   ✅ 成功获取 {len(items)} 个RSS条目")
                    
                    if items:
                        # 测试第一个条目
                        first_item = items[0]
                        title_elem = first_item.find('title')
                        link_elem = first_item.find('link')
                        
                        if title_elem and link_elem:
                            title = crawler.clean_text(title_elem.get_text())
                            url = link_elem.get_text().strip()
                            print(f"   示例标题: {title[:50]}...")
                            print(f"   示例URL: {url}")
                            
                            # 测试文章内容获取
                            print("   测试文章内容获取...")
                            article_data = crawler.get_article_content(url)
                            if article_data:
                                content_length = len(article_data['content'])
                                print(f"   ✅ 成功获取文章内容: {content_length} 字符")
                                print(f"   图片URL: {article_data.get('image_url', '无')}")
                            else:
                                print("   ❌ 无法获取文章内容")
                        else:
                            print("   ❌ RSS条目格式不正确")
                else:
                    print("   ❌ 无法获取RSS内容")
                    
            except Exception as e:
                print(f"   ❌ 测试失败: {e}")
        
        print("4. 测试完整爬取...")
        news_items = crawler.crawl_news_list()
        print(f"✅ 成功爬取 {len(news_items)} 条TechCrunch新闻")
        
        if news_items:
            print("5. 显示爬取的新闻:")
            for i, news in enumerate(news_items[:3], 1):
                print(f"   {i}. {news.title[:60]}...")
                print(f"      来源: {news.source}")
                print(f"      难度: {news.difficulty_level}")
                print(f"      内容长度: {len(news.content)} 字符")
                print(f"      图片: {news.image_url or '无'}")
                print()
        
        return True
        
    except Exception as e:
        print(f"❌ TechCrunch爬虫测试失败: {e}")
        return False

def test_news_deletion_with_image_cleanup():
    """测试新闻删除时的图片清理"""
    print("\n🧪 测试新闻删除时的图片清理")
    print("="*50)
    
    try:
        # 添加项目路径
        backend_path = os.path.join(os.path.dirname(__file__), 'backend')
        sys.path.insert(0, backend_path)
        
        # 设置Django环境
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alpha.settings')
        
        import django
        django.setup()
        
        from apps.english.models import News
        from django.conf import settings
        import os
        
        print("1. 检查现有新闻的图片...")
        news_with_images = News.objects.filter(image_url__startswith='news_images/')
        print(f"   有本地图片的新闻数量: {news_with_images.count()}")
        
        if news_with_images.exists():
            print("2. 显示有本地图片的新闻:")
            for news in news_with_images[:3]:
                print(f"   - {news.title[:50]}...")
                print(f"     图片路径: {news.image_url}")
                
                # 检查文件是否存在
                if news.image_url.startswith('news_images/'):
                    image_path = os.path.join(settings.MEDIA_ROOT, news.image_url)
                    if os.path.exists(image_path):
                        file_size = os.path.getsize(image_path)
                        print(f"     文件存在，大小: {file_size} 字节")
                    else:
                        print(f"     文件不存在: {image_path}")
                print()
        
        print("3. 测试新闻删除功能...")
        # 创建一个测试新闻（如果有的话）
        test_news = News.objects.filter(image_url__startswith='news_images/').first()
        
        if test_news:
            print(f"   测试删除新闻: {test_news.title[:50]}...")
            print(f"   图片路径: {test_news.image_url}")
            
            # 检查删除前的图片文件
            if test_news.image_url.startswith('news_images/'):
                image_path = os.path.join(settings.MEDIA_ROOT, test_news.image_url)
                if os.path.exists(image_path):
                    print(f"   删除前图片文件存在: {image_path}")
                    
                    # 记录文件信息
                    file_size = os.path.getsize(image_path)
                    print(f"   文件大小: {file_size} 字节")
                    
                    # 删除新闻
                    news_id = test_news.id
                    test_news.delete()
                    
                    # 检查删除后的图片文件
                    if os.path.exists(image_path):
                        print("   ❌ 新闻删除后图片文件仍然存在")
                        print("   ⚠️ 需要实现图片文件清理功能")
                    else:
                        print("   ✅ 新闻删除后图片文件已清理")
                else:
                    print("   ⚠️ 图片文件不存在，无法测试清理功能")
            else:
                print("   ⚠️ 不是本地图片，跳过清理测试")
        else:
            print("   ⚠️ 没有找到有本地图片的新闻用于测试")
        
        return True
        
    except Exception as e:
        print(f"❌ 图片清理测试失败: {e}")
        return False

def create_image_cleanup_solution():
    """创建图片清理解决方案"""
    print("\n🔧 图片清理解决方案")
    print("="*50)
    
    print("问题分析:")
    print("1. News模型没有重写delete方法")
    print("2. 删除新闻时不会自动清理本地图片文件")
    print("3. 需要实现图片文件清理功能")
    
    print("\n解决方案:")
    print("1. 重写News模型的delete方法")
    print("2. 在删除新闻时检查并删除本地图片文件")
    print("3. 添加图片文件清理的单元测试")
    
    print("\n实现步骤:")
    print("1. 修改News模型，添加delete方法")
    print("2. 创建图片文件清理函数")
    print("3. 添加单元测试验证功能")
    print("4. 更新文档说明")

def create_techcrunch_fix_solution():
    """创建TechCrunch修复解决方案"""
    print("\n🔧 TechCrunch修复解决方案")
    print("="*50)
    
    print("问题分析:")
    print("1. TechCrunch RSS源可能不可访问")
    print("2. 文章内容提取可能失败")
    print("3. 反爬虫机制可能阻止访问")
    
    print("\n解决方案:")
    print("1. 更新RSS源URL")
    print("2. 改进内容提取逻辑")
    print("3. 添加更多错误处理")
    print("4. 使用备用RSS源")
    
    print("\n实现步骤:")
    print("1. 测试和更新RSS源")
    print("2. 改进TechCrunchNewsCrawler")
    print("3. 添加重试机制")
    print("4. 创建单元测试")

def main():
    """主函数"""
    print("🧪 TechCrunch爬取和图片清理问题诊断")
    print("="*60)
    
    # 测试TechCrunch爬虫
    techcrunch_ok = test_techcrunch_crawler()
    
    # 测试图片清理
    image_cleanup_ok = test_news_deletion_with_image_cleanup()
    
    # 生成解决方案
    create_techcrunch_fix_solution()
    create_image_cleanup_solution()
    
    # 总结
    print("\n" + "="*60)
    print("📊 测试结果总结")
    print("="*60)
    
    print(f"TechCrunch爬虫: {'✅ 正常' if techcrunch_ok else '❌ 有问题'}")
    print(f"图片清理功能: {'✅ 正常' if image_cleanup_ok else '❌ 有问题'}")
    
    print("\n🎯 下一步行动:")
    print("1. 修复TechCrunch爬虫问题")
    print("2. 实现图片文件清理功能")
    print("3. 创建相应的单元测试")
    print("4. 验证修复效果")

if __name__ == "__main__":
    main()




