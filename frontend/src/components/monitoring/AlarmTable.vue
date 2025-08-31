<template>
  <div class="alarm-table">
    <!-- 过滤器 -->
    <div class="table-filters">
      <div class="filter-group">
        <el-select
          v-model="levelFilter"
          placeholder="告警级别"
          clearable
          size="small"
          style="width: 120px;"
          @change="handleFilterChange"
        >
          <el-option label="错误" value="error" />
          <el-option label="警告" value="warning" />
          <el-option label="信息" value="info" />
        </el-select>
        
        <el-select
          v-model="serviceFilter"
          placeholder="服务"
          clearable
          size="small"
          style="width: 150px;"
          @change="handleFilterChange"
        >
          <el-option
            v-for="service in serviceOptions"
            :key="service"
            :label="service"
            :value="service"
          />
        </el-select>
        
        <el-input
          v-model="searchKeyword"
          placeholder="搜索消息..."
          clearable
          size="small"
          style="width: 200px;"
          @input="handleSearch"
        >
          <template #prefix>
            <i class="el-icon-search"></i>
          </template>
        </el-input>
      </div>
      
      <div class="filter-actions">
        <el-button size="small" @click="markAllAsRead" :disabled="unreadCount === 0">
          <i class="el-icon-check"></i>
          全部已读
        </el-button>
        <el-button size="small" type="danger" @click="$emit('clear-alarms')">
          <i class="el-icon-delete"></i>
          清空日志
        </el-button>
      </div>
    </div>
    
    <!-- 表格 -->
    <el-table
      :data="filteredAlarms"
      :loading="loading"
      stripe
      size="small"
      height="400"
      @row-click="markAsRead"
      class="alarms-table"
    >
      <el-table-column width="60" align="center">
        <template #default="{ row }">
          <div class="read-indicator" :class="{ 'unread': !row.isRead }">
            <div class="read-dot"></div>
          </div>
        </template>
      </el-table-column>
      
      <el-table-column prop="timestamp" label="时间" width="160" sortable>
        <template #default="{ row }">
          <div class="timestamp">
            {{ formatTimestamp(row.timestamp) }}
          </div>
        </template>
      </el-table-column>
      
      <el-table-column prop="level" label="级别" width="80" align="center">
        <template #default="{ row }">
          <el-tag
            :type="getLevelTagType(row.level)"
            size="small"
            class="level-tag"
          >
            {{ getLevelText(row.level) }}
          </el-tag>
        </template>
      </el-table-column>
      
      <el-table-column prop="service" label="服务" width="140">
        <template #default="{ row }">
          <div class="service-name">
            {{ getServiceDisplayName(row.service) }}
          </div>
        </template>
      </el-table-column>
      
      <el-table-column prop="message" label="消息" min-width="200">
        <template #default="{ row }">
          <div class="alarm-message" :class="{ 'unread-message': !row.isRead }">
            {{ row.message }}
          </div>
        </template>
      </el-table-column>
      
      <el-table-column label="操作" width="100" align="center">
        <template #default="{ row }">
          <div class="row-actions">
            <el-tooltip content="标记为已读" v-if="!row.isRead">
              <el-button size="mini" @click.stop="markAsRead(row)">
                <i class="el-icon-check"></i>
              </el-button>
            </el-tooltip>
            <el-tooltip content="查看详情">
              <el-button size="mini" @click.stop="showDetails(row)">
                <i class="el-icon-view"></i>
              </el-button>
            </el-tooltip>
          </div>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 分页 -->
    <div class="table-pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="filteredAlarms.length"
        layout="total, sizes, prev, pager, next, jumper"
        small
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
    
    <!-- 告警详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="告警详情"
      width="500px"
      destroy-on-close
    >
      <div v-if="selectedAlarm" class="alarm-details">
        <div class="detail-item">
          <label>时间:</label>
          <span>{{ formatTimestamp(selectedAlarm.timestamp, true) }}</span>
        </div>
        <div class="detail-item">
          <label>级别:</label>
          <el-tag :type="getLevelTagType(selectedAlarm.level)" size="small">
            {{ getLevelText(selectedAlarm.level) }}
          </el-tag>
        </div>
        <div class="detail-item">
          <label>服务:</label>
          <span>{{ getServiceDisplayName(selectedAlarm.service) }}</span>
        </div>
        <div class="detail-item">
          <label>消息:</label>
          <div class="detail-message">{{ selectedAlarm.message }}</div>
        </div>
        <div class="detail-item">
          <label>ID:</label>
          <code>{{ selectedAlarm.id }}</code>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'

