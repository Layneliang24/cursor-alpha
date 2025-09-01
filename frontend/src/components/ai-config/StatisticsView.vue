<template>
  <div class="statistics-view">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>AI服务统计分析</h2>
      <p class="page-description">
        查看Token消费趋势、使用明细和成本分析，设置预算和告警
      </p>
    </div>

    <!-- 时间范围选择器 -->
    <div class="time-range-selector">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>时间范围</span>
            <div class="header-actions">
              <el-button @click="refreshData" :loading="loading">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
          </div>
        </template>
        
        <el-form :inline="true" :model="timeRangeForm">
          <el-form-item label="时间范围">
            <el-select v-model="timeRangeForm.range" @change="handleTimeRangeChange">
              <el-option label="最近7天" value="7d" />
              <el-option label="最近30天" value="30d" />
              <el-option label="最近90天" value="90d" />
              <el-option label="自定义" value="custom" />
            </el-select>
          </el-form-item>
          
          <el-form-item v-if="timeRangeForm.range === 'custom'" label="开始日期">
            <el-date-picker
              v-model="timeRangeForm.startDate"
              type="date"
              placeholder="选择开始日期"
              @change="handleCustomDateChange"
            />
          </el-form-item>
          
          <el-form-item v-if="timeRangeForm.range === 'custom'" label="结束日期">
            <el-date-picker
              v-model="timeRangeForm.endDate"
              type="date"
              placeholder="选择结束日期"
              @change="handleCustomDateChange"
            />
          </el-form-item>
        </el-form>
      </el-card>
    </div>

    <!-- 统计概览卡片 -->
    <div class="statistics-overview">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="overview-card">
            <div class="overview-item">
              <div class="overview-icon total-consumption">
                <el-icon><TrendCharts /></el-icon>
              </div>
              <div class="overview-content">
                <div class="overview-value">{{ formatNumber(overview.totalConsumption) }}</div>
                <div class="overview-label">总消费 (Token)</div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card class="overview-card">
            <div class="overview-item">
              <div class="overview-icon total-cost">
                <el-icon><Money /></el-icon>
              </div>
              <div class="overview-content">
                <div class="overview-value">¥{{ formatNumber(overview.totalCost, 2) }}</div>
                <div class="overview-label">总成本</div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card class="overview-card">
            <div class="overview-item">
              <div class="overview-icon avg-daily">
                <el-icon><Calendar /></el-icon>
              </div>
              <div class="overview-content">
                <div class="overview-value">{{ formatNumber(overview.avgDailyConsumption) }}</div>
                <div class="overview-label">日均消费</div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card class="overview-card">
            <div class="overview-item">
              <div class="overview-icon budget-usage">
                <el-icon><PieChart /></el-icon>
              </div>
              <div class="overview-content">
                <div class="overview-value">{{ overview.budgetUsage }}%</div>
                <div class="overview-label">预算使用率</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 图表区域 -->
    <div class="charts-section">
      <el-row :gutter="20">
        <!-- 消费趋势图 -->
        <el-col :span="16">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>消费趋势</span>
                <el-radio-group v-model="trendChartType" size="small">
                  <el-radio-button label="tokens">Token数量</el-radio-button>
                  <el-radio-button label="cost">成本</el-radio-button>
                </el-radio-group>
              </div>
            </template>
            <div class="chart-container">
              <v-chart
                :option="trendChartOption"
                :loading="loading"
                style="height: 400px; width: 100%"
              />
            </div>
          </el-card>
        </el-col>
        
        <!-- 消费饼图 -->
        <el-col :span="8">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>消费分布</span>
                <el-select v-model="pieChartType" size="small" style="width: 120px">
                  <el-option label="按提供商" value="provider" />
                  <el-option label="按模型" value="model" />
                  <el-option label="按类型" value="type" />
                </el-select>
              </div>
            </template>
            <div class="chart-container">
              <v-chart
                :option="pieChartOption"
                :loading="loading"
                style="height: 400px; width: 100%"
              />
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 热力图 -->
    <div class="heatmap-section">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>消费热力图</span>
            <span class="subtitle">按小时和星期显示消费分布</span>
          </div>
        </template>
        <div class="chart-container">
          <v-chart
            :option="heatmapOption"
            :loading="loading"
            style="height: 300px; width: 100%"
          />
        </div>
      </el-card>
    </div>

    <!-- 详细数据表格 -->
    <div class="details-section">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>消费明细</span>
            <div class="header-actions">
              <el-button @click="exportData" :disabled="!detailsData.length">
                <el-icon><Download /></el-icon>
                导出
              </el-button>
            </div>
          </div>
        </template>
        
        <el-table
          :data="detailsData"
          style="width: 100%"
          :loading="loading"
          stripe
          border
        >
          <el-table-column prop="timestamp" label="时间" width="180">
            <template #default="{ row }">
              {{ formatDateTime(row.timestamp) }}
            </template>
          </el-table-column>
          <el-table-column prop="provider" label="提供商" width="120" />
          <el-table-column prop="model" label="模型" width="150" />
          <el-table-column prop="tokens_used" label="Token数量" width="120">
            <template #default="{ row }">
              {{ formatNumber(row.tokens_used) }}
            </template>
          </el-table-column>
          <el-table-column prop="cost" label="成本" width="120">
            <template #default="{ row }">
              ¥{{ formatNumber(row.cost, 4) }}
            </template>
          </el-table-column>
          <el-table-column prop="request_type" label="请求类型" width="100" />
          <el-table-column prop="status" label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="row.status === 'success' ? 'success' : 'danger'" size="small">
                {{ row.status === 'success' ? '成功' : '失败' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="user" label="用户" width="100" />
        </el-table>
        
        <div class="pagination-wrapper">
          <el-pagination
            v-model:current-page="pagination.currentPage"
            v-model:page-size="pagination.pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="pagination.total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handlePageSizeChange"
            @current-change="handleCurrentPageChange"
          />
        </div>
      </el-card>
    </div>

    <!-- 预算设置对话框 -->
    <el-dialog
      v-model="budgetDialogVisible"
      title="预算设置"
      width="600px"
    >
      <el-form
        ref="budgetFormRef"
        :model="budgetForm"
        :rules="budgetFormRules"
        label-width="120px"
      >
        <el-form-item label="月度预算" prop="monthly_budget">
          <el-input-number
            v-model="budgetForm.monthly_budget"
            :min="0"
            :precision="2"
            style="width: 100%"
            placeholder="设置月度预算金额"
          />
        </el-form-item>
        
        <el-form-item label="Token预算" prop="token_budget">
          <el-input-number
            v-model="budgetForm.token_budget"
            :min="0"
            style="width: 100%"
            placeholder="设置月度Token预算"
          />
        </el-form-item>
        
        <el-form-item label="告警阈值" prop="alert_threshold">
          <el-input-number
            v-model="budgetForm.alert_threshold"
            :min="0"
            :max="100"
            style="width: 100%"
            placeholder="预算使用率告警阈值（%）"
          />
        </el-form-item>
        
        <el-form-item label="启用预算控制" prop="enabled">
          <el-switch v-model="budgetForm.enabled" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="budgetDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveBudgetSettings" :loading="saving">
          保存
        </el-button>
      </template>
    </el-dialog>

    <!-- 告警配置对话框 -->
    <el-dialog
      v-model="alertDialogVisible"
      :title="isEditAlert ? '编辑告警配置' : '新建告警配置'"
      width="700px"
    >
      <el-form
        ref="alertFormRef"
        :model="alertForm"
        :rules="alertFormRules"
        label-width="120px"
      >
        <el-form-item label="告警名称" prop="name">
          <el-input v-model="alertForm.name" placeholder="输入告警名称" />
        </el-form-item>
        
        <el-form-item label="告警类型" prop="type">
          <el-select v-model="alertForm.type" placeholder="选择告警类型" style="width: 100%">
            <el-option label="预算超限" value="budget_exceeded" />
            <el-option label="消费异常" value="consumption_anomaly" />
            <el-option label="成本超限" value="cost_exceeded" />
            <el-option label="使用率告警" value="usage_rate" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="触发条件" prop="condition">
          <el-input-number
            v-model="alertForm.condition"
            :min="0"
            :precision="2"
            style="width: 100%"
            placeholder="设置触发条件值"
          />
        </el-form-item>
        
        <el-form-item label="通知方式" prop="notification_methods">
          <el-checkbox-group v-model="alertForm.notification_methods">
            <el-checkbox label="email">邮件</el-checkbox>
            <el-checkbox label="webhook">Webhook</el-checkbox>
            <el-checkbox label="sms">短信</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        
        <el-form-item label="通知邮箱" prop="email" v-if="alertForm.notification_methods.includes('email')">
          <el-input v-model="alertForm.email" placeholder="输入通知邮箱" />
        </el-form-item>
        
        <el-form-item label="Webhook URL" prop="webhook_url" v-if="alertForm.notification_methods.includes('webhook')">
          <el-input v-model="alertForm.webhook_url" placeholder="输入Webhook URL" />
        </el-form-item>
        
        <el-form-item label="启用状态" prop="enabled">
          <el-switch v-model="alertForm.enabled" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="alertDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveAlertConfig" :loading="saving">
          保存
        </el-button>
      </template>
    </el-dialog>

    <!-- 浮动操作按钮 -->
    <div class="floating-actions">
      <el-button
        type="primary"
        circle
        @click="showBudgetSettings"
        title="预算设置"
      >
        <el-icon><Setting /></el-icon>
      </el-button>
      <el-button
        type="success"
        circle
        @click="showAlertConfig"
        title="告警配置"
      >
        <el-icon><Bell /></el-icon>
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Refresh, TrendCharts, Money, Calendar, PieChart, 
  Download, Setting, Bell 
} from '@element-plus/icons-vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, PieChart as EChartsPieChart, HeatmapChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import { aiConfigAPI } from '@/api/aiConfig'
import { formatDateTime } from '@/utils/dateUtils'

// 注册ECharts组件
use([
  CanvasRenderer,
  LineChart,
  EChartsPieChart,
  HeatmapChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent
])

// 响应式数据
const loading = ref(false)
const saving = ref(false)
const budgetDialogVisible = ref(false)
const alertDialogVisible = ref(false)
const isEditAlert = ref(false)

// 时间范围表单
const timeRangeForm = reactive({
  range: '7d',
  startDate: null,
  endDate: null
})

// 图表类型
const trendChartType = ref('tokens')
const pieChartType = ref('provider')

// 分页
const pagination = reactive({
  currentPage: 1,
  pageSize: 20,
  total: 0
})

// 概览数据
const overview = reactive({
  totalConsumption: 0,
  totalCost: 0,
  avgDailyConsumption: 0,
  budgetUsage: 0
})

// 图表数据
const trendData = ref([])
const pieData = ref([])
const heatmapData = ref([])
const detailsData = ref([])

// 预算表单
const budgetForm = reactive({
  monthly_budget: 0,
  token_budget: 0,
  alert_threshold: 80,
  enabled: true
})

const budgetFormRules = {
  monthly_budget: [
    { required: true, message: '请输入月度预算', trigger: 'blur' }
  ],
  token_budget: [
    { required: true, message: '请输入Token预算', trigger: 'blur' }
  ],
  alert_threshold: [
    { required: true, message: '请输入告警阈值', trigger: 'blur' }
  ]
}

// 告警表单
const alertForm = reactive({
  name: '',
  type: '',
  condition: 0,
  notification_methods: [],
  email: '',
  webhook_url: '',
  enabled: true
})

const alertFormRules = {
  name: [
    { required: true, message: '请输入告警名称', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择告警类型', trigger: 'change' }
  ],
  condition: [
    { required: true, message: '请输入触发条件', trigger: 'blur' }
  ],
  notification_methods: [
    { required: true, message: '请选择通知方式', trigger: 'change' }
  ]
}

// 表单引用
const budgetFormRef = ref()
const alertFormRef = ref()

// 计算属性 - 趋势图配置
const trendChartOption = computed(() => ({
  title: {
    text: '消费趋势',
    left: 'center'
  },
  tooltip: {
    trigger: 'axis',
    formatter: (params) => {
      const data = params[0]
      if (trendChartType.value === 'tokens') {
        return `${data.name}<br/>${data.seriesName}: ${formatNumber(data.value)} tokens`
      } else {
        return `${data.name}<br/>${data.seriesName}: ¥${formatNumber(data.value, 2)}`
      }
    }
  },
  xAxis: {
    type: 'category',
    data: trendData.value.map(item => item.date)
  },
  yAxis: {
    type: 'value',
    name: trendChartType.value === 'tokens' ? 'Token数量' : '成本 (¥)'
  },
  series: [
    {
      name: trendChartType.value === 'tokens' ? 'Token消费' : '成本',
      type: 'line',
      data: trendData.value.map(item => 
        trendChartType.value === 'tokens' ? item.tokens : item.cost
      ),
      smooth: true,
      areaStyle: {
        opacity: 0.3
      }
    }
  ]
}))

// 计算属性 - 饼图配置
const pieChartOption = computed(() => ({
  title: {
    text: '消费分布',
    left: 'center'
  },
  tooltip: {
    trigger: 'item',
    formatter: '{a} <br/>{b}: {c} ({d}%)'
  },
  legend: {
    orient: 'vertical',
    left: 'left'
  },
  series: [
    {
      name: '消费分布',
      type: 'pie',
      radius: '50%',
      data: pieData.value,
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }
  ]
}))

// 计算属性 - 热力图配置
const heatmapOption = computed(() => ({
  title: {
    text: '消费热力图',
    left: 'center'
  },
  tooltip: {
    position: 'top',
    formatter: (params) => {
      return `${params.data[1]} ${params.data[0]}<br/>消费: ${formatNumber(params.data[2])} tokens`
    }
  },
  grid: {
    height: '70%',
    top: '10%'
  },
  xAxis: {
    type: 'category',
    data: ['00:00', '02:00', '04:00', '06:00', '08:00', '10:00', '12:00', '14:00', '16:00', '18:00', '20:00', '22:00'],
    splitArea: {
      show: true
    }
  },
  yAxis: {
    type: 'category',
    data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
    splitArea: {
      show: true
    }
  },
  visualMap: {
    min: 0,
    max: Math.max(...heatmapData.value.map(item => item[2]), 1),
    calculable: true,
    orient: 'horizontal',
    left: 'center',
    bottom: '15%'
  },
  series: [{
    name: '消费热力图',
    type: 'heatmap',
    data: heatmapData.value,
    label: {
      show: true
    },
    emphasis: {
      itemStyle: {
        shadowBlur: 10,
        shadowColor: 'rgba(0, 0, 0, 0.5)'
      }
    }
  }]
}))

// 初始化
onMounted(() => {
  loadData()
})

// 监听图表类型变化
watch([trendChartType, pieChartType], () => {
  loadChartData()
})

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    await Promise.all([
      loadOverview(),
      loadChartData(),
      loadDetailsData()
    ])
  } catch (error) {
    ElMessage.error('加载数据失败')
    console.error('Load data error:', error)
  } finally {
    loading.value = false
  }
}

