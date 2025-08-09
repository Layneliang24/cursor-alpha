import request from './request'

/**
 * 上传图片
 * @param {File} file - 图片文件
 * @returns {Promise} - 返回包含图片URL的Promise
 */
export const uploadImage = (file) => {
  const formData = new FormData()
  formData.append('image', file)
  
  return request.post('/upload/image/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export const uploadAvatar = (file) => {
  const formData = new FormData()
  formData.append('avatar', file)
  
  return request.post('/upload/avatar/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export const updateAvatarUrl = (avatarUrl) => {
  return request.post('/update-avatar-url/', {
    avatar_url: avatarUrl
  })
}

export default {
  uploadImage,
  uploadAvatar,
  updateAvatarUrl
}
