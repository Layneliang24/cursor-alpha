<template>
  <div class="category-detail-container">
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="5" animated />
    </div>
    
    <div v-else-if="category" class="category-content">
      <div class="category-header">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
          <el-breadcrumb-item :to="{ path: '/articles' }">文章</el-breadcrumb-item>
          <el-breadcrumb-item>{{ category.name }}</el-breadcrumb-item>
        </el-breadcrumb>
        
        <div class="category-info">
          <h1 class="category-name">{{ category.name }}</h1>
          <p class="category-description" v-if="category.description">
            {{ category.description }}
          </p>
          <div class="category-stats">
            <span class="stat-item">
              <el-icon><Document /></el-icon>
              {{ category.article_count || 0 }} 篇文章
            </span>
          </div>
        </div>
      </div>
      
      <!-- 文章列表 -->
      <div class="articles-section">
        <div class="section-header">
          <h2>分类文章</h2>
          <div class="sort-controls">
            <el-select
              v-model="sortBy"
              @change="handleSortChange"
              style="width: 150px"
            >
              <el-option label="最新发布" value="-created_at" />
              <el-option label="最多浏览" value="-views" />
              <el-option label="最多点赞" value="-likes" />
            </el-select>
          </div>
        </div>
        
        <div class="articles-grid">
          <el-row :gutter="20" v-loading="articlesLoading">
            <el-col 
              :span="8" 
              v-for="article in articles" 
              :key="article.id"
              class="article-col"
            >
              <el-card 
                class="article-card" 
                :body-style="{ padding: '20px' }"
                @click="viewArticle(article.id)"
              >
                <div class="article-cover" v-if="article.cover_image">
                  <img :src="article.cover_image" :alt="article.title" />
                </div>
                
                <div class="article-header">
                  <h3 class="article-title">{{ article.title }}</h3>
                  <el-tag v-if="article.featured" type="danger" size="small">推荐</el-tag>
                </div>
                
                <p class="article-summary">{{ article.summary || '暂无摘要' }}</p>
                
                <div class="article-meta">
                  <div class="meta-left">
                    <el-avatar :size="24" :src="article.author?.avatar">
                      {{ article.author?.username?.charAt(0)?.toUpperCase() }}
                    </el-avatar>
                    <span class="author-name">{{ article.author?.username }}</span>
                  </div>
                  <div class="meta-right">
                    <span class="meta-item">
                      <el-icon><View /></el-icon>
                      {{ article.views }}
                    </span>
                    <span class="meta-item">
                      <el-icon><Star /></el-icon>
                      {{ article.likes }}
                    </span>
                  </div>
                </div>
                
                <div class="article-footer">
                  <span class="publish-time">
                    {{ formatDate(article.created_at) }}
                  </span>
                </div>
              </el-card>
            </el-col>
            
            <!-- 空状态 -->
            <el-col :span="24" v-if="!articlesLoading && articles.length === 0">
              <el-empty description="该分类下暂无文章">
                <el-button type="primary" @click="$router.push('/articles/create')">
                  发布第一篇文章
                </el-button>
              </el-empty>
            </el-col>
          </el-row>
        </div>
        
        <!-- 分页 -->
        <div class="pagination-container" v-if="pagination.total > 0">
          <el-pagination
            v-model:current-page="pagination.current"
            v-model:page-size="pagination.pageSize"
            :total="pagination.total"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </div>
    </div>
    
    <div v-else class="error-container">
      <el-empty description="分类不存在">
        <el-button type="primary" @click="$router.push('/articles')">
          返回文章列表
        </el-button>
      </el-empty>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { categoriesAPI } from '@/api/categories'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const articlesLoading = ref(false)
const category = ref(null)
const articles = ref([])
const sortBy = ref('-created_at')

const pagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0
})

// 获取分类详情
const fetchCategory = async () => {
  try {
    loading.value = true
    category.value = await categoriesAPI.getCategory(route.params.id)
  } catch (error) {
    console.error('获取分类失败:', error)
    ElMessage.error('分类不存在')
  } finally {
    loading.value = false
  }
}

// 获取分类文章
const fetchCategoryArticles = async () => {
  try {
    articlesLoading.value = true
    const params = {
      page: pagination.current,
      page_size: pagination.pageSize,
      ordering: sortBy.value
    }
    
    const response = await categoriesAPI.getCategoryArticles(route.params.id, params)
    
    articles.value = response.results || response
    pagination.total = response.count || articles.value.length
  } catch (error) {
    console.error('获取文章失败:', error)
    ElMessage.error('获取文章失败')
  } finally {
    articlesLoading.value = false
  }
}

// 排序变化处理
const handleSortChange = () => {
  pagination.current = 1
  fetchCategoryArticles()
}

// 分页大小变化
const handleSizeChange = (size) => {
  pagination.pageSize = size
  pagination.current = 1
  fetchCategoryArticles()
}

// 当前页变化
const handleCurrentChange = (page) => {
  pagination.current = page
  fetchCategoryArticles()
}

// 查看文章详情
const viewArticle = (id) => {
  router.push({ name: 'ArticleDetail', params: { id } })
}

// 格式化日期
const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

onMounted(async () => {
  await fetchCategory()
  if (category.value) {
    await fetchCategoryArticles()
  }
})
</script>

<style scoped>
.category-detail-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.loading-container {
  padding: 20px;
}

.category-header {
  margin-bottom: 40px;
}

.category-info {
  margin: 20px 0;
}

.category-name {
  font-size: 32px;
  font-weight: 700;
  color: #333;
  margin: 20px 0 10px 0;
}

.category-description {
  color: #666;
  font-size: 16px;
  line-height: 1.6;
  margin: 10px 0 20px 0;
}

.category-stats {
  display: flex;
  gap: 20px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #666;
  font-size: 14px;
}

.articles-section {
  margin-top: 30px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.section-header h2 {
  margin: 0;
  color: #333;
}

.articles-grid {
  margin-bottom: 30px;
}

.article-col {
  margin-bottom: 20px;
}

.article-card {
  height: 100%;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.article-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.1);
}

.article-cover {
  width: 100%;
  height: 160px;
  margin-bottom: 15px;
  border-radius: 4px;
  overflow: hidden;
}

.article-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.article-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}

.article-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.article-summary {
  color: #666;
  font-size: 14px;
  line-height: 1.6;
  margin: 10px 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.article-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 15px 0;
}

.meta-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.author-name {
  font-size: 14px;
  color: #666;
}

.meta-right {
  display: flex;
  gap: 15px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #999;
  font-size: 12px;
}

.article-footer {
  padding-top: 15px;
  border-top: 1px solid #f0f0f0;
  text-align: right;
}

.publish-time {
  color: #999;
  font-size: 12px;
}

.pagination-container {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

.error-container {
  text-align: center;
  padding: 60px 20px;
}
</style>