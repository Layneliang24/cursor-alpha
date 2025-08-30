<template>
  <div class="mastery-distribution-chart">
    <div class="chart-header">
      <h3>表达掌握分布</h3>
      <div class="chart-controls">
        <el-select
          v-model="selectedCategory"
          placeholder="选择分类"
          size="small"
          style="width: 150px"
          @change="handleCategoryChange"
        >
          <el-option label="全部分类" value="" />
          <el-option label="商务英语" value="business" />
          <el-option label="日常对话" value="daily" />
          <el-option label="学术英语" value="academic" />
        </el-select>
        <el-button
          size="small"
          type="primary"
          @click="refreshData"
          :loading="loading"
          style="margin-left: 10px"
        >
          刷新
        </el-button>
      </div>
    </div>
    <div class="chart-content">
      <div 
        ref="chartContainer" 
        class="chart-container"
        v-loading="loading"
      ></div>
      <div class="chart-legend">
        <div class="legend-item" v-for="item in legendData" :key="item.name">
          <span class="legend-color" :style="{ backgroundColor: item.color }"></span>
          <span class="legend-label">{{ item.name }}</span>
          <span class="legend-value">{{ item.value }}个 ({{ item.percentage }}%)</span>
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
  name: 'MasteryDistributionChart',
  props: {
    height: {
      type: String,
      default: '350px'
    }
  },
  data() {
    return {
      chart: null,
      loading: false,
      selectedCategory: '',
      chartData: null,
      legendData: []
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
        const params = {}
        if (this.selectedCategory) {
          params.category = this.selectedCategory
        }
        
        const response = await dataAnalysisAPI.getMasteryDistribution(params)
        this.chartData = response.data
        this.updateChart()
        this.updateLegend()
      } catch (error) {
        console.error('加载掌握度分布数据失败:', error)
        ElMessage.error('加载数据失败，请稍后重试')
      } finally {
        this.loading = false
      }
    },
    
    updateChart() {
      if (!this.chart || !this.chartData) return
      
      const colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
      
      const option = {
        title: {
          text: '掌握度分布',
          subtext: this.getSubtitle(),
          left: 'center',
          textStyle: {
            fontSize: 16,
            fontWeight: 'normal'
          }
        },
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c}个 ({d}%)'
        },
        color: colors,
        series: [
          {
            name: '掌握度分布',
            type: 'pie',
            radius: ['40%', '70%'],
            center: ['50%', '55%'],
            avoidLabelOverlap: false,
            itemStyle: {
              borderRadius: 10,
              borderColor: '#fff',
              borderWidth: 2
            },
            label: {
              show: false,
              position: 'center'
            },
            emphasis: {
              label: {
                show: true,
                fontSize: 20,
                fontWeight: 'bold',
                formatter: '{b}\n{d}%'
              },
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            },
            labelLine: {
              show: false
            },
            data: this.chartData.data || []
          }
        ]
      }
      
      this.chart.setOption(option, true)
      
      // 添加点击事件
      this.chart.off('click')
      this.chart.on('click', (params) => {
        this.$emit('segment-click', {
          name: params.name,
          value: params.value,
          category: this.selectedCategory
        })
      })
    },
    
    updateLegend() {
      if (!this.chartData || !this.chartData.data) {
        this.legendData = []
        return
      }
      
      const colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
      const total = this.chartData.data.reduce((sum, item) => sum + item.value, 0)
      
      this.legendData = this.chartData.data.map((item, index) => ({
        name: item.name,
        value: item.value,
        percentage: total > 0 ? ((item.value / total) * 100).toFixed(1) : '0.0',
        color: colors[index % colors.length]
      }))
    },
    
    getSubtitle() {
      if (!this.chartData || !this.chartData.summary) return ''
      
      const { total_expressions, avg_mastery } = this.chartData.summary
      return `总计 ${total_expressions} 个表达 | 平均掌握度 ${avg_mastery?.toFixed(2) || '0.00'}`
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
.mastery-distribution-chart {
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

.chart-content {
  display: flex;
  align-items: flex-start;
}

.chart-container {
  height: v-bind(height);
  flex: 1;
  min-width: 0;
}

.chart-legend {
  width: 200px;
  margin-left: 20px;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 6px;
}

.legend-item {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  font-size: 14px;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-right: 8px;
  flex-shrink: 0;
}

.legend-label {
  flex: 1;
  color: #606266;
}

.legend-value {
  color: #303133;
  font-weight: 500;
  margin-left: 5px;
}

@media (max-width: 768px) {
  .chart-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .chart-controls {
    margin-top: 10px;
  }
  
  .chart-content {
    flex-direction: column;
  }
  
  .chart-legend {
    width: 100%;
    margin-left: 0;
    margin-top: 15px;
  }
  
  .chart-container {
    height: 250px;
  }
}
</style>
