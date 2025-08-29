<template>
  <div class="expression-card" :class="{ 'is-flipped': isFlipped }">
    <div class="card-inner">
      <!-- 正面 - 表达式 -->
      <div class="card-front" @click="flipCard">
        <div class="card-header">
          <div class="difficulty-badge" :class="`difficulty-${expression.difficulty_level}`">
            {{ getDifficultyText(expression.difficulty_level) }}
          </div>
          <div class="formality-badge" :class="`formality-${expression.formality_level}`">
            {{ getFormalityText(expression.formality_level) }}
          </div>
        </div>
        
        <div class="expression-content">
          <h3 class="expression-text">{{ expression.expression }}</h3>
          <div class="pronunciation" v-if="showPronunciation">
            <span class="phonetic">{{ expression.pronunciation }}</span>
            <el-button 
              type="text" 
              @click.stop="playAudio" 
              :loading="audioLoading"
              class="audio-btn"
            >
              <el-icon><VideoPlay /></el-icon>
            </el-button>
          </div>
        </div>
        
        <div class="card-footer">
          <div class="frequency-indicator">
            <span class="frequency-label">使用频率:</span>
            <div class="frequency-bars">
              <div 
                v-for="i in 3" 
                :key="i"
                class="frequency-bar"
                :class="{ 'active': getFrequencyLevel(expression.usage_frequency) >= i }"
              ></div>
            </div>
          </div>
          <div class="flip-hint">
            <el-icon><RefreshLeft /></el-icon>
            点击翻转查看含义
          </div>
        </div>
      </div>
      
      <!-- 背面 - 含义和例句 -->
      <div class="card-back" @click="flipCard">
        <div class="card-header">
          <div class="mastery-level" v-if="userProgress">
            <span class="mastery-label">掌握度:</span>
            <el-progress 
              :percentage="userProgress.mastery_level" 
              :color="getMasteryColor(userProgress.mastery_level)"
              :show-text="false"
              :stroke-width="6"
            />
            <span class="mastery-text">{{ userProgress.mastery_level }}%</span>
          </div>
        </div>
        
        <div class="meaning-content">
          <h4 class="meaning-title">含义</h4>
          <p class="meaning-text">{{ expression.meaning }}</p>
          
          <div class="explanation" v-if="expression.explanation">
            <h5>详细解释</h5>
            <p>{{ expression.explanation }}</p>
          </div>
          
          <div class="examples" v-if="expression.usage_examples?.length">
            <h5>使用示例</h5>
            <div class="example-item" v-for="(example, index) in expression.usage_examples.slice(0, 2)" :key="index">
              <p class="example-text">"{{ example.example }}"</p>
              <p class="example-translation">{{ example.translation }}</p>
              <span class="example-context" v-if="example.context">{{ example.context }}</span>
            </div>
          </div>
        </div>
        
        <div class="card-actions">
          <el-button-group>
            <el-button 
              type="success" 
              size="small" 
              @click.stop="markAsKnown"
              :loading="actionLoading.known"
            >
              <el-icon><Check /></el-icon>
              掌握
            </el-button>
            <el-button 
              type="warning" 
              size="small" 
              @click.stop="markForReview"
              :loading="actionLoading.review"
            >
              <el-icon><Clock /></el-icon>
              复习
            </el-button>
            <el-button 
              :type="userProgress?.is_favorite ? 'danger' : 'primary'" 
              size="small" 
              @click.stop="toggleFavorite"
              :loading="actionLoading.favorite"
            >
              <el-icon>
                <StarFilled v-if="userProgress?.is_favorite" />
                <Star v-else />
              </el-icon>
              {{ userProgress?.is_favorite ? '取消收藏' : '收藏' }}
            </el-button>
          </el-button-group>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  VideoPlay, RefreshLeft, Check, Clock, Star, StarFilled 
} from '@element-plus/icons-vue'
import type { IdiomaticExpression, UserExpressionProgress } from '@/stores/modules/expressionStore'
import { useExpressionStore } from '@/stores/modules/expressionStore'
import { useLearningStore } from '@/stores/modules/learningStore'

// Props
interface Props {
  expression: IdiomaticExpression
  userProgress?: UserExpressionProgress
  showPronunciation?: boolean
  autoFlip?: boolean
  flipDelay?: number
}

const props = withDefaults(defineProps<Props>(), {
  showPronunciation: true,
  autoFlip: false,
  flipDelay: 3000
})

// Emits
const emit = defineEmits<{
  flip: [flipped: boolean]
  favorite: [expressionId: number, isFavorite: boolean]
  mastery: [expressionId: number, masteryLevel: number]
  audioPlay: [expression: string]
}>()

// Stores
const expressionStore = useExpressionStore()
const learningStore = useLearningStore()

// 状态
const isFlipped = ref(false)
const audioLoading = ref(false)
const actionLoading = reactive({
  known: false,
  review: false,
  favorite: false
})

// 计算属性
const getDifficultyText = (level: string) => {
  const map = {
    beginner: '初级',
    intermediate: '中级', 
    advanced: '高级'
  }
  return map[level] || level
}

const getFormalityText = (level: string) => {
  const map = {
    informal: '非正式',
    neutral: '中性',
    formal: '正式'
  }
  return map[level] || level
}

const getFrequencyLevel = (frequency: string) => {
  const map = {
    low: 1,
    medium: 2,
    high: 3
  }
  return map[frequency] || 1
}

const getMasteryColor = (level: number) => {
  if (level >= 80) return '#67c23a'
  if (level >= 60) return '#e6a23c'
  if (level >= 40) return '#f56c6c'
  return '#909399'
}

// 方法
const flipCard = () => {
  isFlipped.value = !isFlipped.value
  emit('flip', isFlipped.value)
}

