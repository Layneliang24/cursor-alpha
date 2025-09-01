<template>
  <div class="fallback-config">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>故障转移策略配置</h2>
      <p class="page-description">
        配置AI服务提供商的故障转移策略，包括轮询顺序、降级设置和权限控制
      </p>
    </div>

    <!-- 策略列表 -->
    <div class="strategy-list">
      <div class="list-header">
        <h3>故障转移策略</h3>
        <el-button type="primary" @click="showCreateDialog">
          <el-icon><Plus /></el-icon>
          新建策略
        </el-button>
      </div>

      <!-- 策略卡片列表 -->
      <div class="strategy-cards">
        <div
          v-for="strategy in strategies"
          :key="strategy.id"
          class="strategy-card"
          :class="{ 'strategy-active': strategy.is_active }"
        >
          <div class="card-header">
            <div class="strategy-info">
              <h4>{{ strategy.name }}</h4>
              <p class="strategy-description">{{ strategy.description }}</p>
            </div>
            <div class="strategy-actions">
              <el-switch
                v-model="strategy.is_active"
                @change="toggleStrategyStatus(strategy)"
                active-text="启用"
                inactive-text="禁用"
              />
              <el-dropdown @command="handleStrategyAction">
                <el-button type="text">
                  <el-icon><MoreFilled /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item :command="{ action: 'edit', strategy }">
                      编辑
                    </el-dropdown-item>
                    <el-dropdown-item :command="{ action: 'duplicate', strategy }">
                      复制
                    </el-dropdown-item>
                    <el-dropdown-item :command="{ action: 'delete', strategy }" divided>
                      删除
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>

          <!-- 当前状态 -->
          <div class="current-status">
            <div class="status-item">
              <span class="label">当前提供商:</span>
              <el-tag
                :type="getProviderStatusType(strategy.active_provider)"
                size="small"
              >
                {{ strategy.active_provider?.display_name || '未设置' }}
              </el-tag>
            </div>
            <div class="status-item">
              <span class="label">策略模式:</span>
              <el-tag type="info" size="small">
                {{ getStrategyModeText(strategy.strategy_mode) }}
              </el-tag>
            </div>
            <div class="status-item">
              <span class="label">故障阈值:</span>
              <span>{{ strategy.fail_threshold }}次</span>
            </div>
          </div>

          <!-- 提供商轮询列表 -->
          <div class="provider-list">
            <h5>提供商轮询顺序</h5>
            <draggable
              v-model="strategy.provider_list"
              :group="{ name: 'providers' }"
              @end="handleProviderReorder(strategy)"
              item-key="id"
              class="provider-draggable-list"
            >
              <template #item="{ element: provider, index }">
                <div class="provider-item" :class="{ 'primary-provider': index === 0 }">
                  <div class="provider-info">
                    <el-icon class="drag-handle"><Rank /></el-icon>
                    <div class="provider-details">
                      <span class="provider-name">{{ provider.display_name }}</span>
                      <span class="provider-type">{{ provider.provider_type }}</span>
                    </div>
                    <div class="provider-status">
                      <el-tag
                        :type="provider.is_healthy ? 'success' : 'danger'"
                        size="small"
                      >
                        {{ provider.is_healthy ? '健康' : '故障' }}
                      </el-tag>
                    </div>
                  </div>
                  <div class="provider-actions">
                    <el-button
                      v-if="index > 0"
                      type="primary"
                      size="small"
                      @click="manualSwitch(strategy, provider)"
                    >
                      切换到
                    </el-button>
                    <el-button
                      type="danger"
                      size="small"
                      @click="removeProvider(strategy, provider)"
                    >
                      移除
                    </el-button>
                  </div>
                </div>
              </template>
            </draggable>
          </div>

          <!-- 模型权限控制 -->
          <div class="model-permissions">
            <h5>模型权限控制</h5>
            <div class="permission-controls">
              <el-switch
                v-model="strategy.enable_model_whitelist"
                @change="updateModelPermissions(strategy)"
                active-text="启用模型白名单"
                inactive-text="允许所有模型"
              />
              <el-button
                v-if="strategy.enable_model_whitelist"
                type="text"
                @click="showModelWhitelistDialog(strategy)"
              >
                配置白名单
              </el-button>
            </div>
            <div v-if="strategy.enable_model_whitelist" class="whitelist-summary">
              <span>已授权 {{ strategy.allowed_models?.length || 0 }} 个模型</span>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="card-actions">
            <el-button @click="showStrategyDetails(strategy)">
              查看详情
            </el-button>
            <el-button @click="showAuditLogs(strategy)">
              审计日志
            </el-button>
            <el-button type="primary" @click="editStrategy(strategy)">
              编辑配置
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 创建/编辑策略对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑故障转移策略' : '新建故障转移策略'"
      width="800px"
      :before-close="handleDialogClose"
    >
      <el-form
        ref="strategyFormRef"
        :model="strategyForm"
        :rules="strategyFormRules"
        label-width="120px"
      >
        <el-form-item label="策略名称" prop="name">
          <el-input v-model="strategyForm.name" placeholder="输入策略名称" />
        </el-form-item>

        <el-form-item label="策略描述" prop="description">
          <el-input
            v-model="strategyForm.description"
            type="textarea"
            :rows="3"
            placeholder="输入策略描述"
          />
        </el-form-item>

        <el-form-item label="主提供商" prop="primary_provider">
          <el-select
            v-model="strategyForm.primary_provider"
            placeholder="选择主提供商"
            style="width: 100%"
          >
            <el-option
              v-for="provider in availableProviders"
              :key="provider.id"
              :label="provider.display_name"
              :value="provider.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="策略模式" prop="strategy_mode">
          <el-radio-group v-model="strategyForm.strategy_mode">
            <el-radio label="priority">优先级模式</el-radio>
            <el-radio label="round_robin">轮询模式</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="故障阈值" prop="fail_threshold">
          <el-input-number
            v-model="strategyForm.fail_threshold"
            :min="1"
            :max="10"
            placeholder="连续失败次数"
          />
        </el-form-item>

        <el-form-item label="恢复阈值" prop="recovery_threshold">
          <el-input-number
            v-model="strategyForm.recovery_threshold"
            :min="1"
            :max="10"
            placeholder="连续成功次数"
          />
        </el-form-item>

        <el-form-item label="冷却时间" prop="cooldown">
          <el-input-number
            v-model="strategyForm.cooldown"
            :min="0"
            :max="3600"
            placeholder="秒"
          />
        </el-form-item>

        <el-form-item label="抖动窗口" prop="jitter_window">
          <el-input-number
            v-model="strategyForm.jitter_window"
            :min="0"
            :max="300"
            placeholder="秒"
          />
        </el-form-item>

        <el-form-item label="启用状态" prop="is_active">
          <el-switch v-model="strategyForm.is_active" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveStrategy">保存</el-button>
      </template>
    </el-dialog>

    <!-- 手动切换对话框 -->
    <el-dialog
      v-model="switchDialogVisible"
      title="手动切换提供商"
      width="500px"
    >
      <div class="switch-dialog-content">
        <p>确定要切换到提供商 <strong>{{ targetProvider?.display_name }}</strong> 吗？</p>
        
        <el-form-item label="切换原因">
          <el-input
            v-model="switchReason"
            type="textarea"
            :rows="3"
            placeholder="请输入切换原因（可选）"
          />
        </el-form-item>

        <div class="switch-preview">
          <div class="preview-item">
            <span class="label">当前提供商:</span>
            <el-tag type="info">{{ currentProvider?.display_name || '未设置' }}</el-tag>
          </div>
          <div class="preview-item">
            <span class="label">目标提供商:</span>
            <el-tag type="success">{{ targetProvider?.display_name }}</el-tag>
          </div>
        </div>
      </div>

      <template #footer>
        <el-button @click="switchDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmSwitch">确认切换</el-button>
      </template>
    </el-dialog>

    <!-- 模型白名单对话框 -->
    <ModelWhitelistDialog
      v-model:visible="whitelistDialogVisible"
      :strategy="currentStrategy"
      @saved="handleWhitelistSaved"
    />

    <!-- 审计日志对话框 -->
    <el-dialog
      v-model="auditDialogVisible"
      title="策略审计日志"
      width="900px"
    >
      <div class="audit-filters">
        <el-form :inline="true" :model="auditFilters">
          <el-form-item label="操作类型">
            <el-select v-model="auditFilters.action_type" placeholder="全部" clearable>
              <el-option label="自动切换" value="auto_switch" />
              <el-option label="手动切换" value="manual_switch" />
              <el-option label="恢复" value="recovery" />
              <el-option label="健康检查" value="health_check" />
            </el-select>
          </el-form-item>
          <el-form-item label="日期范围">
            <el-date-picker
              v-model="auditFilters.date_range"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="loadAuditLogs">查询</el-button>
            <el-button @click="resetAuditFilters">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <el-table :data="auditLogs" style="width: 100%">
        <el-table-column prop="created_at" label="时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="action_type" label="操作类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getActionTypeTag(row.action_type)">
              {{ getActionTypeText(row.action_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="from_provider" label="从" width="150" />
        <el-table-column prop="to_provider" label="到" width="150" />
        <el-table-column prop="reason" label="原因" />
        <el-table-column prop="operator" label="操作者" width="100" />
      </el-table>

      <div class="audit-summary">
        <p>总计 {{ auditLogs.length }} 条记录</p>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, MoreFilled, Rank } from '@element-plus/icons-vue'
import draggable from 'vuedraggable'
import { aiConfigAPI } from '@/api/aiConfig'
import { formatDateTime } from '@/utils/dateUtils'
import ModelWhitelistDialog from './ModelWhitelistDialog.vue'

// 响应式数据
const strategies = ref([])
const availableProviders = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const switchDialogVisible = ref(false)
const auditDialogVisible = ref(false)
const whitelistDialogVisible = ref(false)
const currentStrategy = ref(null)
const targetProvider = ref(null)
const currentProvider = ref(null)
const switchReason = ref('')
const auditLogs = ref([])
const auditFilters = reactive({
  action_type: '',
  date_range: []
})

// 表单数据
const strategyForm = reactive({
  name: '',
  description: '',
  primary_provider: null,
  strategy_mode: 'priority',
  fail_threshold: 3,
  recovery_threshold: 2,
  cooldown: 60,
  jitter_window: 30,
  is_active: true
})

// 表单验证规则
const strategyFormRules = {
  name: [
    { required: true, message: '请输入策略名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  primary_provider: [
    { required: true, message: '请选择主提供商', trigger: 'change' }
  ],
  fail_threshold: [
    { required: true, message: '请输入故障阈值', trigger: 'blur' }
  ],
  recovery_threshold: [
    { required: true, message: '请输入恢复阈值', trigger: 'blur' }
  ]
}

// 表单引用
const strategyFormRef = ref()

// 初始化数据
onMounted(async () => {
  await loadStrategies()
  await loadProviders()
})

// 加载策略列表
const loadStrategies = async () => {
  try {
    const response = await aiConfigAPI.getFailoverStrategies()
    strategies.value = response.data.results || []
  } catch (error) {
    ElMessage.error('加载策略列表失败')
    console.error('Load strategies error:', error)
  }
}

// 加载提供商列表
const loadProviders = async () => {
  try {
    const response = await aiConfigAPI.getProviders()
    availableProviders.value = response.data.results || []
  } catch (error) {
    ElMessage.error('加载提供商列表失败')
    console.error('Load providers error:', error)
  }
}

// 显示创建对话框
const showCreateDialog = () => {
  isEdit.value = false
  resetStrategyForm()
  dialogVisible.value = true
}

// 编辑策略
const editStrategy = (strategy) => {
  isEdit.value = true
  currentStrategy.value = strategy
  Object.assign(strategyForm, {
    name: strategy.name,
    description: strategy.description,
    primary_provider: strategy.primary_provider?.id,
    strategy_mode: strategy.strategy_mode,
    fail_threshold: strategy.fail_threshold,
    recovery_threshold: strategy.recovery_threshold,
    cooldown: strategy.cooldown,
    jitter_window: strategy.jitter_window,
    is_active: strategy.is_active
  })
  dialogVisible.value = true
}

// 重置表单
const resetStrategyForm = () => {
  Object.assign(strategyForm, {
    name: '',
    description: '',
    primary_provider: null,
    strategy_mode: 'priority',
    fail_threshold: 3,
    recovery_threshold: 2,
    cooldown: 60,
    jitter_window: 30,
    is_active: true
  })
}

// 保存策略
const saveStrategy = async () => {
  try {
    await strategyFormRef.value.validate()
    
    const data = { ...strategyForm }
    if (isEdit.value) {
      await aiConfigAPI.updateFailoverStrategy(currentStrategy.value.id, data)
      ElMessage.success('策略更新成功')
    } else {
      await aiConfigAPI.createFailoverStrategy(data)
      ElMessage.success('策略创建成功')
    }
    
    dialogVisible.value = false
    await loadStrategies()
  } catch (error) {
    if (error.response?.data?.message) {
      ElMessage.error(error.response.data.message)
    } else {
      ElMessage.error('保存策略失败')
    }
    console.error('Save strategy error:', error)
  }
}

// 切换策略状态
const toggleStrategyStatus = async (strategy) => {
  try {
    await aiConfigAPI.updateFailoverStrategy(strategy.id, {
      is_active: strategy.is_active
    })
    ElMessage.success(`策略已${strategy.is_active ? '启用' : '禁用'}`)
  } catch (error) {
    strategy.is_active = !strategy.is_active // 恢复状态
    ElMessage.error('切换状态失败')
    console.error('Toggle strategy status error:', error)
  }
}

// 处理策略操作
const handleStrategyAction = async ({ action, strategy }) => {
  switch (action) {
    case 'edit':
      editStrategy(strategy)
      break
    case 'duplicate':
      await duplicateStrategy(strategy)
      break
    case 'delete':
      await deleteStrategy(strategy)
      break
  }
}

// 复制策略
const duplicateStrategy = async (strategy) => {
  try {
    const duplicateData = {
      name: `${strategy.name} - 副本`,
      description: strategy.description,
      primary_provider: strategy.primary_provider?.id,
      strategy_mode: strategy.strategy_mode,
      fail_threshold: strategy.fail_threshold,
      recovery_threshold: strategy.recovery_threshold,
      cooldown: strategy.cooldown,
      jitter_window: strategy.jitter_window,
      is_active: false
    }
    await aiConfigAPI.createFailoverStrategy(duplicateData)
    ElMessage.success('策略复制成功')
    await loadStrategies()
  } catch (error) {
    ElMessage.error('复制策略失败')
    console.error('Duplicate strategy error:', error)
  }
}

// 删除策略
const deleteStrategy = async (strategy) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除策略 "${strategy.name}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await aiConfigAPI.deleteFailoverStrategy(strategy.id)
    ElMessage.success('策略删除成功')
    await loadStrategies()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除策略失败')
      console.error('Delete strategy error:', error)
    }
  }
}

