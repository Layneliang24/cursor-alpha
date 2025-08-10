# Alpha技术共享平台 - Linux生产环境部署指南

## 📋 系统要求

### 服务器配置
- **操作系统**: Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- **CPU**: 2核心以上
- **内存**: 4GB以上
- **存储**: 50GB以上SSD
- **网络**: 公网IP，开放80/443端口

### 软件要求
- Docker 20.10+
- Docker Compose 2.0+
- Git
- Curl

## 🚀 快速部署

### 1. 服务器初始化

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装必要软件
sudo apt install -y git curl wget vim

# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 重新登录以应用Docker组权限
```

### 2. 克隆项目

```bash
git clone https://github.com/your-username/alpha.git
cd alpha
```

### 3. 配置环境变量

```bash
# 复制环境变量模板
cp production.env production.env.local

# 编辑配置文件
vim production.env.local
```

**重要配置项**：
```bash
# 数据库密码（必须修改）
MYSQL_ROOT_PASSWORD=your_secure_root_password
MYSQL_PASSWORD=your_secure_db_password

# Django密钥（必须修改）
DJANGO_SECRET_KEY=your_very_long_and_secure_secret_key

# 域名配置
DJANGO_ALLOWED_HOSTS=your-domain.com,www.your-domain.com,your-server-ip

# 管理员账号
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@your-domain.com
DJANGO_SUPERUSER_PASSWORD=your_secure_admin_password
```

### 4. 配置域名

编辑 `frontend/nginx.prod.conf`：
```nginx
server_name your-domain.com www.your-domain.com;
```

### 5. 执行部署

```bash
# 给脚本执行权限
chmod +x deploy.sh setup-ssl.sh backup.sh monitor.sh

# 执行部署
./deploy.sh
```

### 6. 申请SSL证书

```bash
# 申请Let's Encrypt证书
./setup-ssl.sh your-domain.com admin@your-domain.com
```

### 7. 重新部署启用HTTPS

```bash
./deploy.sh
```

## 🔧 高级配置

### 防火墙设置

```bash
# UFW防火墙
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable
```

### 系统优化

```bash
# 增加文件描述符限制
echo "* soft nofile 65535" | sudo tee -a /etc/security/limits.conf
echo "* hard nofile 65535" | sudo tee -a /etc/security/limits.conf

# 优化内核参数
echo "net.core.somaxconn = 65535" | sudo tee -a /etc/sysctl.conf
echo "net.ipv4.tcp_max_syn_backlog = 65535" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

### 监控设置

```bash
# 设置定时监控
(crontab -l 2>/dev/null; echo "*/5 * * * * /path/to/alpha/monitor.sh") | crontab -

# 设置定时备份
(crontab -l 2>/dev/null; echo "0 2 * * * /path/to/alpha/backup.sh") | crontab -
```

## 📊 性能优化

### 数据库优化

编辑 `mysql/conf.d/mysql.cnf`：
```ini
# 根据服务器内存调整
innodb_buffer_pool_size = 512M  # 服务器内存的70%

# 连接数优化
max_connections = 500
```

### Nginx优化

```nginx
# 在nginx.prod.conf中添加
worker_processes auto;
worker_connections 1024;

# 启用HTTP/2
listen 443 ssl http2;

# 启用Gzip压缩
gzip_comp_level 6;
```

### Django优化

在 `backend/alpha/settings.py` 中：
```python
# 缓存配置
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://redis:6379/1',
    }
}

# 会话存储
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
```

## 🔐 安全配置

### 1. 服务器安全

```bash
# 禁用root登录
sudo sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl restart sshd

# 安装fail2ban
sudo apt install fail2ban
```

### 2. 应用安全

- 定期更新Docker镜像
- 使用强密码
- 启用HTTPS
- 配置安全头
- 定期备份数据

## 📈 监控和日志

### 日志位置
- Nginx日志: `./logs/nginx/`
- Django日志: `./logs/`
- MySQL日志: Docker容器内

### 查看日志
```bash
# 查看所有服务日志
docker-compose -f docker-compose.prod.yml logs -f

# 查看特定服务日志
docker-compose -f docker-compose.prod.yml logs -f backend
```

### 监控指标
- 容器状态
- 服务响应时间
- 磁盘使用率
- 内存使用率
- 数据库连接

## 🛠️ 故障排除

### 常见问题

1. **容器启动失败**
   ```bash
   docker-compose -f docker-compose.prod.yml logs [service_name]
   ```

2. **数据库连接失败**
   ```bash
   docker exec -it alpha_mysql_prod mysql -u root -p
   ```

3. **SSL证书问题**
   ```bash
   sudo certbot certificates
   sudo certbot renew --dry-run
   ```

4. **磁盘空间不足**
   ```bash
   docker system prune -a
   docker volume prune
   ```

### 紧急恢复

```bash
# 从备份恢复数据库
docker exec -i alpha_mysql_prod mysql -u root -p alpha_db < backup.sql

# 恢复媒体文件
tar -xzf media_backup.tar.gz -C backend/
```

## 📞 技术支持

- **文档**: [项目README](./README.md)
- **问题反馈**: [GitHub Issues](https://github.com/your-username/alpha/issues)
- **邮箱**: admin@your-domain.com

---

© 2024 Alpha技术共享平台. 保留所有权利。

