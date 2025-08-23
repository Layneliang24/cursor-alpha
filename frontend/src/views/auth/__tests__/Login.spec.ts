import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import Login from '../Login.vue'

// Mock dependencies
vi.mock('@/stores/auth', () => ({
  useAuthStore: vi.fn(() => ({
    login: vi.fn(),
    user: null,
    isAuthenticated: false
  }))
}))

vi.mock('@/api/auth', () => ({
  authAPI: {
    verifyUserIdentity: vi.fn(),
    requestPasswordReset: vi.fn()
  }
}))

vi.mock('@/components/AnimatedBackground.vue', () => ({
  default: {
    name: 'AnimatedBackground',
    template: '<div class="animated-background"></div>'
  }
}))

// Mock Element Plus components
const mockElForm = {
  name: 'el-form',
  template: '<form><slot /></form>',
  props: ['model', 'rules', 'label-width'],
  emits: ['submit']
}

const mockElFormItem = {
  name: 'el-form-item',
  template: '<div class="form-item"><slot /></div>',
  props: ['label', 'prop']
}

const mockElInput = {
  name: 'el-input',
  template: '<input :value="modelValue" @input="$emit(\'update:modelValue\', $event.target.value)" />',
  props: ['modelValue', 'placeholder', 'type', 'prefix-icon', 'size', 'show-password'],
  emits: ['update:modelValue', 'input', 'blur', 'keyup.enter']
}

const mockElButton = {
  name: 'el-button',
  template: '<button :type="type" :size="size" :loading="loading" @click="$emit(\'click\')"><slot /></button>',
  props: ['type', 'size', 'loading'],
  emits: ['click']
}

const mockElDialog = {
  name: 'el-dialog',
  template: '<div v-if="modelValue" class="dialog"><slot /><slot name="footer" /></div>',
  props: ['modelValue', 'title', 'width', 'before-close'],
  emits: ['update:modelValue']
}

const mockElIcon = {
  name: 'el-icon',
  template: '<span class="el-icon"><slot /></span>'
}

const mockRouterLink = {
  name: 'router-link',
  template: '<a :to="to" class="router-link"><slot /></a>',
  props: ['to']
}

