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
    
    return {
      count,
      state
    }
  }
}
```

### 2. 响应式引用
- `ref()` - 创建响应式引用
- `reactive()` - 创建响应式对象
- `computed()` - 计算属性

### 3. 生命周期钩子
```javascript
import { onMounted, onUnmounted } from 'vue'

export default {
  setup() {
    onMounted(() => {
      console.log('组件已挂载')
    })
    
    onUnmounted(() => {
      console.log('组件即将卸载')
    })
  }
}
```

## 最佳实践

1. 使用 `<script setup>` 语法糖
2. 合理组织可复用逻辑
3. 避免过度使用 reactive

## 总结

Composition API 为 Vue 3 带来了更强大的逻辑复用能力和更好的 TypeScript 支持。''',
        'category': 'frontend',
        'tags': ['Vue.js', 'JavaScript', 'Frontend']
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

# 运行协程
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

### 3. 事件循环
```python
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
```

## 实际应用场景

1. Web爬虫
2. API调用
3. 数据库操作
4. 文件I/O

## 性能优势

异步编程在I/O密集型任务中能显著提升性能，特别是在处理大量并发请求时。''',
        'category': 'backend',
        'tags': ['Python', 'Async', 'Backend']
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
# 构建阶段
FROM node:16-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# 运行阶段
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

### 3. 安全考虑
```dockerfile
# 创建非root用户
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001
USER nextjs
```

## Docker Compose

```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=myapp
```

## 生产环境部署

1. 使用健康检查
2. 配置资源限制
3. 实施日志管理
4. 设置监控告警''',
        'category': 'devops',
        'tags': ['Docker', 'DevOps', 'Deployment']
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
      <button onClick={() => setCount(count + 1)}>
        Increment
      </button>
    </div>
  );
}
```

### 2. useEffect
```jsx
import React, { useState, useEffect } from 'react';

function UserProfile({ userId }) {
  const [user, setUser] = useState(null);
  
  useEffect(() => {
    fetchUser(userId).then(setUser);
  }, [userId]);
  
  return user ? <div>{user.name}</div> : <div>Loading...</div>;
}
```

### 3. useContext
```jsx
const ThemeContext = React.createContext();

function App() {
  return (
    <ThemeContext.Provider value="dark">
      <Header />
    </ThemeContext.Provider>
  );
}

function Header() {
  const theme = useContext(ThemeContext);
  return <h1 className={theme}>Hello World</h1>;
}
```

## 自定义Hooks

```jsx
function useLocalStorage(key, initialValue) {
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      return initialValue;
    }
  });
  
  const setValue = (value) => {
    try {
      setStoredValue(value);
      window.localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error(error);
    }
  };
  
  return [storedValue, setValue];
}
```

## 性能优化

1. 使用useMemo和useCallback
2. 避免不必要的重渲染
3. 合理使用依赖数组''',
        'category': 'frontend',
        'tags': ['React', 'JavaScript', 'Frontend']
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
// 使用process.memoryUsage()监控内存
setInterval(() => {
  const usage = process.memoryUsage();
  console.log('Memory usage:', {
    rss: Math.round(usage.rss / 1024 / 1024) + 'MB',
    heapTotal: Math.round(usage.heapTotal / 1024 / 1024) + 'MB',
    heapUsed: Math.round(usage.heapUsed / 1024 / 1024) + 'MB'
  });
}, 5000);
```

### 2. 垃圾回收优化
```bash
# 调整V8垃圾回收参数
node --max-old-space-size=4096 --optimize-for-size app.js
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

### 2. 使用Worker Threads
```javascript
const { Worker, isMainThread, parentPort } = require('worker_threads');

if (isMainThread) {
  // 主线程
  const worker = new Worker(__filename);
  worker.postMessage('Hello');
  worker.on('message', (data) => {
    console.log('Received:', data);
  });
} else {
  // 工作线程
  parentPort.on('message', (data) => {
    // CPU密集型任务
    const result = heavyComputation(data);
    parentPort.postMessage(result);
  });
}
```

## 集群模式

```javascript
const cluster = require('cluster');
const numCPUs = require('os').cpus().length;

if (cluster.isMaster) {
  // 创建工作进程
  for (let i = 0; i < numCPUs; i++) {
    cluster.fork();
  }
  
  cluster.on('exit', (worker) => {
    console.log(`Worker ${worker.process.pid} died`);
    cluster.fork();
  });
} else {
  // 工作进程运行应用
  require('./app.js');
}
```

## 缓存策略

1. Redis缓存
2. 内存缓存
3. CDN缓存
4. 数据库查询缓存''',
        'category': 'backend',
        'tags': ['Node.js', 'Performance', 'Backend']
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

