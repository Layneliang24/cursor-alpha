# Alpha 技术共享平台

基于 Django + Vue.js 的现代化技术文章分享平台

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- npm 或 yarn

### 启动项目
```bash
# 一键启动前后端服务
start.bat

# 或分别启动
# 后端
cd backend
python manage.py runserver 127.0.0.1:8000

# 前端
cd frontend  
npm run dev
```

### 访问地址
- 前端：http://localhost:5173
- 后端API：http://127.0.0.1:8000/api/v1/
- 管理后台：http://127.0.0.1:8000/admin/

## 📁 项目结构

```
alpha/
├── backend/           # Django后端
│   ├── alpha/        # 项目配置
│   ├── apps/         # 应用模块
│   │   ├── api/      # API接口
│   │   ├── articles/ # 文章模块
│   │   ├── categories/ # 分类模块
│   │   └── users/    # 用户模块
│   └── manage.py
├── frontend/         # Vue.js前端
│   ├── src/
│   │   ├── api/      # API调用
│   │   ├── components/ # 组件
│   │   ├── views/    # 页面
│   │   └── stores/   # 状态管理
│   └── package.json
└── start.bat        # 启动脚本
```

## ✨ 主要功能

- 🔐 **用户认证**：注册、登录、JWT认证
- 📝 **文章管理**：发布、编辑、删除、Markdown支持
- 🏷️ **分类标签**：文章分类和标签管理
- 💬 **评论系统**：文章评论和回复
- 👤 **用户中心**：个人资料、文章管理
- 🔍 **搜索功能**：全文搜索文章内容
- 📱 **响应式设计**：支持移动端访问

## 🛠️ 技术栈

**后端**：
- Django 4.2
- Django REST Framework
- SQLite/PostgreSQL
- JWT认证

**前端**：
- Vue 3
- Element Plus
- Pinia状态管理
- Vue Router
- Axios

## 📊 测试数据

运行以下命令创建测试数据：
```bash
cd backend
python create_test_user.py    # 创建测试用户
python create_articles.py     # 创建技术文章
```

测试账号：
- 用户名：testuser
- 密码：123456

## 🎨 特色功能

- 🌟 **鼠标特效**：可切换的撒花、小鱼、星星特效
- 🎭 **动态背景**：登录页面动态渐变背景
- 📖 **Markdown渲染**：支持代码高亮的文章显示
- 🔧 **固定导航**：顶部导航栏和侧边菜单固定
- 📱 **响应式布局**：完美适配各种屏幕尺寸

## 📄 开发说明

### API接口
- 基础URL：`/api/v1/`
- 认证方式：JWT Bearer Token
- 数据格式：JSON

### 主要端点
- `POST /auth/login/` - 用户登录
- `GET /articles/` - 获取文章列表
- `POST /articles/` - 创建文章
- `GET /articles/{id}/` - 获取文章详情

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 📝 更新日志

### v1.0.0 (2024-01-15)
- ✅ 完成基础功能开发
- ✅ 用户认证系统
- ✅ 文章CRUD操作
- ✅ 响应式界面设计
- ✅ Markdown文章渲染
- ✅ 鼠标特效和动画

## 📞 联系方式

- 项目地址：https://github.com/Layneliang24/cursor-alpha
- 问题反馈：GitHub Issues

---

© 2024 Alpha 技术共享平台. All rights reserved.