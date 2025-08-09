<template>
  <div class="table-of-contents" v-if="headings.length > 0">
    <div class="toc-header">
      <h4>目录</h4>
    </div>
    <nav class="toc-nav">
      <ul class="toc-list">
        <li 
          v-for="heading in headings" 
          :key="heading.id"
          :class="['toc-item', `toc-level-${heading.level}`, { active: activeId === heading.id }]"
        >
          <a 
            :href="`#${heading.id}`" 
            @click.prevent="scrollToHeading(heading.id)"
            class="toc-link"
          >
            {{ heading.text }}
          </a>
        </li>
      </ul>
    </nav>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const headings = ref([])
const activeId = ref('')

const generateTOC = () => {
  const articleContent = document.querySelector('.article-content')
  if (!articleContent) return

  const headingElements = articleContent.querySelectorAll('h1, h2, h3, h4, h5, h6')
  
  headings.value = Array.from(headingElements).map((heading, index) => {
    const id = heading.id || `heading-${index}`
    heading.id = id
    
    return {
      id,
      text: heading.textContent,
      level: parseInt(heading.tagName.charAt(1))
    }
  })
}

const scrollToHeading = (id) => {
  const element = document.getElementById(id)
  if (element) {
    element.scrollIntoView({ 
      behavior: 'smooth',
      block: 'start'
    })
  }
}

const updateActiveHeading = () => {
  const headingElements = headings.value.map(h => document.getElementById(h.id)).filter(Boolean)
  
  for (let i = headingElements.length - 1; i >= 0; i--) {
    const rect = headingElements[i].getBoundingClientRect()
    if (rect.top <= 100) {
      activeId.value = headingElements[i].id
      break
    }
  }
}

onMounted(() => {
  setTimeout(() => {
    generateTOC()
    window.addEventListener('scroll', updateActiveHeading)
    updateActiveHeading()
  }, 100)
})

onUnmounted(() => {
  window.removeEventListener('scroll', updateActiveHeading)
})

defineExpose({ generateTOC })
</script>

<style scoped>
.table-of-contents {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
  position: sticky;
  top: 80px;
  max-height: calc(100vh - 100px);
  overflow-y: auto;
}

.toc-header {
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e9ecef;
}

.toc-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.toc-nav {
  font-size: 14px;
}

.toc-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.toc-item {
  margin: 4px 0;
}

.toc-level-1 {
  padding-left: 0;
}

.toc-level-2 {
  padding-left: 16px;
}

.toc-level-3 {
  padding-left: 32px;
}

.toc-level-4 {
  padding-left: 48px;
}

.toc-level-5 {
  padding-left: 64px;
}

.toc-level-6 {
  padding-left: 80px;
}

.toc-link {
  display: block;
  padding: 4px 8px;
  color: #666;
  text-decoration: none;
  border-radius: 4px;
  transition: all 0.2s ease;
  line-height: 1.4;
}

.toc-link:hover {
  background: #e9ecef;
  color: #333;
}

.toc-item.active .toc-link {
  background: #667eea;
  color: white;
}

.toc-item.active .toc-link:hover {
  background: #5a6fd8;
}

/* 滚动条样式 */
.table-of-contents::-webkit-scrollbar {
  width: 4px;
}

.table-of-contents::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 2px;
}

.table-of-contents::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 2px;
}

.table-of-contents::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>