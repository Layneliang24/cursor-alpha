import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { ElMessage, ElMessageBox } from 'element-plus'
import FallbackConfig from '../FallbackConfig.vue'
import { aiConfigAPI } from '@/api/aiConfig'

// Mock API
vi.mock('@/api/aiConfig', () => ({
  aiConfigAPI: {
    getFailoverStrategies: vi.fn(),
    getProviders: vi.fn(),
    updateFailoverStrategy: vi.fn(),
    createFailoverStrategy: vi.fn(),
    deleteFailoverStrategy: vi.fn(),
    switchProvider: vi.fn(),
    getStrategyAuditLogs: vi.fn()
  }
}))

// Mock Element Plus components
vi.mock('element-plus', () => ({
  ElMessage: {
    success: vi.fn(),
    error: vi.fn(),
    info: vi.fn()
  },
  ElMessageBox: {
    confirm: vi.fn()
  }
}))

// Mock vuedraggable
vi.mock('vuedraggable', () => ({
  default: {
    name: 'draggable',
    template: '<div><slot /></div>'
  }
}))

describe('FallbackConfig', () => {
  let wrapper

  const mockStrategies = [
    {
      id: 1,
      name: '测试策略1',
      description: '测试描述1',
      is_active: true,
      strategy_mode: 'priority',
      fail_threshold: 3,
      recovery_threshold: 2,
      cooldown: 60,
      jitter_window: 30,
      primary_provider: {
        id: 1,
        display_name: 'OpenAI',
        is_healthy: true
      },
      active_provider: {
        id: 1,
        display_name: 'OpenAI',
        is_healthy: true
      },
      provider_list: [
        {
          id: 1,
          display_name: 'OpenAI',
          provider_type: 'openai',
          is_healthy: true
        },
        {
          id: 2,
          display_name: 'Anthropic',
          provider_type: 'anthropic',
          is_healthy: true
        }
      ],
      enable_model_whitelist: false,
      allowed_models: []
    }
  ]

  const mockProviders = [
    {
      id: 1,
      display_name: 'OpenAI',
      provider_type: 'openai',
      is_healthy: true
    },
    {
      id: 2,
      display_name: 'Anthropic',
      provider_type: 'anthropic',
      is_healthy: true
    }
  ]

  beforeEach(() => {
    // Reset mocks
    vi.clearAllMocks()
    
    // Setup API mocks
    aiConfigAPI.getFailoverStrategies.mockResolvedValue({
      data: { results: mockStrategies }
    })
    aiConfigAPI.getProviders.mockResolvedValue({
      data: { results: mockProviders }
    })
    
    // Mount component
    wrapper = mount(FallbackConfig, {
      global: {
        stubs: {
          'el-dialog': true,
          'el-form': true,
          'el-form-item': true,
          'el-input': true,
          'el-select': true,
          'el-option': true,
          'el-radio-group': true,
          'el-radio': true,
          'el-input-number': true,
          'el-switch': true,
          'el-button': true,
          'el-dropdown': true,
          'el-dropdown-menu': true,
          'el-dropdown-item': true,
          'el-tag': true,
          'el-table': true,
          'el-table-column': true,
          'el-date-picker': true,
          'el-checkbox-group': true,
          'el-checkbox': true,
          'el-icon': true,
          'draggable': true,
          ModelWhitelistDialog: true
        }
      }
    })
  })

  describe('组件初始化', () => {
    it('应该正确加载策略和提供商数据', async () => {
      await wrapper.vm.$nextTick()
      
      expect(aiConfigAPI.getFailoverStrategies).toHaveBeenCalled()
      expect(aiConfigAPI.getProviders).toHaveBeenCalled()
      expect(wrapper.vm.strategies).toEqual(mockStrategies)
      expect(wrapper.vm.availableProviders).toEqual(mockProviders)
    })

    it('应该处理API错误', async () => {
      aiConfigAPI.getFailoverStrategies.mockRejectedValue(new Error('API Error'))
      
      await wrapper.vm.loadStrategies()
      
      expect(ElMessage.error).toHaveBeenCalledWith('加载策略列表失败')
    })
  })

  describe('策略管理', () => {
    it('应该能够创建新策略', async () => {
      const strategyData = {
        name: '新策略',
        description: '新策略描述',
        primary_provider: 1,
        strategy_mode: 'priority',
        fail_threshold: 3,
        recovery_threshold: 2,
        cooldown: 60,
        jitter_window: 30,
        is_active: true
      }
      
      aiConfigAPI.createFailoverStrategy.mockResolvedValue({ data: { id: 2 } })
      
      Object.assign(wrapper.vm.strategyForm, strategyData)
      wrapper.vm.strategyFormRef = { validate: vi.fn().mockResolvedValue() }
      
      await wrapper.vm.saveStrategy()
      
      expect(aiConfigAPI.createFailoverStrategy).toHaveBeenCalledWith(strategyData)
      expect(ElMessage.success).toHaveBeenCalledWith('策略创建成功')
    })

    it('应该能够更新策略', async () => {
      const strategyData = {
        name: '更新策略',
        description: '更新策略描述',
        primary_provider: 1,
        strategy_mode: 'priority',
        fail_threshold: 3,
        recovery_threshold: 2,
        cooldown: 60,
        jitter_window: 30,
        is_active: true
      }
      
      aiConfigAPI.updateFailoverStrategy.mockResolvedValue({ data: { id: 1 } })
      
      wrapper.vm.isEdit = true
      wrapper.vm.currentStrategy = mockStrategies[0]
      Object.assign(wrapper.vm.strategyForm, strategyData)
      wrapper.vm.strategyFormRef = { validate: vi.fn().mockResolvedValue() }
      
      await wrapper.vm.saveStrategy()
      
      expect(aiConfigAPI.updateFailoverStrategy).toHaveBeenCalledWith(1, strategyData)
      expect(ElMessage.success).toHaveBeenCalledWith('策略更新成功')
    })

    it('应该能够删除策略', async () => {
      ElMessageBox.confirm.mockResolvedValue()
      aiConfigAPI.deleteFailoverStrategy.mockResolvedValue()
      
      await wrapper.vm.deleteStrategy(mockStrategies[0])
      
      expect(ElMessageBox.confirm).toHaveBeenCalled()
      expect(aiConfigAPI.deleteFailoverStrategy).toHaveBeenCalledWith(1)
      expect(ElMessage.success).toHaveBeenCalledWith('策略删除成功')
    })

    it('应该能够切换策略状态', async () => {
      aiConfigAPI.updateFailoverStrategy.mockResolvedValue()
      
      await wrapper.vm.toggleStrategyStatus(mockStrategies[0])
      
      expect(aiConfigAPI.updateFailoverStrategy).toHaveBeenCalledWith(1, {
        is_active: true
      })
      expect(ElMessage.success).toHaveBeenCalledWith('策略已启用')
    })
  })

  describe('提供商管理', () => {
    it('应该能够手动切换提供商', async () => {
      aiConfigAPI.switchProvider.mockResolvedValue()
      
      wrapper.vm.currentStrategy = mockStrategies[0]
      wrapper.vm.targetProvider = mockProviders[1]
      wrapper.vm.currentProvider = mockProviders[0]
      wrapper.vm.switchReason = '测试切换'
      
      await wrapper.vm.confirmSwitch()
      
      expect(aiConfigAPI.switchProvider).toHaveBeenCalledWith(1, {
        target_provider: 2,
        reason: '测试切换'
      })
      expect(ElMessage.success).toHaveBeenCalledWith('提供商切换成功')
    })

    it('应该能够移除提供商', async () => {
      ElMessageBox.confirm.mockResolvedValue()
      
      await wrapper.vm.removeProvider(mockStrategies[0], mockProviders[1])
      
      expect(ElMessageBox.confirm).toHaveBeenCalled()
      expect(ElMessage.success).toHaveBeenCalledWith('提供商已移除')
    })
  })

  describe('审计日志', () => {
    it('应该能够加载审计日志', async () => {
      const mockLogs = [
        {
          id: 1,
          action_type: 'manual_switch',
          from_provider: 'OpenAI',
          to_provider: 'Anthropic',
          reason: '测试切换',
          operator: 'admin',
          created_at: '2024-01-01T10:00:00Z'
        }
      ]
      
      aiConfigAPI.getStrategyAuditLogs.mockResolvedValue({
        data: { results: mockLogs }
      })
      
      wrapper.vm.currentStrategy = mockStrategies[0]
      await wrapper.vm.loadAuditLogs()
      
      expect(aiConfigAPI.getStrategyAuditLogs).toHaveBeenCalledWith(1, {})
      expect(wrapper.vm.auditLogs).toEqual(mockLogs)
    })
  })

  describe('工具函数', () => {
    it('应该正确获取提供商状态类型', () => {
      expect(wrapper.vm.getProviderStatusType(mockProviders[0])).toBe('success')
      expect(wrapper.vm.getProviderStatusType({ is_healthy: false })).toBe('danger')
      expect(wrapper.vm.getProviderStatusType(null)).toBe('info')
    })

    it('应该正确获取策略模式文本', () => {
      expect(wrapper.vm.getStrategyModeText('priority')).toBe('优先级')
      expect(wrapper.vm.getStrategyModeText('round_robin')).toBe('轮询')
      expect(wrapper.vm.getStrategyModeText('unknown')).toBe('unknown')
    })

    it('应该正确获取操作类型标签', () => {
      expect(wrapper.vm.getActionTypeTag('auto_switch')).toBe('warning')
      expect(wrapper.vm.getActionTypeTag('manual_switch')).toBe('primary')
      expect(wrapper.vm.getActionTypeTag('recovery')).toBe('success')
      expect(wrapper.vm.getActionTypeTag('health_check')).toBe('info')
    })

    it('应该正确获取操作类型文本', () => {
      expect(wrapper.vm.getActionTypeText('auto_switch')).toBe('自动切换')
      expect(wrapper.vm.getActionTypeText('manual_switch')).toBe('手动切换')
      expect(wrapper.vm.getActionTypeText('recovery')).toBe('恢复')
      expect(wrapper.vm.getActionTypeText('health_check')).toBe('健康检查')
    })
  })

  describe('错误处理', () => {
    it('应该处理保存策略时的错误', async () => {
      const error = {
        response: {
          data: {
            message: '策略名称已存在'
          }
        }
      }
      
      aiConfigAPI.createFailoverStrategy.mockRejectedValue(error)
      wrapper.vm.strategyFormRef = { validate: vi.fn().mockResolvedValue() }
      
      await wrapper.vm.saveStrategy()
      
      expect(ElMessage.error).toHaveBeenCalledWith('策略名称已存在')
    })

    it('应该处理切换提供商时的错误', async () => {
      const error = {
        response: {
          data: {
            message: '提供商不可用'
          }
        }
      }
      
      aiConfigAPI.switchProvider.mockRejectedValue(error)
      wrapper.vm.targetProvider = mockProviders[1]
      
      await wrapper.vm.confirmSwitch()
      
      expect(ElMessage.error).toHaveBeenCalledWith('切换提供商失败')
    })
  })
})
