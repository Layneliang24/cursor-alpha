<template>
  <div class="news-dashboard">
    <!-- 顶部导航栏 -->
    <div class="dashboard-header">
      <h1 class="dashboard-title">英语新闻</h1>
      <div class="header-actions">
        <el-button type="primary" @click="showCrawlSettings = true">
          <el-icon><Setting /></el-icon>
          爬取设置
        </el-button>
        <el-button type="success" @click="openNewsManagement">
          <el-icon><Management /></el-icon>
          新闻管理
        </el-button>
        <el-button type="warning" @click="crawlNews">
          <el-icon><Refresh /></el-icon>
          开始爬取
        </el-button>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="dashboard-content">
      <!-- 轮播新闻区域 -->
      <div class="carousel-section">
        <h2 class="section-title">最新新闻</h2>
        <el-carousel 
          :interval="5000" 
          height="400px" 
          indicator-position="outside"
          v-if="featuredNews.length > 0"
        >
          <el-carousel-item v-for="news in featuredNews" :key="news.id">
            <div class="carousel-news" @click="viewNewsDetail(news)">
              <div class="carousel-image">
                <img :src="getImageUrl(news.image_url) || '/default-news.jpg'" :alt="news.title">
              </div>
              <div class="carousel-content">
                <h3 class="carousel-title">{{ news.title }}</h3>
                <p class="carousel-summary">{{ news.summary }}</p>
                                 <div class="carousel-meta">
                   <span class="source">{{ news.source }}</span>
                   <span class="date">{{ formatDate(news.published_at || news.publish_date) }}</span>
                   <span class="word-count">{{ news.word_count || 0 }} 词</span>
                 </div>
              </div>
            </div>
          </el-carousel-item>
        </el-carousel>
        <div v-else class="no-news">
          <el-empty description="暂无新闻，请先爬取新闻" />
        </div>
      </div>

      <!-- 新闻分类区域 -->
      <div class="news-categories">
        <div class="category-section">
          <h3 class="category-title">热门新闻</h3>
          <div class="news-grid">
            <div 
              v-for="news in hotNews" 
              :key="news.id" 
              class="news-card"
              @click="viewNewsDetail(news)"
            >
              <div class="news-image">
                <img :src="getImageUrl(news.image_url) || '/default-news.jpg'" :alt="news.title">
              </div>
                             <div class="news-info">
                 <h4 class="news-title">{{ news.title }}</h4>
                 <p class="news-summary">{{ truncateText(news.summary, 80) }}</p>
                 <div class="news-meta">
                   <span class="source">{{ news.source }}</span>
                   <span class="date">{{ formatDate(news.publish_date) }}</span>
                   <span class="word-count">{{ news.word_count || 0 }} 词</span>
                 </div>
               </div>
            </div>
          </div>
        </div>

        <div class="category-section">
          <h3 class="category-title">最新发布</h3>
          <div class="news-list">
            <div 
              v-for="news in latestNews" 
              :key="news.id" 
              class="news-item"
              @click="viewNewsDetail(news)"
            >
              <div class="news-thumbnail">
                <img :src="getImageUrl(news.image_url) || '/default-news.jpg'" :alt="news.title">
              </div>
                             <div class="news-content">
                 <h4 class="news-title">{{ news.title }}</h4>
                 <p class="news-summary">{{ truncateText(news.summary, 60) }}</p>
                 <div class="news-meta">
                   <span class="source">{{ news.source }}</span>
                   <span class="date">{{ formatDate(news.published_at || news.publish_date) }}</span>
                   <span class="word-count">{{ news.word_count || 0 }} 词</span>
                 </div>
               </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 查看更多按钮 -->
      <div class="view-more-section">
        <el-button type="primary" size="large" @click="viewAllNews">
          查看更多新闻
        </el-button>
      </div>
    </div>

    <!-- 爬取设置对话框 -->
    <el-dialog 
      v-model="showCrawlSettings" 
      title="爬取设置" 
      width="1000px"
      :close-on-click-modal="false"
    >
      <el-form :model="crawlSettings" label-width="120px">
        <el-form-item label="爬取条数">
          <el-input-number 
            v-model="crawlSettings.maxArticles" 
            :min="1" 
            :max="5" 
            :step="1"
          />
          <span class="form-tip">最多爬取5条新闻</span>
        </el-form-item>
        
                 <el-form-item label="超时时间">
           <el-input-number 
             v-model="crawlSettings.timeout" 
             :min="10" 
             :max="300" 
             :step="5"
           />
           <span class="form-tip">秒 (最大300秒)</span>
         </el-form-item>
        
                 <el-form-item label="新闻源选择">
           <div class="source-selection-info">
             <p>最多可选择3个新闻源同时爬取</p>
             <p v-if="crawlSettings.sources.length === 0" class="warning-text">请选择新闻源</p>
             <p v-else>当前已选择: {{ crawlSettings.sources.length }}/3</p>
           </div>
           <el-checkbox-group 
             v-model="crawlSettings.sources" 
             class="source-checkbox-group"
           >
            <div class="source-categories">
              <!-- 英语新闻源 -->
              <div class="source-category">
                <h4>英语新闻源</h4>
                <div class="source-options">
                  <el-checkbox label="uk.BBC">BBC News</el-checkbox>
                  <el-checkbox label="uk.TheGuardian">The Guardian</el-checkbox>
                  <el-checkbox label="uk.TheIndependent">The Independent</el-checkbox>
                  <el-checkbox label="uk.DailyMail">Daily Mail</el-checkbox>
                  <el-checkbox label="uk.EveningStandard">Evening Standard</el-checkbox>
                  <el-checkbox label="us.APNews">Associated Press</el-checkbox>
                  <el-checkbox label="us.BusinessInsider">Business Insider</el-checkbox>
                  <el-checkbox label="us.CNBC">CNBC</el-checkbox>
                  <el-checkbox label="us.LATimes">Los Angeles Times</el-checkbox>
                  <el-checkbox label="us.TheNewYorker">The New Yorker</el-checkbox>
                  <el-checkbox label="us.Wired">Wired</el-checkbox>
                  <el-checkbox label="us.TechCrunch">TechCrunch</el-checkbox>
                  <el-checkbox label="ca.CBCNews">CBC News</el-checkbox>
                  <el-checkbox label="ca.TheGlobeAndMail">The Globe and Mail</el-checkbox>
                  <el-checkbox label="au.NineNews">Nine News</el-checkbox>
                </div>
              </div>
              
              <!-- 技术新闻源 -->
              <div class="source-category">
                <h4>技术新闻源</h4>
                <div class="source-options">
                  <el-checkbox label="us.TechCrunch">TechCrunch</el-checkbox>
                  <el-checkbox label="us.Wired">Wired</el-checkbox>
                  <el-checkbox label="de.Heise">Heise Online</el-checkbox>
                  <el-checkbox label="de.Golem">Golem</el-checkbox>
                  <el-checkbox label="de.SpiegelOnline">Spiegel Online</el-checkbox>
                  <el-checkbox label="de.Focus">Focus</el-checkbox>
                  <el-checkbox label="de.DW">Deutsche Welle</el-checkbox>
                  <el-checkbox label="uk.BBC">BBC Technology</el-checkbox>
                  <el-checkbox label="uk.TheGuardian">The Guardian Tech</el-checkbox>
                </div>
              </div>
              
              <!-- 国际新闻源 -->
              <div class="source-category">
                <h4>国际新闻源</h4>
                <div class="source-options">
                  <el-checkbox label="uk.EuronewsEN">Euronews</el-checkbox>
                  <el-checkbox label="fr.EuronewsFR">Euronews French</el-checkbox>
                  <el-checkbox label="de.EuronewsDE">Euronews German</el-checkbox>
                  <el-checkbox label="us.VoiceOfAmerica">Voice of America</el-checkbox>
                  <el-checkbox label="jp.TheJapanNews">The Japan News</el-checkbox>
                  <el-checkbox label="jp.AsahiShimbun">Asahi Shimbun</el-checkbox>
                  <el-checkbox label="jp.YomiuriShimbun">Yomiuri Shimbun</el-checkbox>
                  <el-checkbox label="kr.HankookIlbo">Hankook Ilbo</el-checkbox>
                  <el-checkbox label="ind.TimesOfIndia">Times of India</el-checkbox>
                  <el-checkbox label="es.ElPais">El País</el-checkbox>
                  <el-checkbox label="fr.LeFigaro">Le Figaro</el-checkbox>
                  <el-checkbox label="it.LaRepubblica">La Repubblica</el-checkbox>
                </div>
              </div>
            </div>
          </el-checkbox-group>
        </el-form-item>
        
        <el-form-item label="自动爬取">
          <el-switch v-model="crawlSettings.autoCrawl" />
          <span class="form-tip">启用后每小时自动爬取一次</span>
        </el-form-item>
      </el-form>
      
             <template #footer>
         <el-button @click="showCrawlSettings = false">取消</el-button>
         <el-button type="warning" @click="resetCrawlSettings">重置设置</el-button>
         <el-button type="primary" @click="saveCrawlSettings">保存设置</el-button>
       </template>
    </el-dialog>

    <!-- 新闻管理对话框 -->
    <el-dialog 
      v-model="showNewsManagement" 
      title="新闻管理" 
      width="1000px"
      :close-on-click-modal="false"
    >
      <div class="management-toolbar">
        <el-input 
          v-model="searchKeyword" 
          placeholder="搜索新闻标题或内容"
          style="width: 300px"
          clearable
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-select v-model="filterSource" placeholder="选择新闻源" clearable>
          <el-option label="全部" value="" />
          <el-option label="BBC" value="uk.BBC" />
          <el-option label="The Guardian" value="uk.TheGuardian" />
          <el-option label="TechCrunch" value="us.TechCrunch" />
          <el-option label="Wired" value="us.Wired" />
          <el-option label="AP News" value="us.APNews" />
          <el-option label="Business Insider" value="us.BusinessInsider" />
        </el-select>
        
        <el-button type="danger" @click="batchDelete" :disabled="selectedNews.length === 0">
          批量删除
        </el-button>
      </div>
      
      <el-table 
        :data="filteredNews" 
        @selection-change="handleSelectionChange"
        style="width: 100%"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="title" label="标题" min-width="200" />
        <el-table-column prop="source" label="来源" width="120" />
        <el-table-column prop="word_count" label="词数" width="80">
          <template #default="scope">
            {{ scope.row.word_count || 0 }}
          </template>
        </el-table-column>
        <el-table-column prop="publish_date" label="发布时间" width="150">
          <template #default="scope">
            {{ formatDate(scope.row.publish_date) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="150">
          <template #default="scope">
            <el-button size="small" @click="viewNewsDetail(scope.row)">查看</el-button>
            <el-button 
              size="small" 
              type="danger" 
              @click="deleteNews(scope.row)"
            >删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="totalNews"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Setting, Management, Refresh, Search } from '@element-plus/icons-vue'
import { useNewsStore } from '@/stores/news'

const router = useRouter()
const newsStore = useNewsStore()

// 响应式数据
const showCrawlSettings = ref(false)
const showNewsManagement = ref(false)
const searchKeyword = ref('')
const filterSource = ref('')
const selectedNews = ref([])
const currentPage = ref(1)
const pageSize = ref(20)

// 爬取设置
const crawlSettings = ref({
  maxArticles: 3,
  timeout: 300, // 默认300秒超时
  sources: [],
  autoCrawl: false
})

// 初始化逻辑已移到下面的onMounted中统一处理

// 计算属性
const featuredNews = computed(() => {
  return newsStore.news.slice(0, 5)
})

const hotNews = computed(() => {
  return newsStore.news.slice(0, 6)
})

const latestNews = computed(() => {
  return newsStore.news.slice(0, 10)
})

const filteredNews = computed(() => {
  let filtered = newsStore.news || []

  if (searchKeyword.value) {
    filtered = filtered.filter(news =>
      news.title.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
      news.summary.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }

  if (filterSource.value) {
    filtered = filtered.filter(news => news.source === filterSource.value)
  }

  return filtered
})

const totalNews = computed(() => filteredNews.value.length)

// 方法
const formatDate = (dateString) => {
  if (!dateString) return '暂无日期'
  try {
    const date = new Date(dateString)
    if (isNaN(date.getTime())) {
      return '日期无效'
    }
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    })
  } catch (error) {
    console.error('日期格式化错误:', error, dateString)
    return '日期错误'
  }
}

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

