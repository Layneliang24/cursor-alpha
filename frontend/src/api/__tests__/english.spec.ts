import { describe, it, expect, vi, beforeEach } from 'vitest'
import { englishAPI, dataAnalysisAPI } from '../english'

// Mock request module
vi.mock('../request', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn()
  }
}))

describe('englishAPI', () => {
  let mockRequest: any

  beforeEach(async () => {
    const requestModule = await import('../request')
    mockRequest = requestModule.default
    mockRequest.get.mockClear()
    mockRequest.post.mockClear()
    mockRequest.put.mockClear()
    mockRequest.delete.mockClear()
  })

  describe('Words API', () => {
    it('应该获取单词列表', async () => {
      const mockResponse = [
        { id: 1, word: 'hello', translation: '你好' },
        { id: 2, word: 'world', translation: '世界' }
      ]
      mockRequest.get.mockResolvedValue(mockResponse)

      const result = await englishAPI.getWords({ page: 1, size: 10 })
      
      expect(mockRequest.get).toHaveBeenCalledWith('/english/words/', { params: { page: 1, size: 10 } })
      expect(result).toEqual(mockResponse)
    })

    it('应该获取单个单词', async () => {
      const mockResponse = { id: 1, word: 'hello', translation: '你好' }
      mockRequest.get.mockResolvedValue(mockResponse)

      const result = await englishAPI.getWord(1)
      
      expect(mockRequest.get).toHaveBeenCalledWith('/english/words/1/')
      expect(result).toEqual(mockResponse)
    })

    it('应该创建单词', async () => {
      const wordData = { word: 'hello', translation: '你好' }
      const mockResponse = { id: 1, ...wordData }
      mockRequest.post.mockResolvedValue(mockResponse)

      const result = await englishAPI.createWord(wordData)
      
      expect(mockRequest.post).toHaveBeenCalledWith('/english/words/', wordData)
      expect(result).toEqual(mockResponse)
    })

    it('应该更新单词', async () => {
      const wordData = { translation: '你好世界' }
      const mockResponse = { id: 1, word: 'hello', translation: '你好世界' }
      mockRequest.put.mockResolvedValue(mockResponse)

      const result = await englishAPI.updateWord(1, wordData)
      
      expect(mockRequest.put).toHaveBeenCalledWith('/english/words/1/', wordData)
      expect(result).toEqual(mockResponse)
    })

    it('应该删除单词', async () => {
      mockRequest.delete.mockResolvedValue({ success: true })

      const result = await englishAPI.deleteWord(1)
      
      expect(mockRequest.delete).toHaveBeenCalledWith('/english/words/1/')
      expect(result).toEqual({ success: true })
    })
  })

  describe('User Word Progress API', () => {
    it('应该获取学习进度', async () => {
      const mockResponse = [
        { id: 1, word: 'hello', status: 'learning', next_review: '2024-01-01' }
      ]
      mockRequest.get.mockResolvedValue(mockResponse)

      const result = await englishAPI.getProgress({ status: 'learning' })
      
      expect(mockRequest.get).toHaveBeenCalledWith('/english/progress/', { params: { status: 'learning' } })
      expect(result).toEqual(mockResponse)
    })

    it('应该获取到期复习列表', async () => {
      const mockResponse = [
        { id: 1, word: 'hello', due_date: '2024-01-01' }
      ]
      mockRequest.get.mockResolvedValue(mockResponse)

      const result = await englishAPI.getDueReviews({ limit: 10 })
      
      expect(mockRequest.get).toHaveBeenCalledWith('/english/progress/review/', { params: { limit: 10 } })
      expect(result).toEqual(mockResponse)
    })

    it('应该提交复习进度', async () => {
      const payload = { difficulty: 'easy', time_spent: 30 }
      const mockResponse = { success: true, next_review: '2024-01-02' }
      mockRequest.post.mockResolvedValue(mockResponse)

      const result = await englishAPI.reviewProgress(1, payload)
      
      expect(mockRequest.post).toHaveBeenCalledWith('/english/progress/1/review/', payload)
      expect(result).toEqual(mockResponse)
    })

    it('应该批量提交复习', async () => {
      const data = [
        { id: 1, difficulty: 'easy' },
        { id: 2, difficulty: 'hard' }
      ]
      const mockResponse = { success: true, updated_count: 2 }
      mockRequest.post.mockResolvedValue(mockResponse)

      const result = await englishAPI.batchReview(data)
      
      expect(mockRequest.post).toHaveBeenCalledWith('/english/progress/batch_review/', data)
      expect(result).toEqual(mockResponse)
    })

    it('应该获取学习概览', async () => {
      const mockResponse = { total_words: 100, learned_words: 50, review_words: 20 }
      mockRequest.get.mockResolvedValue(mockResponse)

      const result = await englishAPI.getLearningOverview(7)
      
      expect(mockRequest.get).toHaveBeenCalledWith('/english/progress/learning_overview/?days=7')
      expect(result).toEqual(mockResponse)
    })
  })

  describe('Expressions API', () => {
    it('应该获取表达列表', async () => {
      const mockResponse = [
        { id: 1, expression: 'How are you?', translation: '你好吗？' }
      ]
      mockRequest.get.mockResolvedValue(mockResponse)

      const result = await englishAPI.getExpressions({ category: 'greeting' })
      
      expect(mockRequest.get).toHaveBeenCalledWith('/english/expressions/', { params: { category: 'greeting' } })
      expect(result).toEqual(mockResponse)
    })

    it('应该获取单个表达', async () => {
      const mockResponse = { id: 1, expression: 'How are you?', translation: '你好吗？' }
      mockRequest.get.mockResolvedValue(mockResponse)

      const result = await englishAPI.getExpression(1)
      
      expect(mockRequest.get).toHaveBeenCalledWith('/english/expressions/1/')
      expect(result).toEqual(mockResponse)
    })

    it('应该创建表达', async () => {
      const expressionData = { expression: 'How are you?', translation: '你好吗？' }
      const mockResponse = { id: 1, ...expressionData }
      mockRequest.post.mockResolvedValue(mockResponse)

      const result = await englishAPI.createExpression(expressionData)
      
      expect(mockRequest.post).toHaveBeenCalledWith('/english/expressions/', expressionData)
      expect(result).toEqual(mockResponse)
    })

    it('应该更新表达', async () => {
      const expressionData = { translation: '你好吗？最近怎么样？' }
      const mockResponse = { id: 1, expression: 'How are you?', translation: '你好吗？最近怎么样？' }
      mockRequest.put.mockResolvedValue(mockResponse)

      const result = await englishAPI.updateExpression(1, expressionData)
      
      expect(mockRequest.put).toHaveBeenCalledWith('/english/expressions/1/', expressionData)
      expect(result).toEqual(mockResponse)
    })

    it('应该删除表达', async () => {
      mockRequest.delete.mockResolvedValue({ success: true })

      const result = await englishAPI.deleteExpression(1)
      
      expect(mockRequest.delete).toHaveBeenCalledWith('/english/expressions/1/')
      expect(result).toEqual({ success: true })
    })
  })

  describe('News API', () => {
    it('应该获取新闻列表', async () => {
      const mockResponse = [
        { id: 1, title: 'Breaking News', source: 'BBC' }
      ]
      mockRequest.get.mockResolvedValue(mockResponse)

      const result = await englishAPI.getNewsList({ source: 'BBC' })
      
      expect(mockRequest.get).toHaveBeenCalledWith('/english/news/', { params: { source: 'BBC' } })
      expect(result).toEqual(mockResponse)
    })

    it('应该获取新闻管理列表', async () => {
      const mockResponse = [
        { id: 1, title: 'Breaking News', status: 'published' }
      ]
      mockRequest.get.mockResolvedValue(mockResponse)

      const result = await englishAPI.getNewsManagementList({ status: 'published' })
      
      expect(mockRequest.get).toHaveBeenCalledWith('/english/news/management_list/', { params: { status: 'published' } })
      expect(result).toEqual(mockResponse)
    })

    it('应该获取新闻详情', async () => {
      const mockResponse = { id: 1, title: 'Breaking News', content: 'News content...' }
      mockRequest.get.mockResolvedValue(mockResponse)

      const result = await englishAPI.getNewsDetail(1)
      
      expect(mockRequest.get).toHaveBeenCalledWith('/english/news/1/')
      expect(result).toEqual(mockResponse)
    })

    it('应该获取新闻', async () => {
      const mockResponse = { id: 1, title: 'Breaking News', content: 'News content...' }
      mockRequest.get.mockResolvedValue(mockResponse)

      const result = await englishAPI.getNews(1)
      
      expect(mockRequest.get).toHaveBeenCalledWith('/english/news/1/')
      expect(result).toEqual(mockResponse)
    })

    it('应该触发新闻爬取', async () => {
      const settings = { maxArticles: 5, timeout: 60, sources: ['BBC'], autoCrawl: true }
      const mockResponse = { success: true, task_id: 'task_123' }
      mockRequest.post.mockResolvedValue(mockResponse)

      const result = await englishAPI.triggerNewsCrawl(settings)
      
      expect(mockRequest.post).toHaveBeenCalledWith('/english/news/crawl/', {
        sources: ['BBC'],
        max_articles: 5,
        timeout: 60,
        auto_crawl: true
      }, { timeout: 120000 })
      expect(result).toEqual(mockResponse)
    })

    it('应该使用默认设置触发新闻爬取', async () => {
      const mockResponse = { success: true, task_id: 'task_123' }
      mockRequest.post.mockResolvedValue(mockResponse)

      const result = await englishAPI.triggerNewsCrawl()
      
      expect(mockRequest.post).toHaveBeenCalledWith('/english/news/crawl/', {
        sources: ['uk.BBC'],
        max_articles: 3,
        timeout: 30,
        auto_crawl: false
      }, { timeout: 120000 })
      expect(result).toEqual(mockResponse)
    })

    it('应该获取新闻发布者', async () => {
      const mockResponse = ['BBC', 'CNN', 'Reuters']
      mockRequest.get.mockResolvedValue(mockResponse)

      const result = await englishAPI.getFundusPublishers()
      
      expect(mockRequest.get).toHaveBeenCalledWith('/english/news/fundus_publishers/')
      expect(result).toEqual(mockResponse)
    })

    it('应该删除新闻', async () => {
      mockRequest.delete.mockResolvedValue({ success: true })

      const result = await englishAPI.deleteNews(1)
      
      expect(mockRequest.delete).toHaveBeenCalledWith('/english/news/1/delete_news/')
      expect(result).toEqual({ success: true })
    })
  })

  describe('Dictionary and Chapter API', () => {
    it('应该获取词典列表', async () => {
      const mockResponse = [
        { id: 1, name: 'Oxford 3000', description: 'Core vocabulary' }
      ]
      mockRequest.get.mockResolvedValue(mockResponse)

      const result = await englishAPI.getDictionaries()
      
      expect(mockRequest.get).toHaveBeenCalledWith('/english/dictionaries/')
      expect(result).toEqual(mockResponse)
    })

    it('应该获取章节列表', async () => {
      const mockResponse = [
        { id: 1, name: 'Chapter 1', word_count: 100 }
      ]
      mockRequest.get.mockResolvedValue(mockResponse)

      const result = await englishAPI.getChapters(1)
      
      expect(mockRequest.get).toHaveBeenCalledWith('/english/dictionaries/1/chapters/')
      expect(result).toEqual(mockResponse)
    })

    it('应该获取章节单词数量', async () => {
      const mockResponse = { chapter_1: 100, chapter_2: 150 }
      mockRequest.get.mockResolvedValue(mockResponse)

      const result = await englishAPI.getChapterWordCounts(1)
      
      expect(mockRequest.get).toHaveBeenCalledWith('/english/dictionaries/chapter_word_counts/', { 
        params: { dictionary_id: 1 } 
      })
      expect(result).toEqual(mockResponse)
    })
  })

  describe('Typing Practice API', () => {
    it('应该获取练习单词', async () => {
      const mockResponse = [
        { id: 1, word: 'hello', difficulty: 'easy' }
      ]
      mockRequest.get.mockResolvedValue(mockResponse)

      const result = await englishAPI.getWordsForPractice({ difficulty: 'easy' })
      
      expect(mockRequest.get).toHaveBeenCalledWith('/english/typing-practice/words/', { params: { difficulty: 'easy' } })
      expect(result).toEqual(mockResponse)
    })

    it('应该根据词典获取打字单词', async () => {
      const mockResponse = [
        { id: 1, word: 'hello', chapter: 1 }
      ]
      mockRequest.get.mockResolvedValue(mockResponse)

      const result = await englishAPI.getTypingWordsByDictionary({ dictionary_id: 1, chapter: 1 })
      
      expect(mockRequest.get).toHaveBeenCalledWith('/english/typing-words/by_dictionary/', { 
        params: { dictionary_id: 1, chapter: 1 } 
      })
      expect(result).toEqual(mockResponse)
    })

    it('应该获取打字统计', async () => {
      const mockResponse = { total_words: 1000, accuracy: 95.5, wpm: 60 }
      mockRequest.get.mockResolvedValue(mockResponse)

      const result = await englishAPI.getTypingStats()
      
      expect(mockRequest.get).toHaveBeenCalledWith('/english/typing-practice/statistics/')
      expect(result).toEqual(mockResponse)
    })

    it('应该获取每日进度', async () => {
      const mockResponse = [
        { date: '2024-01-01', words_typed: 100, accuracy: 95 }
      ]
      mockRequest.get.mockResolvedValue(mockResponse)

      const result = await englishAPI.getTypingDailyProgress({ month: '2024-01' })
      
      expect(mockRequest.get).toHaveBeenCalledWith('/english/typing-practice/daily-progress/', { params: { month: '2024-01' } })
      expect(result).toEqual(mockResponse)
    })

    it('应该提交打字练习', async () => {
      const data = { word_id: 1, time_spent: 30, accuracy: 100 }
      const mockResponse = { success: true, score: 100 }
      mockRequest.post.mockResolvedValue(mockResponse)

      const result = await englishAPI.submitTypingPractice(data)
      
      expect(mockRequest.post).toHaveBeenCalledWith('/english/typing-practice/submit/', data)
      expect(result).toEqual(mockResponse)
    })

    it('应该完成打字会话', async () => {
      const mockResponse = { success: true, session_score: 850 }
      mockRequest.post.mockResolvedValue(mockResponse)

      const result = await englishAPI.completeTypingSession()
      
      expect(mockRequest.post).toHaveBeenCalledWith('/english/typing-practice/complete_session/')
      expect(result).toEqual(mockResponse)
    })

    it('应该提交打字结果', async () => {
      const data = { word_id: 1, time_spent: 30, accuracy: 100 }
      const mockResponse = { success: true, score: 100 }
      mockRequest.post.mockResolvedValue(mockResponse)

      const result = await englishAPI.submitTypingResult(data)
      
      expect(mockRequest.post).toHaveBeenCalledWith('/english/typing-practice/submit/', data)
      expect(result).toEqual(mockResponse)
    })

    it('应该获取打字统计信息', async () => {
      const mockResponse = { total_words: 1000, accuracy: 95.5, wpm: 60 }
      mockRequest.get.mockResolvedValue(mockResponse)

      const result = await englishAPI.getTypingStatistics()
      
      expect(mockRequest.get).toHaveBeenCalledWith('/english/typing-practice/statistics/')
      expect(result).toEqual(mockResponse)
    })

    it('应该获取每日进度数据', async () => {
      const mockResponse = [
        { date: '2024-01-01', words_typed: 100, accuracy: 95 }
      ]
      mockRequest.get.mockResolvedValue(mockResponse)

      const result = await englishAPI.getDailyProgress({ month: '2024-01' })
      
      expect(mockRequest.get).toHaveBeenCalledWith('/english/typing-practice/daily-progress/', { params: { month: '2024-01' } })
      expect(result).toEqual(mockResponse)
    })
  })

  describe('Data Analysis API', () => {
    it('应该获取数据概览', async () => {
      const mockResponse = { total_words: 1000, learned_words: 500, accuracy: 95.5 }
      mockRequest.get.mockResolvedValue(mockResponse)

      const result = await englishAPI.getDataOverview({ days: 30 })
      
      expect(mockRequest.get).toHaveBeenCalledWith('/english/data-analysis/overview/', { params: { days: 30 } })
      expect(result).toEqual(mockResponse)
    })

    it('应该获取练习热力图', async () => {
      const mockResponse = { dates: ['2024-01-01'], counts: [10] }
      mockRequest.get.mockResolvedValue(mockResponse)

      const result = await englishAPI.getExerciseHeatmap({ year: 2024 })
      
      expect(mockRequest.get).toHaveBeenCalledWith('/english/data-analysis/exercise_heatmap/', { params: { year: 2024 } })
      expect(result).toEqual(mockResponse)
    })

    it('应该获取单词热力图', async () => {
      const mockResponse = { words: ['hello', 'world'], frequencies: [100, 80] }
      mockRequest.get.mockResolvedValue(mockResponse)

      const result = await englishAPI.getWordHeatmap({ limit: 20 })
      
      expect(mockRequest.get).toHaveBeenCalledWith('/english/data-analysis/word_heatmap/', { params: { limit: 20 } })
      expect(result).toEqual(mockResponse)
    })

    it('应该获取WPM趋势', async () => {
      const mockResponse = { dates: ['2024-01-01'], wpm: [60, 65, 70] }
      mockRequest.get.mockResolvedValue(mockResponse)

      const result = await englishAPI.getWpmTrend({ days: 7 })
      
      expect(mockRequest.get).toHaveBeenCalledWith('/english/data-analysis/wpm_trend/', { params: { days: 7 } })
      expect(result).toEqual(mockResponse)
    })

    it('应该获取准确率趋势', async () => {
      const mockResponse = { dates: ['2024-01-01'], accuracy: [95, 96, 97] }
      mockRequest.get.mockResolvedValue(mockResponse)

      const result = await englishAPI.getAccuracyTrend({ days: 7 })
      
      expect(mockRequest.get).toHaveBeenCalledWith('/english/data-analysis/accuracy_trend/', { params: { days: 7 } })
      expect(result).toEqual(mockResponse)
    })

    it('应该获取按键错误统计', async () => {
      const mockResponse = { common_errors: ['a', 's'], error_counts: [10, 8] }
      mockRequest.get.mockResolvedValue(mockResponse)

      const result = await englishAPI.getKeyErrorStats()
      
      expect(mockRequest.get).toHaveBeenCalledWith('/english/data-analysis/key_error_stats/')
      expect(result).toEqual(mockResponse)
    })
  })
})

