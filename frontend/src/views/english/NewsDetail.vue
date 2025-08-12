<template>
  <div class="page-container" v-loading="loading">
    <el-page-header @back="goBack" content="新闻详情" />
    <h2 class="title">{{ news?.title }}</h2>
    <div class="meta">来源：{{ news?.source }} | 时间：{{ news?.published_at }}</div>
    <el-divider />
    <div class="content" v-html="news?.content"></div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { englishAPI } from '@/api/english'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const news = ref(null)

const fetchDetail = async () => {
  loading.value = true
  try {
    const id = route.params.id
    const resp = await englishAPI.getNews(id)
    news.value = resp?.data || resp
  } finally {
    loading.value = false
  }
}

const goBack = () => router.back()

onMounted(fetchDetail)
</script>

<style scoped>
.page-container { padding: 16px; }
.title { margin: 12px 0 6px; }
.meta { color: #888; font-size: 13px; }
.content { line-height: 1.8; }
</style>


