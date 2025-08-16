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
  
  batchDeleteNews(newsIds) {
    return request.post('/english/news/batch_delete/', { news_ids: newsIds })
  },
  

  
  getNewsCategories() {
    return request.get('/english/news/categories/')
  },
  
  filterNewsByCategory(params) {
    return request.get('/english/news/filter_by_category/', { params })
  },

  // Learning Plans
  getLearningPlans(params = {}) {
    return request.get('/english/plans/', { params })
  },
  createLearningPlan(data) {
    return request.post('/english/plans/', data)
  },
  updateLearningPlan(id, data) {
    return request.put(`/english/plans/${id}/`, data)
  },
  deleteLearningPlan(id) {
    return request.delete(`/english/plans/${id}/`)
  },
  getDailyWords(planId) {
    return request.get(`/english/plans/${planId}/daily_words/`)
  },
  getDailyExpressions(planId) {
    return request.get(`/english/plans/${planId}/daily_expressions/`)
  },

  // Practice System
  getPracticeRecords(params = {}) {
    return request.get('/english/practice/', { params })
  },
  generateQuestions(type = 'word_spelling', count = 5) {
    return request.get(`/english/practice/generate_questions/?type=${type}&count=${count}`)
  },
  submitPractice(data) {
    return request.post('/english/practice/submit_practice/', data)
  },

  // Pronunciation
  getPronunciationRecords(params = {}) {
    return request.get('/english/pronunciation/', { params })
  },
  createPronunciationRecord(data) {
    return request.post('/english/pronunciation/', data)
  },

      // Learning Statistics
    getLearningStats(params = {}) {
        return request.get('/english/stats/', { params })
    },
    updateTodayStats() {
        return request.post('/english/stats/update_today/')
    },

    // Pronunciation Practice
    submitPronunciation(formData) {
        return request.post('/english/pronunciation/submit/', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        })
    },
    generateTTS(text, language = 'en-US') {
        return request.post('/english/tts/generate/', {
            text,
            language
        })
    },

    // External API Integration
    enrichWordDefinition(wordId) {
        return request.post(`/english/words/${wordId}/enrich_definition/`)
    },
    generateWordAudio(wordId) {
        return request.post(`/english/words/${wordId}/generate_audio/`)
    },
    
    // Dictionary API
    searchDictionary(word, source = 'auto') {
        return request.get('/english/dictionary/search/', {
            params: { word, source }
        })
    }
}


