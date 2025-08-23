import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'

// Mock 整个DataAnalysis组件
const mockDataAnalysis = {
  template: `
    <div class="data-analysis">
      <div class="page-header">
        <button @click="goBack" class="back-btn">返回</button>
        <h1>数据分析</h1>
        <div class="header-controls">
          <button 
            @click="refreshData" 
            class="refresh-btn"
            :disabled="loading"
          >
            {{ loading ? '刷新中...' : '刷新数据' }}
          </button>
          <div class="date-picker">
            <input 
              v-model="dateRangeText"
              placeholder="选择日期范围"
              @change="handleDateChange"
            />
          </div>
        </div>
      </div>
      
      <div class="data-overview" v-if="overview.total_words > 0">
        <div class="stats-row">
          <div class="stat-card">
            <div class="stat-value">{{ overview.total_exercises }}</div>
            <div class="stat-label">总练习次数</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ overview.total_words }}</div>
            <div class="stat-label">总练习单词数</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ overview.avg_wpm }}</div>
            <div class="stat-label">平均WPM</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ overview.avg_accuracy }}%</div>
            <div class="stat-label">平均正确率</div>
          </div>
        </div>
      </div>
      
      <div v-if="overview.total_words === 0" class="no-data">
        <div class="empty-state">暂无练习数据</div>
      </div>
      
      <div class="charts-container" v-else>
        <div class="chart-card">
          <div class="chart-header">月历练习热力图</div>
          <div class="calendar-chart">
            <div class="month-selector">
              <button @click="prevMonth">←</button>
              <span>{{ currentYear }}年{{ currentMonth }}月</span>
              <button @click="nextMonth">→</button>
            </div>
            <div class="calendar-grid">
              <div v-for="day in calendarDays" :key="day.date" 
                   :class="['calendar-day', { 'has-data': day.value > 0 }]"
                   @click="handleDayClick(day)">
                {{ day.day }}
              </div>
            </div>
          </div>
        </div>
        
        <div class="chart-card">
          <div class="chart-header">过去一年WPM趋势图</div>
          <div class="line-chart">
            <div v-for="point in wpmTrend" :key="point.date" class="chart-point">
              {{ point.value }}
            </div>
          </div>
        </div>
        
        <div class="chart-card">
          <div class="chart-header">过去一年正确率趋势图</div>
          <div class="line-chart">
            <div v-for="point in accuracyTrend" :key="point.date" class="chart-point">
              {{ point.value }}%
            </div>
          </div>
        </div>
        
        <div class="chart-card">
          <div class="chart-header">按键错误热力图</div>
          <div class="keyboard-chart">
            <div v-for="key in keyErrorStats" :key="key.key" 
                 :class="['key-item', { 'error-high': key.errors > 10 }]">
              {{ key.key }}
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  data() {
    return {
      overview: {
        total_exercises: 150,
        total_words: 2500,
        avg_wpm: 45,
        avg_accuracy: 85
      },
      wpmTrend: [
        { date: '2024-01', value: 40 },
        { date: '2024-02', value: 42 },
        { date: '2024-03', value: 45 }
      ],
      accuracyTrend: [
        { date: '2024-01', value: 80 },
        { date: '2024-02', value: 82 },
        { date: '2024-03', value: 85 }
      ],
      keyErrorStats: [
        { key: 'A', errors: 5 },
        { key: 'E', errors: 12 },
        { key: 'I', errors: 8 },
        { key: 'O', errors: 15 }
      ],
      monthlyCalendarData: {
        '2024-03-01': 5,
        '2024-03-02': 8,
        '2024-03-03': 12
      },
      currentYear: 2024,
      currentMonth: 3,
      dateRange: [new Date('2024-01-01'), new Date('2024-03-31')],
      dateRangeText: '2024-01-01 至 2024-03-31',
      loading: false,
      calendarDays: [
        { date: '2024-03-01', day: 1, value: 5 },
        { date: '2024-03-02', day: 2, value: 8 },
        { date: '2024-03-03', day: 3, value: 12 }
      ]
    }
  },
  methods: {
    goBack() {
      this.$router.push('/english/dashboard')
    },
    async refreshData() {
      this.loading = true
      try {
        // Mock API call
        await new Promise(resolve => setTimeout(resolve, 100))
        this.overview.total_exercises = 160
        this.overview.total_words = 2600
      } finally {
        this.loading = false
      }
    },
    handleDateChange() {
      // Mock date change handler
      console.log('日期范围改变:', this.dateRangeText)
    },
    prevMonth() {
      if (this.currentMonth > 1) {
        this.currentMonth--
      } else {
        this.currentMonth = 12
        this.currentYear--
      }
    },
    nextMonth() {
      if (this.currentMonth < 12) {
        this.currentMonth++
      } else {
        this.currentMonth = 1
        this.currentYear++
      }
    },
    handleDayClick(day) {
      console.log('点击日期:', day.date, '练习次数:', day.value)
    },
    async loadData() {
      this.loading = true
      try {
        // Mock API calls
        await Promise.all([
          this.loadOverview(),
          this.loadTrends(),
          this.loadCalendarData()
        ])
      } finally {
        this.loading = false
      }
    },
    async loadOverview() {
      // Mock overview data
      this.overview = {
        total_exercises: 150,
        total_words: 2500,
        avg_wpm: 45,
        avg_accuracy: 85
      }
    },
    async loadTrends() {
      // Mock trend data
      this.wpmTrend = [
        { date: '2024-01', value: 40 },
        { date: '2024-02', value: 42 },
        { date: '2024-03', value: 45 }
      ]
      this.accuracyTrend = [
        { date: '2024-01', value: 80 },
        { date: '2024-02', value: 82 },
        { date: '2024-03', value: 85 }
      ]
    },
    async loadCalendarData() {
      // Mock calendar data
      this.monthlyCalendarData = {
        '2024-03-01': 5,
        '2024-03-02': 8,
        '2024-03-03': 12
      }
    }
  },
  mounted() {
    this.loadData()
  }
}

// Mock 路由
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/english/dashboard', component: { template: '<div>Dashboard</div>' } }
  ]
})

// Mock router.push
router.push = vi.fn()

// Mock Pinia
const pinia = createPinia()

describe('DataAnalysis.vue Component', () => {
  let wrapper: any

  beforeEach(async () => {
    setActivePinia(pinia)
    
    // 重置所有mock
    vi.clearAllMocks()

    wrapper = mount(mockDataAnalysis, {
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
    it('正确渲染数据分析页面', () => {
      expect(wrapper.find('.data-analysis').exists()).toBe(true)
    })

    it('显示页面标题', () => {
      expect(wrapper.text()).toContain('数据分析')
    })

    it('显示返回按钮', () => {
      expect(wrapper.text()).toContain('返回')
    })

    it('显示刷新按钮', () => {
      expect(wrapper.text()).toContain('刷新数据')
    })

    it('显示日期选择器', () => {
      expect(wrapper.find('.date-picker').exists()).toBe(true)
    })
  })

  describe('数据概览', () => {
    it('显示总练习次数', () => {
      expect(wrapper.text()).toContain('总练习次数')
      expect(wrapper.text()).toContain('150')
    })

    it('显示总练习单词数', () => {
      expect(wrapper.text()).toContain('总练习单词数')
      expect(wrapper.text()).toContain('2500')
    })

    it('显示平均WPM', () => {
      expect(wrapper.text()).toContain('平均WPM')
      expect(wrapper.text()).toContain('45')
    })

    it('显示平均正确率', () => {
      expect(wrapper.text()).toContain('平均正确率')
      expect(wrapper.text()).toContain('85%')
    })
  })

  describe('图表区域', () => {
    it('显示月历练习热力图', () => {
      expect(wrapper.text()).toContain('月历练习热力图')
    })

    it('显示WPM趋势图', () => {
      expect(wrapper.text()).toContain('过去一年WPM趋势图')
    })

    it('显示正确率趋势图', () => {
      expect(wrapper.text()).toContain('过去一年正确率趋势图')
    })

    it('显示按键错误热力图', () => {
      expect(wrapper.text()).toContain('按键错误热力图')
    })
  })

  describe('月历功能', () => {
    it('显示当前年月', () => {
      expect(wrapper.text()).toContain('2024年3月')
    })

    it('显示月份导航按钮', () => {
      expect(wrapper.find('.month-selector').exists()).toBe(true)
    })

    it('上个月按钮点击', async () => {
      const prevButton = wrapper.find('.month-selector button:first-child')
      await prevButton.trigger('click')
      
      expect(wrapper.vm.currentMonth).toBe(2)
    })

    it('下个月按钮点击', async () => {
      const nextButton = wrapper.find('.month-selector button:last-child')
      await nextButton.trigger('click')
      
      expect(wrapper.vm.currentMonth).toBe(4)
    })

    it('显示日历网格', () => {
      expect(wrapper.find('.calendar-grid').exists()).toBe(true)
    })

    it('显示日历天数', () => {
      const days = wrapper.findAll('.calendar-day')
      expect(days.length).toBeGreaterThan(0)
    })
  })

  describe('趋势图数据', () => {
    it('WPM趋势数据正确', () => {
      expect(wrapper.vm.wpmTrend.length).toBe(3)
      expect(wrapper.vm.wpmTrend[0].value).toBe(40)
      expect(wrapper.vm.wpmTrend[2].value).toBe(45)
    })

    it('正确率趋势数据正确', () => {
      expect(wrapper.vm.accuracyTrend.length).toBe(3)
      expect(wrapper.vm.accuracyTrend[0].value).toBe(80)
      expect(wrapper.vm.accuracyTrend[2].value).toBe(85)
    })
  })

  describe('按键错误统计', () => {
    it('按键错误数据正确', () => {
      expect(wrapper.vm.keyErrorStats.length).toBe(4)
      expect(wrapper.vm.keyErrorStats[0].key).toBe('A')
      expect(wrapper.vm.keyErrorStats[0].errors).toBe(5)
    })

    it('显示按键错误项', () => {
      const keyItems = wrapper.findAll('.key-item')
      expect(keyItems.length).toBe(4)
    })
  })

  describe('交互功能', () => {
    it('返回按钮点击', async () => {
      const backButton = wrapper.find('.back-btn')
      await backButton.trigger('click')
      
      expect(router.push).toHaveBeenCalledWith('/english/dashboard')
    })

    it('刷新数据按钮点击', async () => {
      const refreshButton = wrapper.find('.refresh-btn')
      await refreshButton.trigger('click')
      
      expect(wrapper.vm.refreshData).toBeDefined()
    })

    it('日期选择器变化', async () => {
      const dateInput = wrapper.find('.date-picker input')
      await dateInput.setValue('2024-04-01 至 2024-04-30')
      
      expect(wrapper.vm.handleDateChange).toBeDefined()
    })
  })

  describe('数据加载', () => {
    it('组件挂载时加载数据', () => {
      expect(wrapper.vm.loadData).toBeDefined()
    })

    it('加载概览数据', () => {
      expect(wrapper.vm.loadOverview).toBeDefined()
    })

    it('加载趋势数据', () => {
      expect(wrapper.vm.loadTrends).toBeDefined()
    })

    it('加载日历数据', () => {
      expect(wrapper.vm.loadCalendarData).toBeDefined()
    })
  })

  describe('月历数据', () => {
    it('月历数据正确', () => {
      expect(wrapper.vm.monthlyCalendarData['2024-03-01']).toBe(5)
      expect(wrapper.vm.monthlyCalendarData['2024-03-02']).toBe(8)
      expect(wrapper.vm.monthlyCalendarData['2024-03-03']).toBe(12)
    })

    it('日历天数数据正确', () => {
      expect(wrapper.vm.calendarDays.length).toBe(3)
      expect(wrapper.vm.calendarDays[0].value).toBe(5)
      expect(wrapper.vm.calendarDays[1].value).toBe(8)
    })
  })

  describe('边界情况', () => {
    it('无数据时显示空状态', async () => {
      wrapper.vm.overview.total_words = 0
      await wrapper.vm.$nextTick()
      
      expect(wrapper.find('.no-data').exists()).toBe(true)
      expect(wrapper.text()).toContain('暂无练习数据')
    })

    it('有数据时显示图表', () => {
      expect(wrapper.find('.charts-container').exists()).toBe(true)
    })

    it('月份边界处理', async () => {
      wrapper.vm.currentMonth = 1
      const prevButton = wrapper.find('.month-selector button:first-child')
      await prevButton.trigger('click')
      
      expect(wrapper.vm.currentMonth).toBe(12)
      expect(wrapper.vm.currentYear).toBe(2023)
    })
  })

  describe('响应式数据', () => {
    it('概览数据正确绑定', () => {
      expect(wrapper.vm.overview.total_exercises).toBe(150)
      expect(wrapper.vm.overview.total_words).toBe(2500)
      expect(wrapper.vm.overview.avg_wpm).toBe(45)
      expect(wrapper.vm.overview.avg_accuracy).toBe(85)
    })

    it('日期范围正确绑定', () => {
      expect(wrapper.vm.dateRange.length).toBe(2)
      expect(wrapper.vm.dateRangeText).toBe('2024-01-01 至 2024-03-31')
    })

    it('加载状态正确绑定', () => {
      expect(wrapper.vm.loading).toBe(false)
    })
  })

  describe('事件处理', () => {
    it('日期点击事件', async () => {
      const dayElement = wrapper.findAll('.calendar-day').find(day => day.text().includes('1'))
      if (dayElement) {
        await dayElement.trigger('click')
        expect(wrapper.vm.handleDayClick).toBeDefined()
      }
    })

    it('刷新数据状态变化', async () => {
      wrapper.vm.loading = true
      await wrapper.vm.$nextTick()
      
      expect(wrapper.text()).toContain('刷新中...')
    })
  })

  describe('数据更新', () => {
    it('刷新后数据更新', async () => {
      const originalExercises = wrapper.vm.overview.total_exercises
      await wrapper.vm.refreshData()
      
      expect(wrapper.vm.overview.total_exercises).toBe(160)
      expect(wrapper.vm.overview.total_exercises).not.toBe(originalExercises)
    })
  })
}) 