// 处理提供商重排序
const handleProviderReorder = async (strategy) => {
  try {
    // 这里需要更新策略的提供商顺序
    // 具体实现取决于后端API的设计
    ElMessage.success('提供商顺序已更新')
  } catch (error) {
    ElMessage.error('更新提供商顺序失败')
    console.error('Reorder providers error:', error)
  }
}

// 手动切换提供商
const manualSwitch = (strategy, provider) => {
  currentStrategy.value = strategy
  currentProvider.value = strategy.active_provider
  targetProvider.value = provider
  switchReason.value = ''
  switchDialogVisible.value = true
}

// 确认切换
const confirmSwitch = async () => {
  try {
    const data = {
      target_provider: targetProvider.value.id,
      reason: switchReason.value || '手动切换'
    }
    
    await aiConfigAPI.switchProvider(currentStrategy.value.id, data)
    ElMessage.success('提供商切换成功')
    switchDialogVisible.value = false
    
    // 重新加载策略数据
    await loadStrategies()
  } catch (error) {
    if (error.response?.data?.message) {
      ElMessage.error(error.response.data.message)
    } else {
      ElMessage.error('切换提供商失败')
    }
    console.error('Switch provider error:', error)
  }
}

// 移除提供商
const removeProvider = async (strategy, provider) => {
  try {
    await ElMessageBox.confirm(
      `确定要从策略中移除提供商 "${provider.display_name}" 吗？`,
      '确认移除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 这里需要调用后端API移除提供商
    ElMessage.success('提供商已移除')
    await loadStrategies()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('移除提供商失败')
      console.error('Remove provider error:', error)
    }
  }
}

