import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import request from '@/api/request'

export const useUserStore = defineStore('user', () => {
  // 状态
  const user = ref(null)
  const token = ref(localStorage.getItem('token'))
  const permissions = ref([])
  const roles = ref([])
  const loading = ref(false)
  
  // 计算属性
  const isAuthenticated = computed(() => !!user.value && !!token.value)
  const isAdmin = computed(() => {
    return user.value?.is_staff || 
           user.value?.is_superuser || 
           roles.value.some(role => ['admin', 'superadmin'].includes(role.name))
  })
  const isSuperAdmin = computed(() => {
    return user.value?.is_superuser || 
           roles.value.some(role => role.name === 'superadmin')
  })
  
  // 用户信息相关方法
  const setUser = (userData) => {
    user.value = userData
    if (userData?.permissions) {
      permissions.value = userData.permissions
    }
    if (userData?.roles) {
      roles.value = userData.roles
    }
  }
  
  const setToken = (tokenValue) => {
    token.value = tokenValue
    if (tokenValue) {
      localStorage.setItem('token', tokenValue)
    } else {
      localStorage.removeItem('token')
    }
  }
  
  const setPermissions = (permissionList) => {
    permissions.value = permissionList || []
  }
  
  const setRoles = (roleList) => {
    roles.value = roleList || []
  }
  
  // 登录
  const login = async (credentials) => {
    loading.value = true
    try {
      const response = await request.post('/auth/login/', credentials)
      const { user: userData, tokens } = response.data
      
      setUser(userData)
      setToken(tokens.access)
      
      // 获取用户权限和角色信息
      await fetchUserPermissions()
      
      return userData
    } catch (error) {
      console.error('登录失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }
  
  // 登出
  const logout = async () => {
    try {
      // 可以调用后端登出接口
      // await request.post('/auth/logout/')
    } catch (error) {
      console.error('登出失败:', error)
    } finally {
      // 清除本地状态
      user.value = null
      permissions.value = []
      roles.value = []
      setToken(null)
    }
  }
  
  // 获取当前用户信息
  const fetchCurrentUser = async () => {
    if (!token.value) return null
    
    loading.value = true
    try {
      const response = await request.get('/users/me/')
      const userData = response.data
      
      setUser(userData)
      await fetchUserPermissions()
      
      return userData
    } catch (error) {
      console.error('获取用户信息失败:', error)
      // Token可能已过期，清除本地状态
      if (error.response?.status === 401) {
        await logout()
      }
      throw error
    } finally {
      loading.value = false
    }
  }
  
  // 获取用户权限信息
  const fetchUserPermissions = async () => {
    if (!user.value) return
    
    try {
      // 获取用户权限
      const permResponse = await request.get('/rbac/user-permissions/')
      setPermissions(permResponse.data.permissions)
      
      // 获取用户角色
      const roleResponse = await request.get('/rbac/user-roles/')
      setRoles(roleResponse.data.roles)
      
    } catch (error) {
      console.error('获取权限信息失败:', error)
      // 如果获取权限失败，设置为空数组而不是抛出错误
      setPermissions([])
      setRoles([])
    }
  }
  
  // 刷新用户权限（在权限变更后调用）
  const refreshPermissions = async () => {
    if (isAuthenticated.value) {
      await fetchUserPermissions()
    }
  }
  
  // 检查权限
  const hasPermission = (permission) => {
    if (!permission) return true
    if (isSuperAdmin.value) return true
    return permissions.value.includes(permission)
  }
  
  const hasAnyPermission = (permissionList) => {
    if (!permissionList || permissionList.length === 0) return true
    if (isSuperAdmin.value) return true
    return permissionList.some(permission => permissions.value.includes(permission))
  }
  
  const hasAllPermissions = (permissionList) => {
    if (!permissionList || permissionList.length === 0) return true
    if (isSuperAdmin.value) return true
    return permissionList.every(permission => permissions.value.includes(permission))
  }
  
  const hasRole = (roleName) => {
    if (!roleName) return true
    return roles.value.some(role => role.name === roleName)
  }
  
  // 更新用户信息
  const updateUserInfo = async (updateData) => {
    loading.value = true
    try {
      const response = await request.patch('/users/me/', updateData)
      const userData = response.data
      
      setUser(userData)
      return userData
    } catch (error) {
      console.error('更新用户信息失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }
  
  // 修改密码
  const changePassword = async (passwordData) => {
    try {
      await request.post('/auth/change-password/', passwordData)
    } catch (error) {
      console.error('修改密码失败:', error)
      throw error
    }
  }
  
  // 初始化（应用启动时调用）
  const initialize = async () => {
    if (token.value) {
      try {
        await fetchCurrentUser()
      } catch (error) {
        console.error('初始化用户状态失败:', error)
        // 初始化失败时清除token
        await logout()
      }
    }
  }
  
  return {
    // 状态
    user,
    token,
    permissions,
    roles,
    loading,
    
    // 计算属性
    isAuthenticated,
    isAdmin,
    isSuperAdmin,
    
    // 方法
    setUser,
    setToken,
    setPermissions,
    setRoles,
    login,
    logout,
    fetchCurrentUser,
    fetchUserPermissions,
    refreshPermissions,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    hasRole,
    updateUserInfo,
    changePassword,
    initialize
  }
})
