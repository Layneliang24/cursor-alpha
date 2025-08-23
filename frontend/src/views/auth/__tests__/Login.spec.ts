import { describe, it, expect, vi, beforeEach } from 'vitest'
import { shallowMount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import { nextTick } from 'vue'
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

// Mock Element Plus
vi.mock('element-plus', () => ({
  ElMessage: {
    error: vi.fn(),
    success: vi.fn(),
    warning: vi.fn(),
    info: vi.fn()
  }
}))

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

    // 确保mock函数被正确设置
    mockAuthStore.login = vi.fn()
    mockAuthAPI.verifyUserIdentity = vi.fn()
    mockAuthAPI.requestPasswordReset = vi.fn()

    wrapper = shallowMount(Login, {
      global: {
        plugins: [mockRouter],
        stubs: {
          'el-form': true,
          'el-form-item': true,
          'el-input': true,
          'el-button': true,
          'el-dialog': true,
          'el-icon': true,
          'router-link': true,
          'AnimatedBackground': true,
          'Document': true,
          'User': true,
          'Star': true,
          'Check': true,
          'Message': true,
          'Lock': true,
          'Key': true
        }
      }
    })
  })

  describe('基本功能', () => {
    it('应该正确渲染登录页面', () => {
      expect(wrapper.exists()).toBe(true)
    })

    it('应该包含必要的方法', () => {
      expect(typeof wrapper.vm.generateCaptcha).toBe('function')
      expect(typeof wrapper.vm.refreshCaptcha).toBe('function')
      expect(typeof wrapper.vm.verifyIdentity).toBe('function')
      expect(typeof wrapper.vm.handleLogin).toBe('function')
      expect(typeof wrapper.vm.handleForgotPassword).toBe('function')
    })

    it('应该有正确的初始数据', () => {
      expect(wrapper.vm.loginForm).toBeDefined()
      expect(wrapper.vm.captchaCode).toBeDefined()
      expect(wrapper.vm.showForgotPassword).toBe(false)
      expect(wrapper.vm.verifiedUser).toBeNull()
    })
  })

  describe('登录功能', () => {
    it('应该成功登录', async () => {
      // 设置表单数据
      wrapper.vm.loginForm.username = 'testuser'
      wrapper.vm.loginForm.password = 'testpass'
      
      // 确保验证码匹配
      await wrapper.vm.refreshCaptcha()
      const currentCaptcha = wrapper.vm.captchaCode
      wrapper.vm.loginForm.captcha = currentCaptcha

      console.log('验证码设置:', {
        captcha: wrapper.vm.loginForm.captcha,
        captchaCode: wrapper.vm.captchaCode,
        captchaMatch: wrapper.vm.loginForm.captcha.toLowerCase() === wrapper.vm.captchaCode.toLowerCase()
      })

      // 模拟登录成功
      mockAuthStore.login.mockResolvedValue()

      // 模拟表单验证通过 - 直接设置整个ref对象
      const mockValidate = vi.fn().mockResolvedValue(true)
      wrapper.vm.loginFormRef.value = { validate: mockValidate }
      
      // 等待响应式更新
      await nextTick()

      // 执行登录
      console.log('执行登录前:', {
        mockLogin: mockAuthStore.login,
        mockLoginCalls: mockAuthStore.login.mock?.calls?.length || 0,
        loginFormRef: wrapper.vm.loginFormRef,
        loginFormRefValue: wrapper.vm.loginFormRef?.value,
        loginFormRefValueValidate: wrapper.vm.loginFormRef?.value?.validate,
        loginFormRefValueType: typeof wrapper.vm.loginFormRef?.value,
        loginFormRefValueTruthy: !!wrapper.vm.loginFormRef?.value
      })
      
      try {
        await wrapper.vm.handleLogin()
        console.log('handleLogin 执行成功')
      } catch (error) {
        console.log('handleLogin 执行失败:', error)
      }
      
      console.log('执行登录后:', {
        mockLoginCalls: mockAuthStore.login.mock?.calls?.length || 0,
        mockLoginArgs: mockAuthStore.login.mock?.calls || []
      })

      expect(mockValidate).toHaveBeenCalled()
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

      // 模拟表单验证通过
      const mockValidate = vi.fn().mockResolvedValue(true)
      wrapper.vm.loginFormRef.value = { validate: mockValidate }
      
      // 等待响应式更新
      await nextTick()

      // 执行登录
      await wrapper.vm.handleLogin()

      // 应该不会调用登录API
      expect(mockAuthStore.login).not.toHaveBeenCalled()
    })

    it('应该处理登录失败', async () => {
      wrapper.vm.loginForm.username = 'testuser'
      wrapper.vm.loginForm.password = 'wrongpass'
      
      // 确保验证码匹配
      await wrapper.vm.refreshCaptcha()
      const currentCaptcha = wrapper.vm.captchaCode
      wrapper.vm.loginForm.captcha = currentCaptcha

      const error = new Error('用户名或密码错误') as any
      error.response = { data: { error: '用户名或密码错误' } }
      mockAuthStore.login.mockRejectedValue(error)

      // 模拟表单验证通过
      const mockValidate = vi.fn().mockResolvedValue(true)
      wrapper.vm.loginFormRef.value = { validate: mockValidate }
      
      // 等待响应式更新
      await nextTick()

      await wrapper.vm.handleLogin()

      expect(mockValidate).toHaveBeenCalled()
      expect(mockAuthStore.login).toHaveBeenCalled()
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

      mockAuthAPI.verifyUserIdentity.mockResolvedValue({
        verified: true,
        user_info: mockUserInfo
      })

      await wrapper.vm.verifyIdentity()

      expect(mockAuthAPI.verifyUserIdentity).toHaveBeenCalledWith({
        username: 'testuser',
        password: 'testpass'
      })
      expect(wrapper.vm.verifiedUser).toEqual(mockUserInfo)
    })

    it('应该清除已验证用户信息', async () => {
      // 先设置已验证用户
      wrapper.vm.verifiedUser = { username: 'testuser' }

      // 模拟用户名输入
      wrapper.vm.clearVerifiedUser()

      expect(wrapper.vm.verifiedUser).toBeNull()
    })
  })

  describe('忘记密码功能', () => {
    it('应该发送密码重置邮件', async () => {
      wrapper.vm.showForgotPassword = true
      wrapper.vm.forgotPasswordForm.email = 'test@example.com'

      mockAuthAPI.requestPasswordReset.mockResolvedValue({
        message: '重置邮件已发送'
      })

      // 模拟表单验证通过
      const mockValidate = vi.fn().mockResolvedValue(true)
      wrapper.vm.forgotPasswordFormRef = { validate: mockValidate }

      await wrapper.vm.handleForgotPassword()

      expect(mockValidate).toHaveBeenCalled()
      expect(mockAuthAPI.requestPasswordReset).toHaveBeenCalledWith('test@example.com')
    })

    it('应该关闭忘记密码弹窗', async () => {
      wrapper.vm.showForgotPassword = true

      await wrapper.vm.handleForgotPasswordClose()

      expect(wrapper.vm.showForgotPassword).toBe(false)
      expect(wrapper.vm.forgotPasswordForm.email).toBe('')
    })
  })

  describe('验证码功能', () => {
    it('应该生成验证码', () => {
      // 验证码生成在onMounted中调用
      expect(wrapper.vm.captchaCode).toBeDefined()
      expect(typeof wrapper.vm.captchaCode).toBe('string')
    })

    it('应该刷新验证码', async () => {
      const originalCode = wrapper.vm.captchaCode
      await wrapper.vm.refreshCaptcha()
      expect(wrapper.vm.captchaCode).toBeDefined()
      expect(typeof wrapper.vm.captchaCode).toBe('string')
    })
  })

  describe('错误处理', () => {
    it('应该处理身份验证失败', async () => {
      const error = new Error('验证失败')
      error.response = { status: 401 }
      mockAuthAPI.verifyUserIdentity.mockRejectedValue(error)

      wrapper.vm.loginForm.username = 'testuser'
      wrapper.vm.loginForm.password = 'wrongpass'

      await wrapper.vm.verifyIdentity()

      expect(wrapper.vm.verifiedUser).toBeNull()
    })
  })
}) 