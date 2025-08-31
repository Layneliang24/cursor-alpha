import { ElMessage, ElNotification } from 'element-plus'

/**
 * 全局错误处理器
 */
export class ErrorHandler {
  constructor () {
    this.errorQueue = new Set() // 防止重复错误
    this.maxQueueSize = 10
    this.retryAttempts = new Map() // 记录重试次数
    this.maxRetries = 3
  }

  /**
   * 处理API错误
   * @param {Error} error - 错误对象
   * @param {Object} context - 错误上下文
   */
  handleApiError (error, context = {}) {
    const { response, request, message } = error
    const { operation, silent = false } = context

    // 网络错误
    if (!response && request) {
      return this.handleNetworkError(error, context)
    }

    // HTTP错误响应
    if (response) {
      return this.handleHttpError(error, context)
    }

    // 其他错误
    return this.handleGenericError(error, context)
  }

  /**
   * 处理网络错误
   */
  handleNetworkError (error, context = {}) {
    const { operation, silent } = context
    const errorKey = `network_${operation || 'unknown'}`

    if (this.isDuplicateError(errorKey)) {
      return
    }

    const errorInfo = {
      type: 'network',
      title: '网络连接失败',
      message: '请检查网络连接后重试',
      duration: 5000,
      action: operation ? () => this.suggestRetry(operation) : null,
    }

    if (!silent) {
      this.showErrorNotification(errorInfo)
    }

    this.logError('Network Error', { error, context })
    return errorInfo
  }

  /**
   * 处理HTTP错误
   */
  handleHttpError (error, context = {}) {
    const { response } = error
    const { operation, silent } = context
    const status = response?.status
    const data = response?.data

    const errorKey = `http_${status}_${operation || 'unknown'}`
    
    if (this.isDuplicateError(errorKey)) {
      return
    }

    let errorInfo = {
      type: 'http',
      status,
      duration: 4000,
    }

    switch (status) {
      case 400:
        errorInfo = {
          ...errorInfo,
          title: '请求参数错误',
          message: data?.message || '请检查输入的信息是否正确',
          severity: 'warning',
        }
        break

      case 401:
        errorInfo = {
          ...errorInfo,
          title: '身份验证失败',
          message: '请重新登录',
          severity: 'error',
          action: () => this.redirectToLogin(),
        }
        break

      case 403:
        errorInfo = {
          ...errorInfo,
          title: '权限不足',
          message: '您没有权限执行此操作',
          severity: 'warning',
        }
        break

      case 404:
        errorInfo = {
          ...errorInfo,
          title: '资源未找到',
          message: data?.message || '请求的资源不存在',
          severity: 'warning',
        }
        break

      case 422:
        errorInfo = {
          ...errorInfo,
          title: '数据验证失败',
          message: this.formatValidationErrors(data),
          severity: 'warning',
        }
        break

      case 429:
        errorInfo = {
          ...errorInfo,
          title: '请求过于频繁',
          message: '请稍后再试',
          severity: 'warning',
          duration: 6000,
        }
        break

      case 500:
        errorInfo = {
          ...errorInfo,
          title: '服务器内部错误',
          message: '服务暂时不可用，请稍后重试',
          severity: 'error',
          action: operation ? () => this.suggestRetry(operation) : null,
        }
        break

      case 502:
      case 503:
      case 504:
        errorInfo = {
          ...errorInfo,
          title: '服务不可用',
          message: '服务器正在维护，请稍后重试',
          severity: 'error',
          duration: 6000,
        }
        break

      default:
        errorInfo = {
          ...errorInfo,
          title: '请求失败',
          message: data?.message || `HTTP ${status} 错误`,
          severity: 'error',
        }
    }

    if (!silent) {
      this.showErrorNotification(errorInfo)
    }

    this.logError('HTTP Error', { error, context, errorInfo })
    return errorInfo
  }

  /**
   * 处理通用错误
   */
  handleGenericError (error, context = {}) {
    const { operation, silent } = context
    const errorKey = `generic_${operation || 'unknown'}_${error.message}`

    if (this.isDuplicateError(errorKey)) {
      return
    }

    const errorInfo = {
      type: 'generic',
      title: '操作失败',
      message: error.message || '发生未知错误',
      severity: 'error',
      duration: 4000,
    }

    if (!silent) {
      this.showErrorNotification(errorInfo)
    }

    this.logError('Generic Error', { error, context })
    return errorInfo
  }

  /**
   * 处理Vue组件错误
   */
  handleComponentError (error, instance, info) {
    const errorInfo = {
      type: 'component',
      title: '组件加载失败',
      message: '页面部分功能可能受到影响',
      severity: 'warning',
      duration: 3000,
    }

    this.showErrorNotification(errorInfo)
    this.logError('Component Error', { error, instance, info })

    // 不阻止错误向上传播
    return false
  }

