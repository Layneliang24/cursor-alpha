#!/bin/bash

# Alpha技术共享平台 - 扩容部署脚本
# 适用于单机多实例部署

set -e

echo "🚀 开始扩容部署..."

# 检查环境变量文件
if [ ! -f "production.env.local" ]; then
    echo "❌ 错误: 未找到 production.env.local 文件"
    echo "请先复制 production.env 为 production.env.local 并配置环境变量"
    exit 1
fi

# 加载环境变量
export $(cat production.env.local | grep -v '^#' | xargs)

# 创建必要的目录
echo "📁 创建必要目录..."
mkdir -p logs/nginx
mkdir -p nginx/conf.d
mkdir -p ssl

# 停止现有服务
echo "🛑 停止现有服务..."
docker-compose -f docker-compose.prod.yml down || true

# 构建并启动扩容服务
echo "🔨 构建扩容服务..."
docker-compose -f docker-compose.scale.yml build

echo "🚀 启动扩容服务..."
docker-compose -f docker-compose.scale.yml up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 30

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose -f docker-compose.scale.yml ps

# 检查服务健康状态
echo "🏥 检查服务健康状态..."
for i in {1..5}; do
    echo "第 $i 次健康检查..."
    
    # 检查Nginx
    if curl -f http://localhost/health > /dev/null 2>&1; then
        echo "✅ Nginx 健康检查通过"
    else
        echo "⚠️  Nginx 健康检查失败"
    fi
    
    # 检查后端API
    if curl -f http://localhost/api/health/ > /dev/null 2>&1; then
        echo "✅ 后端API 健康检查通过"
    else
        echo "⚠️  后端API 健康检查失败"
    fi
    
    sleep 10
done

echo "📊 显示资源使用情况..."
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"

echo "✅ 扩容部署完成！"
echo ""
echo "📋 服务信息："
echo "   - 前端访问: http://localhost"
echo "   - 后端API: http://localhost/api/"
echo "   - 管理后台: http://localhost/admin/"
echo ""
echo "🔧 管理命令："
echo "   - 查看服务状态: docker-compose -f docker-compose.scale.yml ps"
echo "   - 查看日志: docker-compose -f docker-compose.scale.yml logs -f"
echo "   - 停止服务: docker-compose -f docker-compose.scale.yml down"
echo "   - 重启服务: docker-compose -f docker-compose.scale.yml restart"
echo ""
echo "📈 扩容配置："
echo "   - 后端实例数: 2"
echo "   - 前端实例数: 2"
echo "   - MySQL内存限制: 2GB"
echo "   - Redis缓存: 512MB"
echo "   - 负载均衡: Nginx (最少连接数算法)"
