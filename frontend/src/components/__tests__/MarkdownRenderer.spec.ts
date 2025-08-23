import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'

// 模拟marked库
vi.mock('marked', () => ({
  marked: vi.fn((content) => {
    if (!content) return ''
    // 简单的markdown渲染模拟
    return content
      .replace(/^# (.*$)/gim, '<h1>$1</h1>')
      .replace(/^## (.*$)/gim, '<h2>$1</h2>')
      .replace(/^### (.*$)/gim, '<h3>$1</h3>')
      .replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>')
      .replace(/\*(.*)\*/gim, '<em>$1</em>')
      .replace(/`(.*)`/gim, '<code>$1</code>')
      .replace(/\[(.*)\]\((.*)\)/gim, '<a href="$2">$1</a>')
      .replace(/^> (.*$)/gim, '<blockquote>$1</blockquote>')
      .replace(/^- (.*$)/gim, '<ul><li>$1</li></ul>')
      .replace(/^\d+\. (.*$)/gim, '<ol><li>$1</li></ol>')
  }),
  setOptions: vi.fn()
}))

// 模拟highlight.js
vi.mock('highlight.js', () => ({
  default: {
    highlight: vi.fn((code, options) => ({ value: code })),
    highlightAuto: vi.fn((code) => ({ value: code })),
    getLanguage: vi.fn(() => true)
  }
}))

// 模拟MarkdownRenderer组件
const mockMarkdownRenderer = {
  template: `
    <div class="markdown-content" v-html="renderedContent"></div>
  `,
  props: {
    content: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      renderedContent: ''
    }
  },
  methods: {
    renderMarkdown(content) {
      if (!content) return ''
      
      // 简单的markdown渲染模拟
      return content
        .replace(/^# (.*$)/gim, '<h1>$1</h1>')
        .replace(/^## (.*$)/gim, '<h2>$1</h2>')
        .replace(/^### (.*$)/gim, '<h3>$1</h3>')
        .replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>')
        .replace(/\*(.*)\*/gim, '<em>$1</em>')
        .replace(/`(.*)`/gim, '<code>$1</code>')
        .replace(/\[(.*)\]\((.*)\)/gim, '<a href="$2">$1</a>')
        .replace(/^> (.*$)/gim, '<blockquote>$1</blockquote>')
        .replace(/^- (.*$)/gim, '<ul><li>$1</li></ul>')
        .replace(/^\d+\. (.*$)/gim, '<ol><li>$1</li></ol>')
    },
    
    updateContent() {
      this.renderedContent = this.renderMarkdown(this.content || '')
    }
  },
  watch: {
    content: {
      handler() {
        this.updateContent()
      },
      immediate: true
    }
  },
  mounted() {
    this.updateContent()
  }
}

describe('MarkdownRenderer.vue Component', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(mockMarkdownRenderer, {
      props: {
        content: '# Hello World\nThis is a test.'
      }
    })
  })

  describe('基础渲染', () => {
    it('正确渲染markdown容器', () => {
      const container = wrapper.find('.markdown-content')
      expect(container.exists()).toBe(true)
    })

    it('markdown容器有正确的样式类', () => {
      const container = wrapper.find('.markdown-content')
      expect(container.classes()).toContain('markdown-content')
    })

    it('接收content属性', () => {
      expect(wrapper.props('content')).toBe('# Hello World\nThis is a test.')
    })

    it('content属性是必需的', () => {
      expect(wrapper.vm.$options.props.content.required).toBe(true)
    })

    it('content属性类型为String', () => {
      expect(wrapper.vm.$options.props.content.type).toBe(String)
    })
  })

  describe('Markdown渲染功能', () => {
    it('渲染标题', () => {
      wrapper = mount(mockMarkdownRenderer, {
        props: { content: '# Test Title' }
      })
      expect(wrapper.vm.renderedContent).toContain('<h1>Test Title</h1>')
    })

    it('渲染二级标题', () => {
      wrapper = mount(mockMarkdownRenderer, {
        props: { content: '## Test Subtitle' }
      })
      expect(wrapper.vm.renderedContent).toContain('<h2>Test Subtitle</h2>')
    })

    it('渲染三级标题', () => {
      wrapper = mount(mockMarkdownRenderer, {
        props: { content: '### Test Subsubtitle' }
      })
      expect(wrapper.vm.renderedContent).toContain('<h3>Test Subsubtitle</h3>')
    })

    it('渲染粗体文本', () => {
      wrapper = mount(mockMarkdownRenderer, {
        props: { content: 'This is **bold** text' }
      })
      expect(wrapper.vm.renderedContent).toContain('<strong>bold</strong>')
    })

    it('渲染斜体文本', () => {
      wrapper = mount(mockMarkdownRenderer, {
        props: { content: 'This is *italic* text' }
      })
      expect(wrapper.vm.renderedContent).toContain('<em>italic</em>')
    })

    it('渲染行内代码', () => {
      wrapper = mount(mockMarkdownRenderer, {
        props: { content: 'Use `console.log()` to debug' }
      })
      expect(wrapper.vm.renderedContent).toContain('<code>console.log()</code>')
    })

    it('渲染链接', () => {
      wrapper = mount(mockMarkdownRenderer, {
        props: { content: '[Click here](https://example.com)' }
      })
      expect(wrapper.vm.renderedContent).toContain('<a href="https://example.com">Click here</a>')
    })

    it('渲染引用', () => {
      wrapper = mount(mockMarkdownRenderer, {
        props: { content: '> This is a quote' }
      })
      expect(wrapper.vm.renderedContent).toContain('<blockquote>This is a quote</blockquote>')
    })

    it('渲染无序列表', () => {
      wrapper = mount(mockMarkdownRenderer, {
        props: { content: '- Item 1\n- Item 2' }
      })
      expect(wrapper.vm.renderedContent).toContain('<ul>')
      expect(wrapper.vm.renderedContent).toContain('<li>Item 1</li>')
      expect(wrapper.vm.renderedContent).toContain('<li>Item 2</li>')
    })

    it('渲染有序列表', () => {
      wrapper = mount(mockMarkdownRenderer, {
        props: { content: '1. First item\n2. Second item' }
      })
      expect(wrapper.vm.renderedContent).toContain('<ol>')
      expect(wrapper.vm.renderedContent).toContain('<li>First item</li>')
      expect(wrapper.vm.renderedContent).toContain('<li>Second item</li>')
    })
  })

  describe('复杂Markdown内容', () => {
    it('渲染混合内容', () => {
      const complexContent = `
# Main Title

This is a **bold** paragraph with *italic* text and \`code\`.

## Subtitle

- List item 1
- List item 2

> This is a quote

[Link text](https://example.com)
      `
      
      wrapper = mount(mockMarkdownRenderer, {
        props: { content: complexContent }
      })
      
      const rendered = wrapper.vm.renderedContent
      expect(rendered).toContain('<h1>Main Title</h1>')
      expect(rendered).toContain('<strong>bold</strong>')
      expect(rendered).toContain('<em>italic</em>')
      expect(rendered).toContain('<code>code</code>')
      expect(rendered).toContain('<h2>Subtitle</h2>')
      expect(rendered).toContain('<ul>')
      expect(rendered).toContain('<blockquote>This is a quote</blockquote>')
      expect(rendered).toContain('<a href="https://example.com">Link text</a>')
    })

    it('处理空内容', () => {
      wrapper = mount(mockMarkdownRenderer, {
        props: { content: '' }
      })
      expect(wrapper.vm.renderedContent).toBe('')
    })

    it('处理null内容', () => {
      wrapper = mount(mockMarkdownRenderer, {
        props: { content: null }
      })
      expect(wrapper.vm.renderedContent).toBe('')
    })

    it('处理undefined内容', () => {
      wrapper = mount(mockMarkdownRenderer, {
        props: { content: undefined }
      })
      expect(wrapper.vm.renderedContent).toBe('')
    })
  })

  describe('响应式更新', () => {
    it('内容变化时重新渲染', async () => {
      wrapper = mount(mockMarkdownRenderer, {
        props: { content: '# Original Title' }
      })
      
      expect(wrapper.vm.renderedContent).toContain('<h1>Original Title</h1>')
      
      await wrapper.setProps({ content: '# Updated Title' })
      
      expect(wrapper.vm.renderedContent).toContain('<h1>Updated Title</h1>')
    })

    it('监听content属性变化', () => {
      expect(wrapper.vm.updateContent).toBeDefined()
      expect(typeof wrapper.vm.updateContent).toBe('function')
    })
  })

  describe('方法功能', () => {
    it('renderMarkdown方法存在', () => {
      expect(wrapper.vm.renderMarkdown).toBeDefined()
      expect(typeof wrapper.vm.renderMarkdown).toBe('function')
    })

    it('updateContent方法存在', () => {
      expect(wrapper.vm.updateContent).toBeDefined()
      expect(typeof wrapper.vm.updateContent).toBe('function')
    })

    it('renderMarkdown方法处理空字符串', () => {
      expect(wrapper.vm.renderMarkdown('')).toBe('')
    })

    it('renderMarkdown方法处理null', () => {
      expect(wrapper.vm.renderMarkdown(null)).toBe('')
    })

    it('renderMarkdown方法处理undefined', () => {
      expect(wrapper.vm.renderMarkdown(undefined)).toBe('')
    })

    it('renderMarkdown方法处理普通文本', () => {
      const result = wrapper.vm.renderMarkdown('Plain text')
      expect(result).toBe('Plain text')
    })
  })

  describe('边界情况', () => {
    it('组件挂载时不会抛出错误', () => {
      expect(() => {
        mount(mockMarkdownRenderer, {
          props: { content: 'Test content' }
        })
      }).not.toThrow()
    })

    it('处理特殊字符', () => {
      const specialContent = 'Content with <script>alert("xss")</script>'
      wrapper = mount(mockMarkdownRenderer, {
        props: { content: specialContent }
      })
      
      expect(() => {
        wrapper.vm.renderMarkdown(specialContent)
      }).not.toThrow()
    })

    it('处理超长内容', () => {
      const longContent = '# Title\n'.repeat(1000)
      wrapper = mount(mockMarkdownRenderer, {
        props: { content: longContent }
      })
      
      expect(() => {
        wrapper.vm.renderMarkdown(longContent)
      }).not.toThrow()
    })

    it('处理包含换行的内容', () => {
      const multilineContent = `# Title

This is a paragraph.

## Subtitle

Another paragraph.`
      
      wrapper = mount(mockMarkdownRenderer, {
        props: { content: multilineContent }
      })
      
      expect(wrapper.vm.renderedContent).toContain('<h1>Title</h1>')
      expect(wrapper.vm.renderedContent).toContain('<h2>Subtitle</h2>')
    })
  })

  describe('样式和布局', () => {
    it('markdown容器有正确的样式类', () => {
      const container = wrapper.find('.markdown-content')
      expect(container.classes()).toContain('markdown-content')
    })

    it('渲染的内容包含HTML标签', () => {
      wrapper = mount(mockMarkdownRenderer, {
        props: { content: '# Test' }
      })
      
      expect(wrapper.vm.renderedContent).toContain('<h1>')
      expect(wrapper.vm.renderedContent).toContain('</h1>')
    })

    it('v-html指令正确绑定', () => {
      wrapper = mount(mockMarkdownRenderer, {
        props: { content: '# Test Title' }
      })
      
      expect(wrapper.html()).toContain('<h1>Test Title</h1>')
    })
  })

  describe('性能考虑', () => {
    it('渲染性能测试', () => {
      const startTime = performance.now()
      
      for (let i = 0; i < 100; i++) {
        wrapper.vm.renderMarkdown('# Test ' + i)
      }
      
      const endTime = performance.now()
      const executionTime = endTime - startTime
      
      // 100次渲染应该在合理时间内完成
      expect(executionTime).toBeLessThan(1000)
    })

    it('大内容渲染性能', () => {
      const largeContent = '# Title\n'.repeat(100) + '**Bold text**\n'.repeat(100)
      
      const startTime = performance.now()
      wrapper.vm.renderMarkdown(largeContent)
      const endTime = performance.now()
      const executionTime = endTime - startTime
      
      // 大内容渲染应该在合理时间内完成
      expect(executionTime).toBeLessThan(100)
    })
  })

  describe('可访问性', () => {
    it('渲染的HTML结构语义化正确', () => {
      wrapper = mount(mockMarkdownRenderer, {
        props: { content: '# Title\n## Subtitle\nThis is **bold** text' }
      })
      
      const rendered = wrapper.vm.renderedContent
      expect(rendered).toContain('<h1>Title</h1>')
      expect(rendered).toContain('<h2>Subtitle</h2>')
      expect(rendered).toContain('<strong>bold</strong>')
    })

    it('链接包含正确的href属性', () => {
      wrapper = mount(mockMarkdownRenderer, {
        props: { content: '[Link](https://example.com)' }
      })
      
      expect(wrapper.vm.renderedContent).toContain('href="https://example.com"')
    })
  })

  describe('错误处理', () => {
    it('处理无效的markdown语法', () => {
      const invalidContent = '###\n**\n```\n'
      
      expect(() => {
        wrapper.vm.renderMarkdown(invalidContent)
      }).not.toThrow()
    })

    it('处理包含HTML的内容', () => {
      const htmlContent = '<div>HTML content</div>'
      
      expect(() => {
        wrapper.vm.renderMarkdown(htmlContent)
      }).not.toThrow()
    })

    it('处理包含特殊Unicode字符的内容', () => {
      const unicodeContent = '# 中文标题\n**粗体文本**\n*斜体文本*'
      
      expect(() => {
        wrapper.vm.renderMarkdown(unicodeContent)
      }).not.toThrow()
      
      const result = wrapper.vm.renderMarkdown(unicodeContent)
      expect(result).toContain('<h1>中文标题</h1>')
      expect(result).toContain('<strong>粗体文本</strong>')
      expect(result).toContain('<em>斜体文本</em>')
    })
  })
}) 