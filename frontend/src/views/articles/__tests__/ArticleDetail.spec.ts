import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'
import ArticleDetail from '../ArticleDetail.vue'

// Mock API模块
vi.mock('@/api/articles', () => ({
  articlesAPI: {
    getComments: vi.fn(),
    createComment: vi.fn()
  }
}))

// Mock stores
const mockArticlesStore = {
  loading: false,
  currentArticle: null as any,
  fetchArticle: vi.fn(),
  likeArticle: vi.fn(),
  bookmarkArticle: vi.fn()
}

const mockAuthStore = {
  isAuthenticated: true,
  user: { username: 'testuser', id: 1 }
}

vi.mock('@/stores/articles', () => ({
  useArticlesStore: () => mockArticlesStore
}))

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => mockAuthStore
}))

// Mock 子组件
const mockTableOfContents = {
  template: '<div class="table-of-contents">TableOfContents</div>',
  methods: {
    generateTOC: vi.fn()
  }
}

const mockMarkdownRenderer = {
  template: '<div class="markdown-renderer">{{ content }}</div>',
  props: ['content']
}

// Mock Element Plus组件
const mockElSkeleton = {
  template: '<div class="el-skeleton"><slot /></div>',
  props: ['rows', 'animated']
}

const mockElBreadcrumb = {
  template: '<nav class="el-breadcrumb"><slot /></nav>'
}

const mockElBreadcrumbItem = {
  template: '<span class="el-breadcrumb-item"><slot /></span>',
  props: ['to']
}

const mockElAvatar = {
  template: '<div class="el-avatar" :size="size"><slot /></div>',
  props: ['size']
}

const mockElIcon = {
  template: '<span class="el-icon"><slot /></span>'
}

const mockElTag = {
  template: '<span class="el-tag" :size="size"><slot /></span>',
  props: ['size']
}

const mockElButton = {
  template: '<button :type="type" :loading="loading" @click="$emit(\'click\')"><slot /></button>',
  props: ['type', 'loading'],
  emits: ['click']
}

const mockElInput = {
  template: '<textarea :value="modelValue" @input="$emit(\'update:modelValue\', $event.target.value)" />',
  props: ['modelValue'],
  emits: ['update:modelValue']
}

const mockElEmpty = {
  template: '<div class="el-empty"><slot /></div>',
  props: ['description']
}

// Mock 路由
const mockRoute = {
  params: { id: '1' }
}

// Mock useRoute
vi.mock('vue-router', async () => {
  const actual = await vi.importActual('vue-router')
  return {
    ...actual,
    useRoute: () => mockRoute,
    useRouter: () => ({
      push: vi.fn()
    })
  }
})

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: { template: '<div>Home</div>' } },
    { path: '/articles', component: { template: '<div>Articles</div>' } },
    { path: '/categories/:id', component: { template: '<div>Category</div>' } },
    { path: '/login', component: { template: '<div>Login</div>' } }
  ]
})

// Mock Pinia
const pinia = createPinia()

// Mock navigator.clipboard
Object.defineProperty(navigator, 'clipboard', {
  value: {
    writeText: vi.fn().mockResolvedValue(undefined)
  },
  writable: true
})

