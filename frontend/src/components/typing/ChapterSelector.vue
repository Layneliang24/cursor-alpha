<template>
  <div class="chapter-selector">
    <div class="selector-header">
      <h3>选择章节</h3>
      <div v-if="selectedDictionary" class="dict-info">
        {{ selectedDictionary.name }} - {{ selectedDictionary.total_words }}词
      </div>
    </div>
    
    <div v-if="selectedDictionary" class="chapters-grid">
      <div
        v-for="chapter in chapterList"
        :key="chapter.number"
        :class="['chapter-card', { 'selected': selectedChapter === chapter.number }]"
        @click="selectChapter(chapter.number)"
      >
        <div class="chapter-header">
          <span class="chapter-number">第{{ chapter.number }}章</span>
          <span v-if="selectedChapter === chapter.number" class="selected-indicator">✓</span>
        </div>
        <div class="chapter-stats">
          <span class="word-count">{{ chapter.wordCount }}词</span>
        </div>
        <div class="chapter-progress" v-if="chapter.progress">
          <div class="progress-bar">
            <div 
              class="progress-fill" 
              :style="{ width: chapter.progress.accuracy + '%' }"
            ></div>
          </div>
          <span class="progress-text">正确率: {{ chapter.progress.accuracy }}%</span>
        </div>
      </div>
    </div>
    
    <div v-else class="no-dict-selected">
      请先选择词库
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  selectedDictionary: {
    type: Object,
    default: null
  },
  selectedChapter: {
    type: Number,
    default: 1
  }
})

const emit = defineEmits(['update:selectedChapter'])

// 生成章节列表
const chapterList = computed(() => {
  if (!props.selectedDictionary) return []
  
  const chapters = []
  for (let i = 1; i <= props.selectedDictionary.chapter_count; i++) {
    // 计算每章的单词数（最后一章可能少于25个）
    const isLastChapter = i === props.selectedDictionary.chapter_count
    const totalWords = props.selectedDictionary.total_words
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
      wordCount,
      progress: null // 这里可以添加用户进度数据
    })
  }
  
  return chapters
})

const selectChapter = (chapterNumber) => {
  emit('update:selectedChapter', chapterNumber)
}
</script>

<style scoped>
.chapter-selector {
  background: #f8fafc;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 20px;
}

.selector-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.selector-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
}

.dict-info {
  font-size: 14px;
  color: #64748b;
  background: white;
  padding: 6px 12px;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
}

.no-dict-selected {
  text-align: center;
  color: #94a3b8;
  font-style: italic;
  padding: 40px 20px;
}

.chapters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 12px;
}

.chapter-card {
  position: relative;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  min-height: 100px;
  display: flex;
  flex-direction: column;
}

.chapter-card:hover {
  border-color: #3b82f6;
  background: #f0f9ff;
}

.chapter-card.selected {
  border-color: #10b981;
  background: #ecfdf5;
}

.chapter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.chapter-number {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.selected-indicator {
  background: #10b981;
  color: white;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
}

.chapter-stats {
  margin-bottom: 12px;
}

.word-count {
  background: #e5e7eb;
  color: #6b7280;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.chapter-progress {
  margin-top: auto;
}

.progress-bar {
  width: 100%;
  height: 6px;
  background: #e5e7eb;
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 8px;
}

.progress-fill {
  height: 100%;
  background: #10b981;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 11px;
  color: #6b7280;
}
</style>
