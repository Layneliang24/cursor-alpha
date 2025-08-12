# 🚀 项目启动修复指南

## ❌ 问题诊断

您遇到的启动问题是因为在**错误的目录**执行了启动命令：

### **问题1：后端启动失败**
```powershell
PS S:\WorkShop\cursor\alpha> python manage.py runserver 0.0.0.0:8000
# ❌ 错误：manage.py 在 backend/ 目录中，不在根目录
```

### **问题2：前端启动失败**  
```powershell
PS S:\WorkShop\cursor\alpha> npm run dev
# ❌ 错误：package.json 在 frontend/ 目录中，不在根目录
```

## ✅ 正确的启动方法

### **方法1：分别进入目录启动（推荐）**

#### **1. 启动后端服务**
```powershell
# 进入后端目录
cd backend

# 启动Django服务器
python manage.py runserver 0.0.0.0:8000
```

#### **2. 启动前端服务（新开一个终端窗口）**
```powershell
# 进入前端目录
cd frontend

# 启动Vite开发服务器
npm run dev
```

### **方法2：从根目录使用相对路径**

#### **1. 启动后端**
```powershell
# 在根目录执行
cd backend && python manage.py runserver 0.0.0.0:8000
```

#### **2. 启动前端**
```powershell
# 在根目录执行（新终端）
cd frontend && npm run dev
```

## 🛠️ 完整启动流程

### **第一步：检查环境**
```powershell
# 检查Python版本
python --version

# 检查Node.js版本  
node --version

# 检查npm版本
npm --version
```

### **第二步：安装依赖（如果还没安装）**

#### **后端依赖**
```powershell
cd backend
pip install -r requirements.txt
```

#### **前端依赖**
```powershell
cd frontend
npm install
```

### **第三步：数据库迁移（如果需要）**
```powershell
cd backend
python manage.py migrate
```

### **第四步：创建测试数据（可选）**
```powershell
cd backend
python manage.py create_test_learning_data
```

### **第五步：启动服务**

#### **终端1 - 后端**
```powershell
cd backend
python manage.py runserver 0.0.0.0:8000
```

#### **终端2 - 前端**  
```powershell
cd frontend
npm run dev
```

## 🌐 访问地址

启动成功后，您可以访问：

- **前端应用**: http://localhost:5173
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/api/docs/
- **Django管理后台**: http://localhost:8000/admin/

## 🔧 常见问题解决

### **问题1：端口被占用**
```powershell
# 查看端口使用情况
netstat -ano | findstr :8000
netstat -ano | findstr :5173

# 杀死占用端口的进程
taskkill /PID <进程ID> /F
```

### **问题2：依赖安装失败**
```powershell
# 清理npm缓存
npm cache clean --force

# 删除node_modules重新安装
cd frontend
rmdir /s node_modules
npm install
```

### **问题3：Python虚拟环境**
```powershell
# 如果使用虚拟环境，先激活
# Windows
venv\Scripts\activate

# 然后再安装依赖
pip install -r requirements.txt
```

## 📝 快速启动脚本

为了方便，我可以为您创建启动脚本：

### **start-backend.bat**
```batch
@echo off
cd backend
python manage.py runserver 0.0.0.0:8000
pause
```

### **start-frontend.bat**  
```batch
@echo off
cd frontend
npm run dev
pause
```

## 🎯 验证启动成功

### **后端验证**
```powershell
# 测试健康检查接口
curl http://localhost:8000/api/v1/health/
```

### **前端验证**
- 浏览器打开 http://localhost:5173
- 应该能看到项目首页

---

## 🚨 重要提醒

1. **必须分别启动**：前端和后端需要在不同的终端窗口中启动
2. **目录很重要**：确保在正确的目录中执行命令
3. **端口冲突**：如果端口被占用，需要先释放端口
4. **依赖完整**：确保所有依赖都已正确安装

**🌟 按照这个指南，您的项目应该能够正常启动！**
