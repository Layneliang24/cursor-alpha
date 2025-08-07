<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <h2>用户登录</h2>
          <p>欢迎回到 Alpha 技术共享平台</p>
        </div>
      </template>
      
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
          </p>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const loginFormRef = ref()
const loading = ref(false)
const captchaCanvas = ref()
let captchaCode = ref('')

const loginForm = reactive({
  username: '',
  password: '',
  captcha: ''
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
    
    // 登录成功后跳转
    const redirectPath = route.query.redirect || '/'
    router.push(redirectPath)
    
  } catch (error) {
    console.error('登录失败:', error)
    if (error.response?.data?.error) {
      ElMessage.error(error.response.data.error)
    }
    refreshCaptcha()
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  generateCaptcha()
})
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 400px;
  margin: 20px;
}

.card-header {
  text-align: center;
}

.card-header h2 {
  margin: 0 0 10px 0;
  color: #333;
}

.card-header p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.login-footer {
  text-align: center;
  margin-top: 20px;
}

.login-footer p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.link {
  color: #409eff;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

:deep(.el-form-item__label) {
  font-weight: 500;
}

.captcha-container {
  display: flex;
  align-items: center;
}

.captcha-image {
  position: relative;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
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
</style>