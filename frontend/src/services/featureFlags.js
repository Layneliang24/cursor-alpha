import { ref, reactive } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { featureFlagsAPI } from '@/api/featureFlags'

/**
 * 特性开关服务
 */
class FeatureFlagService {
  constructor() {
    this.flags = reactive({})
    this.loading = ref(false)
    this.error = ref(null)
    this.initialized = ref(false)
    this.environment = import.meta.env.MODE || 'development'
    
    // 缓存配置
    this.cacheKey = 'feature_flags_cache'
    this.cacheExpiry = 5 * 60 * 1000 // 5分钟
    
    // 自动初始化
    this.init()
  }
  
  /**
   * 初始化特性开关
   */
  async init() {
    if (this.initialized.value) return
    
    try {
      this.loading.value = true
      this.error.value = null
      
      // 尝试从缓存加载
      const cached = this.loadFromCache()
      if (cached) {
        Object.assign(this.flags, cached)
      }
      
      // 从服务器获取最新数据
      await this.fetchFlags()
      
      this.initialized.value = true
    } catch (error) {
      console.error('Failed to initialize feature flags:', error)
      this.error.value = error.message
      
      // 如果有缓存数据，继续使用
      if (Object.keys(this.flags).length === 0) {
        this.loadDefaultFlags()
      }
    } finally {
      this.loading.value = false
    }
  }
  
  /**
   * 从服务器获取特性开关
   */
  async fetchFlags() {
    try {
      const response = await featureFlagsAPI.getUserFlags()
      const flags = {}
      
      if (response && response.flags) {
        Object.keys(response.flags).forEach(key => {
          const flag = response.flags[key]
          flags[key] = {
            enabled: flag.enabled,
            value: flag.value,
            name: flag.name,
            description: flag.description
          }
        })
      }
      
      Object.assign(this.flags, flags)
      this.saveToCache(flags)
      
      return flags
    } catch (error) {
      console.error('Failed to fetch feature flags:', error)
      throw error
    }
  }
  
  /**
   * 检查特性开关是否启用
   * @param {string} key - 特性开关键
   * @param {boolean} defaultValue - 默认值
   * @returns {boolean}
   */
  isEnabled(key, defaultValue = false) {
    const flag = this.flags[key]
    if (!flag) {
      console.warn(`Feature flag '${key}' not found, using default value: ${defaultValue}`)
      return defaultValue
    }
    
    // 记录使用情况
    this.recordUsage(key, flag.enabled)
    
    return flag.enabled
  }
  
  /**
   * 获取特性开关的值
   * @param {string} key - 特性开关键
   * @param {any} defaultValue - 默认值
   * @returns {any}
   */
  getValue(key, defaultValue = null) {
    const flag = this.flags[key]
    if (!flag || !flag.enabled) {
      return defaultValue
    }
    
    // 记录使用情况
    this.recordUsage(key, true, flag.value)
    
    return flag.value || defaultValue
  }
  
  /**
   * 获取所有特性开关状态
   * @returns {Object}
   */
  getAllFlags() {
    return { ...this.flags }
  }
  
  /**
   * 刷新特性开关
   */
  async refresh() {
    try {
      this.loading.value = true
      this.error.value = null
      await this.fetchFlags()
    } catch (error) {
      this.error.value = error.message
      throw error
    } finally {
      this.loading.value = false
    }
  }
  
  /**
   * 记录特性开关使用情况
   * @param {string} key - 特性开关键
   * @param {boolean} enabled - 是否启用
   * @param {any} value - 返回的值
   */
  recordUsage(key, enabled, value = null) {
    // 异步记录，不阻塞主流程
    setTimeout(async () => {
      try {
        const authStore = useAuthStore()
        const context = {
          url: window.location.href,
          userAgent: navigator.userAgent,
          timestamp: new Date().toISOString(),
          environment: this.environment
        }
        
        await featureFlagsAPI.recordUsage(key, {
           is_enabled: enabled,
           value_returned: value,
           context: context,
           environment: process.env.NODE_ENV
         })
      } catch (error) {
        // 静默失败，不影响用户体验
        console.debug('Failed to record feature flag usage:', error)
      }
    }, 0)
  }
  
