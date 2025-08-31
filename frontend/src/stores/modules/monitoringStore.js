import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import * as monitoringAPI from '@/api/monitoring'

export const useMonitoringStore = defineStore('monitoring', () => {
  // 状态
  const services = ref([])
  const metrics = ref({
    responseTime: [],
    successRate: [],
    requestCount: [],
    errorRate: []
  })
  const alarms = ref([])
  const systemHealth = ref({
    overall: 'healthy',
    uptime: '99.9%',
    totalRequests: 0,
    totalErrors: 0,
    avgResponseTime: 0
  })
  const loading = ref(false)
  const lastUpdate = ref(null)
  
  // 计算属性
  const onlineServices = computed(() => {
    return services.value.filter(service => service.status === 'online')
  })
  
  const offlineServices = computed(() => {
    return services.value.filter(service => service.status === 'offline')
  })
  
  const warningServices = computed(() => {
    return services.value.filter(service => service.status === 'warning')
  })
  
  const totalServices = computed(() => services.value.length)
  
  const healthyPercentage = computed(() => {
    if (totalServices.value === 0) return 100
    return Math.round((onlineServices.value.length / totalServices.value) * 100)
  })
  
  const unreadAlarms = computed(() => {
    return alarms.value.filter(alarm => !alarm.isRead)
  })
  
  const criticalAlarms = computed(() => {
    return alarms.value.filter(alarm => alarm.level === 'error' && !alarm.isRead)
  })
  
  const recentAlarms = computed(() => {
    const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000)
    return alarms.value.filter(alarm => new Date(alarm.timestamp) > oneHourAgo)
  })
  
  // 服务管理
  const fetchServices = async () => {
    try {
      loading.value = true
      const response = await monitoringAPI.getServices()
      services.value = response.data || []
      lastUpdate.value = new Date()
      return services.value
    } catch (error) {
      console.error('获取服务列表失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }
  
  const updateServiceStatus = (serviceId, status) => {
    const service = services.value.find(s => s.id === serviceId)
    if (service) {
      service.status = status.status
      service.responseTime = status.responseTime
      service.lastHeartbeat = new Date(status.lastHeartbeat)
      service.uptime = status.uptime
      service.requestCount = status.requestCount
      service.errorRate = status.errorRate
    }
  }
  
  const addService = async (serviceData) => {
    try {
      const response = await monitoringAPI.createService(serviceData)
      services.value.push(response.data)
      return response.data
    } catch (error) {
      console.error('添加服务失败:', error)
      throw error
    }
  }
  
  const updateService = async (serviceId, serviceData) => {
    try {
      const response = await monitoringAPI.updateService(serviceId, serviceData)
      const index = services.value.findIndex(s => s.id === serviceId)
      if (index !== -1) {
        services.value[index] = response.data
      }
      return response.data
    } catch (error) {
      console.error('更新服务失败:', error)
      throw error
    }
  }
  
  const removeService = async (serviceId) => {
    try {
      await monitoringAPI.deleteService(serviceId)
      const index = services.value.findIndex(s => s.id === serviceId)
      if (index !== -1) {
        services.value.splice(index, 1)
      }
    } catch (error) {
      console.error('删除服务失败:', error)
      throw error
    }
  }
  
  // 指标数据管理
  const fetchMetrics = async (timeRange = '6h', serviceId = null) => {
    try {
      loading.value = true
      const response = await monitoringAPI.getMetrics({ timeRange, serviceId })
      metrics.value = response.data || metrics.value
      lastUpdate.value = new Date()
      return metrics.value
    } catch (error) {
      console.error('获取指标数据失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }
  
  const addMetricPoint = (metricType, point) => {
    if (!metrics.value[metricType]) {
      metrics.value[metricType] = []
    }
    
    metrics.value[metricType].push({
      timestamp: point.timestamp || new Date(),
      value: point.value,
      serviceId: point.serviceId
    })
    
    // 保持最新100个数据点
    if (metrics.value[metricType].length > 100) {
      metrics.value[metricType].shift()
    }
  }
  
  const clearMetrics = () => {
    metrics.value = {
      responseTime: [],
      successRate: [],
      requestCount: [],
      errorRate: []
    }
  }
  
  // 告警管理
  const fetchAlarms = async (filters = {}) => {
    try {
      loading.value = true
      const response = await monitoringAPI.getAlarms(filters)
      alarms.value = response.data || []
      lastUpdate.value = new Date()
      return alarms.value
    } catch (error) {
      console.error('获取告警数据失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }
  
  const addAlarm = (alarmData) => {
    const alarm = {
      id: alarmData.id || `alarm_${Date.now()}`,
      timestamp: alarmData.timestamp || new Date(),
      level: alarmData.level,
      service: alarmData.service,
      message: alarmData.message,
      isRead: false,
      ...alarmData
    }
    
    alarms.value.unshift(alarm)
    
    // 保持最新50条告警
    if (alarms.value.length > 50) {
      alarms.value.pop()
    }
    
    return alarm
  }
  
  const markAlarmAsRead = (alarmId) => {
    const alarm = alarms.value.find(a => a.id === alarmId)
    if (alarm) {
      alarm.isRead = true
    }
  }
  
  const markAllAlarmsAsRead = () => {
    alarms.value.forEach(alarm => {
      alarm.isRead = true
    })
  }
  
  const clearAlarms = () => {
    alarms.value = []
  }
  
  const removeAlarm = (alarmId) => {
    const index = alarms.value.findIndex(a => a.id === alarmId)
    if (index !== -1) {
      alarms.value.splice(index, 1)
    }
  }
  
  // 系统健康状态
  const fetchSystemHealth = async () => {
    try {
      const response = await monitoringAPI.getSystemHealth()
      systemHealth.value = response.data || systemHealth.value
      return systemHealth.value
    } catch (error) {
      console.error('获取系统健康状态失败:', error)
      throw error
    }
  }
  
  const updateSystemHealth = (healthData) => {
    systemHealth.value = {
      ...systemHealth.value,
      ...healthData,
      lastUpdate: new Date()
    }
  }
  
  // 实时数据处理
  const handleRealtimeUpdate = (message) => {
    try {
      switch (message.type) {
        case 'metrics_update':
          if (message.data.responseTime) {
            addMetricPoint('responseTime', {
              value: message.data.responseTime,
              timestamp: new Date(),
              serviceId: message.data.serviceId
            })
          }
          if (message.data.successRate !== undefined) {
            addMetricPoint('successRate', {
              value: message.data.successRate,
              timestamp: new Date(),
              serviceId: message.data.serviceId
            })
          }
          break
          
        case 'status_update':
          updateServiceStatus(message.data.serviceId, message.data)
          break
          
        case 'alarm_new':
          addAlarm(message.data)
          break
          
        case 'system_health':
          updateSystemHealth(message.data)
          break
          
        default:
          console.log('未知的实时消息类型:', message.type)
      }
    } catch (error) {
      console.error('处理实时更新失败:', error)
    }
  }
  
  // 数据统计
  const getServiceStatistics = () => {
    return {
      total: totalServices.value,
      online: onlineServices.value.length,
      offline: offlineServices.value.length,
      warning: warningServices.value.length,
      healthyPercentage: healthyPercentage.value
    }
  }
  
  const getAlarmStatistics = () => {
    const errorCount = alarms.value.filter(a => a.level === 'error').length
    const warningCount = alarms.value.filter(a => a.level === 'warning').length
    const infoCount = alarms.value.filter(a => a.level === 'info').length
    
    return {
      total: alarms.value.length,
      unread: unreadAlarms.value.length,
      critical: criticalAlarms.value.length,
      recent: recentAlarms.value.length,
      byLevel: {
        error: errorCount,
        warning: warningCount,
        info: infoCount
      }
    }
  }
  
  const getMetricsStatistics = () => {
    const responseTimeData = metrics.value.responseTime
    const successRateData = metrics.value.successRate
    
    const avgResponseTime = responseTimeData.length > 0
      ? responseTimeData.reduce((sum, item) => sum + item.value, 0) / responseTimeData.length
      : 0
      
    const avgSuccessRate = successRateData.length > 0
      ? successRateData.reduce((sum, item) => sum + item.value, 0) / successRateData.length
      : 0
    
    return {
      avgResponseTime: Math.round(avgResponseTime),
      avgSuccessRate: Math.round(avgSuccessRate * 100) / 100,
      dataPoints: {
        responseTime: responseTimeData.length,
        successRate: successRateData.length
      }
    }
  }
  
  // 重置状态
  const resetState = () => {
    services.value = []
    metrics.value = {
      responseTime: [],
      successRate: [],
      requestCount: [],
      errorRate: []
    }
    alarms.value = []
    systemHealth.value = {
      overall: 'healthy',
      uptime: '99.9%',
      totalRequests: 0,
      totalErrors: 0,
      avgResponseTime: 0
    }
    loading.value = false
    lastUpdate.value = null
  }
  
  // 初始化数据
  const initializeData = async () => {
    try {
      loading.value = true
      await Promise.all([
        fetchServices(),
        fetchMetrics(),
        fetchAlarms(),
        fetchSystemHealth()
      ])
    } catch (error) {
      console.error('初始化监控数据失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }
  
  return {
    // 状态
    services,
    metrics,
    alarms,
    systemHealth,
    loading,
    lastUpdate,
    
    // 计算属性
    onlineServices,
    offlineServices,
    warningServices,
    totalServices,
    healthyPercentage,
    unreadAlarms,
    criticalAlarms,
    recentAlarms,
    
    // 服务管理
    fetchServices,
    updateServiceStatus,
    addService,
    updateService,
    removeService,
    
    // 指标管理
    fetchMetrics,
    addMetricPoint,
    clearMetrics,
    
    // 告警管理
    fetchAlarms,
    addAlarm,
    markAlarmAsRead,
    markAllAlarmsAsRead,
    clearAlarms,
    removeAlarm,
    
    // 系统健康
    fetchSystemHealth,
    updateSystemHealth,
    
    // 实时更新
    handleRealtimeUpdate,
    
    // 统计信息
    getServiceStatistics,
    getAlarmStatistics,
    getMetricsStatistics,
    
    // 系统操作
    resetState,
    initializeData
  }
})
