# Alpha 技术分享平台 - 权限管理设计文档

## 1. 概述

本文档定义了Alpha技术分享平台的用户角色体系和权限分配方案，基于Django的内置权限系统实现细粒度的访问控制。

## 2. 用户角色定义

### 2.1 超级用户 (Superuser)
- **定义**: `is_superuser = True`
- **特征**: 拥有系统所有权限，无需显式分配
- **用途**: 系统初始化、紧急维护、最高级别管理

### 2.2 管理员 (Admin/Staff)
- **定义**: `is_staff = True` 或 属于"管理员"权限组
- **特征**: 可访问Django后台，拥有大部分管理权限
- **用途**: 日常运营管理、内容审核、用户管理

### 2.3 普通用户 (Regular User)
- **定义**: `is_staff = False, is_superuser = False`
- **特征**: 基础的读写权限，主要用于内容创作和互动
- **用途**: 发布文章、评论、点赞、收藏等

## 3. 权限矩阵

### 3.1 用户管理权限

| 操作 | 超级用户 | 管理员 | 普通用户 | Django权限 |
|------|----------|--------|----------|------------|
| 查看用户列表 | ✅ | ✅ | ❌ | `users.view_user` |
| 查看用户详情 | ✅ | ✅ | 仅自己 | `users.view_user` |
| 创建用户 | ✅ | ✅ | ❌ | `users.add_user` |
| 编辑用户信息 | ✅ | ✅ | 仅自己 | `users.change_user` |
| 删除用户 | ✅ | ✅ | ❌ | `users.delete_user` |
| 设置用户为管理员 | ✅ | ❌ | ❌ | 超级用户专有 |
| 分配权限组 | ✅ | ✅ | ❌ | `auth.change_user` |

### 3.2 文章管理权限

| 操作 | 超级用户 | 管理员 | 普通用户 | Django权限 |
|------|----------|--------|----------|------------|
| 查看所有文章 | ✅ | ✅ | ✅ | 无需权限 |
| 查看草稿文章 | ✅ | ✅ | 仅自己 | `articles.view_article` |
| 创建文章 | ✅ | ✅ | ✅ | `articles.add_article` |
| 编辑文章 | ✅ | ✅ | 仅自己 | `articles.change_article` |
| 删除文章 | ✅ | ✅ | 仅自己 | `articles.delete_article` |
| 设置推荐文章 | ✅ | ✅ | ❌ | `articles.feature_article` |
| 审核文章 | ✅ | ✅ | ❌ | `articles.moderate_article` |
| 批量操作文章 | ✅ | ✅ | ❌ | `articles.bulk_action` |

### 3.3 分类管理权限

| 操作 | 超级用户 | 管理员 | 普通用户 | Django权限 |
|------|----------|--------|----------|------------|
| 查看分类 | ✅ | ✅ | ✅ | 无需权限 |
| 创建分类 | ✅ | ✅ | ❌ | `categories.add_category` |
| 编辑分类 | ✅ | ✅ | ❌ | `categories.change_category` |
| 删除分类 | ✅ | ✅ | ❌ | `categories.delete_category` |
| 设置分类状态 | ✅ | ✅ | ❌ | `categories.change_category` |
| 调整分类顺序 | ✅ | ✅ | ❌ | `categories.change_category` |

### 3.4 标签管理权限

| 操作 | 超级用户 | 管理员 | 普通用户 | Django权限 |
|------|----------|--------|----------|------------|
| 查看标签 | ✅ | ✅ | ✅ | 无需权限 |
| 创建标签 | ✅ | ✅ | ✅ | `categories.add_tag` |
| 编辑标签 | ✅ | ✅ | ❌ | `categories.change_tag` |
| 删除标签 | ✅ | ✅ | ❌ | `categories.delete_tag` |

### 3.5 评论管理权限

