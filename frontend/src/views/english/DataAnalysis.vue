<template>
  <div class="data-analysis">
    <!-- 页面头部 -->
    <div class="page-header">
      <el-button @click="goBack" icon="ArrowLeft" type="primary">返回</el-button>
      <h1>数据分析</h1>
      <el-date-picker
        v-model="dateRange"
        type="daterange"
        range-separator="至"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
        @change="handleDateChange"
        :shortcuts="dateShortcuts"
      />
    </div>
    
    <!-- 数据概览 -->
    <div class="data-overview" v-if="overview.total_exercises > 0">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card>
            <div class="stat-item">
              <div class="stat-value">{{ overview.total_exercises }}</div>
              <div class="stat-label">总练习次数</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card>
            <div class="stat-item">
              <div class="stat-value">{{ overview.total_words }}</div>
              <div class="stat-label">总练习单词数</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card>
            <div class="stat-item">
              <div class="stat-value">{{ overview.avg_wpm }}</div>
              <div class="stat-label">平均WPM</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card>
            <div class="stat-item">
              <div class="stat-value">{{ overview.avg_accuracy }}%</div>
              <div class="stat-label">平均正确率</div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <!-- 无数据提示 -->
    <div v-if="overview.total_exercises === 0" class="no-data">
      <el-empty description="暂无练习数据" />
    </div>
    
    <!-- 图表区域 -->
    <div class="charts-container" v-else>
      <!-- 练习次数热力图 -->
      <el-card class="chart-card">
        <template #header>
          <span>过去一年练习次数热力图</span>
        </template>
        <HeatmapChart :data="exerciseHeatmap" />
      </el-card>
      
      <!-- 练习单词数热力图 -->
      <el-card class="chart-card">
        <template #header>
          <span>过去一年练习单词数热力图</span>
        </template>
        <HeatmapChart :data="wordHeatmap" />
      </el-card>
      
      <!-- WPM趋势图 -->
      <el-card class="chart-card">
        <template #header>
          <span>过去一年WPM趋势图</span>
        </template>
        <LineChart :data="wpmTrend" title="WPM" />
      </el-card>
      
      <!-- 正确率趋势图 -->
      <el-card class="chart-card">
        <template #header>
          <span>过去一年正确率趋势图</span>
        </template>
        <LineChart :data="accuracyTrend" title="正确率(%)" suffix="%" />
      </el-card>
      
      <!-- 按键错误分析 -->
      <el-card class="chart-card">
        <template #header>
          <span>按键错误次数排行</span>
        </template>
        <KeyboardErrorChart :data="keyErrorStats" />
      </el-card>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import HeatmapChart from '@/components/charts/HeatmapChart.vue'
import LineChart from '@/components/charts/LineChart.vue'
import KeyboardErrorChart from '@/components/charts/KeyboardErrorChart.vue'
import { dataAnalysisAPI } from '@/api/english'

export default {
  name: 'DataAnalysis',
  components: {
    HeatmapChart,
    LineChart,
    KeyboardErrorChart
  },
  setup() {
    const router = useRouter()
    const dateRange = ref([])
    const overview = ref({
      total_exercises: 0,
      total_words: 0,
      avg_wpm: 0,
      avg_accuracy: 0
    })
    const exerciseHeatmap = ref([])
    const wordHeatmap = ref([])
    const wpmTrend = ref([])
    const accuracyTrend = ref([])
    const keyErrorStats = ref([])
    const loading = ref(false)

    // 日期快捷选项
    const dateShortcuts = [
      {
        text: '最近一周',
        value: () => {
          const end = new Date()
          const start = new Date()
          start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)
          return [start, end]
        }
      },
      {
        text: '最近一个月',
        value: () => {
          const end = new Date()
          const start = new Date()
          start.setTime(start.getTime() - 3600 * 1000 * 24 * 30)
          return [start, end]
        }
      },
      {
        text: '最近三个月',
        value: () => {
          const end = new Date()
          const start = new Date()
          start.setTime(start.getTime() - 3600 * 1000 * 24 * 90)
          return [start, end]
        }
      },
      {
        text: '最近一年',
        value: () => {
          const end = new Date()
          const start = new Date()
          start.setTime(start.getTime() - 3600 * 1000 * 24 * 365)
          return [start, end]
        }
      }
    ]

    const goBack = () => {
      router.push('/english/typing-practice')
    }

    const loadData = async () => {
      if (loading.value) return
      
      loading.value = true
      try {
        const [startDate, endDate] = dateRange.value || [
          new Date(Date.now() - 365 * 24 * 60 * 60 * 1000),
          new Date()
        ]

        const startDateStr = startDate.toISOString().split('T')[0]
        const endDateStr = endDate.toISOString().split('T')[0]

        const [
          overviewData,
          exerciseData,
          wordData,
          wpmData,
          accuracyData,
          keyErrorData
        ] = await Promise.all([
          dataAnalysisAPI.getOverview({ start_date: startDateStr, end_date: endDateStr }),
          dataAnalysisAPI.getExerciseHeatmap({ start_date: startDateStr, end_date: endDateStr }),
          dataAnalysisAPI.getWordHeatmap({ start_date: startDateStr, end_date: endDateStr }),
          dataAnalysisAPI.getWpmTrend({ start_date: startDateStr, end_date: endDateStr }),
          dataAnalysisAPI.getAccuracyTrend({ start_date: startDateStr, end_date: endDateStr }),
          dataAnalysisAPI.getKeyErrorStats()
        ])

        if (overviewData.success) {
          overview.value = overviewData.data
        }
        if (exerciseData.success) {
          exerciseHeatmap.value = exerciseData.data
        }
        if (wordData.success) {
          wordHeatmap.value = wordData.data
        }
        if (wpmData.success) {
          wpmTrend.value = wpmData.data
        }
        if (accuracyData.success) {
          accuracyTrend.value = accuracyData.data
        }
        if (keyErrorData.success) {
          keyErrorStats.value = keyErrorData.data
        }
      } catch (error) {
        console.error('加载数据失败:', error)
        ElMessage.error('加载数据失败，请稍后重试')
      } finally {
        loading.value = false
      }
    }

    const handleDateChange = () => {
      loadData()
    }

    onMounted(() => {
      // 默认加载最近一年的数据
      dateRange.value = [
        new Date(Date.now() - 365 * 24 * 60 * 60 * 1000),
        new Date()
      ]
      loadData()
    })

    return {
      dateRange,
      overview,
      exerciseHeatmap,
      wordHeatmap,
      wpmTrend,
      accuracyTrend,
      keyErrorStats,
      dateShortcuts,
      goBack,
      handleDateChange
    }
  }
}
</script>

