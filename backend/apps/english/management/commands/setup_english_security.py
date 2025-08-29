"""
设置地道表达模块的安全配置
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.english.models import IdiomaticExpression, UserExpressionProgress


class Command(BaseCommand):
    help = '设置地道表达模块的用户组和权限'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='重置所有权限和组设置',
        )
    
    def handle(self, *args, **options):
        if options['reset']:
            self.reset_permissions()
        
        self.create_groups()
        self.assign_permissions()
        
        self.stdout.write(
            self.style.SUCCESS('地道表达安全配置完成')
        )
    
    def reset_permissions(self):
        """重置权限配置"""
        self.stdout.write('重置权限配置...')
        
        # 删除相关组
        groups_to_delete = ['内容管理员', '英语模块管理员']
        for group_name in groups_to_delete:
            try:
                group = Group.objects.get(name=group_name)
                group.delete()
                self.stdout.write(f'删除组: {group_name}')
            except Group.DoesNotExist:
                pass
    
    def create_groups(self):
        """创建用户组"""
        self.stdout.write('创建用户组...')
        
        # 内容管理员组
        content_manager_group, created = Group.objects.get_or_create(
            name='内容管理员'
        )
        if created:
            self.stdout.write('创建组: 内容管理员')
        
        # 英语模块管理员组
        english_admin_group, created = Group.objects.get_or_create(
            name='英语模块管理员'
        )
        if created:
            self.stdout.write('创建组: 英语模块管理员')
    
    def assign_permissions(self):
        """分配权限"""
        self.stdout.write('分配权限...')
        
        # 获取内容类型
        expression_ct = ContentType.objects.get_for_model(IdiomaticExpression)
        progress_ct = ContentType.objects.get_for_model(UserExpressionProgress)
        
        # 内容管理员权限
        content_manager_group = Group.objects.get(name='内容管理员')
        content_permissions = [
            'add_idiomaticexpression',
            'change_idiomaticexpression',
            'delete_idiomaticexpression',
            'view_idiomaticexpression',
        ]
        
        for perm_codename in content_permissions:
            try:
                permission = Permission.objects.get(
                    codename=perm_codename,
                    content_type=expression_ct
                )
                content_manager_group.permissions.add(permission)
                self.stdout.write(f'添加权限: {perm_codename} -> 内容管理员')
            except Permission.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'权限不存在: {perm_codename}')
                )
        
        # 英语模块管理员权限（所有权限）
        english_admin_group = Group.objects.get(name='英语模块管理员')
        all_permissions = Permission.objects.filter(
            content_type__in=[expression_ct, progress_ct]
        )
        
        for permission in all_permissions:
            english_admin_group.permissions.add(permission)
        
        self.stdout.write(f'为英语模块管理员添加了 {all_permissions.count()} 个权限')
        
        self.stdout.write(
            self.style.SUCCESS('权限分配完成')
        )
