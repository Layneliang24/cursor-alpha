<template>
  <div class="article-detail-container">
    <div v-if="articlesStore.loading" class="loading-container">
      <el-skeleton :rows="10" animated />
    </div>
    
    <div v-else-if="article" class="article-layout">
      <div class="article-sidebar">
        <TableOfContents ref="tocRef" />
      </div>
      
      <div class="article-main">
        <!-- 文章头部 -->
        <div class="article-header">
          <div class="article-meta">
            <el-breadcrumb separator="/">
              <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
              <el-breadcrumb-item :to="{ path: '/articles' }">文章</el-breadcrumb-item>
              <el-breadcrumb-item v-if="article.category" :to="{ path: `/categories/${article.category.id}` }">
                {{ article.category.name }}
              </el-breadcrumb-item>
              <el-breadcrumb-item>{{ article.title }}</el-breadcrumb-item>
            </el-breadcrumb>
          </div>
          
          <h1 class="article-title">{{ article.title }}</h1>
          
          <div class="article-info">
            <div class="author-info">
              <el-avatar :size="40" :src="article.author?.avatar">
                {{ article.author?.username?.charAt(0)?.toUpperCase() }}
              </el-avatar>
              <div class="author-details">
                <div class="author-name">{{ article.author?.username }}</div>
                <div class="publish-info">
                  发布于 {{ formatDate(article.created_at) }} · 
                  阅读时间约 {{ article.reading_time }} 分钟
                </div>
              </div>
            </div>
            
            <div class="article-stats">
              <span class="stat-item">
                <el-icon><View /></el-icon>
                {{ article.views }}
              </span>
              <span class="stat-item">
                <el-icon><Star /></el-icon>
                {{ article.likes }}
              </span>
              <span class="stat-item">
                <el-icon><ChatDotRound /></el-icon>
                {{ article.comments_count }}
              </span>
            </div>
          </div>
          
          <div class="article-tags" v-if="article.tags && article.tags.length > 0">
            <el-tag 
              v-for="tag in article.tags" 
              :key="tag.id" 
              size="small"
              :style="{
                backgroundColor: tag.color || '#409eff',
                color: getContrastColor(tag.color || '#409eff'),
                border: `1px solid ${tag.color || '#409eff'}`,
                marginRight: '8px'
              }"
            >
              {{ tag.name }}
            </el-tag>
          </div>
        </div>
        
        <!-- 文章封面 -->
        <div class="article-cover" v-if="article.cover_image">
          <img :src="article.cover_image" :alt="article.title" />
        </div>
        
        <!-- 文章正文 -->
        <div class="article-body">
          <div class="article-content">
            <MarkdownRenderer :content="article.content" />
          </div>
        </div>
        
        <!-- 文章操作 -->
        <div class="article-actions">
          <el-button 
            :type="isLiked ? 'danger' : 'default'"
            @click="toggleLike"
            :loading="likeLoading"
          >
            <el-icon><Star /></el-icon>
            {{ isLiked ? '已点赞' : '点赞' }} ({{ article.likes }})
          </el-button>
          <el-button 
            :type="isBookmarked ? 'warning' : 'default'"
            @click="toggleBookmark"
            :loading="bookmarkLoading"
          >
            <el-icon><Collection /></el-icon>
            {{ isBookmarked ? '已收藏' : '收藏' }}
          </el-button>
          <el-button @click="shareArticle">
            <el-icon><Share /></el-icon>
            分享
          </el-button>
        </div>
        
        <!-- 评论区 -->
        <div class="comments-section">
          <h3>评论 ({{ article.comments_count }})</h3>
          
          <!-- 发表评论 -->
          <div class="comment-form" v-if="authStore.isAuthenticated">
            <el-input
              v-model="newComment"
              type="textarea"
              :rows="4"
              placeholder="写下你的评论..."
              maxlength="500"
              show-word-limit
            />
            <div class="comment-form-actions">
              <el-button 
                type="primary" 
                @click="submitComment"
                :loading="commentLoading"
                :disabled="!newComment.trim()"
              >
                发表评论
              </el-button>
            </div>
          </div>
          
          <div class="login-prompt" v-else>
            <p>
              <router-link to="/login">登录</router-link> 后参与评论
            </p>
          </div>
          
          <!-- 评论列表 -->
          <div class="comments-list">
            <div 
              v-for="comment in comments" 
              :key="comment.id" 
              class="comment-item"
            >
              <div class="comment-header">
                <el-avatar :size="32" :src="comment.author?.avatar">
                  {{ comment.author?.username?.charAt(0)?.toUpperCase() }}
                </el-avatar>
                <div class="comment-info">
                  <div class="comment-author">{{ comment.author?.username }}</div>
                  <div class="comment-time">{{ formatDate(comment.created_at) }}</div>
                </div>
              </div>
              <div class="comment-content">{{ comment.content }}</div>
            </div>
            
            <el-empty v-if="comments.length === 0" description="暂无评论" />
          </div>
        </div>
      </div>
    </div>
    
    <div v-else class="error-container">
      <el-empty description="文章不存在或已被删除">
        <el-button type="primary" @click="$router.push('/articles')">
          返回文章列表
        </el-button>
      </el-empty>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useArticlesStore } from '@/stores/articles'
