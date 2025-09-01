<template>
  <div class="preference-settings">
    <div class="settings-section">
      <h3 class="section-title">界面偏好</h3>
      <el-form
        ref="preferenceFormRef"
        :model="preferenceForm"
        :rules="preferenceRules"
        label-width="120px"
        class="preference-form"
      >
        <el-form-item label="主题模式" prop="theme">
          <el-radio-group v-model="preferenceForm.theme">
            <el-radio label="light">浅色主题</el-radio>
            <el-radio label="dark">深色主题</el-radio>
            <el-radio label="auto">跟随系统</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="语言设置" prop="language">
          <el-select v-model="preferenceForm.language" placeholder="请选择语言">
            <el-option label="中文" value="zh-CN" />
            <el-option label="English" value="en-US" />
          </el-select>
        </el-form-item>

        <el-form-item label="时区设置" prop="timezone">
          <el-select v-model="preferenceForm.timezone" placeholder="请选择时区">
            <el-option label="中国标准时间 (UTC+8)" value="Asia/Shanghai" />
            <el-option label="美国东部时间 (UTC-5)" value="America/New_York" />
            <el-option label="美国西部时间 (UTC-8)" value="America/Los_Angeles" />
            <el-option label="格林威治时间 (UTC+0)" value="UTC" />
            <el-option label="日本标准时间 (UTC+9)" value="Asia/Tokyo" />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="savePreferences" :loading="saving">
            保存偏好设置
          </el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="settings-section">
      <h3 class="section-title">系统偏好</h3>
      <el-form
        ref="systemFormRef"
        :model="systemForm"
        label-width="120px"
        class="system-form"
      >
        <el-form-item label="自动保存">
          <el-switch
            v-model="systemForm.auto_save"
            active-text="启用"
            inactive-text="禁用"
          />
          <div class="form-help">自动保存您的配置和设置</div>
        </el-form-item>

        <el-form-item label="调试模式">
          <el-switch
            v-model="systemForm.debug_mode"
            active-text="启用"
            inactive-text="禁用"
          />
          <div class="form-help">启用调试模式以获取详细的错误信息</div>
        </el-form-item>

        <el-form-item label="数据分析">
          <el-switch
            v-model="systemForm.analytics_enabled"
            active-text="启用"
            inactive-text="禁用"
          />
          <div class="form-help">允许收集匿名使用数据以改进产品</div>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="saveSystemPreferences" :loading="savingSystem">
            保存系统设置
          </el-button>
          <el-button @click="resetSystemForm">重置</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { userSettingsAPI } from '@/api/settings'

const preferenceFormRef = ref()
const systemFormRef = ref()
const saving = ref(false)
const savingSystem = ref(false)

// 界面偏好表单
const preferenceForm = reactive({
  theme: 'auto',
  language: 'zh-CN',
  timezone: 'Asia/Shanghai'
})

// 系统偏好表单
const systemForm = reactive({
  auto_save: true,
  debug_mode: false,
  analytics_enabled: true
})

// 表单验证规则
const preferenceRules = {
  theme: [
    { required: true, message: '请选择主题模式', trigger: 'change' }
  ],
  language: [
    { required: true, message: '请选择语言', trigger: 'change' }
  ],
  timezone: [
    { required: true, message: '请选择时区', trigger: 'change' }
  ]
}

// 获取用户设置
const loadUserSettings = async () => {
  try {
    const response = await userSettingsAPI.getMySettings()
    const settings = response.data
    
    // 更新界面偏好
    preferenceForm.theme = settings.theme || 'auto'
    preferenceForm.language = settings.language || 'zh-CN'
    preferenceForm.timezone = settings.timezone || 'Asia/Shanghai'
    
    // 更新系统偏好
    systemForm.auto_save = settings.auto_save !== false
    systemForm.debug_mode = settings.debug_mode || false
    systemForm.analytics_enabled = settings.analytics_enabled !== false
  } catch (error) {
    ElMessage.error('获取用户设置失败')
  }
}

// 保存界面偏好
const savePreferences = async () => {
  try {
    await preferenceFormRef.value.validate()
    saving.value = true
    
    await userSettingsAPI.updateMySettings({
      theme: preferenceForm.theme,
      language: preferenceForm.language,
      timezone: preferenceForm.timezone
    })
    
    ElMessage.success('界面偏好保存成功')
    
    // 应用主题设置
    applyTheme(preferenceForm.theme)
  } catch (error) {
    if (error.response?.data?.message) {
      ElMessage.error(error.response.data.message)
    } else {
      ElMessage.error('保存界面偏好失败')
    }
  } finally {
    saving.value = false
  }
}

// 保存系统偏好
const saveSystemPreferences = async () => {
  try {
    savingSystem.value = true
    
    await userSettingsAPI.updateMySettings({
      auto_save: systemForm.auto_save,
      debug_mode: systemForm.debug_mode,
      analytics_enabled: systemForm.analytics_enabled
    })
    
    ElMessage.success('系统设置保存成功')
  } catch (error) {
    if (error.response?.data?.message) {
      ElMessage.error(error.response.data.message)
    } else {
      ElMessage.error('保存系统设置失败')
    }
  } finally {
    savingSystem.value = false
  }
}

// 应用主题
const applyTheme = (theme) => {
  const html = document.documentElement
  const body = document.body
  
  // 移除现有主题类
  html.classList.remove('theme-light', 'theme-dark')
  body.classList.remove('theme-light', 'theme-dark')
  
  if (theme === 'auto') {
    // 检测系统主题
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    const themeClass = prefersDark ? 'theme-dark' : 'theme-light'
    html.classList.add(themeClass)
    body.classList.add(themeClass)
  } else {
    // 应用指定主题
    const themeClass = `theme-${theme}`
    html.classList.add(themeClass)
    body.classList.add(themeClass)
  }
}

// 重置界面偏好表单
const resetForm = () => {
  preferenceFormRef.value?.resetFields()
  loadUserSettings()
}

// 重置系统偏好表单
const resetSystemForm = () => {
  loadUserSettings()
}

onMounted(() => {
  loadUserSettings()
})
</script>

<style scoped>
.preference-settings {
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

.preference-form,
.system-form {
  background: #fafafa;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.preference-form :deep(.el-form-item__label),
.system-form :deep(.el-form-item__label) {
  font-weight: 500;
  color: #606266;
}

.form-help {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
  line-height: 1.4;
}

.preference-form :deep(.el-radio-group) {
  display: flex;
  gap: 20px;
}

.preference-form :deep(.el-select) {
  width: 100%;
}

.system-form :deep(.el-switch) {
  margin-right: 10px;
}
</style>
