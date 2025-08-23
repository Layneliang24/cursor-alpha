import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'
import Dashboard from '../Dashboard.vue'

// Mock API模块
vi.mock('@/api/english', () => ({
  englishAPI: {
    getLearningStats: vi.fn(),
    getDueReviews: vi.fn(),
    getLearningOverview: vi.fn(),
    getLearningPlans: vi.fn(),
    getPracticeRecords: vi.fn()
  }
}))

// Mock stores
const mockEnglishStore = {
  todayProgress: {
    wordsLearned: 15,
    wordsReviewed: 8,
    practiceCount: 5,
    studyTime: 45,
    accuracyRate: 85
  },
  dueReviewsCount: 12,
  practiceStatistics: {
    correctRate: 78
  },
  activePlan: {
    id: 1,
    name: '每日学习计划',
    daily_word_target: 20
  },
  learningOverview: {
    daily_data: [
      { date: '2024-01-15', words_learned: 15, words_reviewed: 8 },
      { date: '2024-01-14', words_learned: 12, words_reviewed: 10 }
    ],
    total_stats: {
      study_time_minutes: 120
    },
    mastery_stats: {
      mastered_words: 150,
      learning_words: 45
    }
  },
  overviewLoading: false,
  dueReviews: [
    {
      id: 1,
      word: { word: 'apple', phonetic: '/ˈæpəl/' },
      mastery_level: 0.7
    },
    {
      id: 2,
      word: { word: 'banana', phonetic: '/bəˈnɑːnə/' },
      mastery_level: 0.3
    }
  ],
  fetchLearningStats: vi.fn(),
  fetchDueReviews: vi.fn(),
  fetchLearningOverview: vi.fn(),
  fetchLearningPlans: vi.fn(),
  fetchPracticeRecords: vi.fn()
}

vi.mock('@/stores/english', () => ({
  useEnglishStore: () => mockEnglishStore
}))

// Mock 子组件
const mockLearningChart = {
  template: '<div class="learning-chart"><slot /></div>',
  props: ['data']
}

const mockPlanDialog = {
  template: '<div class="plan-dialog"><slot /></div>',
  props: ['modelValue'],
  emits: ['update:modelValue', 'created']
}

const mockBatchReviewDialog = {
  template: '<div class="batch-review-dialog"><slot /></div>',
  props: ['modelValue', 'words'],
  emits: ['update:modelValue', 'completed']
}

// Mock Element Plus组件
const mockElButton = {
  template: '<button :type="type" :loading="loading" :disabled="disabled" @click="$emit(\'click\')"><slot /></button>',
  props: ['type', 'loading', 'disabled'],
  emits: ['click']
}

const mockElIcon = {
  template: '<span class="el-icon"><slot /></span>'
}

const mockElRow = {
  template: '<div class="el-row" :gutter="gutter"><slot /></div>',
  props: ['gutter']
}

const mockElCol = {
  template: '<div class="el-col" :span="span"><slot /></div>',
  props: ['span']
}

const mockElCard = {
  template: '<div class="el-card" v-loading="loading"><slot /></div>',
  props: ['loading'],
  slots: {
    header: { template: '<div class="card-header"><slot /></div>' }
  }
}

const mockElSelect = {
  template: '<select :value="modelValue" @change="$emit(\'update:modelValue\', $event.target.value)"><slot /></select>',
  props: ['modelValue', 'size'],
  emits: ['update:modelValue', 'change']
}

const mockElOption = {
  template: '<option :value="value" :label="label">{{ label }}</option>',
  props: ['value', 'label']
}

const mockElTag = {
  template: '<span class="el-tag" :type="type" :size="size"><slot /></span>',
  props: ['type', 'size']
}

const mockElProgress = {
  template: '<div class="el-progress" :percentage="percentage" :stroke-width="strokeWidth" :color="color"></div>',
  props: ['percentage', 'stroke-width', 'color']
}

