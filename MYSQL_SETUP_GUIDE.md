# MySQL 数据库设置指南

## 概述

项目已从 SQLite 切换到 MySQL 8.0 数据库，提供更好的性能和扩展性。

## 数据库配置

### 默认配置
- **数据库引擎**: MySQL 8.0
- **数据库名**: `alpha_db`
- **用户名**: `alpha_user`
- **密码**: `alphapassword123`
- **主机**: `127.0.0.1`
- **端口**: `3306` (本地) / `3307` (Docker)

### 环境变量支持
可以通过环境变量自定义配置：
```bash
DB_NAME=alpha_db
DB_USER=alpha_user
DB_PASSWORD=your_password
DB_HOST=127.0.0.1
DB_PORT=3306
```

## 快速启动

### 方法一：使用 Docker (推荐)
```bash
# 启动 MySQL 服务
docker-compose up -d mysql

# 等待服务启动后，运行迁移
cd backend
python manage.py migrate

# 创建超级用户
python manage.py create_superuser_if_not_exists

# 启动后端服务
python manage.py runserver
```

### 方法二：使用脚本
```bash
# Windows
switch_to_mysql.bat

# PowerShell
.\switch_to_mysql.ps1
```

### 方法三：手动步骤
1. 确保 MySQL 服务运行
2. 创建数据库和用户（如果使用本地 MySQL）
3. 安装依赖：`pip install -r backend/requirements.txt`
4. 运行迁移：`python manage.py migrate`
5. 创建超级用户：`python manage.py createsuperuser`

## 测试连接

运行测试脚本验证数据库连接：
```bash
python test_mysql_connection.py
```

## 故障排除

### 常见问题

1. **连接被拒绝**
   - 检查 MySQL 服务是否运行
   - 验证主机和端口配置
   - 确认防火墙设置

2. **认证失败**
   - 检查用户名和密码
   - 确认用户权限
   - 验证数据库是否存在

3. **字符集问题**
   - 确保使用 utf8mb4 字符集
   - 检查数据库初始化脚本

### 重置数据库
```bash
# 删除所有表
python manage.py flush

# 重新运行迁移
python manage.py migrate

# 重新创建超级用户
python manage.py create_superuser_if_not_exists
```

## 备份和恢复

### 备份数据库
```bash
# Docker 环境
docker exec alpha_mysql mysqldump -u alpha_user -p alphapassword123 alpha_db > backup.sql

# 本地 MySQL
mysqldump -u alpha_user -p alphapassword123 alpha_db > backup.sql
```

### 恢复数据库
```bash
# Docker 环境
docker exec -i alpha_mysql mysql -u alpha_user -p alphapassword123 alpha_db < backup.sql

# 本地 MySQL
mysql -u alpha_user -p alphapassword123 alpha_db < backup.sql
```

## 性能优化

1. **索引优化**: 根据查询模式添加适当的数据库索引
2. **连接池**: 考虑使用连接池提高性能
3. **查询优化**: 使用 Django Debug Toolbar 分析慢查询
4. **缓存策略**: 实现适当的缓存机制

## 安全建议

1. **强密码**: 使用强密码并定期更换
2. **最小权限**: 数据库用户只授予必要权限
3. **网络安全**: 限制数据库访问来源
4. **定期备份**: 建立自动备份机制
5. **监控**: 设置数据库监控和告警
