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
  template: '<div class="form-item"><label v-if="label">{{ label }}</label><slot /></div>',
  props: ['label', 'prop']
}

const mockElInput = {
  name: 'el-input',
  template: '<input :value="modelValue" :placeholder="placeholder" :type="type" @input="$emit(\'update:modelValue\', $event.target.value)" />',
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

describe('Login.vue - 简化测试', () => {
  let wrapper: any
  let mockRouter: any
  let mockLogin: any
  let mockVerifyUserIdentity: any
  let mockRequestPasswordReset: any

  beforeEach(async () => {
    setActivePinia(createPinia())
    
    // Setup mocks
    const authStoreModule = await import('@/stores/auth')
    mockLogin = authStoreModule.useAuthStore().login
    
    const authAPIModule = await import('@/api/auth')
    mockVerifyUserIdentity = authAPIModule.authAPI.verifyUserIdentity
    mockRequestPasswordReset = authAPIModule.authAPI.requestPasswordReset

    // Create mock router
    mockRouter = createRouter({
      history: createWebHistory(),
      routes: [
        { path: '/', component: { template: '<div>Home</div>' } },
        { path: '/register', component: { template: '<div>Register</div>' } },
        { path: '/login', component: { template: '<div>Login</div>' } }
      ]
    })

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

  describe('基本功能', () => {
    it('应该正确渲染登录页面', () => {
      expect(wrapper.exists()).toBe(true)
      expect(wrapper.text()).toContain('Alpha')
      expect(wrapper.text()).toContain('技术博客网站')
    })

    it('应该显示登录表单', () => {
      expect(wrapper.findComponent(mockElForm).exists()).toBe(true)
    })

    it('应该包含必要的方法', () => {
      expect(typeof wrapper.vm.generateCaptcha).toBe('function')
      expect(typeof wrapper.vm.refreshCaptcha).toBe('function')
      expect(typeof wrapper.vm.verifyIdentity).toBe('function')
      expect(typeof wrapper.vm.handleLogin).toBe('function')
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
      mockLogin.mockResolvedValue()

      // 模拟表单验证通过
      const mockValidate = vi.fn().mockResolvedValue(true)
      wrapper.vm.loginFormRef = { validate: mockValidate }

      // 执行登录
      await wrapper.vm.handleLogin()

      expect(mockValidate).toHaveBeenCalled()
      expect(mockLogin).toHaveBeenCalledWith({
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

      // 模拟表单验证通过
      const mockValidate = vi.fn().mockResolvedValue(true)
      wrapper.vm.loginFormRef = { validate: mockValidate }

      // 执行登录
      await wrapper.vm.handleLogin()

      // 应该不会调用登录API
      expect(mockLogin).not.toHaveBeenCalled()
    })
  })

  describe('身份验证', () => {
    it('应该验证用户身份', async () => {
      // 设置用户名和密码
      wrapper.vm.loginForm.username = 'testuser'
      wrapper.vm.loginForm.password = 'testpass'

      const mockUserInfo = {
        username: 'testuser',
        first_name: 'Test',
        avatar: '/avatar.jpg'
      }

      mockVerifyUserIdentity.mockResolvedValue({
        verified: true,
        user_info: mockUserInfo
      })

      await wrapper.vm.verifyIdentity()

      expect(mockVerifyUserIdentity).toHaveBeenCalledWith({
        username: 'testuser',
        password: 'testpass'
      })
      expect(wrapper.vm.verifiedUser).toEqual(mockUserInfo)
    })
  })

  describe('忘记密码功能', () => {
    it('应该发送密码重置邮件', async () => {
      wrapper.vm.showForgotPassword = true
      wrapper.vm.forgotPasswordForm.email = 'test@example.com'

      mockRequestPasswordReset.mockResolvedValue({
        message: '重置邮件已发送'
      })

      // 模拟表单验证通过
      const mockValidate = vi.fn().mockResolvedValue(true)
      wrapper.vm.forgotPasswordFormRef = { validate: mockValidate }

      await wrapper.vm.handleForgotPassword()

      expect(mockValidate).toHaveBeenCalled()
      expect(mockRequestPasswordReset).toHaveBeenCalledWith('test@example.com')
    })
  })

  describe('错误处理', () => {
    it('应该处理登录失败', async () => {
      wrapper.vm.loginForm.username = 'testuser'
      wrapper.vm.loginForm.password = 'wrongpass'
      wrapper.vm.loginForm.captcha = 'ABCD'
      wrapper.vm.captchaCode = 'ABCD'

      const error = new Error('用户名或密码错误')
      error.response = { data: { error: '用户名或密码错误' } }
      mockLogin.mockRejectedValue(error)

      // 模拟表单验证通过
      const mockValidate = vi.fn().mockResolvedValue(true)
      wrapper.vm.loginFormRef = { validate: mockValidate }

      await wrapper.vm.handleLogin()

      expect(mockValidate).toHaveBeenCalled()
      expect(mockLogin).toHaveBeenCalled()
    })
  })
}) 