# API接口文档

## 📋 概述

Alpha技术共享平台基于Django REST Framework构建，提供完整的RESTful API接口。所有API都遵循统一的响应格式和错误处理规范。

### 基础信息
- **基础URL**: `http://localhost:8000/api/v1/`
- **认证方式**: JWT Token
- **数据格式**: JSON
- **字符编码**: UTF-8

### 版本控制
- 当前版本: v1
- 版本标识: 在URL路径中体现 `/api/v1/`
- 向后兼容: 新版本保持对旧版本的兼容性

### 公共查询参数规范

为避免重复说明，本文档将列表类接口的通用查询参数统一定义如下：

**通用参数类型（JSON）**
```json
{
  "page": "number (>=1, default: 1)",
  "page_size": "number (1-100, default: 20)",
  "search": "string (模糊匹配)",
  "ordering": "string (字段名，前缀 '-' 表示降序)"
}
```

说明：
- 分页：`page` 从 1 开始；`page_size` 建议 1–100。
- 排序：`ordering` 取模型允许的字段，如 `created_at`、`views`；降序示例 `-created_at`。
- 日期时间：若有日期筛选，统一使用 ISO 8601（如 `2025-01-17T10:30:00Z`）。
- 布尔：使用 `true/false`（小写）。

**查询参数示例（JSON）**
```json
{
  "page": 1,
  "page_size": 20,
  "search": "keyword",
  "ordering": "-created_at"
}
```

---

## 🔐 认证

### JWT Token认证

#### 获取Token
```http
POST /api/v1/auth/token/
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

**响应示例**
```json
{
  "status": "success",
  "data": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  },
  "message": "登录成功"
}
```

#### 刷新Token
```http
POST /api/v1/auth/token/refresh/
Content-Type: application/json

{
  "refresh": "your_refresh_token"
}
```

#### 使用Token
```http
GET /api/v1/users/me/
Authorization: Bearer your_access_token
```

### 权限级别

#### 公开接口
- 用户注册: `POST /api/v1/auth/register/`
- 用户登录: `POST /api/v1/auth/login/`
- 文章列表: `GET /api/v1/articles/`
- 分类列表: `GET /api/v1/categories/`

#### 认证接口
- 用户信息: `GET /api/v1/users/me/`
- 用户资料: `GET /api/v1/profiles/`
- 个人文章: `GET /api/v1/articles/my/`

#### 管理员接口
- 用户管理: `GET /api/v1/users/`
- 系统设置: `GET /api/v1/settings/`
- 数据统计: `GET /api/v1/stats/`

---

## 📡 接口列表

除非另有说明，本文中所有“列表”接口均支持“公共查询参数规范”中的 `page`、`page_size`、`search`、`ordering`。

### 用户认证模块

#### 用户注册
```http
POST /api/v1/auth/register/
Content-Type: application/json

{
  "username": "newuser",
  "email": "user@example.com",
  "password": "secure_password123",
  "first_name": "张",
  "last_name": "三"
}
```

**响应字段**
- `username`: 用户名（必填，唯一）
- `email`: 邮箱（必填，唯一）
- `password`: 密码（必填，最少8位）
- `first_name`: 名（可选）
- `last_name`: 姓（可选）

#### 用户登录
```http
POST /api/v1/auth/login/
Content-Type: application/json

{
  "username": "username",
  "password": "password"
}
```

**响应字段**
- `user`: 用户信息
- `tokens`: 包含access和refresh token
- `message`: 登录状态消息

#### 用户登出
```http
POST /api/v1/auth/logout/
Authorization: Bearer your_access_token
```

#### 获取当前用户信息
```http
GET /api/v1/users/me/
Authorization: Bearer your_access_token
```

**响应示例**
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "first_name": "张",
    "last_name": "三",
    "avatar": "http://localhost:8000/media/avatars/default.jpg",
    "date_joined": "2024-01-15T10:30:00Z",
    "last_login": "2025-01-17T14:20:00Z"
  }
}
```

### 文章管理模块

#### 获取文章列表
```http
GET /api/v1/articles/
```

**查询参数**
- `page`: 页码（默认1）
- `page_size`: 每页数量（默认20，最大100）
- `category`: 分类ID
- `author`: 作者ID
- `featured`: 是否推荐（true/false）
- `search`: 搜索关键词
- `ordering`: 排序字段（created_at, views, likes）

