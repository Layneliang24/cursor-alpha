import { vi } from 'vitest'
import { defineComponent } from 'vue'

// Mock element-plus 的部分 API
vi.mock('element-plus', async () => {
  return {
    ElMessage: {
      success: vi.fn(),
      error: vi.fn(),
      warning: vi.fn(),
      info: vi.fn()
    },
    // 基础图标占位，避免 Unknown component
    ElIcon: defineComponent({ name: 'ElIcon', template: '<i><slot /></i>' }),
  }
})

// Mock @popperjs/core 的 CJS 导出差异
vi.mock('@popperjs/core', async () => {
  const placements = ['top', 'bottom', 'left', 'right']
  return {
    default: { placements },
    placements,
  }
})

// Mock 浏览器API，解决jsdom兼容性问题
Object.defineProperty(window, 'scrollTo', {
  value: vi.fn(),
  writable: true
})

// Mock HTMLMediaElement.prototype.play
Object.defineProperty(HTMLMediaElement.prototype, 'play', {
  value: vi.fn().mockResolvedValue(undefined),
  writable: true
})

// Mock Audio构造函数
global.Audio = vi.fn().mockImplementation(() => ({
  play: vi.fn().mockResolvedValue(undefined),
  pause: vi.fn(),
  currentTime: 0,
  duration: 0,
  volume: 1,
  muted: false,
  addEventListener: vi.fn(),
  removeEventListener: vi.fn()
}))

// Mock fetch API
global.fetch = vi.fn()

// Mock ResizeObserver
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn()
}))

// Mock IntersectionObserver
global.IntersectionObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn()
}))

// Mock matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})

// 如需在单测中自定义路由行为，请在各自测试文件内按需 mock 'vue-router'

// 注意：不在此处全局 mock '@/stores/auth'，以免影响针对 store 的单元测试

// Mock 静态资源导入
vi.mock('@/assets/*', () => ({ default: '' }))