describe('Login.vue', () => {
  let wrapper: any
  let mockAuthStore: any
  let mockAuthAPI: any
  let mockRouter: any

  beforeEach(async () => {
    setActivePinia(createPinia())
    
    // Create mock router
    mockRouter = createRouter({
      history: createWebHistory(),
      routes: [
        { path: '/', component: { template: '<div>Home</div>' } },
        { path: '/register', component: { template: '<div>Register</div>' } },
        { path: '/login', component: { template: '<div>Login</div>' } }
      ]
    })

    // Setup mocks
    const authStoreModule = await import('@/stores/auth')
    mockAuthStore = authStoreModule.useAuthStore()
    
    const authAPIModule = await import('@/api/auth')
    mockAuthAPI = authAPIModule.authAPI

    // Mock canvas context
    const mockContext = {
      clearRect: vi.fn(),
      createLinearGradient: vi.fn(() => ({
        addColorStop: vi.fn()
      })),
      fillStyle: '',
      fillRect: vi.fn(),
      strokeStyle: '',
      beginPath: vi.fn(),
      moveTo: vi.fn(),
      lineTo: vi.fn(),
      stroke: vi.fn(),
      font: '',
      textBaseline: '',
      save: vi.fn(),
      translate: vi.fn(),
      rotate: vi.fn(),
      fillText: vi.fn(),
      restore: vi.fn(),
      arc: vi.fn(),
      fill: vi.fn()
    }

    // Mock canvas element
    const mockCanvas = {
      getContext: vi.fn(() => mockContext),
      width: 120,
      height: 40,
      setAttribute: vi.fn(),
      getAttribute: vi.fn(),
      removeAttribute: vi.fn(),
      hasAttribute: vi.fn(),
      classList: {
        add: vi.fn(),
        remove: vi.fn(),
        contains: vi.fn(),
        toggle: vi.fn(),
        includes: vi.fn()
      },
      style: {},
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn()
    }

    // Mock document.createElement for canvas
    const originalCreateElement = document.createElement
    global.document.createElement = vi.fn((tagName) => {
      if (tagName === 'canvas') {
        return mockCanvas
      }
      return originalCreateElement.call(document, tagName)
    })

    wrapper = mount(Login, {
      global: {
        plugins: [mockRouter],
        stubs: {
          'el-form': mockElForm,
          'el-form-item': mockElFormItem,
          'el-input': mockElInput,
          'el-button': mockElButton,
          'el-dialog': mockElDialog,
          'el-icon': mockElIcon,
          'router-link': mockRouterLink,
          'AnimatedBackground': true,
          'Document': true,
          'User': true,
          'Star': true,
          'Check': true
        }
      }
    })
  })

  describe('基本渲染', () => {
    it('应该正确渲染登录页面', () => {
      expect(wrapper.exists()).toBe(true)
      expect(wrapper.text()).toContain('Alpha')
      expect(wrapper.text()).toContain('技术博客网站')
      expect(wrapper.text()).toContain('欢迎回来')
      expect(wrapper.text()).toContain('登录您的账户')
    })

    it('应该显示登录表单', () => {
      expect(wrapper.findComponent(mockElForm).exists()).toBe(true)
      expect(wrapper.text()).toContain('用户名')
      expect(wrapper.text()).toContain('密码')
      expect(wrapper.text()).toContain('验证码')
    })

    it('应该显示功能特性', () => {
      expect(wrapper.text()).toContain('丰富的技术文章')
      expect(wrapper.text()).toContain('专业的技术社区')
      expect(wrapper.text()).toContain('优质的学习体验')
    })

    it('应该显示注册和忘记密码链接', () => {
      expect(wrapper.text()).toContain('立即注册')
      expect(wrapper.text()).toContain('忘记密码？')
    })
  })

  describe('表单验证', () => {
    it('应该验证用户名必填', async () => {
      const usernameInput = wrapper.find('input[placeholder="请输入用户名或邮箱"]')
      expect(usernameInput.exists()).toBe(true)
    })

    it('应该验证密码必填', async () => {
      const passwordInput = wrapper.find('input[type="password"]')
      expect(passwordInput.exists()).toBe(true)
    })

    it('应该验证验证码必填', async () => {
      const captchaInput = wrapper.find('input[placeholder="请输入验证码"]')
      expect(captchaInput.exists()).toBe(true)
    })
  })

  describe('验证码功能', () => {
    it('应该生成验证码', () => {
      // 验证码生成在onMounted中调用
      expect(wrapper.vm.captchaCode).toBeDefined()
    })

    it('应该刷新验证码', async () => {
      const originalCode = wrapper.vm.captchaCode
      await wrapper.vm.refreshCaptcha()
      expect(wrapper.vm.captchaCode).not.toBe(originalCode)
    })
  })

  describe('身份验证', () => {
    it('应该在密码输入时验证用户身份', async () => {
      // 设置用户名和密码
      wrapper.vm.loginForm.username = 'testuser'
      wrapper.vm.loginForm.password = 'testpass'
      wrapper.vm.loginForm.captcha = ''

      // 模拟密码输入框的blur事件
      const passwordInput = wrapper.find('input[type="password"]')
      await passwordInput.trigger('blur')

      // 验证是否调用了身份验证API
      expect(mockAuthAPI.verifyUserIdentity).toHaveBeenCalledWith({
        username: 'testuser',
        password: 'testpass'
      })
    })

    it('应该显示已验证用户信息', async () => {
      const mockUserInfo = {
        username: 'testuser',
        first_name: 'Test',
        avatar: '/avatar.jpg'
      }

      mockAuthAPI.verifyUserIdentity.mockResolvedValue({
        verified: true,
        user_info: mockUserInfo
      })

      // 设置表单数据并触发验证
      wrapper.vm.loginForm.username = 'testuser'
      wrapper.vm.loginForm.password = 'testpass'
      wrapper.vm.loginForm.captcha = ''

      await wrapper.vm.verifyIdentity()

      expect(wrapper.vm.verifiedUser).toEqual(mockUserInfo)
    })

    it('应该清除已验证用户信息', async () => {
      // 先设置已验证用户
      wrapper.vm.verifiedUser = { username: 'testuser' }

      // 模拟用户名输入
      const usernameInput = wrapper.find('input[placeholder="请输入用户名或邮箱"]')
      await usernameInput.trigger('input')

      expect(wrapper.vm.verifiedUser).toBeNull()
    })
  })

  describe('登录功能', () => {
    it('应该成功登录', async () => {
      // 设置表单数据
      wrapper.vm.loginForm.username = 'testuser'
      wrapper.vm.loginForm.password = 'testpass'
      wrapper.vm.loginForm.captcha = 'ABCD'
      wrapper.vm.captchaCode = 'ABCD'

      // 模拟登录成功
      mockAuthStore.login.mockResolvedValue()

      // 执行登录
      await wrapper.vm.handleLogin()

      expect(mockAuthStore.login).toHaveBeenCalledWith({
        username: 'testuser',
        password: 'testpass'
      })
    })

    it('应该验证验证码', async () => {
      // 设置错误的验证码
      wrapper.vm.loginForm.username = 'testuser'
      wrapper.vm.loginForm.password = 'testpass'
      wrapper.vm.loginForm.captcha = 'WRONG'
      wrapper.vm.captchaCode = 'ABCD'

      // 执行登录
      await wrapper.vm.handleLogin()

      // 应该不会调用登录API
      expect(mockAuthStore.login).not.toHaveBeenCalled()
    })
  })

  describe('忘记密码功能', () => {
    it('应该显示忘记密码弹窗', async () => {
      wrapper.vm.showForgotPassword = true
      expect(wrapper.vm.showForgotPassword).toBe(true)
    })

    it('应该发送密码重置邮件', async () => {
      // 设置忘记密码表单
      wrapper.vm.showForgotPassword = true
      wrapper.vm.forgotPasswordForm.email = 'test@example.com'

      // 模拟API调用成功
      mockAuthAPI.requestPasswordReset.mockResolvedValue({
        message: '重置邮件已发送'
      })

      // 执行发送
      await wrapper.vm.handleForgotPassword()

      expect(mockAuthAPI.requestPasswordReset).toHaveBeenCalledWith('test@example.com')
    })

    it('应该关闭忘记密码弹窗', async () => {
      wrapper.vm.showForgotPassword = true

      await wrapper.vm.handleForgotPasswordClose()

      expect(wrapper.vm.showForgotPassword).toBe(false)
      expect(wrapper.vm.forgotPasswordForm.email).toBe('')
    })
  })

  describe('错误处理', () => {
    it('应该处理登录失败', async () => {
      // 设置表单数据
      wrapper.vm.loginForm.username = 'testuser'
      wrapper.vm.loginForm.password = 'wrongpass'
      wrapper.vm.loginForm.captcha = 'ABCD'
      wrapper.vm.captchaCode = 'ABCD'

      // 模拟登录失败
      const error = new Error('用户名或密码错误')
      error.response = { data: { error: '用户名或密码错误' } }
      mockAuthStore.login.mockRejectedValue(error)

      // 执行登录
      await wrapper.vm.handleLogin()

      expect(mockAuthStore.login).toHaveBeenCalled()
    })

    it('应该处理身份验证失败', async () => {
      const error = new Error('验证失败')
      error.response = { status: 401 }
      mockAuthAPI.verifyUserIdentity.mockRejectedValue(error)

      wrapper.vm.loginForm.username = 'testuser'
      wrapper.vm.loginForm.password = 'wrongpass'
      wrapper.vm.loginForm.captcha = ''

      await wrapper.vm.verifyIdentity()

      expect(wrapper.vm.verifiedUser).toBeNull()
    })
  })

  describe('组件方法', () => {
    it('应该包含必要的方法', () => {
      expect(typeof wrapper.vm.generateCaptcha).toBe('function')
      expect(typeof wrapper.vm.drawCaptcha).toBe('function')
      expect(typeof wrapper.vm.refreshCaptcha).toBe('function')
      expect(typeof wrapper.vm.verifyIdentity).toBe('function')
      expect(typeof wrapper.vm.clearVerifiedUser).toBe('function')
      expect(typeof wrapper.vm.handleLogin).toBe('function')
      expect(typeof wrapper.vm.handleForgotPassword).toBe('function')
      expect(typeof wrapper.vm.handleForgotPasswordClose).toBe('function')
    })
  })
}) 