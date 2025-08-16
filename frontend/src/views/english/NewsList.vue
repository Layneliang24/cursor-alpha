<template>
  <div class="news-container">
    <!-- 顶部导航栏 -->
    <div class="page-header">
      <el-button @click="goBack" type="primary" plain>
        <el-icon><ArrowLeft /></el-icon>
        返回仪表板
      </el-button>
      <h1 class="page-title">英语新闻列表</h1>
    </div>

    <!-- 顶部搜索和筛选区 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-input
          v-model="localQuery.search"
          placeholder="搜索新闻标题..."
          clearable
          :prefix-icon="Search"
          @keyup.enter="handleSearch"
        />
        <el-button type="primary" class="ml8" @click="handleSearch">搜索</el-button>
      </div>

      <div class="toolbar-right">
        <el-select v-model="filterSource" placeholder="来源" clearable @change="handleFilterChange" class="ml8">
          <el-option label="全部来源" value="" />
          <el-option label="BBC" value="BBC" />
          <el-option label="TechCrunch" value="TechCrunch" />
          <el-option label="The Guardian" value="The Guardian" />
          <el-option label="CNN" value="CNN" />
          <el-option label="Reuters" value="Reuters" />
        </el-select>

        <el-select v-model="filterDifficulty" placeholder="难度" clearable @change="handleFilterChange" class="ml8">
          <el-option label="全部难度" value="" />
          <el-option label="初级" value="beginner" />
          <el-option label="中级" value="intermediate" />
          <el-option label="高级" value="advanced" />
        </el-select>
      </div>
    </div>



    <!-- 新闻卡片列表 -->
    <div class="news-grid">
             <el-card
         v-for="(news, index) in englishStore.newsList"
         :key="news.id"
         class="news-card"
         :bordered="false"
         :hoverable="true"
       >
         <template #header>
           <div class="card-header">
             <el-tag
               :type="getDifficultyType(news.difficulty_level)"
               size="small"
               class="difficulty-tag"
             >
               {{ getDifficultyLabel(news.difficulty_level) }}
             </el-tag>
           </div>
         </template>

        <div class="news-content">
          <div class="news-image-container">
            <el-image
              v-if="news.image_url"
              :src="getImageUrl(news.image_url)"
              :alt="news.title"
              class="news-image"
              fit="cover"
              :preview-src-list="[getImageUrl(news.image_url)]"
            />
            <div v-else class="placeholder-image">
              <Document class="icon" /> No Image
            </div>
          </div>

          <div class="news-details">
            <h3 class="news-title" @click="goDetail(news)">{{ news.title }}</h3>
            <div class="news-meta">
              <span class="source">{{ news.source }}</span>
              <span class="date">{{ news.publish_date }}</span>
              <span class="word-count">{{ news.word_count }} 词</span>
            </div>
            <p class="news-preview">{{ news.summary || '点击查看详情...' }}</p>
          </div>
        </div>

                 <template #footer>
           <div class="card-footer">
             <el-button
               type="primary"
               size="small"
               @click="goDetail(news)"
             >
               阅读全文
             </el-button>
           </div>
         </template>
      </el-card>
    </div>

    <!-- 加载更多 -->
    <div class="load-more">
      <el-button
        v-if="englishStore.newsList.length < englishStore.newsPagination.total"
        type="default"
        @click="loadMore"
        :loading="loadingMore"
      >
        加载更多
      </el-button>
      <p v-else class="no-more">没有更多新闻了</p>
    </div>
  </div>
</template>

<script setup>
import { reactive, onMounted, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useEnglishStore } from '@/stores/english'
import { englishAPI } from '@/api/english'
import { ElMessage, ElNotification, ElMessageBox } from 'element-plus'
import { Search, ArrowLeft, Document } from '@element-plus/icons-vue'

const router = useRouter()
const englishStore = useEnglishStore()

const localQuery = reactive({ search: '' })
const crawlLoading = ref(false)
const deleteLoading = ref(false)
const loadingMore = ref(false)
const maxArticles = ref(10)
const crawlStatus = reactive({ visible: false, type: 'info', title: '', desc: '' })
const filterSource = ref('')
const filterDifficulty = ref('')
const selectedNews = ref([])

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

const loadMore = async () => {
  if (loadingMore.value) return

  loadingMore.value = true
  try {
    englishStore.newsPagination.page += 1
    await englishStore.fetchNews({
      search: localQuery.search,
      append: true
    })
  } catch (error) {
    console.error('加载更多失败:', error)
    ElMessage.error('加载更多失败')
    englishStore.newsPagination.page -= 1
  } finally {
    loadingMore.value = false
  }
}

const goDetail = (row) => {
  router.push(`/english/news/${row.id}`)
}

const goBack = () => {
  router.push('/english/news-dashboard')
}

onMounted(fetchList)

const getImageUrl = (imageUrl) => {
  if (!imageUrl) return ''
  
  // 如果是本地保存的图片路径（以news_images/开头）
  if (imageUrl.startsWith('news_images/')) {
    // 使用代理配置，通过/api前缀访问后端
    return `/api/media/${imageUrl}`
  }
  
  // 如果是完整的URL，直接返回
  if (imageUrl.startsWith('http')) {
    return imageUrl
  }
  
  // 其他情况，尝试作为相对路径处理
  return imageUrl
}

