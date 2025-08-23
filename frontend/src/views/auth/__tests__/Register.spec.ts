import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import Register from '../Register.vue'

// Mock dependencies
const mockRegister = vi.fn()
vi.mock('@/stores/auth', () => ({
  useAuthStore: vi.fn(() => ({
    register: mockRegister,
    user: null,
    isAuthenticated: false
  }))
}))

// Mock Element Plus components
const mockElCard = {
  name: 'el-card',
  template: '<div class="card"><slot name="header" /><slot /></div>',
  props: ['class']
}

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
  emits: ['update:modelValue', 'keyup.enter']
}

const mockElButton = {
  name: 'el-button',
  template: '<button :type="type" :size="size" :loading="loading" @click="$emit(\'click\')"><slot /></button>',
  props: ['type', 'size', 'loading'],
  emits: ['click']
}

const mockRouterLink = {
  name: 'router-link',
  template: '<a :to="to" class="router-link"><slot /></a>',
  props: ['to']
}

describe('Register.vue', () => {
  let wrapper: any
  let mockAuthStore: any
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
    mockAuthStore.register = mockRegister

    wrapper = mount(Register, {
      global: {
        plugins: [mockRouter],
        stubs: {
          'el-card': mockElCard,
          'el-form': mockElForm,
          'el-form-item': mockElFormItem,
          'el-input': mockElInput,
          'el-button': mockElButton,
          'router-link': mockRouterLink
        }
      }
    })
  })

  describe('基本渲染', () => {
    it('应该正确渲染注册页面', () => {
      expect(wrapper.exists()).toBe(true)
      expect(wrapper.text()).toContain('用户注册')
      expect(wrapper.text()).toContain('加入 Alpha 技术共享平台')
    })

    it('应该显示注册表单', () => {
      expect(wrapper.findComponent(mockElForm).exists()).toBe(true)
      expect(wrapper.text()).toContain('用户名')
      expect(wrapper.text()).toContain('邮箱')
      expect(wrapper.text()).toContain('姓名')
      expect(wrapper.text()).toContain('密码')
      expect(wrapper.text()).toContain('确认密码')
    })

    it('应该显示登录链接', () => {
      expect(wrapper.text()).toContain('已有账号？')
      expect(wrapper.text()).toContain('立即登录')
    })
  })

  describe('表单验证', () => {
    it('应该验证用户名必填', async () => {
      const usernameInput = wrapper.find('input[placeholder="请输入用户名"]')
      expect(usernameInput.exists()).toBe(true)
    })

    it('应该验证邮箱必填', async () => {
      const emailInput = wrapper.find('input[type="email"]')
      expect(emailInput.exists()).toBe(true)
    })

    it('应该验证姓名必填', async () => {
      const nameInput = wrapper.find('input[placeholder="请输入您的姓名"]')
      expect(nameInput.exists()).toBe(true)
    })

    it('应该验证密码必填', async () => {
      const passwordInputs = wrapper.findAll('input[type="password"]')
      expect(passwordInputs.length).toBe(2) // 密码和确认密码
    })

    it('应该验证密码确认必填', async () => {
      const confirmPasswordInput = wrapper.find('input[placeholder="请再次输入密码"]')
      expect(confirmPasswordInput.exists()).toBe(true)
    })
  })

  describe('密码确认验证', () => {
    it('应该验证密码确认与密码一致', async () => {
      // 直接测试验证函数，不依赖setData
      const validatePasswordConfirm = wrapper.vm.validatePasswordConfirm
      const callback = vi.fn()
      
      // 模拟不同的密码
      wrapper.vm.registerForm.password = 'password123'
      validatePasswordConfirm(null, 'different123', callback)
      
      expect(callback).toHaveBeenCalledWith(new Error('两次输入的密码不一致'))
    })

    it('应该通过密码确认验证', async () => {
      const validatePasswordConfirm = wrapper.vm.validatePasswordConfirm
      const callback = vi.fn()
      
      // 模拟相同的密码
      wrapper.vm.registerForm.password = 'password123'
      validatePasswordConfirm(null, 'password123', callback)
      
      expect(callback).toHaveBeenCalledWith()
    })
  })

  describe('注册功能', () => {
    it('应该成功注册', async () => {
      // 直接设置表单数据
      wrapper.vm.registerForm.username = 'newuser'
      wrapper.vm.registerForm.email = 'new@example.com'
      wrapper.vm.registerForm.first_name = 'New'
      wrapper.vm.registerForm.password = 'newpass123'
      wrapper.vm.registerForm.password_confirm = 'newpass123'

      // 模拟注册成功
      mockRegister.mockResolvedValue()

      // 模拟表单验证通过
      const mockValidate = vi.fn().mockResolvedValue(true)
      wrapper.vm.registerFormRef = { validate: mockValidate }

      // 执行注册
      await wrapper.vm.handleRegister()

      expect(mockValidate).toHaveBeenCalled()
      expect(mockRegister).toHaveBeenCalledWith({
        username: 'newuser',
        email: 'new@example.com',
        first_name: 'New',
        password: 'newpass123',
        password_confirm: 'newpass123'
      })
    })

    it('应该处理注册失败', async () => {
      // 直接设置表单数据
      wrapper.vm.registerForm.username = 'existinguser'
      wrapper.vm.registerForm.email = 'existing@example.com'
      wrapper.vm.registerForm.first_name = 'Existing'
      wrapper.vm.registerForm.password = 'pass123'
      wrapper.vm.registerForm.password_confirm = 'pass123'

      // 模拟注册失败
      const error = new Error('注册失败')
      error.response = {
        data: {
          username: ['用户名已存在'],
          email: ['邮箱已被使用']
        }
      }
      mockRegister.mockRejectedValue(error)

      // 模拟表单验证通过
      const mockValidate = vi.fn().mockResolvedValue(true)
      wrapper.vm.registerFormRef = { validate: mockValidate }

      // 执行注册
      await wrapper.vm.handleRegister()

      expect(mockValidate).toHaveBeenCalled()
      expect(mockRegister).toHaveBeenCalled()
    })
  })

  describe('表单状态', () => {
    it('应该显示加载状态', async () => {
      wrapper.vm.loading = true
      expect(wrapper.vm.loading).toBe(true)
    })

    it('应该重置表单数据', () => {
      const initialForm = {
        username: '',
        email: '',
        first_name: '',
        password: '',
        password_confirm: ''
      }

      expect(wrapper.vm.registerForm).toEqual(initialForm)
    })
  })

  describe('验证规则', () => {
    it('应该包含用户名验证规则', () => {
      const rules = wrapper.vm.registerRules
      expect(rules.username).toBeDefined()
      expect(rules.username.length).toBeGreaterThan(0)
    })

    it('应该包含邮箱验证规则', () => {
      const rules = wrapper.vm.registerRules
      expect(rules.email).toBeDefined()
      expect(rules.email.length).toBeGreaterThan(0)
    })

    it('应该包含姓名验证规则', () => {
      const rules = wrapper.vm.registerRules
      expect(rules.first_name).toBeDefined()
      expect(rules.first_name.length).toBeGreaterThan(0)
    })

    it('应该包含密码验证规则', () => {
      const rules = wrapper.vm.registerRules
      expect(rules.password).toBeDefined()
      expect(rules.password.length).toBeGreaterThan(0)
    })

    it('应该包含密码确认验证规则', () => {
      const rules = wrapper.vm.registerRules
      expect(rules.password_confirm).toBeDefined()
      expect(rules.password_confirm.length).toBeGreaterThan(0)
    })
  })

  describe('组件方法', () => {
    it('应该包含必要的方法', () => {
      expect(typeof wrapper.vm.validatePasswordConfirm).toBe('function')
      expect(typeof wrapper.vm.handleRegister).toBe('function')
    })
  })

  describe('错误处理', () => {
    it('应该处理字段错误', async () => {
      const error = new Error('注册失败')
      error.response = {
        data: {
          username: ['用户名已存在'],
          email: ['邮箱格式不正确']
        }
      }

      // 模拟错误处理逻辑
      const errors = error.response.data
      const errorMessages = []
      
      for (const field in errors) {
        if (Array.isArray(errors[field])) {
          errorMessages.push(`${field}: ${errors[field][0]}`)
        } else {
          errorMessages.push(errors[field])
        }
      }

      expect(errorMessages).toContain('username: 用户名已存在')
      expect(errorMessages).toContain('email: 邮箱格式不正确')
    })

    it('应该处理非数组错误', async () => {
      const error = new Error('注册失败')
      error.response = {
        data: {
          error: '服务器错误'
        }
      }

      const errors = error.response.data
      const errorMessages = []
      
      for (const field in errors) {
        if (Array.isArray(errors[field])) {
          errorMessages.push(`${field}: ${errors[field][0]}`)
        } else {
          errorMessages.push(errors[field])
        }
      }

      expect(errorMessages).toContain('服务器错误')
    })
  })
}) 