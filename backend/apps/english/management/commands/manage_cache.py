# -*- coding: utf-8 -*-
"""
地道表达缓存管理命令
"""
from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache
from apps.english.cache_strategy import EnglishCacheManager, CachePreheater, CacheMonitor
import json


class Command(BaseCommand):
    help = '管理地道表达模块的缓存'

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            choices=['preheat', 'clear', 'stats', 'monitor'],
            help='要执行的缓存操作'
        )
        
        parser.add_argument(
            '--category',
            choices=['hot', 'random', 'all'],
            default='all',
            help='预热缓存的类别（仅用于preheat操作）'
        )

    def handle(self, *args, **options):
        action = options['action']
        
        try:
            if action == 'preheat':
                self._handle_preheat(options['category'])
            elif action == 'clear':
                self._handle_clear()
            elif action == 'stats':
                self._handle_stats()
            elif action == 'monitor':
                self._handle_monitor()
                
        except Exception as e:
            raise CommandError(f'缓存操作失败: {e}')

    def _handle_preheat(self, category):
        """处理缓存预热"""
        self.stdout.write(self.style.SUCCESS('开始缓存预热...'))
        
        if category == 'hot':
            CachePreheater.preheat_hot_expressions()
            self.stdout.write(self.style.SUCCESS('✓ 热门表达缓存预热完成'))
            
        elif category == 'random':
            CachePreheater.preheat_random_pools()
            self.stdout.write(self.style.SUCCESS('✓ 随机池缓存预热完成'))
            
        elif category == 'all':
            CachePreheater.preheat_all()
            self.stdout.write(self.style.SUCCESS('✓ 所有缓存预热完成'))

    def _handle_clear(self):
        """处理缓存清理"""
        self.stdout.write(self.style.WARNING('开始清理地道表达缓存...'))
        
        # 确认操作
        confirm = input('确认要清理所有地道表达缓存吗？(y/N): ')
        if confirm.lower() != 'y':
            self.stdout.write('操作已取消')
            return
        
        EnglishCacheManager.clear_all()
        self.stdout.write(self.style.SUCCESS('✓ 缓存清理完成'))

    def _handle_stats(self):
        """处理缓存统计"""
        self.stdout.write(self.style.SUCCESS('获取缓存统计信息...'))
        
        stats = EnglishCacheManager.get_cache_stats()
        
        if 'error' in stats:
            self.stdout.write(self.style.ERROR(f'获取统计失败: {stats["error"]}'))
            return
        
        self.stdout.write('\n=== 缓存统计信息 ===')
        
        # Redis基本信息
        if 'redis_version' in stats:
            self.stdout.write(f'Redis版本: {stats.get("redis_version", "N/A")}')
            self.stdout.write(f'内存使用: {stats.get("used_memory_human", "N/A")}')
            self.stdout.write(f'连接客户端: {stats.get("connected_clients", "N/A")}')
            self.stdout.write(f'命令处理总数: {stats.get("total_commands_processed", "N/A")}')
            
        # 缓存命中率
        hit_rate = stats.get('hit_rate', 0)
        if hit_rate > 80:
            style = self.style.SUCCESS
        elif hit_rate > 60:
            style = self.style.WARNING
        else:
            style = self.style.ERROR
            
        self.stdout.write(f'缓存命中率: {style(str(hit_rate) + "%")}')
        
        # 应用级统计
        if 'english_cache_keys' in stats:
            self.stdout.write(f'\n地道表达缓存键数量: {stats["english_cache_keys"]}')
            
            categories = stats.get('cache_categories', {})
            for category, count in categories.items():
                self.stdout.write(f'  - {category}: {count}')

    def _handle_monitor(self):
        """处理缓存监控"""
        self.stdout.write(self.style.SUCCESS('开始缓存性能监控...'))
        
        metrics = CacheMonitor.get_cache_metrics()
        
        # 记录监控日志
        CacheMonitor.log_cache_performance()
        
        # 输出关键指标
        self.stdout.write('\n=== 缓存性能指标 ===')
        self.stdout.write(json.dumps(metrics, indent=2, ensure_ascii=False))
        
        # 性能建议
        hit_rate = metrics.get('hit_rate', 0)
        if hit_rate < 60:
            self.stdout.write(
                self.style.WARNING(
                    '\n⚠️ 缓存命中率较低，建议：\n'
                    '  1. 检查缓存键设计是否合理\n'
                    '  2. 考虑增加缓存超时时间\n'
                    '  3. 分析缓存失效模式'
                )
            )
        elif hit_rate > 90:
            self.stdout.write(
                self.style.SUCCESS(
                    '\n✓ 缓存命中率优秀！系统性能良好'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    '\n✓ 缓存命中率良好'
                )
            )
