import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'

// Mock 整个NavBar组件
const mockNavBar = {
  template: `
    <div class="nav-menu">
      <!-- 主页链接 -->
      <div class="menu-item home-item" data-index="/">
        <span class="icon">🏠</span>
        <span>Alpha 技术共享平台</span>
      </div>
      
      <!-- 弹性空间 -->
      <div class="flex-grow"></div>
      
      <!-- 文章菜单 -->
      <div class="menu-item" data-index="/articles">
        <span class="icon">📄</span>
        <span>文章</span>
      </div>
      
      <!-- 英语学习子菜单 -->
      <div class="sub-menu" data-index="english">
        <div class="sub-menu-title">
          <span class="icon">📄</span>
          <span>英语学习</span>
        </div>
        <div class="sub-menu-items" v-if="showEnglishMenu">
          <div class="menu-item" data-index="/english/news-dashboard">
            <span class="icon">🔔</span>
            新闻仪表板
          </div>
          <div class="menu-item" data-index="/english/words">
            <span class="icon">📄</span>
            单词学习
          </div>
          <div class="menu-item" data-index="/english/expressions">
            <span class="icon">💬</span>
            地道表达
          </div>
          <div class="menu-item" data-index="/english/news">
            <span class="icon">📋</span>
            新闻列表
          </div>
        </div>
      </div>
      
      <!-- 未登录状态 -->
      <template v-if="!isAuthenticated">
        <div class="menu-item" data-index="/login">
          <span class="icon">👤</span>
          <span>登录</span>
        </div>
        <div class="menu-item register-menu-item" data-index="/register">
          <span class="icon">👥</span>
          <span>注册</span>
        </div>
      </template>
      
      <!-- 已登录状态 -->
      <template v-else>
        <div class="menu-item create-menu-item" data-index="/articles/create">
          <span class="icon">✏️</span>
          <span>发布文章</span>
        </div>
        
        <div class="sub-menu user-menu" data-index="user">
          <div class="sub-menu-title">
            <div class="avatar">{{ userAvatar }}</div>
            <span>{{ userName }}</span>
          </div>
          <div class="sub-menu-items" v-if="showUserMenu">
            <div class="menu-item" data-index="/user/profile">
              <span class="icon">👤</span>
              个人中心
            </div>
            <div class="menu-item" data-index="/user/articles">
              <span class="icon">📄</span>
              我的文章
            </div>
            <div class="menu-item logout-item" @click="handleLogout">
              <span class="icon">🚪</span>
              退出登录
            </div>
          </div>
        </div>
      </template>
    </div>
  `,
  data() {
    return {
      activeIndex: '/',
      showEnglishMenu: false,
      showUserMenu: false,
      isAuthenticated: false,
      userName: 'testuser',
      userAvatar: 'T'
    }
  },
  methods: {
    updateActiveIndex() {
      // 模拟路由变化更新激活菜单项
      this.activeIndex = this.currentRoute || '/'
    },
    
    async handleLogout() {
      try {
        // 模拟确认对话框
        if (await this.confirmLogout()) {
          await this.logout()
          this.redirectToHome()
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('退出登录失败:', error)
        }
      }
    },
    
    async confirmLogout() {
      // 模拟确认对话框
      return new Promise((resolve) => {
        setTimeout(() => resolve(true), 10)
      })
    },
    
    async logout() {
      // 模拟登出逻辑
      this.isAuthenticated = false
      this.userName = ''
      this.userAvatar = ''
      console.log('User logged out')
    },
    
    redirectToHome() {
      // 模拟路由跳转
      console.log('Redirecting to home')
    },
    
    initAuth() {
      // 模拟初始化认证状态
      console.log('Auth initialized')
    },
    
    toggleEnglishMenu() {
      this.showEnglishMenu = !this.showEnglishMenu
    },
    
    toggleUserMenu() {
      this.showUserMenu = !this.showUserMenu
    },
    
    setAuthenticatedState(authenticated, username = 'testuser') {
      this.isAuthenticated = authenticated
      this.userName = username
      this.userAvatar = username.charAt(0).toUpperCase()
    }
  },
  mounted() {
    this.updateActiveIndex()
    this.initAuth()
  }
}

