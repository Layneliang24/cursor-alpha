<template>
  <div class="password-reset-container">
    <AnimatedBackground />
    
    <div class="reset-content">
      <div class="reset-card">
        <div class="card-header">
          <h2>重置密码</h2>
          <p>请设置您的新密码</p>
        </div>

        <el-form
          ref="resetFormRef"
          :model="resetForm"
          :rules="resetRules"
          label-width="100px"
          @submit.prevent="handleReset"
        >
          <el-form-item label="新密码" prop="newPassword">
            <el-input
              v-model="resetForm.newPassword"
              type="password"
              placeholder="请输入新密码"
              prefix-icon="Lock"
              size="large"
              show-password
            />
          </el-form-item>
          
          <el-form-item label="确认密码" prop="confirmPassword">
            <el-input
              v-model="resetForm.confirmPassword"
              type="password"
              placeholder="请再次输入新密码"
              prefix-icon="Lock"
              size="large"
              show-password
              @keyup.enter="handleReset"
            />
          </el-form-item>
          
          <el-form-item>
            <el-button
              type="primary"
              size="large"
              :loading="loading"
              @click="handleReset"
              style="width: 100%"
            >
              {{ loading ? '重置中...' : '重置密码' }}
            </el-button>
          </el-form-item>
          
          <div class="reset-footer">
            <p>
              <router-link to="/login" class="link">返回登录</router-link>
            </p>
          </div>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import AnimatedBackground from '@/components/AnimatedBackground.vue'
import { authAPI } from '@/api/auth'

const router = useRouter()
const route = useRoute()

const resetFormRef = ref()
const loading = ref(false)

const resetForm = reactive({
  newPassword: '',
  confirmPassword: ''
})

const resetRules = {
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, max: 128, message: '密码长度在 6 到 128 个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== resetForm.newPassword) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

const handleReset = async () => {
  if (!resetFormRef.value) return
  
  try {
    await resetFormRef.value.validate()
    
    loading.value = true
    
    const { uid, token } = route.params
    
    await authAPI.confirmPasswordReset({
      uid,
      token,
      new_password: resetForm.newPassword,
      confirm_password: resetForm.confirmPassword
    })
    
    ElMessage.success('密码重置成功！请使用新密码登录')
    router.push('/login')
    
  } catch (error) {
    console.error('重置密码失败:', error)
    
    let errorMessage = '重置失败，请重试'
    if (error.response?.data?.non_field_errors) {
      errorMessage = error.response.data.non_field_errors[0]
    } else if (error.response?.data?.error) {
      errorMessage = error.response.data.error
    } else if (error.message) {
      errorMessage = error.message
    }
    
    ElMessage.error(errorMessage)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  // 检查是否有必要的参数
  const { uid, token } = route.params
  if (!uid || !token) {
    ElMessage.error('重置链接无效')
    router.push('/login')
  }
})
</script>

<style scoped>
.password-reset-container {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.reset-content {
  position: relative;
  z-index: 2;
  padding: 2rem;
}

.reset-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 2.5rem;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  width: 100%;
  max-width: 400px;
}

.card-header {
  text-align: center;
  margin-bottom: 2rem;
}

.card-header h2 {
  font-size: 2rem;
  font-weight: 600;
  margin: 0 0 0.5rem 0;
  color: #333;
}

.card-header p {
  margin: 0;
  color: #666;
  font-size: 0.95rem;
}

:deep(.el-form-item) {
  margin-bottom: 1.5rem;
}

:deep(.el-form-item__label) {
  font-weight: 500;
  color: #333;
}

:deep(.el-input__wrapper) {
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  border: 1px solid #e4e7ed;
  transition: all 0.3s ease;
}

:deep(.el-input__wrapper:hover) {
  border-color: #c0c4cc;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

:deep(.el-input__wrapper.is-focus) {
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2);
}

:deep(.el-button--primary) {
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  padding: 12px 0;
  font-weight: 500;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
  transition: all 0.3s ease;
}

:deep(.el-button--primary:hover) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5);
}

.reset-footer {
  text-align: center;
  margin-top: 1.5rem;
}

.reset-footer p {
  margin: 0;
  color: #666;
  font-size: 0.9rem;
}

.link {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
}

.link:hover {
  text-decoration: underline;
}

@media (max-width: 768px) {
  .reset-content {
    padding: 1rem;
  }
  
  .card-header h2 {
    font-size: 1.5rem;
  }
}
</style>
