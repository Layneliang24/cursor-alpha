# 部署运维指南

## 📋 目录
- [环境准备](#环境准备)
- [部署方式](#部署方式)
- [监控运维](#监控运维)
- [故障处理](#故障处理)
- [备份恢复](#备份恢复)

---

## 🛠️ 环境准备

### 生产环境要求

#### 硬件要求
- **CPU**: 2核心以上
- **内存**: 4GB以上
- **存储**: 50GB以上可用空间
- **网络**: 稳定的网络连接

#### 软件要求
- **操作系统**: Ubuntu 20.04+ / CentOS 7+ / Windows Server 2019+
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Nginx**: 1.18+
- **MySQL**: 8.0+
- **Redis**: 6.0+

#### 网络要求
- **域名**: 可选的域名配置
- **SSL证书**: HTTPS支持
- **防火墙**: 开放必要端口（80, 443, 8000, 3306, 6379）

### 环境变量配置

#### 复制环境变量模板
```bash
# 复制生产环境配置模板
cp production.env.example production.env

# 编辑配置文件
vim production.env
```

#### 关键配置项
```bash
# Django设置
DEBUG=False
SECRET_KEY=your_secret_key_here
ALLOWED_HOSTS=your-domain.com,localhost,127.0.0.1

# 数据库配置
DB_NAME=alpha_production
DB_USER=alpha_user
DB_PASSWORD=secure_password_here
DB_HOST=localhost
DB_PORT=3306

# Redis配置
REDIS_URL=redis://localhost:6379/0

# 媒体文件配置
MEDIA_ROOT=/var/www/alpha/media
STATIC_ROOT=/var/www/alpha/static

# 邮件配置
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

---

## 🚀 部署方式

### Docker部署（推荐）

#### 1. 构建生产镜像
```bash
# 构建所有服务镜像
docker-compose -f docker-compose.prod.yml build

# 或分别构建
docker-compose -f docker-compose.prod.yml build backend
docker-compose -f docker-compose.prod.yml build frontend
docker-compose -f docker-compose.prod.yml build nginx
```

#### 2. 启动生产服务
```bash
# 启动所有服务
docker-compose -f docker-compose.prod.yml up -d

# 检查服务状态
docker-compose -f docker-compose.prod.yml ps

# 查看服务日志
docker-compose -f docker-compose.prod.yml logs -f
```

#### 3. 数据库迁移
```bash
# 执行数据库迁移
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate

# 创建超级用户
docker-compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser

# 收集静态文件
docker-compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput
```

#### 4. 初始化数据
```bash
# 导入英语学习种子数据
docker-compose -f docker-compose.prod.yml exec backend python manage.py import_english_seed

# 创建测试数据（可选）
docker-compose -f docker-compose.prod.yml exec backend python manage.py create_test_data
```

### 传统部署

#### 1. 安装系统依赖
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nginx mysql-server redis-server

# CentOS/RHEL
sudo yum update -y
sudo yum install -y python3 python3-pip nginx mysql-server redis
```

#### 2. 配置Python环境
```bash
# 创建虚拟环境
cd backend
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 安装Gunicorn
pip install gunicorn
```

#### 3. 配置MySQL
```bash
# 启动MySQL服务
sudo systemctl start mysqld
sudo systemctl enable mysqld

# 安全配置
sudo mysql_secure_installation

# 创建数据库和用户
mysql -u root -p
```

```sql
CREATE DATABASE alpha_production CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'alpha_user'@'localhost' IDENTIFIED BY 'secure_password_here';
GRANT ALL PRIVILEGES ON alpha_production.* TO 'alpha_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

#### 4. 配置Redis
```bash
# 启动Redis服务
sudo systemctl start redis
sudo systemctl enable redis

# 测试连接
redis-cli ping
```

#### 5. 配置Nginx
```bash
# 复制Nginx配置
sudo cp nginx/nginx.conf /etc/nginx/sites-available/alpha

# 创建符号链接
sudo ln -s /etc/nginx/sites-available/alpha /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

#### 6. 配置系统服务
```bash
# 创建后端服务文件
sudo tee /etc/systemd/system/alpha-backend.service > /dev/null <<EOF
[Unit]
Description=Alpha Backend Service
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/alpha/backend
Environment=PATH=/var/www/alpha/backend/venv/bin
ExecStart=/var/www/alpha/backend/venv/bin/gunicorn --workers 3 --bind unix:/var/www/alpha/backend/alpha.sock alpha.wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 创建前端服务文件
sudo tee /etc/systemd/system/alpha-frontend.service > /dev/null <<EOF
[Unit]
Description=Alpha Frontend Service
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/alpha/frontend
ExecStart=/usr/bin/npm run preview
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 重新加载系统服务
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start alpha-backend
sudo systemctl start alpha-frontend
sudo systemctl enable alpha-backend
sudo systemctl enable alpha-frontend
```

### Kubernetes部署

#### 1. 应用配置
```bash
# 应用所有Kubernetes配置
kubectl apply -f k8s/

# 检查资源状态
kubectl get all -n alpha
```

#### 2. 配置持久化存储
```bash
# 创建持久化卷声明
kubectl apply -f k8s/storage/

# 检查存储状态
kubectl get pvc -n alpha
```

#### 3. 配置Ingress
```bash
# 应用Ingress配置
kubectl apply -f k8s/ingress.yaml

# 检查Ingress状态
kubectl get ingress -n alpha
```

---

## 📊 监控运维

### 健康检查

#### 应用健康检查
```bash
# 检查应用状态
curl http://your-domain.com/api/v1/health/

# 检查数据库连接
python manage.py check --database default

# 检查缓存连接
python manage.py shell -c "from django.core.cache import cache; print(cache.get('test'))"
```

#### Railway 部署（整合）
1) 绑定GitHub仓库并触发部署；2) 设置环境变量（如 `DJANGO_SETTINGS_MODULE=alpha.production`、`ALLOWED_HOSTS=.railway.app`）；3) 添加MySQL数据库并填充连接信息；4) 在Shell中创建超级用户并检查部署日志。

示例环境变量：
```
DEBUG=False
SECRET_KEY=your-super-secret-key-here
DJANGO_SETTINGS_MODULE=alpha.production
ALLOWED_HOSTS=.railway.app
```

#### 新机器快速部署（整合）
1) `python check_environment.py` 检查环境；2) 执行 `setup_project.bat` 或 `./setup_project.sh`；3) `python verify_tests.py` 验证测试结构、数据库连接、基础与集成测试、覆盖率。

