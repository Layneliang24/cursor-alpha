import { rest } from 'msw'

// Mock API响应数据
const mockData = {
  providers: [
    {
      id: 1,
      name: 'openai',
      provider_type: 'openai',
      display_name: 'OpenAI',
      base_url: 'https://api.openai.com',
      api_version: 'v1',
      is_active: true,
      is_healthy: true,
      created_at: '2024-01-15T10:00:00Z',
      updated_at: '2024-01-15T10:00:00Z'
    },
    {
      id: 2,
      name: 'anthropic',
      provider_type: 'anthropic',
      display_name: 'Anthropic',
      base_url: 'https://api.anthropic.com',
      api_version: 'v1',
      is_active: true,
      is_healthy: true,
      created_at: '2024-01-15T10:00:00Z',
      updated_at: '2024-01-15T10:00:00Z'
    }
  ],
  apiKeys: [
    {
      id: 1,
      name: 'OpenAI Key',
      provider: 1,
      key_prefix: 'sk-test',
      is_active: true,
      is_default: true,
      created_at: '2024-01-15T10:00:00Z'
    },
    {
      id: 2,
      name: 'Anthropic Key',
      provider: 2,
      key_prefix: 'sk-ant',
      is_active: true,
      is_default: false,
      created_at: '2024-01-15T10:00:00Z'
    }
  ],
  models: [
    {
      id: 1,
      name: 'GPT-4',
      provider: 1,
      model_id: 'gpt-4',
      max_tokens: 4096,
      temperature: 0.7,
      created_at: '2024-01-15T10:00:00Z'
    },
    {
      id: 2,
      name: 'Claude-3',
      provider: 2,
      model_id: 'claude-3',
      max_tokens: 8192,
      temperature: 0.5,
      created_at: '2024-01-15T10:00:00Z'
    }
  ],
  configs: [
    {
      id: 1,
      name: 'Default Config',
      model: 1,
      temperature: 0.7,
      max_tokens: 2048,
      top_p: 0.9,
      frequency_penalty: 0.0,
      presence_penalty: 0.0,
      created_at: '2024-01-15T10:00:00Z'
    }
  ],
  usage: [
    {
      id: 1,
      user: 1,
      provider: 1,
      model_name: 'gpt-4',
      prompt_tokens: 100,
      completion_tokens: 50,
      total_tokens: 150,
      cost: 0.003,
      created_at: '2024-01-15T10:00:00Z'
    }
  ],
  quotas: [
    {
      id: 1,
      user: 1,
      provider: 1,
      quota_type: 'daily',
      limit: 1000000,
      used: 500000,
      reset_date: '2024-01-16T00:00:00Z'
    }
  ],
  strategies: [
    {
      id: 1,
      name: 'Primary Strategy',
      priority: 1,
      providers: [1, 2],
      description: 'Primary failover strategy',
      created_at: '2024-01-15T10:00:00Z'
    }
  ]
}

