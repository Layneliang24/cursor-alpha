<template>
  <div class="metrics-chart">
    <div 
      ref="chartContainer" 
      class="chart-container"
      :class="{ 'chart-loading': loading }"
    ></div>
    <div v-if="loading" class="chart-loading-overlay">
      <el-icon class="is-loading">
        <Loading />
      </el-icon>
      <span>加载中...</span>
    </div>
    <div v-if="!loading && (!data || data.length === 0)" class="chart-empty">
      <i class="el-icon-warning"></i>
      <span>暂无数据</span>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { Loading } from '@element-plus/icons-vue'
import * as echarts from 'echarts/core'
import {
  LineChart,
  BarChart
} from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
  DataZoomComponent
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

// 注册必需的组件
echarts.use([
  LineChart,
  BarChart,
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
  DataZoomComponent,
  CanvasRenderer
])

export default {
  name: 'MetricsChart',
  components: {
    Loading
  },
  props: {
    data: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    },
    chartType: {
      type: String,
      default: 'line', // line, area, bar
      validator: (value) => ['line', 'area', 'bar'].includes(value)
    },
    yAxisLabel: {
      type: String,
      default: ''
    },
    yAxisMax: {
      type: Number,
      default: null
    },
    height: {
      type: String,
      default: '300px'
    },
    smooth: {
      type: Boolean,
      default: true
    },
    showDataZoom: {
      type: Boolean,
      default: false
    }
  },
  emits: ['chart-ready'],
  setup(props, { emit, expose }) {
    const chartContainer = ref()
    let chartInstance = null
    let resizeObserver = null
    
    // 创建图表
    const createChart = () => {
      if (!chartContainer.value) return
      
      // 销毁已存在的图表
      if (chartInstance) {
        chartInstance.dispose()
      }
      
      // 创建新图表实例
      chartInstance = echarts.init(chartContainer.value)
      
      // 设置图表配置
      updateChart()
      
      // 监听窗口大小变化
      setupResize()
      
      emit('chart-ready', chartInstance)
    }
    
    // 更新图表数据
    const updateChart = () => {
      if (!chartInstance || !props.data || props.data.length === 0) return
      
      const option = getChartOption()
      chartInstance.setOption(option, true)
    }
    
    // 获取图表配置
    const getChartOption = () => {
      const xAxisData = props.data.map(item => 
        new Date(item.timestamp).toLocaleTimeString('zh-CN', {
          hour: '2-digit',
          minute: '2-digit'
        })
      )
      const seriesData = props.data.map(item => item.value)
      
      const baseOption = {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross',
            label: {
              backgroundColor: '#6a7985'
            }
          },
          formatter: (params) => {
            if (!params || params.length === 0) return ''
            const param = params[0]
            const timestamp = props.data[param.dataIndex]?.timestamp
            const time = timestamp ? new Date(timestamp).toLocaleString('zh-CN') : ''
            return `${time}<br/>${param.seriesName}: ${param.value} ${getUnit()}`
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: props.showDataZoom ? '15%' : '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: xAxisData,
          axisLabel: {
            color: '#666'
          }
        },
        yAxis: {
          type: 'value',
          name: props.yAxisLabel,
          nameTextStyle: {
            color: '#666'
          },
          max: props.yAxisMax,
          axisLabel: {
            color: '#666',
            formatter: (value) => {
              if (value >= 1000) {
                return (value / 1000).toFixed(1) + 'k'
              }
              return value
            }
          }
        },
        series: [{
          name: props.yAxisLabel,
          type: props.chartType === 'bar' ? 'bar' : 'line',
          data: seriesData,
          smooth: props.smooth && props.chartType !== 'bar',
          areaStyle: props.chartType === 'area' ? {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [{
                offset: 0, color: 'rgba(102, 126, 234, 0.6)'
              }, {
                offset: 1, color: 'rgba(102, 126, 234, 0.1)'
              }]
            }
          } : null,
          lineStyle: {
            color: '#667eea',
            width: 2
          },
          itemStyle: {
            color: '#667eea'
          },
          symbol: 'circle',
          symbolSize: 4,
          emphasis: {
            scale: true,
            itemStyle: {
              color: '#667eea',
              borderColor: '#fff',
              borderWidth: 2
            }
          }
        }]
      }
      
      // 添加数据缩放
      if (props.showDataZoom) {
        baseOption.dataZoom = [
          {
            type: 'inside',
            start: 70,
            end: 100
          },
          {
            start: 70,
            end: 100,
            height: 20,
            bottom: 20
          }
        ]
      }
      
      return baseOption
    }
    
    // 获取单位
    const getUnit = () => {
      if (props.yAxisLabel.includes('时间')) return 'ms'
      if (props.yAxisLabel.includes('率')) return '%'
      if (props.yAxisLabel.includes('数量') || props.yAxisLabel.includes('次数')) return '次'
      return ''
    }
    
    // 设置响应式
    const setupResize = () => {
      if (!chartInstance) return
      
      // 使用ResizeObserver监听容器大小变化
      if (window.ResizeObserver) {
        resizeObserver = new ResizeObserver(() => {
          chartInstance?.resize()
        })
        resizeObserver.observe(chartContainer.value)
      } else {
        // 降级方案：监听窗口大小变化
        window.addEventListener('resize', handleResize)
      }
    }
    
    // 处理窗口大小变化
    const handleResize = () => {
      if (chartInstance) {
        chartInstance.resize()
      }
    }
    
    // 刷新图表
    const refresh = () => {
      if (chartInstance) {
        updateChart()
      }
    }
    
    // 销毁图表
    const dispose = () => {
      if (chartInstance) {
        chartInstance.dispose()
        chartInstance = null
      }
      
      if (resizeObserver) {
        resizeObserver.disconnect()
        resizeObserver = null
      } else {
        window.removeEventListener('resize', handleResize)
      }
    }
    
    // 监听数据变化
    watch(() => props.data, () => {
      nextTick(() => {
        updateChart()
      })
    }, { deep: true })
    
    // 监听loading状态
    watch(() => props.loading, (newLoading) => {
      if (!newLoading && chartInstance) {
        nextTick(() => {
          updateChart()
        })
      }
    })
    
    // 生命周期
    onMounted(() => {
      nextTick(() => {
        createChart()
      })
    })
    
    onUnmounted(() => {
      dispose()
    })
    
    // 暴露方法
    expose({
      refresh,
      dispose,
      getInstance: () => chartInstance
    })
    
    return {
      chartContainer
    }
  }
}
</script>

<style scoped>
.metrics-chart {
  position: relative;
  width: 100%;
  height: v-bind(height);
  min-height: 200px;
}

.chart-container {
  width: 100%;
  height: 100%;
  transition: opacity 0.3s ease;
}

.chart-container.chart-loading {
  opacity: 0.6;
}

.chart-loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background: rgba(255, 255, 255, 0.8);
  z-index: 10;
  gap: 0.5rem;
  color: #666;
  font-size: 0.9rem;
}

.chart-empty {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: #bfbfbf;
  font-size: 0.9rem;
  gap: 0.5rem;
}

.chart-empty i {
  font-size: 2rem;
}

/* 深色模式适配 */
@media (prefers-color-scheme: dark) {
  .chart-loading-overlay {
    background: rgba(45, 45, 45, 0.8);
    color: #ccc;
  }
  
  .chart-empty {
    color: #666;
  }
}
</style>
