<template>
  <div class="external-links">
    <div class="card border-0 shadow-sm">
      <div class="card-header bg-white border-bottom py-3">
        <div class="d-flex justify-content-between align-items-center">
          <h6 class="card-title mb-0">
            <el-icon class="me-2 text-primary"><Link /></el-icon>友情链接
          </h6>
          <el-button 
            v-if="canManage" 
            type="primary" 
            size="small"
            @click="showManageDialog = true"
          >
            <el-icon><Setting /></el-icon>
            管理
          </el-button>
        </div>
      </div>
      <div class="card-body" v-loading="loading">
        <div v-if="links.length === 0" class="text-center text-muted py-3">
          <el-icon style="font-size: 2rem; opacity: 0.5;"><Link /></el-icon>
          <p class="mt-2 mb-0">暂无友情链接</p>
        </div>
        <div v-else class="links-grid">
          <a
            v-for="link in links"
            :key="link.id"
            :href="link.url"
            target="_blank"
            rel="noopener noreferrer"
            class="link-item"
            :title="link.description"
          >
            <div class="link-icon">
              <el-icon v-if="link.icon">{{ getIconComponent(link.icon) }}</el-icon>
              <el-icon v-else><Link /></el-icon>
            </div>
            <span class="link-title">{{ link.title }}</span>
          </a>
        </div>
      </div>
    </div>

    <!-- 管理弹窗 -->
    <el-dialog
      v-model="showManageDialog"
      title="管理友情链接"
      width="800px"
      :before-close="handleCloseManage"
    >
      <div class="mb-3">
        <el-button type="primary" @click="showAddDialog = true">
          <el-icon><Plus /></el-icon>
          添加链接
        </el-button>
      </div>
      
      <el-table :data="allLinks" style="width: 100%">
        <el-table-column prop="title" label="标题" width="150" />
        <el-table-column prop="url" label="链接" min-width="200">
          <template #default="scope">
            <a :href="scope.row.url" target="_blank" class="text-primary">
              {{ scope.row.url }}
            </a>
          </template>
        </el-table-column>
        <el-table-column prop="link_type" label="类型" width="100" />
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'danger'">
              {{ scope.row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="order" label="排序" width="80" />
        <el-table-column label="操作" width="150">
          <template #default="scope">
            <el-button size="small" @click="editLink(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteLink(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <template #footer>
        <el-button @click="showManageDialog = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 添加/编辑弹窗 -->
    <el-dialog
      v-model="showAddDialog"
      :title="editingLink ? '编辑链接' : '添加链接'"
      width="500px"
    >
      <el-form
        ref="linkFormRef"
        :model="linkForm"
        :rules="linkRules"
        label-width="80px"
      >
        <el-form-item label="标题" prop="title">
          <el-input v-model="linkForm.title" placeholder="请输入链接标题" />
        </el-form-item>
        <el-form-item label="链接" prop="url">
          <el-input v-model="linkForm.url" placeholder="请输入链接地址" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="linkForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入链接描述"
          />
        </el-form-item>
        <el-form-item label="图标" prop="icon">
          <el-input v-model="linkForm.icon" placeholder="图标名称（可选）" />
        </el-form-item>
        <el-form-item label="类型" prop="link_type">
          <el-select v-model="linkForm.link_type" placeholder="请选择类型">
            <el-option label="网站" value="website" />
            <el-option label="工具" value="tool" />
            <el-option label="资源" value="resource" />
            <el-option label="文档" value="documentation" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="排序" prop="order">
          <el-input-number v-model="linkForm.order" :min="0" :max="999" />
        </el-form-item>
        <el-form-item label="状态" prop="is_active">
          <el-switch v-model="linkForm.is_active" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitLink">
          {{ submitting ? '保存中...' : '保存' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { linksAPI } from '@/api/home'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Link, Setting, Plus } from '@element-plus/icons-vue'

const authStore = useAuthStore()

const links = ref([])
const allLinks = ref([])
const loading = ref(true)
const showManageDialog = ref(false)
const showAddDialog = ref(false)
const submitting = ref(false)
const editingLink = ref(null)
const linkFormRef = ref()

const linkForm = reactive({
  title: '',
  url: '',
  description: '',
  icon: '',
  link_type: 'website',
  order: 0,
  is_active: true
})

const linkRules = {
  title: [
    { required: true, message: '请输入链接标题', trigger: 'blur' }
  ],
  url: [
    { required: true, message: '请输入链接地址', trigger: 'blur' },
    { type: 'url', message: '请输入正确的URL格式', trigger: 'blur' }
  ]
}

const canManage = computed(() => {
  const user = authStore.user
  if (!user) return false
  if (user.is_staff || user.is_superuser) return true
  if (user.groups && user.groups.includes('管理员')) return true
  if (user.permissions && user.permissions.includes('add_externallink')) return true
  return false
})

const getIconComponent = (iconName) => {
  // 这里可以根据图标名称返回对应的图标组件
  // 简单起见，统一返回Link图标
  return Link
}

const fetchLinks = async () => {
  try {
    loading.value = true
    const data = await linksAPI.getLinks()
    const list = Array.isArray(data) ? data : (data.results || [])
    links.value = list.filter(link => link.is_active)
    if (canManage.value) {
      allLinks.value = list
    }
  } catch (error) {
    console.error('获取友情链接失败:', error)
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  Object.assign(linkForm, {
    title: '',
    url: '',
    description: '',
    icon: '',
    link_type: 'website',
    order: 0,
    is_active: true
  })
  editingLink.value = null
}

const editLink = (link) => {
  editingLink.value = link
  Object.assign(linkForm, link)
  showAddDialog.value = true
}

const submitLink = async () => {
  if (!linkFormRef.value) return
  
  try {
    await linkFormRef.value.validate()
    submitting.value = true
    
    if (editingLink.value) {
      await linksAPI.updateLink(editingLink.value.id, linkForm)
      ElMessage.success('链接更新成功')
    } else {
      await linksAPI.createLink(linkForm)
      ElMessage.success('链接添加成功')
    }
    
    showAddDialog.value = false
    resetForm()
    fetchLinks()
    
  } catch (error) {
    console.error('保存链接失败:', error)
    ElMessage.error('保存失败，请重试')
  } finally {
    submitting.value = false
  }
}

const deleteLink = async (link) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除链接"${link.title}"吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await linksAPI.deleteLink(link.id)
    ElMessage.success('删除成功')
    fetchLinks()
    
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除链接失败:', error)
      ElMessage.error('删除失败，请重试')
    }
  }
}

const handleCloseManage = () => {
  showManageDialog.value = false
  resetForm()
}

onMounted(() => {
  fetchLinks()
})
</script>

<style scoped>
.links-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 0.75rem;
}

.link-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.75rem;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  text-decoration: none;
  color: #606266;
  transition: all 0.3s ease;
  background: #fff;
}

.link-item:hover {
  color: #409eff;
  border-color: #409eff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
  text-decoration: none;
}

.link-icon {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
  color: #409eff;
}

.link-title {
  font-size: 0.8rem;
  text-align: center;
  line-height: 1.2;
}

.card {
  border-radius: 12px;
}

.card-header {
  border-radius: 12px 12px 0 0 !important;
}

@media (max-width: 768px) {
  .links-grid {
    grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
    gap: 0.5rem;
  }
  
  .link-item {
    padding: 0.5rem;
  }
  
  .link-icon {
    font-size: 1.2rem;
  }
  
  .link-title {
    font-size: 0.75rem;
  }
}
</style>
