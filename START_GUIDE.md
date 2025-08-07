# Alpha 技术共享平台 - 启动指南

## 🚀 快速启动

### 环境准备

1. **Python 环境**（已确认）
   - Python 3.10+ ✅
   - pip ✅

2. **Node.js 环境**（需要安装）
   - Node.js 16+ 
   - npm 或 yarn

### 启动步骤

#### 第一步：启动后端服务

```bash
# 1. 进入后端目录
cd "S:\WorkShop\cursor\alpha\backend"

# 2. 安装Python依赖（如果还没安装）
pip install -r requirements.txt

# 3. 执行数据库迁移
py manage.py makemigrations
py manage.py migrate

# 4. 创建测试数据
py create_test_data.py

# 5. 启动Django开发服务器
py manage.py runserver 8000
```

**后端服务现在运行在：http://127.0.0.1:8000**

#### 第二步：启动前端服务（需要Node.js）

```bash
# 1. 进入前端目录
cd "S:\WorkShop\cursor\alpha\frontend"

# 2. 安装Node.js依赖
npm install

# 3. 启动Vue开发服务器
npm run dev
```

**前端应用将运行在：http://localhost:5173**

## 🌐 访问地址

### 主要访问点
- **网站首页**：http://localhost:5173
- **后端API**：http://127.0.0.1:8000/api/
- **管理后台**：http://127.0.0.1:8000/admin/

### 测试账户
- **管理员账户**：需要通过 `py manage.py createsuperuser` 创建
- **测试用户**：testuser / test123（由测试数据脚本创建）

## 📁 项目结构

```
alpha/
├── backend/                 # Django后端
│   ├── alpha/              # Django项目配置
│   ├── apps/               # 应用模块
│   │   ├── users/          # 用户管理
│   │   ├── articles/       # 文章管理
│   │   ├── categories/     # 分类管理
│   │   └── api/            # API接口
│   ├── manage.py           # Django管理脚本
│   └── requirements.txt    # Python依赖
├── frontend/               # Vue前端
│   ├── src/
│   │   ├── api/            # API服务层
│   │   ├── stores/         # 状态管理
│   │   ├── views/          # 页面组件
│   │   ├── components/     # 公共组件
│   │   └── router/         # 路由配置
│   ├── package.json        # Node.js依赖
│   └── vite.config.js      # Vite配置
└── docs/                   # 项目文档
```

## 🎯 功能演示

### 普通用户流程
1. 访问 http://localhost:5173
2. 点击"注册"创建账号
3. 登录后浏览文章
4. 发布自己的文章
5. 与其他用户互动（点赞、评论）

### 管理员功能
1. 访问 http://127.0.0.1:8000/admin/
2. 使用管理员账号登录
3. 管理用户、文章、分类等

## 🔧 开发调试

### 后端调试
- Django Debug Toolbar 已启用
- 日志文件：`backend/logs/django.log`
- API文档：http://127.0.0.1:8000/api/swagger/（可选配置）

### 前端调试
- Vue DevTools 支持
- Hot Module Replacement
- Source Maps 已启用

## 📝 常见问题

### Q: 前端无法连接后端？
A: 确保后端运行在8000端口，检查CORS配置

### Q: 数据库错误？
A: 重新执行数据库迁移：
```bash
py manage.py makemigrations
py manage.py migrate
```

### Q: 缺少Node.js？
A: 下载安装Node.js：https://nodejs.org/

### Q: 依赖安装失败？
A: 尝试使用淘宝镜像：
```bash
npm install --registry=https://registry.npm.taobao.org
```

## 🎉 恭喜！

如果以上步骤都成功完成，您现在拥有一个完整的技术共享平台！

- ✅ 用户可以注册、登录
- ✅ 发布和管理文章
- ✅ 浏览和搜索内容
- ✅ 社交互动功能
- ✅ 响应式移动端支持

**开始享受您的技术分享之旅吧！** 🚀

---

如有问题，请查看 `FINAL_PROJECT_REPORT.md` 获取更多详细信息。