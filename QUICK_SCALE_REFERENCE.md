# Alpha扩容快速参考卡片（1.7GB内存适配版）

## 🚀 一键扩容部署

```bash
# 1. 备份数据
docker exec alpha_mysql_prod mysqldump -u root -p${MYSQL_ROOT_PASSWORD} alpha_db > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. 配置环境变量
cp production.env production.env.local
vim production.env.local

# 3. 给脚本权限
chmod +x deploy-scale.sh monitor-scale.sh

# 4. 执行扩容
./deploy-scale.sh

# 5. 监控状态
./monitor-scale.sh
```

## 📊 常用监控命令

```bash
# 查看服务状态
docker-compose -f docker-compose.scale.yml ps

# 查看资源使用
docker stats --no-stream

# 查看日志
docker-compose -f docker-compose.scale.yml logs -f

# 健康检查
curl -I http://localhost/api/health/
```

## 🔧 扩容管理命令

```bash
# 扩展后端实例（需要额外512MB内存）
docker-compose -f docker-compose.scale.yml up -d --scale backend=2

# 扩展前端实例（需要额外128MB内存）
docker-compose -f docker-compose.scale.yml up -d --scale frontend=2

# 重启服务
docker-compose -f docker-compose.scale.yml restart

# 停止扩容服务
docker-compose -f docker-compose.scale.yml down
```

## 🔍 故障排查命令

```bash
# 检查端口占用
netstat -tlnp | grep :80

# 检查容器状态
docker-compose -f docker-compose.scale.yml ps

# 查看错误日志
docker-compose -f docker-compose.scale.yml logs --tail=50 backend

# 检查数据库连接
docker exec alpha_mysql_scale mysqladmin ping -h localhost -u root -p${MYSQL_ROOT_PASSWORD}

# 检查Redis连接
docker exec alpha_redis_scale redis-cli ping

# 检查内存使用
free -h
docker stats --no-stream
```

## 📈 扩容配置说明（1.7GB内存适配）

| 服务 | 实例数 | 内存限制 | CPU限制 | 说明 |
|------|--------|----------|---------|------|
| 后端 | 1个 | 512MB/实例 | 0.5核/实例 | 2个工作进程/实例 |
| 前端 | 1个 | 128MB/实例 | 0.25核/实例 | Nginx负载均衡 |
| MySQL | 1个 | 512MB | 0.5核 | 100连接数，256MB缓冲池 |
| Redis | 1个 | 128MB | 0.25核 | 64MB缓存，AOF持久化 |
| Nginx | 1个 | 128MB | 0.25核 | 负载均衡器 |

## 🎯 扩容效果

- **高可用性**：单实例部署，适合小服务器
- **负载均衡**：Nginx自动分发请求
- **性能提升**：Redis缓存减少数据库压力
- **资源隔离**：每个容器有明确的资源限制
- **易于管理**：统一的监控和管理命令

## ⚠️ 注意事项

1. **扩容前务必备份数据**
2. **当前服务器内存1.7GB，已适配小内存配置**
3. **磁盘空间充足（28GB可用）**
4. **监控服务启动过程**
5. **定期检查资源使用情况**

## 📊 内存使用预估

**当前配置总内存使用**：
- MySQL: 512MB
- 后端: 512MB  
- 前端: 128MB
- Redis: 128MB
- Nginx: 128MB
- **总计**: ~1.4GB

**可用内存**: 1.7GB - 1.4GB = 300MB（系统预留）

## 🔧 内存优化建议

```bash
# 清理Docker缓存
docker system prune -a

# 重启内存占用高的服务
docker-compose -f docker-compose.scale.yml restart backend

# 监控内存使用
watch -n 5 'free -h && echo "---" && docker stats --no-stream'
```

## 📞 紧急联系

如遇问题，请提供：
- 服务器配置信息（1.7GB内存，40GB磁盘）
- 错误日志
- 当前用户量
- 性能监控数据

## 🚀 下一步扩容建议

当用户量增长时，建议：
1. **升级服务器内存到4GB+**
2. **增加后端实例数量**
3. **配置多服务器集群**
4. **使用CDN加速静态资源**
