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
      }
    }
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets'
  }
}) 