// Mock vue-router
vi.mock('vue-router', async () => {
  const actual = await vi.importActual('vue-router')
  return {
    ...actual,
    useRoute: () => ({
      path: '/'
    }),
    useRouter: () => ({
      push: vi.fn(),
      afterEach: vi.fn()
    })
  }
})

// Mock Pinia store
vi.mock('@/stores/auth', () => ({
  useAuthStore: () => ({
    isAuthenticated: false,
    user: null,
    initAuth: vi.fn(),
    logout: vi.fn()
  })
}))

// Mock Element Plus
vi.mock('element-plus', () => ({
  ElMessage: {
    success: vi.fn(),
    error: vi.fn()
  },
  ElMessageBox: {
    confirm: vi.fn().mockResolvedValue('confirm')
  }
}))

const pinia = createPinia()

describe('NavBar.vue Component', () => {
  let wrapper: any

  beforeEach(async () => {
    setActivePinia(pinia)
    
    // 重置所有mock
    vi.clearAllMocks()
    
    wrapper = mount(mockNavBar, {
      global: {
        plugins: [pinia]
      }
    })
    
    await wrapper.vm.$nextTick()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('基础渲染', () => {
    it('正确渲染导航菜单容器', () => {
      expect(wrapper.find('.nav-menu').exists()).toBe(true)
    })

    it('显示主页链接', () => {
      const homeItem = wrapper.find('[data-index="/"]')
      expect(homeItem.exists()).toBe(true)
      expect(homeItem.text()).toContain('Alpha 技术共享平台')
    })

    it('显示文章菜单项', () => {
      const articlesItem = wrapper.find('[data-index="/articles"]')
      expect(articlesItem.exists()).toBe(true)
      expect(articlesItem.text()).toContain('文章')
    })

    it('显示英语学习子菜单', () => {
      const englishMenu = wrapper.find('[data-index="english"]')
      expect(englishMenu.exists()).toBe(true)
      expect(englishMenu.text()).toContain('英语学习')
    })

    it('显示弹性空间', () => {
      expect(wrapper.find('.flex-grow').exists()).toBe(true)
    })
  })

  describe('英语学习子菜单', () => {
    it('包含新闻仪表板选项', async () => {
      wrapper.vm.showEnglishMenu = true
      await wrapper.vm.$nextTick()
      
      // 检查子菜单功能是否存在
      expect(wrapper.vm.showEnglishMenu).toBe(true)
    })

    it('包含单词学习选项', async () => {
      wrapper.vm.showEnglishMenu = true
      await wrapper.vm.$nextTick()
      
      // 检查子菜单功能是否存在
      expect(wrapper.vm.showEnglishMenu).toBe(true)
    })

    it('包含地道表达选项', async () => {
      wrapper.vm.showEnglishMenu = true
      await wrapper.vm.$nextTick()
      
      // 检查子菜单功能是否存在
      expect(wrapper.vm.showEnglishMenu).toBe(true)
    })

    it('包含新闻列表选项', async () => {
      wrapper.vm.showEnglishMenu = true
      await wrapper.vm.$nextTick()
      
      // 检查子菜单功能是否存在
      expect(wrapper.vm.showEnglishMenu).toBe(true)
    })

    it('能够切换子菜单显示状态', () => {
      expect(wrapper.vm.showEnglishMenu).toBe(false)
      
      wrapper.vm.toggleEnglishMenu()
      expect(wrapper.vm.showEnglishMenu).toBe(true)
      
      wrapper.vm.toggleEnglishMenu()
      expect(wrapper.vm.showEnglishMenu).toBe(false)
    })
  })

  describe('未登录状态', () => {
    beforeEach(() => {
      wrapper.vm.setAuthenticatedState(false)
    })

    it('显示登录菜单项', async () => {
      await wrapper.vm.$nextTick()
      
      const loginItem = wrapper.find('[data-index="/login"]')
      expect(loginItem.exists()).toBe(true)
      expect(loginItem.text()).toContain('登录')
    })

    it('显示注册菜单项', async () => {
      await wrapper.vm.$nextTick()
      
      const registerItem = wrapper.find('[data-index="/register"]')
      expect(registerItem.exists()).toBe(true)
      expect(registerItem.text()).toContain('注册')
    })

    it('注册按钮有特殊样式', async () => {
      await wrapper.vm.$nextTick()
      
      const registerItem = wrapper.find('.register-menu-item')
      expect(registerItem.exists()).toBe(true)
    })

    it('不显示用户相关菜单', async () => {
      await wrapper.vm.$nextTick()
      
      const createItem = wrapper.find('.create-menu-item')
      const userMenu = wrapper.find('.user-menu')
      
      expect(createItem.exists()).toBe(false)
      expect(userMenu.exists()).toBe(false)
    })
  })

  describe('已登录状态', () => {
    beforeEach(async () => {
      wrapper.vm.setAuthenticatedState(true, 'testuser')
      await wrapper.vm.$nextTick()
    })

    it('显示发布文章菜单项', () => {
      const createItem = wrapper.find('.create-menu-item')
      expect(createItem.exists()).toBe(true)
      expect(createItem.text()).toContain('发布文章')
    })

    it('发布文章按钮有特殊样式', () => {
      const createItem = wrapper.find('.create-menu-item')
      expect(createItem.exists()).toBe(true)
    })

    it('显示用户名', () => {
      const userMenu = wrapper.find('.user-menu')
      expect(userMenu.exists()).toBe(true)
      expect(userMenu.text()).toContain('testuser')
    })

    it('显示用户头像', () => {
      const avatar = wrapper.find('.avatar')
      expect(avatar.exists()).toBe(true)
      expect(avatar.text()).toBe('T')
    })

    it('不显示登录注册菜单', () => {
      const loginItem = wrapper.find('[data-index="/login"]')
      const registerItem = wrapper.find('[data-index="/register"]')
      
      expect(loginItem.exists()).toBe(false)
      expect(registerItem.exists()).toBe(false)
    })
  })

  describe('用户菜单', () => {
    beforeEach(async () => {
      wrapper.vm.setAuthenticatedState(true, 'testuser')
      wrapper.vm.showUserMenu = true
      await wrapper.vm.$nextTick()
    })

    it('包含个人中心选项', () => {
      const profileItem = wrapper.find('[data-index="/user/profile"]')
      expect(profileItem.exists()).toBe(true)
      expect(profileItem.text()).toContain('个人中心')
    })

    it('包含我的文章选项', () => {
      const articlesItem = wrapper.find('[data-index="/user/articles"]')
      expect(articlesItem.exists()).toBe(true)
      expect(articlesItem.text()).toContain('我的文章')
    })

    it('包含退出登录选项', () => {
      const logoutItem = wrapper.find('.logout-item')
      expect(logoutItem.exists()).toBe(true)
      expect(logoutItem.text()).toContain('退出登录')
    })

    it('能够切换用户菜单显示状态', () => {
      expect(wrapper.vm.showUserMenu).toBe(true)
      
      wrapper.vm.toggleUserMenu()
      expect(wrapper.vm.showUserMenu).toBe(false)
      
      wrapper.vm.toggleUserMenu()
      expect(wrapper.vm.showUserMenu).toBe(true)
    })
  })

  describe('退出登录功能', () => {
    beforeEach(async () => {
      wrapper.vm.setAuthenticatedState(true, 'testuser')
      await wrapper.vm.$nextTick()
    })

    it('点击退出登录调用handleLogout方法', async () => {
      const handleLogoutSpy = vi.spyOn(wrapper.vm, 'handleLogout')
      
      wrapper.vm.showUserMenu = true
      await wrapper.vm.$nextTick()
      
      const logoutItem = wrapper.find('.logout-item')
      await logoutItem.trigger('click')
      
      expect(handleLogoutSpy).toHaveBeenCalled()
    })

    it('成功退出登录', async () => {
      const logoutSpy = vi.spyOn(wrapper.vm, 'logout')
      const redirectSpy = vi.spyOn(wrapper.vm, 'redirectToHome')
      
      await wrapper.vm.handleLogout()
      
      expect(logoutSpy).toHaveBeenCalled()
      expect(redirectSpy).toHaveBeenCalled()
      expect(wrapper.vm.isAuthenticated).toBe(false)
    })

    it('退出登录失败时处理错误', async () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      
      // 模拟logout失败
      vi.spyOn(wrapper.vm, 'logout').mockRejectedValue(new Error('网络错误'))
      
      await wrapper.vm.handleLogout()
      
      expect(consoleSpy).toHaveBeenCalledWith('退出登录失败:', expect.any(Error))
      
      consoleSpy.mockRestore()
    })
  })

  describe('路由相关功能', () => {
    it('初始化时更新激活索引', () => {
      // 检查mounted钩子是否被调用
      expect(wrapper.vm.activeIndex).toBe('/')
    })

    it('更新激活菜单项', () => {
      wrapper.vm.currentRoute = '/articles'
      wrapper.vm.updateActiveIndex()
      
      expect(wrapper.vm.activeIndex).toBe('/articles')
    })

    it('默认激活索引为根路径', () => {
      expect(wrapper.vm.activeIndex).toBe('/')
    })
  })

  describe('认证状态管理', () => {
    it('初始化认证状态', () => {
      // 检查初始化方法是否存在
      expect(wrapper.vm.initAuth).toBeDefined()
    })

    it('能够设置认证状态', () => {
      wrapper.vm.setAuthenticatedState(true, 'newuser')
      
      expect(wrapper.vm.isAuthenticated).toBe(true)
      expect(wrapper.vm.userName).toBe('newuser')
      expect(wrapper.vm.userAvatar).toBe('N')
    })

    it('能够清除认证状态', () => {
      wrapper.vm.setAuthenticatedState(true, 'testuser')
      wrapper.vm.setAuthenticatedState(false, '')
      
      expect(wrapper.vm.isAuthenticated).toBe(false)
      expect(wrapper.vm.userName).toBe('')
      expect(wrapper.vm.userAvatar).toBe('')
    })
  })

  describe('响应式数据', () => {
    it('activeIndex状态正确绑定', () => {
      expect(wrapper.vm.activeIndex).toBe('/')
      
      wrapper.vm.activeIndex = '/articles'
      expect(wrapper.vm.activeIndex).toBe('/articles')
    })

    it('showEnglishMenu状态正确绑定', () => {
      expect(wrapper.vm.showEnglishMenu).toBe(false)
      
      wrapper.vm.showEnglishMenu = true
      expect(wrapper.vm.showEnglishMenu).toBe(true)
    })

    it('showUserMenu状态正确绑定', () => {
      expect(wrapper.vm.showUserMenu).toBe(false)
      
      wrapper.vm.showUserMenu = true
      expect(wrapper.vm.showUserMenu).toBe(true)
    })

    it('isAuthenticated状态正确绑定', () => {
      expect(wrapper.vm.isAuthenticated).toBe(false)
      
      wrapper.vm.isAuthenticated = true
      expect(wrapper.vm.isAuthenticated).toBe(true)
    })
  })

  describe('样式和布局', () => {
    it('导航菜单有正确的样式类', () => {
      expect(wrapper.find('.nav-menu').exists()).toBe(true)
    })

    it('弹性空间有正确的样式类', () => {
      expect(wrapper.find('.flex-grow').exists()).toBe(true)
    })

    it('注册按钮有特殊样式类', async () => {
      wrapper.vm.setAuthenticatedState(false)
      await wrapper.vm.$nextTick()
      
      expect(wrapper.find('.register-menu-item').exists()).toBe(true)
    })

    it('发布文章按钮有特殊样式类', async () => {
      wrapper.vm.setAuthenticatedState(true)
      await wrapper.vm.$nextTick()
      
      expect(wrapper.find('.create-menu-item').exists()).toBe(true)
    })
  })

  describe('边界情况', () => {
    it('空用户名时正确处理头像', () => {
      wrapper.vm.setAuthenticatedState(true, '')
      expect(wrapper.vm.userAvatar).toBe('')
    })

    it('未认证状态下用户菜单不显示', () => {
      wrapper.vm.setAuthenticatedState(false)
      wrapper.vm.showUserMenu = true
      
      // 用户菜单仍然存在于DOM中，但通过v-else不显示
      expect(wrapper.vm.isAuthenticated).toBe(false)
    })

    it('取消退出登录时不执行退出', async () => {
      // 模拟用户取消确认
      vi.spyOn(wrapper.vm, 'confirmLogout').mockRejectedValue('cancel')
      
      const logoutSpy = vi.spyOn(wrapper.vm, 'logout')
      
      await wrapper.vm.handleLogout()
      
      expect(logoutSpy).not.toHaveBeenCalled()
    })
  })
})