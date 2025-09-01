import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  test: {
    environment: 'jsdom',
    setupFiles: ['./tests/setup.js'],
    globals: true,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      reportsDirectory: './coverage',
      exclude: [
        'node_modules/',
        'dist/',
        'coverage/',
        '**/*.d.ts',
        '**/*.config.js',
        '**/*.config.ts',
        'tests/',
        '**/__tests__/**',
        '**/*.test.js',
        '**/*.test.ts',
        '**/*.spec.js',
        '**/*.spec.ts',
        '**/mocks/**',
        '**/test-utils/**',
        'src/main.js',
        'src/router/index.js',
        'src/i18n/index.js'
      ],
      include: [
        'src/**/*.js',
        'src/**/*.vue',
        'src/**/*.ts'
      ],
      thresholds: {
        global: {
          branches: 80,
          functions: 80,
          lines: 80,
          statements: 80
        },
        './src/components/': {
          branches: 85,
          functions: 85,
          lines: 85,
          statements: 85
        },
        './src/views/': {
          branches: 80,
          functions: 80,
          lines: 80,
          statements: 80
        },
        './src/stores/': {
          branches: 90,
          functions: 90,
          lines: 90,
          statements: 90
        },
        './src/utils/': {
          branches: 95,
          functions: 95,
          lines: 95,
          statements: 95
        },
        './src/api/': {
          branches: 85,
          functions: 85,
          lines: 85,
          statements: 85
        }
      },
      all: true,
      clean: true,
      cleanOnRerun: true
    },
    include: [
      'tests/**/*.{test,spec}.{js,ts,vue}',
      'src/**/*.{test,spec}.{js,ts,vue}'
    ],
    exclude: [
      'node_modules/',
      'dist/',
      'coverage/',
      '**/*.d.ts'
    ]
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '~': resolve(__dirname, 'src')
    }
  }
})
