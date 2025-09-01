<template>
  <el-dialog
    :model-value="visible"
    @update:model-value="$emit('update:visible', $event)"
    title="模型白名单配置"
    width="800px"
    :before-close="handleClose"
  >
    <div class="whitelist-config">
      <!-- 搜索和过滤 -->
      <div class="search-section">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索模型名称或提供商"
          prefix-icon="Search"
          clearable
          @input="filterModels"
        />
        <el-select
          v-model="selectedProvider"
          placeholder="选择提供商"
          clearable
          @change="filterModels"
        >
          <el-option
            v-for="provider in providers"
            :key="provider.id"
            :label="provider.display_name"
            :value="provider.id"
          />
        </el-select>
      </div>

      <!-- 模型列表 -->
      <div class="models-section">
        <div class="section-header">
          <h4>可用模型 ({{ filteredModels.length }})</h4>
          <div class="header-actions">
            <el-button
              type="primary"
              size="small"
              @click="selectAllModels"
              :disabled="filteredModels.length === 0"
            >
              全选
            </el-button>
            <el-button
              size="small"
              @click="clearSelection"
              :disabled="selectedModels.length === 0"
            >
              清空
            </el-button>
          </div>
        </div>

        <div class="models-list">
          <el-checkbox-group v-model="selectedModels" @change="handleSelectionChange">
            <div
              v-for="model in filteredModels"
              :key="model.id"
              class="model-item"
            >
              <el-checkbox :label="model.id">
                <div class="model-info">
                  <div class="model-name">{{ model.model_id }}</div>
                  <div class="model-details">
                    <span class="provider-name">{{ model.provider?.display_name }}</span>
                    <span class="model-type">{{ model.model_type }}</span>
                    <span class="max-tokens">{{ model.max_tokens }} tokens</span>
                  </div>
                </div>
              </el-checkbox>
            </div>
          </el-checkbox-group>
        </div>
      </div>

      <!-- 已选模型 -->
      <div class="selected-section">
        <div class="section-header">
          <h4>已选模型 ({{ selectedModels.length }})</h4>
          <el-button
            type="danger"
            size="small"
            @click="clearSelection"
            :disabled="selectedModels.length === 0"
          >
            清空选择
          </el-button>
        </div>

        <div class="selected-models">
          <el-tag
            v-for="modelId in selectedModels"
            :key="modelId"
            closable
            @close="removeModel(modelId)"
            class="model-tag"
          >
            {{ getModelName(modelId) }}
          </el-tag>
        </div>
      </div>

      <!-- 批量操作 -->
      <div class="batch-actions">
        <el-button
          type="primary"
          @click="saveWhitelist"
          :loading="saving"
          :disabled="selectedModels.length === 0"
        >
          保存白名单
        </el-button>
        <el-button @click="handleClose">取消</el-button>
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { aiConfigAPI } from '@/api/aiConfig'

// Props
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  strategy: {
    type: Object,
    required: true
  }
})

// Emits
const emit = defineEmits(['update:visible', 'saved'])

// 响应式数据
const searchKeyword = ref('')
const selectedProvider = ref('')
const selectedModels = ref([])
const saving = ref(false)
const models = ref([])
const providers = ref([])
const filteredModels = ref([])

// 计算属性
const currentWhitelist = computed(() => {
  return props.strategy.allowed_models || []
})

// 监听器
watch(() => props.visible, (newVal) => {
  if (newVal) {
    loadData()
  }
})

watch(() => props.strategy, (newStrategy) => {
  if (newStrategy && props.visible) {
    selectedModels.value = [...(newStrategy.allowed_models || [])]
  }
}, { immediate: true })

// 初始化数据
onMounted(() => {
  if (props.visible) {
    loadData()
  }
})

// 加载数据
const loadData = async () => {
  try {
    await Promise.all([
      loadModels(),
      loadProviders()
    ])
    
    // 设置当前白名单
    selectedModels.value = [...currentWhitelist.value]
    filterModels()
  } catch (error) {
    ElMessage.error('加载数据失败')
    console.error('Load data error:', error)
  }
}

// 加载模型列表
const loadModels = async () => {
  try {
    const response = await aiConfigAPI.getModels()
    models.value = response.data.results || []
  } catch (error) {
    console.error('Load models error:', error)
    throw error
  }
}

// 加载提供商列表
const loadProviders = async () => {
  try {
    const response = await aiConfigAPI.getProviders()
    providers.value = response.data.results || []
  } catch (error) {
    console.error('Load providers error:', error)
    throw error
  }
}

// 过滤模型
const filterModels = () => {
  let filtered = [...models.value]
  
  // 按关键词过滤
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    filtered = filtered.filter(model => 
      model.model_id.toLowerCase().includes(keyword) ||
      model.provider?.display_name.toLowerCase().includes(keyword)
    )
  }
  
  // 按提供商过滤
  if (selectedProvider.value) {
    filtered = filtered.filter(model => 
      model.provider?.id === selectedProvider.value
    )
  }
  
  filteredModels.value = filtered
}

// 全选模型
const selectAllModels = () => {
  const modelIds = filteredModels.value.map(model => model.id)
  selectedModels.value = [...new Set([...selectedModels.value, ...modelIds])]
}

// 清空选择
const clearSelection = () => {
  selectedModels.value = []
}

// 移除单个模型
const removeModel = (modelId) => {
  selectedModels.value = selectedModels.value.filter(id => id !== modelId)
}

// 处理选择变化
const handleSelectionChange = (value) => {
  selectedModels.value = value
}

// 获取模型名称
const getModelName = (modelId) => {
  const model = models.value.find(m => m.id === modelId)
  return model ? model.model_id : modelId
}

// 保存白名单
const saveWhitelist = async () => {
  try {
    saving.value = true
    
    await aiConfigAPI.updateFailoverStrategy(props.strategy.id, {
      allowed_models: selectedModels.value
    })
    
    ElMessage.success('白名单保存成功')
    emit('saved', selectedModels.value)
    emit('update:visible', false)
  } catch (error) {
    if (error.response?.data?.message) {
      ElMessage.error(error.response.data.message)
    } else {
      ElMessage.error('保存白名单失败')
    }
    console.error('Save whitelist error:', error)
  } finally {
    saving.value = false
  }
}

// 关闭对话框
const handleClose = () => {
  emit('update:visible', false)
}
</script>

<style scoped>
.whitelist-config {
  padding: 20px 0;
}

.search-section {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
}

.search-section .el-input {
  flex: 1;
}

.search-section .el-select {
  width: 200px;
}

.models-section,
.selected-section {
  margin-bottom: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e4e7ed;
}

.section-header h4 {
  margin: 0;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.models-list {
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 10px;
}

.model-item {
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.model-item:last-child {
  border-bottom: none;
}

.model-info {
  margin-left: 8px;
}

.model-name {
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.model-details {
  display: flex;
  gap: 15px;
  font-size: 12px;
  color: #909399;
}

.provider-name {
  color: #409eff;
}

.model-type {
  text-transform: capitalize;
}

.max-tokens {
  color: #67c23a;
}

.selected-models {
  min-height: 60px;
  padding: 10px;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  background: #f5f7fa;
}

.model-tag {
  margin: 2px;
}

.batch-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding-top: 20px;
  border-top: 1px solid #e4e7ed;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .search-section {
    flex-direction: column;
  }
  
  .search-section .el-select {
    width: 100%;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .header-actions {
    width: 100%;
    justify-content: flex-end;
  }
  
  .batch-actions {
    flex-direction: column;
  }
}
</style>
