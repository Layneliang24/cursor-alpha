# Alpha 技术共享平台

## 📋 项目概述

Alpha 技术共享平台是一个现代化的技术文章分享网站，采用前后端分离架构，提供完善的文章管理、用户认证、分类管理等功能。

## 🏗️ 技术架构

### 后端技术栈
- **框架**: Django 4.2.7
- **API**: Django REST Framework 3.14.0
- **认证**: JWT (JSON Web Tokens)
- **数据库**: SQLite (开发) / MySQL (生产)
- **邮件**: Django Email Backend
- **验证码**: django-simple-captcha
- **文档**: drf-yasg (Swagger)

### 前端技术栈
- **框架**: Vue 3.3.4
- **UI库**: Element Plus 2.4.2
- **路由**: Vue Router 4.2.5
- **状态管理**: Pinia 2.1.7
- **HTTP客户端**: Axios 1.5.0
- **构建工具**: Vite 4.4.11

## 📁 项目结构

```
alpha/
├── backend/                 # Django后端
│   ├── alpha/              # Django项目配置
│   ├── apps/               # Django应用
│   │   ├── users/          # 用户管理
│   │   ├── articles/       # 文章管理
│   │   ├── categories/     # 分类管理
│   │   └── api/            # API接口
│   ├── static/             # 静态文件
│   ├── media/              # 媒体文件
│   ├── templates/          # 模板文件
│   └── requirements.txt    # Python依赖
├── frontend/               # Vue前端
│   ├── src/
│   │   ├── components/     # Vue组件
│   │   ├── views/          # 页面视图
│   │   ├── router/         # 路由配置
│   │   ├── stores/         # 状态管理
│   │   ├── api/            # API服务
│   │   └── assets/         # 静态资源
│   ├── public/             # 公共文件
│   └── package.json        # Node.js依赖
├── docs/                   # 项目文档
├── scripts/                # 部署脚本
└── README.md              # 项目说明
```

## 🎯 功能模块

### 1. 用户管理模块
- **用户注册**: 邮箱验证注册
- **用户登录**: 用户名/邮箱 + 密码 + 图形验证码
- **用户登出**: JWT Token 注销
- **密码重置**: 邮箱验证重置
- **用户资料**: 个人信息管理

### 2. 文章管理模块
- **文章列表**: 分页展示、搜索、筛选
- **文章详情**: 完整内容展示
- **文章发布**: 富文本编辑器
- **文章编辑**: 在线编辑功能
- **文章删除**: 软删除机制
- **文章分类**: 多级分类管理

### 3. 分类管理模块
- **分类树**: 多级分类结构
- **分类管理**: 增删改查操作
- **分类文章**: 按分类查看文章

### 4. 系统管理模块
- **权限管理**: 基于角色的权限控制
- **系统配置**: 网站基本设置
- **数据统计**: 访问量、用户数等统计

## 🔐 安全特性

### 认证与授权
- JWT Token 认证
- 基于角色的权限控制 (RBAC)
- 图形验证码防机器人
- 邮箱验证防恶意注册

### 数据安全
- SQL注入防护
- XSS攻击防护
- CSRF防护
- 密码加密存储

## 📊 数据库设计

### 用户表 (users_user)
```sql
- id: 主键
- username: 用户名
- email: 邮箱
- password: 密码
- is_active: 是否激活
- date_joined: 注册时间
- last_login: 最后登录
```

### 文章表 (articles_article)
```sql
- id: 主键
- title: 标题
- content: 内容
- summary: 摘要
- author: 作者 (外键)
- category: 分类 (外键)
- status: 状态 (草稿/发布)
- created_at: 创建时间
- updated_at: 更新时间
- views: 浏览量
```

### 分类表 (categories_category)
```sql
- id: 主键
- name: 分类名称
- slug: 分类别名
- parent: 父分类 (自关联)
- description: 描述
- created_at: 创建时间
```

## 🚀 部署方案

### 开发环境
- Django 开发服务器
- Vue 开发服务器
- SQLite 数据库

### 生产环境
- Nginx 反向代理
- Gunicorn WSGI 服务器
- MySQL 数据库
- Redis 缓存
- Docker 容器化

## 📝 API 接口设计

### 认证接口
- `POST /api/auth/register/` - 用户注册
- `POST /api/auth/login/` - 用户登录
- `POST /api/auth/logout/` - 用户登出
- `POST /api/auth/refresh/` - 刷新Token

### 文章接口
- `GET /api/articles/` - 获取文章列表
- `POST /api/articles/` - 创建文章
- `GET /api/articles/{id}/` - 获取文章详情
- `PUT /api/articles/{id}/` - 更新文章
- `DELETE /api/articles/{id}/` - 删除文章

### 分类接口
- `GET /api/categories/` - 获取分类列表
- `POST /api/categories/` - 创建分类
- `GET /api/categories/{id}/` - 获取分类详情
- `PUT /api/categories/{id}/` - 更新分类
- `DELETE /api/categories/{id}/` - 删除分类

## 🎨 前端页面设计

### 主要页面
1. **首页** - 文章列表、分类导航
2. **文章详情页** - 完整文章内容
3. **登录页** - 用户登录界面
4. **注册页** - 用户注册界面
5. **个人中心** - 用户信息管理
6. **文章编辑页** - 文章发布/编辑
7. **分类管理页** - 分类管理界面

### UI/UX 设计原则
- 响应式设计，适配多设备
- 现代化界面，简洁美观
- 用户体验优先
- 无障碍访问支持

## 🔧 开发计划

### 第一阶段：基础架构 (1-2天)
- [x] 项目结构搭建
- [x] Django 后端基础配置
- [x] Vue 前端基础配置
- [ ] 数据库模型设计
- [ ] API 接口设计

### 第二阶段：核心功能 (3-5天)
- [ ] 用户认证系统
- [ ] 文章管理功能
- [ ] 分类管理功能
- [ ] 前端页面开发

### 第三阶段：完善功能 (2-3天)
- [ ] 邮件验证功能
- [ ] 图形验证码
- [ ] 权限管理
- [ ] 数据统计

### 第四阶段：测试部署 (1-2天)
- [ ] 功能测试
- [ ] 性能优化
- [ ] 部署配置
- [ ] 上线部署

## 📞 联系方式

- **项目负责人**: AI Assistant
- **技术支持**: 在线文档
- **问题反馈**: GitHub Issues

---

*最后更新时间: 2024年1月* 