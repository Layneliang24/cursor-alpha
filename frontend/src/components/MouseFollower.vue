<template>
  <div class="mouse-follower">
    <!-- 撒花特效 -->
    <div
      v-for="particle in particles"
      :key="particle.id"
      class="particle"
      :style="{
        left: particle.x + 'px',
        top: particle.y + 'px',
        opacity: particle.opacity,
        transform: `scale(${particle.scale}) rotate(${particle.rotation}deg)`,
        color: particle.color
      }"
    >
      {{ particle.symbol }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const particles = ref([])
let particleId = 0
let mouseX = 0
let mouseY = 0

// 花朵和装饰符号
const symbols = ['🌸', '🌺', '🌻', '🌷', '🌹', '💐', '🦋', '✨', '⭐', '💫', '🌟', '💖']
const colors = ['#ff6b9d', '#ffa726', '#66bb6a', '#42a5f5', '#ab47bc', '#ef5350']

// 创建粒子
const createParticle = (x, y) => {
  const particle = {
    id: particleId++,
    x: x + (Math.random() - 0.5) * 20,
    y: y + (Math.random() - 0.5) * 20,
    opacity: 1,
    scale: Math.random() * 0.5 + 0.5,
    rotation: Math.random() * 360,
    symbol: symbols[Math.floor(Math.random() * symbols.length)],
    color: colors[Math.floor(Math.random() * colors.length)],
    vx: (Math.random() - 0.5) * 2,
    vy: (Math.random() - 0.5) * 2,
    life: 60
  }
  
  particles.value.push(particle)
  
  // 限制粒子数量
  if (particles.value.length > 50) {
    particles.value.shift()
  }
}

// 更新粒子
const updateParticles = () => {
  particles.value.forEach((particle, index) => {
    particle.x += particle.vx
    particle.y += particle.vy
    particle.opacity -= 0.02
    particle.scale *= 0.98
    particle.rotation += 2
    particle.life--
    
    if (particle.life <= 0 || particle.opacity <= 0) {
      particles.value.splice(index, 1)
    }
  })
}

// 鼠标移动事件
const handleMouseMove = (e) => {
  mouseX = e.clientX
  mouseY = e.clientY
  
  // 随机创建粒子
  if (Math.random() < 0.3) {
    createParticle(mouseX, mouseY)
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
.mouse-follower {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  pointer-events: none;
  z-index: 9999;
}

.particle {
  position: absolute;
  font-size: 16px;
  user-select: none;
  pointer-events: none;
  animation: float 2s ease-out forwards;
}

@keyframes float {
  0% {
    transform: translateY(0) scale(1) rotate(0deg);
    opacity: 1;
  }
  100% {
    transform: translateY(-30px) scale(0.5) rotate(360deg);
    opacity: 0;
  }
}
</style>