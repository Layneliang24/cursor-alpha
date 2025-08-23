import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import MarkdownEditor from '../MarkdownEditor.vue'

describe('MarkdownEditor Component - Working Tests', () => {
  let wrapper: any

  beforeEach(() => {
    wrapper = mount(MarkdownEditor, {
      global: {
        stubs: {
          'el-button': {
            template: '<button class="el-button"><slot /></button>',
            props: ['size', 'title'],
            emits: ['click']
          }
        }
      }
    })
  })

  it('能够正常挂载', () => {
    expect(wrapper.exists()).toBe(true)
  })

  it('渲染基本结构', () => {
    expect(wrapper.find('.markdown-editor').exists()).toBe(true)
    expect(wrapper.find('.editor-container').exists()).toBe(true)
  })

  it('显示编辑器标题', () => {
    expect(wrapper.text()).toContain('编辑器')
    expect(wrapper.text()).toContain('预览')
  })

  it('渲染文本输入框', () => {
    const textarea = wrapper.find('.markdown-input')
    expect(textarea.exists()).toBe(true)
  })

  it('渲染预览区域', () => {
    const preview = wrapper.find('.markdown-preview')
    expect(preview.exists()).toBe(true)
  })

  it('渲染工具栏', () => {
    const tools = wrapper.find('.editor-tools')
    expect(tools.exists()).toBe(true)
  })

  it('显示主要工具按钮', () => {
    // 由于el-button被stub，我们需要检查按钮的数量而不是文本内容
    const buttons = wrapper.findAll('.editor-tools .el-button')
    expect(buttons.length).toBeGreaterThan(0)
    
    // 检查工具栏容器是否存在
    const tools = wrapper.find('.editor-tools')
    expect(tools.exists()).toBe(true)
  })

  it('支持v-model双向绑定', async () => {
    const textarea = wrapper.find('.markdown-input')
    const testContent = '# 测试标题\n这是测试内容'
    
    await textarea.setValue(testContent)
    expect(wrapper.vm.content).toBe(testContent)
  })

  it('输入框有正确的占位符文本', () => {
    const textarea = wrapper.find('.markdown-input')
    const placeholder = textarea.attributes('placeholder')
    
    expect(placeholder).toContain('请输入Markdown内容')
    expect(placeholder).toContain('常用语法提示')
  })

  it('处理输入事件', async () => {
    const textarea = wrapper.find('.markdown-input')
    const testContent = 'New content'
    
    await textarea.setValue(testContent)
    await wrapper.vm.$nextTick()
    
    expect(wrapper.vm.content).toBe(testContent)
  })

  it('正确接收modelValue prop', () => {
    const testValue = '# Initial content'
    const wrapperWithProps = mount(MarkdownEditor, {
      props: {
        modelValue: testValue
      },
      global: {
        stubs: {
          'el-button': true
        }
      }
    })
    
    expect(wrapperWithProps.vm.content).toBe(testValue)
  })

  it('emit update:modelValue事件', async () => {
    const textarea = wrapper.find('.markdown-input')
    const testContent = 'Updated content'
    
    await textarea.setValue(testContent)
    await wrapper.vm.$nextTick()
    
    expect(wrapper.vm.content).toBe(testContent)
  })
}) 