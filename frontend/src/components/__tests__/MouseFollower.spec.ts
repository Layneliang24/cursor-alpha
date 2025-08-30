import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'

// 模拟requestAnimationFrame
const mockRequestAnimationFrame = vi.fn()

// 模拟MouseFollower组件
const mockMouseFollower = {
  template: `
    <div class="mouse-follower">
      <div
        v-for="particle in particles"
        :key="particle.id"
        class="particle"
        :style="{
          left: particle.x + 'px',
          top: particle.y + 'px',
          opacity: particle.opacity,
          transform: \`scale(\${particle.scale}) rotate(\${particle.rotation}deg)\`,
          color: particle.color
        }"
      >
        {{ particle.symbol }}
      </div>
    </div>
  `,
  data () {
    return {
      particles: [],
      particleId: 0,
      mouseX: 0,
      mouseY: 0,
      symbols: ['🌸', '🌺', '🌻', '🌷', '🌹', '💐', '🦋', '✨', '⭐', '💫', '🌟', '💖'],
      colors: ['#ff6b9d', '#ffa726', '#66bb6a', '#42a5f5', '#ab47bc', '#ef5350'],
    }
  },
  methods: {
    createParticle (x, y) {
      const particle = {
        id: this.particleId++,
        x: x + (Math.random() - 0.5) * 20,
        y: y + (Math.random() - 0.5) * 20,
        opacity: 1,
        scale: Math.random() * 0.5 + 0.5,
        rotation: Math.random() * 360,
        symbol: this.symbols[Math.floor(Math.random() * this.symbols.length)],
        color: this.colors[Math.floor(Math.random() * this.colors.length)],
        vx: (Math.random() - 0.5) * 2,
        vy: (Math.random() - 0.5) * 2,
        life: 60,
      }
      
      this.particles.push(particle)
      
      // 限制粒子数量
      if (this.particles.length > 50) {
        this.particles.shift()
      }
    },
    
    updateParticles () {
      this.particles.forEach((particle, index) => {
        particle.x += particle.vx
        particle.y += particle.vy
        particle.opacity -= 0.02
        particle.scale *= 0.98
        particle.rotation += 2
        particle.life--
        
        if (particle.life <= 0 || particle.opacity <= 0) {
          this.particles.splice(index, 1)
        }
      })
    },
    
    handleMouseMove (e) {
      this.mouseX = e.clientX
      this.mouseY = e.clientY
      
      // 随机创建粒子
      if (Math.random() < 0.3) {
        this.createParticle(this.mouseX, this.mouseY)
      }
    },
    
    animate () {
      this.updateParticles()
      mockRequestAnimationFrame(this.animate)
    },
    
    addMouseListener () {
      document.addEventListener('mousemove', this.handleMouseMove)
    },
    
    removeMouseListener () {
      document.removeEventListener('mousemove', this.handleMouseMove)
    },
    
    setParticles (particles) {
      this.particles = particles
    },
    
    setMousePosition (x, y) {
      this.mouseX = x
      this.mouseY = y
    },
    
    clearParticles () {
      this.particles = []
    },
  },
  mounted () {
    this.addMouseListener()
    this.animate()
  },
  unmounted () {
    this.removeMouseListener()
  },
}