**查询参数类型（JSON）**
```json
{
  "page": "number (>=1, default: 1)",
  "page_size": "number (1-100, default: 20)",
  "category": "number (Category ID)",
  "author": "number (User ID)",
  "featured": "boolean",
  "search": "string",
  "ordering": "string (created_at|views|likes; prefix '-' for desc)"
}
```

**查询参数示例（JSON）**
```json
{
  "page": 1,
  "page_size": 20,
  "category": 3,
  "author": 42,
  "featured": true,
  "search": "python best practice",
  "ordering": "-views"
}
```

**响应示例**
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "title": "Python开发最佳实践",
      "summary": "本文介绍Python开发中的最佳实践...",
      "content": "完整的文章内容...",
      "author": {
        "id": 1,
        "username": "author",
        "avatar": "http://localhost:8000/media/avatars/author.jpg"
      },
      "category": {
        "id": 1,
        "name": "技术开发",
        "slug": "tech-dev"
      },
      "tags": [
        {"id": 1, "name": "Python", "color": "#67C23A"},
        {"id": 2, "name": "最佳实践", "color": "#409EFF"}
      ],
      "status": "published",
      "views": 150,
      "likes": 25,
      "comments_count": 8,
      "reading_time": 5,
      "cover_image": "http://localhost:8000/media/articles/covers/python.jpg",
      "created_at": "2025-01-15T10:30:00Z",
      "updated_at": "2025-01-17T14:20:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 150,
    "total_pages": 8
  }
}
```

#### 获取文章详情
```http
GET /api/v1/articles/{id}/
```

#### 创建文章
```http
POST /api/v1/articles/
Authorization: Bearer your_access_token
Content-Type: application/json

{
  "title": "新文章标题",
  "content": "文章内容",
  "summary": "文章摘要",
  "category": 1,
  "tags": [1, 2, 3],
  "status": "draft"
}
```

#### 更新文章
```http
PUT /api/v1/articles/{id}/
Authorization: Bearer your_access_token
Content-Type: application/json

{
  "title": "更新后的标题",
  "content": "更新后的内容"
}
```

#### 删除文章
```http
DELETE /api/v1/articles/{id}/
Authorization: Bearer your_access_token
```

#### 文章点赞
```http
POST /api/v1/articles/{id}/like/
Authorization: Bearer your_access_token
```

#### 文章收藏
```http
POST /api/v1/articles/{id}/bookmark/
Authorization: Bearer your_access_token
```

#### 获取文章评论
```http
GET /api/v1/articles/{id}/comments/
```

**查询参数类型（JSON）**
```json
{
  "page": "number (>=1, default: 1)",
  "page_size": "number (1-100, default: 20)",
  "ordering": "string (created_at; prefix '-' for desc)"
}
```

**查询参数示例（JSON）**
```json
{
  "page": 1,
  "page_size": 20,
  "ordering": "-created_at"
}
```

### 分类管理模块

#### 获取分类列表
```http
GET /api/v1/categories/
```

**查询参数类型（JSON）**
```json
{
  "page": "number (>=1, default: 1)",
  "page_size": "number (1-100, default: 20)",
  "search": "string (名称/描述模糊匹配)",
  "ordering": "string (name|created_at; prefix '-' for desc)"
}
```

**查询参数示例（JSON）**
```json
{
  "page": 1,
  "page_size": 50,
  "search": "技术",
  "ordering": "name"
}
```

**响应示例**
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "name": "技术开发",
      "slug": "tech-dev",
      "description": "技术开发相关文章",
      "parent": null,
      "status": "active",
      "order": 1,
      "icon": "code",
      "color": "#409EFF",
      "article_count": 45,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

#### 获取分类详情
```http
GET /api/v1/categories/{id}/
```

#### 获取分类下的文章
```http
GET /api/v1/categories/{id}/articles/
```

**查询参数类型（JSON）**
```json
{
  "page": "number (>=1, default: 1)",
  "page_size": "number (1-100, default: 20)",
  "ordering": "string (created_at|views|likes; prefix '-' for desc)"
}
```

**查询参数示例（JSON）**
```json
{
  "page": 2,
  "page_size": 20,
  "ordering": "-created_at"
}
```

### 标签管理模块

#### 获取标签列表
```http
GET /api/v1/tags/
```

**查询参数类型（JSON）**
```json
{
  "page": "number (>=1, default: 1)",
  "page_size": "number (1-100, default: 20)",
  "search": "string (名称模糊匹配)",
  "ordering": "string (name|created_at; prefix '-' for desc)"
}
```

**查询参数示例（JSON）**
```json
{
  "page": 1,
  "page_size": 30,
  "search": "python",
  "ordering": "-created_at"
}
```

#### 获取标签详情
```http
GET /api/v1/tags/{id}/
```

### 英语学习模块

#### 获取单词列表
```http
GET /api/v1/english/words/
```

**查询参数**
- `difficulty_level`: 难度级别（beginner, intermediate, advanced）
- `category_hint`: 分类提示
- `search`: 搜索关键词

**查询参数类型（JSON）**
```json
{
  "page": "number (>=1, default: 1)",
  "page_size": "number (1-100, default: 20)",
  "difficulty_level": "string (beginner|intermediate|advanced)",
  "category_hint": "string",
  "search": "string",
  "ordering": "string (frequency_rank|created_at; prefix '-' for desc)"
}
```

**查询参数示例（JSON）**
```json
{
  "page": 1,
  "page_size": 20,
  "difficulty_level": "beginner",
  "category_hint": "greetings",
  "search": "hello",
  "ordering": "frequency_rank"
}
```

**响应示例**
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "word": "hello",
      "phonetic": "/həˈloʊ/",
      "part_of_speech": "interjection",
      "definition": "你好",
      "example": "Hello, how are you?",
      "difficulty_level": "beginner",
      "frequency_rank": 100,
      "audio_url": "http://localhost:8000/media/audio/hello.mp3",
      "image_url": "http://localhost:8000/media/images/hello.jpg"
    }
  ]
}
```

