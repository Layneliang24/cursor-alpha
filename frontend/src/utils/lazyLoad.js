import { defineAsyncComponent } from 'vue'

// 懒加载配置
const lazyLoadConfig = {
  // 组件加载超时时间
  timeout: 10000,
  // 重试次数
  retryCount: 3,
  // 重试延迟
  retryDelay: 1000,
  // 加载状态组件
  loadingComponent: null,
  // 错误状态组件
  errorComponent: null
}

// 创建懒加载组件
export function createLazyComponent(loader, options = {}) {
  const config = { ...lazyLoadConfig, ...options }
  
  return defineAsyncComponent({
    loader: async () => {
      let lastError
      
      for (let i = 0; i <= config.retryCount; i++) {
        try {
          const component = await loader()
          return component
        } catch (error) {
          lastError = error
          console.warn(`组件加载失败 (尝试 ${i + 1}/${config.retryCount + 1}):`, error)
          
          if (i < config.retryCount) {
            await new Promise(resolve => setTimeout(resolve, config.retryDelay))
          }
        }
      }
      
      throw lastError
    },
    loadingComponent: config.loadingComponent,
    errorComponent: config.errorComponent,
    timeout: config.timeout,
    onError: (error, retry, fail, attempts) => {
      console.error(`组件加载失败 (${attempts} 次尝试):`, error)
      if (attempts <= config.retryCount) {
        retry()
      } else {
        fail()
      }
    }
  })
}

// 预加载组件
export function preloadComponent(loader) {
  return loader().catch(error => {
    console.warn('预加载组件失败:', error)
  })
}

// 批量预加载组件
export function preloadComponents(componentLoaders) {
  const promises = componentLoaders.map(loader => preloadComponent(loader))
  return Promise.allSettled(promises)
}

// 智能预加载策略
export class SmartPreloader {
  constructor() {
    this.preloadedComponents = new Set()
    this.preloadQueue = []
    this.isProcessing = false
  }

  // 添加组件到预加载队列
  addToPreloadQueue(componentName, loader, priority = 'normal') {
    this.preloadQueue.push({
      name: componentName,
      loader,
      priority,
      timestamp: Date.now()
    })
    
    // 按优先级排序
    this.preloadQueue.sort((a, b) => {
      const priorityOrder = { high: 3, normal: 2, low: 1 }
      return priorityOrder[b.priority] - priorityOrder[a.priority]
    })
  }

  // 处理预加载队列
  async processPreloadQueue() {
    if (this.isProcessing || this.preloadQueue.length === 0) {
      return
    }

    this.isProcessing = true

    try {
      while (this.preloadQueue.length > 0) {
        const item = this.preloadQueue.shift()
        
        if (!this.preloadedComponents.has(item.name)) {
          try {
            await preloadComponent(item.loader)
            this.preloadedComponents.add(item.name)
            console.log(`预加载组件成功: ${item.name}`)
          } catch (error) {
            console.warn(`预加载组件失败: ${item.name}`, error)
          }
        }

        // 检查浏览器是否空闲
        if ('requestIdleCallback' in window) {
          await new Promise(resolve => {
            requestIdleCallback(resolve, { timeout: 1000 })
          })
        } else {
          // 降级到短暂延迟
          await new Promise(resolve => setTimeout(resolve, 100))
        }
      }
    } finally {
      this.isProcessing = false
    }
  }

  // 开始智能预加载
  startSmartPreloading() {
    // 监听用户交互
    const startPreloading = () => {
      this.processPreloadQueue()
      document.removeEventListener('mousemove', startPreloading)
      document.removeEventListener('scroll', startPreloading)
    }

    document.addEventListener('mousemove', startPreloading, { once: true })
    document.addEventListener('scroll', startPreloading, { once: true })

    // 延迟启动预加载
    setTimeout(() => {
      this.processPreloadQueue()
    }, 2000)
  }

  // 获取预加载统计
  getPreloadStats() {
    return {
      preloadedCount: this.preloadedComponents.size,
      queueLength: this.preloadQueue.length,
      isProcessing: this.isProcessing
    }
  }
}

// 组件加载性能监控
export class ComponentLoadMonitor {
  constructor() {
    this.metrics = new Map()
  }

  // 开始监控组件加载
  startMonitoring(componentName) {
    const startTime = performance.now()
    
    return {
      finish: () => {
        const loadTime = performance.now() - startTime
        this.recordLoadTime(componentName, loadTime)
      },
      error: (error) => {
        const loadTime = performance.now() - startTime
        this.recordLoadError(componentName, loadTime, error)
      }
    }
  }

  // 记录加载时间
  recordLoadTime(componentName, loadTime) {
    if (!this.metrics.has(componentName)) {
      this.metrics.set(componentName, {
        loadTimes: [],
        errors: [],
        averageLoadTime: 0
      })
    }

    const metric = this.metrics.get(componentName)
    metric.loadTimes.push(loadTime)
    metric.averageLoadTime = metric.loadTimes.reduce((a, b) => a + b, 0) / metric.loadTimes.length

    console.log(`组件加载完成: ${componentName}, 耗时: ${loadTime.toFixed(2)}ms`)
  }

  // 记录加载错误
  recordLoadError(componentName, loadTime, error) {
    if (!this.metrics.has(componentName)) {
      this.metrics.set(componentName, {
        loadTimes: [],
        errors: [],
        averageLoadTime: 0
      })
    }

    const metric = this.metrics.get(componentName)
    metric.errors.push({ loadTime, error, timestamp: Date.now() })

    console.error(`组件加载失败: ${componentName}, 耗时: ${loadTime.toFixed(2)}ms`, error)
  }

  // 获取性能报告
  getPerformanceReport() {
    const report = {
      totalComponents: this.metrics.size,
      averageLoadTime: 0,
      slowestComponent: null,
      fastestComponent: null,
      errorRate: 0
    }

    if (this.metrics.size > 0) {
      const allLoadTimes = []
      let totalErrors = 0
      let totalLoads = 0

      for (const [name, metric] of this.metrics.entries()) {
        allLoadTimes.push(...metric.loadTimes)
        totalErrors += metric.errors.length
        totalLoads += metric.loadTimes.length + metric.errors.length
      }

      report.averageLoadTime = allLoadTimes.reduce((a, b) => a + b, 0) / allLoadTimes.length
      report.errorRate = totalErrors / totalLoads

      const sortedComponents = Array.from(this.metrics.entries())
        .sort((a, b) => b[1].averageLoadTime - a[1].averageLoadTime)

      report.slowestComponent = sortedComponents[0]
      report.fastestComponent = sortedComponents[sortedComponents.length - 1]
    }

    return report
  }
}

// 导出懒加载工具
export const lazyLoadTools = {
  createLazyComponent,
  preloadComponent,
  preloadComponents,
  SmartPreloader,
  ComponentLoadMonitor
}
