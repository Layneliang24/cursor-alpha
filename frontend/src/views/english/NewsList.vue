<template>
  <div class="page-container">
    <div class="toolbar">
      <el-input v-model="localQuery.search" placeholder="搜索新闻标题" clearable style="max-width: 280px" @keyup.enter="handleSearch" />
      <el-button type="primary" class="ml8" @click="handleSearch">查询</el-button>
      <el-button class="ml8" type="success" :loading="crawlLoading" @click="triggerCrawl">抓取新闻</el-button>
    </div>

    <el-table :data="englishStore.newsList" v-loading="englishStore.newsLoading" stripe>
      <el-table-column prop="title" label="标题" min-width="320" show-overflow-tooltip />
      <el-table-column prop="source" label="来源" width="120" />
      <el-table-column prop="published_at" label="发布时间" width="180" />
      <el-table-column label="操作" width="120">
        <template #default="{ row }">
          <el-button size="small" @click="goDetail(row)">阅读</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pager">
      <el-pagination
        background
        layout="total, prev, pager, next, jumper"
        :total="englishStore.newsPagination.total"
        :page-size="englishStore.newsPagination.pageSize"
        :current-page="englishStore.newsPagination.page"
        @current-change="handlePageChange"
      />
    </div>
  </div>
</template>

<script setup>
import { reactive, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useEnglishStore } from '@/stores/english'
import { englishAPI } from '@/api/english'
import { ElMessage } from 'element-plus'

const router = useRouter()
const englishStore = useEnglishStore()

const localQuery = reactive({ search: '' })
const crawlLoading = ref(false)

const fetchList = async () => {
  await englishStore.fetchNews({ search: localQuery.search })
}

const handleSearch = () => {
  englishStore.newsPagination.page = 1
  fetchList()
}

const handlePageChange = (page) => {
  englishStore.newsPagination.page = page
  fetchList()
}

const goDetail = (row) => {
  router.push(`/english/news/${row.id}`)
}

onMounted(fetchList)

const triggerCrawl = async () => {
  crawlLoading.value = true
  try {
    await englishAPI.triggerNewsCrawl('bbc')
    ElMessage.success('已提交后台抓取任务')
  } catch (e) {
    console.error(e)
  } finally {
    crawlLoading.value = false
  }
}
</script>

<style scoped>
.page-container { padding: 16px; }
.toolbar { margin-bottom: 12px; display: flex; align-items: center; }
.ml8 { margin-left: 8px; }
.pager { margin-top: 12px; display: flex; justify-content: flex-end; }
</style>


