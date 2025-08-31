<template>
  <div class="expression-learning">
    <!-- 加载状态 -->
    <div v-if="!isLoaded" v-loading="true" element-loading-text="正在加载学习内容..." class="loading-container">
      <div style="height: 400px; display: flex; align-items: center; justify-content: center;">
        <span>加载中...</span>
      </div>
    </div>
    
    <!-- 主要内容 -->
    <div v-else>
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1>地道表达学习</h1>
        <p class="subtitle">提升英语表达的地道性和准确性</p>
      </div>
      
      <div class="header-actions">
        <el-button type="primary" @click="openDashboard" :icon="TrendCharts">
          学习统计
        </el-button>
        <el-button type="success" @click="startAIChat" :icon="ChatDotSquare">
          AI助教
        </el-button>
      </div>
    </div>
    
    <!-- 学习模式选择 -->
    <el-card class="mode-selector">
      <template #header>
        <span>选择学习模式</span>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="6">
          <div 
            class="mode-card" 
            :class="{ 'active': currentMode === 'flashcard' }"
            @click="setMode('flashcard')"
          >
            <el-icon size="32"><Postcard /></el-icon>
            <h3>闪卡学习</h3>
            <p>通过翻转卡片快速学习表达式</p>
          </div>
        </el-col>
        
        <el-col :span="6">
          <div 
            class="mode-card" 
            :class="{ 'active': currentMode === 'scenario' }"
            @click="setMode('scenario')"
          >
            <el-icon size="32"><VideoPlay /></el-icon>
            <h3>情景学习</h3>
            <p>在真实场景中学习表达用法</p>
          </div>
        </el-col>
        
        <el-col :span="6">
          <div 
            class="mode-card" 
            :class="{ 'active': currentMode === 'ai_chat' }"
            @click="setMode('ai_chat')"
          >
            <el-icon size="32"><ChatDotSquare /></el-icon>
            <h3>AI对话</h3>
            <p>与AI助教互动式学习</p>
          </div>
        </el-col>
        
        <el-col :span="6">
          <div 
            class="mode-card" 
            :class="{ 'active': currentMode === 'review' }"
            @click="setMode('review')"
          >
            <el-icon size="32"><Refresh /></el-icon>
            <h3>复习模式</h3>
            <p>复习需要加强的表达式</p>
          </div>
        </el-col>
      </el-row>
    </el-card>
    
    <!-- 学习内容区域 -->
    <div class="learning-content">
      <!-- 闪卡模式 -->
      <div v-if="currentMode === 'flashcard'" class="flashcard-mode">
        <div class="flashcard-controls">
          <el-button @click="previousCard" :disabled="currentCardIndex <= 0">
            <el-icon><ArrowLeft /></el-icon>
            上一张
          </el-button>
          
          <span class="card-counter">
            {{ currentCardIndex + 1 }} / {{ currentExpressions?.length || 0 }}
          </span>
          
          <el-button @click="nextCard" :disabled="currentCardIndex >= (currentExpressions?.length || 0) - 1">
            下一张
            <el-icon><ArrowRight /></el-icon>
          </el-button>
        </div>
        
        <div class="flashcard-container">
          <ExpressionCard
            v-if="currentExpression"
            :expression="currentExpression"
            :user-progress="getCurrentProgress()"
            :show-pronunciation="settings.show_pronunciation"
            @flip="handleCardFlip"
            @favorite="handleFavorite"
            @mastery="handleMastery"
            @audio-play="handleAudioPlay"
          />
        </div>
      </div>
      
      <!-- 情景模式 -->
      <div v-if="currentMode === 'scenario'" class="scenario-mode">
        <div class="scenario-selector">
          <el-select v-model="selectedScenarioId" placeholder="选择学习场景" @change="loadScenario">
            <el-option
              v-for="scenario in availableScenarios"
              :key="scenario.id"
              :label="scenario.scenario_name"
              :value="scenario.id"
            />
          </el-select>
        </div>
        
        <div class="scenario-container" v-if="currentScenario">
          <ScenarioPlayer
            :scenario="currentScenario"
            :auto-play="settings.auto_play_audio"
            @expression-click="handleExpressionClick"
            @play-state-change="handlePlayStateChange"
          />
        </div>
      </div>
      
      <!-- AI对话模式 -->
      <div v-if="currentMode === 'ai_chat'" class="ai-chat-mode">
        <AIAssistantChat
          :context-expression="selectedExpression"
          :auto-focus="true"
          @messages-sent="handleMessageSent"
          @context-change="handleContextChange"
          @expression-select="handleExpressionSelect"
        />
      </div>
      
      <!-- 复习模式 -->
      <div v-if="currentMode === 'review'" class="review-mode">
        <div class="review-header">
          <h3>今日复习 ({{ needReviewExpressions?.length || 0 }}个)</h3>
          <el-button type="primary" @click="startReview" v-if="!reviewSession.active">
            开始复习
          </el-button>
        </div>
        
        <div class="review-content" v-if="reviewSession.active">
          <div class="review-progress">
            <el-progress 
              :percentage="reviewProgress" 
              :show-text="false"
              :stroke-width="8"
            />
            <span class="progress-text">
              {{ reviewSession.currentIndex + 1 }} / {{ reviewSession.expressions?.length || 0 }}
            </span>
          </div>
          
          <ExpressionCard
            v-if="reviewSession.currentExpression"
            :expression="reviewSession.currentExpression"
            :user-progress="getCurrentProgress()"
            :auto-flip="true"
            :flip-delay="5000"
            @mastery="handleReviewMastery"
          />
          
          <div class="review-actions">
            <el-button @click="reviewEasy" type="success">
              <el-icon><Check /></el-icon>
              简单 (3天后)
            </el-button>
            <el-button @click="reviewMedium" type="warning">
              <el-icon><Clock /></el-icon>
              一般 (1天后)
            </el-button>
            <el-button @click="reviewHard" type="danger">
              <el-icon><Close /></el-icon>
              困难 (稍后)
            </el-button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 学习统计对话框 -->
    <el-dialog v-model="showDashboard" title="学习统计" width="90%" top="5vh">
      <LearningDashboard 
        @start-learning="closeDashboardAndStart"
        @goal-created="handleGoalCreated"
      />
    </el-dialog>
    </div> <!-- 主要内容结束 -->
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue'
import { storeToRefs } from 'pinia'
import { ElMessage } from 'element-plus'
import { 
  TrendCharts, ChatDotSquare, Postcard, VideoPlay, Refresh,
  ArrowLeft, ArrowRight, Check, Clock, Close
} from '@element-plus/icons-vue'
import ExpressionCard from '@/components/idiomatic-expressions/ExpressionCard.vue'
import ScenarioPlayer from '@/components/idiomatic-expressions/ScenarioPlayer.vue'
import LearningDashboard from '@/components/idiomatic-expressions/LearningDashboard.vue'
import AIAssistantChat from '@/components/idiomatic-expressions/AIAssistantChat.vue'
import { useExpressionStore } from '@/stores/modules/expressionStore'
import { useLearningStore } from '@/stores/modules/learningStore'
import type { IdiomaticExpression } from '@/stores/modules/expressionStore'

