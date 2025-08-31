import { ref, computed, watch } from 'vue'
import { useUserStore } from '@/stores/modules/userStore'
import { storeToRefs } from 'pinia'

/**
 * 权限管理 Composable
 * 提供权限检查、角色管理等功能
 */
export function usePermissions() {
  const userStore = useUserStore()
  const { user, permissions, roles } = storeToRefs(userStore)
  
  // 权限缓存
  const permissionCache = ref(new Map())
  
  /**
   * 检查用户是否有指定权限
   * @param {string} permission - 权限代码，如 'ai_config.manage'
   * @returns {boolean}
   */
  const hasPermission = (permission) => {
    if (!permission) return true
    if (!user.value) return false
    
    // 超级用户拥有所有权限
    if (user.value.is_superuser) return true
    
    // 从缓存获取
    if (permissionCache.value.has(permission)) {
      return permissionCache.value.get(permission)
    }
    
    // 检查权限
    const hasPermission = permissions.value?.includes(permission) || false
    
    // 缓存结果
    permissionCache.value.set(permission, hasPermission)
    
    return hasPermission
  }
  
  /**
   * 检查用户是否有任意一个权限
   * @param {string[]} permissionList - 权限代码列表
   * @returns {boolean}
   */
  const hasAnyPermission = (permissionList) => {
    if (!permissionList || permissionList.length === 0) return true
    return permissionList.some(permission => hasPermission(permission))
  }
  
  /**
   * 检查用户是否有所有权限
   * @param {string[]} permissionList - 权限代码列表
   * @returns {boolean}
   */
  const hasAllPermissions = (permissionList) => {
    if (!permissionList || permissionList.length === 0) return true
    return permissionList.every(permission => hasPermission(permission))
  }
  
  /**
   * 检查用户是否有指定角色
   * @param {string} roleName - 角色名称
   * @returns {boolean}
   */
  const hasRole = (roleName) => {
    if (!roleName || !user.value) return false
    return roles.value?.some(role => role.name === roleName) || false
  }
  
  /**
   * 检查用户是否有任意一个角色
   * @param {string[]} roleList - 角色名称列表
   * @returns {boolean}
   */
  const hasAnyRole = (roleList) => {
    if (!roleList || roleList.length === 0) return true
    return roleList.some(roleName => hasRole(roleName))
  }
  
  /**
   * 获取用户角色级别
   * @returns {number} 最高角色级别
   */
  const getUserLevel = () => {
    if (!roles.value || roles.value.length === 0) return 0
    return Math.max(...roles.value.map(role => role.level || 0))
  }
  
  /**
   * 检查用户级别是否满足要求
   * @param {number} requiredLevel - 所需级别
   * @returns {boolean}
   */
  const hasLevel = (requiredLevel) => {
    return getUserLevel() >= requiredLevel
  }
  
  /**
   * 检查是否是管理员
   * @returns {boolean}
   */
  const isAdmin = computed(() => {
    return hasRole('admin') || hasRole('superadmin') || user.value?.is_staff || user.value?.is_superuser
  })
  
  /**
   * 检查是否是超级管理员
   * @returns {boolean}
   */
  const isSuperAdmin = computed(() => {
    return hasRole('superadmin') || user.value?.is_superuser
  })
  
  /**
   * AI配置相关权限检查
   */
  const aiPermissions = {
    canView: computed(() => hasPermission('ai_config.view')),
    canCreate: computed(() => hasPermission('ai_config.create')),
    canEdit: computed(() => hasPermission('ai_config.edit')),
    canDelete: computed(() => hasPermission('ai_config.delete')),
    canTest: computed(() => hasPermission('ai_config.test')),
    canManage: computed(() => hasPermission('ai_config.manage')),
  }
  
  /**
   * 用户管理相关权限检查
   */
  const userPermissions = {
    canView: computed(() => hasPermission('user.view')),
    canCreate: computed(() => hasPermission('user.create')),
    canEdit: computed(() => hasPermission('user.edit')),
    canDelete: computed(() => hasPermission('user.delete')),
    canManage: computed(() => hasPermission('user.manage')),
  }
  
  /**
   * 文章管理相关权限检查
   */
  const articlePermissions = {
    canView: computed(() => hasPermission('article.view')),
    canCreate: computed(() => hasPermission('article.create')),
    canEdit: computed(() => hasPermission('article.edit')),
    canDelete: computed(() => hasPermission('article.delete')),
    canPublish: computed(() => hasPermission('article.publish')),
    canManage: computed(() => hasPermission('article.manage')),
  }
  
  /**
   * 系统管理相关权限检查
   */
  const systemPermissions = {
    canView: computed(() => hasPermission('system.view')),
    canConfig: computed(() => hasPermission('system.config')),
    canAdmin: computed(() => hasPermission('system.admin')),
    canViewAudit: computed(() => hasPermission('audit.view')),
    canExportAudit: computed(() => hasPermission('audit.export')),
  }
  
  /**
   * 角色管理相关权限检查
   */
  const rolePermissions = {
    canView: computed(() => hasPermission('role.view')),
    canCreate: computed(() => hasPermission('role.create')),
    canEdit: computed(() => hasPermission('role.edit')),
    canDelete: computed(() => hasPermission('role.delete')),
    canAssign: computed(() => hasPermission('role.assign')),
  }
  
  // 监听用户变化，清除缓存
  watch(user, () => {
    permissionCache.value.clear()
  }, { deep: true })
  
  // 监听权限变化，清除缓存
  watch(permissions, () => {
    permissionCache.value.clear()
  }, { deep: true })
  
  return {
    // 基础权限检查
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    
    // 角色检查
    hasRole,
    hasAnyRole,
    hasLevel,
    getUserLevel,
    
    // 便捷检查
    isAdmin,
    isSuperAdmin,
    
    // 分组权限
    aiPermissions,
    userPermissions,
    articlePermissions,
    systemPermissions,
    rolePermissions,
    
    // 数据
    user: user,
    roles: roles,
    permissions: permissions
  }
}
