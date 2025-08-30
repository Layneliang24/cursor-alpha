<template>
  <div class="learning-analytics-dashboard">
    <div class="dashboard-header">
      <h2>学习数据分析</h2>
      <div class="header-actions">
        <el-button
          type="primary"
          size="small"
          @click="exportReport"
          icon="el-icon-download"
        >
          导出报告
        </el-button>
        <el-button
          size="small"
          @click="refreshAllData"
          :loading="globalLoading"
          icon="el-icon-refresh"
        >
          刷新数据
        </el-button>
      </div>
    </div>

    <div class="dashboard-content">
      <!-- 第一行：进度趋势和掌握度分布 -->
      <div class="chart-row">
        <div class="chart-col chart-col-8">
          <ProgressTrendChart 
            ref="progressChart"
            height="400px"
            @date-range-change="handleDateRangeChange"
          />
        </div>
        <div class="chart-col chart-col-4">
          <MasteryDistributionChart 
            ref="masteryChart"
            height="400px"
            @segment-click="handleMasterySegmentClick"
          />
        </div>
      </div>

      <!-- 第二行：时间分析和效率雷达 -->
      <div class="chart-row">
        <div class="chart-col chart-col-6">
          <TimeAnalysisChart 
            ref="timeChart"
            height="450px"
            @time-period-click="handleTimePeriodClick"
          />
        </div>
        <div class="chart-col chart-col-6">
          <EfficiencyRadarChart 
            ref="efficiencyChart"
            height="450px"
          />
        </div>
      </div>

      <!-- 第三行：学习洞察面板 -->
      <div class="chart-row">
        <div class="chart-col chart-col-12">
          <LearningInsightsPanel 
            ref="insightsPanel"
            @recommendation-action="handleRecommendationAction"
            @start-practice="handleStartPractice"
            @start-review="handleStartReview"
          />
        </div>
      </div>

      <!-- 第四行：报告生成和目标追踪 -->
      <div class="chart-row">
        <div class="chart-col chart-col-6">
          <ReportGenerator 
            ref="reportGenerator"
          />
        </div>
        <div class="chart-col chart-col-6">
          <GoalTracker 
            ref="goalTracker"
            @goal-created="handleGoalCreated"
            @goal-updated="handleGoalUpdated"
          />
        </div>
      </div>
    </div>

    <!-- 详情弹窗 -->
    <el-dialog
      v-model="detailDialogVisible"
      :title="detailDialogTitle"
      width="60%"
      :before-close="handleDetailDialogClose"
    >
      <div class="detail-content">
        <component 
          :is="detailComponent"
          v-bind="detailProps"
          @close="detailDialogVisible = false"
        />
      </div>
    </el-dialog>
  </div>
</template>

<script>
import ProgressTrendChart from './ProgressTrendChart.vue'
import MasteryDistributionChart from './MasteryDistributionChart.vue'
import TimeAnalysisChart from './TimeAnalysisChart.vue'
import EfficiencyRadarChart from './EfficiencyRadarChart.vue'
import LearningInsightsPanel from './LearningInsightsPanel.vue'
import ReportGenerator from './ReportGenerator.vue'
import GoalTracker from './GoalTracker.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

