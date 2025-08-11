# Alpha技术共享平台 - Linux云服务器扩容指南（小内存适配版）

## 📋 扩容方案概览

### 方案1：小内存服务器优化扩容（当前适配）
- **适用场景**：1-2GB内存服务器，用户量增长但资源有限
- **优势**：资源占用低，适合小服务器
- **配置**：单实例 + 负载均衡 + 小内存缓存

### 方案2：标准扩容（需要8GB+内存）
- **适用场景**：高并发、高可用需求
- **优势**：可扩展性强，容错性好
- **配置**：多服务器 + 集群 + 分布式存储

## 🚀 小内存服务器扩容部署步骤

### 步骤1：检查服务器资源

**命令**：
```bash
# 检查内存（当前1.7GB，适配小内存配置）
free -h

# 检查磁盘空间（至少20GB）
df -h

# 检查CPU核心数
nproc

# 检查系统负载
uptime
```

**作用**：确认服务器资源，适配小内存配置

### 步骤2：备份现有数据

**命令**：
```bash
# 备份数据库
docker exec alpha_mysql_prod mysqldump -u root -p${MYSQL_ROOT_PASSWORD} alpha_db > backup_$(date +%Y%m%d_%H%M%S).sql

# 备份项目文件
tar -czf project_backup_$(date +%Y%m%d_%H%M%S).tar.gz . --exclude=node_modules --exclude=.git

# 备份Docker卷
docker run --rm -v alpha_mysql_data:/data -v $(pwd):/backup alpine tar czf /backup/mysql_data_backup_$(date +%Y%m%d_%H%M%S).tar.gz -C /data .
```

**作用**：防止扩容过程中数据丢失

### 步骤3：配置环境变量

**命令**：
```bash
# 复制环境变量模板
cp production.env production.env.local

# 编辑环境变量文件
vim production.env.local
```

**production.env.local 重要配置项**：
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

**作用**：配置扩容服务所需的环境变量

### 步骤4：创建必要目录

**命令**：
```bash
# 创建日志目录
mkdir -p logs/nginx

# 创建Nginx配置目录
mkdir -p nginx/conf.d

# 创建SSL证书目录
mkdir -p ssl

# 设置目录权限
chmod 755 logs nginx ssl
```

**作用**：为扩容服务创建必要的目录结构

### 步骤5：停止现有服务

**命令**：
```bash
# 停止现有生产服务
docker-compose -f docker-compose.prod.yml down

# 检查是否还有容器运行
docker ps -a
```

**作用**：释放端口和资源，为扩容部署做准备

### 步骤6：给脚本执行权限

**命令**：
```bash
# 给扩容脚本执行权限
chmod +x deploy-scale.sh monitor-scale.sh

# 验证权限
ls -la deploy-scale.sh monitor-scale.sh
```

**作用**：确保脚本可以正常执行

### 步骤7：执行扩容部署

**命令**：
```bash
# 执行扩容部署脚本
./deploy-scale.sh
```

**脚本执行过程**：
1. 检查环境变量文件
2. 创建必要目录
3. 停止现有服务
4. 构建扩容服务镜像
5. 启动扩容服务
6. 等待服务启动
7. 检查服务状态
8. 健康检查
9. 显示资源使用情况

**作用**：自动化完成扩容部署流程

### 步骤8：验证扩容效果

**命令**：
```bash
# 检查服务状态
docker-compose -f docker-compose.scale.yml ps

# 查看容器资源使用
docker stats --no-stream

# 测试负载均衡
curl -I http://localhost/api/health/

# 测试前端访问
curl -I http://localhost/

# 检查Nginx配置
docker exec alpha_nginx_scale nginx -t
```

**作用**：确认扩容服务正常运行

### 步骤9：监控服务状态

**命令**：
```bash
# 执行监控脚本
./monitor-scale.sh

# 实时查看日志
docker-compose -f docker-compose.scale.yml logs -f

# 查看特定服务日志
docker-compose -f docker-compose.scale.yml logs -f backend
docker-compose -f docker-compose.scale.yml logs -f nginx
```

