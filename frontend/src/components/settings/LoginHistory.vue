<template>
  <div class="login-history">
    <div class="settings-section">
      <h3 class="section-title">登录历史</h3>
      
      <el-table
        :data="loginHistory"
        style="width: 100%"
        v-loading="loading"
        class="history-table"
      >
        <el-table-column prop="login_time" label="登录时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.login_time) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="ip_address" label="IP地址" width="140" />
        
        <el-table-column prop="location" label="登录地点" width="150" />
        
        <el-table-column prop="device_type" label="设备类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getDeviceTypeColor(row.device_type)">
              {{ getDeviceTypeLabel(row.device_type) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="browser" label="浏览器" width="120" />
        
        <el-table-column prop="os" label="操作系统" width="120" />
        
        <el-table-column prop="success" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.success ? 'success' : 'danger'">
              {{ row.success ? '成功' : '失败' }}
            </el-tag>
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
import { ElMessage } from 'element-plus'
import { loginHistoryAPI } from '@/api/settings'
import { formatDateTime } from '@/utils/date'

const loading = ref(false)
const loginHistory = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const loadLoginHistory = async () => {
  try {
    loading.value = true
    const response = await loginHistoryAPI.getLoginHistory({
      page: currentPage.value,
      page_size: pageSize.value
    })
    
    loginHistory.value = response.data.results || []
    total.value = response.data.count || 0
  } catch (error) {
    ElMessage.error('获取登录历史失败')
  } finally {
    loading.value = false
  }
}

const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
  loadLoginHistory()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  loadLoginHistory()
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
  loadLoginHistory()
})
</script>

<style scoped>
.login-history {
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

.history-table {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.table-footer {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style>
