from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = '检查用户和权限组的权限配置'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='检查特定用户的权限',
        )
        parser.add_argument(
            '--group',
            type=str,
            help='检查特定权限组的权限',
        )

    def handle(self, *args, **options):
        username = options.get('username')
        group_name = options.get('group')
        
        if username:
            self._check_user_permissions(username)
        elif group_name:
            self._check_group_permissions(group_name)
        else:
            self._check_all_permissions()

    def _check_user_permissions(self, username):
        """检查特定用户的权限"""
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'用户不存在: {username}'))
            return

        self.stdout.write(f'\n=== 用户权限检查: {username} ===')
        self.stdout.write(f'超级用户: {user.is_superuser}')
        self.stdout.write(f'管理员: {user.is_staff}')
        self.stdout.write(f'激活状态: {user.is_active}')
        
        # 显示用户所属的组
        groups = user.groups.all()
        self.stdout.write(f'\n所属权限组 ({groups.count()}):')
        for group in groups:
            self.stdout.write(f'  - {group.name}')
        
        # 显示用户的直接权限
        user_permissions = user.user_permissions.all()
        self.stdout.write(f'\n直接权限 ({user_permissions.count()}):')
        for perm in user_permissions:
            self.stdout.write(f'  - {perm.content_type.app_label}.{perm.codename}: {perm.name}')
        
        # 显示用户的所有权限（包括通过组获得的）
        all_permissions = user.get_all_permissions()
        self.stdout.write(f'\n所有权限 ({len(all_permissions)}):')
        for perm in sorted(all_permissions):
            self.stdout.write(f'  - {perm}')

    def _check_group_permissions(self, group_name):
        """检查特定权限组的权限"""
        try:
            group = Group.objects.get(name=group_name)
        except Group.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'权限组不存在: {group_name}'))
            return

        self.stdout.write(f'\n=== 权限组检查: {group_name} ===')
        
        # 显示组成员
        users = group.user_set.all()
        self.stdout.write(f'组成员 ({users.count()}):')
        for user in users:
            self.stdout.write(f'  - {user.username} (管理员: {user.is_staff}, 超级用户: {user.is_superuser})')
        
        # 显示组权限
        permissions = group.permissions.all()
        self.stdout.write(f'\n组权限 ({permissions.count()}):')
        
        # 按应用分组显示权限
        apps = {}
        for perm in permissions:
            app_label = perm.content_type.app_label
            if app_label not in apps:
                apps[app_label] = []
            apps[app_label].append(perm)
        
        for app_label, perms in apps.items():
            self.stdout.write(f'\n  {app_label.upper()}:')
            for perm in perms:
                self.stdout.write(f'    - {perm.codename}: {perm.name}')

    def _check_all_permissions(self):
        """检查所有权限配置"""
        self.stdout.write('\n=== 系统权限概览 ===')
        
        # 显示所有权限组
        groups = Group.objects.all()
        self.stdout.write(f'\n权限组总数: {groups.count()}')
        for group in groups:
            self.stdout.write(f'  - {group.name}: {group.permissions.count()} 个权限, {group.user_set.count()} 个成员')
        
        # 显示超级用户
        superusers = User.objects.filter(is_superuser=True)
        self.stdout.write(f'\n超级用户 ({superusers.count()}):')
        for user in superusers:
            self.stdout.write(f'  - {user.username}')
        
        # 显示管理员
        staff_users = User.objects.filter(is_staff=True, is_superuser=False)
        self.stdout.write(f'\n管理员 ({staff_users.count()}):')
        for user in staff_users:
            groups_str = ', '.join([g.name for g in user.groups.all()])
            self.stdout.write(f'  - {user.username} (组: {groups_str})')
        
        # 显示所有权限
        all_permissions = Permission.objects.all().order_by('content_type__app_label', 'codename')
        self.stdout.write(f'\n系统权限总数: {all_permissions.count()}')
        
        apps = {}
        for perm in all_permissions:
            app_label = perm.content_type.app_label
            if app_label not in apps:
                apps[app_label] = []
            apps[app_label].append(perm)
        
        for app_label, perms in apps.items():
            self.stdout.write(f'\n  {app_label.upper()} ({len(perms)} 个权限):')
            for perm in perms:
                self.stdout.write(f'    - {perm.codename}: {perm.name}')

