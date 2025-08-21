# 🚀 Alpha 项目热重载快速启动指南

## ✅ 问题已修复！

之前的启动脚本参数错误已经修复，现在可以正常使用了！

## 🔧 使用方法

### 1. 启动后端热重载服务

```bash
cd backend
python run_dev.py
# 或
run_dev.bat
```

**功能**：修改 Python 代码后，Django 服务器自动重启

### 2. 启动前端热重载服务

```bash
cd frontend
npm run dev
# 或
run_dev.bat
```

**功能**：修改 Vue 组件后，浏览器自动刷新

### 3. 使用统一启动器

```bash
# 在项目根目录
start_dev.bat
```

然后选择：
- 1：启动后端服务（Django + 热重载）
- 2：启动前端服务（Vite + 热重载）
- 3：启动前后端服务（需要两个终端）

## 🧪 测试热重载

### 后端测试
1. 启动后端：`python run_dev.py`
2. 修改 `backend/test_hot_reload.py` 文件
3. 观察控制台，应该显示重载信息

### 前端测试
1. 启动前端：`npm run dev`
2. 修改任意 Vue 组件
3. 观察浏览器，应该自动刷新

## 🔍 常见问题

### Q: 启动失败怎么办？
**A**: 脚本会自动降级到标准 Django 服务器

### Q: 热重载不工作？
**A**: 检查文件权限，确认 Django 版本支持

### Q: 端口被占用？
**A**: 使用 `netstat -an | findstr :8000` 检查，然后关闭占用进程

## 📚 详细文档

- [完整热重载指南](docs/HOT_RELOAD_GUIDE.md)
- [项目使用指南](docs/GUIDE.md)
- [API 文档](docs/API.md)

---

**状态**：✅ 热重载功能已修复并正常工作
**最后更新**：2024年12月
