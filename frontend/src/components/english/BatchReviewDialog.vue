<template>
  <el-dialog
    v-model="visible"
    title="批量复习单词"
    width="800px"
    :before-close="handleClose"
    :close-on-click-modal="false"
  >
    <div class="review-container" v-if="words.length > 0">
      <!-- 进度条 -->
      <div class="progress-section">
        <div class="progress-info">
          <span>进度: {{ currentIndex + 1 }} / {{ words.length }}</span>
          <span>已完成: {{ completedReviews.length }}</span>
        </div>
        <el-progress 
          :percentage="Math.round((currentIndex / words.length) * 100)" 
          :stroke-width="8"
          color="#409EFF"
        />
      </div>

      <!-- 当前单词卡片 -->
      <div class="word-card" v-if="currentWord">
        <div class="word-header">
          <h2 class="word-text">{{ currentWord.word?.word }}</h2>
          <span class="phonetic" v-if="currentWord.word?.phonetic">
            {{ currentWord.word.phonetic }}
          </span>
        </div>

        <div class="word-content">
          <div class="definition">
            <h4>释义</h4>
            <p>{{ currentWord.word?.definition }}</p>
          </div>

          <div class="example" v-if="currentWord.word?.example">
            <h4>例句</h4>
            <p>{{ currentWord.word.example }}</p>
          </div>

          <div class="progress-info" v-if="currentWord.mastery_level !== undefined">
            <h4>当前掌握度</h4>
            <el-progress 
              :percentage="Math.round(currentWord.mastery_level * 100)"
              :stroke-width="6"
              :color="getProgressColor(currentWord.mastery_level)"
            />
          </div>
        </div>

        <!-- 复习质量评分 -->
        <div class="quality-rating">
          <h4>请评估您对这个单词的掌握程度：</h4>
          <div class="rating-buttons">
            <el-button
              v-for="(rating, index) in qualityRatings"
              :key="index"
              :type="selectedQuality === index ? 'primary' : 'default'"
              :class="{ 'selected': selectedQuality === index }"
              @click="selectQuality(index)"
              size="large"
            >
              <div class="rating-content">
                <span class="rating-score">{{ index }}</span>
                <span class="rating-text">{{ rating.text }}</span>
                <span class="rating-desc">{{ rating.desc }}</span>
              </div>
            </el-button>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="action-buttons">
          <el-button @click="skipWord" :disabled="submitting">
            跳过
          </el-button>
          <el-button 
            type="primary" 
            @click="submitReview"
            :disabled="selectedQuality === null || submitting"
            :loading="submitting"
          >
            下一个
          </el-button>
        </div>
      </div>

      <!-- 完成页面 -->
      <div class="completion-page" v-else-if="isCompleted">
        <div class="completion-content">
          <el-icon class="completion-icon"><SuccessFilled /></el-icon>
          <h2>复习完成！</h2>
          <div class="completion-stats">
            <div class="stat-item">
              <span class="stat-number">{{ completedReviews.length }}</span>
              <span class="stat-label">复习单词</span>
            </div>
            <div class="stat-item">
              <span class="stat-number">{{ averageQuality.toFixed(1) }}</span>
              <span class="stat-label">平均质量</span>
            </div>
            <div class="stat-item">
              <span class="stat-number">{{ totalTime }}</span>
              <span class="stat-label">总用时(秒)</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="empty-state" v-else>
      <el-empty description="暂无需要复习的单词" />
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">
          {{ isCompleted ? '关闭' : '取消' }}
        </el-button>
        <el-button 
          v-if="isCompleted" 
          type="primary" 
          @click="submitAllReviews"
          :loading="finalSubmitting"
        >
          提交复习结果
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script>
import { ref, computed, watch, nextTick } from 'vue'
import { useEnglishStore } from '@/stores/english'
import { ElMessage } from 'element-plus'
import { SuccessFilled } from '@element-plus/icons-vue'

