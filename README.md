# Alpha 技术共享平台 🚀

基于 Django + Vue.js 的现代化AI技术文章分享平台，专注于AI Agent、大语言模型等前沿技术内容。

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![Vue](https://img.shields.io/badge/vue-3.x-green.svg)
![Django](https://img.shields.io/badge/django-4.x-green.svg)

## 🌟 项目特色

- 🤖 **AI Agent 专题**：专注AI智能体技术文章分享
- 🎨 **自定义轮播**：精美的文章轮播展示组件
- 🔐 **细粒度权限**：基于Django权限系统的精确控制
- 📱 **响应式设计**：完美适配PC和移动端
- 🌈 **现代UI**：基于Element Plus的美观界面
- 🔄 **实时更新**：动态数据加载和状态管理

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- MySQL 5.7+ (推荐) 或 SQLite
- npm 或 yarn

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/yourusername/alpha.git
cd alpha
```

2. **后端设置**
```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

3. **前端设置**
```bash
cd frontend
npm install
npm run dev
```

### 访问地址
- 🌐 前端应用：http://localhost:3000
- 🔧 后端API：http://127.0.0.1:8000/api/v1/
- 👨‍💼 管理后台：http://127.0.0.1:8000/admin/

## 📁 项目架构

```
alpha/
├── 🔧 backend/                    # Django 后端服务
│   ├── alpha/                    # 项目配置
│   │   ├── settings.py          # 全局配置
│   │   └── urls.py              # 根路由
│   ├── apps/                    # 业务应用
│   │   ├── api/                 # REST API层
│   │   │   ├── views.py         # ViewSets & 端点
│   │   │   ├── serializers.py   # 数据序列化
│   │   │   ├── permissions.py   # 权限控制
│   │   │   └── pagination.py    # 分页配置
│   │   ├── articles/            # 文章管理
│   │   ├── categories/          # 分类标签
│   │   ├── users/               # 用户系统
│   │   └── links/               # 友情链接
│   ├── media/                   # 媒体文件
│   └── requirements.txt         # Python依赖
├── 🎨 frontend/                   # Vue.js 前端应用
│   ├── src/
│   │   ├── api/                 # API调用封装
│   │   ├── components/          # 可复用组件
│   │   │   ├── ArticleCarousel.vue  # 自定义轮播
│   │   │   ├── ExternalLinks.vue    # 友情链接
│   │   │   └── MarkdownEditor.vue   # MD编辑器
│   │   ├── views/               # 页面组件
│   │   │   ├── articles/        # 文章相关页面
│   │   │   ├── auth/            # 认证页面
│   │   │   └── user/            # 用户中心
│   │   ├── stores/              # Pinia状态管理
│   │   └── router/              # Vue路由配置
│   └── package.json             # NPM依赖
└── 📄 README.md                  # 项目文档
```

## ✨ 核心功能

### 🔐 用户系统
- JWT认证登录/注册
- 个人资料管理
- 头像上传
- 密码重置功能
- 细粒度权限控制

### 📝 文章管理
- Markdown编辑器
- 文章分类和标签
- 封面图片上传
- 文章状态管理(草稿/发布/归档)
- 搜索和筛选功能
- 分页和排序

### 🎨 用户界面
- 自定义文章轮播组件
- 响应式设计
- 骨架屏加载效果
- 友情链接管理
- 动态统计数据
- 现代化卡片布局

### 🔧 管理功能
- Django Admin后台
- 权限组管理
- 内容审核
- 数据统计
- 日志记录

## 🛠️ 技术栈详解

### 后端技术
| 技术 | 版本 | 用途 |
|------|------|------|
| Django | 4.x | Web框架 |
| Django REST Framework | 3.x | API开发 |
| MySQL | 8.0 | 主数据库 |
| JWT | - | 身份认证 |
| Pillow | - | 图像处理 |
| django-cors-headers | - | 跨域支持 |

### 前端技术
| 技术 | 版本 | 用途 |
|------|------|------|
| Vue.js | 3.x | 前端框架 |
| Element Plus | 2.x | UI组件库 |
| Pinia | 2.x | 状态管理 |
| Vue Router | 4.x | 路由管理 |
| Axios | 1.x | HTTP客户端 |
| Vite | 4.x | 构建工具 |

## 📊 示例数据

运行以下命令创建示例数据：
```bash
cd backend

# 创建权限组和权限
python manage.py setup_permissions

# 创建示例文章和用户
python create_sample_articles_with_covers.py

# 创建AI技术文章
python create_ai_content.py
```

### 测试账号
| 用户名 | 密码 | 角色 | 权限 |
|--------|------|------|------|
| admin | admin123 | 超级管理员 | 所有权限 |
| agent_dev | password123 | 开发者 | 文章管理 |
| layne | password123 | 普通用户 | 基础权限 |

## 🎨 界面预览

### 首页轮播
- 自定义实现的文章轮播组件
- 支持自动播放和手动导航
- 渐变背景和平滑过渡效果
- 响应式设计

### 文章列表
- 分页、搜索、筛选功能
- 骨架屏加载效果
- 多种排序方式
- 分类和标签筛选

### 权限管理
- Django内置权限系统
- 自定义权限类
- 前端权限控制
- 管理员后台

## 🔧 开发指南

### API文档
- 基础URL：`/api/v1/`
- 认证方式：`Bearer <JWT_TOKEN>`
- 数据格式：JSON

### 主要API端点
```
# 认证相关
POST /api/v1/auth/login/          # 用户登录
POST /api/v1/auth/register/       # 用户注册
POST /api/v1/auth/password-reset/ # 密码重置

# 文章相关
GET  /api/v1/articles/            # 文章列表
POST /api/v1/articles/            # 创建文章
GET  /api/v1/articles/{id}/       # 文章详情
PUT  /api/v1/articles/{id}/       # 更新文章

# 首页数据
GET  /api/v1/home/stats/          # 统计数据
GET  /api/v1/home/popular-articles/ # 热门文章

# 友情链接
GET  /api/v1/external-links/      # 友情链接列表
POST /api/v1/external-links/      # 创建友情链接
```

### 权限系统
```python
# 自定义权限类示例
class IsAuthorOrAdminOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.author == request.user or request.user.is_staff
```

## 🚀 部署指南

### Docker部署 (推荐)
```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 初始化数据库
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
```

### 传统部署
```bash
# 后端部署
cd backend
pip install -r requirements.txt
python manage.py collectstatic
python manage.py migrate
gunicorn alpha.wsgi:application

# 前端部署
cd frontend
npm run build
# 将dist目录部署到Nginx
```

## 🤝 贡献指南

我们欢迎所有形式的贡献！

1. **Fork** 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 **Pull Request**

### 开发规范
- 遵循PEP 8 (Python)
- 使用ESLint (JavaScript)
- 编写单元测试
- 更新相关文档

## 📝 更新日志

### v2.0.0 (2025-01-09) 🎉
- ✨ 新增自定义文章轮播组件
- 🔐 完善权限管理系统
- 🔗 添加友情链接功能
- 📧 实现密码重置功能
- 🎨 优化UI界面和用户体验
- 📱 改进响应式设计
- 🐛 修复多项已知问题

### v1.0.0 (2024-12-01)
- ✅ 完成基础功能开发
- ✅ 用户认证系统
- ✅ 文章CRUD操作
- ✅ 响应式界面设计
- ✅ Markdown文章渲染

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系方式

- 🌐 项目地址：[GitHub Repository](https://github.com/yourusername/alpha)
- 🐛 问题反馈：[GitHub Issues](https://github.com/yourusername/alpha/issues)
- 📧 邮箱联系：your.email@example.com

---

<div align="center">

**⭐ 如果这个项目对您有帮助，请给我们一个Star！⭐**

Made with ❤️ by Alpha Team

</div>