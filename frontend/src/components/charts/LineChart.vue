<template>
  <div class="line-chart">
    <div class="chart-container" ref="chartContainer"></div>
  </div>
</template>

<script>
import { ref, onMounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'

export default {
  name: 'LineChart',
  props: {
    data: {
      type: Array,
      default: () => []
    },
    title: {
      type: String,
      default: '趋势图'
    },
    name: {
      type: String,
      default: '数值'
    },
    suffix: {
      type: String,
      default: ''
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
      const dates = props.data.map(item => item[0])
      const values = props.data.map(item => item[1])

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
          formatter: function (params) {
            const data = params[0]
            return `${data.name}<br/>${data.seriesName}: ${data.value}${props.suffix}`
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
          boundaryGap: false,
          data: dates,
          axisLabel: {
            rotate: 45,
            fontSize: 10
          }
        },
        yAxis: {
          type: 'value',
          name: props.name,
          nameLocation: 'middle',
          nameGap: 30
        },
        series: [{
          name: props.name,
          type: 'line',
          data: values,
          smooth: true,
          lineStyle: {
            color: '#409eff',
            width: 3
          },
          itemStyle: {
            color: '#409eff'
          },
          areaStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [{
                offset: 0, color: 'rgba(64, 158, 255, 0.3)'
              }, {
                offset: 1, color: 'rgba(64, 158, 255, 0.1)'
              }]
            }
          },
          emphasis: {
            focus: 'series'
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
.line-chart {
  width: 100%;
  height: 100%;
}

.chart-container {
  width: 100%;
  height: 300px;
}
</style>

