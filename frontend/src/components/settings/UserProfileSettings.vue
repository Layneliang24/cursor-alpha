<template>
  <div class="user-profile-settings">
    <div class="settings-section">
      <h3 class="section-title">个人信息</h3>
      <el-form
        ref="profileFormRef"
        :model="profileForm"
        :rules="profileRules"
        label-width="120px"
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
              <el-input v-model="profileForm.email" type="email" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="显示名称" prop="display_name">
              <el-input v-model="profileForm.display_name" placeholder="请输入显示名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="头像URL" prop="avatar_url">
              <el-input v-model="profileForm.avatar_url" placeholder="请输入头像URL" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="个人简介" prop="bio">
          <el-input
            v-model="profileForm.bio"
            type="textarea"
            :rows="3"
            placeholder="请输入个人简介"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="saveProfile" :loading="saving">
            保存个人信息
          </el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="settings-section">
      <h3 class="section-title">密码修改</h3>
      <el-form
        ref="passwordFormRef"
        :model="passwordForm"
        :rules="passwordRules"
        label-width="120px"
        class="password-form"
      >
        <el-form-item label="当前密码" prop="old_password">
          <el-input
            v-model="passwordForm.old_password"
            type="password"
            placeholder="请输入当前密码"
            show-password
          />
        </el-form-item>

        <el-form-item label="新密码" prop="new_password">
          <el-input
            v-model="passwordForm.new_password"
            type="password"
            placeholder="请输入新密码"
            show-password
          />
        </el-form-item>

        <el-form-item label="确认密码" prop="confirm_password">
          <el-input
            v-model="passwordForm.confirm_password"
            type="password"
            placeholder="请再次输入新密码"
            show-password
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="changePassword" :loading="changingPassword">
            修改密码
          </el-button>
          <el-button @click="resetPasswordForm">重置</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { userProfileAPI } from '@/api/settings'

const profileFormRef = ref()
const passwordFormRef = ref()
const saving = ref(false)
const changingPassword = ref(false)

// 个人信息表单
const profileForm = reactive({
  username: '',
  email: '',
  display_name: '',
  avatar_url: '',
  bio: ''
})

// 密码修改表单
const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

// 表单验证规则
const profileRules = {
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  display_name: [
    { max: 100, message: '显示名称不能超过100个字符', trigger: 'blur' }
  ],
  avatar_url: [
    { type: 'url', message: '请输入正确的URL地址', trigger: 'blur' }
  ],
  bio: [
    { max: 500, message: '个人简介不能超过500个字符', trigger: 'blur' }
  ]
}

const passwordRules = {
  old_password: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 8, message: '密码长度不能少于8位', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== passwordForm.new_password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 获取用户资料
const loadUserProfile = async () => {
  try {
    const response = await userProfileAPI.getMyProfile()
    const { username, email, settings } = response.data
    
    profileForm.username = username
    profileForm.email = email
    if (settings) {
      profileForm.display_name = settings.display_name || ''
      profileForm.avatar_url = settings.avatar_url || ''
      profileForm.bio = settings.bio || ''
    }
  } catch (error) {
    ElMessage.error('获取用户资料失败')
  }
}

// 保存个人信息
const saveProfile = async () => {
  try {
    await profileFormRef.value.validate()
    saving.value = true
    
    await userProfileAPI.updateMyProfile({
      email: profileForm.email,
      settings: {
        display_name: profileForm.display_name,
        avatar_url: profileForm.avatar_url,
        bio: profileForm.bio
      }
    })
    
    ElMessage.success('个人信息保存成功')
  } catch (error) {
    if (error.response?.data?.message) {
      ElMessage.error(error.response.data.message)
    } else {
      ElMessage.error('保存个人信息失败')
    }
  } finally {
    saving.value = false
  }
}

// 修改密码
const changePassword = async () => {
  try {
    await passwordFormRef.value.validate()
    changingPassword.value = true
    
    await userProfileAPI.changePassword({
      old_password: passwordForm.old_password,
      new_password: passwordForm.new_password,
      confirm_password: passwordForm.confirm_password
    })
    
    ElMessage.success('密码修改成功')
    resetPasswordForm()
  } catch (error) {
    if (error.response?.data?.message) {
      ElMessage.error(error.response.data.message)
    } else {
      ElMessage.error('修改密码失败')
    }
  } finally {
    changingPassword.value = false
  }
}

// 重置个人信息表单
const resetForm = () => {
  profileFormRef.value?.resetFields()
  loadUserProfile()
}

// 重置密码表单
const resetPasswordForm = () => {
  passwordFormRef.value?.resetFields()
}

onMounted(() => {
  loadUserProfile()
})
</script>

<style scoped>
.user-profile-settings {
  max-width: 800px;
}

.settings-section {
  margin-bottom: 40px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid #409eff;
}

.profile-form,
.password-form {
  background: #fafafa;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.profile-form :deep(.el-form-item__label),
.password-form :deep(.el-form-item__label) {
  font-weight: 500;
  color: #606266;
}

.profile-form :deep(.el-input__wrapper),
.password-form :deep(.el-input__wrapper) {
  box-shadow: none;
  border: 1px solid #dcdfe6;
}

.profile-form :deep(.el-input__wrapper:hover),
.password-form :deep(.el-input__wrapper:hover) {
  border-color: #409eff;
}

.profile-form :deep(.el-textarea__inner),
.password-form :deep(.el-textarea__inner) {
  border: 1px solid #dcdfe6;
  box-shadow: none;
}

.profile-form :deep(.el-textarea__inner:hover),
.password-form :deep(.el-textarea__inner:hover) {
  border-color: #409eff;
}
</style>
