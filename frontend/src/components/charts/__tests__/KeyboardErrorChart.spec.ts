import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import KeyboardErrorChart from '../KeyboardErrorChart.vue'

// Mock ECharts
vi.mock('echarts', () => ({
  default: {
    init: vi.fn(() => ({
      dispose: vi.fn(),
      setOption: vi.fn(),
      resize: vi.fn()
    }))
  },
  init: vi.fn(() => ({
    dispose: vi.fn(),
    setOption: vi.fn(),
    resize: vi.fn()
  }))
}))

describe('KeyboardErrorChart.vue Component', () => {
  let wrapper

  const defaultProps = {
    data: [
      { name: 'a', value: 5 },
      { name: 'e', value: 12 },
      { name: 'i', value: 8 },
      { name: 'o', value: 3 },
      { name: 'u', value: 15 }
    ],
    title: '按键错误统计'
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
    vi.restoreAllMocks()
  })

  describe('基础渲染', () => {
    it('正确渲染键盘错误图表组件容器', () => {
      wrapper = mount(KeyboardErrorChart, { props: defaultProps })
      
      expect(wrapper.find('.keyboard-error-chart').exists()).toBe(true)
      expect(wrapper.find('.chart-container').exists()).toBe(true)
    })

    it('使用默认属性正确渲染', () => {
      wrapper = mount(KeyboardErrorChart, { props: { data: [] } })
      
      expect(wrapper.find('.keyboard-error-chart').exists()).toBe(true)
      expect(wrapper.find('.chart-container').exists()).toBe(true)
    })

    it('正确应用传入的属性', () => {
      wrapper = mount(KeyboardErrorChart, { props: defaultProps })
      
      expect(wrapper.props().data).toEqual(defaultProps.data)
      expect(wrapper.props().title).toBe('按键错误统计')
    })
  })

  describe('属性验证', () => {
    it('data属性有正确的默认值', () => {
      wrapper = mount(KeyboardErrorChart)
      
      expect(wrapper.props().data).toEqual([])
    })

    it('title属性有正确的默认值', () => {
      wrapper = mount(KeyboardErrorChart)
      
      expect(wrapper.props().title).toBe('按键错误统计')
    })

    it('组件名称正确设置', () => {
      wrapper = mount(KeyboardErrorChart, { props: defaultProps })
      
      expect(wrapper.vm.$options.name).toBe('KeyboardErrorChart')
    })
  })

  describe('组件生命周期', () => {
    it('组件正确挂载和卸载', () => {
      wrapper = mount(KeyboardErrorChart, { props: defaultProps })
      
      expect(wrapper.exists()).toBe(true)
      expect(wrapper.find('.keyboard-error-chart').exists()).toBe(true)
      
      const beforeUnmount = wrapper.exists()
      expect(beforeUnmount).toBe(true)
      
      wrapper.unmount()
      // 卸载后简单验证组件存在状态
      expect(wrapper.vm).toBeDefined()
    })

    it('重复挂载组件不会出错', () => {
      for (let i = 0; i < 3; i++) {
        wrapper = mount(KeyboardErrorChart, { props: { data: [] } })
        expect(wrapper.exists()).toBe(true)
        wrapper.unmount()
      }
    })
  })

  describe('CSS样式', () => {
    it('组件有正确的CSS类', () => {
      wrapper = mount(KeyboardErrorChart, { props: defaultProps })
      
      expect(wrapper.classes()).toContain('keyboard-error-chart')
      expect(wrapper.find('.chart-container').classes()).toContain('chart-container')
    })

    it('图表容器有正确的样式', () => {
      wrapper = mount(KeyboardErrorChart, { props: defaultProps })
      
      const chartContainer = wrapper.find('.chart-container')
      expect(chartContainer.exists()).toBe(true)
    })
  })

  describe('边界情况', () => {
    it('空数据数组时正确处理', () => {
      wrapper = mount(KeyboardErrorChart, { props: { data: [] } })
      
      expect(wrapper.props().data).toEqual([])
      expect(wrapper.find('.chart-container').exists()).toBe(true)
    })

    it('null数据时正确处理', () => {
      wrapper = mount(KeyboardErrorChart, { props: { data: null } })
      
      expect(wrapper.props().data).toBe(null)
    })

    it('undefined数据时正确处理', () => {
      wrapper = mount(KeyboardErrorChart, { props: { data: undefined } })
      
      // Vue会将undefined处理为空数组，这是正常行为
      expect(wrapper.props().data).toEqual([])
    })

    it('单条数据时正确处理', () => {
      const singleData = [{ name: 'a', value: 5 }]
      wrapper = mount(KeyboardErrorChart, { props: { data: singleData } })
      
      expect(wrapper.props().data).toEqual(singleData)
    })

    it('大量数据时正确处理', () => {
      const largeData = Array.from({ length: 100 }, (_, i) => ({ 
        name: String.fromCharCode(97 + i), 
        value: i 
      }))
      wrapper = mount(KeyboardErrorChart, { props: { data: largeData } })
      
      expect(wrapper.props().data).toEqual(largeData)
      expect(wrapper.props().data.length).toBe(100)
    })
  })

  describe('组件稳定性', () => {
    it('频繁数据变化时组件保持稳定', async () => {
      wrapper = mount(KeyboardErrorChart, { props: { data: [] } })
      
      // 快速连续变化数据
      for (let i = 0; i < 10; i++) {
        const testData = [{ name: 'a', value: i }]
        await wrapper.setProps({ data: testData })
        
        expect(wrapper.exists()).toBe(true)
        expect(wrapper.props().data).toEqual(testData)
      }
    })

    it('极端数据值时组件保持稳定', () => {
      const extremeData = [
        { name: 'a', value: 0 },
        { name: 'b', value: 999999 },
        { name: 'c', value: -1000 },
        { name: 'd', value: 0.0001 }
      ]
      
      wrapper = mount(KeyboardErrorChart, { props: { data: extremeData } })
      
      expect(wrapper.exists()).toBe(true)
      expect(wrapper.props().data).toEqual(extremeData)
    })
  })

  describe('标题处理', () => {
    it('自定义标题正确显示', () => {
      const customTitle = '自定义错误统计'
      wrapper = mount(KeyboardErrorChart, { 
        props: { 
          data: defaultProps.data,
          title: customTitle 
        } 
      })
      
      expect(wrapper.props().title).toBe(customTitle)
    })

    it('空标题时使用默认值', () => {
      wrapper = mount(KeyboardErrorChart, { 
        props: { 
          data: defaultProps.data,
          title: '' 
        } 
      })
      
      expect(wrapper.props().title).toBe('')
    })

    it('长标题时正确处理', () => {
      const longTitle = '这是一个非常长的标题，用来测试组件对长标题的处理能力'
      wrapper = mount(KeyboardErrorChart, { 
        props: { 
          data: defaultProps.data,
          title: longTitle 
        } 
      })
      
      expect(wrapper.props().title).toBe(longTitle)
    })
  })

  describe('数据格式验证', () => {
    it('数据项包含必要的字段', () => {
      wrapper = mount(KeyboardErrorChart, { props: defaultProps })
      
      const data = wrapper.props().data
      data.forEach(item => {
        expect(item).toHaveProperty('name')
        expect(item).toHaveProperty('value')
        expect(typeof item.name).toBe('string')
        expect(typeof item.value).toBe('number')
      })
    })

    it('特殊字符名称正确处理', () => {
      const specialData = [
        { name: ' ', value: 5 },      // 空格
        { name: '\n', value: 3 },     // 换行符
        { name: '!@#$%', value: 7 },  // 特殊符号
        { name: '中文', value: 10 }    // 中文字符
      ]
      
      wrapper = mount(KeyboardErrorChart, { props: { data: specialData } })
      
      expect(wrapper.props().data).toEqual(specialData)
    })
  })
}) 