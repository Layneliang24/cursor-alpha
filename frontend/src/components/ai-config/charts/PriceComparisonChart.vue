<template>
  <div ref="chartRef" class="price-comparison-chart" :style="{ height: chartHeight }"></div>
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

  const modelNames = props.models.map(model => model.model_name)
  const inputCosts = props.models.map(model => (model.input_cost_per_token || 0) * 1000) // 转换为每1K tokens
  const outputCosts = props.models.map(model => (model.output_cost_per_token || 0) * 1000)

  return {
    title: {
      text: '模型价格对比',
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
        let result = `<div style="padding: 8px;"><strong>${params[0].axisValue}</strong><br/>`
        params.forEach(param => {
          result += `<div style="margin: 4px 0;">
            <span style="display: inline-block; width: 10px; height: 10px; background: ${param.color}; margin-right: 8px;"></span>
            ${param.seriesName}: $${param.value.toFixed(3)}/1K tokens
          </div>`
        })
        result += '</div>'
        return result
      }
    },
    legend: {
      data: ['输入Token价格', '输出Token价格'],
      top: 30
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '10%',
      top: '20%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: modelNames,
      axisLabel: {
        rotate: modelNames.length > 4 ? 45 : 0,
        fontSize: 11
      }
    },
    yAxis: {
      type: 'value',
      name: '价格 ($)',
      nameTextStyle: {
        fontSize: 12
      },
      axisLabel: {
        formatter: '${value}'
      }
    },
    series: [
      {
        name: '输入Token价格',
        type: 'bar',
        data: inputCosts,
        itemStyle: {
          color: '#67c23a'
        },
        emphasis: {
          focus: 'series'
        }
      },
      {
        name: '输出Token价格',
        type: 'bar',
        data: outputCosts,
        itemStyle: {
          color: '#e6a23c'
        },
        emphasis: {
          focus: 'series'
        }
      }
    ]
  }
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
.price-comparison-chart {
  width: 100%;
  min-height: 300px;
}
</style>