const playAudio = async () => {
  audioLoading.value = true
  try {
    // 使用浏览器的语音合成API
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(props.expression.expression)
      utterance.lang = 'en-US'
      utterance.rate = 0.8
      speechSynthesis.speak(utterance)
    }
    
    emit('audioPlay', props.expression.expression)
  } catch (error) {
    console.error('音频播放失败:', error)
    ElMessage.error('音频播放失败')
  } finally {
    audioLoading.value = false
  }
}

const markAsKnown = async () => {
  actionLoading.known = true
  try {
    await expressionStore.updateMasteryLevel(props.expression.id, 85)
    ElMessage.success('已标记为掌握')
    emit('mastery', props.expression.id, 85)
    
    // 更新学习会话进度
    learningStore.updateSessionProgress(true, props.expression.id)
    
  } catch (error) {
    console.error('标记掌握失败:', error)
    ElMessage.error('操作失败，请重试')
  } finally {
    actionLoading.known = false
  }
}

const markForReview = async () => {
  actionLoading.review = true
  try {
    await expressionStore.updateMasteryLevel(props.expression.id, 30)
    ElMessage.success('已加入复习队列')
    emit('mastery', props.expression.id, 30)
    
    // 更新学习会话进度
    learningStore.updateSessionProgress(false, props.expression.id)
    
  } catch (error) {
    console.error('标记复习失败:', error)
    ElMessage.error('操作失败，请重试')
  } finally {
    actionLoading.review = false
  }
}

const toggleFavorite = async () => {
  actionLoading.favorite = true
  try {
    const newFavoriteStatus = !props.userProgress?.is_favorite
    await expressionStore.markAsFavorite(props.expression.id, newFavoriteStatus)
    ElMessage.success(newFavoriteStatus ? '已添加到收藏' : '已取消收藏')
    emit('favorite', props.expression.id, newFavoriteStatus)
    
  } catch (error) {
    console.error('收藏操作失败:', error)
    ElMessage.error('操作失败，请重试')
  } finally {
    actionLoading.favorite = false
  }
}

// 自动翻转逻辑
if (props.autoFlip) {
  setTimeout(() => {
    flipCard()
  }, props.flipDelay)
}
</script>

<style scoped>
.expression-card {
  perspective: 1000px;
  width: 100%;
  height: 300px;
  margin-bottom: 20px;
}

.card-inner {
  position: relative;
  width: 100%;
  height: 100%;
  text-align: center;
  transition: transform 0.6s;
  transform-style: preserve-3d;
  cursor: pointer;
}

.is-flipped .card-inner {
  transform: rotateY(180deg);
}

.card-front,
.card-back {
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  padding: 20px;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.card-back {
  transform: rotateY(180deg);
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.difficulty-badge,
.formality-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
  text-transform: uppercase;
}

.difficulty-beginner { background: rgba(103, 194, 58, 0.8); }
.difficulty-intermediate { background: rgba(230, 162, 60, 0.8); }
.difficulty-advanced { background: rgba(245, 108, 108, 0.8); }

.formality-informal { background: rgba(64, 158, 255, 0.8); }
.formality-neutral { background: rgba(144, 147, 153, 0.8); }
.formality-formal { background: rgba(103, 194, 58, 0.8); }

.expression-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.expression-text {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 15px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.pronunciation {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 10px;
}

.phonetic {
  font-style: italic;
  color: rgba(255, 255, 255, 0.9);
}

.audio-btn {
  color: white !important;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 20px;
}

.frequency-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
}

.frequency-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
}

.frequency-bars {
  display: flex;
  gap: 2px;
}

.frequency-bar {
  width: 4px;
  height: 16px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 2px;
  transition: background 0.3s;
}

.frequency-bar.active {
  background: rgba(255, 255, 255, 0.9);
}

.flip-hint {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
}

/* 背面样式 */
.mastery-level {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
}

.mastery-label {
  font-size: 14px;
  white-space: nowrap;
}

.mastery-text {
  font-size: 14px;
  font-weight: bold;
}

.meaning-content {
  flex: 1;
  text-align: left;
}

.meaning-title {
  font-size: 18px;
  margin-bottom: 10px;
  color: rgba(255, 255, 255, 0.9);
}

.meaning-text {
  font-size: 16px;
  line-height: 1.5;
  margin-bottom: 15px;
}

.explanation h5,
.examples h5 {
  font-size: 14px;
  margin: 10px 0 8px 0;
  color: rgba(255, 255, 255, 0.9);
}

.explanation p {
  font-size: 14px;
  line-height: 1.4;
  color: rgba(255, 255, 255, 0.8);
}

.example-item {
  margin-bottom: 12px;
  padding: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 6px;
}

.example-text {
  font-style: italic;
  margin-bottom: 4px;
}

.example-translation {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 2px;
}

.example-context {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.6);
}

.card-actions {
  margin-top: 15px;
}

.card-actions .el-button {
  color: white;
  border-color: rgba(255, 255, 255, 0.3);
}

.card-actions .el-button:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.5);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .expression-card {
    height: 280px;
  }
  
  .expression-text {
    font-size: 20px;
  }
  
  .card-footer {
    flex-direction: column;
    gap: 10px;
  }
  
  .card-actions .el-button {
    padding: 6px 12px;
    font-size: 12px;
  }
}

/* 动画效果 */
.expression-card:hover .card-inner {
  transform: scale(1.02);
}

.is-flipped:hover .card-inner {
  transform: rotateY(180deg) scale(1.02);
}

.card-inner {
  transition: transform 0.6s, box-shadow 0.3s;
}

.expression-card:hover .card-front,
.expression-card:hover .card-back {
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}
</style>
