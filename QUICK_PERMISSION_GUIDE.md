# Alpha 权限系统快速使用指南

## 🚀 快速开始

### 1. 初始化权限组
```bash
cd backend
python manage.py setup_permissions
```

### 2. 检查权限配置
```bash
python manage.py check_permissions
```

## 👥 用户角色说明

| 角色 | 定义 | 权限范围 |
|------|------|----------|
| **超级用户** | `is_superuser=True` | 🔥 所有权限 |
| **管理员** | `is_staff=True` 或 "管理员"组 | 📝 内容管理、用户管理 |
| **普通用户** | 默认注册用户 | 👀 基础读写权限 |

## 🔧 常用操作

### 设置用户为管理员
```python
# Django Shell
python manage.py shell

from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
User = get_user_model()

# 方法1: 加入管理员组
admin_group = Group.objects.get(name='管理员')
user = User.objects.get(username='用户名')
user.groups.add(admin_group)

# 方法2: 设置为staff
user.is_staff = True
user.save()
```

### 检查用户权限
```bash
python manage.py check_permissions --username 用户名
```

### 检查权限组
```bash
python manage.py check_permissions --group 管理员
```

## 🎯 权限测试步骤

### 测试场景1: 权限生效
1. 创建测试用户
2. 加入"管理员"组
3. 前端登录测试删除分类功能 ✅

### 测试场景2: 权限限制
1. 在Django后台移除"管理员"组的所有权限
2. 前端尝试删除分类 ❌ (应该失败)
3. 重新分配权限
4. 再次测试 ✅ (应该成功)

## 📋 权限检查清单

- [ ] 运行 `setup_permissions` 命令
- [ ] 在Django后台创建"管理员"权限组
- [ ] 将测试用户加入"管理员"组
- [ ] 测试前端管理功能是否可用
- [ ] 移除权限组权限并测试限制是否生效
- [ ] 重新分配权限并验证恢复

## 🔍 问题排查

### 用户无法删除分类？
1. 检查用户是否在"管理员"组：`check_permissions --username 用户名`
2. 检查"管理员"组是否有 `delete_category` 权限：`check_permissions --group 管理员`
3. 确认API使用的是 `DjangoModelPermissionsOrReadOnly` 权限类

### 权限组没有权限？
1. 运行 `setup_permissions` 重新分配权限
2. 在Django后台手动添加权限到组

### 前端仍显示管理功能？
1. 检查前端权限判断逻辑：`isAdmin` 计算属性
2. 确认用户信息包含 `groups` 字段
3. 检查路由守卫配置

## 📚 相关文档

- [完整权限设计文档](./PERMISSION_DESIGN.md)
- [Django权限系统官方文档](https://docs.djangoproject.com/en/4.2/topics/auth/default/#permissions-and-authorization)
- [DRF权限文档](https://www.django-rest-framework.org/api-guide/permissions/)

## 🆘 紧急恢复

如果权限配置出现问题，可以通过超级用户账号在Django后台手动恢复：

1. 访问 `/admin/`
2. 进入 "认证和授权" → "组"
3. 编辑"管理员"组
4. 重新分配所需权限

或者删除所有组并重新运行：
```bash
python manage.py shell
>>> from django.contrib.auth.models import Group
>>> Group.objects.all().delete()
>>> exit()
python manage.py setup_permissions
```

