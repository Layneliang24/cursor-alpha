import request from '@/utils/request'

/**
 * 监控API接口
 */

// 服务管理
export const monitoringAPI = {
  // 获取服务列表
  getServices() {
    return request.get('/api/v1/monitoring/services/')
  },

  // 获取单个服务详情
  getService(serviceId) {
    return request.get(`/api/v1/monitoring/services/${serviceId}/`)
  },

  // 创建服务
  createService(data) {
    return request.post('/api/v1/monitoring/services/', data)
  },

  // 更新服务
  updateService(serviceId, data) {
    return request.put(`/api/v1/monitoring/services/${serviceId}/`, data)
  },

  // 删除服务
  deleteService(serviceId) {
    return request.delete(`/api/v1/monitoring/services/${serviceId}/`)
  },

  // 测试服务连接
  testService(serviceId) {
    return request.post(`/api/v1/monitoring/services/${serviceId}/test/`)
  },

  // 重启服务
  restartService(serviceId) {
    return request.post(`/api/v1/monitoring/services/${serviceId}/restart/`)
  },

  // 获取指标数据
  getMetrics(params = {}) {
    return request.get('/api/v1/monitoring/metrics/', { params })
  },

  // 获取特定服务的指标
  getServiceMetrics(serviceId, params = {}) {
    return request.get(`/api/v1/monitoring/services/${serviceId}/metrics/`, { params })
  },

  // 获取响应时间数据
  getResponseTimeMetrics(params = {}) {
    return request.get('/api/v1/monitoring/metrics/response-time/', { params })
  },

  // 获取成功率数据
  getSuccessRateMetrics(params = {}) {
    return request.get('/api/v1/monitoring/metrics/success-rate/', { params })
  },

  // 获取请求数量数据
  getRequestCountMetrics(params = {}) {
    return request.get('/api/v1/monitoring/metrics/request-count/', { params })
  },

  // 获取错误率数据
  getErrorRateMetrics(params = {}) {
    return request.get('/api/v1/monitoring/metrics/error-rate/', { params })
  },

  // 告警管理
  getAlarms(params = {}) {
    return request.get('/api/v1/monitoring/alarms/', { params })
  },

  // 获取单个告警
  getAlarm(alarmId) {
    return request.get(`/api/v1/monitoring/alarms/${alarmId}/`)
  },

  // 创建告警
  createAlarm(data) {
    return request.post('/api/v1/monitoring/alarms/', data)
  },

  // 更新告警
  updateAlarm(alarmId, data) {
    return request.put(`/api/v1/monitoring/alarms/${alarmId}/`, data)
  },

  // 标记告警为已读
  markAlarmAsRead(alarmId) {
    return request.patch(`/api/v1/monitoring/alarms/${alarmId}/`, { isRead: true })
  },

  // 批量标记告警为已读
  markAlarmsAsRead(alarmIds) {
    return request.post('/api/v1/monitoring/alarms/mark-read/', { alarmIds })
  },

  // 删除告警
  deleteAlarm(alarmId) {
    return request.delete(`/api/v1/monitoring/alarms/${alarmId}/`)
  },

  // 清空告警
  clearAlarms() {
    return request.delete('/api/v1/monitoring/alarms/clear/')
  },

  // 系统健康
  getSystemHealth() {
    return request.get('/api/v1/monitoring/health/')
  },

  // 获取系统概览
  getSystemOverview() {
    return request.get('/api/v1/monitoring/overview/')
  },

  // 获取服务统计
  getServiceStats(params = {}) {
    return request.get('/api/v1/monitoring/stats/services/', { params })
  },

  // 获取告警统计
  getAlarmStats(params = {}) {
    return request.get('/api/v1/monitoring/stats/alarms/', { params })
  },

  // 获取性能统计
  getPerformanceStats(params = {}) {
    return request.get('/api/v1/monitoring/stats/performance/', { params })
  },

  // 配置管理
  getMonitoringConfig() {
    return request.get('/api/v1/monitoring/config/')
  },

  // 更新监控配置
  updateMonitoringConfig(data) {
    return request.put('/api/v1/monitoring/config/', data)
  },

  // 告警规则管理
  getAlarmRules() {
    return request.get('/api/v1/monitoring/alarm-rules/')
  },

  // 创建告警规则
  createAlarmRule(data) {
    return request.post('/api/v1/monitoring/alarm-rules/', data)
  },

  // 更新告警规则
  updateAlarmRule(ruleId, data) {
    return request.put(`/api/v1/monitoring/alarm-rules/${ruleId}/`, data)
  },

  // 删除告警规则
  deleteAlarmRule(ruleId) {
    return request.delete(`/api/v1/monitoring/alarm-rules/${ruleId}/`)
  },

  // 测试告警规则
  testAlarmRule(ruleId) {
    return request.post(`/api/v1/monitoring/alarm-rules/${ruleId}/test/`)
  },

  // 日志管理
  getLogs(params = {}) {
    return request.get('/api/v1/monitoring/logs/', { params })
  },

  // 获取服务日志
  getServiceLogs(serviceId, params = {}) {
    return request.get(`/api/v1/monitoring/services/${serviceId}/logs/`, { params })
  },

  // 导出日志
  exportLogs(params = {}) {
    return request.get('/api/v1/monitoring/logs/export/', { 
      params,
      responseType: 'blob'
    })
  },

  // 实时监控
  getRealtimeData() {
    return request.get('/api/v1/monitoring/realtime/')
  },

  // WebSocket连接信息
  getWebSocketInfo() {
    return request.get('/api/v1/monitoring/websocket-info/')
  }
}

// 导出所有API方法（保持向后兼容）
export const {
  getServices,
  getService,
  createService,
  updateService,
  deleteService,
  testService,
  restartService,
  getMetrics,
  getServiceMetrics,
  getResponseTimeMetrics,
  getSuccessRateMetrics,
  getRequestCountMetrics,
  getErrorRateMetrics,
  getAlarms,
  getAlarm,
  createAlarm,
  updateAlarm,
  markAlarmAsRead,
  markAlarmsAsRead,
  deleteAlarm,
  clearAlarms,
  getSystemHealth,
  getSystemOverview,
  getServiceStats,
  getAlarmStats,
  getPerformanceStats,
  getMonitoringConfig,
  updateMonitoringConfig,
  getAlarmRules,
  createAlarmRule,
  updateAlarmRule,
  deleteAlarmRule,
  testAlarmRule,
  getLogs,
  getServiceLogs,
  exportLogs,
  getRealtimeData,
  getWebSocketInfo
} = monitoringAPI

export default monitoringAPI