#### MySQL部署检查清单（整合）
- 生产配置启用MySQL，依赖包含 `mysqlclient`
- 环境变量提供完整连接信息（库、用户、密码、主机、端口）
- 验证：迁移成功、静态文件收集、能创建超级用户、应用正常启动

#### 服务状态检查
```bash
# 检查Docker服务状态
docker-compose -f docker-compose.prod.yml ps

# 检查系统服务状态
sudo systemctl status alpha-backend
sudo systemctl status alpha-frontend
sudo systemctl status nginx
sudo systemctl status mysql
sudo systemctl status redis
```

### 日志管理

#### 查看应用日志
```bash
# 查看后端日志
docker-compose -f docker-compose.prod.yml logs -f backend

# 查看前端日志
docker-compose -f docker-compose.prod.yml logs -f frontend

# 查看Nginx日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# 查看系统服务日志
sudo journalctl -u alpha-backend -f
sudo journalctl -u alpha-frontend -f
```

#### 日志轮转配置
```bash
# 配置logrotate
sudo tee /etc/logrotate.d/alpha > /dev/null <<EOF
/var/log/alpha/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload alpha-backend
    endscript
}
EOF
```

### 性能监控

#### 系统资源监控
```bash
# 查看系统资源使用情况
htop
iotop
nethogs

# 查看磁盘使用情况
df -h
du -sh /var/www/alpha/*

# 查看内存使用情况
free -h
```

#### 应用性能监控
```bash
# 查看Django性能统计
python manage.py shell -c "from django.db import connection; print(connection.queries)"

# 查看数据库连接状态
mysql -u root -p -e "SHOW PROCESSLIST;"

# 查看Redis状态
redis-cli info
```

### 监控工具集成

#### Prometheus + Grafana
```bash
# 应用监控配置
kubectl apply -f k8s/monitoring/

# 或使用Docker Compose
docker-compose -f docker-compose.monitoring.yml up -d
```

#### 监控指标
- **系统指标**: CPU、内存、磁盘、网络
- **应用指标**: 请求响应时间、错误率、吞吐量
- **数据库指标**: 连接数、查询性能、锁等待
- **缓存指标**: 命中率、内存使用、过期策略

---

## 🔧 故障处理

### 常见问题

