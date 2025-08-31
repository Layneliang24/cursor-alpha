<template>
  <div class="service-status-panel" :class="`status-${service.status}`">
    <div class="panel-header">
      <div class="service-info">
        <h3 class="service-name">{{ service.name }}</h3>
        <div class="service-id">{{ service.id }}</div>
      </div>
      <div class="status-indicator">
        <div class="status-dot" :class="`dot-${service.status}`"></div>
        <span class="status-text">{{ getStatusText(service.status) }}</span>
      </div>
    </div>
    
    <div class="panel-content">
      <div class="metrics-grid">
        <div class="metric-item">
          <div class="metric-label">响应时间</div>
          <div class="metric-value">
            <span v-if="service.responseTime" class="value-number">
              {{ service.responseTime }}
            </span>
            <span v-else class="value-na">N/A</span>
            <span v-if="service.responseTime" class="value-unit">ms</span>
          </div>
        </div>
        
        <div class="metric-item">
          <div class="metric-label">运行时间</div>
          <div class="metric-value">
            <span class="value-number">{{ service.uptime }}</span>
          </div>
        </div>
        
        <div class="metric-item">
          <div class="metric-label">请求数</div>
          <div class="metric-value">
            <span class="value-number">{{ service.requestCount?.toLocaleString() || 0 }}</span>
          </div>
        </div>
        
        <div class="metric-item">
          <div class="metric-label">错误率</div>
          <div class="metric-value">
            <span class="value-number" :class="{ 'value-error': service.errorRate > 1 }">
              {{ service.errorRate }}%
            </span>
          </div>
        </div>
      </div>
      
      <div class="panel-footer">
        <div class="last-heartbeat">
          <i class="el-icon-time"></i>
          最后心跳: {{ formatTime(service.lastHeartbeat) }}
        </div>
        <div class="panel-actions">
          <el-button size="mini" @click="$emit('refresh', service.id)">
            <i class="el-icon-refresh"></i>
          </el-button>
          <el-dropdown @command="handleCommand">
            <el-button size="mini">
              <i class="el-icon-more"></i>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="details">查看详情</el-dropdown-item>
                <el-dropdown-item command="logs">查看日志</el-dropdown-item>
                <el-dropdown-item command="restart" :disabled="service.status === 'offline'">
                  重启服务
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ElMessage } from 'element-plus'

export default {
  name: 'ServiceStatusPanel',
  props: {
    service: {
      type: Object,
      required: true
    }
  },
  emits: ['refresh'],
  setup(props, { emit }) {
    
    const getStatusText = (status) => {
      const statusMap = {
        online: '在线',
        offline: '离线',
        warning: '警告',
        error: '错误'
      }
      return statusMap[status] || '未知'
    }
    
    const formatTime = (timestamp) => {
      if (!timestamp) return 'N/A'
      
      const now = new Date()
      const time = new Date(timestamp)
      const diff = now - time
      
      if (diff < 60000) { // 小于1分钟
        return '刚刚'
      } else if (diff < 3600000) { // 小于1小时
        return `${Math.floor(diff / 60000)}分钟前`
      } else if (diff < 86400000) { // 小于1天
        return `${Math.floor(diff / 3600000)}小时前`
      } else {
        return time.toLocaleString('zh-CN')
      }
    }
    
    const handleCommand = (command) => {
      switch (command) {
        case 'details':
          ElMessage.info(`查看 ${props.service.name} 详情`)
          break
        case 'logs':
          ElMessage.info(`查看 ${props.service.name} 日志`)
          break
        case 'restart':
          ElMessage.warning(`重启 ${props.service.name} 服务`)
          break
      }
    }
    
    return {
      getStatusText,
      formatTime,
      handleCommand
    }
  }
}
</script>

<style scoped>
.service-status-panel {
  background: white;
  border-radius: 8px;
  border: 2px solid #e6f3ff;
  padding: 1.5rem;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.service-status-panel::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: #e6f3ff;
  transition: background 0.3s ease;
}

.service-status-panel.status-online::before {
  background: linear-gradient(90deg, #52c41a, #73d13d);
}

.service-status-panel.status-warning::before {
  background: linear-gradient(90deg, #faad14, #ffc53d);
}

.service-status-panel.status-error::before {
  background: linear-gradient(90deg, #ff4d4f, #ff7875);
}

.service-status-panel.status-offline::before {
  background: linear-gradient(90deg, #8c8c8c, #bfbfbf);
}

.service-status-panel:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
}

.service-info {
  flex: 1;
}

.service-name {
  font-size: 1.1rem;
  font-weight: 600;
  color: #333;
  margin: 0 0 0.25rem 0;
}

.service-id {
  font-size: 0.85rem;
  color: #666;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  position: relative;
}

.status-dot::after {
  content: '';
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  border-radius: 50%;
  opacity: 0.3;
  animation: pulse 2s infinite;
}

.dot-online {
  background: #52c41a;
}

.dot-online::after {
  background: #52c41a;
}

.dot-warning {
  background: #faad14;
}

.dot-warning::after {
  background: #faad14;
}

.dot-error {
  background: #ff4d4f;
}

.dot-error::after {
  background: #ff4d4f;
}

.dot-offline {
  background: #8c8c8c;
}

.dot-offline::after {
  background: #8c8c8c;
  animation: none;
}

.status-text {
  font-size: 0.9rem;
  font-weight: 500;
  color: #333;
}

.panel-content {
  flex: 1;
}

.metrics-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.metric-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.metric-label {
  font-size: 0.8rem;
  color: #666;
  font-weight: 500;
}

.metric-value {
  display: flex;
  align-items: baseline;
  gap: 0.25rem;
}

.value-number {
  font-size: 1.1rem;
  font-weight: 600;
  color: #333;
}

.value-error {
  color: #ff4d4f;
}

.value-na {
  font-size: 1.1rem;
  font-weight: 600;
  color: #bfbfbf;
}

.value-unit {
  font-size: 0.8rem;
  color: #666;
}

.panel-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid #f0f0f0;
}

.last-heartbeat {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8rem;
  color: #666;
}

.panel-actions {
  display: flex;
  gap: 0.5rem;
}

@keyframes pulse {
  0% {
    opacity: 0.3;
    transform: scale(1);
  }
  50% {
    opacity: 0.8;
    transform: scale(1.2);
  }
  100% {
    opacity: 0.3;
    transform: scale(1);
  }
}

/* 响应式设计 */
@media (max-width: 480px) {
  .service-status-panel {
    padding: 1rem;
  }
  
  .panel-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .status-indicator {
    justify-content: flex-end;
  }
  
  .metrics-grid {
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }
  
  .panel-footer {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
}

/* 深色模式适配 */
@media (prefers-color-scheme: dark) {
  .service-status-panel {
    background: #3a3a3a;
    border-color: #4a4a4a;
  }
  
  .service-name {
    color: #fff;
  }
  
  .service-id {
    color: #ccc;
  }
  
  .status-text {
    color: #fff;
  }
  
  .metric-label {
    color: #ccc;
  }
  
  .value-number {
    color: #fff;
  }
  
  .last-heartbeat {
    color: #ccc;
  }
  
  .panel-footer {
    border-top-color: #4a4a4a;
  }
}
</style>
