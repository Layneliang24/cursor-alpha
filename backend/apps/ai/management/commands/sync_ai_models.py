"""
Django管理命令：同步AI模型
用于从各提供商API获取最新模型列表并同步到数据库
"""

import asyncio
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from ...services.model_discovery_sync import sync_model_discovery_service


class Command(BaseCommand):
    """同步AI模型管理命令"""
    
    help = '从AI提供商API获取最新模型列表并同步到数据库'
    
    def add_arguments(self, parser):
        """添加命令参数"""
        parser.add_argument(
            '--force-refresh',
            action='store_true',
            help='强制刷新缓存，重新从API获取模型列表'
        )
        
        parser.add_argument(
            '--provider',
            type=str,
            help='只同步指定提供商的模型（例如：openai, anthropic, google）'
        )
        
        parser.add_argument(
            '--clear-cache',
            action='store_true',
            help='清除模型发现缓存'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='仅显示将要同步的模型，不实际写入数据库'
        )
    
    def handle(self, *args, **options):
        """执行命令"""
        try:
            if options['clear_cache']:
                self._clear_cache(options.get('provider'))
                return
            
            if options['dry_run']:
                self._dry_run(options)
                return
            
            # 执行同步
            self._sync_models(options)
            
        except Exception as e:
            raise CommandError(f'同步模型失败: {e}')
        finally:
            # 清理资源 (同步版本不需要清理异步资源)
            pass
    
    def _clear_cache(self, provider_type=None):
        """清除缓存"""
        self.stdout.write(
            self.style.WARNING('正在清除模型发现缓存...')
        )
        
        sync_model_discovery_service.clear_cache_sync(provider_type)
        
        if provider_type:
            self.stdout.write(
                self.style.SUCCESS(f'已清除 {provider_type} 提供商的缓存')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('已清除所有模型发现缓存')
            )
    
    def _dry_run(self, options):
        """试运行模式"""
        self.stdout.write(
            self.style.WARNING('试运行模式：仅显示将要同步的模型，不写入数据库')
        )
        
        force_refresh = options.get('force_refresh', False)
        provider_filter = options.get('provider')
        
        # 获取模型列表
        all_models = sync_model_discovery_service.get_all_models_sync(force_refresh=force_refresh)
        
        # 过滤特定提供商
        if provider_filter:
            filtered_models = {
                k: v for k, v in all_models.items() 
                if k == provider_filter
            }
            all_models = filtered_models
        
        total_models = 0
        
        for provider_type, models in all_models.items():
            self.stdout.write(
                self.style.HTTP_INFO(f'\n=== {provider_type.upper()} 提供商 ===')
            )
            
            if not models:
                self.stdout.write(
                    self.style.WARNING('  未找到模型')
                )
                continue
            
            for model in models:
                self.stdout.write(f'  • {model.display_name} ({model.id})')
                self.stdout.write(f'    描述: {model.description[:100]}...')
                self.stdout.write(f'    最大Token: {model.max_tokens}')
                self.stdout.write(f'    推荐: {"是" if model.is_recommended else "否"}')
                
                if model.cost_per_1k_input > 0:
                    self.stdout.write(
                        f'    成本: ${model.cost_per_1k_input:.3f}/${model.cost_per_1k_output:.3f} per 1K tokens'
                    )
                
                self.stdout.write('')
            
            total_models += len(models)
            
            self.stdout.write(
                self.style.SUCCESS(f'  小计: {len(models)} 个模型')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n总计: {total_models} 个模型将被同步')
        )
    
    def _sync_models(self, options):
        """同步模型"""
        force_refresh = options.get('force_refresh', False)
        
        self.stdout.write(
            self.style.WARNING('开始同步AI模型到数据库...')
        )
        
        if force_refresh:
            self.stdout.write('使用强制刷新模式')
        
        start_time = timezone.now()
        
        # 执行同步
        stats = sync_model_discovery_service.sync_models_to_database_sync(force_refresh=force_refresh)
        
        end_time = timezone.now()
        duration = (end_time - start_time).total_seconds()
        
        # 显示结果
        self.stdout.write(
            self.style.SUCCESS('\n=== 同步完成 ===')
        )
        self.stdout.write(f'创建模型: {stats["created"]}')
        self.stdout.write(f'更新模型: {stats["updated"]}')
        self.stdout.write(f'跳过模型: {stats["skipped"]}')
        self.stdout.write(f'错误数量: {stats["errors"]}')
        self.stdout.write(f'耗时: {duration:.2f} 秒')
        
        if stats['errors'] > 0:
            self.stdout.write(
                self.style.WARNING(f'存在 {stats["errors"]} 个错误，请查看日志')
            )
        
        # 显示数据库统计
        self._show_database_stats()
    
    def _show_database_stats(self):
        """显示数据库统计信息"""
        from ...config_models import AIModel, AIProvider
        
        self.stdout.write(
            self.style.HTTP_INFO('\n=== 数据库统计 ===')
        )
        
        total_models = AIModel.objects.filter(is_active=True).count()
        recommended_models = AIModel.objects.filter(
            is_active=True, 
            is_recommended=True
        ).count()
        
        self.stdout.write(f'活跃模型总数: {total_models}')
        self.stdout.write(f'推荐模型数量: {recommended_models}')
        
        # 按提供商统计
        providers = AIProvider.objects.filter(is_active=True)
        for provider in providers:
            model_count = AIModel.objects.filter(
                provider=provider,
                is_active=True
            ).count()
            
            if model_count > 0:
                self.stdout.write(f'{provider.display_name}: {model_count} 个模型')
    
    def _validate_provider(self, provider_type):
        """验证提供商类型"""
        from ...adapters.base import AIProviderType
        
        try:
            AIProviderType(provider_type)
            return True
        except ValueError:
            available_providers = [p.value for p in AIProviderType]
            raise CommandError(
                f'不支持的提供商类型: {provider_type}\n'
                f'可用的提供商: {", ".join(available_providers)}'
            )
