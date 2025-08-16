import { defineStore } from 'pinia'
import { englishAPI } from '@/api/english'

export const useNewsStore = defineStore('news', {
  state: () => ({
    // 新闻列表
    news: [],
    newsLoading: false,
    newsPagination: { page: 1, pageSize: 20, total: 0 },
    newsQuery: { search: '', source: '', ordering: '-published_at' },

    // 爬取设置
    crawlSettings: {
      maxArticles: 3,
      timeout: 300, // 默认300秒超时
      sources: [],
      autoCrawl: false
    },

    // 爬取状态
    crawling: false,
    crawlProgress: 0,
    crawlStatus: '',

    // 新闻详情
    currentNews: null,
    newsDetailLoading: false,
    

  }),

  actions: {
    // 获取新闻列表
    async fetchNews(params = {}) {
      this.newsLoading = true
      try {
        const queryRaw = { ...this.newsQuery, ...params }
        const query = {
          page: this.newsPagination.page,
          page_size: this.newsPagination.pageSize,
          q: queryRaw.search,
          source: queryRaw.source,
          ordering: queryRaw.ordering
        }
        const resp = await englishAPI.getNewsList(query)
        const data = resp?.data || resp?.results || resp?.items || []
        const total = resp?.pagination?.total || resp?.count || 0
        this.news = data
        this.newsPagination.total = total
        return data
      } finally {
        this.newsLoading = false
      }
    },

    // 获取新闻详情
    async fetchNewsDetail(newsId) {
      this.newsDetailLoading = true
      try {
        const resp = await englishAPI.getNewsDetail(newsId)
        this.currentNews = resp?.data || resp
        return this.currentNews
      } finally {
        this.newsDetailLoading = false
      }
    },

    // 爬取新闻
    async crawlNews(settings = null) {
      this.crawling = true
      this.crawlProgress = 0
      this.crawlStatus = '开始爬取...'
      
      try {
        const crawlSettings = settings || this.crawlSettings
        
        // 更新爬取设置
        this.crawlSettings = { ...this.crawlSettings, ...crawlSettings }
        
        // 保存设置到本地存储
        localStorage.setItem('crawlSettings', JSON.stringify(this.crawlSettings))
        
        // 开始爬取
        this.crawlStatus = '正在爬取新闻...'
        this.crawlProgress = 20
        
        const resp = await englishAPI.triggerNewsCrawl(crawlSettings)
        
        this.crawlProgress = 80
        this.crawlStatus = '爬取完成，正在刷新数据...'
        
        // 刷新新闻列表
        await this.fetchNews()
        
        this.crawlProgress = 100
        this.crawlStatus = '爬取完成！'
        
        return resp
      } catch (error) {
        this.crawlStatus = '爬取失败：' + error.message
        throw error
      } finally {
        this.crawling = false
        // 3秒后重置状态
        setTimeout(() => {
          this.crawlProgress = 0
          this.crawlStatus = ''
        }, 3000)
      }
    },

    // 删除新闻
    async deleteNews(newsId) {
      try {
        await englishAPI.deleteNews(newsId)
        // 从本地列表中移除
        this.news = this.news.filter(news => news.id !== newsId)
        this.newsPagination.total -= 1
        return true
      } catch (error) {
        throw error
      }
    },

    // 批量删除新闻
    async batchDeleteNews(newsIds) {
      try {
        const deletePromises = newsIds.map(id => englishAPI.deleteNews(id))
        await Promise.all(deletePromises)
        
        // 从本地列表中移除
        this.news = this.news.filter(news => !newsIds.includes(news.id))
        this.newsPagination.total -= newsIds.length
        
        return true
      } catch (error) {
        throw error
      }
    },



    // 保存爬取设置
    async saveCrawlSettings(settings) {
      try {
        this.crawlSettings = { ...this.crawlSettings, ...settings }
        localStorage.setItem('crawlSettings', JSON.stringify(this.crawlSettings))
        
        // 这里可以调用API保存设置到后端
        // await englishAPI.saveCrawlSettings(this.crawlSettings)
        
        return true
      } catch (error) {
        throw error
      }
    },

    // 加载爬取设置
    loadCrawlSettings() {
      try {
        const savedSettings = localStorage.getItem('crawlSettings')
        if (savedSettings) {
          this.crawlSettings = { ...this.crawlSettings, ...JSON.parse(savedSettings) }
        }
      } catch (error) {
        console.error('加载爬取设置失败:', error)
      }
    },

    // 搜索新闻
    async searchNews(keyword) {
      this.newsQuery.search = keyword
      return await this.fetchNews()
    },

    // 按来源筛选新闻
    async filterNewsBySource(source) {
      this.newsQuery.source = source
      return await this.fetchNews()
    },

    // 重置查询
    resetQuery() {
      this.newsQuery = { search: '', source: '', ordering: '-published_at' }
      this.newsPagination.page = 1
    },

    // 获取管理界面新闻列表


    // 重置状态
    resetState() {
      this.news = []
      this.newsLoading = false
      this.newsPagination = { page: 1, pageSize: 20, total: 0 }
      this.newsQuery = { search: '', source: '', ordering: '-published_at' }
      this.crawling = false
      this.crawlProgress = 0
      this.crawlStatus = ''
      this.currentNews = null
      this.newsDetailLoading = false
      this.managementNews = []
      this.managementNewsLoading = false
    }
  },

  getters: {
    // 获取特色新闻（用于轮播）
    featuredNews: (state) => {
      return state.news.slice(0, 5)
    },

    // 获取热门新闻
    hotNews: (state) => {
      return state.news.slice(0, 6)
    },

    // 获取最新新闻
    latestNews: (state) => {
      return state.news.slice(0, 10)
    },

    // 获取按来源分组的新闻
    newsBySource: (state) => {
      const grouped = {}
      state.news.forEach(news => {
        if (!grouped[news.source]) {
          grouped[news.source] = []
        }
        grouped[news.source].push(news)
      })
      return grouped
    },

    // 获取可见的新闻
    visibleNews: (state) => {
      return state.news.filter(news => news.is_visible !== false)
    },

    // 获取爬取状态
    crawlStatusInfo: (state) => {
      return {
        isCrawling: state.crawling,
        progress: state.crawlProgress,
        status: state.crawlStatus
      }
    },

    // 获取新闻统计
    newsStats: (state) => {
      const total = state.news.length
      const bySource = {}
      const visible = state.news.filter(news => news.is_visible !== false).length
      
      state.news.forEach(news => {
        bySource[news.source] = (bySource[news.source] || 0) + 1
      })
      
      return {
        total,
        visible,
        hidden: total - visible,
        bySource
      }
    }
  }
})
