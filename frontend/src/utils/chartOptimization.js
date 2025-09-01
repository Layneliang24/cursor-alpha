// 图表性能优化工具

// 数据抽样算法
export class DataSampler {
  constructor(options = {}) {
    this.maxPoints = options.maxPoints || 1000
    this.samplingMethod = options.samplingMethod || 'lttb' // largest-triangle-three-buckets
    this.threshold = options.threshold || 0.1
  }

  // 最大三角形三桶抽样算法 (LTTB)
  lttbSample(data, targetCount) {
    if (data.length <= targetCount) {
      return data
    }

    const sampled = []
    const bucketSize = (data.length - 2) / (targetCount - 2)
    
    // 添加第一个点
    sampled.push(data[0])
    
    for (let i = 1; i < targetCount - 1; i++) {
      const bucketStart = Math.floor(i * bucketSize) + 1
      const bucketEnd = Math.floor((i + 1) * bucketSize) + 1
      
      let maxArea = -1
      let selectedPoint = data[bucketStart]
      
      for (let j = bucketStart; j < bucketEnd; j++) {
        const area = this.calculateTriangleArea(
          data[bucketStart - 1],
          data[j],
          data[Math.min(bucketEnd, data.length - 1)]
        )
        
        if (area > maxArea) {
          maxArea = area
          selectedPoint = data[j]
        }
      }
      
      sampled.push(selectedPoint)
    }
    
    // 添加最后一个点
    sampled.push(data[data.length - 1])
    
    return sampled
  }

  // 计算三角形面积
  calculateTriangleArea(p1, p2, p3) {
    // 确保所有点都有x和y属性
    if (!p1 || !p2 || !p3 || typeof p1.x === 'undefined' || typeof p1.y === 'undefined' ||
        typeof p2.x === 'undefined' || typeof p2.y === 'undefined' ||
        typeof p3.x === 'undefined' || typeof p3.y === 'undefined') {
      return 0
    }
    
    return Math.abs(
      (p2.x - p1.x) * (p3.y - p1.y) - (p3.x - p1.x) * (p2.y - p1.y)
    ) / 2
  }

  // 随机抽样
  randomSample(data, targetCount) {
    if (data.length <= targetCount) {
      return data
    }

    const sampled = []
    const step = data.length / targetCount
    
    for (let i = 0; i < targetCount; i++) {
      const index = Math.floor(i * step)
      sampled.push(data[index])
    }
    
    return sampled
  }

  // 均匀抽样
  uniformSample(data, targetCount) {
    if (data.length <= targetCount) {
      return data
    }

    const sampled = []
    const step = (data.length - 1) / (targetCount - 1)
    
    for (let i = 0; i < targetCount; i++) {
      const index = Math.floor(i * step)
      sampled.push(data[index])
    }
    
    return sampled
  }

  // 智能抽样
  smartSample(data, targetCount) {
    if (data.length <= targetCount) {
      return data
    }

    // 根据数据特征选择抽样方法
    const variance = this.calculateVariance(data)
    const trend = this.calculateTrend(data)
    
    if (variance > this.threshold) {
      // 高方差数据使用LTTB
      return this.lttbSample(data, targetCount)
    } else if (Math.abs(trend) > this.threshold) {
      // 有明显趋势的数据使用均匀抽样
      return this.uniformSample(data, targetCount)
    } else {
      // 其他情况使用随机抽样
      return this.randomSample(data, targetCount)
    }
  }

  // 计算数据方差
  calculateVariance(data) {
    if (data.length < 2) return 0
    
    const values = data.map(d => d.y || d.value || d)
    const mean = values.reduce((a, b) => a + b, 0) / values.length
    const variance = values.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / values.length
    
    return variance
  }

