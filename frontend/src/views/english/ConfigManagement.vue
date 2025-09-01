<template>
  <div class="config-management">
    <el-page-header @back="goBack" title="返回">
      <template #content>
        <span class="page-title">AI配置管理</span>
      </template>
    </el-page-header>

    <div class="config-content">
      <!-- 配置管理标签页 -->
      <el-tabs v-model="activeTab" type="border-card" class="config-tabs">
        <!-- 导入导出标签页 -->
        <el-tab-pane label="导入导出" name="import-export">
          <ConfigImportExport />
        </el-tab-pane>

        <!-- 模板管理标签页 -->
        <el-tab-pane label="模板管理" name="templates">
          <ConfigTemplateManager />
        </el-tab-pane>

        <!-- 版本管理标签页 -->
        <el-tab-pane label="版本历史" name="versions">
          <ConfigVersionManager />
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import ConfigImportExport from '@/components/config/ConfigImportExport.vue'
import ConfigTemplateManager from '@/components/config/ConfigTemplateManager.vue'
import ConfigVersionManager from '@/components/config/ConfigVersionManager.vue'

const router = useRouter()
const activeTab = ref('import-export')

const goBack = () => {
  router.go(-1)
}
</script>

<style scoped>
.config-management {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.config-content {
  margin-top: 20px;
}

.config-tabs {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

:deep(.el-tabs__header) {
  margin: 0;
  border-bottom: 1px solid #e4e7ed;
}

:deep(.el-tabs__content) {
  padding: 20px;
}

:deep(.el-tab-pane) {
  min-height: 400px;
}
</style>
