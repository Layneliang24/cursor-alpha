import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import { rest } from 'msw'
import { setupServer } from 'msw/node'
import { mockData } from '../../src/mocks/handlers'
import AIConfig from '../../src/views/AIConfig.vue'
import { useAuthStore } from '../../src/stores/auth'

// 设置MSW服务器
const server = setupServer(
  // AI提供商相关
  rest.get('/api/v1/ai/providers/', (req, res, ctx) => {
    return res(ctx.status(200), ctx.json(mockData.providers))
  }),
  
  rest.post('/api/v1/ai/providers/', (req, res, ctx) => {
    const newProvider = {
      id: mockData.providers.length + 1,
      ...req.body,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }
    mockData.providers.push(newProvider)
    return res(ctx.status(201), ctx.json(newProvider))
  }),
  
  // API密钥相关
  rest.get('/api/v1/ai/api-keys/', (req, res, ctx) => {
    return res(ctx.status(200), ctx.json(mockData.apiKeys))
  }),
  
  // AI模型相关
  rest.get('/api/v1/ai/models/', (req, res, ctx) => {
    return res(ctx.status(200), ctx.json(mockData.models))
  }),
  
  // 模型配置相关
  rest.get('/api/v1/ai/model-configs/', (req, res, ctx) => {
    return res(ctx.status(200), ctx.json(mockData.modelConfigs))
  }),
  
  // 统计信息相关
  rest.get('/api/v1/ai/statistics/', (req, res, ctx) => {
    return res(ctx.status(200), ctx.json(mockData.statistics))
  }),
  
  // 健康检查
  rest.get('/api/v1/ai/health/', (req, res, ctx) => {
    return res(ctx.status(200), ctx.json(mockData.health))
  })
)

// 启动服务器
beforeAll(() => server.listen())

// 重置处理器
afterEach(() => server.resetHandlers())

// 关闭服务器
afterAll(() => server.close())

