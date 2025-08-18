#!/usr/bin/env python3
"""
CNN新闻爬取问题诊断脚本
定位和解决CNN在Fundus中不可用的问题
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

def test_fundus_import():
    """测试Fundus导入"""
    try:
        from fundus import PublisherCollection, Crawler
        logger.info("✅ Fundus导入成功")
        return True
    except ImportError as e:
        logger.error(f"❌ Fundus导入失败: {e}")
        return False

def test_publisher_collection():
    """测试发布者集合"""
    try:
        from fundus import PublisherCollection
        publishers = PublisherCollection()
        logger.info("✅ PublisherCollection创建成功")
        
        # 检查US国家对象
        if hasattr(publishers, 'us'):
            logger.info("✅ US国家对象存在")
            us_publishers = dir(publishers.us)
            logger.info(f"US发布者数量: {len([p for p in us_publishers if not p.startswith('_')])}")
            
            # 检查CNN是否存在
            if hasattr(publishers.us, 'CNN'):
                logger.info("✅ CNN发布者存在")
                return True
            else:
                logger.warning("⚠️ CNN发布者不存在")
                # 列出所有US发布者
                us_pub_list = [p for p in us_publishers if not p.startswith('_')]
                logger.info(f"US发布者列表: {us_pub_list}")
                return False
        else:
            logger.error("❌ US国家对象不存在")
            return False
            
    except Exception as e:
        logger.error(f"❌ 测试发布者集合失败: {e}")
        return False

def test_cnn_publisher():
    """测试CNN发布者"""
    try:
        from fundus import PublisherCollection, Crawler
        
        publishers = PublisherCollection()
        
        # 尝试获取CNN发布者
        if hasattr(publishers.us, 'CNN'):
            cnn_publisher = publishers.us.CNN
            logger.info(f"✅ CNN发布者获取成功: {cnn_publisher}")
            
            # 尝试创建爬虫
            try:
                crawler = Crawler(cnn_publisher)
                logger.info("✅ CNN爬虫创建成功")
                
                # 尝试爬取一篇文章
                article_count = 0
                for article in crawler.crawl(max_articles=1):
                    article_count += 1
                    logger.info(f"✅ 成功爬取CNN文章: {article.title[:50]}...")
                    break
                
                if article_count == 0:
                    logger.warning("⚠️ CNN爬虫没有返回任何文章")
                    return False
                    
                return True
                
            except Exception as e:
                logger.error(f"❌ CNN爬虫创建或运行失败: {e}")
                return False
        else:
            logger.error("❌ CNN发布者不存在")
            return False
            
    except Exception as e:
        logger.error(f"❌ 测试CNN发布者失败: {e}")
        return False

def test_alternative_cnn():
    """测试替代CNN的方法"""
    try:
        from fundus import PublisherCollection
        
        publishers = PublisherCollection()
        
        # 查找可能的CNN替代名称
        us_publishers = dir(publishers.us)
        cnn_variants = [p for p in us_publishers if 'cnn' in p.lower() and not p.startswith('_')]
        
        if cnn_variants:
            logger.info(f"找到CNN变体: {cnn_variants}")
            for variant in cnn_variants:
                try:
                    publisher = getattr(publishers.us, variant)
                    logger.info(f"✅ 找到CNN替代: {variant} - {publisher}")
                except Exception as e:
                    logger.warning(f"⚠️ 测试{variant}失败: {e}")
        else:
            logger.warning("⚠️ 未找到CNN相关发布者")
            
        # 列出所有US发布者供参考
        all_us_publishers = [p for p in us_publishers if not p.startswith('_')]
        logger.info(f"所有US发布者: {all_us_publishers}")
        
    except Exception as e:
        logger.error(f"❌ 测试替代CNN失败: {e}")

def test_fundus_crawler_service():
    """测试FundusCrawlerService"""
    try:
        # 添加项目路径
        backend_path = os.path.join(os.path.dirname(__file__), '..', '..', 'backend')
        sys.path.insert(0, backend_path)
        
        # 设置Django环境
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alpha.settings')
        
        import django
        django.setup()
        
        from apps.english.fundus_crawler import FundusCrawlerService
        
        service = FundusCrawlerService()
        logger.info("✅ FundusCrawlerService创建成功")
        
        # 测试获取可用发布者
        available = service.get_available_publishers()
        logger.info(f"可用发布者: {available}")
        
        # 测试CNN发布者
        cnn_publisher = service._get_publisher('cnn')
        if cnn_publisher:
            logger.info(f"✅ CNN发布者获取成功: {cnn_publisher}")
        else:
            logger.error("❌ CNN发布者获取失败")
            
        return True
        
    except Exception as e:
        logger.error(f"❌ 测试FundusCrawlerService失败: {e}")
        return False

def test_available_publishers_file():
    """测试available_publishers.py文件"""
    try:
        backend_path = os.path.join(os.path.dirname(__file__), '..', '..', 'backend')
        sys.path.insert(0, backend_path)
        
        from available_publishers import AVAILABLE_PUBLISHERS
        
        logger.info(f"✅ available_publishers.py加载成功，共{len(AVAILABLE_PUBLISHERS)}个发布者")
        
        # 检查CNN是否在列表中
        cnn_variants = [p for p in AVAILABLE_PUBLISHERS if 'cnn' in p.lower()]
        if cnn_variants:
            logger.info(f"找到CNN相关发布者: {cnn_variants}")
        else:
            logger.warning("⚠️ CNN不在可用发布者列表中")
            
        # 检查US发布者
        us_publishers = [p for p in AVAILABLE_PUBLISHERS if p.startswith('us.')]
        logger.info(f"US发布者数量: {len(us_publishers)}")
        logger.info(f"US发布者列表: {us_publishers}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 测试available_publishers.py失败: {e}")
        return False

def generate_solution():
    """生成解决方案"""
    logger.info("\n" + "="*50)
    logger.info("🔧 解决方案建议")
    logger.info("="*50)
    
    logger.info("1. 检查CNN发布者名称:")
    logger.info("   - 可能CNN在Fundus中的名称不是'CNN'")
    logger.info("   - 尝试使用'us.CNN'或其他变体")
    
    logger.info("2. 更新available_publishers.py:")
    logger.info("   - 运行测试脚本重新生成可用发布者列表")
    logger.info("   - 确保CNN被包含在测试列表中")
    
    logger.info("3. 使用传统爬虫作为备选:")
    logger.info("   - CNN传统爬虫已经实现")
    logger.info("   - 在Fundus不可用时自动回退")
    
    logger.info("4. 手动测试CNN发布者:")
    logger.info("   - 在Python环境中手动测试CNN发布者")
    logger.info("   - 确认正确的发布者名称")

def main():
    """主函数"""
    logger.info("🧪 CNN新闻爬取问题诊断")
    logger.info("="*50)
    
    # 测试步骤
    tests = [
        ("Fundus导入", test_fundus_import),
        ("发布者集合", test_publisher_collection),
        ("CNN发布者", test_cnn_publisher),
        ("替代CNN", test_alternative_cnn),
        ("FundusCrawlerService", test_fundus_crawler_service),
        ("available_publishers.py", test_available_publishers_file),
    ]
    
    results = {}
    for test_name, test_func in tests:
        logger.info(f"\n📋 测试: {test_name}")
        logger.info("-" * 30)
        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"测试{test_name}时发生异常: {e}")
            results[test_name] = False
    
    # 生成解决方案
    generate_solution()
    
    # 总结
    logger.info("\n" + "="*50)
    logger.info("📊 测试结果总结")
    logger.info("="*50)
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        logger.info(f"{test_name}: {status}")
    
    success_count = sum(results.values())
    total_count = len(results)
    logger.info(f"\n总体结果: {success_count}/{total_count} 测试通过")

if __name__ == "__main__":
    main()
