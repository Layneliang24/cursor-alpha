<template>
  <div class="security-settings">
    <div class="settings-section">
      <h3 class="section-title">安全设置</h3>
      <el-form
        ref="securityFormRef"
        :model="securityForm"
        label-width="120px"
        class="security-form"
      >
        <el-form-item label="双因素认证">
          <el-switch
            v-model="securityForm.two_factor_enabled"
            active-text="启用"
            inactive-text="禁用"
          />
          <div class="form-help">启用双因素认证以提高账户安全性</div>
        </el-form-item>

        <el-form-item label="会话超时" prop="session_timeout">
          <el-input-number
            v-model="securityForm.session_timeout"
            :min="5"
            :max="1440"
            :step="5"
          />
          <span class="unit">分钟</span>
          <div class="form-help">设置会话超时时间，超过时间后需要重新登录</div>
        </el-form-item>

        <el-form-item label="登录通知">
          <el-switch
            v-model="securityForm.login_notifications"
            active-text="启用"
            inactive-text="禁用"
          />
          <div class="form-help">在新设备登录时发送通知</div>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="saveSecuritySettings" :loading="saving">
            保存安全设置
          </el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { userSettingsAPI } from '@/api/settings'

const securityFormRef = ref()
const saving = ref(false)

const securityForm = reactive({
  two_factor_enabled: false,
  session_timeout: 30,
  login_notifications: true
})

const loadSecuritySettings = async () => {
  try {
    const response = await userSettingsAPI.getMySettings()
    const settings = response.data
    
    securityForm.two_factor_enabled = settings.two_factor_enabled || false
    securityForm.session_timeout = settings.session_timeout || 30
    securityForm.login_notifications = settings.login_notifications !== false
  } catch (error) {
    ElMessage.error('获取安全设置失败')
  }
}

const saveSecuritySettings = async () => {
  try {
    saving.value = true
    
    await userSettingsAPI.updateMySettings({
      two_factor_enabled: securityForm.two_factor_enabled,
      session_timeout: securityForm.session_timeout,
      login_notifications: securityForm.login_notifications
    })
    
    ElMessage.success('安全设置保存成功')
  } catch (error) {
    ElMessage.error('保存安全设置失败')
  } finally {
    saving.value = false
  }
}

const resetForm = () => {
  loadSecuritySettings()
}

onMounted(() => {
  loadSecuritySettings()
})
</script>

<style scoped>
.security-settings {
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

.security-form {
  background: #fafafa;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.form-help {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
  line-height: 1.4;
}

.unit {
  margin-left: 10px;
  color: #606266;
}
</style>
