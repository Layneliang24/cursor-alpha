/**
 * 学习状态管理Store
 * 管理学习会话、统计数据、AI对话等功能
 */
import { defineStore } from 'pinia'
import { ref, computed, reactive } from 'vue'
import { englishAPI } from '@/api/english'

// 类型定义
export interface LearningStatistics {
  total_expressions: number
  learned_expressions: number
  favorite_expressions: number
  review_due: number
  learning_streak: number
  total_study_time: number
  average_mastery: number
  weekly_progress: Array<{
    date: string
    expressions_learned: number
    study_time: number
  }>
  mastery_distribution: {
    beginner: number
    intermediate: number
    advanced: number
    mastered: number
  }
  difficulty_breakdown: {
    beginner: number
    intermediate: number
    advanced: number
  }
  weak_areas: Array<{
    category: string
    mastery_rate: number
    total_expressions: number
  }>
}

export interface AIConversation {
  id: string
  messages: Array<{
    id: string
    role: 'user' | 'assistant'
    content: string
    timestamp: string
    expression_id?: number
  }>
  context: 'general' | 'expression_help' | 'practice' | 'review'
  created_at: string
  updated_at: string
}

export interface LearningGoal {
  id: number
  title: string
  description: string
  target_expressions: number
  current_progress: number
  deadline: string
  priority: 'low' | 'medium' | 'high'
  status: 'active' | 'paused' | 'completed'
  created_at: string
}

export interface StudySession {
  id: string
  start_time: string
  end_time?: string
  expressions_studied: number
  correct_answers: number
  total_answers: number
  session_type: 'flashcard' | 'scenario' | 'ai_chat' | 'review'
  performance_score: number
  notes: string
}

