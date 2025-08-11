# Kubernetes监控系统使用指南

## 📋 监控系统概览

### 监控组件
- **Prometheus**: 时序数据库，收集和存储监控指标
- **Grafana**: 可视化面板，展示监控数据
- **AlertManager**: 告警管理，发送通知
- **Node Exporter**: 节点指标收集器

### 监控范围
- Kubernetes集群状态
- 应用性能指标
- 系统资源使用情况
- 数据库和缓存状态
- 网络和存储指标

## 🚀 快速部署

### 1. 前置要求

```bash
# 检查kubectl
kubectl version --client

# 检查集群连接
kubectl cluster-info

# 检查节点状态
kubectl get nodes
```

### 2. 部署监控系统

```bash
# 给脚本执行权限
chmod +x k8s/deploy-monitoring.sh

# 部署监控系统
./k8s/deploy-monitoring.sh

# 部署监控系统（包含Ingress）
./k8s/deploy-monitoring.sh --with-ingress
```

### 3. 验证部署

```bash
# 检查Pod状态
kubectl get pods -n monitoring

# 检查服务状态
kubectl get svc -n monitoring

# 检查命名空间
kubectl get ns monitoring
```

## 🔧 访问监控界面

### 1. 端口转发访问

```bash
# 访问Prometheus
kubectl port-forward -n monitoring svc/prometheus-service 9090:9090

# 访问Grafana
kubectl port-forward -n monitoring svc/grafana-service 3000:3000

# 访问AlertManager
kubectl port-forward -n monitoring svc/alertmanager-service 9093:9093
```

### 2. Ingress访问（需要配置域名）

```bash
# 配置域名解析
# prometheus.your-domain.com -> 集群IP
# grafana.your-domain.com -> 集群IP
# alertmanager.your-domain.com -> 集群IP
```

### 3. 默认登录信息

**Grafana**:
- 用户名: `admin`
- 密码: `admin123`

## 📊 监控指标说明

### 1. 集群指标

**节点指标**:
- CPU使用率: `node_cpu_seconds_total`
- 内存使用率: `node_memory_MemAvailable_bytes`
- 磁盘使用率: `node_filesystem_avail_bytes`
- 网络流量: `node_network_receive_bytes_total`

**Pod指标**:
- CPU使用率: `container_cpu_usage_seconds_total`
- 内存使用率: `container_memory_usage_bytes`
- 网络流量: `container_network_receive_bytes_total`

### 2. 应用指标

**Alpha应用指标**:
- HTTP请求数: `http_requests_total`
- 响应时间: `http_request_duration_seconds`
- 错误率: `http_requests_errors_total`
- 活跃连接数: `http_connections_active`

### 3. 数据库指标

**MySQL指标**:
- 连接数: `mysql_global_status_threads_connected`
- 查询数: `mysql_global_status_queries`
- 慢查询数: `mysql_global_status_slow_queries`
- 缓存命中率: `mysql_global_status_qcache_hits`

**Redis指标**:
- 内存使用: `redis_memory_used_bytes`
- 连接数: `redis_connected_clients`
- 命令数: `redis_commands_processed_total`
- 缓存命中率: `redis_keyspace_hits_total`

## 📈 Grafana仪表板

### 1. 导入仪表板

**集群概览仪表板**:
```json
{
  "dashboard": {
    "title": "Kubernetes Cluster Overview",
    "panels": [
      {
        "title": "Node CPU Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "100 - (avg by (instance) (irate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)"
          }
        ]
      },
      {
        "title": "Node Memory Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "100 - ((node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100)"
          }
        ]
      }
    ]
  }
}
```

**应用性能仪表板**:
```json
{
  "dashboard": {
    "title": "Alpha Application Performance",
    "panels": [
      {
        "title": "HTTP Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"
          }
        ]
      }
    ]
  }
}
```

### 2. 常用查询

**CPU使用率**:
```promql
100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
```

**内存使用率**:
```promql
100 - ((node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100)
```

**磁盘使用率**:
```promql
100 - ((node_filesystem_avail_bytes / node_filesystem_size_bytes) * 100)
```

**Pod重启次数**:
```promql
increase(kube_pod_container_status_restarts_total[1h])
```

## 🚨 告警配置

### 1. 告警规则

**高CPU使用率告警**:
```yaml
groups:
- name: node_alerts
  rules:
  - alert: HighCPUUsage
    expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High CPU usage on {{ $labels.instance }}"
      description: "CPU usage is above 80% for 5 minutes"
```

