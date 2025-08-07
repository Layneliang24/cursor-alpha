#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime, timedelta
import random

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alpha.settings')
django.setup()

from apps.articles.models import Article
from apps.categories.models import Category
from apps.users.models import User

# 技术博客文章数据
tech_articles = [
    {
        'title': 'Vue 3 Composition API 完全指南',
        'summary': '深入探讨Vue 3 Composition API的核心概念、使用方法和最佳实践，帮助开发者更好地理解和应用这一新特性。',
        'content': '''# Vue 3 Composition API 完全指南

## 什么是 Composition API
Composition API 是 Vue 3 中引入的一套新的 API，它提供了一种更灵活的方式来组织组件逻辑。

## 核心概念
### 1. setup() 函数
```javascript
import { ref, reactive } from 'vue'
export default {
  setup() {
    const count = ref(0)
    const state = reactive({ name: 'Vue 3' })
    return { count, state }
  }
}
```

### 2. 响应式引用
- ref() - 创建响应式引用
- reactive() - 创建响应式对象  
- computed() - 计算属性

## 最佳实践
1. 使用 <script setup> 语法糖
2. 合理组织可复用逻辑
3. 避免过度使用 reactive

Composition API 为 Vue 3 带来了更强大的逻辑复用能力。'''
    },
    {
        'title': 'Python异步编程深度解析',
        'summary': '全面介绍Python异步编程的概念、asyncio库的使用、协程的工作原理以及在实际项目中的应用场景。',
        'content': '''# Python异步编程深度解析

## 异步编程基础
异步编程是一种编程范式，允许程序在等待某些操作完成时继续执行其他任务。

## asyncio 核心概念
### 1. 协程 (Coroutines)
```python
import asyncio
async def hello_world():
    print("Hello")
    await asyncio.sleep(1)
    print("World")
asyncio.run(hello_world())
```

### 2. 任务 (Tasks)
```python
async def main():
    task1 = asyncio.create_task(fetch_data(1))
    task2 = asyncio.create_task(fetch_data(2))
    result1 = await task1
    result2 = await task2
```

## 实际应用场景
1. Web爬虫
2. API调用
3. 数据库操作
4. 文件I/O

异步编程在I/O密集型任务中能显著提升性能。'''
    },
    {
        'title': 'Docker容器化部署最佳实践',
        'summary': '详细介绍Docker容器化技术的核心概念、Dockerfile编写技巧、多阶段构建以及生产环境部署策略。',
        'content': '''# Docker容器化部署最佳实践

## Docker基础概念
Docker是一个开源的容器化平台，可以将应用程序及其依赖项打包到轻量级、可移植的容器中。

## Dockerfile最佳实践
### 1. 多阶段构建
```dockerfile
FROM node:16-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:16-alpine
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
```

### 2. 优化镜像大小
- 使用Alpine Linux基础镜像
- 清理不必要的文件
- 合并RUN指令

## 生产环境部署
1. 使用健康检查
2. 配置资源限制
3. 实施日志管理
4. 设置监控告警'''
    },
    {
        'title': 'React Hooks深入理解与实践',
        'summary': '深入探讨React Hooks的工作原理、常用Hook的使用方法、自定义Hook的开发以及性能优化技巧。',
        'content': '''# React Hooks深入理解与实践

## Hooks简介
React Hooks是React 16.8引入的新特性，允许在函数组件中使用状态和其他React特性。

## 常用Hooks
### 1. useState
```jsx
import React, { useState } from 'react';
function Counter() {
  const [count, setCount] = useState(0);
  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>Increment</button>
    </div>
  );
}
```

### 2. useEffect
```jsx
function UserProfile({ userId }) {
  const [user, setUser] = useState(null);
  useEffect(() => {
    fetchUser(userId).then(setUser);
  }, [userId]);
  return user ? <div>{user.name}</div> : <div>Loading...</div>;
}
```

## 性能优化
1. 使用useMemo和useCallback
2. 避免不必要的重渲染
3. 合理使用依赖数组'''
    },
    {
        'title': 'Node.js性能优化实战指南',
        'summary': '从内存管理、事件循环、集群模式等多个角度分析Node.js性能优化策略，提供实用的优化技巧和工具。',
        'content': '''# Node.js性能优化实战指南

## 性能优化基础
Node.js性能优化涉及多个方面，包括代码优化、内存管理、I/O优化等。

## 内存管理
### 1. 内存泄漏检测
```javascript
setInterval(() => {
  const usage = process.memoryUsage();
  console.log('Memory usage:', {
    rss: Math.round(usage.rss / 1024 / 1024) + 'MB',
    heapTotal: Math.round(usage.heapTotal / 1024 / 1024) + 'MB',
    heapUsed: Math.round(usage.heapUsed / 1024 / 1024) + 'MB'
  });
}, 5000);
```

## 事件循环优化
### 1. 避免阻塞事件循环
```javascript
// 错误示例：同步操作阻塞事件循环
const data = fs.readFileSync('large-file.txt');

// 正确示例：使用异步操作
fs.readFile('large-file.txt', (err, data) => {
  if (err) throw err;
  // 处理数据
});
```

## 缓存策略
1. Redis缓存
2. 内存缓存
3. CDN缓存
4. 数据库查询缓存'''
    },
    {
        'title': 'TypeScript高级类型系统详解',
        'summary': '深入探讨TypeScript的高级类型特性，包括泛型、条件类型、映射类型等，帮助开发者编写更安全的代码。',
        'content': '''# TypeScript高级类型系统详解

## 泛型 (Generics)
泛型允许我们创建可重用的组件，这些组件可以处理多种类型的数据。

### 基础泛型
```typescript
function identity<T>(arg: T): T {
  return arg;
}
const result = identity<string>("hello");
const number = identity<number>(42);
```

### 泛型约束
```typescript
interface Lengthwise {
  length: number;
}
function loggingIdentity<T extends Lengthwise>(arg: T): T {
  console.log(arg.length);
  return arg;
}
```

## 条件类型
```typescript
type NonNullable<T> = T extends null | undefined ? never : T;
type Example1 = NonNullable<string | null>; // string
```

## 映射类型
```typescript
type Readonly<T> = {
  readonly [P in keyof T]: T[P];
};
type Partial<T> = {
  [P in keyof T]?: T[P];
};
```

## 最佳实践
1. 合理使用类型断言
2. 避免any类型
3. 利用严格模式
4. 使用类型守卫'''
    }
]

def create_articles():
    # 获取现有分类
    categories = list(Category.objects.all())
    if not categories:
        print("没有找到分类，请先创建分类")
        return
    
    # 获取现有用户
    users = list(User.objects.all())
    if not users:
        print("没有找到用户，请先创建用户")
        return
    
    print(f"找到 {len(categories)} 个分类，{len(users)} 个用户")
    
    # 创建文章
    created_count = 0
    for article_data in tech_articles:
        # 检查文章是否已存在
        if Article.objects.filter(title=article_data['title']).exists():
            print(f"文章已存在: {article_data['title']}")
            continue
        
        # 随机选择分类、作者和发布时间
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
            views=random.randint(50, 500),
            likes=random.randint(5, 50),
            created_at=created_at,
            updated_at=created_at
        )
        
        created_count += 1
        print(f"创建文章: {article.title}")
    
    print(f"\n总共创建了 {created_count} 篇技术博客文章")

if __name__ == '__main__':
    create_articles()