// Store定义
export const useLearningStore = defineStore('learning', () => {
  // 状态
  const statistics = ref<LearningStatistics | null>(null)
  const aiConversations = ref<AIConversation[]>([])
  const currentConversation = ref<AIConversation | null>(null)
  const learningGoals = ref<LearningGoal[]>([])
  const studySessions = ref<StudySession[]>([])
  const currentSession = ref<StudySession | null>(null)
  
  // 加载状态
  const loading = reactive({
    statistics: false,
    conversations: false,
    goals: false,
    sessions: false,
    ai_response: false,
  })
  
  // 学习配置
  const settings = reactive({
    daily_goal: 10,
    review_interval: 24,
    difficulty_preference: 'adaptive' as 'easy' | 'medium' | 'hard' | 'adaptive',
    study_mode: 'mixed' as 'flashcard' | 'scenario' | 'ai_chat' | 'mixed',
    audio_enabled: true,
    animation_enabled: true,
    auto_play_audio: false,
    show_pronunciation: true,
    show_examples: true,
  })
  
  // 缓存
  const cache = reactive({
    statistics: null as { data: LearningStatistics, timestamp: number } | null,
    ttl: 10 * 60 * 1000, // 10分钟缓存
  })
  
  // 计算属性
  const todayProgress = computed(() => {
    if (!statistics.value) return 0
    const today = new Date().toISOString().split('T')[0]
    const todayData = statistics.value.weekly_progress.find(p => p.date === today)
    return todayData?.expressions_learned || 0
  })
  
  const dailyGoalProgress = computed(() => {
    return Math.min((todayProgress.value / settings.daily_goal) * 100, 100)
  })
  
  const currentStreak = computed(() => {
    return statistics.value?.learning_streak || 0
  })
  
  const averagePerformance = computed(() => {
    if (!studySessions.value.length) return 0
    const total = studySessions.value.reduce((sum, session) => sum + session.performance_score, 0)
    return Math.round(total / studySessions.value.length)
  })
  
  const activeGoals = computed(() => {
    return learningGoals.value.filter(goal => goal.status === 'active')
  })
  
  const recentConversations = computed(() => {
    return aiConversations.value
      .sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime())
      .slice(0, 5)
  })
  
  // Actions
  const fetchStatistics = async (useCache = true) => {
    const now = Date.now()
    
    // 检查缓存
    if (useCache && cache.statistics && (now - cache.statistics.timestamp < cache.ttl)) {
      statistics.value = cache.statistics.data
      return
    }
    
    loading.statistics = true
    try {
      const response = await englishAPI.getLearningStatistics()
      statistics.value = response
      
      // 更新缓存
      cache.statistics = {
        data: response,
        timestamp: now,
      }
      
    } catch (error) {
      console.error('获取学习统计失败:', error)
      throw error
    } finally {
      loading.statistics = false
    }
  }
  
  const startStudySession = (type: StudySession['session_type'] = 'flashcard') => {
    const session: StudySession = {
      id: `session_${Date.now()}`,
      start_time: new Date().toISOString(),
      expressions_studied: 0,
      correct_answers: 0,
      total_answers: 0,
      session_type: type,
      performance_score: 0,
      notes: '',
    }
    
    currentSession.value = session
    studySessions.value.unshift(session)
    
    return session
  }
  
  const endStudySession = (notes = '') => {
    if (!currentSession.value) return null
    
    const session = currentSession.value
    session.end_time = new Date().toISOString()
    session.notes = notes
    
    // 计算性能分数
    if (session.total_answers > 0) {
      session.performance_score = Math.round((session.correct_answers / session.total_answers) * 100)
    }
    
    currentSession.value = null
    
    // 保存到后端（可选）
    // saveStudySession(session)
    
    return session
  }
  
  const updateSessionProgress = (correct: boolean, expressionId?: number) => {
    if (!currentSession.value) return
    
    currentSession.value.expressions_studied++
    currentSession.value.total_answers++
    
    if (correct) {
      currentSession.value.correct_answers++
    }
  }
  
  const startAIConversation = (context: AIConversation['context'] = 'general', expressionId?: number) => {
    const conversation: AIConversation = {
      id: `conv_${Date.now()}`,
      messages: [],
      context,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }
    
    if (expressionId && context === 'expression_help') {
      conversation.messages.push({
        id: `msg_${Date.now()}`,
        role: 'user',
        content: '请帮我详细解释这个表达式的用法和含义',
        timestamp: new Date().toISOString(),
        expression_id: expressionId,
      })
    }
    
    currentConversation.value = conversation
    aiConversations.value.unshift(conversation)
    
    return conversation
  }
  
  const sendAIMessage = async (content: string, expressionId?: number) => {
    if (!currentConversation.value) {
      startAIConversation('general')
    }
    
    const userMessage = {
      id: `msg_${Date.now()}`,
      role: 'user' as const,
      content,
      timestamp: new Date().toISOString(),
      expression_id: expressionId,
    }
    
    currentConversation.value!.messages.push(userMessage)
    currentConversation.value!.updated_at = new Date().toISOString()
    
    loading.ai_response = true
    try {
      const response = await englishAPI.sendAIMessage({
        message: content,
        context: currentConversation.value!.context,
        expression_id: expressionId,
        conversation_history: currentConversation.value!.messages.slice(-10), // 最近10条消息作为上下文
      })
      
      const aiMessage = {
        id: `msg_${Date.now() + 1}`,
        role: 'assistant' as const,
        content: response.message,
        timestamp: new Date().toISOString(),
      }
      
      currentConversation.value!.messages.push(aiMessage)
      currentConversation.value!.updated_at = new Date().toISOString()
      
      return aiMessage
      
    } catch (error) {
      console.error('AI对话失败:', error)
      throw error
    } finally {
      loading.ai_response = false
    }
  }
  
  const createLearningGoal = async (goalData: Omit<LearningGoal, 'id' | 'current_progress' | 'created_at'>) => {
    try {
      const response = await englishAPI.createLearningGoal(goalData)
      learningGoals.value.push(response)
      return response
    } catch (error) {
      console.error('创建学习目标失败:', error)
      throw error
    }
  }
  
  const updateLearningGoal = async (goalId: number, updates: Partial<LearningGoal>) => {
    try {
      const response = await englishAPI.updateLearningGoal(goalId, updates)
      
      const index = learningGoals.value.findIndex(g => g.id === goalId)
      if (index >= 0) {
        learningGoals.value[index] = { ...learningGoals.value[index], ...response }
      }
      
      return response
    } catch (error) {
      console.error('更新学习目标失败:', error)
      throw error
    }
  }
  
  const updateSettings = (newSettings: Partial<typeof settings>) => {
    Object.assign(settings, newSettings)
    
    // 保存到本地存储
    localStorage.setItem('learning_settings', JSON.stringify(settings))
  }
  
  const loadSettings = () => {
    const saved = localStorage.getItem('learning_settings')
    if (saved) {
      try {
        const parsedSettings = JSON.parse(saved)
        Object.assign(settings, parsedSettings)
      } catch (error) {
        console.error('加载学习设置失败:', error)
      }
    }
  }
  
  const clearAllData = () => {
    expressions.value = []
    userProgress.value = []
    learningSessions.value = []
    aiConversations.value = []
    currentExpression.value = null
    currentConversation.value = null
    currentSession.value = null
    statistics.value = null
    cache.statistics = null
    clearCache()
  }
  
  // 初始化
  const initialize = async () => {
    loadSettings()
    try {
      await Promise.all([
        fetchStatistics(),
        fetchUserProgress(),
      ])
    } catch (error) {
      console.error('学习数据初始化失败:', error)
    }
  }
  
  return {
    // 状态
    statistics,
    aiConversations,
    currentConversation,
    learningGoals,
    studySessions,
    currentSession,
    loading,
    settings,
    
    // 计算属性
    todayProgress,
    dailyGoalProgress,
    currentStreak,
    averagePerformance,
    activeGoals,
    recentConversations,
    
    // Actions
    fetchStatistics,
    startStudySession,
    endStudySession,
    updateSessionProgress,
    startAIConversation,
    sendAIMessage,
    createLearningGoal,
    updateLearningGoal,
    updateSettings,
    loadSettings,
    clearAllData,
    initialize,
  }
})
