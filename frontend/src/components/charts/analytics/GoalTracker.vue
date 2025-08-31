<template>
  <div class="goal-tracker">
    <el-card class="tracker-card">
      <template #header>
        <div class="card-header">
          <h3>学习目标追踪</h3>
          <div class="header-actions">
            <el-button
              size="small"
              @click="refreshGoals"
              :loading="loading"
              icon="el-icon-refresh"
            >
              刷新
            </el-button>
            <el-button
              type="primary"
              size="small"
              @click="showCreateDialog = true"
              icon="el-icon-plus"
            >
              新建目标
            </el-button>
          </div>
        </div>
      </template>

      <!-- 目标列表 -->
      <div class="goals-list" v-loading="loading">
        <div 
          v-for="goal in goals" 
          :key="goal.id"
          class="goal-item"
          :class="{ 'completed': goal.status === 'completed' }"
        >
          <div class="goal-header">
            <div class="goal-title-section">
              <h4 class="goal-title">{{ goal.title }}</h4>
              <el-tag 
                :type="getPriorityType(goal.priority)" 
                size="small"
                style="margin-left: 10px"
              >
                {{ getPriorityText(goal.priority) }}
              </el-tag>
              <el-tag 
                :type="getStatusType(goal.status)" 
                size="small"
                style="margin-left: 5px"
              >
                {{ getStatusText(goal.status) }}
              </el-tag>
            </div>
            <div class="goal-actions">
              <el-button 
                size="mini" 
                type="text"
                @click="viewGoalDetails(goal)"
              >
                详情
              </el-button>
              <el-button 
                size="mini" 
                type="text"
                @click="editGoal(goal)"
              >
                编辑
              </el-button>
              <el-dropdown @command="handleGoalAction">
                <el-button size="mini" type="text">
                  更多<i class="el-icon-arrow-down el-icon--right"></i>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item :command="{action: 'pause', goal: goal}">
                      暂停目标
                    </el-dropdown-item>
                    <el-dropdown-item :command="{action: 'complete', goal: goal}">
                      标记完成
                    </el-dropdown-item>
                    <el-dropdown-item :command="{action: 'delete', goal: goal}" divided>
                      删除目标
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>

          <div class="goal-description" v-if="goal.description">
            {{ goal.description }}
          </div>

          <div class="goal-progress">
            <div class="progress-info">
              <span class="progress-text">
                进度: {{ goal.current_progress }}/{{ goal.target_expressions }}
              </span>
              <span class="progress-percentage">
                {{ formatPercentage(goal.completion_rate) }}
              </span>
            </div>
            <el-progress 
              :percentage="goal.completion_rate * 100"
              :color="getProgressColor(goal.completion_rate)"
              :stroke-width="8"
              :show-text="false"
            />
          </div>

          <div class="goal-timeline">
            <div class="timeline-item">
              <span class="timeline-label">创建时间:</span>
              <span class="timeline-value">{{ formatDate(goal.created_at) }}</span>
            </div>
            <div class="timeline-item">
              <span class="timeline-label">截止时间:</span>
              <span class="timeline-value" :class="{ 'overdue': isOverdue(goal.deadline) }">
                {{ formatDate(goal.deadline) }}
              </span>
            </div>
            <div class="timeline-item" v-if="goal.estimated_completion">
              <span class="timeline-label">预计完成:</span>
              <span class="timeline-value">{{ formatDate(goal.estimated_completion) }}</span>
            </div>
          </div>

          <!-- 进度追踪图表 -->
          <div class="goal-chart" v-if="goal.showChart">
            <div :ref="`goalChart_${goal.id}`" class="mini-chart"></div>
          </div>
        </div>

        <div class="empty-state" v-if="goals.length === 0 && !loading">
          <el-empty description="暂无学习目标">
            <el-button 
              type="primary" 
              @click="showCreateDialog = true"
            >
              创建第一个目标
            </el-button>
          </el-empty>
        </div>
      </div>
    </el-card>

    <!-- 创建目标对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      title="创建学习目标"
      width="500px"
      :before-close="handleCreateDialogClose"
    >
      <el-form 
        :model="newGoal" 
        :rules="goalRules"
        label-width="100px" 
        ref="goalFormRef"
      >
        <el-form-item label="目标标题" prop="title">
          <el-input 
            v-model="newGoal.title" 
            placeholder="例如：掌握商务英语表达"
            maxlength="50"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="目标描述" prop="description">
          <el-input 
            v-model="newGoal.description" 
            type="textarea" 
            :rows="3"
            placeholder="详细描述学习目标..."
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="目标数量" prop="target_expressions">
          <el-input-number 
            v-model="newGoal.target_expressions" 
            :min="1" 
            :max="500"
            placeholder="目标表达数量"
            style="width: 100%"
          />
        </el-form-item>
        
        <el-form-item label="优先级" prop="priority">
          <el-select v-model="newGoal.priority" style="width: 100%">
            <el-option label="低优先级" value="low" />
            <el-option label="中优先级" value="medium" />
            <el-option label="高优先级" value="high" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="截止日期" prop="deadline">
          <el-date-picker
            v-model="newGoal.deadline"
            type="date"
            placeholder="选择截止日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 100%"
            :disabled-date="disabledDate"
          />
        </el-form-item>

        <el-form-item label="每日目标">
          <el-input-number 
            v-model="newGoal.daily_target" 
            :min="1" 
            :max="20"
            placeholder="每日学习目标"
            style="width: 100%"
          />
          <div class="form-hint">
            建议每日学习{{ calculateDailyTarget() }}个表达
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="handleCreateDialogClose">取消</el-button>
        <el-button 
          type="primary" 
          @click="createGoal"
          :loading="creating"
        >
          创建目标
        </el-button>
      </template>
    </el-dialog>

    <!-- 目标详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      title="目标详情"
      width="70%"
      :before-close="handleDetailDialogClose"
    >
      <div class="goal-detail" v-if="selectedGoal">
        <div class="detail-header">
          <h2>{{ selectedGoal.title }}</h2>
          <div class="detail-meta">
            <el-tag :type="getPriorityType(selectedGoal.priority)">
              {{ getPriorityText(selectedGoal.priority) }}
            </el-tag>
            <el-tag :type="getStatusType(selectedGoal.status)" style="margin-left: 10px">
              {{ getStatusText(selectedGoal.status) }}
            </el-tag>
          </div>
        </div>

        <div class="detail-progress">
          <h3>进度概览</h3>
          <div class="progress-overview">
            <div class="progress-circle">
              <el-progress 
                type="circle" 
                :percentage="selectedGoal.completion_rate * 100"
                :width="120"
                :color="getProgressColor(selectedGoal.completion_rate)"
              />
            </div>
            <div class="progress-stats">
              <div class="stat-item">
                <div class="stat-value">{{ selectedGoal.current_progress }}</div>
                <div class="stat-label">已完成</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ selectedGoal.target_expressions - selectedGoal.current_progress }}</div>
                <div class="stat-label">剩余</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ getDaysRemaining(selectedGoal.deadline) }}</div>
                <div class="stat-label">剩余天数</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 进度追踪图表 -->
        <div class="detail-chart">
          <h3>进度追踪</h3>
          <div :ref="`detailChart_${selectedGoal.id}`" class="tracking-chart"></div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import * as echarts from 'echarts'
