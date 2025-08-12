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
  getNews(id) {
    return request.get(`/english/news/${id}/`)
  },
  triggerNewsCrawl(source = 'bbc') {
    return request.post('/english/news/crawl/', { source })
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
  }
}


