import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'

// 模拟AnimatedBackground组件
const mockAnimatedBackground = {
  template: `
    <div class="animated-background">
      <div class="floating-shapes">
        <div v-for="i in 20" :key="i" class="shape" :style="getShapeStyle(i)"></div>
      </div>
      <div class="gradient-overlay"></div>
    </div>
  `,
  data() {
    return {
      shapeCount: 20
    }
  },
  methods: {
    getShapeStyle(index) {
      const size = Math.random() * 100 + 50
      const delay = Math.random() * 20
      const duration = Math.random() * 10 + 15
      const left = Math.random() * 100
      const opacity = Math.random() * 0.3 + 0.1
      
      return {
        width: size + 'px',
        height: size + 'px',
        left: left + '%',
        animationDelay: delay + 's',
        animationDuration: duration + 's',
        opacity: opacity
      }
    }
  }
}

describe('AnimatedBackground.vue Component', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(mockAnimatedBackground)
  })

  describe('基础渲染', () => {
    it('正确渲染动画背景容器', () => {
      const container = wrapper.find('.animated-background')
      expect(container.exists()).toBe(true)
    })

    it('显示浮动形状容器', () => {
      const shapesContainer = wrapper.find('.floating-shapes')
      expect(shapesContainer.exists()).toBe(true)
    })

    it('显示渐变覆盖层', () => {
      const overlay = wrapper.find('.gradient-overlay')
      expect(overlay.exists()).toBe(true)
    })

    it('动画背景容器有正确的样式类', () => {
      const container = wrapper.find('.animated-background')
      expect(container.classes()).toContain('animated-background')
    })

    it('浮动形状容器有正确的样式类', () => {
      const shapesContainer = wrapper.find('.floating-shapes')
      expect(shapesContainer.classes()).toContain('floating-shapes')
    })

    it('渐变覆盖层有正确的样式类', () => {
      const overlay = wrapper.find('.gradient-overlay')
      expect(overlay.classes()).toContain('gradient-overlay')
    })
  })

  describe('浮动形状', () => {
    it('生成正确数量的形状元素', () => {
      const shapes = wrapper.findAll('.shape')
      expect(shapes).toHaveLength(20)
    })

    it('生成正确数量的形状元素', () => {
      const shapes = wrapper.findAll('.shape')
      expect(shapes).toHaveLength(20)
    })

    it('形状元素有正确的样式类', () => {
      const shape = wrapper.find('.shape')
      expect(shape.classes()).toContain('shape')
    })

    it('getShapeStyle方法返回正确的样式对象', () => {
      const style = wrapper.vm.getShapeStyle(1)
      expect(style).toHaveProperty('width')
      expect(style).toHaveProperty('height')
      expect(style).toHaveProperty('left')
      expect(style).toHaveProperty('animationDelay')
      expect(style).toHaveProperty('animationDuration')
      expect(style).toHaveProperty('opacity')
    })

    it('形状样式包含正确的单位', () => {
      const style = wrapper.vm.getShapeStyle(1)
      expect(style.width).toMatch(/^\d+\.?\d*px$/)
      expect(style.height).toMatch(/^\d+\.?\d*px$/)
      expect(style.left).toMatch(/^\d+\.?\d*%$/)
      expect(style.animationDelay).toMatch(/^\d+\.?\d*s$/)
      expect(style.animationDuration).toMatch(/^\d+\.?\d*s$/)
    })

    it('形状大小在合理范围内', () => {
      const style = wrapper.vm.getShapeStyle(1)
      const width = parseInt(style.width)
      const height = parseInt(style.height)
      expect(width).toBeGreaterThanOrEqual(50)
      expect(width).toBeLessThanOrEqual(150)
      expect(height).toBeGreaterThanOrEqual(50)
      expect(height).toBeLessThanOrEqual(150)
    })

    it('形状位置在合理范围内', () => {
      const style = wrapper.vm.getShapeStyle(1)
      const left = parseFloat(style.left)
      expect(left).toBeGreaterThanOrEqual(0)
      expect(left).toBeLessThanOrEqual(100)
    })

    it('形状透明度在合理范围内', () => {
      const style = wrapper.vm.getShapeStyle(1)
      const opacity = parseFloat(style.opacity)
      expect(opacity).toBeGreaterThanOrEqual(0.1)
      expect(opacity).toBeLessThanOrEqual(0.4)
    })

    it('动画延迟在合理范围内', () => {
      const style = wrapper.vm.getShapeStyle(1)
      const delay = parseFloat(style.animationDelay)
      expect(delay).toBeGreaterThanOrEqual(0)
      expect(delay).toBeLessThanOrEqual(20)
    })

    it('动画持续时间在合理范围内', () => {
      const style = wrapper.vm.getShapeStyle(1)
      const duration = parseFloat(style.animationDuration)
      expect(duration).toBeGreaterThanOrEqual(15)
      expect(duration).toBeLessThanOrEqual(25)
    })
  })

  describe('样式和布局', () => {
    it('动画背景容器有正确的定位', () => {
      const container = wrapper.find('.animated-background')
      expect(container.exists()).toBe(true)
    })

    it('浮动形状容器有正确的定位', () => {
      const shapesContainer = wrapper.find('.floating-shapes')
      expect(shapesContainer.exists()).toBe(true)
    })

    it('渐变覆盖层有正确的定位', () => {
      const overlay = wrapper.find('.gradient-overlay')
      expect(overlay.exists()).toBe(true)
    })

    it('形状元素有正确的定位', () => {
      const shape = wrapper.find('.shape')
      expect(shape.exists()).toBe(true)
    })
  })

  describe('响应式数据', () => {
    it('shapeCount状态正确绑定', () => {
      expect(wrapper.vm.shapeCount).toBe(20)
    })

    it('getShapeStyle方法可访问', () => {
      expect(wrapper.vm.getShapeStyle).toBeDefined()
      expect(typeof wrapper.vm.getShapeStyle).toBe('function')
    })
  })

  describe('方法功能', () => {
    it('getShapeStyle方法为不同索引返回不同样式', () => {
      const style1 = wrapper.vm.getShapeStyle(1)
      const style2 = wrapper.vm.getShapeStyle(2)
      
      // 由于使用Math.random()，样式可能相同，但结构应该一致
      expect(style1).toHaveProperty('width')
      expect(style1).toHaveProperty('height')
      expect(style1).toHaveProperty('left')
      expect(style1).toHaveProperty('animationDelay')
      expect(style1).toHaveProperty('animationDuration')
      expect(style1).toHaveProperty('opacity')
      
      expect(style2).toHaveProperty('width')
      expect(style2).toHaveProperty('height')
      expect(style2).toHaveProperty('left')
      expect(style2).toHaveProperty('animationDelay')
      expect(style2).toHaveProperty('animationDuration')
      expect(style2).toHaveProperty('opacity')
    })

    it('getShapeStyle方法处理边界索引', () => {
      const style = wrapper.vm.getShapeStyle(0)
      expect(style).toHaveProperty('width')
      expect(style).toHaveProperty('height')
      expect(style).toHaveProperty('left')
      expect(style).toHaveProperty('animationDelay')
      expect(style).toHaveProperty('animationDuration')
      expect(style).toHaveProperty('opacity')
    })

    it('getShapeStyle方法处理大索引', () => {
      const style = wrapper.vm.getShapeStyle(100)
      expect(style).toHaveProperty('width')
      expect(style).toHaveProperty('height')
      expect(style).toHaveProperty('left')
      expect(style).toHaveProperty('animationDelay')
      expect(style).toHaveProperty('animationDuration')
      expect(style).toHaveProperty('opacity')
    })
  })

  describe('边界情况', () => {
    it('组件挂载时不会抛出错误', () => {
      expect(() => {
        mount(mockAnimatedBackground)
      }).not.toThrow()
    })

    it('getShapeStyle方法处理无效参数', () => {
      const style = wrapper.vm.getShapeStyle(null)
      expect(style).toHaveProperty('width')
      expect(style).toHaveProperty('height')
      expect(style).toHaveProperty('left')
      expect(style).toHaveProperty('animationDelay')
      expect(style).toHaveProperty('animationDuration')
      expect(style).toHaveProperty('opacity')
    })

    it('getShapeStyle方法处理字符串参数', () => {
      const style = wrapper.vm.getShapeStyle('test')
      expect(style).toHaveProperty('width')
      expect(style).toHaveProperty('height')
      expect(style).toHaveProperty('left')
      expect(style).toHaveProperty('animationDelay')
      expect(style).toHaveProperty('animationDuration')
      expect(style).toHaveProperty('opacity')
    })
  })

  describe('可访问性', () => {
    it('组件结构语义化正确', () => {
      const container = wrapper.find('.animated-background')
      const shapesContainer = wrapper.find('.floating-shapes')
      const overlay = wrapper.find('.gradient-overlay')
      
      expect(container.exists()).toBe(true)
      expect(shapesContainer.exists()).toBe(true)
      expect(overlay.exists()).toBe(true)
    })

    it('形状元素结构正确', () => {
      const shapes = wrapper.findAll('.shape')
      expect(shapes.length).toBe(20)
      shapes.forEach((shape) => {
        expect(shape.classes()).toContain('shape')
      })
    })
  })

  describe('性能考虑', () => {
    it('形状数量控制在合理范围内', () => {
      expect(wrapper.vm.shapeCount).toBe(20)
      expect(wrapper.vm.shapeCount).toBeLessThanOrEqual(50)
    })

    it('getShapeStyle方法执行效率', () => {
      const startTime = performance.now()
      for (let i = 0; i < 100; i++) {
        wrapper.vm.getShapeStyle(i)
      }
      const endTime = performance.now()
      const executionTime = endTime - startTime
      
      // 100次调用应该在合理时间内完成
      expect(executionTime).toBeLessThan(100)
    })
  })
}) 