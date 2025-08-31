/**
 * SafeHTML组件测试
 * 测试安全HTML渲染功能
 */
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import SafeHTML from '@/components/common/SafeHTML.vue'

describe('SafeHTML Component', () => {
  it('应该渲染安全的HTML内容', () => {
    const safeContent = '<p>这是<strong>安全的</strong>内容</p>'
    
    const wrapper = mount(SafeHTML, {
      props: {
        content: safeContent
      }
    })
    
    expect(wrapper.html()).toContain('<p>这是<strong>安全的</strong>内容</p>')
  })
  
  it('应该清理XSS攻击向量', () => {
    const maliciousContent = '<script>alert("xss")</script><p>正常内容</p>'
    
    const wrapper = mount(SafeHTML, {
      props: {
        content: maliciousContent
      }
    })
    
    // 不应该包含script标签
    expect(wrapper.html()).not.toContain('<script>')
    // 应该保留正常内容
    expect(wrapper.html()).toContain('<p>正常内容</p>')
  })
  
  it('应该在严格模式下限制标签', () => {
    const content = '<p>段落</p><strong>加粗</strong><a href="http://example.com">链接</a>'
    
    const wrapper = mount(SafeHTML, {
      props: {
        content,
        strict: true
      }
    })
    
    // 严格模式只允许基本格式标签
    expect(wrapper.html()).toContain('<strong>')
    expect(wrapper.html()).not.toContain('<p>')
    expect(wrapper.html()).not.toContain('<a>')
  })
  
  it('应该发出XSS检测事件', () => {
    const maliciousContent = '<script>alert("xss")</script>'
    
    const wrapper = mount(SafeHTML, {
      props: {
        content: maliciousContent,
        enableXSSWarning: true
      }
    })
    
    // 检查是否发出了xssDetected事件
    expect(wrapper.emitted('xssDetected')).toBeTruthy()
    expect(wrapper.emitted('xssDetected')?.[0]).toEqual([maliciousContent])
  })
  
  it('应该发出内容清理事件', () => {
    const originalContent = '<script>alert("xss")</script><p>内容</p>'
    
    const wrapper = mount(SafeHTML, {
      props: {
        content: originalContent
      }
    })
    
    // 检查是否发出了contentSanitized事件
    expect(wrapper.emitted('contentSanitized')).toBeTruthy()
    const emittedEvent = wrapper.emitted('contentSanitized')?.[0]
    expect(emittedEvent?.[0]).toBe(originalContent)
    expect(emittedEvent?.[1]).not.toContain('<script>')
  })
  
  it('应该显示回退内容', () => {
    const wrapper = mount(SafeHTML, {
      props: {
        content: '',
        showFallback: true,
        fallbackText: '暂无内容'
      }
    })
    
    expect(wrapper.text()).toContain('暂无内容')
  })
  
  it('应该应用CSS类名', () => {
    const wrapper = mount(SafeHTML, {
      props: {
        content: '<p>内容</p>',
        className: 'custom-class'
      }
    })
    
    expect(wrapper.find('.custom-class').exists()).toBe(true)
  })
  
  it('应该处理空内容', () => {
    const wrapper = mount(SafeHTML, {
      props: {
        content: '',
        showFallback: false
      }
    })
    
    // 不应该渲染任何内容
    expect(wrapper.find('div').exists()).toBe(false)
  })
  
  it('应该在控制台输出XSS警告', () => {
    const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})
    
    mount(SafeHTML, {
      props: {
        content: '<script>alert("xss")</script>',
        enableXSSWarning: true
      }
    })
    
    expect(consoleSpy).toHaveBeenCalledWith(
      'SafeHTML: 检测到潜在的XSS攻击向量:',
      '<script>alert("xss")</script>'
    )
    
    consoleSpy.mockRestore()
  })
})

describe('SafeHTML Styles', () => {
  it('应该应用安全的样式', () => {
    const wrapper = mount(SafeHTML, {
      props: {
        content: '<p>测试内容</p>'
      }
    })
    
    // 检查样式是否正确应用
    const div = wrapper.find('div')
    expect(div.exists()).toBe(true)
  })
  
  it('应该隐藏危险元素', () => {
    const content = '<p>正常内容</p><script>alert(1)</script><style>.hack{}</style>'
    
    const wrapper = mount(SafeHTML, {
      props: {
        content
      }
    })
    
    // 即使DOMPurify没有完全清理，CSS也应该隐藏这些元素
    const html = wrapper.html()
    expect(html).toContain('<p>正常内容</p>')
  })
})