  // 计算数据趋势
  calculateTrend(data) {
    if (data.length < 2) return 0
    
    const values = data.map(d => d.y || d.value || d)
    const n = values.length
    const sumX = (n * (n - 1)) / 2
    const sumY = values.reduce((a, b) => a + b, 0)
    const sumXY = values.reduce((a, b, i) => a + (i * b), 0)
    const sumX2 = values.reduce((a, b, i) => a + (i * i), 0)
    
    const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX)
    return slope
  }

  // 抽样数据
  sample(data, targetCount = this.maxPoints) {
    switch (this.samplingMethod) {
      case 'lttb':
        return this.lttbSample(data, targetCount)
      case 'random':
        return this.randomSample(data, targetCount)
      case 'uniform':
        return this.uniformSample(data, targetCount)
      case 'smart':
        return this.smartSample(data, targetCount)
      default:
        return this.lttbSample(data, targetCount)
    }
  }
}

// 图表虚拟化渲染
export class ChartVirtualization {
  constructor(options = {}) {
    this.viewportHeight = options.viewportHeight || 400
    this.itemHeight = options.itemHeight || 20
    this.bufferSize = options.bufferSize || 5
    this.visibleItems = Math.ceil(this.viewportHeight / this.itemHeight)
  }

  // 计算可见范围
  calculateVisibleRange(scrollTop, dataLength) {
    const startIndex = Math.max(0, Math.floor(scrollTop / this.itemHeight) - this.bufferSize)
    const endIndex = Math.min(
      dataLength,
      Math.ceil((scrollTop + this.viewportHeight) / this.itemHeight) + this.bufferSize
    )
    
    return { startIndex, endIndex }
  }

  // 获取可见数据
  getVisibleData(data, scrollTop) {
    const { startIndex, endIndex } = this.calculateVisibleRange(scrollTop, data.length)
    return data.slice(startIndex, endIndex)
  }

  // 计算总高度
  getTotalHeight(dataLength) {
    return dataLength * this.itemHeight
  }

  // 计算偏移量
  getOffsetY(index) {
    return index * this.itemHeight
  }
}

// 图表更新优化
export class ChartUpdateOptimizer {
  constructor(options = {}) {
    this.debounceDelay = options.debounceDelay || 300
    this.throttleDelay = options.throttleDelay || 100
    this.updateQueue = []
    this.isUpdating = false
    this.lastUpdateTime = 0
  }

  // 防抖更新
  debounceUpdate(updateFunction) {
    let timeoutId
    
    return (...args) => {
      clearTimeout(timeoutId)
      timeoutId = setTimeout(() => {
        updateFunction(...args)
      }, this.debounceDelay)
    }
  }

  // 节流更新
  throttleUpdate(updateFunction) {
    return (...args) => {
      const now = Date.now()
      
      if (now - this.lastUpdateTime >= this.throttleDelay) {
        updateFunction(...args)
        this.lastUpdateTime = now
      }
    }
  }

  // 批量更新
  batchUpdate(updates) {
    this.updateQueue.push(...updates)
    
    if (!this.isUpdating) {
      this.processUpdateQueue()
    }
  }

  // 处理更新队列
  async processUpdateQueue() {
    if (this.isUpdating || this.updateQueue.length === 0) {
      return
    }

    this.isUpdating = true

    try {
      while (this.updateQueue.length > 0) {
        const batch = this.updateQueue.splice(0, 10) // 每次处理10个更新
        
        // 批量执行更新
        await Promise.all(batch.map(update => update()))
        
        // 让出控制权
        await new Promise(resolve => setTimeout(resolve, 0))
      }
    } finally {
      this.isUpdating = false
    }
  }

  // 智能更新策略
  smartUpdate(updateFunction, data, options = {}) {
    const { strategy = 'auto', threshold = 1000 } = options
    
    if (strategy === 'auto') {
      if (data.length > threshold) {
        return this.throttleUpdate(updateFunction)
      } else {
        return this.debounceUpdate(updateFunction)
      }
    } else if (strategy === 'debounce') {
      return this.debounceUpdate(updateFunction)
    } else if (strategy === 'throttle') {
      return this.throttleUpdate(updateFunction)
    }
    
    return updateFunction
  }
}

