<template>
  <div class="profile-container">
    <div class="profile-header">
      <h1>个人中心</h1>
    </div>
    
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card class="profile-card">
          <div class="avatar-section">
            <el-avatar :size="100" :src="userProfile.avatar">
              {{ authStore.user?.username?.charAt(0)?.toUpperCase() }}
            </el-avatar>
            <el-button type="primary" size="small" @click="showAvatarUpload = true">
              更换头像
            </el-button>
          </div>
          
          <div class="user-info">
            <h3>{{ authStore.user?.username }}</h3>
            <p class="user-email">{{ authStore.user?.email }}</p>
            <p class="join-date">
              加入时间：{{ formatDate(authStore.user?.date_joined) }}
            </p>
          </div>
          
          <el-divider />
          
          <div class="user-stats">
            <div class="stat-item">
              <span class="stat-number">{{ userStats.articles }}</span>
              <span class="stat-label">文章</span>
            </div>
            <div class="stat-item">
              <span class="stat-number">{{ userStats.likes }}</span>
              <span class="stat-label">获赞</span>
            </div>
            <div class="stat-item">
              <span class="stat-number">{{ userStats.views }}</span>
              <span class="stat-label">阅读</span>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="16">
        <el-card class="profile-form-card">
          <template #header>
            <div class="card-header">
              <span>个人资料</span>
            </div>
          </template>
          
          <el-form
            ref="profileFormRef"
            :model="profileForm"
            :rules="profileRules"
            label-width="100px"
            class="profile-form"
          >
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="用户名" prop="username">
                  <el-input v-model="profileForm.username" disabled />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="邮箱" prop="email">
                  <el-input v-model="profileForm.email" />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="姓名" prop="first_name">
                  <el-input v-model="profileForm.first_name" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="手机号" prop="phone">
                  <el-input v-model="profileForm.phone" />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="公司" prop="company">
                  <el-input v-model="profileForm.company" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="职位" prop="position">
                  <el-input v-model="profileForm.position" />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-form-item label="所在地" prop="location">
              <el-input v-model="profileForm.location" />
            </el-form-item>
            
            <el-form-item label="个人简介" prop="bio">
              <el-input
                v-model="profileForm.bio"
                type="textarea"
                :rows="4"
                placeholder="介绍一下自己..."
                maxlength="500"
                show-word-limit
              />
            </el-form-item>
            
            <el-form-item label="个人网站" prop="website">
              <el-input v-model="profileForm.website" />
            </el-form-item>
            
            <el-form-item label="技能标签" prop="skills">
              <el-input
                v-model="profileForm.skills"
                placeholder="用逗号分隔，如：JavaScript, Vue.js, Python"
              />
            </el-form-item>
            
            <el-divider content-position="left">社交链接</el-divider>
            
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="GitHub" prop="github">
                  <el-input v-model="profileForm.github" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="LinkedIn" prop="linkedin">
                  <el-input v-model="profileForm.linkedin" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="Twitter" prop="twitter">
                  <el-input v-model="profileForm.twitter" />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-form-item>
              <el-button type="primary" @click="updateProfile" :loading="updating">
                保存修改
              </el-button>
              <el-button @click="resetForm">重置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 头像上传对话框 -->
    <el-dialog v-model="showAvatarUpload" title="更换头像" width="400px">
      <el-upload
        class="avatar-uploader"
        :show-file-list="false"
        :before-upload="beforeAvatarUpload"
        action="#"
        :http-request="uploadAvatar"
      >
        <img v-if="newAvatar" :src="newAvatar" class="avatar-preview" />
        <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
      </el-upload>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showAvatarUpload = false">取消</el-button>
          <el-button type="primary" @click="saveAvatar" :disabled="!newAvatar">
            保存
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { usersAPI } from '@/api/users'
import { ElMessage } from 'element-plus'

const authStore = useAuthStore()

const profileFormRef = ref()
const updating = ref(false)
const showAvatarUpload = ref(false)
const newAvatar = ref('')

const userProfile = reactive({
  avatar: ''
})

const userStats = reactive({
  articles: 0,
  likes: 0,
  views: 0
})

const profileForm = reactive({
  username: '',
  email: '',
  first_name: '',
  phone: '',
  company: '',
  position: '',
  location: '',
  bio: '',
  website: '',
  skills: '',
  github: '',
  linkedin: '',
  twitter: ''
})

const profileRules = {
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  website: [
    { type: 'url', message: '请输入正确的网址格式', trigger: 'blur' }
  ],
  github: [
    { type: 'url', message: '请输入正确的GitHub链接', trigger: 'blur' }
  ],
  linkedin: [
    { type: 'url', message: '请输入正确的LinkedIn链接', trigger: 'blur' }
  ],
  twitter: [
    { type: 'url', message: '请输入正确的Twitter链接', trigger: 'blur' }
  ]
}

