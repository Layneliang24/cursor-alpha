#!/usr/bin/env python3
"""
验证TechCrunch爬虫和图片清理修复效果的快速测试脚本
"""

import sys
import os

def test_techcrunch_fixes():
    """测试TechCrunch修复效果"""
    print("🧪 验证TechCrunch爬虫修复效果")
    print("="*50)
    
    try:
        # 添加项目路径
        backend_path = os.path.join(os.path.dirname(__file__), '..', '..', 'backend')
        sys.path.insert(0, backend_path)
        
        # 设置Django环境
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alpha.settings')
        
        import django
        django.setup()
        
        from apps.english.news_crawler import TechCrunchNewsCrawler
        
        print("1. 检查TechCrunch爬虫配置...")
        crawler = TechCrunchNewsCrawler()
        
        # 验证配置
        print(f"   RSS源数量: {len(crawler.rss_feeds)}")
        print(f"   重试次数: {crawler.max_retries}")
        print(f"   重试延迟: {crawler.retry_delay}秒")
        
        # 检查RSS源
        expected_feeds = [
            'https://techcrunch.com/feed/',
            'https://techcrunch.com/category/artificial-intelligence/feed/',
            'https://techcrunch.com/category/startups/feed/',
            'https://techcrunch.com/category/enterprise/feed/',
            'https://techcrunch.com/category/security/feed/'
        ]
        
        if crawler.rss_feeds == expected_feeds:
            print("   ✅ RSS源配置正确")
        else:
            print("   ❌ RSS源配置不正确")
            return False
        
        print("2. 测试RSS源访问...")
        # 测试第一个RSS源
        first_rss = crawler.rss_feeds[0]
        print(f"   测试RSS源: {first_rss}")
        
        soup = crawler.get_rss_content(first_rss)
        if soup:
            items = soup.find_all('item')
            print(f"   ✅ 成功获取RSS内容，找到 {len(items)} 个条目")
            
            if items:
                print("   ✅ RSS源工作正常")
            else:
                print("   ⚠️ RSS源没有条目，但可以访问")
        else:
            print("   ❌ 无法获取RSS内容")
            return False
        
        print("3. 测试完整爬取流程...")
        news_items = crawler.crawl_news_list()
        print(f"   ✅ 爬取完成，获取 {len(news_items)} 条新闻")
        
        if news_items:
            print("4. 显示爬取的新闻:")
            for i, news in enumerate(news_items[:3], 1):
                print(f"   {i}. {news.title[:60]}...")
                print(f"      来源: {news.source}")
                print(f"      难度: {news.difficulty_level}")
                print(f"      内容长度: {len(news.content)} 字符")
                print()
        
        return True
        
    except Exception as e:
        print(f"❌ TechCrunch测试失败: {e}")
        return False

