import { defineStore } from 'pinia'
import { ElLoading } from 'element-plus'

/**
 * 全局加载状态管理
 */
export const useLoadingStore = defineStore('loading', {
  state: () => ({
    // 全局加载状态
    globalLoading: false,
    globalLoadingInstance: null,
    
    // 局部加载状态映射
    localLoadings: new Map(),
    
    // 加载计数器（用于处理并发请求）
    loadingCounters: new Map(),
    
    // 加载消息
    loadingMessages: new Map(),
    
    // 最小加载时间（防止闪烁）
    minLoadingTime: 300,
    
    // 加载开始时间记录
    loadingStartTimes: new Map(),
  }),

  getters: {
    /**
     * 检查是否有任何加载状态
     */
    hasAnyLoading: (state) => {
      return state.globalLoading || state.localLoadings.size > 0
    },

    /**
     * 获取特定键的加载状态
     */
    isLoading: (state) => (key) => {
      return state.localLoadings.get(key) || false
    },

    /**
     * 获取所有活跃的加载状态
     */
    activeLoadings: (state) => {
      return Array.from(state.localLoadings.entries())
        .filter(([_, loading]) => loading)
        .map(([key]) => key)
    },

    /**
     * 获取加载消息
     */
    getLoadingMessage: (state) => (key) => {
      return state.loadingMessages.get(key) || '加载中...'
    },
  },

  actions: {
    /**
     * 显示全局加载
     */
    showGlobalLoading (options = {}) {
      const {
        text = '加载中...',
        spinner = 'el-icon-loading',
        background = 'rgba(0, 0, 0, 0.7)',
        customClass = '',
        target = document.body,
      } = options

      if (this.globalLoading) {
        return this.globalLoadingInstance
      }

      this.globalLoading = true
      this.globalLoadingInstance = ElLoading.service({
        lock: true,
        text,
        spinner,
        background,
        customClass,
        target,
      })

      return this.globalLoadingInstance
    },

    /**
     * 隐藏全局加载
     */
    hideGlobalLoading () {
      if (this.globalLoadingInstance) {
        this.globalLoadingInstance.close()
        this.globalLoadingInstance = null
      }
      this.globalLoading = false
    },

    /**
     * 显示局部加载
     */
    showLoading (key, options = {}) {
      const {
        message = '加载中...',
        minTime = this.minLoadingTime,
      } = options

      // 增加计数器
      const currentCount = this.loadingCounters.get(key) || 0
      this.loadingCounters.set(key, currentCount + 1)

      // 设置加载状态
      this.localLoadings.set(key, true)
      this.loadingMessages.set(key, message)

      // 记录开始时间
      if (!this.loadingStartTimes.has(key)) {
        this.loadingStartTimes.set(key, Date.now())
      }

      // 如果设置了最小时间，确保加载至少显示指定时间
      if (minTime > 0) {
        setTimeout(() => {
          // 只有在没有新的加载请求时才隐藏
          if (this.loadingCounters.get(key) === 1) {
            this.hideLoading(key)
          }
        }, minTime)
      }
    },

    /**
     * 隐藏局部加载
     */
    async hideLoading (key) {
      const currentCount = this.loadingCounters.get(key) || 0
      
      if (currentCount <= 1) {
        // 检查最小显示时间
        const startTime = this.loadingStartTimes.get(key)
        const minTime = this.minLoadingTime
        
        if (startTime && minTime > 0) {
          const elapsed = Date.now() - startTime
          const remaining = minTime - elapsed
          
          if (remaining > 0) {
            // 等待剩余时间
            await new Promise(resolve => setTimeout(resolve, remaining))
          }
        }

        // 清除加载状态
        this.localLoadings.set(key, false)
        this.loadingCounters.delete(key)
        this.loadingMessages.delete(key)
        this.loadingStartTimes.delete(key)
      } else {
        // 减少计数器
        this.loadingCounters.set(key, currentCount - 1)
      }
    },

    /**
     * 切换加载状态
     */
    toggleLoading (key, options = {}) {
      if (this.isLoading(key)) {
        this.hideLoading(key)
      } else {
        this.showLoading(key, options)
      }
    },

    /**
     * 清除所有加载状态
     */
    clearAllLoading () {
      this.hideGlobalLoading()
      this.localLoadings.clear()
      this.loadingCounters.clear()
      this.loadingMessages.clear()
      this.loadingStartTimes.clear()
    },

    /**
     * 包装异步函数，自动处理加载状态
     */
    async withLoading (key, asyncFn, options = {}) {
      const {
        global = false,
        message = '加载中...',
        minTime = this.minLoadingTime,
        onError = null,
      } = options

      try {
        // 显示加载状态
        if (global) {
          this.showGlobalLoading({ text: message })
        } else {
          this.showLoading(key, { message, minTime })
        }

        // 执行异步函数
        const result = await asyncFn()
        return result

      } catch (error) {
        // 错误处理
        if (onError) {
          onError(error)
        }
        throw error

      } finally {
        // 隐藏加载状态
        if (global) {
          this.hideGlobalLoading()
        } else {
          await this.hideLoading(key)
        }
      }
    },

    /**
     * 批量操作加载状态
     */
    async withMultipleLoading (loadingConfigs, asyncFn) {
      try {
        // 显示所有加载状态
        loadingConfigs.forEach(config => {
          const { key, global = false, message = '加载中...' } = config
          if (global) {
            this.showGlobalLoading({ text: message })
          } else {
            this.showLoading(key, { message })
          }
        })

        // 执行异步函数
        const result = await asyncFn()
        return result

      } finally {
        // 隐藏所有加载状态
        for (const config of loadingConfigs) {
          const { key, global = false } = config
          if (global) {
            this.hideGlobalLoading()
          } else {
            await this.hideLoading(key)
          }
        }
      }
    },

    /**
     * 创建加载装饰器
     */
    createLoadingDecorator (key, options = {}) {
      return (target, propertyName, descriptor) => {
        const originalMethod = descriptor.value

        descriptor.value = async function (...args) {
          return await this.$loadingStore.withLoading(
            key, 
            () => originalMethod.apply(this, args),
            options,
          )
        }

        return descriptor
      }
    },

    /**
     * 设置最小加载时间
     */
    setMinLoadingTime (time) {
      this.minLoadingTime = time
    },

    /**
     * 获取加载统计信息
     */
    getLoadingStats () {
      return {
        globalLoading: this.globalLoading,
        activeLoadingsCount: this.localLoadings.size,
        activeLoadings: this.activeLoadings,
        totalCounters: Array.from(this.loadingCounters.entries()),
      }
    },

    /**
     * 调试信息
     */
    debugLoading () {
      if (process.env.NODE_ENV === 'development') {
        console.group('🔄 Loading Store Debug Info')
        console.log('Global Loading:', this.globalLoading)
        console.log('Local Loadings:', Object.fromEntries(this.localLoadings))
        console.log('Loading Counters:', Object.fromEntries(this.loadingCounters))
        console.log('Loading Messages:', Object.fromEntries(this.loadingMessages))
        console.log('Start Times:', Object.fromEntries(this.loadingStartTimes))
        console.groupEnd()
      }
    },
  },
})
