# 🗄️ MySQL部署检查清单

## 📋 部署前检查

### 1. 代码配置
- [ ] `backend/alpha/production.py` 使用MySQL配置
- [ ] `backend/requirements.txt` 包含 `mysqlclient`
- [ ] `railway.json` 使用 `start.sh` 启动脚本
- [ ] `backend/start.sh` 可执行权限

### 2. 数据库配置
```python
# 确认production.py中的配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('MYSQLDATABASE', 'railway'),
        'USER': os.environ.get('MYSQLUSER', 'root'),
        'PASSWORD': os.environ.get('MYSQLPASSWORD'),
        'HOST': os.environ.get('MYSQLHOST'),
        'PORT': os.environ.get('MYSQLPORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES', time_zone='+08:00'",
        },
    }
}
```

## 🚀 Railway部署步骤

### 第一步：创建项目
1. 访问 https://railway.app
2. 点击 "Start a New Project"
3. 选择 "Deploy from GitHub repo"
4. 选择您的 `cursor-alpha` 仓库

### 第二步：添加MySQL数据库
1. 在Railway控制台点击 "New"
2. 选择 "Database" → "MySQL"
3. 等待数据库创建完成
4. 记录数据库连接信息

### 第三步：配置环境变量
在Railway控制台设置以下环境变量：

```bash
# 基本配置
DEBUG=False
SECRET_KEY=your-super-secret-key-here
DJANGO_SETTINGS_MODULE=alpha.production

# MySQL数据库配置 (Railway自动提供)
MYSQLDATABASE=railway
MYSQLUSER=root
MYSQLPASSWORD=your-password
MYSQLHOST=your-host
MYSQLPORT=3306

# 应用配置
ALLOWED_HOSTS=.railway.app
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app
```

### 第四步：部署应用
1. 确保代码已推送到GitHub
2. Railway会自动检测并开始部署
3. 查看部署日志确保成功

## 🔧 部署后验证

### 1. 检查部署状态
```bash
# 在Railway控制台查看日志
# 确保看到以下信息：
# ✅ MySQL数据库连接成功
# ✅ 数据库迁移成功
# ✅ 静态文件收集成功
# ✅ Gunicorn启动成功
```

### 2. 访问应用
- **API地址**: `https://your-app.railway.app/api/`
- **管理后台**: `https://your-app.railway.app/admin/`
- **健康检查**: `https://your-app.railway.app/api/health/`

### 3. 数据库验证
```bash
# 在Railway Shell中运行
python manage.py dbshell
# 应该能连接到MySQL数据库
```

### 4. 创建超级用户
```bash
# 在Railway控制台的Shell中运行
python manage.py createsuperuser
```

## 🛠️ 故障排除

### 常见MySQL问题

#### 1. 数据库连接失败
```bash
# 检查环境变量
echo $MYSQLHOST
echo $MYSQLUSER
echo $MYSQLPASSWORD

# 测试连接
python manage.py check --database default
```

#### 2. 字符集问题
```python
# 确保MySQL配置包含
'OPTIONS': {
    'charset': 'utf8mb4',
    'init_command': "SET sql_mode='STRICT_TRANS_TABLES', time_zone='+08:00'",
}
```

#### 3. 权限问题
```bash
# 确保MySQL用户有足够权限
# Railway会自动配置正确的权限
```

### 调试命令
```bash
# 在Railway Shell中运行
python manage.py check
python manage.py showmigrations
python manage.py dbshell
```

## 📊 MySQL优势

### 相比PostgreSQL的优势
- ✅ **熟悉度**: 更多开发者熟悉MySQL
- ✅ **资源占用**: 通常比PostgreSQL占用更少内存
- ✅ **免费额度**: Railway MySQL可能更节省资源
- ✅ **兼容性**: 与现有代码兼容性更好

### 注意事项
- ⚠️ **功能限制**: MySQL某些高级功能不如PostgreSQL
- ⚠️ **性能**: 复杂查询性能可能不如PostgreSQL
- ⚠️ **扩展性**: 大规模应用可能需要考虑PostgreSQL

## 💰 成本优化

### MySQL资源优化
- **连接池**: 合理配置数据库连接数
- **查询优化**: 使用索引优化查询性能
- **缓存策略**: 使用Django缓存减少数据库查询

### 监控建议
- 监控数据库连接数
- 监控查询性能
- 定期备份数据库

---

**MySQL部署配置完成！您的Alpha项目将使用MySQL数据库在Railway上运行。** 🎉
