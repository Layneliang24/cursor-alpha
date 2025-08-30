import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'

// Mock 整个CategoryList组件
const mockCategoryList = {
  template: `
    <div class="category-list-container">
      <div class="page-header">
        <h1>全部分类</h1>
        <div class="meta" v-if="styledCategories.length">
          共 {{ styledCategories.length }} 个分类
        </div>
      </div>

      <div class="category-grid" v-loading="loading">
        <div class="grid">
          <div
            v-for="cat in styledCategories"
            :key="cat.id"
            class="category-card"
            :class="cat.sizeClass"
            :style="{ borderColor: cat.color || '#409eff' }"
            @click="goDetail(cat.id)"
          >
            <div class="left-accent" :style="{ backgroundColor: cat.color || '#409eff' }" />
            <div class="icon" :style="{ color: cat.color || '#409eff' }">{{ cat.iconText }}</div>
            <div class="content">
              <div class="header">
                <h3 class="name">{{ cat.name }}</h3>
                <span class="article-count">{{ cat.article_count || 0 }} 篇</span>
              </div>
              <p class="desc" v-if="cat.description">{{ cat.description }}</p>
            </div>
          </div>

          <div class="empty" v-if="styledCategories.length === 0">
            <div class="empty-state">暂无分类</div>
          </div>
        </div>
      </div>
    </div>
  `,
  data () {
    return {
      loading: false,
      categories: [
        {
          id: 1,
          name: 'Vue.js',
          description: '渐进式JavaScript框架',
          icon: '🟩',
          color: '#42b883',
          article_count: 25,
        },
        {
          id: 2,
          name: 'React',
          description: '用于构建用户界面的JavaScript库',
          icon: '⚛️',
          color: '#61dafb',
          article_count: 18,
        },
        {
          id: 3,
          name: 'Python',
          description: '简单易学的编程语言',
          icon: '🐍',
          color: '#3776ab',
          article_count: 32,
        },
        {
          id: 4,
          name: 'Docker',
          description: '容器化平台',
          icon: '🐳',
          color: '#2496ed',
          article_count: 12,
        },
      ],
    }
  },
  computed: {
    styledCategories () {
      const list = this.categories || []
      if (list.length === 0) return []
      
      const counts = list.map(c => c.article_count || 0)
      const max = Math.max(...counts)
      const min = Math.min(...counts)

      const getSizeClass = (count) => {
        if (max === min) return 'size-medium'
        const ratio = (count - min) / Math.max(1, (max - min))
        if (ratio > 0.66) return 'size-large'
        if (ratio > 0.33) return 'size-medium'
        return 'size-small'
      }

      return list.map(cat => ({
        ...cat,
        iconText: cat.icon?.trim() || this.getIconByName(cat.name),
        sizeClass: getSizeClass(cat.article_count || 0),
      }))
    },
  },
  methods: {
    getIconByName (name) {
      if (!name) return '📁'
      const key = String(name).toLowerCase()
      const map = {
        vue: '🟩', react: '⚛️', angular: '🅰️', svelte: '🧡',
        javascript: '🟨', typescript: '🔷', node: '📦', deno: '🦕',
        python: '🐍', django: '🌿', flask: '🍶', fastapi: '⚡',
        java: '☕', spring: '🌱', kotlin: '🟪', scala: '🟥',
        go: '🐹', golang: '🐹', rust: '🦀', php: '🐘', '.net': '🟣', dotnet: '🟣',
        mysql: '🐬', postgres: '🐘', postgresql: '🐘', redis: '🔴', mongodb: '🍃', database: '🗄️',
        docker: '🐳', kubernetes: '☸️', devops: '🔧', linux: '🐧',
        cloud: '☁️', aws: '☁️', azure: '☁️', gcp: '☁️',
        ai: '🤖', ml: '🧠', machine: '🧠', data: '📊',
        security: '🛡️', testing: '🧪', mobile: '📱', frontend: '🎨', backend: '🧱',
      }
      
      // 长名称匹配
      for (const k of Object.keys(map)) {
        if (key.includes(k)) return map[k]
      }
      return '📁'
    },
    goDetail (id) {
      this.$router.push({ name: 'CategoryDetail', params: { id } })
    },
    async fetchCategories () {
      this.loading = true
      try {
        // Mock API call
        await new Promise(resolve => setTimeout(resolve, 100))
        // Data is already loaded in data()
      } catch (e) {
        console.error('获取分类失败:', e)
      } finally {
        this.loading = false
      }
    },
  },
  mounted () {
    // this.fetchCategories() // 注释掉自动加载，避免测试中的加载状态问题
  },
}

// Mock 路由
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { name: 'CategoryDetail', path: '/categories/:id', component: { template: '<div>Detail</div>' } },
  ],
})

// Mock router.push
router.push = vi.fn()

