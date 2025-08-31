import axios from 'axios'
import { globalErrorHandler } from './errorHandler'

/**
 * API错误拦截器配置
 */
export function setupApiErrorInterceptor () {
  // 请求拦截器
  axios.interceptors.request.use(
    (config) => {
      // 添加请求超时
      if (!config.timeout) {
        config.timeout = 30000 // 30秒超时
      }

      // 添加请求标识，用于错误处理
      config.metadata = {
        startTime: Date.now(),
        operation: config.operation || extractOperationFromUrl(config.url),
        retryCount: config.retryCount || 0,
      }

      return config
    },
    (error) => {
      return Promise.reject(error)
    },
  )

  // 响应拦截器
  axios.interceptors.response.use(
    (response) => {
      // 成功响应，记录性能数据
      const { config } = response
      if (config.metadata) {
        const duration = Date.now() - config.metadata.startTime
        logApiSuccess(config.metadata.operation, duration)
      }

      return response
    },
    async (error) => {
      const { config } = error
      const operation = config?.metadata?.operation || 'unknown'

      // 处理超时错误
      if (error.code === 'ECONNABORTED' && error.message.includes('timeout')) {
        return handleTimeoutError(error, config)
      }

      // 处理网络错误
      if (!error.response && error.request) {
        return handleNetworkError(error, config)
      }

      // 处理HTTP错误
      if (error.response) {
        return handleHttpError(error, config)
      }

      // 处理其他错误
      return handleGenericApiError(error, config)
    },
  )
}

/**
 * 处理超时错误
 */
function handleTimeoutError (error, config) {
  const operation = config?.metadata?.operation
  const retryCount = config?.metadata?.retryCount || 0

  // 自动重试逻辑（仅对GET请求）
  if (config.method.toLowerCase() === 'get' && retryCount < 2) {
    console.log(`请求超时，正在重试... (${retryCount + 1}/2)`)
    
    const retryConfig = {
      ...config,
      metadata: {
        ...config.metadata,
        retryCount: retryCount + 1,
      },
    }

    // 延迟重试
    return new Promise(resolve => {
      setTimeout(() => {
        resolve(axios.request(retryConfig))
      }, 1000 * (retryCount + 1)) // 递增延迟
    })
  }

  // 处理超时错误
  const errorInfo = globalErrorHandler.handleApiError(error, {
    operation,
    type: 'timeout',
  })

  return Promise.reject({ ...error, errorInfo })
}

/**
 * 处理网络错误
 */
function handleNetworkError (error, config) {
  const operation = config?.metadata?.operation
  
  const errorInfo = globalErrorHandler.handleNetworkError(error, {
    operation,
    silent: config?.silent,
  })

  return Promise.reject({ ...error, errorInfo })
}

/**
 * 处理HTTP错误
 */
async function handleHttpError (error, config) {
  const { response } = error
  const operation = config?.metadata?.operation
  const status = response?.status

  // 401错误特殊处理
  if (status === 401) {
    await handleUnauthorizedError(error, config)
  }

  // 5xx错误自动重试逻辑
  if (status >= 500 && status < 600) {
    const retryCount = config?.metadata?.retryCount || 0
    
    if (retryCount < 1 && ['get', 'head'].includes(config.method.toLowerCase())) {
      console.log(`服务器错误，正在重试... (${retryCount + 1}/1)`)
      
      const retryConfig = {
        ...config,
        metadata: {
          ...config.metadata,
          retryCount: retryCount + 1,
        },
      }

      return new Promise(resolve => {
        setTimeout(() => {
          resolve(axios.request(retryConfig))
        }, 2000) // 2秒后重试
      })
    }
  }

  const errorInfo = globalErrorHandler.handleHttpError(error, {
    operation,
    silent: config?.silent,
  })

  return Promise.reject({ ...error, errorInfo })
}

/**
 * 处理通用API错误
 */
function handleGenericApiError (error, config) {
  const operation = config?.metadata?.operation
  
  const errorInfo = globalErrorHandler.handleGenericError(error, {
    operation,
    silent: config?.silent,
  })

  return Promise.reject({ ...error, errorInfo })
}

/**
 * 处理401未授权错误
 */
