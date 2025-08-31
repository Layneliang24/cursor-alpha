from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.rbac.models import Permission, Role, UserRole

User = get_user_model()


class Command(BaseCommand):
    help = '初始化RBAC系统的默认角色和权限'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='强制重新创建所有角色和权限',
        )

    def handle(self, *args, **options):
        force = options['force']
        
        self.stdout.write(self.style.SUCCESS('开始初始化RBAC系统...'))
        
        # 创建默认权限
        self.create_permissions(force)
        
        # 创建默认角色
        self.create_roles(force)
        
        # 分配默认权限给角色
        self.assign_permissions_to_roles()
        
        # 为超级用户分配超级管理员角色
        self.assign_superuser_roles()
        
        self.stdout.write(self.style.SUCCESS('RBAC系统初始化完成！'))

    def create_permissions(self, force):
        """创建默认权限"""
        self.stdout.write('创建默认权限...')
        
        permissions_data = [
            # 用户管理权限
            {'codename': 'user.view', 'name': '查看用户', 'resource': 'user', 'action': 'view', 'level': 1},
            {'codename': 'user.create', 'name': '创建用户', 'resource': 'user', 'action': 'create', 'level': 2},
            {'codename': 'user.edit', 'name': '编辑用户', 'resource': 'user', 'action': 'edit', 'level': 2},
            {'codename': 'user.delete', 'name': '删除用户', 'resource': 'user', 'action': 'delete', 'level': 3},
            {'codename': 'user.manage', 'name': '用户管理', 'resource': 'user', 'action': 'manage', 'level': 4},
            
            # 文章管理权限
            {'codename': 'article.view', 'name': '查看文章', 'resource': 'article', 'action': 'view', 'level': 1},
            {'codename': 'article.create', 'name': '创建文章', 'resource': 'article', 'action': 'create', 'level': 2},
            {'codename': 'article.edit', 'name': '编辑文章', 'resource': 'article', 'action': 'edit', 'level': 2},
            {'codename': 'article.delete', 'name': '删除文章', 'resource': 'article', 'action': 'delete', 'level': 3},
            {'codename': 'article.publish', 'name': '发布文章', 'resource': 'article', 'action': 'publish', 'level': 3},
            {'codename': 'article.manage', 'name': '文章管理', 'resource': 'article', 'action': 'manage', 'level': 4},
            
            # AI配置管理权限
            {'codename': 'ai_config.view', 'name': '查看AI配置', 'resource': 'ai_config', 'action': 'view', 'level': 1},
            {'codename': 'ai_config.create', 'name': '创建AI配置', 'resource': 'ai_config', 'action': 'create', 'level': 2},
            {'codename': 'ai_config.edit', 'name': '编辑AI配置', 'resource': 'ai_config', 'action': 'edit', 'level': 2},
            {'codename': 'ai_config.delete', 'name': '删除AI配置', 'resource': 'ai_config', 'action': 'delete', 'level': 3},
            {'codename': 'ai_config.test', 'name': '测试AI连接', 'resource': 'ai_config', 'action': 'test', 'level': 2},
            {'codename': 'ai_config.manage', 'name': 'AI配置管理', 'resource': 'ai_config', 'action': 'manage', 'level': 4},
            
            # 系统管理权限
            {'codename': 'system.view', 'name': '查看系统信息', 'resource': 'system', 'action': 'view', 'level': 1},
            {'codename': 'system.config', 'name': '系统配置', 'resource': 'system', 'action': 'config', 'level': 4},
            {'codename': 'system.admin', 'name': '系统管理', 'resource': 'system', 'action': 'admin', 'level': 5},
            
            # 角色权限管理
            {'codename': 'role.view', 'name': '查看角色', 'resource': 'role', 'action': 'view', 'level': 1},
            {'codename': 'role.create', 'name': '创建角色', 'resource': 'role', 'action': 'create', 'level': 4},
            {'codename': 'role.edit', 'name': '编辑角色', 'resource': 'role', 'action': 'edit', 'level': 4},
            {'codename': 'role.delete', 'name': '删除角色', 'resource': 'role', 'action': 'delete', 'level': 4},
            {'codename': 'role.assign', 'name': '分配角色', 'resource': 'role', 'action': 'assign', 'level': 4},
            
            # 审计日志权限
            {'codename': 'audit.view', 'name': '查看审计日志', 'resource': 'audit', 'action': 'view', 'level': 3},
            {'codename': 'audit.export', 'name': '导出审计日志', 'resource': 'audit', 'action': 'export', 'level': 4},
        ]
        
        created_count = 0
        for perm_data in permissions_data:
            permission, created = Permission.objects.get_or_create(
                codename=perm_data['codename'],
                defaults={
                    'name': perm_data['name'],
                    'resource': perm_data['resource'],
                    'action': perm_data['action'],
                    'level': perm_data['level'],
                    'description': f"{perm_data['name']}权限"
                }
            )
            if created or force:
                if force and not created:
                    # 更新现有权限
                    for key, value in perm_data.items():
                        if key != 'codename':
                            setattr(permission, key, value)
                    permission.save()
                created_count += 1
                self.stdout.write(f'  ✓ 创建权限: {permission.name}')
        
        self.stdout.write(self.style.SUCCESS(f'权限创建完成，共创建/更新 {created_count} 个权限'))

    def create_roles(self, force):
        """创建默认角色"""
        self.stdout.write('创建默认角色...')
        
        roles_data = [
            {
                'name': 'guest',
                'display_name': '访客',
                'description': '未登录用户或基础访问权限',
                'level': 1,
                'is_system': True,
                'is_default': False,
            },
            {
                'name': 'user',
                'display_name': '普通用户',
                'description': '已注册的普通用户',
                'level': 2,
                'is_system': True,
                'is_default': True,
            },
            {
                'name': 'editor',
                'display_name': '编辑者',
                'description': '可以创建和编辑内容的用户',
                'level': 3,
                'is_system': True,
                'is_default': False,
            },
            {
                'name': 'moderator',
                'display_name': '版主',
                'description': '可以管理内容和用户的版主',
                'level': 4,
                'is_system': True,
                'is_default': False,
            },
            {
                'name': 'admin',
                'display_name': '管理员',
                'description': '系统管理员，拥有大部分管理权限',
                'level': 5,
                'is_system': True,
                'is_default': False,
            },
            {
                'name': 'superadmin',
                'display_name': '超级管理员',
                'description': '拥有所有权限的超级管理员',
                'level': 6,
                'is_system': True,
                'is_default': False,
            },
        ]
        
        created_count = 0
        for role_data in roles_data:
            role, created = Role.objects.get_or_create(
                name=role_data['name'],
                defaults=role_data
            )
            if created or force:
                if force and not created:
                    # 更新现有角色
                    for key, value in role_data.items():
                        if key != 'name':
                            setattr(role, key, value)
                    role.save()
                created_count += 1
                self.stdout.write(f'  ✓ 创建角色: {role.display_name}')
        
        self.stdout.write(self.style.SUCCESS(f'角色创建完成，共创建/更新 {created_count} 个角色'))

    def assign_permissions_to_roles(self):
        """为角色分配权限"""
        self.stdout.write('为角色分配权限...')
        
        # 权限分配策略
        role_permissions = {
            'guest': [
                'article.view', 'user.view'
            ],
            'user': [
                'article.view', 'article.create', 'user.view'
            ],
            'editor': [
                'article.view', 'article.create', 'article.edit', 'article.publish',
                'user.view', 'ai_config.view'
            ],
            'moderator': [
                'article.view', 'article.create', 'article.edit', 'article.delete', 'article.publish', 'article.manage',
                'user.view', 'user.edit',
                'ai_config.view', 'ai_config.create', 'ai_config.edit', 'ai_config.test',
                'audit.view'
            ],
            'admin': [
                'user.view', 'user.create', 'user.edit', 'user.delete', 'user.manage',
                'article.view', 'article.create', 'article.edit', 'article.delete', 'article.publish', 'article.manage',
                'ai_config.view', 'ai_config.create', 'ai_config.edit', 'ai_config.delete', 'ai_config.test', 'ai_config.manage',
                'role.view', 'role.assign',
                'audit.view', 'audit.export',
                'system.view', 'system.config'
            ],
            'superadmin': [
                # 超级管理员拥有所有权限
                'user.view', 'user.create', 'user.edit', 'user.delete', 'user.manage',
                'article.view', 'article.create', 'article.edit', 'article.delete', 'article.publish', 'article.manage',
                'ai_config.view', 'ai_config.create', 'ai_config.edit', 'ai_config.delete', 'ai_config.test', 'ai_config.manage',
                'role.view', 'role.create', 'role.edit', 'role.delete', 'role.assign',
                'audit.view', 'audit.export',
                'system.view', 'system.config', 'system.admin'
            ]
        }
        
        for role_name, permission_codes in role_permissions.items():
            try:
                role = Role.objects.get(name=role_name)
                permissions = Permission.objects.filter(codename__in=permission_codes)
                
                # 清除现有权限（如果强制更新）
                role.permissions.clear()
                
                # 添加新权限
                role.permissions.set(permissions)
                
                self.stdout.write(f'  ✓ 为角色 {role.display_name} 分配了 {permissions.count()} 个权限')
                
            except Role.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'  ⚠ 角色 {role_name} 不存在，跳过权限分配')
                )

    def assign_superuser_roles(self):
        """为超级用户分配超级管理员角色"""
        self.stdout.write('为超级用户分配角色...')
        
        try:
            superadmin_role = Role.objects.get(name='superadmin')
            superusers = User.objects.filter(is_superuser=True)
            
            assigned_count = 0
            for user in superusers:
                user_role, created = UserRole.objects.get_or_create(
                    user=user,
                    role=superadmin_role,
                    defaults={
                        'assigned_by': None,  # 系统自动分配
                        'is_active': True,
                    }
                )
                if created:
                    assigned_count += 1
                    self.stdout.write(f'  ✓ 为超级用户 {user.username} 分配超级管理员角色')
            
            if assigned_count == 0:
                self.stdout.write('  - 没有需要分配角色的超级用户')
            else:
                self.stdout.write(self.style.SUCCESS(f'为 {assigned_count} 个超级用户分配了角色'))
                
        except Role.DoesNotExist:
            self.stdout.write(
                self.style.WARNING('  ⚠ 超级管理员角色不存在，跳过角色分配')
            )
