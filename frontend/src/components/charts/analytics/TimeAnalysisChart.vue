<template>
  <div class="time-analysis-chart">
    <div class="chart-header">
      <h3>学习时间分析</h3>
      <div class="chart-controls">
        <el-radio-group 
          v-model="viewMode" 
          size="small"
          @change="handleViewModeChange"
        >
          <el-radio-button label="daily">按日</el-radio-button>
          <el-radio-button label="weekly">按周</el-radio-button>
          <el-radio-button label="monthly">按月</el-radio-button>
        </el-radio-group>
        <el-select
          v-model="timeMetric"
          placeholder="时间指标"
          size="small"
          style="width: 120px; margin-left: 10px"
          @change="handleMetricChange"
        >
          <el-option label="学习时长" value="duration" />
          <el-option label="最佳时段" value="best_time" />
          <el-option label="活跃度" value="activity" />
        </el-select>
      </div>
    </div>
    <div 
      ref="chartContainer" 
      class="chart-container"
      v-loading="loading"
    ></div>
    <div class="chart-summary" v-if="summaryData">
      <div class="summary-item">
        <span class="summary-label">总学习时长:</span>
        <span class="summary-value">{{ formatDuration(summaryData.total_duration) }}</span>
      </div>
      <div class="summary-item">
        <span class="summary-label">平均每日:</span>
        <span class="summary-value">{{ formatDuration(summaryData.avg_daily) }}</span>
      </div>
      <div class="summary-item">
        <span class="summary-label">最佳学习时段:</span>
        <span class="summary-value">{{ summaryData.best_time_slot || '-' }}</span>
      </div>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts'
import { dataAnalysisAPI } from '@/api/english'
import { ElMessage } from 'element-plus'