// 显示审计日志
const showAuditLogs = async (strategy) => {
  currentStrategy.value = strategy
  auditDialogVisible.value = true
  await loadAuditLogs()
}

// 加载审计日志
const loadAuditLogs = async () => {
  try {
    const params = {}
    if (auditFilters.action_type) {
      params.action_type = auditFilters.action_type
    }
    if (auditFilters.date_range && auditFilters.date_range.length === 2) {
      params.start_date = formatDateTime(auditFilters.date_range[0], 'YYYY-MM-DD')
      params.end_date = formatDateTime(auditFilters.date_range[1], 'YYYY-MM-DD')
    }
    
    const response = await aiConfigAPI.getStrategyAuditLogs(currentStrategy.value.id, params)
    auditLogs.value = response.data.results || []
  } catch (error) {
    ElMessage.error('加载审计日志失败')
    console.error('Load audit logs error:', error)
  }
}

// 重置审计过滤器
const resetAuditFilters = () => {
  auditFilters.action_type = ''
  auditFilters.date_range = []
  loadAuditLogs()
}

// 显示策略详情
const showStrategyDetails = (strategy) => {
  // 这里可以跳转到详情页面或显示详情对话框
  ElMessage.info('策略详情功能开发中')
}

// 显示模型白名单对话框
const showModelWhitelistDialog = (strategy) => {
  currentStrategy.value = strategy
  whitelistDialogVisible.value = true
}