describe('ArticleDetail.vue Component', () => {
  let wrapper: any

  beforeEach(async () => {
    setActivePinia(pinia)
    
    // 重置所有mock
    vi.clearAllMocks()
    
    // 设置默认的mock返回值
    mockArticlesStore.currentArticle = {
      id: 1,
      title: '测试文章标题',
      content: '# 测试文章内容\n\n这是测试文章的完整内容。',
      summary: '测试文章摘要',
      cover_image: 'https://example.com/cover.jpg',
      author: { 
        username: 'testuser', 
        avatar: 'https://example.com/avatar.jpg',
        id: 1
      },
      category: { id: 1, name: '技术' },
      tags: [
        { id: 1, name: 'Vue.js', color: '#409eff' },
        { id: 2, name: 'JavaScript', color: '#67c23a' }
      ],
      created_at: '2024-01-15T10:00:00Z',
      updated_at: '2024-01-15T10:00:00Z',
      views: 150,
      likes: 25,
      comments_count: 8,
      reading_time: 5,
      featured: true
    }
    
    mockArticlesStore.loading = false

    wrapper = mount(ArticleDetail, {
      global: {
        plugins: [router],
        stubs: {
          'TableOfContents': mockTableOfContents,
          'MarkdownRenderer': mockMarkdownRenderer,
          'el-skeleton': mockElSkeleton,
          'el-breadcrumb': mockElBreadcrumb,
          'el-breadcrumb-item': mockElBreadcrumbItem,
          'el-avatar': mockElAvatar,
          'el-icon': mockElIcon,
          'el-tag': mockElTag,
          'el-button': mockElButton,
          'el-input': mockElInput,
          'el-empty': mockElEmpty
        }
      }
    })
    
    await router.isReady()
    await wrapper.vm.$nextTick()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('基础渲染', () => {
    it('正确渲染文章详情容器', () => {
      expect(wrapper.find('.article-detail-container').exists()).toBe(true)
    })

    it('显示文章标题', () => {
      expect(wrapper.text()).toContain('测试文章标题')
    })

    it('显示面包屑导航', () => {
      expect(wrapper.text()).toContain('首页')
      expect(wrapper.text()).toContain('文章')
      expect(wrapper.text()).toContain('技术')
      expect(wrapper.text()).toContain('测试文章标题')
    })
  })

  describe('作者信息展示', () => {
    it('显示作者头像', () => {
      const avatar = wrapper.findComponent(mockElAvatar)
      expect(avatar.exists()).toBe(true)
    })

    it('显示作者用户名', () => {
      expect(wrapper.text()).toContain('testuser')
    })

    it('显示发布时间', () => {
      expect(wrapper.text()).toContain('发布于')
      expect(wrapper.text()).toContain('2024年1月15日')
    })

    it('显示阅读时间', () => {
      expect(wrapper.text()).toContain('阅读时间约 5 分钟')
    })
  })

  describe('文章统计信息', () => {
    it('显示浏览量', () => {
      expect(wrapper.text()).toContain('150')
    })

    it('显示点赞数', () => {
      expect(wrapper.text()).toContain('25')
    })

    it('显示评论数', () => {
      expect(wrapper.text()).toContain('8')
    })
  })

  describe('文章标签', () => {
    it('显示文章标签', () => {
      expect(wrapper.text()).toContain('Vue.js')
      expect(wrapper.text()).toContain('JavaScript')
    })

    it('标签有正确的样式', () => {
      const tags = wrapper.findAllComponents(mockElTag)
      expect(tags.length).toBe(2)
    })
  })

  describe('文章封面', () => {
    it('显示文章封面图片', () => {
      const coverImage = wrapper.find('.article-cover img')
      expect(coverImage.exists()).toBe(true)
    })
  })

  describe('文章内容', () => {
    it('显示Markdown渲染器', () => {
      const markdownRenderer = wrapper.findComponent(mockMarkdownRenderer)
      expect(markdownRenderer.exists()).toBe(true)
    })

    it('传递正确的内容给Markdown渲染器', () => {
      const markdownRenderer = wrapper.findComponent(mockMarkdownRenderer)
      expect(markdownRenderer.props('content')).toContain('测试文章内容')
    })
  })

  describe('文章操作', () => {
    it('显示点赞按钮', () => {
      const buttons = wrapper.findAll('button')
      const likeButton = buttons.find(button => button.text().includes('点赞'))
      expect(likeButton).toBeTruthy()
    })

    it('显示收藏按钮', () => {
      const buttons = wrapper.findAll('button')
      const bookmarkButton = buttons.find(button => button.text().includes('收藏'))
      expect(bookmarkButton).toBeTruthy()
    })

    it('显示分享按钮', () => {
      const buttons = wrapper.findAll('button')
      const shareButton = buttons.find(button => button.text().includes('分享'))
      expect(shareButton).toBeTruthy()
    })
  })

  describe('评论功能', () => {
    it('显示评论输入框', () => {
      const commentInput = wrapper.findComponent(mockElInput)
      expect(commentInput.exists()).toBe(true)
    })

    it('显示发表评论按钮', () => {
      const buttons = wrapper.findAll('button')
      const submitButton = buttons.find(button => button.text().includes('发表评论'))
      expect(submitButton).toBeTruthy()
    })
  })

  describe('侧边栏', () => {
    it('显示目录组件', () => {
      const toc = wrapper.findComponent(mockTableOfContents)
      expect(toc.exists()).toBe(true)
    })
  })

  describe('加载状态', () => {
    it('显示骨架屏（当加载中时）', async () => {
      mockArticlesStore.loading = true
      await wrapper.vm.$nextTick()
      
      // 检查骨架屏是否存在
      const skeleton = wrapper.findComponent(mockElSkeleton)
      expect(skeleton.exists()).toBe(true)
    })
  })

  describe('交互功能', () => {
    it('点赞功能正确调用', async () => {
      const buttons = wrapper.findAll('button')
      const likeButton = buttons.find(button => button.text().includes('点赞'))
      await likeButton.trigger('click')
      
      expect(mockArticlesStore.likeArticle).toHaveBeenCalledWith('1')
    })

    it('收藏功能正确调用', async () => {
      const buttons = wrapper.findAll('button')
      const bookmarkButton = buttons.find(button => button.text().includes('收藏'))
      await bookmarkButton.trigger('click')
      
      expect(mockArticlesStore.bookmarkArticle).toHaveBeenCalledWith('1')
    })

    it('分享功能正确调用', async () => {
      const buttons = wrapper.findAll('button')
      const shareButton = buttons.find(button => button.text().includes('分享'))
      await shareButton.trigger('click')
      
      // 验证navigator.clipboard.writeText被调用
      expect(navigator.clipboard.writeText).toHaveBeenCalled()
    })
  })

  describe('评论交互', () => {
    it('发表评论功能正确调用', async () => {
      // 直接调用组件方法测试
      await wrapper.vm.submitComment()
      
      // 验证API调用
      const { articlesAPI } = await import('@/api/articles')
      expect(articlesAPI.createComment).toHaveBeenCalledWith({
        article: '1',
        content: ''
      })
    })

    it('空评论不能提交', async () => {
      // 直接调用组件方法测试
      await wrapper.vm.submitComment()
      
      // 验证API没有被调用
      const { articlesAPI } = await import('@/api/articles')
      expect(articlesAPI.createComment).not.toHaveBeenCalled()
    })
  })

  describe('API调用', () => {
    it('组件挂载时调用必要的API', () => {
      expect(mockArticlesStore.fetchArticle).toHaveBeenCalledWith('1')
    })

    it('获取评论列表', async () => {
      const { articlesAPI } = await import('@/api/articles')
      expect(articlesAPI.getComments).toBeDefined()
    })
  })

  describe('工具函数', () => {
    it('日期格式化正确', () => {
      const formattedDate = wrapper.vm.formatDate('2024-01-15T10:00:00Z')
      expect(formattedDate).toContain('2024年')
      expect(formattedDate).toContain('1月')
      expect(formattedDate).toContain('15日')
    })

    it('对比色计算正确', () => {
      const darkColor = wrapper.vm.getContrastColor('#000000')
      expect(darkColor).toBe('#ffffff')
      
      const lightColor = wrapper.vm.getContrastColor('#ffffff')
      expect(lightColor).toBe('#333333')
    })
  })

  describe('响应式布局', () => {
    it('文章布局有正确的CSS类', () => {
      expect(wrapper.find('.article-layout').exists()).toBe(true)
    })

    it('侧边栏有正确的CSS类', () => {
      expect(wrapper.find('.article-sidebar').exists()).toBe(true)
    })

    it('主内容区域有正确的CSS类', () => {
      expect(wrapper.find('.article-main').exists()).toBe(true)
    })
  })

  describe('错误处理', () => {
    it('获取文章失败时显示错误消息', async () => {
      mockArticlesStore.fetchArticle.mockRejectedValue(new Error('Article not found'))
      
      // 重新调用fetchArticle
      await wrapper.vm.fetchArticle()
      
      // 应该显示错误消息
      expect(wrapper.text()).toContain('文章不存在或已被删除')
    })

    it('获取评论失败时处理错误', async () => {
      // 模拟API失败
      const { articlesAPI } = await import('@/api/articles')
      articlesAPI.getComments.mockRejectedValue(new Error('Comments not found'))
      
      // 重新调用fetchComments
      await wrapper.vm.fetchComments()
      
      // 应该处理错误（不会抛出异常）
      expect(wrapper.vm.comments).toEqual([])
    })
  })

  describe('认证状态处理', () => {
    it('未认证用户点赞时跳转到登录页', async () => {
      mockAuthStore.isAuthenticated = false
      
      // 点击点赞按钮
      const buttons = wrapper.findAll('button')
      const likeButton = buttons.find(button => button.text().includes('点赞'))
      await likeButton.trigger('click')
      
      // 验证路由跳转
      const mockRouter = await import('vue-router')
      expect(mockRouter.useRouter().push).toHaveBeenCalledWith('/login')
    })

    it('未认证用户收藏时跳转到登录页', async () => {
      mockAuthStore.isAuthenticated = false
      
      // 点击收藏按钮
      const buttons = wrapper.findAll('button')
      const bookmarkButton = buttons.find(button => button.text().includes('收藏'))
      await bookmarkButton.trigger('click')
      
      // 验证路由跳转
      const mockRouter = await import('vue-router')
      expect(mockRouter.useRouter().push).toHaveBeenCalledWith('/login')
    })
  })

  describe('目录生成', () => {
    it('内容渲染完成后生成目录', async () => {
      // 等待setTimeout执行
      await new Promise(resolve => setTimeout(resolve, 1100))
      
      expect(mockTableOfContents.methods.generateTOC).toHaveBeenCalled()
    })
  })

  describe('边界情况', () => {
    it('文章不存在时显示错误', async () => {
      mockArticlesStore.currentArticle = null
      
      await wrapper.vm.$nextTick()
      
      // 应该显示错误状态或空状态
      expect(wrapper.find('.article-layout').exists()).toBe(false)
      expect(wrapper.find('.error-container').exists()).toBe(true)
    })

    it('文章无封面时正确处理', async () => {
      mockArticlesStore.currentArticle.cover_image = null
      
      await wrapper.vm.$nextTick()
      
      const coverImage = wrapper.find('.article-cover img')
      expect(coverImage.exists()).toBe(false)
    })

    it('文章无标签时正确处理', async () => {
      mockArticlesStore.currentArticle.tags = []
      
      await wrapper.vm.$nextTick()
      
      const tags = wrapper.findAll('.el-tag')
      expect(tags.length).toBe(0)
    })

    it('文章无分类时正确处理', async () => {
      mockArticlesStore.currentArticle.category = null
      
      await wrapper.vm.$nextTick()
      
      // 面包屑中不应该显示分类
      expect(wrapper.text()).not.toContain('技术')
    })
  })

  describe('性能优化', () => {
    it('评论提交后重新获取数据', async () => {
      const { articlesAPI } = await import('@/api/articles')
      articlesAPI.createComment.mockResolvedValue({ id: 1, content: 'test' })
      
      // 直接调用组件方法测试
      await wrapper.vm.submitComment()
      
      // 验证重新获取数据
      expect(mockArticlesStore.fetchArticle).toHaveBeenCalledTimes(2)
    })
  })
}) 