export default {
  name: 'TimeAnalysisChart',
  props: {
    height: {
      type: String,
      default: '400px'
    }
  },
  data() {
    return {
      chart: null,
      loading: false,
      viewMode: 'daily',
      timeMetric: 'duration',
      chartData: null,
      summaryData: null
    }
  },
  mounted() {
    this.initChart()
    this.loadData()
  },
  beforeUnmount() {
    if (this.chart) {
      this.chart.dispose()
    }
    window.removeEventListener('resize', this.handleResize)
  },
  methods: {
    initChart() {
      this.chart = echarts.init(this.$refs.chartContainer)
      
      // 监听窗口大小变化
      window.addEventListener('resize', this.handleResize)
    },
    
    handleResize() {
      if (this.chart) {
        this.chart.resize()
      }
    },
    
    async loadData() {
      this.loading = true
      try {
        const params = {
          view_mode: this.viewMode,
          metric: this.timeMetric
        }
        
        const response = await dataAnalysisAPI.getTimeAnalysis(params)
        this.chartData = response.data
        this.summaryData = response.data.summary
        this.updateChart()
      } catch (error) {
        console.error('加载时间分析数据失败:', error)
        ElMessage.error('加载数据失败，请稍后重试')
      } finally {
        this.loading = false
      }
    },
    
    updateChart() {
      if (!this.chart || !this.chartData) return
      
      const option = {
        title: {
          text: this.getChartTitle(),
          left: 'center',
          textStyle: {
            fontSize: 16,
            fontWeight: 'normal'
          }
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          },
          formatter: (params) => {
            const param = params[0]
            const value = this.formatTooltipValue(param.value, this.timeMetric)
            return `${param.axisValue}<br/>${param.seriesName}: ${value}`
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          top: '12%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: this.chartData.xAxis || [],
          axisLabel: {
            rotate: this.viewMode === 'daily' ? 45 : 0,
            interval: this.getXAxisInterval()
          }
        },
        yAxis: {
          type: 'value',
          name: this.getYAxisName(),
          axisLabel: {
            formatter: (value) => this.formatAxisValue(value, this.timeMetric)
          }
        },
        series: [
          {
            name: this.getSeriesName(),
            type: 'bar',
            data: this.chartData.data || [],
            itemStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: '#83bff6' },
                { offset: 0.5, color: '#188df0' },
                { offset: 1, color: '#188df0' }
              ]),
              borderRadius: [4, 4, 0, 0]
            },
            emphasis: {
              itemStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                  { offset: 0, color: '#2378f7' },
                  { offset: 0.7, color: '#2378f7' },
                  { offset: 1, color: '#83bff6' }
                ])
              }
            },
            markLine: this.getMarkLine()
          }
        ]
      }
      
      this.chart.setOption(option, true)
      
      // 添加点击事件
      this.chart.off('click')
      this.chart.on('click', (params) => {
        this.$emit('time-period-click', {
          period: params.name,
          value: params.value,
          viewMode: this.viewMode,
          metric: this.timeMetric
        })
      })
    },
    
    getMarkLine() {
      if (!this.summaryData || this.timeMetric !== 'duration') return null
      
      return {
        data: [
          {
            name: '平均值',
            type: 'average',
            label: {
              formatter: '平均: {c}分钟'
            }
          }
        ],
        lineStyle: {
          color: '#FF6B6B',
          type: 'dashed'
        }
      }
    },
    
    getXAxisInterval() {
      if (this.viewMode === 'daily') {
        return 'auto'
      }
      return 0
    },
    
    getChartTitle() {
      const titles = {
        daily: '每日学习时间',
        weekly: '每周学习时间', 
        monthly: '每月学习时间'
      }
      return titles[this.viewMode] || '学习时间分析'
    },
    
    getSeriesName() {
      const names = {
        duration: '学习时长',
        best_time: '最佳时段',
        activity: '活跃度'
      }
      return names[this.timeMetric] || '时间指标'
    },
    
    getYAxisName() {
      const names = {
        duration: '时长 (分钟)',
        best_time: '时段评分',
        activity: '活跃度'
      }
      return names[this.timeMetric] || ''
    },
    
    formatAxisValue(value, metric) {
      switch (metric) {
        case 'duration':
          return `${value}分`
        case 'best_time':
          return value.toFixed(1)
        case 'activity':
          return `${value}%`
        default:
          return value.toString()
      }
    },
    
    formatTooltipValue(value, metric) {
      switch (metric) {
        case 'duration':
          return `${value}分钟`
        case 'best_time':
          return `评分: ${value.toFixed(1)}`
        case 'activity':
          return `${value}%`
        default:
          return value.toString()
      }
    },
    
    formatDuration(minutes) {
      if (!minutes) return '0分钟'
      
      const hours = Math.floor(minutes / 60)
      const mins = Math.round(minutes % 60)
      
      if (hours > 0) {
        return `${hours}小时${mins}分钟`
      }
      return `${mins}分钟`
    },
    
    handleViewModeChange() {
      this.loadData()
    },
    
    handleMetricChange() {
      this.loadData()
    },
    
    handleCategoryChange() {
      this.loadData()
    },
    
    refreshData() {
      this.loadData()
    }
  }
}
</script>

<style scoped>
.time-analysis-chart {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.chart-header h3 {
  margin: 0;
  color: #303133;
  font-size: 18px;
  font-weight: 500;
}

.chart-controls {
  display: flex;
  align-items: center;
}

.chart-container {
  height: v-bind(height);
  width: 100%;
}

.chart-summary {
  display: flex;
  justify-content: space-around;
  margin-top: 15px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 6px;
}

.summary-item {
  text-align: center;
}

.summary-label {
  display: block;
  font-size: 12px;
  color: #909399;
  margin-bottom: 5px;
}

.summary-value {
  display: block;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

@media (max-width: 768px) {
  .chart-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .chart-controls {
    margin-top: 10px;
    flex-wrap: wrap;
  }
  
  .chart-container {
    height: 300px;
  }
  
  .chart-summary {
    flex-direction: column;
  }
  
  .summary-item {
    margin-bottom: 10px;
  }
}
</style>
