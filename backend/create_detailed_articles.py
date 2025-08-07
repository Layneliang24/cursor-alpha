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

# 技术文章数据
tech_articles = [
    # 前端开发类
    {
        'title': 'Vue 3 响应式原理深度解析',
        'summary': '深入探讨Vue 3响应式系统的实现原理，包括Proxy、effect、track和trigger机制。',
        'content': '''# Vue 3 响应式原理深度解析

## 概述

Vue 3 的响应式系统是其核心特性之一，相比 Vue 2 有了重大改进。本文将深入分析其实现原理。

## 响应式系统架构

### 1. Proxy 代理

Vue 3 使用 Proxy 替代了 Vue 2 的 Object.defineProperty：

```javascript
function reactive(target) {
  return new Proxy(target, {
    get(target, key, receiver) {
      // 依赖收集
      track(target, key)
      return Reflect.get(target, key, receiver)
    },
    set(target, key, value, receiver) {
      const result = Reflect.set(target, key, value, receiver)
      // 触发更新
      trigger(target, key)
      return result
    }
  })
}
```

### 2. 依赖收集机制

```javascript
let activeEffect = null
const targetMap = new WeakMap()

function track(target, key) {
  if (!activeEffect) return
  
  let depsMap = targetMap.get(target)
  if (!depsMap) {
    targetMap.set(target, (depsMap = new Map()))
  }
  
  let dep = depsMap.get(key)
  if (!dep) {
    depsMap.set(key, (dep = new Set()))
  }
  
  dep.add(activeEffect)
}
```

### 3. 副作用函数

```javascript
function effect(fn) {
  const effectFn = () => {
    activeEffect = effectFn
    fn()
    activeEffect = null
  }
  effectFn()
  return effectFn
}
```

## 实际应用

### 计算属性实现

```javascript
function computed(getter) {
  let value
  let dirty = true
  
  const effectFn = effect(() => {
    value = getter()
    dirty = false
  })
  
  return {
    get value() {
      if (dirty) {
        effectFn()
      }
      return value
    }
  }
}
```

## 性能优势

1. **更好的性能**：Proxy 可以监听整个对象
2. **支持数组**：原生支持数组索引和 length 属性
3. **支持 Map/Set**：可以监听更多数据类型

## 总结

Vue 3 的响应式系统通过 Proxy、effect、track 和 trigger 的配合，实现了高效的数据响应式更新机制。''',
        'category': '前端开发'
    },
    {
        'title': 'React 18 并发特性详解',
        'summary': '全面介绍React 18的并发特性，包括Concurrent Mode、Suspense、useTransition等新功能。',
        'content': '''# React 18 并发特性详解

## 并发模式概述

React 18 引入了并发特性，允许 React 在渲染过程中暂停、恢复或放弃工作。

## 核心特性

### 1. Concurrent Mode

```jsx
import { createRoot } from 'react-dom/client'

const container = document.getElementById('root')
const root = createRoot(container)
root.render(<App />)
```

### 2. useTransition Hook

```jsx
import { useTransition, useState } from 'react'

function App() {
  const [isPending, startTransition] = useTransition()
  const [count, setCount] = useState(0)
  
  const handleClick = () => {
    startTransition(() => {
      setCount(c => c + 1)
    })
  }
  
  return (
    <div>
      <button onClick={handleClick}>
        {isPending ? 'Loading...' : `Count: ${count}`}
      </button>
    </div>
  )
}
```

### 3. useDeferredValue

```jsx
import { useDeferredValue, useState } from 'react'

function SearchResults({ query }) {
  const deferredQuery = useDeferredValue(query)
  
  return <ExpensiveList query={deferredQuery} />
}
```

### 4. Suspense 改进

```jsx
function App() {
  return (
    <Suspense fallback={<Loading />}>
      <ProfilePage />
    </Suspense>
  )
}

function ProfilePage() {
  return (
    <Suspense fallback={<h2>Loading posts...</h2>}>
      <ProfileTimeline />
    </Suspense>
  )
}
```

## 自动批处理

```jsx
// React 18 会自动批处理这些更新
function handleClick() {
  setCount(c => c + 1)
  setFlag(f => !f)
  // React 只会重新渲染一次
}
```

## 性能优化

### 1. 时间切片

React 18 可以将长时间运行的渲染工作分解为小块，避免阻塞主线程。

### 2. 优先级调度

不同的更新有不同的优先级：
- 用户输入：高优先级
- 数据获取：中优先级
- 动画：低优先级

## 最佳实践

1. 使用 `startTransition` 包装非紧急更新
2. 合理使用 `useDeferredValue` 延迟昂贵计算
3. 利用 Suspense 改善用户体验

## 总结

React 18 的并发特性为构建更流畅的用户界面提供了强大工具，通过合理使用这些特性可以显著提升应用性能。''',
        'category': '前端开发'
    },
    {
        'title': 'TypeScript 4.9 新特性解析',
        'summary': '详细介绍TypeScript 4.9版本的新特性，包括satisfies操作符、auto-accessor等功能。',
        'content': '''# TypeScript 4.9 新特性解析

## 概述

TypeScript 4.9 带来了许多实用的新特性，提升了开发体验和类型安全性。

## 主要新特性

### 1. satisfies 操作符

```typescript
type Colors = "red" | "green" | "blue"
type RGB = [red: number, green: number, blue: number]

const palette = {
  red: [255, 0, 0],
  green: "#00ff00",
  blue: [0, 0, 255]
} satisfies Record<Colors, string | RGB>

// 现在可以安全地访问属性
const redComponent = palette.red.at(0) // number | undefined
const greenNormalized = palette.green.toUpperCase() // string
```

### 2. Auto-Accessor 字段

```typescript
class Person {
  accessor name: string
  
  constructor(name: string) {
    this.name = name
  }
}

// 等价于：
class Person {
  #__name: string
  
  get name() {
    return this.#__name
  }
  
  set name(value: string) {
    this.#__name = value
  }
}
```

### 3. 改进的 in 操作符缩窄

```typescript
interface A {
  a: number
}

interface B {
  b: string
}

function foo(x: A | B) {
  if ("a" in x) {
    // x 现在被正确缩窄为 A 类型
    return x.a.toFixed()
  }
  
  // x 现在被正确缩窄为 B 类型
  return x.b.toUpperCase()
}
```

### 4. NaN 相等性检查

```typescript
function validate(someValue: number) {
  return someValue !== NaN
  //     ~~~~~~~~~~~~~~~~
  // 错误：此条件将始终返回 'true'，因为 'NaN' 与任何值都不相等，包括它自己
}

// 正确的方式
function validate(someValue: number) {
  return !Number.isNaN(someValue)
}
```

## 性能改进

### 1. 文件监听优化

TypeScript 4.9 改进了文件监听机制，减少了不必要的重新编译。

### 2. 更快的类型检查

```typescript
// 改进了大型联合类型的性能
type ManyStrings = 
  | "option1" | "option2" | "option3" 
  | "option4" | "option5" | "option6"
  // ... 更多选项
```

## 编辑器改进

### 1. 更好的自动导入

```typescript
// 现在可以更智能地建议导入
import { someFunction } from './utils'
//       ~~~~~~~~~~~~
// 自动建议并导入
```

### 2. 改进的重构功能

- 更准确的重命名
- 更好的提取函数功能
- 改进的组织导入

## 配置改进

### 1. 新的编译器选项

```json
{
  "compilerOptions": {
    "verbatimModuleSyntax": true,
    "allowUnreachableCode": false
  }
}
```

## 最佳实践

1. 使用 `satisfies` 操作符进行类型约束
2. 利用 auto-accessor 简化类定义
3. 注意 NaN 比较的陷阱
4. 合理配置新的编译器选项

## 总结

TypeScript 4.9 通过 satisfies 操作符、auto-accessor 等新特性，进一步提升了类型安全性和开发效率。''',
        'category': '前端开发'
    },
    {
        'title': 'Webpack 5 模块联邦实战',
        'summary': '深入讲解Webpack 5的模块联邦特性，实现微前端架构的最佳实践。',
        'content': '''# Webpack 5 模块联邦实战

## 模块联邦概述

模块联邦（Module Federation）是 Webpack 5 的革命性特性，允许多个独立的构建共享模块。

## 基础配置

### 1. 主应用配置

```javascript
// webpack.config.js (主应用)
const ModuleFederationPlugin = require('@module-federation/webpack')

module.exports = {
  mode: 'development',
  devServer: {
    port: 3000,
  },
  plugins: [
    new ModuleFederationPlugin({
      name: 'host',
      remotes: {
        mfApp: 'mfApp@http://localhost:3001/remoteEntry.js',
      },
    }),
  ],
}
```

### 2. 远程应用配置

```javascript
// webpack.config.js (远程应用)
const ModuleFederationPlugin = require('@module-federation/webpack')

module.exports = {
  mode: 'development',
  devServer: {
    port: 3001,
  },
  plugins: [
    new ModuleFederationPlugin({
      name: 'mfApp',
      filename: 'remoteEntry.js',
      exposes: {
        './Button': './src/Button',
        './Header': './src/Header',
      },
      shared: {
        react: { singleton: true },
        'react-dom': { singleton: true },
      },
    }),
  ],
}
```

## 动态导入

### 1. 异步加载远程模块

```javascript
// 主应用中使用远程组件
import React, { Suspense } from 'react'

const RemoteButton = React.lazy(() => import('mfApp/Button'))

function App() {
  return (
    <div>
      <h1>主应用</h1>
      <Suspense fallback={<div>Loading...</div>}>
        <RemoteButton />
      </Suspense>
    </div>
  )
}
```

### 2. 错误边界处理

```javascript
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true }
  }

  componentDidCatch(error, errorInfo) {
    console.log('模块联邦加载错误:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return <h1>远程模块加载失败</h1>
    }

    return this.props.children
  }
}
```

## 共享依赖

### 1. 版本控制

```javascript
const ModuleFederationPlugin = require('@module-federation/webpack')

module.exports = {
  plugins: [
    new ModuleFederationPlugin({
      shared: {
        react: {
          singleton: true,
          requiredVersion: '^17.0.0',
        },
        lodash: {
          singleton: false,
          version: '4.17.21',
        },
      },
    }),
  ],
}
```

### 2. 动态共享

```javascript
// 运行时共享模块
const sharedModules = {
  react: () => import('react'),
  'react-dom': () => import('react-dom'),
}

// 在运行时注册共享模块
Object.entries(sharedModules).forEach(([name, factory]) => {
  __webpack_share_scopes__.default[name] = {
    '17.0.0': {
      get: factory,
      loaded: 1,
    },
  }
})
```

## 实际应用场景

### 1. 微前端架构

```javascript
// 主壳应用
const routes = [
  {
    path: '/dashboard',
    component: React.lazy(() => import('dashboard/App')),
  },
  {
    path: '/profile',
    component: React.lazy(() => import('profile/App')),
  },
]
```

### 2. 组件库共享

```javascript
// 设计系统应用
const ModuleFederationPlugin = require('@module-federation/webpack')

module.exports = {
  plugins: [
    new ModuleFederationPlugin({
      name: 'designSystem',
      filename: 'remoteEntry.js',
      exposes: {
        './Button': './src/components/Button',
        './Input': './src/components/Input',
        './Modal': './src/components/Modal',
      },
    }),
  ],
}
```

## 最佳实践

### 1. 版本管理策略

- 使用语义化版本控制
- 设置合理的版本兼容范围
- 建立版本升级流程

### 2. 性能优化

```javascript
// 预加载关键模块
const preloadModules = [
  'mfApp/Button',
  'mfApp/Header',
]

preloadModules.forEach(module => {
  import(module)
})
```

### 3. 监控和调试

```javascript
// 模块加载监控
window.__FEDERATION_DEBUG__ = true

// 自定义加载器
const customLoader = {
  get: (scope, module) => {
    console.log(`Loading ${module} from ${scope}`)
    return __webpack_require__.federation.runtime.loadRemote(`${scope}/${module}`)
  }
}
```

## 总结

模块联邦为微前端架构提供了强大的技术支持，通过合理的配置和最佳实践，可以构建高效、可维护的分布式前端应用。''',
        'category': '前端开发'
    }
]

def create_articles():
    # 获取现有分类和用户
    categories = list(Category.objects.all())
    users = list(User.objects.all())
    
    if not categories or not users:
        print("请先创建分类和用户")
        return
    
    # 创建文章
    created_count = 0
    for article_data in tech_articles:
        # 检查文章是否已存在
        if Article.objects.filter(title=article_data['title']).exists():
            print(f"文章已存在: {article_data['title']}")
            continue
        
        # 查找对应分类
        category = None
        for cat in categories:
            if cat.name == article_data['category']:
                category = cat
                break
        
        if not category:
            category = random.choice(categories)
        
        # 随机选择作者和发布时间
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
    
    print(f"\n总共创建了 {created_count} 篇前端开发文章")

if __name__ == '__main__':
    create_articles()