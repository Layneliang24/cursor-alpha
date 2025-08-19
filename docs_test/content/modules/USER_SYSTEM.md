# 用户系统模块

## 📋 模块概述

用户系统是Alpha技术共享平台的核心管理模块，负责用户账户的创建、维护、权限分配和安全管理，与权限系统无缝集成，确保系统安全和数据保护。

## 🎯 核心价值

- **用户生命周期管理**：从注册到注销的完整用户管理
- **安全控制**：确保系统安全和数据保护
- **权限集成**：与权限系统无缝集成
- **用户体验**：提供友好的用户管理界面

## 🏗️ 功能架构

### 功能模块图
```
用户管理系统
├── 用户账户管理
│   ├── 用户注册
│   ├── 用户认证
│   ├── 密码管理
│   └── 账户状态管理
├── 用户信息管理
│   ├── 基本信息
│   ├── 扩展信息
│   ├── 偏好设置
│   └── 头像管理
├── 用户权限管理
│   ├── 角色分配
│   ├── 权限分配
│   ├── 权限继承
│   └── 权限审计
└── 用户安全管理
    ├── 登录安全
    ├── 密码策略
    ├── 会话管理
    └── 安全日志
```

## 📊 数据模型设计

### 1. 用户基础模型
```python
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """扩展用户模型"""
    # 基础信息
    phone = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    birth_date = models.DateField(blank=True, null=True)
    
    # 状态信息
    is_verified = models.BooleanField(default=False)
    email_verified_at = models.DateTimeField(blank=True, null=True)
    phone_verified_at = models.DateTimeField(blank=True, null=True)
    
    # 安全信息
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    password_changed_at = models.DateTimeField(blank=True, null=True)
    failed_login_attempts = models.IntegerField(default=0)
    locked_until = models.DateTimeField(blank=True, null=True)
    
    # 偏好设置
    timezone = models.CharField(max_length=50, default='Asia/Shanghai')
    language = models.CharField(max_length=10, default='zh-hans')
    theme = models.CharField(max_length=20, default='light')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
```

### 2. 用户配置模型
```python
class UserProfile(models.Model):
    """用户扩展配置"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # 个人信息
    real_name = models.CharField(max_length=100, blank=True)
    company = models.CharField(max_length=200, blank=True)
    position = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    
    # 社交信息
    github_username = models.CharField(max_length=100, blank=True)
    linkedin_url = models.URLField(blank=True)
    twitter_username = models.CharField(max_length=100, blank=True)
    
    # 学习偏好
    learning_goals = models.JSONField(default=list)
    skill_tags = models.JSONField(default=list)
    interests = models.JSONField(default=list)
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
```

## 🔐 用户认证与授权

### 1. 认证机制
**JWT Token认证**：
- 使用JWT (JSON Web Token) 进行无状态认证
- 支持Token刷新机制
- 支持多设备同时登录
- 自动Token过期处理

**多因素认证**：
- 支持邮箱验证码
- 支持手机短信验证
- 支持Google Authenticator
- 支持硬件密钥认证

### 2. 权限系统
**基于角色的访问控制 (RBAC)**：
- 角色定义：管理员、编辑者、普通用户、访客
- 权限继承：角色间权限继承关系
- 细粒度权限：功能级、数据级权限控制
- 动态权限：运行时权限调整

## 🛡️ 安全机制

### 1. 密码安全
**密码策略**：
- 最小长度：8位
- 复杂度要求：包含大小写字母、数字、特殊字符
- 密码历史：禁止重复使用最近5个密码
- 定期更换：90天强制更换密码

### 2. 登录安全
**防暴力破解**：
- 登录失败次数限制：5次
- 账户锁定时间：30分钟
- IP地址黑名单机制
- 验证码验证机制

## 👤 用户管理功能

### 1. 用户注册
**注册流程**：
1. 用户填写基本信息
2. 邮箱/手机验证
3. 设置密码
4. 完善个人资料
5. 选择学习偏好

### 2. 用户信息管理
**基本信息**：
- 用户名、邮箱、手机号
- 真实姓名、头像、个人简介
- 生日、性别、所在地

**扩展信息**：
- 公司、职位、个人网站
- GitHub、LinkedIn、Twitter账号
- 学习目标、技能标签、兴趣爱好

## 🔧 技术实现

### 1. 后端架构
**技术栈**：
- **框架**: Django 4.2+
- **认证**: Django REST Framework + JWT
- **权限**: Django Guardian
- **数据库**: MySQL 8.0+
- **缓存**: Redis 6.0+

### 2. 前端架构
**技术栈**：
- **框架**: Vue 3.0+
- **状态管理**: Pinia
- **路由**: Vue Router 4.0+
- **UI组件**: Element Plus
- **HTTP客户端**: Axios

## 📁 相关文件

### 后端代码
- `backend/apps/users/models.py` - 用户数据模型
- `backend/apps/users/views.py` - 用户相关视图
- `backend/apps/users/urls.py` - 用户相关路由
- `backend/apps/users/forms.py` - 用户表单
- `backend/apps/users/permissions.py` - 用户权限

### 前端代码
- `frontend/src/views/user/` - 用户相关页面
- `frontend/src/components/` - 用户相关组件
- `frontend/src/stores/auth.js` - 认证状态管理
- `frontend/src/stores/user.js` - 用户状态管理

---

*最后更新：2025-01-17*
*更新内容：整合用户管理模块设计文档，创建完整的用户系统模块文档*
