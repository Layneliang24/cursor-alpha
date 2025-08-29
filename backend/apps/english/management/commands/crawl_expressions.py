"""
地道表达爬取管理命令
支持同步和异步两种模式
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '爬取地道表达'

    def add_arguments(self, parser):
        parser.add_argument(
            '--sources',
            type=str,
            nargs='*',
            default=None,
            help='数据源列表，如 cambridge collins reddit。不指定则使用所有可用源'
        )
        
        parser.add_argument(
            '--max-items',
            type=int,
            default=50,
            help='每个源的最大抓取数量 (默认: 50)'
        )
        
        parser.add_argument(
            '--quality-threshold',
            type=float,
            default=0.6,
            help='质量阈值 (0.0-1.0, 默认: 0.6)'
        )
        
        parser.add_argument(
            '--async',
            action='store_true',
            help='使用异步任务执行（需要Celery）'
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
        sources = options['sources']
        max_items = options['max_items']
        quality_threshold = options['quality_threshold']
        use_async = options['async']
        dry_run = options['dry_run']
        verbose = options['verbose']
        
        if verbose:
            logging.basicConfig(level=logging.INFO)
        
        # 验证质量阈值
        if not 0.0 <= quality_threshold <= 1.0:
            raise CommandError('质量阈值必须在 0.0 到 1.0 之间')
        
        self.stdout.write(
            self.style.SUCCESS(f'开始爬取地道表达...')
        )
        
        if sources:
            self.stdout.write(f'目标数据源: {", ".join(sources)}')
        else:
            self.stdout.write('使用所有可用数据源')
        
        self.stdout.write(f'每源最大数量: {max_items}')
        self.stdout.write(f'质量阈值: {quality_threshold}')
        self.stdout.write(f'执行模式: {"异步" if use_async else "同步"}')
        
        try:
            if use_async:
                result = self._run_async_task(sources, max_items, quality_threshold, verbose)
            else:
                result = self._run_sync_task(sources, max_items, quality_threshold, dry_run, verbose)
                
        except Exception as e:
            logger.error(f'爬取地道表达失败: {str(e)}')
            raise CommandError(f'爬取地道表达失败: {str(e)}')
        
        self.stdout.write(
            self.style.SUCCESS('地道表达爬取任务完成！')
        )

    def _run_async_task(self, sources, max_items, quality_threshold, verbose):
        """运行异步任务"""
        try:
            from ..tasks import crawl_expressions_task
            
            # 提交异步任务
            task = crawl_expressions_task.delay(
                sources=sources,
                max_items_per_source=max_items,
                quality_threshold=quality_threshold
            )
            
            self.stdout.write(f'异步任务已提交: {task.id}')
            
            if verbose:
                self.stdout.write('监控任务状态...')
                
                # 等待任务完成并显示进度
                while not task.ready():
                    try:
                        result = task.result
                        if isinstance(result, dict) and 'current' in result:
                            progress = result.get('percentage', 0)
                            description = result.get('description', '')
                            self.stdout.write(f'进度: {progress}% - {description}', ending='\r')
                    except:
                        pass
                    
                    import time
                    time.sleep(2)
                
                # 显示最终结果
                result = task.result
                if isinstance(result, dict):
                    if result.get('status') == 'success':
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'\n任务完成！抓取: {result.get("total_crawled", 0)}, '
                                f'通过质量检查: {result.get("total_accepted", 0)}, '
                                f'保存: {result.get("total_saved", 0)}'
                            )
                        )
                        
                        if 'sources' in result:
                            for source, stats in result['sources'].items():
                                if 'error' in stats:
                                    self.stdout.write(f'  {source}: 失败 - {stats["error"]}')
                                else:
                                    self.stdout.write(
                                        f'  {source}: {stats["accepted"]}/{stats["total_crawled"]} 通过'
                                    )
                    else:
                        self.stdout.write(
                            self.style.ERROR(f'\n任务失败: {result.get("error", "未知错误")}')
                        )
            else:
                self.stdout.write('任务在后台运行中...')
                self.stdout.write(f'使用以下命令查看状态: celery -A backend.celery_config inspect active')
            
            return task.result
            
        except ImportError:
            raise CommandError('Celery未安装或配置不正确，无法使用异步模式')

    def _run_sync_task(self, sources, max_items, quality_threshold, dry_run, verbose):
        """运行同步任务"""
        from ..expression_crawler import ExpressionCrawlerService
        from ..specialized_crawlers import register_specialized_crawlers
        from ..data_quality import data_processor
        
        start_time = timezone.now()
        
        # 初始化爬虫服务
        crawler_service = ExpressionCrawlerService()
        register_specialized_crawlers(crawler_service)
        
        # 获取可用的爬虫
        available_crawlers = list(crawler_service.crawlers.keys())
        target_sources = sources or available_crawlers
        
        # 过滤不存在的源
        valid_sources = [s for s in target_sources if s in available_crawlers]
        if not valid_sources:
            raise CommandError(f"没有找到有效的数据源: {target_sources}")
        
        self.stdout.write(f'有效数据源: {", ".join(valid_sources)}')
        
        all_items = []
        source_results = {}
        
        for source in valid_sources:
            try:
                self.stdout.write(f'正在爬取 {source}...')
                
                crawler = crawler_service.crawlers[source]
                
                # 爬取数据
                items = crawler.crawl_expressions(max_items=max_items)
                
                # 数据质量处理
                processing_results = data_processor.process_expression_items(items, quality_threshold)
                
                accepted_items = processing_results['accepted']
                all_items.extend(accepted_items)
                
                source_results[source] = {
                    'total_crawled': len(items),
                    'accepted': len(accepted_items),
                    'rejected_quality': len(processing_results['rejected_quality']),
                    'rejected_duplicate': len(processing_results['rejected_duplicate']),
                    'rejected_invalid': len(processing_results['rejected_invalid'])
                }
                
                self.stdout.write(
                    f'  {source}: {len(accepted_items)}/{len(items)} 通过质量检查'
                )
                
                if verbose and accepted_items:
                    for i, item in enumerate(accepted_items[:5], 1):  # 显示前5个
                        self.stdout.write(f'    {i}. {item.expression} - {item.meaning[:50]}...')
                    if len(accepted_items) > 5:
                        self.stdout.write(f'    ... 还有 {len(accepted_items) - 5} 个')
                
            except Exception as e:
                logger.error(f"爬取 {source} 失败: {str(e)}")
                source_results[source] = {
                    'error': str(e),
                    'total_crawled': 0,
                    'accepted': 0
                }
                self.stdout.write(f'  {source}: 失败 - {str(e)}')
        
        end_time = timezone.now()
        duration = (end_time - start_time).total_seconds()
        
        if not all_items:
            self.stdout.write(
                self.style.WARNING('未抓取到任何符合质量要求的表达式')
            )
            return
        
        self.stdout.write(
            self.style.SUCCESS(f'抓取完成！共找到 {len(all_items)} 个高质量表达式 (耗时 {duration:.2f}秒)')
        )
        
        # 保存到数据库
        saved_count = 0
        if not dry_run:
            self.stdout.write('正在保存到数据库...')
            saved_count = crawler_service.save_expressions_to_db(all_items)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'保存完成！新增 {saved_count} 条表达式，跳过 {len(all_items) - saved_count} 条重复'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING('--dry-run 模式，未保存到数据库')
            )
        
        # 显示详细统计
        if verbose:
            self.stdout.write('\n=== 详细统计 ===')
            for source, stats in source_results.items():
                if 'error' in stats:
                    self.stdout.write(f'{source}: 失败 - {stats["error"]}')
                else:
                    self.stdout.write(
                        f'{source}: 抓取 {stats["total_crawled"]}, '
                        f'通过 {stats["accepted"]}, '
                        f'质量拒绝 {stats["rejected_quality"]}, '
                        f'重复拒绝 {stats["rejected_duplicate"]}, '
                        f'无效拒绝 {stats["rejected_invalid"]}'
                    )
        
        # 生成质量报告
        quality_report = data_processor.generate_quality_report({
            'accepted': all_items,
            'rejected_quality': [],
            'rejected_duplicate': [],
            'rejected_invalid': []
        })
        
        if verbose and 'avg_quality_score' in quality_report:
            self.stdout.write(f'平均质量评分: {quality_report["avg_quality_score"]:.3f}')
        
        return {
            'total_crawled': sum(r.get('total_crawled', 0) for r in source_results.values()),
            'total_accepted': len(all_items),
            'total_saved': saved_count,
            'sources': source_results,
            'quality_report': quality_report
        }
