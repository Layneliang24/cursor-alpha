<template>
  <div class="system-settings">
    <div class="settings-section">
      <h3 class="section-title">系统设置</h3>
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
          <el-button type="primary" @click="saveSystemSettings" :loading="saving">
            保存系统设置
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

const systemFormRef = ref()
const saving = ref(false)

const systemForm = reactive({
  auto_save: true,
  debug_mode: false,
  analytics_enabled: true
})

const loadSystemSettings = async () => {
  try {
    const response = await userSettingsAPI.getMySettings()
    const settings = response.data
    
    systemForm.auto_save = settings.auto_save !== false
    systemForm.debug_mode = settings.debug_mode || false
    systemForm.analytics_enabled = settings.analytics_enabled !== false
  } catch (error) {
    ElMessage.error('获取系统设置失败')
  }
}

const saveSystemSettings = async () => {
  try {
    saving.value = true
    
    await userSettingsAPI.updateMySettings({
      auto_save: systemForm.auto_save,
      debug_mode: systemForm.debug_mode,
      analytics_enabled: systemForm.analytics_enabled
    })
    
    ElMessage.success('系统设置保存成功')
  } catch (error) {
    ElMessage.error('保存系统设置失败')
  } finally {
    saving.value = false
  }
}

const resetForm = () => {
  loadSystemSettings()
}

onMounted(() => {
  loadSystemSettings()
})
</script>

<style scoped>
.system-settings {
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

.system-form {
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
</style>