const truncateText = (text, maxLength) => {
  if (!text) return ''
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
}

const crawlNews = async () => {
  try {
    console.log('开始爬取新闻，设置:', crawlSettings.value)
    
    // 检查是否选择了新闻源
    if (crawlSettings.value.sources.length === 0) {
      ElMessage.warning('请先在爬取设置中选择新闻源')
      showCrawlSettings.value = true
      return
    }
    
    ElMessage.info('开始爬取新闻...')
    await newsStore.crawlNews(crawlSettings.value)
    ElMessage.success('新闻爬取完成！')
  } catch (error) {
    console.error('爬取失败:', error)
    ElMessage.error('新闻爬取失败：' + error.message)
  }
}

const saveCrawlSettings = async () => {
  try {
    // 验证是否选择了新闻源
    if (crawlSettings.value.sources.length === 0) {
      ElMessage.warning('请至少选择一个新闻源')
      return
    }
    
    // 验证选择的新闻源数量
    if (crawlSettings.value.sources.length > 3) {
      ElMessage.warning('最多只能选择3个新闻源')
      return
    }
    
    // 保存设置到localStorage
    localStorage.setItem('crawlSettings', JSON.stringify(crawlSettings.value))
    console.log('保存设置到localStorage:', crawlSettings.value)
    ElMessage.success('设置保存成功！')
    showCrawlSettings.value = false
  } catch (error) {
    ElMessage.error('设置保存失败：' + error.message)
  }
}

