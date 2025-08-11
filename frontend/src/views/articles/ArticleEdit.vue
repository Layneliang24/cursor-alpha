<template>
  <div class="article-edit-container">
    <div class="page-header">
      <h1>编辑文章</h1>
      <div class="header-actions">
        <el-button @click="saveDraft" :loading="savingDraft">保存草稿</el-button>
        <el-button type="primary" @click="updateArticle" :loading="updating">
          更新文章
        </el-button>
      </div>
    </div>
    
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="10" animated />
    </div>
    
    <div v-else-if="articleForm.title" class="edit-layout">
      <div class="edit-sidebar">
        <TableOfContents ref="tocRef" :content="articleForm.content" />
      </div>
      
      <div class="edit-main">
        <el-form
          ref="articleFormRef"
          :model="articleForm"
          :rules="articleRules"
          label-width="100px"
          class="article-form"
        >
      <el-form-item label="文章标题" prop="title">
        <el-input
          v-model="articleForm.title"
          placeholder="请输入文章标题"
          maxlength="200"
          show-word-limit
          size="large"
        />
      </el-form-item>
      
      <el-form-item label="文章摘要" prop="summary">
        <el-input
          v-model="articleForm.summary"
          type="textarea"
          :rows="3"
          placeholder="请输入文章摘要（可选）"
          maxlength="500"
          show-word-limit
        />
      </el-form-item>
      
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="文章分类" prop="category">
            <el-select
              v-model="articleForm.category"
              placeholder="请选择分类"
              style="width: 100%"
            >
              <el-option
                v-for="category in categories"
                :key="category.id"
                :label="category.name"
                :value="category.id"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="文章标签">
            <el-select
              v-model="articleForm.tags"
              multiple
              filterable
              allow-create
              placeholder="请选择或创建标签"
              style="width: 100%"
            >
              <el-option
                v-for="tag in tags"
                :key="tag.id"
                :label="tag.name"
                :value="tag.id"
              />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
      
      <el-form-item label="封面图片">
        <el-upload
          class="cover-uploader"
          :show-file-list="false"
          :before-upload="beforeCoverUpload"
          action="#"
          :http-request="uploadCover"
        >
          <img v-if="articleForm.cover_image" :src="articleForm.cover_image" class="cover-image" />
          <el-icon v-else class="cover-uploader-icon"><Plus /></el-icon>
          <div class="upload-tip">点击上传封面图片</div>
        </el-upload>
      </el-form-item>
      
      <el-form-item label="文章内容" prop="content" class="content-form-item">
        <MarkdownEditor v-model="articleForm.content" />
      </el-form-item>
      
        <el-form-item label="文章设置">
          <el-checkbox v-model="articleForm.featured">设为推荐文章</el-checkbox>
        </el-form-item>
        </el-form>
      </div>
    </div>
    
    <div v-else class="error-container">
      <el-empty description="文章不存在或无权限编辑">
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
import { useArticlesStore } from '@/stores/articles'
import { categoriesAPI } from '@/api/categories'
import { ElMessage } from 'element-plus'
import MarkdownEditor from '@/components/MarkdownEditor.vue'
import TableOfContents from '@/components/TableOfContents.vue'

const route = useRoute()
const router = useRouter()
const articlesStore = useArticlesStore()

const articleFormRef = ref()
const tocRef = ref()
const loading = ref(true)
const updating = ref(false)
const savingDraft = ref(false)
const categories = ref([])
const tags = ref([])

const articleForm = reactive({
  title: '',
  content: '',
  summary: '',
  category: '',
  tags: [],
  cover_image: '',
  featured: false,
  status: 'draft'
})

const articleRules = {
  title: [
    { required: true, message: '请输入文章标题', trigger: 'blur' },
    { min: 5, max: 200, message: '标题长度在 5 到 200 个字符', trigger: 'blur' }
  ],
  content: [
    { required: true, message: '请输入文章内容', trigger: 'blur' },
    { min: 50, message: '文章内容至少50个字符', trigger: 'blur' }
  ],
  category: [
    { required: true, message: '请选择文章分类', trigger: 'change' }
  ]
}

// 获取文章数据
const fetchArticle = async () => {
  try {
    loading.value = true
    await articlesStore.fetchArticle(route.params.id)
    
    const article = articlesStore.currentArticle
    if (article) {
      // 填充表单数据
      Object.assign(articleForm, {
        title: article.title,
        content: article.content,
        summary: article.summary || '',
        category: article.category?.id || '',
        tags: article.tags?.map(tag => tag.id) || [],
        cover_image: article.cover_image || '',
        featured: article.featured || false,
        status: article.status
      })
    }
  } catch (error) {
    console.error('获取文章失败:', error)
    ElMessage.error('文章不存在或无权限编辑')
  } finally {
    loading.value = false
  }
}

