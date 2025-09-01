import { setupWorker } from 'msw/browser'
import { handlers } from './handlers'

// 设置MSW Worker
export const worker = setupWorker(...handlers)

// 启动Mock服务
export const startMockServer = () => {
  if (process.env.NODE_ENV === 'development' || process.env.NODE_ENV === 'test') {
    worker.start({
      onUnhandledRequest: 'bypass', // 对于未处理的请求，直接通过
      serviceWorker: {
        url: '/mockServiceWorker.js'
      }
    })
  }
}

// 停止Mock服务
export const stopMockServer = () => {
  worker.stop()
}

// 重置Mock数据
export const resetMockData = () => {
  // 这里可以重置Mock数据到初始状态
  console.log('Mock data reset')
}
