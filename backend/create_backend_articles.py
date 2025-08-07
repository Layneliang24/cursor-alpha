#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime, timedelta
import random

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alpha.settings')
django.setup()

from apps.articles.models import Article
from apps.categories.models import Category
from apps.users.models import User

backend_articles = [
    {
        'title': 'Django REST Framework 高级用法',
        'summary': '深入探讨DRF的高级特性，包括自定义序列化器、权限系统、过滤器等。',
        'content': '''# Django REST Framework 高级用法

## 自定义序列化器

### 1. 动态字段序列化器

```python
class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)
        
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

class UserSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

# 使用
serializer = UserSerializer(user, fields=('id', 'username', 'email'))
```

### 2. 嵌套序列化器

```python
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['bio', 'avatar', 'location']

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile']
    
    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', None)
        instance = super().update(instance, validated_data)
        
        if profile_data:
            Profile.objects.filter(user=instance).update(**profile_data)
        
        return instance
```

## 高级权限系统

### 1. 自定义权限类

```python
from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # 读权限允许任何请求
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # 写权限只给对象的所有者
        return obj.owner == request.user

class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user
```

### 2. 基于角色的权限

```python
class RoleBasedPermission(permissions.BasePermission):
    required_roles = []
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        user_roles = set(request.user.roles.values_list('name', flat=True))
        required_roles = set(self.required_roles)
        
        return bool(user_roles.intersection(required_roles))

class AdminOnlyPermission(RoleBasedPermission):
    required_roles = ['admin']

class EditorPermission(RoleBasedPermission):
    required_roles = ['admin', 'editor']
```

## 高级过滤和搜索

### 1. 自定义过滤器

```python
import django_filters
from django_filters import rest_framework as filters

class ArticleFilter(filters.FilterSet):
    title = filters.CharFilter(lookup_expr='icontains')
    created_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    category = filters.ModelChoiceFilter(queryset=Category.objects.all())
    tags = filters.ModelMultipleChoiceFilter(queryset=Tag.objects.all())
    
    class Meta:
        model = Article
        fields = ['status', 'featured']

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    filter_backends = [filters.DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ArticleFilter
    search_fields = ['title', 'content', 'summary']
    ordering_fields = ['created_at', 'views', 'likes']
```

### 2. 全文搜索

```python
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank

class ArticleSearchViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ArticleSerializer
    
    def get_queryset(self):
        query = self.request.query_params.get('q')
        if query:
            search_vector = SearchVector('title', weight='A') + SearchVector('content', weight='B')
            search_query = SearchQuery(query)
            
            return Article.objects.annotate(
                search=search_vector,
                rank=SearchRank(search_vector, search_query)
            ).filter(search=search_query).order_by('-rank')
        
        return Article.objects.none()
```

## 缓存策略

### 1. 视图级缓存

```python
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers

@method_decorator(cache_page(60 * 15), name='list')
@method_decorator(vary_on_headers('Authorization'), name='list')
class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
```

### 2. 查询集缓存

```python
from django.core.cache import cache

class CachedModelMixin:
    cache_timeout = 60 * 15
    
    def get_queryset(self):
        cache_key = f"{self.__class__.__name__}_queryset"
        queryset = cache.get(cache_key)
        
        if queryset is None:
            queryset = super().get_queryset()
            cache.set(cache_key, queryset, self.cache_timeout)
        
        return queryset
```

## 性能优化

### 1. 查询优化

```python
class OptimizedArticleViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return Article.objects.select_related(
            'author', 'category'
        ).prefetch_related(
            'tags', 'comments__author'
        ).annotate(
            comments_count=Count('comments'),
            likes_count=Count('likes')
        )
```

### 2. 分页优化

```python
from rest_framework.pagination import CursorPagination

class ArticleCursorPagination(CursorPagination):
    page_size = 20
    ordering = '-created_at'
    cursor_query_param = 'cursor'
    page_size_query_param = 'page_size'
    max_page_size = 100
```

## 总结

DRF的高级特性为构建复杂的API提供了强大支持，通过合理使用这些特性可以构建高性能、可维护的REST API。''',
        'category': '后端开发'
    },
    {
        'title': 'FastAPI 异步编程最佳实践',
        'summary': '详细介绍FastAPI的异步特性，包括异步路由、数据库操作、后台任务等。',
        'content': '''# FastAPI 异步编程最佳实践

## FastAPI 异步基础

### 1. 异步路由定义

```python
from fastapi import FastAPI
import asyncio
import httpx

app = FastAPI()

@app.get("/sync")
def read_sync():
    return {"message": "同步响应"}

@app.get("/async")
async def read_async():
    await asyncio.sleep(1)
    return {"message": "异步响应"}

@app.get("/external-api")
async def call_external_api():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/data")
        return response.json()
```

### 2. 异步依赖注入

```python
from fastapi import Depends
import aioredis

async def get_redis():
    redis = aioredis.from_url("redis://localhost")
    try:
        yield redis
    finally:
        await redis.close()

async def get_current_user(redis: aioredis.Redis = Depends(get_redis)):
    # 从Redis获取用户信息
    user_data = await redis.get("current_user")
    return json.loads(user_data) if user_data else None

@app.get("/profile")
async def get_profile(user = Depends(get_current_user)):
    return {"user": user}
```

## 异步数据库操作

### 1. SQLAlchemy 异步支持

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

# 异步引擎
engine = create_async_engine(
    "postgresql+asyncpg://user:password@localhost/dbname",
    echo=True
)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# 异步CRUD操作
class UserCRUD:
    @staticmethod
    async def get_user(db: AsyncSession, user_id: int):
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create_user(db: AsyncSession, user_data: dict):
        user = User(**user_data)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    
    @staticmethod
    async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100):
        result = await db.execute(
            select(User).offset(skip).limit(limit)
        )
        return result.scalars().all()

@app.post("/users/", response_model=UserResponse)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    return await UserCRUD.create_user(db, user.dict())
```

### 2. MongoDB 异步操作

```python
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

class MongoDB:
    client: AsyncIOMotorClient = None
    database = None

db = MongoDB()

async def connect_to_mongo():
    db.client = AsyncIOMotorClient("mongodb://localhost:27017")
    db.database = db.client["myapp"]

async def close_mongo_connection():
    db.client.close()

# 异步文档操作
class ArticleService:
    @staticmethod
    async def create_article(article_data: dict):
        result = await db.database.articles.insert_one(article_data)
        return str(result.inserted_id)
    
    @staticmethod
    async def get_article(article_id: str):
        article = await db.database.articles.find_one(
            {"_id": ObjectId(article_id)}
        )
        if article:
            article["_id"] = str(article["_id"])
        return article
    
    @staticmethod
    async def get_articles(skip: int = 0, limit: int = 10):
        cursor = db.database.articles.find().skip(skip).limit(limit)
        articles = await cursor.to_list(length=limit)
        for article in articles:
            article["_id"] = str(article["_id"])
        return articles
```

## 后台任务

### 1. 简单后台任务

```python
from fastapi import BackgroundTasks
import smtplib
from email.mime.text import MIMEText

def send_email(email: str, message: str):
    # 发送邮件的逻辑
    msg = MIMEText(message)
    msg['Subject'] = '通知'
    msg['From'] = 'noreply@example.com'
    msg['To'] = email
    
    with smtplib.SMTP('localhost') as server:
        server.send_message(msg)

@app.post("/send-notification/")
async def send_notification(
    email: str,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(send_email, email, "感谢您的注册！")
    return {"message": "通知已发送"}
```

### 2. Celery 集成

```python
from celery import Celery

celery_app = Celery(
    "worker",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

@celery_app.task
def process_data(data: dict):
    # 处理数据的耗时任务
    import time
    time.sleep(10)
    return {"status": "completed", "result": data}

@app.post("/process/")
async def start_processing(data: dict):
    task = process_data.delay(data)
    return {"task_id": task.id, "status": "processing"}

@app.get("/task/{task_id}")
async def get_task_status(task_id: str):
    task = celery_app.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": task.status,
        "result": task.result
    }
```

## 流式响应

### 1. 服务器发送事件 (SSE)

```python
from fastapi.responses import StreamingResponse
import json
import asyncio

@app.get("/events")
async def stream_events():
    async def event_generator():
        counter = 0
        while True:
            # 检查客户端是否断开连接
            if await request.is_disconnected():
                break
            
            # 发送数据
            data = {"counter": counter, "timestamp": time.time()}
            yield f"data: {json.dumps(data)}\n\n"
            
            counter += 1
            await asyncio.sleep(1)
    
    return StreamingResponse(
        event_generator(),
        media_type="text/plain"
    )
```

### 2. 文件流式上传

```python
from fastapi import File, UploadFile
import aiofiles

@app.post("/upload-large-file/")
async def upload_large_file(file: UploadFile = File(...)):
    async with aiofiles.open(f"uploads/{file.filename}", "wb") as f:
        while chunk := await file.read(1024):  # 1KB chunks
            await f.write(chunk)
    
    return {"filename": file.filename, "status": "uploaded"}
```

## 性能优化

### 1. 连接池配置

```python
import asyncpg
from asyncpg import Pool

class DatabasePool:
    pool: Pool = None

db_pool = DatabasePool()

async def create_pool():
    db_pool.pool = await asyncpg.create_pool(
        "postgresql://user:password@localhost/dbname",
        min_size=10,
        max_size=20,
        command_timeout=60
    )

async def get_db_connection():
    async with db_pool.pool.acquire() as connection:
        yield connection
```

### 2. 缓存策略

```python
from functools import wraps
import pickle

def cache_result(expire_time: int = 300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # 尝试从缓存获取
            cached_result = await redis.get(cache_key)
            if cached_result:
                return pickle.loads(cached_result)
            
            # 执行函数并缓存结果
            result = await func(*args, **kwargs)
            await redis.setex(
                cache_key, 
                expire_time, 
                pickle.dumps(result)
            )
            return result
        return wrapper
    return decorator

@cache_result(expire_time=600)
async def get_popular_articles():
    # 耗时的数据库查询
    return await ArticleService.get_popular_articles()
```

## 总结

FastAPI的异步特性为构建高性能API提供了强大支持，通过合理使用异步编程模式可以显著提升应用的并发处理能力。''',
        'category': '后端开发'
    },
    {
        'title': 'Spring Boot 3.0 新特性详解',
        'summary': '全面介绍Spring Boot 3.0的新特性，包括原生镜像支持、虚拟线程等。',
        'content': '''# Spring Boot 3.0 新特性详解

## 概述

Spring Boot 3.0 是一个重大版本更新，带来了许多激动人心的新特性和改进。

## 主要新特性

### 1. Java 17 基线要求

Spring Boot 3.0 要求 Java 17 作为最低版本：

```java
// 使用 Java 17 的新特性
public record UserDto(String name, String email, int age) {}

public class UserService {
    public UserDto createUser(String name, String email, int age) {
        // 使用 switch 表达式
        var status = switch (age) {
            case int a when a < 18 -> "未成年";
            case int a when a < 65 -> "成年";
            default -> "老年";
        };
        
        return new UserDto(name, email, age);
    }
}
```

### 2. 原生镜像支持

```xml
<!-- pom.xml -->
<plugin>
    <groupId>org.graalvm.buildtools</groupId>
    <artifactId>native-maven-plugin</artifactId>
</plugin>
```

```java
@SpringBootApplication
@RegisterReflectionForBinding({User.class, Article.class})
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}

// 原生提示配置
@NativeHint(
    types = @TypeHint(types = MyService.class, access = AccessBits.ALL)
)
public class NativeConfiguration {
}
```

### 3. 虚拟线程支持

```java
@Configuration
@EnableAsync
public class AsyncConfig {
    
    @Bean
    public Executor taskExecutor() {
        return Executors.newVirtualThreadPerTaskExecutor();
    }
}

@Service
public class AsyncService {
    
    @Async
    public CompletableFuture<String> processAsync() {
        // 虚拟线程中执行
        return CompletableFuture.completedFuture("处理完成");
    }
}
```

### 4. 可观测性改进

```java
// 自定义指标
@Component
public class CustomMetrics {
    
    private final Counter requestCounter;
    private final Timer requestTimer;
    
    public CustomMetrics(MeterRegistry meterRegistry) {
        this.requestCounter = Counter.builder("custom.requests")
            .description("自定义请求计数器")
            .register(meterRegistry);
            
        this.requestTimer = Timer.builder("custom.request.duration")
            .description("请求处理时间")
            .register(meterRegistry);
    }
    
    @EventListener
    public void handleRequest(RequestEvent event) {
        requestCounter.increment();
        requestTimer.record(event.getDuration(), TimeUnit.MILLISECONDS);
    }
}

// 分布式追踪
@RestController
public class UserController {
    
    @GetMapping("/users/{id}")
    @NewSpan("get-user")
    public ResponseEntity<User> getUser(@PathVariable Long id) {
        // 自动创建 span
        return ResponseEntity.ok(userService.findById(id));
    }
}
```

### 5. 问题详情支持 (RFC 7807)

```java
@ControllerAdvice
public class GlobalExceptionHandler {
    
    @ExceptionHandler(UserNotFoundException.class)
    public ResponseEntity<ProblemDetail> handleUserNotFound(
            UserNotFoundException ex) {
        
        ProblemDetail problemDetail = ProblemDetail.forStatusAndDetail(
            HttpStatus.NOT_FOUND, 
            ex.getMessage()
        );
        
        problemDetail.setTitle("用户未找到");
        problemDetail.setProperty("userId", ex.getUserId());
        problemDetail.setProperty("timestamp", Instant.now());
        
        return ResponseEntity.of(problemDetail).build();
    }
}
```

### 6. HTTP 接口声明式客户端

```java
@HttpExchange("/api/users")
public interface UserClient {
    
    @GetExchange("/{id}")
    User getUser(@PathVariable Long id);
    
    @PostExchange
    User createUser(@RequestBody User user);
    
    @PutExchange("/{id}")
    User updateUser(@PathVariable Long id, @RequestBody User user);
    
    @DeleteExchange("/{id}")
    void deleteUser(@PathVariable Long id);
}

@Configuration
public class HttpClientConfig {
    
    @Bean
    public UserClient userClient() {
        WebClient webClient = WebClient.builder()
            .baseUrl("http://localhost:8080")
            .build();
            
        HttpServiceProxyFactory factory = HttpServiceProxyFactory
            .builder(WebClientAdapter.forClient(webClient))
            .build();
            
        return factory.createClient(UserClient.class);
    }
}
```

## 配置改进

### 1. 新的配置属性

```yaml
# application.yml
spring:
  threads:
    virtual:
      enabled: true
  
  docker:
    compose:
      enabled: true
      file: docker-compose.yml
  
  sql:
    init:
      platform: postgresql
      
management:
  tracing:
    sampling:
      probability: 1.0
  metrics:
    distribution:
      percentiles-histogram:
        http.server.requests: true
```

### 2. 配置数据验证

```java
@ConfigurationProperties("app.user")
@Validated
public class UserProperties {
    
    @NotBlank
    private String defaultRole;
    
    @Min(1)
    @Max(100)
    private int maxLoginAttempts;
    
    @Valid
    private Security security = new Security();
    
    public static class Security {
        @NotNull
        private Duration sessionTimeout;
        
        @Pattern(regexp = "^[A-Z0-9]{32}$")
        private String secretKey;
        
        // getters and setters
    }
    
    // getters and setters
}
```

## 测试改进

### 1. 测试切片增强

```java
@WebMvcTest(UserController.class)
class UserControllerTest {
    
    @MockBean
    private UserService userService;
    
    @Test
    void shouldReturnUser() throws Exception {
        // 使用新的测试工具
        given(userService.findById(1L))
            .willReturn(new User("John", "john@example.com"));
        
        mockMvc.perform(get("/users/1"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.name").value("John"));
    }
}

@TestcontainersConfiguration(disabledWithoutDocker = true)
class IntegrationTest {
    
    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15")
            .withDatabaseName("testdb")
            .withUsername("test")
            .withPassword("test");
    
    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }
}
```

### 2. AOT 测试支持

```java
@SpringBootTest
@EnabledInAotMode
class AotTest {
    
    @Test
    void contextLoads() {
        // 在 AOT 模式下测试
    }
}
```

## 性能优化

### 1. 启动时间优化

```java
@SpringBootApplication
@ImportRuntimeHints(MyRuntimeHints.class)
public class Application {
    
    public static void main(String[] args) {
        System.setProperty("spring.aot.enabled", "true");
        SpringApplication.run(Application.class, args);
    }
}

public class MyRuntimeHints implements RuntimeHintsRegistrar {
    
    @Override
    public void registerHints(RuntimeHints hints, ClassLoader classLoader) {
        // 注册反射提示
        hints.reflection().registerType(User.class, MemberCategory.INVOKE_DECLARED_METHODS);
        
        // 注册资源提示
        hints.resources().registerPattern("static/**");
    }
}
```

### 2. 内存使用优化

```java
@Configuration
public class OptimizationConfig {
    
    @Bean
    @ConditionalOnProperty("app.optimization.enabled")
    public BeanPostProcessor memoryOptimizer() {
        return new BeanPostProcessor() {
            @Override
            public Object postProcessAfterInitialization(Object bean, String beanName) {
                // 内存优化逻辑
                return bean;
            }
        };
    }
}
```

## 总结

Spring Boot 3.0 通过 Java 17 支持、原生镜像、虚拟线程等新特性，为构建现代化的 Java 应用提供了强大支持。''',
        'category': '后端开发'
    }
]

def create_articles():
    categories = list(Category.objects.all())
    users = list(User.objects.all())
    
    if not categories or not users:
        print("请先创建分类和用户")
        return
    
    created_count = 0
    for article_data in backend_articles:
        if Article.objects.filter(title=article_data['title']).exists():
            print(f"文章已存在: {article_data['title']}")
            continue
        
        category = None
        for cat in categories:
            if cat.name == article_data['category']:
                category = cat
                break
        
        if not category:
            category = random.choice(categories)
        
        author = random.choice(users)
        created_at = datetime.now() - timedelta(days=random.randint(1, 30))
        
        article = Article.objects.create(
            title=article_data['title'],
            content=article_data['content'],
            summary=article_data['summary'],
            author=author,
            category=category,
            status='published',
            featured=random.choice([True, False]),
            views=random.randint(100, 1000),
            likes=random.randint(10, 100),
            created_at=created_at,
            updated_at=created_at
        )
        
        created_count += 1
        print(f"创建文章: {article.title}")
    
    print(f"\n总共创建了 {created_count} 篇后端开发文章")

if __name__ == '__main__':
    create_articles()