| 操作 | 超级用户 | 管理员 | 普通用户 | Django权限 |
|------|----------|--------|----------|------------|
| 查看评论 | ✅ | ✅ | ✅ | 无需权限 |
| 发表评论 | ✅ | ✅ | ✅ | `articles.add_comment` |
| 编辑评论 | ✅ | ✅ | 仅自己 | `articles.change_comment` |
| 删除评论 | ✅ | ✅ | 仅自己 | `articles.delete_comment` |
| 审核评论 | ✅ | ✅ | ❌ | `articles.moderate_comment` |

### 3.6 系统管理权限

| 操作 | 超级用户 | 管理员 | 普通用户 | Django权限 |
|------|----------|--------|----------|------------|
| 访问Django后台 | ✅ | ✅ | ❌ | `is_staff = True` |
| 查看系统日志 | ✅ | ✅ | ❌ | `admin.view_logentry` |
| 管理权限组 | ✅ | ❌ | ❌ | 超级用户专有 |
| 系统配置 | ✅ | ❌ | ❌ | 超级用户专有 |

## 4. 权限组配置

### 4.1 预定义权限组

#### 管理员组 (Admin Group)
```python
# 组名: "管理员"
permissions = [
    # 文章权限
    'articles.view_article',
    'articles.add_article', 
    'articles.change_article',
    'articles.delete_article',
    'articles.feature_article',
    'articles.moderate_article',
    
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
    'articles.moderate_comment',
    
    # 用户权限
    'users.view_user',
    'users.add_user',
    'users.change_user',
    'users.delete_user',
]
```

#### 内容编辑组 (Content Editor Group)
```python
# 组名: "内容编辑"
permissions = [
    # 文章权限
    'articles.view_article',
    'articles.add_article',
    'articles.change_article',
    'articles.feature_article',
    'articles.moderate_article',
    
    # 标签权限
    'categories.view_tag',
    'categories.add_tag',
    'categories.change_tag',
    
    # 评论权限
    'articles.view_comment',
    'articles.moderate_comment',
]
```

#### 分类管理组 (Category Manager Group)
```python
# 组名: "分类管理员"
permissions = [
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
```

## 5. 技术实现

### 5.1 权限检查机制

#### 基于Django模型权限的权限类
```python
class DjangoModelPermissionsOrReadOnly(DjangoModelPermissions):
    """
    基于Django模型权限的权限类
    - 允许所有人读取
    - 写操作需要具体的模型权限
    """
    
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return super().has_permission(request, view)
```

#### ViewSet权限配置
```python
class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissionsOrReadOnly]
    
class ArticleViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissionsOrReadOnly]
```

### 5.2 前端权限控制

#### 路由守卫
```javascript
// 管理员路由保护
{
  path: '/admin/categories',
  meta: { requiresAuth: true, adminOnly: true }
}

// 路由守卫逻辑
router.beforeEach((to, from, next) => {
  if (to.meta.adminOnly && !isAdmin(user)) {
    next('/403')
  }
})
```

#### 组件权限控制
```javascript
// 检查管理员权限
const isAdmin = computed(() => {
  return user.value?.is_staff || 
         user.value?.is_superuser || 
         user.value?.groups?.includes('管理员')
})
```

### 5.3 API权限验证

#### 权限装饰器
```python
@permission_required('articles.delete_article')
def delete_article(request, article_id):
    # 删除文章逻辑
    pass
```

#### 对象级权限
```python
def has_object_permission(self, request, view, obj):
    # 用户只能编辑自己的文章
    if request.method in ['PUT', 'PATCH', 'DELETE']:
        return obj.author == request.user or request.user.is_staff
    return True
```

## 6. 权限分配流程

### 6.1 新用户注册
1. 创建用户账号 (`is_staff=False, is_superuser=False`)
2. 自动分配基础权限（发表文章、评论等）
3. 创建用户资料 (UserProfile)

### 6.2 管理员提升
1. 超级用户在Django后台设置 `is_staff=True`
2. 将用户添加到"管理员"权限组
3. 用户获得管理员权限

