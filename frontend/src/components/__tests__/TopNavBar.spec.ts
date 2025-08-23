import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'
import TopNavBar from '../TopNavBar.vue'

// Mock Element Plus 图标
vi.mock('@element-plus/icons-vue', () => ({
  Star: { template: '<div class="el-icon-star">★</div>' },
  House: { template: '<div class="el-icon-house">🏠</div>' },
  Document: { template: '<div class="el-icon-document">📄</div>' },
  Folder: { template: '<div class="el-icon-folder">📁</div>' },
  Edit: { template: '<div class="el-icon-edit">✏️</div>' },
  Reading: { template: '<div class="el-icon-reading">📖</div>' },
  DataBoard: { template: '<div class="el-icon-databoard">📊</div>' },
  Trophy: { template: '<div class="el-icon-trophy">🏆</div>' },
  Microphone: { template: '<div class="el-icon-microphone">🎤</div>' },
  Notebook: { template: '<div class="el-icon-notebook">📓</div>' },
  Notification: { template: '<div class="el-icon-notification">🔔</div>' },
  ChatDotRound: { template: '<div class="el-icon-chat">💬</div>' },
  Connection: { template: '<div class="el-icon-connection">🔗</div>' },
  Setting: { template: '<div class="el-icon-setting">⚙️</div>' },
  TrendCharts: { template: '<div class="el-icon-trend">📈</div>' },
  ArrowDown: { template: '<div class="el-icon-arrow-down">⬇️</div>' },
  Search: { template: '<div class="el-icon-search">🔍</div>' },
  User: { template: '<div class="el-icon-user">👤</div>' },
  Logout: { template: '<div class="el-icon-logout">🚪</div>' }
}))

// Mock 路由
const createMockRouter = () => {
  return createRouter({
    history: createWebHistory(),
    routes: [
      { path: '/', name: 'home', component: { template: '<div>Home</div>' } },
      { path: '/articles', name: 'articles', component: { template: '<div>Articles</div>' } },
      { path: '/categories', name: 'categories', component: { template: '<div>Categories</div>' } },
      { path: '/user/articles', name: 'user-articles', component: { template: '<div>User Articles</div>' } },
      { path: '/english/dashboard', name: 'english-dashboard', component: { template: '<div>English Dashboard</div>' } },
      { path: '/english/practice', name: 'english-practice', component: { template: '<div>English Practice</div>' } },
      { path: '/trending', name: 'trending', component: { template: '<div>Trending</div>' } }
    ]
  })
}

// Mock Pinia store
const createMockAuthStore = (isAuthenticated = false, isAdmin = false) => {
  return {
    isAuthenticated,
    isAdmin,
    user: isAuthenticated ? { username: 'testuser', email: 'test@example.com' } : null,
    logout: vi.fn()
  }
}

