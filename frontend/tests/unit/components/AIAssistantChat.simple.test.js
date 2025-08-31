import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import AIAssistantChat from '@/components/idiomatic-expressions/AIAssistantChat.vue'
import { createTestingPinia } from '@pinia/testing'

// Mock stores
vi.mock('@/stores/modules/learningStore', () => ({
  useLearningStore: vi.fn(),
}))

// Mock Element Plus message
global.ElMessage = {
  success: vi.fn(),
  error: vi.fn(),
}

global.ElMessageBox = {
  confirm: vi.fn(),
}

describe('AIAssistantChat', () => {
  let wrapper

  const mockExpression = {
    id: 1,
    expression: 'break the ice',
    meaning: '打破沉默，缓解尴尬气氛',
  }

  beforeEach(async () => {
    const { useLearningStore } = await import('@/stores/modules/learningStore')
    
    useLearningStore.mockReturnValue({
      loading: { ai_response: false },
      currentConversation: {
        value: {
          messages: [
            {
              id: 'msg-1',
              role: 'user',
              content: '你好',
              timestamp: '2024-01-15T10:00:00Z',
            },
          ],
        },
      },
      startAIConversation: vi.fn(),
      sendAIMessage: vi.fn().mockResolvedValue({}),
    })

    vi.clearAllMocks()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  describe('基础渲染', () => {
    it('应该正确渲染AI助教聊天界面', () => {
      wrapper = mount(AIAssistantChat, {
        global: {
          plugins: [createTestingPinia({ createSpy: vi.fn })],
          stubs: {
            'el-button': { template: '<button><slot /></button>' },
            'el-icon': { template: '<span><slot /></span>' },
            'el-dialog': { template: '<div><slot /></div>' },
            'el-input': { template: '<textarea></textarea>' },
          },
        },
        props: {},
      })

      expect(wrapper.find('.ai-assistant-chat').exists()).toBe(true)
      expect(wrapper.find('.chat-header').exists()).toBe(true)
      expect(wrapper.find('.chat-container').exists()).toBe(true)
    })

    it('应该显示AI助教信息', () => {
      wrapper = mount(AIAssistantChat, {
        global: {
          plugins: [createTestingPinia({ createSpy: vi.fn })],
          stubs: {
            'el-button': { template: '<button><slot /></button>' },
            'el-icon': { template: '<span><slot /></span>' },
            'el-dialog': { template: '<div><slot /></div>' },
            'el-input': { template: '<textarea></textarea>' },
          },
        },
        props: {},
      })

      const assistantInfo = wrapper.find('.assistant-info')
      expect(assistantInfo.exists()).toBe(true)
      expect(assistantInfo.text()).toContain('AI英语助教')
    })

    it('应该显示消息输入区域', () => {
      wrapper = mount(AIAssistantChat, {
        global: {
          plugins: [createTestingPinia({ createSpy: vi.fn })],
          stubs: {
            'el-button': { template: '<button><slot /></button>' },
            'el-icon': { template: '<span><slot /></span>' },
            'el-dialog': { template: '<div><slot /></div>' },
            'el-input': { template: '<textarea></textarea>' },
          },
        },
        props: {},
      })

      const chatInput = wrapper.find('.chat-input')
      expect(chatInput.exists()).toBe(true)
    })
  })

  describe('消息显示', () => {
    it('应该显示对话消息', () => {
      wrapper = mount(AIAssistantChat, {
        global: {
          plugins: [createTestingPinia({ createSpy: vi.fn })],
          stubs: {
            'el-button': { template: '<button><slot /></button>' },
            'el-icon': { template: '<span><slot /></span>' },
            'el-dialog': { template: '<div><slot /></div>' },
            'el-input': { template: '<textarea></textarea>' },
          },
        },
        props: {},
      })

      const messages = wrapper.findAll('.message-item')
      expect(messages.length).toBeGreaterThan(0)
    })
  })

  describe('工具函数', () => {
    it('应该正确格式化时间', () => {
      wrapper = mount(AIAssistantChat, {
        global: {
          plugins: [createTestingPinia({ createSpy: vi.fn })],
          stubs: {
            'el-button': { template: '<button><slot /></button>' },
            'el-icon': { template: '<span><slot /></span>' },
            'el-dialog': { template: '<div><slot /></div>' },
            'el-input': { template: '<textarea></textarea>' },
          },
        },
        props: {},
      })

      const recentTime = new Date().toISOString()
      expect(wrapper.vm.formatTime(recentTime)).toBe('刚刚')
    })

    it('应该正确获取上下文文本', () => {
      wrapper = mount(AIAssistantChat, {
        global: {
          plugins: [createTestingPinia({ createSpy: vi.fn })],
          stubs: {
            'el-button': { template: '<button><slot /></button>' },
            'el-icon': { template: '<span><slot /></span>' },
            'el-dialog': { template: '<div><slot /></div>' },
            'el-input': { template: '<textarea></textarea>' },
          },
        },
        props: {},
      })

      expect(wrapper.vm.getContextText('general')).toBe('通用对话')
      expect(wrapper.vm.getContextText('expression_help')).toBe('表达解释')
      expect(wrapper.vm.getContextText('practice')).toBe('练习对话')
      expect(wrapper.vm.getContextText('review')).toBe('复习指导')
    })

    it('应该格式化消息内容中的markdown', () => {
      wrapper = mount(AIAssistantChat, {
        global: {
          plugins: [createTestingPinia({ createSpy: vi.fn })],
          stubs: {
            'el-button': { template: '<button><slot /></button>' },
            'el-icon': { template: '<span><slot /></span>' },
            'el-dialog': { template: '<div><slot /></div>' },
            'el-input': { template: '<textarea></textarea>' },
          },
        },
        props: {},
      })

      const content = '这是**粗体**和*斜体*以及`代码`'
      const formatted = wrapper.vm.formatMessageContent(content)
      expect(formatted).toContain('<strong>粗体</strong>')
      expect(formatted).toContain('<em>斜体</em>')
      expect(formatted).toContain('<code>代码</code>')
    })
  })

  describe('表达式上下文', () => {
    it('有表达式上下文时应该显示表达式信息', () => {
      wrapper = mount(AIAssistantChat, {
        global: {
          plugins: [createTestingPinia({ createSpy: vi.fn })],
          stubs: {
            'el-button': { template: '<button><slot /></button>' },
            'el-icon': { template: '<span><slot /></span>' },
            'el-dialog': { template: '<div><slot /></div>' },
            'el-input': { template: '<textarea></textarea>' },
          },
        },
        props: {
          contextExpression: mockExpression,
        },
      })

      const contextInfo = wrapper.find('.expression-context')
      expect(contextInfo.exists()).toBe(true)
      expect(contextInfo.text()).toContain('break the ice')
    })
  })
})
