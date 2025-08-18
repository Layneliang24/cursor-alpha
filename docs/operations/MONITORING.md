# 监控方案

## 📋 概述

Alpha技术共享平台的监控方案基于Prometheus + Grafana构建，提供全面的系统监控、应用性能监控和业务指标监控。

### 监控目标
- **系统健康**: 实时监控系统运行状态
- **性能监控**: 监控应用性能和资源使用
- **业务监控**: 监控关键业务指标
- **告警通知**: 及时发现问题并通知相关人员

---

## 🏗️ 监控架构

### 整体架构
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   应用服务      │    │   数据库服务    │    │   缓存服务      │
│   (Django)      │    │   (MySQL)       │    │   (Redis)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   数据收集      │
                    │   (Exporters)   │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │   指标存储      │
                    │   (Prometheus)  │
                    └─────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   数据可视化    │    │   告警管理      │    │   日志聚合      │
│   (Grafana)     │    │   (Alertmanager)│    │   (ELK Stack)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 监控组件

#### 1. 数据收集层
- **Node Exporter**: 系统指标收集
- **MySQL Exporter**: MySQL数据库指标
- **Redis Exporter**: Redis缓存指标
- **Django Exporter**: 应用性能指标

#### 2. 数据存储层
- **Prometheus**: 时序数据库，存储监控指标
- **Prometheus Operator**: Kubernetes环境下的Prometheus管理

#### 3. 数据展示层
- **Grafana**: 数据可视化和仪表板
- **Alertmanager**: 告警管理和通知

#### 4. 日志管理
- **Elasticsearch**: 日志存储和搜索
- **Logstash**: 日志收集和处理
- **Kibana**: 日志可视化和分析

---

## 📊 监控指标

### 系统指标

#### 基础系统指标
- **CPU使用率**: 系统CPU使用情况
- **内存使用率**: 系统内存使用情况
- **磁盘使用率**: 磁盘空间使用情况
- **网络流量**: 网络输入输出流量
- **系统负载**: 系统平均负载

#### 容器指标
- **容器状态**: 运行、停止、重启次数
- **资源使用**: CPU、内存、磁盘使用量
- **网络连接**: 容器网络连接数
- **存储使用**: 容器存储使用量

### 应用指标

#### Django应用指标
- **请求数量**: HTTP请求总数和状态码分布
- **响应时间**: 请求响应时间分布
- **错误率**: 应用错误和异常统计
- **数据库查询**: 数据库查询数量和性能
- **缓存命中率**: Redis缓存命中率

#### 业务指标
- **用户活跃度**: 日活跃用户、月活跃用户
- **内容统计**: 文章数量、评论数量、用户数量
- **学习数据**: 单词学习进度、新闻阅读量
- **系统性能**: API响应时间、页面加载时间

### 数据库指标

#### MySQL指标
- **连接数**: 当前连接数、最大连接数
- **查询性能**: 慢查询数量、查询响应时间
- **锁等待**: 锁等待时间和次数
- **缓存效率**: 查询缓存命中率
- **存储使用**: 数据库大小、表大小

#### Redis指标
- **内存使用**: 内存使用量和碎片率
- **连接数**: 客户端连接数
- **命令统计**: 各种Redis命令执行次数
- **缓存命中率**: 键值命中率
- **网络流量**: 网络输入输出流量

---

## 🔧 监控配置

### Prometheus配置

#### 基础配置
```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rules/*.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'alpha-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics/'
    scrape_interval: 10s

  - job_name: 'alpha-mysql'
    static_configs:
      - targets: ['mysql-exporter:9104']

  - job_name: 'alpha-redis'
    static_configs:
      - targets: ['redis-exporter:9121']

  - job_name: 'alpha-node'
    static_configs:
      - targets: ['node-exporter:9100']
```

#### 告警规则
```yaml
# rules/alerts.yml
groups:
  - name: system_alerts
    rules:
      - alert: HighCPUUsage
        expr: 100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage on {{ $labels.instance }}"
          description: "CPU usage is above 80% for 5 minutes"

      - alert: HighMemoryUsage
        expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100 > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage on {{ $labels.instance }}"
          description: "Memory usage is above 85% for 5 minutes"

      - alert: HighDiskUsage
        expr: (node_filesystem_size_bytes - node_filesystem_free_bytes) / node_filesystem_size_bytes * 100 > 90
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High disk usage on {{ $labels.instance }}"
          description: "Disk usage is above 90% for 5 minutes"

  - name: application_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) * 100 > 5
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High error rate on {{ $labels.instance }}"
          description: "Error rate is above 5% for 2 minutes"

      - alert: SlowResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Slow response time on {{ $labels.instance }}"
          description: "95th percentile response time is above 2 seconds"

  - name: database_alerts
    rules:
      - alert: MySQLHighConnections
        expr: mysql_global_status_threads_connected > 100
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High MySQL connections on {{ $labels.instance }}"
          description: "MySQL connections are above 100"

      - alert: RedisHighMemoryUsage
        expr: redis_memory_used_bytes / redis_memory_max_bytes * 100 > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High Redis memory usage on {{ $labels.instance }}"
          description: "Redis memory usage is above 80%"
```

