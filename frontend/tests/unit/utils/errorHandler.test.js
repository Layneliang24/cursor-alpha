import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { ErrorHandler } from '@/utils/errorHandler'
import { ElMessage, ElNotification } from 'element-plus'

// Mock Element Plus组件
vi.mock('element-plus', () => ({
  ElMessage: {
    error: vi.fn(),
    warning: vi.fn(),
    info: vi.fn(),
  },
  ElNotification: vi.fn(),
}))

describe('ErrorHandler', () => {
  let errorHandler

  beforeEach(() => {
    errorHandler = new ErrorHandler()
    vi.clearAllMocks()
    vi.stubGlobal('console', {
      error: vi.fn(),
      warn: vi.fn(),
      log: vi.fn(),
      group: vi.fn(),
      groupEnd: vi.fn(),
    })
  })

  afterEach(() => {
    errorHandler.cleanup()
    vi.unstubAllGlobals()
  })

  describe('网络错误处理', () => {
    it('应该处理网络连接错误', () => {
      const error = {
        request: {},
        message: 'Network Error',
      }

      const result = errorHandler.handleNetworkError(error, { operation: 'test_api' })

      expect(result.type).toBe('network')
      expect(result.title).toBe('网络连接失败')
      expect(result.message).toBe('请检查网络连接后重试')
      expect(ElNotification).toHaveBeenCalled()
    })

    it('应该防止重复的网络错误通知', () => {
      const error = {
        request: {},
        message: 'Network Error',
      }

      // 第一次调用
      errorHandler.handleNetworkError(error, { operation: 'test_api' })
      // 第二次调用（应该被忽略）
      errorHandler.handleNetworkError(error, { operation: 'test_api' })

      expect(ElNotification).toHaveBeenCalledTimes(1)
    })

    it('应该支持静默模式', () => {
      const error = {
        request: {},
        message: 'Network Error',
      }

      errorHandler.handleNetworkError(error, { operation: 'test_api', silent: true })

      expect(ElNotification).not.toHaveBeenCalled()
    })
  })

  describe('HTTP错误处理', () => {
    it('应该处理400错误', () => {
      const error = {
        response: {
          status: 400,
          data: { message: '请求参数无效' },
        },
      }

      const result = errorHandler.handleHttpError(error, { operation: 'test_api' })

      expect(result.status).toBe(400)
      expect(result.title).toBe('请求参数错误')
      expect(result.severity).toBe('warning')
      expect(ElMessage.warning).toHaveBeenCalled()
    })

    it('应该处理401未授权错误', () => {
      const error = {
        response: {
          status: 401,
          data: { message: '未授权访问' },
        },
      }

      const result = errorHandler.handleHttpError(error, { operation: 'test_api' })

      expect(result.status).toBe(401)
      expect(result.title).toBe('身份验证失败')
      expect(result.severity).toBe('error')
      expect(result.action).toBeDefined()
    })

    it('应该处理403权限不足错误', () => {
      const error = {
        response: {
          status: 403,
          data: { message: '权限不足' },
        },
      }

      const result = errorHandler.handleHttpError(error, { operation: 'test_api' })

      expect(result.status).toBe(403)
      expect(result.title).toBe('权限不足')
      expect(result.severity).toBe('warning')
    })

    it('应该处理404资源未找到错误', () => {
      const error = {
        response: {
          status: 404,
          data: { message: '资源不存在' },
        },
      }

      const result = errorHandler.handleHttpError(error, { operation: 'test_api' })

      expect(result.status).toBe(404)
      expect(result.title).toBe('资源未找到')
      expect(result.severity).toBe('warning')
    })

    it('应该处理422验证错误', () => {
      const error = {
        response: {
          status: 422,
          data: {
            errors: {
              email: ['邮箱格式不正确'],
              password: ['密码长度不足'],
            },
          },
        },
      }

      const result = errorHandler.handleHttpError(error, { operation: 'test_api' })

      expect(result.status).toBe(422)
      expect(result.title).toBe('数据验证失败')
      expect(result.message).toContain('邮箱格式不正确')
    })

    it('应该处理429请求频繁错误', () => {
      const error = {
        response: {
          status: 429,
          data: { message: '请求过于频繁' },
        },
      }

      const result = errorHandler.handleHttpError(error, { operation: 'test_api' })

      expect(result.status).toBe(429)
      expect(result.title).toBe('请求过于频繁')
      expect(result.duration).toBe(6000)
    })

    it('应该处理500服务器错误', () => {
      const error = {
        response: {
          status: 500,
          data: { message: '服务器内部错误' },
        },
      }

      const result = errorHandler.handleHttpError(error, { operation: 'test_api' })

      expect(result.status).toBe(500)
      expect(result.title).toBe('服务器内部错误')
      expect(result.severity).toBe('error')
      expect(result.action).toBeDefined()
    })

    it('应该处理503服务不可用错误', () => {
      const error = {
        response: {
          status: 503,
          data: { message: '服务不可用' },
        },
      }

      const result = errorHandler.handleHttpError(error, { operation: 'test_api' })

      expect(result.status).toBe(503)
      expect(result.title).toBe('服务不可用')
      expect(result.duration).toBe(6000)
    })
  })

  describe('通用错误处理', () => {
    it('应该处理JavaScript错误', () => {
      const error = new Error('Unexpected token')

      const result = errorHandler.handleGenericError(error, { operation: 'test_operation' })

      expect(result.type).toBe('generic')
      expect(result.title).toBe('操作失败')
      expect(result.message).toBe('Unexpected token')
      expect(result.severity).toBe('error')
    })

    it('应该处理无消息的错误', () => {
      const error = new Error()

      const result = errorHandler.handleGenericError(error, { operation: 'test_operation' })

      expect(result.message).toBe('发生未知错误')
    })
  })

  describe('Vue组件错误处理', () => {
    it('应该处理Vue组件错误', () => {
      const error = new Error('Component error')
      const instance = { $options: { name: 'TestComponent' } }
      const info = 'render function'

      const result = errorHandler.handleComponentError(error, instance, info)

      expect(result).toBe(false) // 不阻止错误传播
      expect(ElNotification).toHaveBeenCalledWith({
        title: '组件加载失败',
        message: '页面部分功能可能受到影响',
        type: 'warning',
        duration: 3000,
      })
    })
  })

  describe('资源加载错误处理', () => {
    it('应该处理资源加载失败', () => {
      const error = new Error('Failed to load resource')
      const resource = 'image.jpg'

      errorHandler.handleResourceError(error, resource)

      expect(ElNotification).toHaveBeenCalledWith({
        title: '资源加载失败',
        message: '无法加载 image.jpg',
        type: 'warning',
        duration: 3000,
      })
    })
  })

  describe('错误去重机制', () => {
    it('应该检测重复错误', () => {
      const errorKey = 'test_error_key'

      const firstCall = errorHandler.isDuplicateError(errorKey)
      const secondCall = errorHandler.isDuplicateError(errorKey)

      expect(firstCall).toBe(false)
      expect(secondCall).toBe(true)
    })

    it('应该在超时后清除错误记录', async () => {
      const errorKey = 'test_error_key'

      errorHandler.isDuplicateError(errorKey)
      
      // 模拟5秒后
      vi.advanceTimersByTime(5000)
      await new Promise(resolve => setTimeout(resolve, 0))

      const result = errorHandler.isDuplicateError(errorKey)
      expect(result).toBe(false)
    })
  })

  describe('重试机制', () => {
    it('应该跟踪重试次数', () => {
      const operation = 'test_operation'

      errorHandler.suggestRetry(operation)
      errorHandler.suggestRetry(operation)
      errorHandler.suggestRetry(operation)

      expect(errorHandler.retryAttempts.get(operation)).toBe(3)
    })

    it('应该在达到最大重试次数时显示警告', () => {
      const operation = 'test_operation'

      // 设置重试次数达到上限
      errorHandler.retryAttempts.set(operation, errorHandler.maxRetries)
      
      errorHandler.suggestRetry(operation)

      expect(ElMessage.warning).toHaveBeenCalledWith({
        message: '重试次数已达上限，请稍后再试',
        type: 'warning',
      })
    })
  })

  describe('验证错误格式化', () => {
    it('应该格式化验证错误对象', () => {
      const data = {
        errors: {
          email: ['邮箱格式不正确', '邮箱已存在'],
          password: ['密码长度不足'],
        },
      }

      const result = errorHandler.formatValidationErrors(data)

      expect(result).toBe('邮箱格式不正确; 邮箱已存在; 密码长度不足')
    })

    it('应该限制错误消息长度', () => {
      const data = {
        errors: {
          field1: ['错误1'],
          field2: ['错误2'],
          field3: ['错误3'],
          field4: ['错误4'],
          field5: ['错误5'],
        },
      }

      const result = errorHandler.formatValidationErrors(data)

      expect(result).toBe('错误1; 错误2; 错误3...')
    })

    it('应该处理简单的错误消息', () => {
      const data = { message: '简单错误消息' }

      const result = errorHandler.formatValidationErrors(data)

      expect(result).toBe('简单错误消息')
    })

    it('应该提供默认错误消息', () => {
      const data = {}

      const result = errorHandler.formatValidationErrors(data)

      expect(result).toBe('数据验证失败')
    })
  })

  describe('日志记录', () => {
    it('应该在开发环境记录错误日志', () => {
      vi.stubEnv('NODE_ENV', 'development')
      
      const error = new Error('Test error')
      errorHandler.logError('Test Error', { error })

      expect(console.group).toHaveBeenCalledWith('🚨 Test Error')
      expect(console.error).toHaveBeenCalled()
      expect(console.groupEnd).toHaveBeenCalled()
    })
  })

  describe('清理功能', () => {
    it('应该清理所有错误记录', () => {
      // 添加一些错误记录
      errorHandler.isDuplicateError('error1')
      errorHandler.suggestRetry('operation1')

      expect(errorHandler.errorQueue.size).toBe(1)
      expect(errorHandler.retryAttempts.size).toBe(1)

      errorHandler.cleanup()

      expect(errorHandler.errorQueue.size).toBe(0)
      expect(errorHandler.retryAttempts.size).toBe(0)
    })
  })

  describe('API错误处理集成', () => {
    it('应该正确路由网络错误', () => {
      const error = {
        request: {},
        message: 'Network Error',
      }

      const spy = vi.spyOn(errorHandler, 'handleNetworkError')
      errorHandler.handleApiError(error, { operation: 'test' })

      expect(spy).toHaveBeenCalledWith(error, { operation: 'test' })
    })

    it('应该正确路由HTTP错误', () => {
      const error = {
        response: { status: 404 },
        message: 'Not Found',
      }

      const spy = vi.spyOn(errorHandler, 'handleHttpError')
      errorHandler.handleApiError(error, { operation: 'test' })

      expect(spy).toHaveBeenCalledWith(error, { operation: 'test' })
    })

    it('应该正确路由通用错误', () => {
      const error = new Error('Generic error')

      const spy = vi.spyOn(errorHandler, 'handleGenericError')
      errorHandler.handleApiError(error, { operation: 'test' })

      expect(spy).toHaveBeenCalledWith(error, { operation: 'test' })
    })
  })
})
