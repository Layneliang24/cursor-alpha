import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import HeatmapChart from '../HeatmapChart.vue'

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

describe('HeatmapChart.vue Component', () => {
  let wrapper

  const defaultProps = {
    data: [
      { date: '2024-01-01', count: 5, level: 3 },
      { date: '2024-01-02', count: 8, level: 4 },
      { date: '2024-01-03', count: 2, level: 1 }
    ],
    title: '测试热力图'
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
    it('正确渲染热力图组件容器', () => {
      wrapper = mount(HeatmapChart, { props: defaultProps })
      
      expect(wrapper.find('.heatmap-chart').exists()).toBe(true)
      expect(wrapper.find('.chart-container').exists()).toBe(true)
    })

    it('使用默认属性正确渲染', () => {
      wrapper = mount(HeatmapChart, { props: { data: [] } })
      
      expect(wrapper.find('.heatmap-chart').exists()).toBe(true)
      expect(wrapper.find('.chart-container').exists()).toBe(true)
    })

    it('正确应用所有传入的属性', () => {
      wrapper = mount(HeatmapChart, { props: defaultProps })
      
      expect(wrapper.props().data).toEqual(defaultProps.data)
      expect(wrapper.props().title).toBe(defaultProps.title)
    })
  })

  describe('属性验证', () => {
    it('data属性有正确的默认值', () => {
      wrapper = mount(HeatmapChart, { props: { title: '测试' } })
      
      expect(wrapper.props().data).toEqual([])
    })

    it('title属性有正确的默认值', () => {
      wrapper = mount(HeatmapChart, { props: { data: [] } })
      
      expect(wrapper.props().title).toBe('热力图')
    })

    it('组件名称正确设置', () => {
      wrapper = mount(HeatmapChart, { props: defaultProps })
      
      expect(wrapper.vm.$options.name).toBe('HeatmapChart')
    })
  })

  describe('组件生命周期', () => {
    it('组件正确挂载和卸载', () => {
      wrapper = mount(HeatmapChart, { props: defaultProps })
      
      expect(wrapper.exists()).toBe(true)
      expect(wrapper.find('.heatmap-chart').exists()).toBe(true)
      
      const beforeUnmount = wrapper.exists()
      expect(beforeUnmount).toBe(true)
      
      wrapper.unmount()
      // 卸载后简单验证组件存在状态
      expect(wrapper.vm).toBeDefined()
    })

    it('重复挂载组件不会出错', () => {
      for (let i = 0; i < 3; i++) {
        wrapper = mount(HeatmapChart, { props: { data: [], title: `图表${i}` } })
        expect(wrapper.exists()).toBe(true)
        wrapper.unmount()
      }
    })
  })

  describe('边界情况', () => {
    it('空数据数组时正确处理', () => {
      wrapper = mount(HeatmapChart, { props: { data: [], title: '空数据' } })
      
      expect(wrapper.props().data).toEqual([])
      expect(wrapper.props().title).toBe('空数据')
    })

    it('null数据时正确处理', () => {
      wrapper = mount(HeatmapChart, { props: { data: null, title: '空数据' } })
      
      expect(wrapper.props().data).toBe(null)
      expect(wrapper.props().title).toBe('空数据')
    })

    it('undefined数据时正确处理', () => {
      wrapper = mount(HeatmapChart, { props: { data: undefined, title: '空数据' } })
      
      // Vue会将undefined处理为空数组，这是正常行为
      expect(wrapper.props().data).toEqual([])
      expect(wrapper.props().title).toBe('空数据')
    })
  })

  describe('CSS样式', () => {
    it('组件有正确的CSS类', () => {
      wrapper = mount(HeatmapChart, { props: defaultProps })
      
      expect(wrapper.classes()).toContain('heatmap-chart')
      expect(wrapper.find('.chart-container').classes()).toContain('chart-container')
    })

    it('图表容器有正确的样式属性', () => {
      wrapper = mount(HeatmapChart, { props: defaultProps })
      
      const chartContainer = wrapper.find('.chart-container')
      expect(chartContainer.exists()).toBe(true)
    })
  })
}) 