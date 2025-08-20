<template>
  <div class="data-analysis">
    <!-- 页面头部 -->
    <div class="page-header">
      <el-button @click="goBack" icon="ArrowLeft" type="primary">返回</el-button>
      <h1>数据分析</h1>
      <div class="header-controls">
        <el-button 
          @click="refreshData" 
          icon="Refresh" 
          type="primary" 
          :loading="loading"
        >
          刷新数据
        </el-button>
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          @change="handleDateChange"
          :shortcuts="dateShortcuts"
          style="width: 280px;"
        />
      </div>
    </div>
    
    <!-- 数据概览 -->
    <div class="data-overview" v-if="overview.total_words > 0">
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
    <div v-if="overview.total_words === 0" class="no-data">
      <el-empty description="暂无练习数据" />
    </div>
    
    <!-- 图表区域 -->
    <div class="charts-container" v-else>
      <!-- Windows风格月历热力图 -->
      <el-card class="chart-card">
        <template #header>
          <span>月历练习热力图</span>
        </template>
        <MonthlyCalendarHeatmap 
          :data="monthlyCalendarData" 
          :initial-year="currentYear"
          :initial-month="currentMonth"
          @month-change="handleMonthChange"
          @day-click="handleDayClick"
        />
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
          <span>按键错误热力图</span>
        </template>
        <KeyboardLayoutChart :data="keyErrorStats" />
      </el-card>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import LineChart from '@/components/charts/LineChart.vue'
import KeyboardLayoutChart from '@/components/charts/KeyboardLayoutChart.vue'
import MonthlyCalendarHeatmap from '@/components/charts/MonthlyCalendarHeatmap.vue'
import { dataAnalysisAPI } from '@/api/english'

export default {
  name: 'DataAnalysis',
  components: {
    LineChart,
    KeyboardLayoutChart,
    MonthlyCalendarHeatmap
  },
  setup() {
    const router = useRouter()
    
    // 响应式数据
    const overview = ref({
      total_exercises: 0,
      total_words: 0,
      avg_wpm: 0,
      avg_accuracy: 0
    })
    
    const wpmTrend = ref([])
    const accuracyTrend = ref([])
    const keyErrorStats = ref([])
    
    // 月历热力图相关数据
    const monthlyCalendarData = ref({})
    const currentYear = ref(new Date().getFullYear())
    const currentMonth = ref(new Date().getMonth() + 1)
    
    const dateRange = ref([])
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
    
    // 初始化日期范围（默认最近一年）
    const initDateRange = () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 365)
      dateRange.value = [start, end]
    }
    
    // 获取数据概览
    const fetchOverview = async () => {
      try {
        const startDate = dateRange.value[0]?.toISOString().split('T')[0]
        const endDate = dateRange.value[1]?.toISOString().split('T')[0]
        
        const response = await dataAnalysisAPI.getOverview({
          start_date: startDate,
          end_date: endDate
        })
        
        if (response.success && response.data) {
          overview.value = response.data
        }
      } catch (error) {
        console.error('获取数据概览失败:', error)
        ElMessage.error('获取数据概览失败')
      }
    }
    

    
    // 获取WPM趋势数据
    const fetchWpmTrend = async () => {
      try {
        const startDate = dateRange.value[0]?.toISOString().split('T')[0]
        const endDate = dateRange.value[1]?.toISOString().split('T')[0]
        
        const response = await dataAnalysisAPI.getWpmTrend({
          start_date: startDate,
          end_date: endDate
        })
        
        if (response.success && response.data) {
          wpmTrend.value = response.data
        }
      } catch (error) {
        console.error('获取WPM趋势数据失败:', error)
        ElMessage.error('获取WPM趋势数据失败')
      }
    }
    
    // 获取正确率趋势数据
    const fetchAccuracyTrend = async () => {
      try {
        const startDate = dateRange.value[0]?.toISOString().split('T')[0]
        const endDate = dateRange.value[1]?.toISOString().split('T')[0]
        
        const response = await dataAnalysisAPI.getAccuracyTrend({
          start_date: startDate,
          end_date: endDate
        })
        
        if (response.success && response.data) {
          accuracyTrend.value = response.data
        }
      } catch (error) {
        console.error('获取正确率趋势数据失败:', error)
        ElMessage.error('获取正确率趋势数据失败')
      }
    }
    
    // 获取按键错误统计
    const fetchKeyErrorStats = async () => {
      try {
        const response = await dataAnalysisAPI.getKeyErrorStats()
        
        if (response.success && response.data) {
          keyErrorStats.value = response.data
        }
      } catch (error) {
        console.error('获取按键错误统计失败:', error)
        ElMessage.error('获取按键错误统计失败')
      }
    }
    
    // 获取月历热力图数据
    const fetchMonthlyCalendar = async () => {
      try {
        const response = await dataAnalysisAPI.getMonthlyCalendar({
          year: currentYear.value,
          month: currentMonth.value
        })
        
        if (response.success && response.data) {
          monthlyCalendarData.value = response.data
        }
      } catch (error) {
        console.error('获取月历热力图数据失败:', error)
        ElMessage.error('获取月历热力图数据失败')
      }
    }
    
    // 加载所有数据
    const loadData = async () => {
      loading.value = true
      try {
        await Promise.all([
          fetchOverview(),
          fetchWpmTrend(),
          fetchAccuracyTrend(),
          fetchKeyErrorStats(),
          fetchMonthlyCalendar()
        ])
      } catch (error) {
        console.error('加载数据失败:', error)
        ElMessage.error('加载数据失败')
      } finally {
        loading.value = false
      }
    }
    
    // 处理日期变化
    const handleDateChange = () => {
      loadData()
    }
    
    // 刷新数据
    const refreshData = () => {
      loadData()
    }
    
    // 处理月份变化
    const handleMonthChange = (params) => {
      currentYear.value = params.year
      currentMonth.value = params.month
      fetchMonthlyCalendar()
    }
    
    // 处理日期点击
    const handleDayClick = (day) => {
      console.log('点击日期:', day)
      // 可以在这里添加日期点击的处理逻辑
    }
    
    // 返回上一页
    const goBack = () => {
      router.go(-1)
    }
    
    // 组件挂载时加载数据
    onMounted(() => {
      initDateRange()
      loadData()
    })
    
    return {
      overview,
      wpmTrend,
      accuracyTrend,
      keyErrorStats,
      monthlyCalendarData,
      currentYear,
      currentMonth,
      dateRange,
      loading,
      dateShortcuts,
      handleDateChange,
      refreshData,
      handleMonthChange,
      handleDayClick,
      goBack
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

.header-controls {
  display: flex;
  align-items: center;
  gap: 15px;
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