#### 获取单词详情
```http
GET /api/v1/english/words/{id}/
```

#### 获取新闻列表
```http
GET /api/v1/english/news/
```

**查询参数**
- `category`: 新闻分类
- `difficulty_level`: 难度级别
- `source`: 新闻来源
- `search`: 搜索关键词

**查询参数类型（JSON）**
```json
{
  "page": "number (>=1, default: 1)",
  "page_size": "number (1-100, default: 20)",
  "category": "string",
  "difficulty_level": "string (beginner|intermediate|advanced)",
  "source": "string (publisher key)",
  "search": "string",
  "ordering": "string (publish_date|created_at; prefix '-' for desc)"
}
```

**查询参数示例（JSON）**
```json
{
  "page": 1,
  "page_size": 10,
  "category": "technology",
  "difficulty_level": "intermediate",
  "source": "uk.BBC",
  "search": "AI",
  "ordering": "-publish_date"
}
```

#### 获取新闻详情
```http
GET /api/v1/english/news/{id}/
```

#### 创建打字练习会话
```http
POST /api/v1/english/typing/session/
Authorization: Bearer your_access_token
Content-Type: application/json

{
  "dictionary": "CET4",
  "chapter": 1,
  "mode": "practice"
}
```

#### 提交打字练习记录
```http
POST /api/v1/english/typing/record/
Authorization: Bearer your_access_token
Content-Type: application/json

{
  "session_id": 1,
  "word": "hello",
  "user_input": "hello",
  "is_correct": true,
  "time_spent": 1.5,
  "key_errors": []
}
```

#### 获取学习统计
```http
GET /api/v1/english/stats/
Authorization: Bearer your_access_token
```

**响应示例**
```json
{
  "status": "success",
  "data": {
    "total_words_learned": 150,
    "total_practice_time": 120,
    "accuracy_rate": 0.85,
    "current_streak": 7,
    "weekly_progress": [
      {"date": "2025-01-13", "words": 10, "time": 15},
      {"date": "2025-01-14", "words": 12, "time": 18},
      {"date": "2025-01-15", "words": 8, "time": 12}
    ]
  }
}
```

### 新闻爬取模块

#### 爬取新闻
```http
POST /api/v1/english/crawl-news/
Authorization: Bearer your_access_token
Content-Type: application/json

{
  "source": "bbc",
  "crawler": "fundus",
  "count": 10,
  "category": "technology"
}
```

**参数说明**
- `source`: 新闻源（bbc, cnn, reuters, techcrunch等）
- `crawler`: 爬虫类型（fundus, traditional）
- `count`: 爬取数量（1-50）
- `category`: 新闻分类（可选）