// 加载概览数据
const loadOverview = async () => {
  const response = await aiConfigAPI.getUsageStatistics(timeRangeForm.range)
  const data = response.data
  Object.assign(overview, {
    totalConsumption: data.total_consumption || 0,
    totalCost: data.total_cost || 0,
    avgDailyConsumption: data.avg_daily_consumption || 0,
    budgetUsage: data.budget_usage || 0
  })
}

// 加载图表数据
const loadChartData = async () => {
  try {
    const params = getTimeRangeParams()
    
    // 加载趋势数据
    const trendResponse = await aiConfigAPI.getConsumptionTrends({
      ...params,
      type: trendChartType.value
    })
    trendData.value = trendResponse.data.results || []
    
    // 加载饼图数据
    const pieResponse = await aiConfigAPI.getConsumptionPieChart({
      ...params,
      type: pieChartType.value
    })
    pieData.value = pieResponse.data.results || []
    
    // 加载热力图数据
    const heatmapResponse = await aiConfigAPI.getConsumptionHeatmap(params)
    heatmapData.value = heatmapResponse.data.results || []
  } catch (error) {
    console.error('Load chart data error:', error)
  }
}

// 加载详细数据
const loadDetailsData = async () => {
  try {
    const params = {
      ...getTimeRangeParams(),
      page: pagination.currentPage,
      page_size: pagination.pageSize
    }
    
    const response = await aiConfigAPI.getConsumptionDetails(params)
    detailsData.value = response.data.results || []
    pagination.total = response.data.count || 0
  } catch (error) {
    console.error('Load details error:', error)
  }
}

