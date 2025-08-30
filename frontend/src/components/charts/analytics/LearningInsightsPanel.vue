<template>
  <div class="learning-insights-panel">
    <div class="panel-header">
      <h3>个性化学习洞察</h3>
      <div class="header-controls">
        <el-button
          size="small"
          type="primary"
          @click="refreshInsights"
          :loading="loading"
          icon="el-icon-refresh"
        >
          刷新分析
        </el-button>
      </div>
    </div>
    
    <div class="insights-content" v-loading="loading">
      <!-- 学习概览卡片 -->
      <div class="overview-card" v-if="overviewData">
        <div class="overview-header">
          <i class="el-icon-data-analysis"></i>
          <span>学习概览</span>
        </div>
        <div class="overview-stats">
          <div class="stat-item">
            <div class="stat-value">{{ overviewData.total_expressions || 0 }}</div>
            <div class="stat-label">总学习表达</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ formatPercentage(overviewData.avg_mastery) }}</div>
            <div class="stat-label">平均掌握度</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ formatDuration(overviewData.total_study_time) }}</div>
            <div class="stat-label">总学习时长</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ overviewData.learning_streak || 0 }}</div>
            <div class="stat-label">连续学习天数</div>
          </div>
        </div>
      </div>

      <!-- 智能建议 -->
      <div class="insights-grid">
        <div class="insight-card recommendations" v-if="recommendationsData">
          <div class="card-header">
            <i class="el-icon-lightbulb"></i>
            <span>智能建议</span>
          </div>
          <div class="recommendations-list">
            <div 
              class="recommendation-item"
              v-for="(rec, index) in recommendationsData"
              :key="index"
              :class="rec.priority"
            >
              <div class="rec-icon">
                <i :class="getRecommendationIcon(rec.type)"></i>
              </div>
              <div class="rec-content">
                <div class="rec-title">{{ rec.title }}</div>
                <div class="rec-description">{{ rec.description }}</div>
                <div class="rec-action" v-if="rec.action">
                  <el-button 
                    size="mini" 
                    type="text"
                    @click="handleRecommendationAction(rec)"
                  >
                    {{ rec.action.text }}
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 薄弱环节分析 -->
        <div class="insight-card weak-areas" v-if="weakAreasData">
          <div class="card-header">
            <i class="el-icon-warning"></i>
            <span>薄弱环节</span>
          </div>
          <div class="weak-areas-list">
            <div 
              class="weak-area-item"
              v-for="area in weakAreasData"
              :key="area.expression_id"
            >
              <div class="area-info">
                <div class="area-expression">{{ area.expression }}</div>
                <div class="area-stats">
                  <span class="stat-badge accuracy">
                    准确率: {{ formatPercentage(area.accuracy) }}
                  </span>
                  <span class="stat-badge attempts">
                    练习: {{ area.attempts }}次
                  </span>
                </div>
              </div>
              <div class="area-actions">
                <el-button 
                  size="mini" 
                  type="warning" 
                  plain
                  @click="startPractice(area.expression_id)"
                >
                  重点练习
                </el-button>
              </div>
            </div>
          </div>
        </div>

        <!-- 学习成就 -->
        <div class="insight-card achievements" v-if="achievementsData">
          <div class="card-header">
            <i class="el-icon-trophy"></i>
            <span>学习成就</span>
          </div>
          <div class="achievements-list">
            <div 
              class="achievement-item"
              v-for="achievement in achievementsData"
              :key="achievement.id"
              :class="{ unlocked: achievement.unlocked }"
            >
              <div class="achievement-icon">
                <i :class="achievement.icon"></i>
              </div>
              <div class="achievement-info">
                <div class="achievement-title">{{ achievement.title }}</div>
                <div class="achievement-description">{{ achievement.description }}</div>
                <div class="achievement-progress" v-if="!achievement.unlocked">
                  <el-progress 
                    :percentage="achievement.progress" 
                    :stroke-width="6"
                    :show-text="false"
                  />
                  <span class="progress-text">{{ achievement.progress }}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 学习模式分析 -->
        <div class="insight-card learning-patterns" v-if="patternsData">
          <div class="card-header">
            <i class="el-icon-pie-chart"></i>
            <span>学习模式</span>
          </div>
          <div class="patterns-content">
            <div class="pattern-item" v-for="pattern in patternsData" :key="pattern.name">
              <div class="pattern-label">{{ pattern.label }}</div>
              <div class="pattern-value">{{ pattern.value }}</div>
              <div class="pattern-bar">
                <div 
                  class="pattern-fill"
                  :style="{ 
                    width: `${pattern.percentage}%`,
                    backgroundColor: pattern.color 
                  }"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { dataAnalysisAPI } from '@/api/english'
import { ElMessage } from 'element-plus'