const resetCrawlSettings = () => {
  try {
    // 清除localStorage中的设置
    localStorage.removeItem('crawlSettings')
    // 重置为默认值
    crawlSettings.value = {
      maxArticles: 3,
      timeout: 300, // 重置为300秒
      sources: [],
      autoCrawl: false
    }
    console.log('重置设置完成:', crawlSettings.value)
    ElMessage.success('设置已重置！')
  } catch (error) {
    ElMessage.error('重置设置失败：' + error.message)
  }
}

const viewNewsDetail = (news) => {
  // 改为页面跳转而不是对话框
  router.push(`/english/news/${news.id}`)
}

const viewAllNews = () => {
  console.log('点击查看更多新闻按钮')
  console.log('当前路由:', router.currentRoute.value.path)
  console.log('目标路由: /english/news')
  router.push('/english/news')
}

const handleSelectionChange = (selection) => {
  selectedNews.value = selection
}



const deleteNews = async (news) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除新闻"${news.title}"吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await newsStore.deleteNews(news.id)
    ElMessage.success('新闻删除成功！')
    
    // 删除后立即刷新新闻列表
    await newsStore.fetchNews()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('新闻删除失败：' + error.message)
    }
  }
}

const openNewsManagement = async () => {
  showNewsManagement.value = true
  // 加载管理界面的新闻列表
  try {
    await newsStore.fetchNews()
  } catch (error) {
    ElMessage.error('加载新闻列表失败：' + error.message)
  }
}