export default {
  name: 'AlarmTable',
  props: {
    alarms: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['filter-change', 'clear-alarms'],
  setup(props, { emit }) {
    
    // 响应式数据
    const levelFilter = ref('')
    const serviceFilter = ref('')
    const searchKeyword = ref('')
    const currentPage = ref(1)
    const pageSize = ref(20)
    const detailDialogVisible = ref(false)
    const selectedAlarm = ref(null)
    
    // 计算属性
    const serviceOptions = computed(() => {
      const services = [...new Set(props.alarms.map(alarm => alarm.service))]
      return services.sort()
    })
    
    const unreadCount = computed(() => {
      return props.alarms.filter(alarm => !alarm.isRead).length
    })
    
    const filteredAlarms = computed(() => {
      let filtered = [...props.alarms]
      
      // 级别过滤
      if (levelFilter.value) {
        filtered = filtered.filter(alarm => alarm.level === levelFilter.value)
      }
      
      // 服务过滤
      if (serviceFilter.value) {
        filtered = filtered.filter(alarm => alarm.service === serviceFilter.value)
      }
      
      // 关键词搜索
      if (searchKeyword.value.trim()) {
        const keyword = searchKeyword.value.trim().toLowerCase()
        filtered = filtered.filter(alarm => 
          alarm.message.toLowerCase().includes(keyword) ||
          alarm.service.toLowerCase().includes(keyword)
        )
      }
      
      // 分页
      const start = (currentPage.value - 1) * pageSize.value
      const end = start + pageSize.value
      return filtered.slice(start, end)
    })
    
    // 方法
    const getLevelTagType = (level) => {
      const typeMap = {
        error: 'danger',
        warning: 'warning',
        info: 'info'
      }
      return typeMap[level] || 'info'
    }
    
    const getLevelText = (level) => {
      const textMap = {
        error: '错误',
        warning: '警告',
        info: '信息'
      }
      return textMap[level] || level
    }
    
    const getServiceDisplayName = (serviceId) => {
      const nameMap = {
        'openai-gpt4': 'OpenAI GPT-4',
        'claude-sonnet': 'Claude Sonnet',
        'gemini-pro': 'Gemini Pro',
        'local-llama': 'Local Llama'
      }
      return nameMap[serviceId] || serviceId
    }
    
    const formatTimestamp = (timestamp, detailed = false) => {
      if (!timestamp) return 'N/A'
      
      const date = new Date(timestamp)
      
      if (detailed) {
        return date.toLocaleString('zh-CN')
      }
      
      const now = new Date()
      const diff = now - date
      
      if (diff < 60000) { // 小于1分钟
        return '刚刚'
      } else if (diff < 3600000) { // 小于1小时
        return `${Math.floor(diff / 60000)}分钟前`
      } else if (diff < 86400000) { // 小于1天
        const hours = Math.floor(diff / 3600000)
        return `${hours}小时前`
      } else {
        return date.toLocaleDateString('zh-CN')
      }
    }
    
    const handleFilterChange = () => {
      currentPage.value = 1 // 重置到第一页
      emit('filter-change', {
        level: levelFilter.value,
        service: serviceFilter.value,
        keyword: searchKeyword.value
      })
    }
    
    const handleSearch = () => {
      // 防抖搜索
      clearTimeout(handleSearch.timer)
      handleSearch.timer = setTimeout(() => {
        handleFilterChange()
      }, 300)
    }
    
    const handleSizeChange = (size) => {
      pageSize.value = size
      currentPage.value = 1
    }
    
    const handleCurrentChange = (page) => {
      currentPage.value = page
    }
    
    const markAsRead = (alarm) => {
      if (!alarm.isRead) {
        alarm.isRead = true
        ElMessage.success('已标记为已读')
      }
    }
    
    const markAllAsRead = () => {
      props.alarms.forEach(alarm => {
        alarm.isRead = true
      })
      ElMessage.success(`已标记 ${unreadCount.value} 条告警为已读`)
    }
    
    const showDetails = (alarm) => {
      selectedAlarm.value = alarm
      detailDialogVisible.value = true
      markAsRead(alarm)
    }
    
    // 监听告警数组变化，重置分页
    watch(() => props.alarms.length, () => {
      currentPage.value = 1
    })
    
    return {
      // 数据
      levelFilter,
      serviceFilter,
      searchKeyword,
      currentPage,
      pageSize,
      detailDialogVisible,
      selectedAlarm,
      
      // 计算属性
      serviceOptions,
      unreadCount,
      filteredAlarms,
      
      // 方法
      getLevelTagType,
      getLevelText,
      getServiceDisplayName,
      formatTimestamp,
      handleFilterChange,
      handleSearch,
      handleSizeChange,
      handleCurrentChange,
      markAsRead,
      markAllAsRead,
      showDetails
    }
  }
}
</script>

<style scoped>
.alarm-table {
  background: white;
  border-radius: 8px;
}

.table-filters {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 0;
  margin-bottom: 1rem;
  border-bottom: 1px solid #f0f0f0;
}

.filter-group {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.filter-actions {
  display: flex;
  gap: 0.5rem;
}

.alarms-table {
  border-radius: 8px;
  overflow: hidden;
}

.read-indicator {
  display: flex;
  justify-content: center;
  align-items: center;
}

.read-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: transparent;
  transition: background 0.3s ease;
}

.read-indicator.unread .read-dot {
  background: #1890ff;
  box-shadow: 0 0 6px rgba(24, 144, 255, 0.5);
}

.timestamp {
  font-size: 0.85rem;
  color: #666;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

.level-tag {
  font-weight: 500;
}

.service-name {
  font-size: 0.9rem;
  color: #333;
}

.alarm-message {
  font-size: 0.9rem;
  color: #666;
  line-height: 1.4;
  word-break: break-word;
}

.alarm-message.unread-message {
  color: #333;
  font-weight: 500;
}

.row-actions {
  display: flex;
  justify-content: center;
  gap: 0.25rem;
}

.table-pagination {
  display: flex;
  justify-content: center;
  padding: 1.5rem 0;
  border-top: 1px solid #f0f0f0;
  margin-top: 1rem;
}

/* 告警详情对话框 */
.alarm-details {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.detail-item {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
}

.detail-item label {
  min-width: 60px;
  font-weight: 600;
  color: #333;
}

.detail-message {
  flex: 1;
  padding: 0.5rem;
  background: #f5f5f5;
  border-radius: 4px;
  font-size: 0.9rem;
  line-height: 1.5;
  word-break: break-word;
}

.detail-item code {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  background: #f5f5f5;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .table-filters {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .filter-group {
    flex-wrap: wrap;
    justify-content: space-between;
  }
  
  .filter-actions {
    justify-content: center;
  }
  
  .alarms-table :deep(.el-table__body-wrapper) {
    overflow-x: auto;
  }
}

/* 深色模式适配 */
@media (prefers-color-scheme: dark) {
  .alarm-table {
    background: #3a3a3a;
  }
  
  .table-filters {
    border-bottom-color: #4a4a4a;
  }
  
  .timestamp {
    color: #ccc;
  }
  
  .service-name {
    color: #fff;
  }
  
  .alarm-message {
    color: #ccc;
  }
  
  .alarm-message.unread-message {
    color: #fff;
  }
  
  .table-pagination {
    border-top-color: #4a4a4a;
  }
  
  .detail-item label {
    color: #fff;
  }
  
  .detail-message,
  .detail-item code {
    background: #4a4a4a;
    color: #fff;
  }
}
</style>