export default {
  name: 'LearningAnalyticsDashboard',
  components: {
    ProgressTrendChart,
    MasteryDistributionChart,
    TimeAnalysisChart,
    EfficiencyRadarChart,
    LearningInsightsPanel,
    ReportGenerator,
    GoalTracker
  },
  data() {
    return {
      globalLoading: false,
      detailDialogVisible: false,
      detailDialogTitle: '',
      detailComponent: null,
      detailProps: {}
    }
  },
  mounted() {
    this.initDashboard()
  },
  methods: {
    initDashboard() {
      // 初始化仪表板
      ElMessage.success('学习分析仪表板加载完成')
    },
    
    async refreshAllData() {
      this.globalLoading = true
      try {
        // 刷新所有图表数据
        const refreshPromises = []
        
        if (this.$refs.progressChart) {
          refreshPromises.push(this.$refs.progressChart.loadData())
        }
        if (this.$refs.masteryChart) {
          refreshPromises.push(this.$refs.masteryChart.loadData())
        }
        if (this.$refs.timeChart) {
          refreshPromises.push(this.$refs.timeChart.loadData())
        }
        if (this.$refs.efficiencyChart) {
          refreshPromises.push(this.$refs.efficiencyChart.loadData())
        }
        if (this.$refs.insightsPanel) {
          refreshPromises.push(this.$refs.insightsPanel.loadInsights())
        }
        if (this.$refs.reportGenerator) {
          refreshPromises.push(this.$refs.reportGenerator.loadRecentReports())
        }
        if (this.$refs.goalTracker) {
          refreshPromises.push(this.$refs.goalTracker.loadGoals())
        }
        
        await Promise.all(refreshPromises)
        ElMessage.success('所有数据已刷新')
      } catch (error) {
        console.error('刷新数据失败:', error)
        ElMessage.error('刷新数据失败，请稍后重试')
      } finally {
        this.globalLoading = false
      }
    },
    
    handleDateRangeChange(dateRange) {
      // 同步日期范围到其他图表
      if (this.$refs.timeChart) {
        this.$refs.timeChart.dateRange = dateRange
        this.$refs.timeChart.loadData()
      }
    },
    
    handleMasterySegmentClick(data) {
      // 处理掌握度分布点击事件
      this.showDetailDialog('掌握度详情', 'MasteryDetail', {
        segment: data.name,
        value: data.value,
        category: data.category
      })
    },
    
    handleTimePeriodClick(data) {
      // 处理时间分析点击事件
      this.showDetailDialog('时间段详情', 'TimePeriodDetail', {
        period: data.period,
        value: data.value,
        viewMode: data.viewMode,
        metric: data.metric
      })
    },
    
    handleRecommendationAction(recommendation) {
      // 处理智能建议操作
      switch (recommendation.type) {
        case 'practice':
          this.handleStartPractice(recommendation.target_id)
          break
        case 'review':
          this.handleStartReview(recommendation.target_id)
          break
        case 'difficulty':
          this.adjustDifficulty(recommendation.target_id)
          break
        default:
          ElMessage.info(`执行建议: ${recommendation.title}`)
      }
    },
    
    handleStartPractice(expressionId) {
      // 开始练习特定表达
      this.$router.push({
        path: '/english/idiomatic-learning',
        query: { 
          mode: 'practice',
          expressionId: expressionId
        }
      })
    },
    
    handleStartReview(expressionId) {
      // 开始复习特定表达
      this.$router.push({
        path: '/english/idiomatic-learning',
        query: { 
          mode: 'review',
          expressionId: expressionId
        }
      })
    },
    
    adjustDifficulty(expressionId) {
      ElMessageBox.confirm(
        '是否要调整该表达的难度级别？',
        '难度调整',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      ).then(() => {
        // 实现难度调整逻辑
        ElMessage.success('难度已调整')
      }).catch(() => {
        ElMessage.info('已取消操作')
      })
    },
    
    showDetailDialog(title, component, props) {
      this.detailDialogTitle = title
      this.detailComponent = component
      this.detailProps = props
      this.detailDialogVisible = true
    },
    
    handleDetailDialogClose() {
      this.detailDialogVisible = false
      this.detailComponent = null
      this.detailProps = {}
    },
    
    async exportReport() {
      try {
        ElMessage.info('正在生成报告...')
        
        // 收集所有图表数据
        const reportData = {
          generated_at: new Date().toISOString(),
          progress_trend: this.$refs.progressChart?.chartData,
          mastery_distribution: this.$refs.masteryChart?.chartData,
          time_analysis: this.$refs.timeChart?.chartData,
          efficiency_analysis: this.$refs.efficiencyChart?.chartData,
          learning_insights: {
            overview: this.$refs.insightsPanel?.overviewData,
            recommendations: this.$refs.insightsPanel?.recommendationsData,
            weak_areas: this.$refs.insightsPanel?.weakAreasData
          }
        }
        
        // 生成并下载报告
        const blob = new Blob([JSON.stringify(reportData, null, 2)], {
          type: 'application/json'
        })
        
        const url = URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `learning-analytics-report-${new Date().toISOString().split('T')[0]}.json`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        URL.revokeObjectURL(url)
        
        ElMessage.success('报告已导出')
      } catch (error) {
        console.error('导出报告失败:', error)
        ElMessage.error('导出失败，请稍后重试')
      }
    },
    
    handleGoalCreated(goal) {
      // 处理新目标创建
      ElMessage.success(`学习目标"${goal.title}"创建成功`)
      // 刷新相关数据
      this.refreshAllData()
    },
    
    handleGoalUpdated(goal) {
      // 处理目标更新
      ElMessage.success(`学习目标"${goal.title}"更新成功`)
      // 刷新相关数据
      this.refreshAllData()
    }
  }
}
</script>

<style scoped>
.learning-analytics-dashboard {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.dashboard-header h2 {
  margin: 0;
  color: #303133;
  font-size: 24px;
  font-weight: 500;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.dashboard-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.chart-row {
  display: flex;
  gap: 20px;
}

.chart-col {
  flex: 1;
}

.chart-col-4 {
  flex: 0 0 33.333%;
}

.chart-col-6 {
  flex: 0 0 50%;
}

.chart-col-8 {
  flex: 0 0 66.666%;
}

.chart-col-12 {
  flex: 0 0 100%;
}

.detail-content {
  max-height: 60vh;
  overflow-y: auto;
}

@media (max-width: 1200px) {
  .chart-row {
    flex-direction: column;
  }
  
  .chart-col-4,
  .chart-col-6,
  .chart-col-8 {
    flex: 1;
  }
}

@media (max-width: 768px) {
  .learning-analytics-dashboard {
    padding: 10px;
  }
  
  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .header-actions {
    margin-top: 15px;
    width: 100%;
    justify-content: flex-end;
  }
}
</style>
