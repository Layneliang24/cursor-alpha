import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { DataSampler, ChartVirtualization, ChartUpdateOptimizer } from '@/utils/chartOptimization'
import { SmartPreloader, ComponentLoadMonitor } from '@/utils/lazyLoad'
import { smartPreload, RoutePerformanceMonitor } from '@/router/performance'

describe('性能优化工具测试', () => {
  describe('DataSampler', () => {
    let sampler

    beforeEach(() => {
      sampler = new DataSampler({ maxPoints: 100 })
    })

    it('应该正确进行LTTB抽样', () => {
      const data = Array.from({ length: 1000 }, (_, i) => ({ x: i, y: Math.sin(i * 0.1) }))
      const sampled = sampler.lttbSample(data, 100)
      
      expect(sampled.length).toBe(100)
      expect(sampled[0]).toEqual(data[0])
      expect(sampled[sampled.length - 1]).toEqual(data[data.length - 1])
    })

    it('应该正确进行随机抽样', () => {
      const data = Array.from({ length: 1000 }, (_, i) => ({ x: i, y: i }))
      const sampled = sampler.randomSample(data, 100)
      
      expect(sampled.length).toBe(100)
    })

    it('应该正确进行均匀抽样', () => {
      const data = Array.from({ length: 1000 }, (_, i) => ({ x: i, y: i }))
      const sampled = sampler.uniformSample(data, 100)
      
      expect(sampled.length).toBe(100)
      expect(sampled[0]).toEqual(data[0])
      expect(sampled[sampled.length - 1]).toEqual(data[data.length - 1])
    })

    it('应该正确计算数据方差', () => {
      const data = [{ y: 1 }, { y: 2 }, { y: 3 }, { y: 4 }, { y: 5 }]
      const variance = sampler.calculateVariance(data)
      
      expect(variance).toBe(2)
    })

    it('应该正确计算数据趋势', () => {
      const data = [{ y: 1 }, { y: 2 }, { y: 3 }, { y: 4 }, { y: 5 }]
      const trend = sampler.calculateTrend(data)
      
      expect(trend).toBe(1)
    })

    it('应该根据数据特征选择抽样方法', () => {
      const highVarianceData = [{ y: 1 }, { y: 10 }, { y: 2 }, { y: 15 }, { y: 3 }]
      const trendData = [{ y: 1 }, { y: 2 }, { y: 3 }, { y: 4 }, { y: 5 }]
      const stableData = [{ y: 1 }, { y: 1.1 }, { y: 0.9 }, { y: 1.2 }, { y: 0.8 }]
      
      const highVarianceSampled = sampler.smartSample(highVarianceData, 3)
      const trendSampled = sampler.smartSample(trendData, 3)
      const stableSampled = sampler.smartSample(stableData, 3)
      
      expect(highVarianceSampled.length).toBe(3)
      expect(trendSampled.length).toBe(3)
      expect(stableSampled.length).toBe(3)
    })
  })

  describe('ChartVirtualization', () => {
    let virtualization

    beforeEach(() => {
      virtualization = new ChartVirtualization({
        viewportHeight: 400,
        itemHeight: 20,
        bufferSize: 5
      })
    })

    it('应该正确计算可见范围', () => {
      const { startIndex, endIndex } = virtualization.calculateVisibleRange(100, 1000)
      
      expect(startIndex).toBeGreaterThanOrEqual(0)
      expect(endIndex).toBeLessThanOrEqual(1000)
      expect(endIndex).toBeGreaterThan(startIndex)
    })

    it('应该正确获取可见数据', () => {
      const data = Array.from({ length: 1000 }, (_, i) => ({ id: i, value: i }))
      const visibleData = virtualization.getVisibleData(data, 100)
      
      expect(visibleData.length).toBeLessThanOrEqual(data.length)
      expect(visibleData.length).toBeGreaterThan(0)
    })

    it('应该正确计算总高度', () => {
      const totalHeight = virtualization.getTotalHeight(1000)
      expect(totalHeight).toBe(20000)
    })

    it('应该正确计算偏移量', () => {
      const offsetY = virtualization.getOffsetY(10)
      expect(offsetY).toBe(200)
    })
  })

  describe('ChartUpdateOptimizer', () => {
    let optimizer

    beforeEach(() => {
      optimizer = new ChartUpdateOptimizer({
        debounceDelay: 100,
        throttleDelay: 50
      })
    })

    it('应该正确进行防抖更新', async () => {
      const updateFn = vi.fn()
      const debouncedUpdate = optimizer.debounceUpdate(updateFn)
      
      debouncedUpdate()
      debouncedUpdate()
      debouncedUpdate()
      
      expect(updateFn).not.toHaveBeenCalled()
      
      await new Promise(resolve => setTimeout(resolve, 150))
      expect(updateFn).toHaveBeenCalledTimes(1)
    })

    it('应该正确进行节流更新', async () => {
      const updateFn = vi.fn()
      const throttledUpdate = optimizer.throttleUpdate(updateFn)
      
      throttledUpdate()
      throttledUpdate()
      throttledUpdate()
      
      expect(updateFn).toHaveBeenCalledTimes(1)
      
      await new Promise(resolve => setTimeout(resolve, 60))
      throttledUpdate()
      expect(updateFn).toHaveBeenCalledTimes(2)
    })

    it('应该正确进行批量更新', async () => {
      const updates = [
        vi.fn(),
        vi.fn(),
        vi.fn()
      ]
      
      optimizer.batchUpdate(updates)
      
      await new Promise(resolve => setTimeout(resolve, 100))
      
      updates.forEach(update => {
        expect(update).toHaveBeenCalled()
      })
    })

    it('应该根据数据大小选择更新策略', () => {
      const updateFn = vi.fn()
      
      const smallDataUpdate = optimizer.smartUpdate(updateFn, Array.from({ length: 100 }))
      const largeDataUpdate = optimizer.smartUpdate(updateFn, Array.from({ length: 2000 }))
      
      expect(typeof smallDataUpdate).toBe('function')
      expect(typeof largeDataUpdate).toBe('function')
    })
  })

  describe('SmartPreloader', () => {
    let preloader

    beforeEach(() => {
      preloader = new SmartPreloader()
    })

    it('应该正确添加组件到预加载队列', () => {
      const loader = vi.fn()
      preloader.addToPreloadQueue('TestComponent', loader, 'high')
      
      expect(preloader.preloadQueue.length).toBe(1)
      expect(preloader.preloadQueue[0].name).toBe('TestComponent')
      expect(preloader.preloadQueue[0].priority).toBe('high')
    })

    it('应该按优先级排序预加载队列', () => {
      const loader1 = vi.fn()
      const loader2 = vi.fn()
      const loader3 = vi.fn()
      
      preloader.addToPreloadQueue('LowPriority', loader1, 'low')
      preloader.addToPreloadQueue('HighPriority', loader2, 'high')
      preloader.addToPreloadQueue('NormalPriority', loader3, 'normal')
      
      expect(preloader.preloadQueue[0].priority).toBe('high')
      expect(preloader.preloadQueue[1].priority).toBe('normal')
      expect(preloader.preloadQueue[2].priority).toBe('low')
    })

    it('应该正确获取预加载统计', () => {
      const stats = preloader.getPreloadStats()
      
      expect(stats.preloadedCount).toBe(0)
      expect(stats.queueLength).toBe(0)
      expect(stats.isProcessing).toBe(false)
    })
  })

  describe('ComponentLoadMonitor', () => {
    let monitor

    beforeEach(() => {
      monitor = new ComponentLoadMonitor()
    })

    it('应该正确监控组件加载时间', () => {
      const monitoring = monitor.startMonitoring('TestComponent')
      
      // 模拟加载完成
      monitoring.finish()
      
      const report = monitor.getPerformanceReport()
      expect(report.totalComponents).toBe(1)
      expect(report.averageLoadTime).toBeGreaterThan(0)
    })

    it('应该正确监控组件加载错误', () => {
      const monitoring = monitor.startMonitoring('TestComponent')
      const error = new Error('Load failed')
      
      // 模拟加载错误
      monitoring.error(error)
      
      const report = monitor.getPerformanceReport()
      expect(report.totalComponents).toBe(1)
      expect(report.errorRate).toBeGreaterThan(0)
    })

    it('应该正确生成性能报告', () => {
      const monitoring1 = monitor.startMonitoring('Component1')
      const monitoring2 = monitor.startMonitoring('Component2')
      
      monitoring1.finish()
      monitoring2.error(new Error('Failed'))
      
      const report = monitor.getPerformanceReport()
      expect(report.totalComponents).toBe(2)
      expect(report.errorRate).toBe(0.5)
    })
  })

  describe('路由性能优化', () => {
    it('应该正确进行智能预加载', async () => {
      const preloadPromise = smartPreload('/english/news-dashboard')
      expect(preloadPromise).toBeInstanceOf(Promise)
      
      await preloadPromise
    })

    it('应该正确创建路由性能监控器', () => {
      const monitor = new RoutePerformanceMonitor()
      expect(monitor.metrics).toBeInstanceOf(Map)
      expect(monitor.observer).toBeNull()
    })

    it('应该正确生成路由性能报告', () => {
      const monitor = new RoutePerformanceMonitor()
      const report = monitor.getPerformanceReport()
      
      expect(report.totalRoutes).toBe(0)
      expect(report.averageLoadTime).toBe(0)
      expect(report.slowestRoute).toBeNull()
      expect(report.fastestRoute).toBeNull()
    })
  })

  describe('性能基准测试', () => {
    it('应该在大数据集上保持良好性能', () => {
      const largeData = Array.from({ length: 10000 }, (_, i) => ({ x: i, y: Math.random() }))
      const sampler = new DataSampler({ maxPoints: 100 })
      
      const startTime = performance.now()
      const sampled = sampler.sample(largeData)
      const endTime = performance.now()
      
      expect(sampled.length).toBe(100)
      expect(endTime - startTime).toBeLessThan(100) // 应该在100ms内完成
    })

    it('应该正确处理大量组件预加载', () => {
      const preloader = new SmartPreloader()
      const loaders = Array.from({ length: 100 }, (_, i) => vi.fn())
      
      loaders.forEach((loader, i) => {
        preloader.addToPreloadQueue(`Component${i}`, loader)
      })
      
      expect(preloader.preloadQueue.length).toBe(100)
    })

    it('应该正确处理大量图表更新', () => {
      const optimizer = new ChartUpdateOptimizer()
      const updateFn = vi.fn()
      const throttledUpdate = optimizer.throttleUpdate(updateFn)
      
      // 快速触发多次更新
      for (let i = 0; i < 100; i++) {
        throttledUpdate()
      }
      
      expect(updateFn).toHaveBeenCalled()
    })
  })
})
