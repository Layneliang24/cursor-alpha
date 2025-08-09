from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = '设置Alpha平台的权限组和权限'

    def handle(self, *args, **options):
        self.stdout.write('开始设置权限组...')
        
        # 创建管理员组
        admin_group, created = Group.objects.get_or_create(name='管理员')
        if created:
            self.stdout.write(self.style.SUCCESS('创建管理员组'))
        else:
            self.stdout.write('管理员组已存在')
            
        # 管理员组权限
        admin_permissions = [
            # 文章权限
            'articles.view_article',
            'articles.add_article',
            'articles.change_article',
            'articles.delete_article',
            
            # 分类权限
            'categories.view_category',
            'categories.add_category',
            'categories.change_category',
            'categories.delete_category',
            
            # 标签权限
            'categories.view_tag',
            'categories.add_tag',
            'categories.change_tag',
            'categories.delete_tag',
            
            # 评论权限
            'articles.view_comment',
            'articles.add_comment',
            'articles.change_comment',
            'articles.delete_comment',
            
            # 用户权限
            'users.view_user',
            'users.add_user',
            'users.change_user',
            'users.delete_user',
            
            # 用户资料权限
            'users.view_userprofile',
            'users.add_userprofile',
            'users.change_userprofile',
            'users.delete_userprofile',
        ]
        
        self._assign_permissions_to_group(admin_group, admin_permissions)
        
        # 创建内容编辑组
        editor_group, created = Group.objects.get_or_create(name='内容编辑')
        if created:
            self.stdout.write(self.style.SUCCESS('创建内容编辑组'))
        else:
            self.stdout.write('内容编辑组已存在')
            
        # 内容编辑组权限
        editor_permissions = [
            # 文章权限
            'articles.view_article',
            'articles.add_article',
            'articles.change_article',
            
            # 标签权限
            'categories.view_tag',
            'categories.add_tag',
            'categories.change_tag',
            
            # 评论权限
            'articles.view_comment',
            'articles.add_comment',
            'articles.change_comment',
        ]
        
        self._assign_permissions_to_group(editor_group, editor_permissions)
        
        # 创建分类管理组
        category_manager_group, created = Group.objects.get_or_create(name='分类管理员')
        if created:
            self.stdout.write(self.style.SUCCESS('创建分类管理员组'))
        else:
            self.stdout.write('分类管理员组已存在')
            
        # 分类管理组权限
        category_permissions = [
            # 分类权限
            'categories.view_category',
            'categories.add_category',
            'categories.change_category',
            'categories.delete_category',
            
            # 标签权限
            'categories.view_tag',
            'categories.add_tag',
            'categories.change_tag',
            'categories.delete_tag',
        ]
        
        self._assign_permissions_to_group(category_manager_group, category_permissions)
        
        self.stdout.write(self.style.SUCCESS('权限组设置完成！'))
        
        # 显示权限组信息
        self._display_group_info()
    
    def _assign_permissions_to_group(self, group, permission_codenames):
        """为权限组分配权限"""
        permissions = []
        for codename in permission_codenames:
            try:
                app_label, perm_codename = codename.split('.')
                permission = Permission.objects.get(
                    content_type__app_label=app_label,
                    codename=perm_codename
                )
                permissions.append(permission)
            except Permission.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'权限不存在: {codename}')
                )
            except ValueError:
                self.stdout.write(
                    self.style.ERROR(f'权限格式错误: {codename}')
                )
        
        group.permissions.set(permissions)
        self.stdout.write(f'为 {group.name} 组分配了 {len(permissions)} 个权限')
    
    def _display_group_info(self):
        """显示权限组信息"""
        self.stdout.write('\n=== 权限组信息 ===')
        for group in Group.objects.all():
            self.stdout.write(f'\n组名: {group.name}')
            self.stdout.write(f'权限数量: {group.permissions.count()}')
            self.stdout.write('权限列表:')
            for perm in group.permissions.all():
                self.stdout.write(f'  - {perm.content_type.app_label}.{perm.codename}: {perm.name}')

