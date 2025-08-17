<template>
  <div class="practice-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1>英语练习</h1>
      <div class="header-stats">
        <el-statistic title="总练习次数" :value="practiceStatistics.totalPractices" />
        <el-statistic title="正确率" :value="practiceStatistics.correctRate" suffix="%" />
        <el-statistic title="平均用时" :value="practiceStatistics.averageTime" suffix="秒" />
      </div>
    </div>

    <!-- 练习类型选择 -->
    <el-card class="practice-selector" v-if="!practiceStarted">
      <template #header>
        <span>选择练习类型</span>
      </template>
      
      <div class="practice-types">
        <div 
          v-for="type in practiceTypes" 
          :key="type.value"
          class="practice-type-card"
          :class="{ 'selected': selectedType === type.value }"
          @click="selectPracticeType(type.value)"
        >
          <div class="type-icon">
            <el-icon><component :is="type.icon" /></el-icon>
          </div>
          <h3>{{ type.name }}</h3>
          <p>{{ type.description }}</p>
          <div class="type-stats" v-if="type.stats">
            <span>难度: {{ type.difficulty }}</span>
            <span>题目数: {{ type.questionCount }}</span>
          </div>
        </div>
      </div>

      <div class="practice-settings">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="题目数量">
              <el-select v-model="questionCount" style="width: 100%">
                <el-option label="5题" :value="5" />
                <el-option label="10题" :value="10" />
                <el-option label="15题" :value="15" />
                <el-option label="20题" :value="20" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="难度等级">
              <el-select v-model="difficultyLevel" style="width: 100%">
                <el-option label="初级" value="beginner" />
                <el-option label="中级" value="intermediate" />
                <el-option label="高级" value="advanced" />
                <el-option label="混合" value="mixed" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </div>

      <div class="start-button">
        <el-button 
          type="primary" 
          size="large" 
          @click="startPractice"
          :disabled="!selectedType"
          :loading="questionsLoading"
        >
          开始练习
        </el-button>
      </div>
    </el-card>

    <!-- 练习进行中 -->
    <div class="practice-session" v-else-if="currentQuestions.length > 0">
      <!-- 练习进度 -->
      <div class="practice-progress">
        <div class="progress-info">
          <span>题目进度: {{ currentQuestionIndex + 1 }} / {{ currentQuestions.length }}</span>
          <span>用时: {{ formatTime(sessionTime) }}</span>
          <span>正确: {{ correctAnswers }} / {{ answeredQuestions }}</span>
        </div>
        <el-progress 
          :percentage="Math.round(((currentQuestionIndex + 1) / currentQuestions.length) * 100)"
          :stroke-width="8"
          color="#409EFF"
        />
      </div>

      <!-- 当前题目 -->
      <el-card class="question-card" v-if="currentQuestion">
        <div class="question-header">
          <h2>第 {{ currentQuestionIndex + 1 }} 题</h2>
          <el-tag :type="getQuestionTypeTag(currentQuestion.type)">
            {{ getQuestionTypeName(currentQuestion.type) }}
          </el-tag>
        </div>

        <div class="question-content">
          <div class="question-text">
            {{ currentQuestion.question }}
          </div>

          <!-- 不同题型的答题界面 -->
          <!-- 单词拼写题 -->
          <div v-if="currentQuestion.type === 'word_spelling'" class="answer-input">
            <el-input
              v-model="userAnswer"
              placeholder="请输入单词拼写"
              size="large"
              @keyup.enter="submitAnswer"
              :disabled="answerSubmitted"
            />
          </div>

          <!-- 单词释义题 -->
          <div v-else-if="currentQuestion.type === 'word_meaning'" class="answer-input">
            <el-input
              v-model="userAnswer"
              type="textarea"
              :rows="3"
              placeholder="请输入单词释义"
              @keyup.ctrl.enter="submitAnswer"
              :disabled="answerSubmitted"
            />
          </div>

          <!-- 选择题 -->
          <div v-else-if="currentQuestion.options" class="answer-options">
            <el-radio-group v-model="userAnswer" @change="handleOptionChange" :disabled="answerSubmitted">
              <el-radio
                v-for="(option, index) in currentQuestion.options"
                :key="index"
                :label="option"
                class="option-radio"
              >
                {{ option }}
              </el-radio>
            </el-radio-group>
          </div>
        </div>

        <!-- 答案反馈 -->
        <div class="answer-feedback" v-if="answerSubmitted">
          <div class="feedback-result" :class="{ 'correct': isCorrect, 'incorrect': !isCorrect }">
            <el-icon>
              <SuccessFilled v-if="isCorrect" />
              <CircleCloseFilled v-else />
            </el-icon>
            <span>{{ isCorrect ? '回答正确！' : '回答错误' }}</span>
          </div>
          
          <div class="correct-answer" v-if="!isCorrect">
            <strong>正确答案:</strong> {{ currentQuestion.correct_answer }}
          </div>

          <div class="answer-explanation" v-if="currentQuestion.explanation">
            <strong>解释:</strong> {{ currentQuestion.explanation }}
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="question-actions">
          <el-button @click="skipQuestion" :disabled="answerSubmitted">
            跳过
          </el-button>
          <el-button 
            v-if="!answerSubmitted"
            type="primary" 
            @click="submitAnswer"
            :disabled="!userAnswer.trim()"
          >
            提交答案
          </el-button>
          <el-button 
            v-else
            type="primary" 
            @click="nextQuestion"
          >
            {{ currentQuestionIndex < currentQuestions.length - 1 ? '下一题' : '完成练习' }}
          </el-button>
        </div>
      </el-card>
    </div>

    <!-- 练习完成 -->
    <div class="practice-completed" v-else-if="practiceCompleted">
      <el-card class="completion-card">
        <div class="completion-content">
          <el-icon class="completion-icon"><Trophy /></el-icon>
          <h2>练习完成！</h2>
          
          <div class="completion-stats">
            <div class="stat-row">
              <div class="stat-item">
                <span class="stat-number">{{ currentQuestions.length }}</span>
                <span class="stat-label">总题数</span>
              </div>
              <div class="stat-item">
                <span class="stat-number">{{ correctAnswers }}</span>
                <span class="stat-label">正确数</span>
              </div>
              <div class="stat-item">
                <span class="stat-number">{{ Math.round((correctAnswers / currentQuestions.length) * 100) }}%</span>
                <span class="stat-label">正确率</span>
              </div>
              <div class="stat-item">
                <span class="stat-number">{{ formatTime(totalTime) }}</span>
                <span class="stat-label">总用时</span>
              </div>
            </div>
          </div>

          <div class="completion-actions">
            <el-button size="large" @click="resetPractice">
              重新练习
            </el-button>
            <el-button type="primary" size="large" @click="goToDashboard">
              返回首页
            </el-button>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useEnglishStore } from '@/stores/english'