**作用**：监控扩容服务的运行状态和性能

## 🔧 扩容管理命令详解

### 服务管理命令

**启动扩容服务**：
```bash
docker-compose -f docker-compose.scale.yml up -d
```
**作用**：后台启动所有扩容服务

**停止扩容服务**：
```bash
docker-compose -f docker-compose.scale.yml down
```
**作用**：停止并移除所有扩容服务

**重启服务**：
```bash
docker-compose -f docker-compose.scale.yml restart
```
**作用**：重启所有扩容服务

**查看服务状态**：
```bash
docker-compose -f docker-compose.scale.yml ps
```
**作用**：显示所有服务的运行状态

### 实例管理命令

**扩展后端实例**（仅在有足够内存时）：
```bash
docker-compose -f docker-compose.scale.yml up -d --scale backend=2
```
**作用**：将后端实例数量扩展到2个（需要额外512MB内存）

**扩展前端实例**（仅在有足够内存时）：
```bash
docker-compose -f docker-compose.scale.yml up -d --scale frontend=2
```
**作用**：将前端实例数量扩展到2个（需要额外128MB内存）

**查看实例状态**：
```bash
docker-compose -f docker-compose.scale.yml ps
```
**作用**：查看所有实例的运行状态

### 日志管理命令

**查看所有服务日志**：
```bash
docker-compose -f docker-compose.scale.yml logs -f
```
**作用**：实时查看所有服务的日志输出

**查看特定服务日志**：
```bash
docker-compose -f docker-compose.scale.yml logs -f backend
docker-compose -f docker-compose.scale.yml logs -f nginx
docker-compose -f docker-compose.scale.yml logs -f mysql
docker-compose -f docker-compose.scale.yml logs -f redis
```
**作用**：查看特定服务的日志

**查看最近日志**：
```bash
docker-compose -f docker-compose.scale.yml logs --tail=100 backend
```
**作用**：查看后端服务最近100行日志

### 资源监控命令

**查看容器资源使用**：
```bash
docker stats --no-stream
```
**作用**：显示所有容器的CPU、内存、网络使用情况

**实时监控资源**：
```bash
docker stats
```
**作用**：实时监控容器资源使用情况

**查看系统资源**：
```bash
# 查看系统负载
uptime

# 查看内存使用
free -h

# 查看磁盘使用
df -h

# 查看CPU使用
top
```
**作用**：监控系统整体资源使用情况

## 📊 小内存扩容配置详解

### 后端扩容配置

**实例配置**：
- 实例数：1个（适配小内存）
- 工作进程：2个/实例（降低内存占用）
- 内存限制：512MB/实例
- CPU限制：0.5核/实例

**Gunicorn配置**：
```bash
gunicorn --bind 0.0.0.0:8000 --workers 2 --timeout 120 --max-requests 500 --max-requests-jitter 50 alpha.wsgi:application
```
**参数说明**：
- `--workers 2`：每个实例启动2个工作进程（降低内存占用）
- `--timeout 120`：请求超时时间120秒
- `--max-requests 500`：每个工作进程处理500个请求后重启
- `--max-requests-jitter 50`：随机抖动，避免同时重启

### 前端扩容配置

**实例配置**：
- 实例数：1个（适配小内存）
- 内存限制：128MB/实例
- CPU限制：0.25核/实例

**负载均衡**：
- 算法：最少连接数（least_conn）
- 健康检查：max_fails=3, fail_timeout=30s

### 数据库优化配置

**MySQL配置**：
```bash
--innodb-buffer-pool-size=256M --max-connections=100
```
**参数说明**：
- `innodb-buffer-pool-size=256M`：InnoDB缓冲池大小256MB（适配小内存）
- `max-connections=100`：最大连接数100（降低内存占用）

**资源限制**：
- 内存限制：512MB
- CPU限制：0.5核
- 内存预留：256MB
- CPU预留：0.25核

### 缓存层配置

