<template>
  <div class="animated-background">
    <div class="floating-shapes">
      <div v-for="i in 20" :key="i" class="shape" :style="getShapeStyle(i)"></div>
    </div>
    <div class="gradient-overlay"></div>
  </div>
</template>

<script setup>
const getShapeStyle = (index) => {
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
</script>

<style scoped>
.animated-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
}

.floating-shapes {
  position: absolute;
  width: 100%;
  height: 100%;
}

.shape {
  position: absolute;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  animation: float infinite linear;
  backdrop-filter: blur(2px);
}

.gradient-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle at 30% 70%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
              radial-gradient(circle at 70% 30%, rgba(255, 255, 255, 0.05) 0%, transparent 50%);
  animation: gradientShift 8s ease-in-out infinite;
}

@keyframes float {
  0% {
    transform: translateY(100vh) rotate(0deg);
  }
  100% {
    transform: translateY(-100px) rotate(360deg);
  }
}

@keyframes gradientShift {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}
</style>