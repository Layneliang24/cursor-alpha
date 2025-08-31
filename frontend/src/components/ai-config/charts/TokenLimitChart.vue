<template>
  <div ref="chartRef" class="token-limit-chart" :style="{ height: chartHeight }"></div>
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
  const chartData = props.models.map((model, index) => {
    const colors = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272']
    return {
      name: model.model_name,
      value: model.max_tokens || 0,
      provider: model.provider.display_name,
      itemStyle: {
        color: colors[index % colors.length]
      }
    }
  })

  // 按Token数量排序
  chartData.sort((a, b) => b.value - a.value)

  // 创建饼图数据
  const pieData = chartData.map(item => ({
    name: `${item.name}\n${item.value.toLocaleString()}`,
    value: item.value,
    provider: item.provider,
    modelName: item.name,
    itemStyle: item.itemStyle
  }))

  return {
    title: {
      text: '模型Token限制对比',
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'item',
      formatter: function(params) {
        const percentage = params.percent
        return `
          <div style="padding: 8px;">
            <div style="font-weight: bold; margin-bottom: 8px;">${params.data.modelName}</div>
            <div>最大Token: ${params.value.toLocaleString()}</div>
            <div>提供商: ${params.data.provider}</div>
            <div>占比: ${percentage.toFixed(1)}%</div>
          </div>
        `
      }
    },
    legend: {
      type: 'scroll',
      orient: 'vertical',
      right: 10,
      top: 20,
      bottom: 20,
      data: pieData.map(item => item.name),
      textStyle: {
        fontSize: 11
      }
    },
    series: [
      {
        type: 'pie',
        radius: ['30%', '70%'],
        center: ['40%', '50%'],
        data: pieData,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        label: {
          show: true,
          position: 'outside',
          formatter: function(params) {
            return `${params.data.modelName}\n${params.value.toLocaleString()}`
          },
          fontSize: 10
        },
        labelLine: {
          show: true,
          length: 15,
          length2: 10
        }
      }
    ],
    // 添加数据缩放组件（如果需要）
    dataZoom: chartData.length > 10 ? [{
      type: 'inside',
      disabled: false
    }] : undefined
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
.token-limit-chart {
  width: 100%;
  min-height: 300px;
}
</style>