### Grafana配置

#### 数据源配置
```yaml
# grafana/datasources.yml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true

  - name: MySQL
    type: mysql
    access: proxy
    url: mysql:3306
    database: alpha_production
    user: grafana_user
    secureJsonData:
      password: "grafana_password"
    jsonData:
      maxOpenConns: 100
      maxIdleConns: 100
      connMaxLifetime: 14400
```

#### 仪表板配置
```json
{
  "dashboard": {
    "id": null,
    "title": "Alpha Platform Overview",
    "tags": ["alpha", "overview"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "System Overview",
        "type": "stat",
        "targets": [
          {
            "expr": "up",
            "legendFormat": "{{instance}}"
          }
        ]
      },
      {
        "id": 2,
        "title": "CPU Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "100 - (avg by (instance) (irate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)",
            "legendFormat": "{{instance}}"
          }
        ]
      },
      {
        "id": 3,
        "title": "Memory Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100",
            "legendFormat": "{{instance}}"
          }
        ]
      }
    ]
  }
}
```

---

## 🚨 告警管理

### Alertmanager配置

#### 基础配置
```yaml
# alertmanager.yml
global:
  resolve_timeout: 5m
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'alertmanager@your-domain.com'
  smtp_auth_username: 'your-email@gmail.com'
  smtp_auth_password: 'your-app-password'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'

receivers:
  - name: 'web.hook'
    webhook_configs:
      - url: 'http://127.0.0.1:5001/'

  - name: 'email'
    email_configs:
      - to: 'admin@your-domain.com'
        send_resolved: true

  - name: 'slack'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'
        channel: '#alerts'
        send_resolved: true

inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'dev', 'instance']
```

#### 告警通知模板
```yaml
# templates/alert.tmpl
{{ define "email.to.html" }}
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Alert Notification</title>
</head>
<body>
    <h1>Alert: {{ .GroupLabels.alertname }}</h1>
    <p><strong>Severity:</strong> {{ .CommonLabels.severity }}</p>
    <p><strong>Instance:</strong> {{ .CommonLabels.instance }}</p>
    <p><strong>Summary:</strong> {{ .CommonAnnotations.summary }}</p>
    <p><strong>Description:</strong> {{ .CommonAnnotations.description }}</p>
    
    <h2>Alerts:</h2>
    {{ range .Alerts }}
    <div style="border: 1px solid #ccc; margin: 10px 0; padding: 10px;">
        <p><strong>Alert:</strong> {{ .Labels.alertname }}</p>
        <p><strong>Status:</strong> {{ .Status }}</p>
        <p><strong>Started:</strong> {{ .StartsAt }}</p>
        {{ if .EndsAt }}
        <p><strong>Ended:</strong> {{ .EndsAt }}</p>
        {{ end }}
    </div>
    {{ end }}
</body>
</html>
{{ end }}
```

### 告警策略

#### 告警级别
- **Critical**: 系统严重问题，需要立即处理
- **Warning**: 系统警告，需要关注和处理
- **Info**: 信息性通知，无需立即处理

#### 告警规则
- **系统资源**: CPU > 80%, 内存 > 85%, 磁盘 > 90%
- **应用性能**: 错误率 > 5%, 响应时间 > 2s
- **数据库**: 连接数 > 100, 慢查询 > 10s
- **缓存**: 内存使用 > 80%, 命中率 < 90%

---

## 📈 监控仪表板

### 系统概览仪表板

#### 关键指标
- **系统状态**: 服务运行状态概览
- **资源使用**: CPU、内存、磁盘使用率
- **网络流量**: 网络输入输出流量
- **容器状态**: Docker容器运行状态

#### 图表类型
- **状态面板**: 服务运行状态
- **趋势图**: 资源使用趋势
- **热力图**: 系统负载分布
- **仪表盘**: 资源使用百分比

### 应用性能仪表板

#### 性能指标
- **请求统计**: 请求数量、状态码分布
- **响应时间**: 平均响应时间、95分位数
- **错误统计**: 错误类型、错误率趋势
- **业务指标**: 用户活跃度、内容统计

#### 可视化组件
- **折线图**: 性能趋势分析
- **柱状图**: 请求分布统计
- **饼图**: 错误类型分布
- **表格**: 详细性能数据

### 数据库监控仪表板

#### 数据库指标
- **连接状态**: 当前连接数、最大连接数
- **查询性能**: 查询数量、慢查询统计
- **锁等待**: 锁等待时间和次数
- **存储使用**: 数据库大小、表大小

#### 监控图表
- **时序图**: 性能指标变化趋势
- **热力图**: 查询性能分布
- **状态面板**: 数据库运行状态
- **告警面板**: 数据库告警信息

---

## 🔍 日志监控

### ELK Stack配置

#### Elasticsearch配置
```yaml
# elasticsearch.yml
cluster.name: alpha-cluster
node.name: alpha-node-1
network.host: 0.0.0.0
http.port: 9200
discovery.seed_hosts: ["elasticsearch"]
cluster.initial_master_nodes: ["alpha-node-1"]
```

