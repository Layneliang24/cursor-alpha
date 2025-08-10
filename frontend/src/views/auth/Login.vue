<template>
  <div class="login-container">
    <AnimatedBackground />
    
    <div class="login-content">
      <div class="login-left">
        <div class="welcome-text">
          <h1>Alpha</h1>
          <p>技术博客网站 - 测试CI/CD</p>
          <div class="features">
            <div class="feature-item">
              <el-icon><Document /></el-icon>
              <span>丰富的技术文章</span>
            </div>
            <div class="feature-item">
              <el-icon><User /></el-icon>
              <span>专业的技术社区</span>
            </div>
            <div class="feature-item">
              <el-icon><Star /></el-icon>
              <span>优质的学习体验</span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="login-right">
        <div class="login-card">
          <div class="card-header">
            <h2>欢迎回来</h2>
            <p>登录您的账户</p>
            
            <!-- 用户头像预览 -->
            <div v-if="verifiedUser" class="user-preview">
              <div class="user-avatar">
                <img :src="verifiedUser.avatar" :alt="verifiedUser.username" />
              </div>
              <div class="user-info">
                <h3>{{ verifiedUser.first_name || verifiedUser.username }}</h3>
                <p>@{{ verifiedUser.username }}</p>
              </div>
              <div class="verified-badge">
                <el-icon><Check /></el-icon>
              </div>
            </div>
          </div>
      
      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        label-width="80px"
        @submit.prevent="handleLogin"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名或邮箱"
            prefix-icon="User"
            size="large"
            @input="clearVerifiedUser"
          />
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            prefix-icon="Lock"
            size="large"
            show-password
            @blur="verifyIdentity"
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        
        <el-form-item label="验证码" prop="captcha">
          <div class="captcha-container">
            <el-input
              v-model="loginForm.captcha"
              placeholder="请输入验证码"
              prefix-icon="Key"
              size="large"
              style="flex: 1; margin-right: 10px;"
              @keyup.enter="handleLogin"
            />
            <div class="captcha-image" @click="refreshCaptcha">
              <canvas ref="captchaCanvas" width="120" height="40"></canvas>
              <div class="captcha-refresh">
                <i class="el-icon-refresh"></i>
              </div>
            </div>
          </div>
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            @click="handleLogin"
            style="width: 100%"
          >
            {{ loading ? '登录中...' : '登录' }}
          </el-button>
        </el-form-item>
        
        <div class="login-footer">
          <p>
            还没有账号？
            <router-link to="/register" class="link">立即注册</router-link>
            <span style="margin: 0 10px;">|</span>
            <a href="#" @click.prevent="showForgotPassword = true" class="link">忘记密码？</a>
          </p>
          <p style="margin-top: 8px;">
            管理员入口：
            <a
              href="http://127.0.0.1:8000/admin/"
              class="link"
              target="_blank"
              rel="noopener noreferrer"
              title="打开Django管理后台（需要管理员账号）"
            >打开 Django 后台</a>
          </p>
        </div>
          </el-form>
        </div>
      </div>
    </div>

    <!-- 忘记密码弹窗 -->
    <el-dialog
      v-model="showForgotPassword"
      title="找回密码"
      width="400px"
      :before-close="handleForgotPasswordClose"
    >
      <el-form
        ref="forgotPasswordFormRef"
        :model="forgotPasswordForm"
        :rules="forgotPasswordRules"
        label-width="80px"
      >
        <el-form-item label="邮箱" prop="email">
          <el-input
            v-model="forgotPasswordForm.email"
            placeholder="请输入注册邮箱"
            prefix-icon="Message"
            size="large"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showForgotPassword = false">取消</el-button>
          <el-button 
            type="primary" 
            :loading="forgotPasswordLoading"
            @click="handleForgotPassword"
          >
            {{ forgotPasswordLoading ? '发送中...' : '发送重置邮件' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
import { Document, User, Star, Check } from '@element-plus/icons-vue'
import AnimatedBackground from '@/components/AnimatedBackground.vue'
import { authAPI } from '@/api/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const loginFormRef = ref()
const loading = ref(false)
const captchaCanvas = ref()
let captchaCode = ref('')
const verifiedUser = ref(null)
const verifying = ref(false)

// 忘记密码相关
const showForgotPassword = ref(false)
const forgotPasswordFormRef = ref()
const forgotPasswordLoading = ref(false)

const loginForm = reactive({
  username: '',
  password: '',
  captcha: ''
})

const forgotPasswordForm = reactive({
  email: ''
})

const loginRules = {
  username: [
    { required: true, message: '请输入用户名或邮箱', trigger: 'blur' },
    { min: 2, max: 150, message: '用户名长度在 2 到 150 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 128, message: '密码长度在 6 到 128 个字符', trigger: 'blur' }
  ],
  captcha: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { len: 4, message: '验证码为4位字符', trigger: 'blur' }
  ]
}

const forgotPasswordRules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ]
}

