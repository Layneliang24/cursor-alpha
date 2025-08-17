<template>
  <div class="heatmap-chart">
    <div class="chart-container" ref="chartContainer"></div>
  </div>
</template>

<script>
import { ref, onMounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'

export default {
  name: 'HeatmapChart',
  props: {
    data: {
      type: Array,
      default: () => []
    },
    title: {
      type: String,
      default: '热力图'
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
      const processedData = props.data.map(item => [
        item.date,
        item.count,
        item.level
      ])

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
          position: 'top',
          formatter: function (params) {
            return `${params.data[0]}<br/>数量: ${params.data[1]}`
          }
        },
        grid: {
          height: '70%',
          top: '15%'
        },
        xAxis: {
          type: 'category',
          data: getMonthLabels(),
          splitArea: {
            show: true
          }
        },
        yAxis: {
          type: 'category',
          data: getWeekLabels(),
          splitArea: {
            show: true
          }
        },
        visualMap: {
          min: 0,
          max: 10,
          calculable: true,
          orient: 'horizontal',
          left: 'center',
          bottom: '5%',
          inRange: {
            color: ['#ebedf0', '#c6e48b', '#7bc96f', '#239a3b', '#196127']
          }
        },
        series: [{
          name: '数据',
          type: 'heatmap',
          data: processedData,
          label: {
            show: false
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

    const getMonthLabels = () => {
      const months = []
      const currentDate = new Date()
      for (let i = 11; i >= 0; i--) {
        const date = new Date(currentDate.getFullYear(), currentDate.getMonth() - i, 1)
        months.push(date.toLocaleDateString('zh-CN', { month: 'short' }))
      }
      return months
    }

    const getWeekLabels = () => {
      return ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
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
.heatmap-chart {
  width: 100%;
  height: 100%;
}

.chart-container {
  width: 100%;
  height: 300px;
}
</style>

  <div class="heatmap-chart">
    <div class="chart-container" ref="chartContainer"></div>
  </div>
</template>

<script>
import { ref, onMounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'

export default {
  name: 'HeatmapChart',
  props: {
    data: {
      type: Array,
      default: () => []
    },
    title: {
      type: String,
      default: '热力图'
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
      const processedData = props.data.map(item => [
        item.date,
        item.count,
        item.level
      ])

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
          position: 'top',
          formatter: function (params) {
            return `${params.data[0]}<br/>数量: ${params.data[1]}`
          }
        },
        grid: {
          height: '70%',
          top: '15%'
        },
        xAxis: {
          type: 'category',
          data: getMonthLabels(),
          splitArea: {
            show: true
          }
        },
        yAxis: {
          type: 'category',
          data: getWeekLabels(),
          splitArea: {
            show: true
          }
        },
        visualMap: {
          min: 0,
          max: 10,
          calculable: true,
          orient: 'horizontal',
          left: 'center',
          bottom: '5%',
          inRange: {
            color: ['#ebedf0', '#c6e48b', '#7bc96f', '#239a3b', '#196127']
          }
        },
        series: [{
          name: '数据',
          type: 'heatmap',
          data: processedData,
          label: {
            show: false
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

    const getMonthLabels = () => {
      const months = []
      const currentDate = new Date()
      for (let i = 11; i >= 0; i--) {
        const date = new Date(currentDate.getFullYear(), currentDate.getMonth() - i, 1)
        months.push(date.toLocaleDateString('zh-CN', { month: 'short' }))
      }
      return months
    }

    const getWeekLabels = () => {
      return ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
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
.heatmap-chart {
  width: 100%;
  height: 100%;
}

.chart-container {
  width: 100%;
  height: 300px;
}
</style>