def test_image_cleanup_fixes():
    """测试图片清理修复效果"""
    print("\n🧪 验证图片清理修复效果")
    print("="*50)
    
    try:
        # 添加项目路径
        backend_path = os.path.join(os.path.dirname(__file__), '..', '..', 'backend')
        sys.path.insert(0, backend_path)
        
        # 设置Django环境
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alpha.settings')
        
        import django
        django.setup()
        
        from apps.english.models import News
        from django.conf import settings
        import tempfile
        import shutil
        
        print("1. 检查News模型方法...")
        
        # 检查News模型是否有新的方法
        news_methods = dir(News)
        required_methods = ['delete', '_cleanup_local_image', 'save']
        
        for method in required_methods:
            if method in news_methods:
                print(f"   ✅ {method} 方法存在")
            else:
                print(f"   ❌ {method} 方法不存在")
                return False
        
        print("2. 创建测试环境...")
        
        # 创建临时媒体目录
        temp_media_dir = tempfile.mkdtemp()
        original_media_root = settings.MEDIA_ROOT
        settings.MEDIA_ROOT = temp_media_dir
        
        # 创建news_images目录
        news_images_dir = os.path.join(temp_media_dir, 'news_images')
        os.makedirs(news_images_dir, exist_ok=True)
        
        try:
            print("3. 测试图片清理功能...")
            
            # 创建测试图片文件
            test_image_filename = 'test_cleanup_image.jpg'
            test_image_path = os.path.join(news_images_dir, test_image_filename)
            
            with open(test_image_path, 'wb') as f:
                f.write(b'fake image content for testing')
            
            # 验证文件存在
            if os.path.exists(test_image_path):
                print("   ✅ 测试图片文件创建成功")
            else:
                print("   ❌ 测试图片文件创建失败")
                return False
            
            # 创建新闻记录
            news = News.objects.create(
                title='Test News for Image Cleanup',
                content='Test content for image cleanup verification',
                source='Test',
                image_url=f'news_images/{test_image_filename}'
            )
            
            print(f"   ✅ 测试新闻创建成功，ID: {news.id}")
            
            # 删除新闻
            news.delete()
            
            # 验证新闻已删除
            if not News.objects.filter(id=news.id).exists():
                print("   ✅ 新闻删除成功")
            else:
                print("   ❌ 新闻删除失败")
                return False
            
            # 验证图片文件已删除
            if not os.path.exists(test_image_path):
                print("   ✅ 图片文件清理成功")
            else:
                print("   ❌ 图片文件清理失败")
                return False
            
            print("4. 测试图片URL更新功能...")
            
            # 创建两个测试图片文件
            old_image_filename = 'old_image.jpg'
            new_image_filename = 'new_image.jpg'
            old_image_path = os.path.join(news_images_dir, old_image_filename)
            new_image_path = os.path.join(news_images_dir, new_image_filename)
            
            with open(old_image_path, 'wb') as f:
                f.write(b'old image content')
            with open(new_image_path, 'wb') as f:
                f.write(b'new image content')
            
            # 创建新闻记录
            news = News.objects.create(
                title='Test News for Image Update',
                content='Test content',
                source='Test',
                image_url=f'news_images/{old_image_filename}'
            )
            
            # 更新图片URL
            news.image_url = f'news_images/{new_image_filename}'
            news.save()
            
            # 验证旧图片文件已删除
            if not os.path.exists(old_image_path):
                print("   ✅ 旧图片文件清理成功")
            else:
                print("   ❌ 旧图片文件清理失败")
            
            # 验证新图片文件仍然存在
            if os.path.exists(new_image_path):
                print("   ✅ 新图片文件保留成功")
            else:
                print("   ❌ 新图片文件意外删除")
            
            # 清理
            news.delete()
            
        finally:
            # 恢复原始设置
            settings.MEDIA_ROOT = original_media_root
            
            # 删除临时目录
            if os.path.exists(temp_media_dir):
                shutil.rmtree(temp_media_dir)
        
        return True
        
    except Exception as e:
        print(f"❌ 图片清理测试失败: {e}")
        return False

def run_unit_tests():
    """运行单元测试"""
    print("\n🧪 运行单元测试")
    print("="*50)
    
    try:
        # 添加项目路径
        backend_path = os.path.join(os.path.dirname(__file__), '..', '..', 'backend')
        sys.path.insert(0, backend_path)
        
        # 设置Django环境
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alpha.settings')
        
        import django
        django.setup()
        
        # 运行单元测试
        import subprocess
        import os
        
        test_file = os.path.join('tests', 'unit', 'test_techcrunch_and_image_cleanup.py')
        
        if os.path.exists(test_file):
            print(f"运行测试文件: {test_file}")
            
            # 切换到backend目录
            os.chdir(backend_path)
            
            # 运行pytest
            result = subprocess.run([
                'python', '-m', 'pytest', 
                os.path.join('..', test_file),
                '-v'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ 单元测试通过")
                print("测试输出:")
                print(result.stdout)
            else:
                print("❌ 单元测试失败")
                print("错误输出:")
                print(result.stderr)
                return False
        else:
            print(f"❌ 测试文件不存在: {test_file}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 运行单元测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🔧 TechCrunch爬虫和图片清理修复验证")
    print("="*60)
    
    # 测试TechCrunch修复
    techcrunch_ok = test_techcrunch_fixes()
    
    # 测试图片清理修复
    image_cleanup_ok = test_image_cleanup_fixes()
    
    # 运行单元测试
    unit_tests_ok = run_unit_tests()
    
    # 总结
    print("\n" + "="*60)
    print("📊 修复验证结果总结")
    print("="*60)
    
    print(f"TechCrunch爬虫修复: {'✅ 成功' if techcrunch_ok else '❌ 失败'}")
    print(f"图片清理功能修复: {'✅ 成功' if image_cleanup_ok else '❌ 失败'}")
    print(f"单元测试: {'✅ 通过' if unit_tests_ok else '❌ 失败'}")
    
    if techcrunch_ok and image_cleanup_ok and unit_tests_ok:
        print("\n🎉 所有修复验证通过！")
        print("✅ TechCrunch爬虫问题已解决")
        print("✅ 图片清理功能已实现")
        print("✅ 单元测试已创建并通过")
    else:
        print("\n⚠️ 部分修复验证失败，需要进一步检查")
    
    print("\n🎯 下一步建议:")
    print("1. 在生产环境中测试TechCrunch爬虫")
    print("2. 监控图片清理功能的性能")
    print("3. 定期运行单元测试确保功能稳定")

if __name__ == "__main__":
    main()
