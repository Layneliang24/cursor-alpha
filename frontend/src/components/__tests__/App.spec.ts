import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import App from '../../App.vue'

// Mock 路由
const createMockRouter = (path: string) => {
  const router = createRouter({
    history: createWebHistory(),
    routes: [
      { path: '/', name: 'home', component: { template: '<div>Home</div>' } },
      { path: '/login', name: 'login', component: { template: '<div>Login</div>' } },
      { path: '/register', name: 'register', component: { template: '<div>Register</div>' } },
      { path: '/dashboard', name: 'dashboard', component: { template: '<div>Dashboard</div>' } }
    ]
  })
  
  // 设置当前路径
  router.push(path)
  return router
}

// Mock Pinia store
const pinia = createPinia()

// Mock 子组件
const mockComponents = {
  TopNavBar: { template: '<div class="top-nav-bar">TopNavBar</div>' },
  SideMenu: { template: '<div class="side-menu">SideMenu</div>' },
  FooterComponent: { template: '<div class="footer-component">FooterComponent</div>' },
  MouseEffects: { template: '<div class="mouse-effects">MouseEffects</div>' }
}

describe('App Component', () => {
  describe('认证页面布局', () => {
    it('在登录页面显示简洁布局', async () => {
      const router = createMockRouter('/login')
      const wrapper = mount(App, {
        global: {
          plugins: [router, pinia],
          components: mockComponents,
          stubs: {
            'router-view': true
          }
        }
      })
      
      await router.isReady()
      await wrapper.vm.$nextTick()
      
      expect(wrapper.find('.auth-layout').exists()).toBe(true)
      expect(wrapper.find('.top-nav-bar').exists()).toBe(false)
      expect(wrapper.find('.side-menu').exists()).toBe(false)
    })

    it('在注册页面显示简洁布局', async () => {
      const router = createMockRouter('/register')
      const wrapper = mount(App, {
        global: {
          plugins: [router, pinia],
          components: mockComponents,
          stubs: {
            'router-view': true
          }
        }
      })
      
      await router.isReady()
      await wrapper.vm.$nextTick()
      
      expect(wrapper.find('.auth-layout').exists()).toBe(true)
      expect(wrapper.find('.top-nav-bar').exists()).toBe(false)
      expect(wrapper.find('.side-menu').exists()).toBe(false)
    })
  })

  describe('普通页面布局', () => {
    it('在首页显示完整布局', async () => {
      const router = createMockRouter('/')
      const wrapper = mount(App, {
        global: {
          plugins: [router, pinia],
          components: mockComponents,
          stubs: {
            'router-view': true
          }
        }
      })
      
      await router.isReady()
      await wrapper.vm.$nextTick()
      
      expect(wrapper.find('.auth-layout').exists()).toBe(false)
      expect(wrapper.find('.top-nav-bar').exists()).toBe(true)
      expect(wrapper.find('.side-menu').exists()).toBe(true)
      expect(wrapper.find('.footer-component').exists()).toBe(true)
      expect(wrapper.find('.mouse-effects').exists()).toBe(true)
    })

    it('在仪表板页面显示完整布局', async () => {
      const router = createMockRouter('/dashboard')
      const wrapper = mount(App, {
        global: {
          plugins: [router, pinia],
          components: mockComponents,
          stubs: {
            'router-view': true
          }
        }
      })
      
      await router.isReady()
      await wrapper.vm.$nextTick()
      
      expect(wrapper.find('.auth-layout').exists()).toBe(false)
      expect(wrapper.find('.top-nav-bar').exists()).toBe(true)
      expect(wrapper.find('.side-menu').exists()).toBe(true)
    })
  })

  describe('响应式布局', () => {
    it('主内容区域根据侧边栏状态调整样式', async () => {
      const router = createMockRouter('/')
      const wrapper = mount(App, {
        global: {
          plugins: [router, pinia],
          components: mockComponents,
          stubs: {
            'router-view': true
          }
        }
      })
      
      await router.isReady()
      await wrapper.vm.$nextTick()
      
      const mainContent = wrapper.find('.main-content')
      expect(mainContent.classes()).toContain('with-sidebar')
    })
  })

  describe('组件挂载', () => {
    it('正确挂载所有子组件', async () => {
      const router = createMockRouter('/')
      const wrapper = mount(App, {
        global: {
          plugins: [router, pinia],
          components: mockComponents,
          stubs: {
            'router-view': true
          }
        }
      })
      
      await router.isReady()
      await wrapper.vm.$nextTick()
      
      expect(wrapper.findComponent(mockComponents.TopNavBar).exists()).toBe(true)
      expect(wrapper.findComponent(mockComponents.SideMenu).exists()).toBe(true)
      expect(wrapper.findComponent(mockComponents.FooterComponent).exists()).toBe(true)
      expect(wrapper.findComponent(mockComponents.MouseEffects).exists()).toBe(true)
    })
  })
}) 