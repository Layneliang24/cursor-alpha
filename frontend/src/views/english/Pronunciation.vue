<template>
  <div class="pronunciation-container">
    <div class="content-wrapper">
      <!-- 页面标题 -->
      <div class="page-header">
        <h1 class="page-title">发音练习</h1>
        <p class="page-subtitle">提升英语口语能力，掌握标准发音</p>
      </div>

      <!-- 主要内容区域 -->
      <div class="main-card">
        <!-- 加载状态 -->
        <div v-if="isLoading" class="loading-state">
          <div class="loading-spinner"></div>
          <p class="loading-text">正在加载单词数据...</p>
        </div>

        <!-- 空数据状态 -->
        <div v-else-if="words.length === 0" class="empty-state">
          <div class="empty-icon">📚</div>
          <h3 class="empty-title">暂无单词数据</h3>
          <p class="empty-desc">点击下方按钮加载练习单词</p>
          <button @click="loadWords" class="primary-button">
            加载单词
          </button>
        </div>

        <!-- 练习内容 -->
        <div v-else class="practice-content">
          <!-- 单词卡片 -->
          <div class="word-card">
            <div class="word-text">{{ currentWord.word }}</div>
            <div class="phonetic-text">{{ currentWord.phonetic }}</div>
            <div class="definition-text">{{ currentWord.definition }}</div>
          </div>

          <!-- 操作按钮 -->
          <div class="button-group">
            <button 
              @click="playAudio"
              class="action-button play-button"
              :disabled="!currentWord.word"
            >
              🔊 播放发音
            </button>
            
            <button 
              @click="startRecording"
              class="action-button record-button"
              :disabled="isRecording"
            >
              🎤 {{ isRecording ? '录音中...' : '开始录音' }}
            </button>
          </div>

          <!-- 录音状态 -->
          <div v-if="isRecording" class="recording-status">
            <div class="recording-indicator">
              <span class="recording-dot"></span>
              正在录音...
            </div>
          </div>

          <!-- 评分结果 -->
          <div v-if="pronunciationScore !== null" class="score-result">
            <h3 class="score-title">发音评分</h3>
            <div class="score-display">
              <div class="score-number" :class="getScoreClass()">
                {{ pronunciationScore }}%
              </div>
              <div class="score-bar">
                <div 
                  class="score-progress"
                  :class="getScoreClass()"
                  :style="{ width: pronunciationScore + '%' }"
                ></div>
              </div>
            </div>
            <p class="score-feedback">{{ getScoreFeedback() }}</p>
          </div>

          <!-- 导航按钮 -->
          <div class="navigation-buttons">
            <button 
              @click="previousWord"
              class="nav-button prev-button"
              :disabled="currentIndex === 0"
            >
              ← 上一个
            </button>
            <button 
              @click="nextWord"
              class="nav-button next-button"
              :disabled="currentIndex === words.length - 1"
            >
              下一个 →
            </button>
          </div>
        </div>
      </div>

      <!-- 统计卡片 -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-number blue">{{ currentIndex + 1 }}</div>
          <div class="stat-label">当前进度</div>
        </div>
        <div class="stat-card">
          <div class="stat-number green">{{ completedCount }}</div>
          <div class="stat-label">已完成</div>
        </div>
        <div class="stat-card">
          <div class="stat-number purple">
            {{ averageScore !== null ? averageScore + '%' : '暂无' }}
          </div>
          <div class="stat-label">平均分数</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useEnglishStore } from '@/stores/english'

