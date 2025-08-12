<template>
  <el-dialog
    v-model="visible"
    title="创建学习计划"
    width="600px"
    :before-close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="120px"
      @submit.prevent
    >
      <el-form-item label="计划名称" prop="name">
        <el-input
          v-model="form.name"
          placeholder="请输入学习计划名称"
          maxlength="50"
          show-word-limit
        />
      </el-form-item>

      <el-form-item label="计划描述" prop="description">
        <el-input
          v-model="form.description"
          type="textarea"
          :rows="3"
          placeholder="请描述您的学习计划"
          maxlength="200"
          show-word-limit
        />
      </el-form-item>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="每日单词目标" prop="daily_word_target">
            <el-input-number
              v-model="form.daily_word_target"
              :min="1"
              :max="100"
              controls-position="right"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="每日表达目标" prop="daily_expression_target">
            <el-input-number
              v-model="form.daily_expression_target"
              :min="1"
              :max="50"
              controls-position="right"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="复习频率" prop="review_frequency">
        <el-radio-group v-model="form.review_frequency">
          <el-radio label="daily">每日复习</el-radio>
          <el-radio label="weekly">每周复习</el-radio>
          <el-radio label="custom">自定义</el-radio>
        </el-radio-group>
      </el-form-item>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="开始日期" prop="start_date">
            <el-date-picker
              v-model="form.start_date"
              type="date"
              placeholder="选择开始日期"
              style="width: 100%"
              :disabled-date="disabledStartDate"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="结束日期" prop="end_date">
            <el-date-picker
              v-model="form.end_date"
              type="date"
              placeholder="选择结束日期（可选）"
              style="width: 100%"
              :disabled-date="disabledEndDate"
            />
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="是否激活" prop="is_active">
        <el-switch
          v-model="form.is_active"
          active-text="立即激活此计划"
          inactive-text="暂不激活"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          创建计划
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script>
import { ref, reactive, computed, watch } from 'vue'
import { useEnglishStore } from '@/stores/english'
import { ElMessage } from 'element-plus'

export default {
  name: 'PlanDialog',
  props: {
    modelValue: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:modelValue', 'created'],
  setup(props, { emit }) {
    const englishStore = useEnglishStore()
    const formRef = ref(null)
    const submitting = ref(false)

    // 表单数据
    const form = reactive({
      name: '',
      description: '',
      daily_word_target: 10,
      daily_expression_target: 5,
      review_frequency: 'daily',
      start_date: new Date(),
      end_date: null,
      is_active: true
    })

    // 表单验证规则
    const rules = {
      name: [
        { required: true, message: '请输入计划名称', trigger: 'blur' },
        { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
      ],
      daily_word_target: [
        { required: true, message: '请设置每日单词目标', trigger: 'blur' },
        { type: 'number', min: 1, max: 100, message: '目标应在 1 到 100 之间', trigger: 'blur' }
      ],
      daily_expression_target: [
        { required: true, message: '请设置每日表达目标', trigger: 'blur' },
        { type: 'number', min: 1, max: 50, message: '目标应在 1 到 50 之间', trigger: 'blur' }
      ],
      review_frequency: [
        { required: true, message: '请选择复习频率', trigger: 'change' }
      ],
      start_date: [
        { required: true, message: '请选择开始日期', trigger: 'change' }
      ]
    }

    // 计算属性
    const visible = computed({
      get: () => props.modelValue,
      set: (value) => emit('update:modelValue', value)
    })

    // 方法
    const disabledStartDate = (time) => {
      return time.getTime() < Date.now() - 24 * 60 * 60 * 1000
    }

    const disabledEndDate = (time) => {
      if (!form.start_date) return false
      return time.getTime() < new Date(form.start_date).getTime()
    }

    const resetForm = () => {
      Object.assign(form, {
        name: '',
        description: '',
        daily_word_target: 10,
        daily_expression_target: 5,
        review_frequency: 'daily',
        start_date: new Date(),
        end_date: null,
        is_active: true
      })
      if (formRef.value) {
        formRef.value.clearValidate()
      }
    }

    const handleClose = () => {
      visible.value = false
      resetForm()
    }

    const handleSubmit = async () => {
      if (!formRef.value) return

      try {
        await formRef.value.validate()
        submitting.value = true

        // 格式化日期
        const submitData = {
          ...form,
          start_date: form.start_date.toISOString().split('T')[0],
          end_date: form.end_date ? form.end_date.toISOString().split('T')[0] : null
        }

        await englishStore.createLearningPlan(submitData)
        
        ElMessage.success('学习计划创建成功')
        emit('created')
        handleClose()
      } catch (error) {
        console.error('创建学习计划失败:', error)
        ElMessage.error(error.message || '创建学习计划失败')
      } finally {
        submitting.value = false
      }
    }

    // 监听对话框显示状态
    watch(visible, (newVal) => {
      if (newVal) {
        resetForm()
      }
    })

    return {
      formRef,
      form,
      rules,
      visible,
      submitting,
      disabledStartDate,
      disabledEndDate,
      handleClose,
      handleSubmit
    }
  }
}
</script>

<style scoped>
.dialog-footer {
  text-align: right;
}

.el-form-item {
  margin-bottom: 24px;
}

.el-input-number {
  width: 100%;
}

:deep(.el-radio-group) {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

:deep(.el-radio) {
  margin-right: 0;
}
</style>
