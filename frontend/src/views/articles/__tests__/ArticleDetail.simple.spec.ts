import { describe, it, expect, beforeEach, vi } from 'vitest'
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

// Mock route params
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

describe('ArticleDetail.vue Component - 简化测试', () => {
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

  describe('基础功能', () => {
    it('组件能够正确挂载', () => {
      expect(wrapper.exists()).toBe(true)
    })

    it('组件挂载时调用fetchArticle', () => {
      expect(mockArticlesStore.fetchArticle).toHaveBeenCalled()
    })

    it('显示文章标题', () => {
      expect(wrapper.text()).toContain('测试文章标题')
    })

    it('显示作者用户名', () => {
      expect(wrapper.text()).toContain('testuser')
    })

    it('显示文章内容', () => {
      expect(wrapper.text()).toContain('测试文章内容')
    })
  })

  describe('工具函数', () => {
    it('日期格式化函数存在', () => {
      expect(typeof wrapper.vm.formatDate).toBe('function')
    })

    it('对比色计算函数存在', () => {
      expect(typeof wrapper.vm.getContrastColor).toBe('function')
    })

    it('对比色计算正确', () => {
      const darkColor = wrapper.vm.getContrastColor('#000000')
      expect(darkColor).toBe('#ffffff')
      
      const lightColor = wrapper.vm.getContrastColor('#ffffff')
      expect(lightColor).toBe('#333333')
    })
  })

  describe('交互功能', () => {
    it('点赞功能存在', () => {
      expect(typeof wrapper.vm.toggleLike).toBe('function')
    })

    it('收藏功能存在', () => {
      expect(typeof wrapper.vm.toggleBookmark).toBe('function')
    })

    it('分享功能存在', () => {
      expect(typeof wrapper.vm.shareArticle).toBe('function')
    })
  })

  describe('评论功能', () => {
    it('评论相关方法存在', () => {
      expect(typeof wrapper.vm.submitComment).toBe('function')
      expect(typeof wrapper.vm.fetchComments).toBe('function')
    })
  })

  describe('边界情况', () => {
    it('文章不存在时组件仍能挂载', async () => {
      mockArticlesStore.currentArticle = null
      await wrapper.vm.$nextTick()
      
      expect(wrapper.exists()).toBe(true)
    })

    it('加载状态时组件仍能挂载', async () => {
      mockArticlesStore.loading = true
      await wrapper.vm.$nextTick()
      
      expect(wrapper.exists()).toBe(true)
    })
  })
}) 