// 获取分类和标签
const fetchData = async () => {
  try {
    const [categoriesRes, tagsRes] = await Promise.all([
      categoriesAPI.getCategories(),
      categoriesAPI.getTags()
    ])
    
    categories.value = categoriesRes.results || categoriesRes
    tags.value = tagsRes.results || tagsRes
  } catch (error) {
    console.error('获取数据失败:', error)
    ElMessage.error('获取分类和标签失败')
  }
}

// 上传封面图片前的验证
const beforeCoverUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  const isLt2M = file.size / 1024 / 1024 < 2
  
  if (!isImage) {
    ElMessage.error('上传文件只能是图片格式!')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('上传文件大小不能超过 2MB!')
    return false
  }
  return true
}

// 上传封面图片
const uploadCover = async (options) => {
  const formData = new FormData()
  formData.append('file', options.file)
  
  try {
    // 这里应该调用后端的文件上传接口
    // const response = await uploadAPI.uploadFile(formData)
    // articleForm.cover_image = response.url
    
    // 临时使用本地预览
    const reader = new FileReader()
    reader.onload = (e) => {
      articleForm.cover_image = e.target.result
    }
    reader.readAsDataURL(options.file)
    
    ElMessage.success('封面上传成功')
  } catch (error) {
    console.error('上传失败:', error)
    ElMessage.error('封面上传失败')
  }
}

// 保存草稿
const saveDraft = async () => {
  if (!articleForm.title.trim()) {
    ElMessage.warning('请至少输入文章标题')
    return
  }
  
  // 防止重复保存
  if (savingDraft.value) {
    ElMessage.warning('正在保存中，请稍候...')
    return
  }
  
  savingDraft.value = true
  try {
    const articleData = {
      ...articleForm,
      status: 'draft'
    }
    
    await articlesStore.updateArticle(route.params.id, articleData)
    ElMessage.success('草稿保存成功！')
  } catch (error) {
    console.error('保存草稿失败:', error)
    ElMessage.error('保存草稿失败')
  } finally {
    savingDraft.value = false
  }
}

// 更新文章
const updateArticle = async () => {
  if (!articleFormRef.value) return
  
  // 防止重复更新
  if (updating.value) {
    ElMessage.warning('正在更新中，请稍候...')
    return
  }
  
  try {
    await articleFormRef.value.validate()
    
    updating.value = true
    const articleData = {
      ...articleForm,
      status: 'published'
    }
    
    await articlesStore.updateArticle(route.params.id, articleData)
    
    // 显示成功动画和倒计时
    showUpdateSuccessAnimation()
    
  } catch (error) {
    console.error('更新文章失败:', error)
    if (error.response?.data) {
      const errors = error.response.data
      for (const field in errors) {
        if (Array.isArray(errors[field])) {
          ElMessage.error(`${field}: ${errors[field][0]}`)
        }
      }
    } else {
      ElMessage.error('更新失败，请重试')
    }
  } finally {
    updating.value = false
  }
}

