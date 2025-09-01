<template>
  <div class="settings-page">
    <el-page-header @back="goBack" title="返回">
      <template #content>
        <span class="page-title">系统设置</span>
      </template>
    </el-page-header>

    <div class="settings-content">
      <el-tabs v-model="activeTab" type="border-card" class="settings-tabs">
        <!-- 个人信息设置 -->
        <el-tab-pane label="个人信息" name="profile">
          <UserProfileSettings />
        </el-tab-pane>

        <!-- 偏好设置 -->
        <el-tab-pane label="偏好设置" name="preferences">
          <PreferenceSettings />
        </el-tab-pane>

        <!-- 安全设置 -->
        <el-tab-pane label="安全设置" name="security">
          <SecuritySettings />
        </el-tab-pane>

        <!-- 通知设置 -->
        <el-tab-pane label="通知设置" name="notifications">
          <NotificationSettings />
        </el-tab-pane>

        <!-- 系统设置 -->
        <el-tab-pane label="系统设置" name="system">
          <SystemSettings />
        </el-tab-pane>

        <!-- 登录历史 -->
        <el-tab-pane label="登录历史" name="login-history">
          <LoginHistory />
        </el-tab-pane>

        <!-- 设备管理 -->
        <el-tab-pane label="设备管理" name="devices">
          <DeviceManagement />
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import UserProfileSettings from '@/components/settings/UserProfileSettings.vue'
import PreferenceSettings from '@/components/settings/PreferenceSettings.vue'
import SecuritySettings from '@/components/settings/SecuritySettings.vue'
import NotificationSettings from '@/components/settings/NotificationSettings.vue'
import SystemSettings from '@/components/settings/SystemSettings.vue'
import LoginHistory from '@/components/settings/LoginHistory.vue'
import DeviceManagement from '@/components/settings/DeviceManagement.vue'

const router = useRouter()
const activeTab = ref('profile')

const goBack = () => {
  router.go(-1)
}
</script>

<style scoped>
.settings-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.settings-content {
  margin-top: 20px;
}

.settings-tabs {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.settings-tabs :deep(.el-tabs__header) {
  margin: 0;
  border-bottom: 1px solid #e4e7ed;
}

.settings-tabs :deep(.el-tabs__nav-wrap) {
  padding: 0 20px;
}

.settings-tabs :deep(.el-tabs__item) {
  height: 50px;
  line-height: 50px;
  font-size: 14px;
  color: #606266;
}

.settings-tabs :deep(.el-tabs__item.is-active) {
  color: #409eff;
  font-weight: 600;
}

.settings-tabs :deep(.el-tabs__content) {
  padding: 20px;
  min-height: 400px;
}
</style>
