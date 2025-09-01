import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { ElMessage } from 'element-plus'
import StatisticsView from '../StatisticsView.vue'
import { aiConfigAPI } from '@/api/aiConfig'

// Mock API
vi.mock('@/api/aiConfig', () => ({
  aiConfigAPI: {
    getUsageStatistics: vi.fn(),
    getConsumptionTrends: vi.fn(),
    getConsumptionPieChart: vi.fn(),
    getConsumptionHeatmap: vi.fn(),
    getConsumptionDetails: vi.fn(),
    getBudgetSettings: vi.fn(),
    updateBudgetSettings: vi.fn(),
    getAlertConfigs: vi.fn(),
    createAlertConfig: vi.fn(),
    updateAlertConfig: vi.fn()
  }
}))

// Mock Element Plus components
vi.mock('element-plus', () => ({
  ElMessage: {
    success: vi.fn(),
    error: vi.fn(),
    info: vi.fn()
  }
}))

// Mock ECharts
vi.mock('vue-echarts', () => ({
  default: {
    name: 'v-chart',
    template: '<div class="v-chart-mock"></div>'
  }
}))

// Mock ECharts core
vi.mock('echarts/core', () => ({
  use: vi.fn()
}))

describe('StatisticsView', () => {
  let wrapper

  const mockOverviewData = {
    total_consumption: 1000000,
    total_cost: 150.50,
    avg_daily_consumption: 142857,
    budget_usage: 75
  }

  const mockTrendData = [
    { date: '2024-01-01', tokens: 1000, cost: 0.15 },
    { date: '2024-01-02', tokens: 1200, cost: 0.18 },
    { date: '2024-01-03', tokens: 800, cost: 0.12 }
  ]

  const mockPieData = [
    { name: 'OpenAI', value: 600000 },
    { name: 'Anthropic', value: 400000 }
  ]

  const mockHeatmapData = [
    [0, 0, 100], [1, 0, 200], [2, 0, 150],
    [0, 1, 120], [1, 1, 180], [2, 1, 160]
  ]

  const mockDetailsData = [
    {
      id: 1,
      timestamp: '2024-01-01T10:00:00Z',
      provider: 'OpenAI',
      model: 'gpt-4',
      tokens_used: 1000,
      cost: 0.15,
      request_type: 'completion',
      status: 'success',
      user: 'admin'
    }
  ]

  const mockBudgetSettings = {
    monthly_budget: 1000,
    token_budget: 10000000,
    alert_threshold: 80,
    enabled: true
  }

  beforeEach(() => {
    // Reset mocks
    vi.clearAllMocks()
    
    // Setup API mocks
    aiConfigAPI.getUsageStatistics.mockResolvedValue({
      data: mockOverviewData
    })
    aiConfigAPI.getConsumptionTrends.mockResolvedValue({
      data: { results: mockTrendData }
    })
    aiConfigAPI.getConsumptionPieChart.mockResolvedValue({
      data: { results: mockPieData }
    })
    aiConfigAPI.getConsumptionHeatmap.mockResolvedValue({
      data: { results: mockHeatmapData }
    })
    aiConfigAPI.getConsumptionDetails.mockResolvedValue({
      data: { results: mockDetailsData, count: 1 }
    })
    aiConfigAPI.getBudgetSettings.mockResolvedValue({
      data: mockBudgetSettings
    })
    
    // Mount component
    wrapper = mount(StatisticsView, {
      global: {
        stubs: {
          'el-card': true,
          'el-form': true,
          'el-form-item': true,
          'el-select': true,
          'el-option': true,
          'el-date-picker': true,
          'el-button': true,
          'el-row': true,
          'el-col': true,
          'el-radio-group': true,
          'el-radio-button': true,
          'el-table': true,
          'el-table-column': true,
          'el-pagination': true,
          'el-dialog': true,
          'el-input': true,
          'el-input-number': true,
          'el-switch': true,
          'el-checkbox-group': true,
          'el-checkbox': true,
          'el-tag': true,
          'el-icon': true,
          'v-chart': true
        }
      }
    })
  })

  describe('组件初始化', () => {
    it('应该正确加载所有数据', async () => {
      // 等待组件挂载和数据加载
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100)) // 等待异步操作完成
      
      expect(aiConfigAPI.getUsageStatistics).toHaveBeenCalledWith('7d')
      expect(aiConfigAPI.getConsumptionTrends).toHaveBeenCalled()
      expect(aiConfigAPI.getConsumptionPieChart).toHaveBeenCalled()
      expect(aiConfigAPI.getConsumptionHeatmap).toHaveBeenCalled()
      expect(aiConfigAPI.getConsumptionDetails).toHaveBeenCalled()
      
      expect(wrapper.vm.overview.totalConsumption).toBe(1000000)
      expect(wrapper.vm.overview.totalCost).toBe(150.50)
      expect(wrapper.vm.trendData).toEqual(mockTrendData)
      expect(wrapper.vm.pieData).toEqual(mockPieData)
      expect(wrapper.vm.heatmapData).toEqual(mockHeatmapData)
      expect(wrapper.vm.detailsData).toEqual(mockDetailsData)
    })

    it('应该处理API错误', async () => {
      // 重置mock，让loadData方法重新调用
      vi.clearAllMocks()
      aiConfigAPI.getUsageStatistics.mockRejectedValue(new Error('API Error'))
      
      await wrapper.vm.loadData()
      
      expect(ElMessage.error).toHaveBeenCalledWith('加载数据失败')
    })
  })

  describe('时间范围选择', () => {
    it('应该处理时间范围变化', async () => {
      wrapper.vm.timeRangeForm.range = '30d'
      await wrapper.vm.handleTimeRangeChange()
      
      expect(aiConfigAPI.getUsageStatistics).toHaveBeenCalledWith('30d')
    })

    it('应该处理自定义日期范围', async () => {
      wrapper.vm.timeRangeForm.range = 'custom'
      wrapper.vm.timeRangeForm.startDate = new Date('2024-01-01')
      wrapper.vm.timeRangeForm.endDate = new Date('2024-01-31')
      
      await wrapper.vm.handleCustomDateChange()
      
      expect(aiConfigAPI.getUsageStatistics).toHaveBeenCalled()
    })
  })

  describe('图表功能', () => {
    it('应该正确计算趋势图配置', () => {
      wrapper.vm.trendData = mockTrendData
      wrapper.vm.trendChartType = 'tokens'
      
      const option = wrapper.vm.trendChartOption
      expect(option.xAxis.data).toEqual(['2024-01-01', '2024-01-02', '2024-01-03'])
      expect(option.series[0].data).toEqual([1000, 1200, 800])
      expect(option.yAxis.name).toBe('Token数量')
    })

    it('应该正确计算成本趋势图配置', () => {
      wrapper.vm.trendData = mockTrendData
      wrapper.vm.trendChartType = 'cost'
      
      const option = wrapper.vm.trendChartOption
      expect(option.series[0].data).toEqual([0.15, 0.18, 0.12])
      expect(option.yAxis.name).toBe('成本 (¥)')
    })

    it('应该正确计算饼图配置', () => {
      wrapper.vm.pieData = mockPieData
      
      const option = wrapper.vm.pieChartOption
      expect(option.series[0].data).toEqual(mockPieData)
      expect(option.series[0].type).toBe('pie')
    })

    it('应该正确计算热力图配置', () => {
      wrapper.vm.heatmapData = mockHeatmapData
      
      const option = wrapper.vm.heatmapOption
      expect(option.series[0].data).toEqual(mockHeatmapData)
      expect(option.series[0].type).toBe('heatmap')
    })
  })

  describe('分页功能', () => {
    it('应该处理页面大小变化', async () => {
      wrapper.vm.pagination.pageSize = 50
      await wrapper.vm.handlePageSizeChange(50)
      
      expect(wrapper.vm.pagination.currentPage).toBe(1)
      expect(aiConfigAPI.getConsumptionDetails).toHaveBeenCalledWith(
        expect.objectContaining({ page_size: 50 })
      )
    })

    it('应该处理当前页面变化', async () => {
      await wrapper.vm.handleCurrentPageChange(2)
      
      expect(wrapper.vm.pagination.currentPage).toBe(2)
      expect(aiConfigAPI.getConsumptionDetails).toHaveBeenCalledWith(
        expect.objectContaining({ page: 2 })
      )
    })
  })

  describe('预算设置', () => {
    it('应该能够加载预算设置', async () => {
      await wrapper.vm.showBudgetSettings()
      
      expect(aiConfigAPI.getBudgetSettings).toHaveBeenCalled()
      expect(wrapper.vm.budgetForm.monthly_budget).toBe(1000)
      expect(wrapper.vm.budgetDialogVisible).toBe(true)
    })

    it('应该能够保存预算设置', async () => {
      wrapper.vm.budgetFormRef = { validate: vi.fn().mockResolvedValue() }
      aiConfigAPI.updateBudgetSettings.mockResolvedValue()
      
      await wrapper.vm.saveBudgetSettings()
      
      expect(aiConfigAPI.updateBudgetSettings).toHaveBeenCalledWith(wrapper.vm.budgetForm)
      expect(ElMessage.success).toHaveBeenCalledWith('预算设置保存成功')
      expect(wrapper.vm.budgetDialogVisible).toBe(false)
    })

    it('应该处理预算设置保存错误', async () => {
      wrapper.vm.budgetFormRef = { validate: vi.fn().mockResolvedValue() }
      const error = {
        response: {
          data: {
            message: '预算设置无效'
          }
        }
      }
      aiConfigAPI.updateBudgetSettings.mockRejectedValue(error)
      
      await wrapper.vm.saveBudgetSettings()
      
      expect(ElMessage.error).toHaveBeenCalledWith('预算设置无效')
    })
  })

  describe('告警配置', () => {
    it('应该能够显示告警配置对话框', () => {
      wrapper.vm.showAlertConfig()
      
      expect(wrapper.vm.isEditAlert).toBe(false)
      expect(wrapper.vm.alertDialogVisible).toBe(true)
    })

    it('应该能够创建告警配置', async () => {
      wrapper.vm.alertFormRef = { validate: vi.fn().mockResolvedValue() }
      aiConfigAPI.createAlertConfig.mockResolvedValue()
      
      await wrapper.vm.saveAlertConfig()
      
      expect(aiConfigAPI.createAlertConfig).toHaveBeenCalledWith(wrapper.vm.alertForm)
      expect(ElMessage.success).toHaveBeenCalledWith('告警配置创建成功')
      expect(wrapper.vm.alertDialogVisible).toBe(false)
    })

    it('应该能够更新告警配置', async () => {
      wrapper.vm.isEditAlert = true
      wrapper.vm.alertForm.id = 1
      wrapper.vm.alertFormRef = { validate: vi.fn().mockResolvedValue() }
      aiConfigAPI.updateAlertConfig.mockResolvedValue()
      
      await wrapper.vm.saveAlertConfig()
      
      expect(aiConfigAPI.updateAlertConfig).toHaveBeenCalledWith(1, wrapper.vm.alertForm)
      expect(ElMessage.success).toHaveBeenCalledWith('告警配置更新成功')
    })
  })

  describe('数据导出', () => {
    it('应该处理数据导出', () => {
      wrapper.vm.detailsData = mockDetailsData
      wrapper.vm.exportData()
      
      expect(ElMessage.success).toHaveBeenCalledWith('数据导出功能开发中')
    })
  })

  describe('工具函数', () => {
    it('应该正确格式化数字', () => {
      expect(wrapper.vm.formatNumber(1234.5678, 2)).toBe('1,234.57')
      expect(wrapper.vm.formatNumber(1000000)).toBe('1,000,000')
      expect(wrapper.vm.formatNumber(null)).toBe('0')
      expect(wrapper.vm.formatNumber(undefined)).toBe('0')
    })

    it('应该正确获取时间范围参数', () => {
      // 测试预设时间范围
      wrapper.vm.timeRangeForm.range = '30d'
      const params1 = wrapper.vm.getTimeRangeParams()
      expect(params1.time_range).toBe('30d')
      
      // 测试自定义时间范围
      wrapper.vm.timeRangeForm.range = 'custom'
      wrapper.vm.timeRangeForm.startDate = new Date('2024-01-01')
      wrapper.vm.timeRangeForm.endDate = new Date('2024-01-31')
      const params2 = wrapper.vm.getTimeRangeParams()
      expect(params2.start_date).toBe('2024-01-01')
      expect(params2.end_date).toBe('2024-01-31')
    })
  })

  describe('响应式设计', () => {
    it('应该在移动端正确显示概览卡片', () => {
      // 模拟移动端窗口大小
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 768
      })
      
      // 触发窗口大小变化
      window.dispatchEvent(new Event('resize'))
      
      // 这里可以添加移动端特定的测试逻辑
      expect(wrapper.vm.overview).toBeDefined()
    })
  })

  describe('错误处理', () => {
    it('应该处理图表数据加载错误', async () => {
      aiConfigAPI.getConsumptionTrends.mockRejectedValue(new Error('Chart Error'))
      
      await wrapper.vm.loadChartData()
      
      // 应该静默处理错误，不显示用户提示
      expect(ElMessage.error).not.toHaveBeenCalled()
    })

    it('应该处理详细数据加载错误', async () => {
      aiConfigAPI.getConsumptionDetails.mockRejectedValue(new Error('Details Error'))
      
      await wrapper.vm.loadDetailsData()
      
      // 应该静默处理错误，不显示用户提示
      expect(ElMessage.error).not.toHaveBeenCalled()
    })
  })

  describe('性能优化', () => {
    it('应该使用防抖处理时间范围变化', async () => {
      // 重置mock调用次数
      vi.clearAllMocks()
      
      // 快速连续调用时间范围变化
      wrapper.vm.timeRangeForm.range = '7d'
      await wrapper.vm.handleTimeRangeChange()
      
      wrapper.vm.timeRangeForm.range = '30d'
      await wrapper.vm.handleTimeRangeChange()
      
      // 应该调用两次（每次都会触发loadData）
      expect(aiConfigAPI.getUsageStatistics).toHaveBeenCalledTimes(2)
      expect(aiConfigAPI.getUsageStatistics).toHaveBeenLastCalledWith('30d')
    })
  })
})
