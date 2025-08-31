import { beforeAll, afterAll, beforeEach, afterEach, vi } from 'vitest'
import { config } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'

// 全局测试配置
beforeAll(() => {
  // 基础测试配置 - 移除Element Plus以避免导入问题
  config.global.plugins = []
  config.global.components = {}
  
  // 模拟全局对象
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: vi.fn().mockImplementation(query => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: vi.fn(), // deprecated
      removeListener: vi.fn(), // deprecated
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })),
  })

  // 模拟ResizeObserver
  global.ResizeObserver = vi.fn().mockImplementation(() => ({
    observe: vi.fn(),
    unobserve: vi.fn(),
    disconnect: vi.fn(),
  }))

  // 模拟IntersectionObserver
  global.IntersectionObserver = vi.fn().mockImplementation(() => ({
    observe: vi.fn(),
    unobserve: vi.fn(),
    disconnect: vi.fn(),
  }))

  // 模拟localStorage
  const localStorageMock = {
    getItem: vi.fn(),
    setItem: vi.fn(),
    removeItem: vi.fn(),
    clear: vi.fn(),
  }
  vi.stubGlobal('localStorage', localStorageMock)

  // 模拟sessionStorage
  const sessionStorageMock = {
    getItem: vi.fn(),
    setItem: vi.fn(),
    removeItem: vi.fn(),
    clear: vi.fn(),
  }
  vi.stubGlobal('sessionStorage', sessionStorageMock)

  // 模拟fetch API
  global.fetch = vi.fn()

  // 模拟console方法以减少测试输出噪音
  vi.spyOn(console, 'warn').mockImplementation(() => {})
  vi.spyOn(console, 'error').mockImplementation(() => {})
})

// 每个测试前的设置
beforeEach(() => {
  // 重置所有mock
  vi.clearAllMocks()
  
  // 重置localStorage和sessionStorage
  localStorage.clear()
  sessionStorage.clear()
  
  // 设置默认的Pinia测试实例
  config.global.plugins.push(createTestingPinia({
    createSpy: vi.fn,
    stubActions: false,
  }))
})

// 每个测试后的清理
afterEach(() => {
  // 清理DOM
  document.body.innerHTML = ''
  
  // 清理定时器
  vi.clearAllTimers()
})

// 全局测试清理
afterAll(() => {
  // 恢复所有mock
  vi.restoreAllMocks()
})

// 测试工具函数
export const testUtils = {
  // 创建测试用的Pinia实例
  createTestPinia: (options = {}) => {
    return createTestingPinia({
      createSpy: vi.fn,
      stubActions: false,
      ...options,
    })
  },

  // 等待Vue的下一个tick
  nextTick: async () => {
    const { nextTick } = await import('vue')
    await nextTick()
  },

  // 等待指定时间
  sleep: (ms) => new Promise(resolve => setTimeout(resolve, ms)),

  // 触发DOM事件
  triggerEvent: (element, eventType, eventData = {}) => {
    const event = new Event(eventType, { bubbles: true, ...eventData })
    element.dispatchEvent(event)
  },

  // 模拟用户输入
  mockUserInput: async (input, value) => {
    input.value = value
    input.dispatchEvent(new Event('input', { bubbles: true }))
    await testUtils.nextTick()
  },

  // 模拟API响应
  mockApiResponse: (data, status = 200) => {
    global.fetch.mockResolvedValueOnce({
      ok: status >= 200 && status < 300,
      status,
      json: async () => data,
      text: async () => JSON.stringify(data),
    })
  },

  // 模拟API错误
  mockApiError: (error, status = 500) => {
    global.fetch.mockRejectedValueOnce({
      status,
      message: error,
      response: { status, statusText: error },
    })
  },

  // 获取组件的文本内容
  getTextContent: (wrapper) => {
    return wrapper.element.textContent.replace(/\s+/g, ' ').trim()
  },

  // 检查元素是否可见
  isVisible: (element) => {
    const style = window.getComputedStyle(element)
    return style.display !== 'none' && 
           style.visibility !== 'hidden' && 
           style.opacity !== '0'
  },
}

// 导出常用的测试配置
export const commonMountOptions = {
  global: {
    plugins: [ElementPlus, testUtils.createTestPinia()],
    components: config.global.components,
    stubs: {
      // 默认存根一些复杂的组件
      'router-link': true,
      'router-view': true,
      'el-icon': true,
    },
  },
}

// 导出Element Plus相关的测试工具
export const elementPlusUtils = {
  // 等待Element Plus组件渲染完成
  waitForElementPlus: async () => {
    await testUtils.nextTick()
    await testUtils.sleep(100) // Element Plus组件可能需要额外的渲染时间
  },

  // 触发Element Plus表单验证
  triggerFormValidation: async (wrapper) => {
    const form = wrapper.findComponent({ name: 'ElForm' })
    if (form.exists()) {
      await form.vm.validate()
    }
  },

  // 模拟Element Plus消息框
  mockElMessage: () => {
    const ElMessage = {
      success: vi.fn(),
      error: vi.fn(),
      warning: vi.fn(),
      info: vi.fn(),
    }
    vi.mock('element-plus', async () => {
      const actual = await vi.importActual('element-plus')
      return {
        ...actual,
        ElMessage,
      }
    })
    return ElMessage
  },
}
