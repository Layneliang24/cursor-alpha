<template>
  <div class="learning-analytics-page">
    <!-- 页面导航 -->
    <div class="page-nav">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/english' }">英语学习</el-breadcrumb-item>
        <el-breadcrumb-item>学习分析</el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <!-- 快速统计卡片 -->
    <div class="quick-stats" v-if="quickStats">
      <div class="stat-card">
        <div class="stat-icon">
          <i class="el-icon-reading"></i>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ quickStats.total_expressions || 0 }}</div>
          <div class="stat-label">学习表达总数</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">
          <i class="el-icon-medal"></i>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ formatPercentage(quickStats.mastery_rate) }}</div>
          <div class="stat-label">平均掌握率</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">
          <i class="el-icon-timer"></i>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ formatDuration(quickStats.study_time_today) }}</div>
          <div class="stat-label">今日学习时长</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">
          <i class="el-icon-trophy"></i>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ quickStats.streak_days || 0 }}</div>
          <div class="stat-label">连续学习天数</div>
        </div>
      </div>
    </div>

    <!-- 主要仪表板 -->
    <LearningAnalyticsDashboard 
      ref="dashboard"
      @navigation-request="handleNavigationRequest"
    />

    <!-- 加载遮罩 -->
    <div class="page-loading" v-if="pageLoading">
      <el-loading-spinner />
      <p>正在加载学习分析数据...</p>
    </div>
  </div>
</template>

<script>
import LearningAnalyticsDashboard from '@/components/charts/analytics/LearningAnalyticsDashboard.vue'
import { dataAnalysisAPI } from '@/api/english'
import { ElMessage } from 'element-plus'

export default {
  name: 'LearningAnalytics',
  components: {
    LearningAnalyticsDashboard
  },
  data() {
    return {
      pageLoading: true,
      quickStats: null
    }
  },
  async mounted() {
    await this.loadQuickStats()
    this.pageLoading = false
  },
  methods: {
    async loadQuickStats() {
      try {
        // 模拟快速统计数据，实际应该调用专门的API
        const response = await dataAnalysisAPI.getLearningInsights()
        
        if (response.data && response.data.overview) {
          this.quickStats = {
            total_expressions: response.data.overview.total_expressions || 0,
            mastery_rate: response.data.overview.avg_mastery || 0,
            study_time_today: response.data.overview.study_time_today || 0,
            streak_days: response.data.overview.learning_streak || 0
          }
        }
      } catch (error) {
        console.error('加载快速统计失败:', error)
        // 设置默认值
        this.quickStats = {
          total_expressions: 0,
          mastery_rate: 0,
          study_time_today: 0,
          streak_days: 0
        }
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
    
    handleNavigationRequest(route) {
      // 处理从仪表板发起的导航请求
      this.$router.push(route)
    }
  }
}
</script>

<style scoped>
.learning-analytics-page {
  min-height: 100vh;
  background: #f5f7fa;
}

.page-nav {
  padding: 15px 20px;
  background: white;
  border-bottom: 1px solid #e4e7ed;
}

.quick-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  padding: 20px;
  margin-bottom: 0;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.15);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
}

.stat-icon i {
  color: white;
  font-size: 24px;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #606266;
}

.page-loading {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.page-loading p {
  margin-top: 15px;
  color: #606266;
  font-size: 14px;
}

@media (max-width: 768px) {
  .quick-stats {
    grid-template-columns: repeat(2, 1fr);
    gap: 15px;
    padding: 15px;
  }
  
  .stat-card {
    padding: 15px;
  }
  
  .stat-icon {
    width: 50px;
    height: 50px;
    margin-right: 12px;
  }
  
  .stat-icon i {
    font-size: 20px;
  }
  
  .stat-value {
    font-size: 24px;
  }
  
  .stat-label {
    font-size: 13px;
  }
}

@media (max-width: 480px) {
  .quick-stats {
    grid-template-columns: 1fr;
  }
}
</style>