export default {
  name: 'BatchReviewDialog',
  components: {
    SuccessFilled
  },
  props: {
    modelValue: {
      type: Boolean,
      default: false
    },
    words: {
      type: Array,
      default: () => []
    }
  },
  emits: ['update:modelValue', 'completed'],
  setup(props, { emit }) {
    const englishStore = useEnglishStore()
    
    const currentIndex = ref(0)
    const selectedQuality = ref(null)
    const submitting = ref(false)
    const finalSubmitting = ref(false)
    const completedReviews = ref([])
    const startTime = ref(Date.now())
    const wordStartTime = ref(Date.now())

    // 质量评分定义
    const qualityRatings = [
      { text: '完全不记得', desc: '需要重新学习' },
      { text: '很陌生', desc: '答错且很陌生' },
      { text: '有印象', desc: '答错但有印象' },
      { text: '犹豫后想起', desc: '答对但需努力' },
      { text: '较容易想起', desc: '答对稍有犹豫' },
      { text: '完全掌握', desc: '立即想起答案' }
    ]

    // 计算属性
    const visible = computed({
      get: () => props.modelValue,
      set: (value) => emit('update:modelValue', value)
    })

    const currentWord = computed(() => {
      if (currentIndex.value >= props.words.length) return null
      return props.words[currentIndex.value]
    })

    const isCompleted = computed(() => {
      return currentIndex.value >= props.words.length && props.words.length > 0
    })

    const averageQuality = computed(() => {
      if (completedReviews.value.length === 0) return 0
      const sum = completedReviews.value.reduce((acc, review) => acc + review.quality, 0)
      return sum / completedReviews.value.length
    })

    const totalTime = computed(() => {
      return Math.round((Date.now() - startTime.value) / 1000)
    })

    // 方法
    const getProgressColor = (masteryLevel) => {
      if (masteryLevel >= 0.8) return '#67C23A'
      if (masteryLevel >= 0.5) return '#E6A23C'
      return '#F56C6C'
    }

    const selectQuality = (quality) => {
      selectedQuality.value = quality
    }

    const skipWord = () => {
      nextWord()
    }

    const submitReview = async () => {
      if (selectedQuality.value === null) return

      submitting.value = true
      try {
        const timeSpent = Math.round((Date.now() - wordStartTime.value) / 1000)
        
        // 记录复习结果
        completedReviews.value.push({
          word_id: currentWord.value.word.id,
          quality: selectedQuality.value,
          time_spent: timeSpent
        })

        nextWord()
        ElMessage.success(`已记录复习结果，质量评分: ${selectedQuality.value}`)
      } catch (error) {
        ElMessage.error('记录复习结果失败')
        console.error(error)
      } finally {
        submitting.value = false
      }
    }

    const nextWord = () => {
      currentIndex.value++
      selectedQuality.value = null
      wordStartTime.value = Date.now()
    }

    const submitAllReviews = async () => {
      if (completedReviews.value.length === 0) {
        handleClose()
        return
      }

      finalSubmitting.value = true
      try {
        await englishStore.submitBatchReview(completedReviews.value)
        ElMessage.success(`成功提交 ${completedReviews.value.length} 个单词的复习结果`)
        emit('completed')
        handleClose()
      } catch (error) {
        ElMessage.error('提交复习结果失败')
        console.error(error)
      } finally {
        finalSubmitting.value = false
      }
    }

    const resetState = () => {
      currentIndex.value = 0
      selectedQuality.value = null
      completedReviews.value = []
      startTime.value = Date.now()
      wordStartTime.value = Date.now()
    }

    const handleClose = () => {
      visible.value = false
      // 延迟重置状态，避免关闭动画时看到状态变化
      setTimeout(resetState, 300)
    }

    // 监听对话框显示状态
    watch(visible, (newVal) => {
      if (newVal) {
        resetState()
      }
    })

    // 监听当前单词变化，重置选择
    watch(currentIndex, () => {
      selectedQuality.value = null
      wordStartTime.value = Date.now()
    })

    return {
      visible,
      currentIndex,
      currentWord,
      selectedQuality,
      submitting,
      finalSubmitting,
      completedReviews,
      isCompleted,
      averageQuality,
      totalTime,
      qualityRatings,
      getProgressColor,
      selectQuality,
      skipWord,
      submitReview,
      submitAllReviews,
      handleClose
    }
  }
}
</script>

<style scoped>
.review-container {
  padding: 20px 0;
}

.progress-section {
  margin-bottom: 30px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  font-size: 14px;
  color: #606266;
}

.word-card {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 30px;
  text-align: center;
}

.word-header {
  margin-bottom: 30px;
}

.word-text {
  font-size: 36px;
  font-weight: 700;
  color: #303133;
  margin: 0 0 8px 0;
}

.phonetic {
  font-size: 18px;
  color: #909399;
  font-style: italic;
}

.word-content {
  margin-bottom: 30px;
  text-align: left;
}

.word-content h4 {
  color: #606266;
  font-size: 16px;
  margin: 0 0 8px 0;
}

.word-content p {
  color: #303133;
  font-size: 16px;
  line-height: 1.6;
  margin: 0 0 20px 0;
}

.quality-rating {
  margin-bottom: 30px;
}

.quality-rating h4 {
  color: #303133;
  font-size: 18px;
  margin: 0 0 20px 0;
  text-align: center;
}

.rating-buttons {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.rating-buttons .el-button {
  height: auto;
  padding: 16px 12px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.rating-buttons .el-button.selected {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.rating-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.rating-score {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
}

.rating-text {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.rating-desc {
  font-size: 12px;
  color: #909399;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 16px;
}

.action-buttons .el-button {
  padding: 12px 32px;
  font-size: 16px;
}

.completion-page {
  text-align: center;
  padding: 60px 20px;
}

.completion-content {
  max-width: 400px;
  margin: 0 auto;
}

.completion-icon {
  font-size: 80px;
  color: #67C23A;
  margin-bottom: 20px;
}

.completion-content h2 {
  color: #303133;
  font-size: 28px;
  margin: 0 0 30px 0;
}

.completion-stats {
  display: flex;
  justify-content: space-around;
  margin-top: 30px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.stat-number {
  font-size: 32px;
  font-weight: bold;
  color: #409EFF;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.empty-state {
  padding: 40px;
  text-align: center;
}

.dialog-footer {
  text-align: right;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .rating-buttons {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .word-text {
    font-size: 28px;
  }
  
  .completion-stats {
    flex-direction: column;
    gap: 20px;
  }
}
</style>