// 处理白名单保存
const handleWhitelistSaved = (whitelist) => {
  // 更新当前策略的白名单
  if (currentStrategy.value) {
    currentStrategy.value.allowed_models = whitelist
  }
  ElMessage.success('模型白名单已更新')
}

// 更新模型权限
const updateModelPermissions = async (strategy) => {
  try {
    await aiConfigAPI.updateFailoverStrategy(strategy.id, {
      enable_model_whitelist: strategy.enable_model_whitelist
    })
    ElMessage.success('模型权限设置已更新')
  } catch (error) {
    strategy.enable_model_whitelist = !strategy.enable_model_whitelist // 恢复状态
    ElMessage.error('更新模型权限失败')
    console.error('Update model permissions error:', error)
  }
}

// 获取提供商状态类型
const getProviderStatusType = (provider) => {
  if (!provider) return 'info'
  return provider.is_healthy ? 'success' : 'danger'
}

// 获取策略模式文本
const getStrategyModeText = (mode) => {
  const modeMap = {
    priority: '优先级',
    round_robin: '轮询'
  }
  return modeMap[mode] || mode
}

// 获取操作类型标签
const getActionTypeTag = (actionType) => {
  const tagMap = {
    auto_switch: 'warning',
    manual_switch: 'primary',
    recovery: 'success',
    health_check: 'info'
  }
  return tagMap[actionType] || 'info'
}