// 获取时间范围参数
const getTimeRangeParams = () => {
  const params = {}
  if (timeRangeForm.range === 'custom') {
    if (timeRangeForm.startDate) {
      params.start_date = formatDateTime(timeRangeForm.startDate, 'YYYY-MM-DD')
    }
    if (timeRangeForm.endDate) {
      params.end_date = formatDateTime(timeRangeForm.endDate, 'YYYY-MM-DD')
    }
  } else {
    params.time_range = timeRangeForm.range
  }
  return params
}

// 处理时间范围变化
const handleTimeRangeChange = () => {
  if (timeRangeForm.range !== 'custom') {
    loadData()
  }
}

// 处理自定义日期变化
const handleCustomDateChange = () => {
  if (timeRangeForm.startDate && timeRangeForm.endDate) {
    loadData()
  }
}

// 处理分页变化
const handlePageSizeChange = (size) => {
  pagination.pageSize = size
  pagination.currentPage = 1
  loadDetailsData()
}

const handleCurrentPageChange = (page) => {
  pagination.currentPage = page
  loadDetailsData()
}

// 刷新数据
const refreshData = () => {
  loadData()
}

// 导出数据
const exportData = () => {
  // 这里可以实现数据导出功能
  ElMessage.success('数据导出功能开发中')
}

