<template>
  <div class="learning-dashboard">
    <!-- 头部统计卡片 -->
    <div class="stats-overview">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ statistics?.total_expressions || 0 }}</div>
              <div class="stat-label">总表达数</div>
            </div>
            <div class="stat-icon">
              <el-icon size="24"><Document /></el-icon>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ statistics?.learned_expressions || 0 }}</div>
              <div class="stat-label">已掌握</div>
            </div>
            <div class="stat-icon">
              <el-icon size="24"><Check /></el-icon>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ currentStreak }}</div>
              <div class="stat-label">连续天数</div>
            </div>
            <div class="stat-icon">
              <el-icon size="24"><Calendar /></el-icon>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ Math.round(statistics?.average_mastery || 0) }}%</div>
              <div class="stat-label">平均掌握度</div>
            </div>
            <div class="stat-icon">
              <el-icon size="24"><TrendCharts /></el-icon>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <!-- 今日目标进度 -->
    <el-card class="daily-progress-card">
      <template #header>
        <div class="card-header">
          <span>今日学习目标</span>
          <el-tag :type="dailyGoalProgress >= 100 ? 'success' : 'info'">
            {{ todayProgress }}/{{ settings.daily_goal }}
          </el-tag>
        </div>
      </template>
      
      <div class="daily-progress">
        <el-progress 
          :percentage="dailyGoalProgress"
          :color="getProgressColor(dailyGoalProgress)"
          :stroke-width="12"
          text-inside
        />
        <div class="progress-actions">
          <el-button 
            type="primary" 
            size="small"
            @click="startLearning"
            v-if="dailyGoalProgress < 100"
          >
            <el-icon><VideoPlay /></el-icon>
            开始学习
          </el-button>
          <el-button 
            type="success" 
            size="small"
            disabled
            v-else
          >
            <el-icon><Check /></el-icon>
            今日目标已完成
          </el-button>
        </div>
      </div>
    </el-card>
    
    <!-- 图表区域 -->
    <el-row :gutter="20" class="charts-section">
      <!-- 学习趋势图 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>学习趋势</span>
          </template>
          <div ref="learningTrendChart" class="chart-container"></div>
        </el-card>
      </el-col>
      
      <!-- 掌握度分布 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>掌握度分布</span>
          </template>
          <div ref="masteryDistributionChart" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" class="charts-section">
      <!-- 难度分布 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>难度分布</span>
          </template>
          <div ref="difficultyChart" class="chart-container"></div>
        </el-card>
      </el-col>
      
      <!-- 薄弱环节分析 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>薄弱环节</span>
          </template>
          <div class="weak-areas">
            <div 
              v-for="area in statistics?.weak_areas?.slice(0, 5)" 
              :key="area.category"
              class="weak-area-item"
            >
              <div class="area-info">
                <span class="area-name">{{ area.category }}</span>
                <span class="area-count">{{ area.total_expressions }}个表达</span>
              </div>
              <div class="area-progress">
                <el-progress 
                  :percentage="area.mastery_rate" 
                  :color="getWeakAreaColor(area.mastery_rate)"
                  :show-text="false"
                  :stroke-width="6"
                />
                <span class="area-rate">{{ area.mastery_rate }}%</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 学习目标 -->
    <el-card class="goals-section">
      <template #header>
        <div class="card-header">
          <span>学习目标</span>
          <div class="header-actions">
            <el-button 
              type="info" 
              size="small" 
              @click="navigateToAnalytics"
              style="margin-right: 10px"
            >
              <el-icon><TrendCharts /></el-icon>
              详细分析
            </el-button>
            <el-button type="primary" size="small" @click="showCreateGoalDialog = true">
              <el-icon><Plus /></el-icon>
              新建目标
            </el-button>
          </div>
        </div>
      </template>
      
      <div class="goals-list">
        <div 
          v-for="goal in activeGoals" 
          :key="goal.id"
          class="goal-item"
        >
          <div class="goal-info">
            <h4 class="goal-title">{{ goal.title }}</h4>
            <p class="goal-description">{{ goal.description }}</p>
            <div class="goal-meta">
              <el-tag :type="getPriorityType(goal.priority)" size="small">
                {{ getPriorityText(goal.priority) }}
              </el-tag>
              <span class="goal-deadline">截止：{{ formatDate(goal.deadline) }}</span>
            </div>
          </div>
          <div class="goal-progress">
            <el-progress 
              type="circle" 
              :percentage="(goal.current_progress / goal.target_expressions) * 100"
              :width="80"
            />
            <div class="progress-text">
              {{ goal.current_progress }}/{{ goal.target_expressions }}
            </div>
          </div>
        </div>
      </div>
    </el-card>
    
    <!-- 创建目标对话框 -->
    <el-dialog v-model="showCreateGoalDialog" title="创建学习目标" width="500px">
      <el-form :model="newGoal" label-width="100px">
        <el-form-item label="目标标题" required>
          <el-input v-model="newGoal.title" placeholder="例如：掌握商务英语表达" />
        </el-form-item>
        
        <el-form-item label="目标描述">
          <el-input 
            v-model="newGoal.description" 
            type="textarea" 
            :rows="3"
            placeholder="详细描述学习目标..."
          />
        </el-form-item>
        
        <el-form-item label="目标数量" required>
          <el-input-number 
            v-model="newGoal.target_expressions" 
            :min="1" 
            :max="500"
            placeholder="目标表达数量"
          />
        </el-form-item>
        
        <el-form-item label="优先级">
          <el-select v-model="newGoal.priority">
            <el-option label="低" value="low" />
            <el-option label="中" value="medium" />
            <el-option label="高" value="high" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="截止日期">
          <el-date-picker
            v-model="newGoal.deadline"
            type="date"
            placeholder="选择截止日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showCreateGoalDialog = false">取消</el-button>
        <el-button type="primary" @click="createGoal" :loading="loading.goals">
          创建目标
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Document, Check, Calendar, TrendCharts, VideoPlay, Plus 
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { useLearningStore } from '@/stores/modules/learningStore'
import type { LearningGoal } from '@/stores/modules/learningStore'