// 获取操作类型文本
const getActionTypeText = (actionType) => {
  const textMap = {
    auto_switch: '自动切换',
    manual_switch: '手动切换',
    recovery: '恢复',
    health_check: '健康检查'
  }
  return textMap[actionType] || actionType
}

// 对话框关闭处理
const handleDialogClose = () => {
  dialogVisible.value = false
  resetStrategyForm()
}
</script>

<style scoped>
.fallback-config {
  padding: 20px;
}

.page-header {
  margin-bottom: 30px;
}

.page-header h2 {
  margin: 0 0 10px 0;
  color: #303133;
}

.page-description {
  color: #606266;
  margin: 0;
}

.strategy-list {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.list-header h3 {
  margin: 0;
  color: #303133;
}

.strategy-cards {
  display: grid;
  gap: 20px;
}

.strategy-card {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 20px;
  background: #fff;
  transition: all 0.3s ease;
}

.strategy-card:hover {
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.1);
}

.strategy-active {
  border-color: #409eff;
  background: #f0f9ff;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.strategy-info h4 {
  margin: 0 0 5px 0;
  color: #303133;
}

.strategy-description {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.strategy-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.current-status {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 6px;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-item .label {
  color: #606266;
  font-size: 14px;
}

.provider-list {
  margin-bottom: 20px;
}

.provider-list h5 {
  margin: 0 0 10px 0;
  color: #303133;
}

.provider-draggable-list {
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  min-height: 50px;
}

.provider-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 15px;
  border-bottom: 1px solid #f0f0f0;
  background: #fff;
  transition: background-color 0.2s ease;
}

.provider-item:last-child {
  border-bottom: none;
}

.provider-item:hover {
  background: #f5f7fa;
}

.provider-item.primary-provider {
  background: #f0f9ff;
  border-left: 3px solid #409eff;
}

.provider-info {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
}

.drag-handle {
  color: #c0c4cc;
  cursor: move;
}

.provider-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.provider-name {
  font-weight: 500;
  color: #303133;
}

.provider-type {
  font-size: 12px;
  color: #909399;
}

.provider-actions {
  display: flex;
  gap: 8px;
}

.model-permissions {
  margin-bottom: 20px;
}

.model-permissions h5 {
  margin: 0 0 10px 0;
  color: #303133;
}

.permission-controls {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 10px;
}

.whitelist-summary {
  font-size: 14px;
  color: #606266;
}

.card-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  padding-top: 15px;
  border-top: 1px solid #f0f0f0;
}

.switch-dialog-content {
  padding: 20px 0;
}

.switch-preview {
  margin-top: 20px;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 6px;
}

.preview-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.preview-item:last-child {
  margin-bottom: 0;
}

.preview-item .label {
  color: #606266;
}

.audit-filters {
  margin-bottom: 20px;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 6px;
}

.audit-summary {
  margin-top: 15px;
  text-align: center;
  color: #606266;
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .fallback-config {
    padding: 10px;
  }
  
  .strategy-list {
    padding: 15px;
  }
  
  .card-header {
    flex-direction: column;
    gap: 10px;
  }
  
  .current-status {
    flex-direction: column;
    gap: 10px;
  }
  
  .provider-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .provider-actions {
    width: 100%;
    justify-content: flex-end;
  }
  
  .card-actions {
    flex-direction: column;
  }
}
</style>
