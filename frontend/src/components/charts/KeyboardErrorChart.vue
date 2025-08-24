<template>
  <div class="keyboard-error-chart">
    <div class="chart-container" ref="chartContainer"></div>
  </div>
</template>

<script>
import { ref, onMounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'

export default {
  name: 'KeyboardErrorChart',
  props: {
    data: {
      type: Array,
      default: () => []
    },
    title: {
      type: String,
      default: '按键错误统计'
    }
  },
  setup(props) {
    const chartContainer = ref(null)
    let chart = null

    const initChart = () => {
      if (!chartContainer.value) return

      // 销毁旧图表
      if (chart) {
        chart.dispose()
      }

      // 创建新图表
      chart = echarts.init(chartContainer.value)

      // 处理数据
      if (!props.data || !Array.isArray(props.data)) {
        return
      }
      const keys = props.data.map(item => item.name)
      const values = props.data.map(item => item.value)

      // 配置选项
      const option = {
        title: {
          text: props.title,
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
          formatter: function (params) {
            const data = params[0]
            return `${data.name}<br/>错误次数: ${data.value}`
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: keys,
          axisLabel: {
            rotate: 45,
            fontSize: 10
          }
        },
        yAxis: {
          type: 'value',
          name: '错误次数',
          nameLocation: 'middle',
          nameGap: 30
        },
        series: [{
          name: '错误次数',
          type: 'bar',
          data: values,
          itemStyle: {
            color: function(params) {
              // 根据错误次数设置颜色深浅
              const value = params.value
              if (value > 20) {
                return '#ff4757'
              } else if (value > 10) {
                return '#ff6b6b'
              } else if (value > 5) {
                return '#ffa502'
              } else {
                return '#2ed573'
              }
            }
          },
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }]
      }

      chart.setOption(option)
    }

    const handleResize = () => {
      if (chart) {
        chart.resize()
      }
    }

    onMounted(() => {
      nextTick(() => {
        initChart()
        window.addEventListener('resize', handleResize)
      })
    })

    watch(() => props.data, () => {
      nextTick(() => {
        initChart()
      })
    }, { deep: true })

    watch(() => props.title, () => {
      if (chart) {
        chart.setOption({
          title: {
            text: props.title
          }
        })
      }
    })

    return {
      chartContainer
    }
  }
}
</script>

<style scoped>
.keyboard-error-chart {
  width: 100%;
  height: 100%;
}

.chart-container {
  width: 100%;
  height: 300px;
}
</style>

