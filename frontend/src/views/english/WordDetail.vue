<template>
  <div class="page-container" v-loading="loading">
    <el-page-header @back="goBack" content="单词详情" />

    <el-descriptions :column="2" border class="mt12">
      <el-descriptions-item label="单词">{{ word?.text }}</el-descriptions-item>
      <el-descriptions-item label="音标">{{ word?.phonetic }}</el-descriptions-item>
      <el-descriptions-item label="词性">{{ word?.pos }}</el-descriptions-item>
      <el-descriptions-item label="难度">{{ word?.difficulty }}</el-descriptions-item>
      <el-descriptions-item label="释义" :span="2">{{ word?.definition }}</el-descriptions-item>
      <el-descriptions-item label="例句" :span="2">{{ word?.examples?.[0]?.text }}</el-descriptions-item>
      <el-descriptions-item label="来源">{{ word?.source }}</el-descriptions-item>
      <el-descriptions-item label="更新时间">{{ word?.updated_at }}</el-descriptions-item>
    </el-descriptions>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { englishAPI } from '@/api/english'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const word = ref(null)

const fetchDetail = async () => {
  loading.value = true
  try {
    const id = route.params.id
    const resp = await englishAPI.getWord(id)
    word.value = resp?.data || resp
  } finally {
    loading.value = false
  }
}

const goBack = () => router.back()

onMounted(fetchDetail)
</script>

<style scoped>
.page-container { padding: 16px; }
.mt12 { margin-top: 12px; }
</style>