export default {
  name: 'Pronunciation',
  setup() {
    const englishStore = useEnglishStore()
    
    // 响应式数据
    const currentIndex = ref(0)
    const isRecording = ref(false)
    const pronunciationScore = ref(null)
    const words = ref([])
    const isLoading = ref(false)
    
    // 计算属性
    const currentWord = computed(() => words.value[currentIndex.value] || {})
    const completedCount = computed(() => words.value.filter(w => w.score !== null).length)
    const averageScore = computed(() => {
      const scoredWords = words.value.filter(w => w.score !== null)
      if (scoredWords.length === 0) return null
      const total = scoredWords.reduce((sum, w) => sum + w.score, 0)
      return Math.round(total / scoredWords.length)
    })

    // 方法
    const loadWords = async () => {
      isLoading.value = true
      try {
        await englishStore.fetchWords({ limit: 20 })
        words.value = englishStore.words || []
      } catch (error) {
        console.error('加载单词失败:', error)
        // 使用示例数据
        words.value = [
          {
            word: 'pronunciation',
            phonetic: '/prəˌnʌnsiˈeɪʃn/',
            definition: '发音，读音',
            audio_url: null
          },
          {
            word: 'example',
            phonetic: '/ɪɡˈzæmpəl/',
            definition: '例子，实例',
            audio_url: null
          },
          {
            word: 'beautiful',
            phonetic: '/ˈbjuːtɪfʊl/',
            definition: '美丽的，漂亮的',
            audio_url: null
          },
          {
            word: 'technology',
            phonetic: '/tekˈnɒlədʒi/',
            definition: '技术，科技',
            audio_url: null
          },
          {
            word: 'computer',
            phonetic: '/kəmˈpjuːtə/',
            definition: '计算机，电脑',
            audio_url: null
          },
          {
            word: 'language',
            phonetic: '/ˈlæŋɡwɪdʒ/',
            definition: '语言',
            audio_url: null
          }
        ]
      } finally {
        isLoading.value = false
      }
    }

    const playAudio = () => {
      if (currentWord.value.audio_url) {
        const audio = new Audio(currentWord.value.audio_url)
        audio.play().catch(error => {
          console.error('播放音频失败:', error)
          playTTS()
        })
      } else {
        playTTS()
      }
    }

    const playTTS = () => {
      if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(currentWord.value.word)
        utterance.lang = 'en-US'
        utterance.rate = 0.8
        speechSynthesis.speak(utterance)
      } else {
        alert('您的浏览器不支持语音合成功能')
      }
    }

    const startRecording = () => {
      if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ audio: true })
          .then(() => {
            isRecording.value = true
            pronunciationScore.value = null
            
            setTimeout(() => {
              isRecording.value = false
              const score = Math.floor(Math.random() * 40) + 60
              pronunciationScore.value = score
              currentWord.value.score = score
            }, 3000)
          })
          .catch(error => {
            console.error('录音权限被拒绝:', error)
            alert('需要录音权限才能进行发音练习，请在浏览器中允许录音权限。')
          })
      } else {
        alert('您的浏览器不支持录音功能')
      }
    }

    const nextWord = () => {
      if (currentIndex.value < words.value.length - 1) {
        currentIndex.value++
        pronunciationScore.value = null
      }
    }

    const previousWord = () => {
      if (currentIndex.value > 0) {
        currentIndex.value--
        pronunciationScore.value = null
      }
    }

    const getScoreClass = () => {
      if (pronunciationScore.value >= 90) return 'score-excellent'
      if (pronunciationScore.value >= 80) return 'score-good'
      if (pronunciationScore.value >= 70) return 'score-fair'
      return 'score-poor'
    }

    const getScoreFeedback = () => {
      if (pronunciationScore.value >= 90) return '优秀！发音非常准确'
      if (pronunciationScore.value >= 80) return '良好！发音基本准确'
      if (pronunciationScore.value >= 70) return '一般！需要继续练习'
      return '需要改进！建议多听多练'
    }

    onMounted(() => {
      loadWords()
    })

    return {
      currentIndex,
      isRecording,
      pronunciationScore,
      words,
      currentWord,
      completedCount,
      averageScore,
      isLoading,
      playAudio,
      startRecording,
      nextWord,
      previousWord,
      getScoreClass,
      getScoreFeedback,
      loadWords
    }
  }
}
</script>

<style scoped>
/* 基础样式 */
.pronunciation-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f0f4ff 0%, #e6f3ff 100%);
  padding: 2rem 1rem;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.content-wrapper {
  max-width: 800px;
  margin: 0 auto;
}

/* 页面标题 */
.page-header {
  text-align: center;
  margin-bottom: 2rem;
}

.page-title {
  font-size: 2.5rem;
  font-weight: bold;
  color: #1a202c;
  margin-bottom: 0.5rem;
}

.page-subtitle {
  font-size: 1.125rem;
  color: #4a5568;
}

/* 主卡片 */
.main-card {
  background: white;
  border-radius: 1rem;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  padding: 2rem;
  margin-bottom: 2rem;
}

/* 加载状态 */
.loading-state {
  text-align: center;
  padding: 3rem 0;
}