// 显示更新成功动画和倒计时
const showUpdateSuccessAnimation = () => {
  // 创建成功动画容器
  const successContainer = document.createElement('div')
  successContainer.className = 'success-animation-container'
  
  // 倒计时跳转
  let countdown = 3
  let countdownInterval = null
  let shouldRedirect = true // 控制是否应该跳转
  
  const updateCountdown = () => {
    const countdownElement = document.getElementById('countdown-number')
    if (countdownElement) {
      countdownElement.textContent = countdown
    }
    if (countdown <= 0 && shouldRedirect) {
      clearInterval(countdownInterval)
      router.push({ name: 'ArticleDetail', params: { id: route.params.id } })
    }
  }
  
  // 继续编辑的处理函数
  const handleContinueEdit = () => {
    shouldRedirect = false // 停止自动跳转
    clearInterval(countdownInterval) // 清除倒计时
    successContainer.remove() // 移除动画容器
    
    ElMessage.success('可以继续编辑文章')
  }
  
  successContainer.innerHTML = `
    <div class="success-content">
      <div class="success-icon">✨</div>
      <h2>更新成功！</h2>
      <p>文章已成功更新并发布</p>
      <div class="countdown">
        <span id="countdown-number">3</span> 秒后自动跳转到文章页面
      </div>
      <div class="success-actions">
        <button class="view-article-btn" onclick="window.location.href='/articles/${route.params.id}'">
          查看文章
        </button>
        <button class="go-home-btn" onclick="window.location.href='/'">
          返回首页
        </button>
        <button class="stay-here-btn" id="continue-edit-btn">
          继续编辑
        </button>
      </div>
    </div>
  `
  
  // 添加样式
  successContainer.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.8);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 9999;
    animation: fadeIn 0.3s ease;
  `
  
  document.body.appendChild(successContainer)
  
  // 绑定继续编辑按钮事件
  const continueEditBtn = document.getElementById('continue-edit-btn')
  if (continueEditBtn) {
    continueEditBtn.addEventListener('click', handleContinueEdit)
  }
  
  // 开始倒计时
  countdownInterval = setInterval(() => {
    countdown--
    updateCountdown()
  }, 1000)
  
  // 添加CSS动画
  const style = document.createElement('style')
  style.textContent = `
    @keyframes fadeIn {
      from { opacity: 0; }
      to { opacity: 1; }
    }
    
    @keyframes bounce {
      0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
      40% { transform: translateY(-10px); }
      60% { transform: translateY(-5px); }
    }
    
    .success-content {
      background: white;
      padding: 40px;
      border-radius: 16px;
      text-align: center;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
      animation: bounce 0.6s ease;
      max-width: 400px;
      width: 90%;
    }
    
    .success-icon {
      font-size: 60px;
      margin-bottom: 20px;
      animation: bounce 1s ease infinite;
    }
    
    .success-content h2 {
      color: #67c23a;
      margin: 0 0 10px 0;
      font-size: 24px;
      font-weight: bold;
    }
    
    .success-content p {
      color: #666;
      margin: 0 0 20px 0;
      font-size: 16px;
    }
    
    .countdown {
      background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
      padding: 15px;
      border-radius: 8px;
      margin: 20px 0;
      color: #409eff;
      font-weight: bold;
      border: 1px solid #bae6fd;
    }
    
    #countdown-number {
      font-size: 20px;
      color: #e6a23c;
      font-weight: bold;
    }
    
    .success-actions {
      display: flex;
      flex-direction: column;
      gap: 10px;
      margin-top: 20px;
    }
    
    .view-article-btn, .go-home-btn, .stay-here-btn {
      padding: 12px 20px;
      border: none;
      border-radius: 6px;
      cursor: pointer;
      font-size: 14px;
      font-weight: 500;
      transition: all 0.3s ease;
      width: 100%;
    }
    
    .view-article-btn {
      background: linear-gradient(135deg, #409eff 0%, #337ecc 100%);
      color: white;
    }
    
    .view-article-btn:hover {
      background: linear-gradient(135deg, #337ecc 0%, #2c5aa0 100%);
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
    }
    
    .go-home-btn {
      background: linear-gradient(135deg, #67c23a 0%, #5daf34 100%);
      color: white;
    }
    
    .go-home-btn:hover {
      background: linear-gradient(135deg, #5daf34 0%, #4c8b2a 100%);
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(103, 194, 58, 0.3);
    }
    
    .stay-here-btn {
      background: #f5f7fa;
      color: #606266;
      border: 1px solid #dcdfe6;
    }
    
    .stay-here-btn:hover {
      background: #e4e7ed;
      transform: translateY(-2px);
    }
  `
  document.head.appendChild(style)
}

onMounted(async () => {
  await Promise.all([fetchData(), fetchArticle()])
})
</script>

<style scoped>
.article-edit-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.edit-layout {
  display: grid;
  grid-template-columns: 220px 1fr;
  gap: 20px;
  align-items: start;
}

.edit-main {
  min-width: 0;
}

.edit-sidebar {
  position: sticky;
  top: 80px;
  max-height: calc(100vh - 100px);
  overflow-y: auto;
  margin-left: -40px;
}

@media (max-width: 1024px) {
  .edit-layout {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .edit-sidebar {
    order: -1;
    position: static;
  }
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.page-header h1 {
  margin: 0;
  color: #333;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.loading-container {
  padding: 20px;
}

.article-form {
  background: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
}

.content-form-item {
  margin-bottom: 30px;
}

.content-form-item :deep(.el-form-item__content) {
  width: 100% !important;
}

.cover-uploader {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: border-color 0.3s;
  width: 200px;
  height: 120px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.cover-uploader:hover {
  border-color: #409eff;
}

.cover-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  margin-bottom: 8px;
}

.cover-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.upload-tip {
  color: #8c939d;
  font-size: 12px;
  text-align: center;
}

.error-container {
  text-align: center;
  padding: 60px 20px;
}

:deep(.el-form-item__label) {
  font-weight: 600;
  color: #333;
}

:deep(.el-input__inner),
:deep(.el-textarea__inner) {
  border-radius: 4px;
}

:deep(.el-select) {
  width: 100%;
}
</style>