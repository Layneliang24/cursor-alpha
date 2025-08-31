<template>
  <el-dialog
    v-model="dialogVisible"
    :title="isEdit ? '编辑提示模板' : '新建提示模板'"
    width="60%"
    :before-close="handleClose"
    destroy-on-close
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-width="100px"
      label-position="top"
    >
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="模板名称" prop="name">
            <el-input
              v-model="formData.name"
              placeholder="请输入模板名称"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="分类" prop="category">
            <el-select
              v-model="formData.category"
              placeholder="请选择分类"
              style="width: 100%"
            >
              <el-option
                v-for="category in categories"
                :key="category.value"
                :label="category.label"
                :value="category.value"
              />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="描述" prop="description">
        <el-input
          v-model="formData.description"
          placeholder="请输入模板描述"
          clearable
        />
      </el-form-item>

      <el-form-item label="模板内容" prop="content">
        <el-input
          v-model="formData.content"
          type="textarea"
          :rows="8"
          placeholder="请输入提示模板内容"
          show-word-limit
          maxlength="2000"
        />
      </el-form-item>

      <el-form-item label="可见性">
        <el-radio-group v-model="formData.is_public">
          <el-radio :label="false">私有 (仅自己可见)</el-radio>
          <el-radio :label="true">公开 (所有用户可见)</el-radio>
        </el-radio-group>
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ isEdit ? '更新' : '创建' }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script>
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useAIConfigStore } from '@/stores/modules/aiConfigStore'

export default {
  name: 'PromptTemplateDialog',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    template: {
      type: Object,
      default: null
    }
  },
  emits: ['update:visible', 'success'],
  setup(props, { emit }) {
    const aiConfigStore = useAIConfigStore()
    const formRef = ref()
    const submitting = ref(false)
    
    // 表单数据
    const formData = reactive({
      name: '',
      description: '',
      content: '',
      category: 'general',
      is_public: false
    })
    
    // 分类选项
    const categories = [
      { value: 'general', label: '通用' },
      { value: 'coding', label: '编程' },
      { value: 'writing', label: '写作' },
      { value: 'analysis', label: '分析' },
      { value: 'translation', label: '翻译' },
      { value: 'creative', label: '创意' },
      { value: 'education', label: '教育' },
      { value: 'business', label: '商务' },
      { value: 'custom', label: '自定义' }
    ]
    
    // 计算属性
    const dialogVisible = computed({
      get: () => props.visible,
      set: (value) => emit('update:visible', value)
    })
    
    const isEdit = computed(() => !!props.template?.id)
    
    // 表单验证规则
    const formRules = {
      name: [
        { required: true, message: '请输入模板名称', trigger: 'blur' },
        { min: 2, max: 50, message: '模板名称长度在 2 到 50 个字符', trigger: 'blur' }
      ],
      content: [
        { required: true, message: '请输入模板内容', trigger: 'blur' },
        { min: 10, max: 2000, message: '模板内容长度在 10 到 2000 个字符', trigger: 'blur' }
      ],
      category: [
        { required: true, message: '请选择分类', trigger: 'change' }
      ]
    }
    
    // 方法
    const initializeForm = () => {
      if (props.template) {
        Object.assign(formData, {
          name: props.template.name || '',
          description: props.template.description || '',
          content: props.template.content || '',
          category: props.template.category || 'general',
          is_public: props.template.is_public || false
        })
      } else {
        // 重置表单
        Object.assign(formData, {
          name: '',
          description: '',
          content: '',
          category: 'general',
          is_public: false
        })
      }
    }
    
    const handleSubmit = async () => {
      try {
        const valid = await formRef.value.validate()
        if (!valid) return
        
        submitting.value = true
        
        let result
        if (isEdit.value) {
          result = await aiConfigStore.updatePromptTemplate(props.template.id, formData)
        } else {
          result = await aiConfigStore.createPromptTemplate(formData)
        }
        
        ElMessage.success(isEdit.value ? '模板更新成功' : '模板创建成功')
        emit('success', result)
        dialogVisible.value = false
      } catch (error) {
        ElMessage.error(isEdit.value ? '更新模板失败' : '创建模板失败')
        console.error('提交失败:', error)
      } finally {
        submitting.value = false
      }
    }
    
    const handleClose = () => {
      dialogVisible.value = false
      // 延迟重置表单，避免关闭动画期间看到数据变化
      setTimeout(() => {
        formRef.value?.resetFields()
      }, 300)
    }
    
    // 监听props变化
    watch(() => props.visible, (visible) => {
      if (visible) {
        initializeForm()
      }
    })
    
    watch(() => props.template, () => {
      if (props.visible) {
        initializeForm()
      }
    }, { deep: true })
    
    return {
      formRef,
      formData,
      formRules,
      submitting,
      categories,
      dialogVisible,
      isEdit,
      handleSubmit,
      handleClose
    }
  }
}
</script>

<style scoped>
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

:deep(.el-dialog__body) {
  padding-top: 1rem;
}

:deep(.el-textarea__inner) {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 0.9rem;
  line-height: 1.5;
}

/* 响应式设计 */
@media (max-width: 768px) {
  :deep(.el-dialog) {
    width: 95% !important;
    margin: 5vh auto;
  }
}
</style>
