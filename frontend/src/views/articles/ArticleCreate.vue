<template>
  <div class="article-create-container">
    <div class="page-header">
      <h1>发布文章</h1>
      <div class="header-actions">
        <el-button @click="saveDraft" :loading="savingDraft">保存草稿</el-button>
        <el-button type="primary" @click="publishArticle" :loading="publishing">
          发布文章
        </el-button>
      </div>
    </div>
    
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
      
      <el-form-item label="文章内容" prop="content">
        <div class="editor-container">
          <el-input
            v-model="articleForm.content"
            type="textarea"
            :rows="20"
            placeholder="请输入文章内容，支持 Markdown 格式..."
            class="content-editor"
          />
        </div>
      </el-form-item>
      
      <el-form-item label="文章设置">
        <el-checkbox v-model="articleForm.featured">设为推荐文章</el-checkbox>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useArticlesStore } from '@/stores/articles'
import { categoriesAPI } from '@/api/categories'
import { ElMessage } from 'element-plus'

const router = useRouter()
const articlesStore = useArticlesStore()

const articleFormRef = ref()
const publishing = ref(false)
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
  
  savingDraft.value = true
  try {
    const articleData = {
      ...articleForm,
      status: 'draft'
    }
    
    await articlesStore.createArticle(articleData)
    ElMessage.success('草稿保存成功！')
    router.push('/user/articles')
  } catch (error) {
    console.error('保存草稿失败:', error)
    ElMessage.error('保存草稿失败')
  } finally {
    savingDraft.value = false
  }
}

// 发布文章
const publishArticle = async () => {
  if (!articleFormRef.value) return
  
  try {
    await articleFormRef.value.validate()
    
    publishing.value = true
    const articleData = {
      ...articleForm,
      status: 'published',
      published_at: new Date().toISOString()
    }
    
    const article = await articlesStore.createArticle(articleData)
    ElMessage.success('文章发布成功！')
    router.push({ name: 'ArticleDetail', params: { id: article.id } })
  } catch (error) {
    console.error('发布文章失败:', error)
    if (error.response?.data) {
      const errors = error.response.data
      for (const field in errors) {
        if (Array.isArray(errors[field])) {
          ElMessage.error(`${field}: ${errors[field][0]}`)
        }
      }
    }
  } finally {
    publishing.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.article-create-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
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

.article-form {
  background: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
}

.editor-container {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
}

.content-editor {
  border: none;
}

.content-editor :deep(.el-textarea__inner) {
  border: none;
  box-shadow: none;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  line-height: 1.6;
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