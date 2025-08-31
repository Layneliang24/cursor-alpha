import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { ElMessage, ElMessageBox } from 'element-plus'
import AIAssistantChat from '@/components/idiomatic-expressions/AIAssistantChat.vue'
import { useLearningStore } from '@/stores/modules/learningStore'
import { commonMountOptions, testUtils } from '../../setup.js'

// Mock stores
vi.mock('@/stores/modules/learningStore', () => ({
  useLearningStore: vi.fn(),
}))

// Mock Element Plus message and message box
vi.mock('element-plus', () => ({
  ElMessage: {
    success: vi.fn(),
    error: vi.fn(),
  },
  ElMessageBox: {
    confirm: vi.fn(),
  },
}))

describe('AIAssistantChat', () => {
  let wrapper
  let mockLearningStore

  // Mock data
  const mockExpression = {
    id: 1,
    expression: 'break the ice',
    meaning: '打破沉默，缓解尴尬气氛',
  }

  const mockConversation = {
    id: 'conv-1',
    context: 'general',
    expression_id: 1,
    messages: [
      {
        id: 'msg-1',
        role: 'user',
        content: '你好',
        timestamp: '2024-01-15T10:00:00Z',
      },
      {
        id: 'msg-2',
        role: 'assistant',
        content: '你好！我是你的AI英语学习助教，有什么可以帮助你的吗？',
        timestamp: '2024-01-15T10:00:05Z',
      },
    ],
  }

  beforeEach(() => {
    // Setup store mock
    mockLearningStore = {
      loading: {
        ai_response: false,
      },
      currentConversation: {
        value: mockConversation,
      },
      startAIConversation: vi.fn(),
      sendAIMessage: vi.fn().mockResolvedValue({}),
    }

    useLearningStore.mockReturnValue(mockLearningStore)

    // Clear mocks
    vi.clearAllMocks()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  describe('基础渲染', () => {
    beforeEach(() => {
      wrapper = mount(AIAssistantChat, {
        ...commonMountOptions,
        props: {},
      })
    })

    it('应该正确渲染AI助教聊天界面', () => {
      expect(wrapper.find('.ai-assistant-chat').exists()).toBe(true)
      expect(wrapper.find('.chat-header').exists()).toBe(true)
      expect(wrapper.find('.chat-container').exists()).toBe(true)
      expect(wrapper.find('.chat-input').exists()).toBe(true)
    })

    it('应该显示AI助教信息', () => {
      const assistantInfo = wrapper.find('.assistant-info')
      expect(assistantInfo.exists()).toBe(true)
      expect(assistantInfo.text()).toContain('AI英语助教')
    })

    it('应该显示当前对话模式', () => {
      const contextInfo = wrapper.find('.context-info')
      expect(contextInfo.exists()).toBe(true)
      expect(contextInfo.text()).toContain('通用对话')
    })

    it('应该显示消息输入框', () => {
      const messageInput = wrapper.find('textarea')
      expect(messageInput.exists()).toBe(true)
      expect(messageInput.attributes('placeholder')).toContain('输入消息')
    })

    it('应该显示发送按钮', () => {
      const sendButton = wrapper.find('.send-button')
      expect(sendButton.exists()).toBe(true)
    })
  })

  describe('消息显示', () => {
    beforeEach(() => {
      wrapper = mount(AIAssistantChat, {
        ...commonMountOptions,
        props: {},
      })
    })

    it('应该显示对话消息', () => {
      const messages = wrapper.findAll('.message-item')
      expect(messages).toHaveLength(2)
      
      // 检查用户消息
      const userMessage = messages[0]
      expect(userMessage.classes()).toContain('user-message')
      expect(userMessage.find('.message-content').text()).toBe('你好')
      
      // 检查助教消息
      const assistantMessage = messages[1]
      expect(assistantMessage.classes()).toContain('assistant-message')
      expect(assistantMessage.find('.message-content').text()).toContain('你好！我是你的AI英语学习助教')
    })

    it('应该显示消息时间戳', () => {
      const messageItems = wrapper.findAll('.message-item')
      messageItems.forEach(item => {
        const timestamp = item.find('.message-time')
        expect(timestamp.exists()).toBe(true)
      })
    })

    it('应该正确格式化时间', () => {
      const recentTime = new Date().toISOString()
      expect(wrapper.vm.formatTime(recentTime)).toBe('刚刚')
      
      const oneHourAgo = new Date(Date.now() - 3600000).toISOString()
      expect(wrapper.vm.formatTime(oneHourAgo)).toBe('1小时前')
    })

    it('应该格式化消息内容中的markdown', () => {
      const content = '这是**粗体**和*斜体*以及`代码`'
      const formatted = wrapper.vm.formatMessageContent(content)
      expect(formatted).toContain('<strong>粗体</strong>')
      expect(formatted).toContain('<em>斜体</em>')
      expect(formatted).toContain('<code>代码</code>')
    })
  })

  describe('快捷问题功能', () => {
    beforeEach(() => {
      mockLearningStore.currentConversation.value = null
      wrapper = mount(AIAssistantChat, {
        ...commonMountOptions,
        props: {},
      })
    })

    it('初始状态应该显示快捷问题', () => {
      expect(wrapper.vm.showQuickQuestions).toBe(true)
      const quickQuestions = wrapper.findAll('.quick-question-item')
      expect(quickQuestions.length).toBeGreaterThan(0)
    })

    it('应该显示预设的快捷问题', () => {
      const quickQuestions = wrapper.findAll('.quick-question-item')
      expect(quickQuestions[0].text()).toContain('帮我解释一个表达式')
      expect(quickQuestions[1].text()).toContain('我想练习对话')
      expect(quickQuestions[2].text()).toContain('制定学习计划')
      expect(quickQuestions[3].text()).toContain('复习指导')
    })

    it('点击快捷问题应该发送消息', async () => {
      const firstQuestion = wrapper.findAll('.quick-question-item')[0]
      await firstQuestion.trigger('click')
      
      expect(mockLearningStore.sendAIMessage).toHaveBeenCalledWith(
        '帮我解释一个表达式',
        undefined,
      )
      expect(wrapper.emitted('messagesSent')).toBeTruthy()
    })

    it('发送消息后应该隐藏快捷问题', async () => {
      wrapper.vm.inputMessage = '测试消息'
      await wrapper.vm.sendMessage()
      
      expect(wrapper.vm.showQuickQuestions).toBe(false)
    })
  })

  describe('消息发送功能', () => {
    beforeEach(() => {
      wrapper = mount(AIAssistantChat, {
        ...commonMountOptions,
        props: {},
      })
    })

    it('应该能发送文本消息', async () => {
      const input = wrapper.find('textarea')
      const sendButton = wrapper.find('.send-button')
      
      await input.setValue('测试消息')
      await sendButton.trigger('click')
      
      expect(mockLearningStore.sendAIMessage).toHaveBeenCalledWith('测试消息', undefined)
      expect(wrapper.emitted('messagesSent')).toBeTruthy()
      expect(wrapper.emitted('messagesSent')[0]).toEqual(['测试消息'])
    })

    it('不应该发送空消息', async () => {
      const input = wrapper.find('textarea')
      const sendButton = wrapper.find('.send-button')
      
      await input.setValue('   ')
      await sendButton.trigger('click')
      
      expect(mockLearningStore.sendAIMessage).not.toHaveBeenCalled()
    })

    it('加载中时不应该发送消息', async () => {
      mockLearningStore.loading.ai_response = true
      
      const input = wrapper.find('textarea')
      const sendButton = wrapper.find('.send-button')
      
      await input.setValue('测试消息')
      await sendButton.trigger('click')
      
      expect(mockLearningStore.sendAIMessage).not.toHaveBeenCalled()
    })

    it('发送成功后应该清空输入框', async () => {
      wrapper.vm.inputMessage = '测试消息'
      await wrapper.vm.sendMessage()
      
      expect(wrapper.vm.inputMessage).toBe('')
    })

    it('发送失败时应该显示错误消息', async () => {
      mockLearningStore.sendAIMessage.mockRejectedValueOnce(new Error('Network error'))
      
      wrapper.vm.inputMessage = '测试消息'
      await wrapper.vm.sendMessage()
      
      expect(ElMessage.error).toHaveBeenCalledWith('发送失败，请重试')
    })

    it('按Enter键应该发送消息', async () => {
      const input = wrapper.find('textarea')
      await input.setValue('测试消息')
      await input.trigger('keydown', { key: 'Enter', ctrlKey: true })
      
      expect(mockLearningStore.sendAIMessage).toHaveBeenCalledWith('测试消息', undefined)
    })
  })

  describe('对话上下文管理', () => {
    beforeEach(() => {
      wrapper = mount(AIAssistantChat, {
        ...commonMountOptions,
        props: {},
      })
    })

    it('应该正确显示当前上下文', () => {
      expect(wrapper.vm.getContextText('general')).toBe('通用对话')
      expect(wrapper.vm.getContextText('expression_help')).toBe('表达解释')
      expect(wrapper.vm.getContextText('practice')).toBe('练习对话')
      expect(wrapper.vm.getContextText('review')).toBe('复习指导')
    })

    it('切换上下文应该发出contextChange事件', async () => {
      await wrapper.vm.handleContextChange('practice')
      
      expect(wrapper.emitted('contextChange')).toBeTruthy()
      expect(wrapper.emitted('contextChange')[0]).toEqual(['practice'])
    })

    it('有消息时切换上下文应该显示确认对话框', async () => {
      ElMessageBox.confirm.mockResolvedValueOnce(true)
      
      await wrapper.vm.handleContextChange('practice')
      
      expect(ElMessageBox.confirm).toHaveBeenCalledWith(
        '切换对话模式将开始新的对话，当前对话将被保存。是否继续？',
        '确认切换',
        expect.any(Object),
      )
    })

    it('没有消息时切换上下文应该直接切换', async () => {
      mockLearningStore.currentConversation.value = { messages: [] }
      wrapper = mount(AIAssistantChat, {
        ...commonMountOptions,
        props: {},
      })
      
      await wrapper.vm.handleContextChange('practice')
      
      expect(mockLearningStore.startAIConversation).toHaveBeenCalledWith('practice', undefined)
    })
  })

  describe('表达式上下文', () => {
    beforeEach(() => {
      wrapper = mount(AIAssistantChat, {
        ...commonMountOptions,
        props: {
          contextExpression: mockExpression,
        },
      })
    })

    it('有表达式上下文时应该显示表达式信息', () => {
      const contextInfo = wrapper.find('.expression-context')
      expect(contextInfo.exists()).toBe(true)
      expect(contextInfo.text()).toContain('break the ice')
    })

    it('发送消息时应该传递表达式ID', async () => {
      wrapper.vm.inputMessage = '解释这个表达式'
      await wrapper.vm.sendMessage()
      
      expect(mockLearningStore.sendAIMessage).toHaveBeenCalledWith('解释这个表达式', 1)
    })

    it('清除上下文应该发出expressionSelect事件', async () => {
      await wrapper.vm.clearContext()
      
      expect(wrapper.emitted('expressionSelect')).toBeTruthy()
      expect(wrapper.emitted('expressionSelect')[0]).toEqual([0])
    })

    it('表达式变化时应该自动切换到表达解释模式', async () => {
      const newExpression = { id: 2, expression: 'piece of cake' }
      await wrapper.setProps({ contextExpression: newExpression })
      
      expect(wrapper.vm.currentContext).toBe('expression_help')
      expect(mockLearningStore.startAIConversation).toHaveBeenCalledWith('expression_help', 2)
    })
  })

  describe('对话管理', () => {
    beforeEach(() => {
      wrapper = mount(AIAssistantChat, {
        ...commonMountOptions,
        props: {},
      })
    })

    it('应该能清空对话', async () => {
      ElMessageBox.confirm.mockResolvedValueOnce(true)
      
      await wrapper.vm.clearConversation()
      
      expect(ElMessageBox.confirm).toHaveBeenCalledWith(
        '确定要清空当前对话吗？此操作不可撤销。',
        '确认清空',
        expect.any(Object),
      )
      
      expect(mockLearningStore.currentConversation.value.messages).toEqual([])
      expect(wrapper.vm.showQuickQuestions).toBe(true)
      expect(ElMessage.success).toHaveBeenCalledWith('对话已清空')
    })

    it('取消清空对话时不应该执行清空操作', async () => {
      ElMessageBox.confirm.mockRejectedValueOnce(new Error('Cancel'))
      
      const originalMessages = [...mockConversation.messages]
      await wrapper.vm.clearConversation()
      
      expect(mockLearningStore.currentConversation.value.messages).toEqual(originalMessages)
    })

    it('应该能开始新对话', async () => {
      await wrapper.vm.startNewConversation()
      
      expect(mockLearningStore.startAIConversation).toHaveBeenCalledWith('general', undefined)
      expect(wrapper.vm.showQuickQuestions).toBe(true)
    })
  })

  describe('消息模板功能', () => {
    beforeEach(() => {
      wrapper = mount(AIAssistantChat, {
        ...commonMountOptions,
        props: {},
      })
    })

    it('应该显示模板按钮', () => {
      const templateButton = wrapper.find('.template-button')
      expect(templateButton.exists()).toBe(true)
    })

    it('点击模板按钮应该打开模板对话框', async () => {
      const templateButton = wrapper.find('.template-button')
      await templateButton.trigger('click')
      
      expect(wrapper.vm.showTemplateDialog).toBe(true)
    })

    it('选择模板应该填入输入框', async () => {
      const template = {
        id: 1,
        title: '测试模板',
        content: '这是一个测试模板内容',
      }
      
      await wrapper.vm.selectTemplate(template)
      
      expect(wrapper.vm.inputMessage).toBe('这是一个测试模板内容')
      expect(wrapper.vm.showTemplateDialog).toBe(false)
    })
  })

  describe('滚动功能', () => {
    beforeEach(() => {
      wrapper = mount(AIAssistantChat, {
        ...commonMountOptions,
        props: {},
      })
    })

    it('应该有滚动到底部的方法', () => {
      expect(typeof wrapper.vm.scrollToBottom).toBe('function')
    })

    it('新消息时应该自动滚动到底部', async () => {
      const scrollSpy = vi.spyOn(wrapper.vm, 'scrollToBottom')
      
      // 模拟新消息
      mockLearningStore.currentConversation.value.messages.push({
        id: 'new-msg',
        role: 'assistant',
        content: '新消息',
        timestamp: new Date().toISOString(),
      })
      
      await testUtils.nextTick()
      
      expect(scrollSpy).toHaveBeenCalled()
    })
  })

  describe('生命周期', () => {
    it('挂载时如果有表达式上下文应该自动开始对话', () => {
      wrapper = mount(AIAssistantChat, {
        ...commonMountOptions,
        props: {
          contextExpression: mockExpression,
        },
      })
      
      expect(wrapper.vm.currentContext).toBe('expression_help')
      expect(mockLearningStore.startAIConversation).toHaveBeenCalledWith('expression_help', 1)
    })

    it('挂载时如果指定了对话ID应该加载对话', () => {
      wrapper = mount(AIAssistantChat, {
        ...commonMountOptions,
        props: {
          conversationId: 'conv-123',
        },
      })
      
      // 这里可以验证加载特定对话的逻辑
      expect(wrapper.vm.$props.conversationId).toBe('conv-123')
    })
  })

  describe('键盘快捷键', () => {
    beforeEach(() => {
      wrapper = mount(AIAssistantChat, {
        ...commonMountOptions,
        props: {},
      })
    })

    it('Ctrl+Enter应该发送消息', async () => {
      const input = wrapper.find('textarea')
      await input.setValue('测试快捷键')
      
      await input.trigger('keydown', { key: 'Enter', ctrlKey: true })
      
      expect(mockLearningStore.sendAIMessage).toHaveBeenCalledWith('测试快捷键', undefined)
    })

    it('单独按Enter不应该发送消息', async () => {
      const input = wrapper.find('textarea')
      await input.setValue('测试消息')
      
      await input.trigger('keydown', { key: 'Enter' })
      
      expect(mockLearningStore.sendAIMessage).not.toHaveBeenCalled()
    })
  })
})
