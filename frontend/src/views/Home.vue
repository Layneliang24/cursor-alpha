<template>
  <div class="home">
    <el-row :gutter="20">
      <el-col :span="16">
        <div class="welcome-section">
          <h1>欢迎来到 Alpha 技术共享平台</h1>
          <p>这是一个现代化的技术文章分享网站，提供优质的技术内容</p>
          <el-button type="primary" size="large" @click="$router.push('/articles')">
            浏览文章
          </el-button>
        </div>
        
        <div class="featured-articles">
          <h2>推荐文章</h2>
          <el-row :gutter="20">
            <el-col :span="12" v-for="article in featuredArticles" :key="article.id">
              <el-card class="article-card" @click="viewArticle(article.id)">
                <template #header>
                  <div class="article-header">
                    <h3>{{ article.title }}</h3>
                    <el-tag size="small" v-if="article.featured">推荐</el-tag>
                  </div>
                </template>
                <div class="article-content">
                  <p>{{ article.summary }}</p>
                  <div class="article-meta">
                    <span>作者: {{ article.author?.username }}</span>
                    <span>阅读时间: {{ article.reading_time }}分钟</span>
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </div>
      </el-col>
      
      <el-col :span="8">
        <div class="sidebar">
          <el-card class="stats-card">
            <template #header>
              <h3>平台统计</h3>
            </template>
            <div class="stats">
              <div class="stat-item">
                <el-icon><Document /></el-icon>
                <span>文章: {{ stats.articles || 0 }}</span>
              </div>
              <div class="stat-item">
                <el-icon><User /></el-icon>
                <span>用户: {{ stats.users || 0 }}</span>
              </div>
              <div class="stat-item">
                <el-icon><Folder /></el-icon>
                <span>分类: {{ stats.categories || 0 }}</span>
              </div>
            </div>
          </el-card>
          
          <el-card class="categories-card">
            <template #header>
              <h3>热门分类</h3>
            </template>
            <div class="categories">
              <div 
                v-for="category in categories" 
                :key="category.id"
                class="category-item"
                @click="viewCategory(category.id)"
              >
                <span>{{ category.name }}</span>
                <el-tag size="small">{{ category.article_count }}</el-tag>
              </div>
            </div>
          </el-card>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'Home',
  setup() {
    const router = useRouter()
    const featuredArticles = ref([])
    const categories = ref([])
    const stats = ref({})
    
    const viewArticle = (id) => {
      router.push(`/articles/${id}`)
    }
    
    const viewCategory = (id) => {
      router.push(`/categories/${id}`)
    }
    
    onMounted(() => {
      // 模拟数据
      featuredArticles.value = [
        {
          id: 1,
          title: 'Django REST Framework 入门指南',
          summary: '详细介绍 Django REST Framework 的基本概念和使用方法',
          author: { username: 'admin' },
          reading_time: 5,
          featured: true
        },
        {
          id: 2,
          title: 'Vue.js 3.0 新特性解析',
          summary: '深入解析 Vue.js 3.0 的新特性和改进',
          author: { username: 'testuser' },
          reading_time: 8,
          featured: true
        }
      ]
      
      categories.value = [
        { id: 1, name: '技术分享', article_count: 5 },
        { id: 2, name: '学习笔记', article_count: 3 },
        { id: 3, name: '项目经验', article_count: 2 }
      ]
      
      stats.value = {
        articles: 10,
        users: 25,
        categories: 5
      }
    })
    
    return {
      featuredArticles,
      categories,
      stats,
      viewArticle,
      viewCategory
    }
  }
}
</script>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.welcome-section {
  text-align: center;
  padding: 40px 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 10px;
  margin-bottom: 30px;
}

.welcome-section h1 {
  font-size: 2.5em;
  margin-bottom: 20px;
}

.welcome-section p {
  font-size: 1.2em;
  margin-bottom: 30px;
  opacity: 0.9;
}

.featured-articles {
  margin-bottom: 30px;
}

.featured-articles h2 {
  margin-bottom: 20px;
  color: #303133;
}

.article-card {
  margin-bottom: 20px;
  cursor: pointer;
  transition: transform 0.2s;
}

.article-card:hover {
  transform: translateY(-2px);
}

.article-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.article-header h3 {
  margin: 0;
  color: #303133;
}

.article-content p {
  color: #606266;
  margin-bottom: 10px;
}

.article-meta {
  display: flex;
  justify-content: space-between;
  color: #909399;
  font-size: 0.9em;
}

.sidebar {
  position: sticky;
  top: 20px;
}

.stats-card, .categories-card {
  margin-bottom: 20px;
}

.stats {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #606266;
}

.categories {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.category-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.category-item:hover {
  background-color: #f5f7fa;
}

@media (max-width: 768px) {
  .el-col {
    width: 100% !important;
  }
  
  .welcome-section h1 {
    font-size: 2em;
  }
}
</style> 