const batchDelete = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedNews.value.length} 条新闻吗？`,
      '批量删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const deletePromises = selectedNews.value.map(news => newsStore.deleteNews(news.id))
    await Promise.all(deletePromises)
    ElMessage.success('批量删除成功！')
    selectedNews.value = []
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败：' + error.message)
    }
  }
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
}

const handleCurrentChange = (page) => {
  currentPage.value = page
}

// 生命周期
onMounted(async () => {
  // 优先从localStorage加载设置，如果没有则使用store的默认值
  const savedSettings = localStorage.getItem('crawlSettings')
  if (savedSettings) {
    try {
      const parsedSettings = JSON.parse(savedSettings)
      crawlSettings.value = { ...crawlSettings.value, ...parsedSettings }
      console.log('从localStorage加载设置:', parsedSettings)
    } catch (error) {
      console.error('解析localStorage设置失败:', error)
      // 如果解析失败，清除localStorage
      localStorage.removeItem('crawlSettings')
    }
  } else {
    // 如果没有保存的设置，从store加载默认值
    const storeSettings = newsStore.crawlSettings
    crawlSettings.value = {
      maxArticles: storeSettings.maxArticles,
      timeout: storeSettings.timeout,
      sources: [...storeSettings.sources],
      autoCrawl: storeSettings.autoCrawl
    }
    console.log('使用store默认设置:', crawlSettings.value)
  }

  // 加载新闻数据
  await newsStore.fetchNews()
})

// 监听搜索和筛选变化
watch([searchKeyword, filterSource], () => {
  currentPage.value = 1
})

// 监听新闻源选择，限制最多3个
watch(() => crawlSettings.value.sources, (newSources, oldSources) => {
  // 只有当新选择的新闻源数量增加且超过3个时才触发限制
  if (newSources.length > 3 && newSources.length > oldSources.length) {
    ElMessage.warning('最多只能选择3个新闻源')
    // 移除最后选择的新闻源
    crawlSettings.value.sources = newSources.slice(0, 3)
  }
}, { deep: true })
</script>

<style scoped>
.news-dashboard {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 15px;
  color: white;
}

.dashboard-title {
  margin: 0;
  font-size: 2rem;
  font-weight: 700;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.dashboard-content {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.carousel-section {
  background: white;
  border-radius: 15px;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.section-title {
  margin: 0 0 20px 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: #2c3e50;
}

.carousel-news {
  position: relative;
  height: 100%;
  border-radius: 10px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.carousel-news:hover {
  transform: scale(1.02);
}

.carousel-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
}

.carousel-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.carousel-content {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.8));
  color: white;
  padding: 30px 20px 20px;
  z-index: 2;
}

.carousel-title {
  margin: 0 0 10px 0;
  font-size: 1.4rem;
  font-weight: 600;
  line-height: 1.3;
}

.carousel-summary {
  margin: 0 0 15px 0;
  font-size: 0.95rem;
  line-height: 1.4;
  opacity: 0.9;
}

.carousel-meta {
  display: flex;
  gap: 15px;
  font-size: 0.85rem;
  opacity: 0.8;
}

.carousel-meta .source {
  background: rgba(255, 255, 255, 0.2);
  padding: 4px 8px;
  border-radius: 4px;
}

.carousel-meta .date {
  background: rgba(255, 255, 255, 0.2);
  padding: 4px 8px;
  border-radius: 4px;
}

.carousel-meta .word-count {
  background: rgba(255, 255, 255, 0.2);
  padding: 4px 8px;
  border-radius: 4px;
}

.news-categories {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
}

.category-section {
  background: white;
  border-radius: 15px;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.category-title {
  margin: 0 0 20px 0;
  font-size: 1.3rem;
  font-weight: 600;
  color: #2c3e50;
}

.news-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.news-card {
  background: #f8f9fa;
  border-radius: 10px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
}

.news-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.news-image {
  height: 160px;
  overflow: hidden;
}

.news-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.news-card:hover .news-image img {
  transform: scale(1.1);
}

.news-info {
  padding: 15px;
}

.news-title {
  margin: 0 0 10px 0;
  font-size: 1rem;
  font-weight: 600;
  line-height: 1.4;
  color: #2c3e50;
}

.news-summary {
  margin: 0 0 15px 0;
  font-size: 0.9rem;
  line-height: 1.4;
  color: #6c757d;
}

.news-meta {
  display: flex;
  gap: 10px;
  font-size: 0.8rem;
  color: #6c757d;
}

.news-meta .source {
  background: #e9ecef;
  padding: 2px 6px;
  border-radius: 3px;
  font-weight: 500;
}

.news-meta .date {
  background: #e9ecef;
  padding: 2px 6px;
  border-radius: 3px;
}

.news-meta .word-count {
  background: #e9ecef;
  padding: 2px 6px;
  border-radius: 3px;
}

.news-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.news-item {
  display: flex;
  gap: 15px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.news-item:hover {
  background: #e9ecef;
  transform: translateX(5px);
}

.news-thumbnail {
  width: 80px;
  height: 60px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
}

.news-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.news-content {
  flex: 1;
  min-width: 0;
}

.news-content .news-title {
  margin: 0 0 8px 0;
  font-size: 1rem;
  font-weight: 600;
  line-height: 1.3;
  color: #2c3e50;
}

.news-content .news-summary {
  margin: 0 0 10px 0;
  font-size: 0.85rem;
  line-height: 1.4;
  color: #6c757d;
}

.view-more-section {
  text-align: center;
  margin-top: 30px;
}

.no-news {
  text-align: center;
  padding: 60px 20px;
}

/* 爬取设置样式 */
.source-selection-info {
  margin-bottom: 15px;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #409eff;
}

.source-selection-info p {
  margin: 5px 0;
  font-size: 0.9rem;
  color: #606266;
}

.source-checkbox-group {
  max-height: 400px;
  overflow-y: auto;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  padding: 15px;
}

.source-categories {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.source-category h4 {
  margin: 0 0 10px 0;
  font-size: 1rem;
  font-weight: 600;
  color: #2c3e50;
  border-bottom: 2px solid #409eff;
  padding-bottom: 5px;
}

.source-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 8px;
}

.source-options .el-checkbox {
  margin-right: 0;
  margin-bottom: 8px;
}

.source-selection-info .warning-text {
  color: #e6a23c;
  font-weight: 500;
}



/* 新闻管理样式 */
.management-toolbar {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  align-items: center;
}

.pagination-wrapper {
  margin-top: 20px;
  text-align: center;
}

.form-tip {
  margin-left: 10px;
  font-size: 0.85rem;
  color: #909399;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .news-categories {
    grid-template-columns: 1fr;
  }
  
  .news-grid {
    grid-template-columns: 1fr;
  }
  
  .dashboard-header {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }
  
  .header-actions {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .carousel-content {
    padding: 20px 15px 15px;
  }
  
  .carousel-title {
    font-size: 1.2rem;
  }
  
  .source-categories {
    grid-template-columns: 1fr;
  }
  
  .management-toolbar {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
