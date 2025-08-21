import { defineConfig } from 'vite'
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
    port: 3000,
    historyApiFallback: true,
    hmr: {
      overlay: true, // 错误覆盖层
      port: 24678   // HMR 端口
    },
    watch: {
      usePolling: true, // Windows 环境优化
      interval: 100
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
        }
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
        }
      }
    }
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets'
  }
}) 