#### Logstash配置
```ruby
# logstash.conf
input {
  beats {
    port => 5044
  }
}

filter {
  if [fields][service] == "alpha-backend" {
    grok {
      match => { "message" => "%{TIMESTAMP_ISO8601:timestamp} %{LOGLEVEL:level} %{GREEDYDATA:message}" }
    }
    date {
      match => [ "timestamp", "ISO8601" ]
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "alpha-logs-%{+YYYY.MM.dd}"
  }
}
```

#### Kibana配置
```yaml
# kibana.yml
server.name: kibana
server.host: "0.0.0.0"
elasticsearch.hosts: ["http://elasticsearch:9200"]
monitoring.ui.container.elasticsearch.enabled: true
```

### 日志分析

#### 日志类型
- **应用日志**: Django应用运行日志
- **访问日志**: Nginx访问日志
- **错误日志**: 系统错误和异常日志
- **审计日志**: 用户操作审计日志

#### 分析功能
- **实时搜索**: 实时日志搜索和过滤
- **统计分析**: 日志数量、错误率统计
- **异常检测**: 自动异常模式识别
- **趋势分析**: 日志变化趋势分析

---

## 🚀 部署配置

### Docker Compose配置

#### 监控服务配置
```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - ./monitoring/rules:/etc/prometheus/rules
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    volumes:
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - grafana_data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123

  alertmanager:
    image: prom/alertmanager:latest
    ports:
      - "9093:9093"
    volumes:
      - ./monitoring/alertmanager.yml:/etc/alertmanager/alertmanager.yml
      - alertmanager_data:/alertmanager
    command:
      - '--config.file=/etc/alertmanager/alertmanager.yml'
      - '--storage.path=/alertmanager'

  node-exporter:
    image: prom/node-exporter:latest
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.ignored-mount-points=^/(sys|proc|dev|host|etc)($$|/)'

  mysql-exporter:
    image: prom/mysqld-exporter:latest
    ports:
      - "9104:9104"
    environment:
      - DATA_SOURCE_NAME=root:password@(mysql:3306)/
    depends_on:
      - mysql

  redis-exporter:
    image: oliver006/redis_exporter:latest
    ports:
      - "9121:9121"
    environment:
      - REDIS_ADDR=redis://redis:6379
    depends_on:
      - redis

volumes:
  prometheus_data:
  grafana_data:
  alertmanager_data:
```

### Kubernetes配置

#### 监控命名空间
```yaml
# k8s/monitoring/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: monitoring
  labels:
    name: monitoring
```

#### Prometheus部署
```yaml
# k8s/monitoring/prometheus.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      containers:
      - name: prometheus
        image: prom/prometheus:latest
        ports:
        - containerPort: 9090
        volumeMounts:
        - name: config
          mountPath: /etc/prometheus
        - name: storage
          mountPath: /prometheus
      volumes:
      - name: config
        configMap:
          name: prometheus-config
      - name: storage
        persistentVolumeClaim:
          claimName: prometheus-pvc
```

---

## 轻量监控方案（低配服务器）

### 方案A（超轻量）
- 存活：Docker healthcheck 或 `docker ps` 周期巡检
- 日志：Nginx/后端 5xx 比例脚本 + Webhook 通知
- 资源：磁盘水位脚本（阈值告警）

### 方案B（推荐）
- 组件：Prometheus + node-exporter + cAdvisor + Grafana（独立 Compose）
- 目录建议：`/opt/alpha/monitor/`（`docker-compose.monitor.yml`、`prometheus.yml`）
- 启动：`docker-compose -f docker-compose.monitor.yml up -d`

### 方案C（增强）
- 在 B 基础上增加 Alertmanager 与应用自定义指标（`/metrics`）
- 告警：CPU/内存/磁盘水位、HTTP 5xx、容器重启、队列堆积

### 2GB 优化建议
- Prometheus 保留 7 天、`scrape_interval >= 15s`
- Grafana 仅内网访问、限制仪表盘数量
- 合理设置告警阈值，避免噪声

## 📚 相关文档

### 技术文档
- [系统架构](../technical/ARCHITECTURE.md) - 整体架构设计
- [部署指南](../DEPLOYMENT.md) - 部署运维指南
- [性能优化](../technical/PERFORMANCE.md) - 性能调优指南

### 用户文档
- [用户指南](../GUIDE.md) - 完整的使用指南
- [开发者指南](../DEVELOPMENT.md) - 开发环境搭建
- [常见问题](../FAQ.md) - 问题解答

---

## 📞 支持

### 技术支持
- 查看 [开发者指南](../DEVELOPMENT.md) 了解技术细节
- 参考 [部署指南](../DEPLOYMENT.md) 解决部署问题
- 查看 [常见问题](../FAQ.md) 解决监控问题

### 监控支持
- 监控配置问题: monitoring@your-domain.com
- 告警配置问题: alerts@your-domain.com
- 性能优化问题: performance@your-domain.com

---

*最后更新：2025-01-17*
*更新内容：创建完整的监控方案文档，包含监控架构、指标配置、告警管理等*
