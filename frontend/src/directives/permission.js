import { usePermissions } from '@/composables/usePermissions'

/**
 * 权限指令
 * 用法：
 * v-permission="'ai_config.manage'" - 检查单个权限
 * v-permission="['ai_config.view', 'ai_config.edit']" - 检查多个权限（任一）
 * v-permission:all="['ai_config.view', 'ai_config.edit']" - 检查多个权限（全部）
 * v-permission:role="'admin'" - 检查角色
 * v-permission:level="5" - 检查级别
 */
export const permissionDirective = {
  mounted(el, binding) {
    checkPermission(el, binding)
  },
  
  updated(el, binding) {
    checkPermission(el, binding)
  }
}

function checkPermission(el, binding) {
  const { hasPermission, hasAnyPermission, hasAllPermissions, hasRole, hasLevel } = usePermissions()
  
  const { value, arg, modifiers } = binding
  let hasPermissionFlag = false
  
  if (!value) {
    // 没有指定权限要求，默认显示
    hasPermissionFlag = true
  } else if (arg === 'role') {
    // 角色检查
    if (Array.isArray(value)) {
      hasPermissionFlag = value.some(role => hasRole(role))
    } else {
      hasPermissionFlag = hasRole(value)
    }
  } else if (arg === 'level') {
    // 级别检查
    hasPermissionFlag = hasLevel(value)
  } else {
    // 权限检查
    if (Array.isArray(value)) {
      if (modifiers.all || arg === 'all') {
        // 需要所有权限
        hasPermissionFlag = hasAllPermissions(value)
      } else {
        // 需要任一权限
        hasPermissionFlag = hasAnyPermission(value)
      }
    } else {
      // 单个权限
      hasPermissionFlag = hasPermission(value)
    }
  }
  
  if (!hasPermissionFlag) {
    // 没有权限，隐藏元素
    if (modifiers.hide) {
      el.style.visibility = 'hidden'
    } else {
      el.style.display = 'none'
    }
    
    // 添加无权限标记
    el.classList.add('no-permission')
  } else {
    // 有权限，显示元素
    if (modifiers.hide) {
      el.style.visibility = 'visible'
    } else {
      el.style.display = ''
    }
    
    // 移除无权限标记
    el.classList.remove('no-permission')
  }
}

// 全局注册指令
export default {
  install(app) {
    app.directive('permission', permissionDirective)
  }
}