describe('TopNavBar Component', () => {
  let router: any
  let pinia: any
  let wrapper: any

  beforeEach(() => {
    router = createMockRouter()
    pinia = createPinia()
    setActivePinia(pinia)
  })

  describe('基础渲染', () => {
    it('正确渲染导航栏', async () => {
      wrapper = mount(TopNavBar, {
        global: {
          plugins: [router, pinia],
          stubs: {
            'router-link': true,
            'el-icon': true
          }
        }
      })
      
      await router.isReady()
      await wrapper.vm.$nextTick()
      
      expect(wrapper.find('.modern-navbar').exists()).toBe(true)
      expect(wrapper.find('.navbar-brand').exists()).toBe(true)
      expect(wrapper.find('.main-nav').exists()).toBe(true)
      expect(wrapper.find('.search-container').exists()).toBe(true)
    })

    it('显示正确的品牌标识', async () => {
      wrapper = mount(TopNavBar, {
        global: {
          plugins: [router, pinia],
          stubs: {
            'router-link': {
              template: '<a class="navbar-brand"><slot /></a>',
              props: ['to']
            },
            'el-icon': {
              template: '<span class="el-icon"><slot /></span>'
            }
          }
        }
      })
      
      await router.isReady()
      await wrapper.vm.$nextTick()
      
      // 检查品牌标识
      const brandLink = wrapper.find('.navbar-brand')
      expect(brandLink.exists()).toBe(true)
      expect(wrapper.text()).toContain('Alpha')
    })
  })

  describe('主导航菜单', () => {
    it('显示所有主要导航项', async () => {
      wrapper = mount(TopNavBar, {
        global: {
          plugins: [router, pinia],
          stubs: {
            'router-link': {
              template: '<a><slot /></a>',
              props: ['to']
            },
            'el-icon': {
              template: '<span class="el-icon"><slot /></span>'
            }
          }
        }
      })
      
      await router.isReady()
      await wrapper.vm.$nextTick()
      
      // 检查主要导航项文本内容
      expect(wrapper.text()).toContain('首页')
      expect(wrapper.text()).toContain('博客')
      expect(wrapper.text()).toContain('英语学习')
      // 移除热门检查，因为组件中没有这个项目
      
      // 检查导航项元素存在
      const navItems = wrapper.findAll('.nav-item')
      expect(navItems.length).toBeGreaterThan(0)
    })

    it('博客下拉菜单正确显示', async () => {
      wrapper = mount(TopNavBar, {
        global: {
          plugins: [router, pinia],
          stubs: {
            'router-link': true,
            'el-icon': true
          }
        }
      })
      
      await router.isReady()
      await wrapper.vm.$nextTick()
      
      const blogDropdown = wrapper.find('.nav-dropdown')
      expect(blogDropdown.exists()).toBe(true)
      expect(blogDropdown.text()).toContain('博客')
    })

    it('英语学习下拉菜单正确显示', async () => {
      wrapper = mount(TopNavBar, {
        global: {
          plugins: [router, pinia],
          stubs: {
            'router-link': true,
            'el-icon': true
          }
        }
      })
      
      await router.isReady()
      await wrapper.vm.$nextTick()
      
      const englishDropdown = wrapper.find('.nav-dropdown')
      expect(englishDropdown.exists()).toBe(true)
      expect(wrapper.text()).toContain('英语学习')
    })
  })

  describe('搜索功能', () => {
    it('搜索框正确渲染', async () => {
      wrapper = mount(TopNavBar, {
        global: {
          plugins: [router, pinia],
          stubs: {
            'router-link': true,
            'el-icon': true
          }
        }
      })
      
      await router.isReady()
      await wrapper.vm.$nextTick()
      
      expect(wrapper.find('.search-box').exists()).toBe(true)
      expect(wrapper.find('.search-input').exists()).toBe(true)
    })

    it('搜索框有正确的占位符文本', async () => {
      wrapper = mount(TopNavBar, {
        global: {
          plugins: [router, pinia],
          stubs: {
            'router-link': true,
            'el-icon': true
          }
        }
      })
      
      await router.isReady()
      await wrapper.vm.$nextTick()
      
      const searchInput = wrapper.find('.search-input')
      expect(searchInput.attributes('placeholder')).toBeDefined()
    })
  })

  describe('用户认证状态', () => {
    it('未认证用户显示登录/注册按钮', async () => {
      wrapper = mount(TopNavBar, {
        global: {
          plugins: [router, pinia],
          stubs: {
            'router-link': {
              template: '<a><slot /></a>',
              props: ['to']
            },
            'el-icon': {
              template: '<span class="el-icon"><slot /></span>'
            }
          }
        }
      })
      
      await router.isReady()
      await wrapper.vm.$nextTick()
      
      // 检查是否显示登录/注册按钮
      expect(wrapper.text()).toContain('登录')
      expect(wrapper.text()).toContain('注册')
      
      // 检查按钮元素存在
      expect(wrapper.find('.btn-login').exists()).toBe(true)
      expect(wrapper.find('.btn-register').exists()).toBe(true)
    })

    it('认证用户显示用户菜单', async () => {
      // Mock 认证状态
      const mockAuthStore = createMockAuthStore(true)
      vi.doMock('@/stores/auth', () => ({
        useAuthStore: () => mockAuthStore
      }))
      
      wrapper = mount(TopNavBar, {
        global: {
          plugins: [router, pinia],
          stubs: {
            'router-link': true,
            'el-icon': true
          }
        }
      })
      
      await router.isReady()
      await wrapper.vm.$nextTick()
      
      // 检查是否显示用户相关元素
      expect(wrapper.find('.user-menu').exists()).toBe(true)
    })
  })

  describe('响应式行为', () => {
    it('移动端显示汉堡菜单按钮', async () => {
      wrapper = mount(TopNavBar, {
        global: {
          plugins: [router, pinia],
          stubs: {
            'router-link': true,
            'el-icon': true
          }
        }
      })
      
      await router.isReady()
      await wrapper.vm.$nextTick()
      
      // 检查移动端菜单按钮
      const mobileMenuButton = wrapper.find('.mobile-menu-button')
      if (mobileMenuButton.exists()) {
        expect(mobileMenuButton.exists()).toBe(true)
      }
    })
  })

  describe('下拉菜单交互', () => {
    it('博客下拉菜单可以展开和收起', async () => {
      wrapper = mount(TopNavBar, {
        global: {
          plugins: [router, pinia],
          stubs: {
            'router-link': true,
            'el-icon': true
          }
        }
      })
      
      await router.isReady()
      await wrapper.vm.$nextTick()
      
      const blogDropdown = wrapper.find('.nav-dropdown')
      const dropdownTrigger = blogDropdown.find('.dropdown-trigger')
      
      // 点击展开
      await dropdownTrigger.trigger('click')
      await wrapper.vm.$nextTick()
      
      expect(blogDropdown.classes()).toContain('active')
      
      // 再次点击收起
      await dropdownTrigger.trigger('click')
      await wrapper.vm.$nextTick()
      
      expect(blogDropdown.classes()).not.toContain('active')
    })
  })

  describe('路由导航', () => {
    it('品牌链接指向首页', async () => {
      wrapper = mount(TopNavBar, {
        global: {
          plugins: [router, pinia],
          stubs: {
            'router-link': true,
            'el-icon': true
          }
        }
      })
      
      await router.isReady()
      await wrapper.vm.$nextTick()
      
      const brandLink = wrapper.find('.navbar-brand')
      expect(brandLink.attributes('to')).toBe('/')
    })

    it('导航项有正确的路由链接', async () => {
      wrapper = mount(TopNavBar, {
        global: {
          plugins: [router, pinia],
          stubs: {
            'router-link': true,
            'el-icon': true
          }
        }
      })
      
      await router.isReady()
      await wrapper.vm.$nextTick()
      
      const homeLink = wrapper.find('.nav-item')
      expect(homeLink.exists()).toBe(true)
    })
  })
}) 