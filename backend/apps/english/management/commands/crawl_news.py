"""
手动抓取英语新闻的管理命令
用于测试和维护新闻抓取功能
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from apps.english.news_crawler import news_crawler_service
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '抓取英语新闻'

    def add_arguments(self, parser):
        parser.add_argument(
            '--source',
            type=str,
            default='bbc',
            choices=['bbc', 'cnn', 'reuters', 'all'],
            help='新闻源 (默认: bbc)'
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
        dry_run = options['dry_run']
        verbose = options['verbose']
        
        if verbose:
            logging.basicConfig(level=logging.INFO)
        
        self.stdout.write(
            self.style.SUCCESS(f'开始抓取 {source} 新闻...')
        )
        
        try:
            # 抓取新闻
            start_time = timezone.now()
            
            if source == 'all':
                news_items = news_crawler_service.crawl_all_sources()
            else:
                news_items = news_crawler_service.crawl_news(source)
            
            end_time = timezone.now()
            duration = (end_time - start_time).total_seconds()
            
            if not news_items:
                self.stdout.write(
                    self.style.WARNING(f'未抓取到任何 {source} 新闻')
                )
                return
            
            self.stdout.write(
                self.style.SUCCESS(f'抓取完成！共找到 {len(news_items)} 条新闻 (耗时 {duration:.2f}秒)')
            )
            
            # 显示新闻列表
            if verbose:
                for i, item in enumerate(news_items, 1):
                    self.stdout.write(f'{i}. {item.title} ({item.source})')
                    self.stdout.write(f'   URL: {item.url}')
                    self.stdout.write(f'   难度: {item.difficulty_level}')
                    self.stdout.write(f'   发布时间: {item.published_at}')
                    self.stdout.write(f'   摘要: {item.summary[:100]}...')
                    self.stdout.write('')
            
            # 保存到数据库
            if not dry_run:
                self.stdout.write('正在保存到数据库...')
                saved_count = news_crawler_service.save_news_to_db(news_items)
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'保存完成！新增 {saved_count} 条新闻，跳过 {len(news_items) - saved_count} 条重复新闻'
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
