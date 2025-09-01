<template>
  <div class="config-version-manager">
    <el-card class="version-card">
      <template #header>
        <div class="card-header">
          <span>配置版本管理</span>
          <el-button type="primary" @click="exportCurrentConfig" icon="Download">
            导出当前配置
          </el-button>
        </div>
      </template>

      <!-- 版本列表 -->
      <el-table :data="versions" border v-loading="loading">
        <el-table-column prop="version_name" label="版本名称" />
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column prop="version_hash" label="版本哈希" width="120">
          <template #default="{ row }">
            <el-tooltip :content="row.version_hash" placement="top">
              <span class="hash-text">{{ row.version_hash.substring(0, 8) }}...</span>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="created_by" label="创建者" />
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" @click="previewVersion(row)" icon="View">
              预览
            </el-button>
            <el-button 
              size="small" 
              type="warning" 
              @click="rollbackVersion(row)"
              :loading="rollingBackVersion === row.id"
              icon="Refresh"
            >
              回滚
            </el-button>
            <el-button 
              size="small" 
              type="primary" 
              @click="downloadVersion(row)"
              icon="Download"
            >
              下载
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 版本预览对话框 -->
    <el-dialog
      v-model="previewVisible"
      title="版本预览"
      width="900px"
    >
      <div v-if="previewData">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="版本名称">
            {{ previewData.version_name }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDateTime(previewData.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="描述">
            {{ previewData.description }}
          </el-descriptions-item>
          <el-descriptions-item label="创建者">
            {{ previewData.created_by }}
          </el-descriptions-item>
          <el-descriptions-item label="版本哈希">
            {{ previewData.version_hash }}
          </el-descriptions-item>
        </el-descriptions>
        
        <div class="mt-3">
          <h4>配置内容</h4>
          <el-tabs v-model="previewTab" type="border-card">
            <el-tab-pane label="基本信息" name="basic">
              <el-descriptions :column="2" border>
                <el-descriptions-item label="配置版本">
                  {{ previewData.config_data?.version || 'unknown' }}
                </el-descriptions-item>
                <el-descriptions-item label="导出时间">
                  {{ formatDateTime(previewData.config_data?.export_time) }}
                </el-descriptions-item>
                <el-descriptions-item label="提供商数量">
                  {{ previewData.config_data?.metadata?.total_providers || 0 }}
                </el-descriptions-item>
                <el-descriptions-item label="策略数量">
                  {{ previewData.config_data?.metadata?.total_strategies || 0 }}
                </el-descriptions-item>
              </el-descriptions>
            </el-tab-pane>
            
            <el-tab-pane label="提供商配置" name="providers">
              <el-table :data="previewData.config_data?.providers || []" border>
                <el-table-column prop="name" label="名称" />
                <el-table-column prop="api_type" label="API类型" />
                <el-table-column prop="status" label="状态">
                  <template #default="{ row }">
                    <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
                      {{ row.status }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="is_healthy" label="健康状态">
                  <template #default="{ row }">
                    <el-tag :type="row.is_healthy ? 'success' : 'danger'">
                      {{ row.is_healthy ? '健康' : '异常' }}
                    </el-tag>
                  </template>
                </el-table-column>
              </el-table>
            </el-tab-pane>
            
            <el-tab-pane label="策略配置" name="strategies">
              <el-table :data="previewData.config_data?.strategies || []" border>
                <el-table-column prop="name" label="名称" />
                <el-table-column prop="priority" label="优先级" />
                <el-table-column prop="status" label="状态">
                  <template #default="{ row }">
                    <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
                      {{ row.status }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="description" label="描述" show-overflow-tooltip />
              </el-table>
            </el-tab-pane>
            
            <el-tab-pane label="系统设置" name="settings">
              <el-descriptions :column="2" border>
                <el-descriptions-item 
                  v-for="(value, key) in previewData.config_data?.settings" 
                  :key="key"
                  :label="key"
                >
                  {{ value }}
                </el-descriptions-item>
              </el-descriptions>
            </el-tab-pane>
            
            <el-tab-pane label="JSON格式" name="json">
              <pre class="json-preview">{{ formatJson(previewData.config_data) }}</pre>
            </el-tab-pane>
          </el-tabs>
        </div>
      </div>
    </el-dialog>

    <!-- 版本比较对话框 -->
    <el-dialog
      v-model="compareVisible"
      title="版本比较"
      width="1200px"
    >
      <div v-if="compareData">
        <el-row :gutter="20">
          <el-col :span="12">
            <h4>版本 A: {{ compareData.versionA?.version_name }}</h4>
            <el-descriptions :column="1" border>
              <el-descriptions-item label="创建时间">
                {{ formatDateTime(compareData.versionA?.created_at) }}
              </el-descriptions-item>
              <el-descriptions-item label="提供商数量">
                {{ compareData.versionA?.config_data?.metadata?.total_providers || 0 }}
              </el-descriptions-item>
              <el-descriptions-item label="策略数量">
                {{ compareData.versionA?.config_data?.metadata?.total_strategies || 0 }}
              </el-descriptions-item>
            </el-descriptions>
          </el-col>
          <el-col :span="12">
            <h4>版本 B: {{ compareData.versionB?.version_name }}</h4>
            <el-descriptions :column="1" border>
              <el-descriptions-item label="创建时间">
                {{ formatDateTime(compareData.versionB?.created_at) }}
              </el-descriptions-item>
              <el-descriptions-item label="提供商数量">
                {{ compareData.versionB?.config_data?.metadata?.total_providers || 0 }}
              </el-descriptions-item>
              <el-descriptions-item label="策略数量">
                {{ compareData.versionB?.config_data?.metadata?.total_strategies || 0 }}
              </el-descriptions-item>
            </el-descriptions>
          </el-col>
        </el-row>
        
        <div class="mt-3">
          <h4>差异对比</h4>
          <el-tabs v-model="compareTab" type="border-card">
            <el-tab-pane label="提供商差异" name="providers">
              <div class="diff-content">
                <pre>{{ compareData.diff?.providers || '无差异' }}</pre>
              </div>
            </el-tab-pane>
            <el-tab-pane label="策略差异" name="strategies">
              <div class="diff-content">
                <pre>{{ compareData.diff?.strategies || '无差异' }}</pre>
              </div>
            </el-tab-pane>
            <el-tab-pane label="设置差异" name="settings">
              <div class="diff-content">
                <pre>{{ compareData.diff?.settings || '无差异' }}</pre>
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Download, View, Refresh } from '@element-plus/icons-vue'
import { configImportExportAPI } from '@/api/configImportExport'

// 响应式数据
const loading = ref(false)
const versions = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const previewVisible = ref(false)
const previewData = ref(null)
const previewTab = ref('basic')
const rollingBackVersion = ref(null)
const compareVisible = ref(false)
const compareData = ref(null)
const compareTab = ref('providers')

// 获取版本列表
const fetchVersions = async () => {
  try {
    loading.value = true
    const response = await configImportExportAPI.getVersions({
      page: currentPage.value,
      page_size: pageSize.value
    })
    versions.value = response.data.results || response.data
    total.value = response.data.count || response.data.length
  } catch (error) {
    console.error('获取版本列表失败:', error)
    ElMessage.error('获取版本列表失败: ' + (error.response?.data?.error || error.message))
  } finally {
    loading.value = false
  }
}

// 导出当前配置
const exportCurrentConfig = async () => {
  try {
    const response = await configImportExportAPI.exportConfig('json')
    
    // 创建下载链接
    const blob = new Blob([response.data], { type: 'application/json' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `current_config_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('当前配置导出成功')
  } catch (error) {
    console.error('导出当前配置失败:', error)
    ElMessage.error('导出当前配置失败: ' + (error.response?.data?.error || error.message))
  }
}

// 预览版本
const previewVersion = async (version) => {
  try {
    const response = await configImportExportAPI.getVersion(version.id)
    previewData.value = response.data
    previewVisible.value = true
  } catch (error) {
    console.error('获取版本详情失败:', error)
    ElMessage.error('获取版本详情失败: ' + (error.response?.data?.error || error.message))
  }
}

// 回滚版本
const rollbackVersion = async (version) => {
  try {
    await ElMessageBox.confirm(
      `确定要回滚到版本 "${version.version_name}" 吗？这将覆盖当前配置。`,
      '确认回滚',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    rollingBackVersion.value = version.id
    
    const response = await configImportExportAPI.rollbackVersion(version.id)
    
    ElMessage.success('版本回滚成功')
  } catch (error) {
    if (error === 'cancel') return
    
    console.error('版本回滚失败:', error)
    ElMessage.error('版本回滚失败: ' + (error.response?.data?.error || error.message))
  } finally {
    rollingBackVersion.value = null
  }
}

// 下载版本
const downloadVersion = async (version) => {
  try {
    const configData = version.config_data
    const jsonContent = JSON.stringify(configData, null, 2)
    const blob = new Blob([jsonContent], { type: 'application/json' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${version.version_name}_${new Date(version.created_at).toISOString().slice(0, 19).replace(/:/g, '-')}.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('版本下载成功')
  } catch (error) {
    console.error('版本下载失败:', error)
    ElMessage.error('版本下载失败: ' + (error.response?.data?.error || error.message))
  }
}

// 分页处理
const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
  fetchVersions()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchVersions()
}

// 格式化JSON
const formatJson = (json) => {
  try {
    return JSON.stringify(json, null, 2)
  } catch {
    return json
  }
}

// 格式化日期时间
const formatDateTime = (dateTimeStr) => {
  if (!dateTimeStr) return ''
  return new Date(dateTimeStr).toLocaleString('zh-CN')
}

// 生命周期
onMounted(() => {
  fetchVersions()
})
</script>

<style scoped>
.config-version-manager {
  padding: 20px;
}

.version-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination-wrapper {
  margin-top: 20px;
  text-align: right;
}

.hash-text {
  font-family: 'Courier New', monospace;
  font-size: 12px;
  color: #666;
}

.mt-3 {
  margin-top: 15px;
}

.json-preview {
  background-color: #f5f5f5;
  padding: 15px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.5;
  max-height: 400px;
  overflow-y: auto;
}

.diff-content {
  background-color: #f5f5f5;
  padding: 15px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.5;
  max-height: 400px;
  overflow-y: auto;
}

:deep(.el-table) {
  margin-top: 10px;
}

:deep(.el-descriptions__label) {
  font-weight: 600;
}
</style>
