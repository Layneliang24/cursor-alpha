# 扩展与性能优化

## 📋 概述

本文档汇总Alpha项目的扩展、负载均衡与自动扩缩容实践，并包含数据库/缓存/前端的性能优化要点。

## 📈 性能优化

### 数据库优化
```sql
-- 添加索引
CREATE INDEX idx_article_created_at ON articles_article(created_at);
CREATE INDEX idx_article_author ON articles_article(author_id);
CREATE INDEX idx_article_category ON articles_article(category_id);

-- 查询分析
EXPLAIN SELECT * FROM articles_article WHERE author_id = 1 ORDER BY created_at DESC;
```

### 缓存优化
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

# 视图缓存
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)  # 缓存15分钟
def article_list(request):
    pass
```

### 前端优化
```javascript
// 代码分割
const ArticleList = lazy(() => import('./ArticleList'));

// 图片懒加载
<img src={imageUrl} loading="lazy" alt={alt} />

// 简易缓存
const cache = new Map();
const getCachedData = async (key) => {
  if (cache.has(key)) return cache.get(key);
  const data = await fetchData(key);
  cache.set(key, data);
  return data;
};
```

## ⚖️ 负载均衡

### Nginx负载均衡
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

### Docker Swarm（可选）
```bash
# 初始化集群
docker swarm init

# 部署服务
docker stack deploy -c docker-compose.swarm.yml alpha
```

## 🤖 自动扩缩容（Kubernetes）

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

最后更新：2025-01-17
来源：docs/DEPLOYMENT.md 扩展优化与负载均衡章节
