# Alpha 项目热重载开发指南

## 📋 概述

本指南介绍如何在 Alpha 项目中使用热重载功能，提升开发效率。

## 🚀 热重载功能特性

### 后端热重载
- ✅ **自动重载**：修改 Python 代码后，Django 服务器自动重启
- ✅ **文件监控**：实时监控代码文件变化
- ✅ **智能降级**：热重载失败时自动降级到标准模式
- ✅ **错误提示**：启动失败时提供详细错误信息

### 前端热重载
- ✅ **HMR 支持**：修改 Vue 组件后，浏览器自动刷新
- ✅ **实时更新**：样式、脚本、组件变更即时生效
- ✅ **错误覆盖**：编译错误直接在浏览器中显示
- ✅ **快速响应**：毫秒级更新，开发体验流畅

## 🔧 使用方法

### 1. 启动后端热重载服务

#### 方式一：使用 Python 脚本（推荐）
```bash
cd backend
python run_dev.py
```

#### 方式二：使用批处理文件
```bash
cd backend
run_dev.bat
```

#### 方式三：手动命令
```bash
cd backend
python manage.py runserver_plus --reloader-type=stat 0.0.0.0:8000
```

### 2. 启动前端热重载服务

#### 方式一：使用批处理文件
```bash
cd frontend
run_dev.bat
```

#### 方式二：使用 npm 命令
```bash
cd frontend
npm run dev
```

### 3. 使用统一启动器

在项目根目录运行：
```bash
start_dev.bat
```

然后选择：
- 1：启动后端服务（Django + 热重载）
- 2：启动前端服务（Vite + 热重载）
- 3：启动前后端服务（需要两个终端）

## 📁 文件结构

```
alpha/
├── start_dev.bat              # 统一启动器
├── backend/
│   ├── run_dev.py            # 后端热重载启动脚本
│   ├── run_dev.bat           # 后端启动批处理文件
│   └── test_hot_reload.py    # 热重载测试文件
└── frontend/
    ├── run_dev.bat           # 前端启动批处理文件
    └── vite.config.js        # Vite 配置文件（已优化）
```

## 🧪 测试热重载功能

### 后端测试
1. 启动后端服务：`python run_dev.py`
2. 修改 `backend/test_hot_reload.py` 文件
3. 观察控制台输出，应该显示重载信息

### 前端测试
1. 启动前端服务：`npm run dev`
2. 修改任意 Vue 组件
3. 观察浏览器，应该自动刷新

## ⚠️ 注意事项

### 后端热重载限制
- **模型变更**：修改数据库模型后仍需执行 `python manage.py migrate`
- **设置文件**：修改 `settings.py` 后需要手动重启
- **静态文件**：静态文件变更不会触发重载

### 前端热重载限制
- **配置文件**：修改 `vite.config.js` 后需要重启
- **依赖变更**：安装新依赖后需要重启
- **环境变量**：环境变量变更需要重启

## 🔍 故障排除

### 后端热重载问题

#### 问题1：runserver_plus 命令不存在
**解决方案**：
```bash
pip install django-extensions
```

#### 问题2：热重载不工作
**解决方案**：
1. 检查 `django_extensions` 是否在 `INSTALLED_APPS` 中
2. 尝试使用 `--reloader-type=stat` 参数（Windows 兼容）
3. 检查文件权限
4. 确认地址端口格式为 `0.0.0.0:8000`

#### 问题3：端口被占用
**解决方案**：
```bash
# 检查端口占用
netstat -an | findstr :8000

# 关闭占用进程
taskkill /PID <进程ID> /F
```

### 前端热重载问题

#### 问题1：HMR 不工作
**解决方案**：
1. 检查浏览器控制台是否有错误
2. 确认 Vite 配置正确
3. 尝试刷新页面

#### 问题2：代理配置问题
**解决方案**：
检查 `vite.config.js` 中的代理配置是否正确

## 📚 相关文档

- [项目指南](GUIDE.md) - 完整的项目使用指南
- [API 文档](API.md) - 后端 API 接口文档
- [测试指南](TEST_GUIDE.md) - 测试相关说明

## 🤝 贡献

如果你发现热重载功能的问题或有改进建议，请：
1. 在 GitHub 上提交 Issue
2. 或者联系开发团队

---

**最后更新**：2024年12月
**维护者**：Alpha 开发团队
