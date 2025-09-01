<template>
  <div class="monitoring-dashboard">
    <div class="dashboard-header">
      <h1 class="dashboard-title">AI服务监控仪表板</h1>
      <div class="dashboard-actions">
        <el-button @click="refreshData" :loading="loading" type="primary" size="small">
          <i class="el-icon-refresh"></i>
          刷新数据
        </el-button>
        <el-select v-model="timeRange" size="small" style="width: 120px;">
          <el-option label="最近1小时" value="1h" />
          <el-option label="最近6小时" value="6h" />
          <el-option label="最近24小时" value="24h" />
          <el-option label="最近7天" value="7d" />
        </el-select>
      </div>
    </div>

    <div class="dashboard-content">
      <!-- 服务状态区域 -->
      <div class="status-section">
        <h2 class="section-title">
          <i class="el-icon-monitor"></i>
          服务状态
        </h2>
        <div class="status-grid">
          <ServiceStatusPanel
            v-for="service in serviceStatuses"
            :key="service.id"
            :service="service"
            @refresh="refreshServiceStatus"
          />
        </div>
      </div>

      <!-- 性能图表区域 -->
      <div class="metrics-section">
        <h2 class="section-title">
          <i class="el-icon-data-line"></i>
          性能指标
        </h2>
        <div class="charts-grid">
          <div class="chart-card">
            <h3 class="chart-title">响应时间趋势</h3>
            <MetricsChart
              ref="responseTimeChart"
              :data="responseTimeData"
              :loading="chartsLoading"
              chart-type="line"
              y-axis-label="响应时间 (ms)"
            />
          </div>
          <div class="chart-card">
            <h3 class="chart-title">成功率趋势</h3>
            <MetricsChart
              ref="successRateChart"
              :data="successRateData"
              :loading="chartsLoading"
              chart-type="area"
              y-axis-label="成功率 (%)"
              :y-axis-max="100"
            />
          </div>
        </div>
      </div>

      <!-- 告警日志区域 -->
      <div class="alarms-section">
        <h2 class="section-title">
          <i class="el-icon-warning"></i>
          告警日志
          <el-badge :value="unreadAlarmsCount" :hidden="unreadAlarmsCount === 0" />
        </h2>
        <AlarmTable
          :alarms="alarmLogs"
          :loading="alarmsLoading"
          @filter-change="handleAlarmFilter"
          @clear-alarms="clearAlarms"
        />
      </div>
    </div>

    <!-- WebSocket连接状态 -->
    <div class="connection-status" :class="{ 'connected': wsConnected, 'disconnected': !wsConnected }">
      <i :class="wsConnected ? 'el-icon-success' : 'el-icon-warning'"></i>
      {{ wsConnected ? '实时连接已建立' : '实时连接断开' }}
      <span v-if="!wsConnected" class="reconnect-info">正在尝试重连...</span>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import ServiceStatusPanel from '@/components/monitoring/ServiceStatusPanel.vue'
import MetricsChart from '@/components/monitoring/MetricsChart.vue'
import AlarmTable from '@/components/monitoring/AlarmTable.vue'
import { useMonitoringStore } from '@/stores/modules/monitoringStore'
import { useAIWebSocket } from '@/composables/useWebSocket'

