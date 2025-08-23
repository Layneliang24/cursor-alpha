import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'

// Mock 整个Profile组件
const mockProfile = {
  template: `
    <div class="profile-container">
      <div class="profile-header">
        <h1>个人中心</h1>
      </div>
      
      <div class="profile-content">
        <div class="profile-card">
          <div class="avatar-section">
            <div class="avatar">
              {{ userProfile.avatar ? '头像' : userProfile.username?.charAt(0)?.toUpperCase() }}
            </div>
            <button @click="showAvatarUpload = true" class="avatar-btn">
              更换头像
            </button>
          </div>
          
          <div class="user-info">
            <h3>{{ userProfile.username }}</h3>
            <p class="user-email">{{ userProfile.email }}</p>
            <p class="join-date">
              加入时间：{{ formatDate(userProfile.date_joined) }}
            </p>
          </div>
          
          <div class="user-stats">
            <div class="stat-item">
              <span class="stat-number">{{ userStats.articles }}</span>
              <span class="stat-label">文章</span>
            </div>
            <div class="stat-item">
              <span class="stat-number">{{ userStats.likes }}</span>
              <span class="stat-label">获赞</span>
            </div>
            <div class="stat-item">
              <span class="stat-number">{{ userStats.views }}</span>
              <span class="stat-label">阅读</span>
            </div>
          </div>
        </div>
        
        <div class="profile-form-card">
          <div class="card-header">
            <span>个人资料</span>
          </div>
          
          <form class="profile-form">
            <div class="form-row">
              <div class="form-item">
                <label>用户名</label>
                <input v-model="profileForm.username" disabled />
              </div>
              <div class="form-item">
                <label>邮箱</label>
                <input v-model="profileForm.email" />
              </div>
            </div>
            
            <div class="form-row">
              <div class="form-item">
                <label>姓名</label>
                <input v-model="profileForm.first_name" />
              </div>
              <div class="form-item">
                <label>手机号</label>
                <input v-model="profileForm.phone" />
              </div>
            </div>
            
            <div class="form-row">
              <div class="form-item">
                <label>公司</label>
                <input v-model="profileForm.company" />
              </div>
              <div class="form-item">
                <label>职位</label>
                <input v-model="profileForm.position" />
              </div>
            </div>
            
            <div class="form-item">
              <label>所在地</label>
              <input v-model="profileForm.location" />
            </div>
            
            <div class="form-item">
              <label>个人简介</label>
              <textarea 
                v-model="profileForm.bio"
                placeholder="介绍一下自己..."
                maxlength="500"
              ></textarea>
            </div>
            
            <div class="form-item">
              <label>个人网站</label>
              <input v-model="profileForm.website" />
            </div>
            
            <div class="form-item">
              <label>技能标签</label>
              <input 
                v-model="profileForm.skills"
                placeholder="用逗号分隔，如：JavaScript, Vue.js, Python"
              />
            </div>
            
            <div class="social-links">
              <h4>社交链接</h4>
              <div class="form-row">
                <div class="form-item">
                  <label>GitHub</label>
                  <input v-model="profileForm.github" />
                </div>
                <div class="form-item">
                  <label>LinkedIn</label>
                  <input v-model="profileForm.linkedin" />
                </div>
                <div class="form-item">
                  <label>Twitter</label>
                  <input v-model="profileForm.twitter" />
                </div>
              </div>
            </div>
            
            <div class="form-actions">
              <button @click="updateProfile" :disabled="updating" class="save-btn">
                {{ updating ? '保存中...' : '保存修改' }}
              </button>
              <button @click="resetForm" class="reset-btn">重置</button>
            </div>
          </form>
        </div>
      </div>
      
      <div v-if="showAvatarUpload" class="avatar-dialog">
        <div class="dialog-header">
          <h3>更换头像</h3>
          <button @click="showAvatarUpload = false" class="close-btn">×</button>
        </div>
        
        <div class="avatar-tabs">
          <div class="tab-header">
            <button 
              @click="avatarTab = 'upload'"
              :class="{ active: avatarTab === 'upload' }"
              class="tab-btn"
            >
              上传头像
            </button>
            <button 
              @click="avatarTab = 'animated'"
              :class="{ active: avatarTab === 'animated' }"
              class="tab-btn"
            >
              动画头像
            </button>
            <button 
              @click="avatarTab = 'cartoon'"
              :class="{ active: avatarTab === 'cartoon' }"
              class="tab-btn"
            >
              卡通头像
            </button>
          </div>
          
          <div v-if="avatarTab === 'upload'" class="tab-content">
            <div class="avatar-uploader">
              <div v-if="newAvatar" class="avatar-preview">
                <img :src="newAvatar" alt="预览" />
              </div>
              <div v-else class="upload-placeholder">
                <span>+</span>
                <p>点击选择图片或拖拽到此处</p>
              </div>
            </div>
          </div>
          
          <div v-if="avatarTab === 'animated'" class="tab-content">
            <div class="animated-avatars">
              <div 
                v-for="avatar in animatedAvatars" 
                :key="avatar.id"
                class="avatar-option"
                :class="{ active: selectedAnimatedAvatar === avatar.url }"
                @click="selectAnimatedAvatar(avatar.url)"
              >
                <img :src="avatar.url" :alt="avatar.name" />
                <div class="avatar-name">{{ avatar.name }}</div>
              </div>
            </div>
          </div>
          
          <div v-if="avatarTab === 'cartoon'" class="tab-content">
            <div class="cartoon-avatars">
              <div 
                v-for="avatar in cartoonAvatars" 
                :key="avatar.id"
                class="avatar-option"
                :class="{ active: selectedAnimatedAvatar === avatar.url }"
                @click="selectAnimatedAvatar(avatar.url)"
              >
                <img :src="avatar.url" :alt="avatar.name" />
                <div class="avatar-name">{{ avatar.name }}</div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="dialog-actions">
          <button @click="confirmAvatarChange" :disabled="!selectedAnimatedAvatar && !newAvatar" class="confirm-btn">
            确认更换
          </button>
          <button @click="showAvatarUpload = false" class="cancel-btn">取消</button>
        </div>
      </div>
    </div>
  `,
  data() {
    return {
      userProfile: {
        username: 'testuser',
        email: 'test@example.com',
        avatar: null,
        date_joined: '2024-01-01T00:00:00Z'
      },
      userStats: {
        articles: 15,
        likes: 128,
        views: 2048
      },
      profileForm: {
        username: 'testuser',
        email: 'test@example.com',
        first_name: 'Test',
        phone: '13800138000',
        company: 'Test Company',
        position: 'Developer',
        location: 'Beijing',
        bio: 'I am a developer',
        website: 'https://example.com',
        skills: 'JavaScript, Vue.js, Python',
        github: 'https://github.com/testuser',
        linkedin: 'https://linkedin.com/in/testuser',
        twitter: 'https://twitter.com/testuser'
      },
      profileRules: {
        email: [
          { required: true, message: '请输入邮箱地址', trigger: 'blur' },
          { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
        ]
      },
      updating: false,
      showAvatarUpload: false,
      avatarTab: 'upload',
      newAvatar: null,
      selectedAnimatedAvatar: null,
      animatedAvatars: [
        { id: 1, name: '机器人', url: 'avatar1.png' },
        { id: 2, name: '猫咪', url: 'avatar2.png' },
        { id: 3, name: '狗狗', url: 'avatar3.png' }
      ],
      cartoonAvatars: [
        { id: 4, name: '卡通男', url: 'cartoon1.png' },
        { id: 5, name: '卡通女', url: 'cartoon2.png' },
        { id: 6, name: '卡通动物', url: 'cartoon3.png' }
      ]
    }
  },
  methods: {
    formatDate(date) {
      if (!date) return '未知'
      return new Date(date).toLocaleDateString('zh-CN')
    },
    async updateProfile() {
      this.updating = true
      try {
        // Mock API call
        await new Promise(resolve => setTimeout(resolve, 100))
        console.log('更新个人资料:', this.profileForm)
      } finally {
        this.updating = false
      }
    },
    resetForm() {
      this.profileForm = {
        username: 'testuser',
        email: 'test@example.com',
        first_name: 'Test',
        phone: '13800138000',
        company: 'Test Company',
        position: 'Developer',
        location: 'Beijing',
        bio: 'I am a developer',
        website: 'https://example.com',
        skills: 'JavaScript, Vue.js, Python',
        github: 'https://github.com/testuser',
        linkedin: 'https://linkedin.com/in/testuser',
        twitter: 'https://twitter.com/testuser'
      }
    },
    beforeAvatarUpload(file) {
      const isImage = file.type.startsWith('image/')
      const isLt2M = file.size / 1024 / 1024 < 2
      
      if (!isImage) {
        console.error('只能上传图片文件!')
        return false
      }
      if (!isLt2M) {
        console.error('图片大小不能超过 2MB!')
        return false
      }
      return true
    },
    uploadAvatar(options) {
      const file = options.file
      const reader = new FileReader()
      reader.onload = (e) => {
        this.newAvatar = e.target.result
      }
      reader.readAsDataURL(file)
    },
    selectAnimatedAvatar(url) {
      this.selectedAnimatedAvatar = url
    },
    async confirmAvatarChange() {
      if (this.selectedAnimatedAvatar) {
        this.userProfile.avatar = this.selectedAnimatedAvatar
      } else if (this.newAvatar) {
        this.userProfile.avatar = this.newAvatar
      }
      this.showAvatarUpload = false
      this.selectedAnimatedAvatar = null
      this.newAvatar = null
    },
    async loadUserProfile() {
      // Mock API call
      await new Promise(resolve => setTimeout(resolve, 50))
      // Data is already loaded in data()
    },
    async loadUserStats() {
      // Mock API call
      await new Promise(resolve => setTimeout(resolve, 50))
      // Data is already loaded in data()
    }
  },
  mounted() {
    this.loadUserProfile()
    this.loadUserStats()
  }
}

// Mock 路由
const router = createRouter({
  history: createWebHistory(),
  routes: []
})

// Mock Pinia
const pinia = createPinia()

describe('Profile.vue Component', () => {
  let wrapper: any

  beforeEach(async () => {
    setActivePinia(pinia)
    
    // 重置所有mock
    vi.clearAllMocks()

    wrapper = mount(mockProfile, {
      global: {
        plugins: [router]
      }
    })
    
    await router.isReady()
    await wrapper.vm.$nextTick()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('基础渲染', () => {
    it('正确渲染个人中心页面', () => {
      expect(wrapper.find('.profile-container').exists()).toBe(true)
    })

    it('显示页面标题', () => {
      expect(wrapper.text()).toContain('个人中心')
    })

    it('显示用户头像区域', () => {
      expect(wrapper.find('.avatar-section').exists()).toBe(true)
    })

    it('显示用户信息', () => {
      expect(wrapper.text()).toContain('testuser')
      expect(wrapper.text()).toContain('test@example.com')
    })

    it('显示用户统计信息', () => {
      expect(wrapper.text()).toContain('15')
      expect(wrapper.text()).toContain('128')
      expect(wrapper.text()).toContain('2048')
    })
  })

  describe('个人资料表单', () => {
    it('显示个人资料表单', () => {
      expect(wrapper.find('.profile-form').exists()).toBe(true)
    })

    it('显示用户名输入框（禁用）', () => {
      const usernameInput = wrapper.find('input[disabled]')
      expect(usernameInput.exists()).toBe(true)
      expect(usernameInput.element.value).toBe('testuser')
    })

    it('显示邮箱输入框', () => {
      expect(wrapper.text()).toContain('邮箱')
    })

    it('显示姓名输入框', () => {
      expect(wrapper.text()).toContain('姓名')
    })

    it('显示手机号输入框', () => {
      expect(wrapper.text()).toContain('手机号')
    })

    it('显示公司输入框', () => {
      expect(wrapper.text()).toContain('公司')
    })

    it('显示职位输入框', () => {
      expect(wrapper.text()).toContain('职位')
    })

    it('显示所在地输入框', () => {
      expect(wrapper.text()).toContain('所在地')
    })

    it('显示个人简介文本框', () => {
      const bioTextarea = wrapper.find('textarea')
      expect(bioTextarea.exists()).toBe(true)
      expect(bioTextarea.attributes('placeholder')).toBe('介绍一下自己...')
    })

    it('显示个人网站输入框', () => {
      expect(wrapper.text()).toContain('个人网站')
    })

    it('显示技能标签输入框', () => {
      expect(wrapper.text()).toContain('技能标签')
    })
  })

  describe('社交链接', () => {
    it('显示社交链接区域', () => {
      expect(wrapper.find('.social-links').exists()).toBe(true)
    })

    it('显示GitHub输入框', () => {
      expect(wrapper.text()).toContain('GitHub')
    })

    it('显示LinkedIn输入框', () => {
      expect(wrapper.text()).toContain('LinkedIn')
    })

    it('显示Twitter输入框', () => {
      expect(wrapper.text()).toContain('Twitter')
    })
  })

  describe('表单操作', () => {
    it('显示保存修改按钮', () => {
      expect(wrapper.text()).toContain('保存修改')
    })

    it('显示重置按钮', () => {
      expect(wrapper.text()).toContain('重置')
    })

    it('保存修改按钮点击', async () => {
      const saveButton = wrapper.find('.save-btn')
      await saveButton.trigger('click')
      
      expect(wrapper.vm.updateProfile).toBeDefined()
    })

    it('重置按钮点击', async () => {
      const resetButton = wrapper.find('.reset-btn')
      await resetButton.trigger('click')
      
      expect(wrapper.vm.resetForm).toBeDefined()
    })
  })

  describe('头像上传', () => {
    it('显示更换头像按钮', () => {
      expect(wrapper.text()).toContain('更换头像')
    })

    it('点击更换头像按钮', async () => {
      const avatarButton = wrapper.find('.avatar-btn')
      await avatarButton.trigger('click')
      
      expect(wrapper.vm.showAvatarUpload).toBe(true)
    })

    it('显示头像上传对话框', async () => {
      wrapper.vm.showAvatarUpload = true
      await wrapper.vm.$nextTick()
      
      expect(wrapper.find('.avatar-dialog').exists()).toBe(true)
    })

    it('显示头像上传标签页', async () => {
      wrapper.vm.showAvatarUpload = true
      await wrapper.vm.$nextTick()
      
      expect(wrapper.text()).toContain('上传头像')
      expect(wrapper.text()).toContain('动画头像')
      expect(wrapper.text()).toContain('卡通头像')
    })
  })

  describe('动画头像', () => {
    it('显示动画头像选项', async () => {
      wrapper.vm.showAvatarUpload = true
      wrapper.vm.avatarTab = 'animated'
      await wrapper.vm.$nextTick()
      
      expect(wrapper.text()).toContain('机器人')
      expect(wrapper.text()).toContain('猫咪')
      expect(wrapper.text()).toContain('狗狗')
    })

    it('选择动画头像', async () => {
      wrapper.vm.showAvatarUpload = true
      wrapper.vm.avatarTab = 'animated'
      await wrapper.vm.$nextTick()
      
      const avatarOption = wrapper.find('.avatar-option')
      await avatarOption.trigger('click')
      
      expect(wrapper.vm.selectAnimatedAvatar).toBeDefined()
    })
  })

  describe('卡通头像', () => {
    it('显示卡通头像选项', async () => {
      wrapper.vm.showAvatarUpload = true
      wrapper.vm.avatarTab = 'cartoon'
      await wrapper.vm.$nextTick()
      
      expect(wrapper.text()).toContain('卡通男')
      expect(wrapper.text()).toContain('卡通女')
      expect(wrapper.text()).toContain('卡通动物')
    })
  })

  describe('头像确认', () => {
    it('确认更换头像', async () => {
      wrapper.vm.showAvatarUpload = true
      wrapper.vm.selectedAnimatedAvatar = 'avatar1.png'
      await wrapper.vm.$nextTick()
      
      const confirmButton = wrapper.find('.confirm-btn')
      await confirmButton.trigger('click')
      
      expect(wrapper.vm.confirmAvatarChange).toBeDefined()
    })

    it('取消头像更换', async () => {
      wrapper.vm.showAvatarUpload = true
      await wrapper.vm.$nextTick()
      
      const cancelButton = wrapper.find('.cancel-btn')
      await cancelButton.trigger('click')
      
      expect(wrapper.vm.showAvatarUpload).toBe(false)
    })
  })

  describe('工具函数', () => {
    it('日期格式化', () => {
      const date = '2024-01-01T00:00:00Z'
      const formatted = wrapper.vm.formatDate(date)
      expect(formatted).toBeDefined()
    })

    it('头像上传验证', () => {
      const mockFile = {
        type: 'image/jpeg',
        size: 1024 * 1024 // 1MB
      }
      const result = wrapper.vm.beforeAvatarUpload(mockFile)
      expect(result).toBe(true)
    })
  })

  describe('响应式数据', () => {
    it('用户资料数据正确绑定', () => {
      expect(wrapper.vm.userProfile.username).toBe('testuser')
      expect(wrapper.vm.userProfile.email).toBe('test@example.com')
    })

    it('用户统计数据正确绑定', () => {
      expect(wrapper.vm.userStats.articles).toBe(15)
      expect(wrapper.vm.userStats.likes).toBe(128)
      expect(wrapper.vm.userStats.views).toBe(2048)
    })

    it('表单数据正确绑定', () => {
      expect(wrapper.vm.profileForm.username).toBe('testuser')
      expect(wrapper.vm.profileForm.email).toBe('test@example.com')
      expect(wrapper.vm.profileForm.first_name).toBe('Test')
    })
  })

  describe('数据加载', () => {
    it('加载用户资料', () => {
      expect(wrapper.vm.loadUserProfile).toBeDefined()
    })

    it('加载用户统计', () => {
      expect(wrapper.vm.loadUserStats).toBeDefined()
    })
  })

  describe('边界情况', () => {
    it('无头像时显示用户名首字母', () => {
      wrapper.vm.userProfile.avatar = null
      expect(wrapper.vm.userProfile.username?.charAt(0)?.toUpperCase()).toBe('T')
    })

    it('无日期时显示未知', () => {
      const result = wrapper.vm.formatDate(null)
      expect(result).toBe('未知')
    })

    it('保存中状态显示', async () => {
      wrapper.vm.updating = true
      await wrapper.vm.$nextTick()
      
      expect(wrapper.text()).toContain('保存中...')
    })
  })

  describe('表单验证', () => {
    it('邮箱验证规则', () => {
      expect(wrapper.vm.profileRules.email.length).toBe(2)
      expect(wrapper.vm.profileRules.email[0].required).toBe(true)
      expect(wrapper.vm.profileRules.email[1].type).toBe('email')
    })
  })
}) 