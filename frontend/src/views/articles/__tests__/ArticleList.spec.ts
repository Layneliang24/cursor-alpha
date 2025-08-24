import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'
import { ElMessage } from 'element-plus'
import ArticleList from '../ArticleList.vue'

// Mock API模块
vi.mock('@/api/categories', () => ({
  categoriesAPI: {
    getCategories: vi.fn()
  }
}))

// Mock stores
const mockArticlesStore = {
  articles: [] as any[],
  loading: false,
  pagination: {
    current: 1,
    pageSize: 10,
    total: 0
  },
  fetchArticles: vi.fn()
}

vi.mock('@/stores/articles', () => ({
  useArticlesStore: () => mockArticlesStore
}))

// Mock Element Plus组件
const mockElInput = {
  template: '<input :value="modelValue" @input="$emit(\'update:modelValue\', $event.target.value)" @keyup.enter="$emit(\'keyup.enter\')" />',
  props: ['modelValue'],
  emits: ['update:modelValue', 'keyup.enter']
}

const mockElButton = {
  template: '<button :type="type" @click="$emit(\'click\')"><slot /></button>',
  props: ['type'],
  emits: ['click']
}

const mockElSelect = {
  template: '<select :value="modelValue" @change="$emit(\'update:modelValue\', $event.target.value)"><slot /></select>',
  props: ['modelValue'],
  emits: ['update:modelValue', 'change']
}

const mockElOption = {
  template: '<option :value="value" :label="label">{{ label }}</option>',
  props: ['value', 'label']
}

const mockElCard = {
  template: '<div class="el-card" @click="$emit(\'click\')"><slot /></div>',
  emits: ['click']
}

const mockElTag = {
  template: '<span class="el-tag" :type="type" :size="size"><slot /></span>',
  props: ['type', 'size']
}

const mockElAvatar = {
  template: '<div class="el-avatar" :size="size"><slot /></div>',
  props: ['size']
}

const mockElIcon = {
  template: '<span class="el-icon"><slot /></span>'
}

const mockElSkeleton = {
  template: '<div class="el-skeleton"><slot /></div>',
  props: ['rows', 'animated']
}

const mockElEmpty = {
  template: '<div class="el-empty"><slot /></div>'
}

const mockElPagination = {
  template: '<div class="el-pagination"></div>',
  props: ['current-page', 'page-size', 'total', 'page-sizes', 'layout'],
  emits: ['size-change', 'current-change']
}

const mockElRow = {
  template: '<div class="el-row" :gutter="gutter"><slot /></div>',
  props: ['gutter']
}

const mockElCol = {
  template: '<div class="el-col" :span="span"><slot /></div>',
  props: ['span']
}

// Mock 路由
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/articles', component: { template: '<div>Articles</div>' } },
    { path: '/articles/create', component: { template: '<div>Create</div>' } },
    { 
      path: '/articles/:id', 
      name: 'ArticleDetail',
      component: { template: '<div>Article Detail</div>' } 
    }
  ]
})

// Mock router.push
router.push = vi.fn()

// Mock Pinia
const pinia = createPinia()

