<template>
  <div class="typing-practice-page">
    <!-- 顶部设置栏 -->
    <div class="top-settings" style="display: flex !important; visibility: visible !important; opacity: 1 !important;">
      <div class="left-section">
        <div class="logo">⌨️ Alpha Learner</div>
      </div>
      
      <!-- 词库和章节选择区域 - 同时展示 -->
      <div class="dict-chapter-section">
        <!-- 词库选择 -->
        <div class="dict-selector">
          <span class="selector-label">词库</span>
          <button :class="['dict-btn', { 'expanded': isDictExpanded }]" @click="toggleDictExpanded">
            {{ selectedDictionary ? selectedDictionary.name : 'TOEFL' }}
            <span class="arrow">▼</span>
          </button>
          
          <!-- 词库下拉菜单 -->
          <div :class="['dict-dropdown', { 'expanded': isDictExpanded }]">
            <div 
              v-for="category in groupedDictionaries" 
              :key="category.name" 
              class="category-group"
            >
              <div class="category-title">{{ category.name }}</div>
              <div class="dict-list">
                <div
                  v-for="dict in category.dictionaries"
                  :key="dict.id"
                  :class="['dict-item', { 'selected': selectedDictionary?.id === dict.id }]"
                  @click="selectDictionary(dict)"
                >
                  <span class="dict-name">{{ dict.name }}</span>
                  <span class="dict-info">{{ dict.total_words }}词 · {{ dict.chapter_count }}章</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 章节选择 -->
        <div class="chapter-selector">
          <span class="selector-label">章节</span>
          <button :class="['chapter-btn', { 'expanded': isChapterExpanded }]" @click="toggleChapterExpanded">
            第{{ selectedChapter }}章
            <span class="arrow">▼</span>
          </button>
          
          <!-- 章节下拉菜单 -->
          <div :class="['chapter-dropdown', { 'expanded': isChapterExpanded }]">
            <div
              v-for="chapter in chapterList"
              :key="chapter.number"
              :class="['chapter-item', { 'selected': selectedChapter === chapter.number }]"
              @click="selectChapter(chapter.number)"
            >
              第{{ chapter.number }}章 ({{ chapter.wordCount }}词)
              <span class="practice-count" v-if="getChapterPracticeCount(chapter.number) > 0">
                · 练习{{ getChapterPracticeCountDisplay(chapter.number) }}次
              </span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="settings-bar">
        <span class="setting-item">美音 🔊</span>
        
        <!-- 数据分析入口 -->
        <button @click="goToDataAnalysis" class="analysis-btn" title="数据分析">
          📊
        </button>
        
        <!-- 错题本入口 -->
        <button @click="openWrongWordsNotebook" class="notebook-btn" title="错题本">
          📝
        </button>
        

        
        <!-- 练习控制按钮 -->
        <div class="practice-controls" v-if="practiceStarted && !practiceCompleted">
          <button @click="togglePause" class="control-btn pause-btn">
          {{ isPaused ? '继续' : '暂停' }}
        </button>
          <button @click="resetPractice" class="control-btn restart-btn">
            重新开始
          </button>
        </div>
      </div>
    </div>

    <!-- 主练习区域 -->
    <div class="main-practice-area">
      <!-- 开始状态 -->
      <div v-if="!practiceStarted" class="start-state">
        <div class="start-title">
          {{ selectedDictionary && selectedChapter ? '按任意键开始练习' : '请先选择词库和章节' }}
        </div>
        <div v-if="!selectedDictionary || !selectedChapter" class="selection-hint">
          请在上方选择词库和章节
        </div>
      </div>

      <!-- 打字状态 -->
      <div v-else-if="!practiceCompleted" class="typing-state">
        <div class="current-word-container">
          <div :class="getWordContainerClass()" v-if="wordState && wordState.displayWord">
            <span 
              v-for="(letter, index) in wordState.displayWord" 
              :key="index"
              :class="getLetterClass(index)"
              class="letter"
            >
              {{ letter }}
            </span>
          </div>
          <!-- 使用WordPronunciationIcon组件，每个单词独立管理发音 -->
          <WordPronunciationIcon 
            :key="`pronunciation-${currentWord?.word || 'default'}`"
            ref="wordPronunciationRef"
            :word="currentWord?.word || ''"
            pronunciation-type="us"
          />
        </div>
        
        <div class="word-info" v-if="currentWord">
          <span v-if="currentWord.phonetic" class="phonetic">AmE: [{{ currentWord.phonetic }}]</span>
          <span v-if="currentWord.translation" class="translation">{{ currentWord.translation }}</span>
        </div>
        
        <!-- 进度条 -->
        <div class="progress-section" v-show="shouldShowProgressBar">
          <div class="progress-bar">
            <div 
              class="progress-fill" 
              :style="{ width: progressBarWidth + '%' }"
            ></div>
          </div>
          <div class="progress-text">{{ progressBarText }}</div>
        </div>
        
        <!-- 左右提示词 - 动态显示上一个和下一个单词 -->
        <div class="word-hints">
          <div class="hint-left" v-if="previousWord">
            <span class="hint-word">{{ previousWord.word }}</span>
            <span class="hint-translation">{{ previousWord.translation }}</span>
          </div>
          <div class="hint-right" v-if="nextWord">
            <span class="hint-word">{{ nextWord.word }}</span>
            <span class="hint-translation">{{ nextWord.translation }}</span>
          </div>
        </div>
      </div>

      <!-- 章节完成状态 -->
      <div v-else-if="chapterCompleted" class="chapter-completion-state">
        <!-- 撒花效果 -->
        <div class="confetti-container" v-if="showConfetti">
          <div class="confetti" v-for="i in 50" :key="i" :style="getConfettiStyle(i)"></div>
        </div>
        
        <div class="completion-title">🎉 章节练习完成！</div>
        
        <div class="completion-stats">
          <div class="stat-item">
            <div class="stat-value">{{ chapterCompletionData?.accuracy || 0 }}%</div>
            <div class="stat-label">正确率</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ formatTime(chapterCompletionData?.practiceTime || 0) }}</div>
            <div class="stat-label">练习用时</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ chapterCompletionData?.wpm || 0 }}</div>
            <div class="stat-label">WPM</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ chapterCompletionData?.wrongWords?.length || 0 }}</div>
            <div class="stat-label">错误单词数</div>
          </div>
        </div>
        
        <!-- 错误单词列表 -->
        <div class="wrong-words-section" v-if="chapterCompletionData?.wrongWords?.length > 0">
          <h3>本次练习的错误单词：</h3>
          <div class="wrong-words-list">
            <div 
              v-for="word in chapterCompletionData.wrongWords" 
              :key="word.word"
              class="wrong-word-item"
            >
              <span class="word-text">{{ word.word }}</span>
              <span class="word-translation">{{ word.translation }}</span>
            </div>
          </div>
        </div>
        
        <div class="completion-actions">
          <button @click="repeatChapter" class="action-btn repeat-btn">🔄 重复本章</button>
          <button @click="nextChapter" class="action-btn next-btn">➡️ 下一章节</button>
        </div>
      </div>

      <!-- 练习完成状态（保持向后兼容） -->
      <div v-else class="completion-state">
        <div class="completion-title">练习完成！</div>
        
        <div class="completion-stats">
          <div class="stat-item">
            <div class="stat-value">{{ accuracy || 0 }}%</div>
            <div class="stat-label">正确率</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ totalInputLetters || 0 }}</div>
            <div class="stat-label">输入字母数</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ totalCorrectLetters || 0 }}</div>
            <div class="stat-label">正确字母数</div>
          </div>
        </div>
        
        <button @click="resetPractice" class="restart-btn">重新开始</button>
      </div>
    </div>

    <!-- 底部状态栏 -->
    <div class="bottom-stats" style="display: flex !important; visibility: visible !important; opacity: 1 !important;">
      <div class="stat-item">
        <div class="stat-value">{{ formatTime(sessionTime || 0) }}</div>
        <div class="stat-label">时间</div>
      </div>
      <div class="stat-item">
        <div class="stat-value">{{ totalInputLetters || 0 }}</div>
        <div class="stat-label">输入字母数</div>
      </div>
      <div class="stat-item">
        <div class="stat-value">{{ wpm || 0 }}</div>
        <div class="stat-label">WPM</div>
      </div>
      <div class="stat-item">
        <div class="stat-value">{{ totalCorrectLetters || 0 }}</div>
        <div class="stat-label">正确字母数</div>
      </div>
      <div class="stat-item">
        <div class="stat-value">{{ accuracy || 0 }}%</div>
        <div class="stat-label">正确率</div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, nextTick, computed, reactive, watch, getCurrentInstance } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useTypingStore } from '@/stores/typing'
