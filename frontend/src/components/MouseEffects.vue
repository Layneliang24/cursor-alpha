<template>
  <div class="mouse-effects">
    <!-- 切换按钮 -->
    <div class="effect-toggle">
      <button @click="toggleEffect" class="toggle-btn" title="切换鼠标特效">
        {{ currentEffect === 'flowers' ? '🌸' : currentEffect === 'fish' ? '🐠' : '✨' }}
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
          transform: `scale(${particle.scale}) rotate(${particle.rotation}deg)`
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
          transform: `rotate(${fish.angle}deg) scale(${fish.scale})`
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
          transform: `scale(${star.scale})`
        }"
      >
        ✨
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const currentEffect = ref('flowers')
const flowerParticles = ref([])
const fishParticles = ref([])
const starParticles = ref([])

let particleId = 0
let mouseX = 0
let mouseY = 0
let lastMouseX = 0
let lastMouseY = 0

const flowerSymbols = ['🌸', '🌺', '🌷', '🦋', '💫', '✨']
const effects = ['flowers', 'fish', 'stars']

// 切换特效
const toggleEffect = () => {
  const currentIndex = effects.indexOf(currentEffect.value)
  currentEffect.value = effects[(currentIndex + 1) % effects.length]
  
  // 清空所有粒子
  flowerParticles.value = []
  fishParticles.value = []
  starParticles.value = []
}

// 创建撒花粒子
const createFlowerParticle = (x, y) => {
  const particle = {
    id: particleId++,
    x: x + (Math.random() - 0.5) * 20,
    y: y + (Math.random() - 0.5) * 20,
    opacity: 0.6,
    scale: Math.random() * 0.4 + 0.3,
    rotation: Math.random() * 360,
    symbol: flowerSymbols[Math.floor(Math.random() * flowerSymbols.length)],
    vx: (Math.random() - 0.5) * 1.5,
    vy: (Math.random() - 0.5) * 1.5,
    life: 120
  }
  
  flowerParticles.value.push(particle)
  if (flowerParticles.value.length > 15) {
    flowerParticles.value.shift()
  }
}

// 创建小鱼粒子
const createFishParticle = (x, y) => {
  const dx = x - lastMouseX
  const dy = y - lastMouseY
  const angle = Math.atan2(dy, dx) * 180 / Math.PI
  
  const fish = {
    id: particleId++,
    x: x - 20 + Math.random() * 40,
    y: y - 20 + Math.random() * 40,
    targetX: x,
    targetY: y,
    angle: angle,
    scale: Math.random() * 0.5 + 0.8,
    speed: Math.random() * 2 + 1,
    life: 120
  }
  
  fishParticles.value.push(fish)
  if (fishParticles.value.length > 8) {
    fishParticles.value.shift()
  }
}

// 创建星星粒子
const createStarParticle = (x, y) => {
  const particle = {
    id: particleId++,
    x: x + (Math.random() - 0.5) * 30,
    y: y + (Math.random() - 0.5) * 30,
    opacity: 0.4,
    scale: Math.random() * 0.6 + 0.2,
    vx: (Math.random() - 0.5) * 1,
    vy: (Math.random() - 0.5) * 1,
    life: 100
  }
  
  starParticles.value.push(particle)
  if (starParticles.value.length > 12) {
    starParticles.value.shift()
  }
}

// 更新粒子
const updateParticles = () => {
  // 更新撒花粒子
  flowerParticles.value.forEach((particle, index) => {
    particle.x += particle.vx
    particle.y += particle.vy
    particle.opacity -= 0.008
    particle.scale *= 0.995
    particle.rotation += 1.5
    particle.life--
    
    if (particle.life <= 0 || particle.opacity <= 0) {
      flowerParticles.value.splice(index, 1)
    }
  })

  // 更新小鱼粒子
  fishParticles.value.forEach((fish, index) => {
    const dx = mouseX - fish.x
    const dy = mouseY - fish.y
    const distance = Math.sqrt(dx * dx + dy * dy)
    
    if (distance > 5) {
      fish.x += (dx / distance) * fish.speed
      fish.y += (dy / distance) * fish.speed
      fish.angle = Math.atan2(dy, dx) * 180 / Math.PI
    }
    
    fish.life--
    if (fish.life <= 0) {
      fishParticles.value.splice(index, 1)
    }
  })

  // 更新星星粒子
  starParticles.value.forEach((particle, index) => {
    particle.x += particle.vx
    particle.y += particle.vy
    particle.opacity -= 0.006
    particle.scale *= 0.992
    particle.life--
    
    if (particle.life <= 0 || particle.opacity <= 0) {
      starParticles.value.splice(index, 1)
    }
  })
}

// 鼠标移动事件
const handleMouseMove = (e) => {
  lastMouseX = mouseX
  lastMouseY = mouseY
  mouseX = e.clientX
  mouseY = e.clientY
  
  if (currentEffect.value === 'flowers' && Math.random() < 0.2) {
    createFlowerParticle(mouseX, mouseY)
  } else if (currentEffect.value === 'fish' && Math.random() < 0.6) {
    createFishParticle(mouseX, mouseY)
  } else if (currentEffect.value === 'stars' && Math.random() < 0.15) {
    createStarParticle(mouseX, mouseY)
  }
}

// 动画循环
const animate = () => {
  updateParticles()
  requestAnimationFrame(animate)
}

onMounted(() => {
  document.addEventListener('mousemove', handleMouseMove)
  animate()
})

onUnmounted(() => {
  document.removeEventListener('mousemove', handleMouseMove)
})
</script>

<style scoped>
.mouse-effects {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  pointer-events: none;
  z-index: 9999;
}

.effect-toggle {
  position: fixed;
  top: 80px;
  right: 20px;
  pointer-events: auto;
  z-index: 10000;
}

.toggle-btn {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.9);
  font-size: 24px;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
}

.toggle-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
}

.effect-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.flower-particle {
  position: absolute;
  font-size: 14px;
  user-select: none;
  pointer-events: none;
  filter: blur(0.5px);
  animation: flowerFloat 3s ease-out forwards;
}

.fish-particle {
  position: absolute;
  font-size: 16px;
  user-select: none;
  pointer-events: none;
  opacity: 0.7;
  filter: blur(0.3px);
  transition: transform 0.2s ease;
}

.star-particle {
  position: absolute;
  font-size: 12px;
  user-select: none;
  pointer-events: none;
  filter: blur(0.5px);
  animation: starTwinkle 2.5s ease-out forwards;
}

@keyframes flowerFloat {
  0% {
    transform: translateY(0) scale(1) rotate(0deg);
    opacity: 0.6;
  }
  50% {
    opacity: 0.3;
  }
  100% {
    transform: translateY(-30px) scale(0.5) rotate(180deg);
    opacity: 0;
  }
}

@keyframes starTwinkle {
  0% {
    transform: scale(0);
    opacity: 0.4;
  }
  50% {
    transform: scale(1);
    opacity: 0.2;
  }
  100% {
    transform: scale(0.3);
    opacity: 0;
  }
}
</style>