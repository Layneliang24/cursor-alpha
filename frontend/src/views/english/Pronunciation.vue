<template>
  <div class="pronunciation-page">
    <div class="container mx-auto px-4 py-8">
      <div class="max-w-4xl mx-auto">
        <!-- 页面标题 -->
        <div class="mb-8">
          <h1 class="text-3xl font-bold text-gray-900 mb-2">发音练习</h1>
          <p class="text-gray-600">通过语音识别和发音评估提升英语口语能力</p>
        </div>

        <!-- 练习区域 -->
        <div class="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div class="mb-6">
            <h2 class="text-xl font-semibold mb-4">当前练习</h2>
            
            <!-- 单词显示 -->
            <div class="text-center mb-6">
              <div class="text-4xl font-bold text-blue-600 mb-2">{{ currentWord.word }}</div>
              <div class="text-lg text-gray-600 mb-2">{{ currentWord.phonetic }}</div>
              <div class="text-gray-700">{{ currentWord.definition }}</div>
            </div>

            <!-- 发音按钮 -->
            <div class="flex justify-center space-x-4 mb-6">
              <button 
                @click="playAudio"
                class="bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-lg flex items-center space-x-2 transition-colors"
                :disabled="!currentWord.audio_url"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <span>播放发音</span>
              </button>
              
              <button 
                @click="startRecording"
                class="bg-green-500 hover:bg-green-600 text-white px-6 py-3 rounded-lg flex items-center space-x-2 transition-colors"
                :disabled="isRecording"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"></path>
                </svg>
                <span>{{ isRecording ? '录音中...' : '开始录音' }}</span>
              </button>
            </div>

            <!-- 录音状态 -->
            <div v-if="isRecording" class="text-center">
              <div class="text-red-500 font-semibold mb-2">正在录音...</div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div class="bg-red-500 h-2 rounded-full animate-pulse" style="width: 100%"></div>
              </div>
            </div>

            <!-- 评分结果 -->
            <div v-if="pronunciationScore !== null" class="mt-6 p-4 bg-gray-50 rounded-lg">
              <h3 class="font-semibold mb-2">发音评分</h3>
              <div class="flex items-center space-x-4">
                <div class="text-2xl font-bold" :class="getScoreColor()">
                  {{ pronunciationScore }}%
                </div>
                <div class="flex-1">
                  <div class="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      class="h-2 rounded-full transition-all duration-500"
                      :class="getScoreColor()"
                      :style="{ width: pronunciationScore + '%' }"
                    ></div>
                  </div>
                </div>
              </div>
              <div class="mt-2 text-sm text-gray-600">
                {{ getScoreFeedback() }}
              </div>
            </div>
          </div>

          <!-- 控制按钮 -->
          <div class="flex justify-center space-x-4">
            <button 
              @click="previousWord"
              class="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-lg transition-colors"
              :disabled="currentIndex === 0"
            >
              上一个
            </button>
            <button 
              @click="nextWord"
              class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg transition-colors"
              :disabled="currentIndex === words.length - 1"
            >
              下一个
            </button>
          </div>
        </div>

        <!-- 练习统计 -->
        <div class="bg-white rounded-lg shadow-lg p-6">
          <h2 class="text-xl font-semibold mb-4">练习统计</h2>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div class="text-center p-4 bg-blue-50 rounded-lg">
              <div class="text-2xl font-bold text-blue-600">{{ currentIndex + 1 }}</div>
              <div class="text-sm text-gray-600">当前进度</div>
            </div>
            <div class="text-center p-4 bg-green-50 rounded-lg">
              <div class="text-2xl font-bold text-green-600">{{ completedCount }}</div>
              <div class="text-sm text-gray-600">已完成</div>
            </div>
            <div class="text-center p-4 bg-purple-50 rounded-lg">
              <div class="text-2xl font-bold text-purple-600">{{ averageScore }}%</div>
              <div class="text-sm text-gray-600">平均分数</div>
            </div>
          </div>
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
    
    // 计算属性
    const currentWord = computed(() => words.value[currentIndex.value] || {})
    const completedCount = computed(() => words.value.filter(w => w.score !== null).length)
    const averageScore = computed(() => {
      const scoredWords = words.value.filter(w => w.score !== null)
      if (scoredWords.length === 0) return 0
      const total = scoredWords.reduce((sum, w) => sum + w.score, 0)
      return Math.round(total / scoredWords.length)
    })

    // 方法
    const loadWords = async () => {
      try {
        const response = await englishStore.fetchWords({ limit: 20 })
        words.value = response.results || []
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
          }
        ]
      }
    }

    const playAudio = () => {
      if (currentWord.value.audio_url) {
        const audio = new Audio(currentWord.value.audio_url)
        audio.play()
      } else {
        // 使用浏览器TTS作为备选
        if ('speechSynthesis' in window) {
          const utterance = new SpeechSynthesisUtterance(currentWord.value.word)
          utterance.lang = 'en-US'
          speechSynthesis.speak(utterance)
        }
      }
    }

    const startRecording = () => {
      isRecording.value = true
      pronunciationScore.value = null
      
      // 模拟录音过程
      setTimeout(() => {
        isRecording.value = false
        // 模拟评分结果
        const score = Math.floor(Math.random() * 40) + 60 // 60-100分
        pronunciationScore.value = score
        currentWord.value.score = score
      }, 3000)
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

    const getScoreColor = () => {
      if (pronunciationScore.value >= 90) return 'text-green-600 bg-green-500'
      if (pronunciationScore.value >= 80) return 'text-blue-600 bg-blue-500'
      if (pronunciationScore.value >= 70) return 'text-yellow-600 bg-yellow-500'
      return 'text-red-600 bg-red-500'
    }

    const getScoreFeedback = () => {
      if (pronunciationScore.value >= 90) return '优秀！发音非常准确'
      if (pronunciationScore.value >= 80) return '良好！发音基本准确'
      if (pronunciationScore.value >= 70) return '一般！需要继续练习'
      return '需要改进！建议多听多练'
    }

    // 生命周期
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
      playAudio,
      startRecording,
      nextWord,
      previousWord,
      getScoreColor,
      getScoreFeedback
    }
  }
}
</script>

<style scoped>
.pronunciation-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: .5;
  }
}
</style>
