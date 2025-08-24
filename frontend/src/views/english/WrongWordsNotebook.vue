<template>
  <div class="wrong-words-notebook">
    <div class="notebook-header">
      <h1>📝 错题本</h1>
      <div class="header-actions">
        <button class="export-btn" @click="exportToExcel">
          📊 导出Excel
        </button>
        <button class="clear-btn" @click="clearNotebook">
          🗑️ 清空错题本
        </button>
      </div>
    </div>

    <div class="notebook-stats">
      <div class="stat-item">
        <span class="stat-label">总错误单词数:</span>
        <span class="stat-value">{{ wrongWordsNotebook.length }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">总错误次数:</span>
        <span class="stat-value">{{ totalErrorCount }}</span>
      </div>
    </div>

    <div v-if="wrongWordsNotebook.length === 0" class="empty-state">
      <p>🎉 太棒了！目前没有错误单词</p>
      <p>继续练习，保持这个状态！</p>
    </div>

    <div v-else class="wrong-words-list">
      <div
        v-for="(word, index) in wrongWordsNotebook"
        :key="index"
        class="wrong-word-item"
      >
        <div class="word-info">
          <div class="word-main">
            <span class="word-text">{{ word.word }}</span>
            <span class="word-translation">{{ word.translation }}</span>
          </div>
          <div class="word-details">
            <span class="error-count">错误次数: {{ word.errorCount }}</span>
            <span class="dictionary">来自: {{ word.dictionary }}</span>
          </div>
        </div>
        <div class="word-actions">
          <button class="delete-btn" @click="removeWrongWord(word.word)">
            🗑️ 删除
          </button>
        </div>
      </div>
    </div>

    <div class="back-to-practice">
      <button class="back-btn" @click="goBackToPractice">
        ← 返回练习
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useTypingStore } from '@/stores/typing'

const router = useRouter()
const typingStore = useTypingStore()

// 计算属性
const wrongWordsNotebook = computed(() => typingStore.wrongWordsNotebook)
const totalErrorCount = computed(() => {
  return wrongWordsNotebook.value.reduce((total, word) => total + word.errorCount, 0)
})

// 方法
const removeWrongWord = (word) => {
  typingStore.removeWrongWord(word)
}

const clearNotebook = () => {
  if (confirm('确定要清空错题本吗？此操作不可恢复。')) {
    typingStore.clearWrongWordsNotebook()
  }
}

const exportToExcel = () => {
  // 这里实现Excel导出功能
  alert('Excel导出功能待实现')
}

const goBackToPractice = () => {
  router.push('/english/typing-practice')
}

// 生命周期
onMounted(() => {
  // 页面加载时的初始化逻辑
  console.log('错题本页面加载完成')
})
</script>

<style scoped>
.wrong-words-notebook {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.notebook-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid #f0f0f0;
}

.notebook-header h1 {
  margin: 0;
  color: #333;
  font-size: 28px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.export-btn, .clear-btn {
  padding: 10px 16px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
}

.export-btn {
  background: #4CAF50;
  color: white;
}

.export-btn:hover {
  background: #45a049;
}

.clear-btn {
  background: #f44336;
  color: white;
}

.clear-btn:hover {
  background: #da190b;
}

.notebook-stats {
  display: flex;
  gap: 30px;
  margin-bottom: 30px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #666;
}

.empty-state p {
  margin: 10px 0;
  font-size: 16px;
}

.wrong-words-list {
  margin-bottom: 30px;
}

.wrong-word-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  margin-bottom: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #ff6b6b;
  transition: all 0.3s ease;
}

.wrong-word-item:hover {
  background: #e9ecef;
  transform: translateX(5px);
}

.word-info {
  flex: 1;
}

.word-main {
  margin-bottom: 8px;
}

.word-text {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin-right: 15px;
}

.word-translation {
  font-size: 16px;
  color: #666;
}

.word-details {
  display: flex;
  gap: 20px;
  font-size: 14px;
  color: #888;
}

.error-count {
  color: #ff6b6b;
  font-weight: 500;
}

.delete-btn {
  padding: 8px 12px;
  background: #ff6b6b;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.3s ease;
}

.delete-btn:hover {
  background: #ff5252;
}

.back-to-practice {
  text-align: center;
  padding-top: 20px;
  border-top: 2px solid #f0f0f0;
}

.back-btn {
  padding: 12px 24px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  transition: background 0.3s ease;
}

.back-btn:hover {
  background: #0056b3;
}

@media (max-width: 768px) {
  .notebook-header {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }
  
  .header-actions {
    justify-content: center;
  }
  
  .notebook-stats {
    flex-direction: column;
    gap: 15px;
  }
  
  .word-details {
    flex-direction: column;
    gap: 5px;
  }
}
</style> 