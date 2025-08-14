<template>
  <div class="page-container">
    <div class="toolbar">
      <div class="toolbar-left">
        <el-input v-model="localQuery.search" placeholder="搜索新闻标题" clearable style="max-width: 280px" @keyup.enter="handleSearch" />
        <el-button type="primary" class="ml8" @click="handleSearch">查询</el-button>
        
        <!-- 分类筛选 -->
        <el-select v-model="filterSource" placeholder="按来源筛选" clearable @change="handleFilterChange" class="ml8" style="width: 150px;">
          <el-option label="全部来源" value="" />
          <el-option label="BBC" value="BBC" />
          <el-option label="TechCrunch" value="TechCrunch" />
          <el-option label="The Guardian" value="The Guardian" />
          <el-option label="CNN" value="CNN" />
          <el-option label="Reuters" value="Reuters" />
        </el-select>
        
        <el-select v-model="filterDifficulty" placeholder="按难度筛选" clearable @change="handleFilterChange" class="ml8" style="width: 150px;">
          <el-option label="全部难度" value="" />
          <el-option label="初级" value="beginner" />
          <el-option label="中级" value="intermediate" />
          <el-option label="高级" value="advanced" />
        </el-select>
      </div>
      
      <div class="toolbar-right">
        <!-- 批量操作 -->
        <el-button 
          type="danger" 
          :disabled="selectedNews.length === 0" 
          @click="handleBatchDelete"
          class="ml8"
        >
          批量删除 ({{ selectedNews.length }})
        </el-button>
        
        <!-- 抓取新闻 -->
         <el-dropdown @command="handleCrawlCommand" class="ml8">
          <el-button type="success" :loading="crawlLoading">
            抓取新闻 <el-icon><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="bbc">抓取 BBC 新闻 (Fundus)</el-dropdown-item>
              <el-dropdown-item command="cnn">抓取 CNN 新闻 (Fundus)</el-dropdown-item>
              <el-dropdown-item command="reuters">抓取 Reuters 新闻 (Fundus)</el-dropdown-item>
              <el-dropdown-item command="techcrunch">抓取 TechCrunch 新闻 (Fundus)</el-dropdown-item>
              <el-dropdown-item command="the_guardian">抓取 The Guardian 新闻 (Fundus)</el-dropdown-item>
              <el-dropdown-item command="the_new_york_times">抓取 The New York Times 新闻 (Fundus)</el-dropdown-item>
              <el-dropdown-item command="wired">抓取 Wired 新闻 (Fundus)</el-dropdown-item>
              <el-dropdown-item command="ars_technica">抓取 Ars Technica 新闻 (Fundus)</el-dropdown-item>
              <el-dropdown-item command="hacker_news">抓取 Hacker News (Fundus)</el-dropdown-item>
              <el-dropdown-item command="stack_overflow">抓取 Stack Overflow 热帖 (Fundus)</el-dropdown-item>
              <el-dropdown-item command="all" divided>抓取所有源 (Fundus)</el-dropdown-item>
              <el-dropdown-item command="more_sources" divided>更多来源...</el-dropdown-item>
              <el-dropdown-item disabled>
                <div style="width: 260px; padding: 6px 6px 0;">
                  <div style="display:flex; align-items:center; gap:8px;">
                    <span style="white-space:nowrap; color:#666;">每次抓取数量</span>
                    <el-input-number v-model="maxArticles" :min="1" :max="50" size="small" />
                  </div>
                </div>
              </el-dropdown-item>
              <el-dropdown-item command="local_test" divided>抓取 China Daily 新闻 (传统)</el-dropdown-item>
              <el-dropdown-item command="xinhua">抓取新华社英语新闻 (传统)</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        
        <!-- 更多来源对话框 -->
        <el-dialog v-model="moreSourcesVisible" title="选择更多新闻源" width="600px">
          <div class="more-sources-content">
            <el-input
              v-model="publisherSearch"
              placeholder="搜索新闻源..."
              clearable
              style="margin-bottom: 16px;"
            />
            <div class="publishers-list" style="max-height: 400px; overflow-y: auto;">
              <el-radio-group v-model="selectedPublisher" @change="handlePublisherSelect">
                <div
                  v-for="item in filteredPublishers"
                  :key="item.id"
                  class="publisher-item"
                  style="padding: 8px 12px; border-bottom: 1px solid #f0f0f0; cursor: pointer;"
                  @click="selectedPublisher = item.id"
                >
                  <el-radio :label="item.id">
                    <span style="font-weight: 500;">{{ item.name }}</span>
                    <span style="color: #666; margin-left: 8px;">({{ item.country.toUpperCase() }})</span>
                  </el-radio>
                </div>
              </el-radio-group>
            </div>
          </div>
          <template #footer>
            <span class="dialog-footer">
              <el-button @click="moreSourcesVisible = false">取消</el-button>
              <el-button type="primary" @click="handleMoreSourcesConfirm" :disabled="!selectedPublisher">
                确认抓取
              </el-button>
            </span>
          </template>
        </el-dialog>
      </div>
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

    <el-table 
      :data="englishStore.newsList" 
      v-loading="englishStore.newsLoading" 
      stripe
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="55" />
      <el-table-column label="图片" width="80">
        <template #default="{ row }">
          <el-image 
            v-if="row.image_url" 
            :src="getImageUrl(row.image_url)" 
            :alt="row.image_alt"
            style="width: 60px; height: 40px; object-fit: cover; border-radius: 4px;"
            fit="cover"
            :preview-src-list="[getImageUrl(row.image_url)]"
            :preview-teleported="true"
          />
          <div v-else style="width: 60px; height: 40px; background: #f5f5f5; border-radius: 4px; display: flex; align-items: center; justify-content: center; color: #999; font-size: 12px;">
            无图
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="title" label="标题" min-width="280" show-overflow-tooltip />
      <el-table-column prop="source" label="来源" width="100" />
      <el-table-column prop="difficulty_level" label="难度" width="80">
        <template #default="{ row }">
          <el-tag :type="getDifficultyType(row.difficulty_level)" size="small">
            {{ getDifficultyLabel(row.difficulty_level) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="publish_date" label="发布时间" width="120" />
      <el-table-column prop="word_count" label="词数" width="80" />
      <el-table-column label="操作" width="150">
        <template #default="{ row }">
          <el-button size="small" @click="goDetail(row)">阅读</el-button>
          <el-button size="small" type="danger" @click="handleDeleteNews(row)">删除</el-button>
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
import { reactive, onMounted, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useEnglishStore } from '@/stores/english'
import { englishAPI } from '@/api/english'
import { ElMessage, ElNotification, ElMessageBox } from 'element-plus'
import { ArrowDown } from '@element-plus/icons-vue'

const router = useRouter()
const englishStore = useEnglishStore()

const localQuery = reactive({ search: '' })
const crawlLoading = ref(false)
const maxArticles = ref(10)
const crawlStatus = reactive({ visible: false, type: 'info', title: '', desc: '' })
const fundusPublishers = ref([])
const customPublisher = ref('')
const filterSource = ref('')
const filterDifficulty = ref('')
const selectedNews = ref([])
const moreSourcesVisible = ref(false)
const publisherSearch = ref('')
const selectedPublisher = ref('')

const showCrawlStatus = (type, title, desc) => {
  crawlStatus.type = type
  crawlStatus.title = title
  crawlStatus.desc = desc
  crawlStatus.visible = true
}
// 加载Fundus发布者列表
const loadFundusPublishers = async () => {
  try {
    const res = await englishAPI.getFundusPublishers()
    if (res?.success) {
      fundusPublishers.value = res.data || []
    }
  } catch (e) {
    console.warn('加载Fundus发布者失败', e)
  }
}

onMounted(() => {
  loadFundusPublishers()
})

// 计算过滤后的发布者列表
const filteredPublishers = computed(() => {
  if (!publisherSearch.value) {
    return fundusPublishers.value
  }
  return fundusPublishers.value.filter(item => 
    item.name.toLowerCase().includes(publisherSearch.value.toLowerCase()) ||
    item.country.toLowerCase().includes(publisherSearch.value.toLowerCase())
  )
})

// 处理更多来源选择
const handlePublisherSelect = (value) => {
  selectedPublisher.value = value
}

// 处理更多来源确认
const handleMoreSourcesConfirm = async () => {
  if (!selectedPublisher.value) return
  
  moreSourcesVisible.value = false
  await handleCrawlCommand(selectedPublisher.value)
  selectedPublisher.value = ''
  publisherSearch.value = ''
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
  // 处理更多来源对话框
  if (source === 'more_sources') {
    moreSourcesVisible.value = true
    return
  }
  
  crawlLoading.value = true
  try {
    const sourceNames = { 
      local_test: 'China Daily', 
      xinhua: '新华社英语', 
      bbc: 'BBC', 
      cnn: 'CNN', 
      reuters: 'Reuters', 
      techcrunch: 'TechCrunch',
      the_guardian: 'The Guardian',
      the_new_york_times: 'The New York Times',
      wired: 'Wired',
      ars_technica: 'Ars Technica',
      hacker_news: 'Hacker News',
      stack_overflow: 'Stack Overflow',
      all: '所有源' 
    }
    const sourceName = sourceNames[source] || source
    
    // 根据源选择爬虫类型
    const crawlerType = ['local_test', 'xinhua'].includes(source) ? 'traditional' : 'fundus'

    ElNotification({
      title: '开始抓取',
      message: `正在后台抓取 ${sourceName} 新闻 (${crawlerType === 'fundus' ? 'Fundus爬虫' : '传统爬虫'})，请稍候...`,
      type: 'info',
      duration: 3000
    })

    const response = await englishAPI.triggerNewsCrawl(source, crawlerType, maxArticles.value)

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
    // 超时单独提示：很可能后端已在后台执行
    if (error?.code === 'ECONNABORTED') {
      ElNotification({ title: '提交超时', message: '已超过120秒，抓取可能已在后台运行，请稍后刷新列表查看结果', type: 'warning', duration: 6000 })
    } else {
      ElNotification({ title: '抓取失败', message: '新闻抓取任务提交失败，请重试', type: 'error', duration: 5000 })
    }
  } finally {
    crawlLoading.value = false
  }
}

// 处理选择变化
const handleSelectionChange = (selection) => {
  selectedNews.value = selection
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
</style>


