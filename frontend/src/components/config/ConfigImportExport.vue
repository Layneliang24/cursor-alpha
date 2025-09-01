<template>
  <div class="config-import-export">
    <el-card class="config-card">
      <template #header>
        <div class="card-header">
          <span>配置导入导出</span>
          <el-tag type="info">支持JSON/YAML格式</el-tag>
        </div>
      </template>

      <!-- 导出配置 -->
      <el-row :gutter="20" class="config-section">
        <el-col :span="12">
          <div class="export-section">
            <h3>导出配置</h3>
            <p class="section-desc">将当前AI服务配置导出为文件</p>
            
            <el-form :model="exportForm" label-width="100px">
              <el-form-item label="导出格式">
                <el-radio-group v-model="exportForm.format">
                  <el-radio label="json">JSON</el-radio>
                  <el-radio label="yaml">YAML</el-radio>
                </el-radio-group>
              </el-form-item>
              
              <el-form-item>
                <el-button 
                  type="primary" 
                  @click="exportConfig"
                  :loading="exportLoading"
                  icon="Download"
                >
                  导出配置
                </el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-col>

        <!-- 导入配置 -->
        <el-col :span="12">
          <div class="import-section">
            <h3>导入配置</h3>
            <p class="section-desc">从文件导入AI服务配置</p>
            
            <el-form :model="importForm" label-width="100px">
              <el-form-item label="配置文件">
                <el-upload
                  ref="uploadRef"
                  :auto-upload="false"
                  :on-change="handleFileChange"
                  :before-upload="beforeFileUpload"
                  accept=".json,.yaml,.yml"
                  :limit="1"
                  :file-list="fileList"
                >
                  <el-button type="primary" icon="Upload">选择文件</el-button>
                  <template #tip>
                    <div class="el-upload__tip">
                      支持JSON/YAML格式，文件大小不超过10MB
                    </div>
                  </template>
                </el-upload>
              </el-form-item>
              
              <el-form-item label="导入选项">
                <el-checkbox v-model="importForm.validateOnly">仅验证配置</el-checkbox>
                <el-checkbox v-model="importForm.overwriteExisting">覆盖现有配置</el-checkbox>
              </el-form-item>
              
              <el-form-item>
                <el-button 
                  type="success" 
                  @click="importConfig"
                  :loading="importLoading"
                  :disabled="!selectedFile"
                  icon="Upload"
                >
                  导入配置
                </el-button>
                <el-button @click="validateConfig" :loading="validateLoading">
                  验证配置
                </el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-col>
      </el-row>

      <!-- 配置预览 -->
      <el-row v-if="configPreview" class="config-section">
        <el-col :span="24">
          <div class="preview-section">
            <h3>配置预览</h3>
            <el-tabs v-model="previewTab" type="border-card">
              <el-tab-pane label="基本信息" name="basic">
                <el-descriptions :column="2" border>
                  <el-descriptions-item label="配置版本">
                    {{ configPreview.version }}
                  </el-descriptions-item>
                  <el-descriptions-item label="导出时间">
                    {{ formatDateTime(configPreview.export_time) }}
                  </el-descriptions-item>
                  <el-descriptions-item label="提供商数量">
                    {{ configPreview.metadata?.total_providers || 0 }}
                  </el-descriptions-item>
                  <el-descriptions-item label="策略数量">
                    {{ configPreview.metadata?.total_strategies || 0 }}
                  </el-descriptions-item>
                </el-descriptions>
              </el-tab-pane>
              
              <el-tab-pane label="提供商配置" name="providers">
                <el-table :data="configPreview.providers || []" border>
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
                <el-table :data="configPreview.strategies || []" border>
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
                    v-for="(value, key) in configPreview.settings" 
                    :key="key"
                    :label="key"
                  >
                    {{ value }}
                  </el-descriptions-item>
                </el-descriptions>
              </el-tab-pane>
            </el-tabs>
          </div>
        </el-col>
      </el-row>

      <!-- 导入结果 -->
      <el-row v-if="importResult" class="config-section">
        <el-col :span="24">
          <div class="result-section">
            <h3>导入结果</h3>
            <el-alert
              :title="importResult.message"
              :type="importResult.success ? 'success' : 'error'"
              :closable="false"
              show-icon
            />
            
            <el-descriptions :column="2" border class="mt-3">
              <el-descriptions-item label="导入提供商">
                {{ importResult.import_result?.providers_imported || 0 }}
              </el-descriptions-item>
              <el-descriptions-item label="更新提供商">
                {{ importResult.import_result?.providers_updated || 0 }}
              </el-descriptions-item>
              <el-descriptions-item label="导入策略">
                {{ importResult.import_result?.strategies_imported || 0 }}
              </el-descriptions-item>
              <el-descriptions-item label="更新策略">
                {{ importResult.import_result?.strategies_updated || 0 }}
              </el-descriptions-item>
            </el-descriptions>
            
            <div v-if="importResult.import_result?.errors?.length" class="mt-3">
              <h4>错误信息</h4>
              <el-alert
                v-for="error in importResult.import_result.errors"
                :key="error"
                :title="error"
                type="warning"
                :closable="false"
                show-icon
                class="mb-2"
              />
            </div>
          </div>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Download, Upload } from '@element-plus/icons-vue'
