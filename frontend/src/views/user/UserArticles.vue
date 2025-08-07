<template>
  <div class="user-articles-container">
    <div class="page-header">
      <h1>我的文章</h1>
      <el-button type="primary" @click="$router.push('/articles/create')">
        <el-icon><EditPen /></el-icon>
        发布新文章
      </el-button>
    </div>
    
    <div class="filters">
      <el-tabs v-model="activeStatus" @tab-change="handleStatusChange">
        <el-tab-pane label="全部" name="all" />
        <el-tab-pane label="已发布" name="published" />
        <el-tab-pane label="草稿" name="draft" />
        <el-tab-pane label="已归档" name="archived" />
      </el-tabs>
    </div>
    
    <div class="articles-table">
      <el-table
        v-loading="loading"
        :data="articles"
        style="width: 100%"
        empty-text="暂无文章"
      >
        <el-table-column label="标题" min-width="300">
          <template #default="{ row }">
            <div class="article-title-cell">
              <h4 class="article-title" @click="viewArticle(row.id)">
                {{ row.title }}
              </h4>
              <p class="article-summary">{{ row.summary || '暂无摘要' }}</p>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag
              :type="getStatusType(row.status)"
              size="small"
            >
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="分类" width="120" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.category" size="small" :color="row.category.color">
              {{ row.category.name }}
            </el-tag>
            <span v-else class="text-muted">未分类</span>
          </template>
        </el-table-column>
        
        <el-table-column label="统计" width="150" align="center">
          <template #default="{ row }">
            <div class="article-stats">
              <span class="stat-item">
                <el-icon><View /></el-icon>
                {{ row.views }}
              </span>
              <span class="stat-item">
                <el-icon><Star /></el-icon>
                {{ row.likes }}
              </span>
              <span class="stat-item">
                <el-icon><ChatDotRound /></el-icon>
                {{ row.comments_count }}
              </span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="创建时间" width="150" align="center">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="180" align="center">
          <template #default="{ row }">
            <el-button size="small" @click="viewArticle(row.id)">
              查看
            </el-button>
            <el-button size="small" type="primary" @click="editArticle(row.id)">
              编辑
            </el-button>
            <el-popconfirm
              title="确定要删除这篇文章吗？"
              @confirm="deleteArticle(row.id)"
            >
              <template #reference>
                <el-button size="small" type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
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
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { usersAPI } from '@/api/users'
import { articlesAPI } from '@/api/articles'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(false)
const activeStatus = ref('all')
const articles = ref([])

const pagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0
})

// 获取用户文章
const fetchUserArticles = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.current,
      page_size: pagination.pageSize
    }
    
    // 根据状态筛选
    if (activeStatus.value !== 'all') {
      params.status = activeStatus.value
    }
    
    const response = await usersAPI.getUserArticles(authStore.user.id, params)
    
    articles.value = response.results || response
    pagination.total = response.count || articles.value.length
  } catch (error) {
    console.error('获取文章失败:', error)
    ElMessage.error('获取文章失败')
  } finally {
    loading.value = false
  }
}

// 状态变化处理
const handleStatusChange = () => {
  pagination.current = 1
  fetchUserArticles()
}

// 分页大小变化
const handleSizeChange = (size) => {
  pagination.pageSize = size
  pagination.current = 1
  fetchUserArticles()
}

// 当前页变化
const handleCurrentChange = (page) => {
  pagination.current = page
  fetchUserArticles()
}

// 查看文章
const viewArticle = (id) => {
  router.push({ name: 'ArticleDetail', params: { id } })
}

// 编辑文章
const editArticle = (id) => {
  router.push({ name: 'ArticleEdit', params: { id } })
}

// 删除文章
const deleteArticle = async (id) => {
  try {
    await articlesAPI.deleteArticle(id)
    ElMessage.success('文章删除成功！')
    
    // 重新获取文章列表
    await fetchUserArticles()
  } catch (error) {
    console.error('删除文章失败:', error)
    ElMessage.error('删除文章失败')
  }
}

// 获取状态类型
const getStatusType = (status) => {
  const types = {
    published: 'success',
    draft: 'warning',
    archived: 'info'
  }
  return types[status] || 'info'
}

// 获取状态文本
const getStatusText = (status) => {
  const texts = {
    published: '已发布',
    draft: '草稿',
    archived: '已归档'
  }
  return texts[status] || status
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
  fetchUserArticles()
})
</script>

<style scoped>
.user-articles-container {
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

.page-header h1 {
  margin: 0;
  color: #333;
}

.filters {
  margin-bottom: 20px;
}

.articles-table {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
}

.article-title-cell {
  padding: 5px 0;
}

.article-title {
  margin: 0 0 8px 0;
  color: #333;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: color 0.3s;
}

.article-title:hover {
  color: #409eff;
}

.article-summary {
  margin: 0;
  color: #666;
  font-size: 14px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.article-stats {
  display: flex;
  gap: 15px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #666;
  font-size: 12px;
}

.text-muted {
  color: #999;
}

.pagination-container {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

:deep(.el-table) {
  font-size: 14px;
}

:deep(.el-table th) {
  background: #fafafa;
  color: #333;
  font-weight: 600;
}

:deep(.el-table td) {
  padding: 12px 0;
}

:deep(.el-button) {
  margin: 0 2px;
}
</style>