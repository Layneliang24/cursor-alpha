import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'
import i18n from './i18n'

// 导入MSW
import { startMockServer } from './mocks/server'

// 在开发环境中启动Mock服务
if (process.env.NODE_ENV === 'development') {
  startMockServer()
}

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(ElementPlus)
app.use(i18n)

app.mount('#app') 