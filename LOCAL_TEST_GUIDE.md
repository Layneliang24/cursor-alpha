# 🧪 Alpha 项目本地测试指南

## 🚀 一键启动（推荐）

### **Windows用户**
双击项目根目录下的启动脚本：
- **`start-all.bat`** - 一键启动前后端服务（推荐）
- **`start-backend.bat`** - 仅启动后端服务
- **`start-frontend.bat`** - 仅启动前端服务

### **前置要求**
- Python 3.8+
- Node.js 16+
- npm 或 yarn

## 📋 手动启动步骤

### **1. 启动后端服务**
```bash
# 进入后端目录
cd backend

# 安装依赖（首次运行）
pip install -r requirements.txt

# 数据库迁移
python manage.py migrate

# 创建测试数据（可选）
python manage.py create_test_learning_data

# 启动服务器
python manage.py runserver 0.0.0.0:8000
```

### **2. 启动前端服务**（新开一个终端）
```bash
# 进入前端目录
cd frontend

# 安装依赖（首次运行）
npm install

# 启动开发服务器
npm run dev
```

## 🌐 访问地址

启动成功后，您可以访问：
- **前端应用**: http://localhost:5173
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/api/docs/
- **Django管理后台**: http://localhost:8000/admin/

## 🧪 功能测试

### **导航测试**
1. ✅ 点击顶部导航"博客"下拉菜单
2. ✅ 点击顶部导航"英语学习"下拉菜单
3. ✅ 验证侧边菜单功能分组
4. ✅ 测试移动端响应式效果

### **英语学习模块测试**
1. ✅ 访问学习仪表板：http://localhost:5173/english/dashboard
2. ✅ 测试智能练习：http://localhost:5173/english/practice
3. ✅ 查看单词学习：http://localhost:5173/english/words
4. ✅ 浏览地道表达：http://localhost:5173/english/expressions
5. ✅ 阅读英语新闻：http://localhost:5173/english/news

### **API测试**
```bash
# 健康检查
curl http://localhost:8000/api/v1/health/

# 获取单词列表
curl http://localhost:8000/api/v1/english/words/

# 获取表达列表
curl http://localhost:8000/api/v1/english/expressions/
```

## 🔧 常见问题解决

### **问题1：端口被占用**
```bash
# 查看端口使用情况
netstat -ano | findstr :8000
netstat -ano | findstr :5173

# 杀死占用端口的进程
taskkill /PID <进程ID> /F
```

### **问题2：依赖安装失败**
```bash
# 清理npm缓存
npm cache clean --force

# 删除node_modules重新安装
cd frontend
rmdir /s node_modules
npm install
```

### **问题3：Python虚拟环境**
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境（Windows）
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### **问题4：数据库迁移错误**
```bash
# 删除迁移文件（如果需要）
cd backend
python manage.py migrate --fake-initial

# 重新创建迁移
python manage.py makemigrations
python manage.py migrate
```

## 🎯 测试用户账号

系统会自动创建以下测试账号：
- **用户名**: `testuser`
- **密码**: `testpass123`
- **邮箱**: `test@example.com`

## 📊 测试数据

系统会自动生成以下测试数据：
- ✅ 100个英语单词
- ✅ 50个地道表达
- ✅ 20篇英语新闻
- ✅ 用户学习进度记录
- ✅ 学习计划和统计数据

## 🚨 故障排除

如果遇到问题，请检查：
1. **Python和Node.js版本**是否符合要求
2. **网络连接**是否正常
3. **防火墙设置**是否阻止了端口访问
4. **磁盘空间**是否足够
5. **权限设置**是否正确

## 📞 获取帮助

如果仍然无法解决问题，请：
1. 查看终端错误信息
2. 检查日志文件
3. 参考项目文档
4. 提交问题反馈

---

**🌟 现在您可以开始测试Alpha项目的完整功能了！**