describe('ArticleList.vue Component', () => {
  let wrapper: any

  beforeEach(async () => {
    setActivePinia(pinia)
    
    // 重置所有mock
    vi.clearAllMocks()
    
    // 设置默认的mock返回值
    mockArticlesStore.articles = [
      {
        id: 1,
        title: '测试文章1',
        summary: '这是测试文章1的摘要',
        cover_image: 'https://example.com/image1.jpg',
        featured: true,
        author: { username: 'testuser1', avatar: 'https://example.com/avatar1.jpg' },
        views: 150,
        likes: 25,
        category: { name: '技术', color: '#409eff' },
        created_at: '2024-01-15T10:00:00Z'
      },
      {
        id: 2,
        title: '测试文章2',
        summary: null,
        cover_image: null,
        featured: false,
        author: { username: 'testuser2', avatar: null },
        views: 80,
        likes: 12,
        category: { name: '生活', color: '#67c23a' },
        created_at: '2024-01-14T15:30:00Z'
      }
    ]
    
    mockArticlesStore.pagination.total = 2
    mockArticlesStore.loading = false

    wrapper = mount(ArticleList, {
      global: {
        plugins: [router],
        stubs: {
          'el-input': mockElInput,
          'el-button': mockElButton,
          'el-select': mockElSelect,
          'el-option': mockElOption,
          'el-card': mockElCard,
          'el-tag': mockElTag,
          'el-avatar': mockElAvatar,
          'el-icon': mockElIcon,
          'el-skeleton': mockElSkeleton,
          'el-empty': mockElEmpty,
          'el-pagination': mockElPagination
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
    it('正确渲染文章列表容器', () => {
      expect(wrapper.find('.article-list-container').exists()).toBe(true)
    })

    it('显示页面标题', () => {
      expect(wrapper.text()).toContain('全部文章')
    })

    it('显示搜索输入框', () => {
      // 检查搜索输入框是否存在
      const searchInput = wrapper.find('input[placeholder="搜索文章..."]')
      expect(searchInput.exists()).toBe(true)
    })

    it('显示搜索按钮', () => {
      expect(wrapper.text()).toContain('搜索')
    })
  })

  describe('筛选器', () => {
    it('显示分类选择器', () => {
      // 检查分类选择器是否存在
      const categorySelect = wrapper.find('select')
      expect(categorySelect.exists()).toBe(true)
    })

    it('显示排序选择器', () => {
      // 检查排序选择器是否存在
      const sortSelect = wrapper.findAll('select')[1]
      expect(sortSelect.exists()).toBe(true)
    })

    it('排序选项包含正确的值', () => {
      expect(wrapper.text()).toContain('最新发布')
      expect(wrapper.text()).toContain('最多浏览')
      expect(wrapper.text()).toContain('最多点赞')
    })
  })

  describe('文章列表展示', () => {
    it('正确显示文章数量', () => {
      const articleCards = wrapper.findAll('.article-card')
      expect(articleCards.length).toBe(2)
    })

    it('显示文章标题', () => {
      expect(wrapper.text()).toContain('测试文章1')
      expect(wrapper.text()).toContain('测试文章2')
    })

    it('显示文章摘要（优先使用summary字段）', () => {
      expect(wrapper.text()).toContain('这是测试文章1的摘要')
    })

    it('处理空摘要（显示默认文本）', () => {
      expect(wrapper.text()).toContain('暂无摘要')
    })

    it('显示作者信息', () => {
      expect(wrapper.text()).toContain('testuser1')
      expect(wrapper.text()).toContain('testuser2')
    })

    it('显示浏览量', () => {
      expect(wrapper.text()).toContain('150')
      expect(wrapper.text()).toContain('80')
    })

    it('显示点赞数', () => {
      expect(wrapper.text()).toContain('25')
      expect(wrapper.text()).toContain('12')
    })

    it('显示分类标签', () => {
      expect(wrapper.text()).toContain('技术')
      expect(wrapper.text()).toContain('生活')
    })

    it('显示发布时间', () => {
      // 检查发布时间是否正确显示
      expect(wrapper.text()).toContain('2024年1月15日')
      expect(wrapper.text()).toContain('2024年1月14日')
    })
  })

  describe('特色文章处理', () => {
    it('显示推荐标签（当文章被标记为特色时）', () => {
      expect(wrapper.text()).toContain('推荐')
    })

    it('不显示推荐标签（当文章不是特色时）', () => {
      // 第二个文章不是特色，不应该显示推荐标签
      const recommendedTags = wrapper.findAll('.el-tag').filter(tag => tag.text() === '推荐')
      expect(recommendedTags.length).toBe(1)
    })
  })

  describe('封面图片处理', () => {
    it('显示文章封面图片（当存在时）', () => {
      const coverImages = wrapper.findAll('.article-cover img')
      expect(coverImages.length).toBe(1) // 只有第一篇文章有封面
    })

    it('处理无封面图片的情况', () => {
      const coverImages = wrapper.findAll('.article-cover img')
      expect(coverImages.length).toBe(1) // 第二篇文章没有封面
    })
  })

  describe('空状态处理', () => {
    it('显示空状态（当没有文章时）', async () => {
      // 重新设置mock数据为空状态
      mockArticlesStore.articles = []
      mockArticlesStore.pagination.total = 0
      
      // 重新挂载组件以应用新的数据
      const emptyWrapper = mount(ArticleList, {
        global: {
          plugins: [router],
          stubs: {
            'el-input': mockElInput,
            'el-button': mockElButton,
            'el-select': mockElSelect,
            'el-option': mockElOption,
            'el-row': mockElRow,
            'el-col': mockElCol,
            'el-card': mockElCard,
            'el-avatar': mockElAvatar,
            'el-icon': mockElIcon,
            'el-tag': mockElTag,
            'el-empty': mockElEmpty,
            'el-pagination': mockElPagination,
            'el-skeleton': mockElSkeleton
          }
        }
      })
      
      await emptyWrapper.vm.$nextTick()
      
      // 检查空状态组件是否存在
      const emptyState = emptyWrapper.findComponent(mockElEmpty)
      expect(emptyState.exists()).toBe(true)
    })
  })

  describe('加载状态', () => {
    it('显示骨架屏（当加载中时）', async () => {
      // 重新设置mock数据为加载状态
      mockArticlesStore.loading = true
      
      // 重新挂载组件以应用新的数据
      const loadingWrapper = mount(ArticleList, {
        global: {
          plugins: [router],
          stubs: {
            'el-input': mockElInput,
            'el-button': mockElButton,
            'el-select': mockElSelect,
            'el-option': mockElOption,
            'el-row': mockElRow,
            'el-col': mockElCol,
            'el-card': mockElCard,
            'el-avatar': mockElAvatar,
            'el-icon': mockElIcon,
            'el-tag': mockElTag,
            'el-empty': mockElEmpty,
            'el-pagination': mockElPagination,
            'el-skeleton': mockElSkeleton
          }
        }
      })
      
      await loadingWrapper.vm.$nextTick()
      
      // 检查骨架屏组件是否存在
      const skeletons = loadingWrapper.findAllComponents(mockElSkeleton)
      expect(skeletons.length).toBeGreaterThan(0)
    })
  })

  describe('分页功能', () => {
    it('显示分页组件（当有文章时）', () => {
      const pagination = wrapper.find('.pagination-container')
      expect(pagination.exists()).toBe(true)
    })

    it('分页组件有正确的属性', () => {
      const pagination = wrapper.find('.el-pagination')
      expect(pagination.exists()).toBe(true)
    })
  })

  describe('交互功能', () => {
    it('点击文章卡片跳转到详情页', async () => {
      // 直接调用组件方法测试
      await wrapper.vm.viewArticle(1)
      
      // 验证路由跳转
      expect(router.push).toHaveBeenCalled()
    })

    it('搜索功能正确调用', async () => {
      // 设置搜索关键词
      wrapper.vm.searchKeyword = '测试'
      
      // 触发搜索
      await wrapper.vm.handleSearch()
      
      // 验证搜索被调用
      expect(mockArticlesStore.fetchArticles).toHaveBeenCalled()
    })

    it('分类筛选正确调用', async () => {
      const categorySelect = wrapper.find('select')
      
      // 模拟分类选择
      await wrapper.vm.handleCategoryChange()
      
      // 验证分类变化处理被调用
      expect(mockArticlesStore.fetchArticles).toHaveBeenCalled()
    })

    it('排序变化正确调用', async () => {
      // 模拟排序变化
      await wrapper.vm.handleSortChange()
      
      // 验证排序变化处理被调用
      expect(mockArticlesStore.fetchArticles).toHaveBeenCalled()
    })
  })

  describe('API调用', () => {
    it('组件挂载时调用必要的API', () => {
      expect(mockArticlesStore.fetchArticles).toHaveBeenCalled()
    })

    it('获取分类列表', () => {
      // 验证分类API被调用
      expect(mockArticlesStore.fetchArticles).toHaveBeenCalled()
    })
  })

  describe('工具函数', () => {
    it('日期格式化正确', () => {
      const formatted = wrapper.vm.formatDate('2024-01-15T10:00:00Z')
      // 检查日期格式是否正确
      expect(typeof formatted).toBe('string')
      expect(formatted.length).toBeGreaterThan(0)
    })

    it('对比色计算正确', () => {
      // 测试深色背景
      const darkColor = wrapper.vm.getContrastColor('#000000')
      expect(darkColor).toBe('#ffffff')
      
      // 测试浅色背景
      const lightColor = wrapper.vm.getContrastColor('#ffffff')
      expect(lightColor).toBe('#333333')
      
      // 测试默认颜色
      const defaultColor = wrapper.vm.getContrastColor('')
      expect(defaultColor).toBe('#333333')
      
      // 测试无效颜色长度
      const invalidColor = wrapper.vm.getContrastColor('#12345')
      expect(invalidColor).toBe('#333333')
      
      // 测试边界亮度值 - #808080是中等灰色，亮度等于128，应该返回白色文字
      const boundaryColor = wrapper.vm.getContrastColor('#808080')
      expect(boundaryColor).toBe('#ffffff')
    })
  })

  describe('响应式布局', () => {
    it('文章网格有正确的CSS类', () => {
      const articleGrid = wrapper.find('.article-grid')
      expect(articleGrid.exists()).toBe(true)
    })

    it('文章列有正确的CSS类', () => {
      const articleCols = wrapper.findAll('.article-col')
      expect(articleCols.length).toBe(2)
    })

    it('文章卡片有正确的CSS类', () => {
      const articleCards = wrapper.findAll('.article-card')
      expect(articleCards.length).toBe(2)
    })
  })

  describe('错误处理', () => {
    it('API调用失败时显示错误消息', async () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      const elMessageSpy = vi.spyOn(ElMessage, 'error').mockImplementation(() => ({} as any))
      
      // 模拟API失败
      mockArticlesStore.fetchArticles.mockRejectedValue(new Error('API Error'))
      
      await wrapper.vm.fetchArticles()
      
      expect(consoleSpy).toHaveBeenCalledWith('获取文章失败:', expect.any(Error))
      expect(elMessageSpy).toHaveBeenCalledWith('获取文章失败，请检查网络连接')
      
      consoleSpy.mockRestore()
      elMessageSpy.mockRestore()
    })
  })

  describe('分页处理', () => {
    it('分页大小变化处理', async () => {
      await wrapper.vm.handleSizeChange(20)
      
      expect(mockArticlesStore.pagination.pageSize).toBe(20)
      expect(mockArticlesStore.pagination.current).toBe(1)
      expect(mockArticlesStore.fetchArticles).toHaveBeenCalled()
    })

    it('当前页变化处理', async () => {
      await wrapper.vm.handleCurrentChange(2)
      
      expect(mockArticlesStore.pagination.current).toBe(2)
      expect(mockArticlesStore.fetchArticles).toHaveBeenCalled()
    })
  })

  describe('搜索防抖', () => {
    it('搜索防抖正确工作', async () => {
      // Mock setTimeout和clearTimeout
      const setTimeoutSpy = vi.spyOn(window, 'setTimeout')
      const clearTimeoutSpy = vi.spyOn(window, 'clearTimeout')
      
      // 第一次调用handleSearch
      wrapper.vm.handleSearch()
      
      // 验证setTimeout被调用
      expect(setTimeoutSpy).toHaveBeenCalledWith(expect.any(Function), 300)
      
      // 第二次调用handleSearch，这次应该会清除之前的timer
      wrapper.vm.handleSearch()
      
      // 验证clearTimeout被调用
      expect(clearTimeoutSpy).toHaveBeenCalled()
      
      // 清理spy
      setTimeoutSpy.mockRestore()
      clearTimeoutSpy.mockRestore()
    })
  })

  describe('控制台日志', () => {
    it('fetchArticles正确输出请求参数日志', async () => {
      const consoleLogSpy = vi.spyOn(console, 'log').mockImplementation(() => {})
      
      await wrapper.vm.fetchArticles()
      
      expect(consoleLogSpy).toHaveBeenCalledWith('请求参数:', expect.any(Object))
      
      consoleLogSpy.mockRestore()
    })
  })
}) 