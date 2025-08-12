<template>
  <div class="learning-chart">
    <div ref="chartContainer" style="width: 100%; height: 300px;"></div>
  </div>
</template>

<script>
import { ref, onMounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'

export default {
  name: 'LearningChart',
  props: {
    data: {
      type: Array,
      default: () => []
    }
  },
  setup(props) {
    const chartContainer = ref(null)
    let chartInstance = null

    const initChart = async () => {
      await nextTick()
      if (!chartContainer.value) return

      chartInstance = echarts.init(chartContainer.value)
      updateChart()
    }

    const updateChart = () => {
      if (!chartInstance || !props.data.length) return

      const dates = props.data.map(item => {
        const date = new Date(item.date)
        return `${date.getMonth() + 1}/${date.getDate()}`
      })
      
      const wordsLearned = props.data.map(item => item.words_learned)
      const wordsReviewed = props.data.map(item => item.words_reviewed)
      const practiceCount = props.data.map(item => item.practice_count)
      const accuracyRate = props.data.map(item => item.accuracy_rate)

      const option = {
        title: {
          text: '学习进度趋势',
          left: 'center',
          textStyle: {
            color: '#303133',
            fontSize: 16,
            fontWeight: 'normal'
          }
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross'
          },
          formatter: function(params) {
            let result = `${params[0].axisValue}<br/>`
            params.forEach(param => {
              const unit = param.seriesName === '正确率' ? '%' : 
                          param.seriesName === '学习时长' ? '分钟' : '个'
              result += `${param.marker}${param.seriesName}: ${param.value}${unit}<br/>`
            })
            return result
          }
        },
        legend: {
          data: ['学习单词', '复习单词', '练习次数', '正确率'],
          top: 30,
          textStyle: {
            color: '#606266'
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          top: '15%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: dates,
          axisLine: {
            lineStyle: {
              color: '#E4E7ED'
            }
          },
          axisLabel: {
            color: '#909399'
          }
        },
        yAxis: [
          {
            type: 'value',
            name: '数量',
            position: 'left',
            axisLine: {
              lineStyle: {
                color: '#E4E7ED'
              }
            },
            axisLabel: {
              color: '#909399'
            },
            splitLine: {
              lineStyle: {
                color: '#F2F6FC'
              }
            }
          },
          {
            type: 'value',
            name: '正确率(%)',
            position: 'right',
            min: 0,
            max: 100,
            axisLine: {
              lineStyle: {
                color: '#E4E7ED'
              }
            },
            axisLabel: {
              color: '#909399',
              formatter: '{value}%'
            }
          }
        ],
        series: [
          {
            name: '学习单词',
            type: 'line',
            smooth: true,
            data: wordsLearned,
            lineStyle: {
              color: '#409EFF',
              width: 3
            },
            itemStyle: {
              color: '#409EFF'
            },
            areaStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
                { offset: 1, color: 'rgba(64, 158, 255, 0.1)' }
              ])
            }
          },
          {
            name: '复习单词',
            type: 'line',
            smooth: true,
            data: wordsReviewed,
            lineStyle: {
              color: '#67C23A',
              width: 3
            },
            itemStyle: {
              color: '#67C23A'
            },
            areaStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: 'rgba(103, 194, 58, 0.3)' },
                { offset: 1, color: 'rgba(103, 194, 58, 0.1)' }
              ])
            }
          },
          {
            name: '练习次数',
            type: 'line',
            smooth: true,
            data: practiceCount,
            lineStyle: {
              color: '#E6A23C',
              width: 3
            },
            itemStyle: {
              color: '#E6A23C'
            }
          },
          {
            name: '正确率',
            type: 'line',
            smooth: true,
            yAxisIndex: 1,
            data: accuracyRate,
            lineStyle: {
              color: '#F56C6C',
              width: 3,
              type: 'dashed'
            },
            itemStyle: {
              color: '#F56C6C'
            }
          }
        ]
      }

      chartInstance.setOption(option)
    }

    const resizeChart = () => {
      if (chartInstance) {
        chartInstance.resize()
      }
    }

    // 监听数据变化
    watch(() => props.data, updateChart, { deep: true })

    // 监听窗口大小变化
    onMounted(() => {
      initChart()
      window.addEventListener('resize', resizeChart)
    })

    // 清理
    const cleanup = () => {
      if (chartInstance) {
        chartInstance.dispose()
        chartInstance = null
      }
      window.removeEventListener('resize', resizeChart)
    }

    return {
      chartContainer,
      cleanup
    }
  },
  beforeUnmount() {
    this.cleanup()
  }
}
</script>

<style scoped>
.learning-chart {
  width: 100%;
  height: 100%;
}
</style>