**响应示例**
```json
{
  "status": "success",
  "data": {
    "crawled_count": 10,
    "success_count": 8,
    "failed_count": 2,
    "details": [
      {
        "title": "BBC News Article",
        "status": "success",
        "url": "https://www.bbc.com/news/article"
      }
    ]
  },
  "message": "新闻爬取完成"
}
```

#### 获取爬取状态
```http
GET /api/v1/english/crawl-status/
Authorization: Bearer your_access_token
```

### 用户管理模块

#### 获取用户列表（管理员）
```http
GET /api/v1/users/
Authorization: Bearer your_access_token
```

**查询参数类型（JSON）**
```json
{
  "page": "number (>=1, default: 1)",
  "page_size": "number (1-100, default: 20)",
  "search": "string (用户名/邮箱模糊匹配)",
  "ordering": "string (date_joined|last_login; prefix '-' for desc)"
}
```

**查询参数示例（JSON）**
```json
{
  "page": 1,
  "page_size": 50,
  "search": "test",
  "ordering": "-last_login"
}
```

#### 获取用户详情
```http
GET /api/v1/users/{id}/
Authorization: Bearer your_access_token
```

#### 更新用户信息
```http
PUT /api/v1/users/{id}/
Authorization: Bearer your_access_token
Content-Type: application/json

{
  "first_name": "新名字",
  "last_name": "新姓氏",
  "email": "newemail@example.com"
}
```

#### 获取用户资料
```http
GET /api/v1/profiles/{id}/
Authorization: Bearer your_access_token
```

#### 更新用户资料
```http
PUT /api/v1/profiles/{id}/
Authorization: Bearer your_access_token
Content-Type: application/json

{
  "bio": "个人简介",
  "location": "北京",
  "company": "科技公司",
  "skills": "Python, Vue.js, Django"
}
```

### 文件上传模块

#### 上传图片
```http
POST /api/v1/upload/image/
Authorization: Bearer your_access_token
Content-Type: multipart/form-data

file: [图片文件]
```

#### 上传头像
```http
POST /api/v1/upload/avatar/
Authorization: Bearer your_access_token
Content-Type: multipart/form-data

file: [头像文件]
```

---

## 📊 响应格式

### 成功响应
```json
{
  "status": "success",
  "data": {},
  "message": "操作成功",
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 100,
    "total_pages": 5
  }
}
```

### 错误响应
```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "字段验证失败",
    "details": {
      "title": ["标题不能为空"],
      "content": ["内容不能为空"]
    }
  }
}
```

### 分页响应
```json
{
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 150,
    "total_pages": 8,
    "has_next": true,
    "has_previous": false,
    "next_page": 2,
    "previous_page": null
  }
}
```

---

## ⚠️ 错误处理

### 错误代码

#### HTTP状态码
- `200 OK`: 请求成功
- `201 Created`: 创建成功
- `400 Bad Request`: 请求参数错误
- `401 Unauthorized`: 未认证
- `403 Forbidden`: 权限不足
- `404 Not Found`: 资源不存在
- `429 Too Many Requests`: 请求频率过高
- `500 Internal Server Error`: 服务器内部错误

#### 业务错误码
- `VALIDATION_ERROR`: 字段验证失败
- `AUTHENTICATION_FAILED`: 认证失败
- `PERMISSION_DENIED`: 权限不足
- `RESOURCE_NOT_FOUND`: 资源不存在
- `DUPLICATE_RESOURCE`: 资源重复
- `RATE_LIMIT_EXCEEDED`: 请求频率超限

### 错误处理示例

#### 字段验证错误
```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "字段验证失败",
    "details": {
      "username": ["用户名已存在"],
      "email": ["邮箱格式不正确"],
      "password": ["密码长度至少8位"]
    }
  }
}
```

#### 权限不足错误
```json
{
  "status": "error",
  "error": {
    "code": "PERMISSION_DENIED",
    "message": "您没有权限执行此操作",
    "details": {
      "required_permission": "can_delete_article",
      "user_permissions": ["can_view_article", "can_edit_article"]
    }
  }
}
```

---

## 🔒 安全规范

### 认证要求
- 所有修改操作必须提供有效的JWT Token
- Token过期时间为1小时，需要定期刷新
- 敏感操作可能需要重新输入密码

