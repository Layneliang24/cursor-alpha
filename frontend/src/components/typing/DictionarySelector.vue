<template>
  <div class="dictionary-selector">
    <div class="selector-header">
      <h3>选择词库</h3>
      <button @click="toggleExpanded" class="toggle-btn">
        {{ isExpanded ? '收起' : '展开' }}
      </button>
    </div>
    
    <div v-if="isExpanded" class="dictionary-grid">
      <div 
        v-for="category in groupedDictionaries" 
        :key="category.name" 
        class="category-group"
      >
        <h4 class="category-title">{{ category.name }}</h4>
        <div class="dictionaries">
          <div
            v-for="dict in category.dictionaries"
            :key="dict.id"
            :class="['dictionary-card', { 'selected': selectedDictionary?.id === dict.id }]"
            @click="selectDictionary(dict)"
          >
            <div class="dict-name">{{ dict.name }}</div>
            <div class="dict-description">{{ dict.description }}</div>
            <div class="dict-stats">
              <span class="word-count">{{ dict.total_words }}词</span>
              <span class="chapter-count">{{ dict.chapter_count }}章</span>
            </div>
            <div v-if="selectedDictionary?.id === dict.id" class="selected-indicator">✓</div>
          </div>
        </div>
      </div>
    </div>
    
    <div v-else class="current-selection">
      <div v-if="selectedDictionary" class="selected-dict">
        <span class="dict-name">{{ selectedDictionary.name }}</span>
        <span class="dict-info">{{ selectedDictionary.total_words }}词 · {{ selectedDictionary.chapter_count }}章</span>
      </div>
      <div v-else class="no-selection">请选择词库</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const props = defineProps({
  modelValue: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:modelValue'])

const dictionaries = ref([])
const isExpanded = ref(false)
const selectedDictionary = computed(() => props.modelValue)

// 按分类分组词库
const groupedDictionaries = computed(() => {
  const groups = {}
  dictionaries.value.forEach(dict => {
    if (!groups[dict.category]) {
      groups[dict.category] = []
    }
    groups[dict.category].push(dict)
  })
  
  return Object.entries(groups).map(([name, dicts]) => ({
    name,
    dictionaries: dicts
  }))
})

const toggleExpanded = () => {
  isExpanded.value = !isExpanded.value
}

const selectDictionary = (dict) => {
  emit('update:modelValue', dict)
  isExpanded.value = false
}

// 获取词库数据
const fetchDictionaries = async () => {
  try {
    const response = await fetch('/api/english/dictionaries/')
    if (response.ok) {
      const data = await response.json()
      dictionaries.value = data
    }
  } catch (error) {
    console.error('获取词库失败:', error)
  }
}

onMounted(() => {
  fetchDictionaries()
})
</script>

<style scoped>
.dictionary-selector {
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

.toggle-btn {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.toggle-btn:hover {
  background: #2563eb;
}

.current-selection {
  padding: 12px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.selected-dict {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.dict-name {
  font-weight: 600;
  color: #1e293b;
}

.dict-info {
  font-size: 14px;
  color: #64748b;
}

.no-selection {
  color: #94a3b8;
  font-style: italic;
}

.dictionary-grid {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.category-group {
  background: white;
  border-radius: 8px;
  padding: 16px;
  border: 1px solid #e2e8f0;
}

.category-title {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #374151;
  padding-bottom: 8px;
  border-bottom: 1px solid #e5e7eb;
}

.dictionaries {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
}

.dictionary-card {
  position: relative;
  background: #f9fafb;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.dictionary-card:hover {
  border-color: #3b82f6;
  background: #f0f9ff;
}

.dictionary-card.selected {
  border-color: #10b981;
  background: #ecfdf5;
}

.dict-name {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 8px;
}

.dict-description {
  font-size: 14px;
  color: #64748b;
  margin-bottom: 12px;
  line-height: 1.4;
}

.dict-stats {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #6b7280;
}

.word-count, .chapter-count {
  background: #e5e7eb;
  padding: 4px 8px;
  border-radius: 4px;
}

.selected-indicator {
  position: absolute;
  top: -8px;
  right: -8px;
  background: #10b981;
  color: white;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: bold;
}
</style>