// API处理器
export const handlers = [
  // 认证相关
  rest.post('/api/v1/auth/login/', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        access: 'mock-access-token',
        refresh: 'mock-refresh-token',
        user: {
          id: 1,
          username: 'testuser',
          email: 'test@example.com'
        }
      })
    )
  }),

  rest.post('/api/v1/auth/logout/', (req, res, ctx) => {
    return res(ctx.status(200), ctx.json({ message: 'Logged out successfully' }))
  }),

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

  rest.get('/api/v1/ai/providers/:id/', (req, res, ctx) => {
    const provider = mockData.providers.find(p => p.id === parseInt(req.params.id))
    if (!provider) {
      return res(ctx.status(404), ctx.json({ message: 'Provider not found' }))
    }
    return res(ctx.status(200), ctx.json(provider))
  }),

  rest.put('/api/v1/ai/providers/:id/', (req, res, ctx) => {
    const index = mockData.providers.findIndex(p => p.id === parseInt(req.params.id))
    if (index === -1) {
      return res(ctx.status(404), ctx.json({ message: 'Provider not found' }))
    }
    const updatedProvider = {
      ...mockData.providers[index],
      ...req.body,
      updated_at: new Date().toISOString()
    }
    mockData.providers[index] = updatedProvider
    return res(ctx.status(200), ctx.json(updatedProvider))
  }),

  rest.delete('/api/v1/ai/providers/:id/', (req, res, ctx) => {
    const index = mockData.providers.findIndex(p => p.id === parseInt(req.params.id))
    if (index === -1) {
      return res(ctx.status(404), ctx.json({ message: 'Provider not found' }))
    }
    mockData.providers.splice(index, 1)
    return res(ctx.status(204))
  }),

  // API密钥相关
  rest.get('/api/v1/ai/api-keys/', (req, res, ctx) => {
    return res(ctx.status(200), ctx.json(mockData.apiKeys))
  }),

  rest.post('/api/v1/ai/api-keys/', (req, res, ctx) => {
    const newKey = {
      id: mockData.apiKeys.length + 1,
      ...req.body,
      created_at: new Date().toISOString()
    }
    mockData.apiKeys.push(newKey)
    return res(ctx.status(201), ctx.json(newKey))
  }),

  rest.get('/api/v1/ai/api-keys/:id/', (req, res, ctx) => {
    const key = mockData.apiKeys.find(k => k.id === parseInt(req.params.id))
    if (!key) {
      return res(ctx.status(404), ctx.json({ message: 'API key not found' }))
    }
    return res(ctx.status(200), ctx.json(key))
  }),

  rest.put('/api/v1/ai/api-keys/:id/', (req, res, ctx) => {
    const index = mockData.apiKeys.findIndex(k => k.id === parseInt(req.params.id))
    if (index === -1) {
      return res(ctx.status(404), ctx.json({ message: 'API key not found' }))
    }
    const updatedKey = {
      ...mockData.apiKeys[index],
      ...req.body
    }
    mockData.apiKeys[index] = updatedKey
    return res(ctx.status(200), ctx.json(updatedKey))
  }),

  rest.delete('/api/v1/ai/api-keys/:id/', (req, res, ctx) => {
    const index = mockData.apiKeys.findIndex(k => k.id === parseInt(req.params.id))
    if (index === -1) {
      return res(ctx.status(404), ctx.json({ message: 'API key not found' }))
    }
    mockData.apiKeys.splice(index, 1)
    return res(ctx.status(204))
  }),

  // AI模型相关
  rest.get('/api/v1/ai/models/', (req, res, ctx) => {
    return res(ctx.status(200), ctx.json(mockData.models))
  }),

  rest.post('/api/v1/ai/models/', (req, res, ctx) => {
    const newModel = {
      id: mockData.models.length + 1,
      ...req.body,
      created_at: new Date().toISOString()
    }
    mockData.models.push(newModel)
    return res(ctx.status(201), ctx.json(newModel))
  }),

  // 模型配置相关
  rest.get('/api/v1/ai/model-configs/', (req, res, ctx) => {
    return res(ctx.status(200), ctx.json(mockData.configs))
  }),

  rest.post('/api/v1/ai/model-configs/', (req, res, ctx) => {
    const newConfig = {
      id: mockData.configs.length + 1,
      ...req.body,
      created_at: new Date().toISOString()
    }
    mockData.configs.push(newConfig)
    return res(ctx.status(201), ctx.json(newConfig))
  }),

  // Token使用量相关
  rest.get('/api/v1/ai/token-usage/', (req, res, ctx) => {
    return res(ctx.status(200), ctx.json(mockData.usage))
  }),

  rest.post('/api/v1/ai/token-usage/', (req, res, ctx) => {
    const newUsage = {
      id: mockData.usage.length + 1,
      ...req.body,
      created_at: new Date().toISOString()
    }
    mockData.usage.push(newUsage)
    return res(ctx.status(201), ctx.json(newUsage))
  }),

  // 使用配额相关
  rest.get('/api/v1/ai/usage-quotas/', (req, res, ctx) => {
    return res(ctx.status(200), ctx.json(mockData.quotas))
  }),

  // 故障转移策略相关
  rest.get('/api/v1/ai/failover-strategies/', (req, res, ctx) => {
    return res(ctx.status(200), ctx.json(mockData.strategies))
  }),

  rest.post('/api/v1/ai/failover-strategies/', (req, res, ctx) => {
    const newStrategy = {
      id: mockData.strategies.length + 1,
      ...req.body,
      created_at: new Date().toISOString()
    }
    mockData.strategies.push(newStrategy)
    return res(ctx.status(201), ctx.json(newStrategy))
  }),

  // 配置导入导出相关
  rest.get('/api/v1/ai/config/export/', (req, res, ctx) => {
    const exportData = {
      providers: mockData.providers,
      api_keys: mockData.apiKeys,
      models: mockData.models,
      configs: mockData.configs,
      strategies: mockData.strategies,
      export_date: new Date().toISOString()
    }
    return res(ctx.status(200), ctx.json(exportData))
  }),

  rest.post('/api/v1/ai/config/import/', (req, res, ctx) => {
    return res(ctx.status(200), ctx.json({ message: 'Configuration imported successfully' }))
  }),

  // 设置相关
  rest.get('/api/v1/ai/settings/', (req, res, ctx) => {
    return res(ctx.status(200), ctx.json({
      id: 1,
      user: 1,
      display_name: 'Test User',
      theme: 'light',
      language: 'zh-CN',
      timezone: 'Asia/Shanghai',
      email_notifications: true,
      push_notifications: false,
      created_at: '2024-01-15T10:00:00Z',
      updated_at: '2024-01-15T10:00:00Z'
    }))
  }),

  rest.put('/api/v1/ai/settings/', (req, res, ctx) => {
    return res(ctx.status(200), ctx.json({
      id: 1,
      user: 1,
      ...req.body,
      updated_at: new Date().toISOString()
    }))
  }),

  // 统计相关
  rest.get('/api/v1/ai/statistics/', (req, res, ctx) => {
    return res(ctx.status(200), ctx.json({
      total_requests: 1500,
      total_tokens: 250000,
      total_cost: 15.50,
      success_rate: 98.5,
      avg_response_time: 1.2,
      daily_usage: [
        { date: '2024-01-10', requests: 100, tokens: 15000, cost: 1.20 },
        { date: '2024-01-11', requests: 120, tokens: 18000, cost: 1.44 },
        { date: '2024-01-12', requests: 95, tokens: 14000, cost: 1.12 },
        { date: '2024-01-13', requests: 110, tokens: 16000, cost: 1.28 },
        { date: '2024-01-14', requests: 130, tokens: 20000, cost: 1.60 },
        { date: '2024-01-15', requests: 145, tokens: 22000, cost: 1.76 }
      ],
      provider_stats: [
        { provider: 'OpenAI', requests: 800, tokens: 120000, cost: 9.60 },
        { provider: 'Anthropic', requests: 700, tokens: 130000, cost: 5.90 }
      ]
    }))
  }),

  // 健康检查相关
  rest.get('/api/v1/ai/health/', (req, res, ctx) => {
    return res(ctx.status(200), ctx.json({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      services: {
        openai: { status: 'healthy', response_time: 0.8 },
        anthropic: { status: 'healthy', response_time: 1.2 },
        google: { status: 'degraded', response_time: 2.5 }
      }
    }))
  }),

  // 默认处理器 - 捕获未匹配的请求
  rest.all('*', (req, res, ctx) => {
    console.warn(`Unhandled ${req.method} request to ${req.url}`)
    return res(ctx.status(404), ctx.json({ message: 'Not found' }))
  })
]

// 导出Mock数据供测试使用
export { mockData }