#### 1. 服务无法启动

**问题现象**
- 服务启动失败
- 端口被占用
- 配置文件错误

**排查步骤**
```bash
# 检查端口占用
sudo netstat -tlnp | grep :8000
sudo netstat -tlnp | grep :5173

# 检查配置文件
python manage.py check
nginx -t

# 查看错误日志
docker-compose -f docker-compose.prod.yml logs backend
sudo journalctl -u alpha-backend -n 50
```

**解决方案**
- 关闭占用端口的进程
- 修复配置文件错误
- 检查环境变量设置

#### 2. 数据库连接失败

**问题现象**
- 应用启动失败
- 数据库连接超时
- 权限错误

**排查步骤**
```bash
# 检查MySQL服务状态
sudo systemctl status mysql

# 测试数据库连接
mysql -u alpha_user -p -h localhost alpha_production

# 检查用户权限
mysql -u root -p -e "SHOW GRANTS FOR 'alpha_user'@'localhost';"
```

**解决方案**
- 启动MySQL服务
- 创建数据库用户
- 配置正确的连接参数

#### 3. 静态文件404错误

**问题现象**
- 图片无法显示
- CSS/JS文件加载失败
- 媒体文件访问错误

**排查步骤**
```bash
# 检查静态文件目录
ls -la /var/www/alpha/static/
ls -la /var/www/alpha/media/

# 检查Nginx配置
sudo nginx -t

# 重新收集静态文件
python manage.py collectstatic --noinput
```

**解决方案**
- 重新收集静态文件
- 检查Nginx配置
- 验证文件权限

#### 4. 新闻爬取网络问题

**问题现象**
- 爬虫无法访问外部网站
- 网络超时错误
- 代理配置问题

**排查步骤**
```bash
# 测试网络连接
curl -I https://www.bbc.com/news
ping www.bbc.com

# 检查代理设置
echo $http_proxy
echo $https_proxy

# 测试爬虫功能
python manage.py crawl_news --source local_test --crawler traditional --dry-run
```

**解决方案**
- 检查网络代理设置
- 使用本地测试源
- 配置网络防火墙规则

### 故障恢复流程

#### 1. 问题识别
- 收集错误信息
- 分析日志文件
- 确定影响范围

#### 2. 紧急处理
- 停止问题服务
- 回滚到稳定版本
- 启用备用方案

#### 3. 问题修复
- 定位根本原因
- 实施修复方案
- 验证修复效果

#### 4. 服务恢复
- 逐步启动服务
- 监控服务状态
- 确认功能正常

---

## 💾 备份恢复
> 提示：本章节已拆分为独立文档，详见 `operations/BACKUP.md`（此处保留可快速执行的摘要与脚本示例）。

### 数据备份策略

#### 数据库备份
```bash
# 创建备份脚本
sudo tee /usr/local/bin/backup_alpha_db.sh > /dev/null <<EOF
#!/bin/bash
BACKUP_DIR="/var/backups/alpha"
DATE=\$(date +%Y%m%d_%H%M%S)
DB_NAME="alpha_production"
DB_USER="alpha_user"
DB_PASS="your_password_here"

# 创建备份目录
mkdir -p \$BACKUP_DIR

# 备份数据库
mysqldump -u \$DB_USER -p\$DB_PASS \$DB_NAME > \$BACKUP_DIR/\${DB_NAME}_\${DATE}.sql

# 压缩备份文件
gzip \$BACKUP_DIR/\${DB_NAME}_\${DATE}.sql

# 删除7天前的备份
find \$BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

echo "Database backup completed: \${DB_NAME}_\${DATE}.sql.gz"
EOF

# 设置执行权限
sudo chmod +x /usr/local/bin/backup_alpha_db.sh

# 添加到定时任务
sudo crontab -e
# 添加以下行：每天凌晨2点执行备份
0 2 * * * /usr/local/bin/backup_alpha_db.sh
```

