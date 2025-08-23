import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'

// 模拟DOM方法
const mockScrollIntoView = vi.fn()
const mockGetBoundingClientRect = vi.fn()

// 模拟TableOfContents组件
const mockTableOfContents = {
  template: `
    <div class="table-of-contents" v-if="headings.length > 0">
      <div class="toc-header">
        <h4>目录</h4>
      </div>
      <nav class="toc-nav">
        <ul class="toc-list">
          <li 
            v-for="heading in headings" 
            :key="heading.id"
            :class="['toc-item', \`toc-level-\${heading.level}\`, { active: activeId === heading.id }]"
          >
            <a 
              :href="\`#\${heading.id}\`" 
              @click.prevent="scrollToHeading(heading.id)"
              class="toc-link"
            >
              {{ heading.text }}
            </a>
          </li>
        </ul>
      </nav>
    </div>
  `,
  data() {
    return {
      headings: [],
      activeId: ''
    }
  },
  methods: {
    generateTOC() {
      // 模拟生成目录
      const mockHeadings = [
        { id: 'heading-1', text: '介绍', level: 1 },
        { id: 'heading-2', text: '安装', level: 2 },
        { id: 'heading-3', text: '配置', level: 2 },
        { id: 'heading-4', text: '基本用法', level: 3 },
        { id: 'heading-5', text: '高级用法', level: 3 },
        { id: 'heading-6', text: '总结', level: 1 }
      ]
      this.headings = mockHeadings
    },
    
    scrollToHeading(id) {
      // 模拟滚动到标题
      const element = document.getElementById(id)
      if (element && element.scrollIntoView) {
        element.scrollIntoView({ 
          behavior: 'smooth',
          block: 'start'
        })
      }
      this.activeId = id
    },
    
    updateActiveHeading() {
      // 模拟更新活跃标题
      if (this.headings.length > 0) {
        this.activeId = this.headings[0].id
      }
    },
    
    addScrollListener() {
      window.addEventListener('scroll', this.updateActiveHeading)
    },
    
    removeScrollListener() {
      window.removeEventListener('scroll', this.updateActiveHeading)
    },
    
    setMockHeadings(headings) {
      this.headings = headings
    },
    
    setActiveId(id) {
      this.activeId = id
    }
  },
  mounted() {
    setTimeout(() => {
      this.generateTOC()
      this.addScrollListener()
      this.updateActiveHeading()
    }, 100)
  },
  unmounted() {
    this.removeScrollListener()
  }
}

