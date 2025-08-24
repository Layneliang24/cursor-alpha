import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    fs: {
      // 允许访问上一级目录（以便从项目根 tests/ 读取用例）
      allow: ['..']
    }
  },
  test: {
    environment: 'jsdom',
    globals: true,
    css: true,
    // 仅扫描前端项目内的测试，避免跨根解析问题
    include: [
      'src/**/__tests__/**/*.{test,spec}.{js,ts,jsx,tsx}'
    ],
    setupFiles: ['./tests/setupTests.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html'],
      reportsDirectory: './coverage',
      include: ['src/**/*.{vue,js,ts}'],
      exclude: [
        'src/main.js',
        'src/**/*.d.ts',
        'src/**/__tests__/**',
        'src/**/*.spec.{js,ts}',
        'src/**/*.test.{js,ts}'
      ]
    }
  }
})
