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

// 如需在单测中自定义路由行为，请在各自测试文件内按需 mock 'vue-router'

// 注意：不在此处全局 mock '@/stores/auth'，以免影响针对 store 的单元测试

// Mock 静态资源导入
vi.mock('@/assets/*', () => ({ default: '' }))