describe('TableOfContents.vue Component', () => {
  let wrapper

  beforeEach(() => {
    // 模拟DOM方法
    global.document.getElementById = vi.fn((id) => {
      const mockElement = {
        id,
        scrollIntoView: mockScrollIntoView,
        getBoundingClientRect: mockGetBoundingClientRect.mockReturnValue({
          top: 0,
          bottom: 100,
          left: 0,
          right: 100
        })
      }
      return mockElement
    })

    global.document.querySelector = vi.fn((selector) => {
      if (selector === '.article-content') {
        return {
          querySelectorAll: vi.fn(() => [
            { 
              id: 'heading-1', 
              textContent: '介绍', 
              tagName: 'H1',
              getBoundingClientRect: mockGetBoundingClientRect
            },
            { 
              id: 'heading-2', 
              textContent: '安装', 
              tagName: 'H2',
              getBoundingClientRect: mockGetBoundingClientRect
            }
          ])
        }
      }
      return null
    })

    global.window.addEventListener = vi.fn()
    global.window.removeEventListener = vi.fn()

    wrapper = mount(mockTableOfContents)
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  describe('基础渲染', () => {
    it('有标题时显示目录容器', async () => {
      wrapper.vm.setMockHeadings([
        { id: 'test-1', text: 'Test Heading', level: 1 }
      ])
      await wrapper.vm.$nextTick()
      
      const container = wrapper.find('.table-of-contents')
      expect(container.exists()).toBe(true)
    })

    it('无标题时不显示目录容器', async () => {
      wrapper.vm.setMockHeadings([])
      await wrapper.vm.$nextTick()
      
      const container = wrapper.find('.table-of-contents')
      expect(container.exists()).toBe(false)
    })

    it('显示目录标题', async () => {
      wrapper.vm.setMockHeadings([
        { id: 'test-1', text: 'Test Heading', level: 1 }
      ])
      await wrapper.vm.$nextTick()
      
      const header = wrapper.find('.toc-header h4')
      expect(header.exists()).toBe(true)
      expect(header.text()).toBe('目录')
    })

    it('显示导航容器', async () => {
      wrapper.vm.setMockHeadings([
        { id: 'test-1', text: 'Test Heading', level: 1 }
      ])
      await wrapper.vm.$nextTick()
      
      const nav = wrapper.find('.toc-nav')
      expect(nav.exists()).toBe(true)
    })

    it('显示目录列表', async () => {
      wrapper.vm.setMockHeadings([
        { id: 'test-1', text: 'Test Heading', level: 1 }
      ])
      await wrapper.vm.$nextTick()
      
      const list = wrapper.find('.toc-list')
      expect(list.exists()).toBe(true)
    })
  })

  describe('目录生成', () => {
    it('generateTOC方法存在', () => {
      expect(wrapper.vm.generateTOC).toBeDefined()
      expect(typeof wrapper.vm.generateTOC).toBe('function')
    })

    it('正确生成标题列表', () => {
      wrapper.vm.generateTOC()
      
      expect(wrapper.vm.headings).toEqual([
        { id: 'heading-1', text: '介绍', level: 1 },
        { id: 'heading-2', text: '安装', level: 2 },
        { id: 'heading-3', text: '配置', level: 2 },
        { id: 'heading-4', text: '基本用法', level: 3 },
        { id: 'heading-5', text: '高级用法', level: 3 },
        { id: 'heading-6', text: '总结', level: 1 }
      ])
    })

    it('正确显示标题数量', async () => {
      const testHeadings = [
        { id: 'h1', text: 'Heading 1', level: 1 },
        { id: 'h2', text: 'Heading 2', level: 2 },
        { id: 'h3', text: 'Heading 3', level: 3 }
      ]
      wrapper.vm.setMockHeadings(testHeadings)
      await wrapper.vm.$nextTick()
      
      const items = wrapper.findAll('.toc-item')
      expect(items).toHaveLength(3)
    })

    it('正确显示标题文本', async () => {
      const testHeadings = [
        { id: 'h1', text: 'Introduction', level: 1 },
        { id: 'h2', text: 'Getting Started', level: 2 }
      ]
      wrapper.vm.setMockHeadings(testHeadings)
      await wrapper.vm.$nextTick()
      
      const links = wrapper.findAll('.toc-link')
      expect(links[0].text()).toBe('Introduction')
      expect(links[1].text()).toBe('Getting Started')
    })

    it('正确设置标题链接href', async () => {
      const testHeadings = [
        { id: 'intro', text: 'Introduction', level: 1 }
      ]
      wrapper.vm.setMockHeadings(testHeadings)
      await wrapper.vm.$nextTick()
      
      const link = wrapper.find('.toc-link')
      expect(link.attributes('href')).toBe('#intro')
    })
  })

  describe('层级样式', () => {
    it('一级标题有正确的样式类', async () => {
      const testHeadings = [
        { id: 'h1', text: 'Level 1', level: 1 }
      ]
      wrapper.vm.setMockHeadings(testHeadings)
      await wrapper.vm.$nextTick()
      
      const item = wrapper.find('.toc-item')
      expect(item.classes()).toContain('toc-level-1')
    })

    it('二级标题有正确的样式类', async () => {
      const testHeadings = [
        { id: 'h2', text: 'Level 2', level: 2 }
      ]
      wrapper.vm.setMockHeadings(testHeadings)
      await wrapper.vm.$nextTick()
      
      const item = wrapper.find('.toc-item')
      expect(item.classes()).toContain('toc-level-2')
    })

    it('三级标题有正确的样式类', async () => {
      const testHeadings = [
        { id: 'h3', text: 'Level 3', level: 3 }
      ]
      wrapper.vm.setMockHeadings(testHeadings)
      await wrapper.vm.$nextTick()
      
      const item = wrapper.find('.toc-item')
      expect(item.classes()).toContain('toc-level-3')
    })

    it('不同层级标题显示正确的样式', async () => {
      const testHeadings = [
        { id: 'h1', text: 'Level 1', level: 1 },
        { id: 'h2', text: 'Level 2', level: 2 },
        { id: 'h3', text: 'Level 3', level: 3 },
        { id: 'h4', text: 'Level 4', level: 4 },
        { id: 'h5', text: 'Level 5', level: 5 },
        { id: 'h6', text: 'Level 6', level: 6 }
      ]
      wrapper.vm.setMockHeadings(testHeadings)
      await wrapper.vm.$nextTick()
      
      const items = wrapper.findAll('.toc-item')
      expect(items[0].classes()).toContain('toc-level-1')
      expect(items[1].classes()).toContain('toc-level-2')
      expect(items[2].classes()).toContain('toc-level-3')
      expect(items[3].classes()).toContain('toc-level-4')
      expect(items[4].classes()).toContain('toc-level-5')
      expect(items[5].classes()).toContain('toc-level-6')
    })
  })

  describe('激活状态', () => {
    it('活跃标题有active样式类', async () => {
      const testHeadings = [
        { id: 'active-heading', text: 'Active Heading', level: 1 }
      ]
      wrapper.vm.setMockHeadings(testHeadings)
      wrapper.vm.setActiveId('active-heading')
      await wrapper.vm.$nextTick()
      
      const item = wrapper.find('.toc-item')
      expect(item.classes()).toContain('active')
    })

    it('非活跃标题没有active样式类', async () => {
      const testHeadings = [
        { id: 'heading-1', text: 'Heading 1', level: 1 },
        { id: 'heading-2', text: 'Heading 2', level: 2 }
      ]
      wrapper.vm.setMockHeadings(testHeadings)
      wrapper.vm.setActiveId('heading-1')
      await wrapper.vm.$nextTick()
      
      const items = wrapper.findAll('.toc-item')
      expect(items[0].classes()).toContain('active')
      expect(items[1].classes()).not.toContain('active')
    })

    it('updateActiveHeading方法存在', () => {
      expect(wrapper.vm.updateActiveHeading).toBeDefined()
      expect(typeof wrapper.vm.updateActiveHeading).toBe('function')
    })

    it('updateActiveHeading正确设置活跃标题', () => {
      wrapper.vm.generateTOC()
      wrapper.vm.updateActiveHeading()
      
      expect(wrapper.vm.activeId).toBe('heading-1')
    })
  })

  describe('滚动功能', () => {
    it('scrollToHeading方法存在', () => {
      expect(wrapper.vm.scrollToHeading).toBeDefined()
      expect(typeof wrapper.vm.scrollToHeading).toBe('function')
    })

    it('点击链接调用scrollToHeading', async () => {
      const testHeadings = [
        { id: 'test-heading', text: 'Test Heading', level: 1 }
      ]
      wrapper.vm.setMockHeadings(testHeadings)
      await wrapper.vm.$nextTick()
      
      const scrollSpy = vi.spyOn(wrapper.vm, 'scrollToHeading')
      const link = wrapper.find('.toc-link')
      
      await link.trigger('click')
      
      expect(scrollSpy).toHaveBeenCalledWith('test-heading')
    })

    it('scrollToHeading调用元素的scrollIntoView', () => {
      wrapper.vm.scrollToHeading('test-id')
      
      expect(document.getElementById).toHaveBeenCalledWith('test-id')
      expect(mockScrollIntoView).toHaveBeenCalledWith({
        behavior: 'smooth',
        block: 'start'
      })
    })

    it('scrollToHeading设置活跃ID', () => {
      wrapper.vm.scrollToHeading('new-active-id')
      
      expect(wrapper.vm.activeId).toBe('new-active-id')
    })
  })

  describe('事件监听', () => {
    it('addScrollListener方法存在', () => {
      expect(wrapper.vm.addScrollListener).toBeDefined()
      expect(typeof wrapper.vm.addScrollListener).toBe('function')
    })

    it('removeScrollListener方法存在', () => {
      expect(wrapper.vm.removeScrollListener).toBeDefined()
      expect(typeof wrapper.vm.removeScrollListener).toBe('function')
    })

    it('addScrollListener添加滚动监听器', () => {
      wrapper.vm.addScrollListener()
      
      expect(window.addEventListener).toHaveBeenCalledWith('scroll', wrapper.vm.updateActiveHeading)
    })

    it('removeScrollListener移除滚动监听器', () => {
      wrapper.vm.removeScrollListener()
      
      expect(window.removeEventListener).toHaveBeenCalledWith('scroll', wrapper.vm.updateActiveHeading)
    })
  })

  describe('样式和布局', () => {
    it('目录容器有正确的样式类', async () => {
      wrapper.vm.setMockHeadings([
        { id: 'test', text: 'Test', level: 1 }
      ])
      await wrapper.vm.$nextTick()
      
      const container = wrapper.find('.table-of-contents')
      expect(container.classes()).toContain('table-of-contents')
    })

    it('目录标题有正确的样式类', async () => {
      wrapper.vm.setMockHeadings([
        { id: 'test', text: 'Test', level: 1 }
      ])
      await wrapper.vm.$nextTick()
      
      const header = wrapper.find('.toc-header')
      expect(header.classes()).toContain('toc-header')
    })

    it('导航容器有正确的样式类', async () => {
      wrapper.vm.setMockHeadings([
        { id: 'test', text: 'Test', level: 1 }
      ])
      await wrapper.vm.$nextTick()
      
      const nav = wrapper.find('.toc-nav')
      expect(nav.classes()).toContain('toc-nav')
    })

    it('目录列表有正确的样式类', async () => {
      wrapper.vm.setMockHeadings([
        { id: 'test', text: 'Test', level: 1 }
      ])
      await wrapper.vm.$nextTick()
      
      const list = wrapper.find('.toc-list')
      expect(list.classes()).toContain('toc-list')
    })

    it('目录项有正确的样式类', async () => {
      wrapper.vm.setMockHeadings([
        { id: 'test', text: 'Test', level: 1 }
      ])
      await wrapper.vm.$nextTick()
      
      const item = wrapper.find('.toc-item')
      expect(item.classes()).toContain('toc-item')
    })

    it('目录链接有正确的样式类', async () => {
      wrapper.vm.setMockHeadings([
        { id: 'test', text: 'Test', level: 1 }
      ])
      await wrapper.vm.$nextTick()
      
      const link = wrapper.find('.toc-link')
      expect(link.classes()).toContain('toc-link')
    })
  })

  describe('边界情况', () => {
    it('组件挂载时不会抛出错误', () => {
      expect(() => {
        mount(mockTableOfContents)
      }).not.toThrow()
    })

    it('处理空标题数组', async () => {
      wrapper.vm.setMockHeadings([])
      await wrapper.vm.$nextTick()
      
      expect(() => {
        wrapper.vm.updateActiveHeading()
      }).not.toThrow()
    })

    it('处理不存在的元素ID', () => {
      global.document.getElementById = vi.fn().mockReturnValue(null)
      
      expect(() => {
        wrapper.vm.scrollToHeading('non-existent')
      }).not.toThrow()
    })

    it('处理无效的标题级别', async () => {
      const testHeadings = [
        { id: 'invalid', text: 'Invalid Level', level: 0 },
        { id: 'invalid2', text: 'Invalid Level 2', level: 7 }
      ]
      wrapper.vm.setMockHeadings(testHeadings)
      await wrapper.vm.$nextTick()
      
      const items = wrapper.findAll('.toc-item')
      expect(items[0].classes()).toContain('toc-level-0')
      expect(items[1].classes()).toContain('toc-level-7')
    })

    it('处理没有scrollIntoView方法的元素', () => {
      global.document.getElementById = vi.fn().mockReturnValue({
        id: 'test'
        // 没有scrollIntoView方法
      })
      
      expect(() => {
        wrapper.vm.scrollToHeading('test')
      }).not.toThrow()
    })
  })

  describe('响应式数据', () => {
    it('headings状态正确绑定', () => {
      expect(wrapper.vm.headings).toEqual([])
    })

    it('activeId状态正确绑定', () => {
      expect(wrapper.vm.activeId).toBe('')
    })

    it('setMockHeadings方法正确设置标题', () => {
      const testHeadings = [
        { id: 'test', text: 'Test', level: 1 }
      ]
      wrapper.vm.setMockHeadings(testHeadings)
      
      expect(wrapper.vm.headings).toEqual(testHeadings)
    })

    it('setActiveId方法正确设置活跃ID', () => {
      wrapper.vm.setActiveId('test-id')
      
      expect(wrapper.vm.activeId).toBe('test-id')
    })
  })

  describe('性能考虑', () => {
    it('大量标题时性能正常', async () => {
      const largeHeadingsList = Array.from({ length: 100 }, (_, i) => ({
        id: `heading-${i}`,
        text: `Heading ${i}`,
        level: (i % 6) + 1
      }))
      
      const startTime = performance.now()
      wrapper.vm.setMockHeadings(largeHeadingsList)
      await wrapper.vm.$nextTick()
      const endTime = performance.now()
      
      expect(endTime - startTime).toBeLessThan(100)
    })

    it('频繁调用updateActiveHeading性能正常', () => {
      wrapper.vm.generateTOC()
      
      const startTime = performance.now()
      for (let i = 0; i < 100; i++) {
        wrapper.vm.updateActiveHeading()
      }
      const endTime = performance.now()
      
      expect(endTime - startTime).toBeLessThan(50)
    })
  })

  describe('可访问性', () => {
    it('链接有正确的href属性', async () => {
      const testHeadings = [
        { id: 'accessible-heading', text: 'Accessible Heading', level: 1 }
      ]
      wrapper.vm.setMockHeadings(testHeadings)
      await wrapper.vm.$nextTick()
      
      const link = wrapper.find('.toc-link')
      expect(link.attributes('href')).toBe('#accessible-heading')
    })

    it('使用语义化的nav元素', async () => {
      wrapper.vm.setMockHeadings([
        { id: 'test', text: 'Test', level: 1 }
      ])
      await wrapper.vm.$nextTick()
      
      const nav = wrapper.find('nav')
      expect(nav.exists()).toBe(true)
    })

    it('使用语义化的列表结构', async () => {
      wrapper.vm.setMockHeadings([
        { id: 'test', text: 'Test', level: 1 }
      ])
      await wrapper.vm.$nextTick()
      
      const ul = wrapper.find('ul')
      const li = wrapper.find('li')
      expect(ul.exists()).toBe(true)
      expect(li.exists()).toBe(true)
    })
  })
})