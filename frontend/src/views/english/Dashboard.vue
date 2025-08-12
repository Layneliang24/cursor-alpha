<template>
  <div class="english-dashboard">
    <!-- 页面头部 -->
    <div class="dashboard-header">
      <h1>英语学习仪表板</h1>
      <div class="header-actions">
        <el-button type="primary" @click="refreshAllData" :loading="refreshing">
          <el-icon><Refresh /></el-icon>
          刷新数据
        </el-button>
      </div>
    </div>

    <!-- 今日概览卡片 -->
    <el-row :gutter="20" class="overview-cards">
      <el-col :span="6">
        <el-card class="overview-card">
          <div class="card-content">
            <div class="card-icon words">
              <el-icon><Document /></el-icon>
            </div>
            <div class="card-info">
              <h3>{{ todayProgress?.wordsLearned || 0 }}</h3>
              <p>今日学习单词</p>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="overview-card">
          <div class="card-content">
            <div class="card-icon reviews">
              <el-icon><Clock /></el-icon>
            </div>
            <div class="card-info">
              <h3>{{ dueReviewsCount }}</h3>
              <p>待复习单词</p>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="overview-card">
          <div class="card-content">
            <div class="card-icon practice">
              <el-icon><Trophy /></el-icon>
            </div>
            <div class="card-info">
              <h3>{{ practiceStatistics.correctRate }}%</h3>
              <p>练习正确率</p>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="overview-card">
          <div class="card-content">
            <div class="card-icon time">
              <el-icon><Timer /></el-icon>
            </div>
            <div class="card-info">
              <h3>{{ todayProgress?.studyTime || 0 }}</h3>
              <p>今日学习时长(分钟)</p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 主要功能区域 -->
    <el-row :gutter="20" class="main-content">
      <!-- 左侧：学习进度和统计 -->
      <el-col :span="16">
        <!-- 学习进度图表 -->
        <el-card class="chart-card" v-loading="overviewLoading">
          <template #header>
            <div class="card-header">
              <span>学习进度趋势</span>
              <el-select v-model="chartDays" @change="fetchLearningOverview(chartDays)" size="small">
                <el-option label="7天" :value="7" />
                <el-option label="14天" :value="14" />
                <el-option label="30天" :value="30" />
              </el-select>
            </div>
          </template>
          <div class="chart-container">
            <LearningChart :data="learningOverview?.daily_data || []" />
          </div>
        </el-card>

        <!-- 复习单词列表 -->
        <el-card class="review-card" v-if="dueReviews.length > 0">
          <template #header>
            <div class="card-header">
              <span>待复习单词 ({{ dueReviews.length }})</span>
              <el-button type="primary" size="small" @click="startBatchReview">
                开始复习
              </el-button>
            </div>
          </template>
          <div class="review-list">
            <div v-for="progress in dueReviews.slice(0, 5)" :key="progress.id" class="review-item">
              <div class="word-info">
                <span class="word">{{ progress.word?.word }}</span>
                <span class="phonetic">{{ progress.word?.phonetic }}</span>
              </div>
              <div class="progress-info">
                <el-tag :type="getProgressType(progress.mastery_level)" size="small">
                  掌握度: {{ Math.round(progress.mastery_level * 100) }}%
                </el-tag>
              </div>
            </div>
            <div v-if="dueReviews.length > 5" class="more-reviews">
              还有 {{ dueReviews.length - 5 }} 个单词待复习...
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：快速操作和每日任务 -->
      <el-col :span="8">
        <!-- 快速操作 -->
        <el-card class="quick-actions">
          <template #header>
            <span>快速操作</span>
          </template>
          <div class="action-buttons">
            <el-button type="primary" @click="goToPractice" :disabled="!activePlan">
              <el-icon><Edit /></el-icon>
              开始练习
            </el-button>
            <el-button type="success" @click="goToWords">
              <el-icon><Document /></el-icon>
              单词学习
            </el-button>
            <el-button type="info" @click="goToNews">
              <el-icon><Reading /></el-icon>
              新闻阅读
            </el-button>
            <el-button type="warning" @click="showPlanDialog = true">
              <el-icon><Calendar /></el-icon>
              学习计划
            </el-button>
          </div>
        </el-card>

        <!-- 每日任务 -->
        <el-card class="daily-tasks" v-if="activePlan">
          <template #header>
            <span>今日任务</span>
          </template>
          <div class="task-list">
            <div class="task-item">
              <div class="task-info">
                <span>学习新单词</span>
                <span class="task-progress">
                  {{ todayProgress?.wordsLearned || 0 }} / {{ activePlan.daily_word_target }}
                </span>
              </div>
              <el-progress 
                :percentage="Math.min(100, (todayProgress?.wordsLearned || 0) / activePlan.daily_word_target * 100)"
                :stroke-width="6"
              />
            </div>
            
            <div class="task-item">
              <div class="task-info">
                <span>复习单词</span>
                <span class="task-progress">
                  {{ todayProgress?.wordsReviewed || 0 }} / {{ Math.max(5, dueReviewsCount) }}
                </span>
              </div>
              <el-progress 
                :percentage="Math.min(100, (todayProgress?.wordsReviewed || 0) / Math.max(5, dueReviewsCount) * 100)"
                :stroke-width="6"
                color="#67C23A"
              />
            </div>
            
            <div class="task-item">
              <div class="task-info">
                <span>练习次数</span>
                <span class="task-progress">
                  {{ todayProgress?.practiceCount || 0 }} / 10
                </span>
              </div>
              <el-progress 
                :percentage="Math.min(100, (todayProgress?.practiceCount || 0) / 10 * 100)"
                :stroke-width="6"
                color="#E6A23C"
              />
            </div>
          </div>
        </el-card>

        <!-- 学习统计 -->
        <el-card class="stats-card">
          <template #header>
            <span>学习统计</span>
          </template>
          <div class="stats-list">
            <div class="stat-item">
              <span class="stat-label">总学习时长</span>
              <span class="stat-value">{{ learningOverview?.total_stats?.study_time_minutes || 0 }} 分钟</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">已掌握单词</span>
              <span class="stat-value">{{ learningOverview?.mastery_stats?.mastered_words || 0 }} 个</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">学习中单词</span>
              <span class="stat-value">{{ learningOverview?.mastery_stats?.learning_words || 0 }} 个</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">平均正确率</span>
              <span class="stat-value">{{ todayProgress?.accuracyRate || 0 }}%</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 学习计划对话框 -->
    <PlanDialog v-model="showPlanDialog" @created="onPlanCreated" />

    <!-- 批量复习对话框 -->
    <BatchReviewDialog v-model="showReviewDialog" :words="dueReviews" @completed="onReviewCompleted" />
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useEnglishStore } from '@/stores/english'
import { ElMessage } from 'element-plus'
import { 
  Refresh, Document, Clock, Trophy, Timer, Edit, Reading, Calendar
} from '@element-plus/icons-vue'
import LearningChart from '@/components/english/LearningChart.vue'
import PlanDialog from '@/components/english/PlanDialog.vue'
import BatchReviewDialog from '@/components/english/BatchReviewDialog.vue'

