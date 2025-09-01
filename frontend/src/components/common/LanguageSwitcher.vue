<template>
  <div class="language-switcher">
    <el-dropdown @command="handleLanguageChange" trigger="click">
      <div class="language-trigger">
        <el-icon class="language-icon">
          <Globe />
        </el-icon>
        <span class="current-language">{{ currentLanguageLabel }}</span>
        <el-icon class="arrow-icon">
          <ArrowDown />
        </el-icon>
      </div>
      <template #dropdown>
        <el-dropdown-menu>
          <el-dropdown-item 
            v-for="lang in availableLanguages" 
            :key="lang.code"
            :command="lang.code"
            :class="{ active: currentLocale === lang.code }"
          >
            <div class="language-option">
              <span class="flag">{{ lang.flag }}</span>
              <span class="name">{{ lang.name }}</span>
              <el-icon v-if="currentLocale === lang.code" class="check-icon">
                <Check />
              </el-icon>
            </div>
          </el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Globe, ArrowDown, Check } from '@element-plus/icons-vue'

const { locale } = useI18n()

// 可用语言列表
const availableLanguages = [
  {
    code: 'zh-CN',
    name: '中文',
    flag: '🇨🇳'
  },
  {
    code: 'en-US',
    name: 'English',
    flag: '🇺🇸'
  }
]

// 当前语言
const currentLocale = computed(() => locale.value)

// 当前语言标签
const currentLanguageLabel = computed(() => {
  const lang = availableLanguages.find(l => l.code === currentLocale.value)
  return lang ? lang.name : '中文'
})

// 处理语言切换
const handleLanguageChange = (languageCode) => {
  locale.value = languageCode
}
</script>

<style scoped>
.language-switcher {
  display: inline-block;
}

.language-trigger {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s;
  user-select: none;
}

.language-trigger:hover {
  background-color: var(--el-fill-color-light);
}

.language-icon {
  font-size: 16px;
  color: var(--el-text-color-regular);
}

.current-language {
  font-size: 14px;
  color: var(--el-text-color-primary);
  font-weight: 500;
}

.arrow-icon {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  transition: transform 0.2s;
}

.language-trigger:hover .arrow-icon {
  transform: rotate(180deg);
}

.language-option {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 0;
}

.flag {
  font-size: 16px;
}

.name {
  flex: 1;
  font-size: 14px;
  color: var(--el-text-color-primary);
}

.check-icon {
  font-size: 14px;
  color: var(--el-color-primary);
}

:deep(.el-dropdown-menu__item.active) {
  background-color: var(--el-color-primary-light-9);
  color: var(--el-color-primary);
}

:deep(.el-dropdown-menu__item:hover) {
  background-color: var(--el-fill-color-light);
}
</style>