// Stores
const expressionStore = useExpressionStore()
const learningStore = useLearningStore()

// 使用 storeToRefs 获取响应式引用
const { 
  expressions, 
  userProgress, 
  needReviewExpressions, 
  loading 
} = storeToRefs(expressionStore)

// 状态
const currentMode = ref<'flashcard' | 'scenario' | 'ai_chat' | 'review'>('flashcard')
const currentCardIndex = ref(0)
const selectedScenarioId = ref<number | null>(null)
const selectedExpression = ref<IdiomaticExpression | null>(null)
const showDashboard = ref(false)
const isLoaded = ref(false)

// 学习会话状态
const reviewSession = reactive({
  active: false,
  expressions: [] as IdiomaticExpression[],
  currentIndex: 0,
  currentExpression: null as IdiomaticExpression | null,
  results: [] as Array<{ expressionId: number, difficulty: 'easy' | 'medium' | 'hard' }>
})

const { settings } = learningStore

const currentExpressions = computed(() => {
  try {
    if (currentMode?.value === 'review') {
      return needReviewExpressions?.value || []
    }
    return expressions?.value || []
  } catch (error) {
    console.warn('Error in currentExpressions computed:', error)
    return []
  }
})

const currentExpression = computed(() => {
  try {
    if (reviewSession?.active) {
      return reviewSession.currentExpression
    }
    const expressions = currentExpressions.value || []
    const index = currentCardIndex.value || 0
    return expressions[index] || null
  } catch (error) {
    console.warn('Error in currentExpression computed:', error)
    return null
  }
})

const availableScenarios = computed(() => {
  // 从表达式中提取场景
  const scenarios = new Map()
  const expressionList = expressions.value || []
  expressionList.forEach(expr => {
    expr.scenarios?.forEach(scenario => {
      if (!scenarios.has(scenario.id)) {
        scenarios.set(scenario.id, scenario)
      }
    })
  })
  return Array.from(scenarios.values())
})

