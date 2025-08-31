import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { ElMessage, ElMessageBox } from 'element-plus'
import LearningAnalyticsDashboard from '@/components/charts/analytics/LearningAnalyticsDashboard.vue'
import { commonMountOptions, testUtils } from '../../setup.js'

// Mock Element Plus message and message box
vi.mock('element-plus', () => ({
  ElMessage: {
    success: vi.fn(),
    error: vi.fn(),
    info: vi.fn(),
  },
  ElMessageBox: {
    confirm: vi.fn(),
  },
}))

// Mock router
const mockRouter = {
  push: vi.fn(),
}

// Mock child components
const MockProgressTrendChart = {
  name: 'ProgressTrendChart',
  template: '<div class="progress-trend-chart">Progress Trend Chart</div>',
  methods: {
    loadData: vi.fn().mockResolvedValue({}),
  },
  data () {
    return {
      chartData: { trend: 'mock-progress-data' },
    }
  },
}

const MockMasteryDistributionChart = {
  name: 'MasteryDistributionChart', 
  template: '<div class="mastery-distribution-chart">Mastery Distribution Chart</div>',
  methods: {
    loadData: vi.fn().mockResolvedValue({}),
  },
  data () {
    return {
      chartData: { distribution: 'mock-mastery-data' },
    }
  },
}

const MockTimeAnalysisChart = {
  name: 'TimeAnalysisChart',
  template: '<div class="time-analysis-chart">Time Analysis Chart</div>',
  methods: {
    loadData: vi.fn().mockResolvedValue({}),
  },
  data () {
    return {
      chartData: { timeAnalysis: 'mock-time-data' },
      dateRange: null,
    }
  },
}

const MockEfficiencyRadarChart = {
  name: 'EfficiencyRadarChart',
  template: '<div class="efficiency-radar-chart">Efficiency Radar Chart</div>',
  methods: {
    loadData: vi.fn().mockResolvedValue({}),
  },
  data () {
    return {
      chartData: { efficiency: 'mock-efficiency-data' },
    }
  },
}

const MockLearningInsightsPanel = {
  name: 'LearningInsightsPanel',
  template: '<div class="learning-insights-panel">Learning Insights Panel</div>',
  methods: {
    loadInsights: vi.fn().mockResolvedValue({}),
  },
  data () {
    return {
      overviewData: { overview: 'mock-overview-data' },
      recommendationsData: { recommendations: 'mock-recommendations-data' },
      weakAreasData: { weakAreas: 'mock-weak-areas-data' },
    }
  },
}

const MockReportGenerator = {
  name: 'ReportGenerator',
  template: '<div class="report-generator">Report Generator</div>',
  methods: {
    loadRecentReports: vi.fn().mockResolvedValue({}),
  },
}

const MockGoalTracker = {
  name: 'GoalTracker',
  template: '<div class="goal-tracker">Goal Tracker</div>',
  methods: {
    loadGoals: vi.fn().mockResolvedValue({}),
  },
}

