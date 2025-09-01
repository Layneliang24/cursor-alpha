<template>
  <div class="notification-settings">
    <div class="settings-section">
      <h3 class="section-title">通知设置</h3>
      <el-form
        ref="notificationFormRef"
        :model="notificationForm"
        label-width="120px"
        class="notification-form"
      >
        <el-form-item label="邮件通知">
          <el-switch
            v-model="notificationForm.email_notifications"
            active-text="启用"
            inactive-text="禁用"
          />
          <div class="form-help">接收邮件通知</div>
        </el-form-item>

        <el-form-item label="推送通知">
          <el-switch
            v-model="notificationForm.push_notifications"
            active-text="启用"
            inactive-text="禁用"
          />
          <div class="form-help">接收浏览器推送通知</div>
        </el-form-item>

        <el-form-item label="通知频率" prop="notification_frequency">
          <el-select v-model="notificationForm.notification_frequency">
            <el-option label="立即" value="immediate" />
            <el-option label="每日" value="daily" />
            <el-option label="每周" value="weekly" />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="saveNotificationSettings" :loading="saving">
            保存通知设置
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

const notificationFormRef = ref()
const saving = ref(false)

const notificationForm = reactive({
  email_notifications: true,
  push_notifications: true,
  notification_frequency: 'immediate'
})

const loadNotificationSettings = async () => {
  try {
    const response = await userSettingsAPI.getMySettings()
    const settings = response.data
    
    notificationForm.email_notifications = settings.email_notifications !== false
    notificationForm.push_notifications = settings.push_notifications !== false
    notificationForm.notification_frequency = settings.notification_frequency || 'immediate'
  } catch (error) {
    ElMessage.error('获取通知设置失败')
  }
}

const saveNotificationSettings = async () => {
  try {
    saving.value = true
    
    await userSettingsAPI.updateMySettings({
      email_notifications: notificationForm.email_notifications,
      push_notifications: notificationForm.push_notifications,
      notification_frequency: notificationForm.notification_frequency
    })
    
    ElMessage.success('通知设置保存成功')
  } catch (error) {
    ElMessage.error('保存通知设置失败')
  } finally {
    saving.value = false
  }
}

const resetForm = () => {
  loadNotificationSettings()
}

onMounted(() => {
  loadNotificationSettings()
})
</script>

<style scoped>
.notification-settings {
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

.notification-form {
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