import { ElMessage } from 'element-plus'
import { 
  Document, Edit, Trophy, SuccessFilled, CircleCloseFilled 
} from '@element-plus/icons-vue'

export default {
  name: 'EnglishPractice',
  components: {
    Document,
    Edit,
    Trophy,
    SuccessFilled,
    CircleCloseFilled
  },
  setup() {
    const router = useRouter()
    const englishStore = useEnglishStore()

    // 状态管理
    const practiceStarted = ref(false)
    const practiceCompleted = ref(false)
    const selectedType = ref('')
    const questionCount = ref(10)
    const difficultyLevel = ref('mixed')
    const currentQuestionIndex = ref(0)
    const userAnswer = ref('')
    const answerSubmitted = ref(false)
    const isCorrect = ref(false)
    const correctAnswers = ref(0)
    const answeredQuestions = ref(0)
    const sessionStartTime = ref(0)
    const sessionTime = ref(0)
    const totalTime = ref(0)
    
    let timer = null

    // 练习类型配置
    const practiceTypes = [
      {
        value: 'word_spelling',
        name: '单词拼写',
        description: '根据释义拼写单词',
        icon: 'Edit',
        difficulty: '中等',
        questionCount: '5-20题'
      },
      {
        value: 'word_meaning',
        name: '单词释义',
        description: '写出单词的中文释义',
        icon: 'Document',
        difficulty: '简单',
        questionCount: '5-20题'
      },
      {
        value: 'typing_practice',
        name: '智能打字练习',
        description: '实时打字练习，提升拼写速度和准确性',
        icon: 'Trophy',
        difficulty: '自适应',
        questionCount: '10-50题'
      }
    ]

    // 计算属性
    const practiceStatistics = computed(() => englishStore.practiceStatistics)
    const questionsLoading = computed(() => englishStore.questionsLoading)
    const currentQuestions = computed(() => englishStore.currentQuestions)
    
    const currentQuestion = computed(() => {
      if (currentQuestionIndex.value >= currentQuestions.value.length) return null
      return currentQuestions.value[currentQuestionIndex.value]
    })

    // 方法
    const selectPracticeType = (type) => {
      selectedType.value = type
    }

    const startPractice = async () => {
      try {
        // 如果是打字练习，跳转到专门的打字练习页面
        if (selectedType.value === 'typing_practice') {
          // 设置标记，表示从Practice页面跳转过来
          sessionStorage.setItem('from_typing_practice', 'true')
          router.push('/english/typing-practice')
          return
        }
        
        await englishStore.generatePracticeQuestions(selectedType.value, questionCount.value)
        if (currentQuestions.value.length === 0) {
          ElMessage.warning('没有找到合适的题目，请稍后再试')
          return
        }
        
        practiceStarted.value = true
        sessionStartTime.value = Date.now()
        startTimer()
        
        ElMessage.success(`开始 ${getQuestionTypeName(selectedType.value)} 练习`)
      } catch (error) {
        ElMessage.error('生成题目失败')
        console.error(error)
      }
    }

    const submitAnswer = async () => {
      if (!userAnswer.value.trim() || answerSubmitted.value) return

      answerSubmitted.value = true
      answeredQuestions.value++
      
      // 判断答案是否正确
      const correct = userAnswer.value.trim().toLowerCase() === 
                    currentQuestion.value.correct_answer.toLowerCase()
      isCorrect.value = correct
      
      if (correct) {
        correctAnswers.value++
      }

      // 记录练习结果
      try {
        const practiceData = {
          practice_type: selectedType.value,
          content_id: currentQuestion.value.word_id || 0,
          content_type: 'word',
          question: currentQuestion.value.question,
          user_answer: userAnswer.value,
          correct_answer: currentQuestion.value.correct_answer,
          time_spent: Math.round((Date.now() - sessionStartTime.value) / 1000)
        }
        
        await englishStore.submitPracticeAnswer(practiceData)
      } catch (error) {
        console.error('记录练习结果失败:', error)
      }
    }

    const nextQuestion = () => {
      if (currentQuestionIndex.value < currentQuestions.value.length - 1) {
        currentQuestionIndex.value++
        userAnswer.value = ''
        answerSubmitted.value = false
        isCorrect.value = false
      } else {
        completePractice()
      }
    }

    const skipQuestion = () => {
      answeredQuestions.value++
      nextQuestion()
    }

    const completePractice = () => {
      practiceStarted.value = false
      practiceCompleted.value = true
      totalTime.value = sessionTime.value
      stopTimer()
      
      ElMessage.success('练习完成！')
    }

    const resetPractice = () => {
      practiceStarted.value = false
      practiceCompleted.value = false
      selectedType.value = ''
      currentQuestionIndex.value = 0
      userAnswer.value = ''
      answerSubmitted.value = false
      isCorrect.value = false
      correctAnswers.value = 0
      answeredQuestions.value = 0
      sessionTime.value = 0
      totalTime.value = 0
      stopTimer()
    }

    const goToDashboard = () => {
      router.push('/english/dashboard')
    }

    const handleOptionChange = (value) => {
      userAnswer.value = value
    }

    const getQuestionTypeName = (type) => {
      const typeObj = practiceTypes.find(t => t.value === type)
      return typeObj ? typeObj.name : type
    }

    const getQuestionTypeTag = (type) => {
      const typeMap = {
        'word_spelling': 'primary',
        'word_meaning': 'success',
        'typing_practice': 'warning'
      }
      return typeMap[type] || 'info'
    }

    const formatTime = (seconds) => {
      const mins = Math.floor(seconds / 60)
      const secs = seconds % 60
      return `${mins}:${secs.toString().padStart(2, '0')}`
    }

    const startTimer = () => {
      timer = setInterval(() => {
        sessionTime.value = Math.floor((Date.now() - sessionStartTime.value) / 1000)
      }, 1000)
    }

    const stopTimer = () => {
      if (timer) {
        clearInterval(timer)
        timer = null
      }
    }

    // 生命周期
    onMounted(() => {
      englishStore.fetchPracticeRecords({ page: 1, page_size: 50 })
    })

    onUnmounted(() => {
      stopTimer()
    })

    return {
      // 状态
      practiceStarted,
      practiceCompleted,
      selectedType,
      questionCount,
      difficultyLevel,
      currentQuestionIndex,
      userAnswer,
      answerSubmitted,
      isCorrect,
      correctAnswers,
      answeredQuestions,
      sessionTime,
      totalTime,
      
      // 配置
      practiceTypes,
      
      // 计算属性
      practiceStatistics,
      questionsLoading,
      currentQuestions,
      currentQuestion,
      
      // 方法
      selectPracticeType,
      startPractice,
      submitAnswer,
      nextQuestion,
      skipQuestion,
      resetPractice,
      goToDashboard,
      handleOptionChange,
      getQuestionTypeName,
      getQuestionTypeTag,
      formatTime
    }
  }
}
</script>

