import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import { rest } from 'msw'
import { setupServer } from 'msw/node'
import { mockData } from '../../../src/mocks/handlers'
import aiConfigAPI from '../../../src/api/aiConfig'

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
  
  rest.post('/api/v1/ai/api-keys/', (req, res, ctx) => {
    const newKey = {
      id: mockData.apiKeys.length + 1,
      ...req.body,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }
    mockData.apiKeys.push(newKey)
    return res(ctx.status(201), ctx.json(newKey))
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

describe('AI配置API集成测试', () => {
  let pinia

  beforeEach(() => {
    pinia = createTestingPinia({
      createSpy: vi.fn,
      stubActions: false,
    })
  })

  describe('AI提供商API', () => {
    it('应该成功获取AI提供商列表', async () => {
      const providers = await aiConfigAPI.get('/providers/')
      
      expect(providers).toBeDefined()
      expect(Array.isArray(providers)).toBe(true)
      expect(providers.length).toBeGreaterThan(0)
      expect(providers[0]).toHaveProperty('id')
      expect(providers[0]).toHaveProperty('name')
      expect(providers[0]).toHaveProperty('provider_type')
    })

    it('应该成功创建新的AI提供商', async () => {
      const newProvider = {
        name: 'test_provider',
        provider_type: 'openai',
        display_name: 'Test Provider',
        base_url: 'https://api.test.com',
        api_version: 'v1',
        is_active: true
      }

      const createdProvider = await aiConfigAPI.post('/providers/', newProvider)
      
      expect(createdProvider).toBeDefined()
      expect(createdProvider.name).toBe(newProvider.name)
      expect(createdProvider.provider_type).toBe(newProvider.provider_type)
      expect(createdProvider.id).toBeDefined()
    })

    it('应该处理API错误响应', async () => {
      // 模拟服务器错误
      server.use(
        rest.get('/api/v1/ai/providers/', (req, res, ctx) => {
          return res(ctx.status(500), ctx.json({ error: 'Internal Server Error' }))
        })
      )

      await expect(aiConfigAPI.get('/providers/')).rejects.toThrow()
    })
  })

  describe('API密钥API', () => {
    it('应该成功获取API密钥列表', async () => {
      const apiKeys = await aiConfigAPI.get('/api-keys/')
      
      expect(apiKeys).toBeDefined()
      expect(Array.isArray(apiKeys)).toBe(true)
      expect(apiKeys.length).toBeGreaterThan(0)
      expect(apiKeys[0]).toHaveProperty('id')
      expect(apiKeys[0]).toHaveProperty('key_name')
      expect(apiKeys[0]).toHaveProperty('provider')
    })

    it('应该成功创建新的API密钥', async () => {
      const newKey = {
        key_name: 'test_key',
        provider: 1,
        api_key: 'sk-test123456789',
        is_active: true
      }

      const createdKey = await aiConfigAPI.post('/api-keys/', newKey)
      
      expect(createdKey).toBeDefined()
      expect(createdKey.key_name).toBe(newKey.key_name)
      expect(createdKey.provider).toBe(newKey.provider)
      expect(createdKey.id).toBeDefined()
    })
  })

  describe('AI模型API', () => {
    it('应该成功获取AI模型列表', async () => {
      const models = await aiConfigAPI.get('/models/')
      
      expect(models).toBeDefined()
      expect(Array.isArray(models)).toBe(true)
      expect(models.length).toBeGreaterThan(0)
      expect(models[0]).toHaveProperty('id')
      expect(models[0]).toHaveProperty('name')
      expect(models[0]).toHaveProperty('provider')
    })
  })

  describe('模型配置API', () => {
    it('应该成功获取模型配置列表', async () => {
      const configs = await aiConfigAPI.get('/model-configs/')
      
      expect(configs).toBeDefined()
      expect(Array.isArray(configs)).toBe(true)
      expect(configs.length).toBeGreaterThan(0)
      expect(configs[0]).toHaveProperty('id')
      expect(configs[0]).toHaveProperty('name')
      expect(configs[0]).toHaveProperty('model')
    })
  })

  describe('统计信息API', () => {
    it('应该成功获取统计信息', async () => {
      const statistics = await aiConfigAPI.get('/statistics/')
      
      expect(statistics).toBeDefined()
      expect(statistics).toHaveProperty('total_requests')
      expect(statistics).toHaveProperty('total_tokens')
      expect(statistics).toHaveProperty('total_cost')
      expect(statistics).toHaveProperty('providers')
    })
  })

  describe('健康检查API', () => {
    it('应该成功获取健康状态', async () => {
      const health = await aiConfigAPI.get('/health/')
      
      expect(health).toBeDefined()
      expect(health).toHaveProperty('status')
      expect(health).toHaveProperty('timestamp')
      expect(health).toHaveProperty('services')
    })
  })
})
