import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import ExpressionCard from '@/components/idiomatic-expressions/ExpressionCard.vue'
import { createTestingPinia } from '@pinia/testing'

// Mock stores
vi.mock('@/stores/modules/expressionStore', () => ({
  useExpressionStore: vi.fn(),
}))

vi.mock('@/stores/modules/learningStore', () => ({
  useLearningStore: vi.fn(),
}))

// Mock Element Plus message
global.ElMessage = {
  success: vi.fn(),
  error: vi.fn(),
}

// Mock speech synthesis API
Object.defineProperty(window, 'speechSynthesis', {
  writable: true,
  value: {
    speak: vi.fn(),
    cancel: vi.fn(),
  },
})

global.SpeechSynthesisUtterance = vi.fn()

describe('ExpressionCard', () => {
  let wrapper

  // Mock expression data
  const mockExpression = {
    id: 1,
    expression: 'break the ice',
    meaning: '打破沉默，缓解尴尬气氛',
    pronunciation: '/breɪk ði aɪs/',
    difficulty_level: 'intermediate',
    formality_level: 'informal',
    usage_frequency: 'high',
  }

  const mockUserProgress = {
    id: 1,
    mastery_level: 65,
    is_favorite: false,
  }

  beforeEach(async () => {
    // Mock store returns
    const { useExpressionStore } = await import('@/stores/modules/expressionStore')
    const { useLearningStore } = await import('@/stores/modules/learningStore')
    
    useExpressionStore.mockReturnValue({
      updateMasteryLevel: vi.fn().mockResolvedValue({}),
      markAsFavorite: vi.fn().mockResolvedValue({}),
    })

    useLearningStore.mockReturnValue({
      updateSessionProgress: vi.fn(),
    })

    vi.clearAllMocks()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  describe('基础渲染', () => {
    it('应该正确渲染表达式卡片', () => {
      wrapper = mount(ExpressionCard, {
        global: {
          plugins: [createTestingPinia({ createSpy: vi.fn })],
          stubs: {
            'el-button': { template: '<button><slot /></button>' },
            'el-icon': { template: '<span><slot /></span>' },
            'el-progress': { template: '<div class="progress"></div>' },
            'el-button-group': { template: '<div><slot /></div>' },
          },
        },
        props: {
          expression: mockExpression,
          userProgress: mockUserProgress,
        },
      })

      expect(wrapper.find('.expression-card').exists()).toBe(true)
      expect(wrapper.find('.card-inner').exists()).toBe(true)
    })

    it('应该显示表达式文本', () => {
      wrapper = mount(ExpressionCard, {
        global: {
          plugins: [createTestingPinia({ createSpy: vi.fn })],
          stubs: {
            'el-button': { template: '<button><slot /></button>' },
            'el-icon': { template: '<span><slot /></span>' },
            'el-progress': { template: '<div class="progress"></div>' },
            'el-button-group': { template: '<div><slot /></div>' },
          },
        },
        props: {
          expression: mockExpression,
        },
      })

      const expressionText = wrapper.find('.expression-text')
      expect(expressionText.exists()).toBe(true)
      expect(expressionText.text()).toBe('break the ice')
    })

    it('应该显示难度标识', () => {
      wrapper = mount(ExpressionCard, {
        global: {
          plugins: [createTestingPinia({ createSpy: vi.fn })],
          stubs: {
            'el-button': { template: '<button><slot /></button>' },
            'el-icon': { template: '<span><slot /></span>' },
            'el-progress': { template: '<div class="progress"></div>' },
            'el-button-group': { template: '<div><slot /></div>' },
          },
        },
        props: {
          expression: mockExpression,
        },
      })

      const difficultyBadge = wrapper.find('.difficulty-badge')
      expect(difficultyBadge.exists()).toBe(true)
      expect(difficultyBadge.text()).toBe('中级')
    })
  })

  describe('卡片翻转功能', () => {
    it('初始状态应该显示正面', () => {
      wrapper = mount(ExpressionCard, {
        global: {
          plugins: [createTestingPinia({ createSpy: vi.fn })],
          stubs: {
            'el-button': { template: '<button><slot /></button>' },
            'el-icon': { template: '<span><slot /></span>' },
            'el-progress': { template: '<div class="progress"></div>' },
            'el-button-group': { template: '<div><slot /></div>' },
          },
        },
        props: {
          expression: mockExpression,
        },
      })

      expect(wrapper.vm.isFlipped).toBe(false)
      expect(wrapper.classes()).not.toContain('is-flipped')
    })

    it('点击卡片应该翻转', async () => {
      wrapper = mount(ExpressionCard, {
        global: {
          plugins: [createTestingPinia({ createSpy: vi.fn })],
          stubs: {
            'el-button': { template: '<button><slot /></button>' },
            'el-icon': { template: '<span><slot /></span>' },
            'el-progress': { template: '<div class="progress"></div>' },
            'el-button-group': { template: '<div><slot /></div>' },
          },
        },
        props: {
          expression: mockExpression,
        },
      })

      const cardFront = wrapper.find('.card-front')
      await cardFront.trigger('click')
      
      expect(wrapper.vm.isFlipped).toBe(true)
      expect(wrapper.classes()).toContain('is-flipped')
    })
  })

  describe('工具函数', () => {
    it('应该正确转换难度级别文本', () => {
      wrapper = mount(ExpressionCard, {
        global: {
          plugins: [createTestingPinia({ createSpy: vi.fn })],
          stubs: {
            'el-button': { template: '<button><slot /></button>' },
            'el-icon': { template: '<span><slot /></span>' },
            'el-progress': { template: '<div class="progress"></div>' },
            'el-button-group': { template: '<div><slot /></div>' },
          },
        },
        props: {
          expression: mockExpression,
        },
      })

      expect(wrapper.vm.getDifficultyText('beginner')).toBe('初级')
      expect(wrapper.vm.getDifficultyText('intermediate')).toBe('中级')
      expect(wrapper.vm.getDifficultyText('advanced')).toBe('高级')
    })

    it('应该正确转换正式程度文本', () => {
      wrapper = mount(ExpressionCard, {
        global: {
          plugins: [createTestingPinia({ createSpy: vi.fn })],
          stubs: {
            'el-button': { template: '<button><slot /></button>' },
            'el-icon': { template: '<span><slot /></span>' },
            'el-progress': { template: '<div class="progress"></div>' },
            'el-button-group': { template: '<div><slot /></div>' },
          },
        },
        props: {
          expression: mockExpression,
        },
      })

      expect(wrapper.vm.getFormalityText('informal')).toBe('非正式')
      expect(wrapper.vm.getFormalityText('neutral')).toBe('中性')
      expect(wrapper.vm.getFormalityText('formal')).toBe('正式')
    })

    it('应该计算频率级别', () => {
      wrapper = mount(ExpressionCard, {
        global: {
          plugins: [createTestingPinia({ createSpy: vi.fn })],
          stubs: {
            'el-button': { template: '<button><slot /></button>' },
            'el-icon': { template: '<span><slot /></span>' },
            'el-progress': { template: '<div class="progress"></div>' },
            'el-button-group': { template: '<div><slot /></div>' },
          },
        },
        props: {
          expression: mockExpression,
        },
      })

      expect(wrapper.vm.getFrequencyLevel('high')).toBe(3)
      expect(wrapper.vm.getFrequencyLevel('medium')).toBe(2)
      expect(wrapper.vm.getFrequencyLevel('low')).toBe(1)
    })
  })
})