// 使用
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
type Example2 = NonNullable<number | undefined>; // number
```

## 映射类型

```typescript
type Readonly<T> = {
  readonly [P in keyof T]: T[P];
};

type Partial<T> = {
  [P in keyof T]?: T[P];
};

interface User {
  id: number;
  name: string;
  email: string;
}

type ReadonlyUser = Readonly<User>;
type PartialUser = Partial<User>;
```

## 实用类型

### 1. Pick和Omit
```typescript
type UserSummary = Pick<User, 'id' | 'name'>;
type UserWithoutId = Omit<User, 'id'>;
```

### 2. Record
```typescript
type PageInfo = {
  title: string;
  url: string;
};

type Pages = Record<'home' | 'about' | 'contact', PageInfo>;
```

## 高级模式

### 1. 模板字面量类型
```typescript
type EventName<T extends string> = `on${Capitalize<T>}`;
type ClickEvent = EventName<'click'>; // 'onClick'
```

### 2. 递归类型
```typescript
type DeepReadonly<T> = {
  readonly [P in keyof T]: T[P] extends object 
    ? DeepReadonly<T[P]> 
    : T[P];
};
```

## 最佳实践

1. 合理使用类型断言
2. 避免any类型
3. 利用严格模式
4. 使用类型守卫''',
        'category': 'frontend',
        'tags': ['TypeScript', 'JavaScript', 'Types']
    }
]

def create_tech_articles():
    # 获取或创建分类
    categories = {}
    category_data = {
        'frontend': {'name': '前端开发', 'description': '前端技术相关文章'},
        'backend': {'name': '后端开发', 'description': '后端技术相关文章'},
        'devops': {'name': 'DevOps', 'description': 'DevOps和运维相关文章'},
        'database': {'name': '数据库', 'description': '数据库技术相关文章'},
        'ai': {'name': '人工智能', 'description': 'AI和机器学习相关文章'}
    }
    
    for key, data in category_data.items():
        try:
            category = Category.objects.get(name=data['name'])
            print(f"分类已存在: {category.name}")
        except Category.DoesNotExist:
            category = Category.objects.create(
                name=data['name'],
                description=data['description']
            )
            print(f"创建分类: {category.name}")
        categories[key] = category
    
    # 获取或创建用户
    users = []
    user_data = [
        {'username': 'tech_blogger', 'email': 'blogger@example.com'},
        {'username': 'dev_expert', 'email': 'expert@example.com'},
        {'username': 'code_master', 'email': 'master@example.com'}
    ]
    
    for data in user_data:
        user, created = User.objects.get_or_create(
            username=data['username'],
            defaults={
                'email': data['email'],
                'first_name': data['username'].replace('_', ' ').title()
            }
        )
        users.append(user)
        if created:
            print(f"创建用户: {user.username}")
    
    # 创建文章
    created_count = 0
    for i, article_data in enumerate(tech_articles):
        # 检查文章是否已存在
        if Article.objects.filter(title=article_data['title']).exists():
            print(f"文章已存在: {article_data['title']}")
            continue
        
        # 随机选择作者和发布时间
        author = random.choice(users)
        created_at = datetime.now() - timedelta(days=random.randint(1, 30))
        
        article = Article.objects.create(
            title=article_data['title'],
            content=article_data['content'],
            summary=article_data['summary'],
            author=author,
            category=categories[article_data['category']],
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
    create_tech_articles()