import useKeySounds from '@/hooks/useKeySounds'
import WordPronunciationIcon from '@/components/typing/WordPronunciationIcon.vue'
import DictionarySelector from '@/components/typing/DictionarySelector.vue'
import ChapterSelector from '@/components/typing/ChapterSelector.vue'
import { englishAPI } from '@/api/english'

export default {
  name: 'TypingPractice',
  components: {
    // Letter // Removed Letter component
    DictionarySelector,
    ChapterSelector,
    WordPronunciationIcon
  },
  setup() {
    const router = useRouter()
    const typingStore = useTypingStore()
    
    // 简单防护：确保typingStore存在
    if (!typingStore) {
      console.error('typingStore 初始化失败')
      return {}
    }
    
    // 本地状态
    const wordComponentKey = ref(0) // This is no longer needed for Letter component
    const isTyping = ref(false) // This is no longer needed for Letter component
    const isPaused = ref(false)
    
    // 声音系统
    const { playKeySound, playCorrectSound, playWrongSound, preloadSounds, testSounds } = useKeySounds()
    
    // 发音系统 - 由WordPronunciationIcon组件管理，这里不需要全局发音
    // const { play: playPronunciation, stop: stopPronunciation, isPlaying: isPronunciationPlaying } = usePronunciation(
    //   computed(() => typingStore.currentWord?.word || ''),
    //   'us'
    // )
    
    // 发音计数器（用于调试）
    let pronunciationCount = 0
    
    // 引用WordPronunciationIcon组件
    const wordPronunciationRef = ref(null)
    const instance = getCurrentInstance()
    
    // 全局发音管理
    const pronunciationInstances = ref(new Set())
    const pronunciationDebounceTimer = ref(null)
    
    // 停止所有发音
    const stopAllPronunciations = () => {
      pronunciationInstances.value.forEach(instance => {
        if (instance && typeof instance.stop === 'function') {
          instance.stop()
        }
      })
      pronunciationInstances.value.clear()
    }
    
    // 添加发音实例到管理列表
    const addPronunciationInstance = (instance) => {
      if (instance) {
        pronunciationInstances.value.add(instance)
      }
    }
    
    // 防抖发音方法
    const debouncedPlayPronunciation = (componentRef) => {
      // 清除之前的定时器
      if (pronunciationDebounceTimer.value) {
        clearTimeout(pronunciationDebounceTimer.value)
      }
      
      // 设置新的定时器，300ms内只执行一次
      pronunciationDebounceTimer.value = setTimeout(() => {
        if (componentRef && componentRef.playSound) {
          componentRef.playSound()
        }
        pronunciationDebounceTimer.value = null
      }, 300)
    }
    
    // 监听单词变化，实现自动发音
    watch(() => typingStore.currentWord?.word, (newWord, oldWord) => {
      // 当有新单词时，自动播放发音
      if (newWord) {
        console.log('自动发音:', newWord)
        
        // 延迟获取组件引用
        setTimeout(() => {
          let componentRef = wordPronunciationRef.value
          if (!componentRef && instance) {
            componentRef = instance.refs?.wordPronunciationRef
          }
          
          if (componentRef) {
            debouncedPlayPronunciation(componentRef)
          } else {
            console.log('组件不可用，延迟重试...')
            // 如果组件还没准备好，延迟一点再试
            setTimeout(() => {
              componentRef = wordPronunciationRef.value
              if (!componentRef && instance) {
                componentRef = instance.refs?.wordPronunciationRef
              }
              
              if (componentRef) {
                debouncedPlayPronunciation(componentRef)
              } else {
                console.log('重试失败')
              }
            }, 500)
          }
        }, 100) // 给组件100ms时间完成渲染
      }
    }, { immediate: true })
    
    // 监听进度条相关状态变化
    watch(() => [typingStore.words, typingStore.practiceStarted, typingStore.practiceCompleted], ([words, practiceStarted, practiceCompleted]) => {
      console.log('进度条状态变化监听:', {
        words: words,
        wordsLength: words?.length,
        practiceStarted: practiceStarted,
        practiceCompleted: practiceCompleted,
        shouldShow: words && words.length > 0 && practiceStarted && !practiceCompleted
      })
    }, { immediate: true, deep: true })
    
    // 监听当前单词索引变化
    watch(() => typingStore.currentWordIndex, (newIndex, oldIndex) => {
      console.log('当前单词索引变化:', { oldIndex, newIndex })
    }, { immediate: true })
    
    // 练习设置
    const practiceSettings = reactive({
      difficulty: 'beginner',
      wordCount: 20,
      showPhonetic: true
    })
    
    // 词库和章节选择
    const selectedDictionary = ref(null)
    const selectedChapter = ref(1)
    
    // 词库和章节列表
    const dictionaries = ref([])
    const groupedDictionaries = ref([])
    const chapterList = ref([])
    
    // 下拉菜单展开状态
    const isDictExpanded = ref(false)
    const isChapterExpanded = ref(false)
    
    // 方法定义
    const startPracticeWithSelection = async () => {
      if (!selectedDictionary.value || !selectedChapter.value) {
        ElMessage.warning('请先选择词库和章节')
        return
      }
      
      console.log('开始练习，词库:', selectedDictionary.value.name, '章节:', selectedChapter.value)
      
      try {
        const success = await typingStore.startPracticeWithDictionary(
          selectedDictionary.value.name,
          selectedChapter.value
        )
        if (success) {
          console.log('练习开始成功')
          isPaused.value = false
          
          // 练习开始后立即播放第一个单词的发音 - 由watch处理，这里不需要
          // setTimeout(() => {
          //   try {
          //     console.log('尝试播放第一个单词发音')
          //     console.log('typingStore.currentWord:', typingStore.currentWord)
          //     
          //     if (typingStore.currentWord?.word) {
          //       console.log('当前单词:', typingStore.currentWord.word)
          //       
          //       // 使用use-sound库的播放函数
          //       if (playPronunciation && typeof playPronunciation === 'function') {
          //         console.log('调用playPronunciation()')
          //         // 先停止当前播放，再播放新发音（参考qwerty learner的playSound逻辑）
          //         if (stopPronunciation && typeof stopPronunciation === 'function') {
          //           stopPronunciation()
          //         }
          //         setTimeout(() => {
          //           playPronunciation()
          //         }, 100)
          //       } else {
          //         console.log('playPronunciation函数不可用')
          //       }
          //     } else {
          //       console.log('typingStore.currentWord?.word 为空')
          //     }
          //   } catch (error) {
          //     console.log('练习开始时播放发音失败:', error)
          //   }
          // }, 500)
        } else {
          console.log('练习开始失败')
        }
      } catch (error) {
        console.error('开始练习时出错:', error)
      }
    }
    
    // 词库和章节选择相关方法
    const toggleDictExpanded = () => {
      isDictExpanded.value = !isDictExpanded.value
      if (isDictExpanded.value) {
        isChapterExpanded.value = false
      }
    }
    
    const toggleChapterExpanded = () => {
      isChapterExpanded.value = !isChapterExpanded.value
      if (isChapterExpanded.value) {
        isDictExpanded.value = false
      }
    }
    
    const selectDictionary = (dict) => {
      selectedDictionary.value = dict
      selectedChapter.value = 1
      isDictExpanded.value = false
      updateChapterList()
      
      // 如果练习已经开始，重新加载单词
      if (typingStore.practiceStarted) {
        startPracticeWithSelection()
      }
    }
    
    const selectChapter = (chapterNumber) => {
      selectedChapter.value = chapterNumber
      isChapterExpanded.value = false
      
      // 如果练习已经开始，重新加载单词
      if (typingStore.practiceStarted) {
        startPracticeWithSelection()
      }
    }
    
    // 获取词库数据
    const fetchDictionaries = async () => {
      try {
        const data = await englishAPI.getDictionaries()
        dictionaries.value = data
        groupDictionaries()
        
        console.log('获取到的词库数据:', data)
        
        // 自动选择默认词库（TOEFL）
        const defaultDict = data.find(dict => 
          dict.name.includes('TOEFL') || 
          dict.name.includes('toefl') || 
          dict.name.includes('托福')
        )
        
        if (defaultDict) {
          console.log('选择默认词库:', defaultDict)
          selectedDictionary.value = defaultDict
          updateChapterList()
        } else {
          // 如果没有找到TOEFL，选择第一个可用的词库
          if (data.length > 0) {
            console.log('未找到TOEFL，选择第一个词库:', data[0])
            selectedDictionary.value = data[0]
            updateChapterList()
          }
        }
      } catch (error) {
        console.error('获取词库失败:', error)
      }
    }
    
    // 按分类分组词库
    const groupDictionaries = () => {
      const groups = {}
      dictionaries.value.forEach(dict => {
        if (!groups[dict.category]) {
          groups[dict.category] = []
        }
        groups[dict.category].push(dict)
      })
      
      groupedDictionaries.value = Object.entries(groups).map(([name, dicts]) => ({
        name,
        dictionaries: dicts
      }))
    }
    
    // 更新章节列表
    const updateChapterList = async () => {
      if (!selectedDictionary.value) {
        chapterList.value = []
        return
      }
      
      try {
        // 实时获取各章节的单词数量
        const response = await englishAPI.getChapterWordCounts(selectedDictionary.value.id)
        
        if (response && response.chapters) {
          chapterList.value = response.chapters
          console.log('获取到真实章节数据:', response.chapters)
        } else {
          // 如果API调用失败，使用备用逻辑
          console.warn('API调用失败，使用备用逻辑')
          fallbackChapterList()
        }
      } catch (error) {
        console.error('获取章节单词数量失败:', error)
        // 使用备用逻辑
        fallbackChapterList()
      }
    }
    
    // 备用章节列表逻辑（保持原有功能）
    const fallbackChapterList = () => {
      const chapters = []
      for (let i = 1; i <= selectedDictionary.value.chapter_count; i++) {
        const isLastChapter = i === selectedDictionary.value.chapter_count
        const totalWords = selectedDictionary.value.total_words
        const wordsPerChapter = 25
        const remainingWords = totalWords % wordsPerChapter
        
        let wordCount
        if (isLastChapter && remainingWords > 0) {
          wordCount = remainingWords
        } else {
          wordCount = wordsPerChapter
        }
        
        chapters.push({
          number: i,
          wordCount
        })
      }
      
      chapterList.value = chapters
    }
    
    // 点击外部关闭下拉菜单
    const handleClickOutside = (event) => {
      const dictSelector = event.target.closest('.dict-selector')
      const chapterSelector = event.target.closest('.chapter-selector')
      
      if (!dictSelector) {
        isDictExpanded.value = false
      }
      if (!chapterSelector) {
        isChapterExpanded.value = false
      }
    }

    const skipWord = () => {
      typingStore.skipWord()
    }

    const resetPractice = () => {
      console.log('重置练习')
      // 重置暂停状态
      isPaused.value = false
      typingStore.isPaused = false
      typingStore.pauseStartTime = null
      typingStore.pauseElapsedTime = null // 重置暂停已用时间
      
      // 确保计时器停止
      typingStore.stopSessionTimer()
      
      // 重置练习状态
      typingStore.resetPractice()
      
      // 重置组件状态
      wordComponentKey.value = 0
      
      // 重新开始练习
      startPracticeWithSelection()
    }

    const finishPractice = async () => {
      try {
        // 完成练习会话
        await englishAPI.completeTypingSession()
        
        // 重置练习状态
        typingStore.resetPractice()
        
        ElMessage.success('练习完成！')
        
        // 可以在这里添加跳转到数据分析页面的逻辑
        // router.push('/english/data-analysis')
        
      } catch (error) {
        console.error('完成练习会话失败:', error)
        ElMessage.error('完成练习失败，但数据已保存')
        
        // 即使API失败，也要重置练习状态
        typingStore.resetPractice()
      }
    }

    const onDictChange = () => {
      console.log('词典改变:', practiceSettings.dictionary)
    }

    const onDifficultyChange = () => {
      console.log('难度改变:', practiceSettings.difficulty)
    }
    
    const togglePause = () => {
      console.log('=== togglePause 开始 ===')
      console.log('当前暂停状态:', isPaused.value)
      console.log('当前计时器状态:', typingStore.isTimerRunning())
      console.log('当前已用时间:', typingStore.sessionTime, '秒')
      console.log('当前sessionStartTime:', typingStore.sessionStartTime)
      
      isPaused.value = !isPaused.value
      // 同步store中的暂停状态
      typingStore.isPaused = isPaused.value
      
      if (isPaused.value) {
        console.log('练习暂停')
        // 记录当前已用时间
        const currentElapsed = typingStore.sessionTime
        typingStore.pauseElapsedTime = currentElapsed
        console.log('记录暂停时已用时间:', currentElapsed, '秒')
        
        // 暂停计时器 - 直接调用store的方法
        typingStore.stopSessionTimer()
        console.log('暂停后计时器状态:', typingStore.isTimerRunning())
      } else {
        console.log('练习继续')
        // 继续计时器，从暂停的时间开始
        if (typingStore.pauseElapsedTime !== null) {
          // 设置新的开始时间，从暂停的时间开始计算
          const newStartTime = Date.now() - (typingStore.pauseElapsedTime * 1000)
          console.log('继续练习，从时间开始:', typingStore.pauseElapsedTime, '秒，新开始时间:', newStartTime)
          console.log('时间计算验证 - 当前时间:', Date.now(), '暂停时间:', typingStore.pauseElapsedTime, '新开始时间:', newStartTime)
          
          // 使用store的方法设置时间，确保状态同步
          typingStore.setSessionStartTime(newStartTime)
          typingStore.pauseElapsedTime = null
          
          // 使用setTimeout确保时间设置完成后再启动计时器
          setTimeout(() => {
            console.log('setTimeout后启动计时器，sessionStartTime:', typingStore.sessionStartTime)
            console.log('setTimeout后sessionTime:', typingStore.sessionTime)
            typingStore.startSessionTimer()
            console.log('继续后计时器状态:', typingStore.isTimerRunning())
            
            // 验证计时器是否正常工作
            setTimeout(() => {
              console.log('验证计时器 - 1秒后sessionTime:', typingStore.sessionTime)
            }, 1000)
          }, 50) // 给50ms确保时间设置完成
        } else {
          // 如果没有暂停时间记录，直接启动计时器
          typingStore.startSessionTimer()
          console.log('继续后计时器状态:', typingStore.isTimerRunning())
        }
      }
      
      console.log('=== togglePause 结束 ===')
    }
    
    // 键盘事件处理
    const handleGlobalKeydown = (event) => {
      console.log('键盘事件:', event.key, '练习状态:', typingStore.practiceStarted)
      
      // 如果练习还没开始，按任意键开始
      if (!typingStore.practiceStarted) {
        event.preventDefault()
        console.log('按任意键开始练习')
        // 检查是否已选择词库和章节
        if (selectedDictionary.value && selectedChapter.value) {
          startPracticeWithSelection()
        } else {
          ElMessage.warning('请先选择词库和章节')
        }
        return
      }
      
      // 如果练习已开始但还没完成，处理输入
      if (typingStore.practiceStarted && !typingStore.practiceCompleted) {
        // 检查是否处于暂停状态
        if (isPaused.value) {
          console.log('练习已暂停，不处理输入')
          return
        }
        
        // 处理特殊按键
        if (event.key === 'Escape') {
          event.preventDefault()
          console.log('ESC键 - 退出练习')
          finishPractice()
          return
        }
        
        if (event.key === ' ') {
          event.preventDefault()
          console.log('空格键 - 跳过单词')
          skipWord()
          return
        }
        
        if (event.key === 'Enter') {
          event.preventDefault()
          console.log('回车键 - 重新开始')
          resetPractice()
          return
        }
        
        // 处理字母输入
        if (event.key.length === 1 && /[a-zA-Z]/.test(event.key)) {
          event.preventDefault()
          console.log('输入字母:', event.key)
          
          // 播放键盘音效
          try {
            playKeySound()
          } catch (error) {
            console.log('播放键盘音效失败:', error)
          }
          
          typingStore.handleKeyInput(event.key)
        }
      }
    }
    
    // 监听单词变化事件
    const handleWordChanged = (event) => {
      wordComponentKey.value++ // No longer needed
      console.log('单词变化:', event.detail.word)
      
      // 单词变化时，watch会自动处理发音播放，这里不需要额外处理
    }
    
    // 生命周期
    onMounted(async () => {
      // 获取词库数据
      await fetchDictionaries()
      
      // 添加点击外部关闭下拉菜单的事件监听
      document.addEventListener('click', handleClickOutside)
      
      // 监听练习完成事件
      window.addEventListener('practice-completed', finishPractice)
      
      // 预加载键盘音效
      try {
        preloadSounds()
      } catch (error) {
        console.log('预加载键盘音效失败:', error)
      }
      
      // 设置全局声音函数
      window.playKeySound = playKeySound
      window.playCorrectSound = playCorrectSound
      window.playWrongSound = playWrongSound
      // window.playPronunciation = playPronunciation // No longer needed
      window.playCurrentWordPronunciation = () => {
        try {
          if (typingStore.currentWord?.word) {
            console.log('手动发音:', typingStore.currentWord.word)
            
            // 延迟获取组件引用
            setTimeout(() => {
              let componentRef = wordPronunciationRef.value
              if (!componentRef && instance) {
                componentRef = instance.refs?.wordPronunciationRef
              }
              
              if (componentRef) {
                debouncedPlayPronunciation(componentRef)
              } else {
                console.log('组件不可用，延迟重试...')
                // 如果组件还没准备好，延迟一点再试
                setTimeout(() => {
                  componentRef = wordPronunciationRef.value
                  if (!componentRef && instance) {
                    componentRef = instance.refs?.wordPronunciationRef
                  }
                  
                  if (componentRef) {
                    debouncedPlayPronunciation(componentRef)
                  } else {
                    console.log('重试失败')
                  }
                }, 100)
              }
            }, 100)
          } else {
            console.log('当前单词为空')
          }
        } catch (error) {
          console.log('发音失败:', error)
        }
      }
      
      // 添加事件监听 - 只保留一个键盘事件监听
      document.addEventListener('keydown', handleGlobalKeydown)
      window.addEventListener('word-changed', handleWordChanged)
      
      // 移除重复的键盘事件监听
      // document.addEventListener('keydown', handleStartPractice)
      
      // 设置全局发音管理函数
      window.stopAllPronunciations = stopAllPronunciations
      window.addPronunciationInstance = addPronunciationInstance
      
      // 调试信息：检查组件是否正确渲染
      console.log('组件已挂载')
      console.log('初始状态检查:', {
        words: typingStore.words,
        wordsLength: typingStore.words?.length,
        practiceStarted: typingStore.practiceStarted,
        practiceCompleted: typingStore.practiceCompleted,
        currentWordIndex: typingStore.currentWordIndex
      })
      
      // 延迟检查组件状态
      setTimeout(() => {
        if (wordPronunciationRef.value) {
          console.log('发音组件就绪')
        } else {
          console.log('发音组件未就绪')
        }
        
        // 检查进度条状态
        console.log('延迟状态检查:', {
          words: typingStore.words,
          wordsLength: typingStore.words?.length,
          practiceStarted: typingStore.practiceStarted,
          practiceCompleted: typingStore.practiceCompleted,
          currentWordIndex: typingStore.currentWordIndex,
          shouldShowProgressBar: typingStore.words && typingStore.words.length > 0 && typingStore.practiceStarted && !typingStore.practiceCompleted
        })
      }, 1000)
    })
    
    // 处理按任意键开始练习
    const handleStartPractice = (event) => {
      if (!typingStore.practiceStarted && selectedDictionary.value && selectedChapter.value) {
        // 忽略功能键
        if (event.key === 'Shift' || event.key === 'Control' || event.key === 'Alt' || event.key === 'Meta') {
          return
        }
        
        console.log('按任意键开始练习:', event.key)
        startPracticeWithSelection()
      }
    }
    
    onUnmounted(() => {
      // 清理全局发音管理函数
      delete window.stopAllPronunciations
      delete window.addPronunciationInstance
      
      // 清理防抖定时器
      if (pronunciationDebounceTimer.value) {
        clearTimeout(pronunciationDebounceTimer.value)
      }
      
      // 停止所有发音
      stopAllPronunciations()
      
      // 移除全局键盘事件监听
      document.removeEventListener('keydown', handleGlobalKeydown)
    })
    
    // 返回响应式数据
    return {
      // 从store获取的状态
      loading: typingStore.loading,
      practiceCompleted: typingStore.practiceCompleted,
      words: typingStore.words,
      currentWordIndex: typingStore.currentWordIndex,
      wordState: typingStore.wordState,
      correctRate: typingStore.correctRate, // This is now accuracy
      progressPercentage: typingStore.progressPercentage,
      typingStats: typingStore.typingStats,
      practiceSettings: typingStore.practiceSettings,
      averageWPM: typingStore.averageWPM,
      
      // 本地状态
      practiceStarted: computed(() => typingStore.practiceStarted),
      currentWord: computed(() => typingStore.currentWord),
      wordComponentKey, // No longer needed
      isTyping, // No longer needed
      isPaused,
      
      // 方法
      startPracticeWithSelection,
      skipWord,
      resetPractice,
      finishPractice,
      // playPronunciation, // No longer needed
      onDictChange,
      onDifficultyChange,
      togglePause,
      formatTime: (seconds) => {
        const mins = Math.floor(seconds / 60)
        const secs = seconds % 60
        return `${mins}:${secs.toString().padStart(2, '0')}`
      },

      // 计算属性 - 使用computed确保响应式更新
      accuracy: computed(() => typingStore.correctRate),
      totalInputLetters: computed(() => typingStore.totalInputLetters),
      totalCorrectLetters: computed(() => typingStore.totalCorrectLetters),
      totalWrongLetters: computed(() => typingStore.totalWrongLetters),
      sessionTime: computed(() => {
        const time = typingStore.sessionTime
        console.log('sessionTime computed更新:', time)
        return time
      }),
      practiceCompleted: computed(() => typingStore.practiceCompleted),
      currentWord: computed(() => typingStore.currentWord),
      wpm: computed(() => {
        const currentSessionTime = typingStore.sessionTime
        const currentCorrectLetters = typingStore.totalCorrectLetters
        if (currentSessionTime === 0) return 0
        const minutes = currentSessionTime / 60
        // 基于字母计算WPM：每5个字母算一个单词
        return Math.round((currentCorrectLetters / 5) / minutes)
      }),
      
      // 进度条相关计算属性
      shouldShowProgressBar: computed(() => {
        const hasWords = typingStore.words && typingStore.words.length > 0
        const isPracticeActive = typingStore.practiceStarted && !typingStore.practiceCompleted
        console.log('进度条显示条件检查:', { hasWords, isPracticeActive, wordsLength: typingStore.words?.length })
        return hasWords && isPracticeActive
      }),
      
      progressBarWidth: computed(() => {
        if (!typingStore.words || typingStore.words.length === 0) return 0
        const progress = ((typingStore.currentWordIndex + 1) / typingStore.words.length) * 100
        console.log('进度条宽度计算:', { currentIndex: typingStore.currentWordIndex, totalWords: typingStore.words.length, progress })
        return Math.min(progress, 100)
      }),
      
      progressBarText: computed(() => {
        if (!typingStore.words || typingStore.words.length === 0) return '0/0'
        const text = `${typingStore.currentWordIndex + 1}/${typingStore.words.length}`
        console.log('进度条文本:', text)
        return text
      }),
      
      // 字母样式方法
      getLetterClass: (index) => {
        if (!typingStore.wordState || !typingStore.wordState.letterStates) {
          return ''
        }
        const letterState = typingStore.wordState.letterStates[index];
        // 移除频繁的日志输出
        if (letterState === 'correct') {
          return 'correct';
        } else if (letterState === 'wrong') {
          return 'incorrect';
        } else if (letterState === 'current') {
          return 'current';
        } else {
          return '';
        }
      },
      
      // 获取单词容器类名，支持抖动效果
      getWordContainerClass: () => {
        if (!typingStore.wordState) {
          return 'current-word'
        }
        return typingStore.wordState.shake ? 'current-word shake' : 'current-word'
      },

      // 动态提示词
      previousWord: computed(() => typingStore.previousWord),
      nextWord: computed(() => typingStore.nextWordData),

      // 词库和章节选择相关
      selectedDictionary,
      selectedChapter,
      dictionaries,
      groupedDictionaries,
      chapterList,
      isDictExpanded,
      isChapterExpanded,
      toggleDictExpanded,
      toggleChapterExpanded,
      selectDictionary,
      selectChapter,
      
      // 练习开始方法
      startPracticeWithSelection,
      handleStartPractice,
      
      // 跳转到数据分析页面
      goToDataAnalysis: () => {
        router.push('/english/data-analysis')
      },
      
      // 章节完成相关方法 ⭐ 新增
      repeatChapter: () => {
        typingStore.resetChapterCompletion()
        typingStore.resetPractice()
        // 重新开始当前章节
        startPracticeWithSelection()
      },
      
      nextChapter: () => {
        typingStore.resetChapterCompletion()
        typingStore.resetPractice()
        // 选择下一章节
        if (selectedChapter.value < chapterList.value.length) {
          selectChapter(selectedChapter.value + 1)
        } else {
          // 如果是最后一章，回到第一章
          selectChapter(1)
        }
      },
      
      // 错题本相关方法 ⭐ 新增
      openWrongWordsNotebook: () => {
        router.push('/english/wrong-words-notebook')
      },
      
      // 撒花效果相关方法 ⭐ 新增
      getConfettiStyle: (index) => {
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
      },
      
      // 章节完成相关计算属性 ⭐ 新增
      chapterCompleted: computed(() => typingStore.chapterCompleted),
      chapterCompletionData: computed(() => typingStore.chapterCompletionData),
      showConfetti: computed(() => typingStore.chapterCompleted),
      
      // 章节练习次数相关 ⭐ 新增
      getChapterPracticeCount: (chapterNumber) => typingStore.chapterPracticeCounts[chapterNumber] || 0,
      getChapterPracticeCountDisplay: (chapterNumber) => typingStore.getChapterPracticeCountDisplay(chapterNumber),
      
      // 错题本相关 ⭐ 新增
      wrongWordsNotebook: computed(() => typingStore.wrongWordsNotebook),
      wrongWordsNotebookStats: computed(() => typingStore.getWrongWordsNotebookStats()),
      
      // 每日练习时长相关 ⭐ 新增
      dailyPracticeDuration: computed(() => typingStore.dailyPracticeDuration),
      formattedDailyPracticeDuration: computed(() => typingStore.getFormattedDailyPracticeDuration())
    }
  }
}
</script>