**高内存使用率告警**:
```yaml
groups:
- name: node_alerts
  rules:
  - alert: HighMemoryUsage
    expr: 100 - ((node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100) > 85
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High memory usage on {{ $labels.instance }}"
      description: "Memory usage is above 85% for 5 minutes"
```

**Pod重启告警**:
```yaml
groups:
- name: pod_alerts
  rules:
  - alert: PodRestarting
    expr: increase(kube_pod_container_status_restarts_total[15m]) > 0
    for: 1m
    labels:
      severity: warning
    annotations:
      summary: "Pod {{ $labels.pod }} is restarting"
      description: "Pod has restarted {{ $value }} times in the last 15 minutes"
```

### 2. 告警通知

**邮件通知配置**:
```yaml
receivers:
- name: 'email-notifications'
  email_configs:
  - to: 'admin@your-domain.com'
    send_resolved: true
    headers:
      subject: 'Kubernetes Alert: {{ .GroupLabels.alertname }}'
```

**Slack通知配置**:
```yaml
receivers:
- name: 'slack-notifications'
  slack_configs:
  - api_url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'
    channel: '#alerts'
    title: 'Kubernetes Alert'
    text: '{{ .GroupLabels.alertname }}: {{ .CommonAnnotations.summary }}'
```

## 🔧 管理命令

### 1. 查看监控状态

```bash
# 查看所有Pod
kubectl get pods -n monitoring

# 查看服务
kubectl get svc -n monitoring

# 查看配置
kubectl get configmap -n monitoring

# 查看日志
kubectl logs -f prometheus-xxx -n monitoring
```

### 2. 更新配置

```bash
# 更新Prometheus配置
kubectl apply -f k8s/monitoring/prometheus-config.yaml

# 重启Prometheus
kubectl rollout restart deployment/prometheus -n monitoring

# 更新AlertManager配置
kubectl apply -f k8s/monitoring/alertmanager.yaml
```

### 3. 扩容监控

```bash
# 扩容Prometheus
kubectl scale deployment prometheus --replicas=2 -n monitoring

# 扩容Grafana
kubectl scale deployment grafana --replicas=2 -n monitoring
```

### 4. 备份和恢复

```bash
# 备份Prometheus数据
kubectl exec -n monitoring prometheus-xxx -- tar czf /tmp/prometheus-data.tar.gz /prometheus

# 备份Grafana配置
kubectl get configmap grafana-datasources -n monitoring -o yaml > grafana-datasources-backup.yaml
kubectl get configmap grafana-dashboards -n monitoring -o yaml > grafana-dashboards-backup.yaml
```

## 🗑️ 清理监控

```bash
# 删除整个监控命名空间
kubectl delete namespace monitoring

# 删除RBAC资源
kubectl delete clusterrole prometheus
kubectl delete clusterrolebinding prometheus

# 删除持久化存储（如果有）
kubectl delete pvc -n monitoring --all
```

## 📞 故障排查

### 1. 常见问题

**Prometheus无法启动**:
```bash
# 检查配置
kubectl logs prometheus-xxx -n monitoring

# 检查RBAC权限
kubectl auth can-i get pods --as=system:serviceaccount:monitoring:prometheus
```

**Grafana无法访问**:
```bash
# 检查服务状态
kubectl get svc grafana-service -n monitoring

# 检查Pod状态
kubectl describe pod grafana-xxx -n monitoring
```

**告警不工作**:
```bash
# 检查AlertManager配置
kubectl logs alertmanager-xxx -n monitoring

# 检查告警规则
kubectl get prometheusrule -n monitoring
```

### 2. 性能优化

**Prometheus优化**:
```yaml
# 增加存储保留时间
--storage.tsdb.retention.time=30d

# 增加内存限制
resources:
  limits:
    memory: "2Gi"
    cpu: "1000m"
```

**Grafana优化**:
```yaml
# 增加缓存
env:
- name: GF_DASHBOARDS_DEFAULT_HOME_DASHBOARD_PATH
  value: "/etc/grafana/provisioning/dashboards"
```

## 📚 扩展阅读

- [Prometheus官方文档](https://prometheus.io/docs/)
- [Grafana官方文档](https://grafana.com/docs/)
- [Kubernetes监控最佳实践](https://kubernetes.io/docs/tasks/debug-application-cluster/resource-usage-monitoring/)
- [Prometheus查询语言](https://prometheus.io/docs/prometheus/latest/querying/basics/)

---

**注意**: 请根据实际环境调整配置参数，特别是资源限制和告警阈值。
