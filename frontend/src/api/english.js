import request from './request'

// 英语学习模块 API
export const englishAPI = {
  // Words
  getWords(params = {}) {
    return request.get('/english/words/', { params })
  },
  getWord(id) {
    return request.get(`/english/words/${id}/`)
  },
  createWord(data) {
    return request.post('/english/words/', data)
  },
  updateWord(id, data) {
    return request.put(`/english/words/${id}/`, data)
  },
  deleteWord(id) {
    return request.delete(`/english/words/${id}/`)
  },

  // User Word Progress
  getProgress(params = {}) {
    return request.get('/english/progress/', { params })
  },
  // 复习列表（到期）
  getDueReviews(params = {}) {
    return request.get('/english/progress/review/', { params })
  },
  // 复习打卡（detail 动作）
  reviewProgress(id, payload) {
    return request.post(`/english/progress/${id}/review/`, payload)
  },
  // 批量复习提交
  batchReview(data) {
    return request.post('/english/progress/batch_review/', data)
  },
  // 学习概览
  getLearningOverview(days = 7) {
    return request.get(`/english/progress/learning_overview/?days=${days}`)
  },

  // Expressions
  getExpressions(params = {}) {
    return request.get('/english/expressions/', { params })
  },
  getExpression(id) {
    return request.get(`/english/expressions/${id}/`)
  },
  createExpression(data) {
    return request.post('/english/expressions/', data)
  },
  updateExpression(id, data) {
    return request.put(`/english/expressions/${id}/`, data)
  },
  deleteExpression(id) {
    return request.delete(`/english/expressions/${id}/`)
  },

  // News
  getNewsList(params = {}) {
    return request.get('/english/news/', { params })
  },
  getNewsManagementList(params = {}) {
    return request.get('/english/news/management_list/', { params })
  },
  getNewsDetail(id) {
    return request.get(`/english/news/${id}/`)
  },
  getNews(id) {
    return request.get(`/english/news/${id}/`)
  },
  triggerNewsCrawl(settings = {}) {
    // 支持新的爬取设置格式
    const { maxArticles = 3, timeout = 30, sources = [], autoCrawl = false } = settings
    
    // 如果没有选择新闻源，使用默认的BBC
    const finalSources = sources.length > 0 ? sources : ['uk.BBC']
    
    const payload = {
      sources: finalSources,
      max_articles: maxArticles,
      timeout,
      auto_crawl: autoCrawl
    }
    
    console.log('发送爬取请求:', payload)
    // 抓取可能耗时较长，提高超时时间到120秒
    return request.post('/english/news/crawl/', payload, { timeout: 120000 })
  },
  
  // 新闻管理API
  getFundusPublishers() {
    return request.get('/english/news/fundus_publishers/')
  },
  deleteNews(id) {
    return request.delete(`/english/news/${id}/delete_news/`)
  },
  
  // 词库和章节API
  getDictionaries() {
    return request.get('/english/dictionaries/')
  },
  getChapters(dictionaryId) {
    return request.get(`/english/dictionaries/${dictionaryId}/chapters/`)
  },
  getWordsForPractice(params = {}) {
    return request.get('/english/typing-practice/words/', { params })
  },
  getTypingWordsByDictionary(params = {}) {
    return request.get('/english/typing-practice/words/', { 
      params: { 
        category: params.category, 
        chapter: params.chapter
      } 
    })
  },
  // 打字练习相关API
  getTypingWords(params = {}) {
    return request.get('/english/typing-practice/words/', { params })
  },
  getTypingStats() {
    return request.get('/english/typing-practice/statistics/')
  },
  getTypingDailyProgress(params = {}) {
    return request.get('/english/typing-practice/daily-progress/', { params })
  },
      submitTypingPractice(data) {
      return request.post('/english/typing-practice/submit/', data)
    },
    completeTypingSession() {
      return request.post('/english/typing-practice/complete_session/')
    },
  submitTypingResult(data) {
    return request.post('/english/typing-practice/submit/', data)
  },
  getTypingStatistics() {
    return request.get('/english/typing-practice/statistics/')
  },
  getDailyProgress(params = {}) {
    return request.get('/english/typing-practice/daily-progress/', { params })
  },

  // 数据分析API
  getDataOverview(params = {}) {
    return request.get('/english/data-analysis/overview/', { params })
  },
  getExerciseHeatmap(params = {}) {
    return request.get('/english/data-analysis/exercise_heatmap/', { params })
  },
  getWordHeatmap(params = {}) {
    return request.get('/english/data-analysis/word_heatmap/', { params })
  },
  getWpmTrend(params = {}) {
    return request.get('/english/data-analysis/wpm_trend/', { params })
  },
  getAccuracyTrend(params = {}) {
    return request.get('/english/data-analysis/accuracy_trend/', { params })
  },
  getKeyErrorStats() {
    return request.get('/english/data-analysis/key_error_stats/')
  }
}

// 数据分析专用API对象
export const dataAnalysisAPI = {
  getOverview(params = {}) {
    return request.get('/english/data-analysis/overview/', { params })
  },
  getExerciseHeatmap(params = {}) {
    return request.get('/english/data-analysis/exercise_heatmap/', { params })
  },
  getWordHeatmap(params = {}) {
    return request.get('/english/data-analysis/word_heatmap/', { params })
  },
  getWpmTrend(params = {}) {
    return request.get('/english/data-analysis/wpm_trend/', { params })
  },
  getAccuracyTrend(params = {}) {
    return request.get('/english/data-analysis/accuracy_trend/', { params })
  },
  getKeyErrorStats() {
    return request.get('/english/data-analysis/key_error_stats/')
  },
  // 新增：获取月历热力图数据
  getMonthlyCalendar(params = {}) {
    return request.get('/english/data-analysis/monthly-calendar/', { params })
  }
}