export default {
  name: 'MonitoringDashboard',
  components: {
    ServiceStatusPanel,
    MetricsChart,
    AlarmTable
  },
  setup() {
    const monitoringStore = useMonitoringStore()
    
    // 响应式数据
    const loading = ref(false)
    const chartsLoading = ref(false)
    const alarmsLoading = ref(false)
    const timeRange = ref('6h')
    
    // 图表引用
    const responseTimeChart = ref()
    const successRateChart = ref()
    
    // WebSocket连接
    const { 
      isConnected: wsConnected, 
      connectionStatus: wsStatus,
      providerStatus,
      usageStats,
      strategyStatus,
      alerts
    } = useAIWebSocket()
    
    // 服务状态数据 - 使用WebSocket实时数据
    const serviceStatuses = computed(() => {
      return providerStatus.value.map(provider => ({
        id: provider.id,
        name: provider.name,
        status: provider.is_healthy ? 'online' : 'offline',
        responseTime: provider.avg_response_time || 0,
        lastHeartbeat: provider.last_check ? new Date(provider.last_check) : new Date(),
        uptime: '99.9%', // 可以从历史数据计算
        requestCount: 0, // 可以从统计数据获取
        errorRate: provider.is_healthy ? 0.1 : 5.0
      }))
    })
    
    // 性能数据
    const responseTimeData = ref([])
    const successRateData = ref([])
    
    // 告警日志数据 - 使用WebSocket实时告警
    const alarmLogs = computed(() => {
      return alerts.value.map(alert => ({
        id: `alert_${alert.strategy_id}_${alert.timestamp}`,
        timestamp: new Date(alert.timestamp),
        level: alert.alert_type === 'degradation' ? 'warning' : 'error',
        service: alert.strategy_name,
        message: alert.message,
        isRead: false
      }))
    })
    
    // 计算属性
    const unreadAlarmsCount = computed(() => {
      return alarmLogs.value.filter(alarm => !alarm.isRead).length
    })
    
    // 生成模拟数据
    const generateMockData = () => {
      const now = new Date()
      const points = []
      const successPoints = []
      
      // 生成过去6小时的数据点
      for (let i = 360; i >= 0; i -= 10) {
        const timestamp = new Date(now.getTime() - i * 60 * 1000)
        
        // 响应时间数据（加入一些随机波动）
        const baseResponseTime = 800 + Math.sin(i / 60) * 200
        const responseTime = Math.max(200, baseResponseTime + (Math.random() - 0.5) * 400)
        
        points.push({
          timestamp,
          value: Math.round(responseTime)
        })
        
        // 成功率数据
        const baseSuccessRate = 98 + Math.sin(i / 30) * 2
        const successRate = Math.max(90, Math.min(100, baseSuccessRate + (Math.random() - 0.5) * 4))
        
        successPoints.push({
          timestamp,
          value: Math.round(successRate * 100) / 100
        })
      }
      
      responseTimeData.value = points
      successRateData.value = successPoints
    }
    
    // 生成模拟告警数据
    const generateMockAlarms = () => {
      const alarmTypes = [
        { level: 'error', message: 'OpenAI API响应超时', service: 'openai-gpt4' },
        { level: 'warning', message: 'Claude服务响应时间较慢', service: 'claude-sonnet' },
        { level: 'error', message: 'Gemini Pro服务连接失败', service: 'gemini-pro' },
        { level: 'info', message: '本地模型服务重启完成', service: 'local-llama' },
        { level: 'warning', message: 'API调用频率接近限制', service: 'openai-gpt4' },
        { level: 'error', message: '模型推理异常', service: 'local-llama' }
      ]
      
      const alarms = []
      const now = new Date()
      
      for (let i = 0; i < 20; i++) {
        const alarmType = alarmTypes[Math.floor(Math.random() * alarmTypes.length)]
        const timestamp = new Date(now.getTime() - Math.random() * 24 * 60 * 60 * 1000) // 24小时内
        
        alarms.push({
          id: `alarm_${i}`,
          timestamp,
          level: alarmType.level,
          service: alarmType.service,
          message: alarmType.message,
          isRead: Math.random() > 0.3 // 30%未读
        })
      }
      
      // 按时间倒序排列
      alarmLogs.value = alarms.sort((a, b) => b.timestamp - a.timestamp)
    }
    
    // 方法
    const refreshData = async () => {
      loading.value = true
      try {
        await Promise.all([
          refreshServiceStatus(),
          refreshMetrics(),
          refreshAlarms()
        ])
        ElMessage.success('数据刷新成功')
      } catch (error) {
        ElMessage.error('数据刷新失败')
        console.error('刷新数据失败:', error)
      } finally {
        loading.value = false
      }
    }
    
    const refreshServiceStatus = async () => {
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 500))
      
      // 随机更新服务状态
      serviceStatuses.value.forEach(service => {
        if (Math.random() > 0.8) {
          service.responseTime = Math.round(500 + Math.random() * 2000)
          service.lastHeartbeat = new Date()
        }
      })
    }
    
    const refreshMetrics = async () => {
      chartsLoading.value = true
      try {
        await new Promise(resolve => setTimeout(resolve, 800))
        generateMockData()
        
        // 刷新图表
        await nextTick()
        responseTimeChart.value?.refresh()
        successRateChart.value?.refresh()
      } finally {
        chartsLoading.value = false
      }
    }
    
    const refreshAlarms = async () => {
      alarmsLoading.value = true
      try {
        await new Promise(resolve => setTimeout(resolve, 300))
        generateMockAlarms()
      } finally {
        alarmsLoading.value = false
      }
    }
    
    const handleAlarmFilter = (filters) => {
      console.log('告警过滤条件:', filters)
      // 这里可以实现实际的过滤逻辑
    }
    
    const clearAlarms = () => {
      alarmLogs.value = []
      ElMessage.success('告警日志已清空')
    }
    
    // WebSocket事件处理
    const handleWebSocketMessage = (data) => {
      try {
        const message = JSON.parse(data)
        
        switch (message.type) {
          case 'metrics_update':
            // 更新图表数据
            if (message.data.responseTime) {
              responseTimeData.value.push({
                timestamp: new Date(),
                value: message.data.responseTime
              })
              // 保持最新100个数据点
              if (responseTimeData.value.length > 100) {
                responseTimeData.value.shift()
              }
            }
            break
            
          case 'status_update':
            // 更新服务状态
            const serviceIndex = serviceStatuses.value.findIndex(s => s.id === message.data.serviceId)
            if (serviceIndex !== -1) {
              Object.assign(serviceStatuses.value[serviceIndex], message.data)
            }
            break
            
          case 'alarm_new':
            // 新增告警
            alarmLogs.value.unshift({
              id: `alarm_${Date.now()}`,
              timestamp: new Date(),
              ...message.data,
              isRead: false
            })
            // 保持最新50条告警
            if (alarmLogs.value.length > 50) {
              alarmLogs.value.pop()
            }
            break
        }
      } catch (error) {
        console.error('WebSocket消息处理失败:', error)
      }
    }
    
    // 生命周期
    onMounted(async () => {
      // 初始化数据
      generateMockData()
      generateMockAlarms()
      
      // 建立WebSocket连接
      connectWS('ws://localhost:8000/ws/monitoring/', {
        onMessage: handleWebSocketMessage,
        onError: (error) => {
          console.error('WebSocket错误:', error)
          ElMessage.error('实时连接异常')
        },
        onReconnect: () => {
          ElMessage.info('正在重连...')
        }
      })
      
      // 初始加载数据
      await refreshData()
    })
    
    onUnmounted(() => {
      // 清理WebSocket连接
      disconnectWS()
    })
    
    return {
      // 数据
      loading,
      chartsLoading,
      alarmsLoading,
      timeRange,
      serviceStatuses,
      responseTimeData,
      successRateData,
      alarmLogs,
      wsConnected,
      unreadAlarmsCount,
      
      // 引用
      responseTimeChart,
      successRateChart,
      
      // 方法
      refreshData,
      refreshServiceStatus,
      handleAlarmFilter,
      clearAlarms
    }
  }
}
</script>

