#!/bin/bash

# Kubernetes监控系统部署脚本
# 包含Prometheus、Grafana、AlertManager、Node Exporter

set -e

echo "🚀 开始部署Kubernetes监控系统..."

# 检查kubectl是否可用
if ! command -v kubectl &> /dev/null; then
    echo "❌ 错误: kubectl 未安装或不在PATH中"
    exit 1
fi

# 检查集群连接
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ 错误: 无法连接到Kubernetes集群"
    exit 1
fi

echo "✅ Kubernetes集群连接正常"

# 创建监控命名空间
echo "📁 创建监控命名空间..."
kubectl apply -f monitoring/namespace.yaml

# 部署Prometheus
echo "🔍 部署Prometheus..."
kubectl apply -f monitoring/prometheus-config.yaml
kubectl apply -f monitoring/prometheus.yaml

# 部署Node Exporter
echo "📊 部署Node Exporter..."
kubectl apply -f monitoring/node-exporter.yaml

# 部署AlertManager
echo "🚨 部署AlertManager..."
kubectl apply -f monitoring/alertmanager.yaml

# 部署Grafana
echo "📈 部署Grafana..."
kubectl apply -f monitoring/grafana.yaml

# 部署Ingress（可选）
if [ "$1" = "--with-ingress" ]; then
    echo "🌐 部署Ingress..."
    kubectl apply -f monitoring/ingress.yaml
fi

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 30

# 检查服务状态
echo "🔍 检查服务状态..."
kubectl get pods -n monitoring

# 检查服务
echo "🌐 检查服务..."
kubectl get svc -n monitoring

# 显示访问信息
echo ""
echo "✅ Kubernetes监控系统部署完成！"
echo ""
echo "📋 访问信息："
echo "  Prometheus: kubectl port-forward -n monitoring svc/prometheus-service 9090:9090"
echo "  Grafana:    kubectl port-forward -n monitoring svc/grafana-service 3000:3000"
echo "  AlertManager: kubectl port-forward -n monitoring svc/alertmanager-service 9093:9093"
echo ""
echo "🔑 Grafana默认登录信息："
echo "  用户名: admin"
echo "  密码: admin123"
echo ""
echo "🔧 管理命令："
echo "  查看Pod状态: kubectl get pods -n monitoring"
echo "  查看日志: kubectl logs -f <pod-name> -n monitoring"
echo "  删除监控: kubectl delete namespace monitoring"
echo ""
echo "📊 监控指标："
echo "  - 集群节点资源使用情况"
echo "  - Pod资源使用情况"
echo "  - 应用性能指标"
echo "  - 数据库和缓存状态"
echo "  - 网络和存储指标"
