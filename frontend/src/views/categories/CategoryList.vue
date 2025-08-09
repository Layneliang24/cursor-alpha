<template>
  <div class="category-list-container">
    <div class="page-header">
      <h1>全部分类</h1>
      <div class="meta" v-if="!loading && styledCategories.length">
        共 {{ styledCategories.length }} 个分类
      </div>
    </div>

    <div class="category-grid" v-loading="loading">
      <div class="grid">
        <div
          v-for="cat in styledCategories"
          :key="cat.id"
          class="category-card"
          :class="cat.sizeClass"
          :style="{ borderColor: cat.color || '#409eff' }"
          @click="goDetail(cat.id)"
        >
          <div class="left-accent" :style="{ backgroundColor: cat.color || '#409eff' }" />
          <div class="icon" :style="{ color: cat.color || '#409eff' }">{{ cat.iconText }}</div>
          <div class="content">
            <div class="header">
              <h3 class="name">{{ cat.name }}</h3>
              <el-tag size="small" effect="plain" :type="'info'">{{ cat.article_count || 0 }} 篇</el-tag>
            </div>
            <p class="desc" v-if="cat.description">{{ cat.description }}</p>
          </div>
        </div>

        <div class="empty" v-if="!loading && styledCategories.length === 0">
          <el-empty description="暂无分类" />
        </div>
      </div>
    </div>
  </div>
  </template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { categoriesAPI } from '@/api/categories'
import { ElMessage } from 'element-plus'

const router = useRouter()
const loading = ref(false)
const categories = ref([])

const fetchCategories = async () => {
  loading.value = true
  try {
    const res = await categoriesAPI.getCategories()
    categories.value = res.results || res || []
  } catch (e) {
    console.error('获取分类失败:', e)
    ElMessage.error('获取分类失败')
  } finally {
    loading.value = false
  }
}

// 图标映射：优先使用后端提供的 icon，其次按名称猜测，最后给默认
const getIconByName = (name) => {
  if (!name) return '📁'
  const key = String(name).toLowerCase()
  const map = {
    vue: '🟩', react: '⚛️', angular: '🅰️', svelte: '🧡',
    javascript: '🟨', typescript: '🔷', node: '📦', deno: '🦕',
    python: '🐍', django: '🌿', flask: '🍶', fastapi: '⚡',
    java: '☕', spring: '🌱', kotlin: '🟪', scala: '🟥',
    go: '🐹', golang: '🐹', rust: '🦀', php: '🐘', '.net': '🟣', dotnet: '🟣',
    mysql: '🐬', postgres: '🐘', postgresql: '🐘', redis: '🔴', mongodb: '🍃', database: '🗄️',
    docker: '🐳', kubernetes: '☸️', devops: '🔧', linux: '🐧',
    cloud: '☁️', aws: '☁️', azure: '☁️', gcp: '☁️',
    ai: '🤖', ml: '🧠', machine: '🧠', data: '📊',
    security: '🛡️', testing: '🧪', mobile: '📱', frontend: '🎨', backend: '🧱'
  }
  // 长名称匹配
  for (const k of Object.keys(map)) {
    if (key.includes(k)) return map[k]
  }
  return '📁'
}

// 根据文章数量计算视觉大小
const styledCategories = computed(() => {
  const list = categories.value || []
  if (list.length === 0) return []
  const counts = list.map(c => c.article_count || 0)
  const max = Math.max(...counts)
  const min = Math.min(...counts)

  const getSizeClass = (count) => {
    if (max === min) return 'size-medium'
    const ratio = (count - min) / Math.max(1, (max - min))
    if (ratio > 0.66) return 'size-large'
    if (ratio > 0.33) return 'size-medium'
    return 'size-small'
  }

  return list.map(cat => ({
    ...cat,
    iconText: cat.icon?.trim() || getIconByName(cat.name),
    sizeClass: getSizeClass(cat.article_count || 0)
  }))
})

const goDetail = (id) => {
  router.push({ name: 'CategoryDetail', params: { id } })
}

onMounted(fetchCategories)
</script>

<style scoped>
.category-list-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.page-header .meta {
  color: #909399;
  font-size: 13px;
}

.category-grid { margin-top: 10px; }
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
}

.category-card {
  position: relative;
  cursor: pointer;
  border: 1px solid #e4e7ed;
  border-left: 8px solid var(--accent, #409eff);
  border-radius: 12px;
  background: #fff;
  padding: 16px 16px 14px 16px;
  display: grid;
  grid-template-columns: 48px 1fr;
  gap: 14px;
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}

.category-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.08);
}

.left-accent {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 6px;
  border-top-left-radius: 12px;
  border-bottom-left-radius: 12px;
}

.icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: #f5f7fa;
  font-size: 26px;
}

.content .header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.name {
  margin: 0;
  font-size: 16px;
  font-weight: 650;
  color: #333;
}

.desc {
  margin: 6px 0 0;
  color: #666;
  font-size: 13px;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 视觉大小等级 */
.size-small { padding: 14px; }
.size-small .icon { width: 44px; height: 44px; font-size: 22px; }
.size-small .name { font-size: 15px; }

.size-medium { padding: 16px; }
.size-medium .icon { width: 48px; height: 48px; font-size: 26px; }
.size-medium .name { font-size: 16px; }

.size-large { padding: 18px; }
.size-large .icon { width: 56px; height: 56px; font-size: 30px; }
.size-large .name { font-size: 18px; }
</style>