<style scoped>
.monitoring-dashboard {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 1.5rem;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding: 1rem 2rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.dashboard-title {
  font-size: 1.8rem;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0;
}

.dashboard-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.dashboard-content {
  display: grid;
  gap: 2rem;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.3rem;
  font-weight: 600;
  color: #333;
  margin: 0 0 1.5rem 0;
}

.section-title i {
  color: #667eea;
}

/* 服务状态区域 */
.status-section {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}

/* 性能图表区域 */
.metrics-section {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
}

.chart-card {
  background: #f8f9ff;
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid #e6f3ff;
}

.chart-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #333;
  margin: 0 0 1rem 0;
  text-align: center;
}

/* 告警日志区域 */
.alarms-section {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

/* WebSocket连接状态 */
.connection-status {
  position: fixed;
  bottom: 20px;
  right: 20px;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  z-index: 1000;
  transition: all 0.3s ease;
}

.connection-status.connected {
  background: #f6ffed;
  color: #52c41a;
  border: 1px solid #b7eb8f;
}

.connection-status.disconnected {
  background: #fff2f0;
  color: #ff4d4f;
  border: 1px solid #ffccc7;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .monitoring-dashboard {
    padding: 1rem;
  }
  
  .dashboard-header {
    flex-direction: column;
    gap: 1rem;
    padding: 1rem;
  }
  
  .dashboard-actions {
    width: 100%;
    justify-content: space-between;
  }
  
  .status-grid {
    grid-template-columns: 1fr;
  }
  
  .charts-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .connection-status {
    bottom: 10px;
    right: 10px;
    font-size: 0.8rem;
  }
}

/* 深色模式适配 */
@media (prefers-color-scheme: dark) {
  .monitoring-dashboard {
    background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
  }
  
  .dashboard-header,
  .status-section,
  .metrics-section,
  .alarms-section {
    background: #2d2d2d;
    color: #fff;
  }
  
  .chart-card {
    background: #3a3a3a;
    border-color: #4a4a4a;
  }
  
  .section-title {
    color: #fff;
  }
}
</style>
