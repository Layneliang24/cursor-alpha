<template>
  <div class="chapter-completion-page">
    <!-- 撒花效果 -->
    <div class="confetti-container" v-if="showConfetti">
      <div 
        class="confetti" 
        v-for="i in 50" 
        :key="i" 
        :style="getConfettiStyle(i)"
      ></div>
    </div>
    
    <!-- 主要内容 -->
    <div class="completion-content">
      <div class="completion-title">🎉 章节练习完成！</div>
      
      <!-- 统计数据 -->
      <div class="completion-stats">
        <div class="stat-item">
          <div class="stat-value">{{ completionData?.accuracy || 0 }}%</div>
          <div class="stat-label">正确率</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ formatTime(completionData?.practiceTime || 0) }}</div>
          <div class="stat-label">练习用时</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ completionData?.wpm || 0 }}</div>
          <div class="stat-label">WPM</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ completionData?.wrongWords?.length || 0 }}</div>
          <div class="stat-label">错误单词数</div>
        </div>
      </div>
      
      <!-- 错误单词列表 -->
      <div class="wrong-words-section" v-if="completionData?.wrongWords?.length > 0">
        <h3>本次练习的错误单词：</h3>
        <div class="wrong-words-list">
          <div 
            v-for="word in completionData.wrongWords" 
            :key="word.word"
            class="wrong-word-item"
          >
            <span class="word-text">{{ word.word }}</span>
            <span class="word-translation">{{ word.translation }}</span>
          </div>
        </div>
      </div>
      
      <!-- 操作按钮 -->
      <div class="completion-actions">
        <button @click="repeatChapter" class="action-btn repeat-btn">
          🔄 重复本章
        </button>
        <button @click="nextChapter" class="action-btn next-btn">
          ➡️ 下一章节
        </button>
        <button @click="backToPractice" class="action-btn back-btn">
          🏠 返回练习
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useTypingStore } from '@/stores/typing'

export default {
  name: 'ChapterCompletion',
  props: {
    completionData: {
      type: Object,
      required: true
    }
  },
  emits: ['repeat-chapter', 'next-chapter', 'back-to-practice'],
  setup(props, { emit }) {
    const router = useRouter()
    const typingStore = useTypingStore()
    
    const showConfetti = ref(true)
    
    // 撒花样式生成
    const getConfettiStyle = (index) => {
      const colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57', '#ff9ff3', '#54a0ff']
      const color = colors[index % colors.length]
      const left = Math.random() * 100
      const animationDelay = Math.random() * 3
      const animationDuration = 3 + Math.random() * 2
      
      return {
        left: `${left}%`,
        backgroundColor: color,
        animationDelay: `${animationDelay}s`,
        animationDuration: `${animationDuration}s`
      }
    }
    
    // 格式化时间
    const formatTime = (milliseconds) => {
      if (!milliseconds) return '0:00'
      const seconds = Math.floor(milliseconds / 1000)
      const minutes = Math.floor(seconds / 60)
      const remainingSeconds = seconds % 60
      return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
    }
    
    // 重复本章
    const repeatChapter = () => {
      emit('repeat-chapter')
    }
    
    // 下一章节
    const nextChapter = () => {
      emit('next-chapter')
    }
    
    // 返回练习
    const backToPractice = () => {
      emit('back-to-practice')
    }
    
    // 自动隐藏撒花效果
    onMounted(() => {
      setTimeout(() => {
        showConfetti.value = false
      }, 5000) // 5秒后自动隐藏撒花
    })
    
    return {
      showConfetti,
      getConfettiStyle,
      formatTime,
      repeatChapter,
      nextChapter,
      backToPractice
    }
  }
}
</script>

<style scoped>
.chapter-completion-page {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 99999;
  overflow: hidden;
  /* 确保完全覆盖，包括隐藏父组件的顶部栏和底部栏 */
  backdrop-filter: blur(5px);
}

.confetti-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
}

.confetti {
  position: absolute;
  width: 10px;
  height: 10px;
  animation: confetti-fall linear infinite;
}

@keyframes confetti-fall {
  0% {
    transform: translateY(-100vh) rotate(0deg);
    opacity: 1;
  }
  100% {
    transform: translateY(100vh) rotate(720deg);
    opacity: 0;
  }
}

.completion-content {
  position: relative;
  z-index: 2;
  background: white;
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
  max-width: 600px;
  width: 90%;
  text-align: center;
  /* 确保内容完全居中 */
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.completion-title {
  font-size: 36px;
  font-weight: 700;
  color: #3b82f6;
  margin-bottom: 30px;
}

.completion-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 30px;
  /* 确保统计框完全居中 */
  width: 100%;
  max-width: 500px;
  margin-left: auto;
  margin-right: auto;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 20px;
  background: #f8fafc;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #3b82f6;
}

.stat-label {
  font-size: 14px;
  color: #64748b;
  font-weight: 500;
}

.wrong-words-section {
  margin-bottom: 30px;
}

.wrong-words-section h3 {
  font-size: 18px;
  color: #64748b;
  margin-bottom: 15px;
}

.wrong-words-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
}

.wrong-word-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 8px 12px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  font-size: 14px;
}

.word-text {
  font-weight: 600;
  color: #dc2626;
}

.word-translation {
  color: #6b7280;
  font-size: 12px;
}

.completion-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
  flex-wrap: wrap;
}

.action-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.repeat-btn {
  background: #f59e0b;
  color: white;
}

.repeat-btn:hover {
  background: #d97706;
  transform: translateY(-2px);
}

.next-btn {
  background: #10b981;
  color: white;
}

.next-btn:hover {
  background: #059669;
  transform: translateY(-2px);
}

.back-btn {
  background: #6b7280;
  color: white;
}

.back-btn:hover {
  background: #4b5563;
  transform: translateY(-2px);
}

@media (max-width: 768px) {
  .completion-content {
    padding: 20px;
    margin: 20px;
  }
  
  .completion-title {
    font-size: 28px;
  }
  
  .completion-stats {
    grid-template-columns: 1fr;
  }
  
  .completion-actions {
    flex-direction: column;
  }
}
</style> 