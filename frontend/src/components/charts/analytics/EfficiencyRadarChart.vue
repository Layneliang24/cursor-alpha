<template>
  <div class="efficiency-radar-chart">
    <div class="chart-header">
      <h3>学习效率分析</h3>
      <div class="chart-controls">
        <el-select
          v-model="selectedPeriod"
          placeholder="时间周期"
          size="small"
          style="width: 120px"
          @change="handlePeriodChange"
        >
          <el-option label="最近7天" value="7d" />
          <el-option label="最近30天" value="30d" />
          <el-option label="最近90天" value="90d" />
        </el-select>
        <el-switch
          v-model="showComparison"
          active-text="对比模式"
          inactive-text="单一模式"
          size="small"
          style="margin-left: 15px"
          @change="handleComparisonChange"
        />
      </div>
    </div>
    <div 
      ref="chartContainer" 
      class="chart-container"
      v-loading="loading"
    ></div>
    <div class="efficiency-metrics" v-if="metricsData">
      <div class="metric-card" v-for="metric in metricsData" :key="metric.name">
        <div class="metric-icon">
          <i :class="metric.icon"></i>
        </div>
        <div class="metric-info">
          <div class="metric-label">{{ metric.label }}</div>
          <div class="metric-value">{{ metric.value }}</div>
          <div class="metric-trend" :class="metric.trend">
            <i :class="getTrendIcon(metric.trend)"></i>
            {{ metric.change }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts'
import { dataAnalysisAPI } from '@/api/english'
import { ElMessage } from 'element-plus'

export default {
  name: 'EfficiencyRadarChart',
  props: {
    height: {
      type: String,
      default: '450px'
    }
  },
  data() {
    return {
      chart: null,
      loading: false,
      selectedPeriod: '30d',
      showComparison: false,
      chartData: null,
      metricsData: null
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
          period: this.selectedPeriod,
          comparison: this.showComparison
        }
        
        const response = await dataAnalysisAPI.getEfficiencyAnalysis(params)
        this.chartData = response.data
        this.metricsData = response.data.metrics
        this.updateChart()
      } catch (error) {
        console.error('加载效率分析数据失败:', error)
        ElMessage.error('加载数据失败，请稍后重试')
      } finally {
        this.loading = false
      }
    },
    
    updateChart() {
      if (!this.chart || !this.chartData) return
      
      const option = {
        title: {
          text: '学习效率雷达图',
          left: 'center',
          textStyle: {
            fontSize: 16,
            fontWeight: 'normal'
          }
        },
        tooltip: {
          trigger: 'item',
          formatter: (params) => {
            const value = params.value
            const name = params.name
            let result = `${name}<br/>`
            
            if (Array.isArray(value)) {
              this.chartData.indicator.forEach((indicator, index) => {
                result += `${indicator.name}: ${this.formatRadarValue(value[index], indicator.key)}<br/>`
              })
            }
            return result
          }
        },
        legend: {
          data: this.chartData.legend || [],
          top: 30
        },
        radar: {
          indicator: this.chartData.indicator || [],
          center: ['50%', '55%'],
          radius: '65%',
          splitNumber: 5,
          shape: 'polygon',
          name: {
            textStyle: {
              color: '#606266',
              fontSize: 12
            }
          },
          splitLine: {
            lineStyle: {
              color: '#e4e7ed'
            }
          },
          splitArea: {
            show: true,
            areaStyle: {
              color: ['rgba(250,250,250,0.1)', 'rgba(200,200,200,0.1)']
            }
          },
          axisLine: {
            lineStyle: {
              color: '#e4e7ed'
            }
          }
        },
        series: [
          {
            name: '学习效率',
            type: 'radar',
            data: this.chartData.series || [],
            itemStyle: {
              color: '#409EFF'
            },
            areaStyle: {
              opacity: 0.3,
              color: new echarts.graphic.RadialGradient(0.5, 0.5, 1, [
                { offset: 0, color: '#409EFF' },
                { offset: 1, color: 'rgba(64, 158, 255, 0.1)' }
              ])
            },
            lineStyle: {
              width: 2,
              color: '#409EFF'
            },
            symbol: 'circle',
            symbolSize: 6
          }
        ]
      }
      
      // 如果是对比模式，添加第二个系列
      if (this.showComparison && this.chartData.comparison) {
        option.series.push({
          name: '对比期间',
          type: 'radar',
          data: this.chartData.comparison || [],
          itemStyle: {
            color: '#67C23A'
          },
          areaStyle: {
            opacity: 0.2,
            color: new echarts.graphic.RadialGradient(0.5, 0.5, 1, [
              { offset: 0, color: '#67C23A' },
              { offset: 1, color: 'rgba(103, 194, 58, 0.1)' }
            ])
          },
          lineStyle: {
            width: 2,
            color: '#67C23A',
            type: 'dashed'
          },
          symbol: 'diamond',
          symbolSize: 6
        })
      }
      
      this.chart.setOption(option, true)
    },
    
    formatRadarValue(value, key) {
      if (!value && value !== 0) return '-'
      
      switch (key) {
        case 'accuracy':
          return `${(value * 100).toFixed(1)}%`
        case 'speed':
          return `${value.toFixed(1)}分/题`
        case 'retention':
          return `${(value * 100).toFixed(1)}%`
        case 'consistency':
          return `${value.toFixed(2)}`
        case 'engagement':
          return `${(value * 100).toFixed(1)}%`
        default:
          return value.toFixed(2)
      }
    },
    
    formatAxisValue(value, metric) {
      return value.toFixed(1)
    },
    
    formatTooltipValue(value, metric) {
      return this.formatRadarValue(value, metric)
    },
    
    getTrendIcon(trend) {
      switch (trend) {
        case 'up':
          return 'el-icon-caret-top'
        case 'down':
          return 'el-icon-caret-bottom'
        default:
          return 'el-icon-minus'
      }
    },
    
    handlePeriodChange() {
      this.loadData()
    },
    
    handleComparisonChange() {
      this.loadData()
    },
    
    handleMetricChange() {
      this.loadData()
    }
  }
}
</script>

<style scoped>
.efficiency-radar-chart {
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

.efficiency-metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-top: 20px;
}

.metric-card {
  display: flex;
  align-items: center;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #409EFF;
}

.metric-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #409EFF;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
}

.metric-icon i {
  color: white;
  font-size: 18px;
}

.metric-info {
  flex: 1;
}

.metric-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.metric-value {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.metric-trend {
  font-size: 12px;
  display: flex;
  align-items: center;
}

.metric-trend.up {
  color: #67C23A;
}

.metric-trend.down {
  color: #F56C6C;
}

.metric-trend.stable {
  color: #909399;
}

.metric-trend i {
  margin-right: 2px;
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
    height: 350px;
  }
  
  .efficiency-metrics {
    grid-template-columns: 1fr;
  }
}
</style>
