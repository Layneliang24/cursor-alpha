/**
 * 地道表达专用状态管理
 * 基于Pinia，支持TypeScript类型安全
 */
import { defineStore } from 'pinia'
import { ref, computed, reactive } from 'vue'
import { englishAPI } from '@/api/english'

// 类型定义
export interface IdiomaticExpression {
  id: number
  expression: string
  meaning: string
  explanation: string
  pronunciation: string
  difficulty_level: 'beginner' | 'intermediate' | 'advanced'
  formality_level: 'informal' | 'neutral' | 'formal'
  usage_frequency: 'low' | 'medium' | 'high'
  usage_examples: Array<{
    example: string
    translation: string
    context: string
  }>
  scenarios: Array<{
    id: number
    scenario_name: string
    description: string
  }>
  sources: Array<{
    id: number
    source_name: string
    source_type: string
  }>
  created_at: string
  updated_at: string
}

export interface UserExpressionProgress {
  id: number
  expression_id: number
  user_id: number
  mastery_level: number
  review_count: number
  correct_count: number
  last_reviewed: string
  next_review: string
  is_favorite: boolean
  notes: string
}

export interface LearningSession {
  id: number
  user_id: number
  session_type: 'review' | 'practice' | 'test'
  expressions_count: number
  correct_count: number
  session_duration: number
  started_at: string
  completed_at: string
  performance_score: number
}

export interface ExpressionFilters {
  search: string
  difficulty: string
  formality: string
  frequency: string
  scenario: string
  source: string
  mastery_level: string
  is_favorite: boolean | null
  ordering: string
}

export interface PaginationInfo {
  page: number
  pageSize: number
  total: number
  totalPages: number
}

