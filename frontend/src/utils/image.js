/**
 * 图片URL处理工具
 */

const API_BASE_URL = ''

/**
 * 获取完整的图片URL
 * @param {string} imagePath - 图片路径
 * @returns {string} - 完整的图片URL
 */
export function getImageUrl(imagePath) {
  if (!imagePath) {
    return ''
  }
  
  // 如果已经是完整URL，直接返回
  if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
    return imagePath
  }
  
  // 如果是相对路径，拼接完整URL
  if (imagePath.startsWith('/media/')) {
    return imagePath
  }
  
  // 如果是以/开头的其他路径，添加/media前缀
  if (imagePath.startsWith('/')) {
    return `/media${imagePath}`
  }
  
  // 如果不是以/开头，添加/media/前缀
  return `/media/${imagePath}`
}

/**
 * 获取默认头像URL
 * @returns {string} - 默认头像URL
 */
export function getDefaultAvatarUrl() {
  // 使用在线头像生成服务作为默认头像
  return 'https://api.dicebear.com/7.x/initials/svg?seed=User&backgroundColor=667eea&textColor=ffffff'
}