async function handleUnauthorizedError (error, config) {
  // 清除本地存储的认证信息
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  
  // 如果不是登录请求，则重定向到登录页
  if (!config.url.includes('/login') && !config.url.includes('/auth')) {
    const currentPath = window.location.pathname
    if (currentPath !== '/login') {
      localStorage.setItem('redirectAfterLogin', currentPath)
      setTimeout(() => {
        window.location.href = '/login'
      }, 1500) // 给用户时间看到错误提示
    }
  }
}

/**
 * 从URL提取操作名称
 */
function extractOperationFromUrl (url) {
  if (!url) return 'unknown'
  
  try {
    // 移除查询参数和片段
    const cleanUrl = url.split('?')[0].split('#')[0]
    
    // 提取路径的最后两部分作为操作名称
    const pathParts = cleanUrl.split('/').filter(Boolean)
    const operation = pathParts.slice(-2).join('_')
    
    return operation || 'api_call'
  } catch (error) {
    return 'unknown'
  }
}

/**
 * 记录API成功调用
 */
function logApiSuccess (operation, duration) {
  if (process.env.NODE_ENV === 'development') {
    if (duration > 3000) { // 超过3秒的慢请求
      console.warn(`🐌 慢请求: ${operation} 耗时 ${duration}ms`)
    } else if (duration > 1000) {
      console.log(`⏱️ ${operation} 耗时 ${duration}ms`)
    }
  }

  // 可以发送性能数据到监控服务
  if (process.env.NODE_ENV === 'production' && duration > 5000) {
    // 发送慢请求报告
    sendPerformanceData({
      type: 'slow_api',
      operation,
      duration,
      timestamp: new Date().toISOString(),
    })
  }
}

/**
 * 发送性能数据
 */
async function sendPerformanceData (data) {
  try {
    // 可以集成性能监控服务
    /*
    await fetch('/api/performance', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    })
    */
  } catch (error) {
    // 静默处理性能数据发送失败
    console.warn('Failed to send performance data:', error)
  }
}

/**
 * 创建带有错误处理的API客户端
 */
export function createApiClient (baseURL, options = {}) {
  const client = axios.create({
    baseURL,
    timeout: 30000,
    ...options,
  })

  // 为这个客户端单独设置拦截器
  client.interceptors.request.use(
    (config) => {
      config.metadata = {
        startTime: Date.now(),
        operation: config.operation || extractOperationFromUrl(config.url),
        retryCount: 0,
      }
      return config
    },
  )

  client.interceptors.response.use(
    (response) => {
      const { config } = response
      if (config.metadata) {
        const duration = Date.now() - config.metadata.startTime
        logApiSuccess(config.metadata.operation, duration)
      }
      return response
    },
    (error) => {
      const operation = error.config?.metadata?.operation
      
      globalErrorHandler.handleApiError(error, {
        operation,
        silent: error.config?.silent,
      })

      return Promise.reject(error)
    },
  )

  return client
}

/**
 * 用于特定操作的API包装器
 */
export class ApiWrapper {
  constructor (client = axios) {
    this.client = client
  }

  /**
   * 安全的GET请求
   */
  async get (url, config = {}) {
    try {
      const response = await this.client.get(url, {
        ...config,
        operation: config.operation || `get_${extractOperationFromUrl(url)}`,
      })
      return response.data
    } catch (error) {
      if (config.fallback) {
        console.warn(`API调用失败，使用fallback数据: ${url}`)
        return config.fallback
      }
      throw error
    }
  }

  /**
   * 安全的POST请求
   */
  async post (url, data, config = {}) {
    try {
      const response = await this.client.post(url, data, {
        ...config,
        operation: config.operation || `post_${extractOperationFromUrl(url)}`,
      })
      return response.data
    } catch (error) {
      if (config.fallback) {
        console.warn(`API调用失败，使用fallback数据: ${url}`)
        return config.fallback
      }
      throw error
    }
  }

  /**
   * 安全的PUT请求
   */
  async put (url, data, config = {}) {
    try {
      const response = await this.client.put(url, data, {
        ...config,
        operation: config.operation || `put_${extractOperationFromUrl(url)}`,
      })
      return response.data
    } catch (error) {
      throw error
    }
  }

  /**
   * 安全的DELETE请求
   */
  async delete (url, config = {}) {
    try {
      const response = await this.client.delete(url, {
        ...config,
        operation: config.operation || `delete_${extractOperationFromUrl(url)}`,
      })
      return response.data
    } catch (error) {
      throw error
    }
  }
}

// 创建默认的API包装器实例
export const api = new ApiWrapper()
