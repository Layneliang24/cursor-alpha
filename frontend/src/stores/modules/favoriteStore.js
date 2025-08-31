/**
 * 收藏管理Store
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useFavoriteStore = defineStore('favorite', () => {
  // 状态
  const favorites = ref({
    models: [], // 收藏的模型ID列表
    providers: [], // 收藏的提供商ID列表
    configs: [] // 收藏的配置ID列表
  })
  
  const loading = ref(false)

  // 计算属性
  const favoriteModels = computed(() => favorites.value.models || [])
  const favoriteProviders = computed(() => favorites.value.providers || [])
  const favoriteConfigs = computed(() => favorites.value.configs || [])
  
  const totalFavorites = computed(() => {
    return (favorites.value.models?.length || 0) +
           (favorites.value.providers?.length || 0) +
           (favorites.value.configs?.length || 0)
  })

  // 动作
  const loadFavorites = () => {
    try {
      const savedFavorites = localStorage.getItem('ai_config_favorites')
      if (savedFavorites) {
        const parsed = JSON.parse(savedFavorites)
        favorites.value = {
          models: parsed.models || [],
          providers: parsed.providers || [],
          configs: parsed.configs || []
        }
      }
    } catch (error) {
      console.error('Load favorites error:', error)
      // 重置为默认值
      favorites.value = {
        models: [],
        providers: [],
        configs: []
      }
    }
  }

  const saveFavorites = () => {
    try {
      localStorage.setItem('ai_config_favorites', JSON.stringify(favorites.value))
    } catch (error) {
      console.error('Save favorites error:', error)
    }
  }

  const addFavorite = (type, id) => {
    if (!favorites.value[type]) {
      favorites.value[type] = []
    }
    
    if (!favorites.value[type].includes(id)) {
      favorites.value[type].push(id)
      saveFavorites()
      return true
    }
    return false
  }

  const removeFavorite = (type, id) => {
    if (!favorites.value[type]) {
      return false
    }
    
    const index = favorites.value[type].indexOf(id)
    if (index > -1) {
      favorites.value[type].splice(index, 1)
      saveFavorites()
      return true
    }
    return false
  }

  const toggleFavorite = (type, id) => {
    if (isFavorite(type, id)) {
      return removeFavorite(type, id)
    } else {
      return addFavorite(type, id)
    }
  }

  const isFavorite = (type, id) => {
    return favorites.value[type]?.includes(id) || false
  }

  const clearFavorites = (type = null) => {
    if (type) {
      favorites.value[type] = []
    } else {
      favorites.value = {
        models: [],
        providers: [],
        configs: []
      }
    }
    saveFavorites()
  }

  const getFavoritesByType = (type) => {
    return favorites.value[type] || []
  }

  const exportFavorites = () => {
    const exportData = {
      exported_at: new Date().toISOString(),
      favorites: favorites.value
    }
    
    const dataStr = JSON.stringify(exportData, null, 2)
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr)
    
    const exportFileDefaultName = `ai_config_favorites_${new Date().toISOString().split('T')[0]}.json`
    
    const linkElement = document.createElement('a')
    linkElement.setAttribute('href', dataUri)
    linkElement.setAttribute('download', exportFileDefaultName)
    linkElement.click()
  }

  const importFavorites = (data) => {
    try {
      let importData
      if (typeof data === 'string') {
        importData = JSON.parse(data)
      } else {
        importData = data
      }
      
      if (importData.favorites) {
        favorites.value = {
          models: importData.favorites.models || [],
          providers: importData.favorites.providers || [],
          configs: importData.favorites.configs || []
        }
        saveFavorites()
        return true
      }
      return false
    } catch (error) {
      console.error('Import favorites error:', error)
      return false
    }
  }

  // 同步到服务器的方法（如果需要）
  const syncToServer = async () => {
    // 这里可以实现与服务器同步收藏的逻辑
    // 暂时留空，后续可以扩展
  }

  const syncFromServer = async () => {
    // 这里可以实现从服务器获取收藏的逻辑
    // 暂时留空，后续可以扩展
  }

  // 初始化
  loadFavorites()

  return {
    // 状态
    favorites,
    loading,
    
    // 计算属性
    favoriteModels,
    favoriteProviders,
    favoriteConfigs,
    totalFavorites,
    
    // 动作
    loadFavorites,
    saveFavorites,
    addFavorite,
    removeFavorite,
    toggleFavorite,
    isFavorite,
    clearFavorites,
    getFavoritesByType,
    exportFavorites,
    importFavorites,
    syncToServer,
    syncFromServer
  }
})

export default useFavoriteStore
