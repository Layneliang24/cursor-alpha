import { describe, it, expect, beforeEach } from 'vitest'
import { createI18n } from 'vue-i18n'
import zhCN from '@/i18n/locales/zh-CN'
import enUS from '@/i18n/locales/en-US'

// 创建测试用的i18n实例
const createTestI18n = (locale = 'zh-CN') => {
  return createI18n({
    legacy: false,
    locale,
    fallbackLocale: 'zh-CN',
    messages: {
      'zh-CN': zhCN,
      'en-US': enUS
    },
    silentTranslationWarn: true
  })
}

describe('i18n Internationalization', () => {
  let i18n

  beforeEach(() => {
    i18n = createTestI18n()
  })

  describe('Chinese Locale (zh-CN)', () => {
    beforeEach(() => {
      i18n.global.locale.value = 'zh-CN'
    })

    it('应该正确翻译通用文本', () => {
      expect(i18n.global.t('common.confirm')).toBe('确认')
      expect(i18n.global.t('common.cancel')).toBe('取消')
      expect(i18n.global.t('common.save')).toBe('保存')
      expect(i18n.global.t('common.delete')).toBe('删除')
    })

    it('应该正确翻译导航文本', () => {
      expect(i18n.global.t('nav.dashboard')).toBe('仪表板')
      expect(i18n.global.t('nav.aiConfig')).toBe('AI配置')
      expect(i18n.global.t('nav.settings')).toBe('设置')
      expect(i18n.global.t('nav.logout')).toBe('退出登录')
    })

    it('应该正确翻译登录页面文本', () => {
      expect(i18n.global.t('login.title')).toBe('AI服务配置系统')
      expect(i18n.global.t('login.username')).toBe('用户名')
      expect(i18n.global.t('login.password')).toBe('密码')
      expect(i18n.global.t('login.login')).toBe('登录')
    })

    it('应该正确翻译AI配置页面文本', () => {
      expect(i18n.global.t('aiConfig.title')).toBe('AI服务配置')
      expect(i18n.global.t('aiConfig.providers')).toBe('服务提供商')
      expect(i18n.global.t('aiConfig.models')).toBe('AI模型')
      expect(i18n.global.t('aiConfig.apiKeys')).toBe('API密钥')
    })

    it('应该正确翻译设置页面文本', () => {
      expect(i18n.global.t('settings.title')).toBe('系统设置')
      expect(i18n.global.t('settings.userProfile')).toBe('个人信息')
      expect(i18n.global.t('settings.preferencesLabel')).toBe('偏好设置')
      expect(i18n.global.t('settings.securityLabel')).toBe('安全设置')
    })

    it('应该正确翻译错误信息', () => {
      expect(i18n.global.t('errors.networkError')).toBe('网络错误')
      expect(i18n.global.t('errors.serverError')).toBe('服务器错误')
      expect(i18n.global.t('errors.validationError')).toBe('验证错误')
    })

    it('应该正确翻译成功信息', () => {
      expect(i18n.global.t('success.saveSuccess')).toBe('保存成功')
      expect(i18n.global.t('success.deleteSuccess')).toBe('删除成功')
      expect(i18n.global.t('success.updateSuccess')).toBe('更新成功')
    })

    it('应该正确翻译确认对话框', () => {
      expect(i18n.global.t('confirm.deleteConfirm')).toBe('确定要删除吗？')
      expect(i18n.global.t('confirm.logoutConfirm')).toBe('确定要退出登录吗？')
    })
  })

  describe('English Locale (en-US)', () => {
    beforeEach(() => {
      i18n.global.locale.value = 'en-US'
    })

    it('should correctly translate common text', () => {
      expect(i18n.global.t('common.confirm')).toBe('Confirm')
      expect(i18n.global.t('common.cancel')).toBe('Cancel')
      expect(i18n.global.t('common.save')).toBe('Save')
      expect(i18n.global.t('common.delete')).toBe('Delete')
    })

    it('should correctly translate navigation text', () => {
      expect(i18n.global.t('nav.dashboard')).toBe('Dashboard')
      expect(i18n.global.t('nav.aiConfig')).toBe('AI Config')
      expect(i18n.global.t('nav.settings')).toBe('Settings')
      expect(i18n.global.t('nav.logout')).toBe('Logout')
    })

    it('should correctly translate login page text', () => {
      expect(i18n.global.t('login.title')).toBe('AI Service Configuration System')
      expect(i18n.global.t('login.username')).toBe('Username')
      expect(i18n.global.t('login.password')).toBe('Password')
      expect(i18n.global.t('login.login')).toBe('Login')
    })

    it('should correctly translate AI config page text', () => {
      expect(i18n.global.t('aiConfig.title')).toBe('AI Service Configuration')
      expect(i18n.global.t('aiConfig.providers')).toBe('Service Providers')
      expect(i18n.global.t('aiConfig.models')).toBe('AI Models')
      expect(i18n.global.t('aiConfig.apiKeys')).toBe('API Keys')
    })

    it('should correctly translate settings page text', () => {
      expect(i18n.global.t('settings.title')).toBe('System Settings')
      expect(i18n.global.t('settings.userProfile')).toBe('User Profile')
      expect(i18n.global.t('settings.preferencesLabel')).toBe('Preferences')
      expect(i18n.global.t('settings.securityLabel')).toBe('Security')
    })

    it('should correctly translate error messages', () => {
      expect(i18n.global.t('errors.networkError')).toBe('Network Error')
      expect(i18n.global.t('errors.serverError')).toBe('Server Error')
      expect(i18n.global.t('errors.validationError')).toBe('Validation Error')
    })

    it('should correctly translate success messages', () => {
      expect(i18n.global.t('success.saveSuccess')).toBe('Save successful')
      expect(i18n.global.t('success.deleteSuccess')).toBe('Delete successful')
      expect(i18n.global.t('success.updateSuccess')).toBe('Update successful')
    })

    it('should correctly translate confirmation dialogs', () => {
      expect(i18n.global.t('confirm.deleteConfirm')).toBe('Are you sure you want to delete?')
      expect(i18n.global.t('confirm.logoutConfirm')).toBe('Are you sure you want to logout?')
    })
  })

  describe('Locale Switching', () => {
    it('应该能够切换语言', () => {
      // 初始为中文
      i18n.global.locale.value = 'zh-CN'
      expect(i18n.global.t('common.confirm')).toBe('确认')

      // 切换到英文
      i18n.global.locale.value = 'en-US'
      expect(i18n.global.t('common.confirm')).toBe('Confirm')

      // 切换回中文
      i18n.global.locale.value = 'zh-CN'
      expect(i18n.global.t('common.confirm')).toBe('确认')
    })

    it('应该使用回退语言', () => {
      i18n.global.locale.value = 'en-US'
      
      // 测试不存在的翻译键应该使用回退语言
      expect(i18n.global.t('nonexistent.key')).toBe('nonexistent.key')
    })
  })

  describe('Nested Translation Keys', () => {
    it('应该正确处理嵌套的翻译键', () => {
      i18n.global.locale.value = 'zh-CN'
      
      expect(i18n.global.t('aiConfig.provider.name')).toBe('提供商名称')
      expect(i18n.global.t('aiConfig.provider.type')).toBe('提供商类型')
      expect(i18n.global.t('settings.profile.username')).toBe('用户名')
      expect(i18n.global.t('settings.profile.email')).toBe('邮箱')
    })

    it('should handle nested translation keys in English', () => {
      i18n.global.locale.value = 'en-US'
      
      expect(i18n.global.t('aiConfig.provider.name')).toBe('Provider Name')
      expect(i18n.global.t('aiConfig.provider.type')).toBe('Provider Type')
      expect(i18n.global.t('settings.profile.username')).toBe('Username')
      expect(i18n.global.t('settings.profile.email')).toBe('Email')
    })
  })

  describe('Translation Coverage', () => {
    it('应该包含所有必要的翻译键', () => {
      const requiredKeys = [
        'common.confirm',
        'common.cancel',
        'common.save',
        'common.delete',
        'nav.dashboard',
        'nav.aiConfig',
        'nav.settings',
        'nav.logout',
        'login.title',
        'login.username',
        'login.password',
        'login.login',
        'aiConfig.title',
        'aiConfig.providers',
        'aiConfig.models',
        'aiConfig.apiKeys',
              'settings.title',
      'settings.userProfile',
      'settings.preferencesLabel',
      'settings.securityLabel',
        'errors.networkError',
        'errors.serverError',
        'errors.validationError',
        'success.saveSuccess',
        'success.deleteSuccess',
        'success.updateSuccess',
        'confirm.deleteConfirm',
        'confirm.logoutConfirm'
      ]

      requiredKeys.forEach(key => {
        expect(i18n.global.t(key)).toBeTruthy()
        expect(i18n.global.t(key)).not.toBe(key)
      })
    })
  })
})