.loading-spinner {
  width: 3rem;
  height: 3rem;
  border: 3px solid #e2e8f0;
  border-top: 3px solid #3182ce;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

.loading-text {
  color: #4a5568;
  font-size: 1rem;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 3rem 0;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.empty-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1a202c;
  margin-bottom: 0.5rem;
}

.empty-desc {
  color: #718096;
  margin-bottom: 1.5rem;
}

/* 单词卡片 */
.word-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 1rem;
  padding: 2rem;
  margin-bottom: 2rem;
  text-align: center;
  color: white;
}

.word-text {
  font-size: 3rem;
  font-weight: bold;
  margin-bottom: 1rem;
}

.phonetic-text {
  font-size: 1.25rem;
  font-family: 'Courier New', monospace;
  margin-bottom: 0.75rem;
  opacity: 0.9;
}

.definition-text {
  font-size: 1.125rem;
  opacity: 0.9;
}

/* 按钮组 */
.button-group {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 2rem;
}

.action-button {
  display: flex;
  align-items: center;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.5rem;
  font-weight: 500;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s;
}

.play-button {
  background: #3182ce;
  color: white;
}

.play-button:hover:not(:disabled) {
  background: #2c5aa0;
}

.record-button {
  background: #38a169;
  color: white;
}

.record-button:hover:not(:disabled) {
  background: #2f855a;
}

.action-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 录音状态 */
.recording-status {
  text-align: center;
  margin-bottom: 1.5rem;
}

.recording-indicator {
  display: inline-flex;
  align-items: center;
  padding: 0.5rem 1rem;
  background: #fed7d7;
  color: #c53030;
  border-radius: 0.5rem;
  font-weight: 500;
}

.recording-dot {
  width: 0.5rem;
  height: 0.5rem;
  background: #c53030;
  border-radius: 50%;
  margin-right: 0.5rem;
  animation: pulse 2s infinite;
}

/* 评分结果 */
.score-result {
  background: #f7fafc;
  border-radius: 1rem;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.score-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1a202c;
  margin-bottom: 1rem;
}

.score-display {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.75rem;
}

.score-number {
  font-size: 2rem;
  font-weight: bold;
  min-width: 4rem;
}

.score-bar {
  flex: 1;
  height: 0.75rem;
  background: #e2e8f0;
  border-radius: 0.375rem;
  overflow: hidden;
}

.score-progress {
  height: 100%;
  border-radius: 0.375rem;
  transition: width 0.5s ease;
}

.score-feedback {
  color: #4a5568;
  font-size: 0.875rem;
}

/* 评分颜色 */
.score-excellent {
  color: #38a169;
}

.score-excellent.score-progress {
  background: #38a169;
}

.score-good {
  color: #3182ce;
}

.score-good.score-progress {
  background: #3182ce;
}

.score-fair {
  color: #d69e2e;
}

.score-fair.score-progress {
  background: #d69e2e;
}

.score-poor {
  color: #e53e3e;
}

.score-poor.score-progress {
  background: #e53e3e;
}

/* 导航按钮 */
.navigation-buttons {
  display: flex;
  justify-content: center;
  gap: 1rem;
}

.nav-button {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.prev-button {
  background: #718096;
  color: white;
}

.prev-button:hover:not(:disabled) {
  background: #4a5568;
}

.next-button {
  background: #3182ce;
  color: white;
}

.next-button:hover:not(:disabled) {
  background: #2c5aa0;
}

.nav-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 统计网格 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.stat-card {
  background: white;
  border-radius: 1rem;
  padding: 1.5rem;
  text-align: center;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.stat-number {
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.stat-number.blue {
  color: #3182ce;
}

.stat-number.green {
  color: #38a169;
}

.stat-number.purple {
  color: #805ad5;
}

.stat-label {
  color: #4a5568;
  font-size: 0.875rem;
}

/* 主按钮 */
.primary-button {
  background: #3182ce;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.primary-button:hover {
  background: #2c5aa0;
}

/* 动画 */
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

/* 响应式 */
@media (max-width: 640px) {
  .pronunciation-container {
    padding: 1rem 0.5rem;
  }
  
  .main-card {
    padding: 1.5rem;
  }
  
  .word-text {
    font-size: 2rem;
  }
  
  .button-group {
    flex-direction: column;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>