#### 文件备份
```bash
# 创建文件备份脚本
sudo tee /usr/local/bin/backup_alpha_files.sh > /dev/null <<EOF
#!/bin/bash
BACKUP_DIR="/var/backups/alpha"
DATE=\$(date +%Y%m%d_%H%M%S)
SOURCE_DIR="/var/www/alpha"

# 创建备份目录
mkdir -p \$BACKUP_DIR

# 备份媒体文件
tar -czf \$BACKUP_DIR/media_\${DATE}.tar.gz -C \$SOURCE_DIR media/

# 备份代码文件
tar -czf \$BACKUP_DIR/code_\${DATE}.tar.gz -C \$SOURCE_DIR --exclude=venv --exclude=node_modules .

# 删除30天前的备份
find \$BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Files backup completed"
EOF

# 设置执行权限
sudo chmod +x /usr/local/bin/backup_alpha_files.sh

# 添加到定时任务
sudo crontab -e
# 添加以下行：每周日凌晨3点执行备份
0 3 * * 0 /usr/local/bin/backup_alpha_files.sh
```

### 数据恢复流程

#### 数据库恢复
```bash
# 恢复数据库
mysql -u alpha_user -p alpha_production < backup_file.sql

# 或使用gunzip解压后恢复
gunzip -c backup_file.sql.gz | mysql -u alpha_user -p alpha_production
```

#### 文件恢复
```bash
# 恢复媒体文件
tar -xzf media_backup.tar.gz -C /var/www/alpha/

# 恢复代码文件
tar -xzf code_backup.tar.gz -C /var/www/alpha/
```

### 备份验证

#### 定期验证
```bash
# 验证数据库备份
mysql -u alpha_user -p -e "USE alpha_production; SHOW TABLES;"

# 验证文件备份
ls -la /var/backups/alpha/
du -sh /var/backups/alpha/*
```

---

## 📈 扩展优化
> 提示：本章节已拆分为独立文档，详见 `operations/SCALING.md`（此处保留关键示例与片段）。

### 性能优化

#### 数据库优化
```sql
-- 添加索引
CREATE INDEX idx_article_created_at ON articles_article(created_at);
CREATE INDEX idx_article_author ON articles_article(author_id);
CREATE INDEX idx_article_category ON articles_article(category_id);

-- 优化查询
EXPLAIN SELECT * FROM articles_article WHERE author_id = 1 ORDER BY created_at DESC;
```

#### 缓存优化
```python
# 使用Redis缓存
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# 缓存装饰器
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)  # 缓存15分钟
def article_list(request):
    # 视图逻辑
    pass
```

#### 前端优化
```javascript
// 代码分割
const ArticleList = lazy(() => import('./ArticleList'));

// 图片懒加载
<img src={imageUrl} loading="lazy" alt={alt} />

// 缓存策略
const cache = new Map();
const getCachedData = async (key) => {
    if (cache.has(key)) {
        return cache.get(key);
    }
    const data = await fetchData(key);
    cache.set(key, data);
    return data;
};
```

### 负载均衡

#### Nginx负载均衡
```nginx
upstream alpha_backend {
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
}

server {
    listen 80;
    server_name your-domain.com;
    
    location /api/ {
        proxy_pass http://alpha_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### Docker Swarm
```bash
# 初始化Swarm
docker swarm init

# 部署服务
docker stack deploy -c docker-compose.swarm.yml alpha
```

### 自动扩缩容

#### Kubernetes HPA
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: alpha-backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: alpha-backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

---

## 附录：低配服务器部署要点

- 系统：低配主机建议开启 1GB swap（峰值缓冲），谨慎使用已 EOL 的发行版（如 CentOS 7）并固定依赖版本。
- Compose：可使用独立二进制（如 1.29.2）部署最小化编排；镜像按需裁剪，禁用不必要组件。
- 服务参数：Gunicorn `workers=2`、`timeout=60`；Celery `concurrency=1`、`prefetch=1`；限制上传大小与连接数。
- 存储：将 `/media`、`/static`、数据库与缓存数据卷落盘到 `/opt/alpha/data/`；日志滚动与保留策略 7–14 天。
- 回滚：使用上一个 tag 重新 `up`；数据库做好周期备份与恢复演练（详见 `operations/BACKUP.md`）。

## 📞 支持

### 运维支持
- 查看 [开发者指南](../DEVELOPMENT.md) 了解系统架构
- 参考 [模块文档](../modules/) 理解功能实现
- 查看 [常见问题](../FAQ.md) 解决运维问题

### 紧急联系
- 系统管理员: admin@your-domain.com
- 技术支持: support@your-domain.com
- 紧急热线: +86-xxx-xxxx-xxxx

---

*最后更新：2025-01-17*
*更新内容：整合现有部署文档，创建完整的部署运维指南；合入 Railway/新机器/MySQL 清单要点；备份/扩展拆分至 operations/* 并在此保留摘要*