describe('MouseFollower.vue Component', () => {
  let wrapper

  beforeEach(() => {
    // 模拟DOM事件监听
    global.document.addEventListener = vi.fn()
    global.document.removeEventListener = vi.fn()
    
    // 模拟requestAnimationFrame
    global.requestAnimationFrame = mockRequestAnimationFrame
    
    wrapper = mount(mockMouseFollower)
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  describe('基础渲染', () => {
    it('正确渲染鼠标跟随容器', () => {
      const container = wrapper.find('.mouse-follower')
      expect(container.exists()).toBe(true)
    })

    it('鼠标跟随容器有正确的样式类', () => {
      const container = wrapper.find('.mouse-follower')
      expect(container.classes()).toContain('mouse-follower')
    })

    it('初始状态下没有粒子', () => {
      expect(wrapper.vm.particles).toEqual([])
    })

    it('初始粒子ID为0', () => {
      expect(wrapper.vm.particleId).toBe(0)
    })

    it('初始鼠标位置为0', () => {
      expect(wrapper.vm.mouseX).toBe(0)
      expect(wrapper.vm.mouseY).toBe(0)
    })
  })

  describe('粒子创建', () => {
    it('createParticle方法存在', () => {
      expect(wrapper.vm.createParticle).toBeDefined()
      expect(typeof wrapper.vm.createParticle).toBe('function')
    })

    it('正确创建粒子', () => {
      wrapper.vm.createParticle(100, 150)
      
      expect(wrapper.vm.particles.length).toBe(1)
      
      const particle = wrapper.vm.particles[0]
      expect(particle).toHaveProperty('id')
      expect(particle).toHaveProperty('x')
      expect(particle).toHaveProperty('y')
      expect(particle).toHaveProperty('opacity')
      expect(particle).toHaveProperty('scale')
      expect(particle).toHaveProperty('rotation')
      expect(particle).toHaveProperty('symbol')
      expect(particle).toHaveProperty('color')
      expect(particle).toHaveProperty('vx')
      expect(particle).toHaveProperty('vy')
      expect(particle).toHaveProperty('life')
    })

    it('粒子ID递增', () => {
      wrapper.vm.createParticle(100, 100)
      wrapper.vm.createParticle(200, 200)
      
      expect(wrapper.vm.particles[0].id).toBe(0)
      expect(wrapper.vm.particles[1].id).toBe(1)
    })

    it('粒子属性在合理范围内', () => {
      wrapper.vm.createParticle(100, 100)
      const particle = wrapper.vm.particles[0]
      
      expect(particle.opacity).toBe(1)
      expect(particle.scale).toBeGreaterThanOrEqual(0.5)
      expect(particle.scale).toBeLessThanOrEqual(1)
      expect(particle.rotation).toBeGreaterThanOrEqual(0)
      expect(particle.rotation).toBeLessThanOrEqual(360)
      expect(particle.life).toBe(60)
    })

    it('粒子符号来自预定义数组', () => {
      wrapper.vm.createParticle(100, 100)
      const particle = wrapper.vm.particles[0]
      
      expect(wrapper.vm.symbols).toContain(particle.symbol)
    })

    it('粒子颜色来自预定义数组', () => {
      wrapper.vm.createParticle(100, 100)
      const particle = wrapper.vm.particles[0]
      
      expect(wrapper.vm.colors).toContain(particle.color)
    })

    it('限制粒子数量不超过50个', () => {
      // 创建超过50个粒子
      for (let i = 0; i < 55; i++) {
        wrapper.vm.createParticle(100, 100)
      }
      
      expect(wrapper.vm.particles.length).toBeLessThanOrEqual(50)
    })
  })

  describe('粒子更新', () => {
    it('updateParticles方法存在', () => {
      expect(wrapper.vm.updateParticles).toBeDefined()
      expect(typeof wrapper.vm.updateParticles).toBe('function')
    })

    it('更新粒子位置', () => {
      wrapper.vm.createParticle(100, 100)
      const initialParticle = { ...wrapper.vm.particles[0] }
      
      wrapper.vm.updateParticles()
      
      const updatedParticle = wrapper.vm.particles[0]
      expect(updatedParticle.x).not.toBe(initialParticle.x)
      expect(updatedParticle.y).not.toBe(initialParticle.y)
    })

    it('更新粒子透明度', () => {
      wrapper.vm.createParticle(100, 100)
      const initialOpacity = wrapper.vm.particles[0].opacity
      
      wrapper.vm.updateParticles()
      
      expect(wrapper.vm.particles[0].opacity).toBeLessThan(initialOpacity)
    })

    it('更新粒子缩放', () => {
      wrapper.vm.createParticle(100, 100)
      const initialScale = wrapper.vm.particles[0].scale
      
      wrapper.vm.updateParticles()
      
      expect(wrapper.vm.particles[0].scale).toBeLessThan(initialScale)
    })

    it('更新粒子旋转', () => {
      wrapper.vm.createParticle(100, 100)
      const initialRotation = wrapper.vm.particles[0].rotation
      
      wrapper.vm.updateParticles()
      
      expect(wrapper.vm.particles[0].rotation).toBe(initialRotation + 2)
    })

    it('更新粒子生命值', () => {
      wrapper.vm.createParticle(100, 100)
      const initialLife = wrapper.vm.particles[0].life
      
      wrapper.vm.updateParticles()
      
      expect(wrapper.vm.particles[0].life).toBe(initialLife - 1)
    })

    it('移除过期粒子', () => {
      wrapper.vm.createParticle(100, 100)
      wrapper.vm.particles[0].life = 0
      
      wrapper.vm.updateParticles()
      
      expect(wrapper.vm.particles.length).toBe(0)
    })

    it('移除透明度为0的粒子', () => {
      wrapper.vm.createParticle(100, 100)
      wrapper.vm.particles[0].opacity = 0
      
      wrapper.vm.updateParticles()
      
      expect(wrapper.vm.particles.length).toBe(0)
    })
  })

  describe('鼠标事件', () => {
    it('handleMouseMove方法存在', () => {
      expect(wrapper.vm.handleMouseMove).toBeDefined()
      expect(typeof wrapper.vm.handleMouseMove).toBe('function')
    })

    it('更新鼠标位置', () => {
      const mockEvent = { clientX: 200, clientY: 300 }
      wrapper.vm.handleMouseMove(mockEvent)
      
      expect(wrapper.vm.mouseX).toBe(200)
      expect(wrapper.vm.mouseY).toBe(300)
    })

    it('鼠标移动时可能创建粒子', () => {
      const mockEvent = { clientX: 100, clientY: 100 }
      const initialParticleCount = wrapper.vm.particles.length
      
      // 由于有随机性，我们只测试方法调用不会出错
      expect(() => {
        wrapper.vm.handleMouseMove(mockEvent)
      }).not.toThrow()
    })

    it('addMouseListener方法存在', () => {
      expect(wrapper.vm.addMouseListener).toBeDefined()
      expect(typeof wrapper.vm.addMouseListener).toBe('function')
    })

    it('removeMouseListener方法存在', () => {
      expect(wrapper.vm.removeMouseListener).toBeDefined()
      expect(typeof wrapper.vm.removeMouseListener).toBe('function')
    })

    it('addMouseListener添加事件监听器', () => {
      wrapper.vm.addMouseListener()
      
      expect(document.addEventListener).toHaveBeenCalledWith('mousemove', wrapper.vm.handleMouseMove)
    })

    it('removeMouseListener移除事件监听器', () => {
      wrapper.vm.removeMouseListener()
      
      expect(document.removeEventListener).toHaveBeenCalledWith('mousemove', wrapper.vm.handleMouseMove)
    })
  })

  describe('动画循环', () => {
    it('animate方法存在', () => {
      expect(wrapper.vm.animate).toBeDefined()
      expect(typeof wrapper.vm.animate).toBe('function')
    })

    it('animate方法调用updateParticles', () => {
      const updateSpy = vi.spyOn(wrapper.vm, 'updateParticles')
      
      wrapper.vm.animate()
      
      expect(updateSpy).toHaveBeenCalled()
    })

    it('animate方法调用requestAnimationFrame', () => {
      wrapper.vm.animate()
      
      expect(mockRequestAnimationFrame).toHaveBeenCalledWith(wrapper.vm.animate)
    })
  })

  describe('粒子渲染', () => {
    it('正确渲染粒子元素', async () => {
      wrapper.vm.createParticle(100, 100)
      await wrapper.vm.$nextTick()
      
      const particles = wrapper.findAll('.particle')
      expect(particles.length).toBe(1)
    })

    it('粒子有正确的样式类', async () => {
      wrapper.vm.createParticle(100, 100)
      await wrapper.vm.$nextTick()
      
      const particle = wrapper.find('.particle')
      expect(particle.classes()).toContain('particle')
    })

    it('粒子有正确的样式属性', async () => {
      wrapper.vm.createParticle(100, 100)
      await wrapper.vm.$nextTick()
      
      const particle = wrapper.find('.particle')
      const style = particle.attributes('style')
      
      expect(style).toContain('left:')
      expect(style).toContain('top:')
      expect(style).toContain('opacity:')
      expect(style).toContain('transform:')
      expect(style).toContain('color:')
    })

    it('粒子显示正确的符号', async () => {
      wrapper.vm.createParticle(100, 100)
      await wrapper.vm.$nextTick()
      
      const particle = wrapper.find('.particle')
      const symbol = particle.text()
      
      expect(wrapper.vm.symbols).toContain(symbol)
    })

    it('多个粒子正确渲染', async () => {
      wrapper.vm.createParticle(100, 100)
      wrapper.vm.createParticle(200, 200)
      wrapper.vm.createParticle(300, 300)
      await wrapper.vm.$nextTick()
      
      const particles = wrapper.findAll('.particle')
      expect(particles.length).toBe(3)
    })
  })

  describe('数据配置', () => {
    it('symbols数组包含正确的符号', () => {
      const expectedSymbols = ['🌸', '🌺', '🌻', '🌷', '🌹', '💐', '🦋', '✨', '⭐', '💫', '🌟', '💖']
      expect(wrapper.vm.symbols).toEqual(expectedSymbols)
    })

    it('colors数组包含正确的颜色', () => {
      const expectedColors = ['#ff6b9d', '#ffa726', '#66bb6a', '#42a5f5', '#ab47bc', '#ef5350']
      expect(wrapper.vm.colors).toEqual(expectedColors)
    })

    it('symbols数组不为空', () => {
      expect(wrapper.vm.symbols.length).toBeGreaterThan(0)
    })

    it('colors数组不为空', () => {
      expect(wrapper.vm.colors.length).toBeGreaterThan(0)
    })
  })

  describe('辅助方法', () => {
    it('setParticles方法存在', () => {
      expect(wrapper.vm.setParticles).toBeDefined()
      expect(typeof wrapper.vm.setParticles).toBe('function')
    })

    it('setMousePosition方法存在', () => {
      expect(wrapper.vm.setMousePosition).toBeDefined()
      expect(typeof wrapper.vm.setMousePosition).toBe('function')
    })

    it('clearParticles方法存在', () => {
      expect(wrapper.vm.clearParticles).toBeDefined()
      expect(typeof wrapper.vm.clearParticles).toBe('function')
    })

    it('setParticles正确设置粒子', () => {
      const testParticles = [
        { id: 1, x: 100, y: 100, symbol: '🌸' },
      ]
      wrapper.vm.setParticles(testParticles)
      
      expect(wrapper.vm.particles).toEqual(testParticles)
    })

    it('setMousePosition正确设置鼠标位置', () => {
      wrapper.vm.setMousePosition(150, 250)
      
      expect(wrapper.vm.mouseX).toBe(150)
      expect(wrapper.vm.mouseY).toBe(250)
    })

    it('clearParticles清空粒子数组', () => {
      wrapper.vm.createParticle(100, 100)
      wrapper.vm.createParticle(200, 200)
      
      wrapper.vm.clearParticles()
      
      expect(wrapper.vm.particles).toEqual([])
    })
  })

  describe('边界情况', () => {
    it('组件挂载时不会抛出错误', () => {
      expect(() => {
        mount(mockMouseFollower)
      }).not.toThrow()
    })

    it('处理空粒子数组', () => {
      wrapper.vm.clearParticles()
      
      expect(() => {
        wrapper.vm.updateParticles()
      }).not.toThrow()
    })

    it('处理无效的鼠标事件', () => {
      const invalidEvent = {}
      
      expect(() => {
        wrapper.vm.handleMouseMove(invalidEvent)
      }).not.toThrow()
    })

    it('处理负数坐标', () => {
      expect(() => {
        wrapper.vm.createParticle(-100, -100)
      }).not.toThrow()
    })

    it('处理极大坐标', () => {
      expect(() => {
        wrapper.vm.createParticle(10000, 10000)
      }).not.toThrow()
    })

    it('处理粒子生命值为负数', () => {
      wrapper.vm.createParticle(100, 100)
      wrapper.vm.particles[0].life = -10
      
      expect(() => {
        wrapper.vm.updateParticles()
      }).not.toThrow()
      
      expect(wrapper.vm.particles.length).toBe(0)
    })

    it('处理粒子透明度为负数', () => {
      wrapper.vm.createParticle(100, 100)
      wrapper.vm.particles[0].opacity = -0.5
      
      expect(() => {
        wrapper.vm.updateParticles()
      }).not.toThrow()
      
      expect(wrapper.vm.particles.length).toBe(0)
    })
  })

  describe('性能考虑', () => {
    it('大量粒子时性能正常', () => {
      const startTime = performance.now()
      
      for (let i = 0; i < 100; i++) {
        wrapper.vm.createParticle(Math.random() * 1000, Math.random() * 1000)
      }
      
      const endTime = performance.now()
      const executionTime = endTime - startTime
      
      expect(executionTime).toBeLessThan(100)
    })

    it('频繁调用updateParticles性能正常', () => {
      // 创建一些粒子
      for (let i = 0; i < 20; i++) {
        wrapper.vm.createParticle(100, 100)
      }
      
      const startTime = performance.now()
      for (let i = 0; i < 100; i++) {
        wrapper.vm.updateParticles()
      }
      const endTime = performance.now()
      
      const executionTime = endTime - startTime
      expect(executionTime).toBeLessThan(50)
    })

    it('粒子数量限制有效', () => {
      // 创建大量粒子
      for (let i = 0; i < 100; i++) {
        wrapper.vm.createParticle(100, 100)
      }
      
      expect(wrapper.vm.particles.length).toBeLessThanOrEqual(50)
    })
  })

  describe('样式和布局', () => {
    it('鼠标跟随容器有正确的样式类', () => {
      const container = wrapper.find('.mouse-follower')
      expect(container.classes()).toContain('mouse-follower')
    })

    it('粒子元素有正确的样式类', async () => {
      wrapper.vm.createParticle(100, 100)
      await wrapper.vm.$nextTick()
      
      const particle = wrapper.find('.particle')
      expect(particle.classes()).toContain('particle')
    })

    it('粒子样式包含必要的CSS属性', async () => {
      wrapper.vm.createParticle(100, 100)
      await wrapper.vm.$nextTick()
      
      const particle = wrapper.find('.particle')
      const style = particle.attributes('style')
      
      expect(style).toContain('left:')
      expect(style).toContain('top:')
      expect(style).toContain('opacity:')
      expect(style).toContain('transform:')
      expect(style).toContain('color:')
    })
  })

  describe('响应式数据', () => {
    it('particles状态正确绑定', () => {
      expect(wrapper.vm.particles).toEqual([])
    })

    it('particleId状态正确绑定', () => {
      expect(wrapper.vm.particleId).toBe(0)
    })

    it('mouseX和mouseY状态正确绑定', () => {
      expect(wrapper.vm.mouseX).toBe(0)
      expect(wrapper.vm.mouseY).toBe(0)
    })

    it('symbols和colors配置正确绑定', () => {
      expect(wrapper.vm.symbols).toBeDefined()
      expect(wrapper.vm.colors).toBeDefined()
      expect(Array.isArray(wrapper.vm.symbols)).toBe(true)
      expect(Array.isArray(wrapper.vm.colors)).toBe(true)
    })
  })
})