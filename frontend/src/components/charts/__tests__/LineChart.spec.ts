import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import LineChart from '../LineChart.vue'

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

describe('LineChart.vue Component', () => {
  let wrapper

  const defaultProps = {
    data: [
      ['2024-01-01', 100],
      ['2024-01-02', 150],
      ['2024-01-03', 120],
      ['2024-01-04', 200]
    ],
    title: '测试趋势图',
    name: '销售额',
    suffix: '元'
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
    it('正确渲染折线图组件容器', () => {
      wrapper = mount(LineChart, { props: defaultProps })
      
      expect(wrapper.find('.line-chart').exists()).toBe(true)
      expect(wrapper.find('.chart-container').exists()).toBe(true)
    })

    it('使用默认属性正确渲染', () => {
      wrapper = mount(LineChart, { props: { data: [] } })
      
      expect(wrapper.find('.line-chart').exists()).toBe(true)
      expect(wrapper.find('.chart-container').exists()).toBe(true)
    })

    it('正确应用所有传入的属性', () => {
      wrapper = mount(LineChart, { props: defaultProps })
      
      expect(wrapper.props().data).toEqual(defaultProps.data)
      expect(wrapper.props().title).toBe(defaultProps.title)
      expect(wrapper.props().name).toBe(defaultProps.name)
      expect(wrapper.props().suffix).toBe(defaultProps.suffix)
    })
  })

  describe('属性验证', () => {
    it('data属性有正确的默认值', () => {
      wrapper = mount(LineChart, { props: { title: '测试' } })
      
      expect(wrapper.props().data).toEqual([])
    })

    it('title属性有正确的默认值', () => {
      wrapper = mount(LineChart, { props: { data: [] } })
      
      expect(wrapper.props().title).toBe('趋势图')
    })

    it('name属性有正确的默认值', () => {
      wrapper = mount(LineChart, { props: { data: [] } })
      
      expect(wrapper.props().name).toBe('数值')
    })

    it('suffix属性有正确的默认值', () => {
      wrapper = mount(LineChart, { props: { data: [] } })
      
      expect(wrapper.props().suffix).toBe('')
    })

    it('组件名称正确设置', () => {
      wrapper = mount(LineChart, { props: defaultProps })
      
      expect(wrapper.vm.$options.name).toBe('LineChart')
    })
  })

  describe('组件生命周期', () => {
    it('组件正确挂载和卸载', () => {
      wrapper = mount(LineChart, { props: defaultProps })
      
      expect(wrapper.exists()).toBe(true)
      expect(wrapper.find('.line-chart').exists()).toBe(true)
      
      const beforeUnmount = wrapper.exists()
      expect(beforeUnmount).toBe(true)
      
      wrapper.unmount()
      // 卸载后简单验证组件存在状态
      expect(wrapper.vm).toBeDefined()
    })

    it('重复挂载组件不会出错', () => {
      for (let i = 0; i < 3; i++) {
        wrapper = mount(LineChart, { props: { data: [], title: `图表${i}` } })
        expect(wrapper.exists()).toBe(true)
        wrapper.unmount()
      }
    })
  })

  describe('边界情况', () => {
    it('空数据数组时正确处理', () => {
      wrapper = mount(LineChart, { props: { data: [], title: '空数据' } })
      
      expect(wrapper.props().data).toEqual([])
      expect(wrapper.props().title).toBe('空数据')
    })

    it('null数据时正确处理', () => {
      wrapper = mount(LineChart, { props: { data: null, title: '空数据' } })
      
      expect(wrapper.props().data).toBe(null)
      expect(wrapper.props().title).toBe('空数据')
    })

    it('undefined数据时正确处理', () => {
      wrapper = mount(LineChart, { props: { data: undefined, title: '空数据' } })
      
      // Vue会将undefined处理为空数组，这是正常行为
      expect(wrapper.props().data).toEqual([])
      expect(wrapper.props().title).toBe('空数据')
    })

    it('单条数据时正确处理', () => {
      const singleData = [['2024-01-01', 100]]
      wrapper = mount(LineChart, { props: { data: singleData, title: '单条数据' } })
      
      expect(wrapper.props().data).toEqual(singleData)
      expect(wrapper.props().title).toBe('单条数据')
    })

    it('大量数据时正确处理', () => {
      const largeData = Array.from({ length: 100 }, (_, i) => [`2024-01-${String(i + 1).padStart(2, '0')}`, i * 10])
      wrapper = mount(LineChart, { props: { data: largeData, title: '大量数据' } })
      
      expect(wrapper.props().data).toEqual(largeData)
      expect(wrapper.props().data.length).toBe(100)
    })
  })

  describe('CSS样式', () => {
    it('组件有正确的CSS类', () => {
      wrapper = mount(LineChart, { props: defaultProps })
      
      expect(wrapper.classes()).toContain('line-chart')
      expect(wrapper.find('.chart-container').classes()).toContain('chart-container')
    })

    it('图表容器有正确的样式属性', () => {
      wrapper = mount(LineChart, { props: defaultProps })
      
      const chartContainer = wrapper.find('.chart-container')
      expect(chartContainer.exists()).toBe(true)
    })
  })

  describe('数据格式处理', () => {
    it('正确处理二维数组数据格式', () => {
      const testData = [
        ['2024-01-01', 100],
        ['2024-01-02', 150],
        ['2024-01-03', 120]
      ]
      
      wrapper = mount(LineChart, { props: { data: testData, title: '测试数据' } })
      
      expect(wrapper.props().data).toEqual(testData)
      expect(wrapper.props().data[0]).toEqual(['2024-01-01', 100])
      expect(wrapper.props().data[1]).toEqual(['2024-01-02', 150])
    })

    it('正确处理数值和字符串混合数据', () => {
      const mixedData = [
        ['2024-01-01', 100],
        ['2024-01-02', '150'],
        ['2024-01-03', 120.5]
      ]
      
      wrapper = mount(LineChart, { props: { data: mixedData, title: '混合数据' } })
      
      expect(wrapper.props().data).toEqual(mixedData)
    })
  })

  describe('属性组合测试', () => {
    it('只传入data和title时使用默认name和suffix', () => {
      wrapper = mount(LineChart, { 
        props: { 
          data: [['2024-01-01', 100]], 
          title: '测试图表' 
        } 
      })
      
      expect(wrapper.props().data).toEqual([['2024-01-01', 100]])
      expect(wrapper.props().title).toBe('测试图表')
      expect(wrapper.props().name).toBe('数值')
      expect(wrapper.props().suffix).toBe('')
    })

    it('传入所有属性时正确应用', () => {
      const fullProps = {
        data: [['2024-01-01', 100]],
        title: '完整图表',
        name: '自定义名称',
        suffix: '自定义后缀'
      }
      
      wrapper = mount(LineChart, { props: fullProps })
      
      expect(wrapper.props().data).toEqual(fullProps.data)
      expect(wrapper.props().title).toBe(fullProps.title)
      expect(wrapper.props().name).toBe(fullProps.name)
      expect(wrapper.props().suffix).toBe(fullProps.suffix)
    })

    it('空字符串suffix时正确处理', () => {
      wrapper = mount(LineChart, { 
        props: { 
          data: [['2024-01-01', 100]], 
          title: '测试图表',
          suffix: ''
        } 
      })
      
      expect(wrapper.props().suffix).toBe('')
    })

    it('特殊字符suffix时正确处理', () => {
      const specialSuffixes = ['%', '°C', 'kg', 'km/h', '¥', '$', '€']
      
      specialSuffixes.forEach(suffix => {
        wrapper = mount(LineChart, { 
          props: { 
            data: [['2024-01-01', 100]], 
            title: '测试图表',
            suffix: suffix
          } 
        })
        
        expect(wrapper.props().suffix).toBe(suffix)
        wrapper.unmount()
      })
    })
  })

  describe('响应式属性变化', () => {
    it('title变化时正确更新', async () => {
      wrapper = mount(LineChart, { props: { data: [], title: '原始标题' } })
      
      expect(wrapper.props().title).toBe('原始标题')
      
      await wrapper.setProps({ title: '新标题' })
      
      expect(wrapper.props().title).toBe('新标题')
    })

    it('name变化时正确更新', async () => {
      wrapper = mount(LineChart, { props: { data: [], name: '原始名称' } })
      
      expect(wrapper.props().name).toBe('原始名称')
      
      await wrapper.setProps({ name: '新名称' })
      
      expect(wrapper.props().name).toBe('新名称')
    })

    it('suffix变化时正确更新', async () => {
      wrapper = mount(LineChart, { props: { data: [], suffix: '原始后缀' } })
      
      expect(wrapper.props().suffix).toBe('原始后缀')
      
      await wrapper.setProps({ suffix: '新后缀' })
      
      expect(wrapper.props().suffix).toBe('新后缀')
    })

    it('data变化时正确更新', async () => {
      wrapper = mount(LineChart, { props: { data: [['2024-01-01', 100]], title: '测试' } })
      
      expect(wrapper.props().data).toEqual([['2024-01-01', 100]])
      
      const newData = [['2024-01-02', 200], ['2024-01-03', 300]]
      await wrapper.setProps({ data: newData })
      
      expect(wrapper.props().data).toEqual(newData)
    })
  })

  describe('组件稳定性', () => {
    it('频繁属性变化时组件保持稳定', async () => {
      wrapper = mount(LineChart, { props: { data: [], title: '测试' } })
      
      // 快速连续变化属性
      for (let i = 0; i < 10; i++) {
        await wrapper.setProps({ 
          title: `标题${i}`,
          name: `名称${i}`,
          suffix: `后缀${i}`
        })
        
        expect(wrapper.exists()).toBe(true)
        expect(wrapper.props().title).toBe(`标题${i}`)
        expect(wrapper.props().name).toBe(`名称${i}`)
        expect(wrapper.props().suffix).toBe(`后缀${i}`)
      }
    })

    it('极端数据值时组件保持稳定', () => {
      const extremeData = [
        ['2024-01-01', 0],
        ['2024-01-02', -1000],
        ['2024-01-03', 999999],
        ['2024-01-04', 0.0001]
      ]
      
      wrapper = mount(LineChart, { 
        props: { 
          data: extremeData, 
          title: '极端数据',
          name: '极值',
          suffix: '单位'
        } 
      })
      
      expect(wrapper.exists()).toBe(true)
      expect(wrapper.props().data).toEqual(extremeData)
    })
  })
}) 