const handleCrawlCommand = async (source) => {
  crawlLoading.value = true
  try {
    const sourceNames = {
      bbc: 'BBC', 
      cnn: 'CNN', 
      reuters: 'Reuters', 
      techcrunch: 'TechCrunch',
      the_guardian: 'The Guardian',
      all: '所有源' 
    }
    const sourceName = sourceNames[source] || source

    // 默认使用fundus爬虫
    const crawlerType = 'fundus'

    ElNotification({
      title: '开始抓取',
      message: `正在后台抓取 ${sourceName} 新闻，请稍候...`,
      type: 'info',
      duration: 3000
    })

    const response = await englishAPI.triggerNewsCrawl(source, crawlerType, maxArticles.value)

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
      // 简单轮询刷新列表
      setTimeout(() => { fetchList() }, 4000)
      return
    }

    ElMessage.warning(response?.message || '抓取任务提交失败')
  } catch (error) {
    console.error('抓取失败:', error)
    if (error?.code === 'ECONNABORTED') {
      ElNotification({
        title: '提交超时', 
        message: '已超过120秒，抓取可能已在后台运行，请稍后刷新列表查看结果', 
        type: 'warning', 
        duration: 6000 
      })
    } else {
      ElNotification({
        title: '抓取失败', 
        message: '新闻抓取任务提交失败，请重试', 
        type: 'error', 
        duration: 5000 
      })
    }
  } finally {
    crawlLoading.value = false
  }
}

// 处理选择变化
const handleSelectionChange = () => {
  // 由checkbox组件自动处理
}

// 处理筛选变化
const handleFilterChange = async () => {
  const params = {}
  if (filterSource.value) params.source = filterSource.value
  if (filterDifficulty.value) params.difficulty = filterDifficulty.value
  
  try {
    const response = await englishAPI.filterNewsByCategory(params)
    if (response?.success) {
      englishStore.newsList = response.data
    }
  } catch (error) {
    console.error('筛选失败:', error)
    ElMessage.error('筛选失败')
  }
}

// 删除单条新闻
const handleDeleteNews = async (news) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除新闻"${news.title}"吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    const response = await englishAPI.deleteNews(news.id)
    if (response?.success) {
      ElMessage.success('删除成功')
      await fetchList()
    } else {
      ElMessage.error(response?.message || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除新闻失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 批量删除新闻
const handleBatchDelete = async () => {
  if (selectedNews.value.length === 0) {
    ElMessage.warning('请选择要删除的新闻')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedNews.value.length} 条新闻吗？此操作不可恢复。`,
      '确认批量删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    const newsIds = selectedNews.value.map(news => news.id)
    const response = await englishAPI.batchDeleteNews(newsIds)
    if (response?.success) {
      ElMessage.success(response.message)
      selectedNews.value = []
      await fetchList()
    } else {
      ElMessage.error(response?.message || '批量删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量删除失败:', error)
      ElMessage.error('批量删除失败')
    }
  }
}

// 获取难度标签类型
const getDifficultyType = (difficulty) => {
  const types = {
    'beginner': 'success',
    'intermediate': 'warning',
    'advanced': 'danger'
  }
  return types[difficulty] || 'info'
}

// 获取难度标签文本
const getDifficultyLabel = (difficulty) => {
  const labels = {
    'beginner': '初级',
    'intermediate': '中级',
    'advanced': '高级'
  }
  return labels[difficulty] || difficulty
}
</script>

<style scoped>
.page-container { padding: 16px; }

.page-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.page-title {
  margin: 0;
  font-size: 1.8rem;
  font-weight: 600;
  color: #2c3e50;
}
.toolbar { 
  margin-bottom: 12px; 
  display: flex; 
  align-items: center; 
  justify-content: space-between; 
}
.toolbar-left { display: flex; align-items: center; }
.toolbar-right { display: flex; align-items: center; }
.ml8 { margin-left: 8px; }
.mb12 { margin-bottom: 12px; }
.pager { margin-top: 12px; display: flex; justify-content: flex-end; }
.news-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px; }
.news-card { height: 100%; display: flex; flex-direction: column; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.difficulty-tag { margin-left: auto; }
.news-content { display: flex; margin-bottom: 12px; flex-grow: 1; }
.news-image-container { width: 120px; flex-shrink: 0; margin-right: 12px; }
.news-image { width: 100%; height: 100px; object-fit: cover; }
.placeholder-image { width: 120px; height: 100px; background-color: #f5f5f5; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #999; }
.icon { font-size: 24px; margin-bottom: 4px; }
.news-details { flex-grow: 1; display: flex; flex-direction: column; }
.news-title { font-size: 16px; font-weight: bold; margin-bottom: 8px; cursor: pointer; }
.news-meta { display: flex; justify-content: space-between; font-size: 12px; color: #666; margin-bottom: 8px; }
.news-preview { font-size: 14px; color: #333; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; flex-grow: 1; }
.card-footer { display: flex; justify-content: space-between; margin-top: 12px; }
.status-alert { margin-bottom: 12px; }
.load-more { margin-top: 20px; text-align: center; }
.no-more { color: #999; }
</style>