import { configImportExportAPI } from '@/api/configImportExport'

// 响应式数据
const exportForm = reactive({
  format: 'json'
})

const importForm = reactive({
  validateOnly: false,
  overwriteExisting: false
})

const exportLoading = ref(false)
const importLoading = ref(false)
const validateLoading = ref(false)
const selectedFile = ref(null)
const fileList = ref([])
const configPreview = ref(null)
const importResult = ref(null)
const previewTab = ref('basic')

const uploadRef = ref()

// 导出配置
const exportConfig = async () => {
  try {
    exportLoading.value = true
    
    const response = await configImportExportAPI.exportConfig(exportForm.format)
    
    // 创建下载链接
    const blob = new Blob([response.data], {
      type: exportForm.format === 'json' ? 'application/json' : 'application/x-yaml'
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `ai_config_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.${exportForm.format}`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('配置导出成功')
  } catch (error) {
    console.error('导出配置失败:', error)
    ElMessage.error('导出配置失败: ' + (error.response?.data?.error || error.message))
  } finally {
    exportLoading.value = false
  }
}

// 文件选择处理
const handleFileChange = (file) => {
  selectedFile.value = file
  configPreview.value = null
  importResult.value = null
}

// 文件上传前验证
const beforeFileUpload = (file) => {
  const isValidFormat = /\.(json|yaml|yml)$/.test(file.name.toLowerCase())
  const isLt10M = file.size / 1024 / 1024 < 10

  if (!isValidFormat) {
    ElMessage.error('只能上传JSON/YAML格式的文件!')
    return false
  }
  if (!isLt10M) {
    ElMessage.error('文件大小不能超过10MB!')
    return false
  }
  return false // 阻止自动上传
}

// 验证配置
const validateConfig = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择配置文件')
    return
  }

  try {
    validateLoading.value = true
    
    const formData = new FormData()
    formData.append('file', selectedFile.value.raw)
    formData.append('validate_only', true)
    
    const response = await configImportExportAPI.validateConfig(formData)
    
    // 解析配置文件内容用于预览
    const fileContent = await readFileContent(selectedFile.value.raw)
    configPreview.value = fileContent
    
    ElMessage.success('配置验证通过')
  } catch (error) {
    console.error('配置验证失败:', error)
    ElMessage.error('配置验证失败: ' + (error.response?.data?.error || error.message))
  } finally {
    validateLoading.value = false
  }
}

// 导入配置
const importConfig = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择配置文件')
    return
  }

  try {
    await ElMessageBox.confirm(
      importForm.overwriteExisting 
        ? '确定要导入配置吗？这将覆盖现有配置。' 
        : '确定要导入配置吗？',
      '确认导入',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    importLoading.value = true
    
    const formData = new FormData()
    formData.append('file', selectedFile.value.raw)
    formData.append('validate_only', importForm.validateOnly)
    formData.append('overwrite_existing', importForm.overwriteExisting)
    
    const response = await configImportExportAPI.importConfig(formData)
    
    importResult.value = {
      success: true,
      message: response.data.message,
      import_result: response.data.import_result
    }
    
    ElMessage.success('配置导入成功')
    
    // 清空文件选择
    selectedFile.value = null
    fileList.value = []
    uploadRef.value?.clearFiles()
    
  } catch (error) {
    if (error === 'cancel') return
    
    console.error('导入配置失败:', error)
    importResult.value = {
      success: false,
      message: '导入配置失败: ' + (error.response?.data?.error || error.message)
    }
    ElMessage.error('导入配置失败: ' + (error.response?.data?.error || error.message))
  } finally {
    importLoading.value = false
  }
}

// 读取文件内容
const readFileContent = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        const content = e.target.result
        const isJson = file.name.toLowerCase().endsWith('.json')
        
        if (isJson) {
          resolve(JSON.parse(content))
        } else {
          // 对于YAML文件，这里简化处理，实际项目中可能需要引入yaml解析库
          resolve({})
        }
      } catch (error) {
        reject(error)
      }
    }
    reader.onerror = reject
    reader.readAsText(file)
  })
}

// 格式化日期时间
const formatDateTime = (dateTimeStr) => {
  if (!dateTimeStr) return ''
  return new Date(dateTimeStr).toLocaleString('zh-CN')
}
</script>

<style scoped>
.config-import-export {
  padding: 20px;
}

.config-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.config-section {
  margin-bottom: 30px;
}

.export-section,
.import-section {
  padding: 20px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  background-color: #fafafa;
}

.section-desc {
  color: #666;
  margin-bottom: 20px;
  font-size: 14px;
}

.preview-section,
.result-section {
  margin-top: 20px;
}

.mt-3 {
  margin-top: 15px;
}

.mb-2 {
  margin-bottom: 10px;
}

:deep(.el-upload__tip) {
  color: #909399;
  font-size: 12px;
  margin-top: 5px;
}

:deep(.el-descriptions__label) {
  font-weight: 600;
}

:deep(.el-table) {
  margin-top: 10px;
}
</style>