// 生成验证码
const generateCaptcha = () => {
  const chars = 'ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678'
  let code = ''
  for (let i = 0; i < 4; i++) {
    code += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  captchaCode.value = code
  drawCaptcha(code)
}

// 绘制验证码
const drawCaptcha = (code) => {
  const canvas = captchaCanvas.value
  if (!canvas) return
  
  const ctx = canvas.getContext('2d')
  
  // 清空画布
  ctx.clearRect(0, 0, 120, 40)
  
  // 背景渐变
  const gradient = ctx.createLinearGradient(0, 0, 120, 40)
  gradient.addColorStop(0, '#f0f2f5')
  gradient.addColorStop(1, '#e6f7ff')
  ctx.fillStyle = gradient
  ctx.fillRect(0, 0, 120, 40)
  
  // 绘制干扰线
  for (let i = 0; i < 3; i++) {
    ctx.strokeStyle = `rgba(${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)}, 0.3)`
    ctx.beginPath()
    ctx.moveTo(Math.random() * 120, Math.random() * 40)
    ctx.lineTo(Math.random() * 120, Math.random() * 40)
    ctx.stroke()
  }
  
  // 绘制验证码文字
  ctx.font = 'bold 20px Arial'
  ctx.textBaseline = 'middle'
  
  for (let i = 0; i < code.length; i++) {
    const char = code[i]
    const x = 20 + i * 20
    const y = 20 + (Math.random() - 0.5) * 8
    const angle = (Math.random() - 0.5) * 0.4
    
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(angle)
    ctx.fillStyle = `hsl(${Math.floor(Math.random() * 360)}, 70%, 45%)`
    ctx.fillText(char, 0, 0)
    ctx.restore()
  }
  
  // 绘制干扰点
  for (let i = 0; i < 20; i++) {
    ctx.fillStyle = `rgba(${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)}, 0.4)`
    ctx.beginPath()
    ctx.arc(Math.random() * 120, Math.random() * 40, 1, 0, 2 * Math.PI)
    ctx.fill()
  }
}

// 刷新验证码
const refreshCaptcha = () => {
  generateCaptcha()
  loginForm.captcha = ''
}

// 验证用户身份
const verifyIdentity = async () => {
  console.log('=== 验证身份函数被调用 ===')
  console.log('用户名:', loginForm.username)
  console.log('密码长度:', loginForm.password ? loginForm.password.length : 0)
  console.log('是否正在验证:', verifying.value)
  
  // 只有当用户名和密码都不为空时才验证
  if (!loginForm.username || !loginForm.password || verifying.value) {
    console.log('跳过验证：缺少用户名或密码，或正在验证中')
    return
  }
  
  try {
    verifying.value = true
    console.log('开始验证用户身份...')
    
    const response = await authAPI.verifyUserIdentity({
      username: loginForm.username,
      password: loginForm.password
    })
    
    console.log('验证响应:', response)
    
    if (response.verified) {
      verifiedUser.value = response.user_info
      console.log('用户身份验证成功:', response.user_info)
      console.log('设置verifiedUser:', verifiedUser.value)
    } else {
      verifiedUser.value = null
      console.log('用户身份验证失败')
    }
  } catch (error) {
    console.error('身份验证出错:', error)
    console.error('错误状态码:', error.response?.status)
    console.error('错误详情:', error.response?.data)
    console.error('请求URL:', error.config?.url)
    
    if (error.response?.status === 401) {
      console.log('用户名或密码错误，这是正常的，不显示头像')
    }
    
    verifiedUser.value = null
  } finally {
    verifying.value = false
    console.log('验证完成，verifiedUser:', verifiedUser.value)
  }
}

// 监听用户名变化，清除已验证的用户信息
const clearVerifiedUser = () => {
  verifiedUser.value = null
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  try {
    await loginFormRef.value.validate()
    
    // 验证码校验
    if (loginForm.captcha.toLowerCase() !== captchaCode.value.toLowerCase()) {
      ElMessage.error('验证码错误')
      refreshCaptcha()
      return
    }
    
    loading.value = true
    
    await authStore.login({
      username: loginForm.username,
      password: loginForm.password
    })
    
    ElMessage.success('登录成功！')
    
    // 登录成功后跳转
    const redirectPath = route.query.redirect || '/'
    router.push(redirectPath)
    
  } catch (error) {
    console.error('登录失败:', error)
    console.error('错误详情:', error.response)
    
    let errorMessage = '登录失败，请重试'
    if (error.response?.data?.error) {
      errorMessage = error.response.data.error
    } else if (error.response?.data?.message) {
      errorMessage = error.response.data.message
    } else if (error.message) {
      errorMessage = error.message
    }
    
    ElMessage.error(errorMessage)
    refreshCaptcha()
  } finally {
    loading.value = false
  }
}

// 处理忘记密码
const handleForgotPassword = async () => {
  if (!forgotPasswordFormRef.value) return
  
  try {
    await forgotPasswordFormRef.value.validate()
    
    forgotPasswordLoading.value = true
    
    const result = await authAPI.requestPasswordReset(forgotPasswordForm.email)
    
    ElMessage.success('密码重置邮件已发送，请查收邮箱')
    showForgotPassword.value = false
    forgotPasswordForm.email = ''
    
  } catch (error) {
    console.error('发送重置邮件失败:', error)
    
    let errorMessage = '发送失败，请重试'
    if (error.response?.data?.email) {
      errorMessage = error.response.data.email[0]
    } else if (error.response?.data?.error) {
      errorMessage = error.response.data.error
    } else if (error.message) {
      errorMessage = error.message
    }
    
    ElMessage.error(errorMessage)
  } finally {
    forgotPasswordLoading.value = false
  }
}

// 关闭忘记密码弹窗
const handleForgotPasswordClose = () => {
  forgotPasswordForm.email = ''
  if (forgotPasswordFormRef.value) {
    forgotPasswordFormRef.value.clearValidate()
  }
}

onMounted(() => {
  generateCaptcha()
})
</script>

<style scoped>
.login-container {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
}

.login-content {
  position: relative;
  display: flex;
  min-height: 100vh;
  z-index: 2;
}

.login-left {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.welcome-text {
  color: white;
  text-align: center;
  max-width: 500px;
}

.welcome-text h1 {
  font-size: 4.2rem;
  font-weight: 800;
  margin: 0 0 1rem 0;
  background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 30%, #e8f0ff 70%, #ffffff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 0 0 30px rgba(255, 255, 255, 0.5);
  letter-spacing: -1px;
  position: relative;
  font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
}

.welcome-text h1::before {
  content: 'α';
  position: absolute;
  left: -60px;
  top: -10px;
  font-size: 2rem;
  opacity: 0.3;
  color: rgba(255, 255, 255, 0.6);
}

.welcome-text > p {
  font-size: 1.2rem;
  margin: 0.5rem 0 3rem 0;
  opacity: 0.85;
  font-weight: 300;
  letter-spacing: 3px;
  text-transform: uppercase;
  position: relative;
  color: rgba(255, 255, 255, 0.9);
}

.welcome-text > p::after {
  content: '';
  position: absolute;
  bottom: -15px;
  left: 50%;
  transform: translateX(-50%);
  width: 80px;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
}

.features {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  align-items: flex-start;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 1.1rem;
  opacity: 0.9;
}

.feature-item .el-icon {
  font-size: 1.5rem;
  color: rgba(255, 255, 255, 0.8);
}

.login-right {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.login-card {
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

.user-preview {
  margin-top: 1.5rem;
  padding: 1rem;
  background: linear-gradient(135deg, #f8f9ff 0%, #e8f0ff 100%);
  border-radius: 12px;
  border: 1px solid rgba(64, 158, 255, 0.1);
  position: relative;
  animation: fadeInUp 0.5s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.user-avatar {
  width: 60px;
  height: 60px;
  margin: 0 auto 0.8rem;
  position: relative;
}

.user-avatar img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #fff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.user-info {
  text-align: center;
}

.user-info h3 {
  margin: 0 0 0.3rem 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: #333;
}

.user-info p {
  margin: 0;
  font-size: 0.9rem;
  color: #666;
  opacity: 0.8;
}

.verified-badge {
  position: absolute;
  top: -8px;
  right: -8px;
  width: 24px;
  height: 24px;
  background: linear-gradient(135deg, #67c23a, #85ce61);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 12px;
  box-shadow: 0 2px 6px rgba(103, 194, 58, 0.3);
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

.login-footer {
  text-align: center;
  margin-top: 1.5rem;
}

.login-footer p {
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

.captcha-container {
  display: flex;
  align-items: center;
}

.captcha-image {
  position: relative;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  overflow: hidden;
}

.captcha-image:hover {
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

.captcha-image canvas {
  display: block;
}

.captcha-refresh {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
  color: white;
  font-size: 16px;
}

.captcha-image:hover .captcha-refresh {
  opacity: 1;
}

@media (max-width: 768px) {
  .login-content {
    flex-direction: column;
  }
  
  .login-left {
    padding: 1rem;
  }
  
  .welcome-text h1 {
    font-size: 2.5rem;
  }
  
  .login-right {
    width: 100%;
    padding: 1rem;
  }
}
</style>