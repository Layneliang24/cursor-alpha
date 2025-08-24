import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import KeyboardLayoutChart from '../KeyboardLayoutChart.vue'

describe('KeyboardLayoutChart.vue Component', () => {
  let wrapper

  const defaultProps = {
    data: [
      { name: 'a', value: 5 },
      { name: 'e', value: 12 },
      { name: 'i', value: 8 },
      { name: 'o', value: 3 },
      { name: 'u', value: 15 },
      { name: ' ', value: 2 }
    ]
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
    it('正确渲染键盘布局图表组件容器', () => {
      wrapper = mount(KeyboardLayoutChart, { props: defaultProps })
      
      expect(wrapper.find('.keyboard-layout-chart').exists()).toBe(true)
      expect(wrapper.find('.keyboard-container').exists()).toBe(true)
    })

    it('使用默认属性正确渲染', () => {
      wrapper = mount(KeyboardLayoutChart, { props: { data: [] } })
      
      expect(wrapper.find('.keyboard-layout-chart').exists()).toBe(true)
      expect(wrapper.find('.keyboard-container').exists()).toBe(true)
    })

    it('正确应用传入的数据属性', () => {
      wrapper = mount(KeyboardLayoutChart, { props: defaultProps })
      
      expect(wrapper.props().data).toEqual(defaultProps.data)
    })
  })

  describe('属性验证', () => {
    it('data属性有正确的默认值', () => {
      wrapper = mount(KeyboardLayoutChart)
      
      expect(wrapper.props().data).toEqual([])
    })

    it('组件名称正确设置', () => {
      wrapper = mount(KeyboardLayoutChart, { props: defaultProps })
      
      expect(wrapper.vm.$options.name).toBe('KeyboardLayoutChart')
    })
  })

  describe('组件生命周期', () => {
    it('组件正确挂载和卸载', () => {
      wrapper = mount(KeyboardLayoutChart, { props: defaultProps })
      
      expect(wrapper.exists()).toBe(true)
      expect(wrapper.find('.keyboard-layout-chart').exists()).toBe(true)
      
      const beforeUnmount = wrapper.exists()
      expect(beforeUnmount).toBe(true)
      
      wrapper.unmount()
      // 卸载后简单验证组件存在状态
      expect(wrapper.vm).toBeDefined()
    })

    it('重复挂载组件不会出错', () => {
      for (let i = 0; i < 3; i++) {
        wrapper = mount(KeyboardLayoutChart, { props: { data: [] } })
        expect(wrapper.exists()).toBe(true)
        wrapper.unmount()
      }
    })
  })

  describe('键盘布局渲染', () => {
    it('正确渲染数字键行', () => {
      wrapper = mount(KeyboardLayoutChart, { props: defaultProps })
      
      const numberRow = wrapper.find('.keyboard-row')
      expect(numberRow.exists()).toBe(true)
      
      // 检查数字键
      const numberKeys = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
      numberKeys.forEach(key => {
        const keyElement = wrapper.find(`[title*="${key}"]`)
        expect(keyElement.exists()).toBe(true)
      })
    })

    it('正确渲染QWERTY行', () => {
      wrapper = mount(KeyboardLayoutChart, { props: defaultProps })
      
      const qwertyRow = wrapper.findAll('.keyboard-row')[1]
      expect(qwertyRow.exists()).toBe(true)
      
      // 检查QWERTY键
      const qwertyKeys = ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p']
      qwertyKeys.forEach(key => {
        const keyElement = wrapper.find(`[title*="${key.toUpperCase()}"]`)
        expect(keyElement.exists()).toBe(true)
      })
    })

    it('正确渲染ASDF行', () => {
      wrapper = mount(KeyboardLayoutChart, { props: defaultProps })
      
      const asdfRow = wrapper.findAll('.keyboard-row')[2]
      expect(asdfRow.exists()).toBe(true)
      
      // 检查ASDF键
      const asdfKeys = ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l']
      asdfKeys.forEach(key => {
        const keyElement = wrapper.find(`[title*="${key.toUpperCase()}"]`)
        expect(keyElement.exists()).toBe(true)
      })
    })

    it('正确渲染ZXCV行', () => {
      wrapper = mount(KeyboardLayoutChart, { props: defaultProps })
      
      const zxcvRow = wrapper.findAll('.keyboard-row')[3]
      expect(zxcvRow.exists()).toBe(true)
      
      // 检查ZXCV键
      const zxcvKeys = ['z', 'x', 'c', 'v', 'b', 'n', 'm']
      zxcvKeys.forEach(key => {
        const keyElement = wrapper.find(`[title*="${key.toUpperCase()}"]`)
        expect(keyElement.exists()).toBe(true)
      })
    })

    it('正确渲染空格键', () => {
      wrapper = mount(KeyboardLayoutChart, { props: defaultProps })
      
      const spaceKey = wrapper.find('.space-key')
      expect(spaceKey.exists()).toBe(true)
      expect(spaceKey.text()).toContain('SPACE')
    })
  })

  describe('CSS样式', () => {
    it('组件有正确的CSS类', () => {
      wrapper = mount(KeyboardLayoutChart, { props: defaultProps })
      
      expect(wrapper.classes()).toContain('keyboard-layout-chart')
      expect(wrapper.find('.keyboard-container').classes()).toContain('keyboard-container')
    })

    it('键盘行有正确的CSS类', () => {
      wrapper = mount(KeyboardLayoutChart, { props: defaultProps })
      
      const rows = wrapper.findAll('.keyboard-row')
      expect(rows.length).toBeGreaterThan(0)
      
      rows.forEach(row => {
        expect(row.classes()).toContain('keyboard-row')
      })
    })

    it('键盘按键有正确的CSS类', () => {
      wrapper = mount(KeyboardLayoutChart, { props: defaultProps })
      
      const keys = wrapper.findAll('.keyboard-key')
      expect(keys.length).toBeGreaterThan(0)
      
      keys.forEach(key => {
        expect(key.classes()).toContain('keyboard-key')
      })
    })

    it('数字键有正确的CSS类', () => {
      wrapper = mount(KeyboardLayoutChart, { props: defaultProps })
      
      const numberKeys = wrapper.findAll('.number-key')
      expect(numberKeys.length).toBeGreaterThan(0)
      
      numberKeys.forEach(key => {
        expect(key.classes()).toContain('number-key')
      })
    })

    it('字母键有正确的CSS类', () => {
      wrapper = mount(KeyboardLayoutChart, { props: defaultProps })
      
      const letterKeys = wrapper.findAll('.letter-key')
      expect(letterKeys.length).toBeGreaterThan(0)
      
      letterKeys.forEach(key => {
        expect(key.classes()).toContain('letter-key')
      })
    })

    it('空格键有正确的CSS类', () => {
      wrapper = mount(KeyboardLayoutChart, { props: defaultProps })
      
      const spaceKey = wrapper.find('.space-key')
      expect(spaceKey.classes()).toContain('space-key')
    })
  })

  describe('图例渲染', () => {
    it('正确渲染图例容器', () => {
      wrapper = mount(KeyboardLayoutChart, { props: defaultProps })
      
      expect(wrapper.find('.legend').exists()).toBe(true)
      expect(wrapper.find('.legend-title').exists()).toBe(true)
      expect(wrapper.find('.legend-items').exists()).toBe(true)
    })

    it('图例标题正确显示', () => {
      wrapper = mount(KeyboardLayoutChart, { props: defaultProps })
      
      const legendTitle = wrapper.find('.legend-title')
      expect(legendTitle.text()).toBe('错误次数')
    })

    it('图例项目正确渲染', () => {
      wrapper = mount(KeyboardLayoutChart, { props: defaultProps })
      
      const legendItems = wrapper.findAll('.legend-item')
      expect(legendItems.length).toBeGreaterThan(0)
      
      legendItems.forEach(item => {
        expect(item.find('.legend-color').exists()).toBe(true)
        expect(item.find('.legend-label').exists()).toBe(true)
      })
    })
  })

  describe('统计信息渲染', () => {
    it('有数据时正确渲染统计信息', () => {
      wrapper = mount(KeyboardLayoutChart, { props: defaultProps })
      
      expect(wrapper.find('.stats-info').exists()).toBe(true)
      expect(wrapper.find('.stats-title').exists()).toBe(true)
      expect(wrapper.find('.stats-content').exists()).toBe(true)
    })

    it('统计标题正确显示', () => {
      wrapper = mount(KeyboardLayoutChart, { props: defaultProps })
      
      const statsTitle = wrapper.find('.stats-title')
      expect(statsTitle.text()).toBe('错误统计')
    })

    it('统计项目正确渲染', () => {
      wrapper = mount(KeyboardLayoutChart, { props: defaultProps })
      
      const statItems = wrapper.findAll('.stat-item')
      expect(statItems.length).toBeGreaterThan(0)
      
      statItems.forEach(item => {
        expect(item.find('.stat-label').exists()).toBe(true)
        expect(item.find('.stat-value').exists()).toBe(true)
      })
    })

    it('空数据时不显示统计信息', () => {
      wrapper = mount(KeyboardLayoutChart, { props: { data: [] } })
      
      expect(wrapper.find('.stats-info').exists()).toBe(false)
    })
  })

  describe('错误级别样式', () => {
    it('无错误时应用正确的样式类', () => {
      wrapper = mount(KeyboardLayoutChart, { props: { data: [] } })
      
      const keys = wrapper.findAll('.keyboard-key')
      keys.forEach(key => {
        expect(key.classes()).toContain('error-level-0')
      })
    })

    it('有错误时应用正确的样式类', () => {
      const testData = [
        { name: 'a', value: 2 },  // 1-3次错误，应该是error-level-1
        { name: 'e', value: 7 },  // 4-10次错误，应该是error-level-2
        { name: 'i', value: 15 }, // 11-20次错误，应该是error-level-3
        { name: 'o', value: 25 }  // 20次以上错误，应该是error-level-4
      ]
      
      wrapper = mount(KeyboardLayoutChart, { props: { data: testData } })
      
      // 检查特定按键的样式类
      const aKey = wrapper.find('[title*="A"]')
      const eKey = wrapper.find('[title*="E"]')
      const iKey = wrapper.find('[title*="I"]')
      const oKey = wrapper.find('[title*="O"]')
      
      expect(aKey.classes()).toContain('error-level-1')
      expect(eKey.classes()).toContain('error-level-2')
      expect(iKey.classes()).toContain('error-level-3')
      expect(oKey.classes()).toContain('error-level-4')
    })
  })

  describe('错误计数显示', () => {
    it('有错误时显示错误计数', () => {
      const testData = [
        { name: 'a', value: 5 },
        { name: 'e', value: 12 }
      ]
      
      wrapper = mount(KeyboardLayoutChart, { props: { data: testData } })
      
      const aKey = wrapper.find('[title*="A"]')
      const eKey = wrapper.find('[title*="E"]')
      
      expect(aKey.find('.error-count').exists()).toBe(true)
      expect(eKey.find('.error-count').exists()).toBe(true)
      expect(aKey.find('.error-count').text()).toBe('5')
      expect(eKey.find('.error-count').text()).toBe('12')
    })

    it('无错误时不显示错误计数', () => {
      wrapper = mount(KeyboardLayoutChart, { props: { data: [] } })
      
      const keys = wrapper.findAll('.keyboard-key')
      keys.forEach(key => {
        expect(key.find('.error-count').exists()).toBe(false)
      })
    })
  })

  describe('工具提示', () => {
    it('按键有正确的工具提示', () => {
      const testData = [
        { name: 'a', value: 5 },
        { name: ' ', value: 2 }
      ]
      
      wrapper = mount(KeyboardLayoutChart, { props: { data: testData } })
      
      const aKey = wrapper.find('[title*="A"]')
      const spaceKey = wrapper.find('.space-key')
      
      expect(aKey.attributes('title')).toContain('A: 5次错误')
      expect(spaceKey.attributes('title')).toContain('空格键: 2次错误')
    })

    it('无错误时显示正确的工具提示', () => {
      wrapper = mount(KeyboardLayoutChart, { props: { data: [] } })
      
      const aKey = wrapper.find('[title*="A"]')
      expect(aKey.attributes('title')).toContain('A: 0次错误')
    })
  })

  describe('边界情况', () => {
    it('空数据数组时正确处理', () => {
      wrapper = mount(KeyboardLayoutChart, { props: { data: [] } })
      
      expect(wrapper.props().data).toEqual([])
      expect(wrapper.find('.stats-info').exists()).toBe(false)
    })

    it('null数据时正确处理', () => {
      wrapper = mount(KeyboardLayoutChart, { props: { data: null } })
      
      expect(wrapper.props().data).toBe(null)
    })

    it('undefined数据时正确处理', () => {
      wrapper = mount(KeyboardLayoutChart, { props: { data: undefined } })
      
      // Vue会将undefined处理为空数组，这是正常行为
      expect(wrapper.props().data).toEqual([])
    })

    it('单条数据时正确处理', () => {
      const singleData = [{ name: 'a', value: 5 }]
      wrapper = mount(KeyboardLayoutChart, { props: { data: singleData } })
      
      expect(wrapper.props().data).toEqual(singleData)
    })

    it('大量数据时正确处理', () => {
      const largeData = Array.from({ length: 100 }, (_, i) => ({ 
        name: String.fromCharCode(97 + i), 
        value: i 
      }))
      wrapper = mount(KeyboardLayoutChart, { props: { data: largeData } })
      
      expect(wrapper.props().data).toEqual(largeData)
      expect(wrapper.props().data.length).toBe(100)
    })
  })

  describe('组件稳定性', () => {
    it('频繁数据变化时组件保持稳定', async () => {
      wrapper = mount(KeyboardLayoutChart, { props: { data: [] } })
      
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
      
      wrapper = mount(KeyboardLayoutChart, { props: { data: extremeData } })
      
      expect(wrapper.exists()).toBe(true)
      expect(wrapper.props().data).toEqual(extremeData)
    })
  })

  describe('事件处理', () => {
    it('按键点击时正确触发事件', async () => {
      const testData = [{ name: 'a', value: 5 }]
      wrapper = mount(KeyboardLayoutChart, { props: { data: testData } })
      
      const aKey = wrapper.find('[title*="A"]')
      await aKey.trigger('click')
      
      // 检查是否触发了key-click事件
      expect(wrapper.emitted('key-click')).toBeTruthy()
      expect(wrapper.emitted('key-click')[0]).toEqual([{ key: 'a', errorCount: 5 }])
    })

    it('空格键点击时正确触发事件', async () => {
      const testData = [{ name: ' ', value: 2 }]
      wrapper = mount(KeyboardLayoutChart, { props: { data: testData } })
      
      const spaceKey = wrapper.find('.space-key')
      await spaceKey.trigger('click')
      
      expect(wrapper.emitted('key-click')).toBeTruthy()
      expect(wrapper.emitted('key-click')[0]).toEqual([{ key: ' ', errorCount: 2 }])
    })
  })
}) 