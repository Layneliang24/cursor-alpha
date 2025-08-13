<template>
  <div class="page-container">
    <div class="toolbar">
      <el-input v-model="localQuery.search" placeholder="搜索新闻标题" clearable style="max-width: 280px" @keyup.enter="handleSearch" />
      <el-button type="primary" class="ml8" @click="handleSearch">查询</el-button>
      <el-dropdown @command="handleCrawlCommand" class="ml8">
        <el-button type="success" :loading="crawlLoading">
          抓取新闻 <el-icon><ArrowDown /></el-icon>
        </el-button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="local_test">抓取 China Daily 新闻</el-dropdown-item>
            <el-dropdown-item command="xinhua">抓取新华社英语新闻</el-dropdown-item>
            <el-dropdown-item command="techcrunch">抓取 TechCrunch 新闻</el-dropdown-item>
            <el-dropdown-item command="bbc">抓取 BBC 新闻</el-dropdown-item>
            <el-dropdown-item command="cnn">抓取 CNN 新闻</el-dropdown-item>
            <el-dropdown-item command="reuters">抓取 Reuters 新闻</el-dropdown-item>
            <el-dropdown-item command="all" divided>抓取所有源</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>

    <el-alert
      v-if="crawlStatus.visible"
      :title="crawlStatus.title"
      :type="crawlStatus.type"
      :description="crawlStatus.desc"
      show-icon
      class="mb12"
      :closable="true"
      @close="crawlStatus.visible = false"
    />

    <el-table :data="englishStore.newsList" v-loading="englishStore.newsLoading" stripe>
      <el-table-column label="图片" width="80">
        <template #default="{ row }">
          <el-image 
            v-if="row.image_url" 
            :src="row.image_url" 
            :alt="row.image_alt"
            style="width: 60px; height: 40px; object-fit: cover; border-radius: 4px;"
            fit="cover"
            :preview-src-list="[row.image_url]"
          />
          <div v-else style="width: 60px; height: 40px; background: #f5f5f5; border-radius: 4px; display: flex; align-items: center; justify-content: center; color: #999; font-size: 12px;">
            无图
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="title" label="标题" min-width="280" show-overflow-tooltip />
      <el-table-column prop="source" label="来源" width="100" />
      <el-table-column prop="publish_date" label="发布时间" width="120" />
      <el-table-column prop="word_count" label="词数" width="80" />
      <el-table-column label="操作" width="100">
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
import { ElMessage, ElNotification } from 'element-plus'
import { ArrowDown } from '@element-plus/icons-vue'

const router = useRouter()
const englishStore = useEnglishStore()

const localQuery = reactive({ search: '' })
const crawlLoading = ref(false)
const crawlStatus = reactive({ visible: false, type: 'info', title: '', desc: '' })

const showCrawlStatus = (type, title, desc) => {
  crawlStatus.type = type
  crawlStatus.title = title
  crawlStatus.desc = desc
  crawlStatus.visible = true
}

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

const handleCrawlCommand = async (source) => {
  crawlLoading.value = true
  try {
    const sourceNames = { local_test: 'China Daily', xinhua: '新华社英语', bbc: 'BBC', cnn: 'CNN', reuters: 'Reuters', techcrunch: 'TechCrunch', all: '所有源' }
    const sourceName = sourceNames[source] || source

    ElNotification({
      title: '开始抓取',
      message: `正在后台抓取 ${sourceName} 新闻，请稍候...`,
      type: 'info',
      duration: 3000
    })

    const response = await englishAPI.triggerNewsCrawl(source)

    // 支持两种模式：sync(200返回详细统计) 和 async(202仅接受)
    if (response?.success && response?.data?.mode === 'sync') {
      const stats = response.data
      const msg = `来源: ${stats.source} | 共找到: ${stats.total_found} | 新增: ${stats.saved_count} | 跳过: ${stats.skipped_count} | 用时: ${stats.duration_seconds}s`
      showCrawlStatus('success', '抓取完成', msg)
      await fetchList()
      return
    }

    if (response?.success) {
      const taskId = response?.data?.task_id
      const msg = `已提交 ${sourceName} 抓取任务${taskId ? ` (任务ID: ${taskId})` : ''}`
      showCrawlStatus('info', '任务已提交', msg)
      // 简单轮询刷新列表（给后台一些时间）
      setTimeout(() => { fetchList() }, 4000)
      return
    }

    ElMessage.warning(response?.message || '抓取任务提交失败')
  } catch (error) {
    console.error('抓取失败:', error)
    ElNotification({ title: '抓取失败', message: '新闻抓取任务提交失败，请重试', type: 'error', duration: 5000 })
  } finally {
    crawlLoading.value = false
  }
}
</script>

<style scoped>
.page-container { padding: 16px; }
.toolbar { margin-bottom: 12px; display: flex; align-items: center; }
.ml8 { margin-left: 8px; }
.mb12 { margin-bottom: 12px; }
.pager { margin-top: 12px; display: flex; justify-content: flex-end; }
</style>


