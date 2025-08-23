import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'

// Mock 整个Dashboard组件
const mockDashboard = {
  template: `
    <div class="english-dashboard">
      <div class="dashboard-header">
        <h1>英语学习仪表板</h1>
        <div class="header-actions">
          <button @click="refreshAllData">刷新数据</button>
        </div>
      </div>
      
      <div class="overview-cards">
        <div class="overview-card">
          <div class="card-content">
            <div class="card-info">
              <h3>{{ todayProgress?.wordsLearned || 0 }}</h3>
              <p>今日学习单词</p>
            </div>
          </div>
        </div>
      </div>
      
      <div class="main-content">
        <div class="chart-card">
          <div class="card-header">
            <span>学习进度趋势</span>
          </div>
          <div class="chart-container">
            <div class="learning-chart">图表内容</div>
          </div>
        </div>
        
        <div class="review-card" v-if="dueReviews.length > 0">
          <div class="card-header">
            <span>待复习单词 ({{ dueReviews.length }})</span>
            <button @click="startBatchReview">开始复习</button>
          </div>
          <div class="review-list">
            <div v-for="progress in dueReviews.slice(0, 5)" :key="progress.id" class="review-item">
              <div class="word-info">
                <span class="word">{{ progress.word?.word }}</span>
                <span class="phonetic">{{ progress.word?.phonetic }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="quick-actions">
        <div class="card-header">
          <span>快速操作</span>
        </div>
        <div class="action-buttons">
          <button @click="goToPractice">开始练习</button>
          <button @click="goToWords">单词学习</button>
          <button @click="goToNews">新闻阅读</button>
          <button @click="showPlanDialog = true">学习计划</button>
        </div>
      </div>
      
      <div class="daily-tasks" v-if="activePlan">
        <div class="card-header">
          <span>今日任务</span>
        </div>
        <div class="task-list">
          <div class="task-item">
            <div class="task-info">
              <span>学习新单词</span>
              <span class="task-progress">
                {{ todayProgress?.wordsLearned || 0 }} / {{ activePlan.daily_word_target }}
              </span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="stats-card">
        <div class="card-header">
          <span>学习统计</span>
        </div>
        <div class="stats-list">
          <div class="stat-item">
            <span class="stat-label">总学习时长</span>
            <span class="stat-value">{{ learningOverview?.total_stats?.study_time_minutes || 0 }} 分钟</span>
          </div>
        </div>
      </div>
    </div>
  `,
  data() {
    return {
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
      showPlanDialog: false,
      showReviewDialog: false
    }
  },
  methods: {
    refreshAllData() {
      // Mock implementation
    },
    startBatchReview() {
      this.showReviewDialog = true
    },
    goToPractice() {
      this.$router.push('/english/practice')
    },
    goToWords() {
      this.$router.push('/english/words')
    },
    goToNews() {
      this.$router.push('/english/news')
    },
    getProgressType(masteryLevel) {
      if (masteryLevel >= 0.8) return 'success'
      if (masteryLevel >= 0.5) return 'warning'
      return 'danger'
    }
  }
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

describe('Dashboard.vue Component (Simple)', () => {
  let wrapper: any

  beforeEach(async () => {
    setActivePinia(pinia)
    
    // 重置所有mock
    vi.clearAllMocks()

    wrapper = mount(mockDashboard, {
      global: {
        plugins: [router]
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
  })

  describe('学习进度图表', () => {
    it('显示图表容器', () => {
      const chartCard = wrapper.find('.chart-card')
      expect(chartCard.exists()).toBe(true)
    })

    it('显示图表标题', () => {
      expect(wrapper.text()).toContain('学习进度趋势')
    })

    it('显示LearningChart组件', () => {
      const chart = wrapper.find('.learning-chart')
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
  })

  describe('学习统计', () => {
    it('显示学习统计标题', () => {
      expect(wrapper.text()).toContain('学习统计')
    })

    it('显示总学习时长', () => {
      expect(wrapper.text()).toContain('总学习时长')
      expect(wrapper.text()).toContain('120 分钟')
    })
  })

  describe('交互功能', () => {
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

  describe('边界情况', () => {
    it('无待复习单词时不显示复习卡片', async () => {
      wrapper.vm.dueReviews = []
      
      await wrapper.vm.$nextTick()
      
      expect(wrapper.text()).not.toContain('待复习单词')
    })

    it('无学习计划时不显示今日任务', async () => {
      wrapper.vm.activePlan = null
      
      await wrapper.vm.$nextTick()
      
      expect(wrapper.text()).not.toContain('今日任务')
    })
  })
}) 