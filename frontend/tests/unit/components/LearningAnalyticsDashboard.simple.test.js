import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import LearningAnalyticsDashboard from '@/components/charts/analytics/LearningAnalyticsDashboard.vue'
import { createTestingPinia } from '@pinia/testing'

// Mock Element Plus message
global.ElMessage = {
  success: vi.fn(),
  error: vi.fn(),
  info: vi.fn(),
}

global.ElMessageBox = {
  confirm: vi.fn(),
}

// Mock router
const mockRouter = {
  push: vi.fn(),
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
    it('应该正确渲染学习分析仪表板', () => {
      wrapper = mount(LearningAnalyticsDashboard, {
        global: {
          plugins: [createTestingPinia({ createSpy: vi.fn })],
          mocks: {
            $router: mockRouter,
          },
          stubs: {
            'el-button': { template: '<button><slot /></button>' },
            'el-icon': { template: '<span><slot /></span>' },
            'el-dialog': { template: '<div><slot /></div>' },
            'ProgressTrendChart': { template: '<div class="progress-trend-chart">Progress Trend Chart</div>' },
            'MasteryDistributionChart': { template: '<div class="mastery-distribution-chart">Mastery Distribution Chart</div>' },
            'TimeAnalysisChart': { template: '<div class="time-analysis-chart">Time Analysis Chart</div>' },
            'EfficiencyRadarChart': { template: '<div class="efficiency-radar-chart">Efficiency Radar Chart</div>' },
            'LearningInsightsPanel': { template: '<div class="learning-insights-panel">Learning Insights Panel</div>' },
            'ReportGenerator': { template: '<div class="report-generator">Report Generator</div>' },
            'GoalTracker': { template: '<div class="goal-tracker">Goal Tracker</div>' },
          },
        },
      })

      expect(wrapper.find('.learning-analytics-dashboard').exists()).toBe(true)
      expect(wrapper.find('.dashboard-header').exists()).toBe(true)
      expect(wrapper.find('.dashboard-content').exists()).toBe(true)
    })

    it('应该显示仪表板标题', () => {
      wrapper = mount(LearningAnalyticsDashboard, {
        global: {
          plugins: [createTestingPinia({ createSpy: vi.fn })],
          mocks: {
            $router: mockRouter,
          },
          stubs: {
            'el-button': { template: '<button><slot /></button>' },
            'el-icon': { template: '<span><slot /></span>' },
            'el-dialog': { template: '<div><slot /></div>' },
            'ProgressTrendChart': { template: '<div class="progress-trend-chart">Progress Trend Chart</div>' },
            'MasteryDistributionChart': { template: '<div class="mastery-distribution-chart">Mastery Distribution Chart</div>' },
            'TimeAnalysisChart': { template: '<div class="time-analysis-chart">Time Analysis Chart</div>' },
            'EfficiencyRadarChart': { template: '<div class="efficiency-radar-chart">Efficiency Radar Chart</div>' },
            'LearningInsightsPanel': { template: '<div class="learning-insights-panel">Learning Insights Panel</div>' },
            'ReportGenerator': { template: '<div class="report-generator">Report Generator</div>' },
            'GoalTracker': { template: '<div class="goal-tracker">Goal Tracker</div>' },
          },
        },
      })

      const header = wrapper.find('.dashboard-header h2')
      expect(header.text()).toBe('学习数据分析')
    })

    it('应该显示导出报告按钮', () => {
      wrapper = mount(LearningAnalyticsDashboard, {
        global: {
          plugins: [createTestingPinia({ createSpy: vi.fn })],
          mocks: {
            $router: mockRouter,
          },
          stubs: {
            'el-button': { template: '<button><slot /></button>' },
            'el-icon': { template: '<span><slot /></span>' },
            'el-dialog': { template: '<div><slot /></div>' },
            'ProgressTrendChart': { template: '<div class="progress-trend-chart">Progress Trend Chart</div>' },
            'MasteryDistributionChart': { template: '<div class="mastery-distribution-chart">Mastery Distribution Chart</div>' },
            'TimeAnalysisChart': { template: '<div class="time-analysis-chart">Time Analysis Chart</div>' },
            'EfficiencyRadarChart': { template: '<div class="efficiency-radar-chart">Efficiency Radar Chart</div>' },
            'LearningInsightsPanel': { template: '<div class="learning-insights-panel">Learning Insights Panel</div>' },
            'ReportGenerator': { template: '<div class="report-generator">Report Generator</div>' },
            'GoalTracker': { template: '<div class="goal-tracker">Goal Tracker</div>' },
          },
        },
      })

      const exportBtn = wrapper.find('button:contains("导出报告")')
      expect(exportBtn.exists()).toBe(true)
    })

    it('应该显示刷新数据按钮', () => {
      wrapper = mount(LearningAnalyticsDashboard, {
        global: {
          plugins: [createTestingPinia({ createSpy: vi.fn })],
          mocks: {
            $router: mockRouter,
          },
          stubs: {
            'el-button': { template: '<button><slot /></button>' },
            'el-icon': { template: '<span><slot /></span>' },
            'el-dialog': { template: '<div><slot /></div>' },
            'ProgressTrendChart': { template: '<div class="progress-trend-chart">Progress Trend Chart</div>' },
            'MasteryDistributionChart': { template: '<div class="mastery-distribution-chart">Mastery Distribution Chart</div>' },
            'TimeAnalysisChart': { template: '<div class="time-analysis-chart">Time Analysis Chart</div>' },
            'EfficiencyRadarChart': { template: '<div class="efficiency-radar-chart">Efficiency Radar Chart</div>' },
            'LearningInsightsPanel': { template: '<div class="learning-insights-panel">Learning Insights Panel</div>' },
            'ReportGenerator': { template: '<div class="report-generator">Report Generator</div>' },
            'GoalTracker': { template: '<div class="goal-tracker">Goal Tracker</div>' },
          },
        },
      })

      const refreshBtn = wrapper.find('button:contains("刷新数据")')
      expect(refreshBtn.exists()).toBe(true)
    })

    it('应该渲染所有图表组件', () => {
      wrapper = mount(LearningAnalyticsDashboard, {
        global: {
          plugins: [createTestingPinia({ createSpy: vi.fn })],
          mocks: {
            $router: mockRouter,
          },
          stubs: {
            'el-button': { template: '<button><slot /></button>' },
            'el-icon': { template: '<span><slot /></span>' },
            'el-dialog': { template: '<div><slot /></div>' },
            'ProgressTrendChart': { template: '<div class="progress-trend-chart">Progress Trend Chart</div>' },
            'MasteryDistributionChart': { template: '<div class="mastery-distribution-chart">Mastery Distribution Chart</div>' },
            'TimeAnalysisChart': { template: '<div class="time-analysis-chart">Time Analysis Chart</div>' },
            'EfficiencyRadarChart': { template: '<div class="efficiency-radar-chart">Efficiency Radar Chart</div>' },
            'LearningInsightsPanel': { template: '<div class="learning-insights-panel">Learning Insights Panel</div>' },
            'ReportGenerator': { template: '<div class="report-generator">Report Generator</div>' },
            'GoalTracker': { template: '<div class="goal-tracker">Goal Tracker</div>' },
          },
        },
      })

      expect(wrapper.find('.progress-trend-chart').exists()).toBe(true)
      expect(wrapper.find('.mastery-distribution-chart').exists()).toBe(true)
      expect(wrapper.find('.time-analysis-chart').exists()).toBe(true)
      expect(wrapper.find('.efficiency-radar-chart').exists()).toBe(true)
      expect(wrapper.find('.learning-insights-panel').exists()).toBe(true)
      expect(wrapper.find('.report-generator').exists()).toBe(true)
      expect(wrapper.find('.goal-tracker').exists()).toBe(true)
    })

    it('应该正确设置图表布局', () => {
      wrapper = mount(LearningAnalyticsDashboard, {
        global: {
          plugins: [createTestingPinia({ createSpy: vi.fn })],
          mocks: {
            $router: mockRouter,
          },
          stubs: {
            'el-button': { template: '<button><slot /></button>' },
            'el-icon': { template: '<span><slot /></span>' },
            'el-dialog': { template: '<div><slot /></div>' },
            'ProgressTrendChart': { template: '<div class="progress-trend-chart">Progress Trend Chart</div>' },
            'MasteryDistributionChart': { template: '<div class="mastery-distribution-chart">Mastery Distribution Chart</div>' },
            'TimeAnalysisChart': { template: '<div class="time-analysis-chart">Time Analysis Chart</div>' },
            'EfficiencyRadarChart': { template: '<div class="efficiency-radar-chart">Efficiency Radar Chart</div>' },
            'LearningInsightsPanel': { template: '<div class="learning-insights-panel">Learning Insights Panel</div>' },
            'ReportGenerator': { template: '<div class="report-generator">Report Generator</div>' },
            'GoalTracker': { template: '<div class="goal-tracker">Goal Tracker</div>' },
          },
        },
      })

      const chartRows = wrapper.findAll('.chart-row')
      expect(chartRows.length).toBeGreaterThan(0)
      
      const chartCols = wrapper.findAll('.chart-col')
      expect(chartCols.length).toBeGreaterThan(0)
    })
  })

  describe('初始化功能', () => {
    it('组件挂载时应该初始化仪表板', () => {
      wrapper = mount(LearningAnalyticsDashboard, {
        global: {
          plugins: [createTestingPinia({ createSpy: vi.fn })],
          mocks: {
            $router: mockRouter,
          },
          stubs: {
            'el-button': { template: '<button><slot /></button>' },
            'el-icon': { template: '<span><slot /></span>' },
            'el-dialog': { template: '<div><slot /></div>' },
            'ProgressTrendChart': { template: '<div class="progress-trend-chart">Progress Trend Chart</div>' },
            'MasteryDistributionChart': { template: '<div class="mastery-distribution-chart">Mastery Distribution Chart</div>' },
            'TimeAnalysisChart': { template: '<div class="time-analysis-chart">Time Analysis Chart</div>' },
            'EfficiencyRadarChart': { template: '<div class="efficiency-radar-chart">Efficiency Radar Chart</div>' },
            'LearningInsightsPanel': { template: '<div class="learning-insights-panel">Learning Insights Panel</div>' },
            'ReportGenerator': { template: '<div class="report-generator">Report Generator</div>' },
            'GoalTracker': { template: '<div class="goal-tracker">Goal Tracker</div>' },
          },
        },
      })
      
      expect(ElMessage.success).toHaveBeenCalledWith('学习分析仪表板加载完成')
    })
  })

  describe('导航功能', () => {
    it('开始练习应该导航到练习模式', async () => {
      wrapper = mount(LearningAnalyticsDashboard, {
        global: {
          plugins: [createTestingPinia({ createSpy: vi.fn })],
          mocks: {
            $router: mockRouter,
          },
          stubs: {
            'el-button': { template: '<button><slot /></button>' },
            'el-icon': { template: '<span><slot /></span>' },
            'el-dialog': { template: '<div><slot /></div>' },
            'ProgressTrendChart': { template: '<div class="progress-trend-chart">Progress Trend Chart</div>' },
            'MasteryDistributionChart': { template: '<div class="mastery-distribution-chart">Mastery Distribution Chart</div>' },
            'TimeAnalysisChart': { template: '<div class="time-analysis-chart">Time Analysis Chart</div>' },
            'EfficiencyRadarChart': { template: '<div class="efficiency-radar-chart">Efficiency Radar Chart</div>' },
            'LearningInsightsPanel': { template: '<div class="learning-insights-panel">Learning Insights Panel</div>' },
            'ReportGenerator': { template: '<div class="report-generator">Report Generator</div>' },
            'GoalTracker': { template: '<div class="goal-tracker">Goal Tracker</div>' },
          },
        },
      })

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
      wrapper = mount(LearningAnalyticsDashboard, {
        global: {
          plugins: [createTestingPinia({ createSpy: vi.fn })],
          mocks: {
            $router: mockRouter,
          },
          stubs: {
            'el-button': { template: '<button><slot /></button>' },
            'el-icon': { template: '<span><slot /></span>' },
            'el-dialog': { template: '<div><slot /></div>' },
            'ProgressTrendChart': { template: '<div class="progress-trend-chart">Progress Trend Chart</div>' },
            'MasteryDistributionChart': { template: '<div class="mastery-distribution-chart">Mastery Distribution Chart</div>' },
            'TimeAnalysisChart': { template: '<div class="time-analysis-chart">Time Analysis Chart</div>' },
            'EfficiencyRadarChart': { template: '<div class="efficiency-radar-chart">Efficiency Radar Chart</div>' },
            'LearningInsightsPanel': { template: '<div class="learning-insights-panel">Learning Insights Panel</div>' },
            'ReportGenerator': { template: '<div class="report-generator">Report Generator</div>' },
            'GoalTracker': { template: '<div class="goal-tracker">Goal Tracker</div>' },
          },
        },
      })

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
    it('showDetailDialog应该正确设置弹窗属性', () => {
      wrapper = mount(LearningAnalyticsDashboard, {
        global: {
          plugins: [createTestingPinia({ createSpy: vi.fn })],
          mocks: {
            $router: mockRouter,
          },
          stubs: {
            'el-button': { template: '<button><slot /></button>' },
            'el-icon': { template: '<span><slot /></span>' },
            'el-dialog': { template: '<div><slot /></div>' },
            'ProgressTrendChart': { template: '<div class="progress-trend-chart">Progress Trend Chart</div>' },
            'MasteryDistributionChart': { template: '<div class="mastery-distribution-chart">Mastery Distribution Chart</div>' },
            'TimeAnalysisChart': { template: '<div class="time-analysis-chart">Time Analysis Chart</div>' },
            'EfficiencyRadarChart': { template: '<div class="efficiency-radar-chart">Efficiency Radar Chart</div>' },
            'LearningInsightsPanel': { template: '<div class="learning-insights-panel">Learning Insights Panel</div>' },
            'ReportGenerator': { template: '<div class="report-generator">Report Generator</div>' },
            'GoalTracker': { template: '<div class="goal-tracker">Goal Tracker</div>' },
          },
        },
      })

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
      wrapper = mount(LearningAnalyticsDashboard, {
        global: {
          plugins: [createTestingPinia({ createSpy: vi.fn })],
          mocks: {
            $router: mockRouter,
          },
          stubs: {
            'el-button': { template: '<button><slot /></button>' },
            'el-icon': { template: '<span><slot /></span>' },
            'el-dialog': { template: '<div><slot /></div>' },
            'ProgressTrendChart': { template: '<div class="progress-trend-chart">Progress Trend Chart</div>' },
            'MasteryDistributionChart': { template: '<div class="mastery-distribution-chart">Mastery Distribution Chart</div>' },
            'TimeAnalysisChart': { template: '<div class="time-analysis-chart">Time Analysis Chart</div>' },
            'EfficiencyRadarChart': { template: '<div class="efficiency-radar-chart">Efficiency Radar Chart</div>' },
            'LearningInsightsPanel': { template: '<div class="learning-insights-panel">Learning Insights Panel</div>' },
            'ReportGenerator': { template: '<div class="report-generator">Report Generator</div>' },
            'GoalTracker': { template: '<div class="goal-tracker">Goal Tracker</div>' },
          },
        },
      })

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
})
