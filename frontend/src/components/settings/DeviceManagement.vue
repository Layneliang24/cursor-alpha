<template>
  <div class="device-management">
    <div class="settings-section">
      <h3 class="section-title">设备管理</h3>
      
      <div class="device-actions">
        <el-button type="danger" @click="terminateAllSessions" :loading="terminatingAll">
          终止所有会话
        </el-button>
      </div>
      
      <el-table
        :data="deviceSessions"
        style="width: 100%"
        v-loading="loading"
        class="device-table"
      >
        <el-table-column prop="device_name" label="设备名称" width="200" />
        
        <el-table-column prop="device_type" label="设备类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getDeviceTypeColor(row.device_type)">
              {{ getDeviceTypeLabel(row.device_type) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="ip_address" label="IP地址" width="140" />
        
        <el-table-column prop="browser" label="浏览器" width="120" />
        
        <el-table-column prop="os" label="操作系统" width="120" />
        
        <el-table-column prop="last_activity" label="最后活动" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.last_activity) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">
              {{ row.is_active ? '活跃' : '已终止' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button
              v-if="row.is_active"
              type="danger"
              size="small"
              @click="terminateSession(row.id)"
              :loading="terminatingSession === row.id"
            >
              终止
            </el-button>
            <span v-else class="terminated-text">已终止</span>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="table-footer">
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
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { deviceSessionAPI } from '@/api/settings'
import { formatDateTime } from '@/utils/date'

const loading = ref(false)
const deviceSessions = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const terminatingSession = ref(null)
const terminatingAll = ref(false)

const loadDeviceSessions = async () => {
  try {
    loading.value = true
    const response = await deviceSessionAPI.getDeviceSessions({
      page: currentPage.value,
      page_size: pageSize.value
    })
    
    deviceSessions.value = response.data.results || []
    total.value = response.data.count || 0
  } catch (error) {
    ElMessage.error('获取设备会话失败')
  } finally {
    loading.value = false
  }
}

const terminateSession = async (sessionId) => {
  try {
    await ElMessageBox.confirm('确定要终止这个设备会话吗？', '确认终止', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    terminatingSession.value = sessionId
    await deviceSessionAPI.terminateSession(sessionId)
    
    ElMessage.success('会话已终止')
    loadDeviceSessions()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('终止会话失败')
    }
  } finally {
    terminatingSession.value = null
  }
}

const terminateAllSessions = async () => {
  try {
    await ElMessageBox.confirm('确定要终止所有设备会话吗？这将使您在所有设备上退出登录。', '确认终止', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    terminatingAll.value = true
    await deviceSessionAPI.terminateAllSessions()
    
    ElMessage.success('所有会话已终止')
    loadDeviceSessions()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('终止所有会话失败')
    }
  } finally {
    terminatingAll.value = false
  }
}

const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
  loadDeviceSessions()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  loadDeviceSessions()
}

const getDeviceTypeColor = (type) => {
  const colors = {
    desktop: 'primary',
    mobile: 'success',
    tablet: 'warning'
  }
  return colors[type] || 'info'
}

const getDeviceTypeLabel = (type) => {
  const labels = {
    desktop: '桌面',
    mobile: '移动',
    tablet: '平板'
  }
  return labels[type] || type
}

onMounted(() => {
  loadDeviceSessions()
})
</script>

<style scoped>
.device-management {
  max-width: 1200px;
}

.settings-section {
  margin-bottom: 40px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid #409eff;
}

.device-actions {
  margin-bottom: 20px;
}

.device-table {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.terminated-text {
  color: #909399;
  font-size: 12px;
}

.table-footer {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style>
