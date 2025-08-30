<template>
  <div class="progress-trend-chart">
    <div class="chart-header">
      <h3>学习进度趋势</h3>
      <div class="chart-controls">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          @change="handleDateRangeChange"
          size="small"
        />
        <el-select
          v-model="selectedMetric"
          placeholder="选择指标"
          size="small"
          style="width: 120px; margin-left: 10px"
          @change="handleMetricChange"
        >
          <el-option label="准确率" value="accuracy" />
          <el-option label="掌握度" value="mastery" />
          <el-option label="学习时长" value="duration" />
          <el-option label="练习次数" value="attempts" />
        </el-select>
      </div>
    </div>
    <div 
      ref="chartContainer" 
      class="chart-container"
      v-loading="loading"
    ></div>
  </div>
</template>

<script>
import * as echarts from 'echarts'
import { dataAnalysisAPI } from '@/api/english'
import { ElMessage } from 'element-plus'

export default {
  name: 'ProgressTrendChart',
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
      dateRange: [],
      selectedMetric: 'accuracy',
      chartData: null
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
        const params = {}
        if (this.dateRange && this.dateRange.length === 2) {
          params.start_date = this.dateRange[0]
          params.end_date = this.dateRange[1]
        }
        if (this.selectedMetric) {
          params.metric = this.selectedMetric
        }
        
        const response = await dataAnalysisAPI.getProgressTrend(params)
        this.chartData = response.data
        this.updateChart()
      } catch (error) {
        console.error('加载进度趋势数据失败:', error)
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
            type: 'cross',
            label: {
              backgroundColor: '#6a7985'
            }
          },
          formatter: (params) => {
            let result = `${params[0].axisValue}<br/>`
            params.forEach(param => {
              const value = this.formatValue(param.value, this.selectedMetric)
              result += `${param.seriesName}: ${value}<br/>`
            })
            return result
          }
        },
        legend: {
          data: this.chartData.legend || [],
          top: 30
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          top: '15%',
          containLabel: true
        },
        toolbox: {
          feature: {
            saveAsImage: {
              title: '保存图片'
            },
            dataZoom: {
              title: {
                zoom: '区域缩放',
                back: '区域缩放还原'
              }
            }
          }
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: this.chartData.xAxis || [],
          axisLabel: {
            rotate: 45
          }
        },
        yAxis: {
          type: 'value',
          name: this.getYAxisName(),
          axisLabel: {
            formatter: (value) => this.formatValue(value, this.selectedMetric)
          }
        },
        dataZoom: [
          {
            type: 'inside',
            start: 0,
            end: 100
          },
          {
            start: 0,
            end: 100,
            height: 30,
            bottom: 10
          }
        ],
        series: this.chartData.series || []
      }
      
      this.chart.setOption(option, true)
    },
    
    getChartTitle() {
      const metricNames = {
        accuracy: '准确率趋势',
        mastery: '掌握度趋势', 
        duration: '学习时长趋势',
        attempts: '练习次数趋势'
      }
      return metricNames[this.selectedMetric] || '学习进度趋势'
    },
    
    getYAxisName() {
      const axisNames = {
        accuracy: '准确率 (%)',
        mastery: '掌握度',
        duration: '时长 (分钟)',
        attempts: '次数'
      }
      return axisNames[this.selectedMetric] || ''
    },
    
    formatValue(value, metric) {
      if (!value && value !== 0) return '-'
      
      switch (metric) {
        case 'accuracy':
          return `${(value * 100).toFixed(1)}%`
        case 'mastery':
          return value.toFixed(2)
        case 'duration':
          return `${value.toFixed(1)}分钟`
        case 'attempts':
          return `${value}次`
        default:
          return value.toString()
      }
    },
    
    handleDateRangeChange() {
      this.loadData()
    },
    
    handleMetricChange() {
      this.loadData()
    }
  }
}
</script>

<style scoped>
.progress-trend-chart {
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
}
</style>