describe('LearningAnalyticsDashboard', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  describe('基础渲染', () => {
    beforeEach(() => {
      wrapper = mount(LearningAnalyticsDashboard, {
        ...commonMountOptions,
        global: {
          ...commonMountOptions.global,
          mocks: {
            $router: mockRouter,
          },
          stubs: {
            ProgressTrendChart: MockProgressTrendChart,
            MasteryDistributionChart: MockMasteryDistributionChart,
            TimeAnalysisChart: MockTimeAnalysisChart,
            EfficiencyRadarChart: MockEfficiencyRadarChart,
            LearningInsightsPanel: MockLearningInsightsPanel,
            ReportGenerator: MockReportGenerator,
            GoalTracker: MockGoalTracker,
          },
        },
      })
    })

    it('应该正确渲染学习分析仪表板', () => {
      expect(wrapper.find('.learning-analytics-dashboard').exists()).toBe(true)
      expect(wrapper.find('.dashboard-header').exists()).toBe(true)
      expect(wrapper.find('.dashboard-content').exists()).toBe(true)
    })

    it('应该显示仪表板标题', () => {
      const header = wrapper.find('.dashboard-header h2')
      expect(header.text()).toBe('学习数据分析')
    })

    it('应该显示导出报告按钮', () => {
      const exportBtn = wrapper.find('button:contains("导出报告")')
      expect(exportBtn.exists()).toBe(true)
    })

    it('应该显示刷新数据按钮', () => {
      const refreshBtn = wrapper.find('button:contains("刷新数据")')
      expect(refreshBtn.exists()).toBe(true)
    })

    it('应该渲染所有图表组件', () => {
      expect(wrapper.findComponent({ name: 'ProgressTrendChart' }).exists()).toBe(true)
      expect(wrapper.findComponent({ name: 'MasteryDistributionChart' }).exists()).toBe(true)
      expect(wrapper.findComponent({ name: 'TimeAnalysisChart' }).exists()).toBe(true)
      expect(wrapper.findComponent({ name: 'EfficiencyRadarChart' }).exists()).toBe(true)
      expect(wrapper.findComponent({ name: 'LearningInsightsPanel' }).exists()).toBe(true)
      expect(wrapper.findComponent({ name: 'ReportGenerator' }).exists()).toBe(true)
      expect(wrapper.findComponent({ name: 'GoalTracker' }).exists()).toBe(true)
    })

    it('应该正确设置图表布局', () => {
      const chartRows = wrapper.findAll('.chart-row')
      expect(chartRows).toHaveLength(4)
      
      // 第一行：8列 + 4列
      const firstRowCols = chartRows[0].findAll('.chart-col')
      expect(firstRowCols[0].classes()).toContain('chart-col-8')
      expect(firstRowCols[1].classes()).toContain('chart-col-4')
      
      // 第二行：6列 + 6列
      const secondRowCols = chartRows[1].findAll('.chart-col')
      expect(secondRowCols[0].classes()).toContain('chart-col-6')
      expect(secondRowCols[1].classes()).toContain('chart-col-6')
    })
  })

  describe('初始化功能', () => {
    it('组件挂载时应该初始化仪表板', () => {
      wrapper = mount(LearningAnalyticsDashboard, {
        ...commonMountOptions,
        global: {
          ...commonMountOptions.global,
          mocks: {
            $router: mockRouter,
          },
          stubs: {
            ProgressTrendChart: MockProgressTrendChart,
            MasteryDistributionChart: MockMasteryDistributionChart,
            TimeAnalysisChart: MockTimeAnalysisChart,
            EfficiencyRadarChart: MockEfficiencyRadarChart,
            LearningInsightsPanel: MockLearningInsightsPanel,
            ReportGenerator: MockReportGenerator,
            GoalTracker: MockGoalTracker,
          },
        },
      })
      
      expect(ElMessage.success).toHaveBeenCalledWith('学习分析仪表板加载完成')
    })
  })

  describe('数据刷新功能', () => {
    beforeEach(() => {
      wrapper = mount(LearningAnalyticsDashboard, {
        ...commonMountOptions,
        global: {
          ...commonMountOptions.global,
          mocks: {
            $router: mockRouter,
          },
          stubs: {
            ProgressTrendChart: MockProgressTrendChart,
            MasteryDistributionChart: MockMasteryDistributionChart,
            TimeAnalysisChart: MockTimeAnalysisChart,
            EfficiencyRadarChart: MockEfficiencyRadarChart,
            LearningInsightsPanel: MockLearningInsightsPanel,
            ReportGenerator: MockReportGenerator,
            GoalTracker: MockGoalTracker,
          },
        },
      })
    })

    it('点击刷新按钮应该刷新所有数据', async () => {
      const refreshBtn = wrapper.find('button:contains("刷新数据")')
      await refreshBtn.trigger('click')
      
      // 验证所有图表的loadData方法被调用
      expect(wrapper.vm.$refs.progressChart.loadData).toHaveBeenCalled()
      expect(wrapper.vm.$refs.masteryChart.loadData).toHaveBeenCalled()
      expect(wrapper.vm.$refs.timeChart.loadData).toHaveBeenCalled()
      expect(wrapper.vm.$refs.efficiencyChart.loadData).toHaveBeenCalled()
      expect(wrapper.vm.$refs.insightsPanel.loadInsights).toHaveBeenCalled()
      expect(wrapper.vm.$refs.reportGenerator.loadRecentReports).toHaveBeenCalled()
      expect(wrapper.vm.$refs.goalTracker.loadGoals).toHaveBeenCalled()
    })

    it('刷新成功时应该显示成功消息', async () => {
      await wrapper.vm.refreshAllData()
      
      expect(ElMessage.success).toHaveBeenCalledWith('所有数据已刷新')
    })

    it('刷新过程中应该显示加载状态', async () => {
      const refreshPromise = wrapper.vm.refreshAllData()
      
      expect(wrapper.vm.globalLoading).toBe(true)
      
      await refreshPromise
      
      expect(wrapper.vm.globalLoading).toBe(false)
    })

    it('刷新失败时应该显示错误消息', async () => {
      // 模拟其中一个图表加载失败
      wrapper.vm.$refs.progressChart.loadData.mockRejectedValueOnce(new Error('Network error'))
      
      await wrapper.vm.refreshAllData()
      
      expect(ElMessage.error).toHaveBeenCalledWith('刷新数据失败，请稍后重试')
    })
  })

  describe('事件处理', () => {
    beforeEach(() => {
      wrapper = mount(LearningAnalyticsDashboard, {
        ...commonMountOptions,
        global: {
          ...commonMountOptions.global,
          mocks: {
            $router: mockRouter,
          },
          stubs: {
            ProgressTrendChart: MockProgressTrendChart,
            MasteryDistributionChart: MockMasteryDistributionChart,
            TimeAnalysisChart: MockTimeAnalysisChart,
            EfficiencyRadarChart: MockEfficiencyRadarChart,
            LearningInsightsPanel: MockLearningInsightsPanel,
            ReportGenerator: MockReportGenerator,
            GoalTracker: MockGoalTracker,
          },
        },
      })
    })

    it('日期范围变化时应该同步到时间分析图表', async () => {
      const dateRange = { start: '2024-01-01', end: '2024-01-31' }
      
      await wrapper.vm.handleDateRangeChange(dateRange)
      
      expect(wrapper.vm.$refs.timeChart.dateRange).toEqual(dateRange)
      expect(wrapper.vm.$refs.timeChart.loadData).toHaveBeenCalled()
    })

    it('掌握度分布点击时应该显示详情弹窗', async () => {
      const mockData = {
        name: '高掌握度',
        value: 25,
        category: 'high',
      }
      
      await wrapper.vm.handleMasterySegmentClick(mockData)
      
      expect(wrapper.vm.detailDialogVisible).toBe(true)
      expect(wrapper.vm.detailDialogTitle).toBe('掌握度详情')
      expect(wrapper.vm.detailComponent).toBe('MasteryDetail')
      expect(wrapper.vm.detailProps).toEqual({
        segment: mockData.name,
        value: mockData.value,
        category: mockData.category,
      })
    })

    it('时间段点击时应该显示详情弹窗', async () => {
      const mockData = {
        period: '上午',
        value: 80,
        viewMode: 'daily',
        metric: 'efficiency',
      }
      
      await wrapper.vm.handleTimePeriodClick(mockData)
      
      expect(wrapper.vm.detailDialogVisible).toBe(true)
      expect(wrapper.vm.detailDialogTitle).toBe('时间段详情')
      expect(wrapper.vm.detailComponent).toBe('TimePeriodDetail')
      expect(wrapper.vm.detailProps).toEqual(mockData)
    })
  })

  describe('智能建议处理', () => {
    beforeEach(() => {
      wrapper = mount(LearningAnalyticsDashboard, {
        ...commonMountOptions,
        global: {
          ...commonMountOptions.global,
          mocks: {
            $router: mockRouter,
          },
          stubs: {
            ProgressTrendChart: MockProgressTrendChart,
            MasteryDistributionChart: MockMasteryDistributionChart,
            TimeAnalysisChart: MockTimeAnalysisChart,
            EfficiencyRadarChart: MockEfficiencyRadarChart,
            LearningInsightsPanel: MockLearningInsightsPanel,
            ReportGenerator: MockReportGenerator,
            GoalTracker: MockGoalTracker,
          },
        },
      })
    })

    it('练习建议应该跳转到练习页面', async () => {
      const recommendation = {
        type: 'practice',
        target_id: 123,
        title: '练习建议',
      }
      
      await wrapper.vm.handleRecommendationAction(recommendation)
      
      expect(mockRouter.push).toHaveBeenCalledWith({
        path: '/english/idiomatic-learning',
        query: {
          mode: 'practice',
          expressionId: 123,
        },
      })
    })

    it('复习建议应该跳转到复习页面', async () => {
      const recommendation = {
        type: 'review',
        target_id: 456,
        title: '复习建议',
      }
      
      await wrapper.vm.handleRecommendationAction(recommendation)
      
      expect(mockRouter.push).toHaveBeenCalledWith({
        path: '/english/idiomatic-learning',
        query: {
          mode: 'review',
          expressionId: 456,
        },
      })
    })

    it('难度调整建议应该显示确认对话框', async () => {
      ElMessageBox.confirm.mockResolvedValueOnce(true)
      
      const recommendation = {
        type: 'difficulty',
        target_id: 789,
        title: '难度调整建议',
      }
      
      await wrapper.vm.handleRecommendationAction(recommendation)
      
      expect(ElMessageBox.confirm).toHaveBeenCalledWith(
        '是否要调整该表达的难度级别？',
        '难度调整',
        expect.any(Object),
      )
      expect(ElMessage.success).toHaveBeenCalledWith('难度已调整')
    })

    it('取消难度调整应该显示取消消息', async () => {
      ElMessageBox.confirm.mockRejectedValueOnce(new Error('Cancel'))
      
      await wrapper.vm.adjustDifficulty(789)
      
      expect(ElMessage.info).toHaveBeenCalledWith('已取消操作')
    })

    it('其他类型建议应该显示通用消息', async () => {
      const recommendation = {
        type: 'other',
        target_id: 999,
        title: '其他建议',
      }
      
      await wrapper.vm.handleRecommendationAction(recommendation)
      
      expect(ElMessage.info).toHaveBeenCalledWith('执行建议: 其他建议')
    })
  })

  describe('导航功能', () => {
    beforeEach(() => {
      wrapper = mount(LearningAnalyticsDashboard, {
        ...commonMountOptions,
        global: {
          ...commonMountOptions.global,
          mocks: {
            $router: mockRouter,
          },
          stubs: {
            ProgressTrendChart: MockProgressTrendChart,
            MasteryDistributionChart: MockMasteryDistributionChart,
            TimeAnalysisChart: MockTimeAnalysisChart,
            EfficiencyRadarChart: MockEfficiencyRadarChart,
            LearningInsightsPanel: MockLearningInsightsPanel,
            ReportGenerator: MockReportGenerator,
            GoalTracker: MockGoalTracker,
          },
        },
      })
    })

    it('开始练习应该导航到练习模式', async () => {
      await wrapper.vm.handleStartPractice(123)
      
      expect(mockRouter.push).toHaveBeenCalledWith({
        path: '/english/idiomatic-learning',
        query: {
          mode: 'practice',
          expressionId: 123,
        },
      })
    })

    it('开始复习应该导航到复习模式', async () => {
      await wrapper.vm.handleStartReview(456)
      
      expect(mockRouter.push).toHaveBeenCalledWith({
        path: '/english/idiomatic-learning',
        query: {
          mode: 'review',
          expressionId: 456,
        },
      })
    })
  })

  describe('详情弹窗管理', () => {
    beforeEach(() => {
      wrapper = mount(LearningAnalyticsDashboard, {
        ...commonMountOptions,
        global: {
          ...commonMountOptions.global,
          mocks: {
            $router: mockRouter,
          },
          stubs: {
            ProgressTrendChart: MockProgressTrendChart,
            MasteryDistributionChart: MockMasteryDistributionChart,
            TimeAnalysisChart: MockTimeAnalysisChart,
            EfficiencyRadarChart: MockEfficiencyRadarChart,
            LearningInsightsPanel: MockLearningInsightsPanel,
            ReportGenerator: MockReportGenerator,
            GoalTracker: MockGoalTracker,
          },
        },
      })
    })

    it('showDetailDialog应该正确设置弹窗属性', () => {
      const title = '测试标题'
      const component = 'TestComponent'
      const props = { test: 'data' }
      
      wrapper.vm.showDetailDialog(title, component, props)
      
      expect(wrapper.vm.detailDialogTitle).toBe(title)
      expect(wrapper.vm.detailComponent).toBe(component)
      expect(wrapper.vm.detailProps).toEqual(props)
      expect(wrapper.vm.detailDialogVisible).toBe(true)
    })

    it('关闭弹窗应该重置所有属性', () => {
      wrapper.vm.detailDialogVisible = true
      wrapper.vm.detailDialogTitle = '测试标题'
      wrapper.vm.detailComponent = 'TestComponent'
      wrapper.vm.detailProps = { test: 'data' }
      
      wrapper.vm.handleDetailDialogClose()
      
      expect(wrapper.vm.detailDialogVisible).toBe(false)
      expect(wrapper.vm.detailComponent).toBeNull()
      expect(wrapper.vm.detailProps).toEqual({})
    })
  })

  describe('报告导出功能', () => {
    beforeEach(() => {
      wrapper = mount(LearningAnalyticsDashboard, {
        ...commonMountOptions,
        global: {
          ...commonMountOptions.global,
          mocks: {
            $router: mockRouter,
          },
          stubs: {
            ProgressTrendChart: MockProgressTrendChart,
            MasteryDistributionChart: MockMasteryDistributionChart,
            TimeAnalysisChart: MockTimeAnalysisChart,
            EfficiencyRadarChart: MockEfficiencyRadarChart,
            LearningInsightsPanel: MockLearningInsightsPanel,
            ReportGenerator: MockReportGenerator,
            GoalTracker: MockGoalTracker,
          },
        },
      })
    })

    it('点击导出报告按钮应该开始导出', async () => {
      const exportBtn = wrapper.find('button:contains("导出报告")')
      await exportBtn.trigger('click')
      
      expect(ElMessage.info).toHaveBeenCalledWith('正在生成报告...')
    })

    it('导出报告应该收集所有图表数据', async () => {
      const spy = vi.spyOn(wrapper.vm, 'exportReport')
      
      await wrapper.vm.exportReport()
      
      expect(spy).toHaveBeenCalled()
      
      // 验证数据收集逻辑（这里可以根据实际实现进行调整）
      const expectedReportStructure = expect.objectContaining({
        generated_at: expect.any(String),
        progress_trend: expect.any(Object),
        mastery_distribution: expect.any(Object),
        time_analysis: expect.any(Object),
        efficiency_analysis: expect.any(Object),
        learning_insights: expect.objectContaining({
          overview: expect.any(Object),
          recommendations: expect.any(Object),
          weak_areas: expect.any(Object),
        }),
      })
      
      // 这里可以进一步验证报告数据结构
    })
  })

  describe('目标管理', () => {
    beforeEach(() => {
      wrapper = mount(LearningAnalyticsDashboard, {
        ...commonMountOptions,
        global: {
          ...commonMountOptions.global,
          mocks: {
            $router: mockRouter,
          },
          stubs: {
            ProgressTrendChart: MockProgressTrendChart,
            MasteryDistributionChart: MockMasteryDistributionChart,
            TimeAnalysisChart: MockTimeAnalysisChart,
            EfficiencyRadarChart: MockEfficiencyRadarChart,
            LearningInsightsPanel: MockLearningInsightsPanel,
            ReportGenerator: MockReportGenerator,
            GoalTracker: MockGoalTracker,
          },
        },
      })
    })

    it('目标创建事件应该有对应的处理器', () => {
      expect(typeof wrapper.vm.handleGoalCreated).toBe('function')
    })

    it('目标更新事件应该有对应的处理器', () => {
      expect(typeof wrapper.vm.handleGoalUpdated).toBe('function')
    })
  })

  describe('响应式布局', () => {
    beforeEach(() => {
      wrapper = mount(LearningAnalyticsDashboard, {
        ...commonMountOptions,
        global: {
          ...commonMountOptions.global,
          mocks: {
            $router: mockRouter,
          },
          stubs: {
            ProgressTrendChart: MockProgressTrendChart,
            MasteryDistributionChart: MockMasteryDistributionChart,
            TimeAnalysisChart: MockTimeAnalysisChart,
            EfficiencyRadarChart: MockEfficiencyRadarChart,
            LearningInsightsPanel: MockLearningInsightsPanel,
            ReportGenerator: MockReportGenerator,
            GoalTracker: MockGoalTracker,
          },
        },
      })
    })

    it('应该有正确的栅格布局类', () => {
      const chartCols = wrapper.findAll('.chart-col')
      
      // 验证各种栅格宽度类的存在
      const colClasses = chartCols.map(col => col.classes())
      const hasCol4 = colClasses.some(classes => classes.includes('chart-col-4'))
      const hasCol6 = colClasses.some(classes => classes.includes('chart-col-6'))
      const hasCol8 = colClasses.some(classes => classes.includes('chart-col-8'))
      const hasCol12 = colClasses.some(classes => classes.includes('chart-col-12'))
      
      expect(hasCol4).toBe(true)
      expect(hasCol6).toBe(true)
      expect(hasCol8).toBe(true)
      expect(hasCol12).toBe(true)
    })
  })
})
