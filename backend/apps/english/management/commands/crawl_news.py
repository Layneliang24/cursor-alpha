"""
手动抓取英语新闻的管理命令
用于测试和维护新闻抓取功能
支持传统爬虫和Fundus爬虫
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from apps.english.news_crawler import real_news_crawler_service, FUNDUS_AVAILABLE
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '抓取英语新闻'

    def add_arguments(self, parser):
        parser.add_argument(
            '--source',
            type=str,
            default='bbc',
            choices=['bbc', 'cnn', 'reuters', 'techcrunch', 'local_test', 'xinhua', 'all'],
            help='新闻源 (默认: bbc)'
        )
        
        parser.add_argument(
            '--crawler',
            type=str,
            default='traditional',
            choices=['traditional', 'fundus', 'both'],
            help='爬虫类型: traditional(传统), fundus(Fundus), both(两者)'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='只抓取不保存，用于测试'
        )
        
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='详细输出'
        )

    def handle(self, *args, **options):
        source = options['source']
        crawler_type = options['crawler']
        dry_run = options['dry_run']
        verbose = options['verbose']
        
        if verbose:
            logging.basicConfig(level=logging.INFO)
        
        # 检查Fundus可用性
        if crawler_type in ['fundus', 'both'] and not FUNDUS_AVAILABLE:
            self.stdout.write(
                self.style.WARNING('Fundus不可用，将使用传统爬虫')
            )
            crawler_type = 'traditional'
        
        self.stdout.write(
            self.style.SUCCESS(f'开始抓取 {source} 新闻 (使用 {crawler_type} 爬虫)...')
        )
        
        try:
            # 抓取新闻
            start_time = timezone.now()
            all_news_items = []
            
            # 传统爬虫
            if crawler_type in ['traditional', 'both']:
                self.stdout.write('使用传统爬虫...')
                if source == 'all':
                    traditional_items = real_news_crawler_service.crawl_all_sources()
                else:
                    traditional_items = real_news_crawler_service.crawl_news(source)
                all_news_items.extend(traditional_items)
                self.stdout.write(f'传统爬虫获取 {len(traditional_items)} 条新闻')
            
            # Fundus爬虫
            if crawler_type in ['fundus', 'both'] and FUNDUS_AVAILABLE:
                self.stdout.write('使用Fundus爬虫...')
                from apps.english.fundus_crawler import fundus_crawler_service
                
                if source == 'all':
                    fundus_items = fundus_crawler_service.crawl_all_supported()
                else:
                    # 将传统源名称映射到Fundus源名称
                    fundus_source_map = {
                        'bbc': 'bbc',
                        'cnn': 'cnn',
                        'reuters': 'reuters',
                        'techcrunch': 'techcrunch'
                    }
                    fundus_source = fundus_source_map.get(source, source)
                    fundus_items = fundus_crawler_service.crawl_publisher(fundus_source)
                
                all_news_items.extend(fundus_items)
                self.stdout.write(f'Fundus爬虫获取 {len(fundus_items)} 条新闻')
            
            end_time = timezone.now()
            duration = (end_time - start_time).total_seconds()
            
            if not all_news_items:
                self.stdout.write(
                    self.style.WARNING(f'未抓取到任何 {source} 新闻')
                )
                return
            
            self.stdout.write(
                self.style.SUCCESS(f'抓取完成！共找到 {len(all_news_items)} 条新闻 (耗时 {duration:.2f}秒)')
            )
            
            # 显示新闻列表
            if verbose:
                for i, item in enumerate(all_news_items, 1):
                    self.stdout.write(f'{i}. {item.title} ({item.source})')
                    self.stdout.write(f'   URL: {item.url}')
                    self.stdout.write(f'   难度: {item.difficulty_level}')
                    self.stdout.write(f'   发布时间: {item.published_at}')
                    self.stdout.write(f'   摘要: {item.summary[:100]}...')
                    self.stdout.write('')
            
            # 保存到数据库
            if not dry_run:
                self.stdout.write('正在保存到数据库...')
                
                # 分别保存传统爬虫和Fundus爬虫的结果
                saved_count = 0
                if crawler_type in ['traditional', 'both']:
                    traditional_items = [item for item in all_news_items if hasattr(item, 'source') and item.source in ['BBC', 'CNN', 'Reuters', 'TechCrunch', 'China Daily', 'Xinhua', 'Generated']]
                    if traditional_items:
                        saved_count += real_news_crawler_service.save_news_to_db(traditional_items)
                
                if crawler_type in ['fundus', 'both'] and FUNDUS_AVAILABLE:
                    fundus_items = [item for item in all_news_items if hasattr(item, 'source') and item.source in ['BBC', 'CNN', 'Reuters', 'TechCrunch', 'The Guardian', 'The New York Times', 'Wired', 'Ars Technica', 'Hacker News', 'Stack Overflow Blog']]
                    if fundus_items:
                        saved_count += fundus_crawler_service.save_news_to_db(fundus_items)
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'保存完成！新增 {saved_count} 条新闻，跳过 {len(all_news_items) - saved_count} 条重复新闻'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING('--dry-run 模式，未保存到数据库')
                )
            
        except Exception as e:
            logger.error(f'抓取新闻失败: {str(e)}')
            raise CommandError(f'抓取新闻失败: {str(e)}')
        
        self.stdout.write(
            self.style.SUCCESS('新闻抓取任务完成！')
        )