// 显示预算设置
const showBudgetSettings = async () => {
  try {
    const response = await aiConfigAPI.getBudgetSettings()
    const data = response.data
    Object.assign(budgetForm, data)
    budgetDialogVisible.value = true
  } catch (error) {
    ElMessage.error('加载预算设置失败')
    console.error('Load budget settings error:', error)
  }
}

// 保存预算设置
const saveBudgetSettings = async () => {
  try {
    await budgetFormRef.value.validate()
    saving.value = true
    
    await aiConfigAPI.updateBudgetSettings(budgetForm)
    ElMessage.success('预算设置保存成功')
    budgetDialogVisible.value = false
    
    // 重新加载概览数据
    await loadOverview()
  } catch (error) {
    if (error.response?.data?.message) {
      ElMessage.error(error.response.data.message)
    } else {
      ElMessage.error('保存预算设置失败')
    }
    console.error('Save budget settings error:', error)
  } finally {
    saving.value = false
  }
}

// 显示告警配置
const showAlertConfig = () => {
  isEditAlert.value = false
  resetAlertForm()
  alertDialogVisible.value = true
}

// 重置告警表单
const resetAlertForm = () => {
  Object.assign(alertForm, {
    name: '',
    type: '',
    condition: 0,
    notification_methods: [],
    email: '',
    webhook_url: '',
    enabled: true
  })
}