  /**
   * 保存到本地缓存
   * @param {Object} flags - 特性开关数据
   */
  saveToCache(flags) {
    try {
      const cacheData = {
        flags,
        timestamp: Date.now(),
        environment: this.environment
      }
      localStorage.setItem(this.cacheKey, JSON.stringify(cacheData))
    } catch (error) {
      console.warn('Failed to save feature flags to cache:', error)
    }
  }
  
  /**
   * 从本地缓存加载
   * @returns {Object|null}
   */
  loadFromCache() {
    try {
      const cached = localStorage.getItem(this.cacheKey)
      if (!cached) return null
      
      const cacheData = JSON.parse(cached)
      const isExpired = Date.now() - cacheData.timestamp > this.cacheExpiry
      const isWrongEnv = cacheData.environment !== this.environment
      
      if (isExpired || isWrongEnv) {
        localStorage.removeItem(this.cacheKey)
        return null
      }
      
      return cacheData.flags
    } catch (error) {
      console.warn('Failed to load feature flags from cache:', error)
      localStorage.removeItem(this.cacheKey)
      return null
    }
  }
  
  /**
   * 加载默认特性开关
   */
  loadDefaultFlags() {
    const defaultFlags = {
      new_ui_design: {
        enabled: false,
        value: {},
        name: '新UI设计',
        description: '启用新的用户界面设计'
      },
      advanced_analytics: {
        enabled: false,
        value: {},
        name: '高级数据分析',
        description: '启用高级数据分析功能'
      },
      social_learning: {
        enabled: false,
        value: {},
        name: '社交学习',
        description: '启用社交学习功能'
      },
      offline_mode: {
        enabled: false,
        value: {},
        name: '离线模式',
        description: '启用离线学习模式'
      },
      ai_recommendations: {
        enabled: false,
        value: {},
        name: 'AI推荐',
        description: '启用AI学习路径推荐'
      }
    }
    
    Object.assign(this.flags, defaultFlags)
  }
  
  /**
   * 清除缓存
   */
  clearCache() {
    localStorage.removeItem(this.cacheKey)
  }
  
  /**
   * 获取加载状态
   */
  getLoadingState() {
    return {
      loading: this.loading.value,
      error: this.error.value,
      initialized: this.initialized.value
    }
  }
}

// 创建单例实例
const featureFlagService = new FeatureFlagService()

// 导出类和实例
export { FeatureFlagService, featureFlagService }

/**
 * 特性开关组合式API
 * @returns {Object}
 */
export function useFeatureFlags() {
  return {
    flags: featureFlagService.flags,
    loading: featureFlagService.loading,
    error: featureFlagService.error,
    initialized: featureFlagService.initialized,
    
    isEnabled: (key, defaultValue) => featureFlagService.isEnabled(key, defaultValue),
    getValue: (key, defaultValue) => featureFlagService.getValue(key, defaultValue),
    getAllFlags: () => featureFlagService.getAllFlags(),
    refresh: () => featureFlagService.refresh(),
    clearCache: () => featureFlagService.clearCache(),
    getLoadingState: () => featureFlagService.getLoadingState()
  }
}

/**
 * 特性开关指令
 * 用法: v-feature="'feature_key'"
 */
export const vFeature = {
  mounted(el, binding) {
    const key = binding.value
    const enabled = featureFlagService.isEnabled(key, false)
    
    if (!enabled) {
      el.style.display = 'none'
    }
  },
  
  updated(el, binding) {
    const key = binding.value
    const enabled = featureFlagService.isEnabled(key, false)
    
    el.style.display = enabled ? '' : 'none'
  }
}

export default featureFlagService