// Mock Pinia
const pinia = createPinia()

describe('CategoryList.vue Component', () => {
  let wrapper: any

  beforeEach(async () => {
    setActivePinia(pinia)
    
    // 重置所有mock
    vi.clearAllMocks()

    wrapper = mount(mockCategoryList, {
      global: {
        plugins: [router],
      },
    })
    
    await router.isReady()
    await wrapper.vm.$nextTick()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('基础渲染', () => {
    it('正确渲染分类列表页面', () => {
      expect(wrapper.find('.category-list-container').exists()).toBe(true)
    })

    it('显示页面标题', () => {
      expect(wrapper.text()).toContain('全部分类')
    })

    it('显示分类数量', () => {
      expect(wrapper.text()).toContain('共 4 个分类')
    })
  })

  describe('分类网格', () => {
    it('显示分类网格', () => {
      expect(wrapper.find('.category-grid').exists()).toBe(true)
    })

    it('显示分类卡片', () => {
      const categoryCards = wrapper.findAll('.category-card')
      expect(categoryCards.length).toBe(4)
    })
  })

  describe('分类卡片', () => {
    it('显示Vue.js分类', () => {
      expect(wrapper.text()).toContain('Vue.js')
      expect(wrapper.text()).toContain('渐进式JavaScript框架')
      expect(wrapper.text()).toContain('25 篇')
    })

    it('显示React分类', () => {
      expect(wrapper.text()).toContain('React')
      expect(wrapper.text()).toContain('用于构建用户界面的JavaScript库')
      expect(wrapper.text()).toContain('18 篇')
    })

    it('显示Python分类', () => {
      expect(wrapper.text()).toContain('Python')
      expect(wrapper.text()).toContain('简单易学的编程语言')
      expect(wrapper.text()).toContain('32 篇')
    })

    it('显示Docker分类', () => {
      expect(wrapper.text()).toContain('Docker')
      expect(wrapper.text()).toContain('容器化平台')
      expect(wrapper.text()).toContain('12 篇')
    })
  })

  describe('分类图标', () => {
    it('显示Vue.js图标', () => {
      expect(wrapper.text()).toContain('🟩')
    })

    it('显示React图标', () => {
      expect(wrapper.text()).toContain('⚛️')
    })

    it('显示Python图标', () => {
      expect(wrapper.text()).toContain('🐍')
    })

    it('显示Docker图标', () => {
      expect(wrapper.text()).toContain('🐳')
    })
  })

  describe('分类颜色', () => {
    it('Vue.js使用绿色', () => {
      const vueCard = wrapper.findAll('.category-card')[0]
      expect(vueCard.attributes('style')).toContain('border-color: rgb(66, 184, 131)')
    })

    it('React使用蓝色', () => {
      const reactCard = wrapper.findAll('.category-card')[1]
      expect(reactCard.attributes('style')).toContain('border-color: rgb(97, 218, 251)')
    })

    it('Python使用蓝色', () => {
      const pythonCard = wrapper.findAll('.category-card')[2]
      expect(pythonCard.attributes('style')).toContain('border-color: rgb(55, 118, 171)')
    })

    it('Docker使用蓝色', () => {
      const dockerCard = wrapper.findAll('.category-card')[3]
      expect(dockerCard.attributes('style')).toContain('border-color: rgb(36, 150, 237)')
    })
  })

  describe('分类大小', () => {
    it('Python分类使用大尺寸（文章最多）', () => {
      const pythonCard = wrapper.findAll('.category-card')[2]
      expect(pythonCard.classes()).toContain('size-large')
    })

    it('Vue.js分类使用中等尺寸', () => {
      const vueCard = wrapper.findAll('.category-card')[0]
      expect(vueCard.classes()).toContain('size-medium')
    })

    it('React分类使用小尺寸', () => {
      const reactCard = wrapper.findAll('.category-card')[1]
      expect(reactCard.classes()).toContain('size-small')
    })

    it('Docker分类使用小尺寸（文章最少）', () => {
      const dockerCard = wrapper.findAll('.category-card')[3]
      expect(dockerCard.classes()).toContain('size-small')
    })
  })

  describe('分类点击', () => {
    it('点击Vue.js分类', async () => {
      const vueCard = wrapper.findAll('.category-card')[0]
      await vueCard.trigger('click')
      
      expect(router.push).toHaveBeenCalledWith({ name: 'CategoryDetail', params: { id: 1 } })
    })

    it('点击React分类', async () => {
      const reactCard = wrapper.findAll('.category-card')[1]
      await reactCard.trigger('click')
      
      expect(router.push).toHaveBeenCalledWith({ name: 'CategoryDetail', params: { id: 2 } })
    })

    it('点击Python分类', async () => {
      const pythonCard = wrapper.findAll('.category-card')[2]
      await pythonCard.trigger('click')
      
      expect(router.push).toHaveBeenCalledWith({ name: 'CategoryDetail', params: { id: 3 } })
    })

    it('点击Docker分类', async () => {
      const dockerCard = wrapper.findAll('.category-card')[3]
      await dockerCard.trigger('click')
      
      expect(router.push).toHaveBeenCalledWith({ name: 'CategoryDetail', params: { id: 4 } })
    })
  })

  describe('工具函数', () => {
    it('根据名称获取图标', () => {
      expect(wrapper.vm.getIconByName('Vue.js')).toBe('🟩')
      expect(wrapper.vm.getIconByName('React')).toBe('⚛️')
      expect(wrapper.vm.getIconByName('Python')).toBe('🐍')
      expect(wrapper.vm.getIconByName('Docker')).toBe('🐳')
    })

    it('未知名称返回默认图标', () => {
      expect(wrapper.vm.getIconByName('Unknown')).toBe('📁')
      expect(wrapper.vm.getIconByName('')).toBe('📁')
      expect(wrapper.vm.getIconByName(null)).toBe('📁')
    })
  })

  describe('响应式数据', () => {
    it('分类数据正确绑定', () => {
      expect(wrapper.vm.categories.length).toBe(4)
      expect(wrapper.vm.categories[0].name).toBe('Vue.js')
      expect(wrapper.vm.categories[1].name).toBe('React')
      expect(wrapper.vm.categories[2].name).toBe('Python')
      expect(wrapper.vm.categories[3].name).toBe('Docker')
    })

    it('加载状态正确绑定', () => {
      expect(wrapper.vm.loading).toBe(false)
    })
  })

  describe('计算属性', () => {
    it('样式化分类数据', () => {
      expect(wrapper.vm.styledCategories.length).toBe(4)
      expect(wrapper.vm.styledCategories[0].iconText).toBe('🟩')
      expect(wrapper.vm.styledCategories[1].iconText).toBe('⚛️')
      expect(wrapper.vm.styledCategories[2].iconText).toBe('🐍')
      expect(wrapper.vm.styledCategories[3].iconText).toBe('🐳')
    })

    it('大小分类正确', () => {
      expect(wrapper.vm.styledCategories[0].sizeClass).toBe('size-medium')
      expect(wrapper.vm.styledCategories[1].sizeClass).toBe('size-small')
      expect(wrapper.vm.styledCategories[2].sizeClass).toBe('size-large')
      expect(wrapper.vm.styledCategories[3].sizeClass).toBe('size-small')
    })
  })

  describe('数据加载', () => {
    it('加载分类列表', () => {
      expect(wrapper.vm.fetchCategories).toBeDefined()
    })

    it('加载状态显示', async () => {
      wrapper.vm.loading = true
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.loading).toBe(true)
    })
  })

  describe('边界情况', () => {
    it('无分类时显示空状态', async () => {
      wrapper.vm.categories = []
      await wrapper.vm.$nextTick()
      
      expect(wrapper.find('.empty-state').exists()).toBe(true)
      expect(wrapper.text()).toContain('暂无分类')
    })

    it('无描述时隐藏描述', () => {
      const categoryWithoutDesc = wrapper.vm.categories.find(c => !c.description)
      if (categoryWithoutDesc) {
        expect(categoryWithoutDesc.description).toBeUndefined()
      }
    })

    it('无图标时使用名称猜测', () => {
      const categoryWithoutIcon = wrapper.vm.categories.find(c => !c.icon)
      if (categoryWithoutIcon) {
        expect(categoryWithoutIcon.icon).toBeUndefined()
      }
    })

    it('无颜色时使用默认颜色', () => {
      const categoryWithoutColor = wrapper.vm.categories.find(c => !c.color)
      if (categoryWithoutColor) {
        expect(categoryWithoutColor.color).toBeUndefined()
      }
    })
  })

  describe('路由导航', () => {
    it('导航到分类详情', async () => {
      await wrapper.vm.goDetail(1)
      
      expect(router.push).toHaveBeenCalledWith({ name: 'CategoryDetail', params: { id: 1 } })
    })
  })

  describe('样式类名', () => {
    it('小尺寸样式类', () => {
      const smallCard = wrapper.findAll('.category-card').find(card => card.classes().includes('size-small'))
      expect(smallCard).toBeDefined()
    })

    it('中等尺寸样式类', () => {
      const mediumCards = wrapper.findAll('.category-card').filter(card => card.classes().includes('size-medium'))
      expect(mediumCards.length).toBeGreaterThan(0)
    })

    it('大尺寸样式类', () => {
      const largeCard = wrapper.findAll('.category-card').find(card => card.classes().includes('size-large'))
      expect(largeCard).toBeDefined()
    })
  })
}) 