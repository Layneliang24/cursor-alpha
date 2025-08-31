import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { ElMessage } from 'element-plus'
import ExpressionLearning from '../ExpressionLearning.vue'
import { useExpressionStore } from '@/stores/modules/expressionStore'
import { useLearningStore } from '@/stores/modules/learningStore'

// Mock Element Plus
vi.mock('element-plus', () => ({
  ElMessage: vi.fn(),
  ElNotification: vi.fn()
}))

// Mock stores
vi.mock('@/stores/modules/expressionStore')
vi.mock('@/stores/modules/learningStore')

describe('ExpressionLearning.vue - 边界条件测试', () => {
  let wrapper: any
  let expressionStore: any
  let learningStore: any
  let pinia: any

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)

    // Mock store implementations
    expressionStore = {
      expressions: { value: null },
      userProgress: { value: null },
      needReviewExpressions: { value: null },
      loading: { value: false },
      fetchExpressions: vi.fn().mockResolvedValue(undefined),
      fetchUserProgress: vi.fn().mockResolvedValue(undefined)
    }

    learningStore = {
      settings: {},
      initialize: vi.fn().mockResolvedValue(undefined)
    }

    // Mock the store hooks
    vi.mocked(useExpressionStore).mockReturnValue(expressionStore)
    vi.mocked(useLearningStore).mockReturnValue(learningStore)
  })

  describe('数据为空时的边界条件', () => {
    it('应该处理expressions为null的情况', async () => {
      expressionStore.expressions.value = null
      expressionStore.userProgress.value = []
      expressionStore.needReviewExpressions.value = []

      wrapper = mount(ExpressionLearning, {
        global: {
          plugins: [pinia]
        }
      })

      // 等待组件挂载
      await wrapper.vm.$nextTick()
      
      // 验证组件不会崩溃
      expect(wrapper.exists()).toBe(true)
      
      // 验证computed属性返回安全值
      expect(wrapper.vm.currentExpressions).toEqual([])
    })

    it('应该处理userProgress为null的情况', async () => {
      expressionStore.expressions.value = []
      expressionStore.userProgress.value = null
      expressionStore.needReviewExpressions.value = []

      wrapper = mount(ExpressionLearning, {
        global: {
          plugins: [pinia]
        }
      })

      await wrapper.vm.$nextTick()
      
      expect(wrapper.exists()).toBe(true)
      expect(wrapper.vm.getCurrentProgress()).toBeUndefined()
    })

    it('应该处理needReviewExpressions为null的情况', async () => {
      expressionStore.expressions.value = []
      expressionStore.userProgress.value = []
      expressionStore.needReviewExpressions.value = null

      wrapper = mount(ExpressionLearning, {
        global: {
          plugins: [pinia]
        }
      })

      await wrapper.vm.$nextTick()
      
      expect(wrapper.exists()).toBe(true)
      
      // 在复习模式下应该返回空数组
      wrapper.vm.setMode('review')
      expect(wrapper.vm.currentExpressions).toEqual([])
    })
  })

  describe('数据为undefined时的边界条件', () => {
    it('应该处理所有store数据为undefined的情况', async () => {
      expressionStore.expressions.value = undefined
      expressionStore.userProgress.value = undefined
      expressionStore.needReviewExpressions.value = undefined

      wrapper = mount(ExpressionLearning, {
        global: {
          plugins: [pinia]
        }
      })

      await wrapper.vm.$nextTick()
      
      expect(wrapper.exists()).toBe(true)
      expect(wrapper.vm.currentExpressions).toEqual([])
      expect(wrapper.vm.currentExpression).toBeNull()
    })
  })

  describe('异步加载错误处理', () => {
    it('应该处理fetchExpressions失败的情况', async () => {
      expressionStore.fetchExpressions.mockRejectedValue(new Error('API Error'))
      expressionStore.expressions.value = []
      expressionStore.userProgress.value = []
      expressionStore.needReviewExpressions.value = []

      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

      wrapper = mount(ExpressionLearning, {
        global: {
          plugins: [pinia]
        }
      })

      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 0)) // 等待异步操作

      expect(wrapper.exists()).toBe(true)
      expect(wrapper.vm.isLoaded).toBe(true) // 即使失败也应该设置为已加载
      expect(consoleSpy).toHaveBeenCalledWith('Error in onMounted:', expect.any(Error))
      
      consoleSpy.mockRestore()
    })

    it('应该处理所有异步操作都失败的情况', async () => {
      expressionStore.fetchExpressions.mockRejectedValue(new Error('Expressions Error'))
      expressionStore.fetchUserProgress.mockRejectedValue(new Error('Progress Error'))
      learningStore.initialize.mockRejectedValue(new Error('Learning Error'))

      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

      wrapper = mount(ExpressionLearning, {
        global: {
          plugins: [pinia]
        }
      })

      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 0))

      expect(wrapper.exists()).toBe(true)
      expect(wrapper.vm.isLoaded).toBe(true)
      expect(consoleSpy).toHaveBeenCalled()
      
      consoleSpy.mockRestore()
    })
  })

  describe('computed属性错误处理', () => {
    it('应该处理currentExpressions computed中的错误', async () => {
      // 创建一个会抛出错误的响应式对象
      const faultyRef = {
        get value() {
          throw new Error('Computed error')
        }
      }
      
      expressionStore.expressions = faultyRef
      expressionStore.userProgress.value = []
      expressionStore.needReviewExpressions.value = []

      const consoleWarnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})

      wrapper = mount(ExpressionLearning, {
        global: {
          plugins: [pinia]
        }
      })

      await wrapper.vm.$nextTick()
      
      expect(wrapper.exists()).toBe(true)
      expect(wrapper.vm.currentExpressions).toEqual([])
      expect(consoleWarnSpy).toHaveBeenCalledWith('Error in currentExpressions computed:', expect.any(Error))
      
      consoleWarnSpy.mockRestore()
    })

    it('应该处理currentExpression computed中的错误', async () => {
      expressionStore.expressions.value = [{ id: 1, title: 'test' }]
      expressionStore.userProgress.value = []
      expressionStore.needReviewExpressions.value = []

      const consoleWarnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})

      wrapper = mount(ExpressionLearning, {
        global: {
          plugins: [pinia]
        }
      })

      // 故意设置一个会导致错误的状态
      wrapper.vm.currentCardIndex = { 
        get value() { 
          throw new Error('Index error') 
        } 
      }

      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.currentExpression).toBeNull()
      expect(consoleWarnSpy).toHaveBeenCalledWith('Error in currentExpression computed:', expect.any(Error))
      
      consoleWarnSpy.mockRestore()
    })
  })

  describe('复习功能边界条件', () => {
    it('应该处理没有需要复习的表达式时开始复习', async () => {
      expressionStore.expressions.value = []
      expressionStore.userProgress.value = []
      expressionStore.needReviewExpressions.value = []

      wrapper = mount(ExpressionLearning, {
        global: {
          plugins: [pinia]
        }
      })

      await wrapper.vm.$nextTick()
      
      wrapper.vm.startReview()
      
      expect(ElMessage.info).toHaveBeenCalledWith('暂无需要复习的表达式')
      expect(wrapper.vm.reviewSession.active).toBe(false)
    })

    it('应该处理复习表达式列表为null时开始复习', async () => {
      expressionStore.expressions.value = []
      expressionStore.userProgress.value = []
      expressionStore.needReviewExpressions.value = null

      wrapper = mount(ExpressionLearning, {
        global: {
          plugins: [pinia]
        }
      })

      await wrapper.vm.$nextTick()
      
      wrapper.vm.startReview()
      
      expect(ElMessage.info).toHaveBeenCalledWith('暂无需要复习的表达式')
      expect(wrapper.vm.reviewSession.active).toBe(false)
    })
  })

  describe('组件加载状态', () => {
    it('应该在数据加载期间显示加载状态', async () => {
      // 让异步操作永远pending
      expressionStore.fetchExpressions.mockReturnValue(new Promise(() => {}))
      expressionStore.fetchUserProgress.mockResolvedValue(undefined)
      learningStore.initialize.mockResolvedValue(undefined)

      wrapper = mount(ExpressionLearning, {
        global: {
          plugins: [pinia]
        }
      })

      expect(wrapper.vm.isLoaded).toBe(false)
      expect(wrapper.find('.loading-container').exists()).toBe(true)
      expect(wrapper.text()).toContain('加载中')
    })

    it('应该在数据加载完成后隐藏加载状态', async () => {
      expressionStore.expressions.value = []
      expressionStore.userProgress.value = []
      expressionStore.needReviewExpressions.value = []

      wrapper = mount(ExpressionLearning, {
        global: {
          plugins: [pinia]
        }
      })

      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 0))

      expect(wrapper.vm.isLoaded).toBe(true)
      expect(wrapper.find('.loading-container').exists()).toBe(false)
    })
  })
})