<style scoped>
.typing-practice-page {
  height: calc(100vh - 180px);
  width: 100%;
  background: #fafafa;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
  z-index: 1;
  margin: 0;
  padding: 5px;
}

/* 顶部设置栏 */
.top-settings {
  flex-shrink: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background: #f8fafc !important;
  border-bottom: 1px solid #e2e8f0;
  z-index: 10;
  min-height: 50px;
  position: relative;
  margin: 0 20px 12px 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.left-section {
  display: flex;
  align-items: center;
  gap: 12px;
  z-index: 10000;
}

.logo {
  font-size: 24px;
  font-weight: 700;
  color: #3b82f6;
  z-index: 10000;
}

.dict-chapter-section {
  display: flex;
  gap: 20px;
  align-items: center;
  font-size: 16px;
  color: #64748b;
  z-index: 10000;
}

.dict-selector, .chapter-selector {
  position: relative;
  display: flex;
  align-items: center;
  gap: 8px;
}

.selector-label {
  font-size: 14px;
  color: #64748b;
  font-weight: 500;
  min-width: 40px;
}

.dict-btn, .chapter-btn {
  padding: 8px 16px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  color: #1e293b;
  background: white;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 120px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.dict-btn:focus, .chapter-btn:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.dict-btn:hover, .chapter-btn:hover {
  border-color: #cbd5e1;
  background: #f8fafc;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.dict-btn .arrow, .chapter-btn .arrow {
  font-size: 12px;
  transition: transform 0.2s ease;
  color: #64748b;
}

.dict-btn.expanded .arrow, .chapter-btn.expanded .arrow {
  transform: rotate(180deg);
}

.dict-dropdown, .chapter-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  z-index: 10000;
  min-width: 220px;
  max-height: 300px;
  overflow-y: auto;
  display: none;
  margin-top: 8px;
}

.dict-dropdown.expanded, .chapter-dropdown.expanded {
  display: block;
}

.category-group {
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
}

.category-group:last-child {
  border-bottom: none;
}

.category-title {
  font-size: 14px;
  color: #475569;
  font-weight: 600;
  margin-bottom: 10px;
  padding-left: 5px;
}

.dict-list {
  padding: 8px 15px;
  transition: background-color 0.2s ease;
}

.dict-item {
  padding: 10px 15px;
  cursor: pointer;
  transition: all 0.2s ease;
  border-radius: 8px;
  margin-bottom: 6px;
}

.dict-item:hover {
  background-color: #f0f9ff;
  transform: translateX(4px);
}

.dict-item.selected {
  background-color: #dbeafe;
  font-weight: 600;
  color: #1d4ed8;
  border-left: 3px solid #3b82f6;
}

.dict-name {
  font-weight: 500;
  color: #3b82f6;
  display: block;
  font-size: 15px;
}

.dict-info {
  font-size: 12px;
  color: #64748b;
  margin-top: 4px;
  display: block;
}

.chapter-item {
  padding: 10px 15px;
  cursor: pointer;
  transition: all 0.2s ease;
  border-radius: 8px;
  margin-bottom: 6px;
}

.chapter-item:hover {
  background-color: #f0f9ff;
  transform: translateX(4px);
}

.chapter-item.selected {
  background-color: #dbeafe;
  font-weight: 600;
  color: #1d4ed8;
  border-left: 3px solid #3b82f6;
}

.settings-bar {
  display: flex;
  align-items: center;
  gap: 16px;
  z-index: 10000;
}

.setting-item {
  color: #64748b;
  font-size: 14px;
  font-weight: 500;
}

.test-btn {
  padding: 8px 16px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  color: #1e293b;
  background: white;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 100px;
  display: flex;
  justify-content: center;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.test-btn:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.test-btn:hover {
  border-color: #cbd5e1;
  background: #f8fafc;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.analysis-btn {
  padding: 8px 12px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 16px;
  color: #1e293b;
  background: white;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  justify-content: center;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  margin-right: 8px;
}

.analysis-btn:focus {
  outline: none;
  border-color: #10b981;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

.analysis-btn:hover {
  border-color: #10b981;
  background: #f0fdf4;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.practice-controls {
  display: flex;
  gap: 10px;
}

.control-btn {
  padding: 8px 16px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  color: #1e293b;
  background: white;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 100px;
  display: flex;
  justify-content: center;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.control-btn:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.control-btn:hover {
  border-color: #cbd5e1;
  background: #f8fafc;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.control-btn.pause-btn {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.control-btn.pause-btn:hover {
  background: #2563eb;
  border-color: #2563eb;
}

.control-btn.restart-btn {
  background: #10b981;
  color: white;
  border-color: #10b981;
}

.control-btn.restart-btn:hover {
  background: #059669;
  border-color: #059669;
}

.start-practice-btn {
  background: #10b981;
  color: white;
  border: none;
  padding: 16px 32px;
  border-radius: 8px;
  font-size: 18px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.start-practice-btn:hover:not(:disabled) {
  background: #059669;
  transform: translateY(-2px);
}

.start-practice-btn:disabled {
  background: #9ca3af;
  cursor: not-allowed;
  transform: none;
}

.selection-hint {
  margin-top: 16px;
  color: #6b7280;
  font-size: 14px;
}

/* 主练习区域 */
.main-practice-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 0 20px;
  text-align: center;
  min-height: 0;
  overflow: hidden;
  position: relative;
}

/* 开始状态 */
.start-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.start-title {
  font-size: 36px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 20px;
}

.selection-hint {
  color: #64748b;
  font-size: 16px;
  font-style: italic;
}

/* 打字状态 */
.typing-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.current-word-container {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
  font-family: monospace;
}

.current-word {
  display: flex;
  gap: 0;
  font-size: 48px;
  font-weight: 600;
  padding: 0 4px;
  line-height: 1.2;
  height: 1.2em;
  font-family: monospace;
  transition: all 0.2s ease;
}

.letter {
  font-size: 48px;
  font-weight: 600;
  padding: 0 4px;
  line-height: 1.2;
  height: 1.2em;
  font-family: monospace;
  transition: all 0.2s ease;
}

.letter.correct {
  color: #10b981;
}

.letter.incorrect {
  color: #ef4444;
}

.letter.current {
  color: #3b82f6;
  border-bottom: 3px solid #3b82f6;
}

/* 抖动效果 */
.current-word.shake {
  animation: wordShake 0.6s ease-in-out;
}

@keyframes wordShake {
  0%, 100% { transform: translateX(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-4px); }
  20%, 40%, 60%, 80% { transform: translateX(4px); }
}

.word-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 30px;
}

.phonetic {
  font-size: 18px;
  color: #64748b;
  font-style: italic;
}

.translation {
  font-size: 20px;
  color: #1e293b;
  font-weight: 500;
}

.word-hints {
  display: flex;
  gap: 40px;
  margin-top: 20px;
}

.hint-left, .hint-right {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 12px 20px;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.hint-word {
  font-size: 16px;
  font-weight: 600;
  color: #3b82f6;
}

.hint-translation {
  font-size: 14px;
  color: #64748b;
}

/* 完成状态 */
.completion-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 30px;
}

.completion-title {
  font-size: 32px;
  font-weight: 700;
  color: #10b981;
}

.completion-stats {
  display: flex;
  gap: 40px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #1e293b;
}

.stat-label {
  font-size: 14px;
  color: #64748b;
}

.restart-btn {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.restart-btn:hover {
  background: #2563eb;
  transform: translateY(-2px);
}

/* 进度条样式 */
.progress-section {
  width: 100%;
  max-width: 300px;
  margin: 20px 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.progress-bar {
  width: 100%;
  height: 6px;
  background-color: #e2e8f0;
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #8b5cf6);
  border-radius: 3px;
  transition: width 0.3s ease-in-out;
}

.progress-text {
  font-size: 14px;
  font-weight: 600;
  color: #64748b;
}

/* 底部状态栏 */
.bottom-stats {
  flex-shrink: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 40px;
  padding: 16px 20px;
  background: #f8fafc !important;
  border-top: 1px solid #e2e8f0;
  z-index: 10;
  min-height: 50px;
  position: relative;
  margin: 10px 20px 0 20px;
  border-radius: 12px;
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.1);
}

.bottom-stats .stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  min-width: 80px;
}

.bottom-stats .stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #3b82f6;
}

.bottom-stats .stat-label {
  font-size: 12px;
  color: #64748b;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .top-settings {
    flex-direction: column;
    gap: 16px;
    padding: 20px;
}

  .dict-chapter-section {
    flex-direction: column;
    align-items: center;
    gap: 16px;
  }

  .dict-selector, .chapter-selector {
    width: 100%;
    justify-content: center;
  }
  
  .dict-dropdown, .chapter-dropdown {
    left: 50%;
    transform: translateX(-50%);
  }
}

@media (max-width: 768px) {
  .top-settings {
    margin: 0 10px 12px 10px;
    padding: 16px;
  }
  
  .logo {
    font-size: 20px;
  }
  
  .dict-btn, .chapter-btn {
    min-width: 100px;
    font-size: 13px;
    padding: 8px 12px;
  }
  
  .selector-label {
    font-size: 13px;
    min-width: 35px;
  }
  
  .start-practice-btn, .pause-btn {
    padding: 10px 20px;
    font-size: 14px;
  }
}

@media (max-width: 480px) {
  .top-settings {
    margin: 0 5px 10px 5px;
    padding: 12px;
  }
  
  .dict-chapter-section {
    gap: 12px;
  }
  
  .dict-btn, .chapter-btn {
    min-width: 80px;
    font-size: 12px;
    padding: 6px 10px;
  }
  
  .selector-label {
    font-size: 12px;
    min-width: 30px;
  }
  
  .start-practice-btn, .pause-btn {
    padding: 8px 16px;
    font-size: 13px;
  }
}

/* 移除sound-icon样式，现在由WordPronunciationIcon组件管理 */
/* .sound-icon {
  background: none;
  border: none;
    font-size: 24px;
  cursor: pointer;
  padding: 8px;
  border-radius: 50%;
  transition: all 0.2s ease;
  color: #3b82f6;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 48px;
  width: 48px;
}
  
.sound-icon:hover {
  background: #f0f9ff;
  transform: scale(1.1);
}
  
.sound-icon:active {
  transform: scale(0.95);
} */

/* 章节完成界面样式 ⭐ 新增 */
.chapter-completion-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  text-align: center;
  position: relative;
  overflow: hidden;
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

.completion-title {
  font-size: 32px;
  font-weight: 700;
  color: #3b82f6;
  margin-bottom: 30px;
  z-index: 2;
}

.completion-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 30px;
  z-index: 2;
}

