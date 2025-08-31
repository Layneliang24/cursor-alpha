<template>
  <div ref="chartRef" class="response-time-chart" :style="{ height: chartHeight }"></div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'

// Props
const props = defineProps({
  models: {
    type: Array,
    default: () => []
  },
  height: {
    type: String,
    default: '300px'
  }
})

// 响应式数据
const chartRef = ref(null)
const chartInstance = ref(null)
const chartHeight = ref(props.height)

// 图表配置
const getChartOption = () => {
  if (!props.models || props.models.length === 0) {
    return {
      title: {
        text: '暂无数据',
        left: 'center',
        top: 'middle',
        textStyle: {
          color: '#999',
          fontSize: 14
        }
      }
    }
  }

  // 准备数据
  const chartData = props.models.map((model, index) => ({
    name: model.model_name,
    value: model.avg_response_time || 0,
    provider: model.provider.display_name,
    itemStyle: {
      color: getColorByResponseTime(model.avg_response_time || 0)
    }
  }))

  // 按响应时间排序
  chartData.sort((a, b) => a.value - b.value)

  return {
    title: {
      text: '模型响应时间对比',
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: function(params) {
        const data = params[0]
        const model = props.models.find(m => m.model_name === data.name)
        return `
          <div style="padding: 8px;">
            <div style="font-weight: bold; margin-bottom: 8px;">${data.name}</div>
            <div>响应时间: ${data.value}ms</div>
            <div>提供商: ${data.data.provider}</div>
            <div>性能等级: ${getPerformanceLevel(data.value)}</div>
            ${model ? `<div>性能评分: ${(model.performance_score || 0).toFixed(1)}/5</div>` : ''}
          </div>
        `
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      top: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: chartData.map(item => item.name),
      axisLabel: {
        rotate: chartData.length > 4 ? 45 : 0,
        fontSize: 11,
        interval: 0
      }
    },
    yAxis: {
      type: 'value',
      name: '响应时间 (ms)',
      nameTextStyle: {
        fontSize: 12
      },
      axisLabel: {
        formatter: '{value}ms'
      }
    },
    series: [
      {
        type: 'bar',
        data: chartData,
        emphasis: {
          focus: 'series'
        },
        label: {
          show: true,
          position: 'top',
          formatter: '{c}ms',
          fontSize: 10
        },
        markLine: {
          data: [
            {
              type: 'average',
              name: '平均值',
              lineStyle: {
                color: '#909399',
                type: 'dashed'
              },
              label: {
                formatter: '平均: {c}ms'
              }
            }
          ]
        }
      }
    ],
    visualMap: {
      show: false,
      type: 'piecewise',
      pieces: [
        { min: 0, max: 100, color: '#67c23a' }, // 优秀 - 绿色
        { min: 100, max: 300, color: '#e6a23c' }, // 良好 - 橙色
        { min: 300, max: 1000, color: '#f56c6c' }, // 一般 - 红色
        { min: 1000, color: '#909399' } // 较慢 - 灰色
      ]
    }
  }
}

// 根据响应时间获取颜色
const getColorByResponseTime = (responseTime) => {
  if (responseTime <= 100) return '#67c23a' // 优秀 - 绿色
  if (responseTime <= 300) return '#e6a23c' // 良好 - 橙色
  if (responseTime <= 1000) return '#f56c6c' // 一般 - 红色
  return '#909399' // 较慢 - 灰色
}

// 获取性能等级
const getPerformanceLevel = (responseTime) => {
  if (responseTime <= 100) return '优秀'
  if (responseTime <= 300) return '良好'
  if (responseTime <= 1000) return '一般'
  return '较慢'
}

// 初始化图表
const initChart = async () => {
  await nextTick()
  if (!chartRef.value) return

  chartInstance.value = echarts.init(chartRef.value)
  updateChart()
  
  // 监听窗口大小变化
  window.addEventListener('resize', handleResize)
}

// 更新图表
const updateChart = () => {
  if (!chartInstance.value) return
  
  const option = getChartOption()
  chartInstance.value.setOption(option, true)
}

// 处理窗口大小变化
const handleResize = () => {
  if (chartInstance.value) {
    chartInstance.value.resize()
  }
}

// 生命周期
onMounted(() => {
  initChart()
})

onUnmounted(() => {
  if (chartInstance.value) {
    chartInstance.value.dispose()
  }
  window.removeEventListener('resize', handleResize)
})

// 监听数据变化
watch(() => props.models, () => {
  updateChart()
}, { deep: true })

watch(() => props.height, (newHeight) => {
  chartHeight.value = newHeight
  nextTick(() => {
    handleResize()
  })
})
</script>

<style scoped lang="scss">
.response-time-chart {
  width: 100%;
  min-height: 300px;
}
</style>