export default {
  name: 'EnglishDashboard',
  components: {
    LearningChart,
    PlanDialog,
    BatchReviewDialog
  },
  setup() {
    const router = useRouter()
    const englishStore = useEnglishStore()
    
    const refreshing = ref(false)
    const chartDays = ref(7)
    const showPlanDialog = ref(false)
    const showReviewDialog = ref(false)

    // 计算属性
    const todayProgress = computed(() => englishStore.todayProgress)
    const dueReviewsCount = computed(() => englishStore.dueReviewsCount)
    const practiceStatistics = computed(() => englishStore.practiceStatistics)
    const activePlan = computed(() => englishStore.activePlan)
    const learningOverview = computed(() => englishStore.learningOverview)
    const overviewLoading = computed(() => englishStore.overviewLoading)
    const dueReviews = computed(() => englishStore.dueReviews)

    // 方法
    const refreshAllData = async () => {
      refreshing.value = true
      try {
        await Promise.all([
          englishStore.fetchLearningStats({ page: 1, page_size: 30 }),
          englishStore.fetchDueReviews(),
          englishStore.fetchLearningOverview(chartDays.value),
          englishStore.fetchLearningPlans(),
          englishStore.fetchPracticeRecords({ page: 1, page_size: 50 })
        ])
        ElMessage.success('数据刷新成功')
      } catch (error) {
        ElMessage.error('数据刷新失败')
        console.error(error)
      } finally {
        refreshing.value = false
      }
    }

    const getProgressType = (masteryLevel) => {
      if (masteryLevel >= 0.8) return 'success'
      if (masteryLevel >= 0.5) return 'warning'
      return 'danger'
    }

    const startBatchReview = () => {
      showReviewDialog.value = true
    }

    const goToPractice = () => {
      router.push('/english/practice')
    }

    const goToWords = () => {
      router.push('/english/words')
    }

    const goToNews = () => {
      router.push('/english/news')
    }

    const onPlanCreated = () => {
      englishStore.fetchLearningPlans()
      ElMessage.success('学习计划创建成功')
    }

    const onReviewCompleted = () => {
      refreshAllData()
      ElMessage.success('复习完成，进度已更新')
    }

    // 生命周期
    onMounted(() => {
      refreshAllData()
    })

    return {
      // 响应式数据
      refreshing,
      chartDays,
      showPlanDialog,
      showReviewDialog,
      
      // 计算属性
      todayProgress,
      dueReviewsCount,
      practiceStatistics,
      activePlan,
      learningOverview,
      overviewLoading,
      dueReviews,
      
      // 方法
      refreshAllData,
      getProgressType,
      startBatchReview,
      goToPractice,
      goToWords,
      goToNews,
      onPlanCreated,
      onReviewCompleted,
      
      // 图标
      Refresh,
      Document,
      Clock,
      Trophy,
      Timer,
      Edit,
      Reading,
      Calendar
    }
  }
}
</script>

