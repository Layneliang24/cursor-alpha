<template>
  <div ref="chartRef" class="performance-radar-chart" :style="{ height: chartHeight }"></div>
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

  // 雷达图指标
  const indicators = [
    { name: '性能评分', max: 5 },
    { name: '响应速度', max: 1000 },
    { name: '准确率', max: 100 },
    { name: '稳定性', max: 100 },
    { name: '成本效益', max: 100 },
    { name: '易用性', max: 100 }
  ]

  // 为每个模型生成数据
  const seriesData = props.models.map((model, index) => {
    const colors = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272']
    
    // 计算成本效益评分 (性能/成本的比值，归一化到0-100)
    const avgCost = ((model.input_cost_per_token || 0) + (model.output_cost_per_token || 0)) / 2
    const costEfficiency = avgCost > 0 ? Math.min((model.performance_score || 0) / avgCost * 10, 100) : 0

    return {
      name: model.model_name,
      value: [
        model.performance_score || 0, // 性能评分
        Math.min(model.tokens_per_second || 0, 1000), // 响应速度
        (model.accuracy_score || 0) * 100, // 准确率
        (model.reliability_score || 0) * 100, // 稳定性
        costEfficiency, // 成本效益
        (model.ease_of_use_score || 0.8) * 100 // 易用性（默认值）
      ],
      itemStyle: {
        color: colors[index % colors.length]
      },
      areaStyle: {
        color: colors[index % colors.length],
        opacity: 0.1
      }
    }
  })

  return {
    title: {
      text: '模型综合性能对比',
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'bold'
      }
    },
    legend: {
      data: props.models.map(model => model.model_name),
      bottom: 10,
      type: 'scroll'
    },
    radar: {
      indicator: indicators,
      center: ['50%', '55%'],
      radius: '65%',
      axisName: {
        color: '#666',
        fontSize: 12
      },
      splitLine: {
        lineStyle: {
          color: '#e0e0e0'
        }
      },
      splitArea: {
        areaStyle: {
          color: ['#f8f8f8', '#fff'],
          opacity: 0.5
        }
      }
    },
    series: [{
      type: 'radar',
      data: seriesData,
      emphasis: {
        focus: 'series'
      }
    }],
    tooltip: {
      trigger: 'item',
      formatter: function(params) {
        const model = props.models.find(m => m.model_name === params.name)
        if (!model) return ''
        
        return `
          <div style="padding: 8px;">
            <div style="font-weight: bold; margin-bottom: 8px;">${params.name}</div>
            <div>性能评分: ${(model.performance_score || 0).toFixed(1)}/5</div>
            <div>响应速度: ${model.tokens_per_second || 0} tokens/s</div>
            <div>准确率: ${((model.accuracy_score || 0) * 100).toFixed(1)}%</div>
            <div>稳定性: ${((model.reliability_score || 0) * 100).toFixed(1)}%</div>
            <div>提供商: ${model.provider.display_name}</div>
          </div>
        `
      }
    }
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
.performance-radar-chart {
  width: 100%;
  min-height: 300px;
}
</style>
