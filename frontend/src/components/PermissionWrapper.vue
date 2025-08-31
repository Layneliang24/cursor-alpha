<template>
  <div v-if="hasPermissionFlag" :class="wrapperClass">
    <slot />
  </div>
  <div v-else-if="showFallback" class="permission-fallback">
    <slot name="fallback">
      <div class="no-permission-message">
        <el-icon class="no-permission-icon"><Lock /></el-icon>
        <p class="no-permission-text">{{ fallbackMessage }}</p>
      </div>
    </slot>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Lock } from '@element-plus/icons-vue'
import { usePermissions } from '@/composables/usePermissions'

// Props
const props = defineProps({
  // 权限配置
  permission: {
    type: [String, Array],
    default: null
  },
  
  // 角色配置
  role: {
    type: [String, Array],
    default: null
  },
  
  // 级别配置
  level: {
    type: Number,
    default: null
  },
  
  // 权限检查模式
  mode: {
    type: String,
    default: 'any', // 'any' | 'all'
    validator: (value) => ['any', 'all'].includes(value)
  },
  
  // 是否显示无权限提示
  showFallback: {
    type: Boolean,
    default: false
  },
  
  // 无权限提示消息
  fallbackMessage: {
    type: String,
    default: '抱歉，您没有权限访问此功能'
  },
  
  // 包装器CSS类
  wrapperClass: {
    type: String,
    default: ''
  }
})

// 权限检查
const { hasPermission, hasAnyPermission, hasAllPermissions, hasRole, hasLevel } = usePermissions()

const hasPermissionFlag = computed(() => {
  // 角色检查优先
  if (props.role) {
    if (Array.isArray(props.role)) {
      return props.role.some(role => hasRole(role))
    } else {
      return hasRole(props.role)
    }
  }
  
  // 级别检查
  if (props.level !== null) {
    return hasLevel(props.level)
  }
  
  // 权限检查
  if (props.permission) {
    if (Array.isArray(props.permission)) {
      if (props.mode === 'all') {
        return hasAllPermissions(props.permission)
      } else {
        return hasAnyPermission(props.permission)
      }
    } else {
      return hasPermission(props.permission)
    }
  }
  
  // 没有配置权限要求，默认通过
  return true
})
</script>

<style scoped>
.permission-fallback {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  border: 2px dashed #e4e7ed;
  border-radius: 8px;
  background-color: #fafafa;
}

.no-permission-message {
  text-align: center;
  color: #909399;
}

.no-permission-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
  color: #f56c6c;
}

.no-permission-text {
  margin: 0;
  font-size: 0.9rem;
  line-height: 1.4;
}
</style>
