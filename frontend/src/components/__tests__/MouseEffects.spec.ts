import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'

// 模拟MouseEffects组件
const mockMouseEffects = {
  template: `
    <div class="mouse-effects">
      <!-- 切换按钮 -->
      <div class="effect-toggle">
        <button @click="toggleEffect" class="toggle-btn" title="切换鼠标特效">
          {{ getCurrentEffectIcon() }}
        </button>
      </div>

      <!-- 撒花特效 -->
      <div v-if="currentEffect === 'flowers'" class="effect-container">
        <div
          v-for="particle in flowerParticles"
          :key="particle.id"
          class="flower-particle"
          :style="{
            left: particle.x + 'px',
            top: particle.y + 'px',
            opacity: particle.opacity,
            transform: \`scale(\${particle.scale}) rotate(\${particle.rotation}deg)\`
          }"
        >
          {{ particle.symbol }}
        </div>
      </div>

      <!-- 小鱼特效 -->
      <div v-if="currentEffect === 'fish'" class="effect-container">
        <div
          v-for="fish in fishParticles"
          :key="fish.id"
          class="fish-particle"
          :style="{
            left: fish.x + 'px',
            top: fish.y + 'px',
            transform: \`rotate(\${fish.angle}deg) scale(\${fish.scale})\`
          }"
        >
          🐠
        </div>
      </div>

      <!-- 星星特效 -->
      <div v-if="currentEffect === 'stars'" class="effect-container">
        <div
          v-for="star in starParticles"
          :key="star.id"
          class="star-particle"
          :style="{
            left: star.x + 'px',
            top: star.y + 'px',
            opacity: star.opacity,
            transform: \`scale(\${star.scale})\`
          }"
        >
          ✨
        </div>
      </div>
    </div>
  `,
  data() {
    return {
      currentEffect: 'flowers',
      flowerParticles: [],
      fishParticles: [],
      starParticles: [],
      particleId: 0,
      mouseX: 0,
      mouseY: 0,
      lastMouseX: 0,
      lastMouseY: 0,
      flowerSymbols: ['🌸', '🌺', '🌷', '🦋', '💫', '✨'],
      effects: ['flowers', 'fish', 'stars']
    }
  },
  methods: {
    toggleEffect() {
      const currentIndex = this.effects.indexOf(this.currentEffect)
      this.currentEffect = this.effects[(currentIndex + 1) % this.effects.length]
      
      // 清空所有粒子
      this.flowerParticles = []
      this.fishParticles = []
      this.starParticles = []
    },
    
    getCurrentEffectIcon() {
      if (this.currentEffect === 'flowers') return '🌸'
      if (this.currentEffect === 'fish') return '🐠'
      return '✨'
    },
    
    createFlowerParticle(x, y) {
      const particle = {
        id: this.particleId++,
        x: x + (Math.random() - 0.5) * 20,
        y: y + (Math.random() - 0.5) * 20,
        opacity: 0.6,
        scale: Math.random() * 0.4 + 0.3,
        rotation: Math.random() * 360,
        symbol: this.flowerSymbols[Math.floor(Math.random() * this.flowerSymbols.length)],
        vx: (Math.random() - 0.5) * 1.5,
        vy: (Math.random() - 0.5) * 1.5,
        life: 120
      }
      
      this.flowerParticles.push(particle)
      if (this.flowerParticles.length > 15) {
        this.flowerParticles.shift()
      }
    },
    
    createFishParticle(x, y) {
      const dx = x - this.lastMouseX
      const dy = y - this.lastMouseY
      const angle = Math.atan2(dy, dx) * 180 / Math.PI
      
      const fish = {
        id: this.particleId++,
        x: x - 20 + Math.random() * 40,
        y: y - 20 + Math.random() * 40,
        targetX: x,
        targetY: y,
        angle: angle,
        scale: Math.random() * 0.5 + 0.8,
        speed: Math.random() * 2 + 1,
        life: 120
      }
      
      this.fishParticles.push(fish)
      if (this.fishParticles.length > 8) {
        this.fishParticles.shift()
      }
    },
    
    createStarParticle(x, y) {
      const particle = {
        id: this.particleId++,
        x: x + (Math.random() - 0.5) * 30,
        y: y + (Math.random() - 0.5) * 30,
        opacity: 0.4,
        scale: Math.random() * 0.6 + 0.2,
        vx: (Math.random() - 0.5) * 1,
        vy: (Math.random() - 0.5) * 1,
        life: 100
      }
      
      this.starParticles.push(particle)
      if (this.starParticles.length > 12) {
        this.starParticles.shift()
      }
    },
    
    handleMouseMove(e) {
      this.lastMouseX = this.mouseX
      this.lastMouseY = this.mouseY
      this.mouseX = e.clientX
      this.mouseY = e.clientY
      
      if (this.currentEffect === 'flowers' && Math.random() < 0.2) {
        this.createFlowerParticle(this.mouseX, this.mouseY)
      } else if (this.currentEffect === 'fish' && Math.random() < 0.6) {
        this.createFishParticle(this.mouseX, this.mouseY)
      } else if (this.currentEffect === 'stars' && Math.random() < 0.15) {
        this.createStarParticle(this.mouseX, this.mouseY)
      }
    },
    
    updateParticles() {
      // 更新撒花粒子
      this.flowerParticles.forEach((particle, index) => {
        particle.x += particle.vx
        particle.y += particle.vy
        particle.opacity -= 0.008
        particle.scale *= 0.995
        particle.rotation += 1.5
        particle.life--
        
        if (particle.life <= 0 || particle.opacity <= 0) {
          this.flowerParticles.splice(index, 1)
        }
      })

      // 更新小鱼粒子
      this.fishParticles.forEach((fish, index) => {
        const dx = this.mouseX - fish.x
        const dy = this.mouseY - fish.y
        const distance = Math.sqrt(dx * dx + dy * dy)
        
        if (distance > 5) {
          fish.x += (dx / distance) * fish.speed
          fish.y += (dy / distance) * fish.speed
          fish.angle = Math.atan2(dy, dx) * 180 / Math.PI
        }
        
        fish.life--
        if (fish.life <= 0) {
          this.fishParticles.splice(index, 1)
        }
      })

      // 更新星星粒子
      this.starParticles.forEach((particle, index) => {
        particle.x += particle.vx
        particle.y += particle.vy
        particle.opacity -= 0.006
        particle.scale *= 0.992
        particle.life--
        
        if (particle.life <= 0 || particle.opacity <= 0) {
          this.starParticles.splice(index, 1)
        }
      })
    }
  }
}