import { useAuthStore } from '@/stores/auth'
import { articlesAPI } from '@/api/articles'
import { ElMessage } from 'element-plus'
import { View, Star, ChatDotRound, Collection, Share } from '@element-plus/icons-vue'
import MarkdownRenderer from '@/components/MarkdownRenderer.vue'
import TableOfContents from '@/components/TableOfContents.vue'

const route = useRoute()
const router = useRouter()
const articlesStore = useArticlesStore()
const authStore = useAuthStore()

const article = computed(() => articlesStore.currentArticle)
const comments = ref([])
const newComment = ref('')
const commentLoading = ref(false)
const likeLoading = ref(false)
const bookmarkLoading = ref(false)
const isLiked = ref(false)
const isBookmarked = ref(false)
const tocRef = ref()

// 获取文章详情
const fetchArticle = async () => {
  try {
    await articlesStore.fetchArticle(route.params.id)
    // 获取评论
    await fetchComments()
    
    // 等待内容渲染完成后生成目录
    setTimeout(() => {
      if (tocRef.value && tocRef.value.generateTOC) {
        tocRef.value.generateTOC()
      }
    }, 1000)
  } catch (error) {
    console.error('获取文章失败:', error)
    ElMessage.error('文章不存在或已被删除')
  }
}

// 获取评论列表
const fetchComments = async () => {
  try {
    const response = await articlesAPI.getComments(route.params.id)
    comments.value = response.results || response
  } catch (error) {
    console.error('获取评论失败:', error)
  }
}

// 发表评论
const submitComment = async () => {
  if (!newComment.value.trim()) return
  
  commentLoading.value = true
  try {
    await articlesAPI.createComment({
      article: route.params.id,
      content: newComment.value.trim()
    })
    
    newComment.value = ''
    ElMessage.success('评论发表成功！')
    
    // 重新获取评论列表
    await fetchComments()
    // 更新文章评论数
    await fetchArticle()
  } catch (error) {
    console.error('发表评论失败:', error)
    ElMessage.error('发表评论失败')
  } finally {
    commentLoading.value = false
  }
}

// 点赞
const toggleLike = async () => {
  if (!authStore.isAuthenticated) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  
  likeLoading.value = true
  try {
    await articlesStore.likeArticle(route.params.id)
    isLiked.value = !isLiked.value
  } catch (error) {
    console.error('点赞失败:', error)
  } finally {
    likeLoading.value = false
  }
}

