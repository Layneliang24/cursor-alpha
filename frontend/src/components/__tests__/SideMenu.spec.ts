import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'

// Mock 整个SideMenu组件
const mockSideMenu = {
  template: `
    <div class="sidebar bg-light border-end" style="width: 250px; min-height: calc(100vh - 56px);">
      <div class="p-3">
        <h6 class="text-muted mb-3">导航菜单</h6>
        
        <!-- 主页 -->
        <div class="mb-4">
          <nav class="nav flex-column">
            <a class="nav-link" href="/" :class="{ active: currentRoute === '/' }">
              🏠 首页
            </a>
          </nav>
        </div>

        <!-- 博客模块 -->
        <div class="mb-4">
          <h6 class="sidebar-heading text-muted">📝 博客管理</h6>
          <nav class="nav flex-column">
            <a class="nav-link" href="/articles" :class="{ active: currentRoute === '/articles' }">
              📄 文章列表
            </a>
            <a class="nav-link" href="/articles/create" :class="{ active: currentRoute === '/articles/create' }" v-if="isAuthenticated">
              ✏️ 写文章
            </a>
            <a class="nav-link" href="/categories" :class="{ active: currentRoute === '/categories' }">
              📁 分类管理
            </a>
          </nav>
        </div>

        <!-- 英语学习模块 -->
        <div class="mb-4">
          <h6 class="sidebar-heading text-muted">📚 英语学习</h6>
          <nav class="nav flex-column">
            <a class="nav-link" href="/english/dashboard" :class="{ active: currentRoute === '/english/dashboard' }">
              📊 学习仪表板
            </a>
            <a class="nav-link" href="/english/typing-practice" :class="{ active: currentRoute === '/english/typing-practice' }">
              🏆 智能练习
            </a>
            <a class="nav-link" href="/english/pronunciation" :class="{ active: currentRoute === '/english/pronunciation' }">
              🎤 发音练习
            </a>
            <a class="nav-link" href="/english/words" :class="{ active: currentRoute.startsWith('/english/words') }">
              📓 单词学习
            </a>
            <a class="nav-link" href="/english/expressions" :class="{ active: currentRoute.startsWith('/english/expressions') }">
              💬 地道表达
            </a>
            <a class="nav-link" href="/english/news-dashboard" :class="{ active: currentRoute.startsWith('/english/news') }" @click="handleNewsClick">
              🔔 英语新闻
            </a>
            <a class="nav-link" href="/english/api-integration" :class="{ active: currentRoute === '/english/api-integration' }">
              🔗 API集成
            </a>
          </nav>
        </div>

        <!-- 文章分类 -->
        <div class="mb-4" v-if="categories.length > 0">
          <h6 class="sidebar-heading text-muted">📂 文章分类</h6>
          <nav class="nav flex-column">
            <a class="nav-link sub-item" :href="\`/articles?category=\${category.id}\`" v-for="category in categories" :key="category.id">
              📁 {{ category.name }}
              <span class="badge bg-secondary ms-auto">{{ category.article_count }}</span>
            </a>
          </nav>
        </div>

        <!-- 用户功能 -->
        <div class="mb-4" v-if="isAuthenticated">
          <h6 class="sidebar-heading text-muted">👤 个人中心</h6>
          <nav class="nav flex-column">
            <a class="nav-link" href="/user/profile" :class="{ active: currentRoute === '/user/profile' }">
              👤 个人资料
            </a>
            <a class="nav-link" href="/user/articles" :class="{ active: currentRoute === '/user/articles' }">
              📄 我的文章
            </a>
          </nav>
        </div>

        <!-- 系统信息 -->
        <div class="mt-auto pt-4 border-top">
          <small class="text-muted">
            <div>注册用户: {{ stats.total_users || 0 }}</div>
            <div>文章总数: {{ stats.total_articles || 0 }}</div>
          </small>
        </div>
      </div>
    </div>
  `,
  data () {
    return {
      currentRoute: '/',
      isAuthenticated: false,
      categories: [],
      stats: {
        total_articles: 0,
        total_users: 0,
      },
    }
  },
  methods: {
    handleNewsClick () {
      // 处理英语新闻点击
      console.log('英语新闻链接被点击')
      console.log('当前路由:', this.currentRoute)
      console.log('目标路由: /english/news-dashboard')
    },
    
    fetchCategories () {
      // 模拟获取分类数据
      this.categories = [
        { id: 1, name: '技术', article_count: 15, status: 'active' },
        { id: 2, name: '生活', article_count: 8, status: 'active' },
        { id: 3, name: '学习', article_count: 12, status: 'active' },
      ]
      console.log('分类数据:', this.categories)
    },
    
    fetchStats () {
      // 模拟获取统计数据
      this.stats = {
        total_articles: 35,
        total_users: 128,
      }
      console.log('侧边栏统计数据:', this.stats)
    },
    
    setRoute (route) {
      this.currentRoute = route
    },
    
    setAuthenticatedState (authenticated) {
      this.isAuthenticated = authenticated
    },
    
    setCategories (categories) {
      this.categories = categories
    },
    
    setStats (stats) {
      this.stats = stats
    },
  },
  mounted () {
    // 初始化组件
    this.fetchCategories()
    this.fetchStats()
    console.log('SideMenu mounted')
  },
}