const currentScenario = computed(() => {
  if (!selectedScenarioId.value) return null
  const scenarios = availableScenarios.value || []
  return scenarios.find(s => s.id === selectedScenarioId.value)
})

const reviewProgress = computed(() => {
  if (!reviewSession.active || (reviewSession.expressions?.length || 0) === 0) return 0
  return ((reviewSession.currentIndex + 1) / (reviewSession.expressions?.length || 1)) * 100
})

// 方法
const setMode = (mode: typeof currentMode.value) => {
  currentMode.value = mode
  
  if (mode === 'review' && !reviewSession.active) {
    // 自动开始复习模式
    if (needReviewExpressions?.value && needReviewExpressions.value.length > 0) {
      startReview()
    }
  }
}

const previousCard = () => {
  if (currentCardIndex.value > 0) {
    currentCardIndex.value--
  }
}

const nextCard = () => {
  if (currentCardIndex.value < (currentExpressions.value?.length || 0) - 1) {
    currentCardIndex.value++
  }
}

const getCurrentProgress = () => {
  if (!currentExpression.value) return undefined
  return userProgress.value?.find(p => p.expression_id === currentExpression.value?.id)
}

const handleCardFlip = (flipped: boolean) => {
  // 记录翻转事件，可用于学习分析
  console.log('Card flipped:', flipped)
}

