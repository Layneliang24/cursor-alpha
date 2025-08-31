import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import LoadingIndicator from '@/components/common/LoadingIndicator.vue'
import { commonMountOptions, testUtils, elementPlusUtils } from '../../setup.js'

describe('LoadingIndicator', () => {
  let wrapper

  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
    vi.useRealTimers()
  })

  describe('默认旋转加载器', () => {
    beforeEach(() => {
      wrapper = mount(LoadingIndicator, {
        ...commonMountOptions,
        props: {
          message: '加载中...',
        },
      })
    })

    it('应该渲染默认的旋转加载器', () => {
      expect(wrapper.find('.spinner-loading').exists()).toBe(true)
      expect(wrapper.find('.loading-spinner').exists()).toBe(true)
    })

    it('应该显示加载消息', () => {
      expect(wrapper.find('.spinner-message').text()).toBe('加载中...')
    })

    it('应该有正确的CSS类', () => {
      expect(wrapper.classes()).toContain('loading-indicator')
      expect(wrapper.classes()).toContain('loading-medium')
    })
  })

  describe('骨架屏加载器', () => {
    beforeEach(() => {
      wrapper = mount(LoadingIndicator, {
        ...commonMountOptions,
        props: {
          type: 'skeleton',
          skeletonRows: 5,
        },
      })
    })

    it('应该渲染骨架屏', () => {
      expect(wrapper.find('.skeleton-loading').exists()).toBe(true)
      expect(wrapper.findComponent({ name: 'ElSkeleton' }).exists()).toBe(true)
    })

    it('应该传递正确的行数', () => {
      const skeleton = wrapper.findComponent({ name: 'ElSkeleton' })
      expect(skeleton.props('rows')).toBe(5)
      expect(skeleton.props('animated')).toBe(true)
    })
  })

  describe('卡片骨架屏', () => {
    beforeEach(() => {
      wrapper = mount(LoadingIndicator, {
        ...commonMountOptions,
        props: {
          type: 'card-skeleton',
        },
      })
    })

    it('应该渲染卡片骨架屏', () => {
      expect(wrapper.find('.card-skeleton-loading').exists()).toBe(true)
      expect(wrapper.findComponent({ name: 'ElSkeleton' }).exists()).toBe(true)
    })

    it('应该包含卡片相关的骨架元素', () => {
      const skeletonItems = wrapper.findAllComponents({ name: 'ElSkeletonItem' })
      expect(skeletonItems.length).toBeGreaterThan(0)
      
      // 检查是否有图片骨架
      const imageItem = skeletonItems.find(item => item.props('variant') === 'image')
      expect(imageItem).toBeDefined()
    })
  })

  describe('列表骨架屏', () => {
    beforeEach(() => {
      wrapper = mount(LoadingIndicator, {
        ...commonMountOptions,
        props: {
          type: 'list-skeleton',
          skeletonRows: 3,
        },
      })
    })

    it('应该渲染列表骨架屏', () => {
      expect(wrapper.find('.list-skeleton-loading').exists()).toBe(true)
    })

    it('应该渲染正确数量的列表项', () => {
      const listItems = wrapper.findAll('.list-item-skeleton')
      expect(listItems).toHaveLength(3)
    })
  })

  describe('打字指示器', () => {
    beforeEach(() => {
      wrapper = mount(LoadingIndicator, {
        ...commonMountOptions,
        props: {
          type: 'typing',
          message: 'AI正在思考...',
        },
      })
    })

    it('应该渲染打字指示器', () => {
      expect(wrapper.find('.typing-indicator').exists()).toBe(true)
      expect(wrapper.find('.typing-dots').exists()).toBe(true)
    })

    it('应该有3个点', () => {
      const dots = wrapper.findAll('.dot')
      expect(dots).toHaveLength(3)
    })

    it('应该显示打字消息', () => {
      expect(wrapper.find('.typing-message').text()).toBe('AI正在思考...')
    })

    it('点应该有动画类', () => {
      const dots = wrapper.findAll('.dot')
      dots.forEach(dot => {
        expect(dot.element).toHaveStyle({ animation: expect.stringContaining('typing') })
      })
    })
  })

  describe('进度条加载器', () => {
    beforeEach(() => {
      wrapper = mount(LoadingIndicator, {
        ...commonMountOptions,
        props: {
          type: 'progress',
          progress: 50,
          message: '处理中...',
        },
      })
    })

    it('应该渲染进度条', () => {
      expect(wrapper.find('.progress-loading').exists()).toBe(true)
      expect(wrapper.findComponent({ name: 'ElProgress' }).exists()).toBe(true)
    })

    it('应该显示正确的进度值', () => {
      const progress = wrapper.findComponent({ name: 'ElProgress' })
      expect(progress.props('percentage')).toBe(50)
    })

    it('应该显示进度消息', () => {
      expect(wrapper.find('.progress-message').text()).toBe('处理中...')
    })

    it('应该支持进度状态', async () => {
      await wrapper.setProps({ progressStatus: 'success' })
      const progress = wrapper.findComponent({ name: 'ElProgress' })
      expect(progress.props('status')).toBe('success')
    })
  })

  describe('脉冲加载器', () => {
    beforeEach(() => {
      wrapper = mount(LoadingIndicator, {
        ...commonMountOptions,
        props: {
          type: 'pulse',
          message: '连接中...',
        },
      })
    })

    it('应该渲染脉冲加载器', () => {
      expect(wrapper.find('.pulse-loading').exists()).toBe(true)
      expect(wrapper.find('.pulse-circle').exists()).toBe(true)
    })

    it('应该有3个脉冲环', () => {
      const rings = wrapper.findAll('.pulse-ring')
      expect(rings).toHaveLength(3)
    })

    it('应该显示脉冲消息', () => {
      expect(wrapper.find('.pulse-message').text()).toBe('连接中...')
    })
  })

  describe('波浪加载器', () => {
    beforeEach(() => {
      wrapper = mount(LoadingIndicator, {
        ...commonMountOptions,
        props: {
          type: 'wave',
          message: '同步中...',
        },
      })
    })

    it('应该渲染波浪加载器', () => {
      expect(wrapper.find('.wave-loading').exists()).toBe(true)
      expect(wrapper.find('.wave-container').exists()).toBe(true)
    })

    it('应该有5个波浪条', () => {
      const bars = wrapper.findAll('.wave-bar')
      expect(bars).toHaveLength(5)
    })

    it('应该显示波浪消息', () => {
      expect(wrapper.find('.wave-message').text()).toBe('同步中...')
    })
  })

  describe('尺寸变体', () => {
    it('应该支持小尺寸', () => {
      wrapper = mount(LoadingIndicator, {
        ...commonMountOptions,
        props: { size: 'small' },
      })
      expect(wrapper.classes()).toContain('loading-small')
    })

    it('应该支持中等尺寸', () => {
      wrapper = mount(LoadingIndicator, {
        ...commonMountOptions,
        props: { size: 'medium' },
      })
      expect(wrapper.classes()).toContain('loading-medium')
    })

    it('应该支持大尺寸', () => {
      wrapper = mount(LoadingIndicator, {
        ...commonMountOptions,
        props: { size: 'large' },
      })
      expect(wrapper.classes()).toContain('loading-large')
    })
  })

  describe('位置和覆盖', () => {
    it('应该支持居中显示', () => {
      wrapper = mount(LoadingIndicator, {
        ...commonMountOptions,
        props: { center: true },
      })
      expect(wrapper.classes()).toContain('loading-center')
    })

    it('应该支持覆盖模式', () => {
      wrapper = mount(LoadingIndicator, {
        ...commonMountOptions,
        props: { overlay: true },
      })
      expect(wrapper.classes()).toContain('loading-overlay')
    })

    it('应该支持自定义背景色', () => {
      const customBackground = 'rgba(255, 0, 0, 0.5)'
      wrapper = mount(LoadingIndicator, {
        ...commonMountOptions,
        props: { 
          overlay: true,
          background: customBackground,
        },
      })
      
      // 检查CSS变量是否正确设置
      expect(wrapper.element.style.getPropertyValue('--background')).toBe(customBackground)
    })
  })

  describe('自动进度递增', () => {
    it('应该在进度类型且无初始进度时自动递增', async () => {
      wrapper = mount(LoadingIndicator, {
        ...commonMountOptions,
        props: {
          type: 'progress',
          progress: 0,
        },
      })

      const initialProgress = wrapper.vm.progressValue
      
      // 推进定时器
      vi.advanceTimersByTime(1000)
      await testUtils.nextTick()

      expect(wrapper.vm.progressValue).toBeGreaterThan(initialProgress)
    })
  })

  describe('props验证', () => {
    it('应该验证type prop', () => {
      const validTypes = ['spinner', 'skeleton', 'card-skeleton', 'list-skeleton', 'typing', 'progress', 'pulse', 'wave']
      
      validTypes.forEach(type => {
        wrapper = mount(LoadingIndicator, {
          ...commonMountOptions,
          props: { type },
        })
        expect(wrapper.props('type')).toBe(type)
      })
    })

    it('应该验证size prop', () => {
      const validSizes = ['small', 'medium', 'large']
      
      validSizes.forEach(size => {
        wrapper = mount(LoadingIndicator, {
          ...commonMountOptions,
          props: { size },
        })
        expect(wrapper.props('size')).toBe(size)
      })
    })

    it('应该验证progressStatus prop', () => {
      const validStatuses = ['', 'success', 'exception', 'warning']
      
      validStatuses.forEach(status => {
        wrapper = mount(LoadingIndicator, {
          ...commonMountOptions,
          props: { 
            type: 'progress',
            progressStatus: status, 
          },
        })
        expect(wrapper.props('progressStatus')).toBe(status)
      })
    })
  })

  describe('无障碍性', () => {
    it('应该有合适的ARIA属性', () => {
      wrapper = mount(LoadingIndicator, {
        ...commonMountOptions,
        props: { message: '加载中...' },
      })

      // 检查是否有合适的角色和标签
      const loadingElement = wrapper.find('.loading-indicator')
      expect(loadingElement.attributes('role')).toBe('status')
      expect(loadingElement.attributes('aria-live')).toBe('polite')
    })
  })
})