import { dataAnalysisAPI } from '@/api/english'
import { ElMessage, ElMessageBox } from 'element-plus'

export default {
  name: 'GoalTracker',
  data() {
    return {
      loading: false,
      creating: false,
      goals: [],
      showCreateDialog: false,
      showDetailDialog: false,
      selectedGoal: null,
      newGoal: {
        title: '',
        description: '',
        target_expressions: 50,
        priority: 'medium',
        deadline: '',
        daily_target: 2
      },
      goalRules: {
        title: [
          { required: true, message: '请输入目标标题', trigger: 'blur' },
          { min: 2, max: 50, message: '标题长度在 2 到 50 个字符', trigger: 'blur' }
        ],
        target_expressions: [
          { required: true, message: '请设置目标数量', trigger: 'blur' },
          { type: 'number', min: 1, max: 500, message: '目标数量在 1 到 500 之间', trigger: 'blur' }
        ],
        deadline: [
          { required: true, message: '请选择截止日期', trigger: 'change' }
        ]
      }
    }
  },
  mounted() {
    this.loadGoals()
  },
  beforeUnmount() {
    // 清理图表
    this.goals.forEach(goal => {
      const chartRef = this.$refs[`goalChart_${goal.id}`]
      if (chartRef && chartRef[0]) {
        const chart = echarts.getInstanceByDom(chartRef[0])
        if (chart) {
          chart.dispose()
        }
      }
    })
  },
  methods: {
    async loadGoals() {
      this.loading = true
      try {
        const response = await dataAnalysisAPI.getLearningGoals()
        this.goals = response.results || response.data?.results || []
        
        // 为每个目标加载进度追踪数据
        for (const goal of this.goals) {
          try {
            const trackingResponse = await dataAnalysisAPI.getGoalProgressTracking(goal.id)
            goal.trackingData = trackingResponse.data
          } catch (error) {
            console.warn(`加载目标${goal.id}进度追踪失败:`, error)
          }
        }
        
      } catch (error) {
        console.error('加载学习目标失败:', error)
        ElMessage.error('加载数据失败，请稍后重试')
      } finally {
        this.loading = false
      }
    },
    
    async createGoal() {
      this.creating = true
      try {
        await this.$refs.goalFormRef.validate()
        
        const response = await dataAnalysisAPI.createLearningGoal(this.newGoal)
        
        ElMessage.success('学习目标创建成功')
        this.showCreateDialog = false
        this.resetNewGoal()
        await this.loadGoals()
        
      } catch (error) {
        if (error.fields) {
          // 表单验证错误
          return
        }
        
        console.error('创建目标失败:', error)
        ElMessage.error('创建目标失败，请稍后重试')
      } finally {
        this.creating = false
      }
    },
    
    async viewGoalDetails(goal) {
      this.selectedGoal = goal
      this.showDetailDialog = true
      
      // 等待DOM更新后初始化图表
      this.$nextTick(() => {
        this.initTrackingChart(goal)
      })
    },
    
    editGoal(goal) {
      // 编辑目标功能
      ElMessage.info('编辑目标功能开发中...')
    },
    
    async handleGoalAction(command) {
      const { action, goal } = command
      
      try {
        switch (action) {
          case 'pause':
            await this.pauseGoal(goal)
            break
          case 'complete':
            await this.completeGoal(goal)
            break
          case 'delete':
            await this.deleteGoal(goal)
            break
        }
      } catch (error) {
        console.error(`执行目标操作失败:`, error)
        ElMessage.error('操作失败，请稍后重试')
      }
    },
    
    async pauseGoal(goal) {
      await ElMessageBox.confirm(
        `确定要暂停目标"${goal.title}"吗？`,
        '暂停目标',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
      
      // 这里应该调用API更新目标状态
      ElMessage.success('目标已暂停')
      await this.loadGoals()
    },
    
    async completeGoal(goal) {
      await ElMessageBox.confirm(
        `确定要标记目标"${goal.title}"为已完成吗？`,
        '完成目标',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'success'
        }
      )
      
      // 这里应该调用API更新目标状态
      ElMessage.success('目标已完成！恭喜你！')
      await this.loadGoals()
    },
    
    async deleteGoal(goal) {
      await ElMessageBox.confirm(
        `确定要删除目标"${goal.title}"吗？此操作不可恢复。`,
        '删除目标',
        {
          confirmButtonText: '确定删除',
          cancelButtonText: '取消',
          type: 'error'
        }
      )
      
      await dataAnalysisAPI.deleteLearningGoal(goal.id)
      ElMessage.success('目标已删除')
      await this.loadGoals()
    },
    
    initTrackingChart(goal) {
      if (!goal.trackingData) return
      
      const chartRef = this.$refs[`detailChart_${goal.id}`]
      if (!chartRef || !chartRef[0]) return
      
      const chart = echarts.init(chartRef[0])
      
      const progressHistory = goal.trackingData.progress_history || []
      const xAxisData = progressHistory.map(item => item.date)
      const progressData = progressHistory.map(item => item.progress)
      const targetData = progressHistory.map((item, index) => {
        return (index + 1) * (goal.target_expressions / progressHistory.length)
      })
      
      const option = {
        title: {
          text: '进度追踪',
          left: 'center',
          textStyle: {
            fontSize: 14
          }
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross'
          }
        },
        legend: {
          data: ['实际进度', '目标进度'],
          top: 30
        },
        xAxis: {
          type: 'category',
          data: xAxisData,
          axisLabel: {
            rotate: 45,
            fontSize: 10
          }
        },
        yAxis: {
          type: 'value',
          name: '表达数量',
          min: 0,
          max: goal.target_expressions
        },
        series: [
          {
            name: '实际进度',
            type: 'line',
            data: progressData,
            smooth: true,
            itemStyle: { color: '#409EFF' },
            areaStyle: { opacity: 0.3 }
          },
          {
            name: '目标进度',
            type: 'line',
            data: targetData,
            lineStyle: { 
              type: 'dashed',
              color: '#67C23A'
            },
            itemStyle: { color: '#67C23A' }
          }
        ],
        grid: {
          left: '10%',
          right: '10%',
          bottom: '15%',
          top: '20%'
        }
      }
      
      chart.setOption(option)
      
      // 响应式调整
      const resizeHandler = () => chart.resize()
      window.addEventListener('resize', resizeHandler)
      
      // 组件销毁时清理
      this.$once('hook:beforeDestroy', () => {
        window.removeEventListener('resize', resizeHandler)
        chart.dispose()
      })
    },
    
    calculateDailyTarget() {
      if (!this.newGoal.target_expressions || !this.newGoal.deadline) {
        return 2
      }
      
      const deadline = new Date(this.newGoal.deadline)
      const today = new Date()
      const daysRemaining = Math.ceil((deadline - today) / (1000 * 60 * 60 * 24))
      
      if (daysRemaining <= 0) return this.newGoal.target_expressions
      
      return Math.ceil(this.newGoal.target_expressions / daysRemaining)
    },
    
    disabledDate(time) {
      // 禁用今天之前的日期
      return time.getTime() < Date.now() - 24 * 60 * 60 * 1000
    },
    
    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString('zh-CN')
    },
    
    formatPercentage(value) {
      if (!value && value !== 0) return '0%'
      return `${(value * 100).toFixed(1)}%`
    },
    
    isOverdue(deadline) {
      return new Date(deadline) < new Date()
    },
    
    getDaysRemaining(deadline) {
      const deadlineDate = new Date(deadline)
      const today = new Date()
      const diffTime = deadlineDate - today
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
      
      if (diffDays < 0) return '已逾期'
      if (diffDays === 0) return '今天'
      return `${diffDays}天`
    },
    
    getPriorityType(priority) {
      const map = {
        low: 'info',
        medium: 'warning',
        high: 'danger'
      }
      return map[priority] || 'info'
    },
    
    getPriorityText(priority) {
      const map = {
        low: '低',
        medium: '中',
        high: '高'
      }
      return map[priority] || priority
    },
    
    getStatusType(status) {
      const map = {
        active: 'success',
        paused: 'warning',
        completed: 'info'
      }
      return map[status] || 'info'
    },
    
    getStatusText(status) {
      const map = {
        active: '进行中',
        paused: '已暂停',
        completed: '已完成'
      }
      return map[status] || status
    },
    
    getProgressColor(rate) {
      if (rate >= 0.8) return '#67C23A'
      if (rate >= 0.6) return '#E6A23C'
      if (rate >= 0.4) return '#409EFF'
      return '#F56C6C'
    },
    
    refreshGoals() {
      this.loadGoals()
    },
    
    handleCreateDialogClose() {
      this.showCreateDialog = false
      this.resetNewGoal()
    },
    
    handleDetailDialogClose() {
      this.showDetailDialog = false
      this.selectedGoal = null
    },
    
    resetNewGoal() {
      this.newGoal = {
        title: '',
        description: '',
        target_expressions: 50,
        priority: 'medium',
        deadline: '',
        daily_target: 2
      }
      
      if (this.$refs.goalFormRef) {
        this.$refs.goalFormRef.resetFields()
      }
    }
  }
}
</script>