**Redis配置**：
```bash
redis-server --appendonly yes --maxmemory 64mb --maxmemory-policy allkeys-lru
```
**参数说明**：
- `--appendonly yes`：启用AOF持久化
- `--maxmemory 64mb`：最大内存64MB（适配小内存）
- `--maxmemory-policy allkeys-lru`：内存满时使用LRU淘汰策略

**资源限制**：
- 内存限制：128MB
- CPU限制：0.25核

### Nginx负载均衡配置

**上游服务器配置**：
```nginx
upstream backend_servers {
    least_conn;  # 最少连接数负载均衡
    server backend:8000 max_fails=3 fail_timeout=30s;
}

upstream frontend_servers {
    least_conn;
    server frontend:80 max_fails=3 fail_timeout=30s;
}
```

**负载均衡算法**：
- `least_conn`：最少连接数算法
- `max_fails=3`：最大失败次数3次
- `fail_timeout=30s`：失败超时时间30秒

## 🔍 故障排查指南

### 1. 服务无法启动

**检查端口占用**：
```bash
netstat -tlnp | grep :80
netstat -tlnp | grep :443
netstat -tlnp | grep :8000
```

**检查资源使用**：
```bash
docker system df
docker system prune -a
```

**检查容器状态**：
```bash
docker-compose -f docker-compose.scale.yml ps
docker-compose -f docker-compose.scale.yml logs [service_name]
```

### 2. 内存不足问题

**检查内存使用**：
```bash
free -h
docker stats --no-stream
```

**优化内存使用**：
```bash
# 清理Docker缓存
docker system prune -a

# 重启内存占用高的服务
docker-compose -f docker-compose.scale.yml restart backend
```

### 3. 性能问题排查

**检查CPU使用**：
```bash
top
htop
```

**检查内存使用**：
```bash
free -h
cat /proc/meminfo
```

**检查磁盘IO**：
```bash
iostat -x 1
iotop
```

**检查网络连接**：
```bash
netstat -an | grep ESTABLISHED | wc -l
ss -tuln
```

### 4. 数据库问题排查

**检查数据库连接**：
```bash
docker exec alpha_mysql_scale mysqladmin ping -h localhost -u root -p${MYSQL_ROOT_PASSWORD}
```

**查看慢查询**：
```bash
docker exec alpha_mysql_scale mysql -e "SHOW PROCESSLIST;"
```

**检查数据库大小**：
```bash
docker exec alpha_mysql_scale mysql -e "SELECT table_schema, ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'Size (MB)' FROM information_schema.tables GROUP BY table_schema;"
```

### 5. 缓存问题排查

**检查Redis连接**：
```bash
docker exec alpha_redis_scale redis-cli ping
```

**查看Redis信息**：
```bash
docker exec alpha_redis_scale redis-cli info memory
docker exec alpha_redis_scale redis-cli info clients
```

## 📈 进一步扩容建议

### 1. 升级服务器配置

**推荐配置**：
- 内存：4GB以上
- CPU：2核以上
- 磁盘：50GB以上SSD

### 2. 水平扩容（多服务器）

**使用Docker Swarm**：
```bash
# 初始化Swarm
docker swarm init

# 部署服务栈
docker stack deploy -c docker-compose.swarm.yml alpha
```

**使用Kubernetes**：
```bash
# 应用K8s配置
kubectl apply -f k8s/
```

### 3. 数据库分离

**主从复制**：
- 配置MySQL主从复制
- 读写分离

**分库分表**：
- 按业务分库
- 按时间分表

### 4. 缓存集群

**Redis集群**：
- 配置Redis Cluster
- 数据分片

**CDN加速**：
- 静态资源CDN
- 图片CDN

## 📞 技术支持

如遇到扩容问题，请提供以下信息：
1. 服务器配置（CPU、内存、磁盘）
2. 当前用户量和并发数
3. 错误日志
4. 性能监控数据

---

**注意**：扩容前请务必备份数据，并在测试环境验证配置正确性。

