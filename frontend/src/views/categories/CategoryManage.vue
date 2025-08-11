<template>
  <div class="category-manage-container">
    <div class="page-header">
      <h1>分类管理</h1>
      <el-button type="primary" @click="openCreate">新建分类</el-button>
    </div>

    <el-table :data="categories" v-loading="loading" border>
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column label="名称">
        <template #default="{ row }">
          <el-tag :style="{ backgroundColor: row.color, color: '#fff', borderColor: row.color }" effect="dark">
            {{ row.name }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="article_count" label="文章数" width="90" />
      <el-table-column prop="order" label="排序" width="90" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 'active' ? 'success' : 'info'">{{ row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="220">
        <template #default="{ row }">
          <el-button size="small" @click="openEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="confirmDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑分类' : '新建分类'" width="520px">
      <el-form ref="formRef" :model="form" :rules="formRules" label-width="90px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入分类名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="分类描述" />
        </el-form-item>
        <el-form-item label="父分类">
          <el-select v-model="form.parent" placeholder="选择父分类" clearable filterable style="width: 100%">
            <el-option v-for="c in parentOptions" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width: 100%">
            <el-option label="激活" value="active" />
            <el-option label="未激活" value="inactive" />
          </el-select>
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.order" :min="0" :max="9999" />
        </el-form-item>
        <el-form-item label="图标">
          <el-input v-model="form.icon" placeholder="可填 emoji 或关键字，如 vue/python/docker/.net" />
        </el-form-item>
        <el-form-item label="颜色">
          <el-color-picker v-model="form.color" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { categoriesAPI } from '@/api/categories'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const loading = ref(false)
const saving = ref(false)
const categories = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref()

const form = reactive({
  id: null,
  name: '',
  description: '',
  parent: null,
  status: 'active',
  order: 0,
  icon: '',
  color: '#409EFF'
})

const formRules = {
  name: [
    { required: true, message: '请输入分类名称', trigger: 'blur' },
    { min: 1, max: 100, message: '分类名称长度在 1 到 100 个字符', trigger: 'blur' }
  ]
}

const parentOptions = computed(() => categories.value.filter(c => !isEdit.value || c.id !== form.id))

const fetchCategories = async () => {
  loading.value = true
  try {
    const res = await categoriesAPI.getCategories()
    categories.value = res.results || res || []
  } catch (e) {
    console.error(e)
    ElMessage.error('获取分类失败')
  } finally {
    loading.value = false
  }
}

const openCreate = () => {
  isEdit.value = false
  Object.assign(form, { id: null, name: '', description: '', parent: null, status: 'active', order: 0, icon: '', color: '#409EFF' })
  dialogVisible.value = true
}

const openEdit = (row) => {
  isEdit.value = true
  Object.assign(form, { ...row })
  dialogVisible.value = true
}

const handleSave = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    saving.value = true
    
    if (isEdit.value && form.id) {
      await categoriesAPI.updateCategory(form.id, { ...form })
      ElMessage.success('更新成功')
    } else {
      // 创建时排除id字段
      const { id, ...createData } = form
      await categoriesAPI.createCategory(createData)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    await fetchCategories()
  } catch (e) {
    if (e.message) {
      // 表单验证错误，不需要显示
      return
    }
    console.error('保存分类失败:', e)
    // 显示具体的错误信息
    if (e.response?.data) {
      const errors = e.response.data
      if (typeof errors === 'object') {
        for (const field in errors) {
          if (Array.isArray(errors[field])) {
            ElMessage.error(`${field}: ${errors[field][0]}`)
          } else if (typeof errors[field] === 'string') {
            ElMessage.error(errors[field])
          }
        }
      } else if (typeof errors === 'string') {
        ElMessage.error(errors)
      }
    } else if (e.message) {
      ElMessage.error(e.message)
    } else {
      ElMessage.error('保存失败，请检查输入参数')
    }
  } finally {
    saving.value = false
  }
}

const confirmDelete = (row) => {
  ElMessageBox.confirm(`确定删除分类「${row.name}」？此操作可能影响所属文章。`, '提示', {
    type: 'warning'
  }).then(async () => {
    try {
      await categoriesAPI.deleteCategory(row.id)
      ElMessage.success('已删除')
      await fetchCategories()
    } catch (e) {
      console.error(e)
    }
  }).catch(() => {})
}

onMounted(fetchCategories)
</script>

<style scoped>
.category-manage-container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 20px;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
</style>




