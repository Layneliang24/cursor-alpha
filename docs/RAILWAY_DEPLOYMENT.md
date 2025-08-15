# 🚂 Railway 部署指南

## 📋 部署前准备

### 1. 确保代码已提交
```bash
git add .
git commit -m "feat: 准备Railway部署"
git push origin main
```

### 2. 检查必要文件
- ✅ `railway.json` - Railway配置文件
- ✅ `backend/start.sh` - 启动脚本
- ✅ `backend/requirements.txt` - 包含psycopg2-binary
- ✅ `backend/alpha/production.py` - 生产环境配置

## 🚀 部署步骤

### 第一步：注册Railway账户
1. 访问 [https://railway.app](https://railway.app)
2. 点击 "Start a New Project"
3. 使用GitHub账户登录

### 第二步：创建项目
1. 选择 "Deploy from GitHub repo"
2. 选择您的 `cursor-alpha` 仓库
3. 点击 "Deploy Now"

### 第三步：配置环境变量
在Railway控制台中设置以下环境变量：

```bash
# 基本配置
DEBUG=False
SECRET_KEY=your-super-secret-key-here
DJANGO_SETTINGS_MODULE=alpha.production

# 数据库配置 (Railway会自动提供)
MYSQLDATABASE=railway
MYSQLUSER=root
MYSQLPASSWORD=your-password
MYSQLHOST=your-host
MYSQLPORT=3306

# 应用配置
ALLOWED_HOSTS=.railway.app
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app
```

### 第四步：添加数据库
1. 在Railway控制台点击 "New"
2. 选择 "Database" → "MySQL"
3. 等待数据库创建完成
4. 复制数据库连接信息到环境变量

### 第五步：配置域名
1. 在项目设置中找到 "Domains"
2. 点击 "Generate Domain"
3. 记录生成的域名 (例如: `your-app.railway.app`)

## 🔧 部署后配置

### 1. 检查部署状态
```bash
# 在Railway控制台查看日志
# 确保看到以下信息：
# ✅ 数据库迁移成功
# ✅ 静态文件收集成功
# ✅ Gunicorn启动成功
```

### 2. 访问应用
- **API地址**: `https://your-app.railway.app/api/`
- **管理后台**: `https://your-app.railway.app/admin/`
- **健康检查**: `https://your-app.railway.app/api/health/`

### 3. 创建超级用户
```bash
# 在Railway控制台的Shell中运行
python manage.py createsuperuser
```

## 📊 监控和维护

### 1. 查看日志
- 在Railway控制台查看实时日志
- 监控错误和性能问题

### 2. 资源监控
- 查看CPU、内存使用情况
- 监控网络流量
- 确保在免费额度内

### 3. 数据库管理
- 定期备份数据库
- 监控数据库连接数
- 优化查询性能

## 🛠️ 故障排除

### 常见问题

#### 1. 部署失败
```bash
# 检查日志中的错误信息
# 常见原因：
# - 环境变量未设置
# - 依赖包安装失败
# - 数据库连接失败
```

#### 2. 数据库连接问题
```bash
# 确保环境变量正确设置
# 检查数据库服务是否启动
# 验证连接字符串格式
```

#### 3. 静态文件问题
```bash
# 确保WhiteNoise中间件已添加
# 检查STATIC_ROOT配置
# 验证静态文件收集是否成功
```

### 调试命令
```bash
# 在Railway Shell中运行
python manage.py check
python manage.py showmigrations
python manage.py collectstatic --dry-run
```

## 🔄 更新部署

### 自动部署
- 每次推送到main分支会自动触发部署
- 确保测试通过后再推送

### 手动部署
```bash
# 在Railway控制台
1. 点击 "Deployments"
2. 选择 "Deploy Latest"
3. 等待部署完成
```

## 💰 成本控制

### 免费额度使用
- **每月免费额度**: $5
- **监控使用情况**: 在Railway控制台查看
- **优化建议**: 
  - 减少不必要的依赖
  - 优化应用性能
  - 使用缓存减少数据库查询

### 升级建议
- 如果超出免费额度，考虑升级到付费计划
- 或者迁移到其他免费平台

## 📞 支持

### 获取帮助
- **Railway文档**: https://docs.railway.app
- **Discord社区**: https://discord.gg/railway
- **GitHub Issues**: https://github.com/railwayapp/railway

### 联系信息
- 项目问题: 查看Railway控制台日志
- 平台问题: 联系Railway支持

---

**部署完成后，您的Alpha项目将在Railway上运行！** 🎉