describe('dataAnalysisAPI', () => {
  let mockRequest: any

  beforeEach(async () => {
    const requestModule = await import('../request')
    mockRequest = requestModule.default
    mockRequest.get.mockClear()
    mockRequest.post.mockClear()
    mockRequest.put.mockClear()
    mockRequest.delete.mockClear()
  })

  it('应该获取概览数据', async () => {
    const mockResponse = { total_words: 1000, learned_words: 500, accuracy: 95.5 }
    mockRequest.get.mockResolvedValue(mockResponse)

    const result = await dataAnalysisAPI.getOverview({ days: 30 })
    
    expect(mockRequest.get).toHaveBeenCalledWith('/english/data-analysis/overview/', { params: { days: 30 } })
    expect(result).toEqual(mockResponse)
  })

  it('应该获取练习热力图', async () => {
    const mockResponse = { dates: ['2024-01-01'], counts: [10] }
    mockRequest.get.mockResolvedValue(mockResponse)

    const result = await dataAnalysisAPI.getExerciseHeatmap({ year: 2024 })
    
    expect(mockRequest.get).toHaveBeenCalledWith('/english/data-analysis/exercise_heatmap/', { params: { year: 2024 } })
    expect(result).toEqual(mockResponse)
  })

  it('应该获取单词热力图', async () => {
    const mockResponse = { words: ['hello', 'world'], frequencies: [100, 80] }
    mockRequest.get.mockResolvedValue(mockResponse)

    const result = await dataAnalysisAPI.getWordHeatmap({ limit: 20 })
    
    expect(mockRequest.get).toHaveBeenCalledWith('/english/data-analysis/word_heatmap/', { params: { limit: 20 } })
    expect(result).toEqual(mockResponse)
  })

  it('应该获取WPM趋势', async () => {
    const mockResponse = { dates: ['2024-01-01'], wpm: [60, 65, 70] }
    mockRequest.get.mockResolvedValue(mockResponse)

    const result = await dataAnalysisAPI.getWpmTrend({ days: 7 })
    
    expect(mockRequest.get).toHaveBeenCalledWith('/english/data-analysis/wpm_trend/', { params: { days: 7 } })
    expect(result).toEqual(mockResponse)
  })

  it('应该获取准确率趋势', async () => {
    const mockResponse = { dates: ['2024-01-01'], accuracy: [95, 96, 97] }
    mockRequest.get.mockResolvedValue(mockResponse)

    const result = await dataAnalysisAPI.getAccuracyTrend({ days: 7 })
    
    expect(mockRequest.get).toHaveBeenCalledWith('/english/data-analysis/accuracy_trend/', { params: { days: 7 } })
    expect(result).toEqual(mockResponse)
  })

  it('应该获取按键错误统计', async () => {
    const mockResponse = { common_errors: ['a', 's'], error_counts: [10, 8] }
    mockRequest.get.mockResolvedValue(mockResponse)

    const result = await dataAnalysisAPI.getKeyErrorStats()
    
    expect(mockRequest.get).toHaveBeenCalledWith('/english/data-analysis/key_error_stats/')
    expect(result).toEqual(mockResponse)
  })

  it('应该获取月历热力图数据', async () => {
    const mockResponse = { month: '2024-01', daily_counts: [10, 15, 20] }
    mockRequest.get.mockResolvedValue(mockResponse)

    const result = await dataAnalysisAPI.getMonthlyCalendar({ year: 2024, month: 1 })
    
    expect(mockRequest.get).toHaveBeenCalledWith('/english/data-analysis/monthly-calendar/', { params: { year: 2024, month: 1 } })
    expect(result).toEqual(mockResponse)
  })
})
