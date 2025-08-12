import { defineStore } from 'pinia'
import { englishAPI } from '@/api/english'

export const useEnglishStore = defineStore('english', {
  state: () => ({
    // words
    words: [],
    wordsLoading: false,
    wordsPagination: { page: 1, pageSize: 10, total: 0 },
    wordsQuery: { search: '', difficulty: '', ordering: '-updated_at' },

    // expressions
    expressions: [],
    expressionsLoading: false,
    expressionsPagination: { page: 1, pageSize: 10, total: 0 },
    expressionsQuery: { search: '', ordering: '-updated_at' },

    // news
    newsList: [],
    newsLoading: false,
    newsPagination: { page: 1, pageSize: 10, total: 0 },
    newsQuery: { search: '', category: '', ordering: '-published_at' },

    // learning progress
    userProgress: [],
    progressLoading: false,
    dueReviews: [],
    reviewsLoading: false,
    learningOverview: null,
    overviewLoading: false,

    // learning plans
    learningPlans: [],
    plansLoading: false,
    currentPlan: null,
    dailyWords: [],
    dailyExpressions: [],

    // practice system
    practiceRecords: [],
    practiceLoading: false,
    currentQuestions: [],
    questionsLoading: false,
    practiceStats: {
      totalPractices: 0,
      correctRate: 0,
      averageTime: 0
    },

    // learning statistics
    learningStats: [],
    statsLoading: false,
    todayStats: null
  }),

  actions: {
    async fetchWords(params = {}) {
      this.wordsLoading = true
      try {
        const queryRaw = { ...this.wordsQuery, ...params }
        const query = {
          page: this.wordsPagination.page,
          page_size: this.wordsPagination.pageSize,
          // 前端 -> 后端参数名映射
          q: queryRaw.search,
          difficulty_level: queryRaw.difficulty,
          ordering: queryRaw.ordering
        }
        const resp = await englishAPI.getWords(query)
        // 兼容后端统一响应结构或直接返回DRF分页
        const data = resp?.data || resp?.results || resp?.items || []
        const total = resp?.pagination?.total || resp?.count || 0
        this.words = data
        this.wordsPagination.total = total
      } finally {
        this.wordsLoading = false
      }
    },

    async fetchExpressions(params = {}) {
      this.expressionsLoading = true
      try {
        const queryRaw = { ...this.expressionsQuery, ...params }
        const query = {
          page: this.expressionsPagination.page,
          page_size: this.expressionsPagination.pageSize,
          q: queryRaw.search,
          ordering: queryRaw.ordering
        }
        const resp = await englishAPI.getExpressions(query)
        const data = resp?.data || resp?.results || resp?.items || []
        const total = resp?.pagination?.total || resp?.count || 0
        this.expressions = data
        this.expressionsPagination.total = total
      } finally {
        this.expressionsLoading = false
      }
    },

    async fetchNews(params = {}) {
      this.newsLoading = true
      try {
        const queryRaw = { ...this.newsQuery, ...params }
        const query = {
          page: this.newsPagination.page,
          page_size: this.newsPagination.pageSize,
          q: queryRaw.search,
          category: queryRaw.category,
          ordering: queryRaw.ordering
        }
        const resp = await englishAPI.getNewsList(query)
        const data = resp?.data || resp?.results || resp?.items || []
        const total = resp?.pagination?.total || resp?.count || 0
        this.newsList = data
        this.newsPagination.total = total
      } finally {
        this.newsLoading = false
      }
    },

    // Learning Progress Actions
    async fetchUserProgress(params = {}) {
      this.progressLoading = true
      try {
        const resp = await englishAPI.getProgress(params)
        const data = resp?.data || resp?.results || []
        this.userProgress = data
      } finally {
        this.progressLoading = false
      }
    },

    async fetchDueReviews() {
      this.reviewsLoading = true
      try {
        const resp = await englishAPI.getDueReviews()
        const data = resp?.data || resp?.results || []
        this.dueReviews = data
      } finally {
        this.reviewsLoading = false
      }
    },

    async submitBatchReview(reviewData) {
      try {
        const resp = await englishAPI.batchReview(reviewData)
        // 更新本地状态
        await this.fetchDueReviews()
        await this.fetchLearningOverview()
        return resp
      } catch (error) {
        throw error
      }
    },

    async fetchLearningOverview(days = 7) {
      this.overviewLoading = true
      try {
        const resp = await englishAPI.getLearningOverview(days)
        this.learningOverview = resp?.data || resp
      } finally {
        this.overviewLoading = false
      }
    },

    // Learning Plans Actions
    async fetchLearningPlans() {
      this.plansLoading = true
      try {
        const resp = await englishAPI.getLearningPlans()
        const data = resp?.data || resp?.results || []
        this.learningPlans = data
        // 设置当前活跃计划
        this.currentPlan = data.find(plan => plan.is_active) || data[0] || null
      } finally {
        this.plansLoading = false
      }
    },

    async createLearningPlan(planData) {
      try {
        const resp = await englishAPI.createLearningPlan(planData)
        await this.fetchLearningPlans()
        return resp
      } catch (error) {
        throw error
      }
    },

    async fetchDailyContent(planId) {
      try {
        const [wordsResp, expressionsResp] = await Promise.all([
          englishAPI.getDailyWords(planId),
          englishAPI.getDailyExpressions(planId)
        ])
        this.dailyWords = wordsResp?.data || wordsResp?.results || []
        this.dailyExpressions = expressionsResp?.data || expressionsResp?.results || []
      } catch (error) {
        console.error('获取每日学习内容失败:', error)
      }
    },

    // Practice System Actions
    async fetchPracticeRecords(params = {}) {
      this.practiceLoading = true
      try {
        const resp = await englishAPI.getPracticeRecords(params)
        const data = resp?.data || resp?.results || []
        this.practiceRecords = data
        
        // 计算练习统计
        if (data.length > 0) {
          this.practiceStats.totalPractices = data.length
          this.practiceStats.correctRate = (data.filter(r => r.is_correct).length / data.length * 100).toFixed(1)
          this.practiceStats.averageTime = (data.reduce((sum, r) => sum + r.time_spent, 0) / data.length).toFixed(1)
        }
      } finally {
        this.practiceLoading = false
      }
    },

    async generatePracticeQuestions(type = 'word_spelling', count = 5) {
      this.questionsLoading = true
      try {
        const resp = await englishAPI.generateQuestions(type, count)
        this.currentQuestions = resp?.data || resp?.results || []
        return this.currentQuestions
      } finally {
        this.questionsLoading = false
      }
    },

    async submitPracticeAnswer(answerData) {
      try {
        const resp = await englishAPI.submitPractice(answerData)
        // 更新练习记录
        await this.fetchPracticeRecords({ page: 1, page_size: 10 })
        return resp
      } catch (error) {
        throw error
      }
    },

    // Learning Statistics Actions
    async fetchLearningStats(params = {}) {
      this.statsLoading = true
      try {
        const resp = await englishAPI.getLearningStats(params)
        const data = resp?.data || resp?.results || []
        this.learningStats = data
        this.todayStats = data.find(stat => {
          const today = new Date().toISOString().split('T')[0]
          return stat.date === today
        }) || null
      } finally {
        this.statsLoading = false
      }
    },

    async updateTodayStats() {
      try {
        const resp = await englishAPI.updateTodayStats()
        await this.fetchLearningStats({ page: 1, page_size: 30 })
        return resp
      } catch (error) {
        throw error
      }
    },

    // Utility Actions
    async triggerNewsCrawl(source = 'bbc') {
      try {
        const resp = await englishAPI.triggerNewsCrawl(source)
        // 可以显示通知
        return resp
      } catch (error) {
        throw error
      }
    },

    // Reset state
    resetState() {
      this.words = []
      this.expressions = []
      this.newsList = []
      this.userProgress = []
      this.dueReviews = []
      this.learningPlans = []
      this.practiceRecords = []
      this.currentQuestions = []
      this.learningOverview = null
      this.todayStats = null
    }
  },

  getters: {
    // 获取需要复习的单词数量
    dueReviewsCount: (state) => state.dueReviews.length,
    
    // 获取今日学习进度
    todayProgress: (state) => {
      if (!state.todayStats) return null
      return {
        wordsLearned: state.todayStats.words_learned,
        wordsReviewed: state.todayStats.words_reviewed,
        practiceCount: state.todayStats.practice_count,
        accuracyRate: state.todayStats.accuracy_rate,
        studyTime: state.todayStats.study_time_minutes
      }
    },
    
    // 获取当前活跃的学习计划
    activePlan: (state) => state.currentPlan,
    
    // 获取练习统计
    practiceStatistics: (state) => state.practiceStats
  }
})


