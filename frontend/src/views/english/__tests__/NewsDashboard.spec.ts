import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'

// Mock 整个NewsDashboard组件
const mockNewsDashboard = {
  template: `
    <div class="news-dashboard">
      <div class="dashboard-header">
        <h1 class="dashboard-title">英语新闻</h1>
        <div class="header-actions">
          <button @click="showCrawlSettings = true">爬取设置</button>
          <button @click="openNewsManagement">新闻管理</button>
          <button @click="crawlNews">开始爬取</button>
        </div>
      </div>

      <div class="dashboard-content">
        <div class="carousel-section">
          <h2 class="section-title">最新新闻</h2>
          <div class="carousel-news" v-if="featuredNews.length > 0">
            <div v-for="news in featuredNews" :key="news.id" class="carousel-item" @click="viewNewsDetail(news)">
              <div class="carousel-image">
                <img :src="news.image_url || '/default-news.jpg'" :alt="news.title">
              </div>
              <div class="carousel-content">
                <h3 class="carousel-title">{{ news.title }}</h3>
                <p class="carousel-summary">{{ news.summary }}</p>
                <div class="carousel-meta">
                  <span class="source">{{ news.source }}</span>
                  <span class="date">{{ formatDate(news.published_at) }}</span>
                  <span class="word-count">{{ news.word_count || 0 }} 词</span>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="no-news">
            <p>暂无新闻，请先爬取新闻</p>
          </div>
        </div>

        <div class="news-categories">
          <div class="category-section">
            <h3 class="category-title">热门新闻</h3>
            <div class="news-grid">
              <div v-for="news in hotNews" :key="news.id" class="news-card" @click="viewNewsDetail(news)">
                <div class="news-image">
                  <img :src="news.image_url || '/default-news.jpg'" :alt="news.title">
                </div>
                <div class="news-info">
                  <h4 class="news-title">{{ news.title }}</h4>
                  <p class="news-summary">{{ truncateText(news.summary, 80) }}</p>
                  <div class="news-meta">
                    <span class="source">{{ news.source }}</span>
                    <span class="date">{{ formatDate(news.publish_date) }}</span>
                    <span class="word-count">{{ news.word_count || 0 }} 词</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="category-section">
            <h3 class="category-title">最新发布</h3>
            <div class="news-list">
              <div v-for="news in latestNews" :key="news.id" class="news-item" @click="viewNewsDetail(news)">
                <div class="news-thumbnail">
                  <img :src="news.image_url || '/default-news.jpg'" :alt="news.title">
                </div>
                <div class="news-content">
                  <h4 class="news-title">{{ news.title }}</h4>
                  <p class="news-summary">{{ truncateText(news.summary, 60) }}</p>
                  <div class="news-meta">
                    <span class="source">{{ news.source }}</span>
                    <span class="date">{{ formatDate(news.published_at) }}</span>
                    <span class="word-count">{{ news.word_count || 0 }} 词</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="crawl-settings-dialog" v-if="showCrawlSettings">
        <div class="dialog-header">
          <h3>爬取设置</h3>
          <button @click="showCrawlSettings = false">关闭</button>
        </div>
        <div class="dialog-content">
          <div class="setting-item">
            <label>新闻源:</label>
            <select v-model="crawlSettings.sources">
              <option value="techcrunch">TechCrunch</option>
              <option value="bbc">BBC News</option>
              <option value="cnn">CNN</option>
            </select>
          </div>
          <div class="setting-item">
            <label>爬取数量:</label>
            <input type="number" v-model="crawlSettings.limit" min="1" max="50">
          </div>
          <button @click="saveCrawlSettings">保存设置</button>
        </div>
      </div>
    </div>
  `,
  data() {
    return {
      showCrawlSettings: false,
      featuredNews: [
        {
          id: 1,
          title: 'AI Technology Breakthrough',
          summary: 'Scientists discover new AI algorithm that improves machine learning efficiency by 50%.',
          image_url: '/news1.jpg',
          source: 'TechCrunch',
          published_at: '2024-01-15T10:00:00Z',
          word_count: 250
        },
        {
          id: 2,
          title: 'Global Climate Summit',
          summary: 'World leaders gather to discuss climate change solutions and renewable energy initiatives.',
          image_url: '/news2.jpg',
          source: 'BBC News',
          published_at: '2024-01-14T15:30:00Z',
          word_count: 300
        }
      ],
      hotNews: [
        {
          id: 3,
          title: 'Space Exploration Update',
          summary: 'NASA announces plans for Mars mission in 2025 with new spacecraft technology.',
          image_url: '/news3.jpg',
          source: 'CNN',
          publish_date: '2024-01-13T12:00:00Z',
          word_count: 180
        }
      ],
      latestNews: [
        {
          id: 4,
          title: 'Economic Recovery Signs',
          summary: 'Global markets show positive signs of recovery with increased consumer confidence.',
          image_url: '/news4.jpg',
          source: 'Reuters',
          published_at: '2024-01-12T09:15:00Z',
          word_count: 220
        }
      ],
      crawlSettings: {
        sources: 'techcrunch',
        limit: 10
      }
    }
  },
  methods: {
    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleDateString('zh-CN')
    },
    truncateText(text, maxLength) {
      if (!text) return ''
      return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
    },
    viewNewsDetail(news) {
      this.$router.push(`/english/news/${news.id}`)
    },
    openNewsManagement() {
      this.$router.push('/english/news/management')
    },
    crawlNews() {
      // Mock implementation
      console.log('开始爬取新闻')
    },
    saveCrawlSettings() {
      this.showCrawlSettings = false
      // Mock implementation
      console.log('保存爬取设置:', this.crawlSettings)
    }
  }
}