// Store定义
export const useExpressionStore = defineStore('expression', () => {
  // 状态
  const expressions = ref<IdiomaticExpression[]>([])
  const userProgress = ref<UserExpressionProgress[]>([])
  const learningSessions = ref<LearningSession[]>([])
  const currentExpression = ref<IdiomaticExpression | null>(null)
  
  // 加载状态
  const loading = reactive({
    expressions: false,
    progress: false,
    sessions: false,
    details: false
  })
  
  // 筛选和分页
  const filters = reactive<ExpressionFilters>({
    search: '',
    difficulty: '',
    formality: '',
    frequency: '',
    scenario: '',
    source: '',
    mastery_level: '',
    is_favorite: null,
    ordering: '-updated_at'
  })
  
  const pagination = reactive<PaginationInfo>({
    page: 1,
    pageSize: 20,
    total: 0,
    totalPages: 0
  })
  
  // 缓存状态
  const cache = reactive({
    expressions: new Map<string, { data: IdiomaticExpression[], timestamp: number }>(),
    progress: new Map<string, { data: UserExpressionProgress[], timestamp: number }>(),
    lastFetch: 0,
    ttl: 5 * 60 * 1000 // 5分钟缓存
  })
  
  // 计算属性
  const filteredExpressions = computed(() => {
    if (!expressions.value.length) return []
    
    return expressions.value.filter(expr => {
      if (filters.search && !expr.expression.toLowerCase().includes(filters.search.toLowerCase()) &&
          !expr.meaning.toLowerCase().includes(filters.search.toLowerCase())) {
        return false
      }
      if (filters.difficulty && expr.difficulty_level !== filters.difficulty) return false
      if (filters.formality && expr.formality_level !== filters.formality) return false
      if (filters.frequency && expr.usage_frequency !== filters.frequency) return false
      
      return true
    })
  })
  
  const favoriteExpressions = computed(() => {
    return expressions.value.filter(expr => {
      const progress = userProgress.value.find(p => p.expression_id === expr.id)
      return progress?.is_favorite
    })
  })
  
  const needReviewExpressions = computed(() => {
    const now = new Date()
    return expressions.value.filter(expr => {
      const progress = userProgress.value.find(p => p.expression_id === expr.id)
      return progress && new Date(progress.next_review) <= now
    })
  })
  
  const masteryStats = computed(() => {
    const stats = { beginner: 0, intermediate: 0, advanced: 0, mastered: 0 }
    userProgress.value.forEach(progress => {
      if (progress.mastery_level >= 80) stats.mastered++
      else if (progress.mastery_level >= 60) stats.advanced++
      else if (progress.mastery_level >= 40) stats.intermediate++
      else stats.beginner++
    })
    return stats
  })
  
  // Actions
  const fetchExpressions = async (useCache = true) => {
    const cacheKey = JSON.stringify({ filters, page: pagination.page })
    const now = Date.now()
    
    // 检查缓存
    if (useCache && cache.expressions.has(cacheKey)) {
      const cached = cache.expressions.get(cacheKey)!
      if (now - cached.timestamp < cache.ttl) {
        expressions.value = cached.data
        return
      }
    }
    
    loading.expressions = true
    try {
      const params = {
        page: pagination.page,
        page_size: pagination.pageSize,
        search: filters.search || undefined,
        difficulty_level: filters.difficulty || undefined,
        formality_level: filters.formality || undefined,
        usage_frequency: filters.frequency || undefined,
        ordering: filters.ordering
      }
      
      const response = await englishAPI.getIdiomaticExpressions(params)
      
      expressions.value = response.results || []
      pagination.total = response.count || 0
      pagination.totalPages = Math.ceil(pagination.total / pagination.pageSize)
      
      // 更新缓存
      cache.expressions.set(cacheKey, {
        data: expressions.value,
        timestamp: now
      })
      
    } catch (error) {
      console.error('获取地道表达失败:', error)
      throw error
    } finally {
      loading.expressions = false
    }
  }
  
  const fetchUserProgress = async (useCache = true) => {
    const cacheKey = `user_progress_${pagination.page}`
    const now = Date.now()
    
    if (useCache && cache.progress.has(cacheKey)) {
      const cached = cache.progress.get(cacheKey)!
      if (now - cached.timestamp < cache.ttl) {
        userProgress.value = cached.data
        return
      }
    }
    
    loading.progress = true
    try {
      const response = await englishAPI.getUserExpressionProgress({
        page: pagination.page,
        page_size: pagination.pageSize
      })
      
      userProgress.value = response.results || []
      
      cache.progress.set(cacheKey, {
        data: userProgress.value,
        timestamp: now
      })
      
    } catch (error) {
      console.error('获取用户进度失败:', error)
      throw error
    } finally {
      loading.progress = false
    }
  }
  
  const fetchExpressionDetail = async (id: number) => {
    loading.details = true
    try {
      const response = await englishAPI.getIdiomaticExpression(id)
      currentExpression.value = response
      return response
    } catch (error) {
      console.error('获取表达详情失败:', error)
      throw error
    } finally {
      loading.details = false
    }
  }
  
  const updateExpressionProgress = async (expressionId: number, data: Partial<UserExpressionProgress>) => {
    try {
      const response = await englishAPI.updateExpressionProgress(expressionId, data)
      
      // 更新本地状态
      const index = userProgress.value.findIndex(p => p.expression_id === expressionId)
      if (index >= 0) {
        userProgress.value[index] = { ...userProgress.value[index], ...response }
      } else {
        userProgress.value.push(response)
      }
      
      // 清除相关缓存
      cache.progress.clear()
      
      return response
    } catch (error) {
      console.error('更新学习进度失败:', error)
      throw error
    }
  }
  
  const markAsFavorite = async (expressionId: number, isFavorite: boolean) => {
    return updateExpressionProgress(expressionId, { is_favorite: isFavorite })
  }
  
  const updateMasteryLevel = async (expressionId: number, masteryLevel: number) => {
    return updateExpressionProgress(expressionId, { mastery_level: masteryLevel })
  }
  
  const createLearningSession = async (sessionData: Partial<LearningSession>) => {
    loading.sessions = true
    try {
      const response = await englishAPI.createLearningSession(sessionData)
      learningSessions.value.unshift(response)
      return response
    } catch (error) {
      console.error('创建学习会话失败:', error)
      throw error
    } finally {
      loading.sessions = false
    }
  }
  
  const searchExpressions = async (searchTerm: string) => {
    filters.search = searchTerm
    pagination.page = 1
    await fetchExpressions(false) // 搜索时不使用缓存
  }
  
  const applyFilters = async (newFilters: Partial<ExpressionFilters>) => {
    Object.assign(filters, newFilters)
    pagination.page = 1
    await fetchExpressions(false)
  }
  
  const changePage = async (page: number) => {
    pagination.page = page
    await fetchExpressions()
  }
  
  const clearCache = () => {
    cache.expressions.clear()
    cache.progress.clear()
    cache.lastFetch = 0
  }
  
  const resetFilters = () => {
    Object.assign(filters, {
      search: '',
      difficulty: '',
      formality: '',
      frequency: '',
      scenario: '',
      source: '',
      mastery_level: '',
      is_favorite: null,
      ordering: '-updated_at'
    })
    pagination.page = 1
  }
  
  return {
    // 状态
    expressions,
    userProgress,
    learningSessions,
    currentExpression,
    loading,
    filters,
    pagination,
    
    // 计算属性
    filteredExpressions,
    favoriteExpressions,
    needReviewExpressions,
    masteryStats,
    
    // Actions
    fetchExpressions,
    fetchUserProgress,
    fetchExpressionDetail,
    updateExpressionProgress,
    markAsFavorite,
    updateMasteryLevel,
    createLearningSession,
    searchExpressions,
    applyFilters,
    changePage,
    clearCache,
    resetFilters
  }
})