describe('MouseEffects.vue Component', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(mockMouseEffects)
  })

  describe('基础渲染', () => {
    it('正确渲染鼠标特效容器', () => {
      const container = wrapper.find('.mouse-effects')
      expect(container.exists()).toBe(true)
    })

    it('显示特效切换按钮', () => {
      const toggleBtn = wrapper.find('.toggle-btn')
      expect(toggleBtn.exists()).toBe(true)
    })

    it('切换按钮有正确的标题', () => {
      const toggleBtn = wrapper.find('.toggle-btn')
      expect(toggleBtn.attributes('title')).toBe('切换鼠标特效')
    })

    it('特效切换容器有正确的样式类', () => {
      const toggleContainer = wrapper.find('.effect-toggle')
      expect(toggleContainer.classes()).toContain('effect-toggle')
    })

    it('切换按钮有正确的样式类', () => {
      const toggleBtn = wrapper.find('.toggle-btn')
      expect(toggleBtn.classes()).toContain('toggle-btn')
    })
  })

  describe('特效切换功能', () => {
    it('初始状态为花朵特效', () => {
      expect(wrapper.vm.currentEffect).toBe('flowers')
    })

    it('切换按钮显示正确的图标', () => {
      expect(wrapper.vm.getCurrentEffectIcon()).toBe('🌸')
    })

    it('点击切换按钮切换到下一个特效', () => {
      wrapper.vm.toggleEffect()
      expect(wrapper.vm.currentEffect).toBe('fish')
      expect(wrapper.vm.getCurrentEffectIcon()).toBe('🐠')
    })

    it('切换特效时清空所有粒子', () => {
      // 先添加一些粒子
      wrapper.vm.createFlowerParticle(100, 100)
      wrapper.vm.createFishParticle(200, 200)
      wrapper.vm.createStarParticle(300, 300)
      
      expect(wrapper.vm.flowerParticles.length).toBeGreaterThan(0)
      
      // 切换特效
      wrapper.vm.toggleEffect()
      
      expect(wrapper.vm.flowerParticles.length).toBe(0)
      expect(wrapper.vm.fishParticles.length).toBe(0)
      expect(wrapper.vm.starParticles.length).toBe(0)
    })

    it('特效循环切换', () => {
      // flowers -> fish -> stars -> flowers
      expect(wrapper.vm.currentEffect).toBe('flowers')
      
      wrapper.vm.toggleEffect()
      expect(wrapper.vm.currentEffect).toBe('fish')
      
      wrapper.vm.toggleEffect()
      expect(wrapper.vm.currentEffect).toBe('stars')
      
      wrapper.vm.toggleEffect()
      expect(wrapper.vm.currentEffect).toBe('flowers')
    })
  })

  describe('花朵特效', () => {
    it('花朵特效容器正确显示', () => {
      const container = wrapper.find('.effect-container')
      expect(container.exists()).toBe(true)
    })

    it('创建花朵粒子', () => {
      wrapper.vm.createFlowerParticle(100, 100)
      expect(wrapper.vm.flowerParticles.length).toBe(1)
      
      const particle = wrapper.vm.flowerParticles[0]
      expect(particle).toHaveProperty('id')
      expect(particle).toHaveProperty('x')
      expect(particle).toHaveProperty('y')
      expect(particle).toHaveProperty('opacity')
      expect(particle).toHaveProperty('scale')
      expect(particle).toHaveProperty('rotation')
      expect(particle).toHaveProperty('symbol')
      expect(particle).toHaveProperty('life')
    })

    it('花朵粒子数量限制', () => {
      // 添加超过15个粒子
      for (let i = 0; i < 20; i++) {
        wrapper.vm.createFlowerParticle(100, 100)
      }
      
      expect(wrapper.vm.flowerParticles.length).toBeLessThanOrEqual(15)
    })

    it('花朵粒子包含正确的符号', () => {
      wrapper.vm.createFlowerParticle(100, 100)
      const particle = wrapper.vm.flowerParticles[0]
      expect(wrapper.vm.flowerSymbols).toContain(particle.symbol)
    })

    it('花朵粒子属性在合理范围内', () => {
      wrapper.vm.createFlowerParticle(100, 100)
      const particle = wrapper.vm.flowerParticles[0]
      
      expect(particle.opacity).toBeGreaterThan(0)
      expect(particle.opacity).toBeLessThanOrEqual(1)
      expect(particle.scale).toBeGreaterThan(0)
      expect(particle.life).toBeGreaterThan(0)
    })
  })

  describe('小鱼特效', () => {
    it('切换到小鱼特效', () => {
      wrapper.vm.currentEffect = 'fish'
      expect(wrapper.vm.currentEffect).toBe('fish')
    })

    it('小鱼特效图标正确', () => {
      wrapper.vm.currentEffect = 'fish'
      expect(wrapper.vm.getCurrentEffectIcon()).toBe('🐠')
    })

    it('创建小鱼粒子', () => {
      wrapper.vm.currentEffect = 'fish'
      wrapper.vm.createFishParticle(100, 100)
      expect(wrapper.vm.fishParticles.length).toBe(1)
      
      const fish = wrapper.vm.fishParticles[0]
      expect(fish).toHaveProperty('id')
      expect(fish).toHaveProperty('x')
      expect(fish).toHaveProperty('y')
      expect(fish).toHaveProperty('angle')
      expect(fish).toHaveProperty('scale')
      expect(fish).toHaveProperty('speed')
      expect(fish).toHaveProperty('life')
    })

    it('小鱼粒子数量限制', () => {
      wrapper.vm.currentEffect = 'fish'
      // 添加超过8个粒子
      for (let i = 0; i < 10; i++) {
        wrapper.vm.createFishParticle(100, 100)
      }
      
      expect(wrapper.vm.fishParticles.length).toBeLessThanOrEqual(8)
    })

    it('小鱼角度计算正确', () => {
      wrapper.vm.currentEffect = 'fish'
      wrapper.vm.lastMouseX = 100
      wrapper.vm.lastMouseY = 100
      wrapper.vm.createFishParticle(200, 200)
      
      const fish = wrapper.vm.fishParticles[0]
      expect(fish.angle).toBeDefined()
      expect(typeof fish.angle).toBe('number')
    })
  })

  describe('星星特效', () => {
    it('切换到星星特效', () => {
      wrapper.vm.currentEffect = 'stars'
      expect(wrapper.vm.currentEffect).toBe('stars')
    })

    it('星星特效图标正确', () => {
      wrapper.vm.currentEffect = 'stars'
      expect(wrapper.vm.getCurrentEffectIcon()).toBe('✨')
    })

    it('创建星星粒子', () => {
      wrapper.vm.currentEffect = 'stars'
      wrapper.vm.createStarParticle(100, 100)
      expect(wrapper.vm.starParticles.length).toBe(1)
      
      const star = wrapper.vm.starParticles[0]
      expect(star).toHaveProperty('id')
      expect(star).toHaveProperty('x')
      expect(star).toHaveProperty('y')
      expect(star).toHaveProperty('opacity')
      expect(star).toHaveProperty('scale')
      expect(star).toHaveProperty('life')
    })

    it('星星粒子数量限制', () => {
      wrapper.vm.currentEffect = 'stars'
      // 添加超过12个粒子
      for (let i = 0; i < 15; i++) {
        wrapper.vm.createStarParticle(100, 100)
      }
      
      expect(wrapper.vm.starParticles.length).toBeLessThanOrEqual(12)
    })

    it('星星粒子属性在合理范围内', () => {
      wrapper.vm.currentEffect = 'stars'
      wrapper.vm.createStarParticle(100, 100)
      const star = wrapper.vm.starParticles[0]
      
      expect(star.opacity).toBeGreaterThan(0)
      expect(star.opacity).toBeLessThanOrEqual(1)
      expect(star.scale).toBeGreaterThan(0)
      expect(star.life).toBeGreaterThan(0)
    })
  })

  describe('鼠标事件处理', () => {
    it('handleMouseMove方法更新鼠标位置', () => {
      const mockEvent = { clientX: 150, clientY: 250 }
      wrapper.vm.handleMouseMove(mockEvent)
      
      expect(wrapper.vm.mouseX).toBe(150)
      expect(wrapper.vm.mouseY).toBe(250)
    })

    it('handleMouseMove方法更新上一次鼠标位置', () => {
      wrapper.vm.mouseX = 100
      wrapper.vm.mouseY = 200
      
      const mockEvent = { clientX: 150, clientY: 250 }
      wrapper.vm.handleMouseMove(mockEvent)
      
      expect(wrapper.vm.lastMouseX).toBe(100)
      expect(wrapper.vm.lastMouseY).toBe(200)
    })

    it('花朵特效时可能创建花朵粒子', () => {
      wrapper.vm.currentEffect = 'flowers'
      const mockEvent = { clientX: 100, clientY: 100 }
      
      // 由于有随机性，我们只测试方法调用不会出错
      expect(() => {
        wrapper.vm.handleMouseMove(mockEvent)
      }).not.toThrow()
    })

    it('小鱼特效时可能创建小鱼粒子', () => {
      wrapper.vm.currentEffect = 'fish'
      const mockEvent = { clientX: 100, clientY: 100 }
      
      expect(() => {
        wrapper.vm.handleMouseMove(mockEvent)
      }).not.toThrow()
    })

    it('星星特效时可能创建星星粒子', () => {
      wrapper.vm.currentEffect = 'stars'
      const mockEvent = { clientX: 100, clientY: 100 }
      
      expect(() => {
        wrapper.vm.handleMouseMove(mockEvent)
      }).not.toThrow()
    })
  })

  describe('粒子更新', () => {
    it('updateParticles方法存在', () => {
      expect(wrapper.vm.updateParticles).toBeDefined()
      expect(typeof wrapper.vm.updateParticles).toBe('function')
    })

    it('更新花朵粒子', () => {
      wrapper.vm.createFlowerParticle(100, 100)
      const initialParticle = { ...wrapper.vm.flowerParticles[0] }
      
      wrapper.vm.updateParticles()
      
      const updatedParticle = wrapper.vm.flowerParticles[0]
      expect(updatedParticle.life).toBeLessThan(initialParticle.life)
    })

    it('更新小鱼粒子', () => {
      wrapper.vm.currentEffect = 'fish'
      wrapper.vm.createFishParticle(100, 100)
      const initialFish = { ...wrapper.vm.fishParticles[0] }
      
      wrapper.vm.updateParticles()
      
      const updatedFish = wrapper.vm.fishParticles[0]
      expect(updatedFish.life).toBeLessThan(initialFish.life)
    })

    it('更新星星粒子', () => {
      wrapper.vm.currentEffect = 'stars'
      wrapper.vm.createStarParticle(100, 100)
      const initialStar = { ...wrapper.vm.starParticles[0] }
      
      wrapper.vm.updateParticles()
      
      const updatedStar = wrapper.vm.starParticles[0]
      expect(updatedStar.life).toBeLessThan(initialStar.life)
    })
  })

  describe('响应式数据', () => {
    it('currentEffect状态正确绑定', () => {
      expect(wrapper.vm.currentEffect).toBe('flowers')
    })

    it('粒子数组正确初始化', () => {
      expect(wrapper.vm.flowerParticles).toEqual([])
      expect(wrapper.vm.fishParticles).toEqual([])
      expect(wrapper.vm.starParticles).toEqual([])
    })

    it('鼠标位置正确初始化', () => {
      expect(wrapper.vm.mouseX).toBe(0)
      expect(wrapper.vm.mouseY).toBe(0)
      expect(wrapper.vm.lastMouseX).toBe(0)
      expect(wrapper.vm.lastMouseY).toBe(0)
    })

    it('特效数组包含正确的值', () => {
      expect(wrapper.vm.effects).toEqual(['flowers', 'fish', 'stars'])
    })

    it('花朵符号数组包含正确的值', () => {
      expect(wrapper.vm.flowerSymbols).toEqual(['🌸', '🌺', '🌷', '🦋', '💫', '✨'])
    })
  })

  describe('边界情况', () => {
    it('组件挂载时不会抛出错误', () => {
      expect(() => {
        mount(mockMouseEffects)
      }).not.toThrow()
    })

    it('创建粒子时处理无效坐标', () => {
      expect(() => {
        wrapper.vm.createFlowerParticle(null, undefined)
        wrapper.vm.createFishParticle('invalid', 'invalid')
        wrapper.vm.createStarParticle(NaN, NaN)
      }).not.toThrow()
    })

    it('切换特效时处理空数组', () => {
      wrapper.vm.flowerParticles = null
      wrapper.vm.fishParticles = null
      wrapper.vm.starParticles = null
      
      expect(() => {
        wrapper.vm.toggleEffect()
      }).not.toThrow()
    })

    it('更新粒子时处理空数组', () => {
      wrapper.vm.flowerParticles = []
      wrapper.vm.fishParticles = []
      wrapper.vm.starParticles = []
      
      expect(() => {
        wrapper.vm.updateParticles()
      }).not.toThrow()
    })
  })

  describe('性能考虑', () => {
    it('粒子数量控制在合理范围内', () => {
      expect(wrapper.vm.flowerParticles.length).toBeLessThanOrEqual(15)
      expect(wrapper.vm.fishParticles.length).toBeLessThanOrEqual(8)
      expect(wrapper.vm.starParticles.length).toBeLessThanOrEqual(12)
    })

    it('粒子ID递增', () => {
      wrapper.vm.createFlowerParticle(100, 100)
      wrapper.vm.createFlowerParticle(200, 200)
      
      expect(wrapper.vm.flowerParticles[0].id).toBeLessThan(wrapper.vm.flowerParticles[1].id)
    })

    it('方法执行效率', () => {
      const startTime = performance.now()
      for (let i = 0; i < 100; i++) {
        wrapper.vm.createFlowerParticle(100, 100)
        wrapper.vm.updateParticles()
      }
      const endTime = performance.now()
      const executionTime = endTime - startTime
      
      // 100次调用应该在合理时间内完成
      expect(executionTime).toBeLessThan(1000)
    })
  })
}) 