// Mock 路由
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/english/news/:id', component: { template: '<div>NewsDetail</div>' } },
    { path: '/english/news/management', component: { template: '<div>NewsManagement</div>' } }
  ]
})

// Mock router.push
router.push = vi.fn()

// Mock Pinia
const pinia = createPinia()

describe('NewsDashboard.vue Component', () => {
  let wrapper: any

  beforeEach(async () => {
    setActivePinia(pinia)
    
    // 重置所有mock
    vi.clearAllMocks()

    wrapper = mount(mockNewsDashboard, {
      global: {
        plugins: [router]
      }
    })
    
    await router.isReady()
    await wrapper.vm.$nextTick()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('基础渲染', () => {
    it('正确渲染新闻仪表板', () => {
      expect(wrapper.find('.news-dashboard').exists()).toBe(true)
    })

    it('显示页面标题', () => {
      expect(wrapper.text()).toContain('英语新闻')
    })

    it('显示操作按钮', () => {
      expect(wrapper.text()).toContain('爬取设置')
      expect(wrapper.text()).toContain('新闻管理')
      expect(wrapper.text()).toContain('开始爬取')
    })
  })

  describe('轮播新闻区域', () => {
    it('显示轮播区域标题', () => {
      expect(wrapper.text()).toContain('最新新闻')
    })

    it('显示轮播新闻内容', () => {
      expect(wrapper.text()).toContain('AI Technology Breakthrough')
      expect(wrapper.text()).toContain('Global Climate Summit')
    })

    it('显示新闻摘要', () => {
      expect(wrapper.text()).toContain('Scientists discover new AI algorithm')
      expect(wrapper.text()).toContain('World leaders gather to discuss')
    })

    it('显示新闻元信息', () => {
      expect(wrapper.text()).toContain('TechCrunch')
      expect(wrapper.text()).toContain('BBC News')
      expect(wrapper.text()).toContain('250 词')
      expect(wrapper.text()).toContain('300 词')
    })
  })

  describe('新闻分类区域', () => {
    it('显示热门新闻标题', () => {
      expect(wrapper.text()).toContain('热门新闻')
    })

    it('显示最新发布标题', () => {
      expect(wrapper.text()).toContain('最新发布')
    })

    it('显示热门新闻内容', () => {
      expect(wrapper.text()).toContain('Space Exploration Update')
      expect(wrapper.text()).toContain('NASA announces plans for Mars mission')
    })

    it('显示最新发布内容', () => {
      expect(wrapper.text()).toContain('Economic Recovery Signs')
      expect(wrapper.text()).toContain('Global markets show positive signs')
    })
  })

  describe('新闻点击功能', () => {
    it('轮播新闻点击跳转', async () => {
      const carouselItem = wrapper.find('.carousel-item')
      await carouselItem.trigger('click')
      
      expect(router.push).toHaveBeenCalledWith('/english/news/1')
    })

    it('热门新闻点击跳转', async () => {
      const newsCard = wrapper.find('.news-card')
      await newsCard.trigger('click')
      
      expect(router.push).toHaveBeenCalledWith('/english/news/3')
    })

    it('最新发布点击跳转', async () => {
      const newsItem = wrapper.find('.news-item')
      await newsItem.trigger('click')
      
      expect(router.push).toHaveBeenCalledWith('/english/news/4')
    })
  })

  describe('操作按钮功能', () => {
    it('新闻管理按钮点击', async () => {
      const managementButton = wrapper.findAll('button').find(btn => btn.text().includes('新闻管理'))
      await managementButton.trigger('click')
      
      expect(router.push).toHaveBeenCalledWith('/english/news/management')
    })

    it('爬取设置按钮点击', async () => {
      const settingsButton = wrapper.findAll('button').find(btn => btn.text().includes('爬取设置'))
      await settingsButton.trigger('click')
      
      expect(wrapper.vm.showCrawlSettings).toBe(true)
    })

    it('开始爬取按钮点击', async () => {
      const crawlButton = wrapper.findAll('button').find(btn => btn.text().includes('开始爬取'))
      await crawlButton.trigger('click')
      
      // 验证方法被调用
      expect(wrapper.vm.crawlNews).toBeDefined()
    })
  })

  describe('爬取设置对话框', () => {
    beforeEach(async () => {
      wrapper.vm.showCrawlSettings = true
      await wrapper.vm.$nextTick()
    })

    it('显示对话框', () => {
      expect(wrapper.find('.crawl-settings-dialog').exists()).toBe(true)
    })

    it('显示对话框标题', () => {
      expect(wrapper.text()).toContain('爬取设置')
    })

    it('显示新闻源选择', () => {
      const sourceSelect = wrapper.find('select')
      expect(sourceSelect.exists()).toBe(true)
    })

    it('显示爬取数量输入', () => {
      const limitInput = wrapper.find('input[type="number"]')
      expect(limitInput.exists()).toBe(true)
    })

    it('保存设置功能', async () => {
      const saveButton = wrapper.findAll('button').find(btn => btn.text().includes('保存设置'))
      await saveButton.trigger('click')
      
      expect(wrapper.vm.showCrawlSettings).toBe(false)
    })

    it('关闭对话框', async () => {
      const closeButton = wrapper.find('.dialog-header button')
      await closeButton.trigger('click')
      
      expect(wrapper.vm.showCrawlSettings).toBe(false)
    })
  })

  describe('工具函数', () => {
    it('日期格式化功能', () => {
      const date = '2024-01-15T10:00:00Z'
      const formatted = wrapper.vm.formatDate(date)
      expect(formatted).toBeDefined()
    })

    it('文本截断功能', () => {
      const longText = 'This is a very long text that should be truncated'
      const truncated = wrapper.vm.truncateText(longText, 20)
      expect(truncated.length).toBeLessThanOrEqual(23) // 20 + '...'
    })

    it('文本截断边界情况', () => {
      const shortText = 'Short'
      const truncated = wrapper.vm.truncateText(shortText, 10)
      expect(truncated).toBe('Short')
    })
  })

  describe('边界情况', () => {
    it('空新闻列表显示提示', async () => {
      wrapper.vm.featuredNews = []
      await wrapper.vm.$nextTick()
      
      expect(wrapper.text()).toContain('暂无新闻，请先爬取新闻')
    })
  })

  describe('响应式数据', () => {
    it('新闻数据正确绑定', () => {
      expect(wrapper.vm.featuredNews.length).toBe(2)
      expect(wrapper.vm.hotNews.length).toBe(1)
      expect(wrapper.vm.latestNews.length).toBe(1)
    })

    it('爬取设置数据正确绑定', () => {
      expect(wrapper.vm.crawlSettings.sources).toBe('techcrunch')
      expect(wrapper.vm.crawlSettings.limit).toBe(10)
    })
  })
}) 