// 收藏
const toggleBookmark = async () => {
  if (!authStore.isAuthenticated) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  
  bookmarkLoading.value = true
  try {
    await articlesStore.bookmarkArticle(route.params.id)
    isBookmarked.value = !isBookmarked.value
  } catch (error) {
    console.error('收藏失败:', error)
  } finally {
    bookmarkLoading.value = false
  }
}

// 分享文章
const shareArticle = () => {
  const url = window.location.href
  navigator.clipboard.writeText(url).then(() => {
    ElMessage.success('链接已复制到剪贴板')
  }).catch(() => {
    ElMessage.error('复制失败')
  })
}

// 格式化日期
const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 根据背景色计算合适的文字颜色
const getContrastColor = (hexColor) => {
  if (!hexColor) return '#333333'
  
  // 移除#号
  const color = hexColor.replace('#', '')
  
  // 如果颜色长度不对，返回默认颜色
  if (color.length !== 6) return '#333333'
  
  // 转换为RGB
  const r = parseInt(color.substr(0, 2), 16)
  const g = parseInt(color.substr(2, 2), 16)
  const b = parseInt(color.substr(4, 2), 16)
  
  // 计算亮度 (0-255)
  const brightness = (r * 299 + g * 587 + b * 114) / 1000
  
  // 如果背景较暗，使用白色文字；如果背景较亮，使用深色文字
  return brightness > 128 ? '#333333' : '#ffffff'
}

onMounted(() => {
  fetchArticle()
})
</script>

<style scoped>
.article-detail-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
  line-height: 1.6;
}

.article-layout {
  display: grid;
  grid-template-columns: 220px 1fr;
  gap: 20px;
  align-items: start;
}

.article-main {
  min-width: 0;
}

.article-sidebar {
  position: sticky;
  top: 80px;
  max-height: calc(100vh - 100px);
  overflow-y: auto;
  margin-left: -40px;
}

@media (max-width: 1024px) {
  .article-layout {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .article-sidebar {
    order: -1;
    position: static;
  }
}

.loading-container {
  padding: 20px;
}

.article-header {
  margin-bottom: 30px;
}

.article-meta {
  margin-bottom: 20px;
}

.article-title {
  font-size: 32px;
  font-weight: 700;
  color: #333;
  margin: 20px 0;
  line-height: 1.3;
}

.article-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 0;
  border-bottom: 1px solid #f0f0f0;
}

.author-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.author-details {
  display: flex;
  flex-direction: column;
}

.author-name {
  font-weight: 600;
  color: #333;
}

.publish-info {
  color: #666;
  font-size: 14px;
}

.article-stats {
  display: flex;
  gap: 20px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #666;
  font-size: 14px;
}

.article-tags {
  margin: 20px 0;
}

.article-cover {
  margin: 30px 0;
  text-align: center;
}

.article-cover img {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.article-body {
  margin: 40px 0;
}

.article-actions {
  display: flex;
  gap: 15px;
  padding: 30px 0;
  border-top: 1px solid #f0f0f0;
  border-bottom: 1px solid #f0f0f0;
}

.comments-section {
  margin-top: 40px;
}

.comments-section h3 {
  margin-bottom: 20px;
  color: #333;
}

.comment-form {
  margin-bottom: 30px;
}

.comment-form-actions {
  margin-top: 10px;
  text-align: right;
}

.login-prompt {
  text-align: center;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 4px;
  margin-bottom: 30px;
}

.login-prompt a {
  color: #409eff;
  text-decoration: none;
}

.comments-list {
  margin-top: 20px;
}

.comment-item {
  padding: 20px 0;
  border-bottom: 1px solid #f0f0f0;
}

.comment-item:last-child {
  border-bottom: none;
}

.comment-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}

.comment-info {
  display: flex;
  flex-direction: column;
}

.comment-author {
  font-weight: 600;
  color: #333;
  font-size: 14px;
}

.comment-time {
  color: #999;
  font-size: 12px;
}

.comment-content {
  margin-left: 44px;
  color: #333;
  line-height: 1.6;
}

.error-container {
  text-align: center;
  padding: 60px 20px;
}
</style>