<style scoped>
.english-dashboard {
  padding: 20px;
  background-color: #f5f5f5;
  min-height: 100vh;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.dashboard-header h1 {
  margin: 0;
  color: #303133;
  font-size: 28px;
  font-weight: 600;
}

.overview-cards {
  margin-bottom: 24px;
}

.overview-card {
  height: 120px;
  transition: all 0.3s ease;
}

.overview-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.card-content {
  display: flex;
  align-items: center;
  height: 100%;
}

.card-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  font-size: 24px;
  color: white;
}

.card-icon.words { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
.card-icon.reviews { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
.card-icon.practice { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
.card-icon.time { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }

.card-info h3 {
  margin: 0 0 4px 0;
  font-size: 32px;
  font-weight: 700;
  color: #303133;
}

.card-info p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.main-content {
  margin-bottom: 24px;
}

.chart-card, .review-card, .quick-actions, .daily-tasks, .stats-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  height: 300px;
  padding: 20px 0;
}

.review-list {
  max-height: 300px;
  overflow-y: auto;
}

.review-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.review-item:last-child {
  border-bottom: none;
}

.word-info {
  display: flex;
  flex-direction: column;
}

.word {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.phonetic {
  font-size: 14px;
  color: #909399;
}

.more-reviews {
  text-align: center;
  padding: 16px;
  color: #909399;
  font-size: 14px;
}

.action-buttons {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.action-buttons .el-button {
  height: 48px;
  font-size: 14px;
}

.task-list, .stats-list {
  space-y: 16px;
}

.task-item {
  margin-bottom: 20px;
}

.task-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.task-progress {
  font-size: 12px;
  color: #909399;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.stat-item:last-child {
  border-bottom: none;
}

.stat-label {
  color: #606266;
  font-size: 14px;
}

.stat-value {
  color: #303133;
  font-weight: 600;
  font-size: 16px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .overview-cards .el-col {
    margin-bottom: 16px;
  }
  
  .main-content .el-col {
    margin-bottom: 20px;
  }
  
  .action-buttons {
    grid-template-columns: 1fr;
  }
}
</style>