describe('AI配置组件集成测试', () => {
  let wrapper
  let pinia

  beforeEach(() => {
    pinia = createTestingPinia({
      createSpy: vi.fn,
      stubActions: false,
    })

    // 设置认证状态
    const authStore = useAuthStore()
    authStore.isAuthenticated = true
    authStore.user = { id: 1, username: 'testuser' }

    wrapper = mount(AIConfig, {
      global: {
        plugins: [pinia],
        stubs: {
          'router-link': true,
          'router-view': true,
        },
      },
    })
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  describe('组件初始化', () => {
    it('应该正确渲染AI配置页面', () => {
      expect(wrapper.find('.ai-config-container').exists()).toBe(true)
      expect(wrapper.find('.config-tabs').exists()).toBe(true)
    })

    it('应该显示所有配置标签页', () => {
      const tabs = wrapper.findAll('.el-tab-pane')
      expect(tabs.length).toBeGreaterThan(0)
    })

    it('应该加载初始数据', async () => {
      await wrapper.vm.$nextTick()
      expect(wrapper.vm.providers).toBeDefined()
      expect(wrapper.vm.apiKeys).toBeDefined()
      expect(wrapper.vm.models).toBeDefined()
    })
  })

  describe('AI提供商管理', () => {
    it('应该显示提供商列表', async () => {
      await wrapper.vm.$nextTick()
      const providerList = wrapper.find('.provider-list')
      expect(providerList.exists()).toBe(true)
    })

    it('应该能够添加新提供商', async () => {
      const addButton = wrapper.find('.add-provider-btn')
      expect(addButton.exists()).toBe(true)
      
      // 模拟点击添加按钮
      await addButton.trigger('click')
      await wrapper.vm.$nextTick()
      
      // 应该显示添加对话框
      const dialog = wrapper.find('.provider-dialog')
      expect(dialog.exists()).toBe(true)
    })

    it('应该能够编辑现有提供商', async () => {
      await wrapper.vm.$nextTick()
      const editButtons = wrapper.findAll('.edit-provider-btn')
      
      if (editButtons.length > 0) {
        await editButtons[0].trigger('click')
        await wrapper.vm.$nextTick()
        
        // 应该显示编辑对话框
        const dialog = wrapper.find('.provider-dialog')
        expect(dialog.exists()).toBe(true)
      }
    })
  })

  describe('API密钥管理', () => {
    it('应该显示API密钥列表', async () => {
      await wrapper.vm.$nextTick()
      const keyList = wrapper.find('.api-key-list')
      expect(keyList.exists()).toBe(true)
    })

    it('应该能够添加新API密钥', async () => {
      const addButton = wrapper.find('.add-api-key-btn')
      expect(addButton.exists()).toBe(true)
      
      // 模拟点击添加按钮
      await addButton.trigger('click')
      await wrapper.vm.$nextTick()
      
      // 应该显示添加对话框
      const dialog = wrapper.find('.api-key-dialog')
      expect(dialog.exists()).toBe(true)
    })
  })

  describe('AI模型管理', () => {
    it('应该显示模型列表', async () => {
      await wrapper.vm.$nextTick()
      const modelList = wrapper.find('.model-list')
      expect(modelList.exists()).toBe(true)
    })

    it('应该能够查看模型详情', async () => {
      await wrapper.vm.$nextTick()
      const detailButtons = wrapper.findAll('.view-model-detail-btn')
      
      if (detailButtons.length > 0) {
        await detailButtons[0].trigger('click')
        await wrapper.vm.$nextTick()
        
        // 应该显示详情对话框
        const dialog = wrapper.find('.model-detail-dialog')
        expect(dialog.exists()).toBe(true)
      }
    })
  })

  describe('模型配置管理', () => {
    it('应该显示模型配置列表', async () => {
      await wrapper.vm.$nextTick()
      const configList = wrapper.find('.model-config-list')
      expect(configList.exists()).toBe(true)
    })

    it('应该能够创建新配置', async () => {
      const addButton = wrapper.find('.add-config-btn')
      expect(addButton.exists()).toBe(true)
      
      // 模拟点击添加按钮
      await addButton.trigger('click')
      await wrapper.vm.$nextTick()
      
      // 应该显示添加对话框
      const dialog = wrapper.find('.config-dialog')
      expect(dialog.exists()).toBe(true)
    })
  })

  describe('统计信息显示', () => {
    it('应该显示统计信息', async () => {
      await wrapper.vm.$nextTick()
      const statistics = wrapper.find('.statistics-section')
      expect(statistics.exists()).toBe(true)
    })

    it('应该显示使用量统计', async () => {
      await wrapper.vm.$nextTick()
      const usageStats = wrapper.find('.usage-statistics')
      expect(usageStats.exists()).toBe(true)
    })

    it('应该显示成本统计', async () => {
      await wrapper.vm.$nextTick()
      const costStats = wrapper.find('.cost-statistics')
      expect(costStats.exists()).toBe(true)
    })
  })

  describe('健康状态监控', () => {
    it('应该显示健康状态', async () => {
      await wrapper.vm.$nextTick()
      const healthStatus = wrapper.find('.health-status')
      expect(healthStatus.exists()).toBe(true)
    })

    it('应该显示服务状态指示器', async () => {
      await wrapper.vm.$nextTick()
      const statusIndicators = wrapper.findAll('.status-indicator')
      expect(statusIndicators.length).toBeGreaterThan(0)
    })
  })

  describe('错误处理', () => {
    it('应该处理API错误', async () => {
      // 模拟API错误
      server.use(
        rest.get('/api/v1/ai/providers/', (req, res, ctx) => {
          return res(ctx.status(500), ctx.json({ error: 'Internal Server Error' }))
        })
      )

      // 重新挂载组件以触发错误
      wrapper.unmount()
      wrapper = mount(AIConfig, {
        global: {
          plugins: [pinia],
          stubs: {
            'router-link': true,
            'router-view': true,
          },
        },
      })

      await wrapper.vm.$nextTick()
      
      // 应该显示错误信息
      const errorMessage = wrapper.find('.error-message')
      expect(errorMessage.exists()).toBe(true)
    })
  })

  describe('数据刷新', () => {
    it('应该能够刷新数据', async () => {
      const refreshButton = wrapper.find('.refresh-btn')
      expect(refreshButton.exists()).toBe(true)
      
      // 模拟点击刷新按钮
      await refreshButton.trigger('click')
      await wrapper.vm.$nextTick()
      
      // 数据应该被重新加载
      expect(wrapper.vm.loading).toBe(false)
    })
  })
})
