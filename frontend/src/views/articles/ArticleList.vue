<template>
  <div class="article-list-container">
    <div class="page-header">
      <h1>全部文章</h1>
      <div class="header-actions">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索文章..."
          style="width: 300px"
          @keyup.enter="handleSearch"
          clearable
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button type="primary" @click="handleSearch">搜索</el-button>
      </div>
    </div>
    
    <div class="filters">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-select
            v-model="selectedCategory"
            placeholder="选择分类"
            @change="handleCategoryChange"
            clearable
            style="width: 100%"
          >
            <el-option
              v-for="category in categories"
              :key="category.id"
              :label="category.name"
              :value="category.id"
            />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-select
            v-model="selectedSort"
            placeholder="排序方式"
            @change="handleSortChange"
            style="width: 100%"
          >
            <el-option label="最新发布" value="-created_at" />
            <el-option label="最多浏览" value="-views" />
            <el-option label="最多点赞" value="-likes" />
          </el-select>
        </el-col>
      </el-row>
    </div>
    
    <div class="article-grid">
      <el-row :gutter="20" v-loading="articlesStore.loading">
        <el-col 
          :span="8" 
          v-for="article in articlesStore.articles" 
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
              <el-tag 
                v-if="article.category" 
                size="small" 
                :color="article.category.color"
              >
                {{ article.category.name }}
              </el-tag>
              <span class="publish-time">
                {{ formatDate(article.created_at) }}
              </span>
            </div>
          </el-card>
        </el-col>
        
        <!-- 空状态 -->
        <el-col :span="24" v-if="!articlesStore.loading && articlesStore.articles.length === 0">
          <el-empty description="暂无文章">
            <el-button type="primary" @click="$router.push('/articles/create')">
              发布第一篇文章
            </el-button>
          </el-empty>
        </el-col>
      </el-row>
    </div>
    
    <!-- 分页 -->
    <div class="pagination-container" v-if="articlesStore.pagination.total > 0">
      <el-pagination
        v-model:current-page="articlesStore.pagination.current"
        v-model:page-size="articlesStore.pagination.pageSize"
        :total="articlesStore.pagination.total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useArticlesStore } from '@/stores/articles'
import { categoriesAPI } from '@/api/categories'
import { ElMessage } from 'element-plus'

const router = useRouter()
const articlesStore = useArticlesStore()

const searchKeyword = ref('')
const selectedCategory = ref('')
const selectedSort = ref('-created_at')
const categories = ref([])

// 获取分类列表
const fetchCategories = async () => {
  try {
    const response = await categoriesAPI.getCategories()
    categories.value = response.results || response
  } catch (error) {
    console.error('获取分类失败:', error)
  }
}

// 获取文章列表
const fetchArticles = async () => {
  const params = {
    ordering: selectedSort.value
  }
  
  if (searchKeyword.value) {
    params.search = searchKeyword.value
  }
  
  if (selectedCategory.value) {
    params.category = selectedCategory.value
  }
  
  try {
    await articlesStore.fetchArticles(params)
  } catch (error) {
    console.error('获取文章失败:', error)
  }
}

// 搜索处理
const handleSearch = () => {
  articlesStore.pagination.current = 1
  fetchArticles()
}

// 分类变化处理
const handleCategoryChange = () => {
  articlesStore.pagination.current = 1
  fetchArticles()
}

// 排序变化处理
const handleSortChange = () => {
  articlesStore.pagination.current = 1
  fetchArticles()
}

// 分页大小变化
const handleSizeChange = (size) => {
  articlesStore.pagination.pageSize = size
  articlesStore.pagination.current = 1
  fetchArticles()
}

// 当前页变化
const handleCurrentChange = (page) => {
  articlesStore.pagination.current = page
  fetchArticles()
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

onMounted(() => {
  fetchCategories()
  fetchArticles()
})
</script>

<style scoped>
.article-list-container {
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

.header-actions {
  display: flex;
  gap: 10px;
}

.filters {
  margin-bottom: 30px;
}

.article-grid {
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
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 15px;
  border-top: 1px solid #f0f0f0;
}

.publish-time {
  color: #999;
  font-size: 12px;
}

.pagination-container {
  display: flex;
  justify-content: center;
  padding: 40px 0 20px 0;
  margin-top: 30px;
  border-top: 1px solid #f0f0f0;
}

:deep(.el-pagination) {
  --el-pagination-font-size: 14px;
  --el-pagination-bg-color: #fff;
  --el-pagination-text-color: #606266;
  --el-pagination-border-radius: 6px;
}

:deep(.el-pagination .btn-next),
:deep(.el-pagination .btn-prev) {
  background: #fff;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
}

:deep(.el-pagination .el-pager li) {
  background: #fff;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  margin: 0 4px;
}

:deep(.el-pagination .el-pager li.is-active) {
  background: #409eff;
  border-color: #409eff;
  color: #fff;
}
</style>