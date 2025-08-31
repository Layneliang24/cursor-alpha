"""
API密钥轮换管理命令

用于管理API密钥的生命周期，包括轮换、备份、恢复等功能
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from apps.ai.config_models import APIKey, AIProvider

User = get_user_model()
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """API密钥轮换管理命令"""
    
    help = 'Manage API key rotation, backup, and lifecycle'
    
    def add_arguments(self, parser):
        """添加命令参数"""
        parser.add_argument(
            '--action',
            type=str,
            choices=['rotate', 'backup', 'restore', 'list', 'validate'],
            default='list',
            help='操作类型 (默认: list)'
        )
        
        parser.add_argument(
            '--key-id',
            type=str,
            help='特定密钥ID（用于单个密钥操作）'
        )
        
        parser.add_argument(
            '--provider',
            type=str,
            help='提供商名称（用于批量操作）'
        )
        
        parser.add_argument(
            '--user',
            type=str,
            help='用户名（用于用户特定操作）'
        )
        
        parser.add_argument(
            '--new-key',
            type=str,
            help='新的API密钥（用于轮换操作）'
        )
        
        parser.add_argument(
            '--backup-file',
            type=str,
            help='备份文件路径'
        )
        
        parser.add_argument(
            '--expires-days',
            type=int,
            default=90,
            help='新密钥过期天数 (默认: 90天)'
        )
        
        parser.add_argument(
            '--force',
            action='store_true',
            help='强制执行操作，跳过确认'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='模拟运行，不实际执行操作'
        )
    
    def handle(self, *args, **options):
        """处理命令"""
        action = options['action']
        
        try:
            if action == 'list':
                self.list_keys(options)
            elif action == 'rotate':
                self.rotate_keys(options)
            elif action == 'backup':
                self.backup_keys(options)
            elif action == 'restore':
                self.restore_keys(options)
            elif action == 'validate':
                self.validate_keys(options)
            else:
                raise CommandError(f'未知操作: {action}')
                
        except Exception as e:
            logger.error(f'密钥管理操作失败: {e}')
            raise CommandError(f'操作失败: {e}')
    
    def list_keys(self, options):
        """列出API密钥"""
        self.stdout.write(self.style.SUCCESS('📋 API密钥列表'))
        self.stdout.write('=' * 80)
        
        # 构建查询
        queryset = APIKey.objects.select_related('provider', 'user')
        
        if options.get('provider'):
            queryset = queryset.filter(provider__name=options['provider'])
        
        if options.get('user'):
            queryset = queryset.filter(user__username=options['user'])
        
        # 显示密钥信息
        for key in queryset:
            status_icon = '🟢' if key.is_active else '🔴'
            default_icon = '⭐' if key.is_default else '  '
            expired_icon = '⚠️' if key.is_expired() else '  '
            
            self.stdout.write(
                f'{status_icon}{default_icon}{expired_icon} '
                f'{key.name:<20} | {key.provider.display_name:<15} | '
                f'{key.masked_key:<20} | {key.user.username:<10} | '
                f'创建: {key.created_at.strftime("%Y-%m-%d")}'
            )
        
        self.stdout.write(f'\n总计: {queryset.count()} 个密钥')
    
    def rotate_keys(self, options):
        """轮换API密钥"""
        key_id = options.get('key_id')
        new_key = options.get('new_key')
        
        if not key_id:
            raise CommandError('密钥轮换需要指定 --key-id')
        
        if not new_key:
            raise CommandError('密钥轮换需要提供 --new-key')
        
        try:
            # 获取要轮换的密钥
            api_key = APIKey.objects.get(key_id=key_id)
        except APIKey.DoesNotExist:
            raise CommandError(f'未找到密钥: {key_id}')
        
        # 确认操作
        if not options.get('force') and not options.get('dry_run'):
            confirm = input(f'确认轮换密钥 "{api_key.name}" (y/N): ')
            if confirm.lower() != 'y':
                self.stdout.write('操作已取消')
                return
        
        if options.get('dry_run'):
            self.stdout.write(self.style.WARNING('🔄 模拟轮换密钥:'))
            self.stdout.write(f'  密钥: {api_key.name}')
            self.stdout.write(f'  提供商: {api_key.provider.display_name}')
            self.stdout.write(f'  当前掩码: {api_key.masked_key}')
            self.stdout.write(f'  新密钥长度: {len(new_key)}')
            return
        
        # 执行轮换
        with transaction.atomic():
            # 备份旧密钥信息
            old_masked = api_key.masked_key
            
            # 设置新密钥
            api_key.set_key(new_key)
            
            # 更新过期时间
            if options.get('expires_days'):
                api_key.expires_at = timezone.now() + timedelta(days=options['expires_days'])
            
            # 更新最后使用时间
            api_key.updated_at = timezone.now()
            api_key.save()
            
            # 记录操作日志
            self._log_rotation(api_key, old_masked, options)
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ 密钥轮换成功: {api_key.name}')
            )
            self.stdout.write(f'  旧掩码: {old_masked}')
            self.stdout.write(f'  新掩码: {api_key.masked_key}')
    
    def backup_keys(self, options):
        """备份API密钥"""
        backup_file = options.get('backup_file', f'api_keys_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        
        # 构建查询
        queryset = APIKey.objects.select_related('provider', 'user')
        
        if options.get('provider'):
            queryset = queryset.filter(provider__name=options['provider'])
        
        if options.get('user'):
            queryset = queryset.filter(user__username=options['user'])
        
        # 准备备份数据（不包含实际密钥）
        backup_data = {
            'backup_time': timezone.now().isoformat(),
            'total_keys': queryset.count(),
            'keys': []
        }
        
        for key in queryset:
            key_data = {
                'key_id': key.key_id,
                'name': key.name,
                'provider_name': key.provider.name,
                'user_name': key.user.username,
                'masked_key': key.masked_key,
                'is_active': key.is_active,
                'is_default': key.is_default,
                'usage_limit_daily': key.usage_limit_daily,
                'usage_limit_monthly': key.usage_limit_monthly,
                'created_at': key.created_at.isoformat(),
                'expires_at': key.expires_at.isoformat() if key.expires_at else None,
            }
            backup_data['keys'].append(key_data)
        
        # 写入备份文件
        if not options.get('dry_run'):
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ 备份完成: {backup_file}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'🔄 模拟备份到: {backup_file}')
            )
        
        self.stdout.write(f'备份密钥数量: {backup_data["total_keys"]}')
    
    def restore_keys(self, options):
        """恢复API密钥（仅恢复元数据，不包含实际密钥）"""
        backup_file = options.get('backup_file')
        
        if not backup_file:
            raise CommandError('恢复操作需要指定 --backup-file')
        
        try:
            with open(backup_file, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
        except FileNotFoundError:
            raise CommandError(f'备份文件不存在: {backup_file}')
        except json.JSONDecodeError:
            raise CommandError(f'备份文件格式错误: {backup_file}')
        
        self.stdout.write(f'📁 备份文件: {backup_file}')
        self.stdout.write(f'📅 备份时间: {backup_data.get("backup_time")}')
        self.stdout.write(f'📊 密钥数量: {backup_data.get("total_keys")}')
        
        if not options.get('force') and not options.get('dry_run'):
            confirm = input('确认恢复密钥元数据 (实际密钥需要手动设置) (y/N): ')
            if confirm.lower() != 'y':
                self.stdout.write('操作已取消')
                return
        
        restored_count = 0
        skipped_count = 0
        
        for key_data in backup_data.get('keys', []):
            try:
                # 检查密钥是否已存在
                if APIKey.objects.filter(key_id=key_data['key_id']).exists():
                    skipped_count += 1
                    continue
                
                if options.get('dry_run'):
                    self.stdout.write(f'🔄 模拟恢复: {key_data["name"]}')
                    continue
                
                # 获取提供商和用户
                provider = AIProvider.objects.get(name=key_data['provider_name'])
                user = User.objects.get(username=key_data['user_name'])
                
                # 创建密钥对象（不设置实际密钥）
                api_key = APIKey.objects.create(
                    key_id=key_data['key_id'],
                    name=key_data['name'],
                    provider=provider,
                    user=user,
                    is_active=False,  # 恢复后默认禁用，需要手动设置密钥
                    is_default=key_data['is_default'],
                    usage_limit_daily=key_data.get('usage_limit_daily'),
                    usage_limit_monthly=key_data.get('usage_limit_monthly'),
                    expires_at=datetime.fromisoformat(key_data['expires_at']) if key_data.get('expires_at') else None
                )
                
                restored_count += 1
                self.stdout.write(f'✅ 恢复: {api_key.name}')
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ 恢复失败 {key_data.get("name", "unknown")}: {e}')
                )
        
        self.stdout.write(f'\n📊 恢复结果: {restored_count} 成功, {skipped_count} 跳过')
        if restored_count > 0:
            self.stdout.write(
                self.style.WARNING('⚠️ 请手动为恢复的密钥设置实际API密钥值')
            )
    
    def validate_keys(self, options):
        """验证API密钥"""
        self.stdout.write(self.style.SUCCESS('🔍 API密钥验证'))
        self.stdout.write('=' * 80)
        
        # 构建查询
        queryset = APIKey.objects.select_related('provider', 'user')
        
        if options.get('provider'):
            queryset = queryset.filter(provider__name=options['provider'])
        
        if options.get('user'):
            queryset = queryset.filter(user__username=options['user'])
        
        valid_count = 0
        invalid_count = 0
        expired_count = 0
        
        for key in queryset:
            is_valid = key.validate_key()
            is_expired = key.is_expired()
            
            # 状态图标
            if is_expired:
                status_icon = '⚠️ 过期'
                expired_count += 1
            elif is_valid:
                status_icon = '✅ 有效'
                valid_count += 1
            else:
                status_icon = '❌ 无效'
                invalid_count += 1
            
            self.stdout.write(
                f'{status_icon} {key.name:<20} | {key.provider.display_name:<15} | '
                f'{key.masked_key:<20} | {key.user.username:<10}'
            )
        
        # 统计信息
        self.stdout.write('\n📊 验证统计:')
        self.stdout.write(f'  ✅ 有效: {valid_count}')
        self.stdout.write(f'  ❌ 无效: {invalid_count}')
        self.stdout.write(f'  ⚠️ 过期: {expired_count}')
        self.stdout.write(f'  📊 总计: {valid_count + invalid_count + expired_count}')
    
    def _log_rotation(self, api_key: APIKey, old_masked: str, options: Dict[str, Any]):
        """记录轮换操作日志"""
        log_data = {
            'action': 'api_key_rotation',
            'key_id': api_key.key_id,
            'key_name': api_key.name,
            'provider': api_key.provider.name,
            'user': api_key.user.username,
            'old_masked_key': old_masked,
            'new_masked_key': api_key.masked_key,
            'rotation_time': timezone.now().isoformat(),
            'expires_at': api_key.expires_at.isoformat() if api_key.expires_at else None,
            'operator': 'system',  # 可以扩展为实际操作员
        }
        
        logger.info(f'API密钥轮换: {json.dumps(log_data, ensure_ascii=False)}')
        
        # 可以扩展为写入专门的审计日志文件
        audit_log_file = f'logs/api_key_rotations_{datetime.now().strftime("%Y%m")}.log'
        try:
            import os
            os.makedirs('logs', exist_ok=True)
            with open(audit_log_file, 'a', encoding='utf-8') as f:
                f.write(f'{timezone.now().isoformat()}: {json.dumps(log_data, ensure_ascii=False)}\n')
        except Exception as e:
            logger.warning(f'写入审计日志失败: {e}')
    
    def _get_user_input(self, prompt: str, default: str = '') -> str:
        """获取用户输入"""
        try:
            value = input(f'{prompt} [{default}]: ').strip()
            return value if value else default
        except KeyboardInterrupt:
            self.stdout.write('\n操作已取消')
            raise CommandError('用户取消操作')
    
    def _confirm_operation(self, message: str) -> bool:
        """确认操作"""
        try:
            confirm = input(f'{message} (y/N): ').strip().lower()
            return confirm == 'y'
        except KeyboardInterrupt:
            self.stdout.write('\n操作已取消')
            return False