  /**
   * 处理资源加载错误
   */
  handleResourceError (error, resource) {
    const errorInfo = {
      type: 'resource',
      title: '资源加载失败',
      message: `无法加载 ${resource}`,
      severity: 'warning',
      duration: 3000,
    }

    this.showErrorNotification(errorInfo)
    this.logError('Resource Error', { error, resource })
  }

  /**
   * 显示错误通知
   */
  showErrorNotification (errorInfo) {
    const { type, title, message, severity = 'error', duration = 4000, action } = errorInfo

    if (severity === 'error') {
      ElNotification({
        title,
        message: this.formatErrorMessage(message, action),
        type: 'error',
        duration,
        dangerouslyUseHTMLString: !!action,
      })
    } else if (severity === 'warning') {
      ElMessage({
        message: `${title}: ${message}`,
        type: 'warning',
        duration,
        showClose: true,
      })
    } else {
      ElMessage({
        message: `${title}: ${message}`,
        type: 'info',
        duration,
      })
    }
  }

  /**
   * 格式化错误消息
   */
  formatErrorMessage (message, action) {
    if (action) {
      return `${message} <a href="#" onclick="this.parentNode.querySelector('button').click()" style="color: #409eff;">点击重试</a>`
    }
    return message
  }

  /**
   * 格式化验证错误
   */
  formatValidationErrors (data) {
    if (data?.errors && typeof data.errors === 'object') {
      const errors = Object.values(data.errors).flat()
      return errors.slice(0, 3).join('; ') + (errors.length > 3 ? '...' : '')
    }
    return data?.message || '数据验证失败'
  }

  /**
   * 检查是否为重复错误
   */
  isDuplicateError (errorKey) {
    if (this.errorQueue.has(errorKey)) {
      return true
    }

    this.errorQueue.add(errorKey)
    
    // 清理过期的错误记录
    if (this.errorQueue.size > this.maxQueueSize) {
      const firstKey = this.errorQueue.values().next().value
      this.errorQueue.delete(firstKey)
    }

    // 5秒后清除错误记录
    setTimeout(() => {
      this.errorQueue.delete(errorKey)
    }, 5000)

    return false
  }

  /**
   * 建议重试
   */
  suggestRetry (operation) {
    const retryCount = this.retryAttempts.get(operation) || 0
    
    if (retryCount >= this.maxRetries) {
      ElMessage({
        message: '重试次数已达上限，请稍后再试',
        type: 'warning',
      })
      return
    }

    this.retryAttempts.set(operation, retryCount + 1)
    
    // 这里可以触发重试逻辑
    ElMessage({
      message: '正在重试...',
      type: 'info',
    })

    // 清除重试计数（延迟清除）
    setTimeout(() => {
      this.retryAttempts.delete(operation)
    }, 60000)
  }

  /**
   * 重定向到登录页
   */
  redirectToLogin () {
    // 保存当前路径用于登录后重定向
    const currentPath = window.location.pathname
    localStorage.setItem('redirectAfterLogin', currentPath)
    
    // 跳转到登录页
    window.location.href = '/login'
  }

  /**
   * 记录错误日志
   */
  logError (type, details) {
    const logEntry = {
      timestamp: new Date().toISOString(),
      type,
      userAgent: navigator.userAgent,
      url: window.location.href,
      ...details,
    }

    // 开发环境下输出到控制台
    if (process.env.NODE_ENV === 'development') {
      console.group(`🚨 ${type}`)
      console.error(logEntry)
      console.groupEnd()
    }

    // 生产环境下可以发送到错误监控服务
    if (process.env.NODE_ENV === 'production') {
      this.sendToErrorService(logEntry)
    }
  }

  /**
   * 发送错误到监控服务
   */
  async sendToErrorService (logEntry) {
    try {
      // 这里可以集成第三方错误监控服务
      // 如 Sentry, LogRocket, Bugsnag 等
      
      // 示例：发送到自己的错误收集API
      /*
      await fetch('/api/errors', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(logEntry)
      })
      */
    } catch (error) {
      // 静默处理错误服务的失败
      console.warn('Failed to send error to monitoring service:', error)
    }
  }

  /**
   * 清理资源
   */
  cleanup () {
    this.errorQueue.clear()
    this.retryAttempts.clear()
  }
}

// 创建全局实例
export const globalErrorHandler = new ErrorHandler()

// Vue错误处理器
export const vueErrorHandler = (error, instance, info) => {
  return globalErrorHandler.handleComponentError(error, instance, info)
}

// 全局未捕获错误处理器
export const globalUnhandledErrorHandler = (event) => {
  globalErrorHandler.handleGenericError(event.error, {
    operation: 'global_unhandled',
    silent: false,
  })
}

// Promise拒绝处理器
export const globalUnhandledRejectionHandler = (event) => {
  globalErrorHandler.handleGenericError(event.reason, {
    operation: 'global_promise_rejection',
    silent: false,
  })
  
  // 阻止默认的未处理Promise拒绝行为
  event.preventDefault()
}
