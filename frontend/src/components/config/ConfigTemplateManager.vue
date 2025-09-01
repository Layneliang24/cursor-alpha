<template>
  <div class="config-template-manager">
    <el-card class="template-card">
      <template #header>
        <div class="card-header">
          <span>配置模板管理</span>
          <el-button type="primary" @click="showCreateDialog" icon="Plus">
            创建模板
          </el-button>
        </div>
      </template>

      <!-- 模板列表 -->
      <el-table :data="templates" border v-loading="loading">
        <el-table-column prop="name" label="模板名称" />
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column prop="tags" label="标签">
          <template #default="{ row }">
            <el-tag 
              v-for="tag in row.tags" 
              :key="tag" 
              size="small" 
              class="mr-1"
            >
              {{ tag }}
            </el-tag>
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
            <el-button size="small" @click="previewTemplate(row)" icon="View">
              预览
            </el-button>
            <el-button 
              size="small" 
              type="success" 
              @click="applyTemplate(row)"
              :loading="applyingTemplate === row.id"
              icon="Check"
            >
              应用
            </el-button>
            <el-button 
              size="small" 
              type="danger" 
              @click="deleteTemplate(row)"
              icon="Delete"
            >
              删除
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

    <!-- 创建/编辑模板对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      @close="resetForm"
    >
      <el-form :model="templateForm" :rules="templateRules" ref="templateFormRef" label-width="100px">
        <el-form-item label="模板名称" prop="name">
          <el-input v-model="templateForm.name" placeholder="请输入模板名称" />
        </el-form-item>
        
        <el-form-item label="描述" prop="description">
          <el-input 
            v-model="templateForm.description" 
            type="textarea" 
            :rows="3"
            placeholder="请输入模板描述"
          />
        </el-form-item>
        
        <el-form-item label="标签" prop="tags">
          <el-select
            v-model="templateForm.tags"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="请选择或输入标签"
          >
            <el-option
              v-for="tag in availableTags"
              :key="tag"
              :label="tag"
              :value="tag"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="配置数据" prop="config_data">
          <el-input
            v-model="templateForm.config_data"
            type="textarea"
            :rows="10"
            placeholder="请输入JSON格式的配置数据"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveTemplate" :loading="saving">
            保存
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 模板预览对话框 -->
    <el-dialog
      v-model="previewVisible"
      title="模板预览"
      width="800px"
    >
      <div v-if="previewData">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="模板名称">
            {{ previewData.name }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDateTime(previewData.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="描述">
            {{ previewData.description }}
          </el-descriptions-item>
          <el-descriptions-item label="标签">
            <el-tag 
              v-for="tag in previewData.tags" 
              :key="tag" 
              size="small" 
              class="mr-1"
            >
              {{ tag }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
        
        <div class="mt-3">
          <h4>配置内容</h4>
          <el-tabs v-model="previewTab" type="border-card">
            <el-tab-pane label="JSON格式" name="json">
              <pre class="json-preview">{{ formatJson(previewData.config_data) }}</pre>
            </el-tab-pane>
            <el-tab-pane label="结构化视图" name="structured">
              <el-descriptions :column="2" border>
                <el-descriptions-item label="提供商数量">
                  {{ previewData.config_data?.providers?.length || 0 }}
                </el-descriptions-item>
                <el-descriptions-item label="策略数量">
                  {{ previewData.config_data?.strategies?.length || 0 }}
                </el-descriptions-item>
                <el-descriptions-item label="版本">
                  {{ previewData.config_data?.version || 'unknown' }}
                </el-descriptions-item>
              </el-descriptions>
            </el-tab-pane>
          </el-tabs>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, View, Check, Delete } from '@element-plus/icons-vue'
import { configImportExportAPI } from '@/api/configImportExport'

// 响应式数据
const loading = ref(false)
const templates = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const dialogVisible = ref(false)
const dialogTitle = ref('创建模板')
const saving = ref(false)
const applyingTemplate = ref(null)
const previewVisible = ref(false)
const previewData = ref(null)
const previewTab = ref('json')

const templateFormRef = ref()

const templateForm = reactive({
  name: '',
  description: '',
  tags: [],
  config_data: ''
})

const templateRules = {
  name: [
    { required: true, message: '请输入模板名称', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入模板描述', trigger: 'blur' }
  ],
  config_data: [
    { required: true, message: '请输入配置数据', trigger: 'blur' },
    { validator: validateJson, trigger: 'blur' }
  ]
}

const availableTags = ref([
  '生产环境', '测试环境', '开发环境', '高可用', '性能优化', '安全配置'
])

// 获取模板列表
const fetchTemplates = async () => {
  try {
    loading.value = true
    const response = await configImportExportAPI.getTemplates({
      page: currentPage.value,
      page_size: pageSize.value
    })
    templates.value = response.data.results || response.data
    total.value = response.data.count || response.data.length
  } catch (error) {
    console.error('获取模板列表失败:', error)
    ElMessage.error('获取模板列表失败: ' + (error.response?.data?.error || error.message))
  } finally {
    loading.value = false
  }
}

// 显示创建对话框
const showCreateDialog = () => {
  dialogTitle.value = '创建模板'
  dialogVisible.value = true
}

// 重置表单
const resetForm = () => {
  templateForm.name = ''
  templateForm.description = ''
  templateForm.tags = []
  templateForm.config_data = ''
  templateFormRef.value?.resetFields()
}

// 保存模板
const saveTemplate = async () => {
  try {
    await templateFormRef.value.validate()
    saving.value = true
    
    const data = {
      ...templateForm,
      config_data: JSON.parse(templateForm.config_data)
    }
    
    await configImportExportAPI.createTemplate(data)
    
    ElMessage.success('模板创建成功')
    dialogVisible.value = false
    fetchTemplates()
  } catch (error) {
    if (error.name === 'ValidationError') return
    
    console.error('保存模板失败:', error)
    ElMessage.error('保存模板失败: ' + (error.response?.data?.error || error.message))
  } finally {
    saving.value = false
  }
}

// 预览模板
const previewTemplate = (template) => {
  previewData.value = template
  previewVisible.value = true
}

// 应用模板
const applyTemplate = async (template) => {
  try {
    await ElMessageBox.confirm(
      `确定要应用模板 "${template.name}" 吗？这将覆盖现有配置。`,
      '确认应用',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    applyingTemplate.value = template.id
    
    const response = await configImportExportAPI.applyTemplate(template.id)
    
    ElMessage.success('模板应用成功')
  } catch (error) {
    if (error === 'cancel') return
    
    console.error('应用模板失败:', error)
    ElMessage.error('应用模板失败: ' + (error.response?.data?.error || error.message))
  } finally {
    applyingTemplate.value = null
  }
}

// 删除模板
const deleteTemplate = async (template) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除模板 "${template.name}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await configImportExportAPI.deleteTemplate(template.id)
    
    ElMessage.success('模板删除成功')
    fetchTemplates()
  } catch (error) {
    if (error === 'cancel') return
    
    console.error('删除模板失败:', error)
    ElMessage.error('删除模板失败: ' + (error.response?.data?.error || error.message))
  }
}

// 分页处理
const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
  fetchTemplates()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchTemplates()
}

// JSON验证
function validateJson(rule, value, callback) {
  if (!value) {
    callback(new Error('请输入配置数据'))
    return
  }
  
  try {
    JSON.parse(value)
    callback()
  } catch (error) {
    callback(new Error('配置数据必须是有效的JSON格式'))
  }
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
  fetchTemplates()
})
</script>

<style scoped>
.config-template-manager {
  padding: 20px;
}

.template-card {
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

.mr-1 {
  margin-right: 5px;
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

:deep(.el-table) {
  margin-top: 10px;
}

:deep(.el-descriptions__label) {
  font-weight: 600;
}
</style>