### 6.3 权限回收
1. 从权限组中移除用户
2. 设置 `is_staff=False`（如需要）
3. 权限立即生效

## 7. 安全考虑

### 7.1 权限最小化原则
- 用户只获得执行其职责所需的最小权限
- 定期审查和清理不必要的权限

### 7.2 权限分离
- 内容管理与用户管理权限分离
- 系统管理权限仅限超级用户

### 7.3 审计日志
- 记录所有权限变更操作
- 追踪敏感操作的执行者

## 8. 监控与维护

### 8.1 权限监控
- 定期检查权限组成员
- 监控异常权限使用

### 8.2 权限维护
- 及时更新权限配置
- 处理权限相关的用户反馈

## 9. 常见问题

### Q1: 用户属于权限组但仍无法执行操作？
**A**: 检查权限组是否有对应的Django权限，确保使用`DjangoModelPermissionsOrReadOnly`权限类。

### Q2: 如何给用户临时权限？
**A**: 在Django后台直接给用户分配特定权限，无需加入权限组。

### Q3: 前端如何知道用户权限？
**A**: 通过API返回用户的`groups`和`is_staff`状态，前端据此控制UI显示。

## 10. 管理命令

### 10.1 权限组设置命令
```bash
# 设置默认权限组和权限
python manage.py setup_permissions
```

此命令将创建以下权限组：
- **管理员**: 拥有完整的管理权限
- **内容编辑**: 拥有文章和标签的编辑权限
- **分类管理员**: 拥有分类和标签的管理权限

### 10.2 权限检查命令
```bash
# 检查所有权限配置
python manage.py check_permissions

# 检查特定用户权限
python manage.py check_permissions --username admin

# 检查特定权限组
python manage.py check_permissions --group 管理员
```

### 10.3 使用示例
```bash
# 1. 初始化权限组
cd backend
python manage.py setup_permissions

# 2. 检查权限配置
python manage.py check_permissions

# 3. 将用户添加到管理员组（在Django后台操作）
# 或使用Django shell
python manage.py shell
>>> from django.contrib.auth.models import Group
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> admin_group = Group.objects.get(name='管理员')
>>> user = User.objects.get(username='testuser')
>>> user.groups.add(admin_group)
>>> user.save()

# 4. 验证用户权限
python manage.py check_permissions --username testuser
```

## 11. 权限测试

### 11.1 测试场景

#### 场景1: 管理员权限测试
1. 创建测试用户并加入"管理员"组
2. 测试分类的增删改查操作
3. 验证权限生效

#### 场景2: 权限回收测试
1. 从"管理员"组移除所有权限
2. 测试用户是否无法执行管理操作
3. 重新分配权限并验证

#### 场景3: 细粒度权限测试
1. 只给用户特定权限（如只能查看和编辑分类）
2. 测试用户是否只能执行对应操作

### 11.2 测试脚本
```python
# test_permissions.py
from django.test import TestCase
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()

class PermissionTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
    def test_admin_group_permissions(self):
        """测试管理员组权限"""
        admin_group = Group.objects.get(name='管理员')
        self.user.groups.add(admin_group)
        
        self.client.force_authenticate(user=self.user)
        
        # 测试创建分类
        response = self.client.post('/api/categories/', {
            'name': '测试分类',
            'description': '测试描述'
        })
        self.assertEqual(response.status_code, 201)
        
    def test_no_permission_user(self):
        """测试无权限用户"""
        self.client.force_authenticate(user=self.user)
        
        # 测试创建分类（应该失败）
        response = self.client.post('/api/categories/', {
            'name': '测试分类',
            'description': '测试描述'
        })
        self.assertEqual(response.status_code, 403)
```

## 12. 更新日志

- **v1.0** (2024-01-XX): 初始权限设计
- **v1.1** (2024-01-XX): 修复权限检查逻辑，使用Django模型权限
- **v1.2** (2024-01-XX): 添加前端权限控制
- **v1.3** (2024-01-XX): 添加权限管理命令和测试指南