// 获取用户资料
const fetchUserProfile = async () => {
  try {
    const profile = await usersAPI.getUserProfile(authStore.user.id)
    
    // 填充基本信息
    Object.assign(profileForm, {
      username: authStore.user.username,
      email: authStore.user.email,
      first_name: authStore.user.first_name || '',
      ...profile
    })
    
    userProfile.avatar = authStore.user.avatar || profile.avatar
  } catch (error) {
    console.error('获取用户资料失败:', error)
    // ElMessage.error('获取用户资料失败')
  }
}

// 获取用户统计
const fetchUserStats = async () => {
  try {
    const articles = await usersAPI.getUserArticles(authStore.user.id)
    userStats.articles = articles.count || articles.length || 0
    
    // 计算总点赞数和总阅读数
    if (articles.results || articles.length) {
      const articleList = articles.results || articles
      userStats.likes = articleList.reduce((sum, article) => sum + (article.likes || 0), 0)
      userStats.views = articleList.reduce((sum, article) => sum + (article.views || 0), 0)
    }
  } catch (error) {
    console.error('获取用户统计失败:', error)
  }
}

// 更新用户资料
const updateProfile = async () => {
  if (!profileFormRef.value) return
  
  try {
    await profileFormRef.value.validate()
    
    updating.value = true
    
    // 更新用户基本信息
    await usersAPI.updateUser(authStore.user.id, {
      email: profileForm.email,
      first_name: profileForm.first_name
    })
    
    // 更新用户详细资料
    await usersAPI.updateUserProfile(authStore.user.id, {
      phone: profileForm.phone,
      company: profileForm.company,
      position: profileForm.position,
      location: profileForm.location,
      bio: profileForm.bio,
      website: profileForm.website,
      skills: profileForm.skills,
      github: profileForm.github,
      linkedin: profileForm.linkedin,
      twitter: profileForm.twitter
    })
    
    ElMessage.success('资料更新成功！')
    
    // 重新获取用户信息
    await authStore.initAuth()
  } catch (error) {
    console.error('更新资料失败:', error)
    ElMessage.error('更新资料失败')
  } finally {
    updating.value = false
  }
}

// 重置表单
const resetForm = () => {
  fetchUserProfile()
}

// 头像上传前验证
const beforeAvatarUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  const isLt2M = file.size / 1024 / 1024 < 2
  
  if (!isImage) {
    ElMessage.error('头像只能是图片格式!')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('头像大小不能超过 2MB!')
    return false
  }
  return true
}

// 上传头像
const uploadAvatar = async (options) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    newAvatar.value = e.target.result
  }
  reader.readAsDataURL(options.file)
}

// 保存头像
const saveAvatar = async () => {
  try {
    // 这里应该调用后端的头像上传接口
    // await usersAPI.updateAvatar(authStore.user.id, newAvatar.value)
    
    userProfile.avatar = newAvatar.value
    showAvatarUpload.value = false
    newAvatar.value = ''
    ElMessage.success('头像更新成功！')
  } catch (error) {
    console.error('头像更新失败:', error)
    ElMessage.error('头像更新失败')
  }
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '未知'
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

onMounted(() => {
  fetchUserProfile()
  fetchUserStats()
})
</script>

<style scoped>
.profile-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.profile-header {
  margin-bottom: 30px;
}

.profile-header h1 {
  margin: 0;
  color: #333;
}

.profile-card {
  text-align: center;
}

.avatar-section {
  margin-bottom: 20px;
}

.avatar-section .el-button {
  margin-top: 10px;
}

.user-info h3 {
  margin: 10px 0 5px 0;
  color: #333;
}

.user-email {
  color: #666;
  margin: 5px 0;
}

.join-date {
  color: #999;
  font-size: 14px;
  margin: 5px 0;
}

.user-stats {
  display: flex;
  justify-content: space-around;
  padding: 20px 0;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 5px;
}

.stat-label {
  color: #666;
  font-size: 14px;
}

.profile-form-card {
  height: fit-content;
}

.card-header {
  font-weight: 600;
  color: #333;
}

.profile-form {
  padding: 10px 0;
}

.avatar-uploader {
  display: flex;
  justify-content: center;
}

.avatar-uploader :deep(.el-upload) {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: border-color 0.3s;
  width: 150px;
  height: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-uploader :deep(.el-upload:hover) {
  border-color: #409eff;
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
}

.avatar-preview {
  width: 150px;
  height: 150px;
  object-fit: cover;
}

:deep(.el-form-item__label) {
  font-weight: 500;
  color: #333;
}

:deep(.el-divider__text) {
  color: #666;
  font-weight: 500;
}
</style>