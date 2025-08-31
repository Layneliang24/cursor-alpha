import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  server: {
    port: 3000,
    historyApiFallback: true,
    hmr: {
      overlay: true, // 错误覆盖层
      port: 24678,   // HMR 端口
    },
    watch: {
      usePolling: true, // Windows 环境优化
      interval: 100,
    },
    // 安全头配置 - XSS防护
    headers: {
      "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-eval'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' data: https://fonts.gstatic.com; img-src 'self' data: https: blob:; connect-src 'self' https://api.siliconflow.cn https://openrouter.ai https://api.openai.com https://hk.chenmoai.cn https://api.chenmoai.cn ws://localhost:24678; object-src 'none'; frame-src 'none'; base-uri 'self'; form-action 'self'; upgrade-insecure-requests",
      "X-Content-Type-Options": "nosniff",
      "X-Frame-Options": "DENY",
      "X-XSS-Protection": "1; mode=block",
      "Referrer-Policy": "strict-origin-when-cross-origin",
      "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
    },
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: (path) => {
          // 如果是媒体文件，去掉/api前缀
          if (path.startsWith('/api/media/')) {
            return path.replace('/api', '')
          }
          return path
        },
      },
      '/pronunciation': {
        target: 'https://dict.youdao.com',
        changeOrigin: true,
        rewrite: (path) => path.replace('/pronunciation', '/dictvoice'),
        configure: (proxy, options) => {
          proxy.on('proxyReq', (proxyReq, req, res) => {
            // 添加必要的请求头
            proxyReq.setHeader('Referer', 'https://dict.youdao.com')
            proxyReq.setHeader('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
          })
        },
      },
    },
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    // 代码分割和优化配置
    rollupOptions: {
      output: {
        chunkFileNames: 'assets/js/[name]-[hash].js',
        entryFileNames: 'assets/js/[name]-[hash].js',
        assetFileNames: 'assets/[ext]/[name]-[hash].[ext]',
        manualChunks: {
          // 第三方库分离
          'vendor': ['vue', 'vue-router', 'pinia'],
          'ui': ['element-plus', '@element-plus/icons-vue'],
          'charts': ['echarts'],
          // 地道表达模块暂时使用自动分包
        },
      },
    },
    // 压缩配置
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
      },
    },
    // 构建性能优化
    chunkSizeWarningLimit: 1000,
  },
  // 优化配置
  optimizeDeps: {
    include: ['vue', 'vue-router', 'pinia', 'element-plus', 'echarts'],
  },
  
  // Vitest 测试配置
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./tests/setup.js'],
    include: ['tests/unit/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}'],
    exclude: [
      '**/node_modules/**',
      '**/dist/**',
      '**/cypress/**',
      '**/.{idea,git,cache,output,temp}/**',
      '**/tests/e2e/**',
      '**/tests/selenium/**',
    ],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'coverage/**',
        'dist/**',
        'packages/*/test{,s}/**',
        '**/*.d.ts',
        'cypress/**',
        'test{,s}/**',
        'test{,-*}.{js,cjs,mjs,ts,tsx,jsx}',
        '**/*{.,-}test.{js,cjs,mjs,ts,tsx,jsx}',
        '**/*{.,-}spec.{js,cjs,mjs,ts,tsx,jsx}',
        '**/__tests__/**',
        '**/{karma,rollup,webpack,vite,vitest,jest,ava,babel,nyc,cypress,tsup,build}.config.*',
        '**/.{eslint,mocha,prettier}rc.{js,cjs,yml}',
        'src/main.js',
        'src/router/**',
        'tests/**',
      ],
      thresholds: {
        global: {
          branches: 80,
          functions: 80,
          lines: 80,
          statements: 80,
        },
      },
    },
    // 测试超时配置
    testTimeout: 10000,
    hookTimeout: 10000,
    // 并发配置
    threads: true,
    maxThreads: 4,
    minThreads: 1,
    // 监听模式配置
    watch: {
      exclude: ['**/node_modules/**', '**/dist/**'],
    },
  },
}) 