// Mock 路由
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/english/practice', component: { template: '<div>Practice</div>' } },
    { path: '/english/words', component: { template: '<div>Words</div>' } },
    { path: '/english/news', component: { template: '<div>News</div>' } }
  ]
})

// Mock router.push
router.push = vi.fn()

// Mock Pinia
const pinia = createPinia()

// Mock ElMessage
const mockElMessage = {
  success: vi.fn(),
  error: vi.fn()
}

vi.mock('element-plus', async () => {
  const actual = await vi.importActual('element-plus')
  return {
    ...actual,
    ElMessage: mockElMessage
  }
})

describe('Dashboard.vue Component', () => {
  let wrapper: any

  beforeEach(async () => {
    setActivePinia(pinia)
    
    // 重置所有mock
    vi.clearAllMocks()
    
    // 重置store数据
    mockEnglishStore.todayProgress = {
      wordsLearned: 15,
      wordsReviewed: 8,
      practiceCount: 5,
      studyTime: 45,
      accuracyRate: 85
    }
    mockEnglishStore.dueReviewsCount = 12
    mockEnglishStore.practiceStatistics = { correctRate: 78 }
    mockEnglishStore.activePlan = {
      id: 1,
      name: '每日学习计划',
      daily_word_target: 20
    }
    mockEnglishStore.overviewLoading = false

    wrapper = mount(Dashboard, {
      global: {
        plugins: [router],
        stubs: {
          'LearningChart': mockLearningChart,
          'PlanDialog': mockPlanDialog,
          'BatchReviewDialog': mockBatchReviewDialog,
          'el-button': mockElButton,
          'el-icon': mockElIcon,
          'el-row': mockElRow,
          'el-col': mockElCol,
          'el-card': mockElCard,
          'el-select': mockElSelect,
          'el-option': mockElOption,
          'el-tag': mockElTag,
          'el-progress': mockElProgress
        }
      }
    })
    
    await router.isReady()
    await wrapper.vm.$nextTick()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('基础渲染', () => {
    it('正确渲染仪表板容器', () => {
      expect(wrapper.find('.english-dashboard').exists()).toBe(true)
    })

    it('显示页面标题', () => {
      expect(wrapper.text()).toContain('英语学习仪表板')
    })

    it('显示刷新按钮', () => {
      expect(wrapper.text()).toContain('刷新数据')
    })
  })

  describe('概览卡片', () => {
    it('显示今日学习单词数量', () => {
      expect(wrapper.text()).toContain('15')
      expect(wrapper.text()).toContain('今日学习单词')
    })

    it('显示待复习单词数量', () => {
      expect(wrapper.text()).toContain('12')
      expect(wrapper.text()).toContain('待复习单词')
    })

    it('显示练习正确率', () => {
      expect(wrapper.text()).toContain('78%')
      expect(wrapper.text()).toContain('练习正确率')
    })

    it('显示今日学习时长', () => {
      expect(wrapper.text()).toContain('45')
      expect(wrapper.text()).toContain('今日学习时长(分钟)')
    })
  })

  describe('学习进度图表', () => {
    it('显示图表容器', () => {
      const chartCard = wrapper.find('.chart-card')
      expect(chartCard.exists()).toBe(true)
    })

    it('显示图表标题', () => {
      expect(wrapper.text()).toContain('学习进度趋势')
    })

    it('显示时间选择器', () => {
      const select = wrapper.findComponent(mockElSelect)
      expect(select.exists()).toBe(true)
    })

    it('显示LearningChart组件', () => {
      const chart = wrapper.findComponent(mockLearningChart)
      expect(chart.exists()).toBe(true)
    })
  })

  describe('待复习单词列表', () => {
    it('显示复习卡片标题', () => {
      expect(wrapper.text()).toContain('待复习单词 (2)')
    })

    it('显示开始复习按钮', () => {
      expect(wrapper.text()).toContain('开始复习')
    })

    it('显示单词信息', () => {
      expect(wrapper.text()).toContain('apple')
      expect(wrapper.text()).toContain('banana')
    })

    it('显示音标信息', () => {
      expect(wrapper.text()).toContain('/ˈæpəl/')
      expect(wrapper.text()).toContain('/bəˈnɑːnə/')
    })

    it('显示掌握度标签', () => {
      const tags = wrapper.findAllComponents(mockElTag)
      expect(tags.length).toBeGreaterThan(0)
    })
  })

  describe('快速操作', () => {
    it('显示快速操作标题', () => {
      expect(wrapper.text()).toContain('快速操作')
    })

    it('显示开始练习按钮', () => {
      expect(wrapper.text()).toContain('开始练习')
    })

    it('显示单词学习按钮', () => {
      expect(wrapper.text()).toContain('单词学习')
    })

    it('显示新闻阅读按钮', () => {
      expect(wrapper.text()).toContain('新闻阅读')
    })

    it('显示学习计划按钮', () => {
      expect(wrapper.text()).toContain('学习计划')
    })
  })

  describe('今日任务', () => {
    it('显示今日任务标题', () => {
      expect(wrapper.text()).toContain('今日任务')
    })

    it('显示学习新单词任务', () => {
      expect(wrapper.text()).toContain('学习新单词')
      expect(wrapper.text()).toContain('15 / 20')
    })

    it('显示复习单词任务', () => {
      expect(wrapper.text()).toContain('复习单词')
      expect(wrapper.text()).toContain('8 / 12')
    })

    it('显示练习次数任务', () => {
      expect(wrapper.text()).toContain('练习次数')
      expect(wrapper.text()).toContain('5 / 10')
    })

    it('显示进度条', () => {
      const progressBars = wrapper.findAllComponents(mockElProgress)
      expect(progressBars.length).toBe(3)
    })
  })

  describe('学习统计', () => {
    it('显示学习统计标题', () => {
      expect(wrapper.text()).toContain('学习统计')
    })

    it('显示总学习时长', () => {
      expect(wrapper.text()).toContain('总学习时长')
      expect(wrapper.text()).toContain('120 分钟')
    })

    it('显示已掌握单词', () => {
      expect(wrapper.text()).toContain('已掌握单词')
      expect(wrapper.text()).toContain('150 个')
    })

    it('显示学习中单词', () => {
      expect(wrapper.text()).toContain('学习中单词')
      expect(wrapper.text()).toContain('45 个')
    })

    it('显示平均正确率', () => {
      expect(wrapper.text()).toContain('平均正确率')
      expect(wrapper.text()).toContain('85%')
    })
  })

  describe('交互功能', () => {
    it('刷新数据功能正确调用', async () => {
      const refreshButton = wrapper.findAll('button').find(button => button.text().includes('刷新数据'))
      await refreshButton.trigger('click')
      
      expect(mockEnglishStore.fetchLearningStats).toHaveBeenCalled()
      expect(mockEnglishStore.fetchDueReviews).toHaveBeenCalled()
      expect(mockEnglishStore.fetchLearningOverview).toHaveBeenCalled()
      expect(mockEnglishStore.fetchLearningPlans).toHaveBeenCalled()
      expect(mockEnglishStore.fetchPracticeRecords).toHaveBeenCalled()
    })

    it('开始复习功能正确调用', async () => {
      const reviewButton = wrapper.findAll('button').find(button => button.text().includes('开始复习'))
      await reviewButton.trigger('click')
      
      expect(wrapper.vm.showReviewDialog).toBe(true)
    })

    it('开始练习路由跳转', async () => {
      await wrapper.vm.goToPractice()
      
      expect(router.push).toHaveBeenCalledWith('/english/practice')
    })

    it('单词学习路由跳转', async () => {
      await wrapper.vm.goToWords()
      
      expect(router.push).toHaveBeenCalledWith('/english/words')
    })

    it('新闻阅读路由跳转', async () => {
      await wrapper.vm.goToNews()
      
      expect(router.push).toHaveBeenCalledWith('/english/news')
    })
  })

  describe('工具函数', () => {
    it('掌握度类型计算正确', () => {
      // 高掌握度
      expect(wrapper.vm.getProgressType(0.9)).toBe('success')
      
      // 中等掌握度
      expect(wrapper.vm.getProgressType(0.6)).toBe('warning')
      
      // 低掌握度
      expect(wrapper.vm.getProgressType(0.3)).toBe('danger')
    })
  })

  describe('生命周期', () => {
    it('组件挂载时调用数据刷新', () => {
      expect(mockEnglishStore.fetchLearningStats).toHaveBeenCalled()
      expect(mockEnglishStore.fetchDueReviews).toHaveBeenCalled()
      expect(mockEnglishStore.fetchLearningOverview).toHaveBeenCalled()
      expect(mockEnglishStore.fetchLearningPlans).toHaveBeenCalled()
      expect(mockEnglishStore.fetchPracticeRecords).toHaveBeenCalled()
    })
  })

  describe('错误处理', () => {
    it('数据刷新失败时显示错误消息', async () => {
      mockEnglishStore.fetchLearningStats.mockRejectedValue(new Error('API Error'))
      
      await wrapper.vm.refreshAllData()
      
      expect(mockElMessage.error).toHaveBeenCalledWith('数据刷新失败')
    })

    it('数据刷新成功时显示成功消息', async () => {
      await wrapper.vm.refreshAllData()
      
      expect(mockElMessage.success).toHaveBeenCalledWith('数据刷新成功')
    })
  })

  describe('对话框功能', () => {
    it('学习计划对话框显示', async () => {
      const planButton = wrapper.findAll('button').find(button => button.text().includes('学习计划'))
      await planButton.trigger('click')
      
      expect(wrapper.vm.showPlanDialog).toBe(true)
    })

    it('计划创建成功处理', async () => {
      await wrapper.vm.onPlanCreated()
      
      expect(mockEnglishStore.fetchLearningPlans).toHaveBeenCalled()
      expect(mockElMessage.success).toHaveBeenCalledWith('学习计划创建成功')
    })

    it('复习完成处理', async () => {
      await wrapper.vm.onReviewCompleted()
      
      expect(mockElMessage.success).toHaveBeenCalledWith('复习完成，进度已更新')
    })
  })

  describe('响应式布局', () => {
    it('概览卡片有正确的布局', () => {
      const overviewCards = wrapper.find('.overview-cards')
      expect(overviewCards.exists()).toBe(true)
    })

    it('主内容区域有正确的布局', () => {
      const mainContent = wrapper.find('.main-content')
      expect(mainContent.exists()).toBe(true)
    })

    it('左侧内容区域占16列', () => {
      const leftCol = wrapper.findAllComponents(mockElCol)[4] // 概览卡片后是主内容
      expect(leftCol.props('span')).toBe(16)
    })

    it('右侧内容区域占8列', () => {
      const rightCol = wrapper.findAllComponents(mockElCol)[5]
      expect(rightCol.props('span')).toBe(8)
    })
  })

  describe('加载状态', () => {
    it('图表加载状态正确显示', async () => {
      mockEnglishStore.overviewLoading = true
      
      await wrapper.vm.$nextTick()
      
      const chartCard = wrapper.find('.chart-card')
      expect(chartCard.props('loading')).toBe(true)
    })
  })

  describe('边界情况', () => {
    it('无待复习单词时不显示复习卡片', async () => {
      mockEnglishStore.dueReviews = []
      
      await wrapper.vm.$nextTick()
      
      expect(wrapper.text()).not.toContain('待复习单词')
    })

    it('无学习计划时不显示今日任务', async () => {
      mockEnglishStore.activePlan = null
      
      await wrapper.vm.$nextTick()
      
      expect(wrapper.text()).not.toContain('今日任务')
    })

    it('待复习单词超过5个时显示更多提示', () => {
      expect(wrapper.text()).toContain('还有 0 个单词待复习...')
    })
  })
}) 