### 权限控制
- 用户只能访问和修改自己的数据
- 管理员可以访问所有数据
- 文章作者可以编辑自己的文章
- 评论作者可以编辑自己的评论

### 数据验证
- 所有输入数据都进行严格验证
- 防止SQL注入和XSS攻击
- 文件上传类型和大小限制
- 敏感信息加密存储

### 频率限制
- API调用频率限制：每分钟100次
- 登录尝试限制：每分钟5次
- 文件上传限制：每小时10个文件

---

## 📚 使用示例

### Python示例

#### 使用requests库
```python
import requests

# 用户登录
def login(username, password):
    url = "http://localhost:8000/api/v1/auth/login/"
    data = {"username": username, "password": password}
    response = requests.post(url, json=data)
    return response.json()

# 获取文章列表
def get_articles(token, page=1):
    url = "http://localhost:8000/api/v1/articles/"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"page": page}
    response = requests.get(url, headers=headers, params=params)
    return response.json()

# 使用示例
if __name__ == "__main__":
    # 登录获取token
    result = login("testuser", "password123")
    if result["status"] == "success":
        token = result["data"]["tokens"]["access"]
        
        # 获取文章列表
        articles = get_articles(token, page=1)
        print(f"获取到 {len(articles['data'])} 篇文章")
```

#### 使用Django REST Framework客户端
```python
from rest_framework.test import APIClient

client = APIClient()

# 用户登录
response = client.post('/api/v1/auth/login/', {
    'username': 'testuser',
    'password': 'password123'
})
token = response.data['data']['tokens']['access']

# 设置认证头
client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

# 获取用户信息
response = client.get('/api/v1/users/me/')
print(response.data)
```

### JavaScript示例

#### 使用fetch API
```javascript
// 用户登录
async function login(username, password) {
    const response = await fetch('/api/v1/auth/login/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password })
    });
    return await response.json();
}

// 获取文章列表
async function getArticles(token, page = 1) {
    const response = await fetch(`/api/v1/articles/?page=${page}`, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    return await response.json();
}

// 使用示例
async function main() {
    try {
        // 登录
        const loginResult = await login('testuser', 'password123');
        if (loginResult.status === 'success') {
            const token = loginResult.data.tokens.access;
            
            // 获取文章
            const articles = await getArticles(token, 1);
            console.log(`获取到 ${articles.data.length} 篇文章`);
        }
    } catch (error) {
        console.error('操作失败:', error);
    }
}
```

#### 使用axios
```javascript
import axios from 'axios';

// 创建axios实例
const api = axios.create({
    baseURL: '/api/v1/',
    timeout: 10000
});

// 请求拦截器
api.interceptors.request.use(config => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// 响应拦截器
api.interceptors.response.use(
    response => response.data,
    error => {
        if (error.response?.status === 401) {
            // Token过期，跳转登录
            localStorage.removeItem('token');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

// API方法
export const authAPI = {
    login: (credentials) => api.post('auth/login/', credentials),
    register: (userData) => api.post('auth/register/', userData),
    logout: () => api.post('auth/logout/')
};

export const articleAPI = {
    getList: (params) => api.get('articles/', { params }),
    getDetail: (id) => api.get(`articles/${id}/`),
    create: (data) => api.post('articles/', data),
    update: (id, data) => api.put(`articles/${id}/`, data),
    delete: (id) => api.delete(`articles/${id}/`)
};
```

---

## 📝 更新日志

### v1.0.0 (2025-01-17)
- ✨ 完整的用户认证系统
- ✨ 文章管理API
- ✨ 英语学习API
- ✨ 新闻爬取API
- ✨ 文件上传API

### v0.9.0 (2024-12-15)
- 🎉 基础API框架
- 🔧 用户管理接口
- 📝 文章管理接口

---

## 📞 支持

### API支持
- 查看 [开发者指南](../DEVELOPMENT.md) 了解开发环境
- 参考 [模块文档](../modules/) 理解功能实现
- 查看 [常见问题](../FAQ.md) 解决使用问题

### 技术问题
- 检查API响应状态码和错误信息
- 验证请求参数和认证信息
- 查看服务器日志获取详细错误信息

---

*最后更新：2025-01-17*
*更新内容：创建完整的API接口文档，包含所有模块的接口说明*