// Emits
const emit = defineEmits<{
  startLearning: []
  goalCreated: [goal: LearningGoal]
}>()

// Store
const learningStore = useLearningStore()

// 图表引用
const learningTrendChart = ref<HTMLElement>()
const masteryDistributionChart = ref<HTMLElement>()
const difficultyChart = ref<HTMLElement>()

// 状态
const showCreateGoalDialog = ref(false)
const newGoal = reactive({
  title: '',
  description: '',
  target_expressions: 50,
  priority: 'medium' as 'low' | 'medium' | 'high',
  deadline: ''
})

// 计算属性
const { 
  statistics, 
  loading, 
  settings, 
  todayProgress, 
  dailyGoalProgress, 
  currentStreak, 
  activeGoals 
} = learningStore

const getProgressColor = (percentage: number) => {
  if (percentage >= 100) return '#67c23a'
  if (percentage >= 80) return '#e6a23c'
  if (percentage >= 60) return '#f56c6c'
  return '#909399'
}

const getWeakAreaColor = (rate: number) => {
  if (rate >= 70) return '#67c23a'
  if (rate >= 50) return '#e6a23c'
  return '#f56c6c'
}

const getPriorityType = (priority: string) => {
  const map = {
    low: 'info',
    medium: 'warning', 
    high: 'danger'
  }
  return map[priority] || 'info'
}

const getPriorityText = (priority: string) => {
  const map = {
    low: '低优先级',
    medium: '中优先级',
    high: '高优先级'
  }
  return map[priority] || priority
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

// 方法
const startLearning = () => {
  emit('startLearning')
}

const navigateToAnalytics = () => {
  // 导航到详细分析页面
  window.open('/english/learning-analytics', '_blank')
}

const createGoal = async () => {
  if (!newGoal.title || !newGoal.target_expressions || !newGoal.deadline) {
    ElMessage.error('请填写完整信息')
    return
  }
  
  try {
    const goal = await learningStore.createLearningGoal({
      ...newGoal,
      status: 'active'
    })
    
    ElMessage.success('学习目标创建成功')
    showCreateGoalDialog.value = false
    
    // 重置表单
    Object.assign(newGoal, {
      title: '',
      description: '',
      target_expressions: 50,
      priority: 'medium',
      deadline: ''
    })
    
    emit('goalCreated', goal)
  } catch (error) {
    console.error('创建目标失败:', error)
    ElMessage.error('创建目标失败，请重试')
  }
}

// 图表初始化
const initLearningTrendChart = () => {
  if (!learningTrendChart.value || !statistics.value) return
  
  const chart = echarts.init(learningTrendChart.value)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    xAxis: {
      type: 'category',
      data: statistics.value.weekly_progress.map(p => p.date),
      axisLabel: {
        formatter: (value: string) => {
          return new Date(value).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
        }
      }
    },
    yAxis: [
      {
        type: 'value',
        name: '学习数量',
        position: 'left'
      },
      {
        type: 'value',
        name: '学习时间(分钟)',
        position: 'right'
      }
    ],
    series: [
      {
        name: '学习表达数',
        type: 'line',
        data: statistics.value.weekly_progress.map(p => p.expressions_learned),
        smooth: true,
        itemStyle: { color: '#409eff' },
        areaStyle: { opacity: 0.3 }
      },
      {
        name: '学习时间',
        type: 'bar',
        yAxisIndex: 1,
        data: statistics.value.weekly_progress.map(p => Math.round(p.study_time / 60)),
        itemStyle: { color: '#67c23a' }
      }
    ],
    grid: {
      right: '10%'
    }
  }
  
  chart.setOption(option)
  
  // 响应式调整
  window.addEventListener('resize', () => chart.resize())
}

