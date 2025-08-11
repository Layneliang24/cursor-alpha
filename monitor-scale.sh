#!/bin/bash

# Alpha技术共享平台 - 扩容监控脚本

echo "📊 Alpha扩容服务监控"
echo "===================="

# 检查Docker服务状态
echo "🐳 Docker服务状态："
if systemctl is-active --quiet docker; then
    echo "✅ Docker 运行中"
else
    echo "❌ Docker 未运行"
    exit 1
fi

# 检查容器状态
echo ""
echo "📦 容器状态："
docker-compose -f docker-compose.scale.yml ps

# 检查资源使用情况
echo ""
echo "💾 资源使用情况："
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"

# 检查服务健康状态
echo ""
echo "🏥 服务健康检查："

# 检查Nginx
if curl -f http://localhost/health > /dev/null 2>&1; then
    echo "✅ Nginx 负载均衡器正常"
else
    echo "❌ Nginx 负载均衡器异常"
fi

# 检查后端API
if curl -f http://localhost/api/health/ > /dev/null 2>&1; then
    echo "✅ 后端API 服务正常"
else
    echo "❌ 后端API 服务异常"
fi

# 检查前端
if curl -f http://localhost/ > /dev/null 2>&1; then
    echo "✅ 前端服务正常"
else
    echo "❌ 前端服务异常"
fi

# 检查数据库连接
echo ""
echo "🗄️  数据库状态："
if docker exec alpha_mysql_scale mysqladmin ping -h localhost -u root -p${MYSQL_ROOT_PASSWORD} > /dev/null 2>&1; then
    echo "✅ MySQL 数据库正常"
else
    echo "❌ MySQL 数据库异常"
fi

# 检查Redis
echo ""
echo "🔴 Redis状态："
if docker exec alpha_redis_scale redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis 缓存正常"
    # 显示Redis信息
    echo "   Redis内存使用: $(docker exec alpha_redis_scale redis-cli info memory | grep used_memory_human)"
    echo "   Redis连接数: $(docker exec alpha_redis_scale redis-cli info clients | grep connected_clients)"
else
    echo "❌ Redis 缓存异常"
fi

# 检查日志错误
echo ""
echo "📝 最近错误日志："
echo "Nginx错误日志："
docker exec alpha_nginx_scale tail -n 5 /var/log/nginx/error.log 2>/dev/null || echo "无错误日志"

echo ""
echo "后端错误日志："
docker-compose -f docker-compose.scale.yml logs --tail=5 backend 2>/dev/null | grep -i error || echo "无错误日志"

# 性能指标
echo ""
echo "📈 性能指标："
echo "系统负载："
uptime

echo ""
echo "内存使用："
free -h

echo ""
echo "磁盘使用："
df -h /

# 网络连接数
echo ""
echo "🌐 网络连接数："
echo "活跃连接数: $(netstat -an | grep ESTABLISHED | wc -l)"
echo "监听端口:"
netstat -tlnp | grep -E ':(80|443|8000|3306|6379)' || echo "无相关端口监听"

echo ""
echo "✅ 监控检查完成"