// 保存告警配置
const saveAlertConfig = async () => {
  try {
    await alertFormRef.value.validate()
    saving.value = true
    
    if (isEditAlert.value) {
      await aiConfigAPI.updateAlertConfig(alertForm.id, alertForm)
      ElMessage.success('告警配置更新成功')
    } else {
      await aiConfigAPI.createAlertConfig(alertForm)
      ElMessage.success('告警配置创建成功')
    }
    
    alertDialogVisible.value = false
  } catch (error) {
    if (error.response?.data?.message) {
      ElMessage.error(error.response.data.message)
    } else {
      ElMessage.error('保存告警配置失败')
    }
    console.error('Save alert config error:', error)
  } finally {
    saving.value = false
  }
}

// 格式化数字
const formatNumber = (num, decimals = 0) => {
  if (num === null || num === undefined) return '0'
  return Number(num).toLocaleString('zh-CN', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  })
}
</script>

<style scoped>
.statistics-view {
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

.time-range-selector {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.statistics-overview {
  margin-bottom: 20px;
}

.overview-card {
  height: 100%;
}

.overview-item {
  display: flex;
  align-items: center;
  gap: 15px;
}

.overview-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.overview-icon.total-consumption {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.overview-icon.total-cost {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.overview-icon.avg-daily {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.overview-icon.budget-usage {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.overview-content {
  flex: 1;
}

.overview-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}

.overview-label {
  font-size: 14px;
  color: #606266;
}

.charts-section {
  margin-bottom: 20px;
}

.heatmap-section {
  margin-bottom: 20px;
}

.chart-container {
  position: relative;
}

.details-section {
  margin-bottom: 20px;
}

.pagination-wrapper {
  margin-top: 20px;
  text-align: center;
}

.floating-actions {
  position: fixed;
  bottom: 30px;
  right: 30px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  z-index: 1000;
}

.subtitle {
  font-size: 14px;
  color: #909399;
  font-weight: normal;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .statistics-view {
    padding: 10px;
  }
  
  .overview-item {
    flex-direction: column;
    text-align: center;
  }
  
  .overview-icon {
    width: 50px;
    height: 50px;
    font-size: 20px;
  }
  
  .overview-value {
    font-size: 20px;
  }
  
  .floating-actions {
    bottom: 20px;
    right: 20px;
  }
}
</style>