<style scoped>
.practice-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.page-header h1 {
  margin: 0;
  color: #303133;
  font-size: 28px;
}

.header-stats {
  display: flex;
  gap: 40px;
}

.practice-selector {
  margin-bottom: 30px;
}

.practice-types {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.practice-type-card {
  border: 2px solid #e4e7ed;
  border-radius: 12px;
  padding: 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.practice-type-card:hover {
  border-color: #409EFF;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2);
}

.practice-type-card.selected {
  border-color: #409EFF;
  background-color: #f0f9ff;
}

.type-icon {
  font-size: 48px;
  color: #409EFF;
  margin-bottom: 16px;
}

.practice-type-card h3 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 20px;
}

.practice-type-card p {
  margin: 0 0 16px 0;
  color: #606266;
  font-size: 14px;
}

.type-stats {
  display: flex;
  justify-content: space-around;
  font-size: 12px;
  color: #909399;
}

.practice-settings {
  margin-bottom: 30px;
}

.start-button {
  text-align: center;
}

.practice-session {
  max-width: 800px;
  margin: 0 auto;
}

.practice-progress {
  margin-bottom: 30px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  font-size: 14px;
  color: #606266;
}

.question-card {
  margin-bottom: 30px;
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.question-header h2 {
  margin: 0;
  color: #303133;
}

.question-content {
  margin-bottom: 30px;
}

.question-text {
  font-size: 20px;
  color: #303133;
  margin-bottom: 24px;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #409EFF;
}

.answer-input {
  margin-bottom: 24px;
}

.answer-options {
  margin-bottom: 24px;
}

.option-radio {
  display: block;
  margin-bottom: 12px;
  padding: 12px 16px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.option-radio:hover {
  border-color: #409EFF;
  background-color: #f0f9ff;
}

.answer-feedback {
  margin-bottom: 24px;
  padding: 20px;
  border-radius: 8px;
  background-color: #f8f9fa;
}

.feedback-result {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 12px;
}

.feedback-result.correct {
  color: #67C23A;
}

.feedback-result.incorrect {
  color: #F56C6C;
}

.correct-answer, .answer-explanation {
  margin-bottom: 8px;
  color: #606266;
}

.question-actions {
  text-align: center;
}

.question-actions .el-button {
  margin: 0 8px;
  min-width: 100px;
}

.practice-completed {
  max-width: 600px;
  margin: 0 auto;
}

.completion-card {
  text-align: center;
}

.completion-content {
  padding: 40px 20px;
}

.completion-icon {
  font-size: 80px;
  color: #67C23A;
  margin-bottom: 20px;
}

.completion-content h2 {
  margin: 0 0 30px 0;
  color: #303133;
  font-size: 28px;
}

.completion-stats {
  margin-bottom: 40px;
}

.stat-row {
  display: flex;
  justify-content: space-around;
  gap: 20px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.stat-number {
  font-size: 32px;
  font-weight: bold;
  color: #409EFF;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.completion-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 20px;
  }
  
  .header-stats {
    flex-direction: column;
    gap: 16px;
  }
  
  .practice-types {
    grid-template-columns: 1fr;
  }
  
  .stat-row {
    flex-direction: column;
    gap: 20px;
  }
  
  .completion-actions {
    flex-direction: column;
  }
}
</style>