// 图表懒加载
export class ChartLazyLoader {
  constructor(options = {}) {
    this.intersectionThreshold = options.intersectionThreshold || 0.1
    this.loadingDelay = options.loadingDelay || 100
    this.observers = new Map()
  }

  // 懒加载图表
  lazyLoadChart(chartElement, loadFunction) {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            // 延迟加载以避免阻塞
            setTimeout(() => {
              loadFunction()
              observer.unobserve(entry.target)
            }, this.loadingDelay)
          }
        })
      },
      {
        threshold: this.intersectionThreshold
      }
    )
    
    observer.observe(chartElement)
    this.observers.set(chartElement, observer)
    
    return observer
  }

  // 停止观察
  stopObserving(chartElement) {
    const observer = this.observers.get(chartElement)
    if (observer) {
      observer.disconnect()
      this.observers.delete(chartElement)
    }
  }

  // 清理所有观察器
  cleanup() {
    this.observers.forEach(observer => observer.disconnect())
    this.observers.clear()
  }
}

// 图表性能监控
export class ChartPerformanceMonitor {
  constructor() {
    this.metrics = new Map()
  }

  // 开始监控图表渲染
  startMonitoring(chartId) {
    const startTime = performance.now()
    
    return {
      finish: () => {
        const renderTime = performance.now() - startTime
        this.recordRenderTime(chartId, renderTime)
      },
      error: (error) => {
        const renderTime = performance.now() - startTime
        this.recordRenderError(chartId, renderTime, error)
      }
    }
  }

  // 记录渲染时间
  recordRenderTime(chartId, renderTime) {
    if (!this.metrics.has(chartId)) {
      this.metrics.set(chartId, {
        renderTimes: [],
        errors: [],
        averageRenderTime: 0
      })
    }

    const metric = this.metrics.get(chartId)
    metric.renderTimes.push(renderTime)
    metric.averageRenderTime = metric.renderTimes.reduce((a, b) => a + b, 0) / metric.renderTimes.length

    console.log(`图表渲染完成: ${chartId}, 耗时: ${renderTime.toFixed(2)}ms`)
  }

  // 记录渲染错误
  recordRenderError(chartId, renderTime, error) {
    if (!this.metrics.has(chartId)) {
      this.metrics.set(chartId, {
        renderTimes: [],
        errors: [],
        averageRenderTime: 0
      })
    }

    const metric = this.metrics.get(chartId)
    metric.errors.push({ renderTime, error, timestamp: Date.now() })

    console.error(`图表渲染失败: ${chartId}, 耗时: ${renderTime.toFixed(2)}ms`, error)
  }

  // 获取性能报告
  getPerformanceReport() {
    const report = {
      totalCharts: this.metrics.size,
      averageRenderTime: 0,
      slowestChart: null,
      fastestChart: null,
      errorRate: 0
    }

    if (this.metrics.size > 0) {
      const allRenderTimes = []
      let totalErrors = 0
      let totalRenders = 0

      for (const [id, metric] of this.metrics.entries()) {
        allRenderTimes.push(...metric.renderTimes)
        totalErrors += metric.errors.length
        totalRenders += metric.renderTimes.length + metric.errors.length
      }

      report.averageRenderTime = allRenderTimes.reduce((a, b) => a + b, 0) / allRenderTimes.length
      report.errorRate = totalErrors / totalRenders

      const sortedCharts = Array.from(this.metrics.entries())
        .sort((a, b) => b[1].averageRenderTime - a[1].averageRenderTime)

      report.slowestChart = sortedCharts[0]
      report.fastestChart = sortedCharts[sortedCharts.length - 1]
    }

    return report
  }
}

// 导出图表优化工具
export const chartOptimizationTools = {
  DataSampler,
  ChartVirtualization,
  ChartUpdateOptimizer,
  ChartLazyLoader,
  ChartPerformanceMonitor
}
