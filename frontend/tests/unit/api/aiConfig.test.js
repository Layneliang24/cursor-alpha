import { describe, it, expect, beforeEach, vi } from 'vitest'
import { aiConfigAPI } from '@/api/aiConfig'

// Mock axios
vi.mock('axios', () => ({
  default: {
    create: vi.fn(() => ({
      get: vi.fn(),
      post: vi.fn(),
      put: vi.fn(),
      delete: vi.fn(),
      patch: vi.fn(),
    })),
  },
}))

describe('AI Config API', () => {
  let mockAxios

  beforeEach(() => {
    vi.clearAllMocks()
    mockAxios = {
      get: vi.fn(),
      post: vi.fn(),
      put: vi.fn(),
      delete: vi.fn(),
      patch: vi.fn(),
    }
    vi.mocked(require('axios').default.create).mockReturnValue(mockAxios)
  })

  describe('Provider API', () => {
    it('should get providers list', async () => {
      const mockResponse = {
        data: [
          { id: 1, name: 'OpenAI', type: 'openai', status: 'active' },
          { id: 2, name: 'Anthropic', type: 'anthropic', status: 'active' }
        ]
      }
      mockAxios.get.mockResolvedValue(mockResponse)

      const result = await aiConfigAPI.providerAPI.getProviders()
      
      expect(mockAxios.get).toHaveBeenCalledWith('/api/v1/ai/providers/')
      expect(result).toEqual(mockResponse.data)
    })

    it('should create a new provider', async () => {
      const providerData = {
        name: 'Test Provider',
        type: 'openai',
        base_url: 'https://api.openai.com',
        api_version: 'v1'
      }
      const mockResponse = { data: { id: 1, ...providerData } }
      mockAxios.post.mockResolvedValue(mockResponse)

      const result = await aiConfigAPI.providerAPI.createProvider(providerData)
      
      expect(mockAxios.post).toHaveBeenCalledWith('/api/v1/ai/providers/', providerData)
      expect(result).toEqual(mockResponse.data)
    })

    it('should update a provider', async () => {
      const providerId = 1
      const updateData = { name: 'Updated Provider' }
      const mockResponse = { data: { id: providerId, ...updateData } }
      mockAxios.put.mockResolvedValue(mockResponse)

      const result = await aiConfigAPI.providerAPI.updateProvider(providerId, updateData)
      
      expect(mockAxios.put).toHaveBeenCalledWith(`/api/v1/ai/providers/${providerId}/`, updateData)
      expect(result).toEqual(mockResponse.data)
    })

    it('should delete a provider', async () => {
      const providerId = 1
      mockAxios.delete.mockResolvedValue({ status: 204 })

      await aiConfigAPI.providerAPI.deleteProvider(providerId)
      
      expect(mockAxios.delete).toHaveBeenCalledWith(`/api/v1/ai/providers/${providerId}/`)
    })
  })

  describe('Model API', () => {
    it('should get models list', async () => {
      const mockResponse = {
        data: [
          { id: 1, name: 'GPT-4', provider: 1, model_id: 'gpt-4' },
          { id: 2, name: 'Claude-3', provider: 2, model_id: 'claude-3' }
        ]
      }
      mockAxios.get.mockResolvedValue(mockResponse)

      const result = await aiConfigAPI.modelAPI.getModels()
      
      expect(mockAxios.get).toHaveBeenCalledWith('/api/v1/ai/models/')
      expect(result).toEqual(mockResponse.data)
    })

    it('should create a new model', async () => {
      const modelData = {
        name: 'Test Model',
        provider: 1,
        model_id: 'test-model',
        max_tokens: 4096,
        temperature: 0.7
      }
      const mockResponse = { data: { id: 1, ...modelData } }
      mockAxios.post.mockResolvedValue(mockResponse)

      const result = await aiConfigAPI.modelAPI.createModel(modelData)
      
      expect(mockAxios.post).toHaveBeenCalledWith('/api/v1/ai/models/', modelData)
      expect(result).toEqual(mockResponse.data)
    })
  })

  describe('API Key API', () => {
    it('should get API keys list', async () => {
      const mockResponse = {
        data: [
          { id: 1, name: 'OpenAI Key', provider: 1, is_active: true },
          { id: 2, name: 'Anthropic Key', provider: 2, is_active: true }
        ]
      }
      mockAxios.get.mockResolvedValue(mockResponse)

      const result = await aiConfigAPI.apiKeyAPI.getAPIKeys()
      
      expect(mockAxios.get).toHaveBeenCalledWith('/api/v1/ai/api-keys/')
      expect(result).toEqual(mockResponse.data)
    })

    it('should create a new API key', async () => {
      const keyData = {
        name: 'Test Key',
        provider: 1,
        key_value: 'sk-test-key'
      }
      const mockResponse = { data: { id: 1, ...keyData } }
      mockAxios.post.mockResolvedValue(mockResponse)

      const result = await aiConfigAPI.apiKeyAPI.createAPIKey(keyData)
      
      expect(mockAxios.post).toHaveBeenCalledWith('/api/v1/ai/api-keys/', keyData)
      expect(result).toEqual(mockResponse.data)
    })
  })

  describe('Model Config API', () => {
    it('should get model configs list', async () => {
      const mockResponse = {
        data: [
          { id: 1, name: 'Default Config', model: 1 },
          { id: 2, name: 'Custom Config', model: 2 }
        ]
      }
      mockAxios.get.mockResolvedValue(mockResponse)

      const result = await aiConfigAPI.modelConfigAPI.getModelConfigs()
      
      expect(mockAxios.get).toHaveBeenCalledWith('/api/v1/ai/model-configs/')
      expect(result).toEqual(mockResponse.data)
    })
  })

  describe('Token Usage API', () => {
    it('should get token usage statistics', async () => {
      const mockResponse = {
        data: {
          total_tokens: 1000000,
          total_cost: 50.0,
          usage_by_provider: [
            { provider: 'OpenAI', tokens: 600000, cost: 30.0 },
            { provider: 'Anthropic', tokens: 400000, cost: 20.0 }
          ]
        }
      }
      mockAxios.get.mockResolvedValue(mockResponse)

      const result = await aiConfigAPI.tokenUsageAPI.getTokenUsage()
      
      expect(mockAxios.get).toHaveBeenCalledWith('/api/v1/ai/token-usage/')
      expect(result).toEqual(mockResponse.data)
    })
  })

  describe('Error Handling', () => {
    it('should handle API errors properly', async () => {
      const errorResponse = {
        response: {
          status: 400,
          data: { error: 'Bad Request' }
        }
      }
      mockAxios.get.mockRejectedValue(errorResponse)

      await expect(aiConfigAPI.providerAPI.getProviders()).rejects.toThrow()
    })

    it('should handle network errors', async () => {
      const networkError = new Error('Network Error')
      mockAxios.get.mockRejectedValue(networkError)

      await expect(aiConfigAPI.providerAPI.getProviders()).rejects.toThrow('Network Error')
    })
  })
})
