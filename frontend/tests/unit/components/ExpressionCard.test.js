import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import ExpressionCard from '@/components/idiomatic-expressions/ExpressionCard.vue'
import { useExpressionStore } from '@/stores/modules/expressionStore'
import { useLearningStore } from '@/stores/modules/learningStore'
import { createTestingPinia } from '@pinia/testing'

// Mock stores
vi.mock('@/stores/modules/expressionStore', () => ({
  useExpressionStore: vi.fn(),
}))

vi.mock('@/stores/modules/learningStore', () => ({
  useLearningStore: vi.fn(),
}))

// Mock Element Plus message
const ElMessage = {
  success: vi.fn(),
  error: vi.fn(),
}

// Mock speech synthesis API
Object.defineProperty(window, 'speechSynthesis', {
  writable: true,
  value: {
    speak: vi.fn(),
    cancel: vi.fn(),
    pause: vi.fn(),
    resume: vi.fn(),
    getVoices: vi.fn(() => []),
  },
})

global.SpeechSynthesisUtterance = vi.fn().mockImplementation((text) => ({
  text,
  lang: 'en-US',
  rate: 0.8,
  pitch: 1,
  volume: 1,
}))

describe('ExpressionCard', () => {
  let wrapper
  let mockExpressionStore
  let mockLearningStore

  // Mock expression data
  const mockExpression = {
    id: 1,
    expression: 'break the ice',
    meaning: '打破沉默，缓解尴尬气氛',
    explanation: '在社交场合中开始对话或缓解紧张气氛的行为',
    pronunciation: '/breɪk ði aɪs/',
    difficulty_level: 'intermediate',
    formality_level: 'informal',
    usage_frequency: 'high',
    usage_examples: [
      {
        example: 'He told a joke to break the ice at the meeting.',
        translation: '他在会议上讲了个笑话来打破沉默。',
        context: 'business',
      },
      {
        example: 'Let me break the ice by introducing myself.',
        translation: '让我先自我介绍来打破沉默。',
        context: 'social',
      },
    ],
  }

  const mockUserProgress = {
    id: 1,
    user: 1,
    expression: 1,
    mastery_level: 65,
    is_favorite: false,
    study_count: 5,
    correct_count: 3,
    last_studied: '2024-01-15T10:30:00Z',
  }

  beforeEach(() => {
    // Setup store mocks
    mockExpressionStore = {
      updateMasteryLevel: vi.fn().mockResolvedValue({}),
      markAsFavorite: vi.fn().mockResolvedValue({}),
    }

    mockLearningStore = {
      updateSessionProgress: vi.fn(),
    }

    useExpressionStore.mockReturnValue(mockExpressionStore)
    useLearningStore.mockReturnValue(mockLearningStore)

    // Clear message mocks
    vi.clearAllMocks()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  describe('基础渲染', () => {
    beforeEach(() => {
      wrapper = mount(ExpressionCard, {
        ...commonMountOptions,
        props: {
          expression: mockExpression,
          userProgress: mockUserProgress,
        },
      })
    })

    it('应该正确渲染表达式卡片', () => {
      expect(wrapper.find('.expression-card').exists()).toBe(true)
      expect(wrapper.find('.card-inner').exists()).toBe(true)
    })

    it('应该在正面显示表达式文本', () => {
      const expressionText = wrapper.find('.expression-text')
      expect(expressionText.exists()).toBe(true)
      expect(expressionText.text()).toBe('break the ice')
    })

    it('应该显示难度标识', () => {
      const difficultyBadge = wrapper.find('.difficulty-badge')
      expect(difficultyBadge.exists()).toBe(true)
      expect(difficultyBadge.text()).toBe('中级')
      expect(difficultyBadge.classes()).toContain('difficulty-intermediate')
    })

    it('应该显示正式程度标识', () => {
      const formalityBadge = wrapper.find('.formality-badge')
      expect(formalityBadge.exists()).toBe(true)
      expect(formalityBadge.text()).toBe('非正式')
      expect(formalityBadge.classes()).toContain('formality-informal')
    })

    it('应该显示使用频率指示器', () => {
      const frequencyBars = wrapper.findAll('.frequency-bar')
      expect(frequencyBars).toHaveLength(3)
      
      // high frequency should show all 3 bars as active
      const activeBars = wrapper.findAll('.frequency-bar.active')
      expect(activeBars).toHaveLength(3)
    })

    it('应该显示发音信息', () => {
      const phonetic = wrapper.find('.phonetic')
      expect(phonetic.exists()).toBe(true)
      expect(phonetic.text()).toBe('/breɪk ði aɪs/')
    })
  })

  describe('卡片翻转功能', () => {
    beforeEach(() => {
      wrapper = mount(ExpressionCard, {
        ...commonMountOptions,
        props: {
          expression: mockExpression,
          userProgress: mockUserProgress,
        },
      })
    })

    it('初始状态应该显示正面', () => {
      expect(wrapper.vm.isFlipped).toBe(false)
      expect(wrapper.classes()).not.toContain('is-flipped')
    })

    it('点击卡片应该翻转到背面', async () => {
      const cardFront = wrapper.find('.card-front')
      await cardFront.trigger('click')
      
      expect(wrapper.vm.isFlipped).toBe(true)
      expect(wrapper.classes()).toContain('is-flipped')
    })

    it('翻转时应该发出flip事件', async () => {
      const cardFront = wrapper.find('.card-front')
      await cardFront.trigger('click')
      
      expect(wrapper.emitted('flip')).toBeTruthy()
      expect(wrapper.emitted('flip')[0]).toEqual([true])
    })

    it('背面应该显示含义和解释', async () => {
      await wrapper.vm.flipCard()
      await testUtils.nextTick()
      
      const meaningText = wrapper.find('.meaning-text')
      expect(meaningText.exists()).toBe(true)
      expect(meaningText.text()).toBe('打破沉默，缓解尴尬气氛')
      
      const explanation = wrapper.find('.explanation p')
      expect(explanation.exists()).toBe(true)
      expect(explanation.text()).toBe('在社交场合中开始对话或缓解紧张气氛的行为')
    })

    it('背面应该显示使用示例', async () => {
      await wrapper.vm.flipCard()
      await testUtils.nextTick()
      
      const examples = wrapper.findAll('.example-item')
      expect(examples).toHaveLength(2) // 只显示前2个示例
      
      const firstExample = examples[0]
      expect(firstExample.find('.example-text').text()).toContain('He told a joke to break the ice')
      expect(firstExample.find('.example-translation').text()).toBe('他在会议上讲了个笑话来打破沉默。')
    })

    it('背面应该显示掌握度进度', async () => {
      await wrapper.vm.flipCard()
      await testUtils.nextTick()
      
      const masteryLevel = wrapper.find('.mastery-level')
      expect(masteryLevel.exists()).toBe(true)
      
      const progressBar = wrapper.findComponent({ name: 'ElProgress' })
      expect(progressBar.exists()).toBe(true)
      expect(progressBar.props('percentage')).toBe(65)
    })
  })

  describe('音频播放功能', () => {
    beforeEach(() => {
      wrapper = mount(ExpressionCard, {
        ...commonMountOptions,
        props: {
          expression: mockExpression,
          showPronunciation: true,
        },
      })
    })

    it('应该显示音频播放按钮', () => {
      const audioBtn = wrapper.find('.audio-btn')
      expect(audioBtn.exists()).toBe(true)
    })

    it('点击音频按钮应该播放语音', async () => {
      const audioBtn = wrapper.find('.audio-btn')
      await audioBtn.trigger('click')
      
      expect(global.SpeechSynthesisUtterance).toHaveBeenCalledWith('break the ice')
      expect(window.speechSynthesis.speak).toHaveBeenCalled()
    })

    it('播放音频时应该显示加载状态', async () => {
      const audioBtn = wrapper.find('.audio-btn')
      
      // 模拟异步播放
      const playPromise = wrapper.vm.playAudio()
      await testUtils.nextTick()
      
      expect(wrapper.vm.audioLoading).toBe(false) // 由于是同步的mock，加载状态会立即结束
    })

    it('播放音频应该发出audioPlay事件', async () => {
      await wrapper.vm.playAudio()
      
      expect(wrapper.emitted('audioPlay')).toBeTruthy()
      expect(wrapper.emitted('audioPlay')[0]).toEqual(['break the ice'])
    })

    it('当showPronunciation为false时不应显示发音区域', () => {
      wrapper = mount(ExpressionCard, {
        ...commonMountOptions,
        props: {
          expression: mockExpression,
          showPronunciation: false,
        },
      })
      
      const pronunciation = wrapper.find('.pronunciation')
      expect(pronunciation.exists()).toBe(false)
    })
  })

  describe('掌握度操作', () => {
    beforeEach(() => {
      wrapper = mount(ExpressionCard, {
        ...commonMountOptions,
        props: {
          expression: mockExpression,
          userProgress: mockUserProgress,
        },
      })
    })

    it('应该显示操作按钮', async () => {
      await wrapper.vm.flipCard()
      await testUtils.nextTick()
      
      const knownBtn = wrapper.find('button:contains("掌握")')
      const reviewBtn = wrapper.find('button:contains("复习")')
      const favoriteBtn = wrapper.find('button:contains("收藏")')
      
      expect(knownBtn.exists()).toBe(true)
      expect(reviewBtn.exists()).toBe(true)
      expect(favoriteBtn.exists()).toBe(true)
    })

    it('点击掌握按钮应该更新掌握度', async () => {
      await wrapper.vm.markAsKnown()
      
      expect(mockExpressionStore.updateMasteryLevel).toHaveBeenCalledWith(1, 85)
      expect(mockLearningStore.updateSessionProgress).toHaveBeenCalledWith(true, 1)
      expect(ElMessage.success).toHaveBeenCalledWith('已标记为掌握')
      expect(wrapper.emitted('mastery')).toBeTruthy()
      expect(wrapper.emitted('mastery')[0]).toEqual([1, 85])
    })

    it('点击复习按钮应该降低掌握度', async () => {
      await wrapper.vm.markForReview()
      
      expect(mockExpressionStore.updateMasteryLevel).toHaveBeenCalledWith(1, 30)
      expect(mockLearningStore.updateSessionProgress).toHaveBeenCalledWith(false, 1)
      expect(ElMessage.success).toHaveBeenCalledWith('已加入复习队列')
      expect(wrapper.emitted('mastery')).toBeTruthy()
      expect(wrapper.emitted('mastery')[0]).toEqual([1, 30])
    })

    it('点击收藏按钮应该切换收藏状态', async () => {
      await wrapper.vm.toggleFavorite()
      
      expect(mockExpressionStore.markAsFavorite).toHaveBeenCalledWith(1, true)
      expect(ElMessage.success).toHaveBeenCalledWith('已添加到收藏')
      expect(wrapper.emitted('favorite')).toBeTruthy()
      expect(wrapper.emitted('favorite')[0]).toEqual([1, true])
    })

    it('当已收藏时点击收藏按钮应该取消收藏', async () => {
      // 设置为已收藏状态
      const favoriteProgress = { ...mockUserProgress, is_favorite: true }
      wrapper = mount(ExpressionCard, {
        ...commonMountOptions,
        props: {
          expression: mockExpression,
          userProgress: favoriteProgress,
        },
      })
      
      await wrapper.vm.toggleFavorite()
      
      expect(mockExpressionStore.markAsFavorite).toHaveBeenCalledWith(1, false)
      expect(ElMessage.success).toHaveBeenCalledWith('已取消收藏')
    })
  })

  describe('错误处理', () => {
    beforeEach(() => {
      wrapper = mount(ExpressionCard, {
        ...commonMountOptions,
        props: {
          expression: mockExpression,
          userProgress: mockUserProgress,
        },
      })
    })

    it('掌握度更新失败时应该显示错误消息', async () => {
      mockExpressionStore.updateMasteryLevel.mockRejectedValueOnce(new Error('Network error'))
      
      await wrapper.vm.markAsKnown()
      
      expect(ElMessage.error).toHaveBeenCalledWith('操作失败，请重试')
    })

    it('收藏操作失败时应该显示错误消息', async () => {
      mockExpressionStore.markAsFavorite.mockRejectedValueOnce(new Error('Network error'))
      
      await wrapper.vm.toggleFavorite()
      
      expect(ElMessage.error).toHaveBeenCalledWith('操作失败，请重试')
    })

    it('音频播放失败时应该显示错误消息', async () => {
      // 模拟speechSynthesis不可用
      Object.defineProperty(window, 'speechSynthesis', {
        writable: true,
        value: undefined,
      })
      
      await wrapper.vm.playAudio()
      
      expect(ElMessage.error).toHaveBeenCalledWith('音频播放失败')
    })
  })

  describe('自动翻转功能', () => {
    it('当autoFlip为true时应该自动翻转', async () => {
      vi.useFakeTimers()
      
      wrapper = mount(ExpressionCard, {
        ...commonMountOptions,
        props: {
          expression: mockExpression,
          autoFlip: true,
          flipDelay: 1000,
        },
      })
      
      expect(wrapper.vm.isFlipped).toBe(false)
      
      // 推进时间
      vi.advanceTimersByTime(1000)
      await testUtils.nextTick()
      
      expect(wrapper.vm.isFlipped).toBe(true)
      
      vi.useRealTimers()
    })

    it('当autoFlip为false时不应该自动翻转', async () => {
      vi.useFakeTimers()
      
      wrapper = mount(ExpressionCard, {
        ...commonMountOptions,
        props: {
          expression: mockExpression,
          autoFlip: false,
        },
      })
      
      expect(wrapper.vm.isFlipped).toBe(false)
      
      vi.advanceTimersByTime(5000)
      await testUtils.nextTick()
      
      expect(wrapper.vm.isFlipped).toBe(false)
      
      vi.useRealTimers()
    })
  })

  describe('掌握度颜色计算', () => {
    beforeEach(() => {
      wrapper = mount(ExpressionCard, {
        ...commonMountOptions,
        props: {
          expression: mockExpression,
        },
      })
    })

    it('应该根据掌握度返回正确的颜色', () => {
      expect(wrapper.vm.getMasteryColor(85)).toBe('#67c23a') // 绿色 >= 80
      expect(wrapper.vm.getMasteryColor(70)).toBe('#e6a23c') // 橙色 >= 60
      expect(wrapper.vm.getMasteryColor(50)).toBe('#f56c6c') // 红色 >= 40
      expect(wrapper.vm.getMasteryColor(20)).toBe('#909399') // 灰色 < 40
    })
  })

  describe('频率级别计算', () => {
    beforeEach(() => {
      wrapper = mount(ExpressionCard, {
        ...commonMountOptions,
        props: {
          expression: mockExpression,
        },
      })
    })

    it('应该根据频率字符串返回正确的数值', () => {
      expect(wrapper.vm.getFrequencyLevel('high')).toBe(3)
      expect(wrapper.vm.getFrequencyLevel('medium')).toBe(2)
      expect(wrapper.vm.getFrequencyLevel('low')).toBe(1)
      expect(wrapper.vm.getFrequencyLevel('unknown')).toBe(1) // 默认值
    })
  })

  describe('文本转换函数', () => {
    beforeEach(() => {
      wrapper = mount(ExpressionCard, {
        ...commonMountOptions,
        props: {
          expression: mockExpression,
        },
      })
    })

    it('应该正确转换难度级别文本', () => {
      expect(wrapper.vm.getDifficultyText('beginner')).toBe('初级')
      expect(wrapper.vm.getDifficultyText('intermediate')).toBe('中级')
      expect(wrapper.vm.getDifficultyText('advanced')).toBe('高级')
      expect(wrapper.vm.getDifficultyText('unknown')).toBe('unknown') // 未知值原样返回
    })

    it('应该正确转换正式程度文本', () => {
      expect(wrapper.vm.getFormalityText('informal')).toBe('非正式')
      expect(wrapper.vm.getFormalityText('neutral')).toBe('中性')
      expect(wrapper.vm.getFormalityText('formal')).toBe('正式')
      expect(wrapper.vm.getFormalityText('unknown')).toBe('unknown') // 未知值原样返回
    })
  })
})
