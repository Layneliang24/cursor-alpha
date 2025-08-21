
// 在 TypingPractice.vue 中添加的调试代码

// 1. 在 setup 函数开始处添加
console.log('=== TypingPractice 组件 setup 开始 ===')
console.log('初始 store 状态:', {
  words: typingStore.words,
  practiceStarted: typingStore.practiceStarted,
  practiceCompleted: typingStore.practiceCompleted,
  currentWordIndex: typingStore.currentWordIndex
})

// 2. 在 onMounted 中添加
onMounted(async () => {
  console.log('=== TypingPractice 组件 onMounted ===')
  console.log('挂载时 store 状态:', {
    words: typingStore.words,
    practiceStarted: typingStore.practiceStarted,
    practiceCompleted: typingStore.practiceCompleted,
    currentWordIndex: typingStore.currentWordIndex
  })
  
  // 延迟检查
  setTimeout(() => {
    console.log('延迟检查 store 状态:', {
      words: typingStore.words,
      practiceStarted: typingStore.practiceStarted,
      practiceCompleted: typingStore.practiceCompleted,
      currentWordIndex: typingStore.currentWordIndex
    })
  }, 1000)
})

// 3. 添加状态变化监听
watch(() => [typingStore.words, typingStore.practiceStarted, typingStore.practiceCompleted], 
  ([words, started, completed]) => {
    console.log('=== Store 状态变化 ===', {
      words: words,
      wordsLength: words?.length,
      practiceStarted: started,
      practiceCompleted: completed,
      shouldShowProgressBar: words && words.length > 0 && started && !completed
    })
  }, 
  { immediate: true, deep: true }
)

// 4. 在进度条计算属性中添加日志
const shouldShowProgressBar = computed(() => {
  const hasWords = typingStore.words && typingStore.words.length > 0
  const isPracticeActive = typingStore.practiceStarted && !typingStore.practiceCompleted
  const result = hasWords && isPracticeActive
  
  console.log('进度条显示条件计算:', {
    hasWords,
    isPracticeActive,
    result,
    words: typingStore.words,
    wordsLength: typingStore.words?.length,
    practiceStarted: typingStore.practiceStarted,
    practiceCompleted: typingStore.practiceCompleted
  })
  
  return result
})
