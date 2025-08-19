<!-- meta: document=KNOWLEDGEBASE version=1.0 updated=2025-08-19 owner=docs -->

# 项目知识库（扫盲与学习）

面向新同学与复盘的“必备技术扫盲”与速查手册。聚焦本项目实际用到的概念与最佳实践，提供简明定义、为什么、怎么用、进一步阅读四段式结构，便于扩展。

## 目录
- [后端基础](#后端基础)
  - [Django 核心概念](#django-核心概念)
  - [Django REST Framework（DRF）](#django-rest-frameworkdrf)
    - [序列化器 Serializer 是什么](#序列化器-serializer-是什么)
    - [视图集 ViewSet 与路由](#视图集-viewset-与路由)
    - [认证与权限（JWT/RBAC）](#认证与权限jwtrbac)
    - [分页与查询参数](#分页与查询参数)
  - [中间件 Middleware 是什么](#中间件-middleware-是什么)
- [数据与缓存](#数据与缓存)
  - [MySQL 基础](#mysql-基础)
  - [Redis 缓存与会话](#redis-缓存与会话)
  - [Elasticsearch 全文检索](#elasticsearch-全文检索)
  - [缓存穿透/击穿/雪崩](#缓存穿透击穿雪崩)
- [异步与任务](#异步与任务)
  - [Celery 任务队列](#celery-任务队列)
- [前端基础](#前端基础)
  - [Vue 3 基础与 Composition API](#vue-3-基础与-composition-api)
  - [ref 与 reactive 区别与用法](#ref-与-reactive-区别与用法)
  - [Pinia 状态管理](#pinia-状态管理)
  - [Axios 与 API 约定](#axios-与-api-约定)
  - [ECharts 图表](#echarts-图表)
- [爬虫与新闻模块](#爬虫与新闻模块)
  - [Fundus 框架与传统爬虫](#fundus-框架与传统爬虫)
- [API 与规范](#api-与规范)
  - [OpenAPI 规范](#openapi-规范)
  - [API 版本与路径约定](#api-版本与路径约定)
  - [速率限制与重试](#速率限制与重试)
  - [权限矩阵与角色](#权限矩阵与角色)
- [运维与部署](#运维与部署)
  - [Docker Compose 基础](#docker-compose-基础)
  - [环境变量与配置](#环境变量与配置)
  - [监控、备份、扩展](#监控备份扩展)
- [术语速查](#术语速查)
- [进一步阅读](#进一步阅读)

---

## 后端基础

### Django 核心概念
- 是什么：Python Web 框架，提供 MTV（Model-Template-View）模式与管理后台。
- 为什么：快速构建、ORM、自带Admin、生态成熟。
- 怎么用：模型定义、迁移、管理命令、URL 路由、视图与模板。
- 延伸：中间件、Signals、配置分环境管理。

### Django REST Framework（DRF）

#### 序列化器 Serializer 是什么
- 是什么：在模型对象 ↔ JSON 之间做字段映射、校验与转换的组件。
- 为什么：统一输入/输出格式、做校验（验证规则）、控制暴露字段。
- 怎么用：
  - 定义：
    ```python
    from rest_framework import serializers
    from .models import Article

    class ArticleSerializer(serializers.ModelSerializer):
        class Meta:
            model = Article
            fields = ["id", "title", "summary", "created_at"]
    ```
  - 使用：在 ViewSet 中 `serializer_class = ArticleSerializer`；或 `serializer = ArticleSerializer(instance)`/`ArticleSerializer(data=request.data)`。
- 进一步：自定义校验、`SerializerMethodField`、嵌套序列化、只读/写入字段、性能（`select_related/prefetch_related`）。

#### 视图集 ViewSet 与路由
- 是什么：把一组相关操作（列表、详情、创建、更新、删除）聚合为一个类。
- 为什么：约定优于配置，少写重复代码，统一权限与序列化策略。
- 怎么用：
  ```python
  from rest_framework import viewsets
  from .models import Article
  from .serializers import ArticleSerializer

  class ArticleViewSet(viewsets.ModelViewSet):
      queryset = Article.objects.all()
      serializer_class = ArticleSerializer
  ```
  ```python
  # urls.py
  from rest_framework.routers import DefaultRouter
  router = DefaultRouter()
  router.register(r"articles", ArticleViewSet)
  urlpatterns = [path("api/v1/", include(router.urls))]
  ```
- 进一步：自定义动作（`@action(detail=True)`）、过滤、分页、权限、节流。

#### 认证与权限（JWT/RBAC）
- 是什么：JWT 用于无状态认证；RBAC 用角色绑定权限。
- 为什么：前后端分离下的标准方案，易扩展、可审计。
- 怎么用：登录颁发 Access/Refresh；请求头 `Authorization: Bearer <token>`；在 DRF 配置默认认证与权限类。
- 进一步：Token 刷新、黑名单、细粒度对象权限、审计日志。

#### 分页与查询参数
- 规范：统一 `page/page_size/search/ordering`，上限与默认值明确；日期使用 ISO8601。
- 实现：DRF 内置分页器 + 过滤后端；在 `settings.py` 设置全局分页。

### 中间件 Middleware 是什么
- 是什么：位于请求进入视图函数/视图集前后的一组“链式钩子”，可对 Request/Response 做统一处理（鉴权、日志、跨域、限流、追踪等）。
- 为什么：把横切关注点从业务代码中抽离，统一注入、便于复用与审计，减少重复。
- 怎么用（Django）：
  - 顺序：`settings.MIDDLEWARE` 自上而下依次处理请求，自下而上处理响应；顺序非常关键。
  - 自定义：
    ```python
    # backend/middlewares/request_logging.py
    import time
    from django.utils.deprecation import MiddlewareMixin

    class RequestLoggingMiddleware(MiddlewareMixin):
        def process_request(self, request):
            request._start_ts = time.time()
        def process_response(self, request, response):
            try:
                cost_ms = int((time.time() - getattr(request, "_start_ts", time.time())) * 1000)
                # 这里可接入日志/链路追踪
                # logger.info(f"{request.method} {request.path} {response.status_code} {cost_ms}ms")
            finally:
                return response
    ```
  - 配置：
    ```python
    # settings.py
    MIDDLEWARE = [
        # ... 默认中间件
        'backend.middlewares.request_logging.RequestLoggingMiddleware',
    ]
    ```
- 进一步：按模块划分中间件；区分开发/生产配置；结合 `X-Request-ID`、Tracing、限流（配合 Redis）等。

---

## 数据与缓存

### MySQL 基础
- 关注点：表结构规范化、索引设计（覆盖/联合索引）、事务与隔离级别、慢查询优化。

### Redis 缓存与会话
- 用途：热点数据缓存、会话、计数器、分布式锁；Django 可用 `django-redis` 适配。

### Elasticsearch 全文检索
- 用途：全文检索与高亮、聚合分析；需关注映射、分词、索引生命周期。

### 缓存穿透/击穿/雪崩
- 缓存穿透（Cache Penetration）
  - 是什么：请求大量“不存在”的 Key，缓存无法命中，每次都打到数据库。
  - 风险：数据库压力骤增，可能被恶意利用。
  - 防护：参数校验与黑名单；缓存空值（短过期）；布隆过滤器（Bloom Filter）挡不存在 Key；基础限流。
- 缓存击穿（Cache Breakdown/Hot Key Miss）
  - 是什么：某个热点 Key 过期瞬间，海量并发同时落到数据库重建缓存。
  - 防护：互斥锁/单飞（Only One Rebuild）；逻辑过期（续命，后台异步重建）；热点预热；提前延长 TTL。
- 缓存雪崩（Cache Avalanche）
  - 是什么：同一时间大量 Key 集中过期或缓存整体不可用，导致后端被压垮。
  - 防护：过期时间随机抖动（Jitter）；多级缓存（本地+Redis）；熔断/隔离/降级；只读降级与限流；缓存集群高可用。
- 代码要点（示例）：
  ```python
  # 带随机过期的写入（避免雪崩）
  import random
  ttl = 300 + random.randint(0, 60)  # 5min ±60s
  cache.set(key, data, ttl)
  
  # 互斥重建（避免击穿，伪代码）
  lock_key = f"lock:{key}"
  got = redis.set(lock_key, "1", nx=True, ex=30)
  if got:
      try:
          data = load_from_db()
          cache.set(key, data, 300)
      finally:
          redis.delete(lock_key)
  else:
      # 短暂等待或快速失败，返回旧值（逻辑过期策略）
      pass
  ```
- Django/DRF 实践：
  - 只读接口优先缓存（列表/详情）；`cache_page`、低层缓存 API、按用户/条件拼接 Key。
  - 写操作主动失效相关 Key；避免写后读脏数据。
  - 监控命中率与重建耗时；识别热 Key 并做预热/保护。

---

## 异步与任务

### Celery 任务队列
- 是什么：分布式任务队列，基于消息中间件（本项目常配合 Redis）。
- 用途：爬虫、图片下载、统计聚合等异步任务。
- 要点：任务幂等、重试策略、超时设定、监控。

---

## 前端基础

### Vue 3 基础与 Composition API
- 要点：`setup()`、`ref/reactive/computed/watch`、组件通信（props/emit/provide-inject）、路由与异步组件。

### ref 与 reactive 区别与用法
- 是什么：
  - `ref(value)`：为基本类型或对象创建“单值容器”，访问用 `.value`；在模板中自动解包。
  - `reactive(obj)`：将对象转换为深层响应式代理，直接读写属性。
- 选择：
  - 基本类型：优先 `ref`；复杂对象：优先 `reactive`。
  - 需要替换整个对象：`ref` 包裹对象更直观（`state.value = {...}`）。
- 常见坑：
  - `ref` 引用子组件不稳定（动态组件+key 变更）时，可结合 `getCurrentInstance` 与延迟（`nextTick/setTimeout`）获取；统一封装引用获取函数，避免空引用。

### Pinia 状态管理
- 要点：模块化 Store、持久化（本地存储）、异步 Action、`storeToRefs`；避免在组件与 Store 间重复定义状态。

### Axios 与 API 约定
- 统一 `baseURL=/api/v1/`，请求与响应拦截器处理 Token 与错误；与后端统一错误码与分页结构。

### ECharts 图表
- 场景：学习统计（热力图/趋势图/键盘错误统计等）；注意懒加载与尺寸监听。

---

## 爬虫与新闻模块

### Fundus 框架与传统爬虫
- Fundus：高质量新闻源、结构化输出、内置反爬；适合主流媒体。
- 传统爬虫：灵活但维护成本高；适合作为补充与本地测试。
- 实践要点：统一字段模型、图片下载与媒体路径、错误重试与日志。

---

## API 与规范

### OpenAPI 规范
- 作用：接口契约、Mock、客户端生成；本项目以 `docs/spec/openapi.json` 为基。

### API 版本与路径约定
- 本项目固定前缀：`/api/v1/`（请在前后端与测试中保持一致）。

### 速率限制与重试
- 外部接口与爬虫需配置速率限制与重试（见 `docs/spec/rate_limit.yaml`）。

### 权限矩阵与角色
- 参见 `docs/spec/permissions-matrix.yaml`；按模块与操作维度定义权限与角色绑定。

---

## 运维与部署

### Docker Compose 基础
- 将 MySQL/Redis/后端/前端编排启动；注意数据卷、网络、环境变量与健康检查。

### 环境变量与配置
- 统一由 `docs/spec/env.yaml` 定义；区分开发/测试/生产；敏感信息不入库。

### 监控、备份、扩展
- 监控：Prometheus + Grafana（见 `docs/operations/MONITORING.md`）。
- 备份：数据库与媒体分层备份（见 `docs/operations/BACKUP.md`）。
- 扩展：横向扩展与 HPA 策略（见 `docs/operations/SCALING.md`）。

---

## 术语速查
- 序列化器（Serializer）：对象与 JSON 的双向映射组件，承担“字段选择+校验+转换”。
- 视图集（ViewSet）：将一组增删改查操作聚合的 DRF 类，配合 Router 自动生成路由。
- 中间件（Middleware）：对请求/响应做统一处理的链式钩子，适合横切关注点（鉴权/日志/限流等）。
- JWT：无状态认证令牌，放在 `Authorization: Bearer` 请求头。
- RBAC：基于角色的访问控制，用角色聚合权限、绑定用户。
- ref（Vue）：单值响应式容器，`.value` 读写；模板自动解包。
- reactive（Vue）：对象级响应式代理，直接读写属性。
- 缓存穿透：请求不存在 Key 导致每次打到底层存储。
- 缓存击穿：热点 Key 过期瞬间被并发穿透到底层。
- 缓存雪崩：大量 Key 集中过期或缓存整体不可用导致级联故障。
- 逻辑过期：缓存标记过期但仍可读旧值，后台异步重建。
- 幂等：同一操作重复执行结果一致（任务/接口重试的基础）。

---

## 进一步阅读
- 后端：`docs/API.md`、`docs/GUIDE.md`、`docs/technical/`、`docs/modules/*`
- 运维：`docs/DEPLOYMENT.md`、`docs/operations/*`
- 规范：`docs/spec/*`
- 前端：前端目录与路由规范见 `docs/spec/frontend_routes.json`

> 扩展约定：新增条目时保持“四段式”（是什么/为什么/怎么用/进一步），并在“术语速查”补充关键词。
