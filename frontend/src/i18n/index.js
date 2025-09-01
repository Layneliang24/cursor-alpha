import { createI18n } from 'vue-i18n'
import zhCN from './locales/zh-CN'
import enUS from './locales/en-US'

// 获取浏览器语言设置
function getDefaultLocale() {
  const savedLocale = localStorage.getItem('locale')
  if (savedLocale) {
    return savedLocale
  }
  
  const browserLocale = navigator.language || navigator.userLanguage
  if (browserLocale.startsWith('zh')) {
    return 'zh-CN'
  }
  return 'en-US'
}

const i18n = createI18n({
  legacy: false, // 使用Composition API
  locale: getDefaultLocale(),
  fallbackLocale: 'zh-CN',
  messages: {
    'zh-CN': zhCN,
    'en-US': enUS
  },
  globalInjection: true, // 全局注入$t函数
  silentTranslationWarn: process.env.NODE_ENV === 'production'
})

// 监听语言变化
i18n.global.locale.watch((newLocale) => {
  localStorage.setItem('locale', newLocale)
  document.documentElement.lang = newLocale
})

export default i18n
