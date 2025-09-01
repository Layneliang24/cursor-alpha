import { createRouter, createWebHistory } from 'vue-router'

// 预加载配置
const preloadConfig = {
  // 高频访问页面预加载
  highPriority: [
    '/english/news-dashboard',
    '/english/words',
    '/english/expressions'
  ],
  // 中频访问页面预加载
  mediumPriority: [
    '/english/learning-analytics',
    '/english/practice',
    '/english/ai-config'
  ],
  // 低频访问页面延迟加载
  lowPriority: [
    '/english/pronunciation',
    '/english/api-integration',
    '/admin/categories'
  ]
}

// 智能预加载函数
export function smartPreload(routePath) {
  const priority = getRoutePriority(routePath)
  
  switch (priority) {
    case 'high':
      // 立即预加载
      return preloadRoute(routePath)
    case 'medium':
      // 延迟预加载（空闲时）
      return preloadRouteWhenIdle(routePath)
    case 'low':
      // 用户交互时预加载
      return preloadRouteOnInteraction(routePath)
    default:
      return Promise.resolve()
  }
}

// 获取路由优先级
function getRoutePriority(routePath) {
  if (preloadConfig.highPriority.includes(routePath)) {
    return 'high'
  }
  if (preloadConfig.mediumPriority.includes(routePath)) {
    return 'medium'
  }
  if (preloadConfig.lowPriority.includes(routePath)) {
    return 'low'
  }
  return 'low'
}

// 立即预加载
function preloadRoute(routePath) {
  return new Promise((resolve) => {
    // 这里可以添加实际的预加载逻辑
    console.log(`预加载路由: ${routePath}`)
    resolve()
  })
}

// 空闲时预加载
function preloadRouteWhenIdle(routePath) {
  return new Promise((resolve) => {
    if ('requestIdleCallback' in window) {
      requestIdleCallback(() => {
        console.log(`空闲时预加载路由: ${routePath}`)
        resolve()
      })
    } else {
      // 降级到setTimeout
      setTimeout(() => {
        console.log(`延迟预加载路由: ${routePath}`)
        resolve()
      }, 1000)
    }
  })
}

// 用户交互时预加载
function preloadRouteOnInteraction(routePath) {
  return new Promise((resolve) => {
    const preloadOnInteraction = () => {
      console.log(`交互时预加载路由: ${routePath}`)
      document.removeEventListener('mousemove', preloadOnInteraction)
      document.removeEventListener('scroll', preloadOnInteraction)
      resolve()
    }
    
    document.addEventListener('mousemove', preloadOnInteraction, { once: true })
    document.addEventListener('scroll', preloadOnInteraction, { once: true })
  })
}

// 路由性能监控
export class RoutePerformanceMonitor {
  constructor() {
    this.metrics = new Map()
    this.observer = null
  }

  // 开始监控路由性能
  startMonitoring() {
    if ('PerformanceObserver' in window) {
      this.observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (entry.entryType === 'navigation') {
            this.recordNavigationMetrics(entry)
          }
        }
      })
      
      this.observer.observe({ entryTypes: ['navigation'] })
    }
  }

  // 记录导航性能指标
  recordNavigationMetrics(entry) {
    const metrics = {
      timestamp: Date.now(),
      url: entry.name,
      loadTime: entry.loadEventEnd - entry.loadEventStart,
      domContentLoaded: entry.domContentLoadedEventEnd - entry.domContentLoadedEventStart,
      firstPaint: entry.firstPaint,
      firstContentfulPaint: entry.firstContentfulPaint,
      largestContentfulPaint: entry.largestContentfulPaint
    }
    
    this.metrics.set(entry.name, metrics)
    console.log('路由性能指标:', metrics)
  }

  // 获取性能报告
  getPerformanceReport() {
    const report = {
      totalRoutes: this.metrics.size,
      averageLoadTime: 0,
      slowestRoute: null,
      fastestRoute: null
    }
    
    if (this.metrics.size > 0) {
      const loadTimes = Array.from(this.metrics.values()).map(m => m.loadTime)
      report.averageLoadTime = loadTimes.reduce((a, b) => a + b, 0) / loadTimes.length
      
      const sortedRoutes = Array.from(this.metrics.entries())
        .sort((a, b) => b[1].loadTime - a[1].loadTime)
      
      report.slowestRoute = sortedRoutes[0]
      report.fastestRoute = sortedRoutes[sortedRoutes.length - 1]
    }
    
    return report
  }

  // 停止监控
  stopMonitoring() {
    if (this.observer) {
      this.observer.disconnect()
      this.observer = null
    }
  }
}

// 路由缓存管理
export class RouteCacheManager {
  constructor() {
    this.cache = new Map()
    this.maxCacheSize = 10
  }

  // 缓存路由组件
  cacheRoute(routePath, component) {
    if (this.cache.size >= this.maxCacheSize) {
      // 移除最旧的缓存
      const firstKey = this.cache.keys().next().value
      this.cache.delete(firstKey)
    }
    
    this.cache.set(routePath, {
      component,
      timestamp: Date.now(),
      accessCount: 0
    })
  }

  // 获取缓存的组件
  getCachedRoute(routePath) {
    const cached = this.cache.get(routePath)
    if (cached) {
      cached.accessCount++
      cached.lastAccess = Date.now()
      return cached.component
    }
    return null
  }

  // 清理过期缓存
  cleanupCache(maxAge = 30 * 60 * 1000) { // 30分钟
    const now = Date.now()
    for (const [key, value] of this.cache.entries()) {
      if (now - value.timestamp > maxAge) {
        this.cache.delete(key)
      }
    }
  }

  // 获取缓存统计
  getCacheStats() {
    return {
      size: this.cache.size,
      maxSize: this.maxCacheSize,
      hitRate: this.calculateHitRate()
    }
  }

  // 计算缓存命中率
  calculateHitRate() {
    // 这里可以实现更复杂的命中率计算逻辑
    return this.cache.size / this.maxCacheSize
  }
}

// 导出性能优化工具
export const routePerformanceTools = {
  smartPreload,
  RoutePerformanceMonitor,
  RouteCacheManager
}