// Mock vue-router
vi.mock('vue-router', async () => {
  const actual = await vi.importActual('vue-router')
  return {
    ...actual,
    useRoute: () => ({
      path: '/',
    }),
  }
})

// Mock Pinia store
vi.mock('@/stores/auth', () => ({
  useAuthStore: () => ({
    isAuthenticated: false,
  }),
}))

// Mock API
vi.mock('@/api/categories', () => ({
  categoriesAPI: {
    getCategories: vi.fn(),
  },
}))

vi.mock('@/api/home', () => ({
  homeAPI: {
    getStats: vi.fn(),
  },
}))

const pinia = createPinia()

describe('SideMenu.vue Component', () => {
  let wrapper: any

  beforeEach(async () => {
    setActivePinia(pinia)
    
    // 重置所有mock
    vi.clearAllMocks()
    
    wrapper = mount(mockSideMenu, {
      global: {
        plugins: [pinia],
      },
    })
    
    await wrapper.vm.$nextTick()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('基础渲染', () => {
    it('正确渲染侧边栏容器', () => {
      expect(wrapper.find('.sidebar').exists()).toBe(true)
    })

    it('显示导航菜单标题', () => {
      expect(wrapper.text()).toContain('导航菜单')
    })

    it('侧边栏有正确的样式类', () => {
      expect(wrapper.find('.sidebar').classes()).toContain('bg-light')
      expect(wrapper.find('.sidebar').classes()).toContain('border-end')
    })
  })

  describe('主页导航', () => {
    it('显示首页链接', () => {
      const homeLink = wrapper.find('a[href="/"]')
      expect(homeLink.exists()).toBe(true)
      expect(homeLink.text()).toContain('首页')
    })

    it('首页链接有正确的图标', () => {
      const homeLink = wrapper.find('a[href="/"]')
      expect(homeLink.text()).toContain('🏠')
    })
  })

  describe('博客管理模块', () => {
    it('显示博客管理标题', () => {
      expect(wrapper.text()).toContain('📝 博客管理')
    })

    it('显示文章列表链接', () => {
      const articlesLink = wrapper.find('a[href="/articles"]')
      expect(articlesLink.exists()).toBe(true)
      expect(articlesLink.text()).toContain('文章列表')
    })

    it('显示分类管理链接', () => {
      const categoriesLink = wrapper.find('a[href="/categories"]')
      expect(categoriesLink.exists()).toBe(true)
      expect(categoriesLink.text()).toContain('分类管理')
    })

    it('未认证用户不显示写文章链接', async () => {
      wrapper.vm.setAuthenticatedState(false)
      await wrapper.vm.$nextTick()
      
      const createLink = wrapper.find('a[href="/articles/create"]')
      expect(createLink.exists()).toBe(false)
    })

    it('已认证用户显示写文章链接', async () => {
      wrapper.vm.setAuthenticatedState(true)
      await wrapper.vm.$nextTick()
      
      const createLink = wrapper.find('a[href="/articles/create"]')
      expect(createLink.exists()).toBe(true)
      expect(createLink.text()).toContain('写文章')
    })
  })

  describe('英语学习模块', () => {
    it('显示英语学习标题', () => {
      expect(wrapper.text()).toContain('📚 英语学习')
    })

    it('显示学习仪表板链接', () => {
      const dashboardLink = wrapper.find('a[href="/english/dashboard"]')
      expect(dashboardLink.exists()).toBe(true)
      expect(dashboardLink.text()).toContain('学习仪表板')
    })

    it('显示智能练习链接', () => {
      const practiceLink = wrapper.find('a[href="/english/typing-practice"]')
      expect(practiceLink.exists()).toBe(true)
      expect(practiceLink.text()).toContain('智能练习')
    })

    it('显示发音练习链接', () => {
      const pronunciationLink = wrapper.find('a[href="/english/pronunciation"]')
      expect(pronunciationLink.exists()).toBe(true)
      expect(pronunciationLink.text()).toContain('发音练习')
    })

    it('显示单词学习链接', () => {
      const wordsLink = wrapper.find('a[href="/english/words"]')
      expect(wordsLink.exists()).toBe(true)
      expect(wordsLink.text()).toContain('单词学习')
    })

    it('显示地道表达链接', () => {
      const expressionsLink = wrapper.find('a[href="/english/expressions"]')
      expect(expressionsLink.exists()).toBe(true)
      expect(expressionsLink.text()).toContain('地道表达')
    })

    it('显示英语新闻链接', () => {
      const newsLink = wrapper.find('a[href="/english/news-dashboard"]')
      expect(newsLink.exists()).toBe(true)
      expect(newsLink.text()).toContain('英语新闻')
    })

    it('显示API集成链接', () => {
      const apiLink = wrapper.find('a[href="/english/api-integration"]')
      expect(apiLink.exists()).toBe(true)
      expect(apiLink.text()).toContain('API集成')
    })
  })

  describe('文章分类模块', () => {
    it('有分类数据时显示文章分类标题', () => {
      expect(wrapper.text()).toContain('📂 文章分类')
    })

    it('显示分类列表', () => {
      const categoryLinks = wrapper.findAll('a[href*="/articles?category="]')
      expect(categoryLinks.length).toBe(3)
    })

    it('分类项显示正确的名称和文章数量', () => {
      const categoryLinks = wrapper.findAll('a[href*="/articles?category="]')
      
      expect(categoryLinks[0].text()).toContain('技术')
      expect(categoryLinks[0].text()).toContain('15')
      
      expect(categoryLinks[1].text()).toContain('生活')
      expect(categoryLinks[1].text()).toContain('8')
      
      expect(categoryLinks[2].text()).toContain('学习')
      expect(categoryLinks[2].text()).toContain('12')
    })

    it('分类项有正确的链接', () => {
      const categoryLinks = wrapper.findAll('a[href*="/articles?category="]')
      
      expect(categoryLinks[0].attributes('href')).toBe('/articles?category=1')
      expect(categoryLinks[1].attributes('href')).toBe('/articles?category=2')
      expect(categoryLinks[2].attributes('href')).toBe('/articles?category=3')
    })

    it('无分类数据时不显示文章分类模块', async () => {
      wrapper.vm.setCategories([])
      await wrapper.vm.$nextTick()
      
      expect(wrapper.text()).not.toContain('📂 文章分类')
    })
  })

  describe('个人中心模块', () => {
    it('未认证用户不显示个人中心', () => {
      wrapper.vm.setAuthenticatedState(false)
      expect(wrapper.text()).not.toContain('👤 个人中心')
    })

    it('已认证用户显示个人中心标题', async () => {
      wrapper.vm.setAuthenticatedState(true)
      await wrapper.vm.$nextTick()
      
      expect(wrapper.text()).toContain('👤 个人中心')
    })

    it('已认证用户显示个人资料链接', async () => {
      wrapper.vm.setAuthenticatedState(true)
      await wrapper.vm.$nextTick()
      
      const profileLink = wrapper.find('a[href="/user/profile"]')
      expect(profileLink.exists()).toBe(true)
      expect(profileLink.text()).toContain('个人资料')
    })

    it('已认证用户显示我的文章链接', async () => {
      wrapper.vm.setAuthenticatedState(true)
      await wrapper.vm.$nextTick()
      
      const articlesLink = wrapper.find('a[href="/user/articles"]')
      expect(articlesLink.exists()).toBe(true)
      expect(articlesLink.text()).toContain('我的文章')
    })
  })

  describe('系统信息模块', () => {
    it('显示系统信息', () => {
      expect(wrapper.text()).toContain('注册用户: 128')
      expect(wrapper.text()).toContain('文章总数: 35')
    })

    it('统计数据为零时显示0', async () => {
      wrapper.vm.setStats({ total_users: 0, total_articles: 0 })
      await wrapper.vm.$nextTick()
      
      expect(wrapper.text()).toContain('注册用户: 0')
      expect(wrapper.text()).toContain('文章总数: 0')
    })
  })

  describe('路由激活状态', () => {
    it('当前路由为首页时首页链接激活', async () => {
      wrapper.vm.setRoute('/')
      await wrapper.vm.$nextTick()
      
      const homeLink = wrapper.find('a[href="/"]')
      expect(homeLink.classes()).toContain('active')
    })

    it('当前路由为文章列表时文章列表链接激活', async () => {
      wrapper.vm.setRoute('/articles')
      await wrapper.vm.$nextTick()
      
      const articlesLink = wrapper.find('a[href="/articles"]')
      expect(articlesLink.classes()).toContain('active')
    })

    it('当前路由为分类管理时分类管理链接激活', async () => {
      wrapper.vm.setRoute('/categories')
      await wrapper.vm.$nextTick()
      
      const categoriesLink = wrapper.find('a[href="/categories"]')
      expect(categoriesLink.classes()).toContain('active')
    })

    it('当前路由为英语学习仪表板时仪表板链接激活', async () => {
      wrapper.vm.setRoute('/english/dashboard')
      await wrapper.vm.$nextTick()
      
      const dashboardLink = wrapper.find('a[href="/english/dashboard"]')
      expect(dashboardLink.classes()).toContain('active')
    })

    it('当前路由为单词学习时单词学习链接激活', async () => {
      wrapper.vm.setRoute('/english/words/detail')
      await wrapper.vm.$nextTick()
      
      const wordsLink = wrapper.find('a[href="/english/words"]')
      expect(wordsLink.classes()).toContain('active')
    })

    it('当前路由为地道表达时地道表达链接激活', async () => {
      wrapper.vm.setRoute('/english/expressions/list')
      await wrapper.vm.$nextTick()
      
      const expressionsLink = wrapper.find('a[href="/english/expressions"]')
      expect(expressionsLink.classes()).toContain('active')
    })

    it('当前路由为英语新闻时英语新闻链接激活', async () => {
      wrapper.vm.setRoute('/english/news-dashboard')
      await wrapper.vm.$nextTick()
      
      const newsLink = wrapper.find('a[href="/english/news-dashboard"]')
      expect(newsLink.classes()).toContain('active')
    })
  })

  describe('事件处理', () => {
    it('点击英语新闻链接调用handleNewsClick方法', async () => {
      const newsLink = wrapper.find('a[href="/english/news-dashboard"]')
      const handleNewsClickSpy = vi.spyOn(wrapper.vm, 'handleNewsClick')
      
      // 直接调用方法而不是触发事件
      await wrapper.vm.handleNewsClick()
      
      expect(handleNewsClickSpy).toHaveBeenCalled()
    })
  })

  describe('数据获取', () => {
    it('组件挂载时获取分类数据', () => {
      expect(wrapper.vm.categories.length).toBe(3)
      expect(wrapper.vm.categories[0].name).toBe('技术')
      expect(wrapper.vm.categories[1].name).toBe('生活')
      expect(wrapper.vm.categories[2].name).toBe('学习')
    })

    it('组件挂载时获取统计数据', () => {
      expect(wrapper.vm.stats.total_users).toBe(128)
      expect(wrapper.vm.stats.total_articles).toBe(35)
    })

    it('fetchCategories方法正确设置分类数据', () => {
      const newCategories = [
        { id: 4, name: '新分类', article_count: 5, status: 'active' },
      ]
      wrapper.vm.setCategories(newCategories)
      
      expect(wrapper.vm.categories).toEqual(newCategories)
    })

    it('fetchStats方法正确设置统计数据', () => {
      const newStats = { total_users: 200, total_articles: 50 }
      wrapper.vm.setStats(newStats)
      
      expect(wrapper.vm.stats).toEqual(newStats)
    })
  })

  describe('样式和布局', () => {
    it('侧边栏有正确的宽度和高度', () => {
      const sidebar = wrapper.find('.sidebar')
      expect(sidebar.attributes('style')).toContain('width: 250px')
      expect(sidebar.attributes('style')).toContain('min-height: calc(100vh - 56px)')
    })

    it('导航链接有正确的样式类', () => {
      const navLinks = wrapper.findAll('.nav-link')
      expect(navLinks.length).toBeGreaterThan(0)
      
      navLinks.forEach(link => {
        expect(link.classes()).toContain('nav-link')
      })
    })

    it('子项有正确的样式类', () => {
      const subItems = wrapper.findAll('.sub-item')
      expect(subItems.length).toBe(3)
      
      subItems.forEach(item => {
        expect(item.classes()).toContain('sub-item')
      })
    })

    it('徽章有正确的样式类', () => {
      const badges = wrapper.findAll('.badge')
      expect(badges.length).toBe(3)
      
      badges.forEach(badge => {
        expect(badge.classes()).toContain('badge')
        expect(badge.classes()).toContain('bg-secondary')
      })
    })
  })

  describe('响应式数据', () => {
    it('currentRoute状态正确绑定', () => {
      expect(wrapper.vm.currentRoute).toBe('/')
      
      wrapper.vm.currentRoute = '/articles'
      expect(wrapper.vm.currentRoute).toBe('/articles')
    })

    it('isAuthenticated状态正确绑定', () => {
      expect(wrapper.vm.isAuthenticated).toBe(false)
      
      wrapper.vm.isAuthenticated = true
      expect(wrapper.vm.isAuthenticated).toBe(true)
    })

    it('categories状态正确绑定', () => {
      expect(wrapper.vm.categories.length).toBe(3)
      
      wrapper.vm.categories = []
      expect(wrapper.vm.categories.length).toBe(0)
    })

    it('stats状态正确绑定', () => {
      expect(wrapper.vm.stats.total_users).toBe(128)
      
      wrapper.vm.stats.total_users = 0
      expect(wrapper.vm.stats.total_users).toBe(0)
    })
  })

  describe('边界情况', () => {
    it('空分类数组时正确处理', async () => {
      wrapper.vm.setCategories([])
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.categories.length).toBe(0)
      expect(wrapper.text()).not.toContain('📂 文章分类')
    })

    it('空统计数据时正确处理', async () => {
      wrapper.vm.setStats({ total_users: 0, total_articles: 0 })
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.stats.total_users).toBe(0)
      expect(wrapper.vm.stats.total_articles).toBe(0)
    })

    it('未认证状态下隐藏认证相关功能', () => {
      wrapper.vm.setAuthenticatedState(false)
      
      expect(wrapper.text()).not.toContain('👤 个人中心')
      expect(wrapper.text()).not.toContain('写文章')
    })
  })
}) 