<style scoped>
.data-analysis {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 30px;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.page-header h1 {
  margin: 0;
  color: #303133;
  font-size: 24px;
  font-weight: bold;
}

.data-overview {
  margin-bottom: 30px;
}

.stat-item {
  text-align: center;
  padding: 20px;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #606266;
}

.no-data {
  text-align: center;
  padding: 60px 20px;
}

.charts-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.chart-card {
  margin-bottom: 20px;
}

.chart-card :deep(.el-card__header) {
  background: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
}

.chart-card :deep(.el-card__header span) {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.chart-card :deep(.el-card__body) {
  padding: 20px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .data-analysis {
    padding: 10px;
  }
  
  .page-header {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }
  
  .page-header h1 {
    text-align: center;
  }
  
  .stat-value {
    font-size: 24px;
  }
}
</style>

  <div class="data-analysis">
    <!-- 页面头部 -->
    <div class="page-header">
      <el-button @click="goBack" icon="ArrowLeft" type="primary">返回</el-button>
      <h1>数据分析</h1>
      <el-date-picker
        v-model="dateRange"
        type="daterange"
        range-separator="至"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
        @change="handleDateChange"
        :shortcuts="dateShortcuts"
      />
    </div>
    
    <!-- 数据概览 -->
    <div class="data-overview" v-if="overview.total_exercises > 0">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card>
            <div class="stat-item">
              <div class="stat-value">{{ overview.total_exercises }}</div>
              <div class="stat-label">总练习次数</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card>
            <div class="stat-item">
              <div class="stat-value">{{ overview.total_words }}</div>
              <div class="stat-label">总练习单词数</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card>
            <div class="stat-item">
              <div class="stat-value">{{ overview.avg_wpm }}</div>
              <div class="stat-label">平均WPM</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card>
            <div class="stat-item">
              <div class="stat-value">{{ overview.avg_accuracy }}%</div>
              <div class="stat-label">平均正确率</div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <!-- 无数据提示 -->
    <div v-if="overview.total_exercises === 0" class="no-data">
      <el-empty description="暂无练习数据" />
    </div>
    
    <!-- 图表区域 -->
    <div class="charts-container" v-else>
      <!-- 练习次数热力图 -->
      <el-card class="chart-card">
        <template #header>
          <span>过去一年练习次数热力图</span>
        </template>
        <HeatmapChart :data="exerciseHeatmap" />
      </el-card>
      
      <!-- 练习单词数热力图 -->
      <el-card class="chart-card">
        <template #header>
          <span>过去一年练习单词数热力图</span>
        </template>
        <HeatmapChart :data="wordHeatmap" />
      </el-card>
      
      <!-- WPM趋势图 -->
      <el-card class="chart-card">
        <template #header>
          <span>过去一年WPM趋势图</span>
        </template>
        <LineChart :data="wpmTrend" title="WPM" />
      </el-card>
      
      <!-- 正确率趋势图 -->
      <el-card class="chart-card">
        <template #header>
          <span>过去一年正确率趋势图</span>
        </template>
        <LineChart :data="accuracyTrend" title="正确率(%)" suffix="%" />
      </el-card>
      
      <!-- 按键错误分析 -->
      <el-card class="chart-card">
        <template #header>
          <span>按键错误次数排行</span>
        </template>
        <KeyboardErrorChart :data="keyErrorStats" />
      </el-card>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import HeatmapChart from '@/components/charts/HeatmapChart.vue'
import LineChart from '@/components/charts/LineChart.vue'
import KeyboardErrorChart from '@/components/charts/KeyboardErrorChart.vue'
import { dataAnalysisAPI } from '@/api/english'

export default {
  name: 'DataAnalysis',
  components: {
    HeatmapChart,
    LineChart,
    KeyboardErrorChart
  },
  setup() {
    const router = useRouter()
    const dateRange = ref([])
    const overview = ref({
      total_exercises: 0,
      total_words: 0,
      avg_wpm: 0,
      avg_accuracy: 0
    })
    const exerciseHeatmap = ref([])
    const wordHeatmap = ref([])
    const wpmTrend = ref([])
    const accuracyTrend = ref([])
    const keyErrorStats = ref([])
    const loading = ref(false)

    // 日期快捷选项
    const dateShortcuts = [
      {
        text: '最近一周',
        value: () => {
          const end = new Date()
          const start = new Date()
          start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)
          return [start, end]
        }
      },
      {
        text: '最近一个月',
        value: () => {
          const end = new Date()
          const start = new Date()
          start.setTime(start.getTime() - 3600 * 1000 * 24 * 30)
          return [start, end]
        }
      },
      {
        text: '最近三个月',
        value: () => {
          const end = new Date()
          const start = new Date()
          start.setTime(start.getTime() - 3600 * 1000 * 24 * 90)
          return [start, end]
        }
      },
      {
        text: '最近一年',
        value: () => {
          const end = new Date()
          const start = new Date()
          start.setTime(start.getTime() - 3600 * 1000 * 24 * 365)
          return [start, end]
        }
      }
    ]

    const goBack = () => {
      router.push('/english/typing-practice')
    }

    const loadData = async () => {
      if (loading.value) return
      
      loading.value = true
      try {
        const [startDate, endDate] = dateRange.value || [
          new Date(Date.now() - 365 * 24 * 60 * 60 * 1000),
          new Date()
        ]

        const startDateStr = startDate.toISOString().split('T')[0]
        const endDateStr = endDate.toISOString().split('T')[0]

        const [
          overviewData,
          exerciseData,
          wordData,
          wpmData,
          accuracyData,
          keyErrorData
        ] = await Promise.all([
          dataAnalysisAPI.getOverview({ start_date: startDateStr, end_date: endDateStr }),
          dataAnalysisAPI.getExerciseHeatmap({ start_date: startDateStr, end_date: endDateStr }),
          dataAnalysisAPI.getWordHeatmap({ start_date: startDateStr, end_date: endDateStr }),
          dataAnalysisAPI.getWpmTrend({ start_date: startDateStr, end_date: endDateStr }),
          dataAnalysisAPI.getAccuracyTrend({ start_date: startDateStr, end_date: endDateStr }),
          dataAnalysisAPI.getKeyErrorStats()
        ])

        if (overviewData.success) {
          overview.value = overviewData.data
        }
        if (exerciseData.success) {
          exerciseHeatmap.value = exerciseData.data
        }
        if (wordData.success) {
          wordHeatmap.value = wordData.data
        }
        if (wpmData.success) {
          wpmTrend.value = wpmData.data
        }
        if (accuracyData.success) {
          accuracyTrend.value = accuracyData.data
        }
        if (keyErrorData.success) {
          keyErrorStats.value = keyErrorData.data
        }
      } catch (error) {
        console.error('加载数据失败:', error)
        ElMessage.error('加载数据失败，请稍后重试')
      } finally {
        loading.value = false
      }
    }

    const handleDateChange = () => {
      loadData()
    }

    onMounted(() => {
      // 默认加载最近一年的数据
      dateRange.value = [
        new Date(Date.now() - 365 * 24 * 60 * 60 * 1000),
        new Date()
      ]
      loadData()
    })

    return {
      dateRange,
      overview,
      exerciseHeatmap,
      wordHeatmap,
      wpmTrend,
      accuracyTrend,
      keyErrorStats,
      dateShortcuts,
      goBack,
      handleDateChange
    }
  }
}
</script>

<style scoped>
.data-analysis {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 30px;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.page-header h1 {
  margin: 0;
  color: #303133;
  font-size: 24px;
  font-weight: bold;
}

.data-overview {
  margin-bottom: 30px;
}

.stat-item {
  text-align: center;
  padding: 20px;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #606266;
}

.no-data {
  text-align: center;
  padding: 60px 20px;
}

.charts-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.chart-card {
  margin-bottom: 20px;
}

.chart-card :deep(.el-card__header) {
  background: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
}

.chart-card :deep(.el-card__header span) {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.chart-card :deep(.el-card__body) {
  padding: 20px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .data-analysis {
    padding: 10px;
  }
  
  .page-header {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }
  
  .page-header h1 {
    text-align: center;
  }
  
  .stat-value {
    font-size: 24px;
  }
}
</style>