const handleFavorite = async (expressionId: number, isFavorite: boolean) => {
  try {
    await expressionStore.markAsFavorite(expressionId, isFavorite)
    ElMessage.success(isFavorite ? '已添加到收藏' : '已取消收藏')
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const handleMastery = async (expressionId: number, masteryLevel: number) => {
  try {
    await expressionStore.updateMasteryLevel(expressionId, masteryLevel)
    
    // 在闪卡模式下自动切换到下一张
    if (currentMode.value === 'flashcard') {
      setTimeout(() => {
        nextCard()
      }, 1000)
    }
  } catch (error) {
    ElMessage.error('更新失败')
  }
}

const handleAudioPlay = (expression: string) => {
  console.log('Audio played for:', expression)
}

const loadScenario = (scenarioId: number) => {
  selectedScenarioId.value = scenarioId
  // 这里可以加载场景相关的表达式
}

const handleExpressionClick = (expression: any) => {
  // 点击场景中的表达式，切换到表达详情
  const expr = expressions.value?.find(e => e.id === expression.id)
  if (expr) {
    selectedExpression.value = expr
    setMode('ai_chat')
  }
}

const handlePlayStateChange = (isPlaying: boolean) => {
  console.log('Play state changed:', isPlaying)
}

const startAIChat = () => {
  setMode('ai_chat')
  learningStore.startAIConversation('general')
}

const handleMessageSent = (message: string) => {
  console.log('Message sent:', message)
}

const handleContextChange = (context: string) => {
  console.log('Context changed:', context)
}

const handleExpressionSelect = (expressionId: number) => {
  if (expressionId === 0) {
    selectedExpression.value = null
  } else {
    const expr = expressions.value?.find(e => e.id === expressionId)
    selectedExpression.value = expr || null
  }
}

const openDashboard = () => {
  showDashboard.value = true
}

const closeDashboardAndStart = () => {
  showDashboard.value = false
  setMode('flashcard')
}

const handleGoalCreated = (goal: any) => {
  ElMessage.success(`学习目标"${goal.title}"创建成功`)
}

// 复习模式方法
const startReview = () => {
  if (!needReviewExpressions?.value || needReviewExpressions.value.length === 0) {
    ElMessage.info('暂无需要复习的表达式')
    return
  }
  
  reviewSession.active = true
  reviewSession.expressions = [...needReviewExpressions.value]
  reviewSession.currentIndex = 0
  reviewSession.currentExpression = reviewSession.expressions[0]
  reviewSession.results = []
  
  // 开始学习会话
  learningStore.startStudySession('review')
  
  ElMessage.success(`开始复习，共${reviewSession.expressions?.length || 0}个表达式`)
}

const reviewEasy = () => {
  recordReviewResult('easy')
  nextReviewItem()
}

const reviewMedium = () => {
  recordReviewResult('medium')
  nextReviewItem()
}

const reviewHard = () => {
  recordReviewResult('hard')
  nextReviewItem()
}

const recordReviewResult = (difficulty: 'easy' | 'medium' | 'hard') => {
  if (!reviewSession.currentExpression) return
  
  reviewSession.results.push({
    expressionId: reviewSession.currentExpression.id,
    difficulty
  })
  
  // 更新掌握度
  const masteryMap = { easy: 85, medium: 65, hard: 35 }
  handleMastery(reviewSession.currentExpression.id, masteryMap[difficulty])
}

const nextReviewItem = () => {
  if (reviewSession.currentIndex < (reviewSession.expressions?.length || 0) - 1) {
    reviewSession.currentIndex++
    reviewSession.currentExpression = reviewSession.expressions[reviewSession.currentIndex]
  } else {
    // 复习完成
    finishReview()
  }
}

const finishReview = () => {
  const session = learningStore.endStudySession('复习完成')
  
  ElMessage.success(`复习完成！复习了${reviewSession.results?.length || 0}个表达式`)
  
  reviewSession.active = false
  reviewSession.expressions = []
  reviewSession.currentExpression = null
  
  // 显示复习结果
  showReviewResults()
}

const showReviewResults = () => {
  const easy = reviewSession.results?.filter(r => r.difficulty === 'easy').length || 0
  const medium = reviewSession.results?.filter(r => r.difficulty === 'medium').length || 0
  const hard = reviewSession.results?.filter(r => r.difficulty === 'hard').length || 0
  
  ElMessage({
    message: `复习结果：简单 ${easy}个，一般 ${medium}个，困难 ${hard}个`,
    type: 'success',
    duration: 5000
  })
}

const handleReviewMastery = (expressionId: number, masteryLevel: number) => {
  // 在复习模式下的掌握度更新
  handleMastery(expressionId, masteryLevel)
}

// 生命周期
onMounted(async () => {
  try {
    // 初始化数据
    await Promise.all([
      expressionStore.fetchExpressions(),
      expressionStore.fetchUserProgress(),
      learningStore.initialize()
    ])
    
    // 数据加载完成，允许渲染
    isLoaded.value = true
    
    // 如果有需要复习的表达式，提示用户
    if (needReviewExpressions?.value && needReviewExpressions.value.length > 0) {
      ElMessage({
        message: `你有${needReviewExpressions.value.length}个表达式需要复习`,
        type: 'info',
        duration: 3000
      })
    }
  } catch (error) {
    console.error('Error in onMounted:', error)
    // 即使加载失败也要设置isLoaded，避免无限加载
    isLoaded.value = true
  }
})
</script>

<style scoped>
.expression-learning {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.loading-container {
  min-height: 400px;
  position: relative;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-left h1 {
  font-size: 28px;
  color: #303133;
  margin: 0 0 8px 0;
}

.subtitle {
  color: #606266;
  font-size: 14px;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.mode-selector {
  margin-bottom: 24px;
}

.mode-card {
  text-align: center;
  padding: 24px 16px;
  border: 2px solid #ebeef5;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
  height: 140px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 8px;
}

.mode-card:hover {
  border-color: #409eff;
  background: #ecf5ff;
}

.mode-card.active {
  border-color: #409eff;
  background: #409eff;
  color: white;
}

.mode-card h3 {
  font-size: 16px;
  margin: 0;
}

.mode-card p {
  font-size: 12px;
  margin: 0;
  opacity: 0.8;
}

.learning-content {
  min-height: 500px;
}

.flashcard-mode {
  text-align: center;
}

.flashcard-controls {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin-bottom: 24px;
}

.card-counter {
  font-weight: 500;
  color: #606266;
  min-width: 80px;
}

.flashcard-container {
  max-width: 400px;
  margin: 0 auto;
}

.scenario-mode {
  max-width: 800px;
  margin: 0 auto;
}

.scenario-selector {
  margin-bottom: 20px;
  text-align: center;
}

.ai-chat-mode {
  max-width: 800px;
  margin: 0 auto;
}

.review-mode {
  max-width: 600px;
  margin: 0 auto;
}

.review-header {
  text-align: center;
  margin-bottom: 24px;
}

.review-header h3 {
  color: #303133;
  margin-bottom: 16px;
}

.review-progress {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.progress-text {
  font-weight: 500;
  color: #606266;
}

.review-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 24px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .expression-learning {
    padding: 16px;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .header-actions {
    width: 100%;
    justify-content: center;
  }
  
  .mode-selector .el-col {
    margin-bottom: 16px;
  }
  
  .mode-card {
    height: 120px;
    padding: 16px 12px;
  }
  
  .flashcard-controls {
    flex-wrap: wrap;
    gap: 12px;
  }
  
  .review-actions {
    flex-direction: column;
    gap: 12px;
  }
  
  .review-actions .el-button {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .mode-card {
    height: 100px;
    padding: 12px 8px;
  }
  
  .mode-card h3 {
    font-size: 14px;
  }
  
  .mode-card p {
    font-size: 11px;
  }
}
</style>