.completion-stats .stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 20px;
  background: #f8fafc;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}

.completion-stats .stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #3b82f6;
}

.completion-stats .stat-label {
  font-size: 14px;
  color: #64748b;
  font-weight: 500;
}

.wrong-words-section {
  margin-bottom: 30px;
  z-index: 2;
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
  gap: 5px;
  padding: 10px 15px;
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
  color: #7f1d1d;
}

.completion-actions {
  display: flex;
  gap: 20px;
  z-index: 2;
}

.action-btn {
  padding: 15px 30px;
  font-size: 16px;
  font-weight: 600;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.repeat-btn {
  background: #f3f4f6;
  color: #374151;
}

.repeat-btn:hover {
  background: #e5e7eb;
  transform: translateY(-2px);
}

.next-btn {
  background: #3b82f6;
  color: white;
}

.next-btn:hover {
  background: #2563eb;
  transform: translateY(-2px);
}

/* 错题本按钮样式 ⭐ 新增 */
.notebook-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  padding: 8px;
  border-radius: 50%;
  transition: all 0.2s ease;
  color: #f59e0b;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 40px;
  width: 40px;
}

.notebook-btn:hover {
  background: #fef3c7;
  transform: scale(1.1);
}

.notebook-btn:active {
  transform: scale(0.95);
}

/* 章节练习次数样式 ⭐ 新增 */
.practice-count {
  font-size: 12px;
  color: #10b981;
  background: #d1fae5;
  padding: 2px 6px;
  border-radius: 10px;
  margin-left: 8px;
  font-weight: 600;
}
</style>
