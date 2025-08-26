
<template>
  <div class="expression-practice">
    <h2>地道表达练习</h2>
    <div class="practice-content">
      <div class="expression-card">
        <h3>{{ currentExpression.expression }}</h3>
        <p>{{ currentExpression.meaning }}</p>
      </div>
      <div class="practice-options">
        <el-button 
          v-for="option in practiceOptions" 
          :key="option.id"
          @click="selectAnswer(option)"
          :type="selectedAnswer === option ? 'primary' : ''"
        >
          {{ option.text }}
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useExpressionService } from '@/services/expressionService'

const expressionService = useExpressionService()
const currentExpression = ref({})
const practiceOptions = ref([])
const selectedAnswer = ref(null)

const loadPractice = async () => {
  const practice = await expressionService.getPracticeQuestion()
  currentExpression.value = practice.expression
  practiceOptions.value = practice.options
}

const selectAnswer = (option) => {
  selectedAnswer.value = option
}

onMounted(() => {
  loadPractice()
})
</script>