<style scoped>
.goal-tracker {
  margin-bottom: 20px;
}

.tracker-card {
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  color: #303133;
  font-size: 18px;
  font-weight: 500;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.goals-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.goal-item {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 20px;
  background: white;
  transition: all 0.3s;
}

.goal-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.goal-item.completed {
  opacity: 0.8;
  background: #f8f9fa;
}

.goal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.goal-title-section {
  display: flex;
  align-items: center;
  flex: 1;
}

.goal-title {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.goal-actions {
  display: flex;
  gap: 5px;
}

.goal-description {
  font-size: 14px;
  color: #606266;
  margin-bottom: 15px;
  line-height: 1.5;
}

.goal-progress {
  margin-bottom: 15px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.progress-text {
  font-size: 14px;
  color: #606266;
}

.progress-percentage {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.goal-timeline {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
}

.timeline-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.timeline-label {
  color: #909399;
  margin-bottom: 4px;
}

.timeline-value {
  color: #303133;
  font-weight: 500;
}

.timeline-value.overdue {
  color: #F56C6C;
}

.goal-chart {
  margin-top: 15px;
  border-top: 1px solid #f0f0f0;
  padding-top: 15px;
}

.mini-chart {
  height: 200px;
  width: 100%;
}

.empty-state {
  padding: 40px;
  text-align: center;
}

.form-hint {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.goal-detail {
  padding: 10px 0;
}

.detail-header {
  text-align: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e4e7ed;
}

.detail-header h2 {
  margin: 0 0 15px 0;
  color: #303133;
}

.detail-meta {
  display: flex;
  justify-content: center;
  gap: 10px;
}

.detail-progress {
  margin-bottom: 30px;
}

.detail-progress h3 {
  margin: 0 0 20px 0;
  color: #303133;
}

.progress-overview {
  display: flex;
  align-items: center;
  gap: 40px;
}

.progress-circle {
  flex-shrink: 0;
}

.progress-stats {
  display: flex;
  flex: 1;
  justify-content: space-around;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #409EFF;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #606266;
}

.detail-chart {
  margin-bottom: 20px;
}

.detail-chart h3 {
  margin: 0 0 15px 0;
  color: #303133;
}

.tracking-chart {
  height: 300px;
  width: 100%;
}

@media (max-width: 768px) {
  .goal-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .goal-actions {
    margin-top: 10px;
    align-self: flex-end;
  }
  
  .goal-timeline {
    flex-direction: column;
    gap: 10px;
  }
  
  .timeline-item {
    flex-direction: row;
    justify-content: space-between;
  }
  
  .progress-overview {
    flex-direction: column;
    text-align: center;
  }
  
  .progress-stats {
    margin-top: 20px;
  }
}
</style>