const initMasteryDistributionChart = () => {
  if (!masteryDistributionChart.value || !statistics.value) return
  
  const chart = echarts.init(masteryDistributionChart.value)
  
  const data = [
    { value: statistics.value.mastery_distribution.beginner, name: '初学者 (0-40%)' },
    { value: statistics.value.mastery_distribution.intermediate, name: '进步中 (40-60%)' },
    { value: statistics.value.mastery_distribution.advanced, name: '熟练 (60-80%)' },
    { value: statistics.value.mastery_distribution.mastered, name: '已掌握 (80%+)' }
  ]
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    series: [
      {
        name: '掌握度分布',
        type: 'pie',
        radius: '70%',
        data: data,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        itemStyle: {
          borderRadius: 8,
          borderColor: '#fff',
          borderWidth: 2
        },
        color: ['#f56c6c', '#e6a23c', '#409eff', '#67c23a']
      }
    ]
  }
  
  chart.setOption(option)
  window.addEventListener('resize', () => chart.resize())
}

const initDifficultyChart = () => {
  if (!difficultyChart.value || !statistics.value) return
  
  const chart = echarts.init(difficultyChart.value)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    xAxis: {
      type: 'category',
      data: ['初级', '中级', '高级']
    },
    yAxis: {
      type: 'value',
      name: '表达数量'
    },
    series: [
      {
        name: '表达数量',
        type: 'bar',
        data: [
          statistics.value.difficulty_breakdown.beginner,
          statistics.value.difficulty_breakdown.intermediate,
          statistics.value.difficulty_breakdown.advanced
        ],
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#83bff6' },
            { offset: 0.5, color: '#188df0' },
            { offset: 1, color: '#188df0' }
          ])
        },
        emphasis: {
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#2378f7' },
              { offset: 0.7, color: '#2378f7' },
              { offset: 1, color: '#83bff6' }
            ])
          }
        },
        barWidth: '60%',
        borderRadius: [4, 4, 0, 0]
      }
    ]
  }
  
  chart.setOption(option)
  window.addEventListener('resize', () => chart.resize())
}

const initAllCharts = async () => {
  await nextTick()
  initLearningTrendChart()
  initMasteryDistributionChart()
  initDifficultyChart()
}

// 生命周期
onMounted(async () => {
  // 加载数据
  await learningStore.fetchStatistics()
  
  // 初始化图表
  setTimeout(initAllCharts, 100)
})
</script>

<style scoped>
.learning-dashboard {
  padding: 20px;
}

.stats-overview {
  margin-bottom: 24px;
}

.stat-card {
  height: 100px;
}

.stat-card :deep(.el-card__body) {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.stat-icon {
  color: #409eff;
  opacity: 0.8;
}

.daily-progress-card {
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
}

.daily-progress {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.progress-actions {
  text-align: center;
}

.charts-section {
  margin-bottom: 24px;
}

.chart-container {
  height: 300px;
  width: 100%;
}

.weak-areas {
  padding: 16px 0;
}

.weak-area-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #ebeef5;
}

.weak-area-item:last-child {
  border-bottom: none;
}

.area-info {
  flex: 1;
}

.area-name {
  font-weight: 500;
  color: #303133;
  display: block;
  margin-bottom: 4px;
}

.area-count {
  font-size: 12px;
  color: #909399;
}

.area-progress {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 120px;
}

.area-rate {
  font-size: 12px;
  color: #606266;
  min-width: 35px;
  text-align: right;
}

.goals-section {
  margin-bottom: 24px;
}

.goals-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.goal-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  background: #fafafa;
}

.goal-info {
  flex: 1;
  margin-right: 20px;
}

.goal-title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 8px;
}

.goal-description {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
}

.goal-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.goal-deadline {
  font-size: 12px;
  color: #909399;
}

.goal-progress {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.progress-text {
  font-size: 12px;
  color: #606266;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .charts-section .el-col {
    margin-bottom: 20px;
  }
}

@media (max-width: 768px) {
  .learning-dashboard {
    padding: 16px;
  }
  
  .stats-overview .el-col {
    margin-bottom: 16px;
  }
  
  .goal-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .goal-progress {
    align-self: center;
  }
}
</style>
