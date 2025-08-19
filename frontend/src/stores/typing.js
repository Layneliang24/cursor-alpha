import { defineStore } from 'pinia'
import { ref, reactive, computed, nextTick } from 'vue'
import { englishAPI } from '@/api/english'
import { ElMessage } from 'element-plus'

export const useTypingStore = defineStore('typing', () => {
  // 状态
  const loading = ref(false)
  // 练习状态
  const practiceStarted = ref(false)
  const practiceCompleted = ref(false)
  const isPaused = ref(false)
  const pauseStartTime = ref(null)
  const pauseElapsedTime = ref(null) // 暂停时已用时间
  
  const words = ref([])
  const currentWordIndex = ref(0)
  
  // Word State (qwerty-learner style)
  const wordState = reactive({
    displayWord: '',
    inputWord: '',
    letterStates: [], // 'normal' | 'correct' | 'wrong'
    isFinished: false,
    hasWrong: false,
    correctCount: 0,
    wrongCount: 0,
    startTime: null,
    endTime: null
  })
  
  // UI State
  const userInput = ref('')
  const submitting = ref(false)
  const showFeedback = ref(false)
  const isCorrect = ref(false)
  const isIncorrect = ref(false)
  const isTyping = ref(false)
  const feedbackMessage = ref('')
  
  // 计时器相关
  const sessionStartTime = ref(null)
  const sessionTimer = ref(null)
  const sessionTime = ref(0)
  const correctCount = ref(0)
  const answeredCount = ref(0)
  const currentWPM = ref(0)
  const wordStartTime = ref(null)
  
  // 错误处理状态
  const error = ref(null)
  const retryCount = ref(0)
  const maxRetries = 3
  
  const typingStats = reactive({
    total_words_practiced: 0,
    total_correct_words: 0,
    average_wpm: 0,
    total_practice_time: 0,
    last_practice_date: null
  })
  
  const practiceSettings = reactive({
    wordCount: 20,
    showPhonetic: true
  })
  
  // 词库和章节选择
  const selectedDictionary = ref(null)
  const selectedChapter = ref(1)
  
  const dailyProgress = ref([])
  const wordComponentKey = ref(0) // 强制重新渲染的key

  // 计算属性
  const currentWord = computed(() => {
    return words.value[currentWordIndex.value] || null
  })
  
  const previousWord = computed(() => {
    if (currentWordIndex.value > 0) {
      return words.value[currentWordIndex.value - 1] || null
    }
    return null
  })
  
  const nextWordData = computed(() => {
    if (currentWordIndex.value < words.value.length - 1) {
      return words.value[currentWordIndex.value + 1] || null
    }
    return null
  })
  
  const correctRate = computed(() => {
    if (answeredCount.value === 0) return 0
    return Math.round((correctCount.value / answeredCount.value) * 100)
  })
  
  const averageWPM = computed(() => {
    if (answeredCount.value === 0) return 0
    return Math.round(currentWPM.value / answeredCount.value)
  })
  
  const progressPercentage = computed(() => {
    if (words.value.length === 0) return 0
    return Math.round(((currentWordIndex.value + 1) / words.value.length) * 100)
  })
  
  const hasError = computed(() => error.value !== null)
  const canRetry = computed(() => retryCount.value < maxRetries)

  // 错误处理工具函数
  const handleError = (err, operation = '操作') => {
    console.error(`${operation}失败:`, err)
    error.value = {
      message: err.response?.data?.error || err.message || `${operation}失败，请重试`,
      operation,
      timestamp: Date.now()
    }
    
    if (retryCount.value < maxRetries) {
      ElMessage.warning(`${operation}失败，正在重试... (${retryCount.value + 1}/${maxRetries})`)
    } else {
      ElMessage.error(error.value.message)
    }
  }
  
  const clearError = () => {
    error.value = null
    retryCount.value = 0
  }
  
  const retryOperation = async (operation, ...args) => {
    if (retryCount.value >= maxRetries) {
      ElMessage.error('重试次数已达上限，请稍后再试')
      return false
    }
    
    retryCount.value++
    try {
      const result = await operation(...args)
      clearError()
      return result
    } catch (err) {
      handleError(err, '重试操作')
      return false
    }
  }

  // Actions
  const loadTypingStats = async () => {
    try {
      clearError()
      const response = await englishAPI.getTypingStats()
      Object.assign(typingStats, response)
    } catch (err) {
      handleError(err, '获取统计信息')
      // 自动重试
      if (canRetry.value) {
        setTimeout(() => retryOperation(loadTypingStats), 1000)
      }
    }
  }
  
  const loadDailyProgress = async (days = 7) => {
    try {
      clearError()
      const response = await englishAPI.getTypingDailyProgress({ days })
      dailyProgress.value = response || []
    } catch (err) {
      handleError(err, '获取每日进度')
      // 静默失败，不影响主要功能
    }
  }
  
  const startPractice = async () => {
    try {
      console.log('=== startPractice 开始 ===')
      console.log('当前设置:', practiceSettings)
      loading.value = true
      clearError()
      
      console.log('调用API获取单词...')
      const response = await englishAPI.getTypingWords({
        category: practiceSettings.dictionary,
        limit: practiceSettings.wordCount
      })
      
      console.log('API响应:', response)
      words.value = response || []
      console.log('words.value:', words.value)
      console.log('words.value.length:', words.value.length)
      
      if (words.value.length === 0) {
        console.log('没有找到符合条件的单词')
        ElMessage.warning('没有找到符合条件的单词')
        return false
      }
      
      console.log('设置练习状态...')
      practiceStarted.value = true
      practiceCompleted.value = false
      currentWordIndex.value = 0
      correctCount.value = 0
      answeredCount.value = 0
      sessionStartTime.value = Date.now()
      wordStartTime.value = Date.now()
      sessionTime.value = 0
      
      console.log('练习状态设置完成')
      console.log('practiceStarted.value:', practiceStarted.value)
      console.log('currentWordIndex.value:', currentWordIndex.value)
      console.log('words.value.length:', words.value.length)
      
      // 初始化第一个单词状态
      if (words.value.length > 0) {
        console.log('初始化第一个单词:', words.value[0])
        initWordState(words.value[0])
      }
      
      startSessionTimer()
      
      console.log('=== startPractice 完成 ===')
      ElMessage.success(`开始练习，共 ${words.value.length} 个单词`)
      return true
    } catch (err) {
      console.error('startPractice 错误:', err)
      handleError(err, '获取单词')
      return false
    } finally {
      loading.value = false
    }
  }
  
  // 根据词库和章节开始练习
  const startPracticeWithDictionary = async (dictionaryId, chapter) => {
    try {
      console.log('=== startPracticeWithDictionary 开始 ===')
      console.log('词库名称:', dictionaryId, '章节:', chapter)
      loading.value = true
      clearError()
      
      console.log('调用API获取指定词库和章节的单词...')
      const response = await englishAPI.getTypingWordsByDictionary({
        category: dictionaryId,
        chapter: chapter
      })
      
      console.log('API响应:', response)
      words.value = response || []
      console.log('words.value:', words.value)
      console.log('words.value.length:', words.value.length)
      
      if (words.value.length === 0) {
        console.log('没有找到符合条件的单词')
        ElMessage.warning('没有找到符合条件的单词')
        return false
      }
      
      console.log('设置练习状态...')
      practiceStarted.value = true
      practiceCompleted.value = false
      currentWordIndex.value = 0
      correctCount.value = 0
      answeredCount.value = 0
      sessionStartTime.value = Date.now()
      wordStartTime.value = Date.now()
      sessionTime.value = 0
      
      console.log('练习状态设置完成')
      console.log('practiceStarted.value:', practiceStarted.value)
      console.log('currentWordIndex.value:', currentWordIndex.value)
      console.log('words.value.length:', words.value.length)
      
      // 初始化第一个单词状态
      if (words.value.length > 0) {
        console.log('初始化第一个单词:', words.value[0])
        initWordState(words.value[0])
      }
      
      startSessionTimer()
      
      console.log('=== startPracticeWithDictionary 完成 ===')
      ElMessage.success(`开始练习，共 ${words.value.length} 个单词`)
      return true
    } catch (err) {
      console.error('startPracticeWithDictionary 错误:', err)
      handleError(err, '获取单词')
      return false
    } finally {
      loading.value = false
    }
  }
  
  // 设置会话开始时间
  const setSessionStartTime = (time) => {
    console.log('设置sessionStartTime:', time, '当前时间:', Date.now())
    sessionStartTime.value = time
    // 立即更新sessionTime以反映新时间
    if (time) {
      const elapsed = Math.floor((Date.now() - time) / 1000)
      sessionTime.value = elapsed
      console.log('时间设置后立即更新，已用时间:', elapsed, '秒')
      
      // 强制触发响应式更新
      nextTick(() => {
        console.log('nextTick后确认时间更新，sessionTime:', sessionTime.value)
      })
    }
  }
  
  // 启动计时器
  const startSessionTimer = () => {
    console.log('启动计时器，sessionStartTime:', sessionStartTime.value, '暂停状态:', isPaused.value)
    
    // 验证时间设置是否正确
    if (sessionStartTime.value) {
      const currentTime = Date.now()
      const expectedElapsed = Math.floor((currentTime - sessionStartTime.value) / 1000)
      console.log('时间验证 - 当前时间:', currentTime, '开始时间:', sessionStartTime.value, '预期已用时间:', expectedElapsed, '秒')
      
      // 立即更新sessionTime以匹配预期时间
      sessionTime.value = expectedElapsed
      console.log('计时器启动时立即更新时间，sessionTime:', sessionTime.value)
    }
    
    if (sessionTimer.value) {
      clearInterval(sessionTimer.value)
      console.log('清除旧计时器')
    }
    
    sessionTimer.value = setInterval(() => {
      // 检查是否处于暂停状态
      if (isPaused.value) {
        console.log('计时器暂停中，跳过更新')
        return // 暂停时不更新计时
      }
      
      if (sessionStartTime.value) {
        const elapsed = Math.floor((Date.now() - sessionStartTime.value) / 1000)
        sessionTime.value = elapsed
        // 只在每10秒输出一次，减少日志噪音
        if (elapsed % 10 === 0) {
          console.log('计时器更新，用时:', elapsed, '秒')
        }
      } else {
        console.log('sessionStartTime未设置，无法计时')
      }
    }, 1000)
    console.log('新计时器已启动，ID:', sessionTimer.value)
  }
  
  const stopSessionTimer = () => {
    console.log('停止计时器，当前计时器ID:', sessionTimer.value)
    if (sessionTimer.value) {
      clearInterval(sessionTimer.value)
      sessionTimer.value = null
      console.log('计时器已停止')
    } else {
      console.log('计时器已经是null状态')
    }
  }
  
  // 检查计时器状态
  const isTimerRunning = () => {
    return sessionTimer.value !== null
  }
  
  // 初始化单词状态
  const initWordState = (word) => {
    if (!word) {
      return
    }
    
    // 完全重新创建对象，模拟qwerty-learner的useEffect行为
    const newWordState = {
      displayWord: word.word,
      inputWord: '',
      letterStates: new Array(word.word.length).fill('normal'),
      isFinished: false,
      hasWrong: false,
      correctCount: 0,
      wrongCount: 0,
      startTime: Date.now(),
      endTime: null
    }
    
    // 强制触发响应式更新 - 使用reactive重新包装
    Object.assign(wordState, newWordState)
    
    // 强制触发Vue的响应式更新
    nextTick(() => {
      // 强制触发响应式更新
      const temp = wordState.displayWord
    })
  }
  
  // 处理键盘输入
  const handleKeyInput = (key) => {
    // 设置打字状态为true
    isTyping.value = true
    
    // 如果单词已完成，不处理输入
    if (wordState.isFinished) {
      return
    }
    
    // 如果之前有错误，重置状态
    if (wordState.hasWrong) {
      resetWordState()
    }
    
    const currentInputLength = wordState.inputWord.length
    const targetChar = wordState.displayWord[currentInputLength]
    const inputChar = key
    
    if (inputChar === targetChar) {
      // 输入正确，添加到inputWord
      wordState.inputWord += key
      wordState.letterStates[currentInputLength] = 'correct'
      wordState.correctCount++
      
      // 检查是否完成
      if (wordState.inputWord.length >= wordState.displayWord.length) {
        wordState.isFinished = true
        wordState.endTime = Date.now()
        
        // 更新统计
        correctCount.value++
        answeredCount.value++
        
        // 播放正确声音
        if (window.playCorrectSound) {
          window.playCorrectSound()
        }
        
        // 延迟后进入下一题，给用户时间看到完成状态
        setTimeout(() => {
          nextWord()
        }, 500)
      }
    } else {
      // 输入错误，不添加到inputWord，只标记错误状态
      wordState.letterStates[currentInputLength] = 'wrong'
      wordState.hasWrong = true
      wordState.wrongCount++
      
      // 更新统计
      answeredCount.value++
      
      // 播放错误声音
      if (window.playWrongSound) {
        window.playWrongSound()
      }
      
      // 错误时重新播放当前单词的发音
      if (window.playCurrentWordPronunciation) {
        setTimeout(() => {
          window.playCurrentWordPronunciation()
        }, 200)
      }
      
      // 延迟后重置
      setTimeout(() => {
        resetWordState()
      }, 1000)
    }
  }
  
  // 重置单词状态
  const resetWordState = () => {
    wordState.inputWord = ''
    wordState.letterStates = new Array(wordState.displayWord.length).fill('normal')
    wordState.hasWrong = false
  }
  
  const onInput = () => {
    isTyping.value = true
    if (!wordStartTime.value) {
      wordStartTime.value = Date.now()
    }
  }
  
  const submitWord = async () => {
    if (!userInput.value.trim() || submitting.value) return
    
    submitting.value = true
    const inputWord = userInput.value.trim().toLowerCase()
    const targetWord = currentWord.value.word.toLowerCase()
    const isWordCorrect = inputWord === targetWord
    
    // 显示反馈
    showFeedback.value = true
    isCorrect.value = isWordCorrect
    isIncorrect.value = !isWordCorrect
    
    if (isWordCorrect) {
      feedbackMessage.value = '正确！'
      correctCount.value++
    } else {
      feedbackMessage.value = `错误！正确答案是: ${currentWord.value.word}`
    }
    
    answeredCount.value++
    
    // 计算WPM
    if (wordStartTime.value) {
      const timeElapsed = (Date.now() - wordStartTime.value) / 1000 / 60 // 分钟
      const wordLength = targetWord.length / 5 // 标准单词长度
      currentWPM.value = Math.round(wordLength / timeElapsed)
    }
    
    // 提交到后端（带重试机制）
    try {
      await englishAPI.submitTypingPractice({
        word_id: currentWord.value.id,
        is_correct: isWordCorrect,
        typing_speed: currentWPM.value,
        response_time: wordStartTime.value ? (Date.now() - wordStartTime.value) / 1000 : 0
      })
    } catch (err) {
      handleError(err, '提交练习结果')
      // 提交失败不影响用户体验，继续下一题
    }
    
    // 延迟后进入下一题
    setTimeout(() => {
      nextWord()
    }, 1500)
  }
  
  const skipWord = () => {
    if (submitting.value) return
    nextWord()
  }
  
  const nextWord = () => {
    console.log('nextWord called')
    console.log('Current index:', currentWordIndex.value, 'Total words:', words.value.length)
    
    // 重置状态
    userInput.value = ''
    showFeedback.value = false
    isCorrect.value = false
    isIncorrect.value = false
    isTyping.value = false
    submitting.value = false
    wordStartTime.value = null
    
    // 进入下一题
    currentWordIndex.value++
    
    console.log('New index:', currentWordIndex.value)
    console.log('New currentWord:', words.value[currentWordIndex.value])
    
    if (currentWordIndex.value >= words.value.length) {
      // 练习完成
      console.log('Practice completed!')
      practiceCompleted.value = true
      stopSessionTimer()
      
      // 异步更新统计
      loadTypingStats()
      loadDailyProgress()
      
      // 显示完成消息
      ElMessage.success(`练习完成！正确率: ${correctRate.value}%`)
    } else {
      // 初始化下一个单词状态
      console.log('Initializing next word:', words.value[currentWordIndex.value])
      initWordState(words.value[currentWordIndex.value])
      
      // 触发重新渲染
      wordComponentKey.value++
      console.log('Word component key updated:', wordComponentKey.value)
      
      // 强制触发Vue的响应式更新
      nextTick(() => {
        console.log('Forcing Vue reactivity update')
        // 强制触发currentWord计算属性的重新计算
        const temp = currentWord.value
        console.log('Current word in nextTick:', temp)
        console.log('当前单词详情 - 单词:', temp.word, '音标:', temp.phonetic, '翻译:', temp.translation)
        
        // 触发单词变化事件，用于预加载发音（不自动播放）
        console.log('触发word-changed事件，当前单词:', temp.word)
        window.dispatchEvent(new CustomEvent('word-changed', { 
          detail: { 
            wordIndex: currentWordIndex.value,
            word: temp.word,
            phonetic: temp.phonetic,
            translation: temp.translation
          } 
        }))
        
        // 自动播放新单词的发音 - 由组件处理，这里不需要
        // setTimeout(() => {
        //   if (typeof window.playCurrentWordPronunciation === 'function') {
        //     console.log('自动播放新单词发音:', temp.word)
        //     window.playCurrentWordPronunciation()
        //   }
        // }, 300)
      })
    }
  }
  
  const resetPractice = () => {
    console.log('=== resetPractice 开始 ===')
    
    // 重置暂停状态
    isPaused.value = false
    pauseStartTime.value = null
    pauseElapsedTime.value = null
    
    // 停止计时器
    stopSessionTimer()
    
    // 重置练习状态
    practiceStarted.value = false
    practiceCompleted.value = false
    words.value = []
    currentWordIndex.value = 0
    userInput.value = ''
    
    // 重置wordState - 使用Object.assign而不是.value赋值
    Object.assign(wordState, {
      displayWord: '',
      inputWord: '',
      letterStates: [],
      isFinished: false,
      hasWrong: false,
      correctCount: 0,
      wrongCount: 0,
      startTime: null,
      endTime: null
    })
    
    // 重置其他状态
    showFeedback.value = false
    isCorrect.value = false
    isIncorrect.value = false
    isTyping.value = false
    submitting.value = false
    sessionStartTime.value = null
    wordStartTime.value = null
    sessionTime.value = 0
    correctCount.value = 0
    answeredCount.value = 0
    currentWPM.value = 0
    
    stopSessionTimer()
    clearError()
    console.log('Practice reset complete')
  }
  
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }
  
  const updatePracticeSettings = (settings) => {
    Object.assign(practiceSettings, settings)
  }
  
  const clearFeedback = () => {
    showFeedback.value = false
    isCorrect.value = false
    isIncorrect.value = false
    feedbackMessage.value = ''
  }
  
  // 键盘快捷键支持
  const handleKeydown = (event) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault()
      if (!submitting.value && userInput.value.trim()) {
        submitWord()
      }
    } else if (event.key === 'Escape') {
      event.preventDefault()
      skipWord()
    }
  }

  return {
    // 状态
    loading,
    practiceStarted,
    practiceCompleted,
    isPaused,
    pauseStartTime,
    pauseElapsedTime,
    words,
    currentWordIndex,
    userInput,
    submitting,
    showFeedback,
    isCorrect,
    isIncorrect,
    isTyping,
    feedbackMessage,
    sessionTime,
    correctCount,
    answeredCount,
    currentWPM,
    typingStats,
    practiceSettings,
    dailyProgress,
    error,
    retryCount,
    selectedDictionary,
    selectedChapter,
    
    // 计算属性
    currentWord,
    previousWord,
    nextWordData,
    correctRate,
    averageWPM,
    progressPercentage,
    hasError,
    canRetry,
    
    // Actions
    loadTypingStats,
    loadDailyProgress,
    startPractice,
    startPracticeWithDictionary,
    startSessionTimer,
    stopSessionTimer,
    onInput,
    submitWord,
    skipWord,
    nextWord,
    resetPractice,
    formatTime,
    updatePracticeSettings,
    clearFeedback,
    handleKeydown,
    clearError,
    retryOperation,
    // qwerty-learner style methods
    wordState,
    initWordState,
    handleKeyInput,
    resetWordState,
    wordComponentKey,
    isTimerRunning,
    setSessionStartTime
  }
})