export default {
  name: 'LearningInsightsPanel',
  data() {
    return {
      loading: false,
      overviewData: null,
      recommendationsData: null,
      weakAreasData: null,
      achievementsData: null,
      patternsData: null
    }
  },
  mounted() {
    this.loadInsights()
  },
  methods: {
    async loadInsights() {
      this.loading = true
      try {
        const response = await dataAnalysisAPI.getLearningInsights()
        const data = response.data
        
        this.overviewData = data.overview
        this.recommendationsData = data.recommendations
        this.weakAreasData = data.weak_areas
        this.achievementsData = data.achievements
        this.patternsData = data.learning_patterns
        
      } catch (error) {
        console.error('加载学习洞察数据失败:', error)
        ElMessage.error('加载数据失败，请稍后重试')
      } finally {
        this.loading = false
      }
    },
    
    formatPercentage(value) {
      if (!value && value !== 0) return '0%'
      return `${(value * 100).toFixed(1)}%`
    },
    
    formatDuration(minutes) {
      if (!minutes) return '0分钟'
      
      const hours = Math.floor(minutes / 60)
      const mins = Math.round(minutes % 60)
      
      if (hours > 0) {
        return `${hours}小时${mins}分钟`
      }
      return `${mins}分钟`
    },
    
    getRecommendationIcon(type) {
      const icons = {
        practice: 'el-icon-edit',
        review: 'el-icon-refresh',
        difficulty: 'el-icon-star-off',
        time: 'el-icon-timer',
        method: 'el-icon-setting'
      }
      return icons[type] || 'el-icon-info'
    },
    
    getTrendIcon(trend) {
      switch (trend) {
        case 'up':
          return 'el-icon-caret-top'
        case 'down':
          return 'el-icon-caret-bottom'
        default:
          return 'el-icon-minus'
      }
    },
    
    handleRecommendationAction(recommendation) {
      this.$emit('recommendation-action', recommendation)
      
      // 根据建议类型执行相应操作
      switch (recommendation.type) {
        case 'practice':
          this.startPractice(recommendation.target_id)
          break
        case 'review':
          this.startReview(recommendation.target_id)
          break
        default:
          ElMessage.info('功能开发中...')
      }
    },
    
    startPractice(expressionId) {
      this.$emit('start-practice', expressionId)
      ElMessage.success('开始重点练习')
    },
    
    startReview(expressionId) {
      this.$emit('start-review', expressionId)
      ElMessage.success('开始复习')
    },
    
    refreshInsights() {
      this.loadInsights()
    }
  }
}
</script>

<style scoped>
.learning-insights-panel {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.panel-header h3 {
  margin: 0;
  color: #303133;
  font-size: 18px;
  font-weight: 500;
}

.header-controls {
  display: flex;
  align-items: center;
}

.overview-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
}

.overview-header {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
  font-size: 16px;
  font-weight: 500;
}

.overview-header i {
  margin-right: 8px;
  font-size: 18px;
}

.overview-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 15px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 12px;
  opacity: 0.9;
}

.insights-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 20px;
}

.insight-card {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 15px;
}

.card-header {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.card-header i {
  margin-right: 8px;
  font-size: 16px;
}

.recommendations .card-header {
  color: #409EFF;
}

.weak-areas .card-header {
  color: #E6A23C;
}

.achievements .card-header {
  color: #67C23A;
}

.learning-patterns .card-header {
  color: #909399;
}

.recommendation-item {
  display: flex;
  align-items: flex-start;
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 10px;
  border-left: 4px solid transparent;
}

.recommendation-item.high {
  background: #fef0f0;
  border-left-color: #F56C6C;
}

.recommendation-item.medium {
  background: #fdf6ec;
  border-left-color: #E6A23C;
}

.recommendation-item.low {
  background: #f0f9ff;
  border-left-color: #409EFF;
}

.rec-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #409EFF;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  flex-shrink: 0;
}

.rec-icon i {
  color: white;
  font-size: 14px;
}

.rec-content {
  flex: 1;
}

.rec-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.rec-description {
  font-size: 12px;
  color: #606266;
  line-height: 1.4;
  margin-bottom: 8px;
}

.weak-area-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  border: 1px solid #f0f0f0;
  border-radius: 6px;
  margin-bottom: 8px;
}

.area-expression {
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.area-stats {
  display: flex;
  gap: 8px;
}

.stat-badge {
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11px;
  color: white;
}

.stat-badge.accuracy {
  background: #E6A23C;
}

.stat-badge.attempts {
  background: #909399;
}

.achievement-item {
  display: flex;
  align-items: center;
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 10px;
  opacity: 0.6;
  transition: all 0.3s;
}

.achievement-item.unlocked {
  opacity: 1;
  background: #f0f9ff;
  border: 1px solid #b3d8ff;
}

.achievement-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #67C23A;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
}

.achievement-icon i {
  color: white;
  font-size: 18px;
}

.achievement-info {
  flex: 1;
}

.achievement-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.achievement-description {
  font-size: 12px;
  color: #606266;
  margin-bottom: 8px;
}

.achievement-progress {
  display: flex;
  align-items: center;
}

.progress-text {
  margin-left: 10px;
  font-size: 12px;
  color: #909399;
}

.pattern-item {
  margin-bottom: 15px;
}

.pattern-label {
  font-size: 13px;
  color: #606266;
  margin-bottom: 6px;
}

.pattern-value {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 8px;
}

.pattern-bar {
  height: 8px;
  background: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
}

.pattern-fill {
  height: 100%;
  transition: width 0.5s ease;
}

@media (max-width: 768px) {
  .panel-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .header-controls {
    margin-top: 10px;
  }
  
  .insights-grid {
    grid-template-columns: 1fr;
  }
  
  .overview-stats {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
